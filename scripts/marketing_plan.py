import os
import sys
from rich.console import Console

console = Console()

def generate_marketing_plan(topic, niche="Digital Products"):
    console.print(f"[bold green]Generating High-Conversion Marketing Plan for:[/bold green] {topic}")
    
    plan = f"""# Marketing & Monetization Plan: {topic}

## 1. Selar.com Product Optimization
**Recommended Price:** 7,500 NGN (Local) / $27.00 USD (Global)
**High-Conversion Description:**
> "Stop guessing and start executing. This isn't just an ebook; it's a strategic roadmap for those who need results in 2026. Whether you're a beginner or looking to scale, this guide provides the exact frameworks used by industry leaders."

**Key Features for Listing:**
- 10 Comprehensive Chapters
- 3 Done-For-You Templates
- 2026 Trend Analysis included

## 2. Meta Ads Strategy (Facebook & Instagram)

**Ad Creative (Leon's Method):**
> Use the SAME Unsplash cover image from your PDF guide as the ad creative.
> The professional photo that sells the guide also sells the ad. Two birds, one stone.
> Find your cover image at: `assets/covers/` directory.

**Targeting:**
- **Primary:** Professionals interested in {niche}, Entrepreneurship, and Personal Growth.
- **Secondary:** Lookalike audiences from website visitors (Pixel setup required).

### Ad Hook Logic (Leon's Method)
**Variant A: The "How-To" Hook (Problem Solver)**
- **Headline:** How to master {topic} without the 10,000-hour struggle.
- **Primary Text:** Most people fail because they don't have a system. Get the PDF guide that breaks down {topic} into 10 actionable pillars.
- **CTA:** Download Now

**Variant B: The "Shortform" Hook (Urgency)**
- **Headline:** 2026 is the year of {topic}. Are you ready?
- **Primary Text:** The window of opportunity for {topic} is closing. Grab this expert-drafted roadmap before the competition heats up.
- **CTA:** Get Access

## 3. Influencer Outreach (The "Quiet" Strategy)
**Target Influencer Type:** Niche educators with 10k-50k followers (High Engagement).
**DM Script Template:**
"Hey [Name], I've been following your content on [Topic] and love your perspective on [Recent Post]. I've just released a professional PDF guide on {topic} that resonates perfectly with your audience. I'd love to send you a copy and talk about a partnership that provides massive value to your followers. Let me know if you're open to it!"

## 4. Launch Timeline (The "Agile" Method)
- **Day 1:** Set up Selar listing and test download link.
- **Day 2:** Launch Meta Ads with $10-$20/day test budget.
- **Day 3-14:** Post daily organic hooks on TikTok/Reels using the "Chapter Highlights" method.
- **Ongoing:** Reach out to 5 influencers/day.
"""
    
    filename = f"marketing_plan_{topic.lower().replace(' ', '_').replace('\'', '')}.md"
    filepath = os.path.join("output", filename)
    
    os.makedirs("output", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(plan)
    
    console.print(f"[bold blue]High-Conversion Marketing plan saved to:[/bold blue] {filepath}")

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "Modern Digital Assets"
    niche = sys.argv[2] if len(sys.argv) > 2 else "Digital Products"
    generate_marketing_plan(topic, niche)
