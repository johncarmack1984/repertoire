#!/usr/bin/env python3
"""Render icons/<plugin>.svg to plugins/<plugin>/.claude-plugin/icon.png, a 1024 px square, in headless Chrome.

The plugin directory takes a square PNG of 512 to 2048 px and no SVG, so the SVGs here are the sources and
the PNGs are what each plugin ships. Set CHROME to a Chrome or Chromium binary if it isn't found.
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZE = 1024
PAGE = "<!doctype html><style>html, body {{ margin: 0 }} svg {{ display: block; width: {0}px; height: {0}px }}</style>{1}"


def chrome() -> str:
    for c in (os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome"), shutil.which("chromium")):
        if c and Path(c).exists():
            return c
    sys.exit("render.py: no Chrome found; set CHROME to its binary")


def main() -> int:
    browser = chrome()
    for svg in sorted((ROOT / "icons").glob("*.svg")):
        out = ROOT / "plugins" / svg.stem / ".claude-plugin" / "icon.png"
        if not out.parent.is_dir():
            sys.exit(f"render.py: icons/{svg.name} names no plugin")
        with tempfile.TemporaryDirectory(prefix="icon-") as tmp:
            page = Path(tmp) / "icon.html"
            page.write_text(PAGE.format(SIZE, svg.read_text()), encoding="utf-8")
            subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            f"--user-data-dir={tmp}/profile", f"--window-size={SIZE},{SIZE}", f"--screenshot={out}", page.as_uri()],
                           check=True, capture_output=True, env={"MAC_CHROMIUM_TMPDIR": tempfile.gettempdir(), **os.environ})
        w, h = struct.unpack(">II", out.read_bytes()[16:24])
        if (w, h) != (SIZE, SIZE):
            sys.exit(f"render.py: {out.relative_to(ROOT)} came out {w}x{h}, not {SIZE}x{SIZE}")
        print(f"wrote {out.relative_to(ROOT)}, {out.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
