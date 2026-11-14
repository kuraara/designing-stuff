#!/usr/bin/env python3
"""Kinematic check with real meshes (print coords: pressing moves the boss +z).
Renders body / boss / switch from tpu_button.scad, then:
  1. slides the switch in from +X: only the detent bumps may touch it
  2. steps the centre down: reports what it touches first and at what travel
Usage: python3 check_motion.py   (needs openscad, trimesh + manifold3d)"""
import json, subprocess, tempfile, pathlib, warnings
warnings.filterwarnings("ignore")
import numpy as np, trimesh
here = pathlib.Path(__file__).parent
tmp = pathlib.Path(tempfile.mkdtemp())
M = {}
for p in ("body", "boss", "switch"):
    subprocess.run(["openscad", "-D", f'part="{p}"', "-o", str(tmp / f"{p}.stl"), str(here / "tpu_button.scad")],
                   capture_output=True, check=True)
    M[p] = trimesh.load(tmp / f"{p}.stl")
I = json.loads((here / "info.json").read_text())
# the membrane is shared by body and boss (it moves with the centre): drop it from the housing
slab = trimesh.creation.box(extents=[100, 100, I["membrane"] + 0.05]); slab.apply_translation([0, 0, (I["membrane"] + 0.05) / 2 - 0.01])
M["housing"] = M["body"].difference(slab, engine="manifold")


def vol(a, b, move=(0, 0, 0)):
    b = b.copy(); b.apply_translation(move)
    try:
        r = trimesh.boolean.intersection([a, b], engine="manifold")
        return 0.0 if r.is_empty else abs(r.volume)
    except Exception:
        return 0.0

print("1. switch slid out along +X by d mm -> overlap with the body (mm3)")
for d in (0, 1, 2, 2.6, 3, 6, 12, 20, 30):
    print(f"   d={d:4}: {vol(M['body'], M['switch'], (d, 0, 0)):7.2f}")

# switch body only (no plunger) for the face-stop check
body_sw = trimesh.creation.box(extents=[I["sw"][0], I["sw"][1], I["sw"][2]])
body_sw.apply_translation([-I["pl"][0] + I["sw"][0] / 2, 0, I["z_sw_t"] + I["sw"][2] / 2])
print("2. centre pressed by t mm -> overlap with housing / switch top / plunger (mm3)")
plunger = M["switch"].difference(body_sw, engine="manifold")
for t in np.round(np.arange(0, I["stop"] + 0.21, 0.1), 2):
    m = (0, 0, t)
    print(f"   t={t:4.1f}: housing {vol(M['housing'], M['boss'], m):6.2f}  switch top {vol(body_sw, M['boss'], m):6.2f}"
          f"  plunger {vol(plunger, M['boss'], m):6.2f}")
print(f"design: rest gap {I['rest_gap']}, face meets switch at {I['face_travel']}, cone stop at {I['stop']}")
