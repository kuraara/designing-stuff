// Smiggle bottle bumper: TPU replacement for the silicone boot on the bottle's base,
// with a name embossed (raised) or debossed on the side wall.
//
// Use orientation = print orientation: floor on the bed, opening up.
// Origin: Z = 0 on the bed, Z axis = bottle axis. The name faces -Y (front of the plate).
//
// Made for PrusaSlicer's spiral vase mode: the floor prints as normal solid layers, then the
// wall is one continuous spiral of a single line `wall` wide that follows the OUTSIDE of the
// model (letters included). The slicer ignores the inside of the wall, so the bore comes out at
// OD - 2 * wall. That's why the wall here is exactly one line wide, with no inside chamfer or
// fillet: what's modelled is what prints.
//
//   openscad -o bumper.stl -D 'name="Aubrey"' bumper.scad         standalone (slow in 2021.01)
//   openscad -o ring.stl -D 'part="ring"' -D 'ring=1' bumper.scad   fit ring 1 of gauge_fits
//   python3 bumper.py --name Aubrey                               fast path (manifold3d), ~1 s
//
// bumper.py reads the 2D parts (profile2d, text2d, probe) from this file and does the 3D itself.

// Bundled font (SIL OFL), registered so nothing needs installing.
use <fonts/Sniglet-ExtraBold.ttf>

/* [Part] */
part = "bumper";            // [bumper, ring, gauge, profile2d, text2d, probe, info]

/* [Name] */
name = "Aubrey";
// Any font OpenSCAD can see, "Family:style=Style".
font = "Sniglet:style=ExtraBold";
// OpenSCAD text size. bumper.py sets this from the cap height it measures (--letter-h).
text_size = 10;
// Cap height / text_size, for centring when run standalone (Sniglet ExtraBold in OpenSCAD: 1.0).
cap_ratio = 1.0;
spacing = 1.0;
// Letter relief in mm: + raised (emboss), - cut into the wall (deboss).
emboss = 0.8;
// How far raised letters sink into the wall, so they fuse with it.
emboss_root = 0.3;
// Baseline height above the bed. 0 = auto: cap band centred on the straight outer wall.
baseline_z = 0;
// Horizontal shift of the name, mm along the wall (bumper.py centres the ink exactly).
text_dx = 0;
// Where the name sits, degrees about Z. 0 = front (-Y).
text_angle = 0;
// Number of copies of the name, spread evenly round the wall.
copies = 1;

/* [Bottle (measured)] */
// Diameter of the stepped-down base section the bumper goes over.
bottle_d = 72;
// Body diameter above the 45° step (for the drawing; the bumper is not wider than this).
body_d = 76;
// From the start of the 45° step down to the bottom of the bottle.
seat_depth = 20;
// The bottle's bottom edge radius (estimated from the photo).
base_r = 5;

/* [Bumper] */
// Stretch fit: printed bore = bottle_d - fit. 1.6 on a 0.8 wall grips about like 0.8 on 1.6.
fit = 1.6;
// Wall = the vase-mode line width (slice with perimeter widths = wall).
wall = 0.8;
// Floor: printed as normal solid layers (bottom_solid_layers = floor_t / layer height).
floor_t = 2.0;
// Centre hole in the floor (original: 37.5).
hole_d = 37.5;
// 45° chamfer inside the rim, to sit in the bottle's step. 0 for vase mode (it can't print it).
top_c = 0;
// 45° chamfer on the outside bottom edge (also hides elephant foot).
bot_c = 1.6;
// Fillet inside, floor to wall. 0 for vase mode (it can't print it).
inner_r = 0;

/* [Fit rings] */
// One ring per value of fit. Ring n has n lugs (1 = tightest).
gauge_fits = [2.2, 1.6, 1.0];
// Which ring part="ring" makes (1-based).
ring = 2;
gauge_h = 6;
gauge_gap = 5;

/* [Detail] */
$fn = 240;
// Strip width for wrapping the name round the wall in standalone OpenSCAD.
wrap_step = 0.5;
// Widest name the standalone wrap covers, degrees of arc.
wrap_max_deg = 150;

// ---------------------------------------------------------------- derived
r_b = (bottle_d - fit) / 2;           // printed bore radius
r_o = r_b + wall;                     // outer radius
r_h = hole_d / 2;
H   = floor_t + seat_depth + top_c;   // overall height
assert(top_c == 0 || top_c < wall, "top_c must be less than wall");
assert(inner_r < seat_depth, "inner_r too big");
assert(r_h < r_b - inner_r, "hole_d too big for the floor");

cap_h   = text_size * cap_ratio;
base_z  = baseline_z > 0 ? baseline_z : (bot_c + H) / 2 - cap_h / 2;

// ---------------------------------------------------------------- 2D
function arc(c, r, a0, a1, n = 24) =
    [for (k = [0:n]) c + r * [cos(a0 + (a1 - a0) * k / n), sin(a0 + (a1 - a0) * k / n)]];

// Half section in the r-z plane (x = radius, y = height).
function profile_pts(rb, h_top, with_floor = true) =
    let(ro = rb + wall)
    with_floor ?
      concat(
        [[r_h, 0], [ro - bot_c, 0], [ro, bot_c], [ro, h_top]],
        top_c > 0 ? [[rb + top_c, h_top], [rb, h_top - top_c]] : [[rb, h_top]],
        inner_r > 0 ? arc([rb - inner_r, floor_t + inner_r], inner_r, 0, -90) : [[rb, floor_t]],
        [[r_h, floor_t]])
    : [[rb, 0], [ro, 0], [ro, h_top], [rb, h_top]];

module profile2d() { polygon(profile_pts(r_b, H)); }

// The name, flat: x = distance along the wall, y = height, baseline at y = 0.
module name2d() {
    translate([text_dx, 0])
        text(name, size = text_size, font = font, halign = "center", valign = "baseline",
             spacing = spacing);
}

// ---------------------------------------------------------------- 3D
module body() { rotate_extrude() profile2d(); }

// Wrap name2d round a cylinder of radius r, from r + d0 out to r + d1 (radially).
// Cut into vertical strips wrap_step wide, each turned to its own angle.
module wrapped_name(r, d0, d1) {
    w = 2 * PI * r * wrap_max_deg / 360;
    n = ceil(w / wrap_step);
    for (i = [0:n - 1]) {
        x0 = -w / 2 + i * wrap_step;
        xc = x0 + wrap_step / 2;
        rotate([0, 0, xc / r * 180 / PI])
            translate([0, -(r + d0), base_z])
                rotate([90, 0, 0])
                    linear_extrude(d1 - d0)
                        translate([-xc, 0])
                            intersection() {
                                name2d();
                                translate([x0, -100]) square([wrap_step, 200]);
                            }
    }
}

module name_ring(d0, d1) {
    for (k = [0:copies - 1])
        rotate([0, 0, text_angle + k * 360 / copies]) wrapped_name(r_o, d0, d1);
}

module bumper() {
    if (emboss >= 0)
        union() { body(); name_ring(-emboss_root, emboss); }
    else
        difference() { body(); name_ring(emboss, 0.5); }
}

// Short rings at each trial fit, n lugs on ring n.
function gauge_pos(i) = let(p = 2 * (bottle_d / 2 + wall) + gauge_gap)
    [[-p / 2, -p * sqrt(3) / 4], [p / 2, -p * sqrt(3) / 4], [0, p * sqrt(3) / 4]][i % 3];

// One fit ring: a short tube, wall one line wide, i + 1 lugs on the outside (i is 0-based).
// Vase mode prints one object at a time, so each ring is its own STL / G-code.
module fit_ring(i) {
    rb = (bottle_d - gauge_fits[i]) / 2;
    rotate_extrude() polygon(profile_pts(rb, gauge_h, false));
    for (k = [0:i])
        rotate([0, 0, (k - i / 2) * 8])
            translate([-1.5, -(rb + wall + 1.6), 0]) cube([3, 1.6 + wall / 2, gauge_h]);
}

// All rings on one plate, for viewing (print them one at a time in vase mode).
module gauge() { for (i = [0:len(gauge_fits) - 1]) translate(gauge_pos(i)) fit_ring(i); }

// Name at size 10 plus an "H" 500 mm up: bumper.py measures cap height and ink box from it.
module probe() {
    text(name, size = 10, font = font, halign = "center", valign = "baseline", spacing = spacing);
    translate([0, 500]) text("H", size = 10, font = font, valign = "baseline");
}

if (part == "bumper") bumper();
else if (part == "ring") fit_ring(ring - 1);
else if (part == "gauge") gauge();
else if (part == "profile2d") profile2d();
else if (part == "text2d") name2d();
else if (part == "probe") probe();
else if (part == "info") {
    echo(str("INFO {\"bore\": ", 2 * r_b, ", \"od\": ", 2 * r_o, ", \"height\": ", H,
             ", \"wall\": ", wall, ", \"floor\": ", floor_t, ", \"hole\": ", hole_d,
             ", \"fit\": ", fit, ", \"seat_depth\": ", seat_depth, ", \"top_c\": ", top_c,
             ", \"bot_c\": ", bot_c, ", \"inner_r\": ", inner_r, ", \"base_z\": ", base_z,
             ", \"wall_band\": [", bot_c, ", ", H, "]}"));
    cube(1);
}
