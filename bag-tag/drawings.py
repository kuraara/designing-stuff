#!/usr/bin/env python3
"""Drawings for the README, from the example STLs and the generator:

  img/fonts.png          the bundled fonts, each spelling AUBREY (via bag_tag.py --preview-only)
  img/aubrey_sections.png  base (gold) and inlay put back (blue) cut at three heights, with the
                         overlap volume (must be 0: the inlay can't collide with the base)
  img/aubrey_plate.png   both parts as they sit on the bed

Needs numpy, trimesh, manifold3d, matplotlib, Pillow, rsvg-convert, OpenSCAD + xvfb-run.
"""
import json, pathlib, subprocess, sys, tempfile
import numpy as np, trimesh, manifold3d as mf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).parent
img = root / "img"
info = json.loads((root / "info.json").read_text())
FONTS = ["Sniglet:style=ExtraBold", "Lilita One", "Titan One", "Luckiest Guy", "Chewy",
         "Bowlby One", "Bubblegum Sans"]


def font_sheet():
    tiles = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(FONTS):
            subprocess.run([sys.executable, str(root / "bag_tag.py"), "--name", "AUBREY", "--font", f,
                            "--preview-only", "--out", tmp, "--stem", f"f{i}"], check=True,
                           capture_output=True)
            png = pathlib.Path(tmp) / f"f{i}.png"
            subprocess.run(["rsvg-convert", "-h", "560", "-o", str(png), str(pathlib.Path(tmp) / f"f{i}_preview.svg")],
                           check=True)
            tiles.append((f.split(":")[0], Image.open(png).convert("RGBA")))
    W = sum(t.width for _, t in tiles) + 16 * len(tiles)
    sheet = Image.new("RGB", (W, 610), "white")
    d = ImageDraw.Draw(sheet)
    try:
        lab = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        lab = ImageFont.load_default()
    x = 0
    for name, t in tiles:
        sheet.paste(t, (x, 0), t)
        d.text((x + t.width / 2, 585), name, fill="black", font=lab, anchor="mm")
        x += t.width + 16
    sheet.save(img / "fonts.png")


def to_manifold(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                               tri_verts=np.asarray(m.faces, np.uint32)))


def sections():
    base = trimesh.load(root / "stl/aubrey_base.stl")
    inlay = trimesh.load(root / "stl/aubrey_inlay.stl")
    v = inlay.vertices.copy()
    if info["inlay_face_down"]:          # undo rotate([0,180,0]) + lift: (x,y,z) -> (-x, y, top - z)
        v[:, 0] *= -1
        v[:, 2] = info["thickness"] + info["params"].get("inlay_proud", 0) - v[:, 2]
        placed = trimesh.Trimesh(v, inlay.faces[:, ::-1])
    else:
        v[:, 2] += info["floor_t"]
        placed = trimesh.Trimesh(v, inlay.faces)
    overlap = (to_manifold(base) ^ to_manifold(placed)).volume()
    zs = [(info["floor_t"] - 0.5, "groove + bar"), (info["floor_t"] + 1.5, "pockets"),
          (info["thickness"] - 0.1, "face (inlay relief)")]
    fig, ax = plt.subplots(1, 3, figsize=(13, 9))
    for a, (z, what) in zip(ax, zs):
        for mesh, col in ((base, "#c9a400"), (placed, "#2f62c4")):
            s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if s is not None:
                for e in s.discrete:
                    a.plot(e[:, 0], e[:, 1], color=col, lw=0.8)
        a.set_aspect("equal")
        a.set_title(f"z = {z:.1f}: {what}")
    fig.suptitle(f"AUBREY: base (gold) and inlay in place (blue). "
                 f"Overlap {overlap:.3f} mm³, clearance {info['params'].get('clearance', 0.1)} mm/side")
    plt.tight_layout()
    plt.savefig(img / "aubrey_sections.png", dpi=80)
    print(f"overlap base∩inlay = {overlap:.4f} mm3")


def plate():
    w = info["width"]
    view = root / "_plate.scad"
    view.write_text(f'color("#f5d000") import("stl/aubrey_base.stl");\n'
                    f'color("#fbfaf2") translate([{w + 4},0,0]) import("stl/aubrey_inlay.stl");\n')
    subprocess.run(["xvfb-run", "-a", "openscad", "-o", str(img / "aubrey_plate.png"), "--imgsize=1100,1300",
                    "--colorscheme=Tomorrow", "--camera=0,0,0,30,0,0,0", "--viewall", "--autocenter",
                    "--projection=p", str(view)], check=True, capture_output=True)
    view.unlink()


font_sheet()
sections()
plate()
