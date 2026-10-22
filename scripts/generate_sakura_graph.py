#!/usr/bin/env python3
"""Sakura Bloom: grafik kontribusi bertema sakura dengan animasi looping.

Setiap kotak kontribusi jadi bunga sakura (makin banyak kontribusi, makin besar).
Gelombang "mekar" menyapu dari kiri ke kanan, lalu berhenti sebentar, lalu ulang terus.

Pakai:
    GITHUB_TOKEN=... python scripts/generate_sakura_graph.py
    python scripts/generate_sakura_graph.py --sample     # data contoh, tanpa token
"""
import argparse
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ASSETS, SANS, SERIF, esc, fetch_user, petals, sample_user  # noqa: E402

W, H = 1000, 270
PITCH, CELL = 17, 13
Y0 = 96
PERIOD = 7.0           # detik per putaran loop
WAVE_STEP = 0.09       # jeda mekar antar kolom (detik)
FLOWER_COLORS = ["#ffd6de", "#ffb3c1", "#ff8fa6", "#ff5c7c"]
FLOWER_RADIUS = [0, 4.4, 5.4, 6.4, 7.4]
MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]


def build(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    cols = len(weeks)
    x0 = (W - cols * PITCH) / 2 + 2
    peak = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=0)
    rnd = random.Random(42)

    cells, month_marks = [], []
    prev_month = None
    for c, week in enumerate(weeks):
        days = week["contributionDays"]
        if not days:
            continue
        month = int(days[0]["date"][5:7])
        if month != prev_month:
            month_marks.append((c, month))
            prev_month = month
        delay = c * WAVE_STEP - PERIOD  # negatif = loop sudah berjalan sejak awal
        for d in days:
            n = d["contributionCount"]
            cx = x0 + c * PITCH + CELL / 2
            cy = Y0 + d["weekday"] * PITCH + CELL / 2
            tip = f'<title>{d["date"]}: {n} kontribusi</title>'
            if n == 0:
                cells.append(
                    f'<rect class="e" x="{cx - CELL / 2:.1f}" y="{cy - CELL / 2:.1f}" width="{CELL}" height="{CELL}" rx="3" '
                    f'fill="#ffffff" style="animation-delay:{delay:.2f}s">{tip}</rect>'
                )
            else:
                lvl = min(4, math.ceil(4 * n / peak))
                r = FLOWER_RADIUS[lvl]
                rot = rnd.randrange(0, 72)
                cells.append(
                    f'<g transform="translate({cx:.1f} {cy:.1f})"><g class="b" style="animation-delay:{delay:.2f}s">'
                    f'<use href="#f" transform="rotate({rot}) scale({r})" fill="{FLOWER_COLORS[lvl - 1]}"/>{tip}</g></g>'
                )

    # label bulan: buang label yang terlalu dekat dengan label berikutnya (biasanya bulan pertama yang parsial)
    labels = []
    for i, (c, month) in enumerate(month_marks):
        nxt = month_marks[i + 1][0] if i + 1 < len(month_marks) else cols + 10
        if nxt - c >= 3:
            labels.append(
                f'<text x="{x0 + c * PITCH:.1f}" y="{Y0 - 12}" font-family="{SANS}" font-size="11" fill="#ffd0d9" fill-opacity="0.75">{MONTHS[month - 1]}</text>'
            )

    legend_x = W - 40 - 5 * 26 - 70
    legend = f'<text x="{legend_x}" y="{H - 24}" font-family="{SANS}" font-size="11" fill="#ffd0d9" fill-opacity="0.8" text-anchor="end">少</text>'
    for i, lvl in enumerate(range(0, 5)):
        lx = legend_x + 18 + i * 26
        if lvl == 0:
            legend += f'<rect x="{lx - 6}" y="{H - 34}" width="12" height="12" rx="3" fill="#ffffff" fill-opacity="0.12"/>'
        else:
            legend += f'<use href="#f" transform="translate({lx} {H - 28}) scale({FLOWER_RADIUS[lvl] * 0.9})" fill="{FLOWER_COLORS[lvl - 1]}"/>'
    legend += f'<text x="{legend_x + 18 + 5 * 26 - 8}" y="{H - 24}" font-family="{SANS}" font-size="11" fill="#ffd0d9" fill-opacity="0.8">多</text>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Grafik kontribusi Sakura Bloom: {total} kontribusi dalam setahun terakhir">
<title>Sakura Bloom — {total} kontribusi dalam setahun terakhir</title>
<style>
  .b {{ transform-box: fill-box; transform-origin: center; animation: bloom {PERIOD}s ease-in-out infinite; }}
  .e {{ fill-opacity: .07; animation: shimmer {PERIOD}s ease-in-out infinite; }}
  @keyframes bloom {{ 0% {{ transform: scale(.62); }} 14% {{ transform: scale(1.35); }} 32% {{ transform: scale(1); }} 100% {{ transform: scale(.62); }} }}
  @keyframes shimmer {{ 0% {{ fill-opacity: .07; }} 14% {{ fill-opacity: .26; }} 34% {{ fill-opacity: .09; }} 100% {{ fill-opacity: .07; }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#2b0610"/><stop offset="1" stop-color="#6d1226"/>
  </linearGradient>
  <g id="f">
    <path d="M0 0 C-.55 -.5 -.45 -1.05 0 -1 C.45 -1.05 .55 -.5 0 0Z"/>
    <path d="M0 0 C-.55 -.5 -.45 -1.05 0 -1 C.45 -1.05 .55 -.5 0 0Z" transform="rotate(72)"/>
    <path d="M0 0 C-.55 -.5 -.45 -1.05 0 -1 C.45 -1.05 .55 -.5 0 0Z" transform="rotate(144)"/>
    <path d="M0 0 C-.55 -.5 -.45 -1.05 0 -1 C.45 -1.05 .55 -.5 0 0Z" transform="rotate(216)"/>
    <path d="M0 0 C-.55 -.5 -.45 -1.05 0 -1 C.45 -1.05 .55 -.5 0 0Z" transform="rotate(288)"/>
    <circle r=".16" fill="#7a1128"/>
  </g>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <text x="{W - 20}" y="{H - 8}" text-anchor="end" font-family="{SERIF}" font-size="190" fill="#ffffff" fill-opacity="0.05">桜</text>
  {petals(8, W, H, 0.55, 0.45, 0.9, seed=11)}
  <text x="40" y="46" font-family="{SERIF}" font-size="24" font-weight="700" fill="#ffffff" letter-spacing="3">桜の開花</text>
  <text x="160" y="46" font-family="{SANS}" font-size="14" fill="#ffd0d9" letter-spacing="2">SAKURA BLOOM</text>
  <text x="{W - 40}" y="46" text-anchor="end" font-family="{SANS}" font-size="15" fill="#ffffff">{total} kontribusi dalam setahun terakhir</text>
  <rect x="40" y="58" width="56" height="3" rx="1.5" fill="#ff8fa6"/>
  {"".join(labels)}
  {"".join(cells)}
  {legend}
</g>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="21" fill="none" stroke="#ff8fa6" stroke-opacity="0.35" stroke-width="3"/>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="pakai data contoh (tanpa token)")
    ap.add_argument("--out", default=str(ASSETS / "sakura-graph.svg"))
    args = ap.parse_args()
    user = sample_user() if args.sample else fetch_user()
    Path(args.out).write_text(build(user), encoding="utf-8")
    print(f"OK -> {args.out}")


if __name__ == "__main__":
    main()
