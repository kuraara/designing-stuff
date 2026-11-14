# Arcade Button Box

Research into self-contained wireless button boxes: arcade buttons + ESP32-C3 + a Li-ion cell. Started 30 Oct 2026 in the claude.ai project *Designing stuff*.

**3D:** [2×2 tub, cut through the battery bay](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/stl/2x2_tub.stl&cut=x&at=500) · [2×3 top plate](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/stl/2x3_plate.stl) · [TPU button with its switch](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/tpu-membrane-button/stl/tpu_button.stl&m=arcade-button-box/tpu-membrane-button/stl/ref_microswitch.stl&cut=y&at=500&flip=1) · all STLs in the [viewer](https://kuraara.github.io/designing-stuff/?d=arcade-button-box)

| Piece | What | Status |
|---|---|---|
| Enclosure v0.1 (this folder) | Printed tub + removable top plate for long-barrel screw-in buttons, six layouts 1×1 to 2×3, dimensioned 2D drawings in `arcade_button_box.html` | designed, not printed |
| [notes/off-the-shelf-enclosures.md](notes/off-the-shelf-enclosures.md) | Jaycar / Amazon AU boxes deep enough for the long buttons | research |
| [notes/button-options.md](notes/button-options.md) | Lower-profile button options and the TPU membrane idea, with depth comparison | research |
| [tpu-membrane-button](tpu-membrane-button) | Single all-TPU membrane button holding the existing microswitch: box depth ~34 mm instead of ~94 | **v0.2 printing** (no shims) |

## Requests (verbatim)

30 Oct 2026, 14:37: the original brief, below.

30 Oct 2026, 17:08:

> Instead of printing the whole thing, can you find some ready to go boxes  on Amazon or Jaycar

31 Oct 2026, 09:17:

> What other button options are there? Would a membrane button made from tpu that  actuates the microswitches lower the depth?

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

14 Nov 2026, 16:59: screenshot of the microswitch in use (B.Lee, austinamusements.com.au "Bulk Buy- 100 x Microswitch For Arcade Buttons"). 17:10: three caliper photos of it.

14 Nov 2026, 17:30:

> Redo the design so I don’t need to tape anything

14 Nov 2026, 17:41:

> Okay just give me the one you did and I’ll print it anyway

Details in [tpu-membrane-button/README.md](tpu-membrane-button/README.md).

---

# Enclosure v0.1

## Original brief (verbatim, 30 Oct 2026, 14:37)

> I’ve got a heap of IS style arcade cabinet buttons(78mm deep I believe) and micro switches.
>
> Let’s put together some designs for self contained boxes that house the buttons, an esp32 c3 and some sort of power source 1-2x 18650/21700, charge controller.
>
> - Consider various button arrangements: 1x1, 1x2, 1x3,1x4, 2x2, 2x3
>
> - Factor in the spacing needed around the buttons to thread the bottom screw in, running wire from the micro switches etc. ie don’t make the box too small
>
> - Initial designs, create as 2d projections. 3d rendering isn’t terribly important
>
> - if possible, include estimated print times on 0.3mm draft (0.4mm nozzle)  with PLA and PETG

Printer: Prusa i3 MK3S+. Project preference: functional over pretty, faster over perfect; TPU/PETG preferred.

## Architecture

| Part | Print orientation | Holds |
|---|---|---|
| **Tub** (floor + walls) | floor on bed | battery holder on floor rails + corner fences; USB-C cut-outs and KCD11 rocker in back wall; hanging M3 insert posts (45° underside); free-standing centre posts on 2-row layouts; feet recesses |
| **Top plate** | top face on bed | buttons (Ø29 holes); TP4056 + ESP32-C3 in pockets on the underside, component side down, USB ends at the back wall; perimeter locating lip (interrupted at posts); countersunk M3 holes |
| Fit coupon | flat | button hole, insert post, csk M3, USB-C cut-out, rocker cut-out — print first |
| Feet ×4 | flat, TPU | Ø12 × 3 discs into 1 mm recesses |

Why a removable top plate: with a fixed lid and an open bottom, the button nuts sit ~85 mm deep inside the box and can't be reached. With the plate removable, buttons and nuts go on at the bench. Putting both PCBs on the plate means the only plate↔tub harness is the battery lead (JST-PH) plus the rocker pair. **No supports on any part.**

Coordinates in the SCAD: origin = tub outer front-left-bottom; X along columns, Y front→back, Z up. Bay is along the back wall.

## Key numbers (all parameters in `button_box.scad`)

| Parameter | Default | Basis |
|---|---|---|
| `pitch` | 50 | 38 mm nut + 12 mm finger/wire gap |
| `edge` | 28 | button centre → inner wall (nut r19 + 9) |
| `btn_hole_d` | 29.0 | 1-1/8" (28.6) + FDM undersize allowance — verify with coupon |
| `btn_nut_d` | 38 | **assumed — measure** |
| `btn_depth` | 78 | underside of bezel → tips of microswitch tabs. **User's estimate — measure** |
| `conn_clear` | 14 | straight .187" spades + wire bend (6 for flag spades → box 8 mm lower) |
| `plate_t` / `wall` / `floor_t` | 4 / 2.4 / 2.4 | |
| inner height `Hi` | 88 | `btn_depth − plate_t + conn_clear` |
| `bay_d` | 30 | 21700 holder 24 wide + 6 (18650 holder fits too). `cells=2` → 52 |
| min inner length | 95 | 83 mm holder + 2 × 6 lead clearance (makes 1×1 wider than its button) |
| `usb_cut` | 12.5 × 7 | cable overmold clearance so plug seats fully |
| `rocker_cut` | 15.2 × 10.2 | KCD11 mini rocker |
| `standoff` | 4 | plate underside → PCB back (3 mm rails + 1 mm foam tape) |
| centre posts | rows ≥ 2 | Ø10, floor to plate, M3 insert — stiffens plate under hard presses |
| mid posts | `Xi > 170` | long walls (1×4 only) |

## Layouts and print times

PrusaSlicer 2.7.2, stock *Original Prusa i3 MK3S & MK3S+* printer, *0.30mm DRAFT @MK3* print profile (2 perimeters, 15 % grid), *Generic PLA* / *Generic PETG*. Box total = tub + plate.

| Layout | Outside W×D×H (assembled) | Inside | Screws | Tub PLA | Plate PLA | **Total PLA** | Tub PETG | Plate PETG | **Total PETG** | Filament (PLA) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1×1 | 99.8 × 90.8 × 94.4 | 95 × 86 × 88 | 4 | 4h 35m | 1h 25m | **6h 00m** | 4h 51m | 1h 31m | **6h 22m** | 148 g |
| 1×2 | 110.8 × 90.8 × 94.4 | 106 × 86 × 88 | 4 | 4h 54m | 1h 30m | **6h 25m** | 5h 12m | 1h 36m | **6h 48m** | 157 g |
| 1×3 | 160.8 × 90.8 × 94.4 | 156 × 86 × 88 | 4 | 6h 14m | 2h 03m | **8h 17m** | 6h 38m | 2h 12m | **8h 49m** | 206 g |
| 1×4 | 210.8 × 90.8 × 94.4 | 206 × 86 × 88 | 6 | 7h 49m | 2h 38m | **10h 26m** | 8h 18m | 2h 49m | **11h 07m** | 258 g |
| 2×2 | 110.8 × 140.8 × 94.4 | 106 × 136 × 88 | 5 | 6h 43m | 2h 08m | **8h 51m** | 7h 07m | 2h 16m | **9h 23m** | 215 g |
| 2×3 | 160.8 × 140.8 × 94.4 | 156 × 136 × 88 | 6 | 8h 39m | 2h 57m | **11h 36m** | 9h 11m | 3h 09m | **12h 20m** | 280 g |

Fit coupon: 34m PLA / 39m PETG. TPU feet (set of 4, Generic FLEX): 16m.
All parts fit the MK3S+ bed (largest: 1×4 at 210.8 × 90.8).

Speed lever: `wall = floor_t = 1.6` took the 2×2 tub from 6h 43m to 5h 38m (PLA). 2.0 gave 6h 25m. Height (driven by `btn_depth`) is the main cost.

## Electronics

```
cell ─ B+/B− ─[TP4056 USB-C w/ DW01]─ OUT+ ─[KCD11 rocker]─ 5V ─[ESP32-C3 Super Mini]
                                     OUT− ─────────────────── GND
OUT+ ─ 100k ─┬─ 100k ─ GND   (tap → GPIO4, ADC1)
```

- Charges with the rocker off. Switch off for clean charge termination.
- Super Mini 3V3 LDO from the 5V pin works down to roughly a 3.5 V cell. Remove the red power LED for deep sleep.
- Solder wires straight to pads (boards mount component-side down; header pins would hit the plate).

| Signal | GPIO | Note |
|---|---|---|
| B1 | 0 | deep-sleep wake |
| B2 | 1 | wake |
| B3 | 3 | wake |
| B4 | 5 | wake |
| B5 | 2 | wake; strapping pin — don't hold at reset |
| B6 | 6 | no deep-sleep wake (light sleep OK) |
| VBAT | 4 | ADC1 via divider |
| LED | 8 | onboard |

C3 constraints: deep-sleep GPIO wake only on GPIO0–5; reliable ADC (ADC1) only on GPIO0–4; strapping pins 2, 8, 9.

## Assembly order

1. Print the fit coupon; check button fit, insert, USB-C plug seating, rocker snap. Adjust `btn_hole_d`, `insert_d`, `usb_cut` before the big prints.
2. Heat-set M3 × 5.7 inserts into all posts.
3. Buttons + nuts + microswitches onto the plate at the bench.
4. Foam tape on pocket rails; press in TP4056 and ESP32 (USB ends against back stops).
5. Wire switches: COM daisy-chain to GND, NO to GPIOs.
6. Battery holder on floor rails between fences; zip tie under it between the rails or foam tape. JST-PH lead to TP4056.
7. Rocker into back wall from outside.
8. Drop plate on (lip locates), M3 × 8 countersunk screws.

## Hardware per box

4–6 × M3 × 8 csk + M3 × 5.7 heat-set inserts · ESP32-C3 Super Mini · TP4056 USB-C module with protection · KCD11 rocker · 1 × 21700/18650 holder with leads · JST-PH 2-pin pair · .187" female spades (2/button) · 24–26 AWG wire · 1 mm foam tape · 4 feet.

## Open questions / to verify

- **Button depth** — confirm 78 mm and what it's measured from (design assumes bezel underside → tab tips).
- **Nut OD** — 38 assumed.
- "IS style" taken to mean Happ/iL-style long-barrel screw-in with removable microswitch, 28 mm hole.
- Straight or flag spades (`conn_clear`).
- TP4056 module length varies 26–28 mm; pocket is 28.
- Firmware scope (BLE HID? Home Assistant/ESPHome?) not yet defined.

## Files

| File | Purpose |
|---|---|
| `button_box.scad` | parametric model. `part = tub / plate / plate_asm / coupon / feet / assembly / info` |
| `render_all.sh` | renders all six layouts' STLs + `info/*.json` |
| `slice_all.py` | flattens PrusaSlicer vendor profiles and slices everything → `print_times.json` |
| `drawings.py` | 2D sections from the STLs (trimesh) → `drawings.json` (not committed) |
| `build_page.py` | builds `arcade_button_box.html`, the drawing page (open it in a browser) |
| `stl/` | tub, plate (print orientation), plate_asm (assembly orientation, drawings only), coupon, feet |
| `img/` | OpenSCAD previews of the 2×3 |
| `notes/` | off-the-shelf box shortlist, button options |

Regenerate: `./render_all.sh && python3 slice_all.py && python3 drawings.py && python3 build_page.py` (needs OpenSCAD 2021+, PrusaSlicer 2.7 CLI, Python trimesh/shapely/networkx).

## Ideas for v0.2

- TPU corner bumpers or a TPU sleeve for drop protection / grip.
- Cable-tie anchors on the plate underside.
- Light pipe for TP4056 charge LEDs (they face down at present).
- Firmware: ESPHome or NimBLE HID with deep-sleep wake on GPIO0–5.
