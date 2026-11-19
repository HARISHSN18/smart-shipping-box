const $ = (s) => document.querySelector(s);
const itemsEl = $("#items"), resultEl = $("#result"), goBtn = $("#go");
let products = [];

const COLORS = ["#ffc933", "#7dd3fc", "#fca5a5", "#86efac", "#c4b5fd", "#fdba74"];

async function loadProducts() {
  try {
    const r = await fetch("/api/products/?page_size=100");
    const d = await r.json();
    products = d.results || d;
  } catch (e) { products = []; }
  addItem();
}

function addItem() {
  const div = document.createElement("div");
  div.className = "item";
  div.innerHTML = `
    <div class="row">
      <label>Product
        <select class="prod">
          <option value="">Custom size…</option>
          ${products.map(p => `<option value="${p.sku}">${p.name} (${p.sku})</option>`).join("")}
        </select>
      </label>
      <label style="max-width:90px">Quantity<input class="qty" type="number" min="1" value="1"></label>
      <button type="button" class="remove">Remove</button>
    </div>
    <div class="row dims">
      <label>Length<input class="l" type="number" min="0.1" step="any"></label>
      <label>Width<input class="w" type="number" min="0.1" step="any"></label>
      <label>Height<input class="h" type="number" min="0.1" step="any"></label>
      <label>Weight<input class="kg" type="number" min="0" step="any"></label>
      <label class="check"><input class="fr" type="checkbox"> Fragile</label>
    </div>`;
  const sel = div.querySelector(".prod"), dims = div.querySelector(".dims");
  sel.onchange = () => { dims.style.display = sel.value ? "none" : "flex"; };
  div.querySelector(".remove").onclick = () => { if (itemsEl.children.length > 1) div.remove(); };
  itemsEl.appendChild(div);
}

function collect() {
  return [...itemsEl.children].map(el => {
    const q = +el.querySelector(".qty").value || 1;
    const sku = el.querySelector(".prod").value;
    if (sku) return { sku, quantity: q };
    return {
      length: +el.querySelector(".l").value, width: +el.querySelector(".w").value,
      height: +el.querySelector(".h").value, weight: +el.querySelector(".kg").value || 0,
      is_fragile: el.querySelector(".fr").checked, quantity: q,
    };
  });
}

function errText(data) {
  const flat = JSON.stringify(data);
  return flat.includes("missing") || flat.includes("required")
    ? "Fill in length, width, height and weight for each custom item, or pick a product."
    : "Something in the order isn’t valid. Check the sizes and quantities.";
}

function diagram(box, placements) {
  const [L, W] = box.dimensions_cm, s = 300 / Math.max(L, W);
  const rects = placements.map((p, i) =>
    `<rect x="${p.x * s}" y="${p.y * s}" width="${p.l * s}" height="${p.w * s}" fill="${COLORS[i % COLORS.length]}" fill-opacity=".85" stroke="#12263a" stroke-width="1.5"/>`).join("");
  return `<div>
    <svg viewBox="-6 -6 ${L * s + 12} ${W * s + 12}" role="img" aria-label="Top-down view of items packed in the box">
      <rect width="${L * s}" height="${W * s}" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="6 4"/>${rects}
    </svg>
    <p class="cap">Top-down view. Items stacked on top of each other share the same spot.</p></div>`;
}


const f = (n) => Math.round(n * 100) / 100;

function cuboid(cls, x, y, z, l, w, h, s, L, W, H, color) {
  const pl = f(l * s), pw = f(w * s), ph = f(h * s);
  const cx = f((x + l / 2 - L / 2) * s), cy = f((H / 2 - (z + h / 2)) * s), cz = f((y + w / 2 - W / 2) * s);
  const bg = color ? `background:${color};` : "";
  const faces = {
    front: `width:${pl}px;height:${ph}px;transform:translateZ(${pw / 2}px)`,
    back: `width:${pl}px;height:${ph}px;transform:rotateY(180deg) translateZ(${pw / 2}px)`,
    right: `width:${pw}px;height:${ph}px;left:${f((pl - pw) / 2)}px;transform:rotateY(90deg) translateZ(${pl / 2}px)`,
    left: `width:${pw}px;height:${ph}px;left:${f((pl - pw) / 2)}px;transform:rotateY(-90deg) translateZ(${pl / 2}px)`,
    top: `width:${pl}px;height:${pw}px;top:${f((ph - pw) / 2)}px;transform:rotateX(90deg) translateZ(${ph / 2}px)`,
    bottom: `width:${pl}px;height:${pw}px;top:${f((ph - pw) / 2)}px;transform:rotateX(-90deg) translateZ(${ph / 2}px)`,
  };
  return `<div class="cub ${cls}" style="width:${pl}px;height:${ph}px;left:${-pl / 2}px;top:${-ph / 2}px;transform:translate3d(${cx}px,${cy}px,${cz}px)">${
    Object.entries(faces).map(([k, st]) => `<div class="face f-${k}" style="${bg}${st}"></div>`).join("")}</div>`;
}

function viewer(b) {
  const [L, W, H] = b.dimensions_cm, s = 230 / Math.max(L, W, H);
  const items = b.placements.map((p, i) =>
    cuboid("item", p.x, p.y, p.z, p.l, p.w, p.h, s, L, W, H, COLORS[i % COLORS.length])).join("");
  const fw = f(L * s * 1.7), fd = f(W * s * 1.7);
  const floor = `<div class="floor" style="width:${fw}px;height:${fd}px;left:${-fw / 2}px;top:${-fd / 2}px;transform:translateY(${f(H * s / 2 + 2)}px) rotateX(90deg)"></div>`;
  return `<figure class="blueprint viewer" style="margin-inline:0">
    <div class="tabs">
      <button type="button" class="tab" data-v="3d" aria-pressed="true">3D view</button>
      <button type="button" class="tab" data-v="2d" aria-pressed="false">Top view</button>
    </div>
    <div class="stage" aria-label="3D view of the items packed in the box. Drag to rotate."><div class="scene">${floor}${items}${cuboid("shell", 0, 0, 0, L, W, H, s, L, W, H)}</div></div>
    <div class="view2d" hidden>${diagram(b, b.placements)}</div>
    <label class="lidtoggle"><input type="checkbox" class="lid-cb"> Close the lid</label>
    <figcaption class="cap3d">Drag to rotate the box. Each color is one item.</figcaption>
  </figure>`;
}

function init3d(root) {
  const stage = root.querySelector(".stage"), scene = root.querySelector(".scene"), v2 = root.querySelector(".view2d");
  let rx = -24, ry = -32, drag = null;
  let auto = !matchMedia("(prefers-reduced-motion: reduce)").matches;
  const apply = () => { scene.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg)`; };
  apply();
  stage.onpointerdown = (e) => { drag = { x: e.clientX, y: e.clientY }; auto = false; stage.setPointerCapture(e.pointerId); };
  stage.onpointermove = (e) => {
    if (!drag) return;
    ry += (e.clientX - drag.x) * 0.5;
    rx = Math.max(-90, Math.min(90, rx - (e.clientY - drag.y) * 0.5));
    drag = { x: e.clientX, y: e.clientY }; apply();
  };
  stage.onpointerup = stage.onpointercancel = () => { drag = null; };
  (function tick() { if (!root.isConnected) return; if (auto) { ry += 0.25; apply(); } requestAnimationFrame(tick); })();
  root.querySelector(".lid-cb").onchange = (e) => root.classList.toggle("closed", e.target.checked);
  root.querySelectorAll(".tab").forEach((t) => t.onclick = () => {
    const is3d = t.dataset.v === "3d";
    root.querySelectorAll(".tab").forEach((x) => x.setAttribute("aria-pressed", String(x === t)));
    stage.hidden = !is3d; v2.hidden = is3d;
    root.querySelector(".lidtoggle").hidden = !is3d; root.querySelector(".cap3d").hidden = !is3d;
  });
}

async function run() {
  goBtn.disabled = true; goBtn.textContent = "Finding box…";
  try {
    const res = await fetch("/api/recommend-box/", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: collect() }),
    });
    const data = await res.json();
    if (res.status === 400) { resultEl.innerHTML = `<div class="error">${errText(data)}</div>`; return; }
    if (!res.ok) { resultEl.innerHTML = `<div class="error">${data.message || "No box found."} Add a bigger box on the Boxes API or split the order.</div>`; return; }
    const b = data.recommended, pct = Math.round(b.fill_rate * 100);
    resultEl.innerHTML = `
      <div class="best">
        <h3>${b.box_name}</h3>
        <p class="dim">${b.dimensions_cm.join(" × ")} cm</p>
        <div class="meter" role="img" aria-label="${pct}% full"><i style="width:0" data-w="${pct}"></i></div>
        <div class="stats">
          <div class="stat"><b>${pct}%</b><span>Box filled</span></div>
          <div class="stat"><b>${b.total_weight_kg} kg</b><span>Total weight</span></div>
          <div class="stat"><b>$${b.cost}</b><span>Box cost</span></div>
        </div>
        ${viewer(b)}
        ${data.alternatives.length ? `<div class="alts"><h4>Other boxes that fit</h4>${
          data.alternatives.map(a => `<div class="alt"><span>${a.box_name} (${a.dimensions_cm.join(" × ")})</span><span>$${a.cost} · ${Math.round(a.fill_rate * 100)}% full</span></div>`).join("")}</div>` : ""}
      </div>`;
    init3d(resultEl.querySelector(".viewer"));
    requestAnimationFrame(() => { const i = resultEl.querySelector(".meter i"); i.style.width = i.dataset.w + "%"; });
  } catch (e) {
    resultEl.innerHTML = `<div class="error">Can’t reach the server. Check that it’s running and try again.</div>`;
  } finally { goBtn.disabled = false; goBtn.textContent = "Find best box"; }
}

$("#add").onclick = addItem;
goBtn.onclick = run;
loadProducts();
