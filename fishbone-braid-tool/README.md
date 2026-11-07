# Fishbone braid tool — v0.1

A copy of the cheap "fish bone / French braid tool roller" (zigzag strip with a hook), made parametric and set up for TPU on the MK3S+. Status: **designed and test-sliced, not yet printed.** 7 Nov 2026.

## Original brief (verbatim, 7 Nov 2026)

> Can you find or design me one of these tools? To be printed out of TPU

Attached: screenshot of eBay AU listing *"Fish Bone Hair Braiding French Braid Tool Roller Magic Twist Styling Bun Maker"* (seller colleencollection, AU $3.99) — a black wavy plastic strip, ~9 lobes per side, small hook at one end.

Printer: Prusa i3 MK3S+. Project preference: functional over pretty, faster over perfect; TPU/PETG preferred.

## Existing models (the "find" half)

Ready-made versions exist on MakerWorld, e.g. *Braiding Tool* by GENERA 3D MODEL ART (zigzag type, Feb 2026, standard digital file licence) and *braiding tool* by ABO Design (Apr 2026). Both are fixed STLs aimed at PLA, with no TPU guidance, so this design was done from scratch to be parametric and TPU-friendly.

- https://3dgo.app/models/makerworld/2450361 (GENERA, zigzag)
- https://makerworld.com/models/2622007 (ABO Design)
- https://makerworld.com/models/2469321 (AndresMakes — different idea: a slotted strand holder, not the zigzag)

## Design

- **Shape:** 18 straight runs across the width joined by semicircular U-turns that alternate sides, giving 17 hair slots (9 open on one side, 8 on the other). The top end turns up into a stem and a downward-opening hook. Matches the retail size: ~190 × 25 mm.
- **Print orientation:** flat, as drawn. No supports, no bridges, no overhangs.
- **Hair snag control:** top edges have an R1.5 round-over (prints as fine steps, never overhangs); bottom edges a 0.5 mm 45° chamfer so TPU elephant-foot doesn't leave a sharp lip. The outline is one continuous closed loop, so each layer is printed as unbroken perimeters, which means almost no travel moves and no strings across the slots.
- **TPU vs the retail part:** the retail tool is hard plastic. TPU 95A is much softer, so this one will be floppier and its surface grippier. Thickness `t` (stiffness ∝ t³) is the main lever. PETG is the fallback if TPU drags on hair or won't hold its shape.

Coordinates: X centred across the width, Y = 0 at the tail end, Z up.

## Key numbers (all parameters in `braid_tool.scad`)

| Parameter | Default | Notes |
|---|---|---|
| `L` | 190 | overall length incl. hook. Retail listings say 19 cm |
| `W` | 25 | overall width. Retail ~2.5 cm |
| `w` | 4.5 | strand width in plane. Stretchiness of the zigzag ∝ 1/w³ |
| `t` | 4.0 | strand thickness = print height. Floppiness ∝ 1/t³. Try 5 if the TPU one is too limp; 3 for PETG |
| `p` | 10 | run pitch. **Slot gap = p − w = 5.5** |
| `hook_r` / `stem_min` / `hook_tail` | 4.5 / 4 / 3 | hook gap = 2·hook_r − w = 4.5 |
| `top_r` / `bot_c` | 1.5 / 0.5 | edge round-over / chamfer |
| `coupon_L` | 50 | short test piece (4 runs, 3 slots + hook) |

Number of runs is derived: as many as fit in `L` at pitch `p`; the stem absorbs the remainder. `part="info"` echoes the derived numbers as JSON (`info.json`).

## Print settings and times

PrusaSlicer 2.7.2 CLI, stock *Original Prusa i3 MK3S & MK3S+* printer, filament **eSun TPU 95A FAST @MK3S** (from `printer-profiles/esun-tpu95a-mk3s`), *Avoid crossing perimeters* on.

**Recommended:** *0.20mm SPEED @MK3* + **Perimeters = 5** (fills the 4.5 mm strand solid with continuous loops). That's the only change to the stock print profile.

| Part | Profile | Infill variant | TPU (eSun FAST) | PETG (Generic) |
|---|---|---|---|---|
| Tool | 0.20 SPEED | **5 perimeters (rec.)** | **44 min, 11.0 g** | 36 min, 10.5 g |
| Tool | 0.20 SPEED | stock (2 perims + 15 %) | 44 min, 8.2 g | 42 min, 7.8 g |
| Tool | 0.30 DRAFT | 5 perimeters | 42 min, 11.2 g | 27 min, 10.6 g |
| Tool | 0.30 DRAFT | stock | 40 min, 8.9 g | 29 min, 8.5 g |
| Coupon | 0.20 SPEED | 5 perimeters | 12 min, 2.8 g | 10 min, 2.7 g |

Why these choices:
- TPU is capped by max volumetric speed, so 0.30 DRAFT barely saves time (42 vs 44 min) but makes the top round-over coarser. That's why 0.20 is recommended.
- 5 perimeters vs 100 % rectilinear infill (also tested): 44 vs 60 min, **29 vs 583 retractions**, same weight. Fewer retractions means less stringing and less risk of a TPU jam.
- Solid rather than the stock 15 %: stiffer, and it won't tear at the U-turns.

## Use

From the GENERA listing's instructions: hold the tool vertically against the head at the crown. Feed a strand from the right into the first slot open on the left, then a strand from the left into the first slot open on the right, and keep alternating down the tool. Then secure the braid.

## Print order

1. **Coupon first** (12 min). Check: does it hold its shape? Does hair slide in and out of a 5.5 mm slot without dragging? Is there a lip on the bottom edge?
2. Too limp → `t = 5` (≈ 2× stiffer). Too grippy on hair → PETG. Slots too loose or tight → change `p`.
3. Print the full tool.

## Open questions / to verify

- TPU stiffness and surface grip against hair: untested. The coupon answers both.
- Slot gap 5.5 mm and hook size were estimated from the listing photo, not measured from a real tool.
- Which end goes at the crown: the hook end is assumed to be the top/handle end.

## Files

| File | Purpose |
|---|---|
| `braid_tool.scad` | parametric model. `part = tool | coupon | info` |
| `render_all.sh` | renders both STLs, `info.json`, and `img/braid_tool_3d.png` |
| `slice_all.py` | flattens the PrusaSlicer vendor presets + the project's eSun TPU bundle, slices every variant → `print_times.json`, keeps the recommended G-code in `gcode/` |
| `drawings.py` | top view + strand cross-section from the STL → `img/braid_tool_drawing.png` |
| `stl/braid_tool.stl`, `stl/braid_coupon.stl` | print files |
| `gcode/braid_tool_TPU_0.20SPEED_loops.gcode` | ready to print (eSun TPU FAST, 225 °C, bed 50) |

Regenerate: `./render_all.sh && python3 slice_all.py && python3 drawings.py` (needs OpenSCAD 2021+, xvfb-run for the PNG, PrusaSlicer 2.7 CLI, Python trimesh/shapely/matplotlib). `slice_all.py` expects `../printer-profiles/esun-tpu95a-mk3s/eSun_TPU95A_MK3S.ini`. The full-tool render takes about 75 s in OpenSCAD 2021 (CGAL).

## Ideas for v0.2

- Kids' / short-hair size (L 120–140).
- Tapered tail end, to slide into hair more easily.
- Optional stiffening rib along the stem/hook if the TPU hook is too floppy to grab.
