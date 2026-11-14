// =====================================================================
//  TPU membrane button  -  v0.3 (compact)
//  One TPU part. The button face is a thin membrane printed as the first
//  2-3 layers on the bed; a stiff centre, a 45-degree cone backup stop and
//  the microswitch tunnel all grow up from it, so no supports are needed.
//
//  v0.3: compact. A 19 mm face on a 23 mm head with a 45-degree underside,
//  then a narrow stem that only hugs the plunger end of the switch (the
//  rest of the switch sticks out of the side). About a fifth of v0.2's
//  plastic. The no-shim mechanism below is unchanged.
//
//  v0.2: no shimming. The centre's face lands on the SWITCH'S OWN TOP FACE,
//  so the plunger always ends up `pl_stop` above flush whatever its real
//  height. A switch with 1.8-2.8 mm of plunger works unchanged. The
//  switch slides in from the side onto a solid floor (so the press loads
//  the floor, not snap ridges) and clicks onto two bumps in its mounting
//  hole.
//
//  Switch: Happ/Cherry D44X-style arcade microswitch (B.Lee, measured):
//  plunger at one end of the top face, NO/NC tabs out the far end,
//  COM out the bottom near the far end.
//
//  Modelled in PRINT orientation: z = 0 is the bed = the button's top face.
//  "Down" in use is +z here. All z features sit on 0.2 mm layer lines.
//
//  CLI:
//    openscad -D 'part="button"' -o stl/tpu_button.stl tpu_button.scad
//    openscad -D 'part="button"' -D 'membrane=0.4' -o stl/tpu_button_m04.stl tpu_button.scad
//    part = "button" | "switch" (reference body, print coords) | "body" | "boss" | "info"
// =====================================================================

part = "button";

/* [Membrane and centre] */
membrane = 0.6;    // 3 layers at 0.2 (first layer 0.2). 0.4 = 2 layers
gap_c    = 0.3;    // cavity above the membrane at the rim before the cone starts
r_rim    = 9.5;    // free membrane outer radius -> flexible face 19 mm
r_boss   = 4.5;    // stiff centre radius -> 9 mm (5 mm free ring)
R_out    = 11.5;   // head radius -> 23 mm
head_t   = 1.4;    // head rim thickness before its 45-degree underside starts
wall     = 1.6;    // stem walls around the switch tunnel
stem_x   = 8.5;    // stem ends here (+X); COM leaves the switch at ~9.7, outside it

/* [Travel] */
t_face   = 2.1;    // centre travel from rest until its face is level with the ceiling
pl_stop  = 0.2;    // recess in the face: the plunger stops this far above flush
stop_margin = 0.3; // cone backup stop lands this far after the face meets the switch
r_face   = 3.0;    // face that lands on the switch top
r_rec    = 2.0;    // recess over the plunger (plunger 2.7 wide, +/-0.65 position)

/* [Throat] */
r_throat = 3.5;    // hole through the ceiling for the face (clipped to the tunnel)
lip      = 0.8;    // ceiling thickness at the throat

/* [Switch: B.Lee arcade microswitch, measured 14 Nov 2026 from caliper photos (+/-0.3)] */
sw_L     = 27.8;   // body length, plunger end -> tab end (measured ~28)
sw_T     = 10.3;   // body thickness (not measured; Cherry D44X size)
sw_H     = 15.6;   // body height, bottom -> top face (measured ~15.6; D44X nominal 15.9)
pl_off   = 5.9;    // plunger centre from the plunger-end face (measured)
pl_d     = 2.7;    // plunger width (measured)
pl_free  = 2.2;    // plunger height above the top face at rest (measured)
pl_pt    = 1.57;   // pretravel max (Cherry D44X spec; B.Lee assumed similar). OT min 1.27
hole_x   = 2.4;    // mounting hole near the plunger end: from the end face (from photo)
hole_z   = 2.9;    //   ... and above the bottom face (from photo)

/* [Tunnel] */
c_y      = 0.15;   // side clearance per side (TPU pockets print slightly small)
c_end    = 0.2;    // clearance at the plunger end
c_z      = 0.3;    // switch rests on the floor; its top is this far below the ceiling (bridge sag takes some)
groove_w = 3.6;    // slot in the ceiling for the plunger to slide in under
bump_r   = 1.0;    // detent bumps on both side walls, into the mounting hole
bump_h   = 0.45;
base_clear = 3.6;  // floor under the switch; 3.6 lets it stand on a desk clear of the COM tab

$fn = 96;

// ---------------------------------------------------------------- derived
z_c0   = membrane + gap_c;                       // cone starts here at r_rim
z_fun  = z_c0 + (r_rim - r_throat);              // funnel bottom (top of throat lip)
z_ceil = z_fun + lip;                            // tunnel ceiling
face_travel = t_face + c_z;                      // travel until the face meets the switch top
stop   = face_travel + stop_margin;              // cone backup stop
z_bcyl = z_c0 + (r_rim - r_boss) - stop;         // boss cylinder -> cone (cone parallels the funnel)
z_tip  = z_ceil - t_face;                        // face at rest
z_fc   = z_bcyl + (r_boss - r_face);             // cone reaches r_face here, then straight down
z_sw_t = z_ceil + c_z;                           // switch top (resting on the floor)
z_sw_b = z_sw_t + sw_H;                          // floor
z_tot  = z_sw_b + base_clear;
px0    = -(pl_off + c_end);                      // end wall
pw     = sw_T / 2 + c_y;                         // tunnel half width
rest_gap = face_travel + pl_stop - pl_free;      // recess floor to plunger top at rest
pl_travel = pl_free - pl_stop;                   // plunger travel when the face lands

assert(z_bcyl > membrane + 0.5, "boss cylinder too short");
assert(z_fc <= z_tip, "face radius too big for the cone");
assert(r_face < r_throat - 0.3, "face would rub the throat");
assert(rest_gap >= 0.3, "plunger would be pressed at rest");
assert(pl_travel >= pl_pt, "plunger may not reach its click point");
assert(base_clear >= 2, "floor needs at least 2 mm under the switch");
assert(stem_x > hole_x - pl_off + 3, "stem too short for the detent bumps");

// ---------------------------------------------------------------- parts
module boss()
    difference() {
        rotate_extrude() polygon([[0, 0], [r_boss, 0], [r_boss, z_bcyl], [r_face, z_fc], [r_face, z_tip], [0, z_tip]]);
        translate([0, 0, z_tip - pl_stop]) cylinder(r = r_rec, h = pl_stop + 1);
    }

module cavity()      // free ring + funnel, above the membrane
    rotate_extrude() polygon([[0, membrane], [r_rim, membrane], [r_rim, z_c0],
                              [r_throat, z_fun], [0, z_fun]]);

module tunnel2d() translate([px0, -pw]) square([R_out + 5 - px0, 2 * pw]);

// outside: round head, 45-degree underside (keeps >= 2.5 mm outside the funnel), narrow stem
module shell() {
    cylinder(r = R_out, h = head_t);
    translate([0, 0, head_t - 0.01]) cylinder(r1 = R_out, r2 = 0.5, h = R_out - 0.5);
    translate([px0 - wall, -(pw + wall), 0])
        linear_extrude(z_tot) offset(r = 1) offset(delta = -1) square([stem_x - px0 + wall, 2 * (pw + wall)]);
}

module bumps()
    for (s = [-1, 1])
        translate([-pl_off + hole_x, s * (pw + bump_r - bump_h), z_sw_b - hole_z]) sphere(r = bump_r, $fn = 32);

module body() {
    difference() {
        shell();
        cavity();
        // throat through the lip
        translate([0, 0, z_fun - 0.01]) linear_extrude(lip + 0.02)
            intersection() { circle(r_throat); tunnel2d(); }
        // switch tunnel, open at +X
        translate([0, 0, z_ceil]) linear_extrude(z_sw_b - z_ceil) tunnel2d();
        // 45-degree lead-in on the floor's entry edge
        translate([stem_x, 0, z_sw_b]) rotate([90, 0, 0])
            linear_extrude(2 * pw, center = true) polygon([[0.01, -0.01], [-1, -0.01], [0.01, 1]]);
        // plunger slides in under the ceiling along this groove
        translate([0, -groove_w / 2, z_ceil - pl_free - 0.5]) cube([R_out + 5, groove_w, pl_free + 0.6]);
        // small chamfer on the bed edge (stops elephant's foot on the face)
        translate([0, 0, -0.01]) difference() {
            cylinder(r = R_out + 1, h = 0.51);
            cylinder(r1 = R_out - 0.5, r2 = R_out + 0.01, h = 0.51);
        }
    }
    bumps();
}

module button() { body(); boss(); }

// reference switch body in print coordinates, resting on the floor
module switch_ref() {
    translate([-pl_off, -sw_T / 2, z_sw_t]) cube([sw_L, sw_T, sw_H]);
    translate([0, 0, z_sw_t - pl_free]) cylinder(d = pl_d, h = pl_free + 0.01, $fn = 32);
}

module info() echo(str("INFO {",
    "\"version\":\"0.3\",\"membrane\":", membrane, ",\"r_rim\":", r_rim, ",\"r_boss\":", r_boss, ",\"R_out\":", R_out,
    ",\"t_face\":", t_face, ",\"face_travel\":", face_travel, ",\"stop\":", stop, ",\"pl_stop\":", pl_stop,
    ",\"rest_gap\":", rest_gap, ",\"pl_travel\":", pl_travel, ",\"r_face\":", r_face, ",\"r_rec\":", r_rec,
    ",\"r_throat\":", r_throat, ",\"lip\":", lip,
    ",\"z_c0\":", z_c0, ",\"z_fun\":", z_fun, ",\"z_ceil\":", z_ceil, ",\"z_bcyl\":", z_bcyl, ",\"z_fc\":", z_fc,
    ",\"z_tip\":", z_tip, ",\"z_sw_t\":", z_sw_t, ",\"z_sw_b\":", z_sw_b, ",\"z_tot\":", z_tot,
    ",\"px0\":", px0, ",\"pw\":", pw, ",\"c_z\":", c_z, ",\"floor_x\":", stem_x, ",\"groove_w\":", groove_w,
    ",\"hole\":[", hole_x, ",", hole_z, "],\"bump\":[", bump_r, ",", bump_h, "]",
    ",\"sw\":[", sw_L, ",", sw_T, ",", sw_H, "],\"pl\":[", pl_off, ",", pl_d, ",", pl_free, ",", pl_pt, "]",
    ",\"base_clear\":", base_clear, "}"));

if (part == "button") button();
else if (part == "switch") switch_ref();
else if (part == "body") body();      // checks only
else if (part == "boss") boss();      // checks only
else if (part == "info") { info(); cube(1); }
