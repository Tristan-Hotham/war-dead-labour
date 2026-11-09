"""House style for the static figures: light paper, Source Serif text, Fraunces titles, IBM Plex Mono labels.
Party colours checked with the dataviz palette validator (light surface: all checks pass; the Liberal amber is below 3:1
contrast, so every amber mark is also labelled in text)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image
from common import *

for f in os.listdir(FONTS):
    if f.endswith(".ttf"):
        fm.fontManager.addfont(os.path.join(FONTS, f))
SERIF = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf").get_name()
DISPLAY = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name()
MONO = "IBM Plex Mono"
PAPER, INKC, MUT, RULE, GRID = "#FBF7EF", "#22201C", "#6B655B", "#D9D1C2", "#ECE5D8"
LAB, LIB, CON, COAL = "#C8322B", "#D99A1E", "#2E5C9A", "#2A9D8F"
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": MUT, "axes.labelcolor": INKC, "text.color": INKC,
                     "xtick.color": MUT, "ytick.color": MUT, "axes.facecolor": PAPER, "figure.facecolor": PAPER,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.unicode_minus": False,
                     "axes.titleweight": "semibold", "savefig.facecolor": PAPER})
# sequential (memorial names) and Labour scales: one hue, light to dark
SEQ = ["#F3E9DA", "#E3CBB0", "#CFA582", "#B67B58", "#94553A", "#6A3524"]
REDS = ["#FBE9E4", "#F4C2B5", "#E8907C", "#D65A47", "#B4322A", "#7F1D1A"]


def title(fig, t, sub=None, y=0.985):
    fig.text(0.012, y, t, fontsize=17, fontfamily=DISPLAY, fontweight="bold", va="top", color=INKC)
    if sub:
        fig.text(0.012, y - 0.055 * (6.5 / fig.get_figheight()), sub, fontsize=11.5, va="top", color=MUT)


def note(fig, t, y=0.012):
    fig.text(0.012, y, t, fontsize=9, fontfamily=MONO, color=MUT, va="bottom")


def save3(fig, name, paper=True, blog=True, img=True):
    """f_<name>.png 300 dpi (paper), b_<name>.png 1800 px wide (blog), img/<name>.jpg (page)"""
    rp = os.path.join(ROOT, "release", "paper"); rb = os.path.join(ROOT, "release", "blog")
    os.makedirs(rp, exist_ok=True); os.makedirs(rb, exist_ok=True)
    if paper:
        fig.savefig(f"{rp}/f_{name}.png", dpi=300)
    w = fig.get_figwidth()
    fig.savefig(f"{SCR}/b_{name}.png", dpi=1800 / w)
    im = Image.open(f"{SCR}/b_{name}.png").convert("RGB")
    if im.size[0] != 1800:
        im = im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS)
    if blog:
        im.save(f"{rb}/b_{name}.png", optimize=True)
    if img:
        im.resize((1400, round(im.size[1] * 1400 / 1800)), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=86, optimize=True)
    os.remove(f"{SCR}/b_{name}.png")
    plt.close(fig)
