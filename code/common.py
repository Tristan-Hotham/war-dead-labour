"""Shared paths, constants and helpers for the war-dead-labour study ("The war dead and the rise of Labour").

Inputs (read in place, never modified):
  WM/places.csv, memorials.csv          War memorial places and memorials (Imperial War Museums War Memorials Register,
                                        compiled in the study https://github.com/Tristan-Hotham/war-memorials).
  EL/contests.csv, candidates.csv       Every UK general election contest and candidacy 1832 to 2024
                                        (https://github.com/Tristan-Hotham/elections-since-1832).
  GEO/lad23_bsc.geojson                 Local authority districts, December 2023 (ONS, OGL v3).
  GEO/counties_uk.geojson               Ceremonial counties (England), preserved counties (Wales), council areas (Scotland).
Intermediates go to SCR, outside the repo.
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WM = os.environ.get("WDL_WM", "/home/claude/src6/war-memorials/data")
EL = os.environ.get("WDL_EL", "/home/claude/src6/elections-since-1832/data")
GEO = os.environ.get("WDL_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("WDL_FONTS", "/home/claude/ref/fonts")
SCR = os.environ.get("WDL_SCRATCH", "/home/claude/scratch/war-dead-labour")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
for d in (DATA, IMG, SCR):
    os.makedirs(d, exist_ok=True)

SLUG = "war-dead-labour"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
SEED = 20261111
ELECTIONS = ["1906", "January 1910", "December 1910", "1918", "1922", "1923", "1924"]
EKEY = {"1906": "e1906", "January 1910": "j1910", "December 1910": "d1910", "1918": "e1918", "1922": "e1922",
        "1923": "e1923", "1924": "e1924"}
REGIONS = {
    "North East": ["Durham", "Northumberland", "Tyne and Wear"],
    "North West": ["Cheshire", "Cumbria", "Greater Manchester", "Lancashire", "Merseyside"],
    "Yorkshire and the Humber": ["East Riding of Yorkshire", "North Yorkshire", "South Yorkshire", "West Yorkshire"],
    "East Midlands": ["Derbyshire", "Leicestershire", "Lincolnshire", "Northamptonshire", "Nottinghamshire", "Rutland"],
    "West Midlands": ["Herefordshire", "Shropshire", "Staffordshire", "Warwickshire", "West Midlands", "Worcestershire"],
    "East of England": ["Bedfordshire", "Cambridgeshire", "Essex", "Hertfordshire", "Norfolk", "Suffolk"],
    "London": ["Greater London"],
    "South East": ["Berkshire", "Buckinghamshire", "East Sussex", "Hampshire", "Isle of Wight", "Kent", "Oxfordshire",
                   "Surrey", "West Sussex"],
    "South West": ["Bristol", "Cornwall", "Devon", "Dorset", "Gloucestershire", "Somerset", "Wiltshire"],
}
CTY_REGION = {c: r for r, cs in REGIONS.items() for c in cs}
REGION_ORDER = list(REGIONS) + ["Wales", "Scotland"]


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None, keepdash=False):
    obj = nonan(obj) if keepdash else dash(nonan(obj))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def pval(p):
    p = float(p)
    if p < 0.001: return "below 0.001"
    if p < 0.01: return f"{p:.3f}"
    return f"{p:.2f}"


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{round(float(v))}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "s1": return f"{float(v):+.1f}"
    if f == "s2": return f"{float(v):+.2f}"
    if f == "p": return pval(v)
    if f == "pc_frac": return f"{round(float(v) * 100)}%"
    if f == "pc_frac1": return f"{float(v) * 100:.1f}%"
    raise ValueError(f)


def norm(s):
    s = str(s).lower().replace("&", "and").replace("-", " ").replace("'", "").replace(".", "")
    s = re.sub(r"\bst\b", "saint", s)
    return re.sub(r"\s+", " ", s).strip()


# party colours (house election palette): Labour red, Liberal amber, Conservative blue, Coalition purple-grey
COL = {"LAB": "#C8322B", "LIB": "#E5A021", "CON": "#2E5C9A", "COAL": "#6B5B95", "OTH": "#8C8C8C"}
