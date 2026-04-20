"""
Research & Content Generator — V5 (Grounded & Multi-Phase)
Implements a 'NotebookLM' grounded research approach.
FEATURES:
- --mode research: Scrapes web and builds a unique TOC.
- --mode write: Writes chapters using the grounded context.
- Grounded Writing: AI is fed specific 2026 trends/data from the web.
- Multi-Stage Approval: Explicit stops for user review.
"""
import os
import sys
import httpx
import asyncio
import unicodedata
import re
import json
import random
import argparse
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ============================================================
# SETTINGS
# ============================================================
MAX_RETRIES = 15
BASE_DELAY = 15
CHAPTER_COUNT = 10
RESEARCH_FILE = "output/research_context.json"

# ============================================================
# PROMPTS
# ============================================================

Grounded_TOC_PROMPT = """
You are a expert sales consultant and research assistant creating a high-converting guide for the Nigerian market.
TOPIC: "{topic}"
NICHE: "{niche}"

RESEARCH DATA FOUND:
{research_data}

STRICT REQUIREMENTS:
1. Based on the research data above, create a 10-chapter Table of Contents.
2. Appeal to NIGERIAN EMOTIONS and PAIN POINTS (e.g., survival, financial freedom, protecting family from harassment, dignity).
3. Use catchy, high-converting Nigerian headlines (e.g., "The Shield", "Survival Roadmap", "Ending the Extortion").
4. Return ONLY a JSON list of 10 strings representing the chapter titles.
"""

CHAPTER_WRITING_PROMPT = """
You are a specialist author writing for an emotionally-driven Nigerian success guide.
Topic: "{topic}"
Chapter {index}: "{chapter_title}"

YOU MUST BASE YOUR WRITING ON THE FOLLOWING RESEARCH DATA:
---
RESEARCH SOURCE DATA:
{research_data}
---

STRICT REQUIREMENTS:
1. Length: 300-350 words (CRITICAL: Must be concise to fit on one page).
2. Tone: Relatable, urgent, and empowering for a Nigerian audience. Use Nigerian cultural context where appropriate (e.g., street wisdom, resilience). No generic AI corporate tone.
3. Structure: 
   - Powerful Introduction (The Hook).
   - "Why This Matters for You" (Emotional impact).
   - "Your Shield & Action Plan" (Steps to take).
   - "> The 'Naija' Pro Tip": A high-value secret or insight.
4. Grounding: You MUST explicitly use at least 2-3 specific facts or trends from the RESEARCH SOURCE DATA above.
"""

# ============================================================
# UTILITIES
# ============================================================

async def call_gemini_with_retry(prompt, attempt=1):
    if not GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY missing.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-001:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.8, "maxOutputTokens": 4096}}
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 429:
                if attempt > MAX_RETRIES: raise Exception(f"Rate limited after {MAX_RETRIES} tries.")
                wait_time = (BASE_DELAY * (2 ** (attempt - 1))) + (random.random() * 5)
                console.print(f"[yellow]Rate limit (429). Waiting {wait_time:.1f}s...[/yellow]")
                await asyncio.sleep(wait_time)
                return await call_gemini_with_retry(prompt, attempt + 1)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        if attempt <= MAX_RETRIES:
            console.print(f"[dim]API Error {e}. Retrying...[/dim]")
            await asyncio.sleep(5)
            return await call_gemini_with_retry(prompt, attempt + 1)
        raise e

# ============================================================
# CORE PHASES
# ============================================================

async def phase_research(topic, niche, research_text):
    """Generates the grounded TOC and saves the research context."""
    console.print(f"[bold blue]Grounding in Research...[/bold blue]")
    
    prompt = Grounded_TOC_PROMPT.format(topic=topic, niche=niche, research_data=research_text)
    raw_toc = await call_gemini_with_retry(prompt)
    
    try:
        start = raw_toc.find("[")
        end = raw_toc.rfind("]") + 1
        toc_list = json.loads(raw_toc[start:end])
    except:
        console.print("[red]Failed to parse TOC JSON. Using line split fallback.[/red]")
        toc_list = [L.strip() for L in raw_toc.split("\n") if L.strip() and re.match(r'^\d|\*', L)][:10]

    # Save for later phases
    context = {
        "topic": topic,
        "niche": niche,
        "toc": toc_list,
        "research": research_text
    }
    os.makedirs("output", exist_ok=True)
    with open(RESEARCH_FILE, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=4)
        
    console.print(f"\n[bold green]Phase 1 Complete![/bold green]")
    console.print(f"[bold]Topic:[/bold] {topic}")
    console.print(f"[bold]Proposed Table of Contents:[/bold]")
    for i, title in enumerate(toc_list, 1):
        console.print(f"  {i}. {title}")
    
    console.print(f"\n[yellow]ACTION REQUIRED:[/yellow] Review the TOC above. If happy, run with --mode write")


async def phase_write():
    """Writes all chapters based on the saved research context."""
    if not os.path.exists(RESEARCH_FILE):
        console.print("[red]Error: No research context found. Run --mode research first.[/red]")
        return

    with open(RESEARCH_FILE, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    topic = ctx["topic"]
    niche = ctx["niche"]
    toc = ctx["toc"]
    research_text = ctx["research"]

    console.print(f"[bold green]Phase 2: Deep Writing Started...[/bold green]")
    full_md = f"# {topic}\n\n"
    
    for i, chapter_title in enumerate(toc, 1):
        prompt = CHAPTER_WRITING_PROMPT.format(
            index=i,
            chapter_title=chapter_title,
            topic=topic,
            research_data=research_text,
            niche=niche
        )
        chapter_content = await call_gemini_with_retry(prompt)
        full_md += chapter_content + "\n\n---\n\n"
        # Delay to avoid burst limits
        await asyncio.sleep(5)

    filename = f"{topic.lower().replace(' ', '_')}.md"
    filepath = os.path.join("drafts", filename)
    os.makedirs("drafts", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_md)

    console.print(f"\n[bold green]Phase 2 Complete![/bold green]")
    console.print(f"Guide saved to: {filepath}")
    console.print(f"[yellow]ACTION REQUIRED:[/yellow] Review the Markdown file. If happy, run: [bold]python scripts/renderer_v5.py {filepath}[/bold]")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["research", "write"], required=True)
    parser.add_argument("--topic", type=str)
    parser.add_argument("--niche", type=str, default="Business")
    parser.add_argument("--research_text", type=str) # Used to pass search results
    args = parser.parse_args()

    if args.mode == "research":
        if not args.topic or not args.research_text:
            console.print("[red]Error: --topic and --research_text are required for research mode.[/red]")
            return
        await phase_research(args.topic, args.niche, args.research_text)
    elif args.mode == "write":
        await phase_write()

if __name__ == "__main__":
    asyncio.run(main())
