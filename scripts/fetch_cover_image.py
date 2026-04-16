"""
Unsplash Cover Image Fetcher
Downloads a royalty-free portrait image from Unsplash to use as the PDF cover.
Based on Leon's method: search your niche on unsplash.com, find a portrait photo
that matches your guide topic, and use it as the cover + ad creative.
"""
import os
import sys
import requests
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
COVERS_DIR = os.path.join(os.path.dirname(__file__), "assets", "covers")


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

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Unsplash API error: {e}[/red]")
        console.print("[yellow]Using gradient fallback for the cover page.[/yellow]")
        return None


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "networking professional"
    result = fetch_cover_image(query)
    if result:
        console.print(f"\n[bold]Ready to use:[/bold] {result}")
    else:
        console.print("\n[bold yellow]No cover image — PDF will use gradient fallback.[/bold yellow]")
