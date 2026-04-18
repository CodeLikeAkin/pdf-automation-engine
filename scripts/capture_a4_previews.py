import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def capture_pages():
    html_path = Path(r"c:\Users\Trade\Desktop\AI\Routing\pdf-automation-engine\output\taming_the_silent_killer\taming_the_silent_killer.debug.html")
    output_dir = html_path.parent / "a4_previews"
    output_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # A4 at 96 DPI
        await page.set_viewport_size({"width": 794, "height": 1123})
        
        await page.goto(f"file:///{str(html_path).replace('\\', '/')}")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2) # Wait for fonts/images
        
        # Take screenshots of the first 4 pages
        for i in range(4):
            # Scroll to page i
            await page.evaluate(f"window.scrollTo(0, {i * 1123})")
            await page.screenshot(path=str(output_dir / f"page_{i+1}.png"))
            print(f"Captured page {i+1}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_pages())
