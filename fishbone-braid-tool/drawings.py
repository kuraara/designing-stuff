#!/usr/bin/env python3
"""Top view + cross-section of the braid tool from the STL (trimesh/shapely/matplotlib).
Writes img/braid_tool_drawing.png. Reads numbers from info.json (from render_all.sh)."""
import json, pathlib
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly

root = pathlib.Path(__file__).parent
info = json.loads((root / "info.json").read_text())
m = trimesh.load(root / "stl" / "braid_tool.stl")
(img := root / "img").mkdir(exist_ok=True)

def section(z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p2, _ = s.to_2D(to_2D=np.eye(4))
    return p2.polygons_full

fig = plt.figure(figsize=(9, 11))
ax = fig.add_axes([0.04, 0.04, 0.5, 0.92])
for poly in section(info["thickness"] / 2):
    ax.add_patch(MPoly(np.array(poly.exterior.coords), fc="#9ec5e8", ec="#1f4e79", lw=0.8))
    for h in poly.interiors:
        ax.add_patch(MPoly(np.array(h.coords), fc="white", ec="#1f4e79", lw=0.8))
L, W, p, w = info["length"], info["width"], info["pitch"], info["strand"]
ax.set_xlim(-W / 2 - 22, W / 2 + 26); ax.set_ylim(-12, L + 8); ax.set_aspect("equal"); ax.axis("off")

def dim(x0, y0, x1, y1, txt, off=(0, 0), rot=0):
    ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], txt, ha="center", va="center",
            fontsize=8, rotation=rot, bbox=dict(fc="white", ec="none", pad=1))

dim(-W / 2 - 8, 0, -W / 2 - 8, L, f"{L:g}", rot=90)
dim(-W / 2, -6, W / 2, -6, f"{W:g}")
y = w / 2 + 6 * p                                    # pick a mid run
dim(W / 2 + 6, y, W / 2 + 6, y + p, f"pitch {p:g}", off=(9, 0))
dim(W / 2 + 14, y + p + w / 2, W / 2 + 14, y + 2 * p - w / 2, f"slot {info['slot_gap']:g}", off=(9, 0))
ax.text(0, L + 4, "hook", ha="center", fontsize=8)
ax.set_title(f"Top view (print orientation) — {info['runs']} runs, {info['slots_total']} slots", fontsize=10)

# cross-section across a straight run
ax2 = fig.add_axes([0.6, 0.55, 0.36, 0.3])
yr = w / 2 + 4 * p
s = m.section(plane_origin=[0, yr, 0], plane_normal=[1, 0, 0])   # cut across a run
for e in s.discrete:
    if abs(e[:, 1].mean() - yr) > p / 2:
        continue
    ax2.plot(e[:, 1] - yr, e[:, 2], color="#1f4e79", lw=1.2)
    ax2.fill(e[:, 1] - yr, e[:, 2], color="#9ec5e8")
ax2.set_aspect("equal"); ax2.set_xlim(-4, 4); ax2.set_ylim(-1, info["thickness"] + 1.5)
ax2.set_title(f"Strand section {w:g} × {info['thickness']:g}\n"
              f"top round-over R{info['top_r']:g}, bottom chamfer {info['bot_c']:g}", fontsize=9)
ax2.axhline(0, color="k", lw=0.6); ax2.text(3.8, -0.6, "bed", ha="right", fontsize=7)
ax2.grid(alpha=0.3); ax2.set_xlabel("mm", fontsize=7); ax2.tick_params(labelsize=7)

ax3 = fig.add_axes([0.6, 0.1, 0.36, 0.35]); ax3.axis("off")
ax3.text(0, 1, "\n".join([
    "Fishbone braid tool v0.2",
    f"Length {L:g}  Width {W:g}  Thickness {info['thickness']:g}",
    f"Strand {w:g} wide, pitch {p:g} → slot gap {info['slot_gap']:g}",
    f"Slots: {info['slots_total']} ({info['slots_a']} one side, {info['slots_b']} other)",
    f"Hook gap {info['hook_gap']:g}, stem {info['stem']:g}",
    "",
    "Print flat as shown. No supports.",
    "All dims mm.",
]), va="top", fontsize=9, family="monospace")
fig.savefig(img / "braid_tool_drawing.png", dpi=150)
print("wrote", img / "braid_tool_drawing.png")
