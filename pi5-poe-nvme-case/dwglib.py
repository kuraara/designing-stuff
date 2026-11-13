"""Drawing helpers shared by drawings.py and the concept sketches: SVG views in mm, STL sections."""
import math
from functools import reduce
import numpy as np
from shapely.geometry import Polygon, box


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
