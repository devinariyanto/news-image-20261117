# THE WORLD ON TUESDAY — 17 NOVEMBER 2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/devinariyanto/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/devinariyanto/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117)

One image that sums up 17 November 2026's world news, drawn as a real TV
news broadcast frame (1024×576, 16:9): masthead, red breaking banner,
schematic main picture, headline rail, lead lower-third, and a ticker.
Everything is drawn in code with PIL — no copyrighted photos.

## The six stories

1. **KERCH BRIDGE HIT AGAIN** — Ukraine strikes Crimea bridge; Russia strikes Kyiv bridges.
2. **TANKERS STRUCK NEAR HORMUZ** — Mine hits tankers; third US carrier arrives.
3. **XI, TRUMP, PUTIN SUMMIT SET** — First three-way summit, Thursday in Shenzhen.
4. **JPMORGAN OUTAGE HITS ONLINE BANKING** — Glitch hits online banking; Zelle affected.
5. **PENTAGON FAILS NINTH STRAIGHT AUDIT** — Ninth straight year; $4.8 trillion unverified.
6. **EUROPEAN COUNTRIES PLAN RWANDA RETURN HUB** — Five European states plan hub for rejected seekers.

The lead story (Kerch Bridge) is the biggest element on screen — about
twice the size of the rail headlines — so the eye lands on it first. The
main picture is a schematic illustration of the bridge (drawn with PIL
primitives, labelled CRIMEA, marked FILE because this is a still image,
not a live feed). The ticker carries one complete sentence about the
three-way summit.

## How it is made

- `gen_image.py` renders `entry.png` (1024×576, under 1 MiB) with PIL,
  using Noto Sans Condensed Bold for headlines (DejaVu Sans Bold as
  fallback) and Noto Sans Condensed Medium for supporting lines.
- `main.py` (stdlib only, no network, deterministic) validates `entry.png`
  — PNG magic + per-chunk CRC + IHDR/IDAT/IEND with an inflate check and
  no trailing bytes after IEND, or JPEG markers up to EOI with no trailing
  bytes — then copies it byte-for-byte to the output directory.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs produce byte-identical output. Re-render the image with:

```sh
python3 gen_image.py
```

<sub>Entered on [make.fun](https://make.fun/?ref=ghm74v3k&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
