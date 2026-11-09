"""Step 5: data/results.json (every number quoted anywhere) and the page's map data (data/map_units.json,
data/map_places.json, data/map_seats.json)."""
import pandas as pd, numpy as np, geopandas as gpd
from common import *

M = jload(f"{SCR}/models.json")
L = jload(f"{DATA}/link_checks.json")
U = pd.read_csv(f"{DATA}/units.csv")
C = pd.read_pickle(f"{SCR}/contests.pkl")
P = pd.read_pickle(f"{SCR}/places.pkl")
MAIN = U[U.rate >= 10]
R = {k: M[k] for k in ("main", "robust", "placebo", "later", "loro", "explor", "bivar", "perm", "tables", "exp_corr", "review")}


def gb_share(e, fam):
    c = C[(C.election == e) & C.contested]
    return float((c["sh_" + fam] * c.voters).sum() / c.voters.sum())


Kc = pd.read_csv(f"{EL}/candidates.csv", low_memory=False); Kc["election"] = Kc.election.astype(str)
Kc = Kc[(Kc.election == "1918")].merge(C[C.election == "1918"][["constituency"]], on="constituency")
n = {"coupon_lib_gb": int((Kc.party == "Liberal with Coalition Coupon").sum()), "coupon_all_gb": int(Kc.party.str.contains("Coalition Coupon", na=False).sum()),
     "lab_cands_gb": int((Kc.family == "LAB").sum()),
     "units": int(len(U)), "units_main": int(len(MAIN)), "units_low": int((U.rate < 10).sum()),
     "units_lab": R["main"]["d_lab18"]["n"], "places": int(L["n_places_gb"]), "places_count": int(P.ww1_dead.notna().sum()),
     "names": int(U.dead1.sum()), "names_main": int(MAIN.dead1.sum()), "elect18": int(round(U.elect18.sum())),
     "seats18": int(L["seats_1918"]), "seat_ids": int(L["seat_ids_1918"]), "merged_boroughs": int(L["n_merged_boroughs"]),
     "contested18": int(C[(C.election == "1918") & C.contested].shape[0]),
     "uncontested18": int(C[(C.election == "1918") & ~C.contested].shape[0]),
     "nudged18": int(L["seats_1918_nudged"]), "places_moved": int(L["places_moved"]),
     "seat_n_robust": R["robust"]["seat"]["d_lab18"]["n"],
     "imputed_elect_pc": float(100 * C[(C.election == "1918") & ~C.contested].electorate_f.sum() / C[C.election == "1918"].electorate_f.sum())}
desc = {"rate_median": float(MAIN.rate.median()), "rate_q1": float(MAIN.rate.quantile(.25)), "rate_q3": float(MAIN.rate.quantile(.75)),
        "rate_sd": float(R["main"]["d_lab18"]["sd_x"]), "rate_mean": float(MAIN.rate.mean()),
        "rate_all_median": float(U.rate.median()),
        "national_expect": 1000 * 744000 / float(U.elect18.sum()),
        "elect_1910": float(C[C.election == "December 1910"].electorate_f.sum()),
        "elect_ratio": float(C[C.election == "1918"].electorate_f.sum() / C[C.election == "December 1910"].electorate_f.sum()),
        "lab_1910": gb_share("December 1910", "LAB"), "lab_1918": gb_share("1918", "LAB"), "lab_1922": gb_share("1922", "LAB"),
        "lab_1923": gb_share("1923", "LAB"), "lab_1924": gb_share("1924", "LAB"),
        "lib_1910": gb_share("December 1910", "LIBALL"), "lib_1918": gb_share("1918", "LIBALL"), "lib_1922": gb_share("1922", "LIBALL"),
        "coal_1918": gb_share("1918", "COAL"),
        "d_lab18_mean": float(R["main"]["d_lab18"]["mean_y"]), "d_lab18_sd": float(R["main"]["d_lab18"]["sd_y"]),
        "coal18_mean": float(R["main"]["coal18"]["mean_y"]), "turn18_mean": float(R["main"]["turn18"]["mean_y"]),
        "corr_ldens": float(R["exp_corr"]["ldens"]), "corr_rate2": float(R["exp_corr"]["rate2"]),
        "corr_village": float(R["exp_corr"]["village_rate"])}
lk = {"v1_n": L["v1_n"], "v1_ok": L["v1_ok"], "v1_pc": 100 * L["v1_ok"] / L["v1_n"], "v1_unit_ok": L["v1_unit_ok"],
      "v1_unit_pc": 100 * L["v1_unit_ok"] / L["v1_n"], "v2_n": L["v2_n"], "v2_ok": L["v2_ok"], "v2_pc": 100 * L["v2_ok"] / L["v2_n"],
      "seat_d_med": L["seat_d_km_median"], "seat_d_p90": L["seat_d_km_p90"]}
# effect sizes in plain terms
m = R["main"]["d_lab18"]
T = {"lab_b": m["b"], "lab_lo": m["lo"], "lab_hi": m["hi"], "lab_p": m["p"], "lab_holm": m["p_holm"], "lab_per10": m["per10"],
     "lab_b_abs": abs(m["b"]), "lab_lo_abs": abs(m["hi"]), "lab_hi_abs": abs(m["lo"]),
     "lab_frac_sd_y": abs(m["b"]) / m["sd_y"], "perm_p": R["perm"]["p"],
     "lab22_b_abs": abs(R["later"]["d_lab22"]["b"]), "lab22_lo_abs": abs(R["later"]["d_lab22"]["hi"]), "lab22_hi_abs": abs(R["later"]["d_lab22"]["lo"]),
     "lib22_b": R["later"]["d_lib22"]["b"], "lab24_b_abs": abs(R["later"]["d_lab24"]["b"]),
     "coal_b": R["main"]["coal18"]["b"], "coal_lo": R["main"]["coal18"]["lo"], "coal_hi": R["main"]["coal18"]["hi"],
     "lab_n": m["n"], "iqr_sd": (MAIN.rate.quantile(.75) - MAIN.rate.quantile(.25)) / m["sd_x"], "iqr_effect": abs(m["b"]) * (MAIN.rate.quantile(.75) - MAIN.rate.quantile(.25)) / m["sd_x"], "mech_max": 100 * m["sd_x"] / 1000,           # dead per SD as a share of the electorate, pp: an upper bound on composition
     "n_robust": sum(1 for k, v in R["robust"].items() if v.get("d_lab18")),
     "n_robust_neg": sum(1 for k, v in R["robust"].items() if v.get("d_lab18") and v["d_lab18"]["b"] < 0),
     "n_robust_sig": sum(1 for k, v in R["robust"].items() if v.get("d_lab18") and v["d_lab18"]["p"] < 0.05),
     "loro_min_abs": abs(R["loro"]["d_lab18"]["max"]), "loro_max_abs": abs(R["loro"]["d_lab18"]["min"]),
     "loro_sig": R["loro"]["d_lab18"]["n_sig"], "loro_nsig": 11 - R["loro"]["d_lab18"]["n_sig"], "n_placebo": 6,
     "placebo_max_p_min": min(v["p"] for v in R["placebo"].values())}
top = MAIN.sort_values("rate", ascending=False)
R.update({"n": n, "desc": desc, "link": lk, "T": T,
          "top_units": top[["unit", "rate", "dead1", "elect18", "d_lab18"]].head(8).to_dict("records"),
          "low_units": U[U.rate < 10].unit.tolist()})
VARS = [("rate", "Memorial names per 1,000 electors, 1918"), ("d_lab18", "Labour change, Dec 1910 to 1918 (points)"),
        ("coal18", "Coalition share, 1918 (%)"), ("d_lib18", "Liberal change, Dec 1910 to 1918 (points)"), ("turn18", "Turnout, 1918 (%)"),
        ("d_lab22", "Labour change, Dec 1910 to 1922 (points)"), ("d1910_LAB", "Labour share, Dec 1910 (%)"),
        ("d1910_LIBALL", "Liberal share, Dec 1910 (%)"), ("ldens", "Log electors per km2, 1918"), ("rate2", "Second World War names per 1,000 electors"),
        ("coverage", "Share of memorial places with a count"), ("elect18", "Electorate, 1918")]
R["desc_table"] = [{"var": v, "name": nm, "n": int(MAIN[v].notna().sum()), "mean": float(MAIN[v].mean()), "sd": float(MAIN[v].std()),
                    "min": float(MAIN[v].min()), "max": float(MAIN[v].max())} for v, nm in VARS]
# checks
assert R["main"]["d_lab18"]["b"] < 0 and R["main"]["d_lab18"]["p"] < 0.05 and R["main"]["d_lab18"]["p_holm"] > 0.05
assert all(v["p"] > 0.05 for v in R["placebo"].values())
assert R["later"]["d_lab22"]["p"] < 0.01 and R["later"]["d_lib22"]["b"] > 0
assert R["review"]["cov50_dropped"] == 0 and all(v["b"] < 0 for k, v in R["review"].items() if isinstance(v, dict))
assert n["units_main"] == 158 and n["units_lab"] == 131
jsave(R, f"{DATA}/results.json", indent=1, keepdash=True)

# ---------- map data
g = gpd.read_file(f"{SCR}/units_map.geojson")
g = g.merge(U, on="unit", how="inner")
keep = ["unit", "region", "rate", "dead1", "elect18", "places", "places_ww1", "e1918_n_seats", "d1910_LAB", "e1918_LAB", "e1922_LAB",
        "e1923_LAB", "e1924_LAB", "d1910_LIBALL", "e1918_LIBALL", "e1922_LIBALL", "e1918_COAL", "e1918_turnout", "d_lab18", "d_lab22",
        "village_rate"]
g = g[keep + ["geometry"]].copy()
for c in keep[2:]:
    g[c] = g[c].astype(float).round(2)
g["main"] = (g.rate >= 10).astype(int)
import json as _j
gj = _j.loads(g.to_json(drop_id=True))
def rnd(c):
    if isinstance(c[0], (int, float)): return [round(c[0], 4), round(c[1], 4)]
    return [rnd(x) for x in c]
for f in gj["features"]:
    f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    f["properties"] = {k: v for k, v in f["properties"].items() if v is not None and v == v}
jsave(gj, f"{DATA}/map_units.json", keepdash=True)
pl = P[P.ww1_dead.notna()]
pts = [[round(r.lng, 4), round(r.lat, 4), r.place, int(r.ww1_dead), str(r.ww1_title) if isinstance(r.ww1_title, str) else "", int(r.ww1_mid) if r.ww1_mid == r.ww1_mid else 0,
        round(float(r.ww1_per1000), 1) if r.ww1_per1000 == r.ww1_per1000 else None, int(r["pop"]) if r["pop"] == r["pop"] else None, r.unit, r.seat_id]
       for _, r in pl.iterrows()]
jsave({"cols": ["lon", "lat", "place", "dead", "title", "mid", "per1000", "pop", "unit", "seat"], "rows": pts}, f"{DATA}/map_places.json", keepdash=True)
S = pd.read_csv(f"{DATA}/seats_1918.csv")
K = pd.read_csv(f"{EL}/candidates.csv", low_memory=False); K["election"] = K.election.astype(str)
K = K[K.election == "1918"]
win = K[K.elected == True].groupby("constituency").apply(lambda d: "; ".join(f"{a} ({b})" for a, b in zip(d.candidate, d.party)), include_groups=False)
seats = [[round(r.lon, 4), round(r.lat, 4), r.constituency, None if r.sh_LAB != r.sh_LAB else round(r.sh_LAB, 1), None if r.sh_COAL != r.sh_COAL else round(r.sh_COAL, 1),
          None if r.sh_LIBALL != r.sh_LIBALL else round(r.sh_LIBALL, 1), None if r.turnout != r.turnout else round(r.turnout, 1), int(bool(r.contested)), win.get(r.constituency, ""), r.unit]
         for r in S.itertuples()]
jsave({"cols": ["lon", "lat", "name", "lab", "coal", "lib", "turnout", "contested", "won", "unit"], "rows": seats}, f"{DATA}/map_seats.json", keepdash=True)
jsave({"bounds": [-8.2, 49.8, 2.0, 60.9]}, f"{DATA}/site.json")
print("results.json ok;", {k: round(v, 2) if isinstance(v, float) else v for k, v in T.items()})
print(n, {k: round(v, 2) for k, v in desc.items()})
for f in ("map_units.json", "map_places.json", "map_seats.json"):
    print(f, os.path.getsize(f"{DATA}/{f}") // 1024, "KB")
