#!/usr/bin/env python3
"""2D drawings of the Pi 5 case, cut from the real STLs (trimesh sections) with the board stack
drawn from the layout INFO echoed by pi5_case.scad. Writes drawings.json {view: svg}."""
import json, math, pathlib
from functools import reduce
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).parent


def f1(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


class View:
    """SVG elements in mm, v-up coordinates; optional uniform scale for details."""

    def __init__(self, width_hint, scale=1.0):
        self.el = []
        self.k = scale
        self.fs = max(3.6, min(7.0, width_hint * scale * 0.034))
        self.lo = [1e9, 1e9]
        self.hi = [-1e9, -1e9]

    def grow(self, u, v):
        self.lo = [min(self.lo[0], u), min(self.lo[1], v)]
        self.hi = [max(self.hi[0], u), max(self.hi[1], v)]

    def P(self, u, v):
        u, v = u * self.k, v * self.k
        self.grow(u, v)
        return f"{u:.2f},{-v:.2f}"

    def loops(self, loops, cls):
        d = "".join("M" + "L".join(self.P(u, v) for u, v in lp) + "Z" for lp in loops if len(lp) > 2)
        if d:
            self.el.append(f'<path class="{cls}" fill-rule="evenodd" d="{d}"/>')

    def poly(self, pts, cls, closed=True):
        d = "M" + "L".join(self.P(u, v) for u, v in pts) + ("Z" if closed else "")
        self.el.append(f'<path class="{cls}" d="{d}"/>')

    def rect(self, u0, v0, u1, v1, cls, rx=0):
        a, b = sorted((u0 * self.k, u1 * self.k)); c, d = sorted((v0 * self.k, v1 * self.k))
        self.grow(a, c); self.grow(b, d)
        self.el.append(f'<rect class="{cls}" x="{a:.2f}" y="{-d:.2f}" width="{b - a:.2f}" height="{d - c:.2f}" rx="{rx * self.k:.2f}"/>')

    def circle(self, u, v, r, cls):
        u, v, r = u * self.k, v * self.k, r * self.k
        self.grow(u - r, v - r); self.grow(u + r, v + r)
        self.el.append(f'<circle class="{cls}" cx="{u:.2f}" cy="{-v:.2f}" r="{r:.2f}"/>')

    def line(self, u0, v0, u1, v1, cls):
        self.el.append(f'<line class="{cls}" x1="{u0 * self.k:.2f}" y1="{-v0 * self.k:.2f}" x2="{u1 * self.k:.2f}" y2="{-v1 * self.k:.2f}"/>')
        self.grow(u0 * self.k, v0 * self.k); self.grow(u1 * self.k, v1 * self.k)

    # text / dimension helpers take model coordinates; offsets are in paper units (fs)
    def text(self, u, v, s, cls="t", anchor="middle", rot=0, size=1.0, du=0.0, dv=0.0):
        fs = self.fs * size
        U, V = u * self.k + du, v * self.k + dv
        w = len(s) * fs * 0.6
        if rot:
            self.grow(U - fs, V - w / 2); self.grow(U + fs * 0.3, V + w / 2)
        else:
            off = {"middle": -w / 2, "start": 0, "end": -w}[anchor]
            self.grow(U + off, V - fs * 0.3); self.grow(U + off + w, V + fs)
        tr = f' transform="rotate({rot} {U:.2f} {-V:.2f})"' if rot else ""
        self.el.append(f'<text class="{cls}" x="{U:.2f}" y="{-V:.2f}" font-size="{fs:.2f}" text-anchor="{anchor}"{tr}>{s}</text>')

    def arrow(self, U, V, du, dv):
        L = self.fs * 0.75; Wd = self.fs * 0.28
        n = math.hypot(du, dv); du, dv = du / n, dv / n
        bu, bv = U - du * L, V - dv * L
        pts = [(U, V), (bu - dv * Wd, bv + du * Wd), (bu + dv * Wd, bv - du * Wd)]
        self.el.append('<path class="ar" d="M' + "L".join(f"{a:.2f},{-b:.2f}" for a, b in pts) + 'Z"/>')

    def dim_h(self, u0, u1, v_ref, off, label=None, scale_label=True):
        """horizontal dim between model u0..u1; dimension line `off` font-sizes from v_ref (paper)."""
        k = self.k; u0, u1 = sorted((u0, u1)); U0, U1, Vr = u0 * k, u1 * k, v_ref * k
        Vd = Vr + off * self.fs
        s = 1 if off > 0 else -1; g = self.fs * 0.4
        for U in (U0, U1):
            self._l(U, Vr + s * g, U, Vd + s * g, "ext")
        self._l(U0, Vd, U1, Vd, "dl")
        inside = abs(U1 - U0) > self.fs * 2
        if inside:
            self.arrow(U0, Vd, -1, 0); self.arrow(U1, Vd, 1, 0)
        else:
            self.arrow(U0, Vd, 1, 0); self.arrow(U1, Vd, -1, 0)
        lab = label or f1(abs(u1 - u0))
        w = len(lab) * self.fs * 0.56
        if inside or w < abs(U1 - U0):
            self._t((U0 + U1) / 2, Vd + self.fs * 0.35, lab, "dt", "middle")
        else:
            self._t(max(U0, U1) + self.fs * 0.9, Vd - self.fs * 0.35, lab, "dt", "start")

    def dim_v(self, v0, v1, u_ref, off, label=None):
        k = self.k; v0, v1 = sorted((v0, v1)); V0, V1, Ur = v0 * k, v1 * k, u_ref * k
        Ud = Ur + off * self.fs
        s = 1 if off > 0 else -1; g = self.fs * 0.4
        for V in (V0, V1):
            self._l(Ur + s * g, V, Ud + s * g, V, "ext")
        self._l(Ud, V0, Ud, V1, "dl")
        inside = abs(V1 - V0) > self.fs * 2
        if inside:
            self.arrow(Ud, V0, 0, -1 if V0 < V1 else 1); self.arrow(Ud, V1, 0, 1 if V0 < V1 else -1)
        else:
            lo, hi = min(V0, V1), max(V0, V1)
            self.arrow(Ud, lo, 0, 1); self.arrow(Ud, hi, 0, -1)
        lab = label or f1(abs(v1 - v0))
        w = len(lab) * self.fs * 0.56
        if inside and w < abs(V1 - V0) * 1.1:
            self._t(Ud - self.fs * 0.35, (V0 + V1) / 2, lab, "dt", "middle", rot=-90)
        else:
            self._t(Ud + (self.fs * 0.5 if off > 0 else -self.fs * 0.5), max(V0, V1) + self.fs * 0.6, lab, "dt",
                    "start" if off > 0 else "end")

    def leader(self, u0, v0, u1, v1, s, anchor="start"):
        """u0,v0 model point; u1,v1 model point for the label end."""
        self.line(u0, v0, u1, v1, "ld")
        self.circle(u0, v0, self.fs * 0.15 / self.k, "ldot")
        self.text(u1, v1, s, "lt", anchor, du=(self.fs * 0.3 if anchor == "start" else -self.fs * 0.3), dv=-self.fs * 0.32)

    def _l(self, U0, V0, U1, V1, cls):   # paper units
        self.el.append(f'<line class="{cls}" x1="{U0:.2f}" y1="{-V0:.2f}" x2="{U1:.2f}" y2="{-V1:.2f}"/>')
        self.grow(U0, V0); self.grow(U1, V1)

    def _t(self, U, V, s, cls, anchor, rot=0):
        self.text(U / self.k, V / self.k, s, cls, anchor, rot)

    def svg(self, pad=None):
        pad = self.fs * 1.2 if pad is None else pad
        x0, y0 = self.lo[0] - pad, -(self.hi[1] + pad)
        w, h = self.hi[0] - self.lo[0] + 2 * pad, self.hi[1] - self.lo[1] + 2 * pad
        return (f'<svg class="dwg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" xmlns="http://www.w3.org/2000/svg" '
                f'role="img">' + "".join(self.el) + "</svg>")


def section(mesh, origin, normal, to2d):
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    if s is None:
        return []
    return [[to2d(p) for p in np.round(d, 3)] for d in s.discrete]


def clip(loops, u0, v0, u1, v1):
    """even-odd region of the loops, clipped to a box -> list of loops"""
    polys = [Polygon(lp).buffer(0) for lp in loops if len(lp) > 2]
    if not polys:
        return []
    reg = reduce(lambda a, b: a.symmetric_difference(b), polys).intersection(box(u0, v0, u1, v1))
    out = []
    for g in getattr(reg, "geoms", [reg]):
        if g.is_empty or g.geom_type != "Polygon":
            continue
        out.append(list(g.exterior.coords))
        out += [list(r.coords) for r in g.interiors]
    return out


I = json.loads((ROOT / "info" / "info.json").read_text())
body = trimesh.load(ROOT / "stl" / "body_asm.stl")
lid = trimesh.load(ROOT / "stl" / "lid_asm.stl")
ret = trimesh.load(ROOT / "stl" / "retainer_asm.stl")
bw, bl, pcb = I["bw"], I["bl"], I["pcb"]
zd, zdt, zpb, zpt = I["zd"], I["z_duo_t"], I["z_pi_b"], I["z_pi_t"]
zhb, zht, zhc, zr, H = I["z_hat_b"], I["z_hat_t"], I["z_hat_c"], I["z_roof"], I["H"]
zf, zdlb, zplb = I["zf"], I["z_dlb"], I["z_plb"]
yo0, yo1 = I["y_o"]; yi0, yi1 = I["y_in"]
xm, xs, xei, xeo = I["x_mouth"], I["x_skirt"], I["x_end_in"], I["x_end_out"]
lid_t = I["lid_t"]; xl = xm - lid_t
drop = I["drive_drop"]
fg, fh_, pl, dl = I["fence_gap"], I["fence_h"], I["pi_ledge"], I["duo_ledge"]
hat_l, hat_w, hat_gap, hat_comp = I["hat"]
sx0, sx1, scz, sz0, sz1 = I["side"]
yz = lambda p: (p[1], p[2])
xz = lambda p: (p[0], p[2])
xy = lambda p: (p[0], p[1])
out = {}


def stack_yz(v):
    v.rect(dl + 1, zd - drop, bw - dl - 1, zd - 0.01, "ssd", 1)
    v.rect(0, zd, bw, zdt, "pcb")
    v.rect(0, zpb, bw, zpt, "pcb")
    v.rect(-(hat_w - bw) / 2, zhb, bw + (hat_w - bw) / 2, zht, "pcb")
    v.rect(-(hat_w - bw) / 2 + 1, zht, bw + (hat_w - bw) / 2 - 1, zhc, "env", 1)


# ---------------------------------------------------------------- A-A cross-section
xa = 54.0     # between side-vent segments: full wall
v = View(yo1 - yo0)
v.loops(section(body, [xa, 0, 0], [1, 0, 0], yz), "cutf")
stack_yz(v)
v.leader(bw * 0.72, (zht + zhc) / 2, yo1 + 3, zhc + 2, "PoE HAT (G) + parts")
v.leader(bw * 0.8, zpt - 0.8, yo1 + 3, zpt + 5, "Pi 5 on upper ledge")
v.leader(bw - 2, zplb + 2, yo1 + 3, zplb + 1, "upper lip")
v.leader(bw * 0.85, zdt - 0.8, yo1 + 3, zdt - 3, "NVMe Base Duo on lower ledge")
v.leader(bw * 0.7, zd - drop / 2, yo1 + 3, zd - drop / 2 - 3.5, "SSDs, underside")
v.dim_h(yo0, yo1, 0, -2.4, f"{f1(yo1 - yo0)} outside")
v.dim_h(yi0, yi1, H, 1.6, f"{f1(yi1 - yi0)} inside")
v.dim_h(I["low_in"], bw - I["low_in"], zf, 1.0, f"{f1(bw - 2 * I['low_in'])} bay")
v.dim_h(yi0, 0, zr, -1.4)
v.dim_v(0, H, yo0, -4.4, f"{f1(H)} outside")
v.dim_v(zf, zd, yo0, -1.8)
v.dim_v(zdt, zpb, yo0, -1.8)
v.dim_v(zpt, zhb, yo0, -1.8)
v.dim_v(zht, zr, yo0, -1.8)
out["a"] = v.svg()


# ---------------------------------------------------------------- ledge details (scale 3)
def ledge_detail(x, title_note, window=False):
    K = 3
    v = View(14, K)
    u0, u1, v0, v1 = yo0 - 0.6, 6.0, zd - drop - 0.6, zpt + 2.4
    v.loops(clip(section(body, [x, 0, 0], [1, 0, 0], yz), u0, v0, u1, v1), "cutf")
    v.rect(-0.01, zd, u1, zdt, "pcb")
    v.rect(-0.01, zpb, u1, zpt, "pcb")
    v.rect(dl + 1, zd - drop, u1, zd - 5, "ssd")
    v.line(0, v0 - 0.3, 0, v1 + 0.3, "cl")
    v.text(0, v1, "board edge", "zt", "middle", dv=v.fs * 3.0)
    v.leader(4.5, zpb + 0.8, 8.0, zpb + 2.8, "Pi", "start")
    v.leader(4.5, zd + 0.8, 8.0, zd + 3.2, "Duo", "start")
    v.leader(5.0, zd - 6.5, 8.0, zd - 7.5, "SSD zone", "start")
    if window:
        v.rect(yo0 - 0.6, I["side"][2] - 5, -1.6, zpt + 2.4, "plug", 0.6)
        v.leader(-4.5, zpb, -9.5, zpb + 3.4, "plug overmold", "end")
    v.dim_h(yo0, yi0, v1, 1.2, f"{f1(I['wall'])}")
    v.dim_h(yi0, 0, v1, 1.2, f"{f1(-yi0)} air")
    if not window:
        v.dim_h(-fg, pl, zpb, 4.0, f"{f1(fg + pl)} ledge")
        v.dim_h(0, pl, zpb, 2.2, f"{f1(pl)}")
        v.dim_v(zpb, zpb + fh_, yo0 - 0.6, -1.5, f"{f1(fh_)}")
        v.dim_v(zd, zd + fh_, yo0 - 0.6, -1.5, f"{f1(fh_)}")
    else:
        v.dim_h(-I["plug_reach"], 0, zplb, -1.6, f"{f1(I['plug_reach'])}")
        v.dim_v(zpb - I["plug_step"], zpb, yo0 - 0.6, -1.5, f"{f1(I['plug_step'])}")
    v.dim_h(0, dl, v0, -1.6, f"{f1(dl)}")
    v.dim_h(0, I["low_in"], v0, -3.4, f"{f1(I['low_in'])}")
    v.dim_v(zplb, zpb, u1, 1.2, f"{f1(I['pi_lip_t'])}")
    v.dim_v(zdlb, zd, u1, 1.2, f"{f1(I['duo_lip_t'])}")
    v.dim_v(zdt, zpb, u1, 3.0, f"{f1(zpb - zdt)}")
    return v.svg()


out["ledge"] = ledge_detail(54.0, "")
out["ledge_win"] = ledge_detail(I["usbc_x"], "", window=True)

# ---------------------------------------------------------------- B-B long section through the middle
yb = 28.0
v = View(xeo - xl)
v.loops(section(body, [0, yb, 0], [0, 1, 0], xz), "cutf")
v.loops(section(lid, [0, yb, 0], [0, 1, 0], xz), "cutl")
v.loops(section(ret, [0, yb, 0], [0, 1, 0], xz), "cutr")
v.rect(2, zd - drop, 83, zd - 0.01, "ssd", 1)
v.rect(0, zd, bl, zdt, "pcb"); v.rect(0, zpb, bl, zpt, "pcb")
v.rect(0, zhb, hat_l, zht, "pcb"); v.rect(1, zht, hat_l - 1, zhc, "env", 1)
v.rect(bl - 18 + I["port_over"], zpt, bl + I["port_over"], zpt + 16, "jack", 0.8)
ya, yb2 = zpt + 0.6, zdt + 1.0
r = (ya - yb2) / 2; cz = (ya + yb2) / 2
arc = [(2.5, ya), (0.5, ya)] + [(0.5 - r * math.sin(t), cz + r * math.cos(t)) for t in np.linspace(0, math.pi, 24)] + [(2.5, yb2)]
v.poly(arc, "ribbon", closed=False)
v.leader(-0.5 - r, cz + 3, xl - 3, zhb, "PCIe ribbon loop", "end")
v.leader(xl + 0.6, zd + 2, xl - 3, zd + 8, "lid", "end")
v.leader(bl - 4, zpt + 9, bl - 14, zhc + 1.5, "USB-A", "end")
v.dim_h(xl, xeo, 0, -2.6, f"{f1(xeo - xl)} overall")
v.dim_h(xm, xeo, 0, -4.4, f"{f1(xeo - xm)} body")
v.dim_h(xs, 0, H, 1.4, f"{f1(-xs)}")
v.dim_h(xl, xm, H, 3.2, f"{f1(lid_t)}")
v.dim_h(xm, xs, H, 1.4, f"{f1(xs - xm)}")
v.dim_h(bl, xei, H, 1.4, f"{f1(xei - bl)}")
v.dim_h(0, bl, H, 3.2, f"{f1(bl)} boards")
out["b"] = v.svg()

# ---------------------------------------------------------------- C-C long section along the GPIO-side ledges and retainer fingers
yc = bw - 0.6
v = View(xeo - xl)
v.loops(section(body, [0, yc, 0], [0, 1, 0], xz), "cutf")
v.loops(section(lid, [0, yc, 0], [0, 1, 0], xz), "cutl")
v.loops(section(ret, [0, yc, 0], [0, 1, 0], xz), "cutr")
RT = I["ret"]; e0 = RT["edge"]
v.rect(e0, zd, e0 + bl, zdt, "pcb"); v.rect(e0, zpb, e0 + bl, zpt, "pcb")
v.rect(e0, zhb, e0 + hat_l, zht, "pcb")
v.leader(RT["tip"] - 0.3, zpb + 2, xl - 3, zhb, "TPU retainer finger on the Pi corner", "end")
v.leader(RT["tip"] - 0.3, zd + 2, xl - 3, zd + 7, "finger on the Duo corner", "end")
v.leader(-4, zr - 1.2, xl - 3, zr + 4, "TPU card retainer", "end")
v.leader(40, zpb - 1.5, 46, zhb - 6, "upper lip, full length", "start")
v.leader(40, zd - 1.5, 46, -4, "lower lip, full length", "start")
v.leader(xei + 0.2, zd + 0.8, xei - 8, zd + 5, "boards stop on the end wall", "end")
v.dim_h(RT["back"], RT["front"], zr, 1.6, f"{f1(RT['front'] - RT['back'])} ring")
v.dim_v(0, H, xl, -1.8, f"{f1(H)}")
out["c"] = v.svg()

# ---------------------------------------------------------------- side elevation (HDMI / USB-C side)
ye = yo0 + I["wall"] / 2
v = View(xeo - xl)
v.loops(section(body, [0, ye, 0], [0, 1, 0], xz), "panel")
v.loops(section(lid, [0, yo0 + 0.6, 0], [0, 1, 0], xz), "panell")
fd, fh = I["foot"]
for x in I["foot_x"]:
    v.rect(x - fd / 2, -fh + 0.6, x + fd / 2, 0.6, "foot", 1)
for x, lab in [(I["usbc_x"], "USB-C")] + [(x, f"HDMI{i}") for i, x in enumerate(I["hdmi_x"])]:
    v.circle(x, scz, 0.6, "port")
    v.text(x, sz1, lab, "lt", dv=v.fs * 0.5, size=0.85)
v.dim_h(sx0, sx1, sz1, 3.2, f"{f1(sx1 - sx0)} × {f1(sz1 - sz0)} window")
v.dim_h(xl, I["usbc_x"], 0, -3.6 - fh / v.fs, f"{f1(I['usbc_x'] - xl)} to USB-C")
v.dim_v(0, scz, xeo, 1.6, f"{f1(scz)}")
v.dim_v(-fh + 0.6, 0, xl, -1.8, f"{f1(fh - 0.6)}")
v.leader(62, sum(I["sv_z"]) / 2, 70, sz1 + 4, "side vents", "start")
sxw = I["snap_x"]; szs = I["snap_z"]
v.leader((sxw[0] + sxw[1]) / 2, szs[1], xl - 2, H + 3, "latch window", "end")
v.leader((sxw[0] + sxw[1]) / 2, szs[0], xl - 2, szs[0] - 9, "vent (v0.2 snap window)", "end")
out["side"] = v.svg()

# ---------------------------------------------------------------- USB end (seen from the end)
xe = xeo - I["end_t"] / 2
v = View(yo1 - yo0)
ue = lambda p: (yo1 + yo0 - p[1], p[2])
v.loops(section(body, [xe, 0, 0], [1, 0, 0], ue), "panel")
ey, ew, eh = I["eth"]; uw, uh = I["usb_cut"]; pz = I["port_z0"]
m = lambda y: yo1 + yo0 - y
v.text(m(ey), pz + eh / 2, "ETH (PoE)", "lt", size=0.85, dv=-v.fs * 0.3)
for y in I["usb_y"]:
    v.text(m(y), pz + uh / 2, "USB", "lt", size=0.85, dv=-v.fs * 0.3)
v.dim_h(m(ey) - ew / 2, m(ey) + ew / 2, pz + eh, 1.2)
v.dim_h(m(I["usb_y"][0]) - uw / 2, m(I["usb_y"][0]) + uw / 2, pz + uh, 1.2)
v.dim_v(pz, pz + uh, m(I["usb_y"][1]) - uw / 2, -1.8)
v.dim_v(0, pz, yo1, 1.6, f"{f1(pz)}")
v.dim_h(m(ey), yo1, 0, -1.8, f"{f1(ey - yo0)}")
v.dim_h(m(I["usb_y"][0]), yo1, 0, -3.5, f"{f1(I['usb_y'][0] - yo0)}")
v.dim_h(m(I["usb_y"][1]), yo1, 0, -5.2, f"{f1(I['usb_y'][1] - yo0)}")
out["end"] = v.svg()

# ---------------------------------------------------------------- top / bottom
v = View(xeo - xl)
v.loops(section(body, [0, 0, H - I["roof_t"] / 2], [0, 0, 1], xy), "panel")
v.loops(section(lid, [0, 0, H - 1.2], [0, 0, 1], xy), "panell")
v.dim_h(xl, xeo, yo0, -1.8, f"{f1(xeo - xl)}")
v.dim_v(yo0, yo1, xeo, 1.6, f"{f1(yo1 - yo0)}")
v.text(xl + lid_t / 2, yo1, "LID", "cutlbl", dv=v.fs * 0.6)
out["top"] = v.svg()

v = View(xeo - xl)
xyb = lambda p: (p[0], yo1 + yo0 - p[1])
v.loops(section(body, [0, 0, 1.0], [0, 0, 1], xyb), "panel")
v.loops(section(lid, [0, 0, 1.0], [0, 0, 1], xyb), "panell")
for x in I["foot_x"]:
    for y in (I["y_foot"], bw - I["y_foot"]):
        v.circle(x, yo1 + yo0 - y, fd / 2, "footc")
v.dim_h(I["foot_x"][0], I["foot_x"][1], yo0, -1.8, f"{f1(I['foot_x'][1] - I['foot_x'][0])} feet")
v.dim_v(yo1 + yo0 - I["y_foot"], yo1 + yo0 - (bw - I["y_foot"]), xeo, 1.6)
out["bottom"] = v.svg()

# ---------------------------------------------------------------- lid, seen from inside
v = View(yo1 - yo0)
ui = lambda p: (yo1 + yo0 - p[1], p[2])
v.loops(section(lid, [xm - lid_t / 2, 0, 0], [1, 0, 0], ui), "panell")
v.loops(section(lid, [xm + 3.4, 0, 0], [1, 0, 0], ui), "cutl")
v.loops(section(lid, [-3, 0, 0], [1, 0, 0], ui), "cutl")
LT = I["latch"]
v.leader(m(yi0 + 0.8), (LT["free"] + LT["root"]) / 2 + 3, yo1 + 4, LT["root"] + 2, "flexing arm, fixed at the top", "start")
v.leader(m(yi0 - 0.5), LT["z"], yo1 + 4, LT["z"] - 6, "latch hook", "start")
v.dim_v(LT["free"], LT["root"], yo0, -1.8, f"{f1(LT['root'] - LT['free'])} arm")
v.dim_h(yo0, yo1, 0, -1.8)
v.dim_v(0, H, yo0, -4.2)
out["lid"] = v.svg()

# ---------------------------------------------------------------- card retainer, seen from the mouth (cut at x = -4, with the body)
v = View(yo1 - yo0)
xr = (RT["back"] + RT["front"]) / 2 + 0.6
v.loops(section(body, [xr, 0, 0], [1, 0, 0], ui), "cutf")
v.loops(section(ret, [xr, 0, 0], [1, 0, 0], ui), "cutr")
for z0, sd in RT["fz"]:
    yy = 0.9 if sd == 0 else bw - 0.9
    v.circle(m(yy), z0 + RT["fh"] / 2, 0.9, "port")
v.leader(m(RT["roof_y"][0]), zr + RT["bump"] / 2, m(RT["roof_y"][0]) + 6, H + 5, "bumps in the roof vents", "start")
v.leader(m(RT["floor_y"][0]), zf - RT["bump"] / 2, m(RT["floor_y"][0]) + 6, -5, "bumps in the floor vents", "start")
v.leader(m(0.9), RT["fz"][0][0] + 2, yo1 + 4, RT["fz"][0][0] - 3, "finger, Duo corner", "start")
v.leader(m(bw - 0.9), RT["fz"][2][0] + 2, yo0 - 4, RT["fz"][2][0] + 6, "finger, Pi corner (GPIO side)", "end")
v.leader(m(bw - 0.9), RT["fz"][1][0] + 2, yo0 - 4, RT["fz"][1][0] - 3, "finger, Duo corner", "end")
v.text(m(bw / 2), (zf + zr) / 2, "open: ribbon + air", "zt")
v.dim_h(yo0, yo1, 0, -3.6)
out["ret"] = v.svg()

# ---------------------------------------------------------------- retainer details: finger (plan, 3:1) and bump (side, 3:1)
K = 3
v = View(14, K)
zc = RT["fz"][0][0] + RT["fh"] / 2
u0, u1, w0, w1 = RT["back"] - 0.8, e0 + 4.5, I["y_in"][0] - 1.6, 4.2
v.loops(clip(section(body, [0, 0, zc], [0, 0, 1], xy), u0, w0, u1, w1), "cutf")
v.loops(clip(section(ret, [0, 0, zc], [0, 0, 1], xy), u0, w0, u1, w1), "cutr")
v.rect(e0, 0, u1, w1, "pcb")
v.leader(e0 + 3, 2.5, u1 + 1.2, 3.6, "Duo board", "start")
v.leader((RT["front"] + RT["tip"]) / 2 + 0.2, 0.2, u1 + 1.2, -1.4, "finger bends as the board pushes it", "start")
v.dim_h(e0, RT["tip"], w1, 1.2, f"{f1(RT['tip'] - e0)} preload")
v.dim_h(RT["back"], RT["front"], w0, -1.4, f"{f1(RT['front'] - RT['back'])} ring")
out["ret_finger"] = v.svg()

v = View(14, K)
yb0 = RT["roof_y"][0]
u0, u1, w0, w1 = RT["back"] - 2.2, RT["front"] + 0.8, zr - RT["wall"] - 0.6, H + 0.6
v.loops(clip(section(body, [0, yb0, 0], [0, 1, 0], xz), u0, w0, u1, w1), "cutf")
v.loops(clip(section(ret, [0, yb0, 0], [0, 1, 0], xz), u0, w0, u1, w1), "cutr")
v.leader(RT["back"] + 1.0, zr + RT["bump"] * 0.6, u1 + 0.6, H + 1.2, "bump in the roof vent", "start")
v.leader(RT["back"] - 0.3, zr + 1.6, u0 - 0.6, H + 1.2, "catches on the slot end", "end")
v.dim_v(zr, zr + RT["bump"], u1, 1.2, f"{f1(RT['bump'])}")
v.text((u0 + u1) / 2, w0, "cut through a roof vent slot", "zt", dv=-v.fs * 1.4)
out["ret_bump"] = v.svg()

# ---------------------------------------------------------------- latch detail: plan through the GPIO-side hook (4:1)
K = 4
v = View(12, K)
yi1 = I["y_in"][1] - 0.25
u0, u1, w0, w1 = xm - lid_t - 0.6, xm + 7.2, yi1 - 5.2, yo1 + 0.6
xy = lambda p: (p[0], p[1])
v.loops(clip(section(body, [0, 0, LT["z"]], [0, 0, 1], xy), u0, w0, u1, w1), "cutf")
v.loops(clip(section(lid, [0, 0, LT["z"]], [0, 0, 1], xy), u0, w0, u1, w1), "cutl")
hx = LT["hx"]
v.leader(xm + 5.5, yi1 - LT["t"] / 2, xm + 8.4, yi1 - 3.6, "arm (bends in the layer plane)", "start")
v.leader(xm - 1.2, yi1 - LT["t"] - LT["slot"] / 2, xm - 4.2, yi1 - 4.4, "slot: room to flex", "end")
v.leader(xm - 1.2, yi1 + LT["gap"] / 2, xm - 4.2, yo1 + 1.6, "slot through the plate", "end")
v.text(xm + 6.4, yo1 + 0.5, "body wall", "zt", "middle")
v.dim_h(I["snap_x"][0], I["snap_x"][1], yo1, 1.4, f"{f1(I['snap_x'][1] - I['snap_x'][0])} window")
v.dim_h(hx[0], hx[3], yi1, -4.6, f"{f1(hx[3] - hx[0])} hook")
v.dim_v(yi1, yi1 + LT["hook"], u1, 1.2, f"{f1(LT['hook'])}")
v.dim_v(yi1 - LT["t"], yi1, u1, 3.4, f"{f1(LT['t'])} arm")
v.dim_v(I["y_in"][1], yi1 + LT["hook"], u0, -1.4, f"{LT['hook'] - 0.25:.2f} into wall")
out["latch"] = v.svg()

# ---------------------------------------------------------------- foot
ftm = trimesh.load(ROOT / "stl" / "feet.stl")
v = View(30, 3)
v.loops(clip(section(ftm, [0, 0, 0], [0, 1, 0], xz), -fd / 2 - 1, -1, fd / 2 + 1, fh + 1), "cutl")
v.dim_h(-fd / 2, fd / 2, 0, -1.6, f"Ø{f1(fd)}")
cbd, cbh = I["foot_cb"]
v.dim_h(-cbd / 2, cbd / 2, fh, 1.4, f"Ø{f1(cbd)}")
v.dim_h(-1.7, 1.7, fh, 3.2, "Ø3.4")
v.dim_v(0, fh, fd / 2, 1.6)
v.dim_v(fh - cbh, fh, -fd / 2, -1.6, f"{f1(cbh)}")
v.text(0, fh, "counterbore up, as printed", "zt", dv=v.fs * 5.0)
out["foot"] = v.svg()


# ---------------------------------------------------------------- DIN rail bracket
D = I["din"]
din = trimesh.load(ROOT / "stl" / "din.stl")
rail = trimesh.load(ROOT / "stl" / "din_rail.stl"); rail.apply_translation([0, 0, D["H"]])   # into the bracket frame
uc, ut, ub, Hd, led = D["uc"], D["ut"], D["ub"], D["H"], D["ledge"]

# plan, seen from the case side, cut through the plate
v = View(D["u1"] - D["u0"] + D["tab"])
v.loops(section(din, [0, 0, 4.0], [0, 0, 1], xy), "panel")
for x in I["foot_x"]:
    for y in (I["y_foot"], bw - I["y_foot"]):
        v.circle(x, y, 3.1, "hole")
for u in (ut, ub):
    v.line(u, D["v0"] - 6, u, D["v1"] + 6, "cl")
v.text(uc, bw / 2, "rail runs this way", "zt", rot=-90)
v.leader(ub - 1.6, 50, ub + 6, D["v1"] + 12, "fixed hook", "start")
v.leader(ut + 0.8, 38, ut - 3, D["v1"] + 13, "latch", "end")
v.leader(16, 48, 33, 46, "flexures", "start")
v.leader(D["u0"] - D["tab"] + 2.7, bw / 2 + 2, D["u0"] - D["tab"] - 3, D["v1"] + 6, "pull tab", "end")
v.text(69.4, bw / 2, "air window", "zt", rot=-90)
v.leader(80, bw - I["y_foot"], 92, bw - I["y_foot"] + 6, "M3 × 20, counterbored", "start")
v.dim_h(D["u0"] - D["tab"], D["u1"], D["v0"], -2.2, f"{f1(D['u1'] - D['u0'] + D['tab'])}")
v.dim_h(I["foot_x"][0], I["foot_x"][1], D["v0"], -4.0, f"{f1(I['foot_x'][1] - I['foot_x'][0])} holes")
v.dim_h(ut, ub, D["v1"], 1.4, f"{f1(ub - ut)} rail")
v.dim_v(D["v0"], D["v1"], D["u1"], 1.6, f"{f1(D['v1'] - D['v0'])}")
out["din_plan"] = v.svg()

# clip section through the latch tongue, with the rail
K = 2
v = View(60, K)
v.loops(clip(section(din, [0, bw / 2, 0], [0, 1, 0], xz), ut - 10, -1, ub + 9, Hd + 1), "cutf")
v.loops(clip(section(rail, [0, bw / 2, 0], [0, 1, 0], xz), ut - 10, -6, ub + 9, Hd), "railc")
v.line(ut - 10, led - 7.5, ub + 9, led - 7.5, "wall")
v.text(uc, led - 7.5, "wall / panel", "zt", dv=-v.fs * 1.3)
v.leader(ut - 0.5, 0.5, ut - 6, -4.5, "latch lip + ramp", "end")
v.leader(ub - 1.5, 0.6, ub + 4, -4.5, "fixed hook", "start")
v.leader(ut - 4, 4, ut - 8, Hd - 2, "latch tongue", "end")
v.dim_h(ub - D["hook"], ub, D["lip"], -3.4, f"{f1(D['hook'])}")
v.dim_h(ut, ut + D["latch"], D["lip"], -3.4, f"{f1(D['latch'])}")
v.dim_v(0, D["plate"], ub + 9, 1.4, f"{f1(D['plate'])}")
v.dim_v(D["plate"], Hd, ub + 9, 1.4, f"{f1(D['gap'])} air")
v.dim_v(led - 7.5, led, ut - 10, -1.6, "7.5")
out["din_clip"] = v.svg()

# on the rail: case turned 180 deg on the bracket so the USB end is down, latch down
zw = -Hd + led - 7.5          # wall, case frame
rot = lambda p: (p[2] - zw, 84 - p[0])          # (from wall, height)
brk = lambda p: (p[2] - Hd - zw, p[0])
v = View(110)
v.loops(section(body, [0, I["y_o"][0] + 1.2, 0], [0, 1, 0], rot), "panel")
v.loops(section(lid, [0, I["y_o"][0] + 0.6, 0], [0, 1, 0], rot), "panell")
v.loops(section(din, [0, D["v0"] + 3, 0], [0, 1, 0], brk), "cutd")
v.loops(section(din, [0, bw / 2, 0], [0, 1, 0], brk), "cutd")
v.loops(section(rail, [0, bw / 2, 0], [0, 1, 0], brk), "railc")
v.line(0, -30, 0, 115, "wall")
v.text(0, 115, "wall", "zt", dv=v.fs * 0.5)
v.leader(H * 0.6 - zw, 84 - 87.9 - 1, H * 0.6 - zw + 18, -14, "USB / RJ45 end, cables down", "start")
v.leader(-zw - Hd + 3, 10, -zw - Hd - 10, -14, "latch: pull down to release", "end")
v.leader(-zw - 4, 70, 6, 122, "14 mm chimney behind the floor vents", "start")
v.dim_h(0, H - zw, 84 - I["x_mouth"] + I["lid_t"], 1.6, f"{f1(H - zw)} from the wall")
v.dim_h(0, -zw, -30, -1.8, f"{f1(-zw)}")
out["din_side"] = v.svg()

(ROOT / "drawings.json").write_text(json.dumps(out))
print({k: len(s) for k, s in out.items()})
