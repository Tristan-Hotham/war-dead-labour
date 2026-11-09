# war-dead-labour: working notes

Brief: /home/claude/work/new11/BRIEFS.md section 4, plus shared rules (new8, new9, new10 BRIEFS tops) and /home/claude/newdata/BRIEF.md.
Format refs: /home/claude/studies/battle-moons, /home/claude/studies/sea-sunsets.
Scratch: /home/claude/scratch/war-dead-labour (delete at end).
Licence note: the IWM War Memorials Register is reused on non-commercial terms, so (like the source study war-memorials)
derived memorial data and text are CC BY-NC 4.0; code MIT. Election data from elections-since-1832 (Wikidata/Wikipedia derived).

## ANALYSIS PLAN (written 2026, before any outcome model was run or any outcome tabulated against exposure)

### Question
Did places that lost more men in the First World War vote differently in 1918 and the early 1920s: a larger swing to
Labour, a larger Coalition (coupon) vote, a larger Liberal collapse?

### Hypotheses (two-sided; the literature points both ways)
- H1 (grievance / radicalisation): higher war losses -> larger Labour gain from December 1910 to 1918 (and to 1922).
- H2 (patriotic rally / "khaki" vote): higher war losses -> higher Coalition (coupon) share in 1918.
- H3 (Liberal collapse): higher war losses -> larger fall in the Liberal (all Liberal) share from Dec 1910 to 1918.
- H4 (turnout): higher losses -> lower 1918 turnout (absent and dead men's households; mechanical and demobilisation
  effects). Secondary.
Evidence against H1: a Labour coefficient whose 95% CI excludes a substantively meaningful positive effect
(meaningful = 1 percentage point of Labour share per SD of exposure), or a placebo (pre-war) coefficient of similar size,
which would show the exposure measures place character rather than war loss.

### Units of analysis
Main: "county units" built from points, because there are no 1918 boundary files: modern geography used only as a common
container for both memorials and constituency points.
- England: each metropolitan district (E08), London borough (E09) and unitary authority (E06) is its own unit
  (approximating county boroughs and the London metropolitan boroughs); the rest of each ceremonial county is one unit.
- Wales: the eight preserved counties. Scotland: council areas. Ireland/Northern Ireland, Isle of Man, Channel Islands,
  university seats: excluded (Irish politics in 1918 is a different contest; memorial coverage of NI is thin).
- Constituency points (1918, Dec 1910, Jan 1910, 1906, 1922, 1923, 1924) and memorial places are assigned to units by
  point in polygon; points falling in units with no 1918 constituency point are moved to the unit of the nearest 1918
  constituency point (so every memorial place counts somewhere).
Robustness: constituency level (1918 seats; divided boroughs merged into one borough unit; memorial places assigned to
the nearest 1918 constituency point within the same county unit; SEs clustered by county unit).

### Exposure
Main: recorded First World War dead per 1,000 electors of 1918 in the unit = sum over memorial places in the unit of the
chosen community memorial's count (the source study's no-double-counting rule) / 1918 electorate x 1000.
Electorate = votes cast / turnout (for two-member seats, votes cast / 2 / turnout); uncontested seats imputed with the
median electorate of contested seats of the same nation (share imputed reported). Reported per SD and per 10 dead per
1,000 electors.
Alternatives (pre-specified sensitivity): (a) log(1 + rate); (b) percentile rank; (c) winsorised at 2nd/98th
percentiles; (d) the summed all-memorial count (double counted) per 1,000 electors; (e) median names per 1,000 modern
residents among small places (100 to 5,000) with an exact count (the source study's village rate); (f) denominator = seats
instead of electorate.

### Outcomes (votes in contested GB seats aggregated to the unit: family votes / all votes)
Primary: (O1) Labour share 1918 minus Labour share December 1910 (percentage points; Labour = LAB family, Labour with
coupon counted as Coalition). Secondary: (O2) Coalition (coupon) share 1918; (O3) all-Liberal share change Dec 1910 to
1918; (O4) turnout 1918 (votes / electorate in contested seats); (O5) Labour share 1922, 1923, 1924 minus Dec 1910;
(O6) Labour share 1918 level (with the 1910 level as a control).

### Controls (main specification)
Region fixed effects (9 English regions, Wales, Scotland); log electorate density (1918 electors per km2 of land in the
unit); Labour and Liberal shares in December 1910 (pre-war strength; included in all models; for change outcomes this
also handles regression to the mean); share of the unit's 1918 electorate in seats whose name marks a borough
(urban, as a second rurality measure; see below). No industry data exist in the inputs: noted as a limitation.
Recording control (alternative spec): Second World War recorded dead per 1,000 1918 electors (captures volunteer
recording effort and how often places put names on memorials).

### Main specification
OLS, one row per unit, unweighted, HC3 robust SEs:
  Y_u = a + b * Exposure_u (standardised) + controls + region FE + e_u.
Report b with 95% CI, N, R2. Primary test: b for O1. Multiple outcomes: report all; Holm adjustment across O1 to O4.

### Robustness (pre-specified)
1. Weighted by 1918 electorate. 2. Without the 1910 controls (and with Jan 1910 instead of Dec 1910 baseline).
3. Exposure alternatives (a) to (f). 4. Add WW2 recording control. 5. Leave one region out (11 runs) and drop London;
drop Scotland. 6. Drop units with high leverage (Cook's D > 4/N) and units where fewer than half of memorial places have a
WW1 count. 7. Constituency-level models (cluster by unit). 8. Units with at least two 1918 seats only.
9. Spatial: Conley-type check by adding a spatial lag of the outcome is NOT planned; instead region FE and leave-one-region-out.

### Placebo / falsification (pre-specified)
P1 Pre-war outcomes: exposure should not predict the Labour or Liberal change from 1906 to December 1910, or January to
December 1910. P2 Exposure placebo: WW2 recorded dead per 1,000 (cannot cause 1918 votes) as the regressor for O1 to O4.
P3 Permutation: shuffle exposure within region 2,000 times for the O1 coefficient.

### Linkage validation (pre-specified)
V1 Memorial places whose name equals the name of a single-member borough constituency (or the root of a divided borough):
share assigned (by the nearest-point rule) to that constituency. V2 For county-unit assignment, agreement between the unit
from point in polygon and the memorial's own register county (OS Open Names) where names are comparable.
V3 Hand check of a random sample of 40 memorial places against constituency assignment (by eye on names and distances).

### What would count against the hypotheses
Small, imprecise coefficients with CIs spanning zero and excluding 1 pp/SD; placebo coefficients of similar magnitude;
results that vanish when one region is dropped. A careful null is a result.

### Language
Correlational design. "Associated with", not "caused". The exposure is recorded memorial names, not deaths.

## Log
- Linkage built (02_link.py). Constituency display points in the elections data are nudged 2.5 km (town divisions) or
  15 km (county divisions) by the compass word in their name; 55 of 579 GB 1918 seats. These sent several London seats into
  the wrong borough (South West Bethnal Green into Southwark, St Pancras South East into Southwark). Fix: units are
  assigned from the un-nudged anchor point (the place the nudge started from); nearest-seat linkage keeps the nudged points.
  42 divided boroughs merged for the constituency level (464 seats or boroughs). V1: 337 of 365 same-name places within
  15 km of their namesake seat go to it (92.3%); 354 (97.0%) to its unit. V2: register county text agrees with the unit for
  14,950 of 16,255 places (92.0%; crude string test). Median place to seat point 9.9 km.
- AMENDMENT 1 (before any outcome model; decided from the exposure distribution only): the "borough share" control is
  dropped: no source in the inputs says which 1918 seats were boroughs, and names alone cannot tell (Penistone,
  Holderness are county divisions). Rurality is carried by log electorate density; a quadratic in it is added as a
  robustness check.
- AMENDMENT 2 (before any outcome model): the recorded rate has a long low tail of big towns whose city-wide roll is not
  in the register as a count (Plymouth 1.3, Portsmouth 2.1, Southwark 2.2 per 1,000 electors, against a national
  expectation near 35). These are measurement failures, not low losses. Main sample: units with a recorded rate of at
  least 10 per 1,000 electors (about a quarter of the expected level). All units: robustness. Also flagged: Leicester's
  count is the "City and County" book (county names attributed to the city unit); handled by the outlier checks.
- MAIN RESULTS (planned spec, 04_models.py, first run): O1 Labour change Dec 1910 to 1918: -2.90 pp per SD of recorded
  rate [-5.68, -0.13], p 0.040 (Holm across O1-O4 0.16), N 131; permutation within region p 0.027. O2 coalition +3.67
  [-1.83, 9.17] p 0.19; O3 Liberal -1.06 p 0.61; O4 turnout -0.45 p 0.59. Opposite sign to H1. Placebos (1906 to 1910,
  Jan to Dec 1910, 1910 levels; WW2 names as exposure) all null. Secondary O5: Labour change to 1922 -4.76 [-7.43,-2.10],
  1923 -4.58, 1924 -2.69; Liberal change +4.44 (1922). Fragile in some variants (quadratic density p 0.14, log/rank 0.11,
  without Scotland 0.11). Constituency level -2.51 p<0.01.

## References verified (WebSearch/WebFetch, 2026)
Acemoglu, De Feo, De Luca, Russo 2022 QJE 137(2):1233-1296 doi 10.1093/qje/qjac001 (RePEc lists y2023; vol 137 is 2022, Russo's page 2022);
Koenig 2023 JEH 83(1):167-202; de Juan, Haass, Koos, Riaz, Tichelbaecker 2024 APSR 118(1):144-162 doi 10.1017/S000305542300014X
(brief said "Tinnes": the fifth author is Thomas Tichelbaecker); Satyanath, Voigtlaender, Voth 2017 JPE 125(2):478-526;
Karol & Miguel 2007 JoP 69(3):633-648; Kriner & Shen 2007 LSQ 32(4):507-530; Gartner, Segura, Wilkening 1997 JCR 41(5):669-694;
Blattman 2009 APSR 103(2):231-247; Bellows & Miguel 2009 JPubE 93(11-12):1144-1157; Bauer et al. 2016 JEP 30(3):249-274;
Grossman, Manekin, Miodownik 2015 IO 69(4):981-1009; Matthew, McKibbin, Kay 1976 EHR 91:723-752; Tanner 1990 CUP;
Tanner 1991 HJ 34:893-908; McKibbin 1974 OUP; Wilson 1966 Collins; Laybourn 1995 History 80(259):207-226;
Blewett 1965 P&P 32:27-56; Clarke 1971 CUP; Pugh 1978 Routledge & Kegan Paul; Turner 1992 Yale; Kinnear 1968 Batsford;
Lawrence 2003 JMH 75(3):557-589; Winter 1977 Pop Studies 31(3):449-466; Winter 1985 Macmillan; Winter 1995 CUP;
King 1998 Berg; Gregory 1994 Berg; Gregory 2008 CUP; Dewey 1984 HJ 27(1):199-223; Simkins 1988 MUP; Pennell 2012 OUP;
Robinson 1950 ASR 15(3):351-357; King 1997 Princeton; Holm 1979 SJS 6(2):65-70; MacKinnon & White 1985 J Econometrics
29(3):305-325; Cameron & Miller 2015 JHR 50(2):317-372; Seabold & Perktold 2010 SciPy proc. 92-96.
Dropped (could not confirm): Moriarty 1995 (two records give different titles), Englander & Osborne 1978 (pages not
confirmed), "Ferguson 2019" and "Bartov" (not identified; not used). Source-study DOIs (war memorials
10.5281/zenodo.23727151; elections 10.5281/zenodo.23761425) are taken from their READMEs; Zenodo could not be fetched.
Added after search: Carozzi, Pinchbeck, Repetto 2023 "Scars of war: the legacy of WW1 deaths on civic capital and combat
motivation", CEP Discussion Paper 1940 (LSE): WW1 deaths in English parishes raised interwar turnout (closest prior work);
Steed 2015 "Did the Great War really kill the Liberal Party?" Journal of Liberal History 87:12-15.

## Final state (2026)
- Full pipeline rerun from raw inputs reproduces every number (01 to 10, collage). QA: Playwright desktop 1280 and phone 390, no console errors, no horizontal scroll, full-screen button present.
- Exploratory (labelled in paper): Labour stood in fewer seats where names were higher (-5.5 pp of seats, p 0.16); where Labour stood the coefficient is -0.99 (p 0.44).
- Journal word limits in release/paper/cover_note.md could not be verified online (search budget exhausted): check before submission.
- Memorial places layer is off by default on the map (14k dots hid the choropleth); markers have a 3 px floor when on.

## Independent review (2026)
Referee and fact-check pass (reproduction, referee checks, references, house rules). Scratch: /home/claude/scratch/review-war-dead-labour (deleted afterwards).
- Reproduction: scripts 01 to 05 rerun from the raw inputs in a scratch copy; results.json, units.csv, seats.csv, seats_1918.csv, link_checks.json and all map data are byte-identical. Every number in paper, blog, page, README, Zenodo metadata, Reddit post and collage traced to results.json.
- Pre-registration of the 10 per 1,000 exclusion: the only evidence of order is this file (Amendment 2 is logged before MAIN RESULTS); no timestamps survive, so it cannot be independently verified. It matters for precision: all units p 0.063, thresholds 5/15/20 give -2.99 (p 0.036), -2.80 (0.046), -2.21 (0.117). Now reported in the paper.
- Dropped borough control: confirmed, contests.csv has no borough/county flag (columns election, date, constituency, wikidata, seats, uncontested, candidates, turnout, votes_cast, lon, lat, nation).
- Checks added at review (exploratory, R["review"] in 04_models.py, in paper section 6.1 and Measurement): denominator = Dec 1910 electorate -2.51 (p 0.025); controlling for coverage -2.28 (p 0.098); units with no imputed 1918 electorate -3.02 (p 0.072, N 85). "cov50" variant drops no unit (it repeats the main estimate); seat_all was not in the plan. Both now flagged in the text.
- Misstatements fixed: collage title said high-loss places "did not swing to Labour" (they swung +17.6 on average, just less); election source given everywhere as "Wikidata and Wikipedia" but the results are the UK Parliament file (Open Parliament Licence v3.0), now stated with OPL attribution; "survives the removal of any one region" (only 6 of 11 runs significant); "21 pre-specified variants"; "not been tested for Britain" (Carozzi et al. 2023 tested turnout); mechanical-composition bound (could reach 2.2 of 2.9 points in 1918 in the extreme case; cannot explain 1922); blog standfirst 1910 vs 1906; "put back in, changed little"; causal phrasing in abstract and contribution softened; blog, page, Reddit and collage now say the result is suggestive (Holm p 0.16). Denominator paragraph added (1918 register shaped by war deaths, service voters, women's age and property qualification). Winter 1977 sentence now mentions medical unfitness and reserved occupations. Bib titles of the two source studies corrected. Abstract trimmed to 250 words.
- References: spot-verified online Carozzi et al. (CEP DP 1940, 2023), Steed (JLH 87, 12-15, by-elections), Koenig (JEH 83(1) 167-202), Laybourn (History 80(259) 207-226), Tanner (HJ 34, 893-908), Matthew et al. (EHR 91, 723-752), Acemoglu et al. (QJE 137(2) 1233-1296; RePEc says 2023, issue is May 2022), de Juan et al. (APSR 118(1) 144-162), Lawrence (JMH 2003, 557-589), Winter (Pop Studies 31(3) 449-466), Dewey (HJ 27(1) 199-223), Grossman et al. (IO 69(4) 981-1009), Kriner and Shen (LSQ 32(4) 507-530), Gartner et al. (JCR 41(5) 669-694), Pugh 1978. No errors found.
- Journals (verified): Social Science History 12,000 words incl. notes and references, no charge listed; Electoral Studies 8,000 to 10,000 words (APC terms not confirmed on the guide page); TCBH 7,000 to 10,000 incl. footnotes, OA optional with charge. cover_note.md updated.
- Licence: IWM Non-Commercial Licence (iwm.org.uk/corporate/policies/non-commercial-licence) allows non-commercial publication with attribution but forbids altering the Information and uploading it to third-party sites. CC BY-NC 4.0 for derived aggregates is consistent and stated the same way everywhere; residual risk is that map_places.json carries memorial titles and counts per place (as the source study does). Consider asking IWM if in doubt.
- QA: Playwright at 1280 and 390 px, no console errors, no horizontal page scroll, full-screen button present, site-nav.js included, layers panel toggles, memorial markers render at zooms 4 to 14 (3 px floor). At 390 px the Layers chip is part-clipped in a horizontally scrolling chip row (minor).
- Still to ask (referee): 1911 census occupation/industry by registration district to test the reserved-occupation confound directly; casualty records by residence (CWGC/Soldiers Died) instead of memorial names; enlistment rates; a model of Labour's candidacy decision (selection into standing) since the effect runs through where Labour stood; spatial dependence (Conley SEs); constituency boundaries for 1918.
