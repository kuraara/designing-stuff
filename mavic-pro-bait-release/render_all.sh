#!/usr/bin/env bash
# Render STLs, info.json, previews, the horn sweep check and the drawings.
# Needs OpenSCAD 2021+, xvfb-run (PNG on a headless box), python3 + trimesh + manifold3d + matplotlib.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stl img _build
S=bait_release.scad
for p in tub lid horn ref_servo ref_holder ref_boards; do
  openscad -o stl/$p.stl -D "part=\"$p\"" $S &
done
openscad -o _build/horn_lock.stl -D 'part="horn_place"' -D 'horn_rot=0' $S &
openscad -o stl/ref_horn_locked.stl -D 'part="horn_place"' -D 'horn_rot=0' $S &   # in place, for the viewer
openscad -o _build/horn_open.stl -D 'part="horn_place"' -D 'horn_rot=-52.5' $S &
wait
openscad -o _build/info.echo -D 'part="info"' $S
sed -n 's/^ECHO: "INFO \(.*\)"$/\1/p' _build/info.echo | sed 's/\\"/"/g' | head -1 | python3 -m json.tool > info.json
cat info.json
# OpenSCAD 2021 writes ASCII STL; rewrite as binary
python3 -c "import trimesh,sys; [trimesh.load(f).export(f) for f in sys.argv[1:]]" stl/*.stl _build/*.stl
# assembly previews (lid off / on)
xvfb-run -a openscad -o img/assembly_open_top.png --imgsize=1400,1000 --colorscheme=Tomorrow \
  --camera=0,0,8,45,0,300,170 --projection=p -D 'part="assembly"' -D 'show_lid=false' $S
xvfb-run -a openscad -o img/assembly.png --imgsize=1400,1000 --colorscheme=Tomorrow \
  --camera=18,6,4,130,0,230,200 --projection=p -D 'part="assembly"' $S
python3 sweep_check.py
python3 drawings.py
