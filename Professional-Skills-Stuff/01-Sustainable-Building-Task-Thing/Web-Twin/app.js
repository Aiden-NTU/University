import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const DATA = './data/';
const TOUCH = matchMedia('(pointer: coarse)').matches;
const LAT = 52.9135, LON = -1.1839;
const EYE = 1.6, STEP = 0.5, CENTRE = new THREE.Vector3(12, 3, -7.2);

// ---------------------------------------------------------------- renderer + scene
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, TOUCH ? 1.5 : 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const SKY = new THREE.Color(0xbcd6ea);
scene.background = SKY.clone();
scene.fog = new THREE.Fog(SKY.clone(), 260, 750);
const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 2000);

const hemi = new THREE.HemisphereLight(0xe2f0ff, 0xb8b0a2, 1.1);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff1dc, 2.8);
sun.castShadow = true;
sun.shadow.mapSize.set(TOUCH ? 1536 : 3072, TOUCH ? 1536 : 3072);
Object.assign(sun.shadow.camera, { left: -120, right: 120, top: 120, bottom: -120, near: 1, far: 900 });
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.04;
sun.target.position.copy(CENTRE);
scene.add(sun, sun.target);

const orbit = new OrbitControls(camera, canvas);
orbit.enableDamping = true;
orbit.maxPolarAngle = Math.PI * 0.49;
orbit.minDistance = 4;
orbit.maxDistance = 450;
orbit.target.copy(CENTRE);
camera.position.set(-55, 45, 60);

// ---------------------------------------------------------------- state
const S = {
  mode: 'orbit', phase: 'proposed', rooms: [], roomsById: {}, data: null,
  walkables: [], colliders: [], pickables: [], groups: { GF: [], FF: [], RF: [], SITE: [] },
  terrainMat: null, tex: {}, player: { pos: new THREE.Vector3(), yaw: 0, pitch: 0, vy: 0 },
  keys: new Set(), joy: { x: 0, y: 0 }, currentRoom: null, date: '06-21', hour: 13,
};

// ---------------------------------------------------------------- loading
const loadingText = document.getElementById('loading-text');
const json = (f) => fetch(DATA + f).then((r) => r.json());

async function loadTerrain() {
  const meta = await json('terrain.json');
  const h = new Float32Array(await (await fetch(DATA + 'terrain.bin')).arrayBuffer());
  const { x0, y0, dx, nx, ny, tex_x0, tex_y0, tex_w, tex_h } = meta;
  const pos = new Float32Array(nx * ny * 3), uv = new Float32Array(nx * ny * 2);
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const k = j * nx + i, x = x0 + i * dx, y = y0 + j * dx;
    pos.set([x, h[k], -y], 3 * k);
    uv.set([(x - tex_x0) / tex_w, (y - tex_y0) / tex_h], 2 * k);
  }
  const idx = new Uint32Array((nx - 1) * (ny - 1) * 6);
  let n = 0;
  for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
    const a = j * nx + i, b = a + 1, c = a + nx + 1, d = a + nx;
    idx.set([a, b, c, a, c, d], n); n += 6;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.computeVertexNormals();
  const loader = new THREE.TextureLoader();
  for (const k of ['existing', 'proposed']) {
    S.tex[k] = await loader.loadAsync(`${DATA}aerial_${k}.jpg`);
    S.tex[k].colorSpace = THREE.SRGBColorSpace;
    S.tex[k].anisotropy = renderer.capabilities.getMaxAnisotropy();
  }
  S.terrainMat = new THREE.MeshStandardMaterial({ map: S.tex.proposed, roughness: 1 });
  const mesh = new THREE.Mesh(g, S.terrainMat);
  mesh.receiveShadow = true;
  mesh.name = 'terrain';
  scene.add(mesh);
  S.walkables.push(mesh);
}

async function loadContext() {
  const ctx = await json('context.json');
  const geoms = [];
  for (const b of ctx.buildings) {
    const shape = new THREE.Shape(b.p.map(([x, y]) => new THREE.Vector2(x, y)));
    const g = new THREE.ExtrudeGeometry(shape, { depth: Math.max(1, b.t - b.b), bevelEnabled: false });
    g.rotateX(-Math.PI / 2);
    g.translate(0, b.b, 0);
    geoms.push(g.index ? g.toNonIndexed() : g);
  }
  const mesh = new THREE.Mesh(mergeGeometries(geoms), new THREE.MeshStandardMaterial({ color: 0xe8e4dc, roughness: 0.9 }));
  mesh.castShadow = mesh.receiveShadow = true;
  scene.add(mesh);
  S.colliders.push(mesh);

  const n = ctx.trees.length;
  const crown = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1),
    new THREE.MeshStandardMaterial({ roughness: 1, flatShading: true }), n);
  const trunk = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.15, 0.25, 1, 6),
    new THREE.MeshStandardMaterial({ color: 0x5b4632, roughness: 1 }), n);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), c = new THREE.Color();
  ctx.trees.forEach(([x, y, z, h, r], i) => {
    const cz = z + Math.max(h - r, 1.5);
    m.compose(new THREE.Vector3(x, cz, -y), q, new THREE.Vector3(r, r * 1.05, r));
    crown.setMatrixAt(i, m);
    c.setHSL(0.24 + Math.random() * 0.07, 0.42, 0.24 + Math.random() * 0.08);
    crown.setColorAt(i, c);
    m.compose(new THREE.Vector3(x, z + (cz - z) / 2, -y), q, new THREE.Vector3(1, cz - z, 1));
    trunk.setMatrixAt(i, m);
  });
  crown.castShadow = trunk.castShadow = true;
  crown.receiveShadow = true;
  scene.add(crown, trunk);
}

async function loadBuilding() {
  const gltf = await new GLTFLoader().loadAsync(DATA + 'building.glb');
  gltf.scene.traverse((o) => {
    if (!o.isMesh) return;
    const name = o.name || o.parent?.name || '';
    const [lvl, kind, room] = name.split('__');
    o.userData = { lvl, kind, room };
    const glassy = kind && kind.includes('glass') || kind === 'balustrade';
    o.castShadow = !glassy;
    o.receiveShadow = true;
    if (glassy) { o.material.depthWrite = false; o.renderOrder = 2; }
    (S.groups[lvl] || (S.groups[lvl] = [])).push(o);
    if (['floor', 'slab', 'stair', 'plinth', 'annexwall'].includes(kind)) S.walkables.push(o);
    if (['extwall', 'intwall', 'glass', 'annexwall', 'annexglass', 'balustrade', 'furn', 'carport', 'landscape_asset'].includes(kind)) S.colliders.push(o);
    if (kind === 'floor' || kind === 'furn') S.pickables.push(o);
  });
  scene.add(gltf.scene);
}

// ---------------------------------------------------------------- sun
const BST = { '03-20': 0, '06-21': 1, '09-22': 1, '12-21': 0 };
function sunPosition(date) {
  const rad = Math.PI / 180, n = date.getTime() / 86400000 + 2440587.5 - 2451545.0;
  const L = (280.46 + 0.9856474 * n) % 360, g = ((357.528 + 0.9856003 * n) % 360) * rad;
  const lam = (L + 1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g)) * rad, eps = (23.439 - 4e-7 * n) * rad;
  const ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam)), dec = Math.asin(Math.sin(eps) * Math.sin(lam));
  const gmst = (18.697374558 + 24.06570982441908 * n) % 24;
  const H = ((gmst * 15 + LON) * rad) - ra, lat = LAT * rad;
  const alt = Math.asin(Math.sin(lat) * Math.sin(dec) + Math.cos(lat) * Math.cos(dec) * Math.cos(H));
  const az = Math.atan2(-Math.sin(H), Math.tan(dec) * Math.cos(lat) - Math.sin(lat) * Math.cos(H));
  return { alt, az };
}
function updateSun() {
  const [mm, dd] = S.date.split('-').map(Number);
  const utcHour = S.hour - BST[S.date];
  const d = new Date(Date.UTC(2026, mm - 1, dd, Math.floor(utcHour), Math.round((utcHour % 1) * 60)));
  const { alt, az } = sunPosition(d);
  const dir = new THREE.Vector3(Math.cos(alt) * Math.sin(az), Math.sin(alt), -Math.cos(alt) * Math.cos(az));
  sun.position.copy(CENTRE).addScaledVector(dir, 400);
  const day = THREE.MathUtils.clamp(Math.sin(alt) * 4, 0, 1);
  sun.intensity = 2.8 * day;
  hemi.intensity = 0.25 + 0.7 * THREE.MathUtils.clamp(Math.sin(alt) * 3 + 0.3, 0, 1);
  scene.background.copy(SKY).multiplyScalar(0.25 + 0.75 * hemi.intensity / 0.95);
  scene.fog.color.copy(scene.background);
  const hh = Math.floor(S.hour), mi = String(Math.round((S.hour % 1) * 60)).padStart(2, '0');
  document.getElementById('sun-label').textContent =
    `${hh}:${mi} ${BST[S.date] ? 'BST' : 'GMT'} - sun ${(alt / Math.PI * 180).toFixed(0)} deg high, bearing ${((az / Math.PI * 180 + 360) % 360).toFixed(0)} deg`;
}

// ---------------------------------------------------------------- visibility toggles
function applyVisibility() {
  const proposed = S.phase === 'proposed';
  const roof = document.getElementById('show-roof').checked;
  const ff = document.getElementById('show-ff').checked;
  S.terrainMat.map = S.tex[S.phase];
  S.terrainMat.needsUpdate = true;
  for (const [lvl, list] of Object.entries(S.groups)) {
    const vis = proposed && (lvl === 'RF' ? roof && ff : lvl === 'FF' ? ff : true);
    list.forEach((o) => { o.visible = vis; });
  }
}
const visibleOnly = (list) => list.filter((o) => {
  for (let p = o; p; p = p.parent) if (!p.visible) return false;
  return true;
});

// ---------------------------------------------------------------- walking
const ray = new THREE.Raycaster();
const DOWN = new THREE.Vector3(0, -1, 0);
function groundAt(x, feet, z) {
  ray.set(new THREE.Vector3(x, feet + STEP, z), DOWN);
  ray.far = 60;
  const hit = ray.intersectObjects(visibleOnly(S.walkables), false)[0];
  return hit ? hit.point.y : null;
}
function blocked(from, dir, dist) {
  for (const hgt of [0.4, 1.3]) {
    ray.set(new THREE.Vector3(from.x, from.y + hgt, from.z), dir);
    ray.far = dist + 0.3;
    if (ray.intersectObjects(visibleOnly(S.colliders), false).length) return true;
  }
  return false;
}
function tryMove(p, dx, dz) {
  const len = Math.hypot(dx, dz);
  if (len < 1e-5) return false;
  const dir = new THREE.Vector3(dx / len, 0, dz / len);
  if (blocked(p.pos, dir, len)) return false;
  const g = groundAt(p.pos.x + dx, p.pos.y, p.pos.z + dz);
  if (g === null || g - p.pos.y > STEP) return false;
  p.pos.x += dx; p.pos.z += dz;
  return true;
}
function walkUpdate(dt) {
  const p = S.player;
  let f = 0, s = 0;
  if (S.keys.has('KeyW') || S.keys.has('ArrowUp')) f += 1;
  if (S.keys.has('KeyS') || S.keys.has('ArrowDown')) f -= 1;
  if (S.keys.has('KeyD')) s += 1;
  if (S.keys.has('KeyA')) s -= 1;
  if (S.keys.has('ArrowLeft')) p.yaw += 1.8 * dt;
  if (S.keys.has('ArrowRight')) p.yaw -= 1.8 * dt;
  f += -S.joy.y; s += S.joy.x;
  const speed = (S.keys.has('ShiftLeft') ? 4.0 : 1.6) * Math.min(1, Math.hypot(f, s));
  if (f || s) {
    const sin = Math.sin(p.yaw), cos = Math.cos(p.yaw), len = Math.hypot(f, s), d = speed * dt;
    const dx = ((-sin * f + cos * s) / len) * d, dz = ((-cos * f - sin * s) / len) * d;
    if (!tryMove(p, dx, dz)) { tryMove(p, dx, 0) || tryMove(p, 0, dz); }
  }
  const g = groundAt(p.pos.x, p.pos.y, p.pos.z);
  if (g !== null && g >= p.pos.y - 0.05) { p.pos.y = g; p.vy = 0; }
  else { p.vy -= 9.81 * dt; p.pos.y = Math.max(g ?? -50, p.pos.y + p.vy * dt); }
  camera.position.set(p.pos.x, p.pos.y + EYE, p.pos.z);
  camera.rotation.set(p.pitch, p.yaw, 0, 'YXZ');
  detectRoom();
}

function placePlayer(x, y, feet, yawDeg) {
  const p = S.player;
  p.pos.set(x, feet, -y);
  const g = groundAt(p.pos.x, feet, p.pos.z);
  if (g !== null) p.pos.y = g;
  p.yaw = THREE.MathUtils.degToRad(yawDeg);
  p.pitch = -0.05;
  p.vy = 0;
}

// ---------------------------------------------------------------- modes + presets
// yaw: 0 = looking north, 90 = looking west, -90 = looking east, 180 = looking south
const PRESETS = {
  approach: { walk: [30, -58, 0, 25] }, entrance: { walk: [2.2, -5, 0, 0] },
  atrium: { walk: [2.5, 1.2, 0.2, -60] }, hall: { walk: [19, 4, 0.2, 90] },
  library: { walk: [9.2, 2.2, 3.8, -75], ff: true }, cycle: { walk: [27, 2, 0, 0] },
  site: { orbit: [[-90, 95, 110], [20, 0, -5]] }, roof: { orbit: [[12, 32, 22], [12, 7, -7]] },
};
function setMode(mode) {
  S.mode = mode;
  document.querySelectorAll('#mode button').forEach((b) => b.classList.toggle('on', b.dataset.v === mode));
  orbit.enabled = mode === 'orbit';
  document.getElementById('joystick').classList.toggle('hidden', !(mode === 'walk' && TOUCH));
  if (mode === 'walk') {
    if (S.phase !== 'proposed') setPhase('proposed');
    hint(TOUCH ? 'Left stick to walk, drag right side to look' : 'WASD / arrows to walk, drag to look, Shift to run');
  } else {
    camera.position.set(S.player.pos.x - 25, S.player.pos.y + 25, S.player.pos.z + 25);
    orbit.target.copy(CENTRE);
    document.getElementById('room-chip').classList.add('hidden');
    hint(TOUCH ? 'Drag to orbit, pinch to zoom, tap a room for details' : 'Drag to orbit, scroll to zoom, click a room for details');
  }
}
function goTo(key) {
  const pr = PRESETS[key];
  if (!pr) return;
  if (pr.ff) { document.getElementById('show-ff').checked = true; applyVisibility(); }
  if (pr.walk) {
    if (key !== 'approach' && key !== 'entrance') {
      document.getElementById('show-roof').checked = true; applyVisibility();
    }
    const [x, y, feet, yaw] = pr.walk;
    placePlayer(x, y, feet, yaw);
    if (S.mode !== 'walk') setMode('walk');
  } else {
    if (S.mode !== 'orbit') setMode('orbit');
    camera.position.set(...pr.orbit[0]);
    orbit.target.set(...pr.orbit[1]);
  }
}
function setPhase(phase) {
  S.phase = phase;
  document.querySelectorAll('#phase button').forEach((b) => b.classList.toggle('on', b.dataset.v === phase));
  applyVisibility();
}

// ---------------------------------------------------------------- rooms
function inPoly([x, y], poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}
function detectRoom() {
  const p = S.player.pos, lvl = p.y > 2.5 ? 'FF' : 'GF';
  const r = S.rooms.find((rm) => rm.level === lvl && inPoly([p.x, -p.z], rm.polygon));
  const id = r ? r.id : null;
  if (id === S.currentRoom) return;
  S.currentRoom = id;
  const chip = document.getElementById('room-chip');
  if (!r) { chip.classList.add('hidden'); return; }
  chip.textContent = `${r.name} - ${r.area_m2} m2 - tap for details`;
  chip.classList.remove('hidden');
}
const gbp = (v) => (v === null || v === undefined ? 'TBC' : 'GBP ' + Math.round(v).toLocaleString('en-GB'));
function showRoom(id) {
  const r = S.roomsById[id];
  if (!r) return;
  const L = r.lighting, pct = Math.round((1 - L.design_kwh / Math.max(1, L.baseline_kwh)) * 100);
  const rows = r.items.map((it) => `<tr><td>${it.item}<br><span class="small">${it.spec || ''}</span></td>
    <td class="n">${it.qty}</td><td class="n">${gbp(it.capex_gbp)}</td><td class="n">${it.kwh_per_year || ''}</td></tr>`).join('');
  const el = document.getElementById('room');
  el.innerHTML = `<button class="close" aria-label="Close">&times;</button>
    <span class="lvl">${r.level === 'GF' ? 'Ground floor' : 'First floor'} - ${r.id}</span>
    <h3>${r.name}</h3>
    <p class="small">${r.area_m2} m2 net - ${r.use}</p>
    ${r.notes.length ? `<ul>${r.notes.map((n) => `<li>${n}</li>`).join('')}</ul>` : ''}
    <h2>Lighting (lumen method, ${r.lux} lux)</h2>
    <p class="small">${L.fittings} LED panels, ${L.design_w} W (${L.design_w_per_m2} W/m2), ${r.hours} h/yr with daylight + occupancy control</p>
    <div class="small">This design: ${L.design_kwh} kWh/yr</div><div class="bar"><i style="width:${Math.max(2, 100 - pct)}%"></i></div>
    <div class="small">Business-as-usual fluorescent, no controls: ${L.baseline_kwh} kWh/yr</div><div class="bar"><i style="width:100%;background:#7f8c87"></i></div>
    <p class="small"><b>${pct}% less</b> - saves ${gbp(r.lighting_saving.gbp)}/yr and ${r.lighting_saving.kgco2e} kgCO2e/yr</p>
    <h2>Fit-out schedule</h2>
    <table><tr><th>Item</th><th class="n">Qty</th><th class="n">Cost</th><th class="n">kWh/yr</th></tr>${rows}</table>
    <p class="small">Fit-out (priced items): <b>${gbp(r.fitout_capex_gbp)}</b>${r.unpriced_items ? ` + ${r.unpriced_items} item(s) awaiting quotes` : ''}.
      Running electricity: ${gbp(r.running_gbp_per_year)}/yr.</p>
    <p class="note">Prices are indicative placeholders until replaced with sourced quotes (see Costing/items.csv).</p>`;
  el.classList.remove('hidden');
  el.querySelector('.close').onclick = () => el.classList.add('hidden');
}
function renderTotals() {
  const d = S.data, m = d.metrics, t = d.totals;
  document.getElementById('totals').innerHTML = `<h2>Key numbers</h2><div class="kpi">
    <div><b>${m.gross_internal_area_m2} m2</b><span>gross internal area</span></div>
    <div><b>${m.pv_kwp} kWp</b><span>${m.pv_modules} PV modules</span></div>
    <div><b>${Math.round((1 - t.lighting_design_kwh / t.lighting_baseline_kwh) * 100)}%</b><span>less lighting energy</span></div>
    <div><b>${gbp(t.fitout_capex_gbp)}</b><span>fit-out (indicative)</span></div></div>`;
  document.getElementById('credits').textContent = d.credits.join(' | ');
}

// ---------------------------------------------------------------- input
const look = { id: null, x: 0, y: 0, moved: 0 };
const joyEl = document.getElementById('joystick'), knob = document.getElementById('knob');
let joyId = null;
canvas.addEventListener('pointerdown', (e) => {
  look.id = e.pointerId; look.x = e.clientX; look.y = e.clientY; look.moved = 0;
});
addEventListener('pointermove', (e) => {
  if (e.pointerId === joyId) {
    const r = joyEl.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    let dx = (e.clientX - cx) / (r.width / 2), dy = (e.clientY - cy) / (r.height / 2);
    const l = Math.hypot(dx, dy); if (l > 1) { dx /= l; dy /= l; }
    S.joy.x = dx; S.joy.y = dy;
    knob.style.transform = `translate(${dx * 34}px, ${dy * 34}px)`;
    return;
  }
  if (e.pointerId !== look.id) return;
  const dx = e.clientX - look.x, dy = e.clientY - look.y;
  look.moved += Math.abs(dx) + Math.abs(dy);
  look.x = e.clientX; look.y = e.clientY;
  if (S.mode === 'walk') {
    S.player.yaw += dx * 0.004;
    S.player.pitch = THREE.MathUtils.clamp(S.player.pitch + dy * 0.004, -1.2, 1.2);
  }
});
addEventListener('pointerup', (e) => {
  if (e.pointerId === joyId) { joyId = null; S.joy.x = S.joy.y = 0; knob.style.transform = ''; return; }
  if (e.pointerId !== look.id) return;
  look.id = null;
  if (look.moved < 6 && S.mode === 'orbit') pick(e);
});
joyEl.addEventListener('pointerdown', (e) => { joyId = e.pointerId; e.stopPropagation(); });
addEventListener('keydown', (e) => { if (e.target.tagName !== 'SELECT') S.keys.add(e.code); });
addEventListener('keyup', (e) => S.keys.delete(e.code));

function pick(e) {
  const v = new THREE.Vector2((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  ray.setFromCamera(v, camera);
  ray.far = 2000;
  const hit = ray.intersectObjects(visibleOnly([...S.pickables, ...S.colliders]), false)[0];
  if (hit && hit.object.userData.room) showRoom(hit.object.userData.room);
}
document.getElementById('room-chip').onclick = () => S.currentRoom && showRoom(S.currentRoom);

function hint(text) {
  const h = document.getElementById('help');
  h.textContent = text; h.style.opacity = 1;
  clearTimeout(hint.t); hint.t = setTimeout(() => { h.style.opacity = 0; }, 5000);
}

// ---------------------------------------------------------------- UI wiring
document.querySelectorAll('#mode button').forEach((b) => (b.onclick = () => {
  if (b.dataset.v === 'walk' && S.mode !== 'walk') goTo('entrance'); else setMode(b.dataset.v);
}));
document.querySelectorAll('#phase button').forEach((b) => (b.onclick = () => setPhase(b.dataset.v)));
document.querySelectorAll('#date button').forEach((b) => (b.onclick = () => {
  S.date = b.dataset.v;
  document.querySelectorAll('#date button').forEach((x) => x.classList.toggle('on', x === b));
  updateSun();
}));
document.getElementById('time').oninput = (e) => { S.hour = +e.target.value; updateSun(); };
document.getElementById('show-roof').onchange = applyVisibility;
document.getElementById('show-ff').onchange = applyVisibility;
document.getElementById('goto').onchange = (e) => { goTo(e.target.value); e.target.value = ''; e.target.blur(); };
document.getElementById('menu-btn').onclick = () => document.getElementById('controls').classList.toggle('open');

function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.fov = camera.aspect < 1 ? 80 : 60;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

// ---------------------------------------------------------------- main
const clock = new THREE.Clock();
const compass = document.querySelector('#compass span');
function frame() {
  const dt = Math.min(clock.getDelta(), 0.05);
  if (S.mode === 'walk') walkUpdate(dt); else orbit.update();
  const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
  compass.style.transform = `rotate(${Math.atan2(fwd.x, -fwd.z) * -180 / Math.PI}deg)`;
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

(async function main() {
  resize();
  try {
    loadingText.textContent = 'Loading LiDAR terrain and aerial imagery...';
    await loadTerrain();
    loadingText.textContent = 'Loading neighbouring buildings and trees...';
    await loadContext();
    loadingText.textContent = 'Loading The Heat Exchange...';
    await loadBuilding();
    S.data = await json('rooms.json');
    S.rooms = S.data.rooms;
    S.rooms.forEach((r) => { S.roomsById[r.id] = r; });
    renderTotals();
    applyVisibility();
    updateSun();
    placePlayer(2.2, -5, 0, 0);
    setMode('orbit');
    document.getElementById('loading').classList.add('done');
    if (new URLSearchParams(location.search).has('debug')) window.twin = { S, placePlayer, goTo, setMode, walkUpdate };
    frame();
  } catch (err) {
    loadingText.textContent = 'Could not load the model: ' + err.message;
    console.error(err);
  }
})();
