#!/usr/bin/env python3
"""Drawings from the STLs (trimesh/matplotlib):
  img/section.png          section through the middle of the name, with the bottle as measured
  img/names_unwrapped.png  both names laid flat, as they sit on the wall
Reads info.json (from render_all.sh)."""
import json, math, pathlib
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = pathlib.Path(__file__).parent
info = json.loads((root / "info.json").read_text())
(img := root / "img").mkdir(exist_ok=True)
INK, FILL, BOT = "#1f4e79", "#9ed3f2", "#7a7a7a"


def dim(ax, p0, p1, txt, off=(0, 0), rot=0, fs=8):
    ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", lw=0.7, shrinkA=0, shrinkB=0))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], txt, ha="center",
            va="center", fontsize=fs, rotation=rot, bbox=dict(fc="white", ec="none", pad=0.8))


# ------------------------------------------------------------------ section
first = next(iter(info.values()))
b = first["bumper"]
m = trimesh.load(root / "stl" / f"{next(iter(info))}_bumper.stl")
sec = m.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
p2, _ = sec.to_2D(to_2D=np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]]))

fig, ax = plt.subplots(figsize=(11, 6.2))
for poly in p2.polygons_full:
    xy = np.array(poly.exterior.coords)
    ax.fill(xy[:, 0], xy[:, 1], fc=FILL, ec=INK, lw=0.8)

# the bottle, from the measurements (dashed)
rb, step_z = 72 / 2, b["floor"] + b["seat_depth"]
br = 5.0
corner = [(rb - br + br * math.cos(a), b["floor"] + br - br * math.sin(a))
          for a in np.linspace(math.pi / 2, 0, 12)]
half = [(0, b["floor"])] + corner + [(rb, step_z), (rb + 2, step_z + 2), (rb + 2, step_z + 9)]
for s in (1, -1):
    xs, ys = zip(*half)
    ax.plot([s * x for x in xs], ys, ls="--", color=BOT, lw=1)
ax.text(0, step_z + 6, "bottle (as measured, dashed)", ha="center", fontsize=8, color=BOT)

r_o, r_i, H = b["od"] / 2, b["bore"] / 2, b["height"]
ax.set_aspect("equal")
ax.set_xlim(-r_o - 16, r_o + 16)
ax.set_ylim(-12, step_z + 12)
ax.axis("off")
dim(ax, (-r_o, -4), (r_o, -4), f"OD {b['od']:g}")
dim(ax, (-r_i, -9), (r_i, -9), f"bore {b['bore']:g}  (bottle {b['bore'] + b['fit']:g} − fit {b['fit']:g})")
dim(ax, (-b["hole"] / 2, 4.5), (b["hole"] / 2, 4.5), f"hole {b['hole']:g}")
dim(ax, (r_o + 6, 0), (r_o + 6, H), f"{H:g}", rot=90, off=(2.2, 0))
dim(ax, (r_o + 12, b["floor"]), (r_o + 12, step_z), f"seat {b['seat_depth']:g}", rot=90, off=(2.2, 0))
dim(ax, (-r_o - 6, 0), (-r_o - 6, b["floor"]), f"floor {b['floor']:g}", off=(-6, 0))
ax.text(-r_o - 2, H + 2.5, f"name side\nraised {first['emboss']:g}", ha="center", fontsize=8)
ax.text(r_o - 2, H + 2.5, f"wall {b['wall']:g}", ha="center", fontsize=8)
if b["top_c"] > 0:
    ax.text(r_i - 9, H - 1.5, f"45° rim chamfer {b['top_c']:g}\n(sits in the bottle's step)",
            ha="right", fontsize=7)
if b["inner_r"] > 0:
    ax.text(r_i - 6, b["floor"] + 1, f"R{b['inner_r']:g}", fontsize=7)
ax.text(r_i - 3, H - 4, f"wall = one {b['wall']:g} line,\nprinted as a spiral (vase mode)\n"
        f"floor = {round(b['floor'] / 0.2)} solid layers", ha="right", fontsize=7)
ax.text(r_o + 1.5, 0.4, f"{b['bot_c']:g}×45°", fontsize=7)
ax.set_title("Section through the middle of the name (as printed: floor on the bed)", fontsize=10)
fig.tight_layout()
fig.savefig(img / "section.png", dpi=150)
plt.close(fig)
print("wrote", img / "section.png")

# ------------------------------------------------------------------ names, unwrapped
fig, axes = plt.subplots(len(info), 1, figsize=(10, 2.9 * len(info)))
axes = np.atleast_1d(axes)
for ax, (stem, d) in zip(axes, info.items()):
    m = trimesh.load(root / "stl" / f"{stem}_bumper.stl")
    v, r_o = m.vertices, d["bumper"]["od"] / 2
    r = np.hypot(v[:, 0], v[:, 1])
    th = np.arctan2(v[:, 0], -v[:, 1])
    top = r > r_o + d["emboss"] / 2 if d["emboss"] > 0 else r < r_o + d["emboss"] / 2
    faces = m.faces[np.all(top[m.faces], axis=1)]
    for f in faces:
        ax.fill(th[f] * r_o, v[f, 2], color=INK, lw=0)
    H, bc = d["bumper"]["height"], d["bumper"]["bot_c"]
    half = math.pi * r_o * 0.62
    ax.add_patch(plt.Rectangle((-half, 0), 2 * half, H, fc="#eaf6fd", ec=INK, lw=0.6, zorder=0))
    ax.axhline(bc, color=INK, lw=0.4, ls=":")
    z0, z1 = d["letters_z"]
    ax.set_xlim(-half, half)
    ax.set_ylim(-1, H + 1)
    ax.set_aspect("equal")
    ax.set_yticks([0, round(z0, 1), round(z1, 1), H])
    ax.tick_params(labelsize=7)
    ax.set_title(f"{d['name']}: capitals {d['letter_h']:g} mm, {d['name_len']:g} mm long "
                 f"({d['name_arc_deg']:g}° of the wall), raised {d['emboss']:g} mm, "
                 f"letters z {z0:g}–{z1:g}", fontsize=9)
axes[-1].set_xlabel("mm along the outside of the wall (0 = front of the print)",
                    fontsize=8)
fig.tight_layout()
fig.savefig(img / "names_unwrapped.png", dpi=150)
print("wrote", img / "names_unwrapped.png")
