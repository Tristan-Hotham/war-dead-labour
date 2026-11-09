"""Step 1: the county units. Every local authority district (Dec 2023) in Great Britain is put in a unit:
metropolitan districts (E08), London boroughs (E09) and English unitary authorities (E06) are their own unit, the rest of
each English ceremonial county is one unit, Wales uses the eight preserved counties, Scotland its council areas.
Writes SCR/units.gpkg (unit polygons, British National Grid) and data/units.geojson (simplified, WGS84, for the map)."""
import geopandas as gpd, pandas as pd
from shapely.ops import unary_union
from common import *

lad = gpd.read_file(f"{GEO}/lad23_bsc.geojson").to_crs(27700)
cty = gpd.read_file(f"{GEO}/counties_uk.geojson").to_crs(27700)
lad = lad[~lad.LAD23CD.str.startswith("N")].copy()
rp = lad.copy(); rp["geometry"] = lad.representative_point()
j = gpd.sjoin(rp, cty[["county", "nation", "geometry"]], how="left", predicate="within")
lad["county"] = j["county"].values; lad["nation"] = j["nation"].values
miss = lad.county.isna()
if miss.any():   # representative point offshore of the simplified counties: nearest county
    nn = gpd.sjoin_nearest(rp[miss], cty[["county", "nation", "geometry"]], how="left")
    lad.loc[miss, "county"] = nn["county"].values; lad.loc[miss, "nation"] = nn["nation"].values
assert lad.county.notna().all()


def unit_of(r):
    c = r.LAD23CD[:3]
    if c in ("E06", "E08", "E09"):
        return r.LAD23NM, {"E06": "unitary", "E08": "metropolitan district", "E09": "London borough"}[c]
    if c == "E07":
        return r.county + " (shire)", "shire county"
    if c == "W06":
        return r.county, "Welsh county"
    return r.LAD23NM, "Scottish council area"


u = lad.apply(unit_of, axis=1, result_type="expand"); lad["unit"] = u[0]; lad["utype"] = u[1]
lad["region"] = [CTY_REGION.get(c) if n == "England" else n for c, n in zip(lad.county, lad.nation)]
assert lad.region.notna().all(), lad[lad.region.isna()][["LAD23NM", "county"]]
units = lad.dissolve(by="unit", aggfunc={"utype": "first", "county": "first", "nation": "first", "region": "first"}).reset_index()
units["area_km2"] = units.area / 1e6
units.to_file(f"{SCR}/units.gpkg", driver="GPKG")
lad[["LAD23CD", "LAD23NM", "unit", "utype", "county", "nation", "region"]].to_csv(f"{DATA}/lad_to_unit.csv", index=False)
print(len(lad), "districts ->", len(units), "units;", units.utype.value_counts().to_dict())
