/* Borland case as a 3D text-node graph, the same pattern as react-force-graph's text-nodes example. */
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
};

const inspectEl = document.getElementById("case-inspect-body");
const statusEl = document.getElementById("case-status");
const stage = document.getElementById("case-cy");

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

function clip(text, max) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > max ? clean.slice(0, max - 1) + "…" : clean;
}

function person(id) {
  return (payload.persons || []).find((row) => row.id === id);
}

function entity(id) {
  return (payload.entities || []).find((row) => row.id === id);
}

function claim(id) {
  return (payload.claims || []).find((row) => row.id === id);
}

function personCopy(who) {
  if (who.role === "claimant") return "This person made the claims below. A named person in the text is a different role.";
  if (who.role === "host") return "This person is the host. A host question is not a world claim.";
  if (who.role === "played voice") return "This voice is audio played in the interview. It is not Dylan Borland.";
  return "This person is on the record for this case.";
}

function endId(value) {
  return value && typeof value === "object" ? value.id : value;
}

function textOf(node) {
  return String((node && (node.full || node.label)) || "").toLowerCase();
}

function textHeight(node) {
  if (node.kind === "person") return 8;
  if (node.kind === "claim") return 3.4;
  return 5;
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

function shownIds() {
  const pool = new Set(nodes.map((node) => node.id));
  let ids = pool;
  if (activeType === "claim") {
    ids = new Set([...pool].filter((id) => byId.get(id).kind !== "entity"));
  } else if (activeType !== "all") {
    ids = new Set([...pool].filter((id) => {
      const node = byId.get(id);
      return node.kind === "entity" && node.entityType === activeType;
    }));
    links.forEach((link) => {
      const source = endId(link.source);
      const target = endId(link.target);
      const sourceNode = byId.get(source);
      const targetNode = byId.get(target);
      if (ids.has(target) && sourceNode && sourceNode.kind !== "entity") ids.add(source);
      if (ids.has(source) && targetNode && targetNode.kind !== "entity") ids.add(target);
    });
  }
  if (query) {
    const hits = new Set();
    nodes.forEach((node) => {
      if (textOf(node).includes(query)) hits.add(node.id);
    });
    const widened = new Set(hits);
    links.forEach((link) => {
      const source = endId(link.source);
      const target = endId(link.target);
      if (hits.has(source)) widened.add(target);
      if (hits.has(target)) widened.add(source);
    });
    ids = widened;
  }
  if (selected && byId.has(selected)) ids.add(selected);
  return ids;
}

function buildModel() {
  const linked = new Set();
  (payload.claims || []).forEach((item) => (item.entity_ids || []).forEach((id) => linked.add(id)));
  nodes = [];
  (payload.persons || []).forEach((item) => {
    nodes.push({
      id: item.id,
      kind: "person",
      label: item.name,
      full: item.name,
      color: NODE_COLOR.person,
      val: 4,
    });
  });
  (payload.claims || []).forEach((item) => {
    nodes.push({
      id: item.id,
      kind: "claim",
      label: clip(item.text, 42),
      full: item.text,
      color: NODE_COLOR.claim,
      val: 1.4,
    });
  });
  (payload.entities || []).forEach((item) => {
    nodes.push({
      id: item.id,
      kind: "entity",
      entityType: item.type,
      label: item.name,
      full: item.name,
      color: NODE_COLOR[item.type] || "#bac9cc",
      val: linked.has(item.id) ? 1 : 0.6,
    });
  });
  byId = new Map(nodes.map((node) => [node.id, node]));
  const seen = new Set();
  links = [];
  function addLink(source, target, kind) {
    if (!source || !target || source === target || !byId.has(source) || !byId.has(target)) return;
    const key = source + ">" + target + ">" + kind;
    if (seen.has(key)) return;
    seen.add(key);
    links.push({ source, target, kind, color: EDGE_COLOR[kind] || "rgba(186,201,204,0.45)" });
  }
  (payload.claims || []).forEach((item) => {
    addLink(item.id, item.claimant_id, "made");
    (item.entity_ids || []).forEach((id) => addLink(item.id, id, "about"));
  });
  (payload.links || []).forEach((item) => addLink(item.source, item.target, item.kind || "elaborates"));
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

function syncEngineLinks() {
  const hash = selected ? "#" + selected : "";
  const columns = document.getElementById("case-engine-columns");
  const sigma = document.getElementById("case-engine-sigma");
  if (columns) columns.href = "/case/borland" + hash;
  if (sigma) sigma.href = "/case/borland/sigma" + hash;
}

function writeStatus() {
  if (!statusEl) return;
  const typeName = activeType === "all"
    ? "Connected case"
    : (activeType === "claim" ? "Claims" : (TYPE_LABEL[activeType] || activeType));
  statusEl.textContent = (query ? "Search" : typeName) + " · " + viewIds.size + " nodes";
}

function paint() {
  if (!fg) return;
  nodes.forEach(spriteFor);
  fg.nodeVisibility((node) => viewIds.has(node.id));
  fg.linkVisibility((link) => viewIds.has(endId(link.source)) && viewIds.has(endId(link.target)));
  fg.nodeColor((node) => (hot && !hot.has(node.id) && node.id !== hovered) ? "#24384a" : node.color);
  fg.linkColor((link) => {
    const source = endId(link.source);
    const target = endId(link.target);
    if (hot && !(hot.has(source) && hot.has(target))) return "rgba(186,201,204,0.08)";
    return EDGE_COLOR[link.kind] || "rgba(186,201,204,0.45)";
  });
  fg.linkWidth((link) => (link.kind === "contradicts" ? 1.4 : 0.6));
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
  syncEngineLinks();
  paint();
  if (fit) fitVisible();
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

function select(id, shouldCenter) {
  selected = id && byId.has(id) ? id : null;
  hot = selected ? neighborIds(selected) : null;
  if (selected && location.hash !== "#" + selected) history.replaceState(null, "", "#" + selected);
  if (!selected && location.hash) history.replaceState(null, "", location.pathname + location.search);
  renderInspect(selected);
  refresh(false);
  if (shouldCenter && selected) centerOn(selected);
}

function renderInspect(id) {
  if (!id) {
    inspectEl.innerHTML = "Select a claim or an entity. Drag to orbit. Scroll to zoom.";
    return;
  }
  const item = claim(id);
  if (item) {
    const who = person(item.claimant_id);
    const ents = (item.entity_ids || []).map(entity).filter(Boolean);
    const related = (payload.links || []).filter((link) => link.source === item.id || link.target === item.id);
    const t = Math.floor(item.t_start || 0);
    const href = "https://www.youtube.com/watch?v=" + payload.case.video_id + "&t=" + t + "s";
    inspectEl.innerHTML = `
      <div class="font-label-caps text-label-caps text-primary mb-2">Claim · proposed</div>
      <p class="text-on-surface mb-3">${esc(item.text)}</p>
      <p class="mb-2"><span class="text-on-surface-variant">Claimant.</span> ${esc(who ? who.name : item.claimant_id)}</p>
      <p class="mb-2"><span class="text-on-surface-variant">Speaker label.</span> ${esc(item.speaker_label || "—")}</p>
      <p class="mb-3"><span class="text-on-surface-variant">Time.</span> ${esc(clock(item.t_start))}–${esc(clock(item.t_end))}</p>
      <p class="italic text-on-surface mb-3">“${esc(item.quote)}”</p>
      <a class="text-primary font-mono-data text-[12px]" href="${esc(href)}" target="_blank" rel="noreferrer">Open this moment</a>
      <div class="font-label-caps text-label-caps text-on-surface-variant mt-4 mb-2">Entities</div>
      ${ents.map((row) => `<button type="button" data-node="${esc(row.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">${esc(row.name)} <span class="text-on-surface-variant">${esc(TYPE_LABEL[row.type] || row.type)}</span></button>`).join("") || "<p>No entity on this claim.</p>"}
      <div class="font-label-caps text-label-caps text-on-surface-variant mt-4 mb-2">Other claims</div>
      ${related.map((link) => {
        const other = link.source === item.id ? link.target : link.source;
        const otherClaim = claim(other);
        return `<button type="button" data-node="${esc(other)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30"><span class="text-primary">${esc(link.kind)}</span> ${esc(otherClaim ? otherClaim.text : other)}</button>`;
      }).join("") || "<p>No link to another claim.</p>"}
    `;
    return;
  }
  const mentioned = entity(id);
  if (mentioned) {
    const users = (payload.claims || []).filter((row) => (row.entity_ids || []).includes(mentioned.id));
    const mentions = mentioned.mentions || [];
    const mentionHtml = mentions.slice(0, 4).map((row) => {
      const t = Math.floor(row.t_start || 0);
      const href = "https://www.youtube.com/watch?v=" + payload.case.video_id + "&t=" + t + "s";
      return `<p class="mb-2"><a class="font-mono-data text-primary" href="${esc(href)}" target="_blank" rel="noreferrer">${esc(row.speaker_label || "")} · ${esc(clock(row.t_start))}</a><br><span class="italic">“${esc(row.quote)}”</span></p>`;
    }).join("");
    const judged = mentioned.judged_by === "jev"
      ? "Jev proposed this type. The words are copied from the span."
      : "This is an entity mention. It is not a claim, and it is not an event.";
    inspectEl.innerHTML = `
      <div class="font-label-caps text-label-caps text-primary mb-2">${esc(TYPE_LABEL[mentioned.type] || mentioned.type)} · proposed</div>
      <p class="text-on-surface mb-3">${esc(mentioned.name)}</p>
      <p class="mb-3">${esc(judged)} The speaker label is who said the words. A named person is not the claimant unless that person spoke a claim.</p>
      ${mentions.length ? `<div class="font-label-caps text-label-caps text-on-surface-variant mb-2">${mentions.length} mentions</div>${mentionHtml}` : ""}
      <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">Claims that name it</div>
      ${users.map((row) => `<button type="button" data-node="${esc(row.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">${esc(row.text)}</button>`).join("") || "<p>No claim names it in this view.</p>"}
    `;
    return;
  }
  const who = person(id);
  if (who) {
    const made = (payload.claims || []).filter((row) => row.claimant_id === who.id);
    inspectEl.innerHTML = `
      <div class="font-label-caps text-label-caps text-primary mb-2">${esc(who.role)}</div>
      <p class="text-on-surface mb-3">${esc(who.name)}</p>
      <p class="mb-3">${esc(personCopy(who))}</p>
      <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">${made.length} claims</div>
      ${made.slice(0, 12).map((row) => `<button type="button" data-node="${esc(row.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">${esc(row.text)}</button>`).join("")}
    `;
  }
}

function bind() {
  inspectEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-node]");
    if (!button) return;
    select(button.getAttribute("data-node"), true);
  });
  document.querySelectorAll(".case-filter").forEach((button) => {
    button.addEventListener("click", () => {
      activeType = button.getAttribute("data-type");
      document.querySelectorAll(".case-filter").forEach((item) => {
        const on = item === button;
        item.classList.toggle("border-primary", on);
        item.classList.toggle("text-primary", on);
        item.classList.toggle("border-outline-variant/40", !on);
        item.classList.toggle("text-on-surface-variant", !on);
      });
      refresh(true);
    });
  });
  document.getElementById("case-search").addEventListener("input", (event) => {
    query = event.target.value.trim().toLowerCase();
    refresh(true);
  });
  const fit = document.getElementById("case-fit");
  if (fit) fit.addEventListener("click", fitVisible);
  window.addEventListener("resize", () => {
    if (!fg) return;
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
  const hash = location.hash.replace("#", "");
  if (hash && byId.has(hash)) select(hash, false);
  else writeStatus();
}

async function main() {
  let ForceGraph3D;
  try {
    const graphMod = await import("3d-force-graph");
    const textMod = await import("three-spritetext");
    ForceGraph3D = graphMod.default;
    SpriteText = textMod.default;
  } catch (err) {
    inspectEl.textContent = "The 3D graph did not load.";
    console.error(err);
    return;
  }
  if (typeof ForceGraph3D !== "function" || typeof SpriteText !== "function") {
    inspectEl.textContent = "The 3D graph did not load.";
    return;
  }
  const response = await fetch("/api/cases/borland");
  if (!response.ok) {
    inspectEl.textContent = "The case file is not available.";
    return;
  }
  payload = await response.json();
  document.getElementById("case-title").textContent = payload.case.title;
  document.getElementById("case-note").textContent = payload.case.note;
  document.getElementById("case-video").href = "https://www.youtube.com/watch?v=" + payload.case.video_id;
  document.getElementById("case-video").textContent = payload.case.video_id;
  if (statusEl) statusEl.textContent = "Arranging the graph…";
  buildModel();
  bind();
  try {
    mount(ForceGraph3D);
  } catch (err) {
    inspectEl.textContent = "The 3D graph did not start.";
    console.error(err);
  }
}

if (document.fonts && document.fonts.ready) document.fonts.ready.then(main);
else main();
