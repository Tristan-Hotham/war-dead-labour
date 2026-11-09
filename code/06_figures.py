"""Step 6: static figures for the paper (f_*.png), blog (b_*.png) and page (img/*.jpg)."""
import geopandas as gpd, pandas as pd, numpy as np
import statsmodels.formula.api as smf
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from figstyle import *

R = jload(f"{DATA}/results.json")
U = pd.read_csv(f"{DATA}/units.csv")
G = gpd.read_file(f"{SCR}/units.gpkg").merge(U, on="unit")
MAIN = U[U.rate >= 10].copy()


# ---------- 1. maps: recorded names per 1,000 electors, and Labour's gain 1910 to 1918
def choropleth(ax, col, bins, cols, mask=None, inset=None):
    cmap = ListedColormap(cols); norm = BoundaryNorm(bins, len(cols))
    g = G.copy()
    ok = g[col].notna() & (mask(g) if mask is not None else True)
    g[~ok].plot(ax=ax, color="#E4E0D8", edgecolor="white", linewidth=0.25, hatch="////")
    g[ok].plot(ax=ax, column=col, cmap=cmap, norm=norm, edgecolor="white", linewidth=0.25)
    ax.set_axis_off(); ax.set_xlim(60000, 660000); ax.set_ylim(5000, 1220000)
    if inset:
        ia = ax.inset_axes(inset)
        g[~ok].plot(ax=ia, color="#E4E0D8", edgecolor="white", linewidth=0.3, hatch="////")
        g[ok].plot(ax=ia, column=col, cmap=cmap, norm=norm, edgecolor="white", linewidth=0.3)
        ia.set_xlim(503000, 562000); ia.set_ylim(155000, 202000); ia.set_xticks([]); ia.set_yticks([]); ia.set_xlabel(""); ia.set_ylabel("")
        for s in ia.spines.values(): s.set_edgecolor(MUT); s.set_linewidth(0.6); s.set_visible(True)
        ia.set_title("London", fontsize=9, fontfamily=MONO, color=MUT, pad=2)
    return cmap, norm


fig, axs = plt.subplots(1, 2, figsize=(9, 7.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.12, wspace=0.02)
b1 = [10, 25, 35, 45, 55, 70, 140]
choropleth(axs[0], "rate", b1, SEQ, mask=lambda g: g.rate >= 10, inset=[0.64, 0.72, 0.35, 0.24])
b2 = [-5, 5, 10, 15, 20, 30, 60]
choropleth(axs[1], "d_lab18", b2, REDS, mask=lambda g: g.rate >= 10, inset=[0.64, 0.72, 0.35, 0.24])
title(fig, "Where the names were, and where Labour grew", "Left: First World War names on community memorials per 1,000 electors of 1918. Right: Labour's gain in vote share,\nDecember 1910 to 1918 (percentage points). Units are counties, county towns and boroughs.")
for ax, bins, cols, lab in ((axs[0], b1, SEQ, "names per 1,000 electors"), (axs[1], b2, REDS, "Labour gain, points")):
    lx = ax.inset_axes([0.04, -0.08, 0.92, 0.035])
    for i, c in enumerate(cols):
        lx.add_patch(plt.Rectangle((i, 0), 0.94, 1, color=c))
        lx.text(i, -0.4, f"{bins[i]}", fontsize=8.5, fontfamily=MONO, color=MUT, ha="center", va="top")
    lx.text(len(cols), -0.4, f"{bins[-1]}", fontsize=8.5, fontfamily=MONO, color=MUT, ha="center", va="top")
    lx.set_xlim(-0.2, len(cols) + 0.2); lx.set_ylim(-1.6, 1.4); lx.axis("off")
    lx.text(len(cols) / 2, 1.3, lab, fontsize=9.5, ha="center", va="bottom", color=INKC)
note(fig, "Hatched grey: no city-wide count in the register (under 10 names per 1,000) or no contested seat in 1910.\nSources: IWM War Memorials Register; general election results 1910 to 1918.")
save3(fig, "maps")

# ---------- 2. binned scatter (Frisch-Waugh: both sides residualised on the controls)
d = MAIN.dropna(subset=["d_lab18", "rate", "ldens", "d1910_LAB", "d1910_LIBALL"]).copy()
ctrl = "ldens + d1910_LAB + d1910_LIBALL + C(region)"
d["ry"] = smf.ols(f"d_lab18 ~ {ctrl}", d).fit().resid + d.d_lab18.mean()
d["rx"] = smf.ols(f"rate ~ {ctrl}", d).fit().resid + d.rate.mean()
fit = smf.ols("ry ~ rx", d).fit()
fig, ax = plt.subplots(figsize=(9, 5.8)); fig.subplots_adjust(left=0.09, right=0.97, top=0.82, bottom=0.17)
s = 12 + 110 * d.elect18 / d.elect18.max()
ax.scatter(d.rx, d.ry, s=s, color=LAB, alpha=0.35, edgecolor="white", linewidth=0.8, zorder=3)
q = pd.qcut(d.rx, 10, labels=False)
bx = d.groupby(q).rx.mean(); by = d.groupby(q).ry.mean()
ax.scatter(bx, by, s=70, color=INKC, zorder=5, edgecolor="white", linewidth=1.2)
xs = np.linspace(d.rx.min(), d.rx.max(), 50)
pr = fit.get_prediction(pd.DataFrame({"rx": xs})).summary_frame()
ax.fill_between(xs, pr.mean_ci_lower, pr.mean_ci_upper, color=LAB, alpha=0.12, lw=0)
ax.plot(xs, pr["mean"], color=LAB, lw=2)
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_xlabel("Names on community memorials per 1,000 electors (adjusted for the controls)")
ax.set_ylabel("Labour gain, 1910 to 1918 (points, adjusted)")
m = R["main"]["d_lab18"]
ax.text(0.99, 0.95, f"1 SD more names ({m['sd_x']:.0f} per 1,000):\nLabour gain {m['b']:+.1f} points\n95% CI {m['lo']:+.1f} to {m['hi']:+.1f}, N = {m['n']}",
        transform=ax.transAxes, ha="right", va="top", fontsize=10.5, fontfamily=MONO, color=INKC)
title(fig, "More names, a smaller swing to Labour", "Each faint dot is a county or borough unit (size: 1918 electorate); black dots are averages of tenths. Both axes\nare adjusted for region, density and 1910 Labour and Liberal shares.")
note(fig, "Correlational: units with more recorded war dead differed in other ways too.\nData: IWM War Memorials Register; general election results.")
save3(fig, "scatter")

# ---------- 3. the path over time: Labour and Liberal coefficients, with pre-war placebos
rows = [("1906 to\nDec 1910", R["placebo"]["pd_lab_0610"], R["placebo"]["pd_lib_0610"]),
        ("Jan to\nDec 1910", R["placebo"]["pd_lab_j_d"], R["placebo"]["pd_lib_j_d"]),
        ("1910 to\n1918", R["main"]["d_lab18"], R["main"]["d_lib18"]),
        ("1910 to\n1922", R["later"]["d_lab22"], R["later"]["d_lib22"]),
        ("1910 to\n1923", R["later"]["d_lab23"], R["later"]["d_lib23"]),
        ("1910 to\n1924", R["later"]["d_lab24"], R["later"]["d_lib24"])]
fig, ax = plt.subplots(figsize=(9, 5.4)); fig.subplots_adjust(left=0.1, right=0.97, top=0.8, bottom=0.17)
x = np.arange(len(rows))
ax.axvspan(-0.5, 1.5, color="#EFE9DD", lw=0, zorder=0)
ax.text(0.5, 0.97, "before the war\n(placebo)", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=9.5, fontfamily=MONO, color=MUT)
ax.axhline(0, color=MUT, lw=0.9)
for off, k, col, nm in ((-0.12, 1, LAB, "Labour"), (0.12, 2, LIB, "Liberal")):
    b = [r[k]["b"] for r in rows]; lo = [r[k]["lo"] for r in rows]; hi = [r[k]["hi"] for r in rows]
    ax.vlines(x + off, lo, hi, color=col, lw=2.2, zorder=3)
    ax.scatter(x + off, b, s=60, color=col, zorder=4, edgecolor="white", linewidth=1.5)
    ax.plot(x[2:] + off, b[2:], color=col, lw=1, alpha=0.5, zorder=2)
    ax.text(x[-1] + off + 0.1, b[-1], nm, color=INKC, fontsize=10.5, va="center")
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows], fontsize=10.5)
ax.set_xlim(-0.5, len(rows) - 0.2)
ax.set_ylabel("Change in vote share per SD more names (points)")
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
title(fig, "The gap opened with the war and widened in 1922", "Coefficient on recorded war dead (per SD) for the change in each party's vote share since the baseline election,\nwith 95% confidence intervals. Before the war the names predict nothing.")
note(fig, "OLS on county and borough units with region fixed effects and controls; robust (HC3) standard errors.")
save3(fig, "path")

# ---------- 4. robustness forest for the primary outcome
V = [("Main specification", R["main"]["d_lab18"])] + [(v["name"], v["d_lab18"]) for k, v in R["robust"].items() if v.get("d_lab18")]
fig, ax = plt.subplots(figsize=(9, 8.6)); fig.subplots_adjust(left=0.47, right=0.97, top=0.89, bottom=0.1)
y = np.arange(len(V))[::-1]
for yi, (nm, r) in zip(y, V):
    sd = r["b"] / r["sd_x"] * R["main"]["d_lab18"]["sd_x"] if "Exposure" not in nm else r["b"]
    col = LAB if r["p"] < 0.05 else "#B98B86"
    ax.hlines(yi, r["lo"], r["hi"], color=col, lw=2)
    ax.scatter(r["b"], yi, s=36 if nm != "Main specification" else 70, color=col, zorder=3, edgecolor="white", lw=1)
    ax.text(-0.012, yi, f"{nm}  (N {r['n']})", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9.6)
ax.axvline(0, color=MUT, lw=0.9)
ax.axvline(R["main"]["d_lab18"]["b"], color=LAB, lw=0.8, ls=(0, (3, 3)), alpha=0.6)
ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.set_xlabel("Labour gain 1910 to 1918, points per SD more names (95% CI)")
ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
title(fig, "Every variant points the same way", "The primary estimate under alternative samples, measures and models. Dark red: 95% interval excludes zero.", y=0.985)
note(fig, "Exposures are standardised within each sample. Constituency models cluster standard errors by unit.")
save3(fig, "robust")

# ---------- 5. distribution of the exposure and the measurement cut
fig, ax = plt.subplots(figsize=(9, 4.6)); fig.subplots_adjust(left=0.08, right=0.97, top=0.76, bottom=0.16)
bins = np.arange(0, 145, 5)
ax.hist(U.rate[U.rate >= 10], bins=bins, color=SEQ[3], edgecolor=PAPER, lw=1.5)
ax.hist(U.rate[U.rate < 10], bins=bins, color="#C9C2B6", edgecolor=PAPER, lw=1.5)
ax.axvline(R["desc"]["national_expect"], color=INKC, lw=1, ls=(0, (4, 3)))
ax.annotate(f"British Isles dead per\n1,000 GB electors: {R['desc']['national_expect']:.0f}", xy=(R["desc"]["national_expect"], ax.get_ylim()[1] * 0.8), xytext=(R["desc"]["national_expect"] + 34, ax.get_ylim()[1] * 0.8), fontsize=9.5, fontfamily=MONO, va="center", arrowprops=dict(arrowstyle="->", color=INKC, lw=0.8))
ax.text(1, ax.get_ylim()[1] * 1.0, f"{R['n']['units_low']} big towns and boroughs\nwith no city-wide count", fontsize=9.5, fontfamily=MONO, va="top", ha="left", color=MUT, bbox=dict(fc=PAPER, ec="none", pad=2))
ax.set_xlabel("Names on community memorials per 1,000 electors of 1918"); ax.set_ylabel("Units")
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
title(fig, "How many names per thousand voters", f"{R['n']['units']} county and borough units. Units below 10 per 1,000 (grey) are measurement failures and are left out of the main models.")
save3(fig, "dist")

# ---------- header.png 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100)
ax = fig.add_axes([0.56, 0.02, 0.42, 0.96])
cm = ListedColormap(SEQ); nm = BoundaryNorm(b1, len(SEQ))
G[G.rate < 10].plot(ax=ax, color="#E4E0D8", edgecolor="white", linewidth=0.3)
G[G.rate >= 10].plot(ax=ax, column="rate", cmap=cm, norm=nm, edgecolor="white", linewidth=0.3)
ax.set_xlim(60000, 660000); ax.set_ylim(5000, 1220000); ax.set_axis_off()
fig.text(0.05, 0.89, "DATA STUDY · GREAT BRITAIN · 1910 TO 1924", fontsize=13, fontfamily=MONO, color=LAB)
fig.text(0.05, 0.83, "The war dead\nand the rise\nof Labour", fontsize=50, fontfamily=DISPLAY, fontweight="bold", color=INKC, va="top", linespacing=1.0)
fig.text(0.05, 0.33, f"Places with more names on their First World War\nmemorials swung less to Labour in 1918, not more.", fontsize=16.5, color=INKC, va="top")
fig.text(0.05, 0.08, "Dr Tristan Hotham · maps.tristanhotham.com/war-dead-labour", fontsize=12, fontfamily=MONO, color=MUT)
fig.text(0.97, 0.05, "memorial names per\n1,000 voters of 1918", fontsize=10, fontfamily=MONO, color=MUT, ha="right")
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100)
plt.close(fig)
print("figures done")
