#!/usr/bin/env python3
"""Slice the printable parts with PrusaSlicer's stock MK3S+ '0.30mm DRAFT @MK3' profile and
collect print time + filament. Body in PETG (and PLA for reference), lid in PLA or PETG at 0.20 mm, TPU parts with
the project's eSun TPU 95A presets (printer-profiles/esun-tpu95a-mk3s): FAST for estimates, and the slower forum
baseline for the committed feet G-code. Both are rebuilt here from the vendor 'Generic FLEX' + the same overrides.

Also writes committed G-code to gcode/ (forum preset): the four feet as separate objects with
'Complete individual objects' (sequential printing), and the card retainer.

PrusaSlicer 2.7 CLI can't pick vendor presets by name, so the vendor bundle is flattened
(resolving `inherits`) into one .ini per material."""
import configparser, json, re, subprocess, sys, pathlib, concurrent.futures as cf

VENDOR = "/usr/share/PrusaSlicer/profiles/PrusaResearch.ini"
PRINTER = "Original Prusa i3 MK3S & MK3S+"
PROFILES = {"draft": "0.30mm DRAFT @MK3", "speed": "0.20mm SPEED @MK3"}
META = {"inherits", "renamed_from", "alias", "compatible_printers", "compatible_printers_condition",
        "compatible_prints", "compatible_prints_condition", "printer_model", "printer_variant",
        "default_print_profile", "default_filament_profile", "default_sla_material_profile",
        "default_sla_print_profile", "thumbnails", "thumbnails_format"}
ESUN_COMMON = {   # printer-profiles/esun-tpu95a-mk3s/build_bundle.py: common
    "bed_temperature": "50", "first_layer_bed_temperature": "50", "cooling": "1", "fan_always_on": "1",
    "min_fan_speed": "70", "max_fan_speed": "90", "bridge_fan_speed": "80", "disable_fan_first_layers": "3",
    "full_fan_speed_layer": "6", "fan_below_layer_time": "60", "min_print_speed": "15",
    "filament_retract_length": "1", "filament_retract_speed": "25", "filament_deretract_speed": "15",
    "filament_retract_before_travel": "3", "filament_retract_lift": "0", "filament_wipe": "0",
    "filament_density": "1.21", "start_filament_gcode": '"M900 K0 ; Filament gcode"',
}
ESUN_FAST = dict(ESUN_COMMON, **{    # 'eSun TPU 95A FAST @MK3S'
    "first_layer_temperature": "225", "temperature": "225", "filament_max_volumetric_speed": "3.5",
    "extrusion_multiplier": "1.10", "slowdown_below_layer_time": "10"})
ESUN_FORUM = dict(ESUN_COMMON, **{   # 'eSun TPU 95A @MK3S' (forum baseline: the conservative one)
    "first_layer_temperature": "220", "temperature": "212", "filament_max_volumetric_speed": "2.4",
    "extrusion_multiplier": "1.07", "slowdown_below_layer_time": "15"})
MATS = {"PLA": ("Generic PLA", {}), "PETG": ("Generic PETG", {}), "TPU": ("Generic FLEX", ESUN_FAST),
        "TPUforum": ("Generic FLEX", ESUN_FORUM)}

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
    for prof, pname in PROFILES.items():
        cfg = {}
        for kind, name in (("printer", PRINTER), ("print", pname), ("filament", fil)):
            cfg.update({k: v for k, v in flat(kind, name).items() if k not in META})
        cfg.update(over)
        # names + model, so the G-code's printer check (M862.3 P "MK3S") passes and the header says what was used
        fname = {"TPU": "eSun TPU 95A FAST @MK3S", "TPUforum": "eSun TPU 95A @MK3S"}.get(mat, fil)
        cfg.update({"printer_model": "MK3S", "printer_settings_id": PRINTER, "print_settings_id": pname,
                    "filament_settings_id": f'"{fname}"'})
        (work / f"{mat}_{prof}.ini").write_text("\n".join(f"{k} = {v}" for k, v in cfg.items()) + "\n")

TIME_RE = re.compile(r"; estimated printing time \(normal mode\) = (.+)")
GRAM_RE = re.compile(r"; filament used \[g\] = ([\d.]+)")


def to_min(s):
    d = {"d": 1440, "h": 60, "m": 1, "s": 1 / 60}
    return sum(float(n) * d[u] for n, u in re.findall(r"(\d+)([dhms])", s))


def slice_one(stem, mat, prof, extra, key):
    out = work / f"{stem}_{key}.gcode"          # kept in slice/ (git-ignored) for inspection
    cmd = ["prusa-slicer", "--export-gcode", "--load", str(work / f"{mat}_{prof}.ini"), *extra,
           "--center", "125,105", "--ensure-on-bed", "-o", str(out), str(root / "stl" / f"{stem}.stl")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not out.exists():
        return stem, key, None, None, (r.stderr or r.stdout)[-400:]
    g = out.read_text(errors="ignore")
    t, w = TIME_RE.search(g), GRAM_RE.search(g)
    return stem, key, round(to_min(t.group(1)), 1), float(w.group(1)), None


STRONG = ["--perimeters", "4", "--fill-density", "40%", "--fill-pattern", "gyroid"]
JOBS = [  # (stl stem, material, profile, extra CLI args, result key)
    ("body", "PETG", "draft", [], "PETG"), ("body", "PLA", "draft", [], "PLA"), ("body_wall3", "PETG", "draft", [], "PETG"),
    ("lid", "PLA", "speed", [], "PLA"), ("lid", "PETG", "speed", [], "PETG"),          # v0.3 lid: 0.20 mm for the hooks
    ("retainer", "TPU", "draft", [], "TPU"),                                        # v0.4 card retainer
    ("feet", "TPU", "draft", [], "TPU"),
    ("din", "PETG", "draft", [], "PETG"), ("din", "PETG", "draft", STRONG, "PETG_strong")]
results = {}
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    for stem, mat, mins, grams, err in ex.map(lambda a: slice_one(*a), JOBS):   # mat = result key
        if err:
            print("FAIL", stem, mat, err, file=sys.stderr)
        results.setdefault(stem, {})[mat] = {"min": mins, "g": grams}
        print(stem, mat, mins, "min", grams, "g", flush=True)

# ---- committed G-code: feet, one object each, printed one after another
import trimesh
FEET_XY = [(90, 70), (160, 70), (90, 140), (160, 140)]   # 70 mm pitch: clears the MK3S 45 mm extruder radius
(root / "gcode").mkdir(exist_ok=True)
foot = trimesh.load(root / "stl" / "foot.stl")
parts = []
for i, (x, y) in enumerate(FEET_XY):
    m = foot.copy()
    m.apply_translation([x - (m.bounds[0][0] + m.bounds[1][0]) / 2, y - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    f = work / f"foot_seq_{i}.stl"; m.export(f); parts.append(str(f))
gout = root / "gcode" / "pi5_case_feet_x4_TPU_sequential.gcode"
cmd = ["prusa-slicer", "--export-gcode", "--merge", "--load", str(work / "TPUforum_draft.ini"), "--complete-objects",
       "--dont-arrange", "-o", str(gout), *parts]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode or not gout.exists():
    print("FAIL feet G-code", (r.stderr or r.stdout)[-600:], file=sys.stderr)
else:
    g = gout.read_text(errors="ignore")
    mins, grams = round(to_min(TIME_RE.search(g).group(1)), 1), float(GRAM_RE.search(g).group(1))
    results.setdefault("feet", {})["TPUforum_sequential"] = {"min": mins, "g": grams}
    print("feet TPUforum_sequential", mins, "min", grams, "g ->", gout.relative_to(root), flush=True)
# ---- committed G-code: single objects, centred on the bed
GCODE = [  # (stl stem, material, profile, extra CLI args, output name)
    ("retainer", "TPUforum", "draft", [], "pi5_case_card_retainer_TPU.gcode"),   # back face down, slower TPU preset
]
for stem, mat, prof, extra, name in GCODE:
    gout = root / "gcode" / name
    cmd = ["prusa-slicer", "--export-gcode", "--load", str(work / f"{mat}_{prof}.ini"), *extra,
           "--center", "125,105", "--ensure-on-bed", "-o", str(gout), str(root / "stl" / f"{stem}.stl")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not gout.exists():
        print("FAIL", name, (r.stderr or r.stdout)[-600:], file=sys.stderr); continue
    g = gout.read_text(errors="ignore")
    mins, grams = round(to_min(TIME_RE.search(g).group(1)), 1), float(GRAM_RE.search(g).group(1))
    results.setdefault(stem, {})[f"{mat}_gcode"] = {"min": mins, "g": grams}
    print(stem, f"{mat}_gcode", mins, "min", grams, "g ->", gout.relative_to(root), flush=True)
(root / "print_times.json").write_text(json.dumps(results, indent=1))
