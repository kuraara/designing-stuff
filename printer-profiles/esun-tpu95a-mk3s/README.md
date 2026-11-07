# eSun eTPU-95A — PrusaSlicer filament profiles for MK3S / MK3S+

Status: **built and test-sliced (PrusaSlicer 2.7.2 CLI), not yet printed.** 31 Oct 2026.

## Requests (verbatim, 31 Oct 2026)

> Can you search for a print profile for Prusa Slicer, using a Mk3s+ for printing eSun TPU. The Prusa flex profile prints too hot and too slowly ie it’s useless

> There was a discussion on the Prusa forums where someone shared their settings, which I have applied previously and it worked well

> And aim for fast printing

## What's in `eSun_TPU95A_MK3S.ini`

A PrusaSlicer config bundle with two filament presets. Import with **File > Import > Import Config Bundle**; they appear under Filament > User presets for the MK3S+ with a 0.4 nozzle. Each is stock *Generic FLEX* fully resolved, plus the overrides below (`inherits = Generic FLEX`, so PrusaSlicer shows the diffs).

| Setting | Generic FLEX (stock) | **eSun TPU 95A @MK3S** (forum) | **eSun TPU 95A FAST @MK3S** |
|---|---|---|---|
| Nozzle, first layer / rest | 240 / 240 | 220 / 212 | 225 / 225 |
| Bed | 50 | 50 | 50 |
| Max volumetric speed | 1.2 mm³/s | 2.4 | **3.5** |
| Extrusion multiplier | 1.15 | 1.07 | 1.10 |
| Retraction | none | 1 mm @ 25, deretract 15, only travels > 3 mm, no Z-hop | same |
| Fan | off except bridges (auto-cooling off) | off layers 1–3, 70 % min → 90 % (full by layer 6) when layer < 60 s, bridges 80 % | same |
| Slow down below layer time | — | 15 s | 10 s |
| Density | 1.22 | 1.21 (eSun spec) | 1.21 |

MVS is the only speed lever needed: PrusaSlicer caps every move (perimeter, infill, first layer) to it, so the print profile stays stock.

### Where the numbers come from

Prusa forum thread **"e-TPU esun 95A settings"** (MK3/MK3S printing help):
- **Artur5 (Feb 2022)**: 220 °C first layer, 210 after; bed 50; retraction 0.5 mm @ 25, deretract 15; fan off 3 layers, 70 % at layer 6, 90 % when layer < 60 s; MVS 2.4; EM 1.04–1.10. Note he ran a Mosquito hotend.
- **Snowballs Chance (Apr 2023)**: 220/200 °C, bed 50, EM 1.1, density 1.22, same fan scheme, MVS 1.2, retraction 2 mm, all speeds 20 mm/s, filament dried 12 h at 50 °C.
- Several later posters: Prusa's built-in **SainSmart TPU** profile (230 °C, MVS 2.5) works for eTPU-95A.

eSun's spec: 220–250 °C nozzle, 45–60 °C bed, 100 % fan, 20–50 mm/s, dry at 55 °C for 4 h+, direct drive.

Retraction is 1 mm (between Artur5's 0.5 on a Mosquito and Snowballs Chance's 2) to suit the stock E3D V6; Prusa's own SainSmart profile also uses 1 mm.

## Test-slice times (PrusaSlicer 2.7.2, stock MK3S+ printer)

| Part | Print profile | Generic FLEX | SainSmart TPU | eSun forum | **eSun FAST** |
|---|---|---|---|---|---|
| Block 40×40×20 | 0.30 DRAFT | 2h 25m | 1h 12m | 1h 15m | **54m** |
| Ring Ø60/Ø50 × 15 | 0.30 DRAFT | 1h 45m | 53m | 55m | **40m** |
| Block 40×40×20 | 0.20 QUALITY | 2h 14m | 1h 11m | 1h 13m | **59m** |
| Ring Ø60/Ø50 × 15 | 0.20 QUALITY | 1h 41m | 58m | 59m | **50m** |

G-code check (FAST, draft block): M104 S225; fan off then ramps to 70–90 %; 1 mm retractions at F1500; steady extrusion ~3.8 mm³/s (3.5 × the 1.10 multiplier).

## Tuning FAST

1. Dry the spool (50–55 °C, 4 h+). Wet TPU strings and bubbles whatever the profile.
2. Loosen the extruder idler screw (Prusa's flex guidance) so the gears don't chew the filament.
3. Print something small. Clicking extruder or starved/gappy walls → +5 °C, or MVS 3.0. Clean → try MVS 4.0 at 230 °C.
4. Stringing → enable *Print Settings > Layers and perimeters > Avoid crossing perimeters*, or drop 5 °C.
5. Bed: satin or textured sheet as-is. Smooth PEI: glue stick as a release layer (TPU can bond too well).
6. Fall back to the forum preset if FAST won't behave.

## Files

| File | Purpose |
|---|---|
| `eSun_TPU95A_MK3S.ini` | the config bundle to import |
| `build_bundle.py` | regenerates the bundle from PrusaSlicer's `PrusaResearch.ini` (`python3 build_bundle.py [path]`) |

## Sources

- Prusa forum, *e-TPU esun 95A settings*: https://forum.prusa3d.com/forum/original-prusa-i3-mk3s-mk3-how-do-i-print-this-printing-help/e-tpu-esun-95a-settings
- eSun eTPU-95A product page (AU): https://au.esun3d.com/etpu-95a-product
- filament2print eTPU-95A spec: https://filament2print.com/en/flexible-tpe-tpu/2909-esun-etpu-95a.html
- Prusa forum, *TPU printing and the MK3S extruder* (MVS as the speed cap): https://forum.prusa3d.com/forum/original-prusa-i3-mk3s-mk3-general-discussion-announcements-and-releases/tpu-printing-and-the-mk3s-extruder
