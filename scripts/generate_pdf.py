"""
Premium PDF Generator — V3
Direct-to-PDF generation using fpdf2.
NO HTML, NO Browser, NO Encoding Errors.
Supports: Full-bleed covers, chapter openers, and sanitized Markdown input.
"""
import os
import sys
import re
from fpdf import FPDF
from rich.console import Console
from PIL import Image

console = Console()

# ============================================================
# DESIGN SETTINGS
# ============================================================
COLORS = {
    "theme-business": {"primary": (37, 99, 235), "bg": (219, 234, 254)},
    "theme-health": {"primary": (5, 150, 105), "bg": (209, 250, 229)},
    "theme-parenting": {"primary": (225, 29, 72), "bg": (255, 228, 230)},
    "theme-money": {"primary": (217, 119, 6), "bg": (254, 243, 199)},
    "theme-self-improvement": {"primary": (124, 58, 237), "bg": (237, 233, 254)},
    "theme-tech": {"primary": (8, 145, 178), "bg": (207, 250, 254)},
}

def get_theme(title):
    title = title.lower()
    if any(k in title for k in ["parenting", "mom", "baby", "kids"]): return COLORS["theme-parenting"]
    if any(k in title for k in ["health", "fitness", "weight", "yoga"]): return COLORS["theme-health"]
    if any(k in title for k in ["money", "finance", "invest", "budget"]): return COLORS["theme-money"]
    if any(k in title for k in ["self", "mindset", "productivity"]): return COLORS["theme-self-improvement"]
    if any(k in title for k in ["tech", "ai", "coding", "software"]): return COLORS["theme-tech"]
    return COLORS["theme-business"]


class PremiumPDF(FPDF):
    def __init__(self, theme_colors, title):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.theme = theme_colors
        self.guide_title = title
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            # Subtle line at top
            self.set_draw_color(*self.theme["primary"])
            self.set_line_width(0.5)
            self.line(10, 10, 200, 10)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f"{self.guide_title} | Page {self.page_no()}/{{nb}}", align="C")

    def cover_page(self, title, subtitle, image_path=None):
        self.add_page()
        
        # 1. Background (Full Bleed Image or Solid Color)
        if image_path and os.path.exists(image_path):
            # Scale image to fill page
            self.image(image_path, x=0, y=0, w=210, h=297)
            
            # FIXED: Add a semi-transparent overlay instead of solid black
            # fpdf2 supports alpha through set_alpha
            with self.set_alpha(0.5):
                self.set_fill_color(0, 0, 0)
                self.rect(0, 0, 210, 297, "F")
        else:
            # Solid Fallback - Professional Gradient-like solid
            self.set_fill_color(*self.get_darker_color(self.theme["primary"], 0.4))
            self.rect(0, 0, 210, 297, "F")

        # 2. Content
        self.set_y(150)
        self.set_font("Helvetica", "B", 42)
        self.set_text_color(255, 255, 255)
        self.multi_cell(180, 18, title.upper(), align="L")
        
        self.ln(5)
        self.set_fill_color(*self.theme["primary"])
        self.rect(10, self.get_y(), 40, 2, "F")
        self.ln(10)

        self.set_font("Helvetica", "", 16)
        self.set_text_color(230, 230, 230)
        self.multi_cell(160, 8, subtitle, align="L")
        
        # Attribution
        self.set_y(260)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "PREMIUM EDITORIAL | 2026 EDITION", align="L")

    def chapter_opener(self, numeral, title):
        self.add_page()
        # Rich Background for chapter starts
        self.set_fill_color(*self.theme["bg"])
        self.rect(0, 0, 210, 297, "F")
        
        # Accent Bar
        self.set_fill_color(*self.theme["primary"])
        self.rect(0, 0, 15, 297, "F")

        self.set_y(100)
        self.set_x(30)
        self.set_font("Helvetica", "B", 90)
        self.set_text_color(*self.get_lighter_color(self.theme["primary"], 1.3))
        self.cell(180, 20, str(numeral).zfill(2), align="L", new_x="LMARGIN", new_y="NEXT")
        
        self.set_y(125)
        self.set_x(30)
        self.set_font("Helvetica", "B", 38)
        self.set_text_color(20, 20, 20)
        self.multi_cell(160, 15, title, align="L")
        
        self.set_fill_color(*self.theme["primary"])
        self.rect(30, 160, 50, 3, "F")

    def write_markdown(self, text):
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            self.set_x(25) # More generous margins for premium feel
            
            if not line:
                self.ln(6)
                continue
                
            # Headers
            if line.startswith("## "):
                self.ln(10)
                self.set_font("Helvetica", "B", 22)
                self.set_text_color(*self.theme["primary"])
                self.multi_cell(170, 12, line[3:], align="L")
                self.ln(4)
            elif line.startswith("### "):
                self.ln(6)
                self.set_font("Helvetica", "B", 15)
                self.set_text_color(*self.get_darker_color(self.theme["primary"], 0.7))
                self.multi_cell(170, 9, line[4:], align="L")
                self.ln(2)
            # Call-outs (Emotional Resonance)
            elif line.startswith("> "):
                current_y = self.get_y()
                self.set_fill_color(*self.theme["bg"])
                self.set_font("Helvetica", "I", 12)
                self.set_text_color(30, 30, 30)
                
                # Draw the box manually for better control
                text_content = line[2:].strip()
                self.set_x(35)
                self.multi_cell(150, 9, text_content, fill=True, align="L")
                
                # Side accent line for quote
                new_y = self.get_y()
                self.set_fill_color(*self.theme["primary"])
                self.rect(30, current_y, 2, new_y - current_y, "F")
                self.ln(6)
            # Bold Support
            elif "**" in line:
                self.write_styled_line(line)
            else:
                self.set_font("Helvetica", "", 12)
                self.set_text_color(40, 40, 40)
                self.multi_cell(170, 8, line, align="L")

    def write_styled_line(self, line):
        self.set_x(25)
        parts = re.split(r'(\*\*.*?\*\*)', line)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self.set_font("Helvetica", "B", 12)
                self.write(8, part[2:-2])
            else:
                self.set_font("Helvetica", "", 12)
                self.write(8, part)
        self.ln(10)

    def get_darker_color(self, rgb, factor):
        return tuple(max(0, int(c * factor)) for c in rgb)
        
    def get_lighter_color(self, rgb, factor):
        return tuple(min(255, int(c * factor)) for c in rgb)


def generate_pdf(md_path, cover_image_path=None):
    if not os.path.exists(md_path):
        console.print(f"[red]Markdown file not found:[/red] {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Title
    title_match = re.search(r'^# (.+)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Sanitized Guide"
    
    theme = get_theme(title)
    pdf = PremiumPDF(theme, title)
    
    # Cover Page
    subtitle = "A complete step-by-step roadmap for success in 2026."
    pdf.cover_page(title, subtitle, cover_image_path)
    
    # Split into Chapters
    raw_chapters = re.split(r'(?=^## Chapter \d+:)', content, flags=re.MULTILINE)
    
    chapter_count = 0
    for chunk in raw_chapters:
        if not chunk.strip(): continue
        if chunk.startswith("# "): continue # Skip main title
        
        # Extract Chapter Title
        header_match = re.search(r'^## Chapter (\d+): (.+)', chunk, re.MULTILINE)
        if header_match:
            chapter_count += 1
            num = header_match.group(1)
            name = header_match.group(2)
            pdf.chapter_opener(num, name)
            
            # Remove the header from body text
            body = chunk[header_match.end():].strip()
            pdf.add_page()
            pdf.write_markdown(body)
        else:
            pdf.add_page()
            pdf.write_markdown(chunk)

    # 5. Back Cover (Restored)
    pdf.add_page()
    pdf.set_fill_color(*theme["primary"])
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_y(120)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 20, "READY TO START?", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(190, 10, "Your journey begins today.", align="C")
    
    output_path = md_path.replace(".md", ".pdf")
    pdf.output(output_path)
    console.print(f"[bold green]Direct PDF generated successfully:[/bold green] {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("Usage: python generate_pdf.py <markdown_file> [cover_image]")
    else:
        file_path = sys.argv[1]
        img_path = sys.argv[2] if len(sys.argv) > 2 else None
        generate_pdf(file_path, img_path)
