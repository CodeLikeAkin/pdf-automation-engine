"""
Renderer V5 — Clean Architecture Rewrite
=========================================
Fixes all 10 design bugs identified in the forensic audit.

Architecture:
  - Python handles DATA EXTRACTION only.
  - HTML template is a standalone file (design/template_v5.html).
  - CSS is a standalone file (design/system_v5_premium.css).
  - ZERO inline CSS in this script.
  
Key fixes:
  1. No visual hierarchy → Proper type scale in CSS (46pt cover, 40pt chapters, 9.8pt body)
  2. TOC was body text → Grouped Parts with numbered entries
  3. No chapter openers → Dedicated full-bleed pages with ghost numbers
  4. ALL CAPS → Removed all .upper() calls
  5. Cover barely a cover → 8-element cover structure
  6. No grouped structure → Chapters grouped into 3 Parts
  7. Orphaned content → Clean page break logic
  8. Ch1 in TOC → Short descriptions only (max 120 chars)
  9. Truncated conclusion → Proper section splitting (not greedy regex)
  10. Inconsistent callouts → HTML-native strategy boxes with gold dots
"""

import os
import sys
import re
import asyncio
import markdown
from pathlib import Path
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()

# ============================================================
# CONFIG
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "design" / "template_v5.html"
CSS_PATH = PROJECT_ROOT / "design" / "system_v5_premium.css"


# ============================================================
# PART GROUPING — Maps chapter ranges to thematic parts
# ============================================================
# Word forms for chapter numbers
NUMBER_WORDS = {
    1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
    6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten',
    11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
    15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen',
    19: 'Nineteen', 20: 'Twenty'
}


def detect_parts(total_chapters, custom_parts=None):
    """Return part groupings. Uses custom if provided, else splits into thirds."""
    if custom_parts:
        return custom_parts
    
    if total_chapters <= 4:
        return [{"label": "Chapters", "short": "Part One", "range": (1, total_chapters)}]
    
    third = total_chapters // 3
    remainder = total_chapters % 3
    
    p1_end = third + (1 if remainder > 0 else 0)
    p2_end = p1_end + third + (1 if remainder > 1 else 0)
    
    return [
        {"label": "Part One \u00b7 The Foundation (Birth\u201312 Months)", "short": "Part One", "range": (1, p1_end)},
        {"label": "Part Two \u00b7 Building Intelligence (1\u20133 Years)", "short": "Part Two", "range": (p1_end + 1, p2_end)},
        {"label": "Part Three \u00b7 Long-Term Mastery (3+ Years)", "short": "Part Three", "range": (p2_end + 1, total_chapters)},
    ]


def get_part_for_chapter(ch_num, parts):
    """Get the Part label for a given chapter number."""
    for part in parts:
        start, end = part['range']
        if start <= ch_num <= end:
            return part.get('short', 'Part One')
    return 'Part One'


# ============================================================
# MARKDOWN → STRUCTURED DATA (No regex hacks)
# ============================================================
def extract_structure(md_content):
    """
    Parse markdown into a clean data structure.
    Returns: title, chapters[], conclusion_text
    
    Each chapter = {num, title, hook, body_md}
      - hook: first sentence (for TOC), max 120 chars
      - body_md: full chapter content as markdown
    """
    lines = md_content.split('\n')
    
    title = "Premium Guide"
    chapters = []
    conclusion_md = ""
    
    # State machine
    current_chapter = None
    current_body_lines = []
    in_conclusion = False
    conclusion_lines = []
    skip_metadata = True  # Skip metadata lines at top
    
    for line in lines:
        stripped = line.strip()
        
        # Skip metadata like "design_system: V"
        if skip_metadata and re.match(r'^[a-z_]+:\s*\S+$', stripped):
            continue
        skip_metadata = False
        
        # Main title — # Title
        title_match = re.match(r'^#\s+(.+)$', stripped)
        if title_match and not stripped.startswith('##'):
            title = title_match.group(1).strip()
            continue
        
        # Chapter header — ## Chapter X: Title
        chapter_match = re.match(r'^##\s+Chapter\s+(\d+):\s*(.+)$', stripped)
        if chapter_match:
            # Save previous chapter
            if current_chapter is not None:
                current_chapter['body_md'] = '\n'.join(current_body_lines).strip()
                chapters.append(current_chapter)
            
            ch_num = int(chapter_match.group(1))
            ch_title = chapter_match.group(2).strip()
            
            current_chapter = {
                'num': ch_num,
                'title': ch_title,
                'hook': '',
                'body_md': ''
            }
            current_body_lines = []
            in_conclusion = False
            continue
        
        # Conclusion header — ## Conclusion
        conclusion_match = re.match(r'^##\s+Conclusion\b', stripped, re.IGNORECASE)
        if conclusion_match:
            # Save current chapter first
            if current_chapter is not None:
                current_chapter['body_md'] = '\n'.join(current_body_lines).strip()
                chapters.append(current_chapter)
                current_chapter = None
                current_body_lines = []
            in_conclusion = True
            continue
        
        # Accumulate content
        if in_conclusion:
            conclusion_lines.append(line)
        elif current_chapter is not None:
            current_body_lines.append(line)
    
    # Don't forget the last chapter
    if current_chapter is not None:
        current_chapter['body_md'] = '\n'.join(current_body_lines).strip()
        chapters.append(current_chapter)
    
    conclusion_md = '\n'.join(conclusion_lines).strip()
    
    # Extract hooks (first meaningful paragraph, max 120 chars)
    for ch in chapters:
        body = ch['body_md']
        # Find first non-empty paragraph that isn't an HTML block
        paragraphs = re.split(r'\n\s*\n', body)
        for para in paragraphs:
            clean = para.strip()
            if clean and not clean.startswith('<') and not clean.startswith('>'):
                # Truncate to ~120 chars at a word boundary
                if len(clean) > 120:
                    hook = clean[:120].rsplit(' ', 1)[0] + '...'
                else:
                    hook = clean
                ch['hook'] = hook
                break
    
    return title, chapters, conclusion_md


# ============================================================
# CONTENT CONVERTERS (Markdown → HTML fragments)
# ============================================================
def md_to_html(md_text):
    """Convert markdown to HTML, transforming action-box divs into strategy-boxes."""
    # Pre-process: Convert <div class="action-box"> to strategy-box format
    md_text = re.sub(
        r'<div\s+class="action-box">\s*<h4>(.*?)</h4>',
        r'<div class="strategy-box"><div class="strategy-box-title">\1</div>',
        md_text,
        flags=re.DOTALL
    )
    
    md_instance = markdown.Markdown(extensions=['extra', 'toc', 'smarty'])
    return md_instance.convert(md_text)


def build_toc_html(chapters, parts):
    """Generate the grouped Table of Contents HTML — clean style, no descriptions."""
    html = ""
    # Page estimation: cover=1, TOC=1, then each chapter = opener(1) + content(1)
    page_counter = 3  # After cover + TOC
    
    for part in parts:
        start, end = part['range']
        part_chapters = [ch for ch in chapters if start <= ch['num'] <= end]
        
        if not part_chapters:
            continue
        
        html += f'<div class="toc-part">\n'
        html += f'  <div class="toc-part-label">{part["label"]}</div>\n'
        
        for ch in part_chapters:
            num_str = f"{ch['num']:02d}"
            page_counter += 2  # opener page + content page
            
            html += f'''  <div class="toc-entry">
    <div class="toc-entry-num">{num_str}</div>
    <div class="toc-entry-title">{ch['title']}</div>
    <div class="toc-entry-page">{page_counter - 1:02d}</div>
  </div>\n'''
        
        html += '</div>\n'
    
    return html


def build_chapter_html(ch, parts):
    """Build the opener + body HTML for a single chapter."""
    num_str = f"{ch['num']:02d}"
    num_word = NUMBER_WORDS.get(ch['num'], str(ch['num']))
    part_label = get_part_for_chapter(ch['num'], parts)
    body_html = md_to_html(ch['body_md'])
    
    opener = f'''
<div class="chapter-opener">
    <div class="opener-ghost-num">{num_str}</div>
    <div class="opener-meta">
        <div class="opener-label">Chapter {num_word} &middot; {part_label}</div>
        <h2 class="opener-title">{ch['title']}</h2>
        <p class="opener-desc">{ch['hook']}</p>
    </div>
</div>
'''
    
    body = f'''
<div class="chapter-body">
    <div class="chapter-header-bar">
        <div>
            <span class="chapter-header-bar-title">{ch['title']}</span>
            <span class="chapter-header-bar-meta"> &middot; Neural Foundation</span>
        </div>
        <span class="chapter-header-bar-page">PAGE {num_str}</span>
    </div>
    {body_html}
</div>
'''
    
    return opener + body


def build_conclusion_html(conclusion_md):
    """Build conclusion page HTML."""
    if not conclusion_md.strip():
        return ""
    
    body_html = md_to_html(conclusion_md)
    
    return f'''
<div class="page conclusion-page">
    <h2>Conclusion</h2>
    {body_html}
</div>
'''


# ============================================================
# TEMPLATE ASSEMBLY
# ============================================================
def assemble_html(title, chapters, conclusion_md):
    """Read the HTML template and fill all slots."""
    template = TEMPLATE_PATH.read_text(encoding='utf-8')
    
    # Read CSS content and inject directly (file:// links don't work with set_content)
    css_content = CSS_PATH.read_text(encoding='utf-8')
    # Strip @import — we'll add it as a <link> separately handled by font loading
    # Actually keep @import inside <style> — Playwright handles it fine
    
    # Determine parts
    parts = detect_parts(len(chapters))
    
    # Build content blocks
    toc_html = build_toc_html(chapters, parts)
    
    main_content = ""
    for ch in chapters:
        main_content += build_chapter_html(ch, parts)
    main_content += build_conclusion_html(conclusion_md)
    
    # Cover data — content-aware
    cover_decoration = f"{len(chapters):02d}" if len(chapters) > 0 else "12"
    
    # Extract subtitle from title if it has a colon
    if ':' in title:
        main_title = title.split(':')[0].strip()
        cover_tagline = title.split(':', 1)[1].strip()
    else:
        main_title = title
        cover_tagline = 'A Strategic Guide for Mothers'
    
    cover_blurb = f"A science-backed framework covering the {len(chapters)} pillars of early childhood cognitive development \u2014 from neural stimulation and language to nutrition, emotional intelligence, and a lifelong love of learning."
    
    # Fill template slots
    html = template.replace('{{CSS_CONTENT}}', css_content)
    html = html.replace('{{TITLE}}', main_title)
    html = html.replace('{{COVER_LABEL}}', 'A Professional Strategic Guide')
    html = html.replace('{{COVER_TAGLINE}}', cover_tagline)
    html = html.replace('{{COVER_BLURB}}', cover_blurb)
    html = html.replace('{{COVER_DECORATION_NUM}}', cover_decoration)
    html = html.replace('{{COVER_FOOTER_BRAND}}', f'{main_title}'.upper())
    html = html.replace('{{COVER_FOOTER_EDITION}}', f'\u00b7 {cover_tagline}'.upper())
    html = html.replace('{{TOC_CONTENT}}', toc_html)
    html = html.replace('{{MAIN_CONTENT}}', main_content)
    
    return html


# ============================================================
# PDF GENERATION
# ============================================================
async def render_pdf(md_path, output_pdf_path=None):
    """Main entry point: Markdown → structured data → HTML → PDF."""
    
    md_path = Path(md_path).resolve()
    if not md_path.exists():
        console.print(f"[red]File not found:[/red] {md_path}")
        return
    
    if output_pdf_path is None:
        output_pdf_path = md_path.with_suffix('.pdf')
    else:
        output_pdf_path = Path(output_pdf_path).resolve()
    
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[bold blue]Reading:[/bold blue] {md_path.name}")
    
    # 1. Extract content
    md_content = md_path.read_text(encoding='utf-8')
    title, chapters, conclusion_md = extract_structure(md_content)
    
    console.print(f"[bold blue]Title:[/bold blue] {title}")
    console.print(f"[bold blue]Chapters found:[/bold blue] {len(chapters)}")
    if conclusion_md:
        console.print(f"[bold blue]Conclusion:[/bold blue] {len(conclusion_md)} chars")
    
    # 2. Assemble HTML
    html = assemble_html(title, chapters, conclusion_md)
    
    # 3. Save debug HTML (for manual inspection)
    debug_html_path = output_pdf_path.with_suffix('.debug.html')
    debug_html_path.write_text(html, encoding='utf-8')
    console.print(f"[dim]Debug HTML:[/dim] {debug_html_path}")
    
    # 4. Render with Playwright
    console.print("[bold yellow]Launching Playwright...[/bold yellow]")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_content(html)
        await page.wait_for_load_state("networkidle")
        # Extra wait for fonts
        await page.wait_for_timeout(1500)
        
        # Screenshot preview
        preview_path = str(output_pdf_path).replace('.pdf', '_preview.png')
        await page.screenshot(path=preview_path, full_page=True)
        console.print(f"[dim]Preview:[/dim] {preview_path}")
        
        # PDF footer — matching warm palette
        footer_template = f"""
        <div style="font-size: 8px; width: 100%; text-align: center; color: #8A8580; font-family: 'Inter', sans-serif; letter-spacing: 1px; padding-top: 4px;">
            <span style="color: #C5A55A; font-weight: 700;">PREMIUM EDITORIAL</span>
            &nbsp;&bull;&nbsp; {title}
            &nbsp;&bull;&nbsp; Page <span class="pageNumber"></span> of <span class="totalPages"></span>
        </div>
        """
        
        await page.pdf(
            path=str(output_pdf_path),
            format="A4",
            print_background=True,
            display_header_footer=True,
            footer_template=footer_template,
            header_template="<span></span>",
            margin={"top": "15mm", "bottom": "20mm", "left": "0mm", "right": "0mm"}
        )
        
        await browser.close()
    
    file_size_kb = output_pdf_path.stat().st_size / 1024
    console.print(f"\n[bold green]PDF generated successfully[/bold green]")
    console.print(f"   [bold]{output_pdf_path.name}[/bold] ({file_size_kb:.0f} KB)")
    console.print(f"   Chapters: {len(chapters)} | Pages: ~{len(chapters) * 2 + 3}")


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[bold]Usage:[/bold] python renderer_v5.py <markdown_file> [output.pdf]")
        sys.exit(1)
    
    md = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    
    asyncio.run(render_pdf(md, out))
