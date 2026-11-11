#!/usr/bin/env python3
"""Assemble the review page (single self-contained HTML) from drawings.json, info/info.json and print_times.json."""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
D = json.loads((ROOT / "drawings.json").read_text())
I = json.loads((ROOT / "info" / "info.json").read_text())
T = json.loads((ROOT / "print_times.json").read_text())


def hm(m):
    h, mm = divmod(int(round(m)), 60)
    return f"{h}h {mm:02d}m" if h else f"{mm}m"


def f1(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


L, W, H = I["L_total"], I["W"], I["H"]
feet_h = I["foot"][1] - 0.6
body_p, body3 = T["body"]["PETG"], T["body_wall3"]["PETG"]
lid_t = T["lid"]["PLA"]
lid_g = T["lid"]["PETG"]
ret_t = T["retainer"]["TPU"]
RT = I["ret"]
din_s = T["din"]["PETG_strong"]
LT = I["latch"]
feet = T["feet"]["TPU"]
total = body_p["min"] + lid_t["min"] + T["retainer"]["TPU"]["min"] + feet["min"]
saved = body3["min"] - body_p["min"]

GROUPS = [
    ("Cross-section", [
        ("a", "Section A–A · across", "Your second sketch. Each board sits on its own ledge and nothing screws into either board. The upper lip runs between the two boards: the Pi rests on its top, and the Duo's edge runs in the recess under it, resting on the lower lip. Below that the wall steps back out to make the SSD bay."),
        ("ledge", "Detail · the ledges (3:1)", "A 1.2 mm fence on each ledge, lower than the PCB, keeps each board centred with 0.4 mm play a side. The Pi's ledge only reaches 1 mm under it: the GPIO solder joints and the jack tabs on the Pi's underside start about 1.4 mm in from the edge. The Duo's ledge reaches 3 mm, clear of the SSDs."),
        ("ledge_win", "Detail · ledges at the port window (3:1)", "A chunky USB-C plug's overmold hangs about 2 mm below the Pi's board edge. Along the 42 mm port window the upper lip's outer half drops 2.5 mm so the plug can seat; the 1 mm ledge under the Pi carries on, tied to the wall lower down."),
    ]),
    ("Lengthwise", [
        ("c", "Section C–C · along the GPIO-side ledges", "Both lips run the full length. The boards slide in from the SD end, USB first, together (the ribbon joins them) and stop on the closed end wall. The TPU card retainer (v0.4) sits behind them; its fingers spring against both boards' corners."),
        ("b", "Section B–B · down the middle", "Centre line, through the first USB stack. The PCIe ribbon loops round the SD end of the boards; there is 10 mm for it between the boards and the lid."),
    ]),
    ("Outside", [
        ("side", "Side elevation · HDMI / USB-C side", "One 42 × 11 window covers USB-C and both micro HDMI, sized for a dock cable's overmold. Below it, slots vent the space between the two boards. Near the lid, the upper small window takes the lid's latch hook; the lower one is now just a vent. The other long side has the same vents without the port window."),
        ("end", "USB / RJ45 end", "The closed end of the body. It prints first, flat on the bed. Cut-outs are 0.5 mm clear of each jack."),
        ("top", "Top", "Roof vents: 3 mm slots on a 6.25 mm pitch in three rows. The bars between rows stiffen the roof."),
        ("bottom", "Bottom", "Floor vents under the SSDs. M3 heat-set inserts for the four feet sit in the thick SSD-bay walls, inside 0.6 mm locating recesses."),
    ]),
    ("DIN rail bracket", [
        ("din_side", "On the rail · side view", "Optional mount in place of the feet. The case stands with its length vertical, here USB end down so cables hang (the bolt pattern is symmetric, so it also bolts on the other way up). Its floor vents open into a 14 mm chimney behind it."),
        ("din_plan", "Bracket · plan", "Seen from the case side, cut through the plate. Four M3 × 20 socket heads go through counterbored bosses into the foot inserts. The tall side ribs run under the case's thick lower walls, clear of the floor vents, and stiffen the whole bracket. The window and the flexure gaps let air through."),
        ("din_clip", "Bracket · clip on the rail (2:1)", "A fixed hook runs the full width on one flange. The other flange gets a latch on four flexures with a lead-in ramp, so it snaps on when pushed. To remove it, lever the pull tab with a screwdriver; a stop limits the latch to 2.2 mm of travel so it can't be overbent, and the hook stays engaged even then. Rail contact is spread across the bracket's full width."),
    ]),
    ("TPU card retainer (v0.4)", [
        ("ret", "Retainer · seen from the mouth", "TPU ring pushed into the mouth behind the boards, before the lid. It's a 0.15 mm press fit all round, and the middle stays open for the PCIe ribbon and air. Three leaning fingers spring against the board corners: both Duo corners and the Pi's GPIO-side corner. The Pi's power-button corner is left free. Four bumps drop into the first roof and floor vent slots of the printed body."),
        ("ret_finger", "Detail · finger on the Duo corner (3:1)", f"Plan cut at the Duo. The finger leans about 40°, so the board edge bends it instead of crushing it: {f1(RT['tip'] - RT['edge'])} mm of preload gives a few newtons per finger. Printed, the lean is a 40° overhang."),
        ("ret_bump", "Detail · bump in a roof vent (3:1)", "The bump's back face is square and catches on the mouth-side end of the vent slot, so the boards can't push the retainer out. It prints straight off the bed. To remove the retainer, press the four bumps in through the vents and pull it out by the ring."),
    ]),
    ("Lid and feet", [
        ("lid", "Lid · inside face", "v0.4, PLA or PETG. A 6 mm skirt locates it in the mouth. On each long side, slots cut a 19 mm arm out of the skirt, fixed at its top end; its hook clicks into the body's upper side window. No prongs any more: the card retainer holds the boards, so the lid only closes the case."),
        ("latch", "Detail · latch in the window (4:1)", f"Plan cut through the hook. The arm is {f1(LT['t'])} mm thick and bends sideways, in the plane of the print layers, so PLA flexes along its filaments; at the {LT['flex']:.2f} mm it moves to pass the wall, the strain is about {LT['strain'] * 100:.1f}%. The hook's lower face is a 45° overhang as printed; the lead-in is gentler, so it pushes in more easily than it pulls out."),
        ("foot", "Foot", f"v0.4. TPU, Ø14 × {f1(I['foot'][1])}, printed counterbore-up. Fit it counterbore toward the desk: an M3 × 8 button or socket head sits in the Ø{f1(I['foot_cb'][0])} × {f1(I['foot_cb'][1])} counterbore with 3 mm of TPU under it, and 5 mm of thread goes into the heat-set insert."),
    ]),
]

cards = []
for gname, views in GROUPS:
    cards.append(f'<h3 class="grp">{gname}</h3>')
    for key, title, cap in views:
        cards.append(f'<figure class="dwg-card"><figcaption><h4>{title}</h4><p>{cap}</p></figcaption>'
                     f'<div class="dwg-wrap" tabindex="0" role="button" aria-label="Enlarge {title}">{D[key]}'
                     f'<span class="zoom-hint">Tap to enlarge</span></div></figure>')

BRIEF = """Let’s make a raspberry pi 5 case. Requirements:
- it has a PoE hat (check my Gmail inbox for order confirmations from Core Electronics for the part number)
- it has a pimoroni dual nvme base

I want to avoid screw holes, I would prefer. Refer to this sketch of the side profile showing how I would like the pi and the nvme base to sit on a lip

The nvme base will need enough vertical clearance from the pi to account for thick nvme disks (dual Samsung 1TB)

For the USBC port, it will need enough clearance to account for fairly chunky usb connectors like the ones on dell thunderbolt docks

Previous designs I have made use. 3mm walls but that’s not a hard requirement. If strength can be gained through smart use of webbing and structural ribs then that would be ideal if print time can be optimised

Printing in 2-3 parts would be ideal,
- main body
- lid

If the lid is on the smallest face (the usb/rj45 end) or the sd card  end that would be ideal. The pi can slide in like into the case as if it were a tube

Attaching the end pieces “lids” can wither be screw in (m3, counter bore heads, or a nice click in place) for a screwless click in place I would print that from TPU to allow for some flex with whatever you use, and it can still retain some rigidity

Give it ventilation holes top and bottom, you can increase the space between the inner walls and the nvme base/poe hat as they tend to generate a bit of heat

It will also need some feet that can be screwed in with m3  counterbored screws

Make some sort of tray for the as card so it can be slotted in and out like a SIM card

I think those are all the requirements for now

Create 2d projections before the 3d model"""

FOLLOWUPS = ["I’d prefer the cross section be like this  [second sketch]",
             "I don’t want to screw into the pi or the nvme base, the idea is for this to be simple",
             "Alright skip the sad card holder stuff",
             "1. Samsung 980EVO",
             "2. No idea",
             "3. Not fussed, the gpio pins hold it in pretty snugly",
             "Let’s create another component that uses the footprint of the feet to attach it to the case.",
             "It will be a bracket to mount it on a DIN rail",
             "Leave plenty of clearance for the airflow, make sure the bracket is sturdy and rigid as people may be rough installing and removing it",
             "",
             "11 Nov, after printing:",
             "The case printed well, the little tabs on the lid did not print at all",
             "PLA might be able to do the job if you make the tabs thin enough to flex a little",
             "The rails are doing a good job of securing the nvme base",
             "I can shake the case and the base is secure",
             "Can you confirm your design of the feet suit these screws  [2 photos: button-head screw in calipers]",
             "Then I think securing the cards should be separate from the back lid. So we make a TPU insert that locks the cards in tightly, then the pla lid goes on after that",
             "If there’s a better way to do that then by all means suggest it and don’t be 100% stuck to the shape of this bit  [photo: sketch of a frame in the mouth pressing the board edges]"]

html = f"""<title>Pi 5 PoE NVMe Case</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&display=swap">
<style>
/* Layout: a drafting sheet. Spec strip and open questions first, then drawings grouped by what they explain, then notes. */
:root {{
  --paper: #eef2f1; --sheet: #f9fbfa; --ink: #1b2a31; --muted: #5a6b72; --rule: #c9d3d3;
  --cut-bg: #dbe3e3; --hatch: #7e9196; --dim: #0b6b87; --red: #c8322b; --pcb: #2a7d4a; --amber: #b07a06;
  --lid: #2b4f8a; --lid-bg: #d6e3f4; --ssd: #6b4bb5; --hw: #6f7a7e;
  --f-display: "Saira Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper: #10171a; --sheet: #162024; --ink: #dbe6e8; --muted: #8fa3a8; --rule: #2c3b40;
  --cut-bg: #24333a; --hatch: #4f666c; --dim: #4fb6d6; --red: #ff6a5c; --pcb: #5cc485; --amber: #e9ae35;
  --lid: #8fb4ec; --lid-bg: #1d2c43; --ssd: #a98cf0; --hw: #9aa7ab; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --paper: #10171a; --sheet: #162024; --ink: #dbe6e8; --muted: #8fa3a8; --rule: #2c3b40;
  --cut-bg: #24333a; --hatch: #4f666c; --dim: #4fb6d6; --red: #ff6a5c; --pcb: #5cc485; --amber: #e9ae35;
  --lid: #8fb4ec; --lid-bg: #1d2c43; --ssd: #a98cf0; --hw: #9aa7ab; color-scheme: dark; }}
body {{ background: var(--paper); color: var(--ink); font: 15px/1.55 var(--f-body); }}
.wrap {{ max-width: 980px; margin: 0 auto; padding-block: 20px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 28px; }}
h1, h2, h3, h4 {{ font-family: var(--f-display); text-wrap: balance; margin: 0; letter-spacing: .01em; }}
h1 {{ font-size: clamp(2.1rem, 7vw, 3.2rem); line-height: 1; font-weight: 700; text-transform: uppercase; }}
h2 {{ font-size: 1.7rem; font-weight: 600; line-height: 1.1; border-top: 2px solid var(--ink); padding-top: 14px; }}
h3.grp {{ font-size: 1.25rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); margin-top: 8px; }}
h4 {{ font-size: 1.15rem; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }}
p {{ margin: 0; }}
section {{ display: grid; gap: 14px; min-width: 0; }}
.eyebrow {{ font: 500 12px/1.2 var(--f-mono); color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }}
.intro {{ display: grid; gap: 10px; }}
.lede {{ max-width: 66ch; }}
.lede b {{ font-weight: 600; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.chip {{ font: 500 12px/1 var(--f-mono); border: 1px solid var(--rule); border-radius: 3px; padding: 6px 8px; color: var(--muted); background: var(--sheet); }}
.spec {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; margin: 0; background: var(--rule); border: 1px solid var(--rule); }}
@media (max-width: 640px) {{ .spec {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.spec div {{ background: var(--sheet); padding: 8px 10px; min-width: 0; }}
.spec dt {{ font: 500 11px/1.3 var(--f-mono); text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
.spec dd {{ margin: 2px 0 0; font: 500 15px/1.3 var(--f-mono); font-variant-numeric: tabular-nums; }}

/* open questions: the review gate */
.ask {{ background: var(--sheet); border: 1px solid var(--rule); border-left: 4px solid var(--red); border-radius: 4px; padding: 14px 16px; display: grid; gap: 12px; }}
.ask ol {{ margin: 0; padding-left: 1.4em; display: grid; gap: 10px; max-width: 72ch; }}
.ask li::marker {{ font: 600 15px var(--f-mono); color: var(--red); }}
.ask.settled {{ border-left-color: var(--pcb); }}
.ask ul {{ margin: 0; padding-left: 1.2em; display: grid; gap: 8px; max-width: 72ch; }}
.ask.settled li::marker {{ color: var(--pcb); }}
.ask b {{ font-weight: 600; }}

.times table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; background: var(--sheet); border: 1px solid var(--rule); }}
.times caption {{ text-align: left; font: 500 12px/1.4 var(--f-mono); color: var(--muted); padding-bottom: 6px; text-transform: uppercase; letter-spacing: .04em; }}
.times th, .times td {{ padding: 9px 10px; border-bottom: 1px solid var(--rule); text-align: left; vertical-align: top; }}
.times thead th {{ font: 600 13px/1 var(--f-body); color: var(--muted); }}
.times td {{ font: 500 15px/1.2 var(--f-mono); white-space: nowrap; }}
.times td.mat {{ font: 400 13px/1.3 var(--f-body); color: var(--muted); white-space: normal; }}
.times td span {{ display: inline-block; margin-left: 8px; font-size: 12px; color: var(--muted); font-weight: 400; }}
.times tr.tot th, .times tr.tot td {{ border-bottom: 0; font-weight: 600; }}
.times tbody th {{ font-weight: 500; }}
.tbl {{ overflow-x: auto; }}
.note {{ font-size: 13.5px; color: var(--muted); max-width: 72ch; }}

/* drawings */
.dwgs {{ display: grid; gap: 16px; }}
.dwg-card {{ margin: 0; background: var(--sheet); border: 1px solid var(--rule); border-radius: 4px; padding: 12px; display: grid; gap: 8px; min-width: 0; }}
.dwg-card figcaption {{ display: grid; gap: 4px; }}
.dwg-card figcaption p {{ font-size: 13.5px; color: var(--muted); max-width: 72ch; }}
.dwg-wrap {{ position: relative; cursor: zoom-in; border-radius: 3px; }}
.dwg-wrap:focus-visible {{ outline: 2px solid var(--dim); outline-offset: 3px; }}
.zoom-hint {{ position: absolute; right: 0; bottom: 0; font: 11px/1 var(--f-mono); color: var(--muted); background: var(--sheet); padding: 4px 2px 0 6px; }}
@media (hover: hover) {{ .zoom-hint {{ display: none; }} }}
svg.dwg {{ width: 100%; height: auto; display: block; max-height: 78vh; }}
.dwg * {{ vector-effect: non-scaling-stroke; }}
.dwg .cutf {{ fill: url(#hatch); stroke: var(--ink); stroke-width: 1.4px; }}
.dwg .cutl {{ fill: url(#hatchl); stroke: var(--lid); stroke-width: 1.4px; }}
.dwg .cutr {{ fill: var(--lid-bg); stroke: var(--lid); stroke-width: 1.4px; }}
.dwg .panel {{ fill: var(--cut-bg); stroke: var(--ink); stroke-width: 1.4px; }}
.dwg .panell {{ fill: var(--lid-bg); stroke: var(--lid); stroke-width: 1.2px; }}
.dwg .pcb {{ fill: var(--pcb); fill-opacity: .22; stroke: var(--pcb); stroke-width: 1.2px; }}
.dwg .hw {{ fill: var(--hw); stroke: var(--ink); stroke-width: .8px; }}
.dwg .hwo {{ fill: none; stroke: var(--hw); stroke-width: 1px; stroke-dasharray: 4 3; }}
.dwg .env {{ fill: var(--amber); fill-opacity: .08; stroke: var(--amber); stroke-width: 1.1px; stroke-dasharray: 6 3; }}
.dwg .ssd {{ fill: var(--ssd); fill-opacity: .12; stroke: var(--ssd); stroke-width: 1.1px; stroke-dasharray: 6 3; }}
.dwg .jack {{ fill: var(--hw); fill-opacity: .18; stroke: var(--hw); stroke-width: 1px; }}
.dwg .ribbon {{ fill: none; stroke: var(--red); stroke-width: 2.4px; stroke-dasharray: 5 3; }}
.dwg .sd {{ fill: var(--red); fill-opacity: .3; stroke: var(--red); stroke-width: 1px; }}
.dwg .sock {{ fill: var(--hw); fill-opacity: .3; stroke: var(--ink); stroke-width: 1px; }}
.dwg .tray {{ fill: var(--red); fill-opacity: .18; stroke: var(--red); stroke-width: 1px; }}
.dwg .foot {{ fill: var(--lid); fill-opacity: .25; stroke: var(--lid); stroke-width: 1.1px; }}
.dwg .footc {{ fill: none; stroke: var(--lid); stroke-width: 1px; stroke-dasharray: 4 3; }}
.dwg .port {{ fill: var(--red); }}
.dwg .hole {{ fill: none; stroke: var(--ink); stroke-width: 1px; }}
.dwg .railc {{ fill: var(--hw); fill-opacity: .35; stroke: var(--hw); stroke-width: 1px; }}
.dwg .cutd {{ fill: var(--red); fill-opacity: .14; stroke: var(--red); stroke-width: 1.3px; }}
.dwg .wall {{ stroke: var(--muted); stroke-width: 2px; }}
.dwg .plug {{ fill: var(--hw); fill-opacity: .22; stroke: var(--hw); stroke-width: 1px; stroke-dasharray: 4 3; }}
.dwg .ext {{ stroke: var(--dim); stroke-width: .7px; stroke-opacity: .8; }}
.dwg .dl {{ stroke: var(--dim); stroke-width: .9px; }}
.dwg .ar {{ fill: var(--dim); stroke: none; }}
.dwg .cl {{ stroke: var(--dim); stroke-width: 1px; stroke-dasharray: 12 3 2 3; }}
.dwg .ld {{ stroke: var(--muted); stroke-width: .8px; }}
.dwg .ldot {{ fill: var(--muted); }}
.dwg text {{ font-family: var(--f-mono); fill: var(--ink); }}
.dwg .dt {{ fill: var(--dim); font-weight: 500; }}
.dwg .zt {{ fill: var(--muted); font-style: italic; }}
.dwg .cutlbl {{ fill: var(--lid); font-weight: 600; }}
.dwg .lt {{ fill: var(--ink); }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font: 12px/1.3 var(--f-mono); color: var(--muted); }}
.legend i {{ display: inline-block; width: 18px; height: 10px; vertical-align: -1px; margin-right: 6px; border: 1.5px solid; }}
.lg-cut {{ background: var(--cut-bg); border-color: var(--ink) !important; }}
.lg-lid {{ background: var(--lid-bg); border-color: var(--lid) !important; }}
.lg-pcb {{ border-color: var(--pcb) !important; background: color-mix(in srgb, var(--pcb) 22%, transparent); }}
.lg-ssd {{ border-color: var(--ssd) !important; border-style: dashed !important; }}
.lg-env {{ border-color: var(--amber) !important; border-style: dashed !important; }}
.lg-rib {{ border-color: var(--red) !important; border-width: 0 0 2.5px !important; border-style: dashed !important; height: 6px !important; }}
.lg-dim {{ border-color: var(--dim) !important; border-width: 0 0 1.5px !important; height: 6px !important; }}

/* notes */
details {{ background: var(--sheet); border: 1px solid var(--rule); border-radius: 4px; }}
summary {{ cursor: pointer; padding: 12px 14px; font: 600 1.15rem/1.2 var(--f-display); text-transform: uppercase; letter-spacing: .04em; list-style-position: inside; }}
summary:focus-visible {{ outline: 2px solid var(--dim); outline-offset: -2px; }}
.d-body {{ padding: 0 14px 14px; display: grid; gap: 10px; max-width: 72ch; }}
.d-body ol, .d-body ul {{ margin: 0; padding-left: 1.3em; display: grid; gap: 6px; }}
.d-body table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
.d-body th, .d-body td {{ text-align: left; padding: 6px 8px 6px 0; border-bottom: 1px solid var(--rule); vertical-align: top; }}
.d-body th {{ font: 500 12px/1.3 var(--f-mono); color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
.d-body td:first-child {{ font-family: var(--f-mono); white-space: nowrap; }}
code {{ font: 13px var(--f-mono); background: var(--paper); padding: 1px 4px; border-radius: 2px; }}
.brief {{ font: 13px/1.55 var(--f-mono); background: var(--paper); border-left: 3px solid var(--muted); padding: 10px 12px; white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; }}
.foot {{ font-size: 13px; color: var(--muted); display: grid; gap: 6px; }}
.foot a {{ color: var(--dim); }}

.zoom {{ position: fixed; inset: 0; z-index: 50; background: var(--sheet); overflow: auto;
  padding: calc(56px + env(safe-area-inset-top, 0px)) max(12px, env(safe-area-inset-right, 0px)) calc(24px + env(safe-area-inset-bottom, 0px)) max(12px, env(safe-area-inset-left, 0px)); }}
.zoom svg.dwg {{ width: 230%; max-width: none; max-height: none; }}
@media (min-width: 900px) {{ .zoom svg.dwg {{ width: 140%; }} }}
.zoom-close {{ position: fixed; top: calc(10px + env(safe-area-inset-top, 0px)); right: max(12px, env(safe-area-inset-right, 0px)); z-index: 51;
  font: 600 14px/1 var(--f-body); padding: 10px 14px; border: 1px solid var(--rule); border-radius: 4px; background: var(--sheet); color: var(--ink); cursor: pointer; }}
.zoom-close:focus-visible {{ outline: 2px solid var(--dim); }}
</style>

<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <pattern id="hatch" patternUnits="userSpaceOnUse" width="2" height="2" patternTransform="rotate(45)">
      <rect width="2" height="2" style="fill: var(--cut-bg)"/>
      <line x1="0" y1="0" x2="0" y2="2" style="stroke: var(--hatch); stroke-width: .4"/>
    </pattern>
    <pattern id="hatchl" patternUnits="userSpaceOnUse" width="2" height="2" patternTransform="rotate(-45)">
      <rect width="2" height="2" style="fill: var(--lid-bg)"/>
      <line x1="0" y1="0" x2="0" y2="2" style="stroke: var(--lid); stroke-width: .3; stroke-opacity: .6"/>
    </pattern>
  </defs>
</svg>

<main class="wrap">
  <header class="intro">
    <p class="eyebrow">Enclosure study · v0.4 · body printed, lid, retainer and feet revised · 11 Nov 2026</p>
    <h1>Pi 5 PoE NVMe Case</h1>
    <p class="lede">A slide-in tube for a Raspberry Pi 5 with the <b>Waveshare PoE HAT (G)</b> on its header and a <b>Pimoroni NVMe Base Duo</b> underneath. No screws or standoffs in either board: <b>each board rests on its own ledge</b>, the PCIe ribbon is the only link between them, a <b>TPU card retainer</b> springs them against the closed USB end, and a <b>click-in PLA lid</b> closes the SD end against the closed USB end. The body prints standing on its USB end, so the ledges, vents and ports need no supports.</p>
    <div class="chips"><span class="chip">PoE HAT (G) · WS-27670</span><span class="chip">NVMe Base Duo · PIM704</span><span class="chip">Pi 5 + Active Cooler</span><span class="chip">PETG or PLA body · PLA lid · TPU feet</span><span class="chip">Prusa MK3S+</span></div>
  </header>

  <dl class="spec">
    <div><dt>Outside L × W × H</dt><dd>{f1(L)} × {f1(W)} × {f1(H)}</dd></div>
    <div><dt>Height on feet</dt><dd>{f1(H + feet_h)}</dd></div>
    <div><dt>Parts</dt><dd>body · retainer · lid · 4 feet or DIN bracket</dd></div>
    <div><dt>Print, all parts</dt><dd>{hm(total)}</dd></div>
  </dl>

  <section aria-labelledby="ask-h">
    <h2 id="ask-h">Print test, 11 Nov</h2>
    <div class="ask">
      <ul>
        <li><b>Body: printed well</b> (PLA, 10 Nov). The ledges hold the NVMe Base Duo; you shook the case and the base stayed put. No change to the body, so no reprint.</li>
        <li><b>TPU lid: the snap bumps came out as faint nubs.</b> The slicer did include them, but they were only 0.3–0.8 mm proud over five 0.3 mm layers, which TPU smoothed away. Even printed perfectly, only 0.55 mm would have reached into the windows.</li>
        <li><b>v0.3 lid: PLA, with flexing latch arms</b> (your suggestion). One arm per long side, cut free by slots and fixed at the top. Its 1 mm hook clicks into the upper side window that's already in your body. The toolpath now shows the full 1.0 mm hook over 12 layers.</li>
        <li><b>v0.4: a TPU card retainer holds the boards; the lid just closes</b> (your suggestion). The retainer locks in with bumps in the first vent slots, and its fingers spring against the board corners. The lid loses its prongs.</li>
        <li><b>v0.4 feet suit your M3 × 8 button heads.</b> The v0.2 feet would have let the screw bottom out 0.8 mm before it clamped. Now they're 6 mm tall with a 3 mm counterbore.</li>
        <li><b>To print: the lid, the retainer and the feet.</b> The body stays as printed.</li>
      </ul>
    </div>
  </section>

  <section aria-labelledby="set-h">
    <h2 id="set-h">Settled</h2>
    <div class="ask settled">
      <ul>
        <li><b>SSDs: Samsung 980 series.</b> Single-sided, 2.38 mm, no heatsink. On Pimoroni's 5 mm SSD standoffs they reach about 7.4 mm below the Duo, inside the {f1(I['drive_drop'])} mm allowed.</li>
        <li><b>HAT height: unknown, so kept at {f1(I['hat'][2])} mm.</b> That's the tall case. If your HAT sits lower, you just get more air above it.</li>
        <li><b>HAT stays on its headers.</b> No hold-down ribs.</li>
        <li><b>SD tray dropped.</b> Fit the microSD card before the PCIe ribbon.</li>
      </ul>
      <p>The print-ready STLs are in the chat: body (PETG or PLA), card retainer (TPU), lid (PLA), four feet (TPU), DIN bracket (PETG). Each is already oriented for the bed.</p>
    </div>
  </section>

  <section class="times" aria-labelledby="pt-h">
    <h2 id="pt-h">Print time</h2>
    <div class="tbl"><table>
      <caption>PrusaSlicer 2.7 · 0.30 mm DRAFT (lid 0.20 mm SPEED) · 0.4 nozzle · MK3S+</caption>
      <thead><tr><th></th><th scope="col">Material</th><th scope="col">Time</th></tr></thead>
      <tbody>
        <tr><th scope="row">Body</th><td class="mat">PETG, USB end on the bed</td><td>{hm(body_p['min'])}<span>{body_p['g']:.0f} g</span></td></tr>
        <tr><th scope="row">Lid</th><td class="mat">PLA, 0.20 mm, outer face on the bed (PETG: {hm(lid_g['min'])})</td><td>{hm(lid_t['min'])}<span>{lid_t['g']:.0f} g</span></td></tr>
        <tr><th scope="row">Card retainer</th><td class="mat">TPU, eSun 95A FAST, back face on the bed</td><td>{hm(ret_t['min'])}<span>{ret_t['g']:.0f} g</span></td></tr>
        <tr><th scope="row">Feet × 4</th><td class="mat">TPU, eSun 95A FAST</td><td>{hm(feet['min'])}<span>{feet['g']:.0f} g</span></td></tr>
        <tr><th scope="row">DIN bracket</th><td class="mat">PETG, rail side down. Draft: {hm(T['din']['PETG']['min'])}. Recommended 4 walls, 40% gyroid</td><td>{hm(din_s['min'])}<span>{din_s['g']:.0f} g</span></td></tr>
        <tr class="tot"><th scope="row">Case + feet</th><td></td><td>{hm(total)}</td></tr>
      </tbody>
    </table></div>
    <p class="note">Walls, roof, floor and end are 2.4 mm. The same body with your usual 3 mm walls slices at {hm(body3['min'])}, so 2.4 saves {hm(saved)}. The stiffness comes from the two lips and the thick SSD-bay walls, which run the full length on both sides like rails, and from the bars between the vent rows.</p>
  </section>

  <section aria-labelledby="dw-h">
    <h2 id="dw-h">Drawings</h2>
    <div class="legend" aria-label="Drawing legend"><span><i class="lg-cut"></i>body (cut)</span><span><i class="lg-lid"></i>lid / TPU parts</span><span><i class="lg-pcb"></i>PCB</span><span><i class="lg-ssd"></i>SSD zone</span><span><i class="lg-env"></i>HAT parts</span><span><i class="lg-rib"></i>PCIe ribbon</span><span><i class="lg-dim"></i>dimension (mm)</span></div>
    <div class="dwgs">{''.join(cards)}</div>
  </section>

  <section aria-labelledby="notes-h">
    <h2 id="notes-h">Design notes</h2>

    <details open>
      <summary>Where the space goes</summary>
      <div class="d-body"><div class="tbl"><table>
        <thead><tr><th>Value</th><th>Reason</th></tr></thead>
        <tbody>
          <tr><td>{f1(I['air_below'] + I['drive_drop'])} bay</td><td>{f1(I['drive_drop'])} mm for the SSDs on the Duo's underside (5 mm SSD standoffs plus a double-sided drive, with margin) and {f1(I['air_below'])} mm of air above the floor vents.</td></tr>
          <tr><td>{f1(I['duo_gap'])} gap</td><td>Duo top to Pi underside. The case sets it now that there are no standoffs; 12 mm is what Pimoroni's ribbon is made for. The upper lip ({f1(I['pi_lip_t'])} mm) sits in it with 7 mm clear above the Duo.</td></tr>
          <tr><td>{f1(I['pi_ledge'])} / {f1(I['duo_ledge'])} ledges</td><td>How far each ledge reaches under its board. The Pi's is short to stay clear of the solder joints on its underside.</td></tr>
          <tr><td>{f1(I['hat'][2])} header</td><td>Pi top to HAT underside, the usual height that clears the Active Cooler.</td></tr>
          <tr><td>{f1(I['hat'][3])} + {f1(I['air_top'])}</td><td>Tallest part on the HAT, then air under the roof vents.</td></tr>
          <tr><td>{f1(I['side_gap'])} sides</td><td>Air between the boards and the side walls, above the upper lip and in the recess between the lips, as you asked.</td></tr>
          <tr><td>{f1(I['sd_space'])} SD end</td><td>Room for the ribbon loop (about 7 mm) between the boards and the lid.</td></tr>
          <tr><td>42 × 11</td><td>USB-C + HDMI window. A dock cable's USB-C overmold has about 8 mm of window either side and has to reach ~5 mm in to seat the plug.</td></tr>
        </tbody>
      </table></div></div>
    </details>

    <details>
      <summary>Assembly</summary>
      <div class="d-body"><ol>
        <li>Fit the SSDs to the Duo and the ribbon to both boards as Pimoroni describe, but leave the standoffs out. Plug the HAT onto the Pi's GPIO and PoE headers. Fit your microSD card now if you use one.</li>
        <li>Press four M3 × 5.7 heat-set inserts into the floor.</li>
        <li>Fold the Duo under the Pi and slide both in from the open end, USB first: the Duo onto the lower ledges, the Pi onto the upper ledges. Push them together by their SD edges until they stop on the end wall.</li>
        <li>Push the TPU card retainer in behind the boards, bumps up and down, until its four bumps drop into the first roof and floor vent slots. Its fingers press on the board corners.</li>
        <li>Push the lid in until both latches click into the upper side windows.</li>
        <li>Screw the TPU feet on with M3 × 8 button or socket heads.</li>
        <li>To open, pull the lid out by the thumb notch at the top. If it's tight, press both hooks in through the side windows with a small screwdriver as you pull. The boards stay put. To take them out, press the retainer's bumps in through the vents and pull the ring.</li>
      </ol></div>
    </details>

    <details>
      <summary>Printing</summary>
      <div class="d-body"><ul>
        <li>Body: USB end flat on the bed, PETG. Every wall, the lip and the drive-bay walls are vertical in that orientation. Vent slots and windows only bridge 3–10 mm. No supports, no brim.</li>
        <li>Lid: outer face on the bed, PLA (PETG also works and is more forgiving), 0.20 mm layers, no supports, no brim. The arm slots go right through the plate; check they're clear on the first layer. The hooks' undersides are 45° overhangs.</li>
        <li>Card retainer: TPU, back face on the bed. The bumps grow straight off the bed; the fingers lean about 40°.</li>
        <li>Feet: TPU, counterbore side up (no overhang). Turn them over to fit.</li>
        <li>The click is set by <code>latch_t</code> ({f1(LT['t'])}, arm thickness) and <code>latch_hook</code> ({f1(LT['hook'])}). Too stiff: thin the arm to 1.2. Too loose: raise the hook to 1.2. Either way, reprint only the lid ({hm(lid_t['min'])}).</li>
      </ul></div>
    </details>

    <details>
      <summary>Hardware</summary>
      <div class="d-body"><ul>
        <li>4 × M3 × 5.7 heat-set inserts, 4 × M3 × 8 button or socket head screws (feet)</li>
        <li>DIN mount instead of feet: 4 × M3 × 20 button or socket head screws, TS35 rail (35 × 7.5 or 35 × 15)</li>
        <li>Nothing for the boards. The Duo kit's standoffs and screws aren't used.</li>
      </ul></div>
    </details>

    <details>
      <summary>Your brief (verbatim)</summary>
      <div class="d-body"><pre class="brief">{BRIEF}</pre><p class="note">With a first sketch of the side profile: thin upper wall, a lip the board sits on, a thicker wall below.</p>
      <p class="note">Follow-ups:</p><pre class="brief">{chr(10).join(FOLLOWUPS)}</pre><p class="note">The second sketch: an upper lip with the Pi resting on top, a recess in the wall where the NVMe board's edge runs, a lower lip the NVMe board rests on, then the wall steps back out below.</p></div>
    </details>
  </section>

  <footer class="foot">
    <p>Source: <code>pi5_case.scad</code> (OpenSCAD, every value above is a parameter) and a handoff README, saved in the Designing stuff project under <code>pi5-poe-nvme-case/</code>. Drawings are cut from the model's STLs.</p>
    <p>Part data: <a href="https://www.waveshare.com/poe-hat-g.htm?sku=27670" target="_blank" rel="noopener">PoE HAT (G) 64.98 × 56.5</a> · <a href="https://core-electronics.com.au/pimoroni-nvme-base-duo-for-raspberry-pi-5-pim704.html" target="_blank" rel="noopener">NVMe Base Duo kit (12 mm standoffs)</a> · <a href="https://www.digikey.com/en/maker/projects/getting-started-with-nvme-base-duo-for-raspberry-pi-5/abd48355265a4fca812d348726afbd05" target="_blank" rel="noopener">Duo assembly (SSDs face away from the Pi)</a> · <a href="https://raspberry.tips/en/?p=10265" target="_blank" rel="noopener">Pi 5 power button by the USB-C</a> · <a href="https://pip.raspberrypi.com/categories/892-raspberry-pi-5" target="_blank" rel="noopener">Pi 5 mechanical drawing</a></p>
  </footer>
</main>

<script>
(function () {{
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
out = ROOT / "pi5_case.html"
out.write_text(html)
print(out, len(html) // 1024, "KB")
