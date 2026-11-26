#!/usr/bin/env python3
"""Drawings for the Mavic Pro bait release, from the STLs (trimesh + matplotlib).

img/release_section.png  release cross-section at the arc horn, locked and open
img/pod_drawing.png      top section, side section through the gap, lid, key numbers
img/footprint_1to1.pdf   1:1 outline of the lid's tape face, to cut out and hold under the drone

Needs stl/tub.stl, stl/lid.stl, stl/ref_*.stl, _build/horn_lock.stl and _build/horn_open.stl
(render_all.sh makes them) and info.json.
"""
import json, pathlib
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly

root = pathlib.Path(__file__).parent
info = json.loads((root / "info.json").read_text())
L = lambda p: trimesh.load(root / p)
tub, lid = L("stl/tub.stl"), L("stl/lid.stl")
servo, holder, boards = L("stl/ref_servo.stl"), L("stl/ref_holder.stl"), L("stl/ref_boards.stl")
h_lock, h_open = L("_build/horn_lock.stl"), L("_build/horn_open.stl")
(img := root / "img").mkdir(exist_ok=True)

BLUE, EDGE, ORANGE = "#9ec5e8", "#1f4e79", "#f0a830"


def polys(mesh, origin, normal, axes):
    """Section polygons projected onto the two named world axes (0=X, 1=Y, 2=Z)."""
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    if s is None:
        return []
    out = []
    for e in s.discrete:
        out.append(np.c_[e[:, axes[0]], e[:, axes[1]]])
    return out


def draw(ax, mesh, origin, normal, axes, fc=BLUE, ec=EDGE, lw=0.8, alpha=1.0, ls="-", fill=True):
    for p in polys(mesh, origin, normal, axes):
        ax.add_patch(MPoly(p, closed=True, fc=fc if fill else "none", ec=ec, lw=lw, alpha=alpha, ls=ls))


def dim(ax, a, b, txt, off=(0, 0), fs=7, rot=0):
    ax.annotate("", a, b, arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], txt, ha="center", va="center",
            fontsize=fs, rotation=rot, bbox=dict(fc="white", ec="none", pad=0.8))


# ---------------- release section ----------------
xs = info["gap_x"]
fig, axs = plt.subplots(1, 2, figsize=(12, 6.2))
for ax, horn, title in ((axs[0], h_lock, "LOCKED: arc spans the gap, tip in the far ledge"),
                        (axs[1], h_open, f"OPEN: rotated {info['a_throw']}°, gap clear")):
    # section looking forward from behind the drone: +Y (left of drone) on the viewer's left
    draw(ax, tub, [xs, 0, 0], [1, 0, 0], (1, 2))
    draw(ax, horn, [xs, 0, 0], [1, 0, 0], (1, 2), fc=ORANGE, ec="#8a5a00")
    draw(ax, servo, [xs + 9, 0, 0], [1, 0, 0], (1, 2), fc="none", ec="#c33", lw=0.6, ls="--", fill=False)
    ax.set_xlim(32, -30); ax.set_ylim(-4, 30); ax.set_aspect("equal")
    ax.axhline(0, color="k", lw=0.5)
    ax.plot([0], [info["zs"]], "k+", ms=8)
    ax.set_title(title, fontsize=9)
    ax.grid(alpha=0.25); ax.tick_params(labelsize=7)
    ax.set_xlabel("Y (mm), +Y = drone's left", fontsize=7); ax.set_ylabel("Z (mm)", fontsize=7)
g = info["gap"]
a = axs[0]
dim(a, (g / 2, -2), (-g / 2, -2), f"gap {g:g}")
a.annotate("line loop goes up\nthrough here, over the arc", (0, 1), (-14, -2.5), fontsize=7, ha="center",
           arrowprops=dict(arrowstyle="->", lw=0.6))
a.annotate("ledge (TPU)\ncarries the load", (5.2, 2.5), (20, 6), fontsize=7, ha="center",
           arrowprops=dict(arrowstyle="->", lw=0.6))
a.annotate("servo shaft", (0, info["zs"]), (-17, 25), fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.6))
a.text(31, 28, f"arc R{info['arc_ri']:g}–R{info['arc_ro']:g}, {info['arc_t']:g} thick\n"
               f"ledge under arc {info['ledge_min']:g}–{info['ledge_max']:g} mm\n"
               f"room above arc for the loop {info['loop_space_above_arc']:g} mm",
       fontsize=7, va="top", family="monospace")
fig.suptitle(f"Release section at X = {xs:g} (through the arc horn), looking forward", fontsize=10)
fig.tight_layout()
fig.savefig(img / "release_section.png", dpi=150)
plt.close(fig)

# ---------------- pod drawing ----------------
fig = plt.figure(figsize=(12, 10))
ax = fig.add_axes([0.05, 0.42, 0.55, 0.53])
z = 8
draw(ax, tub, [0, 0, z], [0, 0, 1], (0, 1))
for m, c in ((servo, "#c33"), (holder, "#3a3"), (boards, "#aa3")):
    draw(ax, m, [0, 0, z if m is not servo else info["zs"]], [0, 0, 1], (0, 1), fc=c, ec=c, alpha=0.25)
draw(ax, h_lock, [0, 0, info["zs"]], [0, 0, 1], (0, 1), fc=ORANGE, ec="#8a5a00", alpha=0.6)
ax.set_aspect("equal"); ax.set_xlim(-24, 72); ax.set_ylim(-32, 44)
ax.set_title(f"Top section at Z = {z} (nose to the right, +Y = drone's left)", fontsize=9)
ax.grid(alpha=0.25); ax.tick_params(labelsize=7)
for t, xy in (("18650 holder", (21, 24)), ("servo", (10, -6)), ("TP4056\nUSB-C", (46, 2)),
              ("MT3608", (40, -15)), ("ESP32-C3 + RX\nunder servo", (11, -20)),
              ("gap", (info["gap_x"], 0)), ("bay", (-9, -14))):
    ax.text(*xy, t, fontsize=7, ha="center", va="center")
XR, XF, YL, YR = info["x_rear"], info["x_front"], info["y_left"], info["y_right"]
dim(ax, (XR, -29), (XF, -29), f"{info['length']:g}")
dim(ax, (66, YL), (66, YR), f"{info['width']:g}", rot=90)
dim(ax, (info["gap_x"], 40), (XF, 40), f"gap to front {XF - info['gap_x']:g}")

ax2 = fig.add_axes([0.05, 0.06, 0.55, 0.32])
draw(ax2, tub, [0, 0, 0], [0, 1, 0], (0, 2))
lid_asm = lid.copy()                      # lid STL is tape face down; put it back on the tub
lid_asm.vertices[:, 2] = info["rim_z"] + info["lid_t"] - lid_asm.vertices[:, 2]
draw(ax2, lid_asm, [0, 0, 0], [0, 1, 0], (0, 2), fc="#ccc", ec="#666")
draw(ax2, servo, [0, -5, 0], [0, 1, 0], (0, 2), fc="#c33", ec="#c33", alpha=0.25)
draw(ax2, h_lock, [0, 0, 0], [0, 1, 0], (0, 2), fc=ORANGE, ec="#8a5a00")
ax2.set_aspect("equal"); ax2.set_xlim(-24, 72); ax2.set_ylim(-3, 34)
ax2.set_title("Side section at Y = 0 (through the gap and the servo shaft); tape face on top", fontsize=8)
ax2.grid(alpha=0.25); ax2.tick_params(labelsize=7)
dim(ax2, (66, 0), (66, info["rim_z"]), f"{info['rim_z']:g}", rot=90, off=(2.5, 0))

ax3 = fig.add_axes([0.64, 0.06, 0.34, 0.88]); ax3.axis("off")
ax3.text(0, 1, "\n".join([
    "Mavic Pro bait release v0.1",
    "",
    f"Pod  {info['length']:g} x {info['width']:g} x {info['height']:g} mm",
    f"     (L x W x H incl. {info['lid_t']:g} lid)",
    f"Gap  {info['gap']:g} mm, {info['x_front'] - info['gap_x']:g} mm from the front,",
    "     on the pod's Y = 0 line",
    f"     ({(info['y_left'] + info['y_right']) / 2:.1f} mm to the drone's right of the pod's centre)",
    "",
    "Release: arc pin on the servo shaft",
    f"  locked {info['a_lock']}°, open {info['a_open']}°",
    f"  servo travel {info['a_throw']}°",
    "  load is radial -> no servo torque",
    "",
    "Parts (print)",
    "  tub   TPU, open side up",
    "  lid   TPU, tape face on the bed",
    "  horn  PETG (or TPU), pocket up",
    "",
    "Hardware",
    "  4x M3x10 countersunk (self-taps into TPU)",
    "  2x servo screws (tabs to bulkhead)",
    "  horn screw ~8 mm (longer than stock)",
    "",
    "All dims mm. X forward, Y left, Z up.",
]), va="top", fontsize=9, family="monospace")
fig.savefig(img / "pod_drawing.png", dpi=150)
plt.close(fig)

# ---------------- 1:1 footprint ----------------
from matplotlib.backends.backend_pdf import PdfPages
fig = plt.figure(figsize=(8.27, 11.69))          # A4 portrait
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.axis("off")
ox, oy = 105, 160                                 # page position of pod X=20, Y=6
for p in polys(lid, [0, 0, 0.3], [0, 0, 1], (0, 1)):
    # rotate so the nose points up the page; looking DOWN at the tape face from the drone side,
    # i.e. as if lying on your back under the drone: drone's left (+Y) is on the page's right
    q = np.c_[ox + (p[:, 1] - 6), oy + (p[:, 0] - 20)]
    ax.add_patch(MPoly(q, closed=True, fc="none", ec="k", lw=0.6))
gx, gy = ox + (0 - 6), oy + (info["gap_x"] - 20)
ax.plot([gx - 4, gx + 4], [gy, gy], "r", lw=0.8); ax.plot([gx, gx], [gy - 4, gy + 4], "r", lw=0.8)
ax.text(gx - 6, gy - 2, "release gap\n(put this at the\nbalance point)", fontsize=7, color="r", ha="right")
ax.annotate("NOSE", (ox, oy + 50), (ox, oy + 58), ha="center", fontsize=9,
            arrowprops=dict(arrowstyle="<-", lw=0.8))
ax.text(105, 60, "Print at 100 % (no 'fit to page'). The 50 mm bar must measure 50 mm.\n"
        "Cut out and hold against the belly: this is the tape face of the lid, seen from below the drone.\n"
        "Drone's left is on the page's right.",
        ha="center", fontsize=8)
ax.plot([80, 130], [45, 45], "k", lw=1.2); ax.text(105, 40, "50 mm", ha="center", fontsize=8)
with PdfPages(img / "footprint_1to1.pdf") as pdf:
    pdf.savefig(fig)
plt.close(fig)
print("wrote", img / "release_section.png", img / "pod_drawing.png", img / "footprint_1to1.pdf")
