# Fishbone braid tool — v0.2

A copy of the cheap "fish bone / French braid tool roller" (zigzag strip with a hook), made parametric and set up for TPU on the MK3S+. Status: **v0.2 coupon printed and passed (7 Nov 2026). Full tool ready to print with the same conservative settings.** 8 Nov 2026.

**3D:** [braid tool in the viewer](https://kuraara.github.io/designing-stuff/?m=fishbone-braid-tool/stl/braid_tool.stl) · [coupon](https://kuraara.github.io/designing-stuff/?m=fishbone-braid-tool/stl/braid_coupon.stl)

## Requests (verbatim)

7 Nov 2026, 16:14:

> Can you find or design me one of these tools? To be printed out of TPU

Attached: screenshot of eBay AU listing *"Fish Bone Hair Braiding French Braid Tool Roller Magic Twist Styling Bun Maker"* (seller colleencollection, AU $3.99) — a black wavy plastic strip, ~9 lobes per side, small hook at one end.

7 Nov 2026, 16:48:

> Make the short test piece, set t=6, perimeters=5, use a more conservative print speed in the slicing

7 Nov 2026, 16:49:

> Then upload to GitHub and provide instructions on what to do next (print coupon)

8 Nov 2026, 00:20:

> The print worked well, let's go full sized and keep the conservative speeds

Printer: Prusa i3 MK3S+. Project preference: functional over pretty, faster over perfect; TPU/PETG preferred.

## Next step: print the full tool

**Print** `gcode/braid_tool_TPUsafe_0.20SPEED_loops.gcode`: **1 h 30 min, 16.4 g**. It uses exactly the coupon's settings: eSun TPU 95A @MK3S (conservative), 0.20mm SPEED, 5 perimeters, avoid crossing perimeters, t = 6. No design changes from the coupon.

- **Bed:** the part runs front to back, centred, Y ≈ 8–202 mm including the skirt. Wipe the sheet edge to edge, because the hook and tail sit near the front and back.
- **Prep:** same as the coupon: dry filament, loosened idler, glue stick on smooth PEI.
- **First layer:** the long run means a TPU underflow or clog shows up partway through. Check the first layer across the whole length, and look in once or twice.
- **After:** repeat the coupon checks on the full part (table below), particularly stretch end to end and hair sliding through all 17 slots.

## Coupon result (7 Nov 2026)

Printed with `gcode/braid_coupon_TPUsafe_0.20SPEED_loops.gcode`. Reported as working well (see the 8 Nov request above), so nothing changed for the full tool. The individual checks weren't reported one by one.

## Coupon print and checks (reference)

The coupon is a 50 mm slice of the tool: same strand section (4.5 × 6), 4 runs, 3 hair slots, and the hook. **23 min, 4.2 g.**

1. **Filament.** Dry the TPU if it's been out (50–55 °C, 4 h+). Loosen the extruder idler for flex.
2. **Sheet.** Textured or satin sheet as-is. On smooth PEI, use glue stick as a release layer.
3. **Print** `gcode/braid_coupon_TPUsafe_0.20SPEED_loops.gcode`. It uses the conservative eSun preset: 220 °C first layer, 212 °C after, bed 50, 20 mm/s first layer, ~29 mm/s max elsewhere.
   - To slice it yourself in PrusaSlicer: printer *Original Prusa i3 MK3S & MK3S+*, print *0.20mm SPEED @MK3*, filament **eSun TPU 95A @MK3S** (not FAST; from `printer-profiles/esun-tpu95a-mk3s`). Then set **Perimeters = 5** and tick **Avoid crossing perimeters**.
4. **Watch the first layer.** If the extruder clicks or walls look gappy, stop and raise the temperature 5 °C.
5. **Check it once it's off the bed:**

| Check | Pass | If it fails → change |
|---|---|---|
| Stiffness: hold the hook end level | droops a little but springs back | limp → PETG, or `w = 5.5`; too stiff to work hair through → `t = 5` |
| Stretch: pull the ends apart gently | barely opens | stretches a lot → `w = 5.5` (stretch stiffness ∝ w³) |
| Slots: push a pencil-thick lock of hair into each slot and pull it out | goes in easily, slides out without dragging | drags → PETG (TPU is grippy); too tight/loose → `p` (slot = p − w) |
| Edges: run a fingernail along the bottom edge | no lip or string | lip → raise *Elephant foot compensation* to 0.3; strings in slots → dry the filament, or drop 5 °C |
| Hook: can you hook a finger or hair tie? | yes | bigger/smaller → `hook_r` |

6. **Report back** what passed and failed. If everything passes, print the full tool as-is.

## Existing models (the "find" half)

Ready-made versions exist on MakerWorld, e.g. *Braiding Tool* by GENERA 3D MODEL ART (zigzag type, Feb 2026, standard digital file licence) and *braiding tool* by ABO Design (Apr 2026). Both are fixed STLs aimed at PLA, with no TPU guidance, so this design was done from scratch to be parametric and TPU-friendly.

- https://3dgo.app/models/makerworld/2450361 (GENERA, zigzag)
- https://makerworld.com/models/2622007 (ABO Design)
- https://makerworld.com/models/2469321 (AndresMakes — different idea: a slotted strand holder, not the zigzag)

## Design

- **Shape:** 18 straight runs across the width joined by semicircular U-turns that alternate sides, giving 17 hair slots (9 open on one side, 8 on the other). The top end turns up into a stem and a downward-opening hook. Matches the retail size: ~190 × 25 mm.
- **Print orientation:** flat, as drawn. No supports, no bridges, no overhangs.
- **Hair snag control:** top edges have an R1.5 round-over (prints as fine steps, never overhangs); bottom edges a 0.5 mm 45° chamfer so TPU elephant-foot doesn't leave a sharp lip. The outline is one continuous closed loop, so each layer is printed as unbroken perimeters, which means almost no travel moves and no strings across the slots.
- **TPU vs the retail part:** the retail tool is hard plastic. TPU 95A is much softer and grippier. v0.2 raises `t` from 4 to 6, which makes it about 3.4× stiffer against bending toward or away from the head (∝ t³) and about 1.5× stiffer against stretching (∝ t). PETG is the fallback if TPU drags on hair or won't hold its shape.

Coordinates: X centred across the width, Y = 0 at the tail end, Z up.

## Key numbers (all parameters in `braid_tool.scad`)

| Parameter | Default | Notes |
|---|---|---|
| `L` | 190 | overall length incl. hook. Retail listings say 19 cm |
| `W` | 25 | overall width. Retail ~2.5 cm |
| `w` | 4.5 | strand width in plane. Stretchiness of the zigzag ∝ 1/w³ |
| `t` | **6.0** (v0.1: 4.0) | strand thickness = print height. Floppiness ∝ 1/t³. For PETG try 3 |
| `p` | 10 | run pitch. **Slot gap = p − w = 5.5** |
| `hook_r` / `stem_min` / `hook_tail` | 4.5 / 4 / 3 | hook gap = 2·hook_r − w = 4.5 |
| `top_r` / `bot_c` | 1.5 / 0.5 | edge round-over / chamfer |
| `coupon_L` | 50 | short test piece (4 runs, 3 slots + hook) |

Number of runs is derived: as many as fit in `L` at pitch `p`; the stem absorbs the remainder. `part="info"` echoes the derived numbers as JSON (`info.json`).

## Print settings and times (v0.2, t = 6)

PrusaSlicer 2.7.2 CLI, stock *Original Prusa i3 MK3S & MK3S+* printer, *0.20mm SPEED @MK3*, **Perimeters = 5**, *Avoid crossing perimeters* on. The 5 perimeters fill the 4.5 mm strand solid as continuous loops. That's the only change to the stock print profile apart from avoid-crossing.

Filament presets (from `printer-profiles/esun-tpu95a-mk3s`):
- **TPU safe** = *eSun TPU 95A @MK3S* (forum preset): max 2.4 mm³/s, 220/212 °C → ~29 mm/s walls. **Used for the coupon (passed) and the full tool.**
- **TPU FAST** = *eSun TPU 95A FAST @MK3S*: max 3.5 mm³/s, 225 °C → ~43 mm/s walls. Optional later, to save ~25 min on the full tool.

| Part | TPU safe | TPU FAST | PETG (Generic) |
|---|---|---|---|
| **Coupon** | **23 min, 4.2 g** | 17 min, 4.3 g | 14 min, 4.1 g |
| **Tool** | **90 min, 16.4 g** | 66 min, 16.8 g | 52 min, 16.1 g |

G-code kept in `gcode/`: coupon and tool, each in TPU safe and TPU FAST. The other combinations, including 0.30 DRAFT and stock 2 perimeters + 15 %, are in `print_times.json`. TPU is capped by max volumetric speed, so 0.30 DRAFT only saves 1–4 min and makes the top round-over coarser.

v0.1 finding (t = 4): 5 perimeters vs 100 % rectilinear infill gave 44 vs 60 min and **29 vs 583 retractions** at the same weight. Fewer retractions means less stringing and less risk of a TPU jam.

## Use

From the GENERA listing's instructions: hold the tool vertically against the head at the crown. Feed a strand from the right into the first slot open on the left, then a strand from the left into the first slot open on the right, and keep alternating down the tool. Then secure the braid.

## Open questions / to verify

- TPU stiffness and surface grip against hair at t = 6: the coupon passed. Confirm on the full-length tool, especially stretch end to end.
- Slot gap 5.5 mm and hook size were estimated from the listing photo, not measured from a real tool.
- Which end goes at the crown: the hook end is assumed to be the top/handle end.

## Files

| File | Purpose |
|---|---|
| `braid_tool.scad` | parametric model. `part = tool | coupon | info` |
| `render_all.sh` | renders both STLs (converted to binary), `info.json`, and `img/braid_tool_3d.png` |
| `slice_all.py` | flattens the PrusaSlicer vendor presets + the eSun TPU bundle, slices every variant → `print_times.json`, keeps the TPU safe/FAST G-code in `gcode/`. `python3 slice_all.py braid_coupon` slices just one part |
| `drawings.py` | top view + strand cross-section from the STL → `img/braid_tool_drawing.png` |
| `stl/braid_tool.stl`, `stl/braid_coupon.stl` | print files (t = 6) |
| `gcode/braid_coupon_TPUsafe_0.20SPEED_loops.gcode` | coupon, conservative (printed, passed) |
| `gcode/braid_tool_TPUsafe_0.20SPEED_loops.gcode` | **full tool, conservative: print this next** |
| `gcode/*_TPU_0.20SPEED_loops.gcode` | same with the FAST preset |

Regenerate: `./render_all.sh && python3 slice_all.py && python3 drawings.py` (needs OpenSCAD 2021+, xvfb-run for the PNG, PrusaSlicer 2.7 CLI, Python trimesh/shapely/matplotlib). `slice_all.py` expects `../printer-profiles/esun-tpu95a-mk3s/eSun_TPU95A_MK3S.ini`. The full-tool render takes about 80 s in OpenSCAD 2021 (CGAL).

## Changelog

- **v0.2 printed** (8 Nov 2026): coupon passed. Full tool released to print with the conservative preset. Docs only, no geometry or slicing changes.
- **v0.2** (7 Nov 2026): `t` 4 → 6. Coupon first. Conservative eSun preset added to slicing (and its G-code kept). `slice_all.py` takes part names and merges results.
- **v0.1** (7 Nov 2026): first design, t = 4, sliced with eSun FAST only.

## Ideas for v0.3

- Kids' / short-hair size (L 120–140).
- Tapered tail end, to slide into hair more easily.
- Optional stiffening rib along the stem/hook if the TPU hook is too floppy to grab.
