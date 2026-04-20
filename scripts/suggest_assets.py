"""
Suggest Assets — Context-Aware Image Fetcher
Automatically analyze your Markdown guide and fetch a matching Unsplash cover image.
Usage: python scripts/suggest_assets.py drafts/my_guide.md
"""
import os
import sys
import asyncio
import re
from pathlib import Path
from rich.console import Console
from fetch_cover_image import fetch_contextual_cover

console = Console()

async def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/bold red] python scripts/suggest_assets.py <markdown_file>")
        return

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        console.print(f"[bold red]Error:[/bold red] File {md_path} not found.")
        return

    # 1. Fetch the image
    image_path = await fetch_contextual_cover(md_path)
    
    if not image_path:
        console.print("[bold red]Failed to fetch a relevant image.[/bold red]")
        return

    # 2. Update the Markdown metadata
    content = md_path.read_text(encoding="utf-8")
    project_root = Path(__file__).parent.parent
    relative_img_path = os.path.relpath(image_path, project_root).replace("\\", "/")
    
    if "cover_image:" in content:
        # Replace existing
        new_content = re.sub(r"cover_image:.*", f"cover_image: {relative_img_path}", content)
    else:
        # Add to top (after potential frontmatter or at the very top)
        new_content = f"cover_image: {relative_img_path}\n" + content

    md_path.write_text(new_content, encoding="utf-8")
    
    console.print(f"\n[bold green]Success![/bold green]")
    console.print(f"  [bold]Image:[/bold] {image_path}")
    console.print(f"  [bold]Markdown updated:[/bold] {md_path}")

if __name__ == "__main__":
    asyncio.run(main())
