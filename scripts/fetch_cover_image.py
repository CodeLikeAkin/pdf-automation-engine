"""
Unsplash Cover Image Fetcher
Downloads a royalty-free portrait image from Unsplash to use as the PDF cover.
Based on Leon's method: search your niche on unsplash.com, find a portrait photo
that matches your guide topic, and use it as the cover + ad creative.
"""
import os
import sys
import requests
import json
import re
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COVERS_DIR = os.path.join(os.path.dirname(__file__), "assets", "covers")

async def call_gemini(prompt, attempt=1):
    """Simple Gemini API caller for search queries with retry logic."""
    if not GEMINI_API_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-001:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 429:
                if attempt > 5:
                    raise Exception("Rate limited after 5 tries.")
                wait_time = (10 * (2 ** (attempt - 1)))
                console.print(f"[yellow]Rate limit (429). Waiting {wait_time}s...[/yellow]")
                await asyncio.sleep(wait_time)
                return await call_gemini(prompt, attempt + 1)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        if attempt <= 3:
            console.print(f"[dim]API Error {e}. Retrying {attempt}/3...[/dim]")
            await asyncio.sleep(5)
            return await call_gemini(prompt, attempt + 1)
        console.print(f"[red]Gemini API failed after {attempt} attempts. Using fallback query.[/red]")
        return None


def fetch_cover_image(query, orientation="portrait"):
    """
    Searches Unsplash for a photo matching the query and downloads it.
    
    Args:
        query: Search term (e.g., "networking", "new mom", "fitness")
        orientation: "portrait" (recommended for PDF covers) or "landscape"
    
    Returns:
        Absolute path to the downloaded image, or None if failed.
    """
    os.makedirs(COVERS_DIR, exist_ok=True)
    slug = query.lower().replace(" ", "_").replace("'", "")
    filepath = os.path.join(COVERS_DIR, f"{slug}.jpg")

    # If we already have this cover, reuse it
    if os.path.exists(filepath):
        console.print(f"[green]Cover image already exists:[/green] {filepath}")
        return os.path.abspath(filepath)

    if not UNSPLASH_ACCESS_KEY:
        console.print("[yellow]Warning: UNSPLASH_ACCESS_KEY not found in .env[/yellow]")
        console.print("[yellow]  Get a free key at https://unsplash.com/developers[/yellow]")
        console.print("[yellow]  Using gradient fallback for the cover page.[/yellow]")
        return None

    console.print(f"[bold blue]Searching Unsplash for:[/bold blue] '{query}' ({orientation})")

    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": query,
                "orientation": orientation,
                "per_page": 5,
                "client_id": UNSPLASH_ACCESS_KEY,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            console.print("[yellow]No images found for that query. Using fallback.[/yellow]")
            return None

        # Pick the first result
        photo = data["results"][0]
        image_url = photo["urls"]["regular"]  # 1080px wide, good quality
        photographer = photo["user"]["name"]
        unsplash_link = photo["links"]["html"]

        console.print(f"[green]Found image by {photographer}[/green]")

        # Download the image
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(img_response.content)

        # Save attribution info (Unsplash requires this)
        attribution_path = filepath.replace(".jpg", "_credit.txt")
        with open(attribution_path, "w", encoding="utf-8") as f:
            f.write(f"Photo by {photographer} on Unsplash\n")
            f.write(f"Link: {unsplash_link}\n")

        console.print(f"[bold green]Cover image downloaded:[/bold green] {filepath}")
        console.print(f"[dim]Attribution: Photo by {photographer} on Unsplash[/dim]")

        # Trigger download tracking (Unsplash API requirement)
        download_location = photo.get("links", {}).get("download_location")
        if download_location:
            try:
                requests.get(
                    download_location,
                    params={"client_id": UNSPLASH_ACCESS_KEY},
                    timeout=10,
                )
            except Exception:
                pass  # Non-critical

        return os.path.abspath(filepath)

    except Exception as e:
        console.print(f"[red]Unsplash API error: {e}[/red]")
        console.print("[yellow]Using gradient fallback for the cover page.[/yellow]")
        return None


async def fetch_contextual_cover(md_path, orientation="portrait"):
    """
    Analyzes a Markdown file and fetches a relevant cover image from Unsplash.
    """
    md_path = Path(md_path)
    if not md_path.exists():
        console.print(f"[red]File not found:[/red] {md_path}")
        return None

    content = md_path.read_text(encoding="utf-8")
    
    # Extract Title and first 500 words
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Professional Guide"
    body_snippet = content[:2000] # Grab a good chunk for context

    prompt = f"""
    You are an editorial design assistant. Based on the book title and content below, 
    generate ONE single high-quality search query for Unsplash to find a premium cover image.
    
    TITLE: "{title}"
    CONTENT SNIPPET: {body_snippet}
    
    REQUIREMENTS:
    - Query must be 2-4 words maximum.
    - Focus on "aesthetic", "minimalist", or "evocative" photography.
    - Focus on professional, high-end editorial vibes.
    - Return ONLY the query string, no quotes or extra text.
    """
    
    console.print(f"[bold yellow]Analyzing context for:[/bold yellow] {title}")
    try:
        query = await call_gemini(prompt)
    except Exception:
        query = None
    
    if not query:
        # Fallback: Extract keywords from title
        console.print("[yellow]Gemini failed. Extracting keywords from title...[/yellow]")
        clean_title = re.sub(r'[^a-zA-Z\s]', '', title)
        words = [w for w in clean_title.split() if len(w) > 3]
        query = " ".join(words[:3]) if words else title
    
    query = query.strip().strip('"').strip("'")
    return fetch_cover_image(query, orientation)


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "networking professional"
    result = fetch_cover_image(query)
    if result:
        console.print(f"\n[bold]Ready to use:[/bold] {result}")
    else:
        console.print("\n[bold yellow]No cover image — PDF will use gradient fallback.[/bold yellow]")
