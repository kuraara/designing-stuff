# Pi 5 PoE NVMe Case — enclosure v0.5

Slide-in "tube" case for a Raspberry Pi 5 + Waveshare PoE HAT (G) + Pimoroni NVMe Base Duo. No screws or standoffs in any board: each board rests on its own ledge. One parametric OpenSCAD file.

**3D:** [body](https://kuraara.github.io/designing-stuff/?m=pi5-poe-nvme-case/print/pi5_case_body_PETG.stl) · [lid](https://kuraara.github.io/designing-stuff/?m=pi5-poe-nvme-case/print/pi5_case_lid_PLA.stl) · [feet](https://kuraara.github.io/designing-stuff/?m=pi5-poe-nvme-case/print/pi5_case_feet_x4_TPU.stl) · [DIN bracket](https://kuraara.github.io/designing-stuff/?m=pi5-poe-nvme-case/print/pi5_case_din_bracket_PETG.stl) in the viewer

Status (13 Nov 2026, v0.5): **body printed and working; to print next: the v0.5 PLA lid and the v0.5 feet.** The SSDs turned out to sit on top of the NVMe Base Duo, so the empty bay under it now takes a **tray on the lid** that carries the Duo for 75 % of its length. Two corner posts stop both boards and put a small lip over the Duo's top corners ([lid v0.5](#lid-v05-tray-under-the-duo-13-nov-2026)). This replaces the v0.4 TPU card retainer. The **feet now take the owner's M4 × 10 button heads**, screwed straight into the body's 4 mm holes, and are 3 mm taller ([feet v0.5](#feet-v05-m4--10-button-heads-13-nov-2026)). No body reprint.

History: v0.2 body printed 10 Nov in PLA, and its ledges hold the Duo through a shake test. v0.3 replaced the TPU lid's failed snap bumps with PLA latch arms. v0.4 added a TPU card retainer, now superseded.

![Assembly](img/pi5_case_3d_assembly.jpg)

## Print it

**Printed 10 Nov 2026:** the body, in PLA rather than PETG: stock *0.30mm DRAFT @MK3* with *Generic PLA* (215 °C / bed 60), 4 h 22 m, 75 g, sliced by PrusaSlicer 2.7.2 CLI the same way as `slice_all.py`. The owner said it printed fine. Board fit, the lid (TPU) and the feet aren't tested yet.

| USB end (printed on the bed) | Floor | Inside |
| --- | --- | --- |
| ![USB end of the printed body: RJ45 and two USB cut-outs](img/print_v0.2_usb_end.jpg) | ![Floor of the printed body: vent slots and the four counterbored foot holes](img/print_v0.2_floor.jpg) | ![Inside the printed body: the ledges and lips along the walls, and the side vents](img/print_v0.2_inside.jpg) |

The yellow on the USB end is leftover filament from the previous print, pressed into the first layers (nozzle and sheet weren't cleaned first); it's cosmetic. The jack cut-outs, vents, foot counterbores and the board ledges all came out clean at 0.30 mm layers.

**11 Nov 2026:** boards fitted. The ledges hold the NVMe Base Duo through a shake test. The v0.2 TPU lid printed, but its snap bumps came out as faint nubs, so the lid is redesigned for PLA (v0.3, below). The body stays as printed.

| File | Material | Orientation (already set) | Time |
|---|---|---|---|
| [`print/pi5_case_body_PETG.stl`](print/pi5_case_body_PETG.stl) | PETG (PLA works: printed 10 Nov, 4h 22m) | USB end on the bed | 4h 26m, 77 g |
| [`print/pi5_case_lid_PLA.stl`](print/pi5_case_lid_PLA.stl) | **PLA**, v0.5 (tray + corner posts). 0.20 mm up to 9 mm (latch hooks), 0.30 mm above | outer face down, tray standing up (82.7 mm tall) | 2h 03m, 26 g |
| [`gcode/pi5_case_lid_PLA.gcode`](gcode/pi5_case_lid_PLA.gcode) | **ready to print** (MK3S+): the v0.5 lid, Generic PLA, those layer heights | outer face down, bed centre | 2h 03m, 26 g |
| [`print/pi5_case_feet_x4_TPU.stl`](print/pi5_case_feet_x4_TPU.stl) | TPU, v0.5 (M4), eSun 95A FAST | counterbore up (fit them turned over) | 20m, 4 g |
| [`gcode/pi5_case_feet_x4_TPU_sequential.gcode`](gcode/pi5_case_feet_x4_TPU_sequential.gcode) | **ready to print** (MK3S+): the v0.5 feet, slower TPU preset, one foot at a time | 4 separate objects, 70 mm apart | 28m, 4 g |
| [`print/pi5_case_din_bracket_PETG.stl`](print/pi5_case_din_bracket_PETG.stl) | PETG, 4 perimeters, 40% gyroid | rail side down | 2h 24m, 43 g |

Body, feet and bracket at 0.30 DRAFT. No supports. Feet **or** DIN bracket, not both. Fit the microSD card before the PCIe ribbon (the ribbon covers the slot).

[`print/pi5_case_design.pdf`](print/pi5_case_design.pdf): 19-page design pack, v0.5 (drawings, 3D views, print and assembly notes, brief) with the four STLs embedded as PDF attachments.

Online: [drawings page](https://claude.ai/artifact/S3LdNWXs8CYuMMDd2AhQnt) (private to the owner) · [3D viewer](https://claude.ai/artifact/GdAqqBgVog6yVpPGcgRbWo) (anyone with the link). The same pages are in this folder as `pi5_case.html` and `pi5_case_viewer.html`.

| | |
|---|---|
| ![Section through the ledges](img/pi5_case_3d_section.jpg) | ![On a DIN rail](img/pi5_case_3d_din_rail.jpg) |
| Section: Pi on the upper ledge, NVMe Base Duo on the lower ledge | On a TS35 DIN rail via the bracket |

![Section A-A](img/pi5_case_drawing_section_A-A.png)

![Lid latch in the body window, 4:1](img/pi5_case_drawing_lid_latch.png)


## Brief (verbatim, 1 Nov 2026)

> Let’s make a raspberry pi 5 case. Requirements:
> - it has a PoE hat (check my Gmail inbox for order confirmations from Core Electronics for the part number)
> - it has a pimoroni dual nvme base
>
> I want to avoid screw holes, I would prefer. Refer to this sketch of the side profile showing how I would like the pi and the nvme base to sit on a lip
>
> The nvme base will need enough vertical clearance from the pi to account for thick nvme disks (dual Samsung 1TB)
>
> For the USBC port, it will need enough clearance to account for fairly chunky usb connectors like the ones on dell thunderbolt docks
>
> Previous designs I have made use. 3mm walls but that’s not a hard requirement. If strength can be gained through smart use of webbing and structural ribs then that would be ideal if print time can be optimised
>
> Printing in 2-3 parts would be ideal,
> - main body
> - lid
>
> If the lid is on the smallest face (the usb/rj45 end) or the sd card  end that would be ideal. The pi can slide in like into the case as if it were a tube
>
> Attaching the end pieces “lids” can wither be screw in (m3, counter bore heads, or a nice click in place) for a screwless click in place I would print that from TPU to allow for some flex with whatever you use, and it can still retain some rigidity
>
> Give it ventilation holes top and bottom, you can increase the space between the inner walls and the nvme base/poe hat as they tend to generate a bit of heat
>
> It will also need some feet that can be screwed in with m3  counterbored screws
>
> Make some sort of tray for the as card so it can be slotted in and out like a SIM card
>
> I think those are all the requirements for now
>
> Create 2d projections before the 3d model

**Sketch (attached image, described):** side profile of one wall. Thin upper wall; below it the wall steps inward into a solid lip; the Pi box rests on the lip top, overlapping it; below the lip the wall steps back outward, ending thicker than the upper wall.

## Follow-ups (verbatim, 1 Nov 2026, after v0.1)

> I’d prefer the cross section be like this  *(second sketch attached)*
>
> I don’t want to screw into the pi or the nvme base, the idea is for this to be simple
>
> Alright skip the sad card holder stuff

**Second sketch (described):** one wall in section. Upper lip with the Pi resting on its top; below it the wall steps out into a recess where the NVMe board's edge runs; a lower lip the NVMe board rests on; below that the wall steps back out (less far than the recess).

> 1. Samsung 980EVO
> 2. No idea
> 3. Not fussed, the gpio pins hold it in pretty snugly

(Answers to: which SSDs / actual HAT height / add HAT hold-down ribs.)

Changes for v0.2: standoffs and Duo screws dropped, each board on its own ledge (upper lip between the boards); SD tray and microSD-extension sleeve removed; USB-end jaws removed (boards stop on the end wall); lid prongs now push both boards; side vents added in the recess between the lips.

Printer: Prusa i3 MK3S+. Project preference: functional over pretty, faster over perfect; TPU/PETG preferred.

## Print test and lid v0.3 (11 Nov 2026)

Messages (verbatim, 11 Nov 2026):

> The case printed well, the little tabs on the lid did not print at all

*(5 photos: the yellow TPU lid edge-on showing the prongs and only faint nubs where the snap bumps should be; inside the white body showing the ledges and side windows; the floor with vents and feet bosses; the USB/RJ45 end.)*

> PLA might be able to do the job if you make the tabs thin enough to flex a little

> The rails are doing a good job of securing the nvme base

*(2 photos: the NVMe Base Duo sitting on the lower ledges, PCIe connector clear; the lid's TPU prongs printed with stringy roots.)*

> I can shake the case and the base is secure

**Why the TPU bumps failed.** Slicing the v0.2 lid with the TPU preset (0.30 mm layers) and measuring the toolpath: the bumps *were* in the G-code, but they stood only 0.04 → 0.79 → 0.13 mm proud over about five layers, which TPU smoothed away. Even printed perfectly, only 0.55 mm of a 0.8 mm bump (after the 0.25 mm fit gap) would have reached into the windows. Too small for TPU.

**v0.3 lid (body unchanged):**

- PLA (or PETG), rigid. One flexing **latch arm** per long side: 19.1 mm of skirt cut free by slots through the lid plate (1.2 mm inside, 0.8 mm outside, 1.0 mm across the free end), fixed at its top end. Arm 1.6 mm thick; it bends sideways, in the layer plane, so PLA flexes along its filaments. Root to hook 14.1 mm, deflection 0.75 mm to pass the wall, strain ≈ 0.9%.
- Hook 1 mm high × 8 mm wide, 45° retaining face (prints as a 45° overhang), ~40° lead-in; sits in the body's **upper** side window (2.8 × 9) with 0.2/0.1 mm clearance along X and 0.5 mm each side in Z; 0.75 mm reaches into the 2.4 mm wall. The lower windows are now vents (they line up with the Duo prongs, so no arm fits there).
- Toolpath check (PLA, 0.20 SPEED): the hook bulge reaches the full 0.99 mm and spans 12 layers; the 0.8 and 1.2 mm slots have no extrusion on layers 1–2.
- Skirt leading edge chamfered 0.6 mm to ease a rigid lid into the mouth.
- Prongs now stop 0.2 mm short (`prong_tip` 0.6 → 0.3): a rigid lid can't take the old 0.1 mm preload. The ledges already hold the boards.
- Assembled: lid ∩ body = 0, lid ∩ boards = 0. During insertion only the hooks overlap the wall, which the arms flex past.
- To open: pull at the body's thumb notch; if tight, press the hooks in through the side windows with a small screwdriver.

Tuning: `latch_t` (arm thickness, softer at 1.2) and `latch_hook` (hook height, firmer at 1.2). Both only need a lid reprint.

## Lid v0.5: tray under the Duo (13 Nov 2026)

**Settled 13 Nov: modelled, checked and sliced.** The sketches came first, then the owner's answers (below).

Owner's message (verbatim). It came with a photo into the body from the mouth (marked up in magenta: both top corners of the Duo, and the space under it) and a side sketch of the lid ([photos](#photos-and-sketches-originals)):

> Got some lid changes
> - The drives face up, and sit between the pi and base. Your design assumes the other way.  Which isn’t a problem, we can resolve that with a modified lid
> - the ledge for the nvme is too narrow. In future designs it needs to be much wider
> - For now let’s create a pla lid that has a tray to support the base for at least 50-75% the length of the card
> - Have a much smaller lip to secure the top of the card
> - another lip to keep the pi pressed in, this lip will press up directly against the pi
>
> Put together some sketches to verify that you understand my intention

Design (`part = "lid"` print-oriented, `"lid_asm"` in place; parameters under `[Lid v0.5]`, `lid_tray = true`):

- **The SSDs are on top of the Duo**, in the 12 mm gap under the Pi.
  - Height: 5 mm standoff + 2.38 mm drive ≈ 7.4 mm.
  - The upper lip only reaches 1 mm in from each edge, so the drives clear it.
  - The 9.5 mm SSD bay under the Duo is now empty, and the tray goes there.
- **The tray is part of the PLA lid.**
  - Plate: 2 mm thick, 49 mm wide, running between the lower ledges with 0.5 mm clear each side.
  - Height: its top is 0.1 mm below the ledge plane.
  - Reach: 63.75 mm under the Duo, which is 75 % of 85 (`tray_frac`).
  - Slots: lined up with the floor vents.
  - Webs: three 1.6 mm webs underneath run on the floor's bars, stopping 0.4 mm above the floor so the tip can't droop.
  - Tip: a 4 × 1 mm lead-in lifts a sagging board onto the tray.
- **Two corner posts**, 5.6 mm wide, sit in the corners circled in the photo.
  - Stop: the post face stops both boards' SD edges with 0.2 mm float, like the v0.2 prongs.
  - Duo lip: the "much smaller lip" is 1.6 mm thick, sits 0.2 mm above the Duo's top and reaches 1.5 mm over each top corner.
  - Pi stop: the post top is 1 mm above the Pi's top, so the same face is the "lip against the Pi", pushing it home.
  - Clearances: the posts stay clear of the PCIe ribbon (mid-width), the Duo's M.2 socket and ADDON FFC connector, and the Pi's power button. These positions are read off the photo, not measured.
- **The lid replaces the TPU card retainer.** The two can't be fitted together, because the webs and the retainer ring both need the bottom of the mouth. The skirt and latch arms are v0.3, unchanged.
- **Checks** (trimesh):
  - lid ∩ body = 0.
  - No contact with either board (including ±0.4 mm sideways play), the SSD envelope, the ribbon zone, or the heatsink push-pin tail under the Pi's corner.
  - The tray's YZ profile already fits the lipped cavity along its whole length, so it slides in.
- **Printing:** as v0.3, plate down, PLA, no supports. The tray, webs and posts stand straight up (82.7 mm tall) and every layer sits inside the one below. Layers are 0.20 mm up to 9 mm, where the latch hooks are, then 0.30 mm: 2h 03m and 26 g, against 2h 29m at 0.20 mm throughout. PrusaSlicer's CLI has no flag for this, so `slice_all.py` writes a 3MF with layer-height ranges. The tray slots cost about 19 minutes (`tray_slots = false` drops them).
- **Next body:** the Duo ledge gets much wider (owner). With the drives on top, the next body can also drop the SSD bay (`drive_drop`) and carry the Duo on a wide shelf instead.

Questions and the owner's answers (13 Nov, verbatim). The questions asked were 1. tray length (75 % drawn); 2. is the Duo's underside clear over the tray; 3. Pi stop at both corners or the GPIO side only; 4. solid corner posts or two separate fingers like the sketch:

> 1. Yes
> 2. Yes
> 3. Not sure
> 4. Whatever will print more reliably

Decisions:
- **Tray:** 75 % (63.75 mm under the Duo), flat top against the Duo's underside.
- **Pi stop at both corners** (`pi_stop = [true, true]`). The pushes are balanced, and the Pi's power button sits about 15 mm in from the USB-C edge and is pressed from above, so an edge stop doesn't touch it. `pi_stop = [false, true]` drops the USB-C-side stop if it ever gets in the way.
- **Solid posts.** Printed plate-down, two separate fingers would stand 16 mm off the plate with their layer lines across the bending load, so they'd be easy to snap. A solid 5.6 × 18.3 mm post is a stable column. Each is about 2 g.

| | |
|---|---|
| ![Side section through the GPIO-side corner](img/pi5_case_lid_v0.5_sketch_side.png) | ![Corner post, 3:1](img/pi5_case_lid_v0.5_sketch_detail.png) |
| ![From the lid end, same view as the photo](img/pi5_case_lid_v0.5_sketch_end.png) | ![Plan under the Duo](img/pi5_case_lid_v0.5_sketch_plan.png) |

![The v0.5 lid seen from inside the case](img/pi5_case_lid_v0.5_sketch_3d_lid.png)

Orthographic views. The owner asked (verbatim):

> Can you explain corner post 3.2? There’s a very large blue shaded area

> If you can do some orthogonal projections of the new lid design that might help

The shaded area is one solid 5.6 mm-wide corner post, cut through its middle. It spans the 16.3 mm from the lid plate to the boards, which is the ribbon-loop space plus the skirt.

![Lid v0.5, orthographic views](img/pi5_case_lid_v0.5_sketch_ortho.png)

## Feet v0.5: M4 × 10 button heads (13 Nov 2026)

Owner (verbatim):

> Add this to your work list and get to it once we’ve settled on the lid design:
>  I’m not sure if you realised it based on my design specs, the screw holes for the TPU feet fit an m4 screw, not an m3 as initially requested.  
> The only m4’s I have are a button cap screw with a 7mm head. So the counterbore hole for the feet needs to suit that, and be height of the feet needs to increase 3mm

The body's 4.0 mm foot holes were drawn for M3 heat-set inserts, which is why an M4 fits them. Asked for the screw length and how it fixes, the owner answered **M4 × 10**, **straight into the PLA** (it cuts its own thread; no inserts).

- Foot: Ø14 × **9** (was 6, +3 mm as asked), M4 clearance hole Ø4.5, counterbore **Ø7.6 × 3.8** for the Ø7 head (ISO 7380 M4: about 2.2 mm tall, so it sits 1.6 mm up inside).
- Still printed counterbore-up, and fitted counterbore toward the desk. Same Ø14 footprint, so it fits the printed body's 0.6 mm recesses.

Screw stack, case frame (z = 0 at the case bottom; the foot's top sits in the 0.6 mm recess):

| | z |
|---|---|
| head seat (counterbore floor) | -4.6 |
| case bottom / recess floor | 0 / 0.6 |
| screw tip (M4 × 10) | 5.4 |
| end of the printed body's hole (5.4 below the recess) | 6.0 |

So there's 5.2 mm of TPU under the head, 4.8 mm of thread in the PLA, and the tip stops 0.6 mm short of the end of the hole. The model asserts it can't bottom out (`body_hole`). The DIN bracket is unchanged: it still expects M3 × 20 into heat-set inserts.

## Photos and sketches (originals)

Request (verbatim, 12 Nov 2026):

> Can you re-upload the attached images to git

Every image attached in the design chat, full resolution and byte-for-byte as uploaded (no location data in any of them), in [`img/photos/`](img/photos/). Click a thumbnail for the full image. The three `img/print_v0.2_*.jpg` used above are half-size copies of three of these.

| | | |
|---|---|---|
| <a href="img/photos/2026-11-01_sketch-1_side-profile-lip.jpg"><img src="img/photos/2026-11-01_sketch-1_side-profile-lip.jpg" width="220" alt="Sketch 1 (1 Nov): side profile, Pi and NVMe base sitting on a lip"></a> | <a href="img/photos/2026-11-01_sketch-2_cross-section-two-ledges.jpg"><img src="img/photos/2026-11-01_sketch-2_cross-section-two-ledges.jpg" width="220" alt="Sketch 2 (1 Nov): the cross-section adopted in v0.2: Pi on the upper lip, NVMe base on the lower ledge"></a> | <a href="img/photos/2026-11-11_v0.2-tpu-lid_edge-prongs.jpg"><img src="img/photos/2026-11-11_v0.2-tpu-lid_edge-prongs.jpg" width="220" alt="v0.2 TPU lid edge-on: prongs printed, snap bumps barely there"></a> |
| Sketch 1 (1 Nov): side profile, Pi and NVMe base sitting on a lip | Sketch 2 (1 Nov): the cross-section adopted in v0.2: Pi on the upper lip, NVMe base on the lower ledge | v0.2 TPU lid edge-on: prongs printed, snap bumps barely there |
| <a href="img/photos/2026-11-11_v0.2-tpu-lid_side-faint-bumps.jpg"><img src="img/photos/2026-11-11_v0.2-tpu-lid_side-faint-bumps.jpg" width="220" alt="v0.2 TPU lid side: the snap bumps came out as faint nubs"></a> | <a href="img/photos/2026-11-11_v0.2-body_inside-ledges.jpg"><img src="img/photos/2026-11-11_v0.2-body_inside-ledges.jpg" width="220" alt="v0.2 PLA body, inside: ledges and side windows"></a> | <a href="img/photos/2026-11-11_v0.2-body_floor-vents-feet.jpg"><img src="img/photos/2026-11-11_v0.2-body_floor-vents-feet.jpg" width="220" alt="v0.2 PLA body, floor: vents and foot bosses"></a> |
| v0.2 TPU lid side: the snap bumps came out as faint nubs | v0.2 PLA body, inside: ledges and side windows | v0.2 PLA body, floor: vents and foot bosses |
| <a href="img/photos/2026-11-11_v0.2-body_usb-rj45-end.jpg"><img src="img/photos/2026-11-11_v0.2-body_usb-rj45-end.jpg" width="220" alt="v0.2 PLA body, USB/RJ45 end"></a> | <a href="img/photos/2026-11-11_v0.2_nvme-base-and-lid-prongs.jpg"><img src="img/photos/2026-11-11_v0.2_nvme-base-and-lid-prongs.jpg" width="220" alt="NVMe Base Duo on its ledges, TPU lid prongs behind it"></a> | <a href="img/photos/2026-11-11_v0.2_nvme-base-on-ledges.jpg"><img src="img/photos/2026-11-11_v0.2_nvme-base-on-ledges.jpg" width="220" alt="From the mouth: NVMe Base Duo on the lower ledges (held through a shake test)"></a> |
| v0.2 PLA body, USB/RJ45 end | NVMe Base Duo on its ledges, TPU lid prongs behind it | From the mouth: NVMe Base Duo on the lower ledges (held through a shake test) |
| <a href="img/photos/2026-11-11_m3x8-button-head_length.jpg"><img src="img/photos/2026-11-11_m3x8-button-head_length.jpg" width="220" alt="Foot screw in calipers: ~10 mm overall, M3 x 8 button head"></a> | <a href="img/photos/2026-11-11_m3x8-button-head_head.jpg"><img src="img/photos/2026-11-11_m3x8-button-head_head.jpg" width="220" alt="Foot screw in calipers: button head"></a> | <a href="img/photos/2026-11-11_sketch-3_tpu-card-retainer.jpg"><img src="img/photos/2026-11-11_sketch-3_tpu-card-retainer.jpg" width="220" alt="Sketch 3 (11 Nov): TPU frame in the mouth pressing the board edges, which became the v0.4 card retainer"></a> |
| Foot screw in calipers: ~10 mm overall, M3 x 8 button head | Foot screw in calipers: button head | Sketch 3 (11 Nov): TPU frame in the mouth pressing the board edges, which became the v0.4 card retainer |
| <a href="img/photos/2026-11-13_v0.2-body_boards-from-mouth_marked-up.jpg"><img src="img/photos/2026-11-13_v0.2-body_boards-from-mouth_marked-up.jpg" width="220" alt="13 Nov: Pi and Duo in the body, seen from the mouth, marked up: Duo top corners and the space under it"></a> | <a href="img/photos/2026-11-13_sketch-4_lid-tray-side.jpg"><img src="img/photos/2026-11-13_sketch-4_lid-tray-side.jpg" width="220" alt="Sketch 4 (13 Nov): lid side view with a stub against the Pi, a small lip over the Duo and a tray under it"></a> | |
| 13 Nov: boards in the body from the mouth, marked up (Duo top corners, space under the Duo) | Sketch 4 (13 Nov): lid with a Pi stop, a small lip over the Duo and a tray under it | |

## G-code: feet and card retainer (11 Nov 2026)

13 Nov: the feet G-code is now the v0.5 (M4) feet, 28m and 4 g. The card retainer G-code was removed with the retainer, and the v0.5 lid G-code was added (see [Print it](#print-it)).

Request (verbatim, 11 Nov 2026):

> Re-slice the TPU feet to a more conservative speed and set to individual object prints then push to GitHub

[`gcode/pi5_case_feet_x4_TPU_sequential.gcode`](gcode/pi5_case_feet_x4_TPU_sequential.gcode), made by `slice_all.py`:

- Filament: the project's slower **eSun TPU 95A @MK3S** preset (the forum baseline): 220 °C first layer / 212 °C, max volumetric speed 2.4 mm³/s, extrusion multiplier 1.07, slow down below 15 s layer time. The FAST preset used for the estimates elsewhere runs at 225 °C and 3.5 mm³/s.
- Print: stock *0.30mm DRAFT @MK3*, *Original Prusa i3 MK3S & MK3S+*, with **Complete individual objects** on (`complete_objects = 1`). The four feet are separate objects at (90, 70), (160, 70), (90, 140) and (160, 140), 70 mm apart, clear of the MK3S's 45 mm extruder clearance radius. At 6 mm tall they're well under its 20 mm clearance height.
- Each foot prints complete before the next (layer height restarts 4×). Small layers hit the 15 s minimum layer time, so most of it runs at the 15 mm/s floor with the fan on.
- 21 min, 3.2 g. The printer check is `M862.3 P "MK3S"`.

Request (verbatim, 11 Nov 2026):

> If you haven’t already, slice the TPU insert for the card holders and push to GitHub

~~`gcode/pi5_case_card_retainer_TPU.gcode`~~ (removed 13 Nov with the retainer; still in git history): the v0.4 card retainer, same slower **eSun TPU 95A @MK3S** preset and *0.30mm DRAFT* profile, back face down at the bed centre, no supports. 24 min, 4.1 g. Toolpath check: the four lock bumps are the full 1.19 mm from the first layer.

## Card retainer v0.4 (11 Nov 2026)

**Superseded by the v0.5 lid (13 Nov).** The lid's tray and posts hold the boards now, and the two can't be fitted together. The retainer is off the print list (`retainer = false`), but `part = "retainer"` still builds it.

Messages (verbatim, 11 Nov 2026):

> Then I think securing the cards should be separate from the back lid. So we make a TPU insert that locks the cards in tightly, then the pla lid goes on after that

> If there’s a better way to do that then by all means suggest it and don’t be 100% stuck to the shape of this bit

*(photo: the printed body from the mouth, with a magenta sketch of a rectangular frame inside the opening, behind the boards, with marks where it presses the NVMe base and the upper board's edges)*

Design (`part = "retainer"` / `"retainer_asm"`; parameters under `[Card retainer]`):

- TPU ring following the cavity mouth, 2.4 mm section, x -6.52 → -1.5 (boards' SD edges at x = 0.5). Press fit 0.15 mm per side. The middle is open for the PCIe ribbon loop and airflow.
- Three leaning fingers (≈40°, 1.4 mm thick, 4 mm tall) from bosses on the side bars to the board corners: both Duo corners and the Pi's GPIO-side corner. The Pi's power-button corner is left free. The tips reach 0.4 mm past the board edges; the lean turns that into bending, a few newtons per finger instead of a hard jam.
- Locks itself: four bumps (1.2 mm high, 2 mm wide) drop into the first roof vent slots (y = 15.5, 40.5) and floor vent slots (y = 12.375, 43.625). Their square back faces catch on the slots' mouth-side ends (x = −7). These slots are already in the printed v0.2 body. Remove the retainer by pressing the bumps in through the vents and pulling the ring.
- Prints back face down: the bumps grow straight off the bed. Toolpath check (TPU 0.30): full 1.19 mm bumps from the first layer.
- Checks: with no press fit, retainer ∩ body = 0 (bumps clear inside the slots), retainer ∩ lid = 0, and HAT / SSDs / ribbon loop / Pi power-button corner all clear. Fingers overlap each board edge by exactly the 0.4 mm preload. Lid skirt end to ring: 3.5 mm.
- The lid loses its prongs (`if (!retainer)`), so a rigid PLA lid never presses the boards.

## Feet v0.4: suit M3 × 8 button heads (11 Nov 2026)

**Superseded by feet v0.5 (M4 × 10, 13 Nov).**

Message (verbatim, 11 Nov 2026, with two photos of a button-head screw in calipers):

> Can you confirm your design of the feet suit these screws

The caliper display was off; the beam scale reads ≈10 mm overall, i.e. an **M3 × 8 button head** (ISO 7380, head Ø5.7 × 1.65).

**v0.2 feet did not suit it** (design error): the foot left 1.8 mm of TPU under the head, so 6.2 mm of screw entered the case, but the insert hole is only 5.4 mm deep below the 0.6 mm foot recess (shorter than the 5.7 mm insert itself). The screw would bottom out 0.8 mm before clamping.

v0.4 stack-up (z = 0 at the case bottom; foot top sits in the recess at z = 0.6):

| | z |
|---|---|
| head seat (foot 6 tall, 3.0 counterbore → 3.0 mm TPU under the head) | -2.4 |
| screw tip (M3 × 8) | 5.6 |
| insert end (M3 × 5.7, pressed flush with the recess floor) | 6.3 |
| hole end, printed v0.2 body / new bodies (`insert_depth` 6.5 below the recess) | 6.0 / 7.1 |

5.0 mm of thread in the insert; the head sits 1.35 mm below the foot's face. On the printed body, press the inserts flush with the recess floor; the last 0.3 mm melts into solid plastic above the 5.4 mm hole, which is fine. The DIN bracket's M3 × 20 (button or socket head) ends at z = 5.0: 4.4 mm in the insert, no change needed. The model now `assert`s that the foot screw can't bottom out.

## Parts identified

| Part | Source |
|---|---|
| **Waveshare Power Over Ethernet HAT (G) for Raspberry Pi 5 (5V 5A)**, SKU **WS-27670** | Core Electronics order #1000592941, 13 Mar 2025 (Gmail). Same order: Raspberry Pi 5 Model B 4GB (CE09785), Raspberry Pi 5 Active Cooler (CE09791) |
| Pimoroni NVMe Base Duo, PIM704 | User. Kit: 4 × 12 mm M2.5 standoffs, short M2.5 bolts, 5 mm M2 SSD standoffs, PCIe flex |

Known data: HAT (G) 64.98 × 56.5, no fan, compatible with the Active Cooler (Waveshare). Duo 85 × 56, fits under the Pi on 12 mm standoffs, SSDs face up, between the Duo and the Pi (owner, 13 Nov 2026: the earlier note here, "face away from the Pi", was wrong), two M.2 slots side by side (2230–2280), FFC moved to the middle of the SD-end edge; the ribbon blocks the Pi's microSD slot (Tom's Hardware, Pimoroni). Pi 5 port centres from its mechanical drawing: USB-C 11.2, micro HDMI 25.8 / 39.2 along the long edge; Ethernet 10.2, USB 29.1 / 47 across the USB end.

## DIN rail bracket (added 1 Nov 2026)

Request (verbatim):

> Let’s create another component that uses the footprint of the feet to attach it to the case.
>
> It will be a bracket to mount it on a DIN rail
>
> Leave plenty of clearance for the airflow, make sure the bracket is sturdy and rigid as people may be rough installing and removing it

Design (`part = "din"`, `"din_asm"`, `"din_rail"`; parameters under `[DIN rail bracket]`):

- Bolts to the four foot inserts in place of the feet: 4 × M3 × 20 socket heads through counterbored bosses (5.4 deep counterbore leaves 5 mm in the insert). Boss tops have a spigot that sits in the foot recess.
- TS35 rail (35 × 7.5 or 35 × 15) runs **across** the case, so the case stands with its length vertical: 69 mm (4 modules) along the rail. The bolt pattern is symmetric about the bracket centre, so the case bolts on USB-end-down (cables hang) or up.
- Airflow: 14 mm air gap (`din_gap`) between the bracket plate and the case floor, forming a vertical chimney behind the floor vents; side ribs sit under the case's thick lower walls, clear of the vents; open window and flexure gaps in the plate.
- Rigidity: 6.4 mm plate, two 20.4 mm side ribs along the full length, gussets along the spine, rail contact spread across the full 68 mm width.
- Clip: fixed hook on one flange, full width, 3.2 mm under the flange. Latch on the other flange: head 24 mm wide, 1.5 mm under the flange, lead-in ramp so it snaps on; carried by two 1.0 mm flexure beams (≈21 mm free span each side, ~29 MPa at full travel in PETG). Over-travel stop at 2.2 mm (release needs 1.75), and even at the stop the fixed hook still has 0.75 mm of engagement. Pull tab with a screwdriver slot.
- Print: PETG, rail side on the bed, flexures in-plane (they bend within layers). The rail pocket's ceiling is a ~36 mm bridge over the rail channel; sag there touches nothing. Draft profile 1h 39m / 31 g; recommended 4 perimeters + 40% gyroid: 2h 24m / 43 g.
- Stand-off: case floor 25.1 mm from the wall, case front 89.7 mm from the wall.
- Not yet printed; check the latch feel and the snap on a real rail first.

## Architecture

| Part | Material / orientation | What it does |
|---|---|---|
| **Body** | PETG, USB end on the bed (tube vertical) | Closed USB/RJ45 end with jack cut-outs; upper and lower lips along both long walls; thick SSD-bay walls below the lower lip; USB-C/HDMI window; roof, floor and side vents; snap windows at the mouth; feet inserts |
| ~~Card retainer~~ (v0.4) | TPU | Superseded by the v0.5 lid's tray and corner posts |
| **Lid** (v0.5) | PLA, outer face on the bed, 0.20 mm to the hooks then 0.30 | Click-in at the SD end: chamfered skirt + 2 flexing latch arms whose hooks click into the upper side windows. A slotted tray carries the Duo from below for 75 % of its length (webs to just above the floor); two corner posts stop both boards and put a small lip over the Duo's top corners |
| Feet × 4 (v0.5) | TPU, flat, counterbore up | Ø14 × 9, Ø7.6 × 3.8 counterbore (faces the desk when fitted), M4 × 10 button head straight into the body's 4 mm hole |

**How the boards are held (no screws, no standoffs):** each long wall has two lips (user's second sketch). The Duo rests on the lower ledge (3 mm reach, too narrow per the owner, so v0.5's lid tray carries it from below too). The Pi rests on the upper ledge (1 mm reach), and the upper lip sits in the 12 mm gap between the boards, with the SSDs on top of the Duo. The PCIe ribbon is the only link between the boards. They slide in together from the SD end, USB first, and stop on the closed USB end wall. The lid's corner posts stop them there (0.2 mm float). The HAT is held by its GPIO + PoE headers only.

**Why the Pi's ledge is only 1 mm:** the GPIO solder joints and the USB/RJ45/USB-C/HDMI shell tabs on the Pi's underside start about 1.4 mm in from the long edges.

**Port window notch:** a chunky USB-C overmold hangs ~2 mm below the Pi's board edge. Along the window (x 3.2–45.2) the upper lip's outer half (beyond 1.4 mm outside the board edge) drops 2.5 mm; the 1 mm ledge under the Pi continues, tied to the wall below the notch.

**Power button:** the owner's photo shows the Pi 5's button (with its LED) on the SD-end edge about 15 mm in from the USB-C side, pressed from above. The v0.5 posts only touch the board's end face at the corners.

Coordinates in the SCAD: board-aligned. X = 0 at the boards' SD edge, 85 at the USB edge; Y = 0 at the HDMI/USB-C edge; Z = 0 at the case's outside bottom.

## Key numbers (all parameters in `pi5_case.scad`)

| Parameter | Default | Basis |
|---|---|---|
| `drive_drop` | 9.5 | space under the Duo, kept for SSDs on its underside. They sit on top (13 Nov), so the v0.5 lid's tray and webs use it; a future body can drop it |
| `air_below` | 3.5 | more space under the Duo, above the floor vents |
| `duo_gap` | 12 | Duo top → Pi underside, set by the case; matches the length of Pimoroni's ribbon |
| `duo_ledge` / `duo_lip_t` | 3.0 / 3.0 | lower ledge reach / thickness. **Too narrow** (owner, 13 Nov): much wider in the next body |
| `pi_ledge` / `pi_lip_t` | 1.0 / 5.0 | upper ledge reach / thickness (7 mm clear above the Duo) |
| `fence_gap` / `fence_h` | 0.4 / 1.2 | sideways play per side / fence height |
| `plug_step` / `plug_reach` | 2.5 / 1.4 | port-window notch in the upper lip |
| `hat_gap` | 16 | Pi top → HAT underside, clears the Active Cooler. **Check actual** |
| `hat_comp` | 9 | tallest part on the HAT. **Measure** |
| `air_top` | 5 | HAT parts → roof |
| `side_gap` | 4 | board edge → wall (air, per brief) |
| `sd_space` | 10 | board SD edge → lid skirt (ribbon loop ~7) |
| `low_in` | 0.5 | SSD-bay wall face, inward from the board edge |
| `wall` etc. | 2.4 | 3.0 costs +57 min on the body |
| side window | 42 × 11 | USB-C + both micro HDMI |
| `foot_h` / `foot_cb` / `foot_hole` / `foot_screw` | 9 / [7.6, 3.8] / 4.5 / 10 | foot height / counterbore Ø × depth / M4 clearance / screw length under the head (v0.5, M4 × 10 button head) |
| `insert_d` / `insert_depth` / `body_hole` / `foot_recess` | 4.0 / 6.5 / 5.4 / 0.6 | foot hole in the body (M4 self-taps; drawn for M3 inserts) / its depth in new bodies / its depth in the printed v0.2 body (used by the screw check) / foot recess |
| `fit` / `lead_c` | 0.25 / 0.6 | skirt clearance / skirt lead-in chamfer (`prong_tip` only applies with `lid_tray = false` and `retainer = false`) |
| `ret_fit` / `ret_reach` / `ret_bump` | 0.15 / 0.4 / 1.2 | retainer press fit per side / finger preload / bump height into the vent slots |
| `latch_t` / `latch_hook` / `latch_w` | 1.6 / 1 / 8 | lid latch arm thickness / hook height / hook width (v0.3; replaces v0.2's `bump` 0.8) |
| `latch_slot` / `latch_gap` / `latch_end` | 1.2 / 0.8 / 1.0 | slots freeing the arm: inside / outside through the plate / across the free end |
| `tray_frac` / `tray_t` / `tray_drop` / `tray_slots` | 0.75 / 2.0 / 0.1 / true | lid v0.5: tray reach as a fraction of the Duo / plate thickness / top below the ledge plane / slots over the floor vents |
| `post_y` / `stop_x` / `lip_over` / `lip_gap` / `pi_stop` | corners 5.6 wide / 0.3 / 1.5 / 0.2 / both | corner posts across Y / stop face (0.2 float) / lip reach over the Duo / lip above the Duo / which posts reach up to stop the Pi |

Outside: 106.3 L (with lid) × 68.8 W × 64.6 H; 69 H on feet.

## Print times

PrusaSlicer 2.7.2, stock *Original Prusa i3 MK3S & MK3S+*, *0.30mm DRAFT @MK3* (lid: *0.20mm SPEED @MK3*, v0.5 with 0.30 mm layers above 9 mm). TPU = the project's *eSun TPU 95A FAST @MK3S* overrides on Generic FLEX, or the slower *eSun TPU 95A @MK3S* for the committed G-code.

| Part | Material | Time | Filament |
|---|---|---|---|
| Body | PETG | 4h 26m | 77 g |
| Body (reference) | PLA | 4h 23m | 75 g |
| Body with 3 mm walls (comparison) | PETG | 5h 23m | 83 g |
| **Lid v0.5** (0.20 to the hooks, then 0.30; the G-code) | PLA | 2h 03m | 26 g |
| Lid v0.5 at 0.20 throughout (reference) | PLA / PETG | 2h 29m / 2h 50m | 27 / 27 g |
| ~~Lid v0.4~~ (superseded) | PLA | 48m | 14 g |
| ~~Card retainer v0.4~~ (superseded) | TPU | 18m | 4 g |
| ~~Lid v0.2~~ (superseded) | TPU | 1h 09m | 16 g |
| **Feet × 4 v0.5** (FAST / slower preset one at a time, the G-code) | TPU | 20m / 28m | 4 g |
| DIN bracket (draft) | PETG | 1h 39m | 31 g |
| DIN bracket (4 perimeters, 40% gyroid) | PETG | 2h 24m | 43 g |

## Decisions (v0.2)

1. SSDs: Samsung 980-series (user wrote "980EVO"; Samsung's 980 and 970 EVO Plus 1TB are both single-sided 2.38 mm, no heatsink). On the Duo's 5 mm SSD standoffs they reach ~7.4 mm below the Duo; `drive_drop` 9.5 kept (~2 mm spare). **Correction, 13 Nov:** the SSDs sit on top of the Duo, under the Pi (owner); see lid v0.5.
2. HAT height unknown: `hat_gap` kept at 16 (worst case with the Active Cooler). A lower HAT just gets more air above it.
3. HAT held by its GPIO + PoE headers only; no hold-down ribs.
4. SD tray dropped (the PCIe ribbon covers the Pi's microSD slot; fit the card before the ribbon). Lid: click-in TPU (v0.2), then PLA with latch arms (v0.3, after the print test).

Print-orientation check on the exported STLs: lid has no overhangs >45°; body's largest is the 11 mm bridge over the port window (snap windows 9 mm, vents 3 mm); feet print counterbore-up (fit them turned over).

## Hardware

4 × M4 × 10 button head (ISO 7380, Ø7 head) for the feet, straight into the body's 4 mm holes, no inserts. DIN bracket instead of feet: 4 × M3 × 20 into 4 × M3 × 5.7 heat-set inserts (not yet changed for M4). Nothing for the boards; the Duo kit's standoffs and screws aren't used.

## Files

| File | Purpose |
|---|---|
| `pi5_case.scad` | parametric model. `part = body | body_asm | lid | lid_asm | retainer | retainer_asm | feet | din | din_asm | din_rail | assembly | info` (`body`/`lid` are print-oriented; `_asm` in place) |
| `render_all.sh` | renders STLs + `info/info.json` (+ a 3 mm-wall body for comparison) |
| `slice_all.py` | flattens PrusaSlicer vendor profiles (0.30 DRAFT and 0.20 SPEED), adds the eSun TPU FAST overrides, slices each job (per-job profile and extra CLI args) → `print_times.json`; G-code kept in `slice/` (not committed). Also writes the committed G-code to `gcode/`: the feet as complete individual objects (eSun TPU 95A @MK3S), and the v0.5 lid with 0.20/0.30 mm layer-height ranges (it exports a 3MF, adds `Prusa_Slicer_layer_config_ranges.xml`, and slices that) |
| `drawings.py` | 2D sections from the STLs (trimesh + shapely) → `drawings.json` |
| `dwglib.py` | drawing helpers shared by `drawings.py` and `sketch_lid5.py` (SVG view in mm, STL sections, clipping) |
| `sketch_lid5.py` | lid v0.5 sketches → `img/pi5_case_lid_v0.5_sketch_*.png` and `sketches.json` for the drawings page (sections of `stl/lid_asm.stl`, a third-angle orthographic sheet with hidden-line removal by ray casting, and an OpenSCAD preview; needs `xvfb-run` and Playwright). Run `python3 sketch_lid5.py [node_modules]` after `render_all.sh` |
| `build_page.py` | builds the review page HTML |
| `build_pdf.py` | prints the drawings page to an A4 PDF (Chromium via Playwright), adds 3D renders from the viewer, embeds the 4 print STLs as PDF attachments (qpdf), opens with the attachments panel. Needs `npm i @fontsource/ibm-plex-sans@5 @fontsource/ibm-plex-mono@5 @fontsource/saira-condensed@5 three@0.128.0`; run `python3 build_pdf.py <node_modules> [out.pdf]` |
| `build_viewer.py` | builds the 3D viewer page (three.js, STLs embedded) incl. the DIN bracket and a requirements summary |
| `gcode/` | ready-to-print G-code for the MK3S+ (written by `slice_all.py`): `pi5_case_lid_PLA.gcode` (v0.5 lid, Generic PLA, 0.20/0.30 mm layer ranges via a 3MF), `pi5_case_feet_x4_TPU_sequential.gcode` (v0.5 feet, slower eSun TPU 95A @MK3S preset, one at a time) |
| `print/` | **the files to print**: `pi5_case_body_PETG.stl`, `pi5_case_lid_PLA.stl`, `pi5_case_feet_x4_TPU.stl`, `pi5_case_din_bracket_PETG.stl` (binary, bed-oriented, regenerated by `render_all.sh`) and the design PDF `pi5_case_design.pdf` (v0.5, 13 Nov 2026, 19 pages, the four STLs embedded) |
| `img/` | 3D renders (from the viewer, saved by `build_pdf.py`), the Section A-A and latch drawings, and the lid v0.5 sketches and orthographic views |
| `img/photos/` | every image attached in the design chat (sketches, print photos, screw measurements), full resolution |
| `pi5_case.html`, `pi5_case_viewer.html` | the drawings page and 3D viewer, self-contained (open locally in a browser) |
| `info/info.json` | layout values echoed by the SCAD, read by the drawing, page and viewer builders |
| `stl/`, `drawings.json` (not committed) | intermediate renders the drawings are cut from; `render_all.sh` / `drawings.py` regenerate them |

Regenerate: `./render_all.sh && python3 slice_all.py && python3 drawings.py && python3 build_page.py && python3 build_viewer.py` (OpenSCAD 2021+, PrusaSlicer 2.7 CLI, Python trimesh/shapely/networkx/manifold3d).

## Other requests (verbatim)

1 Nov 2026, 11:02:

> Can you create an artifact to view the stl models in the browser?

1 Nov 2026, 11:24:

> Can you include a brief summary of my requirements in the artifact

3 Nov 2026, 11:48:

> Can you provide me the links to all the artefacts generated

4 Nov 2026, 14:21 (recipient address redacted here):

> Can you generate a pdf of the design shown in the artefact and embed the atlas as attachments in pdf? And the use the Gmail plugin to send the file to [work email]

("atlas" read as "STLs". The Gmail connector can't carry an attachment that size, so a draft was left in Gmail for the PDF to be attached by hand.)

8 Nov 2026, 08:14:

> Can you push this to GitHub

## Sources

- Waveshare PoE HAT (G): https://www.waveshare.com/poe-hat-g.htm?sku=27670
- CNX Software on the HAT (G): https://www.cnx-software.com/2024/07/10/waveshare-poe-hat-g-is-a-compact-25w-poe-hat-for-the-raspberry-pi-5/
- NVMe Base Duo kit contents: https://core-electronics.com.au/pimoroni-nvme-base-duo-for-raspberry-pi-5-pim704.html
- Duo assembly guide: https://www.digikey.com/en/maker/projects/getting-started-with-nvme-base-duo-for-raspberry-pi-5/abd48355265a4fca812d348726afbd05
- Duo review (ribbon blocks microSD): https://www.tomshardware.com/raspberry-pi/pimoroni-nvme-base-duo-review
- Pi 5 power button next to the USB-C: https://raspberry.tips/en/?p=10265
- Duo layout (slots side by side, FFC mid-edge): https://www.tomshardware.com/raspberry-pi/raspberry-pi-5-dual-nvme-ssd-board-doubles-the-storage-follows-new-pip-guidelines
- Pi 5 documents (mechanical drawing): https://pip.raspberrypi.com/categories/892-raspberry-pi-5
