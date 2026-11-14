#!/usr/bin/env python3
"""G-code sanity check: membrane layer count and centre-boss fill.
Usage: python3 check_gcode.py gcode/<file>.gcode   (part centred at 125,105)"""
import sys, re, math, collections, json, pathlib
CX, CY = 125.0, 105.0
I = json.loads((pathlib.Path(__file__).parent / "info.json").read_text())
RB, RR = I["r_boss"], I["r_rim"]          # stiff centre / free ring outer radius
z = 0.0; x = y = None; typ = "?"
layers = collections.defaultdict(lambda: collections.defaultdict(float))  # z -> (zone,type) -> mm
for line in open(sys.argv[1], errors="ignore"):
    if line.startswith(";TYPE:"):
        typ = line[6:].strip(); continue
    if line.startswith(";Z:"):
        z = round(float(line[3:]), 2); continue
    if not line.startswith("G1"):
        continue
    m = dict(re.findall(r"([XYE])(-?[\d.]+)", line))
    nx, ny = float(m.get("X", x if x is not None else 0)), float(m.get("Y", y if y is not None else 0))
    if "E" in m and float(m["E"]) > 0 and x is not None:
        r = math.hypot((x + nx) / 2 - CX, (y + ny) / 2 - CY)
        zone = "boss" if r < RB - 0.4 else ("ring" if RB + 0.4 < r < RR - 0.4 else "body")
        layers[z][(zone, typ)] += math.hypot(nx - x, ny - y)
    x, y = nx, ny
zs = sorted(layers)
print("first layers:", zs[:6])
for zz in zs[:5]:
    ring = sum(v for (zone, t), v in layers[zz].items() if zone == "ring")
    print(f"  z={zz:4.2f}  extrusion in the free ring: {ring:7.1f} mm")
for zz in (2.0, 3.0, 6.0):
    if zz in layers:
        d = {f"{zone}/{t}": round(v) for (zone, t), v in layers[zz].items() if zone == "boss"}
        print(f"  z={zz}: boss fill {d}")
