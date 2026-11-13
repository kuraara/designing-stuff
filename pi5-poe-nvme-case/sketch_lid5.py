#!/usr/bin/env python3
"""Concept sketches for the v0.5 lid (13 Nov 2026): tray under the NVMe Base Duo, small lips on the
Duo's top corners, end stops for both boards. Cut from the real STLs (body_asm, lid5_asm) like the
main drawings, plus two OpenSCAD previews. Writes img/pi5_case_lid_v0.5_sketch_*.png.

  openscad -D 'part="lid5_asm"' -o stl/lid5_asm.stl pi5_case.scad   (render_all.sh does the rest)
  python3 sketch_lid5.py [node_modules with @fontsource]

Board-top parts marked "approx." (M.2 socket, FFC connector, PCIe ribbon, Pi power button) are
read off the user's photo of 13 Nov, not measured."""
import json, pathlib, subprocess, sys, tempfile
import trimesh
from dwglib import f1, View, section, clip

ROOT = pathlib.Path(__file__).parent
NM = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
I = json.loads((ROOT / "info" / "info.json").read_text())
T = I["tray"]
body = trimesh.load(ROOT / "stl" / "body_asm.stl")
lid = trimesh.load(ROOT / "stl" / "lid5_asm.stl")
bw, bl = I["bw"], I["bl"]
zf, zd, zdt, zpb, zpt = I["zf"], I["zd"], I["z_duo_t"], I["z_pi_b"], I["z_pi_t"]
zhb, zht, zhc, zr, H = I["z_hat_b"], I["z_hat_t"], I["z_hat_c"], I["z_roof"], I["H"]
yo0, yo1 = I["y_o"]; yi0, yi1 = I["y_in"]
xm, xei, xeo = I["x_mouth"], I["x_end_in"], I["x_end_out"]
xl = xm - I["lid_t"]
e0 = xei - bl                       # boards' SD edges, home
hat_l = I["hat"][0]
ssd_h = 7.4                         # 5 mm standoff + 2.38 mm single-sided drive
x50, x75 = e0 + 0.5 * bl, T["x1"]
tz0, tz1 = T["z"]
xz = lambda p: (p[0], p[2])
xy = lambda p: (p[0], p[1])
m = lambda y: yo1 + yo0 - y         # end view mirrored: seen from the lid end, like the photo
ui = lambda p: (m(p[1]), p[2])
out = {}

# ---------------------------------------------------------------- 1. side section through the GPIO-side corner post
ys = 52.2                            # cuts the post, the lip and the tray's edge
v = View(xeo - xl)
v.loops(section(body, [0, ys, 0], [0, 1, 0], xz), "cutf")
v.loops(section(lid, [0, ys, 0], [0, 1, 0], xz), "cutl")
v.rect(0.8, I["z_dlb"], xei, zd, "hwo"); v.rect(0.8, I["z_plb"], xei, zpb, "hwo")
v.rect(e0, zd, xei, zdt, "pcb"); v.rect(e0, zpb, xei, zpt, "pcb")
v.rect(e0, zhb, e0 + hat_l, zht, "pcb"); v.rect(e0 + 1, zht, e0 + hat_l - 1, zhc, "env", 1)
v.rect(e0 + 2.5, zdt, e0 + 82.5, zdt + ssd_h, "ssd", 0.8)
R = xeo + 4                          # right-hand label column
v.leader(60, zhc - 3, R, zhc - 2, "PoE HAT", "start")
v.leader(75, zpt - 0.8, R, zpt + 2, "Pi 5", "start")
v.leader(76, zdt + ssd_h - 2, R, zdt + 6, "SSDs, on top of the Duo", "start")
v.leader(80, zd + 0.8, R, zd - 0.5, "NVMe Base Duo", "start")
v.leader(78, I["z_dlb"] + 1.2, R, zf + 6, "lower ledge (behind)", "start")
v.leader(56, tz0 + 0.6, R, zf, "tray", "start")
v.leader(xm + 6, (tz0 + zpt) / 2, xl - 4, zpb + 4, "corner post", "end")
v.leader(-4, zf + 2.5, xl - 4, zf + 3, "webs (behind)", "end")
v.text(20, (zf + tz0) / 2, "was the SSD bay", "zt")
for x, s in ((x50, "50 %"), (x75, "75 %")):
    v.line(x, zf + 1, x, zdt + 2, "cl"); v.text(x, (zf + tz0) / 2, s, "dt", dv=-v.fs * 0.35)
v.dim_h(e0, x75, zf, -3.0, f"{f1(x75 - e0)} under the Duo")
v.dim_h(xl, x75, zf, -5.0, f"{f1(x75 - xl)} lid, overall")
v.dim_h(e0, xei, H, 1.6, f"{f1(bl)} Duo")
out["side"] = ("Side section through the GPIO-side corner",
               f"Cut 4 mm in from the GPIO edge. The tray slides under the Duo from the lid and reaches "
               f"{f1(x75 - e0)} mm in (75&nbsp;%). Dashed: the ledges behind the cut, and the SSDs, now on top of the Duo.",
               v.svg())

# ---------------------------------------------------------------- 2. the same, at the lid end, 3:1
K = 3
v = View(14, K)
u0, u1, w0, w1 = xl - 0.8, 7.5, tz0 - 2.4, zpt + 3.2
v.loops(clip(section(body, [0, ys, 0], [0, 1, 0], xz), u0, w0, u1, w1), "cutf")
v.loops(clip(section(lid, [0, ys, 0], [0, 1, 0], xz), u0, w0, u1, w1), "cutl")
v.rect(0.8, max(w0, I["z_dlb"]), u1, zd, "hwo"); v.rect(0.8, I["z_plb"], u1, zpb, "hwo")
v.rect(e0, zd, u1, zdt, "pcb"); v.rect(e0, zpb, u1, zpt, "pcb")
v.rect(e0 + 2.5, zdt, u1, zdt + ssd_h, "ssd", 0.4)
v.leader(5.5, zpt - 0.8, u1 + 1.2, zpt + 1.2, "Pi", "start")
v.leader(5.5, zdt + ssd_h - 1.2, u1 + 1.2, zdt + ssd_h + 0.6, "SSD", "start")
v.leader(5.5, zd + 0.8, u1 + 1.2, zd + 2.6, "Duo", "start")
v.leader(5.5, zd - 1.6, u1 + 1.2, zd - 3.2, "ledge (behind)", "start")
L = u0 - 1.0                          # left-hand label column
v.leader(-0.6, zpt - 0.4, L, zpt + 0.6, f"Pi stop (post top {f1(T['pi_over'])} above the Pi)", "end")
v.leader(1.4, zdt + T["lip_gap"] + T["lip_t"] / 2, L, zdt + 5.0,
         f"small lip: {f1(T['lip_t'])} thick, {f1(T['lip_gap'])} over the Duo", "end")
v.leader(-0.6, zd + 0.8, L, zd + 1.0, "Duo stop", "end")
v.leader(-6, tz0 + 1.0, L, tz0 - 0.6, f"tray: {f1(tz1 - tz0)} thick, top {f1(zd - tz1)} under the ledge", "end")
v.dim_h(T["stop_x"], e0, w1, 1.2, f"{f1(e0 - T['stop_x'])} float")
v.dim_h(e0, e0 + T["lip_over"], zdt + T["lip_gap"] + T["lip_t"], 1.0, f"{f1(T['lip_over'])}")
v.dim_h(xm, T["stop_x"], w0, -1.2, f"{f1(T['stop_x'] - xm)} lid plate → stops")
out["detail"] = ("Corner post, 3:1",
                 "One post per corner does all three jobs: the tray holds the Duo up from below, the small lip sits "
                 f"just over its top corner and reaches {f1(T['lip_over'])} mm in, and the post's face stops the Duo and the Pi. "
                 "The stops leave 0.2 mm float, like the old prongs, so the latches still click.", v.svg())

# ---------------------------------------------------------------- 3. end view from the lid side (like the photo)
v = View(yo1 - yo0)
v.loops(section(body, [3.0, 0, 0], [1, 0, 0], ui), "cutf")
v.loops(section(lid, [-0.5, 0, 0], [1, 0, 0], ui), "cutl")
v.loops(section(lid, [1.2, 0, 0], [1, 0, 0], ui), "cutl")
v.rect(m(0), zd, m(bw), zdt, "pcb"); v.rect(m(0), zpb, m(bw), zpt, "pcb")
v.rect(m(-0.25), zhb, m(bw + 0.25), zht, "pcb")
v.rect(m(4.5), zdt + 0.6, m(51.5), zdt + ssd_h, "ssd", 0.6)
v.rect(m(12.3), zdt, m(30.8), zdt + 2.4, "sock")                 # M.2 socket (approx.)
v.rect(m(32.5), zdt, m(43.1), zdt + 1.6, "sock")                 # ADDON FFC connector (approx.)
v.rect(m(24), zdt + 1.8, m(43), zpt + 4, "ribz", 0.8)            # PCIe ribbon zone (approx.)
v.rect(m(14.5), zpt, m(18.5), zpt + 1.4, "sd")                   # Pi power button + LED (approx.)
R, L = yo1 + 3, yo0 - 3
v.leader(m(16.5), zpt + 1.2, R, zpt + 8, "power button*", "start")
v.leader(m(1.6), zpt - 0.5, R, zpt + 1, "Pi stop", "start")
v.leader(m(20), zdt + 1.6, R, zdt + 7.5, "M.2 socket*", "start")
v.leader(m(1.6), zdt + 1.0, R, zdt + 1.5, "small lip", "start")
v.leader(m(18.7), tz0 + 1, R, tz0 - 4, "slotted tray", "start")
v.leader(m(9.25), zf + 3, R, zf + 0.5, "webs", "start")
v.leader(m(36), zpt + 3.0, L, zpt + 8, "PCIe ribbon*", "end")
v.leader(m(54.4), zpt - 0.5, L, zpt + 1, "Pi stop", "end")
v.leader(m(46), zdt + ssd_h - 1, L, zdt + 7.5, "SSDs", "end")
v.leader(m(54.4), zdt + 1.0, L, zdt + 1.5, "small lip", "end")
v.leader(m(38), zdt + 0.8, L, tz0 - 4, "ADDON conn.*", "end")
v.text(m(bw + 2), H, "GPIO side", "zt", "middle", dv=v.fs * 0.6)
v.text(m(-2), H, "USB-C side", "zt", "middle", dv=v.fs * 0.6)
v.dim_h(m(T["y"][1]), m(T["y"][0]), zf, -2.0, f"{f1(T['y'][1] - T['y'][0])} tray")
v.text(m(bw / 2), 0, "* approx., from your photo", "zt", dv=-v.fs * 4.6)
out["end"] = ("From the lid end, same view as your photo",
              "Lid cut just in front of the boards (posts, tray, webs) over the body cut at the ledges. The two 5.6 mm "
              "posts sit in the corners you circled, clear of the ribbon, the M.2 socket, the FFC connector and the Pi's "
              "power button.", v.svg())

# ---------------------------------------------------------------- 4. plan under the Duo
v = View(xeo - xl)
v.loops(section(body, [0, 0, 14.3], [0, 0, 1], xy), "cutf")
v.loops(section(lid, [0, 0, 14.3], [0, 0, 1], xy), "cutl")
v.loops(clip(section(lid, [0, 0, 8.0], [0, 0, 1], xy), -10, 4, x75, bw - 4), "hwo")    # webs, under the tray
v.rect(e0, 0, xei, bw, "pcbo")
for x, s in ((x50, "50 %"), (x75, "75 %")):
    v.line(x, yo0 - 1, x, yo1 + 1, "cl"); v.text(x, yo1 + 1, s, "dt", dv=v.fs * 0.4)
R = xeo + 3
v.leader(80, bw, R, yo1 - 2, "Duo outline", "start")
v.leader(80, 1.5, R, 4, "lower ledge", "start")
v.leader(75, 28, R, 28, "air (no tray)", "start")
v.leader(-6, 53.8, xl - 3, yo1 - 2, "corner post", "end")
v.leader(-4, 28, xl - 3, 28, "web, under the tray", "end")
v.leader(-4, 9.25, xl - 3, 9.25, "web", "end")
v.dim_h(e0, x75, yo0, -2.0, f"{f1(x75 - e0)} = 75 % of {f1(bl)}")
v.dim_v(T["y"][0], T["y"][1], 70, 0, f"{f1(T['y'][1] - T['y'][0])}")
out["plan"] = ("Plan, cut just under the Duo",
               "The tray runs between the lower ledges with 0.5 mm clear each side. Its slots line up with the floor "
               "vents, so air still reaches the Duo's underside. The webs (dashed) run on the floor's bars between the slots.",
               v.svg())

# ---------------------------------------------------------------- 3D previews (OpenSCAD, colours)
CAMS = {"3d_lid": ("lid", "115,-70,80,20,28,18")}
scad = (ROOT / "pi5_case.scad").resolve()
wrap = f"""use <{scad}>
color([0.17, 0.31, 0.54]) lid_asm(true);
"""
with tempfile.TemporaryDirectory() as td:
    w = pathlib.Path(td) / "w.scad"; w.write_text(wrap)
    for key, (view, cam) in CAMS.items():
        png = ROOT / "img" / f"pi5_case_lid_v0.5_sketch_{key}.png"
        cmd = ["xvfb-run", "-a", "-s", "-screen 0 1800x1400x24", "openscad", "-o", str(png), "--imgsize=1600,1100",
               "--colorscheme=Tomorrow", "--projection=p", f"--camera={cam}", "--viewall",
               str(w)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(key, "ok" if png.exists() and png.stat().st_size > 1000 else r.stderr[-400:])

# ---------------------------------------------------------------- 2D sheets -> PNG (Playwright)
fonts = ""
if NM:
    for w_ in (400, 500):
        f = NM / "@fontsource" / "ibm-plex-mono" / "files" / f"ibm-plex-mono-latin-{w_}-normal.woff2"
        fonts += f"@font-face{{font-family:'IBM Plex Mono';font-weight:{w_};src:url('file://{f}') format('woff2');}}"
    f = NM / "@fontsource" / "ibm-plex-sans" / "files" / "ibm-plex-sans-latin-400-normal.woff2"
    fonts += f"@font-face{{font-family:'IBM Plex Sans';font-weight:400;src:url('file://{f}') format('woff2');}}"
    f = NM / "@fontsource" / "saira-condensed" / "files" / "saira-condensed-latin-600-normal.woff2"
    fonts += f"@font-face{{font-family:'Saira Condensed';font-weight:600;src:url('file://{f}') format('woff2');}}"
CSS = fonts + """
:root { --paper:#eef2f1; --sheet:#f9fbfa; --ink:#1b2a31; --muted:#5a6b72; --rule:#c9d3d3; --cut-bg:#dbe3e3; --hatch:#7e9196;
  --dim:#0b6b87; --red:#c8322b; --pcb:#2a7d4a; --amber:#b07a06; --lid:#2b4f8a; --lid-bg:#d6e3f4; --ssd:#6b4bb5; --hw:#6f7a7e;
  --f-mono:"IBM Plex Mono", ui-monospace, monospace; }
body { margin:0; background:var(--paper); color:var(--ink); font:15px/1.5 "IBM Plex Sans", system-ui, sans-serif; }
.card { width:1100px; box-sizing:border-box; margin:0; background:var(--sheet); border:1px solid var(--rule); padding:18px 20px; }
h4 { font:600 22px/1.1 "Saira Condensed", "Arial Narrow", sans-serif; text-transform:uppercase; letter-spacing:.04em; margin:0 0 4px; }
p { margin:0 0 10px; color:var(--muted); font-size:14px; max-width:78ch; }
svg.dwg { width:100%; height:auto; display:block; max-height:640px; }
.dwg * { vector-effect:non-scaling-stroke; }
.dwg .cutf { fill:url(#hatch); stroke:var(--ink); stroke-width:1.4px; }
.dwg .cutl { fill:url(#hatchl); stroke:var(--lid); stroke-width:1.4px; }
.dwg .pcb { fill:var(--pcb); fill-opacity:.22; stroke:var(--pcb); stroke-width:1.2px; }
.dwg .pcbo { fill:none; stroke:var(--pcb); stroke-width:1.2px; stroke-dasharray:6 3; }
.dwg .hwo { fill:none; stroke:var(--hw); stroke-width:1px; stroke-dasharray:4 3; }
.dwg .env { fill:var(--amber); fill-opacity:.08; stroke:var(--amber); stroke-width:1.1px; stroke-dasharray:6 3; }
.dwg .ssd { fill:var(--ssd); fill-opacity:.12; stroke:var(--ssd); stroke-width:1.1px; stroke-dasharray:6 3; }
.dwg .sock { fill:var(--hw); fill-opacity:.3; stroke:var(--ink); stroke-width:1px; }
.dwg .ribz { fill:var(--red); fill-opacity:.07; stroke:var(--red); stroke-width:1.6px; stroke-dasharray:5 3; }
.dwg .sd { fill:var(--red); fill-opacity:.35; stroke:var(--red); stroke-width:1px; }
.dwg .ext { stroke:var(--dim); stroke-width:.7px; stroke-opacity:.8; }
.dwg .dl { stroke:var(--dim); stroke-width:.9px; }
.dwg .ar { fill:var(--dim); stroke:none; }
.dwg .cl { stroke:var(--dim); stroke-width:1px; stroke-dasharray:12 3 2 3; }
.dwg .ld { stroke:var(--muted); stroke-width:.8px; }
.dwg .ldot { fill:var(--muted); }
.dwg text { font-family:var(--f-mono); fill:var(--ink); }
.dwg .dt { fill:var(--dim); font-weight:500; }
.dwg .zt { fill:var(--muted); font-style:italic; }
.dwg .lt { fill:var(--ink); }
"""
DEFS = """<svg width="0" height="0" style="position:absolute"><defs>
<pattern id="hatch" patternUnits="userSpaceOnUse" width="2" height="2" patternTransform="rotate(45)">
<rect width="2" height="2" style="fill:var(--cut-bg)"/><line x1="0" y1="0" x2="0" y2="2" style="stroke:var(--hatch);stroke-width:.4"/></pattern>
<pattern id="hatchl" patternUnits="userSpaceOnUse" width="2" height="2" patternTransform="rotate(-45)">
<rect width="2" height="2" style="fill:var(--lid-bg)"/><line x1="0" y1="0" x2="0" y2="2" style="stroke:var(--lid);stroke-width:.3;stroke-opacity:.6"/></pattern>
</defs></svg>"""
html = f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{DEFS}" + "".join(
    f"<figure class='card' id='{k}'><h4>{t}</h4><p>{c}</p>{s}</figure>" for k, (t, c, s) in out.items())
(ROOT / "slice").mkdir(exist_ok=True)
page = ROOT / "slice" / "lid5_sketch.html"            # git-ignored work file
page.write_text(html)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1140, "height": 900}, device_scale_factor=2)
    pg.goto(page.as_uri()); pg.wait_for_timeout(400)
    for k in out:
        f = ROOT / "img" / f"pi5_case_lid_v0.5_sketch_{k}.png"
        pg.locator(f"#{k}").screenshot(path=str(f)); print(f.relative_to(ROOT))
    b.close()
