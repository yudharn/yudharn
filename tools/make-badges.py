#!/usr/bin/env python3
"""Mirror the HyperCool README badges into this profile repo.

The HyperCool repo regenerates docs/badges/*.svg daily (and on release) from
shields.io, with the rounded for-the-badge look. Copying those files here
keeps the profile badges identical to the module's badges, without calling
shields.io a second time. An invalid or missing source badge is skipped, so a
temporary shields.io problem never replaces a good badge with "INVALID".
"""

import pathlib
import sys
import urllib.error
import urllib.request

BASE = "https://raw.githubusercontent.com/yudharn/HyperCool/master/docs/badges"
NAMES = ("downloads", "stars", "android", "release")
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "hypercool-profile-badges"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for name in NAMES:
        url = "%s/%s.svg" % (BASE, name)
        try:
            svg = fetch(url)
        except (urllib.error.URLError, OSError) as exc:
            print("skip %s: %s" % (name, exc), file=sys.stderr)
            skipped += 1
            continue

        if "<svg" not in svg or "INVALID" in svg.upper():
            print("skip %s: source badge is not valid" % name, file=sys.stderr)
            skipped += 1
            continue

        path = OUT / ("badge-" + name + ".svg")
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == svg:
            print("%s is current" % path.name)
            continue

        path.write_text(svg, encoding="utf-8")
        written += 1
        print("wrote %s" % path.name)

    if not written and not skipped:
        print("all badges are current")
    elif skipped:
        print("%d badge(s) left untouched" % skipped, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
