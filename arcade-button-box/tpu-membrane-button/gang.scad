// =====================================================================
//  Gang study: N TPU membrane buttons (v0.3) in a row on one top plate,
//  plus an ESP32-C3 Super Mini pocket underneath fed by a USB-C cable
//  channel. Built from tpu_button.scad's modules, so the button
//  mechanism is identical. For comparing print cost with N singles.
//
//  Print orientation (face on the bed), same as tpu_button.scad.
//  Buttons sit along Y at `pitch`; switches slide in from +X side by side.
//  The ESP32 block sits behind the row (-X): board pocket, then a wider
//  zone for the USB-C plug, then a cable channel out to the edge, all
//  open on the underside.
//
//  openscad -D 'part="gang"' -D n=3 -o stl/gang3.stl gang.scad
//  part = "gang" | "singles" (n buttons spaced on one plate) | "cradle" (ESP32 block alone)
// =====================================================================
include <tpu_button.scad>
part  = "gang";
n     = 3;
pitch = 24;       // Ø23 heads with a 1 mm gap; switches 10.3 wide -> 13.7 between them

/* [ESP32-C3 Super Mini + USB-C cable] */
esp   = [23.2, 18.6, 5.0];   // board pocket L (USB axis) x W x depth: 22.5 x 18 board + components
plug  = [18, 12.5, 7.5];     // USB-C plug overmold zone
cable = [4.5, 5.0];          // cable channel width x depth (Ø3.5-4 cable)
esp_wall = 2.0;
plate_t  = 1.6;              // top plate between and around the heads
blk_t    = plug[2] + 1.6;    // ESP block thickness (use: hangs below the top face)

yc  = (n - 1) * pitch / 2;               // row centre
blk_L = esp[0] + plug[0] + 6;            // board + plug + cable stub
blk_W = esp[1] + 2 * esp_wall + 4;
bx1 = px0 - wall;                        // block ends where the stems' end walls are
bx0 = bx1 - blk_L;

module esp_block_solid()
    translate([bx0, yc - blk_W / 2, 0]) linear_extrude(blk_t) offset(r = 2) offset(delta = -2) square([blk_L, blk_W]);

module esp_cuts() {
    zb = blk_t + 0.01;
    // board pocket next to the stems, USB end facing -X
    translate([bx1 - esp_wall - esp[0], yc - esp[1] / 2, zb - esp[2]]) cube([esp[0], esp[1], esp[2] + 1]);
    // plug zone
    translate([bx1 - esp_wall - esp[0] - plug[0], yc - plug[1] / 2, zb - plug[2]]) cube([plug[0] + 0.01, plug[1], plug[2] + 1]);
    // cable channel out of the -X edge
    translate([bx0 - 1, yc - cable[0] / 2, zb - cable[1]]) cube([blk_L - esp[0] - plug[0] - esp_wall + 1.01, cable[0], cable[1] + 1]);
}

module gang() {
    difference() {
        union() {
            for (i = [0 : n - 1]) translate([0, i * pitch, 0]) shell();
            linear_extrude(plate_t) hull() {
                for (i = [0 : n - 1]) translate([0, i * pitch]) circle(R_out);
                translate([bx0, yc - blk_W / 2]) offset(r = 2) offset(delta = -2) square([blk_L, blk_W]);
            }
            esp_block_solid();
        }
        for (i = [0 : n - 1]) translate([0, i * pitch, 0]) cuts(edge_chamfer = false);
        esp_cuts();
    }
    for (i = [0 : n - 1]) translate([0, i * pitch, 0]) { boss(); bumps(); }
}

module cradle() difference() { esp_block_solid(); esp_cuts(); }   // ESP32 holder for loose singles

if (part == "gang") gang();
else if (part == "singles") for (i = [0 : n - 1]) translate([0, i * (2 * R_out + 6), 0]) button();
else if (part == "cradle") cradle();
