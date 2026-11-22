# Sunday 22 November 2026 — The World in One Day

A one-image broadsheet summing up the world news of Sunday 22 November 2026,
built for the make.fun bounty "Sum up 22 November's world news in one image".

[![bounty](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Robekk/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Robekk/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

`main.py` (Python 3.13, Pillow) deterministically renders `entry.png`
(1024x1024): 3 illustrated lead stories, 10 cards and 37 briefs — 50 dated
stories, a UTC timeline band and an explicit date-check box.

Run: `python3 main.py` → writes `output/entry.png`
(honours `MAKEFUN_OUTPUT_DIR` / `OUTPUT_DIR`).
