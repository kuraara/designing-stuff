#!/usr/bin/env python3
"""2D drawings for every layout, generated from the real STLs (trimesh sections)
plus the layout INFO echoed by button_box.scad. Writes drawings.json:
{layout: {view: svg_string}} and footprints for the overview grid."""
import json, math, pathlib
import numpy as np
import trimesh

ROOT = pathlib.Path(__file__).parent
LAYOUTS = ["1x1", "1x2", "1x3", "1x4", "2x2", "2x3"]


def f1(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


class View:
    """Collects SVG elements in mm, v-up coordinates; emits an SVG with viewBox."""

    def __init__(self, width_hint):
        self.el = []
        self.fs = max(3.8, min(8.0, width_hint * 0.034))   # text size (mm)
        self.lo = [1e9, 1e9]
        self.hi = [-1e9, -1e9]

    def grow(self, u, v):
        self.lo = [min(self.lo[0], u), min(self.lo[1], v)]
        self.hi = [max(self.hi[0], u), max(self.hi[1], v)]

    def P(self, u, v):
        self.grow(u, v)
        return f"{u:.2f},{-v:.2f}"

    def loops(self, loops, cls):
        d = "".join("M" + "L".join(self.P(u, v) for u, v in lp) + "Z" for lp in loops if len(lp) > 2)
        if d:
            self.el.append(f'<path class="{cls}" fill-rule="evenodd" d="{d}"/>')

    def rect(self, u0, v0, u1, v1, cls, rx=0):
        a, b = min(u0, u1), max(u0, u1)
        c, d = min(v0, v1), max(v0, v1)
        self.grow(a, c); self.grow(b, d)
        self.el.append(f'<rect class="{cls}" x="{a:.2f}" y="{-d:.2f}" width="{b - a:.2f}" height="{d - c:.2f}" rx="{rx}"/>')

    def circle(self, u, v, r, cls):
        self.grow(u - r, v - r); self.grow(u + r, v + r)
        self.el.append(f'<circle class="{cls}" cx="{u:.2f}" cy="{-v:.2f}" r="{r:.2f}"/>')

    def line(self, u0, v0, u1, v1, cls):
        self.el.append(f'<line class="{cls}" x1="{u0:.2f}" y1="{-v0:.2f}" x2="{u1:.2f}" y2="{-v1:.2f}"/>')
        self.grow(u0, v0); self.grow(u1, v1)

    def text(self, u, v, s, cls="t", anchor="middle", rot=0, size=1.0):
        fs = self.fs * size
        # rough extent so the viewBox leaves room for labels
        w = len(s) * fs * 0.55
        if rot:
            self.grow(u - fs, v - w / 2); self.grow(u + fs * 0.3, v + w / 2)
        else:
            du = {"middle": -w / 2, "start": 0, "end": -w}[anchor]
            self.grow(u + du, v - fs * 0.3); self.grow(u + du + w, v + fs)
        tr = f' transform="rotate({rot} {u:.2f} {-v:.2f})"' if rot else ""
        self.el.append(f'<text class="{cls}" x="{u:.2f}" y="{-v:.2f}" font-size="{fs:.2f}" text-anchor="{anchor}"{tr}>{s}</text>')

    def arrow(self, u, v, du, dv):
        L = self.fs * 0.75; W = self.fs * 0.28
        n = math.hypot(du, dv); du, dv = du / n, dv / n
        bu, bv = u - du * L, v - dv * L
        pts = [(u, v), (bu - dv * W, bv + du * W), (bu + dv * W, bv - du * W)]
        self.el.append('<path class="ar" d="M' + "L".join(f"{a:.2f},{-b:.2f}" for a, b in pts) + 'Z"/>')

    def dim_h(self, u0, u1, v_ref, v_dim, label=None):
        """horizontal dimension between u0..u1, extension lines from v_ref to v_dim"""
        s = 1 if v_dim > v_ref else -1
        g = self.fs * 0.4
        for u in (u0, u1):
            self.line(u, v_ref + s * g, u, v_dim + s * g, "ext")
        self.line(u0, v_dim, u1, v_dim, "dl")
        if abs(u1 - u0) > self.fs * 2:
            self.arrow(u0, v_dim, -1, 0); self.arrow(u1, v_dim, 1, 0)
        self.text((u0 + u1) / 2, v_dim + self.fs * 0.35, label or f1(abs(u1 - u0)), "dt")

    def dim_v(self, v0, v1, u_ref, u_dim, label=None):
        s = 1 if u_dim > u_ref else -1
        g = self.fs * 0.4
        for v in (v0, v1):
            self.line(u_ref + s * g, v, u_dim + s * g, v, "ext")
        self.line(u_dim, v0, u_dim, v1, "dl")
        if abs(v1 - v0) > self.fs * 2:
            self.arrow(u_dim, v0, 0, -1); self.arrow(u_dim, v1, 0, 1)
        self.text(u_dim - self.fs * 0.35, (v0 + v1) / 2, label or f1(abs(v1 - v0)), "dt", rot=-90)

    def leader(self, u0, v0, u1, v1, s, anchor="start"):
        self.line(u0, v0, u1, v1, "ld")
        self.circle(u0, v0, self.fs * 0.15, "ldot")
        self.text(u1 + (self.fs * 0.3 if anchor == "start" else -self.fs * 0.3), v1 - self.fs * 0.32, s, "lt", anchor)

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


def build(L):
    I = json.loads((ROOT / "info" / f"{L}.json").read_text())
    tub = trimesh.load(ROOT / "stl" / f"{L}_tub.stl")
    plate = trimesh.load(ROOT / "stl" / f"{L}_plate_asm.stl")
    plate.apply_translation([0, 0, I["Ho"]])
    Xo, Yo, Ho, pt = I["Xo"], I["Yo"], I["Ho"], I["plate_t"]
    w, ft = I["wall"], I["floor_t"]
    hole, bez, nut, depth, cc = I["btn"]
    B = I["buttons"]
    cols, rows = I["cols"], I["rows"]
    top = Ho + pt
    z_tab = top - depth
    bat_x0, bat_y0, bat_z0 = I["bat"]
    hl, hw, hh = I["holder"]
    boards = {"TP4056": I["tp"], "ESP32-C3": I["esp"]}
    bb = I["board_back"]; so = I["standoff"]
    rk_x, rk_z, rk_w, rk_h = I["rocker"]
    y_back_btn = B[-1][1]
    out = {}

    # ---------------------------------------------------------------- TOP
    v = View(Xo)
    v.loops(section(plate, [0, 0, Ho + pt - 0.25], [0, 0, 1], lambda p: (p[0], p[1])), "panel")
    v.rect(w, Yo - w - I["bay_d"], Xo - w, Yo - w, "bayzone")
    v.text(Xo / 2, Yo - w - I["bay_d"] / 2 - v.fs * 0.35, "electronics bay below", "zt")
    for i, (x, y) in enumerate(B):
        v.circle(x, y, bez / 2, "bezel")
        v.circle(x, y, hole / 2 - 2, "plunger")
        v.text(x, y - v.fs * 0.35, f"B{i + 1}", "bt")
    # section markers
    yb, xc = B[0][1] + 0.3, B[0][0] + 0.3
    ext = v.fs * 1.4
    v.line(-ext, yb, Xo + ext, yb, "cut")
    v.text(-ext - v.fs * 0.2, yb - v.fs * 0.35, "B", "cutl", "end")
    v.text(Xo + ext + v.fs * 0.2, yb - v.fs * 0.35, "B", "cutl", "start")
    v.line(xc, -ext, xc, Yo + ext, "cut")
    v.text(xc, Yo + ext + v.fs * 0.3, "C", "cutl")
    v.text(xc, -ext - v.fs * 1.1, "C", "cutl")
    # dims
    v.dim_h(0, Xo, 0, -ext - v.fs * 3.2)
    v.dim_h(0, B[0][0], 0, -ext - v.fs * 1.6)
    v.dim_v(0, Yo, 0, -ext - v.fs * 3.4)
    v.dim_v(0, B[0][1], 0, -ext - v.fs * 1.8)
    if cols > 1:
        v.dim_h(B[0][0], B[1][0], Yo, Yo + ext + v.fs * 1.6, f"{f1(I['pitch'])} pitch")
    v.dim_v(y_back_btn, Yo, Xo, Xo + ext + v.fs * 1.8)
    if rows > 1:
        v.dim_v(B[0][1], B[cols][1], Xo, Xo + ext + v.fs * 1.8, f"{f1(I['pitch'])}")
    out["top"] = v.svg()

    # ---------------------------------------------------------------- PLAN SECTION A-A
    za = Ho - 6.65
    v = View(Xo)
    for (x, y) in B:
        v.circle(x, y, nut / 2, "nut")
        v.circle(x, y, 15, "barrel")
    v.loops(section(tub, [0, 0, za], [0, 0, 1], lambda p: (p[0], p[1])), "cutf")
    v.rect(bat_x0, bat_y0, bat_x0 + hl, bat_y0 + hw, "batt", 2)
    for name, (cx, bw, bl, pcb, pz) in boards.items():
        v.rect(cx - bw / 2, bb - bl, cx + bw / 2, bb, "pcb", 1)
    tpx = boards["TP4056"][0]; espx = boards["ESP32-C3"][0]
    v.leader(tpx, bb - 14, tpx - 4, Yo + v.fs * 2.2, "TP4056", "end")
    v.leader(espx, bb - 12, espx + 4, Yo + v.fs * 2.2, "ESP32-C3")
    v.rect(rk_x - 6.5, Yo - w - 18, rk_x + 6.5, Yo - w, "rock", 1)
    v.leader(rk_x + 6.5, Yo - w - 9, rk_x + 22, Yo + v.fs * 2.2, "rocker")
    v.dim_h(w, Xo - w, 0, -v.fs * 1.8, f"{f1(I['Xi'])} inside")
    v.dim_v(w, Yo - w, 0, -v.fs * 1.8, f"{f1(I['Yi'])} inside")
    v.dim_v(Yo - w - I["bay_d"], Yo - w, Xo, Xo + v.fs * 1.8, f"{f1(I['bay_d'])} bay")
    v.dim_v(w, B[0][1], Xo, Xo + v.fs * 1.8, f"{f1(I['edge'])}")
    out["plan"] = v.svg()

    # ---------------------------------------------------------------- FRONT SECTION B-B
    yc = B[0][1] + 0.3
    v = View(Xo)
    xz = lambda p: (p[0], p[2])
    v.loops(section(tub, [0, yc, 0], [0, 1, 0], xz) + section(plate, [0, yc, 0], [0, 1, 0], xz), "cutf")
    for (x, y) in B[:cols]:
        btn_side(v, x, top, z_tab, ft, bez, nut, 28)
    v.line(-v.fs, za, Xo + v.fs, za, "cut")
    v.text(-v.fs * 1.2, za - v.fs * 0.35, "A", "cutl", "end")
    v.text(Xo + v.fs * 1.2, za - v.fs * 0.35, "A", "cutl", "start")
    v.dim_v(0, top, 0, -v.fs * 4.8, f"{f1(top)} overall")
    v.dim_v(0, Ho, 0, -v.fs * 2.6, f"{f1(Ho)} tub")
    xr = Xo + v.fs * 1.6
    v.dim_v(z_tab, top, Xo, xr, f"{f1(depth)} button")
    v.dim_v(ft, z_tab, Xo, xr, f"{f1(cc)}")
    v.dim_v(ft, Ho, Xo, xr + v.fs * 2.6, f"{f1(I['Hi'])} inside")
    v.dim_h(0, Xo, 0, -v.fs * 2.2)
    out["front"] = v.svg()

    # ---------------------------------------------------------------- SIDE SECTION C-C (viewed from right: front left, back right)
    xc = B[0][0] + 0.3
    v = View(Yo)
    yz = lambda p: (p[1], p[2])
    v.loops(section(tub, [xc, 0, 0], [1, 0, 0], yz) + section(plate, [xc, 0, 0], [1, 0, 0], yz), "cutf")
    for r in range(rows):
        btn_side(v, B[r * cols][1], top, z_tab, ft, bez, nut, 20)
    v.rect(bat_y0, bat_z0, bat_y0 + hw, bat_z0 + hh, "batt", 2)
    v.leader(bat_y0 + hw / 2, bat_z0 + hh * 0.6, bat_y0 - 6, bat_z0 + hh + v.fs * 2.2, "battery", "end")
    # board under the plate (the one this cut passes through, else the TP4056 shown beyond)
    hit = [n for n, b in boards.items() if abs(xc - b[0]) < b[1] / 2] or ["TP4056"]
    cx, bw, bl, pcb, pz = boards[hit[0]]
    v.rect(bb - bl, Ho - so - pcb, bb, Ho - so, "pcb")
    v.rect(bb - 7.3, pz - 1.6, bb + 0.3, pz + 1.6, "usb", 0.8)
    v.leader(bb - bl / 2, Ho - so - pcb, bb - bl - 4, Ho - so - v.fs * 2.8, hit[0], "end")
    v.dim_h(0, Yo, 0, -v.fs * 2.2)
    v.dim_v(pz, top, Yo, Yo + v.fs * 1.6, f"{f1(top - pz)}")
    v.dim_v(ft, bat_z0 + hh, Yo, Yo + v.fs * 1.6, f"{f1(bat_z0 + hh - ft)}")
    out["side"] = v.svg()

    # ---------------------------------------------------------------- BACK ELEVATION (seen from behind)
    yw = Yo - w / 2
    v = View(Xo)
    bk = lambda p: (Xo - p[0], p[2])
    v.loops(section(tub, [0, yw, 0], [0, 1, 0], bk) + section(plate, [0, yw, 0], [0, 1, 0], bk), "cutf")
    labels = [("CHARGE", boards["TP4056"]), ("ESP32 USB", boards["ESP32-C3"])]
    for i, (lab, b) in enumerate(labels):
        u = Xo - b[0]
        v.text(u, b[4] - I["usb_cut"][1] / 2 - v.fs * 1.3, lab, "lt", size=0.9)
    v.text(Xo - rk_x, rk_z - rk_h / 2 - v.fs * 1.3, "POWER", "lt", size=0.9)
    ports_u = sorted([Xo - boards["ESP32-C3"][0], Xo - boards["TP4056"][0]])
    v.dim_h(Xo - rk_x, Xo, 0, -v.fs * 1.6)
    v.dim_h(ports_u[0], Xo, 0, -v.fs * 3.3)
    v.dim_h(ports_u[1], Xo, 0, -v.fs * 5.0)
    v.dim_v(0, rk_z, Xo, Xo + v.fs * 1.6)
    v.dim_v(0, boards["TP4056"][4], Xo, Xo + v.fs * 3.6)
    out["back"] = v.svg()
    return I, out


def btn_side(v, x, top, z_tab, ft, bez, nut, sw):
    """approximate side profile of a long-barrel arcade button + microswitch"""
    pt = 4
    v.rect(x - bez / 2, top, x + bez / 2, top + 4, "btnf", 1.5)              # bezel
    v.rect(x - 12, top + 4, x + 12, top + 11, "btnf", 4)                       # plunger cap
    v.rect(x - nut / 2, top - pt - 9, x + nut / 2, top - pt, "btno")          # nut
    v.rect(x - 14.5, z_tab + 26, x + 14.5, top - pt - 9, "btno")              # barrel
    v.rect(x - sw / 2, z_tab + 6, x + sw / 2, z_tab + 26, "btno")             # microswitch
    for dx in (-sw / 2 + 3, 0, sw / 2 - 3):
        v.rect(x + dx - 0.6, z_tab, x + dx + 0.6, z_tab + 6, "btnf")          # .187 tabs
    v.rect(x - 15, ft + 1, x + 15, z_tab, "clr")                               # spade + wire zone


def footprint(I):
    return {k: I[k] for k in ("Xo", "Yo", "Ho", "buttons", "bay_d", "wall", "screw_pts")}


if __name__ == "__main__":
    res = {}
    for L in LAYOUTS:
        I, views = build(L)
        res[L] = {"info": I, "views": views}
        print(L, {k: len(s) for k, s in views.items()})
    (ROOT / "drawings.json").write_text(json.dumps(res))
