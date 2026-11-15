#!/usr/bin/env python3
"""Regenerate assets/badge-release.svg from the latest HyperCool release."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

REPO = "yudharn/HyperCool"
API = f"https://api.github.com/repos/{REPO}/releases/latest"
OUT = Path(__file__).resolve().parent.parent / "assets" / "badge-release.svg"

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="240" height="40" viewBox="0 0 240 40" role="img" aria-label="RELEASE: {version}">
  <title>RELEASE: {version}</title>
  <defs>
    <clipPath id="clip"><rect width="240" height="40" rx="4"/></clipPath>
  </defs>
  <g clip-path="url(#clip)" shape-rendering="geometricPrecision">
    <rect width="112" height="40" fill="#3b4046"/>
    <rect x="112" width="128" height="40" fill="#8957E5"/>
    <rect x="112" width="1" height="40" fill="#ffffff" fill-opacity="0.16"/>
  </g>
  <g transform="translate(12 11) scale(0.75)">
    <path fill="#ffffff" fill-rule="evenodd" d="M21.41 11.58l-9-9A2 2 0 0 0 11 2H4a2 2 0 0 0-2 2v7c0 .53.21 1.04.59 1.41l9 9a2 2 0 0 0 2.83 0l7-7a2 2 0 0 0 0-2.83zM6.5 8A1.5 1.5 0 1 1 8 6.5 1.5 1.5 0 0 1 6.5 8z"/>
  </g>
  <g fill="#ffffff" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="12" font-weight="bold" text-rendering="geometricPrecision">
    <text x="38" y="26" letter-spacing="0.7">RELEASE</text>
    <text x="176" y="26" text-anchor="middle" letter-spacing="1.2">{version}</text>
  </g>
  <rect x="0.5" y="0.5" width="239" height="39" rx="3.5" fill="none" stroke="#000000" stroke-opacity="0.22"/>
</svg>
"""


def latest_version() -> str:
    req = urllib.request.Request(
        API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "yudharn-profile-release-badge",
        },
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)

    tag = str(data.get("tag_name", "")).strip()
    if not tag:
        raise SystemExit("Latest release has no tag_name")

    core = tag[1:] if tag.lower().startswith("v") else tag
    return "V" + escape(core.upper())


def main() -> None:
    version = latest_version()
    svg = TEMPLATE.format(version=version)

    current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if current == svg:
        print(f"Release badge already current: {version}")
        return

    OUT.write_text(svg, encoding="utf-8")
    print(f"Updated {OUT} to {version}")


if __name__ == "__main__":
    main()
