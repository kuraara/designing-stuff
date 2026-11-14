# Off-the-shelf enclosure options (30 Oct 2026)

User asked (verbatim): "Instead of printing the whole thing, can you find some ready to go boxes  on Amazon or Jaycar"

## Depth requirement

Buttons are ~78 mm from the top face of the lid to the microswitch tab tips, so with a ~3 mm lid:

| Spade type | Inside height needed (lid underside → floor) | Roughly this outside height |
|---|---|---|
| Straight .187" spades + wire bend | ~89 mm | ~95 mm |
| Flag (right-angle) spades | ~81 mm | ~87 mm |

Footprint needs (inside, 50 mm pitch, from the printed design): 1×2 106 × 86 · 1×3 156 × 86 · 1×4 206 × 86 · 2×2 106 × 136 · 2×3 156 × 136. A bought box doesn't need the dedicated rear bay if the battery fits beside the buttons.

## Jaycar (AU)

| Code | Outside | Price | Fits | Notes |
|---|---|---|---|---|
| HB6134 Sealed ABS enclosure | 240 × 160 × 90 | $41.95 | Any layout up to 2×3 / 1×4 | Only Jaycar box deep enough, and only with flag spades (inside height est. ~84). 6 × M4 lid screws into brass inserts, internal posts and PCB slots, IP65, dark grey. |
| HB6223 / HB6224 polycarbonate | 171 × 121 × 80 | $31.50 (HB6223) | — | Too shallow (~74 inside) unless a printed riser ring goes between lid and base. |
| HB6132 Sealed ABS | 222 × 146 × 75 | $33.50 | — | Too shallow. |

## Amazon AU

Listings found; Amazon blocks automated page reads, so prices and inside heights are unverified.

| Listing | Outside | Fits |
|---|---|---|
| uxcell 200 × 150 × 100 IP65 junction box (B06ZYMXWZB) | 200 × 150 × 100 | 2×3, 2×2, 1×3; 1×4 only with pitch cut to ~45 |
| uxcell 200 × 150 × 100 IP67 (B07CN4HYN5) | 200 × 150 × 100 | same |
| MASO 150 × 200 × 100 IP65 ABS (B07KS15STX) | 150 × 200 × 100 | same |
| 150 × 200 × 130 IP65 ABS, white (B07PF8LYT3) | 150 × 200 × 130 | same; plenty of depth for straight spades |
| 100 × 150 × 90 IP67 hinged (B0GSLZ449V) | 100 × 150 × 90 | 1×1, 1×2 (flag spades) |

## Things to check on any bought box

- Inside height, including the lid's own depth.
- Ribs or a gasket groove on the lid underside: keep button holes clear of them (~15 mm in from the edge).
- 1-1/8" (28.6 mm) hole saw or step drill for the lid; 3 mm ABS lid is fine for long-barrel buttons.
- Lid screws are usually on top in the corners.

## Hybrid plan (not yet started)

Buy the box; print only (a) a drill template for the lid and (b) a battery cradle + board carrier that screws to the box's internal posts. Expected well under 1 h of printing vs 6–12 h for the full printed box.
