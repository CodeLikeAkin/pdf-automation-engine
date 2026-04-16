import os
import sys
import asyncio
import markdown
import json
import re
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()

DESIGN_SYSTEMS = {
    "A": "design/system_a_warm.css",
    "B": "design/system_b_corporate.css",
    "C": "design/system_c_minimal.css",
    "D": "design/system_d_classic.css",
    "V": "design/system_v_vanguard.css"
}

async def render_to_pdf(md_path, output_pdf_path, cover_image_path=None, system_choice=None):
    if not os.path.exists(md_path):
        console.print(f"[red]Markdown file not found:[/red] {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Detect Design System from content and STRIP it from the body
    system_choice = "V" # Default to Vanguard for premium feel
    system_match = re.search(r"design_system:\s*([A-DV])", md_content)
    if system_match:
        system_choice = system_match.group(1)
        # Remove the metadata line from the content
        md_content = re.sub(r"design_system:\s*[A-DV]\n?", "", md_content).strip()
    
    css_path = DESIGN_SYSTEMS.get(system_choice, "design/system_v_vanguard.css")
    console.print(f"[bold blue]Using Design System {system_choice}[/bold blue] ({css_path})")

    # Extract Title for Cover
    title = "Premium Guide"
    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
        # Remove the H1 from body to avoid repetition
        md_content = re.sub(r"^#\s+.+$", "", md_content, count=1, flags=re.MULTILINE).strip()

    # Pre-process Markdown for Chapter Openers
    # This finds '## Chapter X: Title' and only the first paragraph as a description
    chapters = []
    def chapter_replacer(match):
        ch_num_raw = match.group(1)
        ch_title = match.group(2)
        # Use regex split to handle both \n\n and \r\n\r\n robustly
        full_text = match.group(3).strip()
        parts = re.split(r'\r?\n\s*\r?\n', full_text, maxsplit=1)
        ch_hook = parts[0] if parts else ""
        remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Format chapter number to 01, 02...
        try:
            ch_num = f"{int(ch_num_raw):02d}"
        except:
            ch_num = ch_num_raw
            
        # Safeguard: Limit TOC description length for aesthetics
        toc_desc = (ch_hook[:177] + "...") if len(ch_hook) > 180 else ch_hook
        chapters.append({"num": ch_num, "title": ch_title, "desc": toc_desc})
        
        # We return the Opener AND only the remaining text (to avoid duplication)
        return f"""
<div class="chapter-opener">
    <div class="opener-number">{ch_num}</div>
    <div class="opener-content">
        <p class="opener-label">CHAPTER {ch_num}</p>
        <h2 id="chapter-{ch_num}">{ch_title}</h2>
        <p class="opener-desc">{ch_hook}</p>
    </div>
</div>

{remaining_text}
"""

    # Updated Regex to find Chapters and catch the content until the next chapter
    # Looking for '## Chapter X: Title' followed by content
    chapter_pattern = r"## Chapter (\d+):\s*(.+)\n((?:(?!##).)*)"
    md_content = re.sub(chapter_pattern, chapter_replacer, md_content, flags=re.DOTALL)

    # Convert Markdown to HTML
    md_instance = markdown.Markdown(extensions=['extra', 'toc'])
    html_body = md_instance.convert(md_content)
    
    # Custom TOC Generation based on our extracted chapters
    toc_html = "<div class='toc-grid'>"
    for ch in chapters:
        toc_html += f"""
    <div class='toc-item'>
        <div class='toc-num'>{ch['num']}</div>
        <div class='toc-text'>
            <a href='#chapter-{ch['num']}'>{ch['title'].upper()}</a>
            <p>{ch['desc']}</p>
        </div>
        <div class='toc-page-num'>--</div>
    </div>"""
    toc_html += "</div>"

    # Read CSS
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    else:
        console.print(f"[yellow]Warning: CSS file not found at {css_path}. Using fallback styling.[/yellow]")

    # Professional HTML Template
    html_full = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            {css_content}
            @page {{
                size: A4;
                margin: 20mm 15mm 25mm 15mm;
            }}
            body {{ margin: 0; padding: 0; }}
            
            .page {{
                position: relative;
                min-height: 250mm;
            }}
            
            .cover {{
                height: 297mm;
                margin: -20mm -15mm;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                background-color: var(--accent);
                color: white;
                page-break-after: always;
            }}

            .cover-content {{
                padding: 60px;
                background: rgba(0, 0, 0, 0.2);
                border: 4px solid white;
                max-width: 80%;
            }}

            .toc-page {{
                page-break-after: always;
                padding: 10mm 5mm;
            }}
            
            .main-content {{
                line-height: 1.8;
            }}
        </style>
    </head>
    <body class="theme-{system_choice.lower()}">
        <!-- Cover Page -->
        <div class="page cover">
            <div class="cover-overlay"></div>
            <div class="cover-content">
                <p class="cover-label">Premium Strategy Guide</p>
                <h1>{title}</h1>
                <p style="font-size: 1.2rem; opacity: 0.8; font-family: var(--font-body); text-transform: uppercase; letter-spacing: 2px;">
                    Expert Insights • 2026 Edition
                </p>
            </div>
        </div>

        <!-- TOC Page -->
        <div class="page toc-page">
            <h1 style="font-size: 3.5rem; color: var(--accent); border-bottom: 2px solid var(--accent); display: inline-block; margin-bottom: 1rem;">Table of Contents</h1>
            <p style="color: var(--muted); margin-bottom: 3rem;">A comprehensive roadmap to your transformation.</p>
            {toc_html}
        </div>

        <!-- Main Content -->
        <div class="main-content">
            {html_body}
        </div>

        <script>
            // Simple script to handle internal links for PDF
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView();
                }});
            }});
        </script>
    </body>
    </html>
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_content(html_full)
        await page.wait_for_load_state("networkidle")
        
        # Take a screenshot preview
        preview_path = output_pdf_path.replace(".pdf", "_preview.png")
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        await page.screenshot(path=preview_path, full_page=True)

        # Generate PDF with Native Page Numbers
        footer_template = f"""
        <div style="font-size: 9px; width: 100%; text-align: center; color: #64748b; border-top: 1px solid rgba(226, 232, 240, 0.1); padding-top: 5px; font-family: 'Inter', sans-serif; letter-spacing: 1px;">
            <span style="color: #f59e0b; font-weight: 800;">VANGUARD SERIES</span> &bull; {title.upper()} &bull; PAGE <span class="pageNumber"></span> OF <span class="totalPages"></span>
        </div>
        """
        
        await page.pdf(
            path=output_pdf_path, 
            format="A4", 
            print_background=True,
            display_header_footer=True,
            footer_template=footer_template,
            header_template="<span></span>", # Empty header
            margin={"top": "20mm", "bottom": "25mm", "left": "15mm", "right": "15mm"}
        )
        await browser.close()
        
    console.print(f"[bold green]Ready for distribution:[/bold green] {output_pdf_path}")
        
    console.print(f"[bold green]Professional PDF generated:[/bold green] {output_pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("Usage: python renderer_v4.py <md_file> [output_pdf] [cover_image] [system_choice]")
    else:
        md = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else md.replace(".md", ".pdf")
        img = sys.argv[3] if len(sys.argv) > 3 else None
        sys_choice = sys.argv[4] if len(sys.argv) > 4 else None
        
        asyncio.run(render_to_pdf(md, out, img, sys_choice))
