// Fishbone / French braid tool — serpentine strip with a hook, for TPU (or PETG)
// Prints flat, no supports. Origin: X centred, Y = 0 at the bottom (tail) end, Z up.
//
// Shape: straight runs across the width, joined by semicircular U-turns that
// alternate left/right. Each U-turn leaves a slot open on the opposite side;
// hair strands are fed into those slots alternately from left and right.
// Top end: quarter turn into a straight stem and a downward-opening hook.
//
//   openscad -o stl/braid_tool.stl braid_tool.scad
//   openscad -o stl/braid_coupon.stl -D 'part="coupon"' braid_tool.scad
//   openscad -o info.echo -D 'part="info"' braid_tool.scad   (derived numbers as JSON)

/* [Part] */
part = "tool";        // [tool, coupon, info]

/* [Overall] */
L  = 190;             // overall length incl. hook (retail ones are ~190)
W  = 25;              // overall width across the serpentine (retail ~25)
w  = 4.5;             // strand width, in plane. Stretch stiffness of the zigzag ~ w^3
t  = 4.0;             // strand thickness = print height. Floppiness toward/away from the head ~ t^3
p  = 10;              // run pitch, centre to centre. Hair slot gap = p - w

/* [Hook] */
hook      = true;
stem_min  = 4;        // minimum straight stem above the last lobe (absorbs rounding of run count)
hook_r    = 4.5;      // hook centreline radius. Hook gap = 2*hook_r - w
hook_tail = 3;        // straight tail after the hook

/* [Edges — hair snag control] */
top_r = 1.5;          // top edge round-over radius (prints as fine steps, no overhang)
bot_c = 0.5;          // bottom edge 45° chamfer (kills TPU elephant-foot lip)

/* [Coupon] */
coupon_L = 50;        // short test piece: same section, 4-ish runs + hook

/* [Detail] */
arc_seg = 16;         // segments per half circle on the centreline
$fn     = 24;         // strand end circles
z_step  = 0.25;       // slab height for the edge profile

// ---------------------------------------------------------------- derived
A   = (W - w) / 2;            // centreline half-extent across
r_u = p / 2;                  // U-turn centreline radius
xc  = A - r_u;                // U-turn centre x (straight run = 2*xc)
assert(xc >= 0, "W too narrow for pitch p: need W - w >= p");
assert(p > w, "pitch p must exceed strand width w (else slots close)");

function top_len() = hook ? r_u + stem_min + hook_r + w/2 : w/2;
function n_runs(ln) = floor((ln - w/2 - top_len()) / p) + 1;
function stem_eff(ln) = ln - (w/2 + (n_runs(ln) - 1) * p + r_u + hook_r + w/2);

function arc(c, r, a0, a1, n) =
    [for (k = [0:n]) c + r * [cos(a0 + (a1 - a0) * k / n), sin(a0 + (a1 - a0) * k / n)]];

// centreline points, bottom to top
function centreline(ln) =
    let(n   = n_runs(ln),
        y0  = w / 2,
        yl  = y0 + (n - 1) * p,
        s   = ((n - 1) % 2 == 0) ? 1 : -1,     // side the last run ends on
        ys  = yl + r_u + stem_eff(ln))
    concat(
        [for (i = [0:n - 1])
            let(d = (i % 2 == 0) ? 1 : -1, y = y0 + i * p)
            each concat([[-d * xc, y]],
                        i < n - 1 ? arc([d * xc, y + r_u], r_u, -90, d > 0 ? 90 : -270, arc_seg)
                                  : [[d * xc, y]])],
        hook ? concat(
            arc([s * xc, yl + r_u], r_u, -90, s > 0 ? 0 : -180, arc_seg / 2),   // quarter turn up
            [[s * A, ys]],                                                       // stem
            arc([s * (A - hook_r), ys], hook_r, s > 0 ? 0 : 180, s > 0 ? 180 : 0, arc_seg),
            [[s * (A - 2 * hook_r), ys - hook_tail]])                            // tail
        : []);

module strand2d(ln) {
    P = centreline(ln);
    for (i = [0:len(P) - 2])
        hull() { translate(P[i]) circle(d = w); translate(P[i + 1]) circle(d = w); }
}

// edge profile: inset of the outline at height z
function inset(z) =
    z < bot_c ? bot_c - z :
    z > t - top_r ? top_r - sqrt(max(0, top_r * top_r - pow(z - (t - top_r), 2))) : 0;

// slab boundaries: fine steps through the chamfer and round-over, one slab in between
function zs() = concat(
    [for (z = [0:z_step:bot_c - 0.001]) z],
    [bot_c],
    [for (z = [t - top_r:z_step:t - 0.001]) z],
    [t]);

module tool3d(ln) {
    Z = zs();
    for (k = [0:len(Z) - 2])
        let(z0 = Z[k], z1 = Z[k + 1], zm = (z0 + z1) / 2,
            ins = (z1 <= bot_c) ? inset(zm) : (z0 >= t - top_r) ? inset(zm) : 0)
        translate([0, 0, z0])
            linear_extrude(height = z1 - z0 + (k < len(Z) - 2 ? 0.001 : 0))
                if (ins > 0.001) offset(r = -ins) strand2d(ln); else strand2d(ln);
}

module info(ln) {
    n = n_runs(ln);
    echo(str("INFO {\"length\":", ln, ",\"width\":", W, ",\"thickness\":", t,
             ",\"strand\":", w, ",\"pitch\":", p, ",\"slot_gap\":", p - w,
             ",\"runs\":", n, ",\"slots_a\":", ceil((n - 1) / 2), ",\"slots_b\":", floor((n - 1) / 2),
             ",\"slots_total\":", n - 1, ",\"stem\":", hook ? stem_eff(ln) : 0,
             ",\"hook_gap\":", hook ? 2 * hook_r - w : 0,
             ",\"top_r\":", top_r, ",\"bot_c\":", bot_c, "}"));
}

if (part == "tool")   { info(L); tool3d(L); }
if (part == "coupon") { info(coupon_L); tool3d(coupon_L); }
if (part == "info")   { info(L); info(coupon_L); }
