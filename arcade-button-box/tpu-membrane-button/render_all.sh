#!/usr/bin/env bash
# Render STLs + info.json. Needs OpenSCAD 2021+.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stl
openscad -o stl/tpu_button.stl     -D 'part="button"'                    tpu_button.scad   # 3-layer membrane (0.6)
openscad -o stl/tpu_button_m04.stl -D 'part="button"' -D 'membrane=0.4' tpu_button.scad   # 2-layer membrane (0.4)
openscad -o /tmp/tpu_button_info.echo -D 'part="info"' tpu_button.scad
sed -n 's/^ECHO: "INFO \(.*\)"$/\1/p' /tmp/tpu_button_info.echo | head -1 > info.json
python3 -c "import trimesh,sys; [trimesh.load(f).export(f) for f in sys.argv[1:]]" stl/*.stl   # binary STL
python3 check_overhangs.py stl/tpu_button.stl
