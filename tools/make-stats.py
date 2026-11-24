#!/usr/bin/env python3
"""Build a dark GitHub stats card for the profile README.

The card deliberately follows the profile badges instead of the usual
purple/blue stats-card look: #2d333b / #3d444d panels, white values and
rounded corners. It is regenerated from the GitHub API by the stats workflow.
"""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LOGIN = "yudharn"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "github-stats.svg"
API = "https://api.github.com"
GRAPHQL = API + "/graphql"
UA = "yudharn-profile-stats"


def request_json(url: str, token: str | None = None, payload: dict | None = None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": UA,
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp)


def search_total(kind: str, token: str) -> int:
    query = urllib.parse.urlencode({"q": f"author:{LOGIN} is:{kind}", "per_page": 1})
    return int(request_json(API + "/search/issues?" + query, token)["total_count"])


def search_commits(token: str) -> int:
    query = urllib.parse.urlencode({"q": f"author:{LOGIN}", "per_page": 1})
    return int(request_json(API + "/search/commits?" + query, token)["total_count"])


def fmt(value: int) -> str:
    return f"{value:,}"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def color_for(count: int) -> str:
    if count <= 0:
        return "#21262d"
    if count < 10:
        return "#2d333b"
    if count < 25:
        return "#3d444d"
    if count < 50:
        return "#6e7681"
    return "#c9d1d9"


def tile(x: int, y: int, label: str, value: str) -> str:
    return f"""<g transform="translate({x} {y})" clip-path="url(#tile-clip)">
  <rect width="163" height="62" fill="#2d333b"/>
  <rect x="101" width="62" height="62" fill="#3d444d"/>
  <text x="12" y="25" fill="#adbac7" font-size="9.5" letter-spacing=".6">{esc(label)}</text>
  <text x="132" y="40" text-anchor="middle" fill="#f0f6fc" font-size="20" font-weight="bold">{esc(value)}</text>
</g>"""


def render(data: dict) -> str:
    weeks = data["weeks"]
    updated = datetime.now(timezone.utc).strftime("%b %d, %Y").upper()
    heat = []
    for wi, week in enumerate(weeks[:53]):
        for day in week["contributionDays"]:
            wd = int(day.get("weekday", 0))
            heat.append(
                f'<rect x="{36 + wi * 16}" y="{292 + wd * 16}" width="14" height="14" '
                f'rx="3" fill="{color_for(int(day["contributionCount"]))}"/>'
            )

    legend_colors = ["#21262d", "#2d333b", "#3d444d", "#6e7681", "#c9d1d9"]
    legend = []
    for i, color in enumerate(legend_colors):
        legend.append(
            f'<rect x="{74 + i * 14}" y="423" width="10" height="10" rx="2" fill="{color}"/>'
        )

    stats = [
        ("CONTRIBUTIONS", fmt(data["contributions"])),
        ("PUBLIC REPOS", fmt(data["public_repos"])),
        ("TOTAL STARS", fmt(data["stars"])),
        ("COMMITS", fmt(data["commits"])),
        ("CONTRIBUTED TO", fmt(data["contributed_to"])),
        ("CURRENT STREAK", fmt(data["current_streak"])),
        ("LONGEST STREAK", fmt(data["longest_streak"])),
        ("PULL REQUESTS", fmt(data["pull_requests"])),
        ("ISSUES", fmt(data["issues"])),
        ("JOINED", str(data["joined_year"])),
    ]
    tiles = []
    for i, (label, value) in enumerate(stats):
        row, col = divmod(i, 5)
        tiles.append(tile(28 + col * 175, 104 + row * 74, label, value))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="920" height="480" viewBox="0 0 920 480" role="img" aria-labelledby="stats-title stats-desc" font-family="Verdana, Geneva, DejaVu Sans, sans-serif" text-rendering="geometricPrecision">
<title id="stats-title">Yudharn GitHub stats</title>
<desc id="stats-desc">GitHub contributions, repositories, stars, commits, pull requests, issues and streaks.</desc>
<defs><clipPath id="tile-clip"><rect width="163" height="62" rx="8"/></clipPath></defs>
<rect x=".5" y=".5" width="919" height="479" rx="16" fill="#0d1117" stroke="#30363d"/>

<rect x="28" y="28" width="40" height="40" rx="8" fill="#2d333b"/>
<g transform="translate(36 36)" fill="#f0f6fc">
  <path d="M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2.2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1.1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .3z"/>
</g>
<text x="80" y="45" fill="#f0f6fc" font-size="19" font-weight="bold" letter-spacing="1.4">YUDHARN</text>
<text x="80" y="64" fill="#8b949e" font-size="10.5">@{LOGIN} · GitHub snapshot</text>
<text x="892" y="42" text-anchor="end" fill="#8b949e" font-size="8.5" letter-spacing="1.2">UPDATED</text>
<text x="892" y="58" text-anchor="end" fill="#c9d1d9" font-size="10">{updated}</text>
<rect x="28" y="86" width="864" height="1" fill="#30363d"/>

{''.join(tiles)}

<text x="28" y="276" fill="#f0f6fc" font-size="11" font-weight="bold" letter-spacing="1.2">CONTRIBUTION ACTIVITY</text>
<text x="892" y="276" text-anchor="end" fill="#8b949e" font-size="9" letter-spacing=".8">LAST 12 MONTHS</text>
{''.join(heat)}
<text x="36" y="432" fill="#6e7681" font-size="8.5" letter-spacing=".8">LESS</text>
{''.join(legend)}
<text x="150" y="432" fill="#6e7681" font-size="8.5" letter-spacing=".8">MORE</text>
<text x="892" y="432" text-anchor="end" fill="#adbac7" font-size="9">{fmt(data["contributions"])} CONTRIBUTIONS</text>
<rect x="28" y="446" width="864" height="1" fill="#21262d"/>
<text x="28" y="466" fill="#6e7681" font-size="8.5" letter-spacing=".5">GENERATED FROM THE GITHUB API</text>
<text x="892" y="466" text-anchor="end" fill="#8b949e" font-size="9">github.com/{LOGIN}</text>
</svg>
"""


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("GITHUB_TOKEN or GH_TOKEN is required", file=sys.stderr)
        return 1

    user = request_json(f"{API}/users/{LOGIN}", token)
    repos = []
    page = 1
    while True:
        batch = request_json(
            f"{API}/users/{LOGIN}/repos?per_page=100&type=owner&page={page}", token
        )
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    graphql = request_json(
        GRAPHQL,
        token,
        {
            "query": """
                query($login: String!) {
                  user(login: $login) {
                    contributionsCollection {
                      contributionCalendar {
                        totalContributions
                        weeks { contributionDays { date contributionCount weekday } }
                      }
                    }
                    repositoriesContributedTo(first: 1, includeUserRepositories: true,
                      contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
                      totalCount
                    }
                  }
                }
            """,
            "variables": {"login": LOGIN},
        },
    )
    node = graphql["data"]["user"]
    calendar = node["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in calendar["weeks"]:
        for item in week["contributionDays"]:
            days.append((date.fromisoformat(item["date"]), int(item["contributionCount"])))
    days.sort()
    by_date = {day: count for day, count in days}

    current_streak = 0
    cursor = days[-1][0]
    while by_date.get(cursor, 0) > 0:
        current_streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 0
    run = 0
    previous = None
    for day, count in days:
        if count > 0:
            run = run + 1 if previous and day == previous + timedelta(days=1) else 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0
        previous = day

    data = {
        "contributions": int(calendar["totalContributions"]),
        "public_repos": int(user["public_repos"]),
        "stars": sum(int(repo["stargazers_count"]) for repo in repos),
        "commits": search_commits(token),
        "contributed_to": int(node["repositoriesContributedTo"]["totalCount"]),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "pull_requests": search_total("pr", token),
        "issues": search_total("issue", token),
        "joined_year": user["created_at"][:4],
        "weeks": calendar["weeks"],
    }
    svg = render(data)
    if "<svg" not in svg or "INVALID" in svg.upper():
        print("refusing to write an invalid card", file=sys.stderr)
        return 1
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error {exc.code}: {exc.reason}", file=sys.stderr)
        raise SystemExit(1)
    except (urllib.error.URLError, OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"stats generation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
