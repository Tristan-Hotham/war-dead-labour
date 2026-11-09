"""Step 3: the analysis tables. data/units.csv (one row per county unit) and data/seats.csv (one row per 1918 seat or
merged borough), plus data/units.geojson for the map. No models here."""
import geopandas as gpd, pandas as pd, numpy as np
from common import *

units = gpd.read_file(f"{SCR}/units.gpkg")
C = pd.read_pickle(f"{SCR}/contests.pkl")
P = pd.read_pickle(f"{SCR}/places.pkl")
FAM = ["LAB", "LIB", "CON", "COAL", "OTH", "LIBALL", "CONALL"]


def shares(d):
    c = d[d.contested]
    out = {"n_seats": float(d.seats.sum()), "n_contests": len(d), "n_contested": len(c),
           "unopp": float((~d.contested).sum()), "electorate": float(d.electorate_f.sum())}
    if len(c):
        w = c.voters
        for f in FAM:
            out[f] = float((c["sh_" + f] * w).sum() / w.sum())
        out["turnout"] = float(100 * c.voters.sum() / (c.electorate / c.seats).sum())
        out["lab_stood"] = float((c.lab_stood * c.seats).sum() / c.seats.sum())
    return pd.Series(out)


rows = []
for e in ELECTIONS:
    d0 = C[C.election == e]
    g = pd.DataFrame({u: shares(d) for u, d in d0.groupby("unit")}).T
    g.columns = [f"{EKEY[e]}_{c}" for c in g.columns]
    rows.append(g)
E = pd.concat(rows, axis=1)

# memorials
P["d1"] = P.ww1_dead.fillna(0); P["d1all"] = P.ww1_dead_all.fillna(0); P["d2"] = P.ww2_dead.fillna(0)
P["has1"] = P.ww1_dead.notna(); P["has2"] = P.ww2_dead.notna()
P["small"] = P["pop"].between(100, 5000) & P.ww1_exact.astype(bool) & P.ww1_per1000.notna() & P.ww1_dead.notna()
M = P.groupby("unit").agg(places=("pid", "size"), places_ww1=("has1", "sum"), dead1=("d1", "sum"), dead1_all=("d1all", "sum"),
                          dead2=("d2", "sum"), places_ww2=("has2", "sum"), n_small=("small", "sum"))
vr = P[P.small].groupby("unit").ww1_per1000.median().rename("village_rate")
M = M.join(vr)
M.loc[M.n_small < 5, "village_rate"] = np.nan
U = units.drop(columns="geometry").set_index("unit").join(E, how="inner").join(M)
U = U[U.e1918_n_seats > 0].copy()
for c in ("places", "places_ww1", "dead1", "dead1_all", "dead2", "places_ww2", "n_small"):
    U[c] = U[c].fillna(0)
U["coverage"] = U.places_ww1 / U.places.replace(0, np.nan)
U["elect18"] = U.e1918_electorate
U["rate"] = 1000 * U.dead1 / U.elect18
U["rate_all"] = 1000 * U.dead1_all / U.elect18
U["rate2"] = 1000 * U.dead2 / U.elect18
U["rate_seat"] = U.dead1 / U.e1918_n_seats / 1000           # thousand names per seat
U["density"] = U.elect18 / U.area_km2
U["ldens"] = np.log(U.density)
U["imputed_share"] = 0.0
imp = C[(C.election == "1918")].groupby("unit").apply(lambda d: d.loc[~d.contested, "electorate_f"].sum() / d.electorate_f.sum(), include_groups=False)
U["imputed_share"] = imp.reindex(U.index).fillna(0)
# outcomes
U["d_lab18"] = U.e1918_LAB - U.d1910_LAB
U["d_lib18"] = U.e1918_LIBALL - U.d1910_LIBALL
U["d_con18"] = U.e1918_CONALL - U.d1910_CONALL
for e in ("e1922", "e1923", "e1924"):
    U[f"d_lab{e[-2:]}"] = U[f"{e}_LAB"] - U.d1910_LAB
    U[f"d_lib{e[-2:]}"] = U[f"{e}_LIBALL"] - U.d1910_LIBALL
U["coal18"] = U.e1918_COAL
U["turn18"] = U.e1918_turnout
U["d_turn18"] = U.e1918_turnout - U.d1910_turnout
# placebo outcomes (pre-war)
U["pd_lab_0610"] = U.d1910_LAB - U.e1906_LAB
U["pd_lib_0610"] = U.d1910_LIBALL - U.e1906_LIBALL
U["pd_lab_j_d"] = U.d1910_LAB - U.j1910_LAB
U["pd_lib_j_d"] = U.d1910_LIBALL - U.j1910_LIBALL
U.index.name = "unit"
U.reset_index().to_csv(f"{DATA}/units.csv", index=False, float_format="%.4f")

# constituency level (1918 seats, divided boroughs merged)
S = C[C.election == "1918"].copy()
s18 = pd.read_csv(f"{DATA}/seats_1918.csv")[["constituency", "seat_id"]]
S = S.merge(s18, on="constituency")
SS = pd.DataFrame({k: shares(d) for k, d in S.groupby("seat_id")}).T
SS["unit"] = S.groupby("seat_id").unit.first()
SS["seats_in_id"] = S.groupby("seat_id").size()
SS["lon"] = S.groupby("seat_id").lon.mean(); SS["lat"] = S.groupby("seat_id").lat.mean()
PM = P.groupby("seat_id").agg(places=("pid", "size"), places_ww1=("has1", "sum"), dead1=("d1", "sum"), dead2=("d2", "sum"),
                              dead1_all=("d1all", "sum"))
SS = SS.join(PM)
for c in ("places", "places_ww1", "dead1", "dead2", "dead1_all"):
    SS[c] = SS[c].fillna(0)
SS["rate"] = 1000 * SS.dead1 / SS.electorate
SS["rate2"] = 1000 * SS.dead2 / SS.electorate
SS["coverage"] = SS.places_ww1 / SS.places.replace(0, np.nan)
SS = SS.join(U[["region", "nation", "d1910_LAB", "d1910_LIBALL", "d1910_CONALL", "ldens", "utype"]], on="unit")
SS.index.name = "seat_id"
SS.reset_index().to_csv(f"{DATA}/seats.csv", index=False, float_format="%.4f")

# map geometry
g = units[units.unit.isin(U.index)][["unit", "geometry"]].copy()
g["geometry"] = g.geometry.simplify(250)
g = g.to_crs(4326)
g.to_file(f"{SCR}/units_map.geojson", driver="GeoJSON")
print(len(U), "units;", int(U.d1910_LAB.notna().sum()), "with a contested Dec 1910 seat;", len(SS), "seats/boroughs")
print(U[["rate", "rate_all", "rate2", "village_rate", "coverage", "density", "elect18", "imputed_share"]].describe().round(2).T)
print("total names", U.dead1.sum(), "electorate", U.elect18.sum())
print(U.sort_values("rate", ascending=False)[["rate", "dead1", "elect18", "coverage", "places"]].head(12))
print(U.sort_values("rate")[["rate", "dead1", "elect18", "coverage", "places"]].head(12))
