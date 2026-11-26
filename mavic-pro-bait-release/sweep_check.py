#!/usr/bin/env python3
"""Geometry checks for the release (run by render_all.sh). Exits non-zero if one fails.

- the arc horn, rotated in 2.5° steps from locked to open, never touches the tub
- the reference servo, 18650 holder and boards fit the tub
- locked: the arc crosses the gap and its tip sits in the far ledge
- open: nothing of the horn is left in the gap
- running clearance between horn and tub
"""
import json, pathlib, sys
import numpy as np, trimesh, manifold3d as m3

root = pathlib.Path(__file__).parent
info = json.loads((root / "info.json").read_text())
zs, throw = info["zs"], info["a_throw"]


def man(t):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def inter(a, b):
    return m3.Manifold.batch_boolean([a, b], m3.OpType.Intersect).volume()


def box(x0, x1, y0, y1, z0, z1):
    return m3.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def rot(t, deg):   # about the servo shaft (X axis through Y=0, Z=zs)
    t = t.copy()
    t.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), [1, 0, 0], [0, 0, zs]))
    return t


tub_t = trimesh.load(root / "stl/tub.stl")
lock_t = trimesh.load(root / "_build/horn_lock.stl")
for t, n in ((tub_t, "tub"), (lock_t, "horn")):
    assert t.is_watertight, n
tub, lock = man(tub_t), man(lock_t)
fails = []

worst = 0.0
for a in np.arange(0, throw + 0.01, 2.5):
    v = inter(man(rot(lock_t, -a)), tub)
    worst = max(worst, v)
print(f"horn vs tub over 0..{throw}°: worst overlap {worst:.3f} mm3")
if worst > 0.01:
    fails.append("horn hits the tub during its travel")

for r in ("ref_servo", "ref_holder", "ref_boards"):
    v = inter(man(trimesh.load(root / f"stl/{r}.stl")), tub)
    print(f"{r} vs tub: {v:.3f} mm3")
    if v > 0.5:
        fails.append(f"{r} does not fit")

opn = man(rot(lock_t, -throw))
g = info["gap"] / 2
v1 = inter(lock, box(-40, 10, -0.5, 0.5, 0, 13))
v2 = inter(lock, box(-40, 10, g, g + 3.5, 0, 12))
v3 = inter(opn, box(-40, 10, -g, g, 0, 13))
print(f"locked: arc across gap centre {v1:.1f} mm3, tip in far ledge {v2:.1f} mm3")
print(f"open:   horn left in the gap {v3:.3f} mm3")
if v1 < 5 or v2 < 5:
    fails.append("locked arc does not span the gap")
if v3 > 0.01:
    fails.append("gap not clear when open")

q = trimesh.proximity.ProximityQuery(tub_t)
for a in (0, throw):
    d = np.abs(q.signed_distance(rot(lock_t, -a).sample(20000))).min()
    print(f"clearance horn-tub at {-a:g}°: {d:.2f} mm")
    if d < 0.3:
        fails.append(f"clearance under 0.3 mm at {-a}°")

print("FAIL: " + "; ".join(fails) if fails else "all checks passed")
sys.exit(1 if fails else 0)
