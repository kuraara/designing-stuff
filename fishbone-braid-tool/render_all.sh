#!/usr/bin/env bash
# Render STLs, info.json and a 3D preview PNG. Needs OpenSCAD 2021+ (xvfb-run for the PNG on a headless box).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stl img
openscad -o stl/braid_tool.stl   -D 'part="tool"'   braid_tool.scad
openscad -o stl/braid_coupon.stl -D 'part="coupon"' braid_tool.scad
openscad -o /tmp/braid_info.echo -D 'part="info"' braid_tool.scad
sed -n 's/^ECHO: "INFO \(.*\)"$/\1/p' /tmp/braid_info.echo | head -1 > info.json
cat info.json
# 3D preview (STL imported so it's quick)
echo 'color("#3b6ea5") import("stl/braid_tool.stl");' > _view.scad
${XVFB:-xvfb-run -a} openscad -o img/braid_tool_3d.png --imgsize=1400,900 --colorscheme=Tomorrow \
  --camera=0,95,2,55,0,35,360 --projection=p _view.scad
rm -f _view.scad
# OpenSCAD 2021 writes ASCII STL (~7 MB); rewrite as binary (~1.5 MB)
python3 -c "import trimesh,sys; [trimesh.load(f).export(f) for f in sys.argv[1:]]" stl/braid_tool.stl stl/braid_coupon.stl
