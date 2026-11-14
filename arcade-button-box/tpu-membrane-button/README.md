# TPU membrane button — v0.3 (compact)

A small, low-profile button printed as **one TPU part** around an arcade microswitch: a Ø19 face on a Ø23 head, with a narrow stem that only hugs the plunger end of the switch. The face is a 2–3 layer membrane printed on the bed, and a stiff centre presses the microswitch. The centre's face lands on the switch's own top face, so the plunger always stops 0.2 mm above flush whatever its exact height: no shims or tape. A 45° cone behind it is the backup stop. The switch slides in from the side onto a solid floor and clicks onto two bumps in its mounting hole; the rest of the switch sticks out of the side of the stem. No supports. About 36 minutes and 4.5 g.

**3D:** [cut through the middle with the switch in place](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/tpu-membrane-button/stl/tpu_button.stl&m=arcade-button-box/tpu-membrane-button/stl/ref_microswitch.stl&cut=y&at=500&flip=1) · [the part as printed, overhangs in red](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/tpu-membrane-button/stl/tpu_button.stl&over=1) · [2-layer version](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/tpu-membrane-button/stl/tpu_button_m04.stl)

Part of the [arcade-button-box](..) study: aimed at cutting box depth from ~94 mm (long-barrel buttons) to ~27 mm, and at quick prints.

Status: **v0.3 (compact), sliced and ready to print, not yet printed.** 14 Nov 2026. v0.2 (same mechanism, Ø36 × 34 puck, 1 h 08–1 h 44) and v0.1 (housing stop, snap-in from below) are in git history.

![Drawing](img/tpu_button_drawing.png)

## Requests (verbatim)

14 Nov 2026, 16:43:

> Can you do me a mock design of a single TPU membrane button?
>
> Ideally it should be entirely TPU and can hold the  micro switch by slotting it in from the bottom or side
>
> I would like to print it as soon as it it’s ready so this chat needs to go GitHub as a research piece (a folder, not a branch)

14 Nov 2026, 16:44:

> The membrane would be maybe 2-3 layers thick, the less the better I think

14 Nov 2026, 16:57:

> Ohhhh I just realised we’re not on the same page regarding the micro switches

14 Nov 2026, 16:59: screenshot of the switch being used: austinamusements.com.au, *"Bulk Buy- 100 x Microswitch For Arcade Buttons"*, brand B.Lee, $135.00. Red body, orange plunger at one end of the top face, NO/NC tabs out the far end, COM out the bottom near that end, two mounting holes at diagonal corners.

14 Nov 2026, 17:30:

> Redo the design so I don’t need to tape anything

14 Nov 2026, 17:41:

> Okay just give me the one you did and I’ll print it anyway

(v0.2 was sliced and checked by then, so the v0.2 G-code was sent.)

14 Nov 2026, 17:57:

> So which is the recommended file to print?

14 Nov 2026, 18:25:

> Did you upload it to GitHub

14 Nov 2026, 18:28 (with an OctoPrint screenshot of the v0.2 G-code: model size 145.38 × 128.38 × 34.00, 1.5 hours):

> These dimensions from octoprint seem off

(OctoPrint's model size includes the purge line and skirt; the part itself is 36 × 36 × 34.)

14 Nov 2026, 18:28:

> Well 1.5 hours seems like a long print still

(→ the FAST "lean" slice of v0.2, 1 h 08 min.)

14 Nov 2026, 18:57:

> You know the TPU button doesn’t need to be full arcade sized, I just wanted a lower profile button that would print faster. This thing is a bit too big

(→ v0.3.)

14 Nov 2026, 17:10: three caliper photos of the switch (no text), read off the beam scale because the display was off:

| | Read from photo | Used |
|---|---|---|
| Body length | ≈ 28 | 27.8 |
| Body height | ≈ 15.6 | 15.6 |
| Height including plunger | ≈ 17.8 | → plunger 2.2 proud |
| Plunger centre from its end | ≈ 5.9 | 5.9 |
| Plunger width | ≈ 2.7 | 2.7 |
| Thickness | not measured | 10.3 (Cherry D44X) |

Reading accuracy is about ±0.3 mm.

## How it works

Modelled in print orientation: the bed is the button face.

| Layer up from the bed | What it is |
|---|---|
| 0–0.6 (3 layers) | membrane across the whole face; free to flex in the ring Ø9–Ø19 |
| Ø9 centre | solid boss bonded to the membrane, tapering at 45° to a Ø6 face with a 0.2 mm recess over the plunger |
| 45° cone | the body grows inward from the Ø19 rim at 45° (parallel to the boss cone: the backup stop). Outside, the Ø23 head has a matching 45° underside, so the walls stay 2.5 mm thick and nothing overhangs |
| 7.7 down | tunnel ceiling with a Ø7 throat for the face, and a 3.6 mm groove the plunger slides in along |
| stem | 16 × 14 mm, only around the plunger end: tunnel 10.6 wide × 15.9 tall, open at the +X end; solid floor (3.6 thick, so the part stands on a desk clear of the COM tab); two 0.45 mm detent bumps click into the switch's mounting hole. COM leaves the switch just outside the stem |

Overall 23 × 23 head, 27.2 tall; face to switch top 8.0. v0.2 was a Ø36 × 34 solid puck: the face size sets the height (45° cone from the rim to the throat), so the smaller face is what made it lower.

**Why no shims (since v0.2):** the press stops when the centre's face lands on the switch's own top face, with the 0.2 recess over the plunger. The plunger always ends 0.2 above flush: 2.0 of travel for this 2.2 plunger, where the D44X clicks within 1.57. Any plunger from 1.77 to 2.3 proud works unchanged, and the floor (not snap ridges) carries the press.

Travel, checked by moving the real meshes (`check_motion.py`): plunger touched at 0.4–0.5, face lands on the switch at 2.4, cone backup at 2.7, nothing else touches. Sliding the switch in, only the detent bumps touch it, over the last 3 mm.

## Print

**Recommended: `gcode/tpu_button_TPUsafe_0.20SPEED_solidboss.gcode`**: 3-layer (0.6) membrane, **36 min, 4.5 g**. eSun TPU 95A forum-safe preset (220/212 °C, as used for the braid tool), 3 perimeters, solid centre. 2-layer face: `gcode/tpu_button_m04_TPUsafe_0.20SPEED_solidboss.gcode`, 35 min, 4.4 g.

**Quicker: `gcode/tpu_button_TPU_0.20SPEED_lean.gcode`**: 30 min, 4.6 g with the FAST preset (225 °C). Only ~6 min quicker now the part is small, and the FAST preset hasn't been proven on this printer, so the safe file is the default. 2-layer: `gcode/tpu_button_m04_TPU_0.20SPEED_lean.gcode`.

(Sent in chat as `tpu_button_v0.3_3layer_TPUsafe.gcode`.)

All face down, no supports, 0.20mm SPEED. To slice it yourself in PrusaSlicer: printer *Original Prusa i3 MK3S & MK3S+*, print *0.20mm SPEED @MK3*, filament *eSun TPU 95A @MK3S* from [printer-profiles](../../printer-profiles/esun-tpu95a-mk3s), then **Perimeters 3**, **Infill > Solid infill threshold area 260 mm²** (fills the small centre and stem sections solid) and **Avoid crossing perimeters**.

- **Sheet:** textured or satin; glue stick on smooth PEI.
- **First layer:** the membrane *is* the first layers, so watch them. Gaps or a starved ring show up as holes in the face.
- **Floor bridge:** the floor under the switch prints as a 10.6 mm TPU bridge at 23.6 mm. A little sag only makes the switch a snug fit.
- **Removal:** flex the steel sheet and lift from the outer edge. Don't peel the middle up first: the 0.4–0.6 ring tears or stretches before the solid parts let go.

## Fit and test

1. Slide the switch in from the open side, plunger end first and the plunger up, so the plunger runs along the groove. Push until it hits the end wall and clicks onto the bumps; the tabs stay outside.
2. Meter across COM–NO (or wire it to the ESP32), then check:

| Check | Pass | If not |
|---|---|---|
| At rest | open | plunger taller than 2.3: `pl_free` up |
| Press the centre | clicks, then lands firmly | no click: `pl_stop` 0 (plunger pushed flush) |
| Press near the edge of the Ø19 face | still clicks | soft edge: bigger `r_boss` |
| Release | springs back, clicks off | sticky: 3-layer membrane instead of 2 |
| Feel | your call | stiffer: thicker `membrane` or narrower ring (`r_rim`); lighter: the opposite |
| Switch retention | doesn't slide out when the wires are tugged | loose: `bump_h` 0.6 |

3. Report back what passed, which membrane you preferred, and how the click feels.

## Parameters (`tpu_button.scad`)

| Name | Default | Meaning |
|---|---|---|
| `membrane` | 0.6 | face thickness: 0.4 = 2 layers, 0.6 = 3 (first layer 0.2) |
| `r_rim` / `r_boss` / `R_out` | 9.5 / 4.5 / 11.5 | flexible face Ø19, stiff centre Ø9, head Ø23. The face radius sets the height |
| `head_t`, `wall`, `stem_x` | 1.4, 1.6, 8.5 | head rim before the 45° underside, stem walls, stem end past the plunger |
| `t_face` | 2.1 | centre travel until its face is level with the ceiling (+ `c_z` to the switch top) |
| `pl_stop` | 0.2 | recess: the plunger stops this far above flush |
| `stop_margin` | 0.3 | cone backup stop after the face lands |
| `r_face`, `r_rec` | 3.0, 2.0 | landing face and plunger recess |
| `r_throat`, `lip` | 3.5, 0.8 | hole and ceiling at the plunger |
| `sw_L`, `sw_T`, `sw_H` | 27.8, 10.3, 15.6 | switch body |
| `pl_off`, `pl_d`, `pl_free`, `pl_pt` | 5.9, 2.7, 2.2, 1.57 | plunger position, width, height, max pretravel |
| `hole_x`, `hole_z` | 2.4, 2.9 | mounting hole near the plunger end (detent bumps) |
| `c_y`, `c_end`, `c_z` | 0.15, 0.2, 0.3 | tunnel clearances |
| `groove_w` | 3.6 | plunger groove width |
| `bump_r`, `bump_h` | 1.0, 0.45 | detent bumps |
| `base_clear` | 3.6 | floor under the switch; ≥ 2 |

## Print times (PrusaSlicer 2.7.2, stock MK3S+, 0.20mm SPEED)

| STL | Filament | stock (2 perimeters, 15 %) | lean (2 perimeters, 10 %, solid small sections) | solidboss (3 perimeters, 15 %, solid small sections) |
|---|---|---|---|---|
| `tpu_button` (0.6 membrane) | eSun TPU 95A (safe) | 34 min, 4.0 g | 36 min, 4.5 g | **36 min, 4.5 g** |
| | eSun TPU 95A FAST | 28 min, 4.1 g | **30 min, 4.6 g** | 30 min, 4.6 g |
| `tpu_button_m04` (0.4 membrane) | eSun TPU 95A (safe) | 33 min, 3.9 g | 36 min, 4.5 g | **35 min, 4.4 g** |
| | eSun TPU 95A FAST | 28 min, 4.0 g | **30 min, 4.6 g** | 30 min, 4.5 g |

Bold = G-code kept in `gcode/`. v0.2 for comparison: 1 h 44 min / 17.3 g (safe), 1 h 08 min (FAST lean).

G-code check (`check_gcode.py`): the 0.6 file prints the free ring on layers 1–3 and nothing in it from layer 4; the 0.4 file on layers 1–2. The centre boss prints as solid infill. Overhang check (`check_overhangs.py`): only the floor bridge (144 mm² at 23.6 mm) and the detent bumps are steeper than 45°.

## Open questions

- Plunger height (±0.3 from the photo) no longer matters within 1.77–2.5; the hole position for the detent bumps is also from a photo.
- Membrane fatigue: TPU 95A at ~2.4 mm deflection over a 5 mm ring (~11 % stretch) may take a set over thousands of presses.
- The Ø23 head overhangs the 14 mm-wide stem by 4.5 mm on two sides; if presses near the edge feel soft, thicken `head_t`.
- Panel mounting: the head could sit on a panel with the stem through a ~16 × 14 mm hole; not designed yet.
- The thickness (10.3) wasn't measured; the pocket is 10.6.

## Files

| File | Purpose |
|---|---|
| `tpu_button.scad` | the model. `part = button / switch / body / boss / info` |
| `render_all.sh` | STLs (0.6 and 0.4 membranes), `info.json`, overhang check |
| `slice_all.py` | slices with the repo's eSun TPU presets → `print_times.json`, keeps the safe solidboss G-code |
| `check_gcode.py`, `check_overhangs.py`, `check_motion.py` | membrane layer / boss fill; overhangs; switch insertion and press travel with the real meshes (`check_motion.txt`) |
| `drawings.py` | `img/tpu_button_drawing.svg/.png` from STL sections |
| `stl/`, `gcode/`, `img/` | outputs |
| `stl/ref_microswitch.stl` | the switch as modelled, for the 3D viewer overlay; not printed |

Regenerate: `./render_all.sh && python3 slice_all.py && python3 drawings.py`.

## Sources

- Cherry D44X operating data (75 cN, pretravel 1.57 max, overtravel 1.27 min): [Arcadexpress](https://arcadexpress.com/en/microswitches/144-cherry-d44x-48mm-button-microswitch.html), [Paradise Arcade](https://paradisearcadeshop.com/products/cherry-pushbutton-microswitch)
- D4-series body 27.8 × 10.3 × 15.9: [Cherry/ZF catalogue](https://www.roger-tech.com/pdf-0d/DB2CA1RC.pdf)
