"""Step 7: index.html from code/page_template.html, filled from data/results.json, with the full-screen snippet.
10.5281/zenodo.24092044, https://doi.org/10.5281/zenodo.24092044 and https://blog.tristanhotham.com/2026/10/31/war-dead-labour/ stay as placeholders for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
# facts stated in words, checked against the data
T = R["T"]
assert T["lab_b"] < 0 and T["lab_p"] < 0.05 and T["lab_holm"] > 0.05 and T["n_robust_neg"] == T["n_robust"]
assert all(v["p"] > 0.05 for v in R["placebo"].values()) and R["later"]["d_lab22"]["b"] < T["lab_b"]
assert abs(R["later"]["d_lab24"]["b"]) < abs(R["later"]["d_lab22"]["b"]) and R["later"]["d_lib22"]["b"] > 0
assert R["main"]["coal18"]["lo"] < 0 < R["main"]["coal18"]["hi"] and R["main"]["d_lib18"]["p"] > 0.05 and R["main"]["turn18"]["p"] > 0.05
assert R["explor"]["where_stood"]["d_lab18"]["p"] > 0.2 and R["explor"]["stood"]["lab_stood18"]["b"] < 0
assert 2.7 < R["desc"]["elect_ratio"] < 3 and 0.15 < T["lab_frac_sd_y"] < 0.25
assert {"Plymouth", "Portsmouth", "Bristol, City of"} <= set(R["low_units"])
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "20261111")
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
