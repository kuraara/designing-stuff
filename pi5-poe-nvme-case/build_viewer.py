#!/usr/bin/env python3
"""Build a self-contained 3D viewer page (three.js) for the case STLs.
Embeds body_asm / lid_asm / feet as base64 binary STL plus layout info and print times."""
import base64, io, json, pathlib
import trimesh

ROOT = pathlib.Path(__file__).parent
I = json.loads((ROOT / "info" / "info.json").read_text())
T = json.loads((ROOT / "print_times.json").read_text())


def b64(name):
    m = trimesh.load(ROOT / "stl" / f"{name}.stl")
    buf = io.BytesIO()
    m.export(buf, file_type="stl")          # binary STL
    return base64.b64encode(buf.getvalue()).decode()


DATA = {k: b64(k) for k in ("body_asm", "lid_asm", "feet", "din", "din_rail")}

html = """<title>Pi 5 Case Viewer</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Saira+Condensed:wght@600;700&display=swap">
<style>
/* Layout: one-screen viewer. Title + part tabs on top, the model fills the middle, display controls along the bottom. Same drafting palette as the drawings page. */
:root {
  --paper: #eef2f1; --sheet: #f9fbfa; --ink: #1b2a31; --muted: #5a6b72; --rule: #c9d3d3;
  --vp: #e3e9e9; --edge: #22323a; --dim: #0b6b87; --accent: #c8322b;
  --f-display: "Saira Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #10171a; --sheet: #162024; --ink: #dbe6e8; --muted: #8fa3a8; --rule: #2c3b40;
  --vp: #1a252a; --edge: #0b1114; --dim: #4fb6d6; --accent: #ff6a5c; color-scheme: dark; } }
:root[data-theme="dark"] {
  --paper: #10171a; --sheet: #162024; --ink: #dbe6e8; --muted: #8fa3a8; --rule: #2c3b40;
  --vp: #1a252a; --edge: #0b1114; --dim: #4fb6d6; --accent: #ff6a5c; color-scheme: dark; }
html, body { height: 100%; }
body { background: var(--paper); color: var(--ink); font: 14px/1.4 var(--f-body); }
.app { min-height: 100%; box-sizing: border-box; display: grid; grid-template-rows: auto clamp(320px, 64vh, 760px) auto auto; gap: 10px;
  padding-block: 12px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  max-width: 1200px; margin: 0 auto; }
header { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 16px; }
h1 { margin: 0; font: 700 clamp(1.5rem, 5vw, 2.1rem)/1 var(--f-display); text-transform: uppercase; letter-spacing: .02em; }
.tabs { display: flex; flex-wrap: wrap; gap: 0; border: 1px solid var(--rule); border-radius: 4px; overflow: hidden; background: var(--sheet); }
.tabs button { font: 500 13px/1 var(--f-mono); padding: 9px 12px; border: 0; border-left: 1px solid var(--rule); background: transparent; color: var(--muted); cursor: pointer; }
.tabs button:first-child { border-left: 0; }
.tabs button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
button:focus-visible, input:focus-visible { outline: 2px solid var(--dim); outline-offset: 2px; }
.stage { position: relative; min-height: 0; border: 1px solid var(--rule); border-radius: 4px; background: var(--vp); overflow: hidden; }
canvas { display: block; width: 100%; height: 100%; touch-action: none; }
.card { position: absolute; left: 10px; top: 10px; max-width: min(320px, calc(100% - 20px)); background: color-mix(in srgb, var(--sheet) 90%, transparent);
  border: 1px solid var(--rule); border-radius: 4px; padding: 8px 10px; display: grid; gap: 3px; pointer-events: none; }
.card .nm { font: 700 1.15rem/1.1 var(--f-display); text-transform: uppercase; letter-spacing: .03em; }
.card dl { margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 1px 10px; font: 12px/1.45 var(--f-mono); font-variant-numeric: tabular-nums; }
.card dt { color: var(--muted); }
.card dd { margin: 0; }
.views { position: absolute; right: 10px; top: 10px; display: flex; flex-direction: column; gap: 4px; }
.views button, .ctl button { font: 500 12px/1 var(--f-mono); padding: 8px 10px; border: 1px solid var(--rule); border-radius: 4px; background: var(--sheet); color: var(--ink); cursor: pointer; }
.hint { position: absolute; left: 10px; bottom: 8px; font: 11px/1.3 var(--f-mono); color: var(--muted); pointer-events: none; }
.err { position: absolute; inset: 0; display: grid; place-items: center; padding: 20px; text-align: center; color: var(--muted); }
.controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; }
.ctl { display: flex; align-items: center; gap: 6px; font: 13px/1 var(--f-mono); color: var(--muted); }
.ctl button[aria-pressed="true"] { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.ctl input[type=range] { width: min(220px, 46vw); accent-color: var(--accent); }
.ctl output { font-variant-numeric: tabular-nums; min-width: 9ch; color: var(--ink); }
.controls[data-mode="print"] .asm-only { display: none; }
.legend { display: flex; flex-wrap: wrap; gap: 4px 12px; font: 11px/1.3 var(--f-mono); color: var(--muted); }
.req { display: grid; gap: 8px; margin-top: 8px; border-top: 2px solid var(--ink); padding-top: 12px; }
.req h2 { margin: 0; font: 600 1.35rem/1.1 var(--f-display); text-transform: uppercase; letter-spacing: .03em; }
.req .tbl { overflow-x: auto; }
.req table { border-collapse: collapse; width: 100%; background: var(--sheet); border: 1px solid var(--rule); font-size: 13.5px; }
.req th, .req td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--rule); }
.req thead th { font: 500 11px/1.3 var(--f-mono); text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }
.req tbody tr:last-child td { border-bottom: 0; }
.req td:first-child { width: 46%; }
.req td:last-child { color: var(--muted); }
.req .st { font: 500 11px/1 var(--f-mono); padding: 2px 5px; border-radius: 3px; border: 1px solid var(--rule); margin-right: 6px; white-space: nowrap; }
.req .st.dropped { color: var(--accent); border-color: var(--accent); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 5px; vertical-align: -1px; }
</style>

<div class="app">
  <header>
    <h1>Pi 5 Case Viewer</h1>
    <div class="tabs" role="group" aria-label="Part">
      <button type="button" id="tab-asm" data-mode="asm" aria-pressed="true">Assembly</button>
      <button type="button" id="tab-body" data-mode="body" aria-pressed="false">Body</button>
      <button type="button" id="tab-lid" data-mode="lid" aria-pressed="false">Lid</button>
      <button type="button" id="tab-feet" data-mode="feet" aria-pressed="false">Feet</button>
      <button type="button" id="tab-din" data-mode="din" aria-pressed="false">DIN bracket</button>
    </div>
  </header>

  <div class="stage" id="stage">
    <canvas id="cv" aria-label="3D view of the case"></canvas>
    <div class="card" id="card"></div>
    <div class="views">
      <button type="button" id="v-iso">Iso</button>
      <button type="button" id="v-end">End</button>
      <button type="button" id="v-side">Side</button>
    </div>
    <div class="hint">Drag to orbit · scroll or pinch to zoom · right-drag or two fingers to pan</div>
  </div>

  <div class="controls" id="controls" data-mode="asm">
    <div class="ctl asm-only"><button type="button" id="t-boards" aria-pressed="true">Boards</button></div>
    <div class="ctl asm-only"><button type="button" id="t-lid" aria-pressed="false">Lid out</button></div>
    <div class="ctl asm-only"><button type="button" id="t-din" aria-pressed="false">On DIN rail</button></div>
    <div class="ctl asm-only"><button type="button" id="t-cut" aria-pressed="false">Section</button>
      <input type="range" id="cut" min="0" max="100" step="0.5" value="54" aria-label="Section position along the case" disabled>
      <output id="cut-out" for="cut">X 54 mm</output></div>
    <div class="legend asm-only" aria-label="Colours"><span><i style="background:#9fb2b7"></i>body</span><span><i style="background:#5b84c4"></i>lid, feet</span><span><i style="background:#3c9a5f"></i>PCBs</span><span><i style="background:#8a6fd1"></i>SSDs</span><span><i style="background:#d39a2a"></i>HAT parts</span><span><i style="background:#c8322b"></i>DIN bracket</span></div>
  </div>

  <section class="req" aria-labelledby="req-h">
    <h2 id="req-h">Your requirements</h2>
    <div class="tbl"><table>
      <thead><tr><th scope="col">You asked for</th><th scope="col">How the case does it</th></tr></thead>
      <tbody>
        <tr><td>Pi 5 with a PoE HAT and a Pimoroni dual NVMe base</td><td>Waveshare PoE HAT (G), WS-27670 (from your Core Electronics order), NVMe Base Duo underneath</td></tr>
        <tr><td>No screws into the Pi or the NVMe base; boards sit on a lip, per your sketches</td><td>Two ledges on each wall, one per board. No standoffs; the PCIe ribbon is the only link</td></tr>
        <tr><td>Clearance for thick NVMe drives (2 × Samsung 980)</td><td>13 mm SSD bay under the base, about 2 mm spare</td></tr>
        <tr><td>Room for a chunky USB-C plug, like a Dell Thunderbolt dock's</td><td>42 × 11 mm window over USB-C and both HDMI, with the lip notched so the plug seats</td></tr>
        <tr><td>3 mm walls optional; use ribs if they save print time</td><td>2.4 mm walls stiffened by the full-length lips. Saves about an hour on the body</td></tr>
        <tr><td>2–3 parts: body and lid</td><td>Body, lid, and 4 feet</td></tr>
        <tr><td>Lid on an end; the Pi slides in like a tube</td><td>Lid at the SD end. Boards slide in USB first and stop on the closed USB end</td></tr>
        <tr><td>Lid screwed with M3 or clicked in, TPU for a click fit</td><td>TPU click-in lid with 4 snap bumps; its prongs push the boards home</td></tr>
        <tr><td>Vents top and bottom; more space around the base and HAT for heat</td><td>Roof and floor vents, side vents between the boards, 4 mm air down each side</td></tr>
        <tr><td>Feet screwed on with M3 counterbored screws</td><td>4 TPU feet, M3 × 8 into heat-set inserts</td></tr>
        <tr><td>SIM-style SD card tray</td><td><span class="st dropped">dropped</span>At your call. The PCIe ribbon covers the slot, so fit the card before the ribbon</td></tr>
        <tr><td>DIN rail bracket on the feet footprint: plenty of airflow clearance, sturdy enough for rough installing and removing</td><td>Bolts to the 4 foot inserts (M3 × 20). 14 mm air gap under the floor vents plus open windows. Full-width fixed hook, a latch with an over-travel stop, and 20 mm side ribs</td></tr>
        <tr><td>2D projections before the 3D model</td><td>Drawings page first, STLs once you'd answered the questions</td></tr>
      </tbody>
    </table></div>
  </section>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const INFO = __INFO__;
const TIMES = __TIMES__;
const DATA = __DATA__;
(function () {
  const stage = document.getElementById("stage"), canvas = document.getElementById("cv"), card = document.getElementById("card");
  if (!window.THREE || !THREE.OrbitControls) { stage.insertAdjacentHTML("beforeend", '<p class="err">The 3D library did not load. Check your connection and reload the page.</p>'); return; }
  const I = INFO;
  const hm = m => { const t = Math.round(m), h = Math.floor(t / 60), mm = t % 60; return h ? h + "h " + String(mm).padStart(2, "0") + "m" : mm + "m"; };
  const f1 = v => Math.abs(v - Math.round(v)) < 0.05 ? v.toFixed(0) : v.toFixed(1);

  // ---------- STL parsing (binary)
  function parseSTL(b64) {
    const bin = atob(b64), n8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) n8[i] = bin.charCodeAt(i);
    const dv = new DataView(n8.buffer), n = dv.getUint32(80, true);
    const pos = new Float32Array(n * 9), nor = new Float32Array(n * 9);
    let o = 84;
    for (let i = 0; i < n; i++) {
      const nx = dv.getFloat32(o, true), ny = dv.getFloat32(o + 4, true), nz = dv.getFloat32(o + 8, true); o += 12;
      for (let v = 0; v < 3; v++) {
        const k = i * 9 + v * 3;
        pos[k] = dv.getFloat32(o, true); pos[k + 1] = dv.getFloat32(o + 4, true); pos[k + 2] = dv.getFloat32(o + 8, true);
        nor[k] = nx; nor[k + 1] = ny; nor[k + 2] = nz; o += 12;
      }
      o += 2;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.setAttribute("normal", new THREE.BufferAttribute(nor, 3));
    return g;
  }
  const G = { body: parseSTL(DATA.body_asm), lid: parseSTL(DATA.lid_asm), feet: parseSTL(DATA.feet), din: parseSTL(DATA.din), rail: parseSTL(DATA.din_rail) };

  // ---------- renderer / scene (Z up, like the CAD model)
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 1, 5000);
  camera.up.set(0, 0, 1);
  const controls = new THREE.OrbitControls(camera, canvas);
  controls.enableDamping = true; controls.dampingFactor = 0.12;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x6b7378, 0.75));
  const sun = new THREE.DirectionalLight(0xffffff, 0.75); sun.position.set(-1, -1.6, 2.2); scene.add(sun);
  const fill = new THREE.DirectionalLight(0xffffff, 0.3); fill.position.set(1.5, 1, 0.6); scene.add(fill);

  const cutPlane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 1e4);
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x22323a });
  const cutMat = new THREE.MeshBasicMaterial({ color: 0x3a4a52, side: THREE.BackSide });

  function solid(geom, color, opts = {}) {
    const grp = new THREE.Group();
    const m = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0, transparent: !!opts.opacity, opacity: opts.opacity || 1, side: THREE.FrontSide }));
    grp.add(m);
    if (!opts.noBack) grp.add(new THREE.Mesh(geom, cutMat));         // inside faces show dark where the section cuts
    if (!opts.noEdges) grp.add(new THREE.LineSegments(new THREE.EdgesGeometry(geom, 28), edgeMat));
    return grp;
  }
  function box(x0, y0, z0, x1, y1, z1, color, opacity) {
    const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
    g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
    return solid(g, color, { opacity, noBack: true });
  }

  // ---------- assembly
  const BODY = 0x9fb2b7, LID = 0x5b84c4, PCB = 0x3c9a5f, SSD = 0x8a6fd1, AMBER = 0xd39a2a, JACK = 0x8c979b;
  const asm = new THREE.Group();
  const bodyA = solid(G.body, BODY); asm.add(bodyA);
  const lidA = solid(G.lid, LID); asm.add(lidA);
  const feetA = new THREE.Group();
  const fd = I.foot[0], fh = I.foot[1];
  for (const x of I.foot_x) for (const y of [I.y_foot, I.bw - I.y_foot]) {
    const c = new THREE.CylinderGeometry(fd / 2, fd / 2, fh, 32); c.rotateX(Math.PI / 2); c.translate(x, y, 0.6 - fh / 2);
    feetA.add(solid(c, LID, { noBack: true }));
  }
  asm.add(feetA);
  const boards = new THREE.Group();
  const zd = I.zd, zdt = I.z_duo_t, zpb = I.z_pi_b, zpt = I.z_pi_t, bl = I.bl, bw = I.bw;
  boards.add(box(0, 0, zd, bl, bw, zdt, PCB, 0.85));                                     // NVMe Base Duo
  for (const [y0, y1] of [[5, 27], [29, 51]]) boards.add(box(2.5, y0, zd - 7.4, 82.5, y1, zd - 5, SSD, 0.8));  // 980 SSDs (positions assumed)
  boards.add(box(0, 0, zpb, bl, bw, zpt, PCB, 0.85));                                    // Pi 5
  boards.add(box(bl - 17.6 + I.port_over, 2.2, zpt, bl + I.port_over, 18.2, zpt + 13.5, JACK, 0.9));   // RJ45
  for (const y of I.usb_y) boards.add(box(bl - 17.6 + I.port_over, y - 7, zpt, bl + I.port_over, y + 7, zpt + 16, JACK, 0.9));
  boards.add(box(I.usbc_x - 4.5, -1.6, zpt, I.usbc_x + 4.5, 5.8, zpt + 3.2, JACK, 0.9));
  for (const x of I.hdmi_x) boards.add(box(x - 3.3, -1.25, zpt, x + 3.3, 6.2, zpt + 3.0, JACK, 0.9));
  boards.add(box(0, -0.25, I.z_hat_b, I.hat[0], bw + 0.25, I.z_hat_t, PCB, 0.85));      // PoE HAT (G)
  boards.add(box(1, 0.75, I.z_hat_t, I.hat[0] - 1, bw - 0.75, I.z_hat_c, AMBER, 0.28));  // HAT parts envelope
  asm.add(boards);
  const DINC = 0xc8322b;
  const dinA = new THREE.Group();
  const dinG = G.din.clone(); dinG.translate(0, 0, -I.din.H);
  dinA.add(solid(dinG, DINC));
  dinA.add(solid(G.rail, 0xa7b0b3, { opacity: 0.55, noBack: true }));
  dinA.visible = false; asm.add(dinA);

  // ---------- print plates (MK3S+ bed 250 x 210)
  function bed() {
    const g = new THREE.Group(), pts = [];
    for (let x = 0; x <= 250; x += 10) pts.push(x, 0, 0, x, 210, 0);
    for (let y = 0; y <= 210; y += 10) pts.push(0, y, 0, 250, y, 0);
    const lg = new THREE.BufferGeometry(); lg.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
    g.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0x7e9196, transparent: true, opacity: 0.35 })));
    const pl = new THREE.Mesh(new THREE.PlaneGeometry(250, 210), new THREE.MeshBasicMaterial({ color: 0x2b3236, transparent: true, opacity: 0.12, side: THREE.DoubleSide }));
    pl.position.set(125, 105, -0.05); g.add(pl);
    return g;
  }
  function onBed(geom, m4) {
    const g = geom.clone(); if (m4) g.applyMatrix4(m4);
    g.computeBoundingBox(); const b = g.boundingBox;
    g.translate(125 - (b.min.x + b.max.x) / 2, 105 - (b.min.y + b.max.y) / 2, -b.min.z);
    return g;
  }
  const T = (x, y, z) => new THREE.Matrix4().makeTranslation(x, y, z);
  const bodyPrint = new THREE.Matrix4().makeRotationY(Math.PI / 2).multiply(T(-I.x_end_out, 0, 0));          // USB end down
  const lidPrint = new THREE.Matrix4().makeRotationY(-Math.PI / 2).multiply(T(-(I.x_mouth - I.lid_t), 0, 0)); // outer face down
  const plates = {
    body: { grp: new THREE.Group(), geom: onBed(G.body, bodyPrint), color: BODY },
    lid: { grp: new THREE.Group(), geom: onBed(G.lid, lidPrint), color: LID },
    feet: { grp: new THREE.Group(), geom: onBed(G.feet, null), color: LID },
    din: { grp: new THREE.Group(), geom: onBed(G.din, null), color: DINC },
  };
  for (const k in plates) { const p = plates[k]; p.grp.add(bed()); p.part = solid(p.geom, p.color); p.grp.add(p.part); }

  // ---------- info cards
  const PT = TIMES;
  const total = PT.body.PETG.min + PT.lid.TPU.min + PT.feet.TPU.min;
  const CARDS = {
    asm: ["Assembly", [["Outside", f1(I.L_total) + " × " + f1(I.W) + " × " + f1(I.H)], ["On feet", f1(I.H + I.foot[1] - 0.6) + " high"], ["Print, all", hm(total)], ["Boards", "each on its own ledge"]]],
    body: ["Body", [["Material", "PETG"], ["On the bed", "USB end down"], ["Size", ""], ["Print", hm(PT.body.PETG.min) + " · " + Math.round(PT.body.PETG.g) + " g"]]],
    lid: ["Lid", [["Material", "TPU, eSun 95A FAST"], ["On the bed", "outer face down"], ["Size", ""], ["Print", hm(PT.lid.TPU.min) + " · " + Math.round(PT.lid.TPU.g) + " g"]]],
    din: ["DIN bracket", [["Material", "PETG"], ["On the bed", "rail side down"], ["Size", ""], ["Print", hm(PT.din.PETG.min) + " draft · about 2h 24m at 4 walls, 40% infill"], ["Fixing", "4 × M3 × 20 into the foot inserts"], ["Rail", "TS35 (35 × 7.5 or 15)"]]],
    feet: ["Feet × 4", [["Material", "TPU, eSun 95A FAST"], ["On the bed", "counterbore up"], ["Size", "Ø" + f1(I.foot[0]) + " × " + f1(I.foot[1])], ["Print", hm(PT.feet.TPU.min) + " · " + Math.round(PT.feet.TPU.g) + " g"]]],
  };
  for (const k of ["body", "lid", "din"]) {
    const b = plates[k].geom.boundingBox || (plates[k].geom.computeBoundingBox(), plates[k].geom.boundingBox);
    const s = new THREE.Vector3(); plates[k].geom.boundingBox.getSize(s);
    CARDS[k][1][2][1] = f1(s.x) + " × " + f1(s.y) + " × " + f1(s.z) + " tall";
  }
  function setCard(k) {
    const [nm, rows] = CARDS[k];
    card.innerHTML = '<div class="nm">' + nm + "</div><dl>" + rows.map(r => "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>").join("") + "</dl>";
  }

  // ---------- views
  let mode = "asm", current = asm;
  scene.add(asm);
  function fit(dir) {
    const bb = new THREE.Box3();
    if (mode === "asm") bb.setFromObject(asm); else bb.setFromObject(plates[mode].part);
    const c = bb.getCenter(new THREE.Vector3()), r = bb.getBoundingSphere(new THREE.Sphere()).radius;
    const fov = THREE.MathUtils.degToRad(camera.fov), asp = camera.aspect;
    const d = r / Math.sin(Math.min(fov, 2 * Math.atan(Math.tan(fov / 2) * asp)) / 2) * 1.08;
    const v = new THREE.Vector3(...dir).normalize();
    camera.position.copy(c).addScaledVector(v, d);
    controls.target.copy(c); camera.near = d / 50; camera.far = d * 20; camera.updateProjectionMatrix(); controls.update();
  }
  const DIRS = { iso: [-1.0, -1.25, 0.85], end: [1, -0.18, 0.22], side: [0.0001, -1, 0.12] };
  let lastDir = "iso";
  function view(k) { lastDir = k; fit(DIRS[k]); }

  const tabs = document.querySelectorAll(".tabs button"), controlsEl = document.getElementById("controls");
  function setMode(k) {
    mode = k; scene.remove(current);
    current = k === "asm" ? asm : plates[k].grp; scene.add(current);
    tabs.forEach(b => b.setAttribute("aria-pressed", String(b.dataset.mode === k)));
    controlsEl.dataset.mode = k === "asm" ? "asm" : "print";
    applyCut(); setCard(k); view("iso");
  }
  tabs.forEach(b => b.addEventListener("click", () => setMode(b.dataset.mode)));
  document.getElementById("v-iso").addEventListener("click", () => view("iso"));
  document.getElementById("v-end").addEventListener("click", () => view("end"));
  document.getElementById("v-side").addEventListener("click", () => view("side"));

  // ---------- toggles
  function toggle(id, fn) { const b = document.getElementById(id); b.addEventListener("click", () => { const on = b.getAttribute("aria-pressed") !== "true"; b.setAttribute("aria-pressed", String(on)); fn(on); }); }
  toggle("t-boards", on => { boards.visible = on; });
  toggle("t-lid", on => { lidA.position.x = on ? -30 : 0; });
  toggle("t-din", on => { dinA.visible = on; feetA.visible = !on; CARDS.asm[1][1] = on ? ["On the rail", f1(I.H + I.din.H + 7.5 - I.din.ledge) + " from the wall"] : ["On feet", f1(I.H + I.foot[1] - 0.6) + " high"]; setCard("asm"); view(lastDir); });
  const cut = document.getElementById("cut"), cutOut = document.getElementById("cut-out");
  cut.min = (I.x_mouth - I.lid_t).toFixed(1); cut.max = I.x_end_out.toFixed(1);
  let cutOn = false;
  function applyCut() {
    const on = cutOn && mode === "asm";
    cutPlane.constant = parseFloat(cut.value);
    renderer.clippingPlanes = on ? [cutPlane] : [];
    cutOut.textContent = "X " + f1(parseFloat(cut.value)) + " mm";
  }
  toggle("t-cut", on => { cutOn = on; cut.disabled = !on; applyCut(); if (on) view("end"); });
  cut.addEventListener("input", applyCut);

  // ---------- theme
  function applyTheme() {
    const cs = getComputedStyle(document.documentElement);
    edgeMat.color.set(cs.getPropertyValue("--edge").trim() || "#22323a");
  }
  try { matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme); } catch (e) {}
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  applyTheme();

  // ---------- size + loop
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(() => { resize(); }).observe(stage);
  resize();
  setMode("asm");
  (function loop() { controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop); })();
})();
</script>
"""

html = (html.replace("__INFO__", json.dumps(I)).replace("__TIMES__", json.dumps(T))
            .replace("__DATA__", json.dumps(DATA)))
out = ROOT / "pi5_case_viewer.html"
out.write_text(html)
print(out, len(html) // 1024, "KB")
