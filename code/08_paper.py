"""Step 8: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_War_Dead_and_Labour.pdf and .tex beside the f_*.png figures.
The DOI stays a placeholder (https://doi.org/10.5281/zenodo.24092044 printed) unless DOI is set: DOI=10.5281/zenodo.N python3 code/08_paper.py"""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_War_Dead_and_Labour"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    v0 = v
    if f == "int": return f"{int(round(float(v))):,}"
    if f in ("f0", "f1", "f2", "f3"): s = f"{float(v):.{f[1]}f}"; return s.replace("-", "$-$") if s.startswith("-") else s
    if f == "s1": return f"{float(v):+.1f}".replace("-", "$-$")
    return tex(str(v0))


def n(x, d=2):
    s = f"{x:.{d}f}"
    return s.replace("-", "$-$") if s.startswith("-") else s


def pv(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


OUTS = [("d_lab18", "Labour change"), ("coal18", "Coalition share"), ("d_lib18", "Liberal change"), ("turn18", "Turnout")]
M = R["main"]
rows = [("Memorial rate (per SD)", [f"{n(M[y]['b'])}" for y, _ in OUTS]),
        ("", [f"({n(M[y]['se'])})" for y, _ in OUTS]),
        ("95\\% CI", [f"[{n(M[y]['lo'],1)}, {n(M[y]['hi'],1)}]" for y, _ in OUTS]),
        ("$p$", [pv(M[y]["p"]) for y, _ in OUTS]),
        ("Holm-adjusted $p$", [pv(M[y]["p_holm"]) for y, _ in OUTS]),
        ("Per 10 names per 1,000", [n(M[y]["per10"]) for y, _ in OUTS]),
        ("Mean of outcome", [n(M[y]["mean_y"], 1) for y, _ in OUTS]),
        ("$N$ (units)", [str(M[y]["n"]) for y, _ in OUTS]),
        ("$R^2$", [n(M[y]["r2"]) for y, _ in OUTS])]
TM = ("\\begin{table}[tbp]\\centering\\small\\caption{Main specification: memorial names per 1,000 electors (standardised) and the four primary outcomes. OLS on county and borough units with region fixed effects, log density and December 1910 Labour and Liberal shares; HC3 standard errors in parentheses.}\\label{tab:main}"
      "\\begin{tabular}{lrrrr}\\toprule & " + " & ".join(nm for _, nm in OUTS) + "\\\\\\midrule\n" +
      "".join(f"{a} & " + " & ".join(b) + "\\\\\n" for a, b in rows) + "\\bottomrule\\end{tabular}\\end{table}")
PL = R["placebo"]
rows = "".join(f"{tex(v['name'])} & {n(v['b'])} & [{n(v['lo'])}, {n(v['hi'])}] & {pv(v['p'])} & {v['n']}\\\\\n" for k, v in PL.items())
TP = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Placebo and falsification tests. Rows 1 to 6: pre-war outcomes regressed on the First World War memorial rate (controls: density, region and the shares at the start of each window; for 1910 levels, density and region). Rows 7 to 10: the Second World War memorial rate as the exposure for the primary outcomes.}\\label{tab:placebo}"
      "\\begin{tabular}{p{8.3cm}rrrr}\\toprule Test & Coef. & 95\\% CI & $p$ & $N$\\\\\\midrule\n" + rows +
      f"Permutation within region, Labour change 1910 to 1918 (2,000 draws) & {n(R['perm']['b'])} & & {pv(R['perm']['p'])} & {R['main']['d_lab18']['n']}\\\\\n" + "\\bottomrule\\end{tabular}\\end{table}")
LT = R["later"]
rows = "".join(f"{tex(v['name'])} & {n(v['b'])} & [{n(v['lo'])}, {n(v['hi'])}] & {pv(v['p'])} & {v['n']}\\\\\n" for k, v in LT.items())
TL = ("\\begin{table}[tbp]\\centering\\small\\caption{Secondary outcomes: change in Labour and Liberal shares from December 1910 to each later election, and the all-Conservative change to 1918 (main specification; unadjusted $p$).}\\label{tab:later}"
      "\\begin{tabular}{lrrrr}\\toprule Outcome & Coef. & 95\\% CI & $p$ & $N$\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for k, v in [("main", {"name": "Main specification", **{y: M[y] for y, _ in OUTS}})] + list(R["robust"].items()):
    cells = []
    for y, _ in OUTS:
        r = v.get(y)
        cells.append(f"{n(r['b'])} ({pv(r['p'])})" if r else "")
    nn = v["d_lab18"]["n"] if v.get("d_lab18") else ""
    rows += f"{tex(v['name'])} & " + " & ".join(cells) + f" & {nn}\\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\scriptsize\\caption{Robustness: coefficient per SD of the exposure ($p$ in parentheses) under each variant (all pre-specified except the seat-level model restricted to 10 or more names per 1,000). $N$ is for the Labour change.}\\label{tab:robust}"
      "\\begin{tabular}{p{6.2cm}rrrrr}\\toprule Variant & Labour & Coalition & Liberal & Turnout & $N$\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
def dv(d, k):
    return f"{d[k]:,.0f}" if d["var"] == "elect18" else n(d[k], 2 if d["var"] in ("coverage", "ldens") else 1)


rows = "".join(f"{tex(d['name'])} & {d['n']} & {dv(d, 'mean')} & {dv(d, 'sd')} & {dv(d, 'min')} & {dv(d, 'max')}\\\\\n" for d in R["desc_table"])
TD = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Descriptive statistics, main sample (units with at least 10 memorial names per 1,000 electors).}\\label{tab:desc}"
      "\\begin{tabular}{lrrrrr}\\toprule Variable & $N$ & Mean & SD & Min & Max\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
T = R["tables"]
names = {"_z": "Memorial rate (per SD)", "ldens": "Log electors per km2", "d1910_LAB": "Labour share, Dec 1910", "d1910_LIBALL": "Liberal share, Dec 1910", "Intercept": "Constant"}
keys = ["_z", "ldens", "d1910_LAB", "d1910_LIBALL"] + sorted(k for k in T["d_lab18"]["params"] if k.startswith("C(region)")) + ["Intercept"]
rows = ""
for k in keys:
    nm = names.get(k, k.replace("C(region)[T.", "Region: ").rstrip("]"))
    rows += tex(nm).replace("km\\$\\^2\\$", "km$^2$") + " & " + " & ".join(f"{n(T[y]['params'][k])}" for y, _ in OUTS) + "\\\\\n"
    rows += " & " + " & ".join(f"({n(T[y]['bse'][k])})" for y, _ in OUTS) + "\\\\\n"
rows += "\\midrule $N$ & " + " & ".join(str(T[y]["n"]) for y, _ in OUTS) + "\\\\\n$R^2$ (adjusted) & " + " & ".join(f"{n(T[y]['r2'])} ({n(T[y]['r2_adj'])})" for y, _ in OUTS) + "\\\\\n"
TF = ("\\begin{table}[tbp]\\centering\\scriptsize\\caption{Full results of the main specification. HC3 standard errors in parentheses. Reference region: East Midlands.}\\label{tab:full}"
      "\\begin{tabular}{lrrrr}\\toprule & " + " & ".join(nm for _, nm in OUTS) + "\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
LO = R["loro"]
rows = "".join(f"{tex(rg)} & {n(LO['d_lab18']['by'][rg]['b'])} & [{n(LO['d_lab18']['by'][rg]['lo'])}, {n(LO['d_lab18']['by'][rg]['hi'])}] & {LO['d_lab18']['by'][rg]['n']} & {n(LO['coal18']['by'][rg]['b'])} & [{n(LO['coal18']['by'][rg]['lo'])}, {n(LO['coal18']['by'][rg]['hi'])}]\\\\\n" for rg in LO["d_lab18"]["by"])
TLO = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Leaving out one region at a time: Labour change 1910 to 1918 and Coalition share 1918.}\\label{tab:loro}"
       "\\begin{tabular}{lrrrrr}\\toprule Region left out & Labour & 95\\% CI & $N$ & Coalition & 95\\% CI\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", PAGE).replace("{{REPO}}", REPO)
for k, v in (("TABLE_MAIN", TM), ("TABLE_PLACEBO", TP), ("TABLE_LATER", TL), ("TABLE_ROBUST", TR), ("TABLE_DESC", TD), ("TABLE_FULL", TF), ("TABLE_LORO", TLO)):
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24092044", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:5]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:15])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
body = txt.split("References")[0] if "References" in txt else txt
print("paper", r.returncode, len(txt.split()), "words in all;", len(body.split()), "before references;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–"))
