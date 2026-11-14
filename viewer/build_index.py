#!/usr/bin/env python3
"""Build viewer/models.json for the repo's 3D viewer (index.html, served by GitHub Pages).

Every *.stl in the repo is grouped under the nearest folder that has a README.md (a design).
Per design: title (README's first heading), status line, and its STLs with size, triangle
count, bounding box and volume. Files named ref_*.stl are reference bodies (e.g. the
microswitch), drawn see-through and not counted as printable.

Run after adding or changing STLs:  python3 viewer/build_index.py
"""
import json, pathlib, re
import trimesh

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {".git", "slice", "_build", "out", "node_modules"}


def design_dir(p):
    d = p.parent
    while d != ROOT and not (d / "README.md").exists():
        d = d.parent
    return d


def readme_meta(d):
    t = (d / "README.md").read_text(errors="ignore")
    title = next((l.lstrip("# ").strip() for l in t.splitlines() if l.startswith("# ")), d.name)
    m = re.search(r"Status:\s*\*\*(.+?)\*\*", t)
    return title, (m.group(1) if m else "")


designs = {}
for stl in sorted(ROOT.rglob("*.stl")):
    rel = stl.relative_to(ROOT)
    if any(part in SKIP for part in rel.parts):
        continue
    d = design_dir(stl)
    key = d.relative_to(ROOT).as_posix()
    if key == ".":
        continue
    m = trimesh.load(stl)
    lo, hi = m.bounds
    entry = {
        "path": rel.as_posix(),
        "name": stl.stem,
        "kb": round(stl.stat().st_size / 1024),
        "tris": int(len(m.faces)),
        "size": [round(float(v), 1) for v in (hi - lo)],
        "cm3": round(abs(float(m.volume)) / 1000, 2),
        "ref": stl.stem.startswith("ref_"),
    }
    if key not in designs:
        title, status = readme_meta(d)
        designs[key] = {"folder": key, "title": title, "status": status, "stls": []}
    designs[key]["stls"].append(entry)

out = {"repo": "kuraara/designing-stuff", "branch": "main",
       "designs": sorted(designs.values(), key=lambda x: x["folder"])}
(ROOT / "viewer" / "models.json").write_text(json.dumps(out, indent=1))
for d in out["designs"]:
    print(f'{d["folder"]:40s} {len(d["stls"]):3d} STLs  {d["title"]}')
