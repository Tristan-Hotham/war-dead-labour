"""Step 4: the pre-registered models (NOTES.md, analysis plan), robustness, placebos and permutation test.
Writes SCR/models.json (read by 05_results.py)."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from common import *

U0 = pd.read_csv(f"{DATA}/units.csv")
S0 = pd.read_csv(f"{DATA}/seats.csv")
U0["d_lab18_j"] = U0.e1918_LAB - U0.j1910_LAB
U0["d_lib18_j"] = U0.e1918_LIBALL - U0.j1910_LIBALL
U0["lrate"] = np.log1p(U0.rate)
U0["rrate"] = U0.rate.rank(pct=True)
lo, hi = U0.rate.quantile([.02, .98]); U0["wrate"] = U0.rate.clip(lo, hi)
U0["ldens2"] = U0.ldens ** 2
U0["ww"] = U0.elect18
MAIN = U0[U0.rate >= 10].copy()
CTRL = "ldens + d1910_LAB + d1910_LIBALL + C(region)"
OUT = {"d_lab18": "Labour share change, Dec 1910 to 1918", "coal18": "Coalition (coupon) share 1918",
       "d_lib18": "Liberal share change, Dec 1910 to 1918", "turn18": "Turnout 1918"}
LATER = {"d_lab22": "Labour change to 1922", "d_lab23": "Labour change to 1923", "d_lab24": "Labour change to 1924",
         "d_lib22": "Liberal change to 1922", "d_lib23": "Liberal change to 1923", "d_lib24": "Liberal change to 1924",
         "d_con18": "Conservative (all) change to 1918"}


def fit(df, y, x="rate", ctrl=CTRL, w=None, cov="HC3", groups=None, std=True):
    d = df.dropna(subset=[y, x] + [c for c in ("ldens", "d1910_LAB", "d1910_LIBALL", "j1910_LAB", "j1910_LIBALL", "e1906_LAB", "e1906_LIBALL", "rate2", "ldens2") if c in ctrl]).copy()
    sd = d[x].std()
    d["_z"] = (d[x] - d[x].mean()) / sd if std else d[x]
    f = f"{y} ~ _z" + (" + " + ctrl if ctrl else "")
    if w is not None:
        m = smf.wls(f, d, weights=d[w])
    else:
        m = smf.ols(f, d)
    r = m.fit(cov_type="cluster", cov_kwds={"groups": d[groups]}) if groups else m.fit(cov_type=cov)
    b, se = r.params["_z"], r.bse["_z"]; ci = r.conf_int().loc["_z"].tolist()
    return {"b": float(b), "se": float(se), "lo": float(ci[0]), "hi": float(ci[1]), "p": float(r.pvalues["_z"]), "n": int(r.nobs),
            "r2": float(r.rsquared), "sd_x": float(sd), "mean_y": float(d[y].mean()), "sd_y": float(d[y].std()),
            "per10": float(b / sd * 10) if std else None, "_res": r}


def strip(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


R = {"main": {}, "robust": {}, "placebo": {}, "later": {}, "loro": {}, "explor": {}}
full = {}
for y in OUT:
    r = fit(MAIN, y); full[y] = r["_res"]; R["main"][y] = strip(r)
p = [R["main"][y]["p"] for y in OUT]
holm = multipletests(p, method="holm")[1]
for y, ph in zip(OUT, holm):
    R["main"][y]["p_holm"] = float(ph)
# full regression tables for the appendix
R["tables"] = {y: {"params": full[y].params.to_dict(), "bse": full[y].bse.to_dict(), "pvalues": full[y].pvalues.to_dict(),
                   "n": int(full[y].nobs), "r2": float(full[y].rsquared), "r2_adj": float(full[y].rsquared_adj)} for y in OUT}

# ---- robustness grid
V = [
    ("weighted", "Weighted by 1918 electorate", dict(df=MAIN, w="ww")),
    ("no1910", "Without the December 1910 controls", dict(df=MAIN, ctrl="ldens + C(region)")),
    ("jan1910", "January 1910 baseline (outcome and controls)", dict(df=MAIN, ctrl="ldens + j1910_LAB + j1910_LIBALL + C(region)", yalt={"d_lab18": "d_lab18_j", "d_lib18": "d_lib18_j"})),
    ("dens2", "Quadratic in log density", dict(df=MAIN, ctrl=CTRL + " + ldens2")),
    ("noregion", "No region fixed effects", dict(df=MAIN, ctrl="ldens + d1910_LAB + d1910_LIBALL")),
    ("ww2ctrl", "Controlling for Second World War names per 1,000", dict(df=MAIN, ctrl=CTRL + " + rate2")),
    ("log", "Exposure: log(1 + rate)", dict(df=MAIN, x="lrate")),
    ("rank", "Exposure: percentile rank", dict(df=MAIN, x="rrate")),
    ("wins", "Exposure: winsorised at 2nd and 98th percentiles", dict(df=MAIN, x="wrate")),
    ("allmem", "Exposure: all memorials summed (double counted)", dict(df=MAIN, x="rate_all")),
    ("village", "Exposure: median village rate per 1,000 residents", dict(df=MAIN, x="village_rate")),
    ("perseat", "Exposure: names per seat", dict(df=MAIN, x="rate_seat")),
    ("allunits", "All units (including recorded rate below 10)", dict(df=U0)),
    ("cov50", "Units where at least half the places have a count", dict(df=MAIN[MAIN.coverage >= .5])),
    ("seats2", "Units with at least two 1918 seats", dict(df=MAIN[MAIN.e1918_n_seats >= 2])),
    ("nolondon", "Without London", dict(df=MAIN[MAIN.region != "London"])),
    ("noscot", "Without Scotland", dict(df=MAIN[MAIN.region != "Scotland"])),
    ("england", "England only", dict(df=MAIN[MAIN.nation == "England"])),
]
for key, name, kw in V:
    R["robust"][key] = {"name": name}
    for y in OUT:
        kk = dict(kw); ya = kk.pop("yalt", {}).get(y, y)
        try:
            R["robust"][key][y] = strip(fit(y=ya, **kk))
        except Exception as e:
            R["robust"][key][y] = None
            print("fail", key, y, e)
# Cook's distance
R["robust"]["cook"] = {"name": "Dropping influential units (Cook's distance above 4/N)"}
for y in OUT:
    res = full[y]; infl = res.get_influence() if hasattr(res, "get_influence") else None
    d = MAIN.dropna(subset=[y, "rate", "ldens", "d1910_LAB", "d1910_LIBALL"]).copy()
    ols = smf.ols(f"{y} ~ rate + {CTRL}", d).fit()
    cd = ols.get_influence().cooks_distance[0]
    keep = d[cd <= 4 / len(d)]
    R["robust"]["cook"][y] = strip(fit(keep, y)); R["robust"]["cook"][y]["dropped"] = int((cd > 4 / len(d)).sum())
# leave one region out
for y in OUT:
    out = {}
    for rg in REGION_ORDER:
        sub = MAIN[MAIN.region != rg]
        out[rg] = strip(fit(sub, y))
    R["loro"][y] = {"by": out, "min": min(v["b"] for v in out.values()), "max": max(v["b"] for v in out.values()),
                    "n_sig": sum(v["p"] < .05 for v in out.values())}
# constituency level
SM = S0.merge(MAIN[["unit"]], on="unit")
SM = SM[SM.n_contested > 0].copy()
SM["d_lab18"] = SM.LAB - SM.d1910_LAB
SM["d_lib18"] = SM.LIBALL - SM.d1910_LIBALL
SM["coal18"] = SM.COAL; SM["turn18"] = SM.turnout
R["robust"]["seat"] = {"name": "Constituency level (clustered by unit)"}
R["robust"]["seat_all"] = {"name": "Constituency level, seats with 10 or more per 1,000"}
SA = S0[(S0.n_contested > 0)].copy()
SA["d_lab18"] = SA.LAB - SA.d1910_LAB; SA["d_lib18"] = SA.LIBALL - SA.d1910_LIBALL; SA["coal18"] = SA.COAL; SA["turn18"] = SA.turnout
SA = SA[SA.rate >= 10]
for y in OUT:
    R["robust"]["seat"][y] = strip(fit(SM, y, groups="unit"))
    R["robust"]["seat_all"][y] = strip(fit(SA, y, groups="unit"))
# ---- placebos
PL = [("pd_lab_0610", "Labour change 1906 to Dec 1910", "ldens + e1906_LAB + e1906_LIBALL + C(region)"),
      ("pd_lib_0610", "Liberal change 1906 to Dec 1910", "ldens + e1906_LAB + e1906_LIBALL + C(region)"),
      ("pd_lab_j_d", "Labour change Jan to Dec 1910", "ldens + j1910_LAB + j1910_LIBALL + C(region)"),
      ("pd_lib_j_d", "Liberal change Jan to Dec 1910", "ldens + j1910_LAB + j1910_LIBALL + C(region)"),
      ("d1910_LAB", "Labour share Dec 1910 (level)", "ldens + C(region)"),
      ("d1910_LIBALL", "Liberal share Dec 1910 (level)", "ldens + C(region)")]
for y, name, ctrl in PL:
    R["placebo"][y] = {"name": name, **strip(fit(MAIN, y, ctrl=ctrl))}
for y in OUT:
    R["placebo"]["ww2_" + y] = {"name": "Second World War names per 1,000 as the exposure: " + OUT[y], **strip(fit(MAIN, y, x="rate2"))}
# permutation within region for the primary outcome
rng = np.random.default_rng(SEED)
d = MAIN.dropna(subset=["d_lab18", "rate", "ldens", "d1910_LAB", "d1910_LIBALL"]).copy()
X = pd.get_dummies(d[["ldens", "d1910_LAB", "d1910_LIBALL", "region"]], columns=["region"], drop_first=True).astype(float)
X = sm.add_constant(X)
z = ((d.rate - d.rate.mean()) / d.rate.std()).values
Y = d.d_lab18.values


def beta(zz):
    XX = np.column_stack([zz, X.values]); return np.linalg.lstsq(XX, Y, rcond=None)[0][0]


b0 = beta(z); perm = []
grp = d.region.values
for _ in range(2000):
    zz = z.copy()
    for g in np.unique(grp):
        ix = np.where(grp == g)[0]; zz[ix] = rng.permutation(zz[ix])
    perm.append(beta(zz))
perm = np.array(perm)
R["perm"] = {"b": float(b0), "p": float((np.abs(perm) >= abs(b0)).mean()), "reps": 2000}
for y in {**OUT}:
    pass
# later elections
for y, name in LATER.items():
    R["later"][y] = {"name": name, **strip(fit(MAIN, y))}
# exploratory: by nation and by unit type (labelled exploratory)
for k, sub in (("england", MAIN[MAIN.nation == "England"]), ("scotland", MAIN[MAIN.nation == "Scotland"]), ("wales", MAIN[MAIN.nation == "Wales"]),
               ("urban", MAIN[MAIN.density >= MAIN.density.median()]), ("rural", MAIN[MAIN.density < MAIN.density.median()])):
    try:
        R["explor"][k] = {y: strip(fit(sub, y, ctrl="ldens + d1910_LAB + d1910_LIBALL" + (" + C(region)" if sub.region.nunique() > 1 else ""))) for y in ("d_lab18", "coal18")}
    except Exception as e:
        print("explor fail", k, e)
# exploratory: Labour's extensive margin (share of seats where Labour stood) and intensive margin (units where it stood)
MAIN["lab_stood18"] = 100 * MAIN.e1918_lab_stood
R["explor"]["stood"] = {"lab_stood18": strip(fit(MAIN, "lab_stood18"))}
R["explor"]["where_stood"] = {"d_lab18": strip(fit(MAIN[MAIN.e1918_lab_stood > 0], "d_lab18"))}
# bivariate (no controls) for description
R["bivar"] = {y: strip(fit(MAIN, y, ctrl="")) for y in OUT}
# correlates of the exposure (descriptive)
cor = MAIN[["rate", "ldens", "d1910_LAB", "d1910_LIBALL", "coverage", "rate2", "village_rate", "rate_all"]].corr()["rate"].drop("rate")
R["exp_corr"] = cor.to_dict()
# ---- checks added at review (exploratory, not in the plan; labelled as such wherever quoted)
U0["rate10"] = 1000 * U0.dead1 / U0.d1910_electorate      # denominator before the war and the 1918 franchise
MAIN["rate10"] = U0.loc[MAIN.index, "rate10"]
R["review"] = {f"thr{t}": strip(fit(U0[U0.rate >= t], "d_lab18")) for t in (5, 15, 20)}
R["review"]["rate1910"] = strip(fit(MAIN, "d_lab18", x="rate10"))
R["review"]["coverage_ctrl"] = strip(fit(MAIN, "d_lab18", ctrl=CTRL + " + coverage"))
R["review"]["no_imputed"] = strip(fit(MAIN[MAIN.imputed_share == 0], "d_lab18"))
R["review"]["cov50_dropped"] = int(R["main"]["d_lab18"]["n"] - R["robust"]["cov50"]["d_lab18"]["n"])
R["n_main"] = int(len(MAIN)); R["n_all"] = int(len(U0)); R["n_main_lab"] = R["main"]["d_lab18"]["n"]
jsave(R, f"{SCR}/models.json", indent=1, keepdash=True)
for y in OUT:
    m = R["main"][y]; print(f"{y:9s} b={m['b']:+.2f} [{m['lo']:+.2f},{m['hi']:+.2f}] p={m['p']:.3f} holm={m['p_holm']:.3f} n={m['n']} per10={m['per10']:+.2f}")
print("perm", R["perm"])
for k, v in R["robust"].items():
    print(f"{k:9s}", " | ".join(f"{v[y]['b']:+.2f} ({v[y]['p']:.2f}, n={v[y]['n']})" if v.get(y) else "NA" for y in OUT))
for k, v in R["placebo"].items():
    print("PL", k, f"{v['b']:+.2f} [{v['lo']:+.2f},{v['hi']:+.2f}] p={v['p']:.3f} n={v['n']}")
for k, v in R["later"].items():
    print("LT", k, f"{v['b']:+.2f} [{v['lo']:+.2f},{v['hi']:+.2f}] p={v['p']:.3f} n={v['n']}")
for y in OUT:
    print("LORO", y, R["loro"][y]["min"], R["loro"][y]["max"], R["loro"][y]["n_sig"])
print("explor", {k: {y: (round(v[y]["b"], 2), round(v[y]["p"], 3), v[y]["n"]) for y in v} for k, v in R["explor"].items()})
print("bivar", {y: (round(v["b"], 2), round(v["p"], 3)) for y, v in R["bivar"].items()})
print("corr", {k: round(v, 2) for k, v in R["exp_corr"].items()})
