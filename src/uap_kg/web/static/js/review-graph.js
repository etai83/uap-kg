/* Aetheris Intel — Item & Graph Review */
import ForceGraph3D from "3d-force-graph";
import SpriteText from "three-spritetext";

const TYPE_LABEL = {
  named_person: "Persons",
  person: "Persons",
  claim: "Claims",
  object: "Object",
  uap_item: "UAP item",
  location: "Location",
  date_time: "Date & time",
  organization: "Organization",
  project: "Project",
};

const NODE_COLOR = {
  person: "#00E5FF",
  named_person: "#FF3EC8",
  claim: "#FFE14A",
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
  explored: "rgba(195,245,255,0.5)",
};

const FILTER_TYPES = [
  { id: "all", label: "All" },
  { id: "named_person", label: "Persons" },
  { id: "uap_item", label: "UAP item" },
  { id: "location", label: "Location" },
  { id: "organization", label: "Organization" },
  { id: "project", label: "Project" },
  { id: "object", label: "Object" },
  { id: "date_time", label: "Date & time" },
  { id: "claim", label: "Claims" },
];

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}

function getNodeType(node) {
  if (!node) return "object";
  if (node.kind === "person") return "named_person";
  if (node.kind === "claim") return "claim";
  return node.entityType || "object";
}

function getNodeColor(node) {
  const t = getNodeType(node);
  return NODE_COLOR[t] || "#bac9cc";
}

function endId(val) {
  return val && typeof val === "object" ? val.id : val;
}

function levenshtein(a, b) {
  const rows = a.length + 1;
  const cols = b.length + 1;
  const grid = Array.from({ length: rows }, () => new Array(cols).fill(0));
  for (let i = 0; i < rows; i++) grid[i][0] = i;
  for (let j = 0; j < cols; j++) grid[0][j] = j;
  for (let i = 1; i < rows; i++) {
    for (let j = 1; j < cols; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      grid[i][j] = Math.min(grid[i - 1][j] + 1, grid[i][j - 1] + 1, grid[i - 1][j - 1] + cost);
    }
  }
  return grid[a.length][b.length];
}

function stringSimilarity(a, b) {
  if (!a || !b) return 0;
  if (a === b) return 1;
  const dist = levenshtein(a, b);
  return 1 - dist / Math.max(a.length, b.length);
}

// Module state
let allNodes = [];
let allLinks = [];
let byId = new Map();
let adj = new Map(); // id -> Array<{ target, kind }>

let visibleNodeIds = new Set();
let visibleNodes = [];
let visibleLinks = [];
let activeNodeId = null;
let currentTypeFilter = "all";

let fg = null;
let stageEl = null;
let statusEl = null;
let emptyStateEl = null;
let sidePanelEl = null;
let searchInputEl = null;
let searchResultsEl = null;

function buildAdjacency() {
  adj.clear();
  allLinks.forEach((link) => {
    const s = endId(link.source);
    const t = endId(link.target);
    const kind = link.kind || "co_mention";
    if (!adj.has(s)) adj.set(s, []);
    if (!adj.has(t)) adj.set(t, []);
    adj.get(s).push({ target: t, kind });
    adj.get(t).push({ target: s, kind });
  });

  allNodes.forEach((n) => {
    n._degree = (adj.get(n.id) || []).length;
  });
}

function computeClosestItems(nodeId, typeFilter = "all", limit = 10) {
  const target = byId.get(nodeId);
  if (!target) return [];

  const targetName = (target.full || target.label || "").trim().toLowerCase();
  const targetTokens = new Set(targetName.split(/\s+/).filter((w) => w.length > 2));
  const targetCases = new Set(target.caseIds || (target.caseId ? [target.caseId] : []));

  const directMap = new Map();
  (adj.get(nodeId) || []).forEach((rel) => {
    if (!directMap.has(rel.target)) directMap.set(rel.target, []);
    directMap.get(rel.target).push(rel.kind);
  });

  const twoHopMap = new Map();
  directMap.forEach((_, neighborId) => {
    (adj.get(neighborId) || []).forEach((rel) => {
      const n2 = rel.target;
      if (n2 !== nodeId && !directMap.has(n2)) {
        twoHopMap.set(n2, (twoHopMap.get(n2) || 0) + 1);
      }
    });
  });

  const ranked = [];
  allNodes.forEach((other) => {
    if (other.id === nodeId) return;

    const otherType = getNodeType(other);
    if (typeFilter !== "all") {
      if (typeFilter === "named_person") {
        if (otherType !== "named_person" && other.kind !== "person") return;
      } else if (typeFilter === "claim") {
        if (other.kind !== "claim") return;
      } else if (otherType !== typeFilter) {
        return;
      }
    }

    let score = 0;
    let reason = "";

    // Tier 1: Direct connection
    if (directMap.has(other.id)) {
      const kinds = directMap.get(other.id);
      if (kinds.includes("same_surface")) {
        score = 100;
        reason = "Same surface entity";
      } else if (kinds.includes("same_assertion")) {
        score = 95;
        reason = "Asserts same claim";
      } else if (kinds.includes("contradicts")) {
        score = 92;
        reason = "Contradicts claim";
      } else if (kinds.includes("elaborates")) {
        score = 90;
        reason = "Elaborates claim";
      } else if (kinds.includes("about")) {
        score = 85;
        reason = "Subject of claim";
      } else if (kinds.includes("made")) {
        score = 85;
        reason = "Claimant on record";
      } else {
        score = 75 + Math.min(kinds.length, 5) * 4;
        reason = `Mentioned together (${kinds.length} moments)`;
      }
    }
    // Tier 2: 2-Hop shared connection
    else if (twoHopMap.has(other.id)) {
      const cnt = twoHopMap.get(other.id);
      score = 45 + Math.min(cnt, 5) * 6;
      reason = `Shares ${cnt} connection${cnt === 1 ? "" : "s"}`;
    }

    // Tier 3: Lexical / Name similarity
    const otherName = (other.full || other.label || "").trim().toLowerCase();
    if (targetName && otherName && targetName.length >= 3 && otherName.length >= 3) {
      let sim = stringSimilarity(targetName, otherName);
      if (targetName.includes(otherName) || otherName.includes(targetName)) {
        sim = Math.max(sim, 0.75);
      }
      const otherTokens = otherName.split(/\s+/).filter((w) => w.length > 2);
      const shared = otherTokens.filter((t) => targetTokens.has(t));
      if (shared.length > 0) {
        sim = Math.max(sim, 0.5 + 0.15 * shared.length);
      }
      if (sim >= 0.5) {
        const nameScore = Math.floor(sim * 68);
        if (nameScore > score) {
          score = nameScore;
          reason = `Similar name (${Math.floor(sim * 100)}%)`;
        }
      }
    }

    // Tier 4: Same interview case context
    const otherCases = new Set(other.caseIds || (other.caseId ? [other.caseId] : []));
    let hasSharedCase = false;
    for (const c of targetCases) {
      if (otherCases.has(c)) {
        hasSharedCase = true;
        break;
      }
    }
    if (hasSharedCase) {
      score += 5;
      if (!reason) {
        reason = `Same interview case (${other.caseShort || "shared"})`;
      }
    }

    // Tier 5: Prominence baseline ensuring suggestions always available
    const prominence = Math.min(other._degree || 0, 25);
    score += prominence * 0.5 + 1;
    if (!reason) {
      reason = `Prominent ${TYPE_LABEL[otherType] || otherType} in knowledge base`;
    }

    ranked.push({ node: other, score, reason });
  });

  ranked.sort(
    (a, b) => b.score - a.score || (b.node._degree || 0) - (a.node._degree || 0) || (b.node.full || "").length - (a.node.full || "").length
  );
  return ranked.slice(0, limit);
}

function updateGraph() {
  if (!fg) return;

  visibleNodes = Array.from(visibleNodeIds).map((id) => byId.get(id)).filter(Boolean);

  // Collect all edges from allLinks between visible nodes
  const linkSet = new Set();
  const graphLinks = [];

  allLinks.forEach((link) => {
    const s = endId(link.source);
    const t = endId(link.target);
    if (visibleNodeIds.has(s) && visibleNodeIds.has(t)) {
      const key = s < t ? `${s}->${t}` : `${t}->${s}`;
      if (!linkSet.has(key)) {
        linkSet.add(key);
        graphLinks.push({
          source: s,
          target: t,
          kind: link.kind || "co_mention",
        });
      }
    }
  });

  // Check connectivity: ensure newly added nodes are connected visually if no raw link exists
  visibleNodes.forEach((node) => {
    if (node._parentId && visibleNodeIds.has(node._parentId)) {
      const key1 = `${node.id}->${node._parentId}`;
      const key2 = `${node._parentId}->${node.id}`;
      if (!linkSet.has(key1) && !linkSet.has(key2)) {
        linkSet.add(key1);
        graphLinks.push({
          source: node._parentId,
          target: node.id,
          kind: "explored",
        });
      }
    }
  });

  visibleLinks = graphLinks;
  fg.graphData({ nodes: visibleNodes, links: visibleLinks });

  if (emptyStateEl) {
    emptyStateEl.classList.toggle("hidden", visibleNodes.length > 0);
  }
  if (statusEl) {
    statusEl.textContent = `${visibleNodes.length} node${visibleNodes.length === 1 ? "" : "s"} · ${visibleLinks.length} link${visibleLinks.length === 1 ? "" : "s"} in graph`;
  }
}

function selectItem(nodeId, parentId = null) {
  let node = byId.get(nodeId);
  if (!node && nodeId) {
    const term = String(nodeId).trim().toLowerCase();
    node = allNodes.find(
      (n) => (n.full || n.label || "").toLowerCase() === term || n.id.toLowerCase() === term || n.id.toLowerCase().includes(term)
    );
  }
  if (!node) return;
  nodeId = node.id;

  if (!visibleNodeIds.has(nodeId)) {
    if (parentId && byId.has(parentId)) {
      node._parentId = parentId;
    }
    visibleNodeIds.add(nodeId);
    updateGraph();
  }

  activeNodeId = nodeId;

  // Refresh node visual state in 3D graph
  if (fg) {
    fg.nodeColor((n) => getNodeColor(n));
    fg.nodeThreeObject(fg.nodeThreeObject());
    // Center camera smoothly toward node
    if (node.x != null && node.y != null && node.z != null) {
      const dist = 140;
      fg.cameraPosition(
        { x: node.x + dist * 0.6, y: node.y + dist * 0.4, z: node.z + dist * 0.8 },
        { x: node.x, y: node.y, z: node.z },
        600
      );
    }
  }

  renderSidePanel();
}

function renderSidePanel() {
  if (!sidePanelEl) return;

  if (!activeNodeId || !byId.has(activeNodeId)) {
    sidePanelEl.innerHTML = `
      <div class="h-full flex flex-col items-center justify-center text-center p-6">
        <span class="material-symbols-outlined text-4xl text-outline-variant/60 mb-3">hub</span>
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-2">No Item Selected</h3>
        <p class="font-body-sm text-body-sm text-on-surface-variant max-w-xs">
          Search for an item above or click a suggestion to inspect its closest relations and add it to the graph.
        </p>
      </div>
    `;
    return;
  }

  const activeNode = byId.get(activeNodeId);
  const activeType = getNodeType(activeNode);
  const typeLabel = TYPE_LABEL[activeType] || "Item";
  const nodeColor = getNodeColor(activeNode);
  const closest = computeClosestItems(activeNodeId, currentTypeFilter, 10);

  sidePanelEl.innerHTML = `
    <div class="p-5 border-b border-outline-variant/20 bg-surface-container-high/40">
      <div class="flex items-start justify-between gap-3 mb-2">
        <span class="inline-flex items-center gap-1.5 font-label-caps text-[11px] px-2.5 py-1 rounded bg-surface-container border border-outline-variant/40" style="color: ${nodeColor};">
          <span class="w-2 h-2 rounded-full" style="background-color: ${nodeColor};"></span>
          ${esc(typeLabel)}
        </span>
        <div class="flex items-center gap-2">
          <span class="font-mono-data text-[10px] text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded">In Graph</span>
          <button type="button" id="rv-remove-node" class="text-on-surface-variant hover:text-error text-[11px] font-mono-data p-1" title="Remove from graph">
            <span class="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      </div>
      <h2 class="font-headline-sm text-[18px] text-on-surface font-semibold leading-snug mb-1">
        ${esc(activeNode.full || activeNode.label)}
      </h2>
      <div class="font-mono-data text-[11px] text-on-surface-variant/70 mb-2">
        ID: ${esc(activeNode.id)} ${activeNode.caseShort ? `· Case: ${esc(activeNode.caseShort)}` : ""}
      </div>
      ${
        activeNode.quote
          ? `<p class="font-body-sm text-[13px] text-on-surface-variant italic border-l-2 border-primary/40 pl-2.5 py-0.5 line-clamp-3">“${esc(activeNode.quote)}”</p>`
          : ""
      }
    </div>

    <!-- Type filter pills -->
    <div class="p-3 border-b border-outline-variant/20 bg-surface-container flex flex-wrap gap-1.5 shrink-0">
      ${FILTER_TYPES.map((f) => {
        const isActive = currentTypeFilter === f.id;
        return `
          <button type="button" data-filter="${esc(f.id)}" class="font-label-caps text-[10px] px-2.5 py-1 rounded transition-colors ${
          isActive
            ? "bg-primary text-on-primary font-bold shadow-sm"
            : "bg-surface-container-lowest text-on-surface-variant hover:text-on-surface border border-outline-variant/30"
        }">
            ${esc(f.label)}
          </button>
        `;
      }).join("")}
    </div>

    <!-- Closest items list -->
    <div class="flex-1 overflow-y-auto p-4 space-y-2.5">
      <div class="flex items-center justify-between mb-1">
        <span class="font-label-caps text-[11px] text-on-surface-variant tracking-wider">
          ${closest.length} CLOSEST ITEMS ${currentTypeFilter !== "all" ? `(${currentTypeFilter.toUpperCase()})` : ""}
        </span>
        <span class="font-mono-data text-[11px] text-primary-fixed-dim">Ranked by relevance</span>
      </div>

      ${
        closest.length
          ? closest
              .map((item) => {
                const itemType = getNodeType(item.node);
                const itemColor = getNodeColor(item.node);
                const isInGraph = visibleNodeIds.has(item.node.id);
                return `
            <div data-closest-id="${esc(item.node.id)}" class="group cursor-pointer p-3 rounded bg-surface border ${
                  isInGraph
                    ? "border-primary/40 bg-surface-container-low"
                    : "border-outline-variant/30 hover:border-outline-variant/80 hover:bg-surface-container-high/50"
                } transition-all">
              <div class="flex items-center justify-between gap-2 mb-1.5">
                <span class="inline-flex items-center gap-1 font-label-caps text-[10px] text-on-surface-variant" style="color: ${itemColor};">
                  <span class="w-1.5 h-1.5 rounded-full" style="background-color: ${itemColor};"></span>
                  ${esc(TYPE_LABEL[itemType] || itemType)}
                </span>
                <span class="font-mono-data text-[10px] ${
                  isInGraph ? "text-primary font-bold" : "text-on-surface-variant/60 group-hover:text-primary"
                }">
                  ${isInGraph ? "✓ In graph" : "+ Add to graph"}
                </span>
              </div>
              <h4 class="font-headline-sm text-[14px] text-on-surface font-medium leading-snug group-hover:text-primary transition-colors">
                ${esc(item.node.full || item.node.label)}
              </h4>
              <div class="flex items-center gap-2 mt-1.5 text-[11px] font-mono-data text-on-surface-variant/70">
                <span class="text-primary-fixed-dim">${esc(item.reason)}</span>
                ${item.node.caseShort ? `<span>· ${esc(item.node.caseShort)}</span>` : ""}
              </div>
            </div>
          `;
              })
              .join("")
          : `
            <div class="p-6 text-center text-on-surface-variant font-body-sm text-[13px]">
              No items matching filter “${esc(currentTypeFilter)}”.
            </div>
          `
      }
    </div>
  `;

  // Attach event handlers
  sidePanelEl.querySelectorAll("[data-filter]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentTypeFilter = btn.dataset.filter;
      renderSidePanel();
    });
  });

  sidePanelEl.querySelectorAll("[data-closest-id]").forEach((card) => {
    card.addEventListener("click", () => {
      const nextId = card.dataset.closestId;
      selectItem(nextId, activeNodeId);
    });
  });

  const removeBtn = sidePanelEl.querySelector("#rv-remove-node");
  if (removeBtn) {
    removeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      visibleNodeIds.delete(activeNodeId);
      const remaining = Array.from(visibleNodeIds);
      activeNodeId = remaining.length ? remaining[remaining.length - 1] : null;
      updateGraph();
      renderSidePanel();
    });
  }
}

function handleSearch(q) {
  if (!searchResultsEl) return;
  const term = (q || "").trim().toLowerCase();
  if (!term || term.length < 2) {
    searchResultsEl.classList.add("hidden");
    searchResultsEl.innerHTML = "";
    return;
  }

  const matches = [];
  for (const node of allNodes) {
    const name = (node.full || node.label || "").toLowerCase();
    const quote = (node.quote || "").toLowerCase();
    const type = (node.entityType || node.kind || "").toLowerCase();
    if (name.includes(term) || quote.includes(term) || type.includes(term)) {
      const score = name.startsWith(term) ? 2 : name.includes(term) ? 1 : 0.5;
      matches.push({ node, score });
    }
  }

  matches.sort((a, b) => b.score - a.score || (a.node.full || "").length - (b.node.full || "").length);
  const topMatches = matches.slice(0, 12);

  if (!topMatches.length) {
    searchResultsEl.innerHTML = `
      <div class="p-3 text-[12px] font-mono-data text-on-surface-variant">No items match “${esc(term)}”</div>
    `;
    searchResultsEl.classList.remove("hidden");
    return;
  }

  searchResultsEl.innerHTML = topMatches
    .map(({ node }) => {
      const type = getNodeType(node);
      const color = getNodeColor(node);
      const inGraph = visibleNodeIds.has(node.id);
      return `
        <div data-search-id="${esc(node.id)}" class="p-2.5 hover:bg-surface-container-high cursor-pointer flex items-center justify-between gap-3 border-b border-outline-variant/15 last:border-b-0">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full shrink-0" style="background-color: ${color};"></span>
              <span class="font-headline-sm text-[13px] text-on-surface truncate">${esc(node.full || node.label)}</span>
            </div>
            <div class="font-mono-data text-[10px] text-on-surface-variant/70 pl-4">
              ${esc(TYPE_LABEL[type] || type)} ${node.caseShort ? `· ${esc(node.caseShort)}` : ""}
            </div>
          </div>
          ${
            inGraph
              ? `<span class="font-mono-data text-[10px] text-primary">In Graph</span>`
              : `<span class="font-mono-data text-[10px] text-on-surface-variant hover:text-primary">+ Add</span>`
          }
        </div>
      `;
    })
    .join("");

  searchResultsEl.classList.remove("hidden");

  searchResultsEl.querySelectorAll("[data-search-id]").forEach((row) => {
    row.addEventListener("click", () => {
      const id = row.dataset.searchId;
      searchResultsEl.classList.add("hidden");
      if (searchInputEl) searchInputEl.value = "";
      selectItem(id, activeNodeId);
    });
  });
}

export async function initReviewGraph(initialNodeId = "", preferredVideo = "") {
  stageEl = document.getElementById("review-cy");
  statusEl = document.getElementById("review-status");
  emptyStateEl = document.getElementById("review-empty-state");
  sidePanelEl = document.getElementById("review-sidebar");
  searchInputEl = document.getElementById("rv-item-search");
  searchResultsEl = document.getElementById("rv-item-results");

  // Fetch graph payload
  const res = await fetch("/api/graph");
  if (!res.ok) {
    console.error("Failed to load /api/graph");
    return;
  }
  const payload = await res.json();
  allNodes = payload.nodes || [];
  allLinks = payload.links || [];
  byId = new Map(allNodes.map((n) => [n.id, n]));
  buildAdjacency();

  // Initialize ForceGraph3D
  if (stageEl) {
    fg = ForceGraph3D()(stageEl)
      .backgroundColor("#010f1f")
      .nodeLabel((node) => `${node.full || node.label} (${TYPE_LABEL[getNodeType(node)] || getNodeType(node)})`)
      .nodeColor((node) => getNodeColor(node))
      .nodeVal((node) => (node.kind === "person" ? 3.5 : node.kind === "claim" ? 1.5 : 2.2))
      .nodeThreeObject((node) => {
        const sprite = new SpriteText(node.label || node.full);
        sprite.color = getNodeColor(node);
        sprite.textHeight = node.kind === "person" ? 6.5 : node.kind === "claim" ? 3.5 : 4.5;
        sprite.fontWeight = node.id === activeNodeId ? "700" : "400";
        return sprite;
      })
      .nodeThreeObjectExtend(false)
      .linkColor((link) => EDGE_COLOR[link.kind] || "rgba(195,245,255,0.4)")
      .linkWidth((link) => (link.kind === "explored" ? 0.7 : link.kind === "same_surface" ? 1.6 : 0.9))
      .linkDirectionalParticles((link) => (link.kind === "explored" ? 2 : 0))
      .linkDirectionalParticleSpeed(0.006)
      .linkDirectionalParticleWidth(1.4)
      .linkDirectionalParticleColor(() => "#00daf3")
      .onNodeClick((node) => {
        selectItem(node.id, activeNodeId);
      });

    const fitToStage = () => {
      const w = stageEl.clientWidth;
      const h = stageEl.clientHeight;
      if (w > 0 && h > 0) fg.width(w).height(h);
    };
    fitToStage();
    new ResizeObserver(fitToStage).observe(stageEl);
  }

  // Setup search input
  if (searchInputEl) {
    searchInputEl.addEventListener("input", (e) => handleSearch(e.target.value));
    searchInputEl.addEventListener("focus", (e) => handleSearch(e.target.value));
    document.addEventListener("click", (e) => {
      if (!e.target.closest("#rv-search-wrap")) {
        searchResultsEl?.classList.add("hidden");
      }
    });
  }

  // Header controls
  document.getElementById("rv-fit-btn")?.addEventListener("click", () => {
    if (fg && visibleNodes.length) fg.zoomToFit(400, 70);
  });

  document.getElementById("rv-clear-btn")?.addEventListener("click", () => {
    visibleNodeIds.clear();
    visibleNodes = [];
    visibleLinks = [];
    activeNodeId = null;
    updateGraph();
    renderSidePanel();
  });

  // Empty state sample suggestions click handlers
  document.querySelectorAll("[data-seed-item]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.seedItem;
      selectItem(id);
    });
  });

  // If initialNodeId provided, select it right away
  if (initialNodeId && byId.has(initialNodeId)) {
    selectItem(initialNodeId);
  } else {
    // Check if initial seed is desired
    renderSidePanel();
  }
}
