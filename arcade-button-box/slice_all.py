#!/usr/bin/env python3
"""Slice every STL with PrusaSlicer's stock MK3S+ '0.30mm DRAFT' profile in PLA,
PETG (and TPU for the feet) and collect estimated print time + filament use.

PrusaSlicer 2.7 CLI can't select vendor presets by name, so the vendor bundle
(PrusaResearch.ini) is flattened here (resolving `inherits`) into one config.
"""
import configparser, json, re, subprocess, sys, pathlib, concurrent.futures as cf

VENDOR = "/usr/share/PrusaSlicer/profiles/PrusaResearch.ini"
PRINTER = "Original Prusa i3 MK3S & MK3S+"
PRINT = "0.30mm DRAFT @MK3"
FILAMENTS = {"PLA": "Generic PLA", "PETG": "Generic PETG", "TPU": "Generic FLEX"}
META = {"inherits", "renamed_from", "alias", "compatible_printers", "compatible_printers_condition",
        "compatible_prints", "compatible_prints_condition", "printer_model", "printer_variant",
        "default_print_profile", "default_filament_profile", "default_sla_material_profile",
        "default_sla_print_profile", "thumbnails", "thumbnails_format"}

cp = configparser.RawConfigParser(strict=False, interpolation=None)
cp.optionxform = str
cp.read(VENDOR, encoding="utf-8")


def flat(kind, name, seen=()):
    sec = f"{kind}:{name}"
    if not cp.has_section(sec):
        raise KeyError(sec)
    own = dict(cp.items(sec))
    out = {}
    for parent in [p.strip() for p in own.get("inherits", "").split(";") if p.strip()]:
        out.update(flat(kind, parent, seen + (sec,)))
    out.update(own)
    return out


def config_for(fil):
    cfg = {}
    for kind, name in (("printer", PRINTER), ("print", PRINT), ("filament", FILAMENTS[fil])):
        cfg.update({k: v for k, v in flat(kind, name).items() if k not in META})
    return cfg


root = pathlib.Path(__file__).parent
work = root / "slice"
work.mkdir(exist_ok=True)
for fil in FILAMENTS:
    cfg = config_for(fil)
    (work / f"{fil}.ini").write_text("\n".join(f"{k} = {v}" for k, v in cfg.items()) + "\n")

TIME_RE = re.compile(r"; estimated printing time \(normal mode\) = (.+)")
GRAM_RE = re.compile(r"; filament used \[g\] = ([\d.]+)")


def to_min(s):
    d = {"d": 1440, "h": 60, "m": 1, "s": 1 / 60}
    return sum(float(n) * d[u] for n, u in re.findall(r"(\d+)([dhms])", s))


def slice_one(stl, fil):
    out = work / f"{stl.stem}_{fil}.gcode"
    cmd = ["prusa-slicer", "--export-gcode", "--load", str(work / f"{fil}.ini"),
           "--center", "125,105", "--ensure-on-bed", "-o", str(out), str(stl)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not out.exists():
        return stl.stem, fil, None, None, (r.stderr or r.stdout)[-400:]
    g = out.read_text(errors="ignore")
    t, w = TIME_RE.search(g), GRAM_RE.search(g)
    out.unlink()  # keep the workspace small
    return stl.stem, fil, round(to_min(t.group(1)), 1), float(w.group(1)), None


jobs = []
for stl in sorted((root / "stl").glob("*.stl")):
    if stl.stem.endswith("_plate_asm"):
        continue                        # assembly-orientation copy, not printed
    fils = ["TPU"] if stl.stem == "feet_tpu" else ["PLA", "PETG"]
    jobs += [(stl, f) for f in fils]

results = {}
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    for stem, fil, mins, grams, err in ex.map(lambda a: slice_one(*a), jobs):
        if err:
            print("FAIL", stem, fil, err, file=sys.stderr)
        results.setdefault(stem, {})[fil] = {"min": mins, "g": grams}
        print(stem, fil, mins, "min", grams, "g", flush=True)

(root / "print_times.json").write_text(json.dumps(results, indent=1))
