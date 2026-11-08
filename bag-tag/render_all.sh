#!/usr/bin/env bash
# Build the AUBREY example: STLs, previews, info.json, then the drawings.
# Needs python3 + numpy + manifold3d + shapely + fontTools, OpenSCAD 2021+, xvfb-run, rsvg-convert.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf _build && mkdir -p stl img
python3 bag_tag.py --name AUBREY --png --out _build --stem aubrey
mv _build/aubrey_base.stl _build/aubrey_inlay.stl stl/
mv _build/aubrey_preview.svg _build/aubrey_preview.png img/
mv _build/aubrey_info.json info.json
rm -rf _build
python3 drawings.py
