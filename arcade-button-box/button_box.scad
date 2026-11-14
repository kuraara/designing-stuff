// =====================================================================
//  Arcade Button Box  -  parametric enclosure
//  Long-barrel screw-in arcade buttons (Happ / iL style, 28 mm hole)
//  + ESP32-C3 Super Mini + TP4056 USB-C charger + 1-2x 18650/21700
//
//  Architecture
//    TUB   : floor + 4 walls, printed floor-down. Holds the battery on the
//            floor of a rear "bay"; USB-C ports + power rocker in back wall.
//    PLATE : removable top panel, printed top-face-down. Carries the
//            buttons AND both PCBs (pockets on its underside, in the bay
//            region) so the only plate<->tub harness is the battery lead.
//            Buttons/nuts are fitted on the bench, then the plate drops
//            onto the tub and is held by countersunk M3 screws into
//            heat-set inserts in hanging corner posts.
//    No supports needed for any part.
//
//  Coordinates: origin = tub outer front-left-bottom corner.
//  X = along button columns, Y = front(0) -> back, Z = up.
//
//  Usage (CLI):
//    openscad -D 'cols=3' -D 'rows=2' -D 'part="tub"'   -o tub.stl   button_box.scad
//    openscad -D 'cols=3' -D 'rows=2' -D 'part="plate"' -o plate.stl button_box.scad
//  part = "tub" | "plate" | "plate_asm" | "assembly" | "coupon" | "feet" | "info"
// =====================================================================

/* [Layout] */
cols = 2;               // buttons per row (1-4)
rows = 2;               // rows of buttons (1-2)
part = "assembly";      // [tub, plate, plate_asm, assembly, coupon, feet, info]

/* [Buttons] */
pitch       = 50;    // centre-centre. 38 mm nut + 12 mm finger/wire gap
edge        = 28;    // button centre -> inner wall (nut r19 + 9 mm)
btn_hole_d  = 29.0;  // 1-1/8" (28.6) + allowance: printed holes shrink
btn_bezel_d = 36;    // above-panel bezel (drawings / clearance only)
btn_nut_d   = 38;    // locking nut OD (drawings / clearance only) - MEASURE
btn_depth   = 78;    // underside of bezel -> tips of microswitch tabs - MEASURE
conn_clear  = 14;    // below tab tips: straight .187" spade + wire bend
                     // (flag/right-angle spades: ~6 -> box 8 mm lower)

/* [Battery] */
cells            = 1;     // 1 or 2 (parallel only - TP4056 is 1S)
holder_1         = [83, 24, 22];  // 1x21700 holder L,W,H (18650 holder ~77x21x20 also fits)
holder_2         = [83, 46, 22];  // 2x21700 holder
holder_end_clear = 6;     // each end, for the holder's wire leads
holder_rail_h    = 4;     // holder sits on 2 rails (clears DIP pins / zip tie)

/* [Shell] */
wall      = 2.4;
floor_t   = 2.4;
plate_t   = 4.0;
r_corner  = 5;      // outside vertical edge radius
fit       = 0.3;    // plate lip -> tub wall clearance
lip_w     = 1.6;
lip_h     = 3;
post      = 9;      // hanging screw post (square)
post_h    = 22;     // solid height below rim, then 45deg chamfer
insert_d  = 4.0;    // M3 heat-set insert (M3 x 5.7). Use 2.6 for self-tappers
insert_depth = 7;
screw_d   = 3.4;
csk_d     = 6.6;    // M3 countersunk head
mid_post_threshold = 170;   // add mid posts on long walls when Xi exceeds this

/* [Electronics] */
// [width(X), length(Y, USB axis), pcb thickness]
esp      = [18.0, 22.5, 1.0];   // ESP32-C3 Super Mini
tp       = [17.0, 28.0, 1.2];   // TP4056 USB-C module (with protection)
tp_cx    = 22.5;    // board centres, measured from inner left wall
esp_cx   = 46.0;
standoff = 4;       // plate underside -> PCB back face (3 mm rails + 1 mm foam tape)
usb_cut  = [12.5, 7.0];  // through hole sized for the cable OVERMOLD, not the plug
rocker_cut = [15.2, 10.2]; // KCD11 mini rocker (15x10 cutout), in back wall
rocker_cx  = 72;    // from inner left wall
rocker_cz  = 45;    // above floor top

/* [Feet] */
foot_d = 12.5;  foot_recess = 1.0;  foot_inset = 12;

$fn = 48;

// ------------------------------------------------------------ derived
holder  = cells == 1 ? holder_1 : holder_2;
bay_d   = holder[1] + 6;                       // rear electronics bay depth
field_x = (cols - 1) * pitch + 2 * edge;
field_y = (rows - 1) * pitch + 2 * edge;
Xi = max(field_x, holder[0] + 2 * holder_end_clear);
Yi = field_y + bay_d;
Hi = btn_depth - plate_t + conn_clear;       // floor top -> rim
Xo = Xi + 2 * wall;
Yo = Yi + 2 * wall;
Ho = Hi + floor_t;                           // tub height
x0 = wall;  x1 = wall + Xi;
y0 = wall;  y1 = wall + Yi;
bx0 = x0 + (Xi - field_x) / 2 + edge;        // first button column
by0 = y0 + edge;                             // front row
buttons = [for (r = [0 : rows - 1], c = [0 : cols - 1]) [bx0 + c * pitch, by0 + r * pitch]];

corner_posts = [[x0, y0, 1, 1], [x1, y0, -1, 1], [x0, y1, 1, -1], [x1, y1, -1, -1]];
has_mid  = Xi > mid_post_threshold;
mid_posts = has_mid ? [[Xo / 2, y0, 1], [Xo / 2, y1, -1]] : [];
center_posts = rows >= 2 ?
    [for (i = [0 : cols - 2]) [bx0 + (i + 0.5) * pitch, by0 + 0.5 * pitch]] : [];
screw_pts = concat(
    [for (p = corner_posts) [p[0] + p[2] * post / 2, p[1] + p[3] * post / 2]],
    [for (p = mid_posts)    [p[0], p[1] + p[2] * post / 2]],
    center_posts);

bat_x0 = x0 + holder_end_clear;
bat_y1 = y1 - 3;
bat_y0 = bat_y1 - holder[1];
board_back = y1 - 2.2;         // PCB USB edge (lip band ends at y1-1.9)
function port_z(b) = Ho - standoff - b[2] - 1.6;   // USB-C centre (component side down)

// ------------------------------------------------------------ helpers
module rrect(s, r) {
    rr = max(0.01, min(r, s[0] / 2 - 0.01, s[1] / 2 - 0.01));
    hull() for (x = [rr, s[0] - rr], y = [rr, s[1] - rr])
        translate([x, y, 0]) cylinder(r = rr, h = s[2], $fn = 32);
}
module rslot(w, h, d, r = 1.5) {     // rounded rectangle in XZ, depth d along Y
    rotate([-90, 0, 0]) linear_extrude(d)
        offset(r) square([w - 2 * r, h - 2 * r], center = true);
}

// ------------------------------------------------------------ TUB
module hang_corner(px, py, sx, sy) {
    zb = Ho - post_h;
    hull() {
        translate([min(px, px + sx * post), min(py, py + sy * post), zb]) cube([post, post, post_h]);
        translate([px - (sx > 0 ? 0 : 0.01), py - (sy > 0 ? 0 : 0.01), zb - post]) cube(0.01);
    }
}
module hang_mid(px, py, sy, w = 10) {
    zb = Ho - post_h;
    hull() {
        translate([px - w / 2, min(py, py + sy * post), zb]) cube([w, post, post_h]);
        translate([px - w / 2, py - (sy > 0 ? 0 : 0.01), zb - post]) cube([w, 0.01, 0.01]);
    }
}
module battery_fixtures() {
    L = holder[0]; W = holder[1]; c = 0.5; t = 1.6; leg = 8; fh = holder_rail_h + 6;
    // two transverse rails (zip tie / strap passes between them)
    for (fx = [0.2, 0.8]) translate([bat_x0 + fx * L - 1.5, bat_y0, floor_t - 0.01]) cube([3, W, holder_rail_h]);
    // four L-shaped corner fences
    for (cx = [0, 1], cy = [0, 1]) {
        X = cx == 0 ? bat_x0 - c - t : bat_x0 + L + c;
        Y = cy == 0 ? bat_y0 - c - t : bat_y0 + W + c;
        translate([X, Y, floor_t - 0.01]) {
            translate([cx == 0 ? 0 : t - leg, 0, 0]) cube([leg, t, fh]);
            translate([0, cy == 0 ? 0 : t - leg, 0]) cube([t, leg, fh]);
        }
    }
}
module tub() {
    difference() {
        union() {
            difference() {
                rrect([Xo, Yo, Ho], r_corner);
                translate([x0, y0, floor_t]) rrect([Xi, Yi, Ho], r_corner - wall);
            }
            for (p = corner_posts) hang_corner(p[0], p[1], p[2], p[3]);
            for (p = mid_posts) hang_mid(p[0], p[1], p[2]);
            for (p = center_posts) translate([p[0], p[1], floor_t - 0.01]) {
                cylinder(d1 = 18, d2 = 10, h = 8);
                cylinder(d = 10, h = Hi + 0.01);
            }
            battery_fixtures();
        }
        // heat-set insert holes
        for (p = screw_pts) translate([p[0], p[1], Ho - insert_depth]) cylinder(d = insert_d, h = insert_depth + 1);
        // USB-C ports (cable overmold clearance) in back wall
        for (b = [[tp, tp_cx], [esp, esp_cx]])
            translate([x0 + b[1], y1 - 1, port_z(b[0])]) rslot(usb_cut[0], usb_cut[1], wall + 2);
        // power rocker
        translate([x0 + rocker_cx, y1 - 1, floor_t + rocker_cz]) rslot(rocker_cut[0], rocker_cut[1], wall + 2, 0.5);
        // feet recesses
        for (fx = [foot_inset, Xo - foot_inset], fy = [foot_inset, Yo - foot_inset])
            translate([fx, fy, -1]) cylinder(d = foot_d, h = foot_recess + 1);
    }
}

// ------------------------------------------------------------ PLATE (z=0 underside, built in use orientation)
module board_pocket(b, cx) {
    bw = b[0]; bl = b[1]; pcb = b[2];
    yb = board_back; yf = yb - bl;
    gd = standoff + pcb + 1.0;           // guide depth below plate
    // standoff rails under the two long edges (foam tape goes on these)
    for (sx = [-1, 1]) translate([cx + sx * (bw / 2 - 1.5) - 1.5, yf + 1, -(standoff - 1)]) cube([3, bl - 2, standoff - 1 + 0.01]);
    // side guides
    for (sx = [-1, 1]) translate([cx + sx * (bw / 2 + 0.3) + (sx > 0 ? 0 : -1.2), yf, -gd]) cube([1.2, bl, gd + 0.01]);
    // corner stop tabs (back pair leaves room for the USB receptacle)
    for (sx = [-1, 1], ty = [yb, yf - 1.2]) translate([cx + sx * (bw / 2 - 1.5) - 1.5, ty, -gd]) cube([3, 1.2, gd + 0.01]);
}
module plate_asm() {
    difference() {
        union() {
            rrect([Xo, Yo, plate_t], r_corner);
            // locating lip, interrupted at the posts
            difference() {
                translate([x0 + fit, y0 + fit, -lip_h]) difference() {
                    rrect([Xi - 2 * fit, Yi - 2 * fit, lip_h + 0.01], 2);
                    translate([lip_w, lip_w, -1]) rrect([Xi - 2 * fit - 2 * lip_w, Yi - 2 * fit - 2 * lip_w, lip_h + 2], 1);
                }
                for (p = corner_posts) translate([p[0] + (p[2] > 0 ? -1 : -post - 0.6), p[1] + (p[3] > 0 ? -1 : -post - 0.6), -lip_h - 1]) cube([post + 1.6, post + 1.6, lip_h + 1]);
                for (p = mid_posts) translate([p[0] - 5.6, p[1] + (p[2] > 0 ? -1 : -post - 0.6), -lip_h - 1]) cube([11.2, post + 1.6, lip_h + 1]);
            }
            board_pocket(tp, x0 + tp_cx);
            board_pocket(esp, x0 + esp_cx);
        }
        for (b = buttons) translate([b[0], b[1], -lip_h - 1]) cylinder(d = btn_hole_d, h = plate_t + lip_h + 2, $fn = 96);
        for (p = screw_pts) translate([p[0], p[1], -1]) {
            cylinder(d = screw_d, h = plate_t + 2);
            translate([0, 0, 1 + plate_t - (csk_d - screw_d) / 2]) cylinder(d1 = screw_d, d2 = csk_d, h = (csk_d - screw_d) / 2 + 0.01);
        }
    }
}
module plate_print() { translate([0, Yo, plate_t]) rotate([180, 0, 0]) plate_asm(); }

// ------------------------------------------------------------ FIT TEST COUPON (~20 min)
module coupon() {
    W = 64; D = 46; wh = 20;
    difference() {
        union() {
            rrect([W, D, plate_t], 3);
            translate([0, D - wall, 0]) cube([W, wall, wh]);                  // test wall
            translate([W - post - 3, 3, 0]) cube([post, post, 16]);            // insert post
        }
        translate([22, 21, -1]) cylinder(d = btn_hole_d, h = plate_t + 2, $fn = 96);
        translate([W - 3 - post / 2, 3 + post / 2, 16 - insert_depth]) cylinder(d = insert_d, h = insert_depth + 1);
        translate([W - 3 - post / 2, 22, -1]) {                               // countersunk M3
            cylinder(d = screw_d, h = plate_t + 2);
            translate([0, 0, 1 + plate_t - (csk_d - screw_d) / 2]) cylinder(d1 = screw_d, d2 = csk_d, h = (csk_d - screw_d) / 2 + 0.01);
        }
        translate([15, D - wall - 1, plate_t + 6]) rslot(usb_cut[0], usb_cut[1], wall + 2);
        translate([42, D - wall - 1, plate_t + 8]) rslot(rocker_cut[0], rocker_cut[1], wall + 2, 0.5);
    }
}
module feet() { for (i = [0 : 3]) translate([i * 16, 0, 0]) cylinder(d = foot_d - 0.4, h = 3); }

// ------------------------------------------------------------ info (parsed by drawing generator)
module info() {
    echo(str("INFO{",
      "\"cols\":", cols, ",\"rows\":", rows, ",\"Xo\":", Xo, ",\"Yo\":", Yo, ",\"Ho\":", Ho,
      ",\"Xi\":", Xi, ",\"Yi\":", Yi, ",\"Hi\":", Hi, ",\"wall\":", wall, ",\"floor_t\":", floor_t,
      ",\"plate_t\":", plate_t, ",\"pitch\":", pitch, ",\"edge\":", edge, ",\"bay_d\":", bay_d,
      ",\"field_x\":", field_x, ",\"field_y\":", field_y,
      ",\"buttons\":", buttons, ",\"screw_pts\":", screw_pts, ",\"center_posts\":", center_posts,
      ",\"has_mid\":", has_mid ? 1 : 0,
      ",\"btn\":[", btn_hole_d, ",", btn_bezel_d, ",", btn_nut_d, ",", btn_depth, ",", conn_clear, "]",
      ",\"holder\":", holder, ",\"bat\":[", bat_x0, ",", bat_y0, ",", floor_t + holder_rail_h, "]",
      ",\"tp\":[", x0 + tp_cx, ",", tp[0], ",", tp[1], ",", tp[2], ",", port_z(tp), "]",
      ",\"esp\":[", x0 + esp_cx, ",", esp[0], ",", esp[1], ",", esp[2], ",", port_z(esp), "]",
      ",\"board_back\":", board_back, ",\"standoff\":", standoff,
      ",\"usb_cut\":", usb_cut, ",\"rocker\":[", x0 + rocker_cx, ",", floor_t + rocker_cz, ",", rocker_cut[0], ",", rocker_cut[1], "]",
      ",\"post\":", post, ",\"post_h\":", post_h, ",\"foot\":[", foot_d, ",", foot_inset, "]",
      "}"));
}

// ------------------------------------------------------------ dispatch
if (part == "tub") tub();
else if (part == "plate") plate_print();
else if (part == "plate_asm") plate_asm();
else if (part == "coupon") coupon();
else if (part == "feet") feet();
else if (part == "info") { info(); cube(1); }
else { tub(); translate([0, 0, Ho]) %plate_asm(); info(); }
