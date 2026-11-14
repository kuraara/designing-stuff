#!/usr/bin/env python3
"""Assemble the review page (single self-contained HTML) from drawings.json + print_times.json."""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
D = json.loads((ROOT / "drawings.json").read_text())
T = json.loads((ROOT / "print_times.json").read_text())
LAYOUTS = list(D)
DEFAULT = "2x2"


def hm(m):
    h, mm = divmod(int(round(m)), 60)
    return f"{h}h {mm:02d}m" if h else f"{mm}m"


def f1(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


def totals(L):
    t, p = T[f"{L}_tub"], T[f"{L}_plate"]
    return {f: {"min": t[f]["min"] + p[f]["min"], "g": t[f]["g"] + p[f]["g"]} for f in ("PLA", "PETG")}


def footprint_svg(I):
    W, H = 222, 152
    Xo, Yo = I["Xo"], I["Yo"]
    ox, oy = (W - Xo) / 2, (H - Yo) / 2
    yflip = lambda y: H - (oy + y)
    s = [f'<svg viewBox="0 0 {W} {H}" class="fp" aria-hidden="true">',
         f'<rect class="fp-box" x="{ox:.1f}" y="{oy:.1f}" width="{Xo:.1f}" height="{Yo:.1f}" rx="5"/>',
         f'<rect class="fp-bay" x="{ox + I["wall"]:.1f}" y="{yflip(Yo - I["wall"]):.1f}" width="{Xo - 2 * I["wall"]:.1f}" height="{I["bay_d"]:.1f}"/>']
    for x, y in I["buttons"]:
        s.append(f'<circle class="fp-btn" cx="{ox + x:.1f}" cy="{yflip(y):.1f}" r="18"/>')
    s.append("</svg>")
    return "".join(s)


VIEWS = [
    ("top", "Top view", "Plate from above. Bezels shown at Ø36 over the Ø29 holes. B–B and C–C mark the section planes."),
    ("plan", "Section A–A", "Horizontal cut 6.7 mm below the rim, through the screw posts and USB-C ports. Dashed red rings are the 38 mm nuts. Amber dashed: battery holder on the floor. Green: the two boards, hanging from the plate underside. The rocker body is grey."),
    ("front", "Section B–B", "Cut through the front row of buttons. Button profile is an approximate envelope: bezel, nut, barrel, microswitch, tabs, then the dashed zone kept clear for spade connectors and wire bends."),
    ("side", "Section C–C", "Cut through the first column, viewed from the right. Front is on the left, the electronics bay on the right."),
    ("back", "Back elevation", "Back wall seen from behind: charge port, ESP32 programming port and power rocker. USB-C cut-outs 12.5 × 7, rocker 15.2 × 10.2. Dimensions are to centres."),
]


def layout_block(L):
    I = D[L]["info"]
    n = I["cols"] * I["rows"]
    tt = totals(L)
    screws = len(I["screw_pts"])
    rows = []
    for part, key in (("Tub", f"{L}_tub"), ("Top plate", f"{L}_plate")):
        r = T[key]
        rows.append(f"<tr><th scope='row'>{part}</th><td>{hm(r['PLA']['min'])}<span>{r['PLA']['g']:.0f} g</span></td>"
                    f"<td>{hm(r['PETG']['min'])}<span>{r['PETG']['g']:.0f} g</span></td></tr>")
    rows.append(f"<tr class='tot'><th scope='row'>Box total</th><td>{hm(tt['PLA']['min'])}<span>{tt['PLA']['g']:.0f} g</span></td>"
                f"<td>{hm(tt['PETG']['min'])}<span>{tt['PETG']['g']:.0f} g</span></td></tr>")
    extra = []
    if I["center_posts"]:
        extra.append(f"{len(I['center_posts'])} centre support post{'s' if len(I['center_posts']) > 1 else ''} under the plate")
    if I["has_mid"]:
        extra.append("mid posts on both long walls")
    if I["field_x"] < I["Xi"]:
        extra.append(f"widened to {f1(I['Xi'])} mm inside so the battery holder fits")
    note = (" · ".join(extra)).capitalize()
    cards = []
    for key, title, cap in VIEWS:
        cards.append(f'<figure class="dwg-card"><figcaption><h3>{title}</h3><p>{cap}</p></figcaption>'
                     f'<div class="dwg-wrap" tabindex="0" role="button" aria-label="Enlarge {title}">{D[L]["views"][key]}'
                     f'<span class="zoom-hint">Tap to enlarge</span></div></figure>')
    return f"""
<section class="layout" id="panel-{L}" data-layout="{L}" hidden>
  <header class="lay-head">
    <h2><span class="lay-name">{L.replace('x', '×')}</span> {n} button{'s' if n > 1 else ''}</h2>
    <dl class="spec">
      <div><dt>Outside W × D × H</dt><dd>{f1(I['Xo'])} × {f1(I['Yo'])} × {f1(I['Ho'] + I['plate_t'])}</dd></div>
      <div><dt>Inside</dt><dd>{f1(I['Xi'])} × {f1(I['Yi'])} × {f1(I['Hi'])}</dd></div>
      <div><dt>Plate screws</dt><dd>{screws} × M3 csk</dd></div>
      <div><dt>Battery</dt><dd>1 × 21700 / 18650</dd></div>
    </dl>
    {f'<p class="lay-note">{note}.</p>' if note else ''}
  </header>
  <div class="times">
    <table>
      <caption>Estimated print time · 0.30 mm DRAFT, 0.4 nozzle</caption>
      <thead><tr><th></th><th scope="col">PLA</th><th scope="col">PETG</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <div class="dwgs">{''.join(cards)}</div>
</section>"""


fp_cards = []
for L in LAYOUTS:
    I = D[L]["info"]; tt = totals(L)
    fp_cards.append(
        f'<a class="fp-card" href="#{L}" data-layout="{L}" aria-label="{L} layout">{footprint_svg(I)}'
        f'<span class="fp-name">{L.replace("x", "×")}</span>'
        f'<span class="fp-dims">{f1(I["Xo"])} × {f1(I["Yo"])} × {f1(I["Ho"] + I["plate_t"])}</span>'
        f'<span class="fp-time">PLA {hm(tt["PLA"]["min"])}<br>PETG {hm(tt["PETG"]["min"])}</span></a>')

coupon, feet = T["fit_coupon"], T["feet_tpu"]

html = f"""<title>Arcade Button Box</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&display=swap">
<style>
/* Layout: a drafting sheet. Footprint selector (to scale) on top, then one layout's spec, times and stacked drawings. */
:root {{
  --paper: #eef2f1; --sheet: #f9fbfa; --ink: #1b2a31; --muted: #5a6b72; --rule: #c9d3d3;
  --cut-bg: #dbe3e3; --hatch: #7e9196; --dim: #0b6b87; --btn: #c8322b; --pcb: #2a7d4a; --batt: #b07a06;
  --f-display: "Saira Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper: #10171a; --sheet: #162024; --ink: #dbe6e8; --muted: #8fa3a8; --rule: #2c3b40;
  --cut-bg: #24333a; --hatch: #4f666c; --dim: #4fb6d6; --btn: #ff6a5c; --pcb: #5cc485; --batt: #e9ae35; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --paper: #10171a; --sheet: #162024; --ink: #dbe6e8; --muted: #8fa3a8; --rule: #2c3b40;
  --cut-bg: #24333a; --hatch: #4f666c; --dim: #4fb6d6; --btn: #ff6a5c; --pcb: #5cc485; --batt: #e9ae35; color-scheme: dark; }}
body {{ background: var(--paper); color: var(--ink); font: 15px/1.55 var(--f-body); }}
.wrap {{ max-width: 980px; margin: 0 auto; padding-block: 20px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 28px; }}
h1, h2, h3 {{ font-family: var(--f-display); text-wrap: balance; margin: 0; letter-spacing: .01em; }}
h1 {{ font-size: clamp(2.1rem, 7vw, 3.2rem); line-height: 1; font-weight: 700; text-transform: uppercase; }}
h2 {{ font-size: 1.7rem; font-weight: 600; line-height: 1.1; }}
h3 {{ font-size: 1.15rem; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }}
p {{ margin: 0; }}
.eyebrow {{ font: 500 12px/1.2 var(--f-mono); color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }}
.intro {{ display: grid; gap: 10px; }}
.lede {{ max-width: 64ch; color: var(--ink); }}
.lede b {{ font-weight: 600; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.chip {{ font: 500 12px/1 var(--f-mono); border: 1px solid var(--rule); border-radius: 3px; padding: 6px 8px; color: var(--muted); background: var(--sheet); }}

/* footprint selector */
.fp-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
@media (max-width: 640px) {{ .fp-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.fp-card {{ display: grid; gap: 2px; padding: 10px 10px 12px; background: var(--sheet); border: 1px solid var(--rule);
  border-radius: 4px; color: inherit; text-decoration: none; min-width: 0; }}
.fp-card:hover {{ border-color: var(--dim); }}
.fp-card:focus-visible {{ outline: 2px solid var(--dim); outline-offset: 2px; }}
.fp-card[aria-current="true"] {{ border-color: var(--btn); box-shadow: inset 0 0 0 1px var(--btn); }}
.fp {{ width: 100%; height: auto; display: block; margin-bottom: 4px; }}
.fp-box {{ fill: var(--cut-bg); stroke: var(--ink); stroke-width: 1.2; }}
.fp-bay {{ fill: var(--paper); stroke: var(--hatch); stroke-dasharray: 3 2; stroke-width: .8; }}
.fp-btn {{ fill: var(--btn); fill-opacity: .85; }}
.fp-name {{ font: 700 1.35rem/1 var(--f-display); }}
.fp-dims, .fp-time {{ font: 12px/1.35 var(--f-mono); color: var(--muted); font-variant-numeric: tabular-nums; }}
.scale-note {{ font: 12px/1.4 var(--f-mono); color: var(--muted); }}

/* selected layout */
.layout {{ display: grid; gap: 18px; }}
.lay-head {{ display: grid; gap: 12px; border-top: 2px solid var(--ink); padding-top: 14px; }}
.lay-name {{ color: var(--btn); margin-right: .25em; }}
.spec {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; margin: 0; background: var(--rule); border: 1px solid var(--rule); }}
@media (max-width: 640px) {{ .spec {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.spec div {{ background: var(--sheet); padding: 8px 10px; min-width: 0; }}
.spec dt {{ font: 500 11px/1.3 var(--f-mono); text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
.spec dd {{ margin: 2px 0 0; font: 500 15px/1.3 var(--f-mono); font-variant-numeric: tabular-nums; }}
.lay-note {{ color: var(--muted); font-size: 14px; }}
.times table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; background: var(--sheet); border: 1px solid var(--rule); }}
.times caption {{ text-align: left; font: 500 12px/1.4 var(--f-mono); color: var(--muted); padding-bottom: 6px; text-transform: uppercase; letter-spacing: .04em; }}
.times th, .times td {{ padding: 9px 10px; border-bottom: 1px solid var(--rule); text-align: left; }}
.times thead th {{ font: 600 13px/1 var(--f-body); color: var(--muted); }}
.times td {{ font: 500 15px/1.2 var(--f-mono); }}
.times td span {{ display: inline-block; margin-left: 8px; font-size: 12px; color: var(--muted); font-weight: 400; }}
.times tr.tot th, .times tr.tot td {{ border-bottom: 0; font-weight: 600; }}
.times tbody th {{ font-weight: 500; }}

/* drawings */
.dwgs {{ display: grid; gap: 16px; }}
.dwg-card {{ margin: 0; background: var(--sheet); border: 1px solid var(--rule); border-radius: 4px; padding: 12px; display: grid; gap: 8px; min-width: 0; }}
.dwg-card figcaption {{ display: grid; gap: 4px; }}
.dwg-card figcaption p {{ font-size: 13.5px; color: var(--muted); max-width: 70ch; }}
.dwg-wrap {{ position: relative; cursor: zoom-in; border-radius: 3px; }}
.dwg-wrap:focus-visible {{ outline: 2px solid var(--dim); outline-offset: 3px; }}
.zoom-hint {{ position: absolute; right: 0; bottom: 0; font: 11px/1 var(--f-mono); color: var(--muted); background: var(--sheet); padding: 4px 2px 0 6px; }}
@media (hover: hover) {{ .zoom-hint {{ display: none; }} }}
svg.dwg {{ width: 100%; height: auto; display: block; max-height: 78vh; }}
.dwg * {{ vector-effect: non-scaling-stroke; }}
.dwg .panel {{ fill: var(--cut-bg); stroke: var(--ink); stroke-width: 1.4px; }}
.dwg .cutf {{ fill: url(#hatch); stroke: var(--ink); stroke-width: 1.4px; }}
.dwg .bayzone {{ fill: none; stroke: var(--hatch); stroke-width: 1px; stroke-dasharray: 5 3; }}
.dwg .bezel {{ fill: var(--btn); fill-opacity: .16; stroke: var(--btn); stroke-width: 1.2px; }}
.dwg .plunger {{ fill: var(--btn); fill-opacity: .55; stroke: none; }}
.dwg .nut {{ fill: none; stroke: var(--btn); stroke-width: 1px; stroke-dasharray: 4 3; }}
.dwg .barrel {{ fill: none; stroke: var(--btn); stroke-width: .8px; stroke-opacity: .6; }}
.dwg .btnf {{ fill: var(--btn); fill-opacity: .7; stroke: var(--btn); stroke-width: .8px; }}
.dwg .btno {{ fill: var(--btn); fill-opacity: .12; stroke: var(--btn); stroke-width: 1px; }}
.dwg .clr {{ fill: var(--btn); fill-opacity: .05; stroke: var(--btn); stroke-width: .8px; stroke-dasharray: 3 3; }}
.dwg .batt {{ fill: var(--batt); fill-opacity: .14; stroke: var(--batt); stroke-width: 1.2px; stroke-dasharray: 6 3; }}
.dwg .pcb {{ fill: var(--pcb); fill-opacity: .2; stroke: var(--pcb); stroke-width: 1.2px; }}
.dwg .usb {{ fill: var(--muted); stroke: var(--ink); stroke-width: .8px; }}
.dwg .rock {{ fill: var(--muted); fill-opacity: .12; stroke: var(--muted); stroke-width: 1px; stroke-dasharray: 3 2; }}
.dwg .ext {{ stroke: var(--dim); stroke-width: .7px; stroke-opacity: .8; }}
.dwg .dl {{ stroke: var(--dim); stroke-width: .9px; }}
.dwg .ar {{ fill: var(--dim); stroke: none; }}
.dwg .cut {{ stroke: var(--dim); stroke-width: 1.1px; stroke-dasharray: 14 3 2 3; }}
.dwg .ld {{ stroke: var(--muted); stroke-width: .8px; }}
.dwg .ldot {{ fill: var(--muted); }}
.dwg text {{ font-family: var(--f-mono); fill: var(--ink); }}
.dwg .dt {{ fill: var(--dim); font-weight: 500; }}
.dwg .cutl {{ fill: var(--dim); font-family: var(--f-display); font-weight: 700; }}
.dwg .bt {{ fill: var(--ink); font-weight: 500; }}
.dwg .zt {{ fill: var(--muted); font-style: italic; }}
.dwg .ct {{ fill: var(--batt); font-weight: 500; }}
.dwg .lt {{ fill: var(--ink); }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font: 12px/1.3 var(--f-mono); color: var(--muted); }}
.legend i {{ display: inline-block; width: 18px; height: 10px; vertical-align: -1px; margin-right: 6px; border: 1.5px solid; }}
.lg-cut {{ background: var(--cut-bg); border-color: var(--ink) !important; }}
.lg-btn {{ border-color: var(--btn) !important; background: color-mix(in srgb, var(--btn) 18%, transparent); }}
.lg-pcb {{ border-color: var(--pcb) !important; background: color-mix(in srgb, var(--pcb) 20%, transparent); }}
.lg-bat {{ border-color: var(--batt) !important; border-style: dashed !important; }}
.lg-dim {{ border-color: var(--dim) !important; border-width: 0 0 1.5px !important; height: 6px !important; }}

/* notes */
.notes {{ display: grid; gap: 14px; }}
.notes > h2 {{ border-top: 2px solid var(--ink); padding-top: 14px; }}
details {{ background: var(--sheet); border: 1px solid var(--rule); border-radius: 4px; }}
summary {{ cursor: pointer; padding: 12px 14px; font: 600 1.15rem/1.2 var(--f-display); text-transform: uppercase; letter-spacing: .04em; list-style-position: inside; }}
summary:focus-visible {{ outline: 2px solid var(--dim); outline-offset: -2px; }}
.d-body {{ padding: 0 14px 14px; display: grid; gap: 10px; max-width: 72ch; }}
.d-body ol, .d-body ul {{ margin: 0; padding-left: 1.3em; display: grid; gap: 6px; }}
.d-body table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
.d-body th, .d-body td {{ text-align: left; padding: 6px 8px 6px 0; border-bottom: 1px solid var(--rule); vertical-align: top; }}
.d-body th {{ font: 500 12px/1.3 var(--f-mono); color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
.d-body td:first-child {{ font-family: var(--f-mono); white-space: nowrap; }}
.tbl {{ overflow-x: auto; }}
code {{ font: 13px var(--f-mono); background: var(--paper); padding: 1px 4px; border-radius: 2px; }}
.flow {{ font: 13px/1.6 var(--f-mono); background: var(--paper); border-left: 3px solid var(--pcb); padding: 8px 10px; overflow-x: auto; white-space: pre; }}
.foot {{ font-size: 13px; color: var(--muted); display: grid; gap: 6px; }}
.foot a {{ color: var(--dim); }}

/* zoom overlay */
.zoom {{ position: fixed; inset: 0; z-index: 50; background: var(--sheet); overflow: auto;
  padding: calc(56px + env(safe-area-inset-top, 0px)) max(12px, env(safe-area-inset-right, 0px)) calc(24px + env(safe-area-inset-bottom, 0px)) max(12px, env(safe-area-inset-left, 0px)); }}
.zoom svg.dwg {{ width: 230%; max-width: none; max-height: none; }}
@media (min-width: 900px) {{ .zoom svg.dwg {{ width: 140%; }} }}
.zoom-close {{ position: fixed; top: calc(10px + env(safe-area-inset-top, 0px)); right: max(12px, env(safe-area-inset-right, 0px)); z-index: 51;
  font: 600 14px/1 var(--f-body); padding: 10px 14px; border: 1px solid var(--rule); border-radius: 4px; background: var(--sheet); color: var(--ink); cursor: pointer; }}
.zoom-close:focus-visible {{ outline: 2px solid var(--dim); }}
@media (prefers-reduced-motion: no-preference) {{ .fp-card {{ transition: border-color .15s; }} }}
</style>

<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <pattern id="hatch" patternUnits="userSpaceOnUse" width="2.4" height="2.4" patternTransform="rotate(45)">
      <rect width="2.4" height="2.4" style="fill: var(--cut-bg)"/>
      <line x1="0" y1="0" x2="0" y2="2.4" style="stroke: var(--hatch); stroke-width: .45"/>
    </pattern>
  </defs>
</svg>

<main class="wrap">
  <header class="intro">
    <p class="eyebrow">Enclosure study · v0.1 · 30 Oct 2026</p>
    <h1>Arcade Button Box</h1>
    <p class="lede">Self-contained wireless button boxes for long-barrel screw-in arcade buttons. Each box is a <b>tub</b> printed floor-down and a <b>removable top plate</b> printed face-down. The plate carries the buttons and both circuit boards, so you fit the nuts on the bench with full access, then drop the plate on and screw it down. The battery lives on the floor of a 30 mm rear bay. No supports anywhere.</p>
    <div class="chips"><span class="chip">ESP32-C3 Super Mini</span><span class="chip">TP4056 USB-C + protection</span><span class="chip">1 × 21700 or 18650</span><span class="chip">50 mm pitch</span><span class="chip">Prusa MK3S+</span></div>
  </header>

  <section aria-labelledby="fam" style="display:grid;gap:10px">
    <h2 id="fam">Six layouts</h2>
    <nav class="fp-grid" aria-label="Choose a layout">{''.join(fp_cards)}</nav>
    <p class="scale-note">Footprints drawn to the same scale. Grey strip = electronics bay. Dimensions in mm, W × D × H assembled. Times are tub + plate.</p>
  </section>

  {''.join(layout_block(L) for L in LAYOUTS)}

  <div class="legend" aria-label="Drawing legend"><span><i class="lg-cut"></i>printed part (cut)</span><span><i class="lg-btn"></i>button envelope</span><span><i class="lg-pcb"></i>PCB</span><span><i class="lg-bat"></i>battery holder</span><span><i class="lg-dim"></i>dimension</span></div>

  <section class="notes" aria-labelledby="notes-h">
    <h2 id="notes-h">Shared design notes</h2>

    <details open>
      <summary>Why it's this big</summary>
      <div class="d-body">
        <div class="tbl"><table>
          <thead><tr><th>Value</th><th>Reason</th></tr></thead>
          <tbody>
            <tr><td>50 pitch</td><td>38 mm nut plus a 12 mm gap, enough for fingertips to spin a nut next to one already fitted and for wires to pass between switches.</td></tr>
            <tr><td>28 edge</td><td>Button centre to inside wall: nut radius 19 plus 9 mm for wires running along the wall.</td></tr>
            <tr><td>88 inside</td><td>78 mm button depth − 4 mm plate + 14 mm below the tabs for straight .187" spades and a wire bend. Flag (right-angle) spades let you set <code>conn_clear = 6</code> and lose 8 mm of height.</td></tr>
            <tr><td>30 bay</td><td>24 mm wide 21700 holder plus 6 mm. An 18650 holder (≈77 × 21) drops into the same fences.</td></tr>
            <tr><td>95 min. length</td><td>83 mm holder plus 6 mm each end for its leads. This is what makes the 1×1 wider than its button needs.</td></tr>
            <tr><td>Ø29.0 hole</td><td>1-1/8" (28.6) plus allowance, since FDM holes print slightly small. Check on the fit coupon.</td></tr>
            <tr><td>12.5 × 7 ports</td><td>Sized for the USB-C cable overmold, not the plug, so the plug seats fully through the 2.4 mm wall.</td></tr>
          </tbody>
        </table></div>
      </div>
    </details>

    <details>
      <summary>Assembly order</summary>
      <div class="d-body"><ol>
        <li>Print the fit coupon first ({hm(coupon['PLA']['min'])} PLA). It has the button hole, a heat-set insert post, a countersunk M3, a USB-C port and the rocker cut-out.</li>
        <li>Press M3 × 5.7 heat-set inserts into the hanging corner posts (and centre or mid posts where the layout has them).</li>
        <li>Fit the buttons to the plate on the bench, spin the nuts down, clip the microswitches on.</li>
        <li>Put 1 mm foam tape on the pocket rails and press the TP4056 and ESP32 in component-side down, USB ends against the back stops. Solder wires straight to the pads; header pins would hit the plate.</li>
        <li>Wire the switches: COM tabs daisy-chained to GND, each NO tab to its GPIO.</li>
        <li>Set the battery holder on the floor rails between the corner fences. Strap it with a zip tie under the holder between the rails, or foam tape. Run its lead up to the TP4056 through a 2-pin JST-PH so the plate can come off.</li>
        <li>Snap the KCD11 rocker into the back wall from outside and wire it in series with TP4056 OUT+.</li>
        <li>Lower the plate. The lip locates it inside the walls. Fit the countersunk screws.</li>
      </ol></div>
    </details>

    <details>
      <summary>Electronics and pin map</summary>
      <div class="d-body">
        <div class="flow">cell ─ B+/B− ─[TP4056]─ OUT+ ─[rocker]─ 5V pin ─[ESP32-C3]
                    └ OUT− ──────────────── GND
OUT+ ─ 100k ─┬─ 100k ─ GND      (tap → GPIO4 for battery voltage)</div>
        <p>The rocker sits after the charger, so the cell charges with the box switched off. Switch off for a full charge; the ESP32 load can stop the TP4056 from terminating cleanly. The Super Mini's 3.3 V regulator runs from the 5V pin down to roughly a 3.5 V cell, which covers most of the capacity. Remove its red power LED if you use deep sleep.</p>
        <div class="tbl"><table>
          <thead><tr><th>Signal</th><th>Pin</th><th>Note</th></tr></thead>
          <tbody>
            <tr><td>B1</td><td>GPIO0</td><td>Deep-sleep wake capable</td></tr>
            <tr><td>B2</td><td>GPIO1</td><td>Wake capable</td></tr>
            <tr><td>B3</td><td>GPIO3</td><td>Wake capable</td></tr>
            <tr><td>B4</td><td>GPIO5</td><td>Wake capable</td></tr>
            <tr><td>B5</td><td>GPIO2</td><td>Wake capable. Strapping pin, so don't hold B5 while resetting</td></tr>
            <tr><td>B6</td><td>GPIO6</td><td>No deep-sleep wake; light sleep is fine</td></tr>
            <tr><td>VBAT</td><td>GPIO4</td><td>ADC1, via the divider above</td></tr>
            <tr><td>LED</td><td>GPIO8</td><td>Onboard blue LED</td></tr>
          </tbody>
        </table></div>
        <p>Buttons use internal pull-ups and switch to GND. Only GPIO0–5 can wake the C3 from deep sleep, and only GPIO0–4 have the reliable ADC, which is why six buttons plus battery sensing lands like this.</p>
      </div>
    </details>

    <details>
      <summary>Printing</summary>
      <div class="d-body"><ul>
        <li>Times are PrusaSlicer 2.7 estimates using the stock Original Prusa i3 MK3S &amp; MK3S+ profile, 0.30 mm DRAFT (2 perimeters, 15 % grid), Generic PLA and Generic PETG. No supports, no brim.</li>
        <li>Tub: floor on the bed. The corner posts hang from the rim with a 45° underside, and the port holes bridge 12.5–15 mm.</li>
        <li>Plate: top face on the bed (a textured sheet gives a good top). The lip, board pockets and countersinks all print without support.</li>
        <li>Height is the main cost: the tub is 90 mm tall because the buttons are. Dropping <code>wall</code> and <code>floor_t</code> from 2.4 to 1.6 cut the 2×2 tub from {hm(T['2x2_tub']['PLA']['min'])} to 5h 38m in PLA.</li>
        <li>Fit coupon: {hm(coupon['PLA']['min'])} PLA / {hm(coupon['PETG']['min'])} PETG. TPU feet (set of 4, Ø12 × 3, into 1 mm recesses): {hm(feet['TPU']['min'])}.</li>
        <li>PETG copes better with a hot car or a sunny desk. PLA is fine indoors.</li>
      </ul></div>
    </details>

    <details>
      <summary>Hardware per box</summary>
      <div class="d-body"><ul>
        <li>4–6 × M3 × 8 countersunk screws and M3 × 5.7 heat-set inserts (4 on 1×1 to 1×3, 5 on 2×2, 6 on 1×4 and 2×3)</li>
        <li>ESP32-C3 Super Mini, TP4056 USB-C module with protection, KCD11 mini rocker (15 × 10 cut-out)</li>
        <li>1-cell 21700 or 18650 holder with leads, JST-PH 2-pin pair</li>
        <li>.187" female spades (2 per button), 24–26 AWG wire, 1 mm foam tape</li>
        <li>4 × Ø12 feet (printed TPU or stick-on)</li>
      </ul></div>
    </details>

    <details open>
      <summary>Measure before printing</summary>
      <div class="d-body"><ul>
        <li><b>Button depth</b>: from the underside of the bezel to the tips of the microswitch tabs. The design assumes 78 mm. Every millimetre here is a millimetre of box height (<code>btn_depth</code>).</li>
        <li><b>Nut diameter</b>: assumed 38 mm (<code>btn_nut_d</code>). A bigger nut means a bigger pitch.</li>
        <li><b>Your spade type</b>: straight or flag (<code>conn_clear</code> 14 or 6).</li>
        <li><b>Board sizes</b>: TP4056 modules vary between about 26 and 28 mm long.</li>
      </ul>
      <p>Two cells: set <code>cells = 2</code>. The bay grows to 52 mm and every box gets 22 mm deeper.</p></div>
    </details>
  </section>

  <footer class="foot">
    <p>Source: <code>button_box.scad</code> (OpenSCAD, all values above are parameters) in the Designing stuff project, with a handoff README.</p>
    <p>Part data: <a href="https://www.electrokit.com/en/tryckknapp-arkad-35mm-bla" target="_blank" rel="noopener">28 mm button hole</a> · <a href="https://probots.co.in/1-x-21700-cell-lithium-ion-battery-holder-dip-socket.html" target="_blank" rel="noopener">21700 holder 83 × 24 × 22</a> · <a href="https://mischianti.org/esp32-c3-super-mini-high-resolution-pinout-datasheet-and-specs/" target="_blank" rel="noopener">ESP32-C3 Super Mini 22.5 × 18</a> · <a href="https://makerselectronics.com/product/tp4056-type-c-lithium-charging-module/" target="_blank" rel="noopener">TP4056 USB-C 28 × 17</a></p>
  </footer>
</main>

<script>
(function () {{
  const layouts = {json.dumps(LAYOUTS)};
  const fallback = "{DEFAULT}";
  function show() {{
    const h = location.hash.slice(1);
    const cur = layouts.includes(h) ? h : fallback;
    document.querySelectorAll(".layout").forEach(s => {{ s.hidden = s.dataset.layout !== cur; }});
    document.querySelectorAll(".fp-card").forEach(a => a.setAttribute("aria-current", a.dataset.layout === cur ? "true" : "false"));
  }}
  window.addEventListener("hashchange", () => {{
    show();
    const p = document.querySelector(".layout:not([hidden])");
    if (p && layouts.includes(location.hash.slice(1))) p.scrollIntoView({{ block: "start" }});
  }});
  show();

  let overlay = null, lastFocus = null;
  function closeZoom() {{ if (overlay) {{ overlay.remove(); overlay = null; document.body.style.overflow = ""; lastFocus && lastFocus.focus(); }} }}
  function openZoom(wrap) {{
    lastFocus = wrap;
    overlay = document.createElement("div");
    overlay.className = "zoom";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-label", "Enlarged drawing");
    const btn = document.createElement("button");
    btn.className = "zoom-close"; btn.type = "button"; btn.textContent = "Close";
    btn.addEventListener("click", closeZoom);
    overlay.appendChild(btn);
    overlay.appendChild(wrap.querySelector("svg").cloneNode(true));
    document.body.appendChild(overlay);
    document.body.style.overflow = "hidden";
    btn.focus();
  }}
  document.querySelectorAll(".dwg-wrap").forEach(w => {{
    w.addEventListener("click", () => openZoom(w));
    w.addEventListener("keydown", e => {{ if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); openZoom(w); }} }});
  }});
  document.addEventListener("keydown", e => {{ if (e.key === "Escape") closeZoom(); }});
}})();
</script>
"""
out = ROOT / "arcade_button_box.html"
out.write_text(html)
print(out, len(html) // 1024, "KB")
