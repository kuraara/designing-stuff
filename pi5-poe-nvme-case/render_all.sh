#!/bin/bash
# Renders every part to stl/ and dumps the layout info JSON to info/info.json
# Needs OpenSCAD 2021+.
cd "$(dirname "$0")"; mkdir -p stl info
openscad -D 'part="info"' -o /tmp/_pi5_info.stl pi5_case.scad 2>&1 | sed -n 's/^ECHO: "INFO\(.*\)"$/\1/p' > info/info.json
for P in body body_asm lid lid_asm feet din din_asm din_rail; do
  openscad -D "part=\"$P\"" -o stl/$P.stl pi5_case.scad >/dev/null 2>&1 && echo "done $P" &
done
# comparison: the same body with 3 mm walls / floor / roof / end
openscad -D 'part="body"' -D wall=3 -D floor_t=3 -D roof_t=3 -D end_t=3 -o stl/body_wall3.stl pi5_case.scad >/dev/null 2>&1 && echo "done body_wall3" &
wait
# bed-ready binary copies with descriptive names: these are the files to print (committed in print/)
mkdir -p print
python3 - <<'PY'
import trimesh
for src, dst in [("body", "pi5_case_body_PETG"), ("lid", "pi5_case_lid_TPU"),
                 ("feet", "pi5_case_feet_x4_TPU"), ("din", "pi5_case_din_bracket_PETG")]:
    m = trimesh.load(f"stl/{src}.stl")
    m.apply_translation(-m.bounds[0])
    m.export(f"print/{dst}.stl")
    print("print/" + dst + ".stl")
PY
