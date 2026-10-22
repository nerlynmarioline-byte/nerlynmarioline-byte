"""Helper bersama untuk script generator profil (hanya pustaka standar Python)."""
import datetime
import json
import os
import random
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
USER = os.environ.get("GITHUB_USER", "nerlynmarioline-byte")

SANS = "'Segoe UI','Yu Gothic','Hiragino Sans','Noto Sans JP','Noto Sans CJK JP',sans-serif"
SERIF = "'Yu Mincho','Hiragino Mincho ProN','Noto Serif JP','Noto Serif CJK JP',Georgia,serif"

PETAL = "M0 0 C-5 -7 -12 -3 -9 4 C-7 8 -2 9 0 6 C2 9 7 8 9 4 C12 -3 5 -7 0 0Z"
<<<<<<< HEAD
PETAL_COLORS = ["#f3c4cd", "#e58a9d", "#e9a0ae", "#f6d3d9", "#d9677f"]
=======
PETAL_COLORS = ["#ffc2cf", "#ff9db3", "#f7a8b8", "#ffd6de", "#ff7f9c"]
>>>>>>> 96e26ce614bfb2b1eabc03574d4f62bf15ec754e

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 6, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch_user(login=USER):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN belum di-set (atau jalankan dengan --sample).")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-readme-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        raise SystemExit(json.dumps(data["errors"], indent=2))
    return data["data"]["user"]


def sample_user():
    """Data contoh (dipakai untuk --sample / aset awal sebelum workflow pertama jalan)."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=364)
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)  # mundur ke hari Minggu
    hits = {10: 1, 11: 1, 240: 1, 246: 2, 300: 1, 349: 2, 351: 1}
    weeks, day, total = [], start, 0
    while day <= today:
        days = []
        for _ in range(7):
            if day > today:
                break
            n = hits.get((day - start).days, 0)
            total += n
            days.append({"date": day.isoformat(), "contributionCount": n, "weekday": (day.weekday() + 1) % 7})
            day += datetime.timedelta(days=1)
        weeks.append({"contributionDays": days})
    return {
        "name": "Nadia Refnita Putri Batuallo",
        "followers": {"totalCount": 0},
        "repositories": {
            "totalCount": 3,
            "nodes": [
                {"stargazerCount": 0, "languages": {"edges": [{"size": 7000, "node": {"name": "HTML"}}]}},
                {"stargazerCount": 0, "languages": {"edges": [{"size": 3000, "node": {"name": "CSS"}}]}},
            ],
        },
        "contributionsCollection": {
            "totalCommitContributions": total,
            "totalIssueContributions": 0,
            "totalPullRequestContributions": 0,
            "contributionCalendar": {"totalContributions": total, "weeks": weeks},
        },
    }


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def petals(n, w, h, opacity=0.8, smin=0.5, smax=1.1, seed=7):
    """Kelopak sakura jatuh (SMIL). Seed tetap supaya output stabil dan tidak bikin commit harian."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x0 = rnd.uniform(-20, w)
        drift = rnd.uniform(-120, 60)
        dur = rnd.uniform(9, 17)
        begin = -rnd.uniform(0, dur)
        s = rnd.uniform(smin, smax)
        col = rnd.choice(PETAL_COLORS)
        sway = rnd.uniform(14, 34)
        sdur = rnd.uniform(3, 5.5)
        rdur = rnd.uniform(4, 9)
        spin = rnd.choice([360, -360])
        out.append(
            f'<g opacity="{opacity}">'
            f'<animateTransform attributeName="transform" type="translate" values="{x0:.0f},-30;{x0 + drift:.0f},{h + 30}" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="translate" values="0,0;{sway:.0f},0;{-sway:.0f},0;0,0" dur="{sdur:.1f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="{spin}" dur="{rdur:.1f}s" repeatCount="indefinite"/>'
            f'<path d="{PETAL}" transform="scale({s:.2f})" fill="{col}"/></g></g></g>'
        )
    return "\n".join(out)
