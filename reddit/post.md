# Reddit post

**Title:** [OC] Places with more names on their First World War memorials swung less to Labour in 1918, not more: 176 British counties and boroughs against the vote

**Body:**

After 1918 Labour overtook the Liberals. A common idea is that grief and anger at the slaughter pushed voters left, as happened in Italy and Germany. I counted the names on community war memorials (one memorial per place, so no one is counted twice) and set them against every election from 1906 to 1924.

- In the typical county or borough there were 44 names per 1,000 voters of 1918.
- For each 22 more names per 1,000 voters, Labour's gain from 1910 to 1918 was 2.9 points smaller (95% CI 0.1 to 5.7), comparing places in the same region with similar density and 1910 vote. By 1922 the gap was 4.8 points.
- Before the war the same names predict nothing.
- Caveat: the evidence is modest. I tested four outcomes, and allowing for that the 1918 result could be chance (adjusted p = 0.16).
- Caveat: this is a correlation. Men in mining and munitions were often kept at home, and those industrial places were where Labour grew fastest.

Interactive map, paper and data: https://maps.tristanhotham.com/war-dead-labour/

**Source comment:**

Data: Imperial War Museums War Memorials Register (counts of names per memorial; one community memorial per place); UK general election results 1906 to 1924 from UK Parliament (Open Parliament Licence); ONS boundaries. Tools: Python (pandas, geopandas, statsmodels, matplotlib). Analysis plan written before the models were run; 21 robustness checks (all negative, 8 clearly different from zero) and 6 pre-war placebo tests in the paper. Code and data: https://github.com/Tristan-Hotham/war-dead-labour
