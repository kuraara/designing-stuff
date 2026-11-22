#!/usr/bin/env bash
# Build both bumpers (Aubrey, Lincoln), the three fit rings, previews and info.json, then the drawings.
# Needs python3 + numpy + manifold3d (+ fontTools), OpenSCAD 2021+, xvfb-run; trimesh, shapely and
# matplotlib for drawings.py.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf _build && mkdir -p stl img _build
for n in Aubrey Lincoln; do
  python3 bumper.py --name "$n" --png --out _build
done
mv _build/*_bumper.stl stl/
mv _build/*_bumper.png img/
python3 - <<'PY'
import json, pathlib
b = pathlib.Path("_build")
info = {p.stem.replace("_info", ""): json.loads(p.read_text()) for p in sorted(b.glob("*_info.json"))}
pathlib.Path("info.json").write_text(json.dumps(info, indent=1))
PY
# fit rings: one STL each (vase mode prints one object at a time); 1, 2, 3 lugs = fit 2.2 / 1.6 / 1.0
rm -f stl/fit_ring_*.stl
i=1
for tag in tight default loose; do
  openscad -o "stl/fit_ring_${i}_${tag}.stl" -D 'part="ring"' -D "ring=$i" bumper.scad
  i=$((i + 1))
done
python3 -c "import trimesh,sys; [trimesh.load(f).export(f) for f in sys.argv[1:]]" stl/fit_ring_*.stl
# preview of all three rings together
openscad -o _build/gauge.stl -D 'part="gauge"' bumper.scad
echo 'color("#58b4e8") import("_build/gauge.stl");' > _view.scad
${XVFB:-xvfb-run -a} openscad -o img/fit_rings.png --imgsize=1000,900 --colorscheme=Tomorrow \
  --camera=0,-4,0,30,0,0,400 --projection=p _view.scad
rm -f _view.scad
rm -rf _build
python3 drawings.py
