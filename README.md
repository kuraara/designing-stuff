# designing-stuff

Parametric 3D-print designs and slicer profiles, mostly OpenSCAD, mirrored from the claude.ai project *Designing stuff*.

Printer: Prusa i3 MK3S+ with a 0.4 nozzle. Materials: TPU (eSun eTPU-95A) first, PETG sometimes. Preference: functional over pretty, faster over perfect, no supports where possible.

| Folder | What | Status | 3D |
|---|---|---|---|
| [fishbone-braid-tool](fishbone-braid-tool) | Zigzag French/fishbone hair braiding tool in TPU, with a short test coupon | v0.2: coupon passed, full tool ready to print | [view](https://kuraara.github.io/designing-stuff/?m=fishbone-braid-tool/stl/braid_tool.stl) |
| [bag-tag](bag-tag) | Name + flower bag tag as a two-colour press-fit inlay for a single-extruder printer; parametric name, font and size, with a 1–4 s generator script (basis of the shiny-trinkets Bag Tag gadget) | v0.1: STLs and G-code ready, not printed | [view](https://kuraara.github.io/designing-stuff/?m=bag-tag/stl/aubrey_base.stl&m=bag-tag/stl/aubrey_inlay.stl) |
| [pi5-poe-nvme-case](pi5-poe-nvme-case) | Slide-in Raspberry Pi 5 case for the Waveshare PoE HAT (G) and Pimoroni NVMe Base Duo, no screws into the boards, plus a DIN rail bracket | v0.2: body printed in PLA (10 Nov), printed fine; lid, feet, bracket not yet | [view](https://kuraara.github.io/designing-stuff/?m=pi5-poe-nvme-case/print/pi5_case_body_PETG.stl) |
| [arcade-button-box](arcade-button-box) | Wireless ESP32-C3 arcade button boxes: printed enclosure study (6 layouts), off-the-shelf box and button research, and an all-TPU membrane button that holds the arcade microswitch | enclosure v0.1 not printed; TPU button v0.2 printing | [view](https://kuraara.github.io/designing-stuff/?m=arcade-button-box/tpu-membrane-button/stl/tpu_button.stl&m=arcade-button-box/tpu-membrane-button/stl/ref_microswitch.stl&cut=y&at=500&flip=1) |
| [printer-profiles/esun-tpu95a-mk3s](printer-profiles/esun-tpu95a-mk3s) | PrusaSlicer filament presets for eSun TPU 95A: forum-safe and FAST | sliced, not printed |  |

## 3D viewer

**https://kuraara.github.io/designing-stuff/** shows every STL in the repo in a proper 3D viewer (three.js): orbit, pan and zoom; section cuts on X, Y or Z with the cut faces shaded; overhangs steeper than 45° in red; two-point measuring; the MK3S+ bed (250 × 210, 10 mm grid) for scale; parts overlaid in different colours; and a *Copy link* button for the current view. It works on a phone.

Links into it:

| Query | Does |
|---|---|
| `?m=<path/to.stl>` | open that STL; repeat `m=` to overlay parts |
| `&cut=x`/`y`/`z&at=0–1000` | section plane and where it sits across the part (500 = middle); `&side=1` shows the other half |
| `&flip=1` | turn the part over (print orientation ↔ use orientation) |
| `&over=1` | colour overhangs |
| `?d=<folder>` | a design's first STL |

The page is `index.html` at the repo root. Its model list is `viewer/models.json`: rebuild it with `python3 viewer/build_index.py` whenever STLs are added or change. `ref_*.stl` files are reference bodies (drawn see-through, not for printing). `.nojekyll` makes Pages serve the files as they are.

**One-time setup (owner):** Settings → Pages → *Build and deployment* → Source: **Deploy from a branch**, Branch: **main**, folder **/ (root)** → Save. The site appears at the address above a minute or so later.

## Layout

Each design is a self-contained folder:

- `README.md`: brief (verbatim), design notes, parameters, print settings and times, open questions
- `*.scad`: the parametric model
- `render_all.sh`, `slice_all.py`, `drawings.py`: regenerate STLs, G-code, times and images
- `stl/`, `gcode/`, `img/`: build outputs, committed so they can be printed straight from GitHub and viewed in the 3D viewer (pi5-poe-nvme-case keeps its printable STLs in `print/` and ready-to-print G-code in `gcode/`)

Slicing scripts use the PrusaSlicer 2.7 CLI and read TPU presets from `printer-profiles/`.

## Workflow

Each design gets its own folder. Every change is committed and **pushed straight to `main`**: one commit per build, no feature branches, no waiting for sign-off. This repo-wide rule was set by the owner on 8 Nov 2026 and overrides any general "feature branch, check before merging" habit.
