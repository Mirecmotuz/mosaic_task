// ── Palette for rectangle colours ──────────────────────────────────────────
const PALETTE = [
  'rgba(108,99,255,0.35)', 'rgba(255,101,132,0.35)', 'rgba(72,187,120,0.35)',
  'rgba(246,173,85,0.35)',  'rgba(99,179,237,0.35)',  'rgba(237,137,54,0.35)',
  'rgba(159,122,234,0.35)', 'rgba(72,187,187,0.35)',
];
const STROKE = [
  '#6c63ff','#ff6584','#48bb78','#f6ad55','#63b3ed','#ed8936','#9f7aea','#48bbbb',
];

let rectCount = 0;

function makeRectRow(x = 0, y = 0, w = 4, h = 3) {
  const id = rectCount++;
  const div = document.createElement('div');
  div.className = 'rect-item';
  div.dataset.id = id;
  div.innerHTML = `
    <div><label>x</label><input type="number" class="rx" value="${x}" step="any"></div>
    <div><label>y</label><input type="number" class="ry" value="${y}" step="any"></div>
    <div><label>width</label><input type="number" class="rw" value="${w}" step="any" min="0"></div>
    <div><label>height</label><input type="number" class="rh" value="${h}" step="any" min="0"></div>
    <button class="remove-btn" title="Remove">✕</button>`;
  div.querySelector('.remove-btn').addEventListener('click', () => div.remove());
  return div;
}

function getRectangles() {
  return [...document.querySelectorAll('.rect-item')].map(row => ({
    x:      parseFloat(row.querySelector('.rx').value) || 0,
    y:      parseFloat(row.querySelector('.ry').value) || 0,
    width:  parseFloat(row.querySelector('.rw').value) || 0,
    height: parseFloat(row.querySelector('.rh').value) || 0,
  }));
}

// ── Default example ─────────────────────────────────────────────────────────
document.getElementById('addBtn').addEventListener('click', () =>
  document.getElementById('rectList').appendChild(makeRectRow()));

const defaultRects = [
  [0,0,4,3], [2,1,3,3], [1,2,2,4],
];
defaultRects.forEach(([x,y,w,h]) =>
  document.getElementById('rectList').appendChild(makeRectRow(x,y,w,h)));

// ── Analyze ──────────────────────────────────────────────────────────────────
document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const btn = document.getElementById('analyzeBtn');
  const errEl = document.getElementById('errorMsg');
  errEl.style.display = 'none';
  btn.disabled = true;
  btn.textContent = 'Analyzing…';

  try {
    const rects = getRectangles();
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rectangles: rects }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    drawCanvas(rects, data);
    renderResults(data);
    document.getElementById('canvasHint').style.display = 'none';
  } catch (e) {
    errEl.textContent = e.message;
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze';
  }
});

// ── Canvas drawing ────────────────────────────────────────────────────────────
function drawCanvas(rects, data) {
  const wrap = document.getElementById('canvasWrap');
  const canvas = document.getElementById('canvas');
  const W = wrap.clientWidth;
  const H = wrap.clientHeight;
  canvas.width  = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);

  if (!rects.length) return;

  const PAD = 40;
  const xs = rects.flatMap(r => [r.x, r.x + r.width]);
  const ys = rects.flatMap(r => [r.y, r.y + r.height]);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;

  const scaleX = (W - PAD * 2) / rangeX;
  const scaleY = (H - PAD * 2) / rangeY;

  const toCanvas = (x, y) => [
    PAD + (x - minX) * scaleX,
    H - PAD - (y - minY) * scaleY,
  ];

  // Grid
  ctx.strokeStyle = '#22263a';
  ctx.lineWidth = 1;
  const gridStep = Math.pow(10, Math.floor(Math.log10(rangeX / 5)));
  for (let gx = Math.ceil(minX / gridStep) * gridStep; gx <= maxX; gx += gridStep) {
    const [cx] = toCanvas(gx, 0);
    ctx.beginPath(); ctx.moveTo(cx, PAD); ctx.lineTo(cx, H - PAD); ctx.stroke();
  }
  for (let gy = Math.ceil(minY / gridStep) * gridStep; gy <= maxY; gy += gridStep) {
    const [, cy] = toCanvas(0, gy);
    ctx.beginPath(); ctx.moveTo(PAD, cy); ctx.lineTo(W - PAD, cy); ctx.stroke();
  }

  // Rectangles
  rects.forEach((r, i) => {
    const [cx, cy] = toCanvas(r.x, r.y + r.height);
    const pw = r.width * scaleX;
    const ph = r.height * scaleY;
    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.strokeStyle = STROKE[i % STROKE.length];
    ctx.lineWidth = 2;
    ctx.fillRect(cx, cy, pw, ph);
    ctx.strokeRect(cx, cy, pw, ph);

    const [lx, ly] = toCanvas(r.x + r.width / 2, r.y + r.height / 2);
    ctx.fillStyle = STROKE[i % STROKE.length];
    ctx.font = `bold ${Math.min(14, Math.max(9, pw / 3))}px Inter,system-ui,sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`R${i}`, lx, ly);
  });

  // Overlap regions — cross-hatch
  (data.overlap_regions || []).forEach(({ region }) => {
    const [ox, oy] = toCanvas(region.x, region.y + region.height);
    const ow = region.width * scaleX;
    const oh = region.height * scaleY;
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,100,0.6)';
    ctx.lineWidth = 1;
    const gap = 6;
    ctx.beginPath();
    for (let d = -oh; d < ow; d += gap) {
      ctx.moveTo(ox + Math.max(0, d), oy);
      ctx.lineTo(ox + Math.min(ow, d + oh), oy + Math.min(oh, oh - d));
    }
    ctx.stroke();
    ctx.restore();
  });

  // Max overlap point
  if (data.max_overlap_point && data.max_overlap_point.count > 0) {
    const [px, py] = toCanvas(data.max_overlap_point.x, data.max_overlap_point.y);
    ctx.beginPath();
    ctx.arc(px, py, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    ctx.strokeStyle = '#ff6584';
    ctx.lineWidth = 2.5;
    ctx.stroke();
  }

  // Axis labels
  ctx.fillStyle = '#8892a4';
  ctx.font = '11px Inter,system-ui,sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  for (let gx = Math.ceil(minX / gridStep) * gridStep; gx <= maxX; gx += gridStep) {
    const [cx] = toCanvas(gx, 0);
    ctx.fillText(gx, cx, H - PAD + 4);
  }
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';
  for (let gy = Math.ceil(minY / gridStep) * gridStep; gy <= maxY; gy += gridStep) {
    const [, cy] = toCanvas(0, gy);
    ctx.fillText(gy, PAD - 5, cy);
  }
}

// ── Results bar ───────────────────────────────────────────────────────────────
function fmt(v) { return typeof v === 'number' ? +v.toFixed(4) : v; }

function renderResults(data) {
  const bar = document.getElementById('resultsBar');
  const s = data.stats;
  bar.style.display = 'flex';

  const overlapTags = (data.overlaps || [])
    .map(([i,j]) => `<li class="overlap-tag">R${i} ∩ R${j}</li>`)
    .join('') || '<li style="color:var(--text-muted);font-size:0.8rem">None</li>';

  bar.innerHTML = `
    <div class="stat-card"><div class="label">Rectangles</div><div class="value">${s.total_rectangles}</div></div>
    <div class="stat-card"><div class="label">Union Area</div><div class="value">${fmt(s.total_area)}</div></div>
    <div class="stat-card"><div class="label">Overlap Area</div><div class="value">${fmt(s.overlap_area)}</div></div>
    <div class="stat-card"><div class="label">Coverage Efficiency</div><div class="value">${fmt(s.coverage_efficiency * 100)}%</div></div>
    <div class="stat-card"><div class="label">Max Overlap Count</div><div class="value">${data.max_overlap_point?.count ?? 0}</div></div>
    <div class="stat-card" style="flex:1;min-width:200px">
      <div class="label">Overlapping Pairs (${s.overlapping_pairs})</div>
      <ul class="overlap-list">${overlapTags}</ul>
    </div>`;
}

// ── Resize handler ────────────────────────────────────────────────────────────
window.addEventListener('resize', () => {
  if (document.getElementById('resultsBar').style.display !== 'none') {
    document.getElementById('canvasHint').style.display = 'flex';
    const canvas = document.getElementById('canvas');
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  }
});
