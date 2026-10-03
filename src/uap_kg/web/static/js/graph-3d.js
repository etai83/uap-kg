/* Cross-case graph as 3D text nodes, same ForceGraph3D setup as case-3d. */
const TYPE_LABEL = {
  named_person: "Persons",
  object: "Object",
  uap_item: "UAP item",
  location: "Location",
  date_time: "Date and time",
  organization: "Organization",
  project: "Project",
};

const NODE_COLOR = {
  person: "#00E5FF",
  claim: "#FFE14A",
  named_person: "#FF3EC8",
  uap_item: "#FF3B5C",
  location: "#3DFF8A",
  organization: "#FF7A1A",
  project: "#C6F54A",
  object: "#4F86FF",
  date_time: "#E2B0FF",
};

const EDGE_COLOR = {
  made: "rgba(0,229,255,0.9)",
  about: "rgba(232,238,247,0.55)",
  elaborates: "rgba(255,225,74,0.9)",
  same_assertion: "rgba(226,176,255,0.9)",
  contradicts: "rgba(255,59,92,0.95)",
  same_surface: "rgba(244,247,251,0.95)",
  co_mention: "rgba(0,229,255,0.55)",
};

const inspectEl = document.getElementById("graph-inspect-body");
const statusEl = document.getElementById("graph-status");
const stage = document.getElementById("graph-cy");


let payload = null;
let fg = null;
let SpriteText = null;
let nodes = [];
let links = [];
let byId = new Map();
let sprites = new Map();
let viewIds = new Set();
let hot = null;
let hovered = null;
let selected = null;
let sameAnchor = null;
let activeType = "all";
let query = "";
let fitted = false;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}

function clock(t) {
  const s = Math.max(0, Math.floor(Number(t) || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  const mm = String(m).padStart(2, "0");
  const ss = String(r).padStart(2, "0");
  return h ? h + ":" + mm + ":" + ss : m + ":" + ss;
}

function timeRange(node) {
  if (node.tStart == null && node.tEnd == null) return "—";
  if (node.tEnd == null) return clock(node.tStart);
  if (node.tStart == null) return clock(node.tEnd);
  return clock(node.tStart) + "–" + clock(node.tEnd);
}

function endId(value) {
  return value && typeof value === "object" ? value.id : value;
}

function hashId() {
  const raw = location.hash.length > 1 ? location.hash.slice(1) : "";
  if (!raw) return "";
  try {
    return decodeURIComponent(raw);
  } catch (err) {
    return raw;
  }
}

function colorFor(node) {
  if (node.kind === "person") return NODE_COLOR.person;
  if (node.kind === "claim") return NODE_COLOR.claim;
  return NODE_COLOR[node.entityType] || "#bac9cc";
}

function textHeight(node) {
  if (node.kind === "person") return 8;
  if (node.kind === "claim") return 3.4;
  return 5;
}

function linkWidth(link) {
  if (link.kind === "same_surface") return 1.6;
  if (link.kind === "contradicts") return 1.4;
  if (link.kind === "co_mention") return 0.45;
  return 0.6;
}

function checkedCases() {
  const ids = new Set();
  document.querySelectorAll(".graph-case").forEach((input) => {
    if (input.checked) ids.add(input.getAttribute("data-case"));
  });
  return ids;
}

function neighborIds(id) {
  const near = new Set([id]);
  links.forEach((link) => {
    const source = endId(link.source);
    const target = endId(link.target);
    if (source === id) near.add(target);
    if (target === id) near.add(source);
  });
  return near;
}

function caseList(node) {
  if (node.caseIds && node.caseIds.length) return node.caseIds;
  return node.caseId ? [node.caseId] : [];
}

function casePool() {
  const checked = checkedCases();
  const pool = new Set();
  if (!checked.size) return pool;
  nodes.forEach((node) => {
    if (caseList(node).some((id) => checked.has(id))) pool.add(node.id);
  });
  return pool;
}

function applyType(pool) {
  if (activeType === "all") return new Set(pool);
  if (activeType === "claim") {
    return new Set([...pool].filter((id) => byId.get(id).kind !== "entity"));
  }
  const ids = new Set([...pool].filter((id) => {
    const node = byId.get(id);
    return node && node.kind === "entity" && node.entityType === activeType;
  }));
  links.forEach((link) => {
    const source = endId(link.source);
    const target = endId(link.target);
    const sourceNode = byId.get(source);
    const targetNode = byId.get(target);
    if (ids.has(target) && sourceNode && sourceNode.kind !== "entity" && pool.has(source)) ids.add(source);
    if (ids.has(source) && targetNode && targetNode.kind !== "entity" && pool.has(target)) ids.add(target);
  });
  return ids;
}

function matchesQuery(node) {
  return [node.full, node.label, node.caseShort].join("\n").toLowerCase().includes(query);
}

function shownIds() {
  let ids = casePool();
  const scoped = ids;
  ids = applyType(scoped);
  if (query) {
    const hits = new Set();
    scoped.forEach((id) => {
      const node = byId.get(id);
      if (node && matchesQuery(node)) hits.add(id);
    });
    const widened = new Set(hits);
    links.forEach((link) => {
      const source = endId(link.source);
      const target = endId(link.target);
      if (hits.has(source) && scoped.has(target)) widened.add(target);
      if (hits.has(target) && scoped.has(source)) widened.add(source);
    });
    ids = widened;
  }
  if (selected && byId.has(selected)) ids.add(selected);
  return ids;
}

function linkShown(link) {
  if (!viewIds.has(endId(link.source)) || !viewIds.has(endId(link.target))) return false;
  const checked = checkedCases();
  const cases = link.caseIds || [];
  return !cases.length || cases.some((id) => checked.has(id));
}

function joinedNodes() {
  let count = 0;
  nodes.forEach((node) => {
    if (viewIds.has(node.id) && caseList(node).length > 1) count += 1;
  });
  return count;
}

function sharedWith(node) {
  const seen = new Set();
  const rows = [];
  links.forEach((link) => {
    if (link.kind !== "same_surface") return;
    const source = endId(link.source);
    const target = endId(link.target);
    const otherId = source === node.id ? target : target === node.id ? source : null;
    if (!otherId || seen.has(otherId)) return;
    const other = byId.get(otherId);
    if (!other || other.caseId === node.caseId) return;
    seen.add(otherId);
    rows.push(other);
  });
  rows.sort((a, b) => String(a.caseShort || "").localeCompare(String(b.caseShort || ""))
    || String(a.label || "").localeCompare(String(b.label || "")));
  return rows;
}

function buildModel() {
  nodes = (payload.nodes || []).map((node) => ({
    id: node.id,
    caseId: node.caseId,
    caseIds: node.caseIds && node.caseIds.length ? node.caseIds.slice() : (node.caseId ? [node.caseId] : []),
    caseShort: node.caseShort,
    kind: node.kind,
    entityType: node.entityType,
    label: node.label,
    full: node.full,
    quote: node.quote,
    claimant: node.claimant,
    speaker: node.speaker,
    tStart: node.tStart,
    tEnd: node.tEnd,
    videoId: node.videoId,
    val: node.val,
    members: node.members || [],
    curator: !!node.curator,
    also: node.also || [],
    color: colorFor(node),
  }));
  byId = new Map(nodes.map((node) => [node.id, node]));
  const seen = new Set();
  links = [];
  (payload.links || []).forEach((item) => {
    const source = item.source;
    const target = item.target;
    const kind = item.kind;
    if (!source || !target || source === target || !byId.has(source) || !byId.has(target)) return;
    const key = source + ">" + target + ">" + kind;
    if (seen.has(key)) return;
    seen.add(key);
    links.push({
      source,
      target,
      kind,
      caseIds: item.caseIds || [],
      color: EDGE_COLOR[kind] || "rgba(186,201,204,0.45)",
    });
  });
}

function renderCases() {
  const host = document.getElementById("graph-cases");
  if (!host) return;
  host.innerHTML = (payload.cases || []).map((row) => `
    <label class="inline-flex items-center gap-2 font-label-caps text-label-caps px-3 py-1 border border-outline-variant/40">
      <input type="checkbox" class="graph-case" data-case="${esc(row.id)}" checked>
      ${esc(row.short)}
    </label>
  `).join("");
}

function spriteFor(node) {
  let sprite = sprites.get(node.id);
  if (!sprite) {
    sprite = new SpriteText(node.label);
    sprite.fontFace = "Inter, sans-serif";
    sprite.textHeight = textHeight(node);
    sprite.center.y = -0.6;
    sprite.material.depthWrite = false;
    sprites.set(node.id, sprite);
  }
  const dim = hot && !hot.has(node.id) && node.id !== hovered;
  sprite.color = dim ? "#6d7c8a" : node.color;
  return sprite;
}

function insideLinks() {
  let count = 0;
  links.forEach((link) => {
    if (linkShown(link)) count += 1;
  });
  return count;
}

function writeStatus() {
  if (!statusEl) return;
  const selectedCases = checkedCases().size;
  const label = query ? "Search" : selectedCases + (selectedCases === 1 ? " case" : " cases");
  statusEl.textContent = label + " · " + viewIds.size + " nodes · " + insideLinks() + " links · " + joinedNodes() + " joined";
}

function paint() {
  if (!fg) return;
  nodes.forEach(spriteFor);
  fg.nodeVisibility((node) => viewIds.has(node.id));
  fg.linkVisibility((link) => linkShown(link));
  fg.nodeColor((node) => (hot && !hot.has(node.id) && node.id !== hovered) ? "#24384a" : node.color);
  fg.linkColor((link) => {
    const source = endId(link.source);
    const target = endId(link.target);
    if (hot && !(hot.has(source) && hot.has(target))) return "rgba(186,201,204,0.08)";
    return EDGE_COLOR[link.kind] || "rgba(186,201,204,0.45)";
  });
  fg.linkWidth(linkWidth);
}

function fitVisible() {
  if (!fg) return;
  const hasPos = nodes.some((node) => viewIds.has(node.id) && Number.isFinite(node.x));
  if (!hasPos) return;
  fg.zoomToFit(450, 70, (node) => viewIds.has(node.id));
}

function refresh(fit) {
  viewIds = shownIds();
  writeStatus();
  paint();
  if (fit) fitVisible();
}

function nameKey(text) {
  return String(text || "").toLowerCase().replace(/[^a-z0-9' ]+/g, " ").replace(/\s+/g, " ").trim();
}

function nameTokens(text) {
  return nameKey(text).split(" ").filter((token) => token.length >= 2);
}

function levenshtein(left, right) {
  const rows = left.length + 1;
  const cols = right.length + 1;
  const grid = Array.from({ length: rows }, () => new Array(cols).fill(0));
  for (let i = 0; i < rows; i++) grid[i][0] = i;
  for (let j = 0; j < cols; j++) grid[0][j] = j;
  for (let i = 1; i < rows; i++) {
    for (let j = 1; j < cols; j++) {
      const cost = left[i - 1] === right[j - 1] ? 0 : 1;
      grid[i][j] = Math.min(grid[i - 1][j] + 1, grid[i][j - 1] + 1, grid[i - 1][j - 1] + cost);
    }
  }
  return grid[left.length][right.length];
}

function stringRatio(left, right) {
  if (!left || !right) return 0;
  if (left === right) return 1;
  const dist = levenshtein(left, right);
  return 1 - dist / Math.max(left.length, right.length);
}

function soundex(word) {
  const text = String(word || "").toLowerCase().replace(/[^a-z]/g, "");
  if (!text) return "";
  const map = { b: "1", f: "1", p: "1", v: "1", c: "2", g: "2", j: "2", k: "2", q: "2", s: "2", x: "2", z: "2", d: "3", t: "3", l: "4", m: "5", n: "5", r: "6" };
  let code = text[0].toUpperCase();
  let previous = map[text[0]] || "";
  for (let i = 1; i < text.length && code.length < 4; i++) {
    const next = map[text[i]] || "";
    if (next && next !== previous) code += next;
    if (next || "aeiouy".includes(text[i])) previous = next;
  }
  return code.padEnd(4, "0");
}

function extendsName(shorter, longer) {
  if (!shorter || shorter.length < 3 || shorter === longer) return false;
  const tokens = longer.split(" ").filter(Boolean);
  if (tokens.includes(shorter)) return true;
  return shorter.length >= 5 && longer.includes(shorter);
}

function initialsOf(text) {
  return nameTokens(text).map((token) => token[0]).join("");
}

function nameMatch(leftText, rightText) {
  const left = nameKey(leftText);
  const right = nameKey(rightText);
  if (!left || !right) return null;
  if (left === right) return { score: 0.99, reason: "Same name" };
  const shorter = left.length <= right.length ? left : right;
  const longer = left.length <= right.length ? right : left;
  let score = 0;
  let reason = "";
  if (extendsName(shorter, longer)) {
    score = 0.92 + 0.06 * (shorter.length / longer.length);
    reason = "Longer form of this name";
  }
  const leftTokens = nameTokens(left);
  const rightTokens = nameTokens(right);
  const shared = leftTokens.filter((token) => rightTokens.includes(token));
  if (shared.length && leftTokens.length && rightTokens.length) {
    const overlap = shared.length / Math.max(leftTokens.length, rightTokens.length);
    if (overlap > score) {
      score = overlap;
      reason = "Shares part of this name";
    }
  }
  const spelling = Math.max(stringRatio(left, right), stringRatio(shorter, longer));
  if (spelling >= 0.72 && spelling > score) {
    score = spelling;
    reason = "Close spelling";
  }
  let soundRatio = 0;
  leftTokens.forEach((token) => {
    if (token.length < 4) return;
    rightTokens.forEach((other) => {
      if (other === token || other.length < 4 || soundex(token) !== soundex(other)) return;
      soundRatio = Math.max(soundRatio, stringRatio(token, other));
    });
  });
  if (soundRatio >= 0.55) {
    const soundScore = 0.72 + 0.2 * soundRatio;
    if (soundScore > score) {
      score = soundScore;
      reason = "Sounds like this name";
    }
  }
  if (shorter.length >= 3 && shorter.length <= 6 && !shorter.includes(" ") && initialsOf(longer) === shorter) {
    score = Math.max(score, 0.76);
    if (score === 0.76) reason = "Initials of this name";
  }
  if (score < 0.55) return null;
  return { score, reason };
}

function closestNames(node) {
  const ranked = [];
  nodes.forEach((other) => {
    if (other.id === node.id || other.kind === "claim") return;
    const match = nameMatch(node.full || node.label, other.full || other.label);
    if (!match) return;
    const sameType = other.entityType && other.entityType === node.entityType ? 0.02 : 0;
    ranked.push({ node: other, score: match.score + sameType, reason: match.reason });
  });
  ranked.sort((a, b) => b.score - a.score || String(a.node.full || "").length - String(b.node.full || "").length);
  return ranked.slice(0, 10);
}

function closestList(node) {
  const rows = closestNames(node);
  if (!rows.length) return `<p class="mt-4">No close names.</p>`;
  return `<div class="mt-4">
    <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">Closest names</div>
    ${rows.map((row) => {
      const typeName = TYPE_LABEL[row.node.entityType] || (row.node.kind === "person" ? "Person" : "Entity");
      return `<button type="button" data-node="${esc(row.node.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">
        <span class="text-on-surface">${esc(row.node.full || row.node.label)}</span>
        <span class="block text-[11px] text-on-surface-variant">${esc(typeName)} · ${esc(row.node.caseShort || "")} · ${esc(row.reason)}</span>
      </button>`;
    }).join("")}
  </div>`;
}

function joinPanel(node) {
  if (node.kind === "claim") {
    if (!sameAnchor) return "";
    return `<p class="mt-4">A claim stays a claim. Select an entity or a person.</p>
      <button type="button" data-action="same-cancel" class="mt-2 font-label-caps text-label-caps px-3 py-1 border border-outline-variant/40">Cancel</button>`;
  }
  const armed = sameAnchor && byId.has(sameAnchor) ? byId.get(sameAnchor) : null;
  const also = node.also && node.also.length
    ? `<p class="mt-3">Also called ${esc(node.also.join(", "))}.</p>`
    : "";
  if (armed && armed.id === node.id) {
    return `${also}<p class="mt-4">Choose the other node from the closest names.</p>
      ${closestList(node)}
      <button type="button" data-action="same-cancel" class="mt-2 font-label-caps text-label-caps px-3 py-1 border border-outline-variant/40">Cancel</button>`;
  }
  if (armed) {
    return `${also}<p class="mt-4">Which node should stay? Links from the other node move onto the one you keep.</p>
      <button type="button" data-action="same-keep" data-keep="${esc(armed.id)}" class="block w-full text-left mt-2 font-label-caps text-label-caps px-3 py-1 border border-primary text-primary">Keep ${esc(armed.full || armed.label)}</button>
      <button type="button" data-action="same-keep" data-keep="${esc(node.id)}" class="block w-full text-left mt-2 font-label-caps text-label-caps px-3 py-1 border border-primary text-primary">Keep ${esc(node.full || node.label)}</button>
      <button type="button" data-action="same-cancel" class="mt-2 font-label-caps text-label-caps px-3 py-1 border border-outline-variant/40">Cancel</button>`;
  }
  return `${also}<button type="button" data-action="same-arm" class="mt-4 font-label-caps text-label-caps px-3 py-1 border border-primary text-primary">This is the same as…</button>`;
}

function logPanel() {
  const log = payload && payload.log ? payload.log : [];
  const undo = payload && payload.undo ? payload.undo : [];
  if (!log.length && !undo.length) return "";
  const rows = log.map((entry) => `<div class="mb-3">
      <p><span class="text-on-surface">${esc(entry.keepLabel)}</span> stayed. ${esc(entry.replaceLabel)} was replaced.</p>
      <p class="text-[11px] text-on-surface-variant">${esc(String(entry.at || "").replace("T", " ").replace("+00:00", " UTC"))}</p>
      <button type="button" data-action="log-revert" data-index="${Number(entry.index) - 1}" class="mt-1 font-label-caps text-label-caps px-2 py-1 border border-outline-variant/40">Restore the graph from before this</button>
    </div>`).join("");
  const undone = undo.length ? `<p class="mt-3">A newer version is saved.</p>
      ${undo.map((entry) => `<p class="text-[11px]">${esc(entry.keepLabel)} stayed. ${esc(entry.replaceLabel)} was replaced.</p>`).join("")}
      <button type="button" data-action="log-redo" class="mt-1 font-label-caps text-label-caps px-2 py-1 border border-primary text-primary">Restore the newer version</button>` : "";
  return `<div class="mt-6 pt-3 border-t border-outline-variant/30">
    <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">Join log</div>
    ${rows}
    ${undone}
  </div>`;
}

function applyPayload(data, selectId) {
  payload = data;
  sprites = new Map();
  const checked = new Set(checkedCases());
  buildModel();
  renderCases();
  if (checked.size) {
    document.querySelectorAll(".graph-case").forEach((box) => {
      box.checked = checked.has(box.dataset.case);
    });
  }
  fitted = false;
  if (fg) fg.graphData({ nodes, links });
  if (selectId && byId.has(selectId)) select(selectId, true);
  else {
    selected = null;
    hot = null;
    renderInspect(null);
    refresh(true);
  }
}

async function postGraph(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  if (!response.ok) {
    const text = await response.text();
    if (inspectEl) inspectEl.textContent = text || "The graph was not changed.";
    return null;
  }
  return response.json();
}

async function joinSame(keepId) {
  const anchor = sameAnchor && byId.get(sameAnchor);
  const other = selected && byId.get(selected);
  if (!anchor || !other || anchor.id === other.id) return;
  if (keepId !== anchor.id && keepId !== other.id) return;
  const replaceId = keepId === anchor.id ? other.id : anchor.id;
  const members = new Set([...(anchor.members || []), ...(other.members || [])]);
  const data = await postGraph("/api/graph/same", { keep: keepId, replace: replaceId });
  if (!data) return;
  sameAnchor = null;
  const next = (data.nodes || []).find((node) => (node.members || []).some((id) => members.has(id)));
  applyPayload(data, next ? next.id : null);
}

async function revertLog(index) {
  const data = await postGraph("/api/graph/revert", { index: index });
  if (!data) return;
  sameAnchor = null;
  applyPayload(data, null);
}

async function restoreLog() {
  const data = await postGraph("/api/graph/restore", {});
  if (!data) return;
  sameAnchor = null;
  applyPayload(data, null);
}

function select(id, shouldCenter) {
  selected = id && byId.has(id) ? id : null;
  hot = selected ? neighborIds(selected) : null;
  if (selected && location.hash !== "#" + encodeURIComponent(selected)) {
    history.replaceState(null, "", "#" + encodeURIComponent(selected));
  }
  if (!selected && location.hash) history.replaceState(null, "", location.pathname + location.search);
  renderInspect(selected);
  refresh(false);
  if (shouldCenter && selected) centerOn(selected);
}

function centerOn(id) {
  const node = byId.get(id);
  if (!fg || !node || !Number.isFinite(node.x)) return;
  const dist = Math.hypot(node.x, node.y, node.z) || 1;
  const ratio = 1 + 80 / dist;
  fg.cameraPosition(
    { x: node.x * ratio, y: node.y * ratio, z: node.z * ratio },
    node,
    700
  );
}

function renderInspect(id) {
  if (!inspectEl) return;
  if (!id) {
    inspectEl.innerHTML = "Select a claim or an entity. To say two nodes are the same, open one and choose This is the same as. Drag to orbit. Scroll to zoom." + logPanel();
    return;
  }
  const node = byId.get(id);
  if (!node) {
    inspectEl.innerHTML = "Select a claim or an entity. To say two nodes are the same, open one and choose This is the same as. Drag to orbit. Scroll to zoom." + logPanel();
    return;
  }
  if (node.kind === "claim") {
    const seconds = Math.floor(Number(node.tStart) || 0);
    const href = node.videoId && node.tStart != null
      ? "https://www.youtube.com/watch?v=" + node.videoId + "&t=" + seconds
      : "";
    inspectEl.innerHTML = `
      <div class="font-label-caps text-label-caps text-primary mb-2">Claim · proposed</div>
      <p class="text-on-surface mb-3">${esc(node.full || node.label)}</p>
      <p class="mb-2"><span class="text-on-surface-variant">Claimant.</span> ${esc(node.claimant || "—")}</p>
      <p class="mb-2"><span class="text-on-surface-variant">Speaker.</span> ${esc(node.speaker || "—")}</p>
      <p class="mb-2"><span class="text-on-surface-variant">Time.</span> ${esc(timeRange(node))}</p>
      <p class="italic text-on-surface mb-3">${node.quote ? "“" + esc(node.quote) + "”" : "—"}</p>
      <p class="mb-3"><span class="text-on-surface-variant">Case.</span> ${esc(node.caseShort || "—")}</p>
      ${href ? `<a class="text-primary font-mono-data text-[12px]" href="${esc(href)}" target="_blank" rel="noreferrer">Open this moment</a>` : ""}
      ${joinPanel(node)}
      ${logPanel()}
    `;
    return;
  }
  if (node.kind === "entity") {
    const typeName = TYPE_LABEL[node.entityType] || node.entityType || "Entity";
    const joined = caseList(node).length > 1;
    inspectEl.innerHTML = `
      <div class="font-label-caps text-label-caps text-primary mb-2">${esc(typeName)} · proposed</div>
      <p class="mb-2"><span class="text-on-surface-variant">Cases.</span> ${esc(node.caseShort || "—")}</p>
      <p class="text-on-surface mb-3">${esc(node.full || node.label)}</p>
      ${node.quote ? `<p class="italic text-on-surface mb-3">“${esc(node.quote)}”</p>` : ""}
      <p>${joined ? "This name is one node for every selected interview that uses it." : "This name appears in one case."}</p>
      ${joinPanel(node)}
      ${logPanel()}
    `;
    return;
  }
  inspectEl.innerHTML = `
    <p class="text-on-surface mb-3">${esc(node.full || node.label)}</p>
    <p class="mb-3"><span class="text-on-surface-variant">Case.</span> ${esc(node.caseShort || "—")}</p>
    <p>This is a person in the case.</p>
    ${joinPanel(node)}
    ${logPanel()}
  `;
}

function bind() {
  if (inspectEl) {
    inspectEl.addEventListener("click", (event) => {
      const action = event.target.closest("[data-action]");
      if (action) {
        const name = action.getAttribute("data-action");
        if (name === "same-arm") {
          sameAnchor = selected;
          renderInspect(selected);
          return;
        }
        if (name === "same-cancel") {
          sameAnchor = null;
          renderInspect(selected);
          return;
        }
        if (name === "same-keep") {
          joinSame(action.getAttribute("data-keep"));
          return;
        }
        if (name === "log-revert") {
          revertLog(Number(action.getAttribute("data-index")));
          return;
        }
        if (name === "log-redo") {
          restoreLog();
          return;
        }
        return;
      }
      const button = event.target.closest("[data-node]");
      if (!button) return;
      select(button.getAttribute("data-node"), true);
    });
  }
  window.addEventListener("hashchange", () => {
    const hash = hashId();
    if (hash && byId.has(hash)) select(hash, true);
  });
  document.querySelectorAll(".graph-filter").forEach((button) => {
    button.addEventListener("click", () => {
      activeType = button.getAttribute("data-type");
      document.querySelectorAll(".graph-filter").forEach((item) => {
        const on = item === button;
        item.classList.toggle("border-primary", on);
        item.classList.toggle("text-primary", on);
        item.classList.toggle("border-outline-variant/40", !on);
        item.classList.toggle("text-on-surface-variant", !on);
      });
      refresh(true);
    });
  });
  const cases = document.getElementById("graph-cases");
  if (cases) {
    cases.addEventListener("change", (event) => {
      if (!event.target.classList || !event.target.classList.contains("graph-case")) return;
      refresh(true);
    });
  }
  const search = document.getElementById("graph-search");
  if (search) {
    search.addEventListener("input", (event) => {
      query = event.target.value.trim().toLowerCase();
      refresh(true);
    });
  }
  const fit = document.getElementById("graph-fit");
  if (fit) fit.addEventListener("click", fitVisible);
  window.addEventListener("resize", () => {
    if (!fg || !stage) return;
    fg.width(stage.clientWidth || 640);
    fg.height(stage.clientHeight || 480);
    fitVisible();
  });
}

function mount(ForceGraph3D) {
  viewIds = shownIds();
  fg = ForceGraph3D()(stage)
    .backgroundColor("#010f1f")
    .showNavInfo(false)
    .nodeId("id")
    .nodeVal("val")
    .nodeRelSize(4)
    .nodeOpacity(0.9)
    .nodeLabel((node) => node.full || node.label)
    .nodeThreeObjectExtend(true)
    .nodeThreeObject(spriteFor)
    .linkOpacity(0.7)
    .linkDirectionalArrowLength(3.5)
    .linkDirectionalArrowRelPos(1)
    .linkDirectionalArrowColor((link) => EDGE_COLOR[link.kind] || "#bac9cc")
    .warmupTicks(40)
    .cooldownTicks(160)
    .onNodeClick((node) => select(node.id, false))
    .onBackgroundClick(() => select(null, false))
    .onNodeHover((node) => {
      hovered = node ? node.id : null;
      stage.style.cursor = node ? "pointer" : "grab";
      paint();
    })
    .onEngineStop(() => {
      if (fitted) return;
      fitted = true;
      refresh(false);
      fitVisible();
    });
  const charge = fg.d3Force("charge");
  if (charge) charge.strength(-90);
  fg.graphData({ nodes, links });
  fg.width(stage.clientWidth || 640);
  fg.height(stage.clientHeight || 480);
  const hash = hashId();
  if (hash && byId.has(hash)) select(hash, false);
  else {
    renderInspect(null);
    refresh(false);
  }
}

async function main() {
  let ForceGraph3D;
  try {
    const graphMod = await import("3d-force-graph");
    const textMod = await import("three-spritetext");
    ForceGraph3D = graphMod.default;
    SpriteText = textMod.default;
  } catch (err) {
    if (inspectEl) inspectEl.textContent = "The 3D graph did not load.";
    console.error(err);
    return;
  }
  if (typeof ForceGraph3D !== "function" || typeof SpriteText !== "function") {
    if (inspectEl) inspectEl.textContent = "The 3D graph did not load.";
    return;
  }
  try {
    const response = await fetch("/api/graph");
    if (!response.ok) throw new Error(String(response.status));
    payload = await response.json();
  } catch (err) {
    if (inspectEl) inspectEl.textContent = "The 3D graph did not load.";
    console.error(err);
    return;
  }
  const current = document.querySelector(".graph-filter.border-primary");
  if (current) activeType = current.getAttribute("data-type") || "all";
  if (statusEl) statusEl.textContent = "Arranging the graph…";
  buildModel();
  renderCases();
  bind();
  try {
    mount(ForceGraph3D);
  } catch (err) {
    if (inspectEl) inspectEl.textContent = "The 3D graph did not start.";
    console.error(err);
  }
}

if (document.fonts && document.fonts.ready) document.fonts.ready.then(main);
else main();
