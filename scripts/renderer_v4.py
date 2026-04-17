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

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text

async def render_to_pdf(md_path, output_pdf_path=None, cover_image_path=None, system_choice=None, approved=False):
    if not os.path.exists(md_path):
        console.print(f"[red]Markdown file not found:[/red] {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Detect Design System from content and STRIP it from the body
    system_choice_detected = "V" # Default to Vanguard for premium feel
    system_match = re.search(r"design_system:\s*([A-DV])", md_content)
    if system_match:
        system_choice_detected = system_match.group(1)
        # Remove the metadata line from the content
        md_content = re.sub(r"design_system:\s*[A-DV]\n?", "", md_content).strip()
    
    system_choice = system_choice or system_choice_detected
    css_path = DESIGN_SYSTEMS.get(system_choice, "design/system_v_vanguard.css")
    console.print(f"[bold blue]Using Design System {system_choice}[/bold blue] ({css_path})")

    # Extract Title for Cover and Pathing
    title = "Premium Guide"
    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
        # Remove the H1 from body to avoid repetition
        md_content = re.sub(r"^#\s+.+$", "", md_content, count=1, flags=re.MULTILINE).strip()

    # Resolve Output Path
    project_slug = slugify(title)
    base_output_dir = os.path.join("output", project_slug)
    if approved:
        output_dir = os.path.join(base_output_dir, "final")
    else:
        output_dir = base_output_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not output_pdf_path:
        filename = f"{project_slug}_{'final' if approved else 'draft'}.pdf"
        output_pdf_path = os.path.join(output_dir, filename)
    else:
        # If a path was provided, ensure it's in the right folder if it's just a filename
        if not os.path.dirname(output_pdf_path):
            output_pdf_path = os.path.join(output_dir, output_pdf_path)

    # Pre-process Markdown for Chapter Openers
    # ... (rest of the pre-processing logic remains the same)
    chapters = []
    def chapter_replacer(match):
        ch_num_raw = match.group(1)
        ch_title = match.group(2)
        full_text = match.group(3).strip()
        parts = re.split(r'\r?\n\s*\r?\n', full_text, maxsplit=1)
        ch_hook = parts[0] if parts else ""
        remaining_text = parts[1] if len(parts) > 1 else ""
        
        try:
            ch_num = f"{int(ch_num_raw):02d}"
        except:
            ch_num = ch_num_raw
            
        toc_desc = (ch_hook[:177] + "...") if len(ch_hook) > 180 else ch_hook
        chapters.append({"num": ch_num, "title": ch_title, "desc": toc_desc})
        
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

    chapter_pattern = r"## Chapter (\d+):\s*(.+)\n((?:(?!##).)*)"
    md_content = re.sub(chapter_pattern, chapter_replacer, md_content, flags=re.DOTALL)

    # Convert Markdown to HTML
    md_instance = markdown.Markdown(extensions=['extra', 'toc'])
    html_body = md_instance.convert(md_content)
    
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
            .page {{ position: relative; min-height: 250mm; }}
            .cover {{
                height: 297mm;
                margin: -20mm -15mm;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                background-color: var(--accent);
                background-image: url('{cover_image_path or ""}');
                background-size: cover;
                background-position: center;
                color: white;
                page-break-after: always;
                position: relative;
            }
            .cover-overlay {{
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.4);
                display: { 'block' if cover_image_path else 'none' };
            }}
            .cover-content {{
                position: relative;
                z-index: 10;
                padding: 60px;
                background: rgba(0, 0, 0, 0.2);
                border: 4px solid white;
                max-width: 80%;
            }}
            .toc-page {{ page-break-after: always; padding: 10mm 5mm; }}
            .main-content {{ line-height: 1.8; }}
        </style>
    </head>
    <body class="theme-{system_choice.lower()}">
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
        <div class="page toc-page">
            <h1 style="font-size: 3.5rem; color: var(--accent); border-bottom: 2px solid var(--accent); display: inline-block; margin-bottom: 1rem;">Table of Contents</h1>
            <p style="color: var(--muted); margin-bottom: 3rem;">A comprehensive roadmap to your transformation.</p>
            {toc_html}
        </div>
        <div class="main-content">
            {html_body}
        </div>
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
        await page.screenshot(path=preview_path, full_page=True)

        # Debug HTML for inspection
        debug_html_path = output_pdf_path.replace(".pdf", ".debug.html")
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(html_full)

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
            header_template="<span></span>",
            margin={"top": "20mm", "bottom": "25mm", "left": "15mm", "right": "15mm"}
        )
        await browser.close()
        
    console.print(f"[bold green]Professional PDF generated:[/bold green] {output_pdf_path}")
    if approved:
        console.print(f"[bold gold1]★ FINAL COPY ARCHIVED ★[/bold gold1]")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Render Markdown to Premium PDF")
    parser.add_argument("md_file", help="Path to the markdown file")
    parser.add_argument("--out", help="Output PDF filename or path")
    parser.add_argument("--img", help="Cover image path")
    parser.add_argument("--sys", help="Design system choice (A, B, C, D, V)")
    parser.add_argument("--approved", action="store_true", help="Mark as final approved copy")
    
    args = parser.parse_args()
    
    asyncio.run(render_to_pdf(args.md_file, args.out, args.img, args.sys, args.approved))
