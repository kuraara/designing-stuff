#!/usr/bin/env python3
"""Smiggle bottle bumper generator: name in, print-ready STL out.

Wraps bumper.scad. OpenSCAD draws the 2D parts: the half section of the bumper and the name,
flat. It also measures the name (part="probe"), so the cap height is exact in any font. This
script then revolves the section and wraps the name round the wall with manifold3d. That takes
about a second; OpenSCAD 2021.01 takes minutes to render the same thing.

    python3 bumper.py --name Aubrey                      # Sniglet ExtraBold, 12 mm capitals, raised 0.8
    python3 bumper.py --name Lincoln --png               # + a 3D preview PNG
    python3 bumper.py --name Mia --emboss -0.6           # cut into the wall instead
    python3 bumper.py --name Aubrey --set fit=1.4 --set seat_depth=21
    python3 bumper.py --list-fonts

Writes <stem>_bumper.stl (print orientation: floor down, name facing -Y) and <stem>_info.json
to --out (default ./out). Needs python3, OpenSCAD 2021.01+ (env OPENSCAD overrides the
binary), numpy and manifold3d. fontTools is optional (checks the font has every character).
xvfb-run is needed only for --png. Without manifold3d the script falls back to OpenSCAD's own
render, which is slow.
"""
import argparse, json, math, os, re, struct, subprocess, sys, tempfile, time, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SCAD = HERE / "bumper.scad"
FONT_DIR = HERE / "fonts"
OPENSCAD = os.environ.get("OPENSCAD", "openscad")
DEFAULT_FONT = "Sniglet:style=ExtraBold"
NUM = r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
TEXT_FN = 64          # $fn for text curves in the 2D exports (240 makes huge outlines)
REFINE = 1.0          # max edge length before wrapping the letters (mm)
MARGIN = 0.8          # keep the letters this far from the bottom chamfer and the rim


# ------------------------------------------------------------------ OpenSCAD plumbing

def scad_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(float(v), 4))
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(scad_value(x) for x in v) + "]"
    s = str(v)
    if any(ord(c) < 32 for c in s):
        raise ValueError("control characters are not allowed")
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_value(s):
    if s in ("true", "false"):
        return s == "true"
    try:
        return float(s)
    except ValueError:
        return s


def openscad(out, params, part, extra=None, timeout=3000):
    cmd = [OPENSCAD, "-o", str(out)]
    for k, v in {**params, "part": part, **(extra or {})}.items():
        cmd += ["-D", f"{k}={scad_value(v)}"]
    cmd.append(str(SCAD))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0 or not pathlib.Path(out).exists():
        raise RuntimeError(f"openscad {part} failed:\n{r.stderr[-1500:]}")
    return r.stderr


def scad_info(params, work):
    err = openscad(work / "info.echo", params, "info")
    m = re.search(r'ECHO: "INFO (.*)"', (work / "info.echo").read_text() + err)
    if not m:
        raise RuntimeError("no INFO from bumper.scad:\n" + err[-800:])
    return json.loads(m.group(1))


def svg_rings(path):
    """Closed rings from an OpenSCAD 2D SVG export, in model coordinates (SVG y is flipped)."""
    rings = []
    for d in re.findall(r'<path d="([^"]*)"', pathlib.Path(path).read_text()):
        for chunk in d.split("M"):
            pts = [(float(x), -float(y)) for x, y in re.findall(rf"({NUM}),({NUM})", chunk)]
            if len(pts) >= 3:
                rings.append(pts)
    return rings


def section(params, work, part, extra=None):
    p = work / f"{part}.svg"
    openscad(p, params, part, extra)
    return svg_rings(p)


def bbox(rings):
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None


# ------------------------------------------------------------------ STL

def write_stl(path, verts, tris):
    import numpy as np
    v = np.asarray(verts, dtype=np.float64)[:, :3]
    t = np.asarray(tris, dtype=np.int64)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, np.stack([a, b, c], axis=1)
    with open(path, "wb") as f:
        f.write(b"bumper.py".ljust(80, b" ") + struct.pack("<I", len(t)))
        f.write(rec.tobytes())
    return [v.min(axis=0).tolist(), v.max(axis=0).tolist()]


def stl_ascii_to_binary(path):
    data = pathlib.Path(path).read_bytes()
    if data[:5] != b"solid":
        return None
    verts = [tuple(map(float, v)) for v in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)]
    return write_stl(path, verts, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(verts) // 3)])


# ------------------------------------------------------------------ fonts

def list_fonts():
    """Bundled fonts first, then whatever fontconfig (and so OpenSCAD) can see."""
    fmt = "%{family[0]}\t%{style[0]}\t%{file}\n"

    def scan(cmd):
        try:
            r = subprocess.run([*cmd, "--format", fmt], capture_output=True, text=True, timeout=30)
            return [l.split("\t") for l in r.stdout.splitlines() if l.count("\t") == 2]
        except (OSError, subprocess.TimeoutExpired):
            return []
    fonts, seen = [], set()
    for f in sorted(FONT_DIR.glob("*.ttf")):
        for fam, style, file in scan(["fc-scan", str(f)]):
            name = f"{fam}:style={style}"
            if name not in seen:
                seen.add(name)
                fonts.append({"font": name, "bundled": True, "file": file})
    for fam, style, file in sorted(scan(["fc-list", ":"])):
        name = f"{fam}:style={style}"
        if name not in seen and file.lower().endswith((".ttf", ".otf")):
            seen.add(name)
            fonts.append({"font": name, "bundled": False, "file": file})
    return fonts


def resolve_font(font):
    """OpenSCAD silently swaps an unknown font for a default one, so unknown names are an error."""
    fam, _, rest = font.partition(":")
    style = rest.split("style=", 1)[1] if "style=" in rest else ""
    same = [f for f in list_fonts() if f["font"].split(":style=")[0].lower() == fam.strip().lower()]
    if not same:
        raise ValueError(f"font {fam!r} not found (see --list-fonts)")
    if style:
        exact = [f for f in same if f["font"].split(":style=")[1].lower() == style.lower()]
        if not exact:
            raise ValueError(f"{fam!r} has no style {style!r}; it has: "
                             + ", ".join(f["font"].split(":style=")[1] for f in same))
        return exact[0]
    regular = [f for f in same if f["font"].lower().endswith(("=regular", "=book", "=normal"))]
    return (regular or same)[0]


def missing_glyphs(font_file, text):
    try:
        from fontTools.ttLib import TTFont
        cmap = TTFont(font_file, fontNumber=0, lazy=True).getBestCmap() or {}
    except Exception:
        return []
    return sorted({c for c in text if not c.isspace() and ord(c) not in cmap})


# ------------------------------------------------------------------ 3D

def build_3d(params, info, profile, name_rings, out_stl):
    """Revolve the half section and wrap the name round the wall with manifold3d."""
    import numpy as np
    import manifold3d as mf

    fn = int(params.get("$fn", 240))
    body = mf.Manifold.revolve(mf.CrossSection([np.array(r) for r in profile], mf.FillRule.EvenOdd),
                               circular_segments=fn)
    e = float(params["emboss"])
    if abs(e) < 1e-6:
        part = body
    else:
        d0, d1 = (-float(params["emboss_root"]), e) if e > 0 else (e, 0.5)
        r_o = info["od"] / 2
        flat = mf.Manifold.extrude(
            mf.CrossSection([np.array(r) for r in name_rings], mf.FillRule.EvenOdd), d1 - d0)
        flat = flat.refine_to_length(REFINE)
        base_z = info["base_z"]
        copies = max(1, int(params["copies"]))
        letters = []
        for k in range(copies):
            a0 = math.radians(float(params["text_angle"]) + k * 360 / copies)

            def wrap(p, a0=a0):
                th = p[:, 0] / r_o + a0
                rr = r_o + d0 + p[:, 2]
                return np.column_stack([rr * np.sin(th), -rr * np.cos(th), p[:, 1] + base_z])
            letters.append(flat.warp_batch(wrap))
        name3d = mf.Manifold.batch_boolean(letters, mf.OpType.Add)
        part = body + name3d if e > 0 else body - name3d
    if part.status() != mf.Error.NoError:
        raise RuntimeError(f"manifold error: {part.status()}")
    mesh = part.to_mesh()
    write_stl(out_stl, mesh.vert_properties, mesh.tri_verts)
    return {"volume_cm3": round(part.volume() / 1000, 2), "tris": part.num_tri(),
            "genus": part.genus()}


def render_png(stl, png):
    stl, png = stl.resolve(), png.resolve()
    view = stl.with_suffix(".view.scad")
    view.write_text(f'color("#58b4e8") import("{stl.name}");\n')
    cmd = ["xvfb-run", "-a", OPENSCAD, "-o", str(png), "--imgsize=1200,900", "--colorscheme=Tomorrow",
           "--camera=0,0,10,72,0,0,195", "--projection=p", str(view)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=stl.parent)
        if not png.exists():
            print("warning: PNG preview failed:", r.stderr[-300:], file=sys.stderr)
    finally:
        view.unlink(missing_ok=True)


# ------------------------------------------------------------------ the generator

def generate(args):
    t0 = time.time()
    warnings = []
    params = {"name": args.name, "font": args.font, "emboss": args.emboss}
    for kv in args.set or []:
        k, _, v = kv.partition("=")
        params[k.strip()] = parse_value(v.strip())
    defaults = {"emboss_root": 0.3, "copies": 1, "text_angle": 0, "spacing": 1.0}
    for k, v in defaults.items():
        params.setdefault(k, v)
    if not args.name.strip():
        raise ValueError("empty name")

    fnt = resolve_font(args.font)
    miss = missing_glyphs(fnt["file"], args.name)
    if miss:
        raise ValueError(f"font {args.font!r} has no glyph for: {' '.join(miss)}")

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = args.stem or re.sub(r"[^a-z0-9]+", "_", args.name.lower()).strip("_") or "name"

    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        tp = {**params, "$fn": TEXT_FN}

        # 1. measure at size 10: the name's ink box and an H for the cap height
        rings = section(tp, work, "probe")
        name_r = [r for r in rings if max(y for _, y in r) < 250]
        h_r = [r for r in rings if min(y for _, y in r) > 250]
        nb, hb = bbox(name_r), bbox(h_r)
        if nb is None:
            raise RuntimeError(f"font {args.font!r} drew nothing for {args.name!r}")
        cap10 = hb[3] - hb[2]
        size = args.letter_h * 10 / cap10

        # 2. shrink if the name runs further round the wall than --max-deg
        info = scad_info({**params, "text_size": size, "cap_ratio": cap10 / 10}, work)
        r_o = info["od"] / 2
        max_len = r_o * math.radians(args.max_deg)
        width = (nb[1] - nb[0]) * size / 10
        if width > max_len:
            warnings.append(f"long name: capitals shrunk to {args.letter_h * max_len / width:.1f} mm "
                            f"(from {args.letter_h:g}) to keep it within {args.max_deg:g}° of the wall; "
                            "raise --max-deg to wrap it further round")
            size *= max_len / width

        # 3. the name at its final size, ink centred on x = 0, baseline at y = 0
        params.update({"text_size": round(size, 4), "cap_ratio": round(cap10 / 10, 4)})
        b0 = bbox(section({**params, "$fn": TEXT_FN}, work, "text2d"))
        params["text_dx"] = round(float(params.get("text_dx", 0)) - (b0[0] + b0[1]) / 2, 4)
        name_rings = section({**params, "$fn": TEXT_FN}, work, "text2d")
        ink = bbox(name_rings)

        # 4. height on the wall: cap band centred, then nudged so descenders clear the chamfer
        info = scad_info(params, work)
        lo_lim, hi_lim = info["wall_band"][0] + MARGIN, info["wall_band"][1] - MARGIN
        z = float(params.get("baseline_z", 0)) or info["base_z"]
        if z + ink[2] < lo_lim:
            z = lo_lim - ink[2]
        if z + ink[3] > hi_lim:
            z = hi_lim - ink[3]
            if z + ink[2] < lo_lim - 1e-6:
                warnings.append("name is taller than the wall: lower --letter-h")
        params["baseline_z"] = round(z, 3)
        info = scad_info(params, work)
        profile = section(params, work, "profile2d")

        stl = out / f"{stem}_bumper.stl"
        engine = "manifold"
        try:
            stats = build_3d(params, info, profile, name_rings, stl)
        except ImportError:
            engine = "openscad"
            openscad(stl, params, "bumper")
            stl_ascii_to_binary(stl)
            stats = {}

    if args.png:
        render_png(stl, out / f"{stem}_bumper.png")

    arc = math.degrees((ink[1] - ink[0]) / r_o)
    res = {
        "name": args.name, "font": args.font, "letter_h": round(size * cap10 / 10, 2),
        "text_size": params["text_size"], "emboss": params["emboss"],
        "name_len": round(ink[1] - ink[0], 1), "name_arc_deg": round(arc, 1),
        "letters_z": [round(params["baseline_z"] + ink[2], 2), round(params["baseline_z"] + ink[3], 2)],
        "bumper": {k: info[k] for k in ("bore", "od", "height", "wall", "floor", "hole", "fit",
                                        "seat_depth", "top_c", "bot_c", "inner_r")},
        "params": {k: v for k, v in params.items() if k not in ("name", "font")},
        "mesh": stats, "warnings": warnings, "stl": stl.name, "engine": engine,
        "seconds": round(time.time() - t0, 1),
    }
    (out / f"{stem}_info.json").write_text(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="text on the bumper")
    ap.add_argument("--font", default=DEFAULT_FONT, help=f"default {DEFAULT_FONT!r}")
    ap.add_argument("--letter-h", type=float, default=12.0, help="capital height, mm (default 12)")
    ap.add_argument("--max-deg", type=float, default=120.0,
                    help="longest the name may run round the wall, degrees (default 120)")
    ap.add_argument("--emboss", type=float, default=0.8,
                    help="letter relief, mm: + raised (default 0.8), - cut in")
    ap.add_argument("--set", action="append", metavar="KEY=VALUE",
                    help="any bumper.scad parameter, e.g. fit=1.4 seat_depth=21 copies=2")
    ap.add_argument("--out", default="out")
    ap.add_argument("--stem", help="file name stem (default: from the name)")
    ap.add_argument("--png", action="store_true", help="also render a 3D preview PNG")
    ap.add_argument("--json", action="store_true", help="print the info JSON")
    ap.add_argument("--list-fonts", action="store_true")
    a = ap.parse_args()
    if a.list_fonts:
        for f in list_fonts():
            print(("* " if f["bundled"] else "  ") + f["font"])
        return 0
    if not a.name:
        ap.error("--name is required")
    try:
        res = generate(a)
    except (ValueError, RuntimeError) as e:
        print(json.dumps({"error": str(e)}) if a.json else f"error: {e}",
              file=sys.stdout if a.json else sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        print(f"{res['stl']}: {res['name_len']} mm of name over {res['name_arc_deg']}°, "
              f"letters z {res['letters_z'][0]}–{res['letters_z'][1]}, "
              f"{res['mesh'].get('volume_cm3', '?')} cm³, {res['seconds']} s")
        for w in res["warnings"]:
            print("warning:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
