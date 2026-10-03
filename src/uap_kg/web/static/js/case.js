/* Borland case test — claims, claimant, entities. */
(function () {
  const TYPE_LABEL = {
    named_person: "Persons",
    object: "Object",
    uap_item: "UAP item",
    location: "Location",
    date_time: "Date and time",
    organization: "Organization",
    project: "Project",
  };
  const EDGE = {
    about: "rgba(0,218,243,0.45)",
    elaborates: "rgba(195,245,255,0.7)",
    same_assertion: "rgba(183,200,225,0.8)",
    contradicts: "rgba(255,180,171,0.9)",
    made: "rgba(132,147,150,0.35)",
  };

  let graph = null;
  let positions = new Map();
  let selected = null;
  let activeType = "all";
  let query = "";

  const nodesEl = document.getElementById("case-nodes");
  const svgEl = document.getElementById("case-svg");
  const scrollEl = document.getElementById("case-scroll");
  const inspectEl = document.getElementById("case-inspect-body");

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
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

  function personCopy(p) {
    if (p.role === "claimant") return "This person made the claims below. A named person in the text is a different role.";
    if (p.role === "host") return "This person is the host. A host question is not a world claim.";
    if (p.role === "played voice") return "This voice is audio played in the interview. It is not Dylan Borland.";
    return "This person is on the record for this case.";
  }

  function person(id) {
    return (graph.persons || []).find((p) => p.id === id);
  }

  function entity(id) {
    return (graph.entities || []).find((e) => e.id === id);
  }

  function claim(id) {
    return (graph.claims || []).find((c) => c.id === id);
  }

  function matchesQuery(text) {
    if (!query) return true;
    return String(text || "").toLowerCase().includes(query);
  }

  function visibleClaim(c) {
    if (activeType === "all" || activeType === "claim") {
      return matchesQuery(c.text + " " + c.quote);
    }
    return (c.entity_ids || []).some((id) => {
      const e = entity(id);
      return e && e.type === activeType && matchesQuery(c.text + " " + e.name);
    }) && matchesQuery(c.text + " " + (c.quote || ""));
  }

  function visibleEntity(e) {
    if (activeType !== "all" && activeType !== "claim" && e.type !== activeType) return false;
    if (!matchesQuery(e.name)) {
      const used = (graph.claims || []).some((c) => visibleClaim(c) && (c.entity_ids || []).includes(e.id));
      if (!used) return false;
    }
    return (graph.claims || []).some((c) => visibleClaim(c) && (c.entity_ids || []).includes(e.id));
  }

  function columns() {
    const pane = Math.max(320, scrollEl.clientWidth || 720);
    const pad = 12;
    const gap = 16;
    const personW = pane < 520 ? 104 : 132;
    const entityW = Math.max(132, Math.round(pane * 0.28));
    const claimW = Math.max(150, pane - pad * 2 - personW - entityW - gap * 2);
    const width = pad + personW + gap + claimW + gap + entityW + pad;
    return {
      width: Math.max(pane, width),
      personX: pad,
      personW,
      claimX: pad + personW + gap,
      claimW,
      entityX: pad + personW + gap + claimW + gap,
      entityW,
    };
  }

  function layout() {
    positions = new Map();
    const claims = (graph.claims || []).filter(visibleClaim).slice().sort((a, b) => a.t_start - b.t_start);
    const entities = (graph.entities || []).filter(visibleEntity);
    const persons = graph.persons || [];
    const row = 78;
    const col = columns();
    persons.forEach((p, i) => positions.set(p.id, { x: col.personX, y: 28 + i * 110, w: col.personW, h: 72, kind: "person" }));
    claims.forEach((c, i) => positions.set(c.id, { x: col.claimX, y: 28 + i * row, w: col.claimW, h: 68, kind: "claim" }));
    const groups = ["named_person", "uap_item", "object", "location", "date_time", "organization", "project"];
    let y = 28;
    groups.forEach((type) => {
      const group = entities.filter((e) => e.type === type);
      group.forEach((e) => {
        positions.set(e.id, { x: col.entityX, y: y, w: col.entityW, h: 56, kind: "entity", type: e.type });
        y += 64;
      });
      if (group.length) y += 16;
    });
    const height = Math.max(520, y + 40, 28 + claims.length * row + 40, 28 + persons.length * 110 + 40);
    nodesEl.style.width = col.width + "px";
    nodesEl.style.height = height + "px";
    svgEl.setAttribute("width", col.width);
    svgEl.setAttribute("height", height);
    svgEl.style.width = col.width + "px";
    svgEl.style.height = height + "px";
    return { claims, entities, persons, width: col.width, height };
  }

  function edgesOf(view) {
    const edges = [];
    const seen = new Set(view.claims.map((c) => c.id).concat(view.entities.map((e) => e.id), view.persons.map((p) => p.id)));
    view.claims.forEach((c) => {
      if (seen.has(c.claimant_id)) edges.push({ source: c.id, target: c.claimant_id, kind: "made" });
      (c.entity_ids || []).forEach((id) => {
        if (seen.has(id)) edges.push({ source: c.id, target: id, kind: "about" });
      });
    });
    (graph.links || []).forEach((link) => {
      if (seen.has(link.source) && seen.has(link.target)) edges.push(link);
    });
    return edges;
  }

  function nodeButton(id, pos, title, sub, extraClass) {
    const on = selected === id ? " outline outline-1 outline-primary-fixed-dim" : "";
    return `<button type="button" data-node="${esc(id)}" class="absolute text-left rounded border border-outline-variant/40 bg-surface-container px-3 py-2 hover:border-primary/60 ${extraClass || ""}${on}" style="left:${pos.x}px;top:${pos.y}px;width:${pos.w}px;height:${pos.h}px">
      <div class="font-body-sm text-[13px] leading-5 text-on-surface line-clamp-2">${esc(title)}</div>
      <div class="font-mono-data text-[11px] text-on-surface-variant truncate">${esc(sub)}</div>
    </button>`;
  }

  function edgePath(a, b) {
    const y1 = a.y + a.h / 2;
    const y2 = b.y + b.h / 2;
    const sameCol = Math.abs((a.x + a.w / 2) - (b.x + b.w / 2)) < 80;
    if (sameCol) {
      const x1 = a.x + a.w;
      const x2 = b.x + b.w;
      return `M ${x1} ${y1} C ${x1 + 48} ${y1}, ${x2 + 48} ${y2}, ${x2} ${y2}`;
    }
    const leftward = a.x > b.x;
    const x1 = leftward ? a.x : a.x + a.w;
    const x2 = leftward ? b.x + b.w : b.x;
    const mid = (x1 + x2) / 2;
    return `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`;
  }

  function drawEdges(edges) {
    const parts = [];
    edges.forEach((e) => {
      const a = positions.get(e.source);
      const b = positions.get(e.target);
      if (!a || !b) return;
      const hot = selected && (e.source === selected || e.target === selected);
      const color = hot ? (EDGE[e.kind] || "#c3f5ff") : (e.kind === "made" ? "rgba(132,147,150,0.18)" : "rgba(132,147,150,0.28)");
      const width = hot ? 1.8 : 1;
      parts.push(`<path d="${edgePath(a, b)}" fill="none" stroke="${color}" stroke-width="${width}"/>`);
    });
    svgEl.innerHTML = parts.join("");
  }

  function renderInspect(id) {
    if (!id) {
      inspectEl.innerHTML = "Select a claim or an entity.";
      return;
    }
    const c = claim(id);
    if (c) {
      const who = person(c.claimant_id);
      const ents = (c.entity_ids || []).map(entity).filter(Boolean);
      const related = (graph.links || []).filter((l) => l.source === c.id || l.target === c.id);
      const t = Math.floor(c.t_start || 0);
      const href = "https://www.youtube.com/watch?v=" + graph.case.video_id + "&t=" + t + "s";
      inspectEl.innerHTML = `
        <div class="font-label-caps text-label-caps text-primary mb-2">Claim · proposed</div>
        <p class="text-on-surface mb-3">${esc(c.text)}</p>
        <p class="mb-2"><span class="text-on-surface-variant">Claimant.</span> ${esc(who ? who.name : c.claimant_id)}</p>
        <p class="mb-2"><span class="text-on-surface-variant">Speaker label.</span> ${esc(c.speaker_label || "—")}</p>
        <p class="mb-3"><span class="text-on-surface-variant">Time.</span> ${esc(clock(c.t_start))}–${esc(clock(c.t_end))}</p>
        <p class="italic text-on-surface mb-3">“${esc(c.quote)}”</p>
        <a class="text-primary font-mono-data text-[12px]" href="${esc(href)}" target="_blank" rel="noreferrer">Open this moment</a>
        <div class="font-label-caps text-label-caps text-on-surface-variant mt-4 mb-2">Entities</div>
        ${ents.map((e) => `<button type="button" data-node="${esc(e.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">${esc(e.name)} <span class="text-on-surface-variant">${esc(TYPE_LABEL[e.type] || e.type)}</span></button>`).join("") || "<p>No entity on this claim.</p>"}
        <div class="font-label-caps text-label-caps text-on-surface-variant mt-4 mb-2">Other claims</div>
        ${related.map((l) => {
          const other = l.source === c.id ? l.target : l.source;
          const oc = claim(other);
          return `<button type="button" data-node="${esc(other)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30"><span class="text-primary">${esc(l.kind)}</span> ${esc(oc ? oc.text : other)}</button>`;
        }).join("") || "<p>No link to another claim.</p>"}
      `;
      return;
    }
    const e = entity(id);
    if (e) {
      const users = (graph.claims || []).filter((c) => (c.entity_ids || []).includes(e.id));
      inspectEl.innerHTML = `
        <div class="font-label-caps text-label-caps text-primary mb-2">${esc(TYPE_LABEL[e.type] || e.type)}</div>
        <p class="text-on-surface mb-3">${esc(e.name)}</p>
        <p class="mb-3">This is an entity mention. It is not a claim, and it is not an event.</p>
        <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">Claims that name it</div>
        ${users.map((c) => `<button type="button" data-node="${esc(c.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">${esc(c.text)}</button>`).join("") || "<p>No claim names it in this view.</p>"}
      `;
      return;
    }
    const p = person(id);
    if (p) {
      const made = (graph.claims || []).filter((c) => c.claimant_id === p.id);
      inspectEl.innerHTML = `
        <div class="font-label-caps text-label-caps text-primary mb-2">${esc(p.role)}</div>
        <p class="text-on-surface mb-3">${esc(p.name)}</p>
        <p class="mb-3">${esc(personCopy(p))}</p>
        <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">${made.length} claims</div>
        ${made.slice(0, 12).map((c) => `<button type="button" data-node="${esc(c.id)}" class="block w-full text-left mb-1 px-2 py-1 border border-outline-variant/30">${esc(c.text)}</button>`).join("")}
      `;
    }
  }

  function render() {
    const view = layout();
    const html = [];
    view.persons.forEach((p) => {
      const pos = positions.get(p.id);
      const n = (graph.claims || []).filter((c) => c.claimant_id === p.id).length;
      html.push(nodeButton(p.id, pos, p.name, p.role + " · " + n + " claims", "border-primary/50"));
    });
    view.claims.forEach((c) => {
      const pos = positions.get(c.id);
      html.push(nodeButton(c.id, pos, c.text, clock(c.t_start) + " · " + (c.entity_ids || []).length + " entities"));
    });
    let lastType = "";
    view.entities.forEach((e) => {
      const pos = positions.get(e.id);
      if (e.type !== lastType) {
        lastType = e.type;
        html.push(`<div class="absolute font-label-caps text-[10px] text-primary" style="left:${pos.x}px;top:${pos.y - 16}px">${esc(TYPE_LABEL[e.type] || e.type)}</div>`);
      }
      html.push(nodeButton(e.id, pos, e.name, TYPE_LABEL[e.type] || e.type));
    });
    nodesEl.innerHTML = html.join("");
    drawEdges(edgesOf(view));
    renderInspect(selected);
  }

  function bind() {
    nodesEl.addEventListener("click", (ev) => {
      const btn = ev.target.closest("[data-node]");
      if (!btn) return;
      selected = btn.getAttribute("data-node");
      render();
      const pos = positions.get(selected);
      if (pos) scrollEl.scrollTo({ top: Math.max(0, pos.y - 20) });
    });
    inspectEl.addEventListener("click", (ev) => {
      const btn = ev.target.closest("[data-node]");
      if (!btn) return;
      selected = btn.getAttribute("data-node");
      render();
      const pos = positions.get(selected);
      if (pos) scrollEl.scrollTo({ top: Math.max(0, pos.y - 40), behavior: "smooth" });
    });
    document.querySelectorAll(".case-filter").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeType = btn.getAttribute("data-type");
        document.querySelectorAll(".case-filter").forEach((b) => {
          const on = b === btn;
          b.classList.toggle("border-primary", on);
          b.classList.toggle("text-primary", on);
          b.classList.toggle("border-outline-variant/40", !on);
          b.classList.toggle("text-on-surface-variant", !on);
        });
        selected = null;
        render();
      });
    });
    document.getElementById("case-search").addEventListener("input", (ev) => {
      query = ev.target.value.trim().toLowerCase();
      selected = null;
      render();
    });
    let pane = scrollEl.clientWidth;
    if (window.ResizeObserver) {
      new ResizeObserver(() => {
        const next = scrollEl.clientWidth;
        if (next === pane) return;
        pane = next;
        render();
      }).observe(scrollEl);
    }
  }

  async function main() {
    const res = await fetch("/api/cases/borland");
    if (!res.ok) {
      inspectEl.textContent = "The case file is not available.";
      return;
    }
    graph = await res.json();
    document.getElementById("case-title").textContent = graph.case.title;
    document.getElementById("case-note").textContent = graph.case.note;
    document.getElementById("case-video").href = "https://www.youtube.com/watch?v=" + graph.case.video_id;
    document.getElementById("case-video").textContent = graph.case.video_id;
    bind();
    const hash = location.hash.replace("#", "");
    if (hash && (claim(hash) || entity(hash) || person(hash))) selected = hash;
    render();
  }

  main();
})();
