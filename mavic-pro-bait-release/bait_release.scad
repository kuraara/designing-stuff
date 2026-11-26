// Mavic Pro (gen 1) bait release pod — v0.1
// Self-powered drop release: 18650 + ELRS/Crossfire RX + ESP32-C3 + micro servo,
// stuck under the drone with heavy-duty hook-and-loop or double-sided tape.
//
// Release: a rotary "arc pin". An arc concentric with the servo shaft spans a 6 mm gap
// between two TPU ledges; the line loop hangs on the arc in the gap. The load pushes
// straight out from the shaft, so the servo holds no torque; it only has to slide the
// arc ~52° out of the gap.
//
// Coordinates (assembly): X forward (drone nose), Y left, Z up. Z = 0 is the pod's
// bottom face; the lid's top face (the tape face) is at Z = rim_z + lid_t.
// The servo shaft lies along X at (Y = 0, Z = zs) and points rearward.
//
// part = "tub" | "lid" | "horn" | "assembly" | "ref_servo" | "ref_holder" | "ref_boards"
//      | "horn_place" (in place, rotated by horn_rot) | "sweep_check" | "info"
part = "assembly";
horn_rot = 0;      // for part="horn_place": 0 = locked, -a_throw = open
show_lid = true;   // assembly view
$fn = 64;

// ---------------- shell ----------------
wall     = 1.6;     // outer walls (TPU: 3-4 perimeters)
floor_t  = 1.2;
rim_z    = 25.8;    // top of tub walls (servo top is at zs + sv_W/2 = 25.2)
lid_t    = 2.0;     // M3 countersunk heads (1.7) sit flush in the tape face
corner_r = 3;

// ---------------- layout, X ----------------
bay_x0   = -17.5;   // inner face of rear wall
x_rear   = bay_x0 - wall;  // outer rear face
bk_x0    = 0;       // bulkhead rear face (bay is bay_x0..bk_x0)
bk_t     = 3;       // bulkhead; servo tabs seat on its front face (X = bk_t)
xf_in    = 60;      // inner face of front wall
x_front  = xf_in + wall;

// ---------------- layout, Y ----------------
yl_in    = -23.5;   // inner -Y face
y_left   = yl_in - wall;
cell_y0  = 13;      // cell compartment inner -Y face
cell_w   = 22.6;    // Jaycar PH9205 is 22 wide; SparkFun PRT-12899 21.5
cellwall_t = 1.5;
y_right  = cell_y0 + cell_w + wall;
cell_len = xf_in - bay_x0;  // 77.5: PH9205 76, PRT-12899 74.5

// ---------------- servo envelope (MG90S and EMAX ES08MA II) ----------------
sv_L         = 23.2;   // body length (runs along Y here)
sv_W         = 12.4;   // body width (vertical here). MG90S 12.2, ES08MA II 11.5
sv_shaft_off = 6.0;    // shaft centre from the near end of the body
sv_hole_span = 27.8;   // tab screw holes
sv_tab_span  = 32.6;
sv_tab_t     = 2.6;
sv_tab_to_bottom = 18.4;  // tab top face to the bottom of the case
sv_tab_to_case   = 4.5;   // tab top face to the top of the case
zs = 19;               // shaft height
// X of the outer (rear) face of the stock horn arm, once fitted.
// = bk_t - (tab top face -> horn outer face). Measure yours: MG90S ~12.5 mm -> -9.5.
horn_face_x = -9.5;

// ---------------- release geometry ----------------
gap      = 6;      // loop gap between the ledges (Y)
fin_t    = 3.5;    // ledge / stripper thickness (Y)
fin_top  = 11.5;   // stripper height
arc_ri   = 11;     // arc inner radius
arc_ro   = 15;     // arc outer radius
arc_t    = 4;      // horn thickness (X) = print height
engage   = 3;      // arc tip into the far ledge when locked (at the arc's mid radius)
open_clear = 2.5;  // tip retracts this far behind the near stripper face when open
a_spoke  = -50;    // spoke angle when locked (0 = straight down, + towards +Y)
hub_r    = 5.5;
clr      = 0.4;    // running clearance
slit_tol = 2;      // extra room either side of the horn in X (servo/horn tolerance)
arc_rm   = (arc_ri + arc_ro) / 2;
a_lock   = asin((gap/2 + engage) / arc_rm);          // tip angle, locked
a_open   = -asin((gap/2 + open_clear) / arc_rm);     // tip angle, open
a_throw  = a_lock - a_open;                           // servo travel needed
horn_x0  = horn_face_x - arc_t;                       // arc horn X range
horn_x1  = horn_face_x;
slit_x0  = horn_x0 - slit_tol;
slit_x1  = horn_x1 + slit_tol;

// stock single-arm horn (for the pocket and the sweep check)
sh_hub_d = 7.6;  sh_len = 16.5;  sh_w0 = 6.2;  sh_w1 = 4.4;  sh_t = 1.8;  sh_pocket = 1.4;

// ---------------- lid screws (M3 x 10 countersunk, self-tapping into TPU) ----------------
boss_r = 3.25;  boss_z0 = 13;  pilot_d = 2.5;
bosses = [[bay_x0 + 3, yl_in + 3],          // rear left, in the bay
          [bay_x0 + 3, cell_y0 - 3.25],     // rear right, on the cell wall
          [25, cell_y0 - 3.25],             // middle right, on the cell wall
          [xf_in - 2.5, yl_in + 2.5]];        // front left

// ---------------- electronics openings ----------------
tp_w = 17.5; tp_l = 28.5;                    // TP4056 USB-C board
tp_yc = cell_y0 - cellwall_t - tp_w/2 - 0.3; // board centre Y
usb_w = 12.5; usb_h = 7.2; usb_zc = floor_t + 1.6 + 1.65;
sw_x = 44; sw_z = 16; sw_l = 6.5; sw_h = 3.5;   // SS12D00 slide switch window, -Y wall
ant_x = 12; ant_z = 6; ant_d = 4.5;             // RX antenna exit, -Y wall

// ================= helpers =================
function pol(r, a) = [r * sin(a), -r * cos(a)];   // angle 0 = down, + towards +Y

module sector(r0, r1, a0, a1, n = 48) {
  pts = concat([for (i = [0:n]) pol(r1, a0 + (a1 - a0) * i / n)],
               r0 > 0 ? [for (i = [n:-1:0]) pol(r0, a0 + (a1 - a0) * i / n)] : [[0, 0]]);
  polygon(pts);
}

// 2D (u, v) = (Y, Z - zs) extruded along X from x0 to x1
module yz(x0, x1) translate([x0, 0, zs]) rotate([90, 0, 90]) linear_extrude(x1 - x0) children();

module rbox(x0, x1, y0, y1, z0, z1, r = corner_r) {
  translate([0, 0, z0]) linear_extrude(z1 - z0)
    hull() for (x = [x0 + r, x1 - r], y = [y0 + r, y1 - r]) translate([x, y]) circle(r);
}

// ================= arc horn =================
module horn2d() {
  offset(r = 0.8) offset(delta = -0.8) union() {
    circle(hub_r);
    hull() { circle(4.5); translate(pol(13, a_spoke)) circle(3); }
    sector(arc_ri, arc_ro, a_spoke - 8, a_lock);
  }
}
module stock_arm2d() {
  hull() { circle(sh_hub_d/2); translate(pol(sh_len - sh_w1/2, a_spoke)) circle(sh_w1/2); }
}
// in place, locked (rot = 0) or rotated by rot degrees (open = -a_throw)
module horn(rot = 0) {
  difference() {
    yz(horn_x0, horn_x1) rotate(rot) horn2d();
    // pocket for the stock arm on the servo side (+X face)
    yz(horn_x1 - sh_pocket, horn_x1 + 1) rotate(rot) offset(0.25) stock_arm2d();
    // horn screw: through hole + head counterbore from the rear face
    yz(horn_x0 - 1, horn_x1 + 1) circle(d = 2.6);
    yz(horn_x0 - 1, horn_x1 - 1.4) circle(d = 5);
    // two tie / screw holes along the spoke
    for (r = [8.5, 12]) yz(horn_x0 - 1, horn_x1 + 1) rotate(rot) translate(pol(r, a_spoke)) circle(d = 1.8);
  }
}
module horn_print() {   // flat on the bed, pocket face up
  translate([0, 0, arc_t]) rotate([0, -90, 0])
    translate([-horn_x1, 0, -zs]) horn(0);
}

// everything the horns sweep through between locked and open (+ clearance)
module sweep2d(shape = "horn") {
  offset(delta = clr) union()
    for (a = [0:2.5:a_throw + 0.01]) rotate(-a)
      if (shape == "horn") horn2d(); else stock_arm2d();
}

// ================= tub =================
module fin(y0, y1) {
  difference() {
    translate([bay_x0, y0, 0]) cube([bk_x0 - bay_x0, y1 - y0, fin_top]);
    // in the horn's X range only the ledge under the arc is left (open on top for assembly)
    yz(slit_x0, slit_x1) circle(r = arc_ro + clr);
  }
}

module boss(p) {
  translate([p[0], p[1], boss_z0]) cylinder(r = boss_r, h = rim_z - boss_z0);
  translate([p[0], p[1], boss_z0 - boss_r]) cylinder(r1 = 0, r2 = boss_r, h = boss_r); // 45° under
}

module tub() {
  difference() {
    union() {
      difference() {
        rbox(x_rear, x_front, y_left, y_right, 0, rim_z);
        rbox(x_rear + wall, x_front - wall, y_left + wall, y_right - wall, floor_t, rim_z + 1, 0.5);
      }
      // bulkhead
      translate([bk_x0, yl_in, 0]) cube([bk_t, cell_y0 - cellwall_t - yl_in, rim_z]);
      // cell wall
      translate([bay_x0, cell_y0 - cellwall_t, 0]) cube([xf_in - bay_x0, cellwall_t, rim_z]);
      // ledges / strippers
      fin(-gap/2 - fin_t, -gap/2);
      fin(gap/2, gap/2 + fin_t);
      // lid screw bosses
      for (p = bosses) boss(p);
      // TP4056 back stop
      translate([xf_in - tp_l - 2, tp_yc - tp_w/2, 0]) cube([2, tp_w, floor_t + 3]);
    }
    // servo slot through the bulkhead, open at the top
    translate([bk_x0 - 1, -(sv_L - sv_shaft_off) - 0.3, zs - sv_W/2 - 0.2])
      cube([bk_t + 2, sv_L + 0.6, rim_z]);
    // servo tab screw pilots
    for (s = [-1, 1]) translate([bk_x0 - 1, (sv_shaft_off - (sv_L - sv_shaft_off))/2 + s*sv_hole_span/2, zs])
      rotate([0, 90, 0]) cylinder(d = 1.8, h = bk_t + 2, $fn = 16);
    // loop gap: through the floor (flared) and out the back
    hull() {
      translate([x_rear - 1, -gap/2, floor_t]) cube([bk_x0 - x_rear + 1, gap, 0.01]);
      translate([x_rear - 1, -gap/2 - 0.8, -0.01]) cube([bk_x0 - x_rear + 1, gap + 1.6, 0.01]);
    }
    translate([x_rear - 1, -gap/2, -1]) cube([bk_x0 - x_rear + 1, gap, floor_t + 2]);
    translate([x_rear - 1, -gap/2, -1]) cube([wall + 2, gap, 10]);
    // screwdriver / sight hole to the horn screw (teardrop, prints without support)
    translate([x_rear - 1, 0, zs]) rotate([0, 90, 0])
      linear_extrude(wall + 2) rotate(90) teardrop2d(3.5);
    // horn sweep (horn + stock arm) cut from anything in the way
    yz(horn_x0 - slit_tol, horn_x1 + slit_tol) sweep2d("horn");
    yz(horn_x1 - 0.2, horn_x1 + sh_t + 1.5) sweep2d("arm");
    // lid screw pilots
    for (p = bosses) translate([p[0], p[1], boss_z0 - 0.01]) cylinder(d = pilot_d, h = rim_z, $fn = 16);
    // USB-C (TP4056) in the front wall, pointed top so it bridges
    translate([x_front - wall - 1, tp_yc, usb_zc]) rotate([0, 90, 0]) linear_extrude(wall + 2)
      rotate(90) usb2d();
    // slide switch window and antenna exit, -Y wall
    translate([sw_x - sw_l/2, y_left - 1, sw_z - sw_h/2]) cube([sw_l, wall + 2, sw_h]);
    translate([ant_x, y_left - 1, ant_z]) rotate([-90, 0, 0]) cylinder(d = ant_d, h = wall + 2, $fn = 24);
    // weight-saving window in the floor under the 18650 holder
    translate([bay_x0 + 8, cell_y0 + 4, -1]) linear_extrude(floor_t + 2) offset(r = 3) offset(delta = -3)
      square([xf_in - bay_x0 - 16, cell_w - 8]);
    // wire notches over the cell wall
    for (x = [-6, 30]) translate([x - 2.5, cell_y0 - cellwall_t - 1, rim_z - 7]) cube([5, cellwall_t + 2, 8]);
  }
}

module teardrop2d(r) { union() { circle(r); rotate(45) square(r); } }   // point towards local +x/+y
module usb2d() {   // width along local x, height along local y, 45° pointed top (+y) so it prints
  hull() {
    translate([-usb_w/2 + 1, -usb_h/2 + 1]) circle(1);
    translate([ usb_w/2 - 1, -usb_h/2 + 1]) circle(1);
    translate([-usb_w/2, usb_h/2 - 0.01]) square([usb_w, 0.01]);
    translate([0, usb_h/2 + usb_w/2]) square([0.01, 0.01], center = true);
  }
}

// ================= lid (tape face up) =================
module lid() {
  difference() {
    union() {
      rbox(x_rear, x_front, y_left, y_right, 0, lid_t);
      // tether eyelet at the front
      hull() {
        translate([x_front - 3, -5, 0]) cube([1, 10, lid_t]);
        translate([x_front + 5, 0, 0]) cylinder(r = 5, h = lid_t);
      }
    }
    translate([x_front + 5, 0, -1]) cylinder(d = 4.5, h = lid_t + 2);
    for (p = bosses) translate([p[0], p[1], 0]) {
      translate([0, 0, -1]) cylinder(d = 3.4, h = lid_t + 2, $fn = 24);
      translate([0, 0, lid_t - 1.8]) cylinder(d1 = 3.4, d2 = 6.4 + 0.2, h = 1.8 + 0.01, $fn = 24);
    }
  }
}
module lid_print() translate([0, 0, lid_t]) mirror([0, 0, 1]) lid();   // tape face on the bed

// ================= reference bodies =================
module ref_servo() {
  yb = -(sv_L - sv_shaft_off);
  // case, tabs, tower, stock horn
  translate([bk_t - sv_tab_to_case, yb, zs - sv_W/2]) cube([sv_tab_to_case + sv_tab_to_bottom, sv_L, sv_W]);
  translate([bk_t, yb - (sv_tab_span - sv_L)/2, zs - sv_W/2]) cube([sv_tab_t, sv_tab_span, sv_W]);
  yz(bk_t - sv_tab_to_case - 4, bk_t - sv_tab_to_case) circle(d = 11.5);
  yz(horn_x1, horn_x1 + sh_t) stock_arm2d();
  yz(horn_x1 + sh_t, bk_t - sv_tab_to_case - 4) circle(d = sh_hub_d - 1);
}
module ref_holder() translate([bay_x0 + 0.75, cell_y0 + 0.3, floor_t]) cube([76, 22, 21]);
module ref_boards() {
  // TP4056 USB-C, MT3608, ESP32-C3 SuperMini (under the servo), ELRS RX
  translate([xf_in - tp_l, tp_yc - tp_w/2, floor_t]) cube([tp_l, tp_w, 5]);
  translate([xf_in - 37, yl_in + 0.1, floor_t]) cube([36, 17, 6.5]);
  translate([bk_t + 1, -19.5, floor_t]) cube([18, 22.5, 3.5]);
  translate([bk_t + 1, -19.5, floor_t + 4]) cube([18, 12, 3]);
}

module sweep_check() {   // should be empty: horn swept through its travel vs the tub
  intersection() {
    tub();
    union() for (a = [0:2.5:a_throw + 0.01]) horn(-a);
  }
}

// ================= output =================
if (part == "tub") tub();
else if (part == "lid") lid_print();
else if (part == "horn") horn_print();
else if (part == "ref_servo") ref_servo();
else if (part == "ref_holder") ref_holder();
else if (part == "ref_boards") ref_boards();
else if (part == "sweep_check") sweep_check();
else if (part == "horn_place") horn(horn_rot);
else if (part == "assembly") {
  color("#3b6ea5") tub();
  color("#e8a33d") horn(horn_rot);
  if (show_lid) color("#9aa", 0.6) translate([0, 0, rim_z]) lid();
  color("#d55", 0.5) ref_servo();
  color("#5a5", 0.5) ref_holder();
  color("#aa5", 0.5) ref_boards();
}
else if (part == "info") {
  // ledge thickness under the arc at the gap edge and at the ledge's outer face
  l_in  = zs - sqrt(pow(arc_ro + clr, 2) - pow(gap/2, 2));
  l_out = zs - sqrt(pow(arc_ro + clr, 2) - pow(gap/2 + fin_t, 2));
  echo(str("INFO {",
    "\"x_rear\": ", x_rear, ", \"x_front\": ", x_front, ", \"y_left\": ", y_left, ", \"y_right\": ", y_right,
    ", \"length\": ", x_front - x_rear, ", \"width\": ", y_right - y_left, ", \"height\": ", rim_z + lid_t,
    ", \"gap\": ", gap, ", \"gap_x\": ", (horn_x0 + horn_x1)/2, ", \"gap_y\": 0",
    ", \"arc_ri\": ", arc_ri, ", \"arc_ro\": ", arc_ro, ", \"arc_t\": ", arc_t,
    ", \"a_lock\": ", round(a_lock*10)/10, ", \"a_open\": ", round(a_open*10)/10,
    ", \"a_throw\": ", round(a_throw*10)/10,
    ", \"ledge_min\": ", round(l_in*10)/10, ", \"ledge_max\": ", round(l_out*10)/10,
    ", \"loop_space_above_arc\": ", round((zs - hub_r - (zs - arc_ri))*10)/10,
    ", \"cell_len\": ", cell_len, ", \"cell_w\": ", cell_w,
    ", \"zs\": ", zs, ", \"horn_face_x\": ", horn_face_x,
    ", \"lid_t\": ", lid_t, ", \"rim_z\": ", rim_z,
    "}"));
}
