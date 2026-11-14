#!/usr/bin/env python3
"""Dimensioned 2D drawing of the TPU membrane button, cut from the real STL (trimesh sections),
shown in USE orientation (button face up). Writes img/tpu_button_drawing.svg and .png.
Needs: trimesh, shapely, networkx; playwright (chromium) for the PNG."""
import json, math, pathlib
import numpy as np
import trimesh

ROOT = pathlib.Path(__file__).parent
I = json.loads((ROOT / "info.json").read_text())
mesh = trimesh.load(ROOT / "stl" / "tpu_button.stl")
ZT = I["z_tot"]
use = lambda zp: ZT - zp          # print z -> use height above the base


def f1(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


class View:
    def __init__(self, fs=1.9):
        self.el, self.fs = [], fs
        self.lo, self.hi = [1e9, 1e9], [-1e9, -1e9]

    def grow(self, u, v):
        self.lo = [min(self.lo[0], u), min(self.lo[1], v)]
        self.hi = [max(self.hi[0], u), max(self.hi[1], v)]

    def P(self, u, v):
        self.grow(u, v)
        return f"{u:.2f},{-v:.2f}"

    def loops(self, loops, cls):
        d = "".join("M" + "L".join(self.P(u, v) for u, v in lp) + "Z" for lp in loops if len(lp) > 2)
        self.el.append(f'<path class="{cls}" fill-rule="evenodd" d="{d}"/>')

    def poly(self, pts, cls, closed=True):
        self.el.append(f'<path class="{cls}" d="M' + "L".join(self.P(u, v) for u, v in pts) + ("Z" if closed else "") + '"/>')

    def rect(self, u0, v0, u1, v1, cls):
        self.poly([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], cls)

    def circle(self, u, v, r, cls):
        self.grow(u - r, v - r); self.grow(u + r, v + r)
        self.el.append(f'<circle class="{cls}" cx="{u:.2f}" cy="{-v:.2f}" r="{r:.2f}"/>')

    def line(self, u0, v0, u1, v1, cls):
        self.grow(u0, v0); self.grow(u1, v1)
        self.el.append(f'<line class="{cls}" x1="{u0:.2f}" y1="{-v0:.2f}" x2="{u1:.2f}" y2="{-v1:.2f}"/>')

    def text(self, u, v, s, cls="t", anchor="middle", rot=0, size=1.0):
        fs = self.fs * size
        w = len(s) * fs * 0.56
        if rot:
            self.grow(u - fs, v - w / 2); self.grow(u + fs * 0.3, v + w / 2)
        else:
            du = {"middle": -w / 2, "start": 0, "end": -w}[anchor]
            self.grow(u + du, v - fs * 0.3); self.grow(u + du + w, v + fs)
        tr = f' transform="rotate({rot} {u:.2f} {-v:.2f})"' if rot else ""
        self.el.append(f'<text class="{cls}" x="{u:.2f}" y="{-v:.2f}" font-size="{fs:.2f}" text-anchor="{anchor}"{tr}>{s}</text>')

    def arrow(self, u, v, du, dv):
        L, W = self.fs * 0.7, self.fs * 0.25
        n = math.hypot(du, dv); du, dv = du / n, dv / n
        bu, bv = u - du * L, v - dv * L
        pts = [(u, v), (bu - dv * W, bv + du * W), (bu + dv * W, bv - du * W)]
        self.el.append('<path class="ar" d="M' + "L".join(f"{a:.2f},{-b:.2f}" for a, b in pts) + 'Z"/>')

    def dim_h(self, u0, u1, v_ref, v_dim, label=None):
        s = 1 if v_dim > v_ref else -1
        g = self.fs * 0.35
        for u in (u0, u1):
            self.line(u, v_ref + s * g, u, v_dim + s * g, "ext")
        self.line(u0, v_dim, u1, v_dim, "dl")
        self.arrow(u0, v_dim, -1, 0); self.arrow(u1, v_dim, 1, 0)
        self.text((u0 + u1) / 2, v_dim + self.fs * 0.35, label or f1(abs(u1 - u0)), "dt")

    def dim_v(self, v0, v1, u_ref, u_dim, label=None, side=None):
        s = 1 if u_dim > u_ref else -1
        g = self.fs * 0.35
        for v in (v0, v1):
            self.line(u_ref + s * g, v, u_dim + s * g, v, "ext")
        self.line(u_dim, v0, u_dim, v1, "dl")
        if abs(v1 - v0) > self.fs * 1.6:
            self.arrow(u_dim, min(v0, v1), 0, -1); self.arrow(u_dim, max(v0, v1), 0, 1)
            self.text(u_dim - self.fs * 0.35, (v0 + v1) / 2, label or f1(abs(v1 - v0)), "dt", rot=-90)
        else:   # short: arrows outside, label beside
            self.arrow(u_dim, min(v0, v1), 0, 1); self.arrow(u_dim, max(v0, v1), 0, -1)
            self.line(u_dim, min(v0, v1) - self.fs, u_dim, max(v0, v1) + self.fs, "dl")
            a = "end" if (side or -s) < 0 else "start"
            self.text(u_dim + (self.fs * 0.4 if a == "start" else -self.fs * 0.4), (v0 + v1) / 2 - self.fs * 0.33,
                      label or f1(abs(v1 - v0)), "dt", a)

    def leader(self, u0, v0, u1, v1, s, anchor="start"):
        self.line(u0, v0, u1, v1, "ld")
        self.circle(u0, v0, self.fs * 0.14, "ldot")
        self.text(u1 + (self.fs * 0.3 if anchor == "start" else -self.fs * 0.3), v1 - self.fs * 0.32, s, "lt", anchor)

    def group(self, dx, dy, title, sub):
        x0, y0 = self.lo[0], -self.hi[1]
        w, h = self.hi[0] - self.lo[0], self.hi[1] - self.lo[1]
        body = "".join(self.el)
        hdr = (f'<text class="ttl" x="{x0:.1f}" y="{y0 - 7:.1f}" font-size="3.6">{title}</text>'
               f'<text class="sub" x="{x0:.1f}" y="{y0 - 2.6:.1f}" font-size="2.3">{sub}</text>')
        return f'<g transform="translate({dx - x0:.1f},{dy - y0 + 10:.1f})">{hdr}{body}</g>', w, h + 10


def sec(origin, normal, to2d):
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    return [] if s is None else [[to2d(p) for p in d] for d in s.discrete]


R = I["R_out"]; sw_L, sw_T, sw_H = I["sw"]; pl_off, pl_d, pl_free, pl_pt = I["pl"]
zc, zst, zsb = use(I["z_ceil"]), use(I["z_sw_t"]), use(I["z_sw_b"])
membrane, stop = I["membrane"], I["stop"]


def switch_side(v, along_x):
    if along_x:   # switch body, plunger, tabs (approximate), dashed
        v.rect(-pl_off, zsb, -pl_off + sw_L, zst, "sw")
        v.rect(-pl_d / 2, zst, pl_d / 2, zst + pl_free, "plg")
        v.circle(-pl_off + I["hole"][0], zsb + I["hole"][1], 1.2, "hid")
        x1 = -pl_off + sw_L
        for dz in (5.5, 10.5):
            v.rect(x1, zsb + dz - 0.3, x1 + 8, zsb + dz + 0.3, "tab")       # NO / NC out the end
        v.poly([(x1 - 4, zsb), (x1 - 4, zsb - 3.5), (x1 + 6, zsb - 3.5)], "tabl", closed=False)   # COM
    else:
        v.rect(-sw_T / 2, zsb, sw_T / 2, zst, "sw")
        v.rect(-pl_d / 2, zst, pl_d / 2, zst + pl_free, "plg")


# ---------------------------------------------------------------- A-A: along the switch
va = View()
va.loops(sec([0, 0.05, 0], [0, 1, 0], lambda p: (p[0], use(p[2]))), "cut")
switch_side(va, True)
top = ZT
# face widths, innermost first
va.dim_h(-I["r_boss"], I["r_boss"], top, top + 5, f"Ø{f1(2 * I['r_boss'])} stiff centre")
va.dim_h(-I["r_rim"], I["r_rim"], top, top + 10, f"Ø{f1(2 * I['r_rim'])} membrane ring")
va.dim_h(-R, R, top, top + 15, f"Ø{f1(2 * R)}")
# height chain on the right, overall beyond it
xr = R + 50
va.dim_v(zst, top, R, xr, f"{f1(top - zst)}")
va.dim_v(zsb, zst, R + 50, xr, f"{f1(sw_H)} switch")
va.dim_v(0, zsb, R, xr, f"{f1(I['base_clear'])}")
va.dim_v(0, top, R, xr + 7, f"{f1(ZT)} overall")
va.leader(11.8, top - membrane / 2, 21, top + 2.5, f"membrane {f1(membrane)} ({round(membrane / 0.2)} layers)")
zfun = use(I["z_fun"])
r_m = (I["r_throat"] + I["r_boss"]) / 2      # mid of the cone seat
z_gap = use((I["z_c0"] + I["r_rim"] - r_m + I["z_bcyl"] + I["r_boss"] - r_m) / 2)
va.leader(-r_m, z_gap, -24, zfun + 6, f"cone backup stop, {f1(stop)}", "end")
va.leader(-0.8, zst + pl_free, -24, zst + 0.5, "face lands on switch (detail C)", "end")
va.leader(-pl_off + I["hole"][0], zsb + I["hole"][1], -24, zsb + 6, "detent bumps in mounting hole", "end")
va.leader(-3, zsb - 1.5, -24, zsb - 1.5, "solid floor", "end")
va.leader(I["floor_x"] - 2, zc + 1.2, R + 14, zc + 3.5, "plunger groove")
va.leader(-pl_off + sw_L + 4, zsb + 10.5, -pl_off + sw_L + 11, zsb + 13, "NO / NC · slides in this way")
va.leader(-pl_off + sw_L + 2, zsb - 3.5, R + 9, zsb - 6.5, "COM")
ga, wa, ha = va.group(0, 0, "Section A–A", "through the plunger, along the switch · use orientation")

# ---------------------------------------------------------------- B-B: across the switch
vb = View()
vb.loops(sec([0.05, 0, 0], [1, 0, 0], lambda p: (p[1], use(p[2]))), "cut")
switch_side(vb, False)
vb.dim_h(-I["pw"], I["pw"], 0, -5, f"{f1(2 * I['pw'])}")
vb.dim_h(-R, R, top, top + 6, f"Ø{f1(2 * R)}")
gb, wb, hb = vb.group(wa + 18, 0, "Section B–B", "across the switch · pocket width")

# ---------------------------------------------------------------- top view
vt = View()
vt.circle(0, 0, R, "face")
vt.circle(0, 0, I["r_rim"], "ring")
vt.circle(0, 0, I["r_boss"], "ring")
vt.rect(-pl_off, -sw_T / 2, -pl_off + sw_L, sw_T / 2, "hid")
vt.rect(-pl_off + sw_L, -3, -pl_off + sw_L + 8, 3, "hid")
vt.circle(0, 0, pl_d / 2, "hid")
vt.line(-R - 4, 0, R + 18, 0, "cutl"); vt.text(-R - 5, -0.7, "A", "cutt", "end"); vt.text(R + 19, -0.7, "A", "cutt", "start")
vt.line(0, -R - 4, 0, R + 4, "cutl"); vt.text(0, R + 5, "B", "cutt"); vt.text(0, -R - 7, "B", "cutt")
vt.leader(-pl_off + sw_L + 4, 2, R + 8, 12, "switch slides in from here")
gt, wt, ht = vt.group(wa + 18, hb + 16, "Top", "dashed = under the face")

# ---------------------------------------------------------------- detail C: plunger, gap, stop (x3)
from functools import reduce
from shapely.geometry import Polygon, box
from shapely import affinity
K = 3.0
loops = sec([0, 0.05, 0], [0, 1, 0], lambda p: (p[0], use(p[2])))
shape = reduce(lambda a, b: a.symmetric_difference(b), [Polygon(l).buffer(0) for l in loops if len(l) > 2])
win = box(-9, zst - 2.2, 11.5, top + 0.6)
clip = affinity.scale(shape.intersection(win), K, K, origin=(0, 0))
vc = View(fs=2.0)
geoms = getattr(clip, "geoms", [clip])
vc.loops([list(g.exterior.coords) for g in geoms] + [list(h.coords) for g in geoms for h in g.interiors], "cut")
bx = [(-9 * K, (zst - 2.2) * K), (11.5 * K, (zst - 2.2) * K), (11.5 * K, (top + 0.6) * K), (-9 * K, (top + 0.6) * K)]
vc.poly(bx, "win")
sx0 = max(-pl_off, -9) * K
vc.poly([(sx0, (zst - 2.2) * K), (sx0, zst * K), (11.5 * K, zst * K)], "swl", closed=False)
vc.rect(-pl_d / 2 * K, zst * K, pl_d / 2 * K, (zst + pl_free) * K, "plg")
ztip = use(I["z_tip"]); zrec = ztip + I["pl_stop"]
vc.dim_v((zst + pl_free) * K, zrec * K, -9 * K, -10.5 * K, f"gap {I['rest_gap']:.1f}", side=-1)
vc.dim_v(zst * K, ztip * K, -9 * K, -15 * K, f"face meets switch {f1(I['face_travel'])}")
r6 = (I["r_throat"] + I["r_boss"]) / 2
zb6 = use(I["z_bcyl"] + (I["r_boss"] - r6)); zf6 = use(I["z_c0"] + (I["r_rim"] - r6))
vc.dim_v(zf6 * K, zb6 * K, r6 * K, 13.5 * K, f"cone backup {f1(stop)}")
vc.leader(2.0 * K, zrec * K - 0.2, 5.0 * K, (zst + pl_free + 1.2) * K, f"recess {I['pl_stop']:.1f}")
vc.text(-9 * K, (zst - 2.2) * K - 3.5, f"the recess stops the plunger {I['pl_stop']:.1f} above flush: travel {I['pl_travel']:.1f} for this {pl_free:.1f} plunger; it clicks if ≥ {pl_pt} (D44X max pretravel)", "sub", "start", size=0.85)
vc.text(-9 * K, (zst - 2.2) * K - 7.0, f"works unchanged for plungers {pl_pt + I['pl_stop']:.2f}–{I['face_travel'] + I['pl_stop'] - 0.3:.1f} proud (keeps ≥ 0.3 gap at rest)", "sub", "start", size=0.85)
gc, wc, hc = vc.group(0, ha + 16, "Detail C ×3", "at rest: the face lands on the switch top, not on the housing")

W = max(wa, wc, wa + 18 + max(wb, wt)) + 6
H = max(ha + 16 + hc, hb + 16 + ht) + 6
css = """
.cut{fill:#d9e2e2;stroke:#1b2a31;stroke-width:.35}
.face{fill:#d9e2e2;stroke:#1b2a31;stroke-width:.35}
.ring{fill:none;stroke:#0b6b87;stroke-width:.25;stroke-dasharray:1.2 .8}
.sw{fill:#c8322b;fill-opacity:.10;stroke:#c8322b;stroke-width:.3;stroke-dasharray:1.5 .8}
.plg{fill:#e9a23b;stroke:#b07a06;stroke-width:.2}
.tab{fill:#9aa5a8;stroke:#5a6b72;stroke-width:.15}
.tabl{fill:none;stroke:#5a6b72;stroke-width:.6}
.hid{fill:none;stroke:#c8322b;stroke-width:.25;stroke-dasharray:1.2 .8}
.ext{stroke:#0b6b87;stroke-width:.15}.dl{stroke:#0b6b87;stroke-width:.2}.ar{fill:#0b6b87}
.cutl{stroke:#0b6b87;stroke-width:.25;stroke-dasharray:4 .8 .8 .8}
.ld{stroke:#5a6b72;stroke-width:.18}.ldot{fill:#5a6b72}
text{font-family:'IBM Plex Mono',ui-monospace,monospace;fill:#1b2a31}
.dt{fill:#0b6b87}.lt{fill:#1b2a31}.cutt{fill:#0b6b87;font-weight:700}
.ttl{font-family:'Saira Condensed','Arial Narrow',sans-serif;font-weight:700;letter-spacing:.03em}
.sub{fill:#5a6b72}\n.swl{fill:none;stroke:#c8322b;stroke-width:.3;stroke-dasharray:1.5 .8}\n.win{fill:none;stroke:#5a6b72;stroke-width:.2;stroke-dasharray:1 1}\n.click{stroke:#c8322b;stroke-width:.35;stroke-dasharray:2 1}
"""
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-3 -3 {W:.1f} {H:.1f}" width="{W * 6:.0f}" height="{H * 6:.0f}">'
       f'<style>{css}</style><rect x="-3" y="-3" width="{W:.1f}" height="{H:.1f}" fill="#f9fbfa"/>{ga}{gb}{gt}{gc}</svg>')
(ROOT / "img").mkdir(exist_ok=True)
(ROOT / "img" / "tpu_button_drawing.svg").write_text(svg)

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": int(W * 6), "height": int(H * 6)})
        pg.set_content(f"<html><body style='margin:0'>{svg}</body></html>")
        pg.screenshot(path=str(ROOT / "img" / "tpu_button_drawing.png"), full_page=True)
        b.close()
except Exception as e:
    print("PNG skipped:", e)
print("drawing", round(W), "x", round(H), "mm")
