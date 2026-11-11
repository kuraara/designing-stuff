// =====================================================================
//  Raspberry Pi 5 + Waveshare PoE HAT (G) + Pimoroni NVMe Base Duo
//  Slide-in "tube" case. No screws or standoffs in any board.
//
//  Stack (bottom -> top), each board on its own ledge
//    NVMe Base Duo (PIM704), SSDs on its UNDERSIDE  -> rests on the LOWER ledge
//    (12 mm gap, set by the PCIe ribbon)
//    Raspberry Pi 5 (+ Active Cooler)               -> rests on the UPPER ledge
//    PoE HAT (G) WS-27670, held by its GPIO + PoE headers only
//
//  Cross-section per the user's sketch (v0.2): two lips on each long wall.
//  The upper lip sits between the two boards; the Pi rests on its top, the
//  Duo's edge runs in the recess under it and rests on the lower lip. Below the
//  lower lip the wall steps back out to make the SSD bay.
//  A low fence on each ledge (1.2 mm, under PCB thickness) locates each board
//  sideways. The boards slide in from the SD end, USB first, stop on the
//  closed USB end wall, and the lid's prongs push them home.
//
//  Print
//    BODY : USB end wall on the bed, tube vertical. Every lip is a vertical
//           extrusion, vents are vertical slots: no supports.
//    LID  : outer face on the bed, PLA or PETG (two flexing latch arms click into
//           the body's upper side windows).               FEET: flat, TPU.
//
//  Coordinates: board-aligned. X = 0 at the boards' SD-end edge, 85 at the
//  USB end. Y = 0 at the HDMI / USB-C edge, 56 at the GPIO edge.
//  Z = 0 at the outside bottom of the case.
//
//  part = "body" | "body_asm" | "lid" | "lid_asm" | "feet" | "assembly" | "info"
// =====================================================================

part = "assembly";

/* [Stack] */
bl   = 85;       // board length (Pi 5, Duo)
bw   = 56;       // board width
pcb  = 1.6;
duo_gap = 12;    // Duo top -> Pi underside; the PCIe ribbon is made for 12 mm
drive_drop = 9.5;// Duo underside -> lowest point of the SSDs - CHECK (heatsinks: ~14)
hat_gap  = 16;   // Pi top -> HAT underside (16 mm header clears the Active Cooler) - CHECK
hat_l = 65; hat_w = 56.5;
hat_comp = 9;    // tallest part on top of the HAT - MEASURE
port_over = 2.4; // USB-A / RJ45 overhang past the board's USB edge

/* [Ledges] */
fence_gap = 0.4;  // board edge -> fence face (sideways play each side)
fence_h   = 1.2;  // fence height above each ledge (less than the PCB)
pi_ledge  = 1.0;  // upper ledge reach under the Pi. GPIO solder joints and jack tabs
                  // on the Pi's underside start ~1.4 mm in, so keep this small
pi_lip_t  = 5.0;  // upper lip thickness
duo_ledge = 3.0;  // lower ledge reach under the Duo (SSDs must stay further in) - CHECK
duo_lip_t = 3.0;
low_in    = 0.5;  // SSD bay wall face, inward from the board edge
x_lip0    = 0.8;  // ledges start here (boards overhang them slightly at the SD end)
plug_step = 2.5;  // in the port window the upper lip's outer half drops this far,
                  // so a USB-C / HDMI plug overmold can pass under the Pi's edge
plug_reach = 1.4; // ... out to this far outside the board edge

/* [Clearances] */
side_gap  = 4;    // board edge -> inner wall (air)
air_top   = 5;    // HAT parts -> roof
air_below = 3.5;  // SSDs -> floor
sd_space  = 10;   // board SD edge -> lid skirt (PCIe ribbon loop)
usb_gap   = 0.5;  // board USB edge -> end wall

/* [Shell] */
wall   = 2.4;
floor_t = 2.4;
roof_t = 2.4;
end_t  = 2.4;
r_out  = 4;

/* [Ports] */
eth_y = 10.2;  usb_y = [29.1, 47.0];         // centres on the USB end (Pi 5 drawing)
eth_cut = [17, 15.0];  usb_cut = [15, 17.4];  // W x H, from 0.4 below the Pi top
usbc_x = 11.2; hdmi_x = [25.8, 39.2];        // centres on the long edge (Pi 5 drawing)
side_cut_top = 5.25;   // window top above the USB-C centre
side_cut_pad = 8;      // window extends this far each side of the USB-C centre
hdmi = true;           // false: USB-C cut-out only

/* [Lid] */
lid_t  = 2.4;
plug_d = 6;       // skirt depth into the body
skirt  = 1.8;
fit    = 0.25;
lead_c = 0.6;     // chamfer on the skirt's leading edge (rigid lid: eases it into the mouth)
prong_tip = 0.3;  // prongs end here: boards float 0.2 mm, no preload (rigid PLA/PETG lid)

/* [Lid latches] */
// v0.3: PLA/PETG lid. The v0.2 TPU bumps (0.8 mm) printed as faint nubs.
// One flexing arm per long side, cut out of the skirt by slots through the lid,
// fixed at its top end. It bends in the layer plane (along the filaments), and
// its hook clicks into the body's UPPER side window (lower windows: vents only).
latch = true;
latch_t    = 1.6;   // arm thickness (Y). Thinner = softer click
latch_hook = 1.0;   // hook height above the arm face; 0.75 mm of it reaches into the window
latch_w    = 8;     // hook width along Z (window is 9)
latch_slot = 1.2;   // room inside the arm to flex into
latch_gap  = 0.8;   // slot through the lid plate outside the arm (wide enough to survive first-layer squish)
latch_end  = 1.0;   // slot across the arm's free end

/* [Vents] */
vent_w = 3;  vent_pitch = 6.25;  vent_seg = 24;  vent_bar = 4;
side_vents = true;    // slots in both long walls between the two lips

/* [Feet] */
foot_d = 14; foot_h = 6; foot_x = [4, 80];
foot_cb = [6.4, 3.0];   // counterbore Ø x depth: M3 button head (ISO 7380, Ø5.7 x 1.65) or socket head (Ø5.5 x 3)
foot_screw = 8;         // M3 x 8 under-head length; leaves 3.0 mm of TPU under the head, 5.0 mm in the insert
foot_recess = 0.6;      // locating recess in the case floor for each foot / DIN boss
insert_d = 4.0; insert_len = 5.7;
insert_depth = 6.5;     // insert hole below the recess floor (v0.2 printed bodies: 5.4)

/* [DIN rail bracket] */
// Bolts to the four foot inserts in place of the feet. Clips onto a TS35 rail
// (EN 60715, 35 x 7.5 or 15) running across the case, so the case stands with
// its length vertical: 69 mm (4 modules) along the rail. The bolt pattern is
// symmetric, so the case can go USB-end-down or up on the same bracket.
din_rail_w = 35;      // TS35 flange-to-flange width
din_gap    = 14;      // air gap between the bracket plate and the case floor vents
din_plate  = 6.4;     // plate thickness
din_lip    = 1.6;     // hook / latch lip thickness (wall side)
din_slot   = 1.2;     // flange slot: 1.0 mm flange + 0.2
din_hook   = 3.2;     // fixed hook reach under its flange
din_latch  = 1.5;     // latch reach under its flange (releases after 1.75 mm of pull)
din_travel = 2.2;     // latch over-travel stop
din_play   = 0.25;    // flange edge -> hook wall / latch wall
din_beam   = 1.0;     // latch flexure beam thickness (4 beams, ~21 mm free each side)
din_head_w = 24;      // latch head width (along the rail)
din_tongue_w = 12;    // latch tongue width
din_rib    = 6;       // side rib width (under the case's thick lower walls)
din_boss   = 10;
din_cb     = [6.2, 5.4];  // M3 socket head counterbore: M3 x 20 leaves 5 mm in the insert
din_tab    = 7;       // pull tab past the bracket end, with a screwdriver slot

$fn = 40;

// ------------------------------------------------------------ derived
zf      = floor_t;                          // floor top
zd      = zf + air_below + drive_drop;      // Duo underside = lower ledge top
z_dlb   = zd - duo_lip_t;                   // lower lip underside
z_duo_t = zd + pcb;
z_pi_b  = z_duo_t + duo_gap;                // Pi underside = upper ledge top
z_plb   = z_pi_b - pi_lip_t;                // upper lip underside
z_pi_t  = z_pi_b + pcb;
z_hat_b = z_pi_t + hat_gap;
z_hat_t = z_hat_b + pcb;
z_hat_c = z_hat_t + hat_comp;
z_roof  = z_hat_c + air_top;                // roof underside
H       = z_roof + roof_t;
y_in0 = -side_gap;  y_in1 = bw + side_gap;
y_o0  = y_in0 - wall; y_o1 = y_in1 + wall;
W     = y_o1 - y_o0;
x_end_in  = bl + usb_gap;
x_end_out = x_end_in + end_t;
x_skirt   = -sd_space;                      // inner end of the lid skirt
x_mouth   = x_skirt - plug_d;               // body open end
L_body    = x_end_out - x_mouth;
L_total   = L_body + lid_t;
y_foot    = (y_o0 + low_in) / 2;
port_z0   = z_pi_t - 0.4;
side_cz   = z_pi_t + 1.6;                   // USB-C / HDMI centre height
sx0 = usbc_x - side_cut_pad;
sx1 = hdmi ? hdmi_x[1] + 6 : usbc_x + side_cut_pad;
sz0 = z_pi_b - plug_step;                   // window bottom
sz1 = side_cz + side_cut_top;               // window top
snap_z = [zf + (z_roof - zf) * 0.3, zf + (z_roof - zf) * 0.72];
snap_x = [x_mouth + 2.2, x_mouth + 5.0];
sv_z = [zd + fence_h + 1.2, z_plb - 1.2];   // side vent band (recess between the lips)

// ------------------------------------------------------------ helpers
module rrect2(p0, p1, r) {         // 2D rounded rectangle from corner p0 to p1
    rr = max(0.01, min(r, (p1[0] - p0[0]) / 2 - 0.01, (p1[1] - p0[1]) / 2 - 0.01));
    translate(p0 + [rr, rr]) offset(rr) square([p1[0] - p0[0] - 2 * rr, p1[1] - p0[1] - 2 * rr]);
}
module along_x(x0, x1) {           // extrude a YZ profile along X
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0) children();
}
module rect(y0, z0, y1, z1) { translate([y0, z0]) square([y1 - y0, z1 - z0]); }

// cavity profile with both lips (u = Y, v = Z)
module cav_lipped() {
    rect(y_in0, z_pi_b + fence_h, y_in1, z_roof);                        // upper zone
    rect(-fence_gap, z_pi_b, bw + fence_gap, z_pi_b + fence_h + 0.01);    // Pi between fences
    rect(pi_ledge, z_plb - 0.01, bw - pi_ledge, z_pi_b + 0.01);          // between upper ledges
    rect(y_in0, zd + fence_h, y_in1, z_plb);                             // recess between the lips
    rect(-fence_gap, zd, bw + fence_gap, zd + fence_h + 0.01);           // Duo between fences
    rect(duo_ledge, z_dlb - 0.01, bw - duo_ledge, zd + 0.01);            // between lower ledges
    rect(low_in, zf, bw - low_in, z_dlb);                                // SSD bay
}
module cav_mouth() { rrect2([y_in0, zf], [y_in1, z_roof], 1.5); }
module outer2() { rrect2([y_o0, 0], [y_o1, H], r_out); }

// ------------------------------------------------------------ BODY
module vent_slots(z0, z1, ylo, yhi, xlo, xhi) {
    n = floor((yhi - ylo - vent_w) / vent_pitch) + 1;
    off = ((yhi - ylo) - ((n - 1) * vent_pitch + vent_w)) / 2;
    segs = floor((xhi - xlo + vent_bar) / (vent_seg + vent_bar));
    sl = (xhi - xlo - (segs - 1) * vent_bar) / segs;
    for (i = [0 : n - 1], s = [0 : segs - 1])
        translate([xlo + s * (sl + vent_bar), ylo + off + i * vent_pitch, z0 - 0.01])
            hull() for (dx = [vent_w / 2, sl - vent_w / 2])
                translate([dx, vent_w / 2, 0]) cylinder(d = vent_w, h = z1 - z0 + 0.02, $fn = 20);
}
module lip_leadin() {  // chamfer the ledge tops where the boards ride on
    for (s = [0, 1], zt = [zd, z_pi_b]) {
        y0 = s == 0 ? y_in0 - 1 : bw - duo_ledge - 0.01;
        y1 = s == 0 ? duo_ledge + 0.01 : y_in1 + 1;
        translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0)
            polygon([[x_lip0 - 0.01, zt - 1.6], [x_lip0 - 0.01, zt + fence_h + 1], [x_lip0 + 2.4, zt + fence_h + 1]]);
    }
}
module side_slots() {
    segs = [[4, 26], [30, 52], [56, 78]];
    for (s = segs, y = [y_o0 - 1, y_in1 - 1])
        translate([s[0], y, sv_z[0]]) hull() for (x = [s[0] + 1.5, s[1] - 1.5] - [s[0], s[0]])
            translate([x, 0, (sv_z[1] - sv_z[0]) / 2]) rotate([-90, 0, 0])
                cylinder(d = min(3.5, sv_z[1] - sv_z[0]), h = wall + 2, $fn = 20);
}
module body() {
    difference() {
        difference() {
            along_x(x_mouth, x_end_out) outer2();
            along_x(x_lip0, x_end_in) cav_lipped();
            along_x(x_mouth - 1, x_lip0 + 0.01) cav_mouth();
        }
        lip_leadin();
        // USB end: RJ45 + 2x USB-A
        translate([x_end_in - 0.5, 0, 0]) rotate([90, 0, 90]) linear_extrude(end_t + 1) {
            rrect2([eth_y - eth_cut[0] / 2, port_z0], [eth_y + eth_cut[0] / 2, port_z0 + eth_cut[1]], 1);
            for (y = usb_y) rrect2([y - usb_cut[0] / 2, port_z0], [y + usb_cut[0] / 2, port_z0 + usb_cut[1]], 1);
        }
        // long side: USB-C (+ micro HDMI) window. Inside the wall it also drops the
        // upper lip's outer half by plug_step so a plug overmold passes under the Pi's edge.
        translate([sx0, y_o0 - 1, sz0]) cube([sx1 - sx0, wall + side_gap + 1 - plug_reach, sz1 - sz0]);
        // lid snap windows
        for (y = [y_o0 - 1, y_in1 - 1], z = snap_z)
            translate([snap_x[0], y, z - 4.5]) cube([snap_x[1] - snap_x[0], wall + 2, 9]);
        // thumb notch to lift the lid
        translate([x_mouth - 0.1, bw / 2 - 8, H - 1.2]) cube([1.6, 16, 2]);
        // vents
        vent_slots(z_roof - 0.5, H + 0.5, 0, bw, -7, 83);
        vent_slots(-0.5, zf + 0.5, low_in + 2, bw - low_in - 2, -7, 83);
        if (side_vents) side_slots();
        // feet: heat-set insert holes + locating recesses
        for (x = foot_x, y = [y_foot, bw - y_foot]) {
            translate([x, y, -1]) cylinder(d = insert_d, h = 1 + foot_recess + insert_depth);
            translate([x, y, -1]) cylinder(d = foot_d + 0.4, h = 1 + foot_recess);
        }
    }
}

// ------------------------------------------------------------ LID (built in place, outer face at x_mouth - lid_t)
l_yi = [y_in0 + fit, y_in1 - fit];              // skirt outer faces
l_zi = [zf + fit, z_roof - fit];
l_z    = snap_z[1];                              // hook centre = upper window centre
l_free = l_z - latch_w / 2 - 1.0;                // arm's free end
l_root = l_zi[1] - skirt - 0.6;                  // arm's fixed end, under the skirt's top wall
l_len  = l_root - l_z;                           // root -> hook
l_hx   = [snap_x[0] + 0.2, snap_x[0] + 0.2 + latch_hook, snap_x[0] + 0.5 + latch_hook, snap_x[1] - 0.1];
l_flex = latch_hook - fit;                       // arm deflection to pass the wall
l_strain = 1.5 * latch_t * l_flex / (l_len * l_len);

module latch_cuts(s) {
    yf = l_yi[s]; sg = s == 0 ? 1 : -1;          // sg points inward
    yin = [yf + sg * latch_t, yf + sg * (latch_t + latch_slot)];
    yout = [yf, yf - sg * latch_gap];
    module slot2(ya, yb, z0, z1) {               // YZ slot with a round end at the root
        r = abs(yb - ya) / 2; yc = (ya + yb) / 2;
        hull() { translate([min(ya, yb), z0]) square([2 * r, 0.01]); translate([yc, z1 - r]) circle(r = r, $fn = 24); }
    }
    along_x(x_mouth - lid_t - 1, x_skirt + 1) slot2(yin[0], yin[1], l_free - latch_end, l_root);
    along_x(x_mouth - lid_t - 1, x_mouth + 0.01) slot2(yout[0], yout[1], l_free - latch_end, l_root);
    along_x(x_mouth - lid_t - 1, x_skirt + 1)
        translate([min(yin[1], yout[1]), l_free - latch_end]) square([abs(yin[1] - yout[1]), latch_end]);
}
module latch_hook(s) {   // 45 deg retaining face (prints as a 45 deg overhang), ~40 deg lead-in
    yf = l_yi[s] + (s == 0 ? 0.01 : -0.01); sg = s == 0 ? -1 : 1;   // sg points outward
    h = latch_hook;
    translate([0, yf, l_z - latch_w / 2]) linear_extrude(latch_w)
        polygon([[l_hx[0], 0], [l_hx[1], sg * h], [l_hx[2], sg * h], [l_hx[3], 0]]);
}

module lid_asm() {
    yi0 = l_yi[0]; yi1 = l_yi[1]; zi0 = l_zi[0]; zi1 = l_zi[1];
    union() {
        difference() {
            union() {
                along_x(x_mouth - lid_t, x_mouth) outer2();
                // skirt, chamfered on its leading edge
                difference() {
                    union() {
                        along_x(x_mouth - 0.01, x_skirt - lead_c) rrect2([yi0, zi0], [yi1, zi1], 1.25);
                        hull() {
                            along_x(x_skirt - lead_c - 0.01, x_skirt - lead_c) rrect2([yi0, zi0], [yi1, zi1], 1.25);
                            along_x(x_skirt - 0.01, x_skirt) rrect2([yi0 + lead_c, zi0 + lead_c], [yi1 - lead_c, zi1 - lead_c], 0.65);
                        }
                    }
                    along_x(x_mouth, x_skirt + 1) rrect2([yi0 + skirt, zi0 + skirt], [yi1 - skirt, zi1 - skirt], 0.5);
                }
            }
            if (latch) for (s = [0, 1]) latch_cuts(s);
        }
        if (latch) for (s = [0, 1]) latch_hook(s);
        // prongs, clear of the PCIe ribbon in the middle:
        // both corners of the Duo, and the Pi's GPIO-side corner only
        // (its USB-C-side corner is left free: the Pi 5 power button is by the USB-C)
        for (yr = [[yi0, 1.5], [bw - 1.5, yi1]])
            translate([x_mouth - 0.01, yr[0], zd - 0.2]) cube([prong_tip - x_mouth + 0.01, yr[1] - yr[0], pcb + 1.2]);
        translate([x_mouth - 0.01, bw - 1.5, z_pi_b - 0.2]) cube([prong_tip - x_mouth + 0.01, yi1 - bw + 1.5, pcb + 1.2]);
    }
}
module lid_print() { rotate([0, -90, 0]) translate([-(x_mouth - lid_t), 0, 0]) lid_asm(); }

// printed counterbore-up (no overhang); fit with the counterbore facing the desk
// screw stack (case frame, z = 0 at the case bottom): head seat, tip, hole and insert ends
foot_seat = foot_recess - (foot_h - foot_cb[1]);
foot_tip = foot_seat + foot_screw;
assert(foot_tip <= foot_recess + min(insert_len, 5.4) - 0.3, "foot screw would bottom out");
module feet() { for (i = [0 : 3]) translate([i * (foot_d + 3), 0, 0]) difference() {
    cylinder(d = foot_d, h = foot_h);
    translate([0, 0, -1]) cylinder(d = 3.4, h = foot_h + 2);
    translate([0, 0, foot_h - foot_cb[1]]) cylinder(d = foot_cb[0], h = foot_cb[1] + 1);
} }

// ------------------------------------------------------------ DIN RAIL BRACKET
// Local frame for printing: u = case X, v = case Y, z = 0 on the bed (the rail side).
// In the assembly it sits at z = -din_H under the case floor.
din_uc = (foot_x[0] + foot_x[1]) / 2;       // rail centre line
din_H  = din_plate + din_gap;               // bed -> case floor
din_ledge = din_lip + din_slot;             // rail flange front face (contact ledge)
d_ut = din_uc - din_rail_w / 2;             // latch-side flange edge
d_ub = din_uc + din_rail_w / 2;             // hook-side flange edge
d_vc = bw / 2;
d_v0 = y_foot - din_rib / 2;  d_v1 = bw - y_foot + din_rib / 2;
d_u0 = foot_x[0] - din_boss / 2;  d_u1 = foot_x[1] + din_boss / 2;
d_h0 = d_ut - din_play - 2.75;              // latch head, wall-side end
d_h1 = d_ut + din_latch;                    // latch lip tip
d_cA1 = d_h0 - din_travel - 0.6;            // flexure cavity
d_cA0 = foot_x[0] + din_boss / 2 + 1.5;
d_pk0 = d_ut - din_play - din_hook - 0.5;   // pocket beside the head: room to hook on the far side first
d_win = [d_ub + din_play + 4.5, foot_x[1] - din_boss / 2 - 0.5];

module din_frame() {
    // plate, side ribs, bosses, gussets along the spine
    translate([d_u0, d_v0, 0]) cube([d_u1 - d_u0, d_v1 - d_v0, din_plate]);
    for (v = [d_v0, d_v1 - din_rib]) translate([d_u0, v, 0]) cube([d_u1 - d_u0, din_rib, din_H]);
    for (u = foot_x, v = [y_foot, bw - y_foot]) translate([u, v, 0]) {
        cylinder(d = din_boss, h = din_H);
        translate([0, 0, din_H - 0.01]) cylinder(d = foot_d - 0.4, h = 0.5);    // spigot into the foot recess
    }
    for (s = [0, 1]) {
        vr = s == 0 ? d_v0 + din_rib : d_v1 - din_rib;
        sg = s == 0 ? 1 : -1;
        translate([d_pk0, vr, din_plate - 0.01]) rotate([90, 0, 90]) linear_extrude(d_ub - d_pk0)
            polygon([[0, 0], [sg * 5, 0], [0, 5]]);
    }
}
module din_cuts() {
    // rail pocket below the contact ledge (open both ends: the rail runs through)
    translate([d_pk0, -50, -1]) cube([d_ub - din_hook - d_pk0, 200, din_ledge + 1]);
    // flange slot above the fixed hook lip
    translate([d_ub - din_hook - 0.01, -50, din_lip]) cube([din_hook + din_play + 0.01, 200, din_slot]);
    // latch head clearance (lets it travel), tongue slot through the end bar, flexure cavity
    translate([d_cA1, d_vc - din_head_w / 2 - 0.6, -1]) cube([d_h1 + 0.6 - d_cA1, din_head_w + 1.2, din_plate + 2]);
    translate([d_u0 - 1, d_vc - din_tongue_w / 2 - 0.6, -1]) cube([d_h0 - d_u0 + 1, din_tongue_w + 1.2, din_plate + 2]);
    translate([d_cA0, d_v0 + din_rib + 0.5, -1]) cube([d_cA1 - d_cA0 + 0.01, d_v1 - d_v0 - 2 * din_rib - 1, din_plate + 2]);
    // window on the hook side for air
    translate([d_win[0], d_v0 + din_rib, -1]) cube([d_win[1] - d_win[0], d_v1 - d_v0 - 2 * din_rib, din_plate + 2]);
    // M3 counterbored holes
    for (u = foot_x, v = [y_foot, bw - y_foot]) translate([u, v, -1]) {
        cylinder(d = 3.4, h = din_H + 3);
        cylinder(d = din_cb[0], h = din_cb[1] + 1);
    }
}
module din_latch() {
    beam_v0 = d_v0 + din_rib - 0.5; beam_v1 = d_v1 - din_rib + 0.5;   // ends buried 1 mm in the plate
    difference() {
        union() {
            // head with the lip
            translate([d_h0, d_vc - din_head_w / 2, 0]) cube([d_h1 - d_h0, din_head_w, din_plate]);
            // tongue + pull tab
            translate([d_u0 - din_tab, d_vc - din_tongue_w / 2, 0]) cube([d_h0 - d_u0 + din_tab + 0.01, din_tongue_w, din_plate]);
            // stop wing: hits the end bar after din_travel
            translate([d_cA0 + din_travel, d_vc - 13, 0]) cube([0.8, 26, din_plate]);
            // two flexure beams, anchored in the plate beside the side ribs
            for (u = [d_cA0 + din_travel + 2.0, d_cA1 - 1.6])
                translate([u, beam_v0, 0]) cube([din_beam, beam_v1 - beam_v0, din_plate]);
        }
        // flange slot over the lip, and the lead-in ramp on the lip's wall side
        translate([d_ut - din_play, -50, din_lip]) cube([10, 200, din_slot]);
        translate([0, d_vc + din_head_w, 0]) rotate([90, 0, 0]) linear_extrude(din_head_w * 2)
            polygon([[d_ut - din_play - 0.35, -0.01], [d_h1 + 0.01, -0.01], [d_h1 + 0.01, din_lip - 0.4]]);
        // screwdriver slot in the tab
        translate([d_u0 - din_tab + 1.6, d_vc - 3.5, -1]) cube([2.2, 7, din_plate + 2]);
    }
}
module din_bracket() {
    union() {
        difference() { din_frame(); din_cuts(); }
        din_latch();
    }
}
module din_rail(len = 120) {   // TS35 x 7.5 for the assembly view, in the bracket frame
    t = 1.0;
    translate([0, d_vc - len / 2, din_ledge]) rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(len)
        polygon([[d_ut, 0], [d_ub, 0], [d_ub, -t], [din_uc + 13.5, -t], [din_uc + 13.5, -7.5], [din_uc - 13.5, -7.5],
                 [din_uc - 13.5, -t], [d_ut, -t]]);
}

// ------------------------------------------------------------ info for the drawing script
module info() {
    echo(str("INFO{",
      "\"bl\":", bl, ",\"bw\":", bw, ",\"pcb\":", pcb,
      ",\"duo_gap\":", duo_gap, ",\"drive_drop\":", drive_drop,
      ",\"hat\":[", hat_l, ",", hat_w, ",", hat_gap, ",", hat_comp, "]", ",\"port_over\":", port_over,
      ",\"fence_gap\":", fence_gap, ",\"fence_h\":", fence_h, ",\"pi_ledge\":", pi_ledge, ",\"pi_lip_t\":", pi_lip_t,
      ",\"duo_ledge\":", duo_ledge, ",\"duo_lip_t\":", duo_lip_t, ",\"low_in\":", low_in, ",\"x_lip0\":", x_lip0,
      ",\"plug_step\":", plug_step, ",\"plug_reach\":", plug_reach,
      ",\"side_gap\":", side_gap, ",\"air_top\":", air_top, ",\"air_below\":", air_below,
      ",\"sd_space\":", sd_space, ",\"usb_gap\":", usb_gap,
      ",\"wall\":", wall, ",\"floor_t\":", floor_t, ",\"roof_t\":", roof_t, ",\"end_t\":", end_t,
      ",\"zf\":", zf, ",\"zd\":", zd, ",\"z_dlb\":", z_dlb, ",\"z_plb\":", z_plb,
      ",\"z_duo_t\":", z_duo_t, ",\"z_pi_b\":", z_pi_b, ",\"z_pi_t\":", z_pi_t,
      ",\"z_hat_b\":", z_hat_b, ",\"z_hat_t\":", z_hat_t, ",\"z_hat_c\":", z_hat_c, ",\"z_roof\":", z_roof, ",\"H\":", H,
      ",\"y_in\":[", y_in0, ",", y_in1, "],\"y_o\":[", y_o0, ",", y_o1, "],\"W\":", W,
      ",\"x_mouth\":", x_mouth, ",\"x_skirt\":", x_skirt, ",\"x_end_in\":", x_end_in, ",\"x_end_out\":", x_end_out,
      ",\"L_body\":", L_body, ",\"L_total\":", L_total, ",\"lid_t\":", lid_t, ",\"plug_d\":", plug_d, ",\"prong_tip\":", prong_tip,
      ",\"eth\":[", eth_y, ",", eth_cut[0], ",", eth_cut[1], "],\"usb_y\":", usb_y, ",\"usb_cut\":", usb_cut,
      ",\"port_z0\":", port_z0, ",\"usbc_x\":", usbc_x, ",\"hdmi_x\":", hdmi_x, ",\"side\":[", sx0, ",", sx1, ",", side_cz, ",", sz0, ",", sz1, "]",
      ",\"snap_x\":", snap_x, ",\"snap_z\":", snap_z,
      ",\"latch\":{\"z\":", l_z, ",\"free\":", l_free, ",\"root\":", l_root, ",\"len\":", l_len, ",\"t\":", latch_t,
      ",\"hook\":", latch_hook, ",\"w\":", latch_w, ",\"hx\":", l_hx, ",\"slot\":", latch_slot, ",\"gap\":", latch_gap,
      ",\"flex\":", l_flex, ",\"strain\":", l_strain, "}", ",\"sv_z\":", sv_z,
      ",\"foot\":[", foot_d, ",", foot_h, "],\"foot_x\":", foot_x, ",\"y_foot\":", y_foot,
      ",\"foot_cb\":", foot_cb, ",\"foot_screw\":", foot_screw, ",\"foot_seat\":", foot_seat, ",\"foot_tip\":", foot_tip,
      ",\"foot_recess\":", foot_recess, ",\"insert\":[", insert_d, ",", insert_len, ",", insert_depth, "]",
      ",\"din\":{\"uc\":", din_uc, ",\"H\":", din_H, ",\"plate\":", din_plate, ",\"gap\":", din_gap, ",\"ledge\":", din_ledge,
      ",\"ut\":", d_ut, ",\"ub\":", d_ub, ",\"u0\":", d_u0, ",\"u1\":", d_u1, ",\"v0\":", d_v0, ",\"v1\":", d_v1,
      ",\"tab\":", din_tab, ",\"hook\":", din_hook, ",\"latch\":", din_latch, ",\"travel\":", din_travel, ",\"lip\":", din_lip,
      ",\"slot\":", din_slot, ",\"rib\":", din_rib, ",\"cb\":", din_cb, "}",
      "}"));
}

// ------------------------------------------------------------ dispatch
if (part == "body") rotate([0, 90, 0]) translate([-x_end_out, 0, 0]) body();   // USB end down
else if (part == "body_asm") body();
else if (part == "lid") lid_print();
else if (part == "lid_asm") lid_asm();
else if (part == "feet") feet();
else if (part == "din") din_bracket();                                 // rail side on the bed
else if (part == "din_asm") translate([0, 0, -din_H]) din_bracket();   // in place under the case
else if (part == "din_rail") translate([0, 0, -din_H]) din_rail();
else if (part == "info") { info(); cube(1); }
else { body(); %lid_asm(); info(); }
