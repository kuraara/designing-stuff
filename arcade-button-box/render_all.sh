#!/bin/bash
# Renders every layout's parts to stl/ and dumps layout info JSON to info/
cd "$(dirname "$0")"; mkdir -p stl info
jobs=()
for L in 1x1 1x2 1x3 1x4 2x2 2x3; do
  R=${L%x*}; C=${L#*x}
  for P in tub plate plate_asm; do jobs+=("$C $R $P $L"); done
  openscad -D "cols=$C" -D "rows=$R" -D 'part="info"' -o /tmp/_i_$L.stl button_box.scad 2>&1 | sed -n 's/^ECHO: "INFO\(.*\)"$/\1/p' > info/$L.json
done
printf '%s\n' "${jobs[@]}" | xargs -P 2 -L 1 bash -c 'openscad -D "cols=$0" -D "rows=$1" -D "part=\"$2\"" -o stl/$3_$2.stl button_box.scad >/dev/null 2>&1 && echo done $3 $2'
openscad -D 'part="coupon"' -o stl/fit_coupon.stl button_box.scad >/dev/null 2>&1 && echo done coupon
openscad -D 'part="feet"'   -o stl/feet_tpu.stl  button_box.scad >/dev/null 2>&1 && echo done feet
