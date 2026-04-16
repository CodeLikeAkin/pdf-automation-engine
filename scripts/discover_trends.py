import httpx
import asyncio
from rich.console import Console
from rich.table import Table
import sys
import random

console = Console()

# Niche-specific keyword bank for exploration
NICHES = {
    "Parenting": ["new moms", "sleep training", "toddler meals", "gentle parenting", "baby development"],
    "Fitness": ["at-home workouts", "muscle building for busy dads", "glute training", "anti-aging exercise", "hybrid training"],
    "Money": ["passive income ideas", "stock market for beginners", "credit repair", "freelancing mastery", "real estate flipping"],
    "Self Improvement": ["overcoming procrastination", "introvert networking", "productivity hacks", "anxiety management", "manifestation"]
}

async def get_trends(niche="Money", market="Global"):
    """
    Fetches trending topics with Opportunity Scores and Volume data.
    Simulates the Search-Data-Driven discovery used by pro PDF guide makers.
    """
    console.print(f"[bold blue]Analyzing {market} Trends for:[/bold blue] {niche}")
    
    # In production, use SerpApi or Google Trends
    # Here we simulate the logic: Opportunity = (Volume / Competition) * TrendFactor
    
    keywords = NICHES.get(niche, ["digital assets", "online business"])
    trends = []
    
    for kw in keywords:
        volume = random.randint(5000, 25000)
        competition = random.choice(["Low", "Medium", "High"])
        
        # Calculate Opportunity Score (0-100)
        comp_multiplier = {"Low": 1.2, "Medium": 0.8, "High": 0.4}
        score = int((volume / 250) * comp_multiplier[competition])
        score = min(max(score, 40), 98) # Clamp between 40 and 98
        
        trends.append({
            "topic": f"How to: {kw.title()}",
            "relevance": "Top Tier" if score > 75 else "Relevant",
            "volume": f"{volume:,}/mo",
            "competition": competition,
            "opportunity": score
        })
    
    # Sort by Opportunity Score
    trends.sort(key=lambda x: x["opportunity"], reverse=True)
    return trends

def display_trends(trends):
    table = Table(title="[bold gold1]PDF Guide Opportunity Report[/bold gold1]")
    table.add_column("Proposed Title", style="cyan", no_wrap=True)
    table.add_column("Monthly Volume", style="magenta")
    table.add_column("Competition", style="yellow")
    table.add_column("Opp. Score", style="bold green" if trends[0]["opportunity"] > 70 else "white")

    for t in trends:
        score_color = "green" if t["opportunity"] > 70 else "yellow" if t["opportunity"] > 60 else "white"
        table.add_row(
            t["topic"], 
            t["volume"], 
            t["competition"], 
            f"[{score_color}]{t['opportunity']}[/{score_color}]"
        )

    console.print(table)
    if trends[0]["opportunity"] > 70:
        console.print(f"\n[bold green]WINNER DETECTED:[/bold green] '{trends[0]['topic']}' is a high-opportunity search term.")

async def main():
    niche = sys.argv[1] if len(sys.argv) > 1 else "Money"
    market = sys.argv[2] if len(sys.argv) > 2 else "Global"
    
    if niche not in NICHES:
        console.print(f"[yellow]Note: Niche '{niche}' not in pre-defined bank. Using generic search logic.[/yellow]")
        
    trends = await get_trends(niche, market)
    display_trends(trends)

if __name__ == "__main__":
    asyncio.run(main())
