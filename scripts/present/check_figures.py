"""Check the built deck against figures.json.

Usage: uv run python scripts/present/check_figures.py   (after `npm run build` in web/)

Fails on: a data-fig whose text differs from figures.json; a figure without a tag
right after it; any numeral in slide text outside a figure, a tag, speaker notes
or an element marked data-literal (dates, "90-day", chart axes drawn from data).
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "web" / "dist" / "present" / "index.html"
FIGS = json.loads((ROOT / "web" / "public" / "data" / "figures.json").read_text())
VOID = {"img", "br", "hr", "meta", "link", "input", "source", "line", "rect", "polygon", "polyline", "circle", "path"}


class Deck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, skip_reason or None, opens the stage)
        self.fig = None  # [id, text]
        self.expect_tag = None
        self.errors, self.n_figs = [], 0

    def skipping(self):
        return next((r for _, r, _ in reversed(self.stack) if r), None)

    def in_stage(self):
        return any(st for _, _, st in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        reason = None
        if tag in ("script", "style") or (tag == "aside" and "notes" in cls) or "data-literal" in a:
            reason = "skip"
        elif "data-fig" in a:
            reason = "fig"
            self.fig = [a["data-fig"], ""]
        elif "tag" in cls:
            reason = "tag"
            self.expect_tag = None
        if tag not in VOID:
            self.stack.append((tag, reason, "stage" in cls))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, r, _ = self.stack.pop()
            if r == "fig" and self.fig:
                fid, text = self.fig
                self.n_figs += 1
                if fid not in FIGS:
                    self.errors.append(f"unknown figure id {fid!r}")
                elif text.strip() != FIGS[fid]["display"]:
                    self.errors.append(f"{fid}: page shows {text.strip()!r}, figures.json has {FIGS[fid]['display']!r}")
                self.expect_tag = fid
                self.fig = None
            if t == tag:
                break

    def handle_data(self, data):
        if not self.in_stage():
            return
        reason = self.skipping()
        if reason == "fig" and self.fig:
            self.fig[1] += data
            return
        if reason:
            return
        if self.expect_tag and data.strip():
            self.errors.append(f"{self.expect_tag}: figure has no tag")
            self.expect_tag = None
        if re.search(r"\d", data):
            self.errors.append(f"hand-typed numeral outside a figure: {data.strip()[:80]!r}")


def main():
    if not HTML.exists():
        sys.exit(f"{HTML} not found: run `npm run build` in web/ first")
    p = Deck()
    p.feed(HTML.read_text())
    if p.expect_tag:
        p.errors.append(f"{p.expect_tag}: figure has no tag")
    print(f"{p.n_figs} figures checked")
    for e in p.errors:
        print("FAIL", e)
    sys.exit(1 if p.errors else 0)


if __name__ == "__main__":
    main()
