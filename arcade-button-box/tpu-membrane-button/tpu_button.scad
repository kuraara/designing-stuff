// =====================================================================
//  TPU membrane arcade button  -  v0.1 mock
//  One TPU part. The button face is a thin membrane printed as the first
//  2-3 layers on the bed; a stiff centre boss, a 45-degree cone stop and
//  the microswitch pocket all grow up from it, so no supports are needed.
//
//  Switch: Happ/Cherry D44X-style arcade microswitch (B.Lee, measured):
//  plunger at one end of the top face, NO/NC tabs out the far end,
//  COM out the bottom near the far end. The switch is pushed in from the
//  underside, plunger end first; its tab end sticks out of the side.
//
//  Modelled in PRINT orientation: z = 0 is the bed = the button's top face.
//  "Down" in use is +z here.
//
//  CLI:
//    openscad -D 'part="button"' -o stl/tpu_button.stl tpu_button.scad
//    openscad -D 'part="button"' -D 'membrane=0.4' -o stl/tpu_button_m04.stl tpu_button.scad
//    part = "button" | "switch" (reference body, print coords) | "info"
// =====================================================================

part = "button";

/* [Membrane and centre] */
membrane = 0.6;    // 3 layers at 0.2 (first layer 0.2). 0.4 = 2 layers
gap_c    = 0.3;    // cavity above the membrane at the rim before the cone starts
r_rim    = 14.5;   // free membrane outer radius -> flexible face 29 mm
r_boss   = 9.0;    // stiff centre radius -> 18 mm
R_out    = 18.0;   // puck radius -> 36 mm

/* [Travel] */
stop     = 2.2;    // centre travel until the cone lands on its seat
gap0     = 0.2;    // air gap between boss tip and switch plunger at rest

/* [Throat] */
r_throat = 4.0;    // hole through the ceiling for the boss tip (clipped to the pocket)
lip      = 0.8;    // ceiling thickness at the throat

/* [Switch: B.Lee arcade microswitch, measured 14 Nov 2026 from caliper photos (+/-0.3)] */
sw_L     = 27.8;   // body length, plunger end -> tab end (measured ~28)
sw_T     = 10.3;   // body thickness (not measured; Cherry D44X size)
sw_H     = 15.6;   // body height, bottom -> top face (measured ~15.6; D44X nominal 15.9)
pl_off   = 5.9;    // plunger centre from the plunger-end face (measured)
pl_d     = 2.7;    // plunger width (measured)
pl_free  = 2.2;    // plunger height above the top face at rest (measured: 17.8 overall - 15.6)
pl_pt    = 1.57;   // pretravel max (Cherry D44X spec; B.Lee assumed similar). OT min 1.27

/* [Pocket] */
c_y      = 0.15;   // side clearance per side (TPU pockets print slightly small)
c_end    = 0.2;    // clearance at the plunger end
ridge    = 0.6;    // snap ridge under the switch's bottom edges (set 0.1 below sw_H:
                   // a taller switch just squeezes the TPU ridge, a shorter one would drop)
ridge_x  = [-2, 12];
base_clear = 6;    // below the switch, so COM clears the desk; 0 for panel use

$fn = 96;

// ---------------------------------------------------------------- derived
z_c0   = membrane + gap_c;                       // cone starts here at r_rim
z_fun  = z_c0 + (r_rim - r_throat);              // funnel bottom (top of throat lip)
z_ceil = z_fun + lip;                            // switch top face sits here
z_bcyl = z_c0 + (r_rim - r_boss) - stop;         // boss cylinder -> cone
z_tip  = z_ceil - pl_free - gap0;                // boss tip face at rest
r_tip  = r_boss - (z_tip - z_bcyl);              // tip face radius
z_sw_b = z_ceil + sw_H;                          // switch bottom face
z_tot  = z_sw_b + base_clear;
px0    = -(pl_off + c_end);                      // pocket wall at the plunger end
pw     = sw_T / 2 + c_y;                         // pocket half width

assert(z_bcyl > membrane + 0.5, "boss cylinder too short - reduce stop or widen the free ring");
assert(r_tip > pl_d / 2 + 0.3, "boss tip narrower than the plunger");
assert(r_tip < r_throat - 0.4, "boss tip would hit the throat lip");

// ---------------------------------------------------------------- parts
module boss()
    rotate_extrude() polygon([[0, 0], [r_boss, 0], [r_boss, z_bcyl], [r_tip, z_tip], [0, z_tip]]);

module cavity()      // free ring + funnel, above the membrane
    rotate_extrude() polygon([[0, membrane], [r_rim, membrane], [r_rim, z_c0],
                              [r_throat, z_fun], [0, z_fun]]);

module pocket2d() translate([px0, -pw]) square([R_out + 5 - px0, 2 * pw]);

module ridges()
    for (s = [-1, 1]) {
        // flat face (catches the switch's bottom edge) at z_sw_b + 0.1, 45-deg lead-in above
        translate([ridge_x[0], 0, z_sw_b + 0.1])
            rotate([90, 0, 90]) linear_extrude(ridge_x[1] - ridge_x[0])
                polygon([[s * (pw + 0.3), 0], [s * (pw - ridge), 0], [s * (pw + 0.3), ridge + 0.3]]);   // 0.3 buried in the wall
    }

module button() {
    difference() {
        cylinder(r = R_out, h = z_tot);
        cavity();
        translate([0, 0, z_fun - 0.01]) linear_extrude(lip + 0.02)
            intersection() { circle(r_throat); pocket2d(); }
        translate([0, 0, z_ceil]) linear_extrude(z_tot) pocket2d();
        // small chamfer on the bed edge (stops elephant's foot on the face)
        translate([0, 0, -0.01]) difference() {
            cylinder(r = R_out + 1, h = 0.51);
            cylinder(r1 = R_out - 0.5, r2 = R_out + 0.01, h = 0.51);
        }
    }
    boss();
    ridges();
}

// reference switch body in print coordinates (for drawings / checks)
module switch_ref() {
    translate([-pl_off, -sw_T / 2, z_ceil]) cube([sw_L, sw_T, sw_H]);
    translate([0, 0, z_ceil - pl_free]) cylinder(d = pl_d, h = pl_free + 0.01, $fn = 32);
}

module info() echo(str("INFO {",
    "\"membrane\":", membrane, ",\"r_rim\":", r_rim, ",\"r_boss\":", r_boss, ",\"R_out\":", R_out,
    ",\"stop\":", stop, ",\"gap0\":", gap0, ",\"r_throat\":", r_throat, ",\"lip\":", lip,
    ",\"z_c0\":", z_c0, ",\"z_fun\":", z_fun, ",\"z_ceil\":", z_ceil, ",\"z_bcyl\":", z_bcyl,
    ",\"z_tip\":", z_tip, ",\"r_tip\":", r_tip, ",\"z_sw_b\":", z_sw_b, ",\"z_tot\":", z_tot,
    ",\"px0\":", px0, ",\"pw\":", pw, ",\"ridge\":", ridge, ",\"ridge_x\":", ridge_x,
    ",\"sw\":[", sw_L, ",", sw_T, ",", sw_H, "],\"pl\":[", pl_off, ",", pl_d, ",", pl_free, ",", pl_pt, "]",
    ",\"base_clear\":", base_clear, "}"));

if (part == "button") button();
else if (part == "switch") switch_ref();
else if (part == "info") { info(); cube(1); }
