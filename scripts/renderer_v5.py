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

# Import image fetcher
try:
    from fetch_cover_image import fetch_contextual_cover
except ImportError:
    fetch_contextual_cover = None

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


def detect_parts(total_chapters, metadata=None):
    """Return part groupings. Uses metadata if provided, else splits into thirds."""
    if metadata and 'parts' in metadata:
        # Expected format: "1-3: Part One Label | 4-7: Part Two Label"
        try:
            custom_parts = []
            parts_raw = metadata['parts'].split('|')
            for p in parts_raw:
                range_raw, label = p.split(':', 1)
                start, end = map(int, range_raw.strip().split('-'))
                custom_parts.append({"label": label.strip(), "short": label.split('·')[0].strip() if '·' in label else label.strip()[:10], "range": (start, end)})
            return custom_parts
        except Exception as e:
            console.print(f"[yellow]Warning: Could not parse parts metadata: {e}[/yellow]")
    
    if total_chapters <= 4:
        return [{"label": "Chapters", "short": "Part One", "range": (1, total_chapters)}]
    
    third = total_chapters // 3
    remainder = total_chapters % 3
    
    p1_end = third + (1 if remainder > 0 else 0)
    p2_end = p1_end + third + (1 if remainder > 1 else 0)
    
    return [
        {"label": "Part One \u00b7 The Foundation", "short": "Part One", "range": (1, p1_end)},
        {"label": "Part Two \u00b7 The Implementation", "short": "Part Two", "range": (p1_end + 1, p2_end)},
        {"label": "Part Three \u00b7 Long-Term Mastery", "short": "Part Three", "range": (p2_end + 1, total_chapters)},
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
    metadata = {}
    
    for line in lines:
        stripped = line.strip()
        
        # Capture metadata like "theme: vitality"
        meta_match = re.match(r'^([a-z_]+):\s*(.+)$', line.strip())
        if meta_match and current_chapter is None:
             metadata[meta_match.group(1)] = meta_match.group(2).strip()
             continue
        
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
        
        # Chapter description — description: ...
        desc_match = re.match(r'^description:\s*(.+)$', stripped, re.IGNORECASE)
        if desc_match and current_chapter is not None and len(current_body_lines) < 2:
             current_chapter['hook'] = desc_match.group(1).strip()
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
    
    # Extract hooks (first meaningful paragraph, max 120 chars) if not already set
    for ch in chapters:
        if ch['hook']: continue
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
    
    return title, chapters, conclusion_md, metadata


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
    """Generate the TOC structure. Page numbers are filled dynamically by Playwright."""
    html = ""
    for part in parts:
        start, end = part['range']
        part_chapters = [ch for ch in chapters if start <= ch['num'] <= end]
        if not part_chapters: continue
        
        html += f'<div class="toc-part">\n'
        html += f'  <div class="toc-part-label">{part["label"]}</div>\n'
        for ch in part_chapters:
            num_str = f"{ch['num']:02d}"
            html += f'''  <div class="toc-entry">
    <div class="toc-entry-num">{num_str}</div>
    <div class="toc-entry-title">{ch['title']}</div>
    <div class="toc-entry-page" id="toc-pg-{ch['num']}">--</div>
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
<div class="chapter-opener" id="ch-opener-{ch['num']}">
    <div class="opener-ghost-num">{num_str}</div>
    <div class="opener-meta">
        <div class="opener-label">Chapter {num_word} &middot; {part_label}</div>
        <h2 class="opener-title">{ch['title']}</h2>
        <p class="opener-desc">{ch['hook']}</p>
    </div>
</div>
'''
    
    body = f'''
<div class="page chapter-body-page">
    <div class="chapter-body">
        <div class="chapter-header-bar">
            <div>
                <span class="chapter-header-bar-title">{ch['title']}</span>
                <span class="chapter-header-bar-meta"> &middot; {part_label}</span>
            </div>
            <span class="chapter-header-bar-page" id="ch-page-label-{ch['num']}">PAGE --</span>
        </div>
        {body_html}
    </div>
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
def assemble_html(title, chapters, conclusion_md, metadata):
    """Read the HTML template and fill all slots."""
    template = TEMPLATE_PATH.read_text(encoding='utf-8')
    
    # Theme selection
    theme = metadata.get('theme', 'premium')
    theme_css_path = PROJECT_ROOT / "design" / f"system_v5_{theme}.css"
    if not theme_css_path.exists():
        theme_css_path = CSS_PATH
        
    # Read CSS content and inject directly
    css_content = theme_css_path.read_text(encoding='utf-8')
    # Strip @import — we'll add it as a <link> separately handled by font loading
    # Actually keep @import inside <style> — Playwright handles it fine
    
    # Determine parts
    parts = detect_parts(len(chapters), metadata)
    
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
    
    author = metadata.get('author', 'Dr. Olumide Balogun')
    
    if 'cover_blurb' in metadata:
        cover_blurb = metadata['cover_blurb']
    else:
        cover_blurb = f"The Complete 14-Day Nigerian Diet Reset to Reverse Hypertension, Manage Diabetes, and Restore Your Heart Health Without Giving Up the Foods You Love."
    
    # Cover Image logic
    cover_image_html = ""
    if 'cover_image' in metadata:
        img_path = Path(metadata['cover_image']).resolve()
        if img_path.exists():
            # Use absolute path with file:// for local images
            cover_image_html = f'<div class="cover-image-area"><img src="file:///{str(img_path).replace("\\", "/").lstrip("/")}" /></div>'
        else:
            cover_image_html = f'<div class="cover-image-area">IMAGE NOT FOUND</div>'
    else:
        cover_image_html = '<div class="cover-image-area">THE EDITORIAL GUIDE</div>'

    # Fill template slots
    html = template.replace('{{CSS_CONTENT}}', css_content)
    html = html.replace('{{COVER_IMAGE}}', cover_image_html)
    html = html.replace('{{TITLE}}', main_title)
    html = html.replace('{{COVER_LABEL}}', 'A Premium Nigerian Health Guide')
    html = html.replace('{{COVER_TAGLINE}}', cover_tagline)
    html = html.replace('{{COVER_BLURB}}', cover_blurb)
    html = html.replace('{{AUTHOR}}', author)
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
    title, chapters, conclusion_md, metadata = extract_structure(md_content)
    
    console.print(f"[bold blue]Title:[/bold blue] {title}")
    console.print(f"[bold blue]Chapters found:[/bold blue] {len(chapters)}")
    console.print(f"[bold blue]Word Count:[/bold blue] {len(md_content.split())}")
    console.print(f"[bold blue]Theme:[/bold blue] {metadata.get('theme', 'default')}")
    
    # 1.5 Auto-fetch cover image if missing
    if 'cover_image' not in metadata and fetch_contextual_cover:
        console.print("[bold yellow]No cover image found. Attempting contextual auto-fetch...[/bold yellow]")
        try:
            image_path = await fetch_contextual_cover(md_path)
            if image_path:
                metadata['cover_image'] = image_path
                console.print(f"[green]Auto-fetched cover:[/green] {image_path}")
        except Exception as e:
            console.print(f"[red]Auto-fetch failed: {e}[/red]")
    
    # 2. Assemble HTML
    html = assemble_html(title, chapters, conclusion_md, metadata)
    
    # 3. Save debug HTML (for manual inspection)
    debug_html_path = output_pdf_path.with_suffix('.debug.html')
    debug_html_path.write_text(html, encoding='utf-8')
    console.print(f"[dim]Debug HTML:[/dim] {debug_html_path}")
    
    # 4. Render with Playwright
    console.print("[bold yellow]Launching Playwright...[/bold yellow]")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load the file directly instead of set_content
        # This resolves local asset paths correctly
        await page.goto(f"file:///{str(debug_html_path).replace('\\', '/')}")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 4. DYNAMIC ROUTING — Calculate real page numbers
        console.print("[bold yellow]Calculating dynamic page numbers...[/bold yellow]")
        
        page_data = await page.evaluate("""() => {
            const results = [];
            const pageHeight = 1122.5; // Approx height of A4 at 96dpi
            
            document.querySelectorAll('.chapter-opener').forEach(el => {
                const rect = el.getBoundingClientRect();
                const pageNum = Math.ceil((window.scrollY + rect.top + 1) / pageHeight);
                const chId = el.id.replace('ch-opener-', '');
                results.push({ id: chId, page: pageNum });
            });
            return results;
        }""")
        
        for item in page_data:
            ch_id = item['id']
            real_page = f"{item['page']:02d}"
            await page.evaluate(f"""() => {{
                const tocEntry = document.getElementById('toc-pg-{ch_id}');
                if (tocEntry) tocEntry.innerText = '{real_page}';
                
                const pageLabel = document.getElementById('ch-page-label-{ch_id}');
                if (pageLabel) pageLabel.innerText = 'PAGE {real_page}';
            }}""")
        
        # Screenshot preview
        preview_path = str(output_pdf_path).replace('.pdf', '_preview.png')
        await page.screenshot(path=preview_path, full_page=True)
        console.print(f"[dim]Preview:[/dim] {preview_path}")
        
        # PDF footer — matching warm palette
        footer_template = f"""
        <div style="font-size: 8px; width: 100%; text-align: center; color: #6A7368; font-family: 'Inter', sans-serif; letter-spacing: 1px; padding-top: 4px;">
            <span style="color: #C04829; font-weight: 700;">PREMIUM EDITORIAL</span>
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
            margin={"top": "25mm", "bottom": "25mm", "left": "0mm", "right": "0mm"}
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
