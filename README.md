# The war dead and the rise of Labour

Did places that lost more men in the First World War swing harder to Labour in 1918 and the 1920s? Names on community war memorials, counted once per place, set against every Great Britain constituency result from 1906 to 1924, with an analysis plan written before any model of the vote was run.

**Interactive version:** https://maps.tristanhotham.com/war-dead-labour/

**Paper and archived release:** https://doi.org/10.5281/zenodo.24092044

**Blog post:** https://blog.tristanhotham.com/2026/10/31/war-dead-labour/

A data study by Dr Tristan Hotham (Independent researcher).

## Headline results

- 717,287 First World War names on community memorials in 17,689 places in Great Britain, placed with every seat from 1906 to 1924 in 176 county and borough units. The typical unit had 44 names per 1,000 voters of 1918.
- Labour's share in contested seats rose from 6.8% (December 1910) to 23.8% (1918). For each standard deviation (22 per 1,000) more memorial names, Labour's gain was 2.9 points smaller (95% CI 0.1 to 5.7; p = 0.040; Holm-adjusted across four primary outcomes p = 0.16; N = 131 units). Within-region permutation p = 0.027. Not conventionally significant after correction for four outcomes: treat as suggestive.
- The gap widened to 4.8 points by 1922 (CI 2.1 to 7.4), when the Liberals did 4.4 points better; 2.7 points by 1924.
- Six pre-war placebo tests (1906 to 1910 and January to December 1910 changes, 1910 levels) show no association.
- All 21 robustness variants give negative estimates; only 8 have 95% intervals excluding zero (one of these, the coverage restriction, drops no unit).
- Coalition (coupon) share: +3.7 points per SD (CI -1.8 to 9.2). Liberal change and turnout: no association.
- Exploratory: where Labour stood in 1918, the association nearly vanishes (-1.0, CI -3.5 to 1.5); much of it runs through where Labour fielded candidates.
- Correlational: losses tracked enlistment, which tracked occupation (miners and munitions workers were often kept at home); no industry data are available here.

Every number is in `data/results.json`, from which the page, paper, blog, collage and this README are built.

## Files

| Path | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive map and essay (MapLibre, OpenFreeMap Positron). |
| `header.png` | Social card (1200 by 630). |
| `data/units.csv` | One row per unit (176): memorial names, places, electorate, density, vote shares by party family for 1906 to 1924, outcomes. |
| `data/seats.csv` | One row per 1918 seat or merged divided borough (464), with memorial names linked by nearest seat. |
| `data/seats_1918.csv` | Every 1918 Great Britain seat with its unit, seat group, derived electorate and shares. |
| `data/lad_to_unit.csv` | Local authority district (Dec 2023) to unit, county, nation and region. |
| `data/link_checks.json` | Linkage validation counts and failure cases. |
| `data/map_*.json`, `data/site.json` | Page data (units, memorial places, 1918 seats). |
| `data/results.json` | Every number used anywhere. |
| `code/` | Numbered pipeline: `01_units.py`, `02_link.py`, `03_build.py`, `04_models.py`, `05_results.py`, `06_figures.py`, `07_build_site.py`, `08_paper.py`, `09_release.py`, `10_readme.py`, plus `qa.js`. |
| `NOTES.md` | The analysis plan (written first), amendments, results log and the verified reference list. |
| `release/paper/` | Paper (LaTeX source and PDF) and its figures; `cover_note.md` with suggested journals. |
| `release/blog/` | Blog post (WordPress block markup), figures and meta. |
| `release/zenodo/` | Paper PDF, data and code zip, Zenodo metadata. |
| `reddit/` | Collage (`collage.py` and PNG) and post text. |

## Method in brief

- **Memorial names.** From the War Memorials Register compilation: for each place, the community memorial with the most names of the dead (a church memorial if no community memorial gives a count), so each man is counted once per place.
- **Units.** No digital boundaries exist for 1910 or 1918 seats, so seats and memorials are placed in a common geography: English metropolitan districts, London boroughs and unitary authorities, the rest of each ceremonial county, Welsh preserved counties and Scottish council areas. Seats go in by their point (nudged display points are moved back to their anchor place), memorials by their own coordinates.
- **Electorates** are derived from votes cast and turnout; uncontested seats take the median of contested seats (13.8% of the 1918 electorate imputed).
- **Exposure:** names per 1,000 electors of 1918. 18 big towns and London boroughs with no city-wide roll in the register (below 10 per 1,000) are excluded from the main models and restored as a check.
- **Model:** OLS on units, region fixed effects, log density and December 1910 Labour and Liberal shares, HC3 standard errors.
- **Linkage validation:** 337 of 365 places sharing a name with a nearby borough seat go to that seat (92.3%), 97.0% to its unit; register county agrees with the unit for 92.0% of places.

## How to rerun

```
python3 code/01_units.py && python3 code/02_link.py && python3 code/03_build.py && python3 code/04_models.py
python3 code/05_results.py && python3 code/06_figures.py && python3 reddit/collage.py
python3 code/07_build_site.py && python3 code/08_paper.py && python3 code/10_readme.py && python3 code/09_release.py
```

Input paths are at the top of `code/common.py` (the war-memorials and elections-since-1832 repositories' `data/` folders and ONS boundaries). Needs Python 3 with pandas, geopandas, statsmodels, matplotlib and Pillow, and xelatex with TeX Gyre Pagella and Inter. Set `DOI=10.5281/zenodo.N` before `08_paper.py` to print the DOI in the paper.

## Sources and licences

- War memorials: Imperial War Museums, War Memorials Register, https://www.iwm.org.uk/memorials, reused under the IWM Non-Commercial Licence with credit (contains information from the IWM War Memorials Register), via https://github.com/Tristan-Hotham/war-memorials (doi:10.5281/zenodo.23727151).
- Elections: https://github.com/Tristan-Hotham/elections-since-1832 (doi:10.5281/zenodo.23761425), results from the UK Parliament general election file, matched to Wikidata. Contains Parliamentary information licensed under the Open Parliament Licence v3.0.
- Boundaries: ONS local authority districts and counties, Open Government Licence v3.0.
- Base map: OpenFreeMap Positron, OpenStreetMap contributors (ODbL).

Text, figures and derived data: CC BY-NC 4.0 (because of the register's terms). Code: MIT (see `LICENSE`).

## Citation

Hotham, T. (2026) The War Dead and the Rise of Labour: First World War Memorial Names and the British Vote, 1910 to 1924. Zenodo. https://doi.org/10.5281/zenodo.24092044

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
