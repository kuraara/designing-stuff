# Button options and low-profile study (31 Oct 2026)

User asked (verbatim): "What other button options are there? Would a membrane button made from tpu that  actuates the microswitches lower the depth?"

## Depth comparison

Depth = top surface of the panel → lowest point of the switch/wiring. Box height adds ~2.4 mm floor and wire/spade clearance.

| Option | Depth below panel top | Approx. box height | Notes |
|---|---|---|---|
| Current long-barrel Happ/iL screw-in, straight spades | 78 + 14 | ~94 | baseline v0.1 design |
| Same, flag spades or soldered wires | 78 + ~6 | ~86 | `conn_clear = 6` |
| Snap-in 30 mm (Sanwa OBSF-30 and clones) | ~35.5 install depth | ~43 | 30 mm hole, 2–4 mm panel, 55 g, 2.53 mm travel, operates at 0.85 mm |
| Snap-in 24 mm (generic) | 33.8 overall | ~40 | AU stock at arcade-game-sales.com |
| **Existing D44X microswitches under printed caps (TPU membrane or PETG plunger)** | ~31 | **~36** | switch body 16 tall + ~8 mm tabs is the floor on height |
| Cherry MX + printed 30 mm caps | ~8 below plate | ~28–30 (battery-limited) | 21700 holder (22 tall) becomes the tallest part |
| Kailh Choc v1 low profile (Slimbox 2040 / Flatbox style) | ~5 below plate | ~28–30 with 21700; ~15–20 with flat LiPo pouch | 50 g at 1.5 mm, 3 mm travel |

## TPU membrane over existing microswitches — stack estimate

PETG frame 3 · TPU flange 1 (clamped under frame) · ~2 mm to switch operating point · D44X body 15.9 · .187 tabs ~8 · solder/flag spade ~4 · floor 2.4 → **~36 mm** vs 94 mm.

Switch: Cherry D44X (D449-R1AA-CF), 75 g, .187" tabs, V-size body ~27.8 × 15.9 × 10.3 (same family as Omron V). V-type pin-plunger overtravel is only ~1 mm → **needs a hard stop**.

Design rules:
- Pad centre must be stiff (thick solid TPU or a PETG insert) or off-centre presses tilt it and miss the switch pin.
- Hard stop collar so the pad lands on plastic just after the click.
- Hang the switches from the top plate (screwed/clipped to bosses) so actuation height depends on one part only.
- ~2 mm total travel, click at ~1 mm (comparable to Sanwa's 2.53 / 0.85).
- Click comes from the switch; return = switch spring (~75 g) + TPU skirt.
- Flat-printed TPU flexures bend within layers (not peeling them apart). Keep strain low (short travel, 45° skirt, 0.8 mm wall) to limit creep.
- No nuts to spin → pitch can drop from 50 to ~42–44 mm.
- Inside height ~31: 21700 holder on 4 mm rails leaves ~5 mm above it, so boards move beside the battery instead of over it.

## Print-time check (2×2, crude models, PrusaSlicer 2.7 stock MK3S+ 0.30 DRAFT)

| Part | Time | Filament |
|---|---|---|
| Tub at full height (90.4) — PLA | 6h 43m | 171 g |
| Tub at 33.4 tall — PLA | 3h 57m | 89 g |
| One-piece TPU mat (full plate area, 1 mm sheet + 4 domes) — Generic FLEX | 5h 58m | 36 g |
| 4 separate TPU caps (Ø48 flange) — Generic FLEX | 3h 07m | 19 g |

Generic FLEX caps flow at 1.2 mm³/s, so real TPU times with tuned settings will be shorter.

## Variants to carry forward

- **A. One-piece TPU mat**: sealed against dust/drinks, one part, slowest print, softest feel.
- **B. Separate TPU caps under a PETG frame**: individually replaceable, half the TPU time.
- **C. Rigid PETG plunger in a guide bore**: switch spring returns it; fastest print, closest to arcade feel, not sealed.

Status: discussion only, no model yet.
