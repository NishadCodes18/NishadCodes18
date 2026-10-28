#!/usr/bin/env python3
"""No-op migration helper: README now uses static headers and calm GIFs."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
def main():
    # Static PNG headers intentionally replace old animated headers with floating glow dots.
    # This script does not create or move any decorative balls/orbs.
    for p in ASSETS.glob("title-*.png"):
        if not p.exists():
            raise FileNotFoundError(p)
    print("Static section headers are in place; no decorative orb animations are generated.")
if __name__ == "__main__":
    main()
