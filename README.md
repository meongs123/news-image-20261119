[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/meongs123/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/meongs123/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

# The World in One Page — Thursday 19 November 2026

One image that sums up the world's news of Thursday 19 November 2026, as an
editorial front page for the make.fun news-image competition: masthead with the
date and story count, region and field bars, a day-in-numbers strip, 13
illustrated lead cards, a numbered world map, 23 more briefs, a DATE CHECK box
naming what was deliberately left out, and a source line. 36 stories,
7 regions, 8 fields, 13 illustrated.

## How it is made

`compose.py` draws the whole page with PIL (Noto fonts, system install): no
photos, no AI images, no network — every illustration, map shape and letter is
drawn here from code, so the output is fully deterministic (identical bytes on
every run). The 7 evening-refresh lead illustrations live in `ill_new.py`
(imported by `compose.py`); the 6 kept v1 leads reuse the v1 art in
`compose.py`. `main.ts` (Node standard library only) copies the committed
`entry.png` to `/output/entry.png` for the grader.

```sh
python3 compose.py        # writes entry.png (1024x1024 PNG, <1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Stories (all verified against real reporting)

Leads (headlines and decks verbatim from the binding story sheet in
`~/workspace/makefun/news-image-20261119-concept-v2/story-sheet.md`):
Trump, Xi and Putin sign the first-ever joint declaration at APEC; the ICJ
holds Myanmar responsible for the Rohingya genocide; Netanyahu presses Trump
on Iran; Ukraine hits the Crimean Bridge a third time this week; missile
debris damages Riyadh's PIF Tower; Anthropic debuts in a record $81B IPO;
Musk regrets his $446M midterm spending; the COP31 second draft drops all
fossil-fuel references; Nvidia chief Huang steps down; the EU proposes a
€45B loan for Ukraine in 2027; Gaza flooding displaces 46,000+ households;
Cyclone Akvan nears India's east coast; Jeffries is nominated as the first
Black House Speaker.

Briefs (wording shortened from the sheet to fit one line each at the type
floor; facts kept): Houthis seize the Red Sea coast; Estonia shuts its
Russia border from 1 Dec; GTA VI rolls out worldwide; Amazon pledges $7B
for India renewables; Libya's drug haul; Liu Yunping takes the caucus
chair; Denmark ratifies the Greenland–US deal 109–0; IMF inflation 4.7%;
Bangladesh lockdown turns deadly; Garcia's 12 notices; outage-week
prepping; Colombia strike; Litton Das's world record; Congress presses
Modi; New Zealand fight back to 243/5; the Coalition of the Willing meets
in Berlin; Voyager 1 reaches one light-day; Zelensky's Starshield plea;
the NSA outage (CNN); Carney recalibrates Canada–China ties; Mélenchon
could win the presidency; Saudi all-clear; Earth's missing billion years.

DATE CHECK (deliberately left out — first reported 18 November, not today):
the Ali Al Salem attack (overnight 18 Nov); Fed minutes, released 18 Nov
14:00 ET; the Pew projection that Muslims could outnumber Christians by
2035; the Arab League statement on Israeli incursions in southern Syria
(Wed 18 Nov); the tanker hit off Khasab, Oman (16:45 UTC Wed 18 Nov); the
Van Gogh "Blossoming Chestnut Trees" sale for $190.4M (Wed 18 Nov evening).

Field tally, counted from the 36 stories: War & security 8, Politics &
diplomacy 10, Economy & labour 4, Society & culture 3, Disasters & weather 2,
Tech 3, Climate & space 4, Justice 2. Regions: Europe 6, Middle East 5,
Asia 6, Africa 1, Americas 11, Oceania 1, World 6.

## v2 notes (vs v1's 21 stories)

- v1 lead 1 (Iran strikes on US bases) is struck: an 18-Nov event, now a
  DATE CHECK item. A9+A10 combine into one illustrated Iran lead.
- The sheet's decks are verbatim full sentences, so they wrap to 2–4 lines
  at the type floor instead of v1's single line; each row's illustration
  height is computed from its longest deck (big ~99px, small ~55–58px)
  instead of the reference's 63%/54%.
- The containment probe (every illustration rendered alone at its v2 size)
  caught and fixed 5 out-of-box drawing bugs, including 3 latent in v1's
  art (Akvan spiral, EU star circle, Gaza wave rows) that bled above or
  below the illustration at the shorter heights.
