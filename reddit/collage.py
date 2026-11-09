"""Reddit collage (r/dataisbeautiful style): two maps and the election-by-election chart, light background.
Run from the study root: python3 reddit/collage.py  (needs code/ on the path and the scratch units file from 01_units.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import geopandas as gpd, pandas as pd, numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from figstyle import *

R = jload(f"{DATA}/results.json")
U = pd.read_csv(f"{DATA}/units.csv")
G = gpd.read_file(f"{SCR}/units.gpkg").merge(U, on="unit")
fig = plt.figure(figsize=(16, 10.5), dpi=160)
title(fig, "Places with more names on their First World War memorials swung less to Labour, not more",
      f"Names on First World War community memorials per 1,000 voters of 1918, and Labour's gain in vote share from 1910 to 1918, for {R['n']['units']} counties, county towns and boroughs",
      y=0.975)


def panel(rect, col, bins, cols, head, lab):
    ax = fig.add_axes(rect)
    cm = ListedColormap(cols); nm = BoundaryNorm(bins, len(cols))
    ok = (G.rate >= 10) & G[col].notna()
    G[~ok].plot(ax=ax, color="#E4E0D8", edgecolor="white", linewidth=0.3, hatch="////")
    G[ok].plot(ax=ax, column=col, cmap=cm, norm=nm, edgecolor="white", linewidth=0.3)
    ax.set_xlim(-40000, 660000); ax.set_ylim(5000, 1230000); ax.set_axis_off()
    # heading and legend sit on open sea to the west of Ireland's latitude (no land in this frame there)
    ax.text(-30000, 1180000, head, fontsize=15, fontfamily=DISPLAY, fontweight="bold", va="top", color=INKC)
    lx = ax.inset_axes([-0.04, 0.1, 0.3, 0.19])
    for i, c in enumerate(cols):
        lx.add_patch(plt.Rectangle((0, len(cols) - 1 - i), 0.9, 0.85, color=c))
        lx.text(1.15, len(cols) - 1 - i + 0.42, f"{bins[i]} to {bins[i + 1]}", fontsize=10.5, fontfamily=MONO, va="center", color=INKC)
    lx.add_patch(plt.Rectangle((0, -1.2), 0.9, 0.85, facecolor="#E4E0D8", hatch="////", edgecolor="white"))
    lx.text(1.15, -0.78, "no usable count", fontsize=10.5, fontfamily=MONO, va="center", color=MUT)
    lx.text(0, len(cols) + 0.3, lab, fontsize=10.5, fontfamily=MONO, color=MUT)
    lx.set_xlim(0, 6); lx.set_ylim(-1.4, len(cols) + 1.2); lx.axis("off")
    return ax


panel([0.0, 0.08, 0.33, 0.8], "rate", [10, 25, 35, 45, 55, 70, 140], SEQ, "Names on memorials", "per 1,000 voters")
panel([0.31, 0.08, 0.33, 0.8], "d_lab18", [-5, 5, 10, 15, 20, 30, 60], REDS, "Labour's gain, 1910 to 1918", "percentage points")
# chart
ax = fig.add_axes([0.69, 0.36, 0.29, 0.45])
rows = [("1906\nto 1910", R["placebo"]["pd_lab_0610"], R["placebo"]["pd_lib_0610"]), ("Jan to\nDec 1910", R["placebo"]["pd_lab_j_d"], R["placebo"]["pd_lib_j_d"]),
        ("1910\nto 1918", R["main"]["d_lab18"], R["main"]["d_lib18"]), ("1910\nto 1922", R["later"]["d_lab22"], R["later"]["d_lib22"]),
        ("1910\nto 1924", R["later"]["d_lab24"], R["later"]["d_lib24"])]
x = np.arange(len(rows))
ax.axvspan(-0.5, 1.5, color="#EFE9DD", lw=0); ax.axhline(0, color=MUT, lw=0.9)
for off, k, col, nm in ((-0.12, 1, LAB, "Labour"), (0.12, 2, LIB, "Liberal")):
    b = [r[k]["b"] for r in rows]
    ax.vlines(x + off, [r[k]["lo"] for r in rows], [r[k]["hi"] for r in rows], color=col, lw=2.4)
    ax.scatter(x + off, b, s=70, color=col, edgecolor="white", lw=1.5, zorder=3)
    ax.text(x[-1] + off + 0.15, b[-1], nm, fontsize=11.5, va="center", color=INKC)
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows], fontsize=10.5); ax.set_xlim(-0.5, len(rows) - 0.1)
ax.text(0.5, 7.4, "before the war:\nno link", ha="center", fontsize=10, fontfamily=MONO, color=MUT, va="top")
ax.set_ylabel("Change in party's vote share for one SD\nmore names (points, 95% interval)", fontsize=11)
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.set_ylim(-8, 8.5)
ax.set_title("More names, smaller Labour gains", fontsize=15, fontfamily=DISPLAY, fontweight="bold", loc="left", pad=12)
m = R["main"]["d_lab18"]
fig.text(0.69, 0.285, f"For each {m['sd_x']:.0f} more names per 1,000 voters,\nLabour's 1918 gain was {abs(m['b']):.1f} points smaller\n(95% CI {abs(m['hi']):.1f} to {abs(m['lo']):.1f}), and {R['T']['lab22_b_abs']:.1f} smaller by 1922.\nCompares places in the same region with similar\ndensity and 1910 vote. Modest evidence: allowing for\nfour outcomes tested, p = {m['p_holm']:.2f}. A pattern, not proof\nof cause: men in mining and munitions were often\nkept at home, and those places grew Labour fastest.",
         fontsize=11.5, va="top", color=INKC, linespacing=1.3)
note(fig, "Data: Imperial War Museums War Memorials Register (one community memorial per place); general election results 1906 to 1924 (UK Parliament, Open Parliament Licence); ONS boundaries.\n"
          "Grey hatched: big towns with no city-wide roll in the register, or no contested seat in 1910.   Dr Tristan Hotham · maps.tristanhotham.com/war-dead-labour", y=0.015)
out = os.path.join(ROOT, "reddit", "war_dead_labour_collage.png")
fig.savefig(out, dpi=160)
print(out)
