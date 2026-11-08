# designing-stuff

Parametric 3D-print designs and slicer profiles, mostly OpenSCAD, mirrored from the claude.ai project *Designing stuff*.

Printer: Prusa i3 MK3S+ with a 0.4 nozzle. Materials: TPU (eSun eTPU-95A) first, PETG sometimes. Preference: functional over pretty, faster over perfect, no supports where possible.

| Folder | What | Status |
|---|---|---|
| [fishbone-braid-tool](fishbone-braid-tool) | Zigzag French/fishbone hair braiding tool in TPU, with a short test coupon | v0.2: coupon passed, full tool ready to print |
| [printer-profiles/esun-tpu95a-mk3s](printer-profiles/esun-tpu95a-mk3s) | PrusaSlicer filament presets for eSun TPU 95A: forum-safe and FAST | sliced, not printed |

## Layout

Each design is a self-contained folder:

- `README.md`: brief (verbatim), design notes, parameters, print settings and times, open questions
- `*.scad`: the parametric model
- `render_all.sh`, `slice_all.py`, `drawings.py`: regenerate STLs, G-code, times and images
- `stl/`, `gcode/`, `img/`: build outputs, committed so they can be printed straight from GitHub

Slicing scripts use the PrusaSlicer 2.7 CLI and read TPU presets from `printer-profiles/`.

## Workflow

Each design gets its own folder. Every change is committed and **pushed straight to `main`**: one commit per build, no feature branches, no waiting for sign-off. This repo-wide rule was set by the owner on 8 Nov 2026 and overrides any general "feature branch, check before merging" habit.
