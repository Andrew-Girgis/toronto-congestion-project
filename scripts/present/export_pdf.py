"""Print every timed slide, plus the sources slides (data-print), to one 1920x1080 PDF page each.

Usage: uv run python scripts/present/export_pdf.py [base_url]   (default http://localhost:4321)
Writes web/dist/congestion-cordon-talk.pdf and a copy in sim/out/present/.
"""

import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4321"
OUT = ROOT / "sim" / "out" / "present" / "congestion-cordon-talk.pdf"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"{BASE}/present")
        page.wait_for_timeout(1500)
        page.emulate_media(media="print")
        page.pdf(path=str(OUT), width="1920px", height="1080px", print_background=True,
                 margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        browser.close()
    dist = ROOT / "web" / "dist"
    if dist.exists():
        shutil.copy(OUT, dist / OUT.name)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
