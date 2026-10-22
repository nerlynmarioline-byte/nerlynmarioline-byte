#!/usr/bin/env python3
"""Kartu statistik GitHub bertema maroon (assets/stats.svg), diperbarui harian oleh workflow.

Pakai:
    GITHUB_TOKEN=... python scripts/generate_stats.py
    python scripts/generate_stats.py --sample
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ASSETS, SANS, SERIF, esc, fetch_user, sample_user  # noqa: E402

W, H = 1000, 250
BAR_X, BAR_W = 610, 280
LANG_COLORS = ["#ffd6de", "#ffb3c1", "#ff8fa6", "#ff7f9c", "#ff5c7c"]


def collect(user):
    cc = user["contributionsCollection"]
    repos = user["repositories"]["nodes"]
    langs = Counter()
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    total_size = sum(langs.values()) or 1
    top = [(name, size / total_size * 100) for name, size in langs.most_common(5)]
    return {
        "contrib": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": user["followers"]["totalCount"],
        "langs": top,
    }


def build(s):
    tiles = [
        ("貢献", "Contributions", s["contrib"]),
        ("コミット", "Commits", s["commits"]),
        ("プルリク", "Pull Requests", s["prs"]),
        ("リポジトリ", "Public Repos", s["repos"]),
        ("お気に入り", "Stars", s["stars"]),
        ("フォロワー", "Followers", s["followers"]),
    ]
    tile_svg = ""
    for i, (jp, en, val) in enumerate(tiles):
        col, row = i % 3, i // 3
        x, y = 40 + col * 160, 92 + row * 78
        tile_svg += (
            f'<g transform="translate({x} {y})">'
            f'<rect width="146" height="66" rx="12" fill="#ffffff" fill-opacity="0.07" stroke="#ffffff" stroke-opacity="0.18"/>'
            f'<text x="14" y="27" font-family="{SERIF}" font-size="22" font-weight="700" fill="#ffffff">{val}</text>'
            f'<text x="14" y="45" font-family="{SANS}" font-size="12" fill="#ffd0d9">{esc(jp)}</text>'
            f'<text x="14" y="58" font-family="{SANS}" font-size="10" fill="#ffd0d9" fill-opacity="0.65">{esc(en)}</text>'
            f"</g>"
        )

    lang_svg = ""
    if s["langs"]:
        for i, (name, pct) in enumerate(s["langs"]):
            y = 100 + i * 28
            w = max(6, BAR_W * pct / 100)
            lang_svg += (
                f'<text x="{BAR_X - 16}" y="{y + 12}" text-anchor="end" font-family="{SANS}" font-size="13" fill="#ffffff">{esc(name)}</text>'
                f'<rect x="{BAR_X}" y="{y}" width="{BAR_W}" height="14" rx="7" fill="#ffffff" fill-opacity="0.1"/>'
                f'<rect class="bar" x="{BAR_X}" y="{y}" width="{w:.1f}" height="14" rx="7" fill="{LANG_COLORS[i % 5]}" style="animation-delay:{i * 0.15:.2f}s"/>'
                f'<text x="{BAR_X + BAR_W + 12}" y="{y + 12}" font-family="{SANS}" font-size="12" fill="#ffd0d9">{pct:.1f}%</text>'
            )
    else:
        lang_svg = f'<text x="{BAR_X}" y="130" font-family="{SANS}" font-size="14" fill="#ffd0d9">Belum ada data bahasa</text>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Statistik GitHub">
<title>Statistik GitHub</title>
<style>
  .bar {{ transform-box: fill-box; transform-origin: left center; animation: grow 9s ease-out infinite; }}
  @keyframes grow {{ 0% {{ transform: scaleX(0); }} 12% {{ transform: scaleX(1); }} 100% {{ transform: scaleX(1); }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b0610"/><stop offset="1" stop-color="#6d1226"/></linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <text x="940" y="236" text-anchor="end" font-family="{SERIF}" font-size="170" fill="#ffffff" fill-opacity="0.05">統</text>
  <text x="40" y="46" font-family="{SERIF}" font-size="24" font-weight="700" fill="#ffffff" letter-spacing="3">統計</text>
  <text x="104" y="46" font-family="{SANS}" font-size="14" fill="#ffd0d9" letter-spacing="2">GITHUB STATS · UPDATED DAILY</text>
  <rect x="40" y="58" width="56" height="3" rx="1.5" fill="#ff8fa6"/>
  <text x="{BAR_X - 70}" y="82" font-family="{SANS}" font-size="13" fill="#ffd0d9" letter-spacing="2">言語 · TOP LANGUAGES</text>
  {tile_svg}
  {lang_svg}
</g>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="21" fill="none" stroke="#ff8fa6" stroke-opacity="0.35" stroke-width="3"/>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="pakai data contoh (tanpa token)")
    ap.add_argument("--out", default=str(ASSETS / "stats.svg"))
    args = ap.parse_args()
    user = sample_user() if args.sample else fetch_user()
    Path(args.out).write_text(build(collect(user)), encoding="utf-8")
    print(f"OK -> {args.out}")


if __name__ == "__main__":
    main()
