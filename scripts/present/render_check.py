"""Screenshot every slide at 1920x1080 and 1280x720; flag overflow, overlap and console errors.

Usage: uv run python scripts/present/render_check.py [base_url]   (default http://localhost:4321)
Writes sim/out/present/<size>/slide-NN.png (gitignored).
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4321"
OUT = ROOT / "sim" / "out" / "present"

# Elements whose box must sit inside the stage and not overlap their siblings.
PROBE = """() => {
  const stage = document.querySelector('.stage').getBoundingClientRect();
  const s = document.querySelector('.slide.active');
  const sc = stage.width / 1920;
  const issues = [];
  const boxes = [...s.querySelectorAll('h1,h2,h3,p,li,.panel,.case,.callout,figure,svg,.clip,.side > div,.foot,table')]
    .filter(e => !e.closest('.notes') && e.offsetParent !== null);
  for (const e of boxes) {
    const r = e.getBoundingClientRect();
    if (r.right > stage.right + 2 || r.bottom > stage.bottom + 2 || r.left < stage.left - 2)
      issues.push(`outside stage: <${e.tagName.toLowerCase()}> "${e.textContent.trim().slice(0, 50)}"`);
    if (e.scrollHeight > e.clientHeight + 4 && getComputedStyle(e).overflow !== 'visible')
      issues.push(`clipped content: <${e.tagName.toLowerCase()}> "${e.textContent.trim().slice(0, 50)}"`);
  }
  const blocks = [...s.children].filter(e => !e.classList.contains('notes'));
  for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) {
    const a = blocks[i].getBoundingClientRect(), b = blocks[j].getBoundingClientRect();
    const ov = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (ov > 4 * sc && Math.min(a.right, b.right) > Math.max(a.left, b.left))
      issues.push(`overlap: ${blocks[i].className || blocks[i].tagName} / ${blocks[j].className || blocks[j].tagName}`);
  }
  return issues;
}"""


def main():
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in ((1920, 1080), (1280, 720)):
            page = browser.new_page(viewport={"width": w, "height": h})
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"{BASE}/present#1")
            page.wait_for_timeout(800)
            n = page.evaluate("document.querySelectorAll('.slide').length")
            out = OUT / f"{w}x{h}"
            out.mkdir(parents=True, exist_ok=True)
            for i in range(n):
                page.evaluate(f"location.hash = '#{i + 1}'; location.reload()")
                page.wait_for_timeout(600)
                # reveal every step on the slide
                for _ in range(page.evaluate("document.querySelectorAll('.slide.active [data-step]').length")):
                    page.keyboard.press("ArrowRight")
                page.wait_for_timeout(500)
                page.screenshot(path=str(out / f"slide-{i + 1:02d}.png"))
                for issue in page.evaluate(PROBE):
                    problems.append(f"{w}x{h} slide {i + 1}: {issue}")
            problems += [f"{w}x{h} console: {e}" for e in errors]
            page.close()
        browser.close()
    print(f"screenshots in {OUT.relative_to(ROOT)}")
    for x in problems:
        print("FAIL", x)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
