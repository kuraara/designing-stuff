#!/usr/bin/env python3
"""Build a PrusaSlicer config bundle with eSun TPU-95A presets for the MK3S/MK3S+.
Each preset = stock 'Generic FLEX' fully resolved from the installed vendor bundle,
then the overrides below. Sections are complete (no reliance on inherits resolution),
but keep `inherits = Generic FLEX` so PrusaSlicer shows the diffs against stock."""
import configparser, sys, pathlib

VENDOR = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/PrusaSlicer/profiles/PrusaResearch.ini"
cp = configparser.RawConfigParser(strict=False, interpolation=None)
cp.optionxform = str
cp.read(VENDOR, encoding="utf-8")
META = {"inherits", "renamed_from", "alias"}

def flat(name):
    own = dict(cp.items(f"filament:{name}"))
    out = {}
    for p in [x.strip() for x in own.get("inherits", "").split(";") if x.strip()]:
        out.update(flat(p))
    out.update(own)
    return out

base = {k: v for k, v in flat("Generic FLEX").items() if k not in META}

# Settings shared by both presets: Prusa forum thread "e-TPU esun 95A settings" (MK3S,
# Artur5 / Snowballs Chance) - cooler nozzle, fan off 3 layers then 70-90 %, short retraction.
common = {
    "filament_vendor": "eSUN",
    "filament_density": "1.21",
    "filament_colour": "#E0E0E0",
    "bed_temperature": "50",
    "first_layer_bed_temperature": "50",
    "cooling": "1",
    "fan_always_on": "1",
    "min_fan_speed": "70",
    "max_fan_speed": "90",
    "bridge_fan_speed": "80",
    "disable_fan_first_layers": "3",
    "full_fan_speed_layer": "6",
    "fan_below_layer_time": "60",
    "min_print_speed": "15",
    "filament_retract_length": "1",
    "filament_retract_speed": "25",
    "filament_deretract_speed": "15",
    "filament_retract_before_travel": "3",
    "filament_retract_lift": "0",
    "filament_wipe": "0",
    "start_filament_gcode": '"M900 K0 ; Filament gcode"',
}

presets = {
    # The forum numbers, for a known-good fallback.
    "eSun TPU 95A @MK3S": {
        "first_layer_temperature": "220",
        "temperature": "212",
        "filament_max_volumetric_speed": "2.4",
        "extrusion_multiplier": "1.07",
        "slowdown_below_layer_time": "15",
        "filament_notes": '"eSun eTPU-95A, MK3S/MK3S+ stock extruder and hotend, 0.4 nozzle.\\\\n'
                          'Forum baseline: Prusa forum thread \'e-TPU esun 95A settings\' (Artur5 Feb 2022, '
                          'Snowballs Chance Apr 2023).\\\\nMax volumetric speed 2.4 mm3/s (2x Generic FLEX).\\\\n'
                          'Dry 50-55 C for 4 h+. Loosen the extruder idler. Glue stick on smooth PEI."',
    },
    # Pushed for speed: ~3x Generic FLEX flow. More flow needs a bit more heat.
    "eSun TPU 95A FAST @MK3S": {
        "first_layer_temperature": "225",
        "temperature": "225",
        "filament_max_volumetric_speed": "3.5",
        "extrusion_multiplier": "1.10",
        "slowdown_below_layer_time": "10",
        "filament_notes": '"eSun eTPU-95A FAST, MK3S/MK3S+ stock extruder and hotend, 0.4 nozzle.\\\\n'
                          'Forum baseline temps/fan/retraction pushed to 3.5 mm3/s (about 3x Generic FLEX).\\\\n'
                          'If the extruder clicks or walls look starved: +5 C, or drop MVS to 3.0.\\\\n'
                          'If clean: try 4.0 at 230 C.\\\\nDry 50-55 C for 4 h+. Loosen the extruder idler."',
    },
}

lines = ["# PrusaSlicer config bundle: eSun eTPU-95A for Original Prusa i3 MK3S / MK3S+ (0.4 nozzle)",
         "# Import: File > Import > Import Config Bundle. Presets appear under Filament > User presets.",
         "# Built from PrusaSlicer's stock 'Generic FLEX' + overrides (see filament_notes).", ""]
for name, ov in presets.items():
    cfg = dict(base); cfg.update(common); cfg.update(ov)
    cfg["filament_settings_id"] = f'"{name}"'
    lines.append(f"[filament:{name}]")
    lines.append("inherits = Generic FLEX")
    lines += [f"{k} = {cfg[k]}" for k in sorted(cfg)]
    lines.append("")
    # plain single-preset config for CLI test slicing
    pathlib.Path(f"test_{name.split()[3] if 'FAST' in name else 'forum'}.ini").write_text(
        "\n".join(f"{k} = {cfg[k]}" for k in sorted(cfg)) + "\n")
pathlib.Path("eSun_TPU95A_MK3S.ini").write_text("\n".join(lines))
print("ok", len(lines), "lines")
