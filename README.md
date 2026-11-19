[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/meongs123/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/meongs123/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

# The World in One Page — Thursday 19 November 2026

One image that sums up the world's news of Thursday 19 November 2026, as an
editorial front page for the make.fun news-image competition: masthead with the
date and story count, region and field bars, a day-in-numbers strip, 13
illustrated lead cards, a numbered world map, 8 more briefs, a DATE CHECK box
naming what was deliberately left out, and a source line. 21 stories,
6 regions, 8 fields, 13 illustrated.

## How it is made

`compose.py` draws the whole page with PIL (Noto fonts, system install): no
photos, no AI images, no network — every illustration, map shape and letter is
drawn here from code, so the output is fully deterministic (identical bytes on
every run). `main.ts` (Node standard library only) copies the committed
`entry.png` to `/output/entry.png` for the grader.

```sh
python3 compose.py        # writes entry.png (1024x1024 PNG, <1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Stories (all verified against real reporting)

Leads: Iran strikes US bases in Kuwait and Bahrain; Trump, Xi and Putin meet
at APEC in Shenzhen; Jensen Huang steps down at Nvidia; Jeffries is nominated
as the first Black Speaker; the EU proposes a €45bn loan for Kyiv; Gaza
flooding displaces 46,000 households; Cyclone Akvan nears India's east coast;
Houthis seize the Red Sea coast; Estonia shuts its Russia road border;
GTA VI rolls out worldwide; Amazon pledges $7bn for India renewables; Libya
seizes a record drug haul; Liu Yunping takes the Caucus chair.

Briefs: Voyager 1 reaches one light-day out; Zelensky's Starshield plea; the
NSA outage (CNN); Carney's China ties; Melenchon's possible win; Saudi
all-clear; the Earth's missing-billion-years study; the Coalition of the
Willing meets in Berlin.

DATE CHECK (deliberately left out — first reported 18 November, not today):
Bangladesh wage protests shutting 55 factories; Australia sanctioning settler
leader Daniella Weiss; the Pew projection that Muslims could outnumber
Christians by 2035; the Fed minutes, released 18 November.

Field tally, counted from the 21 stories: War & security 6, Politics &
diplomacy 5, Economy & labour 1, Society & culture 1, Disasters & weather 2,
Tech 2, Climate & space 3, Justice 1.
