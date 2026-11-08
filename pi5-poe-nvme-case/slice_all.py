#!/usr/bin/env python3
"""Slice the printable parts with PrusaSlicer's stock MK3S+ '0.30mm DRAFT @MK3' profile and
collect print time + filament. Body in PETG (and PLA for reference), lid/feet in TPU using
the project's 'eSun TPU 95A FAST @MK3S' preset (printer-profiles/esun-tpu95a-mk3s), rebuilt here
from the vendor 'Generic FLEX' + the same overrides.

PrusaSlicer 2.7 CLI can't pick vendor presets by name, so the vendor bundle is flattened
(resolving `inherits`) into one .ini per material."""
import configparser, json, re, subprocess, sys, pathlib, concurrent.futures as cf

VENDOR = "/usr/share/PrusaSlicer/profiles/PrusaResearch.ini"
PRINTER = "Original Prusa i3 MK3S & MK3S+"
PRINT = "0.30mm DRAFT @MK3"
META = {"inherits", "renamed_from", "alias", "compatible_printers", "compatible_printers_condition",
        "compatible_prints", "compatible_prints_condition", "printer_model", "printer_variant",
        "default_print_profile", "default_filament_profile", "default_sla_material_profile",
        "default_sla_print_profile", "thumbnails", "thumbnails_format"}
ESUN_FAST = {   # printer-profiles/esun-tpu95a-mk3s/build_bundle.py: common + FAST
    "bed_temperature": "50", "first_layer_bed_temperature": "50", "cooling": "1", "fan_always_on": "1",
    "min_fan_speed": "70", "max_fan_speed": "90", "bridge_fan_speed": "80", "disable_fan_first_layers": "3",
    "full_fan_speed_layer": "6", "fan_below_layer_time": "60", "min_print_speed": "15",
    "filament_retract_length": "1", "filament_retract_speed": "25", "filament_deretract_speed": "15",
    "filament_retract_before_travel": "3", "filament_retract_lift": "0", "filament_wipe": "0",
    "filament_density": "1.21", "start_filament_gcode": '"M900 K0 ; Filament gcode"',
    "first_layer_temperature": "225", "temperature": "225", "filament_max_volumetric_speed": "3.5",
    "extrusion_multiplier": "1.10", "slowdown_below_layer_time": "10",
}
MATS = {"PLA": ("Generic PLA", {}), "PETG": ("Generic PETG", {}), "TPU": ("Generic FLEX", ESUN_FAST)}

cp = configparser.RawConfigParser(strict=False, interpolation=None)
cp.optionxform = str
cp.read(VENDOR, encoding="utf-8")


def flat(kind, name):
    own = dict(cp.items(f"{kind}:{name}"))
    out = {}
    for parent in [p.strip() for p in own.get("inherits", "").split(";") if p.strip()]:
        out.update(flat(kind, parent))
    out.update(own)
    return out


root = pathlib.Path(__file__).parent
work = root / "slice"
work.mkdir(exist_ok=True)
for mat, (fil, over) in MATS.items():
    cfg = {}
    for kind, name in (("printer", PRINTER), ("print", PRINT), ("filament", fil)):
        cfg.update({k: v for k, v in flat(kind, name).items() if k not in META})
    cfg.update(over)
    (work / f"{mat}.ini").write_text("\n".join(f"{k} = {v}" for k, v in cfg.items()) + "\n")

TIME_RE = re.compile(r"; estimated printing time \(normal mode\) = (.+)")
GRAM_RE = re.compile(r"; filament used \[g\] = ([\d.]+)")


def to_min(s):
    d = {"d": 1440, "h": 60, "m": 1, "s": 1 / 60}
    return sum(float(n) * d[u] for n, u in re.findall(r"(\d+)([dhms])", s))


def slice_one(stem, mat):
    out = work / f"{stem}_{mat}.gcode"
    cmd = ["prusa-slicer", "--export-gcode", "--load", str(work / f"{mat}.ini"),
           "--center", "125,105", "--ensure-on-bed", "-o", str(out), str(root / "stl" / f"{stem}.stl")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not out.exists():
        return stem, mat, None, None, (r.stderr or r.stdout)[-400:]
    g = out.read_text(errors="ignore")
    t, w = TIME_RE.search(g), GRAM_RE.search(g)
    out.unlink()
    return stem, mat, round(to_min(t.group(1)), 1), float(w.group(1)), None


JOBS = [("body", "PETG"), ("body", "PLA"), ("body_wall3", "PETG"), ("lid", "TPU"), ("feet", "TPU"), ("din", "PETG")]
results = {}
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    for stem, mat, mins, grams, err in ex.map(lambda a: slice_one(*a), JOBS):
        if err:
            print("FAIL", stem, mat, err, file=sys.stderr)
        results.setdefault(stem, {})[mat] = {"min": mins, "g": grams}
        print(stem, mat, mins, "min", grams, "g", flush=True)
(root / "print_times.json").write_text(json.dumps(results, indent=1))
