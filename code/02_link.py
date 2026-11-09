"""Step 2: link elections and memorials to the units, and memorials to 1918 constituencies.

Elections: GB contests (no university seats) in 1906, Jan 1910, Dec 1910, 1918, 1922, 1923, 1924, placed in units by their
point. Electorate = votes cast / seats / (turnout/100) (votes cast is the sum of candidates' votes, so a two-member seat
counts each voter about twice); uncontested seats get the median electorate of contested seats in the same nation and
election (flagged). Shares: party family votes / all votes in a contest, averaged over a unit's contested seats with
weight = voters (votes cast / seats).
1918 Coalition = candidates whose label carries the Coalition Coupon (and "Coalition Labour"); Labour = LAB family
without coupon holders; Liberal = all Liberals (coupon and not).

Memorials: places.csv (one row per place, GB nations), the chosen community memorial count for each war (the source
study's no-double-counting rule), summed over the places in a unit. Places and seats in units without a 1918 seat move
to the unit of the nearest 1918 seat. Constituency level: divided boroughs merged; each place goes to the nearest 1918
seat (or merged borough) point within its unit.
Writes SCR/contests.pkl, SCR/places.pkl, data/link_checks.json and data/seats_1918.csv."""
import geopandas as gpd, pandas as pd, numpy as np
from common import *

units = gpd.read_file(f"{SCR}/units.gpkg")
C = pd.read_csv(f"{EL}/contests.csv", low_memory=False); C["election"] = C.election.astype(str)
K = pd.read_csv(f"{EL}/candidates.csv", low_memory=False); K["election"] = K.election.astype(str)
C = C[C.election.isin(ELECTIONS) & C.nation.isin(["England", "Wales", "Scotland"])]
C = C[~C.constituency.str.contains("Universit")].copy()
K = K[K.election.isin(ELECTIONS)].merge(C[["election", "constituency"]], on=["election", "constituency"])


def to_units(df, lon="lon", lat="lat"):
    g = gpd.GeoDataFrame(df.copy(), geometry=gpd.points_from_xy(df[lon], df[lat]), crs=4326).to_crs(27700)
    j = gpd.sjoin(g, units[["unit", "geometry"]], how="left", predicate="within")
    j = j[~j.index.duplicated()]
    m = j.unit.isna()
    if m.any():
        nn = gpd.sjoin_nearest(g[m], units[["unit", "geometry"]], how="left", distance_col="d")
        nn = nn[~nn.index.duplicated()]
        j.loc[m, "unit"] = nn.unit.values
    out = df.copy(); out["unit"] = j.unit.values; out["x"] = g.geometry.x.values; out["y"] = g.geometry.y.values
    out["offshore"] = m.values
    return out


# display points nudged 2.5 km (town divisions) or 15 km (county divisions) by the compass word in the name are moved back
# to the place they were nudged from (the "anchor") for unit assignment; the nudged point is kept for nearest-seat linkage
CP = pd.read_csv(f"{EL}/constituency_places.csv")[["wikidata", "label", "place_source"]]
C = C.merge(CP, on="wikidata", how="left")


def direction(name):
    n = " " + str(name) + " "; dx = dy = 0
    if re.search(r"\b(North|Northern)\b", n): dy += 1
    if re.search(r"\b(South|Southern)\b", n): dy -= 1
    if re.search(r"\b(East|Eastern)\b", n): dx += 1
    if re.search(r"\b(West|Western)\b", n): dx -= 1
    return dx, dy


C["nudged"] = C.place_source.str.contains("nudged", na=False)
C["anc_lon"], C["anc_lat"] = C.lon.copy(), C.lat.copy()
for i, r in C[C.nudged].iterrows():
    k = float(re.search(r"nudged ([\d.]+) km", r.place_source).group(1)); dx, dy = direction(r.label)
    C.at[i, "anc_lon"] = r.lon - dx * k / (111.0 * math.cos(math.radians(r.lat)))
    C.at[i, "anc_lat"] = r.lat - dy * k / 111.0
C = to_units(C, "anc_lon", "anc_lat")
g = gpd.GeoSeries(gpd.points_from_xy(C.lon, C.lat), crs=4326).to_crs(27700)
C["x"], C["y"] = g.x.values, g.y.values           # nudged display point for nearest-seat linkage
s18 = C[C.election == "1918"]
have = set(s18.unit)
pts18 = gpd.GeoDataFrame(s18, geometry=gpd.points_from_xy(s18.x, s18.y), crs=27700)


def fix_unit(df):
    """move rows in units without a 1918 seat to the unit of the nearest 1918 seat"""
    m = ~df.unit.isin(have)
    if m.any():
        g = gpd.GeoDataFrame(df[m], geometry=gpd.points_from_xy(df[m].x, df[m].y), crs=27700)
        nn = gpd.sjoin_nearest(g, pts18[["unit", "geometry"]].rename(columns={"unit": "unit18"}), how="left")
        nn = nn[~nn.index.duplicated()]
        df.loc[m, "unit"] = nn.unit18.values
    df["moved"] = m.values
    return df


C = fix_unit(C)
# ---- candidates: families and coalition
K["coal"] = K.party.str.contains("Coalition Coupon", na=False) | (K.party == "Coalition Labour")
K["fam"] = np.where((K.election == "1918") & K.coal, "COAL", K.family)
K.loc[~K.fam.isin(["LAB", "LIB", "CON", "COAL"]), "fam"] = "OTH"
K["lib_all"] = K.family.eq("LIB")
K["lab_all"] = K.family.eq("LAB")         # incl. the one Labour coupon holder
K["con_all"] = K.family.eq("CON")
K["v"] = K.votes.fillna(0)
tot = K.groupby(["election", "constituency"]).v.sum().rename("tv")
K = K.join(tot, on=["election", "constituency"])
sh = K[K.tv > 0].assign(s=lambda d: 100 * d.v / d.tv)
wide = sh.pivot_table(index=["election", "constituency"], columns="fam", values="s", aggfunc="sum", fill_value=0)
for k in ("LAB", "LIB", "CON", "COAL", "OTH"):
    if k not in wide: wide[k] = 0.0
wide = wide[["LAB", "LIB", "CON", "COAL", "OTH"]].add_prefix("sh_")
for nm, col in (("sh_LIBALL", "lib_all"), ("sh_LABALL", "lab_all"), ("sh_CONALL", "con_all")):
    wide[nm] = sh[sh[col]].groupby(["election", "constituency"]).s.sum().reindex(wide.index).fillna(0)
stood = K.groupby(["election", "constituency"]).apply(lambda d: pd.Series({
    "lab_stood": bool(((d.fam == "LAB")).any()), "ncand": len(d)}), include_groups=False)
C = C.join(wide, on=["election", "constituency"]).join(stood, on=["election", "constituency"])
C["contested"] = ~C.uncontested.astype(bool) & C.votes_cast.notna() & C.turnout.notna() & (C.sh_LAB.notna())
C["electorate"] = np.where(C.contested, C.votes_cast / C.seats / (C.turnout / 100), np.nan)
med = C[C.contested].groupby(["election", "nation"]).electorate.median()
C["elect_imputed"] = C.electorate.isna()
C["electorate_f"] = [e if e == e else med[(el, n)] * s for e, el, n, s in zip(C.electorate, C.election, C.nation, C.seats)]
C["electorate"] = np.where(C.contested, C.electorate * C.seats, np.nan)   # whole electorate of the seat
C["voters"] = np.where(C.contested, C.votes_cast / C.seats, np.nan)
C.to_pickle(f"{SCR}/contests.pkl")

# ---- divided boroughs (constituency level)
COMPASS = ["North East", "North West", "South East", "South West", "North", "South", "East", "West", "Central", "Mid"]
NOMERGE = ("shire", "Dorset", "Norfolk", "Fife", "Surrey", "Essex", "Cornwall", "Cumberland", "Kincardine", "Derbyshire")


def root(n):
    s = n
    for c in COMPASS:
        if s.startswith(c + " "): s = s[len(c) + 1:]; break
    for c in COMPASS:
        if s.endswith(" " + c): s = s[: -len(c) - 1]; break
    return s


s18 = C[C.election == "1918"].copy()
s18["root"] = s18.constituency.map(root)
first = s18.constituency.str.split().str[0]
s18["borough"] = s18.constituency
for u, d in s18.groupby("unit"):
    for r, dd in d.groupby("root"):
        if len(dd) > 1 and not any(w in r for w in NOMERGE):
            s18.loc[dd.index, "borough"] = r
    for f, dd in d.groupby(first.loc[d.index]):
        if len(dd) > 1 and len(f) > 3 and f not in ("East", "West", "North", "South", "Central", "Mid", "Isle", "The") \
                and not any(w in f for w in NOMERGE) and (s18.loc[dd.index, "borough"] == s18.loc[dd.index, "constituency"]).all():
            s18.loc[dd.index, "borough"] = f
s18.loc[s18.borough == "Ham", "borough"] = "East Ham"
merged = s18[s18.borough != s18.constituency].groupby("borough").constituency.apply(list).to_dict()
s18["seat_id"] = s18.borough
s18[["constituency", "seat_id", "unit", "nation", "seats", "lon", "lat", "x", "y", "contested", "electorate",
     "electorate_f", "turnout", "sh_LAB", "sh_LIB", "sh_CON", "sh_COAL", "sh_OTH", "sh_LIBALL", "lab_stood", "moved",
     "offshore"]].to_csv(f"{DATA}/seats_1918.csv", index=False)

# ---- memorial places
P = pd.read_csv(f"{WM}/places.csv", low_memory=False)
P = P[P.nation.isin(["England", "Wales", "Scotland"]) & P.lat.notna()].copy()
P = to_units(P, "lng", "lat")
P = fix_unit(P)
# nearest 1918 seat point within the unit (merged boroughs: a seat_id's point is the mean of its divisions)
sp = s18.groupby("seat_id").agg(unit=("unit", "first"), x=("x", "mean"), y=("y", "mean")).reset_index()
P["seat_id"] = None; P["seat_d_km"] = np.nan
for u, d in P.groupby("unit"):
    c = sp[sp.unit == u]
    dx = d.x.values[:, None] - c.x.values[None, :]; dy = d.y.values[:, None] - c.y.values[None, :]
    D = np.hypot(dx, dy); k = D.argmin(1)
    P.loc[d.index, "seat_id"] = c.seat_id.values[k]; P.loc[d.index, "seat_d_km"] = D[np.arange(len(d)), k] / 1000
P.to_pickle(f"{SCR}/places.pkl")

# ---- validation V1: places named like a single-member undivided 1918 borough, or like a divided borough
cands = {}
for sid, d in s18.groupby("seat_id"):
    cands[norm(sid)] = sid
alias = {norm("Barrow in Furness"): "Barrow in Furness", norm("Kingston upon Hull"): "Kingston upon Hull", "hull": "Kingston upon Hull",
         norm("Newcastle upon Tyne"): "Newcastle upon Tyne", norm("Chester"): "City of Chester", norm("Hartlepool"): "The Hartlepools",
         norm("Grimsby"): "Great Grimsby"}
cands.update({k: v for k, v in alias.items() if v in set(s18.seat_id)})
P["pn"] = P.place.map(norm)
v1 = P[P.pn.isin(cands)].copy()
v1["expect"] = v1.pn.map(cands)
ex = sp.set_index("seat_id")
v1["d_expect_km"] = [math.hypot(x - ex.x[e], y - ex.y[e]) / 1000 for x, y, e in zip(v1.x, v1.y, v1.expect)]
v1 = v1[v1.d_expect_km <= 15].copy()          # namesakes elsewhere (Upton, Stone, Acton in other counties) are not tests
v1["ok"] = v1.expect == v1.seat_id
v1["unit_ok"] = [u in set(s18[s18.seat_id == e].unit) for u, e in zip(v1.unit, v1.expect)]
bad = v1[~v1.ok][["place", "county", "expect", "seat_id", "unit", "seat_d_km"]]
# V2: register county text vs unit's county or unit name
def cty_ok(row):
    rc = norm(row.county) if isinstance(row.county, str) else ""
    if not rc: return None
    un = norm(row.unit.replace(" (shire)", "")); uc = norm(units.set_index("unit").county.get(row.unit, ""))
    toks = set(rc.replace("city of ", "").split()) - {"and", "the", "of", "upon", "county", "city", "borough"}
    return bool(toks & (set(un.split()) | set(uc.split()))) or rc in un or un in rc
P["v2"] = P.apply(cty_ok, axis=1)
v2 = P[P.v2.notna()]
L = {"n_places_gb": int(len(P)), "places_moved": int(P.moved.sum()), "places_offshore": int(P.offshore.sum()),
     "seats_1918": int(len(s18)), "seats_1918_nudged": int(s18.nudged.sum()), "seat_ids_1918": int(s18.seat_id.nunique()), "merged_boroughs": {k: v for k, v in merged.items()},
     "n_merged_boroughs": len(merged), "units_with_1918_seat": len(have),
     "contests_moved": C.groupby("election").moved.sum().to_dict(), "contests_offshore": C.groupby("election").offshore.sum().to_dict(),
     "v1_n": int(len(v1)), "v1_ok": int(v1.ok.sum()), "v1_unit_ok": int(v1.unit_ok.sum()),
     "v1_bad": bad.head(60).to_dict("records"),
     "v2_n": int(len(v2)), "v2_ok": int(v2.v2.sum()),
     "v2_bad_examples": v2[~v2.v2.astype(bool)][["place", "county", "unit"]].sample(min(40, int((~v2.v2.astype(bool)).sum())), random_state=1).to_dict("records"),
     "seat_d_km_median": float(P.seat_d_km.median()), "seat_d_km_p90": float(P.seat_d_km.quantile(.9))}
jsave(L, f"{DATA}/link_checks.json", indent=1)
print({k: v for k, v in L.items() if k not in ("merged_boroughs", "v1_bad", "v2_bad_examples")})
print(sorted(merged))
print(bad.to_string())
