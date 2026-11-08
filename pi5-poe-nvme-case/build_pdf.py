#!/usr/bin/env python3
"""Print the drawings page (pi5_case.html) to an A4 PDF, with rendered 3D views from the viewer
page (pi5_case_viewer.html), and embed the print STLs as PDF file attachments.

Needs: Python playwright (Chromium), qpdf, and local copies of the fonts + three.js, because
Google Fonts and jsDelivr may be unreachable from the build machine:
    npm i @fontsource/ibm-plex-sans@5 @fontsource/ibm-plex-mono@5 @fontsource/saira-condensed@5 three@0.128.0
Usage:
    python3 build_pdf.py <node_modules dir> [out.pdf]
"""
import base64, datetime, io, pathlib, re, subprocess, sys
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
NM = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "pi5_case_design.pdf"
WORK = OUT.parent / "pdf_work"
WORK.mkdir(exist_ok=True)
STLS = ["pi5_case_body_PETG.stl", "pi5_case_lid_TPU.stl", "pi5_case_feet_x4_TPU.stl", "pi5_case_din_bracket_PETG.stl"]
ISSUED = datetime.date.today().strftime("%-d %b %Y")

FONTS = [("IBM Plex Sans", "ibm-plex-sans", (400, 500, 600)),
         ("IBM Plex Mono", "ibm-plex-mono", (400, 500)),
         ("Saira Condensed", "saira-condensed", (500, 600, 700))]


def font_css():
    out = []
    for fam, pkg, weights in FONTS:
        for w in weights:
            f = NM / "@fontsource" / pkg / "files" / f"{pkg}-latin-{w}-normal.woff2"
            b = base64.b64encode(f.read_bytes()).decode()
            out.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:block;"
                       f"src:url(data:font/woff2;base64,{b}) format('woff2');}}")
    return "\n".join(out)


def wrap(body_html, extra_head=""):
    body_html = re.sub(r'<link rel="(?:stylesheet|preconnect)" href="https://fonts\.[^"]*"[^>]*>\n?', "", body_html)
    return ('<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<style>{font_css()}</style>{extra_head}</head><body>{body_html}</body></html>')


def routes(page):
    three = NM / "three"
    page.route(re.compile(r"https://cdn\.jsdelivr\.net/npm/three@0\.128\.0/(.*)"),
               lambda r: r.fulfill(path=str(three / re.match(r".*three@0\.128\.0/(.*)", r.request.url).group(1)),
                                   content_type="application/javascript"))
    page.route(re.compile(r"https://fonts\.(googleapis|gstatic)\.com/.*"), lambda r: r.fulfill(body="", content_type="text/css"))


# ------------------------------------------------------------------ 3D views from the viewer page
VIEWS = [
    ("asm", "Assembly", "Case on its feet with the boards in place (boards, SSDs and HAT parts shown as blocks)."),
    ("lid", "Lid out", "The TPU lid pulled 30 mm off the SD end, showing the two ledges inside the mouth."),
    ("cut", "Section through the ledges", "Cut across the case: the Pi on the upper ledge, the NVMe Base Duo on the lower ledge, SSDs in the bay."),
    ("din", "On a DIN rail", "Feet replaced by the DIN rail bracket, clipped to a TS35 rail."),
]


def render_views(pw):
    vfile = WORK / "viewer.html"
    vfile.write_text(wrap((ROOT / "pi5_case_viewer.html").read_text(),
                          "<style>.card,.views,.hint{display:none!important}</style>"))
    b = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1000, "height": 1150}, device_scale_factor=2, color_scheme="light")
    routes(pg)
    pg.goto(vfile.as_uri())
    pg.wait_for_function("window.THREE && document.querySelector('#cv').width > 0")
    pg.wait_for_timeout(1500)
    shots = {}

    def click(sel):
        pg.eval_on_selector(sel, "e => e.click()")

    def shot(k):
        pg.wait_for_timeout(1200)
        png = pg.locator("#stage").screenshot()
        im = Image.open(io.BytesIO(png)).convert("RGB")
        im = im.crop((4, 4, im.width - 4, im.height - 4))          # drop the stage border
        bg = im.getpixel((6, 6))
        diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L").point(lambda v: 255 if v > 18 else 0)
        x0, y0, x1, y1 = diff.getbbox() or (0, 0, im.width, im.height)
        m = int(0.06 * max(x1 - x0, y1 - y0))
        x0, y0, x1, y1 = max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)
        w, h = x1 - x0, y1 - y0
        W, H = (w, int(w * 3 / 4)) if w * 3 / 4 >= h else (int(h * 4 / 3), h)
        out = Image.new("RGB", (W, H), bg)
        out.paste(im.crop((x0, y0, x1, y1)), ((W - w) // 2, (H - h) // 2))
        im = out.resize((1400, 1050), Image.LANCZOS) if W > 1400 else out
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=88, optimize=True)
        shots[k] = base64.b64encode(buf.getvalue()).decode()

    shot("asm")
    click("#t-lid"); click("#v-iso"); shot("lid"); click("#t-lid")
    click("#t-cut"); pg.eval_on_selector("#cut", "e => { e.value = 54; e.dispatchEvent(new Event('input')); }"); shot("cut"); click("#t-cut")
    click("#t-din"); click("#v-iso"); shot("din")
    b.close()
    return shots


# ------------------------------------------------------------------ PDF of the drawings page
PRINT_CSS = """<style>
:root, :root[data-theme="light"] { --paper: #ffffff; --sheet: #f6f8f8; }
@page { size: A4; margin: 12mm 12mm 15mm; }
body { font-size: 13px; }
.wrap { max-width: none; padding: 0 !important; gap: 20px; }
.dwg-card, .ask, details, .tbl, .spec, .views3d figure, .att, section.times { break-inside: avoid; }
.wrap, .wrap > section, .intro, .dwgs, .ask { display: block; }
.wrap > * + *, .wrap > section > * + *, .intro > * + *, .ask > * + * { margin-top: 12px; }
.dwgs { margin-top: 12px; }
.dwgs > * + * { margin-top: 12px; }
.dwg-card { display: block; }
.dwg-card figcaption { margin-bottom: 8px; }
section[aria-labelledby="v3-h"], section[aria-labelledby="dw-h"], section[aria-labelledby="notes-h"] { break-before: page; }
.views3d img { aspect-ratio: auto; }
h2, h3.grp, .legend { break-after: avoid; }
svg.dwg { max-height: 92mm; }
.dwg-card figcaption p { font-size: 11.5px; line-height: 1.45; }
.dwg-card { padding: 10px; }
.zoom-hint, .zoom, .zoom-close { display: none !important; }
summary { list-style: none; }
summary::-webkit-details-marker { display: none; }
.views3d { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.views3d figure { margin: 0; background: var(--sheet); border: 1px solid var(--rule); border-radius: 4px; padding: 8px; display: grid; gap: 6px; }
.views3d img { width: 100%; height: auto; display: block; border-radius: 2px; }
.views3d figcaption { font-size: 12px; color: var(--muted); }
.views3d figcaption b { display: block; font: 600 1.05rem/1.1 var(--f-display); text-transform: uppercase; letter-spacing: .04em; color: var(--ink); }
.att { margin: 0; padding-left: 1.2em; display: grid; gap: 4px; font: 12.5px/1.4 var(--f-mono); }
</style>"""


def human(n):
    return f"{n / 1024:.0f} KB"


def build_pdf(pw, shots):
    html = (ROOT / "pi5_case.html").read_text()
    figs = "".join(f'<figure><img alt="{t}" src="data:image/jpeg;base64,{shots[k]}"><figcaption><b>{t}</b>{c}</figcaption></figure>'
                   for k, t, c in VIEWS)
    views = (f'<section aria-labelledby="v3-h"><h2 id="v3-h">3D views</h2><div class="views3d">{figs}</div>'
             '<p class="note">Rendered from the 3D model. The interactive viewer is a separate page.</p></section>\n\n  ')
    anchor = '<section aria-labelledby="dw-h">'
    assert anchor in html
    html = html.replace(anchor, views + anchor, 1)
    old = "<p>The print-ready STLs are in the chat: body (PETG), lid (TPU), four feet (TPU). Each is already oriented for the bed.</p>"
    assert old in html
    items = "".join(f"<li>{n} · {human((ROOT / 'print' / n).stat().st_size)}</li>" for n in STLS)
    html = html.replace(old, "<p>The print-ready STLs are attached to this PDF (open the attachments or paperclip panel in your PDF reader). "
                             f"Each is already oriented for the bed:</p><ul class=\"att\">{items}</ul>")
    leg = '<div class="legend"'
    assert leg in html
    html = html.replace(leg, '<p class="note">Dimensions in mm. The drawings are not to scale on the page; a scale in a title (3:1, 2:1) '
                             'is relative to the other views.</p>\n    ' + leg, 1)
    html = html.replace("<details>", "<details open>")
    html = html.replace("Enclosure study · v0.2 · drawings + STLs · 1 Nov 2026", f"Enclosure study · v0.2 · drawings + STLs · issued {ISSUED}")
    pfile = WORK / "drawings.html"
    pfile.write_text(wrap(html + PRINT_CSS))     # after the page's own <style>, so these win

    b = pw.chromium.launch()
    pg = b.new_page(color_scheme="light")
    routes(pg)
    pg.goto(pfile.as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(500)
    raw = WORK / "drawings_raw.pdf"
    foot = ("<div style=\"font: 8px monospace; color: #5a6b72; width: 100%; padding: 0 12mm; display: flex; justify-content: space-between;\">"
            f"<span>Pi 5 PoE NVMe Case · v0.2 · issued {ISSUED}</span><span><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></span></div>")
    pg.pdf(path=str(raw), format="A4", print_background=True, prefer_css_page_size=True,
           display_header_footer=True, header_template="<span></span>", footer_template=foot,
           margin={"top": "12mm", "bottom": "15mm", "left": "12mm", "right": "12mm"})
    b.close()
    return raw


def attach(raw):
    cmd = ["qpdf", str(raw), "--compress-streams=y", "--object-streams=generate"]
    for n in STLS:
        cmd += ["--add-attachment", str(ROOT / "print" / n), f"--key={n}", "--mimetype=model/stl",
                f"--description=Print-ready STL: {n}", "--"]
    cmd.append(str(OUT))
    subprocess.run(cmd, check=True)
    from pypdf import PdfReader, PdfWriter        # open with the attachments panel showing
    w = PdfWriter(clone_from=PdfReader(str(OUT)))
    w.page_mode = "/UseAttachments"
    w.add_metadata({"/Subject": "Raspberry Pi 5 case for the Waveshare PoE HAT (G) and Pimoroni NVMe Base Duo: drawings, 3D views, print notes, STLs attached"})
    tmp = OUT.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as f:
        w.write(f)
    tmp.replace(OUT)


if __name__ == "__main__":
    with sync_playwright() as pw:
        shots = render_views(pw)
        raw = build_pdf(pw, shots)
    attach(raw)
    print(OUT, human(OUT.stat().st_size))
