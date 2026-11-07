#!/usr/bin/env python3
"""Slice the braid tool + coupon with PrusaSlicer 2.7 CLI on the stock MK3S+ printer.

Filaments: 'eSun TPU 95A FAST @MK3S' from ../printer-profiles/esun-tpu95a-mk3s (the
project's tuned TPU bundle) and stock 'Generic PETG' as the stiff alternative.
Vendor presets are flattened here (resolving `inherits`), since the 2.7 CLI can't
pick presets by name. Writes print_times.json and keeps the KEEP G-code in gcode/.

Usage: python3 slice_all.py [stl stem ...]   e.g. `python3 slice_all.py braid_coupon`
(no args = every STL in stl/; results merge into print_times.json)
"""
import configparser, json, re, subprocess, sys, pathlib, concurrent.futures as cf

root = pathlib.Path(__file__).parent
VENDOR = "/usr/share/PrusaSlicer/profiles/PrusaResearch.ini"
TPU_BUNDLE = root.parent / "printer-profiles" / "esun-tpu95a-mk3s" / "eSun_TPU95A_MK3S.ini"
PRINTER = "Original Prusa i3 MK3S & MK3S+"
PRINTS = {"0.20SPEED": "0.20mm SPEED @MK3", "0.30DRAFT": "0.30mm DRAFT @MK3"}
FILAMENTS = {"TPU": ("bundle", "eSun TPU 95A FAST @MK3S"),      # 3.5 mm3/s, 225 C
             "TPUsafe": ("bundle", "eSun TPU 95A @MK3S"),        # forum preset: 2.4 mm3/s, 220/212 C
             "PETG": ("vendor", "Generic PETG")}
# infill variants: stock = profile's own (2 perimeters + 15 % infill);
# loops = recommended: 5 perimeters fill the 4.5 mm strand solid as continuous loops.
# vs 100 % rectilinear infill (tested): 44 vs 60 min, 29 vs 583 retractions, same 11 g.
INFILL = {
    "stock": {},
    "loops": {"perimeters": "5"},
}
COMMON = {"avoid_crossing_perimeters": "1"}   # no travel over the hair slots → no strings in them
KEEP = {("TPU", "0.20SPEED", "loops"), ("TPUsafe", "0.20SPEED", "loops")}   # G-code kept in gcode/
META = {"inherits", "renamed_from", "alias", "compatible_printers", "compatible_printers_condition",
        "compatible_prints", "compatible_prints_condition", "printer_model", "printer_variant",
        "default_print_profile", "default_filament_profile", "default_sla_material_profile",
        "default_sla_print_profile", "thumbnails", "thumbnails_format"}


def load(path):
    cp = configparser.RawConfigParser(strict=False, interpolation=None)
    cp.optionxform = str
    cp.read(path, encoding="utf-8")
    return cp


vendor, bundle = load(VENDOR), load(TPU_BUNDLE)


def flat(kind, name):
    for cp in (bundle, vendor):                 # bundle presets inherit from vendor ones
        sec = f"{kind}:{name}"
        if cp.has_section(sec):
            own = dict(cp.items(sec))
            out = {}
            for parent in [p.strip() for p in own.get("inherits", "").split(";") if p.strip()]:
                out.update(flat(kind, parent))
            out.update(own)
            return out
    raise KeyError(f"{kind}:{name}")


work = root / "slice"
work.mkdir(exist_ok=True)
(root / "gcode").mkdir(exist_ok=True)


def write_cfg(fil, prn, inf):
    cfg = {}
    for kind, name in (("printer", PRINTER), ("print", PRINTS[prn]), ("filament", FILAMENTS[fil][1])):
        cfg.update({k: v for k, v in flat(kind, name).items() if k not in META})
    cfg.update(COMMON)
    cfg.update(INFILL[inf])
    p = work / f"{fil}_{prn}_{inf}.ini"
    p.write_text("\n".join(f"{k} = {v}" for k, v in cfg.items()) + "\n")
    return p


TIME_RE = re.compile(r"; estimated printing time \(normal mode\) = (.+)")
GRAM_RE = re.compile(r"; filament used \[g\] = ([\d.]+)")


def to_min(s):
    d = {"d": 1440, "h": 60, "m": 1, "s": 1 / 60}
    return sum(float(n) * d[u] for n, u in re.findall(r"(\d+)([dhms])", s))


def slice_one(stl, fil, prn, inf):
    ini = work / f"{fil}_{prn}_{inf}.ini"
    keep = (fil, prn, inf) in KEEP
    out = (root / "gcode" if keep else work) / f"{stl.stem}_{fil}_{prn}_{inf}.gcode"
    cmd = ["prusa-slicer", "--export-gcode", "--load", str(ini), "--center", "125,105",
           "--ensure-on-bed", "-o", str(out), str(stl)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not out.exists():
        return stl.stem, fil, prn, inf, None, None, (r.stderr or r.stdout)[-400:]
    g = out.read_text(errors="ignore")
    t, w = TIME_RE.search(g), GRAM_RE.search(g)
    if not keep:
        out.unlink()
    return stl.stem, fil, prn, inf, round(to_min(t.group(1)), 1), float(w.group(1)), None


jobs = []
for fil in FILAMENTS:
    for prn in PRINTS:
        for inf in INFILL:
            write_cfg(fil, prn, inf)
            for stl in sorted((root / "stl").glob("*.stl")):
                if len(sys.argv) > 1 and stl.stem not in sys.argv[1:]:
                    continue
                jobs.append((stl, fil, prn, inf))

pt = root / "print_times.json"
results = json.loads(pt.read_text()) if pt.exists() else {}
for stl, *_ in jobs:
    results.pop(stl.stem, None)          # re-sliced parts are replaced, others kept
with cf.ThreadPoolExecutor(max_workers=4) as ex:
    for stem, fil, prn, inf, mins, grams, err in ex.map(lambda a: slice_one(*a), jobs):
        if err:
            print("FAIL", stem, fil, prn, inf, err, file=sys.stderr)
        results.setdefault(stem, {}).setdefault(fil, {}).setdefault(prn, {})[inf] = {"min": mins, "g": grams}
        print(f"{stem:14s} {fil:7s} {prn:9s} {inf:5s} {mins} min {grams} g", flush=True)

pt.write_text(json.dumps(results, indent=1))
