#!/usr/bin/env python3
"""Printability check in print orientation (STL as exported: z = bed).
Lists downward-facing area steeper than 45 deg from vertical, grouped by height.
Usage: python3 check_overhangs.py stl/tpu_button.stl"""
import sys, collections
import numpy as np, trimesh
m = trimesh.load(sys.argv[1])
n, a, c = m.face_normals, m.area_faces, m.triangles_center
down = (n[:, 2] < -np.cos(np.radians(45)) - 0.01) & (c[:, 2] > 0.05)   # ignore the bed face
bins = collections.defaultdict(float)
for z, ar in zip(c[down, 2], a[down]):
    bins[round(z, 1)] += ar
print(f"{sys.argv[1]}: steeper-than-45 deg overhang area {a[down].sum():.1f} mm2 (bed face excluded)")
for z in sorted(bins):
    print(f"  z={z:5.1f}  {bins[z]:6.1f} mm2")
