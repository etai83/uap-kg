/* Aetheris navigator — shared UX */
const Aetheris = (() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function fmtTime(s) {
    const n = Math.max(0, Math.floor(Number(s) || 0));
    const h = String(Math.floor(n / 3600)).padStart(2, "0");
    const m = String(Math.floor((n % 3600) / 60)).padStart(2, "0");
    const sec = String(n % 60).padStart(2, "0");
    return h === "00" ? `${m}:${sec}` : `${h}:${m}:${sec}`;
  }

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function extractSentences(spans) {
    const tokens = [];
    for (const s of spans || []) {
      const txt = (s.text || "").trim();
      if (!txt) continue;
      const words = txt.split(/\s+/);
      if (!words.length) continue;
      const t0 = Number(s.t_start) || 0;
      const t1 = Number(s.t_end) || 0;
      const dur = Math.max(t1 - t0, 0.01);
      for (let idx = 0; idx < words.length; idx++) {
        const wt0 = t0 + (idx / words.length) * dur;
        const wt1 = t0 + ((idx + 1) / words.length) * dur;
        tokens.push({ word: words[idx], t0: wt0, t1: wt1, speaker: s.speaker_label });
      }
    }

    const sentences = [];
    let cur = [];
    const abbrRegex = /^(mr|mrs|ms|dr|gen|lt|col|sgt|vs|etc|approx|no)\.$/i;
    for (const tok of tokens) {
      cur.push(tok);
      const w = tok.word;
      if (/[.!?]$/.test(w) && !abbrRegex.test(w)) {
        sentences.push({
          text: cur.map((t) => t.word).join(" "),
          t_start: cur[0].t0,
          t_end: cur[cur.length - 1].t1,
          speaker: cur[0].speaker,
        });
        cur = [];
      }
    }
    if (cur.length) {
      sentences.push({
        text: cur.map((t) => t.word).join(" "),
        t_start: cur[0].t0,
        t_end: cur[cur.length - 1].t1,
        speaker: cur[0].speaker,
      });
    }
    return sentences;
  }

  function findClaimContext(claim, sentences) {
    if (!sentences || !sentences.length) {
      return {
        prev: "",
        sentence: claim?.quote || claim?.claim_text || claim?.text || "",
        after: "",
        t_start: Number(claim?.t_start) || 0,
        t_end: Number(claim?.t_end) || 0,
        speaker: claim?.speaker_label || null,
      };
    }

    const q = (claim.quote || "").toLowerCase();
    const ct = (claim.claim_text || claim.text || "").toLowerCase();
    const qWords = q.match(/\b\w{3,}\b/g) || [];
    const ctWords = ct.match(/\b\w{3,}\b/g) || [];
    const targetWords = new Set([...qWords, ...ctWords]);

    const t = claim.t_start != null ? Number(claim.t_start) : null;
    let bestIdx = -1;
    let bestScore = -1;

    for (let i = 0; i < sentences.length; i++) {
      const s = sentences[i];
      const sLower = s.text.toLowerCase();
      const sWords = new Set(sLower.match(/\b\w{3,}\b/g) || []);
      let score = 0;

      if (targetWords.size > 0) {
        let overlap = 0;
        for (const w of targetWords) {
          if (sWords.has(w)) overlap++;
        }
        if (overlap > 0) score += overlap * 15;
      }

      if (t != null) {
        if (t >= s.t_start && t <= s.t_end) {
          score += 50;
        } else if (Math.abs(s.t_start - t) < 4) {
          score += 30;
        } else if (Math.abs(s.t_start - t) < 15) {
          score += 15;
        } else if (Math.abs(s.t_start - t) < 60) {
          score += 5;
        }
      }

      if (score > bestScore) {
        bestScore = score;
        bestIdx = i;
      }
    }

    if (bestIdx === -1 && t != null) {
      let minDiff = Infinity;
      for (let i = 0; i < sentences.length; i++) {
        const diff = Math.abs(sentences[i].t_start - t);
        if (diff < minDiff) {
          minDiff = diff;
          bestIdx = i;
        }
      }
    }

    if (bestIdx === -1) bestIdx = 0;

    return {
      prev: bestIdx > 0 ? sentences[bestIdx - 1].text : "",
      sentence: sentences[bestIdx].text,
      after: bestIdx + 1 < sentences.length ? sentences[bestIdx + 1].text : "",
      t_start: sentences[bestIdx].t_start,
      t_end: sentences[bestIdx].t_end,
      speaker: sentences[bestIdx].speaker,
    };
  }

  function highlightInSpan(spanText, sentence) {
    const st = (spanText || "").trim();
    const sent = (sentence || "").trim();
    if (!st || !sent) return esc(spanText);

    const idx = spanText.toLowerCase().indexOf(sent.toLowerCase());
    if (idx !== -1) {
      const before = spanText.slice(0, idx);
      const match = spanText.slice(idx, idx + sent.length);
      const after = spanText.slice(idx + sent.length);
      return `${esc(before)}<mark class="claim-soft-highlight">${esc(match)}</mark>${esc(after)}`;
    }

    if (sent.toLowerCase().includes(st.toLowerCase())) {
      return `<mark class="claim-soft-highlight">${esc(spanText)}</mark>`;
    }

    const words = sent.split(/\s+/).filter((w) => w.length > 2);
    let bestPhrase = "";
    for (let len = words.length; len >= 3; len--) {
      for (let i = 0; i <= words.length - len; i++) {
        const phrase = words.slice(i, i + len).join(" ");
        if (spanText.toLowerCase().includes(phrase.toLowerCase())) {
          bestPhrase = phrase;
          break;
        }
      }
      if (bestPhrase) break;
    }

    if (bestPhrase) {
      const pIdx = spanText.toLowerCase().indexOf(bestPhrase.toLowerCase());
      if (pIdx !== -1) {
        const before = spanText.slice(0, pIdx);
        const match = spanText.slice(pIdx, pIdx + bestPhrase.length);
        const after = spanText.slice(pIdx + bestPhrase.length);
        return `${esc(before)}<mark class="claim-soft-highlight">${esc(match)}</mark>${esc(after)}`;
      }
    }

    return esc(spanText);
  }

  function ytJump(videoId, t) {
    const sec = Math.floor(Number(t) || 0);
    window.open(`https://www.youtube.com/watch?v=${videoId}&t=${sec}s`, "_blank", "noopener");
  }

  function parseVideoId(raw) {
    const s = (raw || "").trim();
    if (/^[A-Za-z0-9_-]{11}$/.test(s)) return s;
    const m = s.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([A-Za-z0-9_-]{11})/);
    return m ? m[1] : null;
  }

  function statusBadge(status) {
    const map = {
      conflict: { cls: "bg-error/10 border-error/20 text-error", bar: "bg-error", icon: "warning", label: "Conflict" },
      consensus: { cls: "bg-primary-container/10 border-primary-container/20 text-primary-container", bar: "bg-primary-container", icon: "verified", label: "Consensus" },
      provisional: { cls: "bg-secondary-container/20 border-secondary-container/30 text-secondary", bar: "bg-secondary", icon: "help", label: "Provisional" },
    };
    const s = map[status] || map.provisional;
    return `<div class="flex-shrink-0 ${s.cls} border rounded-sm overflow-hidden flex items-stretch">
      <div class="w-1 ${s.bar}"></div>
      <div class="px-3 py-1 font-label-caps text-label-caps flex items-center gap-1">
        <span class="material-symbols-outlined text-[14px]">${s.icon}</span>${s.label}
      </div></div>`;
  }

  function lifecycleBadge(lc) {
    const map = {
      proposed: "PENDING REVIEW",
      live: "LIVE",
      rejected: "REJECTED",
      superseded: "SUPERSEDED",
    };
    return map[lc] || lc;
  }

  async function boot() {
    const res = await fetch("/api/bootstrap");
    if (!res.ok) throw new Error("bootstrap failed");
    return res.json();
  }

  function wireChrome() {
    const drawer = $("#mobile-drawer");
    $("#mobile-menu-btn")?.addEventListener("click", () => drawer.classList.remove("hidden-imp"));
    $("#mobile-close")?.addEventListener("click", () => drawer.classList.add("hidden-imp"));
    drawer?.addEventListener("click", (e) => {
      if (e.target === drawer) drawer.classList.add("hidden-imp");
    });

    const modal = $("#extract-modal");
    $$("[data-open-extract]").forEach((b) =>
      b.addEventListener("click", () => modal.classList.remove("hidden-imp"))
    );
    $$("[data-close-extract]").forEach((b) =>
      b.addEventListener("click", () => modal.classList.add("hidden-imp"))
    );
    $("#extract-submit")?.addEventListener("click", async () => {
      const id = parseVideoId($("#extract-url").value);
      const msg = $("#extract-msg");
      if (!id) {
        msg.textContent = "Could not parse a YouTube video id.";
        return;
      }
      const r = await fetch("/api/videos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, title: `Ingest ${id}`, channel: "Unassigned" }),
      });
      const v = await r.json();
      msg.textContent = `Registered ${v.id}. Opening review…`;
      setTimeout(() => (location.href = `/review?video=${v.id}`), 400);
    });
  }

  async function pageTimeline() {
    const data = await boot();
    const topics = [...new Set(data.events.flatMap((e) => e.topics || []))].sort();
    const sel = $("#tl-topic");
    topics.forEach((t) => {
      const o = document.createElement("option");
      o.value = t;
      o.textContent = t;
      sel.appendChild(o);
    });

    let status = "";
    const render = () => {
      const q = ($("#tl-search").value || "").toLowerCase();
      const topic = sel.value;
      const rows = data.events.filter((e) => {
        if (status && e.status !== status) return false;
        if (topic && !(e.topics || []).includes(topic)) return false;
        const blob = `${e.name} ${e.place} ${e.blurb} ${(e.actors || []).join(" ")}`.toLowerCase();
        return !q || blob.includes(q);
      });
      $("#tl-count").textContent = String(rows.length);
      $("#tl-feed").innerHTML = rows
        .map(
          (e) => `
        <article class="flex gap-4 md:gap-6 items-start group">
          <div class="flex-shrink-0 w-14 md:w-20 pt-1 flex flex-col items-center">
            <div class="w-3 h-3 rounded-full bg-surface border-2 ${e.status === "conflict" ? "border-error" : "border-primary"} ring-4 ring-background mb-2"></div>
            <span class="font-mono-data text-mono-data text-on-surface-variant">${e.when}</span>
          </div>
          <div class="flex-1 bg-surface-container-low border border-outline-variant/40 rounded-lg hover:border-primary/50 transition-colors overflow-hidden">
            <div class="px-5 py-4 border-b border-outline-variant/20 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-container/50">
              <div>
                <div class="flex items-center gap-3">
                  <span class="font-mono-data text-mono-data text-outline">${e.id}</span>
                  <h3 class="font-headline-sm text-headline-sm">${e.name}</h3>
                </div>
                <div class="flex items-center gap-4 font-mono-data text-mono-data text-on-surface-variant mt-1">
                  <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">location_on</span>${e.place}</span>
                  <span class="hidden md:flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">group</span>${(e.actors || []).join(", ")}</span>
                </div>
              </div>
              ${statusBadge(e.status)}
            </div>
            <div class="px-5 py-4 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="md:col-span-2">
                <p class="font-body-sm text-body-sm text-on-surface-variant mb-4">${e.blurb}</p>
                <div class="flex flex-wrap gap-2">${(e.topics || [])
                  .map((t) => `<span class="px-2 py-1 bg-surface-variant rounded-sm font-mono-data text-[11px] border border-outline-variant/30">${t}</span>`)
                  .join("")}</div>
              </div>
              <div class="md:border-l border-outline-variant/20 md:pl-6">
                <div class="font-label-caps text-label-caps text-on-surface-variant mb-2">Tellings Index</div>
                <div class="flex items-end gap-2">
                  <span class="font-headline-md text-headline-md leading-none">${(e.telling_video_ids || []).length}</span>
                  <span class="font-mono-data text-mono-data text-outline mb-1">Sources</span>
                </div>
                <a class="mt-4 inline-block font-mono-data text-mono-data text-primary underline decoration-dotted underline-offset-4" href="/compare?event=${encodeURIComponent(e.id)}">Open multi-telling</a>
              </div>
            </div>
          </div>
        </article>`
        )
        .join("");
    };

    $("#tl-search").addEventListener("input", render);
    sel.addEventListener("change", render);
    $$("#tl-status [data-status]").forEach((btn) => {
      btn.addEventListener("click", () => {
        status = btn.dataset.status;
        $$("#tl-status [data-status]").forEach((b) => {
          b.classList.toggle("bg-surface-variant/50", b === btn);
          b.classList.toggle("text-primary", b === btn);
          b.classList.toggle("text-on-surface-variant", b !== btn);
        });
        render();
      });
    });
    render();
  }

  async function pageCatalog() {
    const data = await boot();
    const n = data.videos.length;
    const spans = data.videos.filter((v) => v.has_spans).length;
    if ($("#cat-count")) {
      $("#cat-count").textContent = `${n} videos · ${spans} with spans on disk`;
    }
    $("#cat-body").innerHTML = data.videos
      .map(
        (v) => `
      <tr class="data-table-row border-t border-outline-variant/20">
        <td class="px-4 py-3">${v.pilot || "—"}</td>
        <td class="px-4 py-3">
          <div class="text-on-surface">${v.title}</div>
          <div class="text-on-surface-variant/60">${v.id}</div>
        </td>
        <td class="px-4 py-3">${v.channel}</td>
        <td class="px-4 py-3">${v.cluster || "—"}</td>
        <td class="px-4 py-3">${v.asr}</td>
        <td class="px-4 py-3">${v.has_spans ? "yes" : "—"}</td>
        <td class="px-4 py-3 whitespace-nowrap">
          <a class="text-primary underline decoration-dotted" href="/transcripts?video=${v.id}">Transcript</a>
          <a class="text-primary underline decoration-dotted ml-3" href="/review?video=${v.id}">Review</a>
          <a class="text-primary underline decoration-dotted ml-3" href="https://www.youtube.com/watch?v=${v.id}" target="_blank" rel="noreferrer">YouTube</a>
        </td>
      </tr>`
      )
      .join("");
  }

  async function pageReview(prefVideo) {
    const data = await boot();
    const sel = $("#rv-video");
    const withSpans = data.videos.filter((v) => v.has_spans);
    const withoutSpans = data.videos.filter((v) => !v.has_spans);
    const addOpt = (v) => {
      const o = document.createElement("option");
      o.value = v.id;
      const mark = v.has_spans ? "●" : "○";
      o.textContent = `${mark} ${v.channel}: ${v.title}`;
      sel.appendChild(o);
    };
    withSpans.forEach(addOpt);
    withoutSpans.forEach(addOpt);
    const pendingVideo = withSpans.find((v) =>
      data.claims.some((c) => c.video_id === v.id && c.lifecycle === "proposed")
    );
    const prefer =
      (prefVideo && data.videos.some((v) => v.id === prefVideo) && prefVideo) ||
      pendingVideo?.id ||
      withSpans[0]?.id ||
      data.videos[0]?.id;
    if (prefer) sel.value = prefer;

    let selectedClaimId = null;
    let videoSpans = [];
    let videoSentences = [];

    const clearSpanHighlights = () => {
      $$("#rv-spans [data-t]").forEach((el) => {
        el.classList.remove("span-active", "claim-span-highlighted");
        const p = el.querySelector(".span-text");
        if (p && el.dataset.rawText) {
          p.textContent = el.dataset.rawText;
        }
      });
    };

    const highlightClaimInTranscript = (ctx) => {
      clearSpanHighlights();
      if (!ctx || !ctx.sentence) return;

      const tStart = ctx.t_start;
      const tEnd = ctx.t_end;
      let targetEl = null;

      $$("#rv-spans [data-t]").forEach((el) => {
        const start = Number(el.dataset.t);
        const end = Number(el.dataset.te);
        const origText = el.dataset.rawText || el.querySelector(".span-text")?.textContent || "";
        if (!el.dataset.rawText) el.dataset.rawText = origText;

        const overlapsTime = (start <= tEnd && end >= tStart) || (Math.abs(start - tStart) < 3);
        const matchesWords = ctx.sentence && (
          ctx.sentence.toLowerCase().includes(origText.toLowerCase().slice(0, 30)) ||
          origText.toLowerCase().includes(ctx.sentence.toLowerCase().slice(0, 30))
        );

        if (overlapsTime || matchesWords) {
          el.classList.add("span-active", "claim-span-highlighted");
          const p = el.querySelector(".span-text");
          if (p) {
            p.innerHTML = highlightInSpan(origText, ctx.sentence);
          }
          if (!targetEl) targetEl = el;
        }
      });

      if (targetEl) {
        targetEl.scrollIntoView({ block: "center", behavior: "smooth" });
      }
    };

    const selectClaim = (claimId, doJump = false) => {
      selectedClaimId = selectedClaimId === claimId && !doJump ? null : claimId;
      renderClaims(sel.value);
      if (selectedClaimId) {
        const c = data.claims.find((x) => x.id === selectedClaimId);
        if (c) {
          const ctx = findClaimContext(c, videoSentences);
          highlightClaimInTranscript(ctx);
          if (doJump) ytJump(sel.value, c.t_start);
        }
      } else {
        clearSpanHighlights();
      }
    };

    const renderClaims = (videoId) => {
      const claims = data.claims.filter((c) => c.video_id === videoId);
      const pending = claims.filter((c) => c.lifecycle === "proposed").length;
      $("#rv-pending").textContent = `${pending} PENDING`;
      const approveAll = $("#rv-approve-all");
      if (approveAll) {
        approveAll.classList.toggle("hidden", pending === 0);
        approveAll.disabled = pending === 0;
        approveAll.textContent = "Approve all";
      }
      $("#rv-claims").innerHTML = claims.length
        ? claims
            .map(
              (c) => {
                const isSelected = c.id === selectedClaimId;
                const ctx = isSelected ? findClaimContext(c, videoSentences) : null;
                return `
        <div class="claim-item cursor-pointer bg-surface border ${
          isSelected
            ? "claim-card-selected border-primary"
            : "border-outline-variant/40 hover:border-outline-variant/70"
        } rounded p-4 transition-all" data-claim="${esc(c.id)}">
          <div class="flex justify-between items-start mb-3">
            <div class="font-mono-data text-mono-data text-on-surface-variant/60 text-[10px]">ID: ${esc(c.id)}</div>
            <span class="font-label-caps text-[9px] px-2 py-0.5 bg-surface-variant">${lifecycleBadge(c.lifecycle)}</span>
          </div>
          <h3 class="font-headline-sm text-[16px] mb-2">${esc(c.claim_text)}</h3>
          <p class="font-body-sm text-body-sm text-on-surface-variant/80 mb-3">${esc(c.body || "")}</p>
          <button type="button" class="font-mono-data text-[12px] text-primary underline decoration-dashed block mb-3 text-left" data-jump="${c.t_start}" data-claim-jump="${esc(c.id)}">
            [${fmtTime(c.t_start)}] ${(c.quote || "").slice(0, 80)}
          </button>
          ${
            isSelected && ctx
              ? `
          <div class="mt-3 pt-3 border-t border-outline-variant/20">
            <div class="font-label-caps text-[10px] tracking-wider text-primary mb-1.5 flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[14px]">subject</span>
              TRANSCRIPT CONTEXT
            </div>
            <div class="p-3 bg-surface-container-lowest/90 border border-outline-variant/30 rounded font-body-sm text-[13px] leading-relaxed text-on-surface-variant">
              ${ctx.prev ? `<span class="opacity-60">${esc(ctx.prev)} </span>` : ""}
              <mark class="claim-soft-highlight">${esc(ctx.sentence)}</mark>
              ${ctx.after ? `<span class="opacity-60"> ${esc(ctx.after)}</span>` : ""}
            </div>
          </div>`
              : ""
          }
          ${
            c.lifecycle === "proposed"
              ? `<div class="flex gap-2 border-t border-outline-variant/20 pt-3 mt-3">
            <button type="button" data-act="rejected" data-id="${esc(c.id)}" class="flex-1 bg-error/10 border border-error/30 text-error font-label-caps text-[11px] py-2 rounded">Reject</button>
            <button type="button" data-act="live" data-id="${esc(c.id)}" class="flex-1 bg-primary/10 border border-primary/40 text-primary font-label-caps text-[11px] py-2 rounded">Approve</button>
          </div>`
              : ""
          }
        </div>`;
              }
            )
            .join("")
        : `<p class="font-body-sm text-on-surface-variant">No claims bound to this video yet. Live extraction is not wired; seed claims appear on Lazar/C2 videos.</p>`;

      $$("#rv-claims [data-claim]").forEach((card) => {
        card.addEventListener("click", (e) => {
          if (e.target.closest("[data-act]")) return;
          if (e.target.closest("[data-jump]")) {
            e.stopPropagation();
            selectClaim(card.dataset.claim, true);
            return;
          }
          selectClaim(card.dataset.claim, false);
        });
      });

      $$("#rv-claims [data-act]").forEach((b) =>
        b.addEventListener("click", async (e) => {
          e.stopPropagation();
          await fetch(`/api/claims/${b.dataset.id}/lifecycle`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lifecycle: b.dataset.act }),
          });
          const fresh = await boot();
          data.claims = fresh.claims;
          renderClaims(videoId);
        })
      );
    };

    $("#rv-approve-all")?.addEventListener("click", async () => {
      const videoId = sel.value;
      const pending = data.claims.filter(
        (c) => c.video_id === videoId && c.lifecycle === "proposed"
      ).length;
      if (!pending) return;
      const btn = $("#rv-approve-all");
      btn.disabled = true;
      btn.textContent = "Approving…";
      try {
        const res = await fetch(`/api/videos/${videoId}/claims/lifecycle`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lifecycle: "live" }),
        });
        if (!res.ok) throw new Error(await res.text());
        const fresh = await boot();
        data.claims = fresh.claims;
        renderClaims(videoId);
      } catch (err) {
        btn.disabled = false;
        btn.textContent = "Approve all";
        console.error(err);
      }
    });

    const loadVideo = async () => {
      const id = sel.value;
      const v = data.videos.find((x) => x.id === id);
      $("#rv-asset").textContent = v ? v.title : id;
      const res = await fetch(`/api/videos/${id}/spans`);
      const pack = res.ok ? await res.json() : { spans: [] };
      const q = ($("#rv-find").value || "").toLowerCase();
      const onDisk = (pack.spans || []).length;
      let spans = pack.spans || [];
      if (!spans.length) {
        spans = data.claims
          .filter((c) => c.video_id === id)
          .map((c) => ({
            t_start: c.t_start,
            t_end: c.t_end,
            text: c.quote || c.claim_text,
            speaker_label: c.speaker_label,
          }));
      }
      const beforeFind = spans.length;
      if (q) spans = spans.filter((s) => (s.text || "").toLowerCase().includes(q));
      videoSpans = spans;
      videoSentences = extractSentences(spans);
      selectedClaimId = null;

      const ready = withSpans.map((x) => x.title).filter(Boolean);
      const emptyMsg = () => {
        if (q && beforeFind) {
          return `<p class="font-body-sm text-on-surface-variant">No spans match “${q}”.</p>`;
        }
        if (onDisk) return "";
        const asr = v?.asr || "queued";
        const extra =
          asr === "audio_ready"
            ? "Audio is on disk; ASR has not been run for this id yet."
            : asr === "complete"
              ? "ASR is marked complete but spans JSON was not found."
              : "This catalog row is still queued for download/ASR.";
        const hint = ready.length
          ? `Transcripts on disk: ${ready.join("; ")}.`
          : "No transcripts are on disk yet.";
        return `<p class="font-body-sm text-on-surface-variant">${extra} ${hint} Pick a ● video in the header dropdown.</p>`;
      };
      $("#rv-spans").innerHTML = spans.length
        ? spans
            .map(
              (s) => `
        <div class="flex gap-4 group" data-t="${s.t_start}" data-te="${s.t_end}" data-raw-text="${esc(s.text)}">
          <div class="w-16 flex-shrink-0 text-right">
            <button type="button" class="font-mono-data text-[11px] text-primary" data-yt="${s.t_start}">${fmtTime(s.t_start)}</button>
            <span class="font-label-caps text-label-caps text-secondary mt-1 block">${esc(s.speaker_label || "?")}</span>
          </div>
          <div class="flex-1 pb-3 border-b border-outline-variant/10 p-2 rounded">
            <p class="span-text font-body-md text-body-md text-on-surface leading-relaxed">${esc(s.text)}</p>
          </div>
        </div>`
            )
            .join("")
        : emptyMsg();
      $$("#rv-spans [data-yt]").forEach((b) =>
        b.addEventListener("click", () => ytJump(id, b.dataset.yt))
      );
      renderClaims(id);
    };

    sel.addEventListener("change", loadVideo);
    $("#rv-find").addEventListener("input", loadVideo);
    await loadVideo();
  }

  async function pageCompare(eventId) {
    const data = await boot();
    const sel = $("#cmp-event");
    data.events.forEach((e) => {
      const o = document.createElement("option");
      o.value = e.id;
      o.textContent = e.id;
      sel.appendChild(o);
    });
    sel.value = eventId && data.events.some((e) => e.id === eventId) ? eventId : data.events[0].id;

    const render = () => {
      const ev = data.events.find((e) => e.id === sel.value);
      if (!ev) return;
      $("#cmp-title").textContent = ev.name;
      $("#cmp-blurb").textContent = ev.blurb;
      $("#cmp-tags").innerHTML = (ev.topics || [])
        .map((t) => `<span class="px-2 py-1 bg-surface-variant/30 font-mono-data text-[10px] border border-outline-variant/20 rounded">${t}</span>`)
        .join("");
      const oqs = data.open_questions.filter((q) => q.event_id === ev.id);
      $("#cmp-oqs").innerHTML = oqs
        .map(
          (q) => `
        <div class="p-3 bg-surface-variant/20 border border-outline-variant/20 rounded">
          <p class="font-body-sm text-[13px] leading-relaxed">${q.text}</p>
          <div class="mt-2 font-mono-data text-[10px] text-on-surface-variant">${q.priority} · ${q.kind}</div>
        </div>`
        )
        .join("");

      const vids = ev.telling_video_ids || [];
      const sources = vids
        .map((id) => data.videos.find((v) => v.id === id))
        .filter(Boolean);
      const eventClaims = data.claims.filter((c) => c.event_id === ev.id && c.lifecycle === "live");
      const rows = [];
      const seen = new Set();
      for (const c of eventClaims) {
        const key = c.claim_text.toLowerCase();
        if (seen.has(key)) continue;
        seen.add(key);
        rows.push(c.claim_text);
      }

      const cols = sources.length || 1;
      let html = `<div class="grid gap-4" style="grid-template-columns: 280px repeat(${cols}, minmax(240px,1fr))">`;
      html += `<div class="sticky top-0 left-0 bg-surface-dim pb-2 font-label-caps text-[10px] text-on-surface-variant/50">Atomic Claims ↓ \\ Sources →</div>`;
      for (const s of sources) {
        html += `<div class="bg-surface-container p-4 border-t-2 border-t-primary border border-outline-variant/20 rounded">
          <div class="font-headline-sm text-[14px]">${s.channel}</div>
          <div class="font-mono-data text-[10px] text-on-surface-variant/70">${s.title}</div>
        </div>`;
      }
      if (!rows.length) {
        html += `<div class="col-span-full font-body-sm text-on-surface-variant">No live claims on this Event yet. Approve claims in Review.</div>`;
      }
      for (const text of rows) {
        html += `<div class="p-4 bg-surface-container-lowest border border-outline-variant/10 rounded">
          <p class="font-body-md text-sm">${text}</p>
        </div>`;
        for (const s of sources) {
          const hit = eventClaims.find((c) => c.video_id === s.id && c.claim_text === text);
          if (hit) {
            html += `<div class="p-4 bg-surface-container-low border border-outline-variant/20 rounded relative">
              <div class="absolute -left-[1px] top-4 w-[2px] h-4 bg-[#81c784]"></div>
              <div class="flex justify-between mb-2">
                <span class="material-symbols-outlined text-[#81c784] text-[18px]">check_circle</span>
                <button type="button" class="text-on-surface-variant" data-yt="${s.id}" data-t="${hit.t_start}" title="Jump to source">
                  <span class="material-symbols-outlined text-[16px]">smart_display</span>
                </button>
              </div>
              <p class="font-body-sm text-[13px]">“${hit.quote}”</p>
              <div class="mt-2 font-mono-data text-[10px] text-on-surface-variant/50">[${fmtTime(hit.t_start)}]</div>
            </div>`;
          } else {
            html += `<div class="p-4 border border-dashed border-outline-variant/30 rounded font-mono-data text-[11px] text-on-surface-variant/50">Coverage gap</div>`;
          }
        }
      }
      html += `</div>`;
      $("#cmp-matrix").innerHTML = html;
      $$("#cmp-matrix [data-yt]").forEach((b) =>
        b.addEventListener("click", () => ytJump(b.dataset.yt, b.dataset.t))
      );
    };

    sel.addEventListener("change", () => {
      history.replaceState(null, "", `/compare?event=${encodeURIComponent(sel.value)}`);
      render();
    });
    $("#cmp-oq-add").addEventListener("click", async () => {
      const text = $("#cmp-oq-text").value.trim();
      if (!text) return;
      await fetch("/api/open-questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_id: sel.value, text }),
      });
      $("#cmp-oq-text").value = "";
      const fresh = await boot();
      data.open_questions = fresh.open_questions;
      render();
    });
    render();
  }

  async function pageTranscripts(prefVideo) {
    const data = await boot();
    const list = $("#tx-list");
    const sel = $("#tx-video");
    const withSpans = data.videos.filter((v) => v.has_spans);
    const withoutSpans = data.videos.filter((v) => !v.has_spans);
    $("#tx-count").textContent = `${withSpans.length} on disk · ${data.videos.length} catalogued`;

    const addOpt = (v) => {
      if (!sel) return;
      const o = document.createElement("option");
      o.value = v.id;
      o.textContent = `${v.has_spans ? "●" : "○"} ${v.channel}: ${v.title}`;
      sel.appendChild(o);
    };
    withSpans.forEach(addOpt);
    withoutSpans.forEach(addOpt);

    const knownPref = prefVideo && data.videos.some((v) => v.id === prefVideo);
    const prefer = knownPref
      ? prefVideo
      : withSpans[0]?.id || data.videos[0]?.id;
    if (prefer && sel) sel.value = prefer;

    const emptyMsg = (v, q, hadSpans) => {
      if (q && hadSpans) {
        return `<p class="font-body-sm text-on-surface-variant">No spans match “${q}”.</p>`;
      }
      if (!v) return `<p class="font-body-sm text-on-surface-variant">Unknown video.</p>`;
      const asr = v.asr || "queued";
      if (asr === "audio_ready") {
        return `<p class="font-body-sm text-on-surface-variant">Audio is on disk; ASR has not been run for this id yet. No transcript to show.</p>`;
      }
      if (asr === "complete") {
        return `<p class="font-body-sm text-on-surface-variant">ASR is marked complete but spans JSON was not found.</p>`;
      }
      return `<p class="font-body-sm text-on-surface-variant">This catalog row is still queued for download/ASR. ${withSpans.length} transcript(s) are on disk — pick a ● video in the list.</p>`;
    };

    const paintList = (activeId, q) => {
      if (!list) return;
      const ql = (q || "").toLowerCase();
      const match = (v) =>
        !ql || `${v.title} ${v.channel} ${v.id} ${v.pilot || ""}`.toLowerCase().includes(ql);
      const group = (label, rows) => {
        const vis = rows.filter(match);
        if (!vis.length) return "";
        return `<div class="font-label-caps text-[10px] tracking-widest uppercase text-on-surface-variant/70 px-2 pt-3 pb-1">${label}</div>${vis
          .map((v) => {
            const on = v.id === activeId;
            return `<button type="button" data-vid="${v.id}" class="w-full text-left px-3 py-2 rounded border ${
              on
                ? "bg-surface-variant/40 border-primary/40 text-on-surface"
                : "border-transparent hover:bg-surface-container-high text-on-surface-variant"
            }">
              <div class="font-mono-data text-[10px] ${v.has_spans ? "text-primary" : ""}">${
              v.has_spans ? "●" : "○"
            } ${v.channel}${v.pilot ? " · " + v.pilot : ""}</div>
              <div class="font-body-sm text-[13px] leading-snug mt-0.5 line-clamp-2">${v.title}</div>
            </button>`;
          })
          .join("")}`;
      };
      list.innerHTML = group("On disk", withSpans) + group("Queued", withoutSpans) ||
        `<p class="font-body-sm text-on-surface-variant px-2">No videos match.</p>`;
      $$("#tx-list [data-vid]").forEach((b) =>
        b.addEventListener("click", () => {
          if (sel) sel.value = b.dataset.vid;
          loadVideo();
        })
      );
    };

    const loadVideo = async () => {
      const id = sel?.value || prefer;
      const v = data.videos.find((x) => x.id === id);
      history.replaceState(null, "", id ? `/transcripts?video=${encodeURIComponent(id)}` : "/transcripts");
      $("#tx-title").textContent = v ? v.title : "Unknown video";
      $("#tx-meta").textContent = v
        ? `${v.channel} · ${v.id}${v.pilot ? " · " + v.pilot : ""} · asr ${v.asr || "queued"}`
        : "";
      const review = $("#tx-review");
      const yt = $("#tx-yt");
      if (review) review.href = id ? `/review?video=${encodeURIComponent(id)}` : "/review";
      if (yt) {
        yt.href = id ? `https://www.youtube.com/watch?v=${id}` : "#";
        yt.classList.toggle("pointer-events-none", !id);
      }
      paintList(id, $("#tx-filter")?.value || "");

      const q = ($("#tx-find").value || "").toLowerCase();
      let spans = [];
      let onDisk = 0;
      if (v) {
        const res = await fetch(`/api/videos/${id}/spans`);
        const pack = res.ok ? await res.json() : { spans: [] };
        spans = pack.spans || [];
        onDisk = spans.length;
      }
      const beforeFind = spans.length;
      if (q) spans = spans.filter((s) => (s.text || "").toLowerCase().includes(q));
      $("#tx-spans").innerHTML = spans.length
        ? spans
            .map(
              (s) => `
        <div class="flex gap-4 group" data-t="${s.t_start}" data-te="${s.t_end}">
          <div class="w-16 flex-shrink-0 text-right">
            <button type="button" class="font-mono-data text-[11px] text-primary" data-yt="${s.t_start}">${fmtTime(s.t_start)}</button>
            <span class="font-label-caps text-label-caps text-secondary mt-1 block">${s.speaker_label || "?"}</span>
          </div>
          <div class="flex-1 pb-3 border-b border-outline-variant/10 p-2 rounded">
            <p class="font-body-md text-body-md text-on-surface leading-relaxed">${s.text}</p>
          </div>
        </div>`
            )
            .join("")
        : emptyMsg(v, q, beforeFind || onDisk);
      $$("#tx-spans [data-yt]").forEach((b) =>
        b.addEventListener("click", () => ytJump(id, b.dataset.yt))
      );
    };

    sel?.addEventListener("change", loadVideo);
    $("#tx-find")?.addEventListener("input", loadVideo);
    $("#tx-filter")?.addEventListener("input", () => paintList(sel?.value || prefer, $("#tx-filter").value));
    await loadVideo();
  }

  async function pageGraph() {
    const data = await boot();
    const ev = data.events[0];
    const people = [...new Set(data.claims.map((c) => c.person).filter(Boolean))];
    const nodes = [
      { id: ev.id, kind: "Event", label: ev.name, x: 80, y: 220 },
      ...people.map((p, i) => ({ id: p, kind: "Person", label: p, x: 360, y: 80 + i * 160 })),
      ...data.claims
        .filter((c) => c.event_id === ev.id)
        .slice(0, 6)
        .map((c, i) => ({
          id: c.id,
          kind: "Claim",
          label: c.claim_text,
          lifecycle: c.lifecycle,
          video_id: c.video_id,
          t: c.t_start,
          person: c.person,
          x: 680,
          y: 40 + i * 110,
        })),
    ];

    const canvas = $("#g-canvas");
    const inspect = $("#g-inspect-body");
    $("#g-focus").textContent = `ENTITY: ${ev.name}`;

    const paint = (q = "") => {
      const ql = q.toLowerCase();
      canvas.innerHTML = nodes
        .filter((n) => !ql || n.label.toLowerCase().includes(ql) || n.kind.toLowerCase().includes(ql))
        .map((n) => {
          const face =
            n.kind === "Person" && n.label === "Bob Lazar"
              ? `<img alt="" class="w-8 h-8 rounded object-cover grayscale mix-blend-screen mb-2 border border-outline-variant/30" src="/static/img/portrait-lazar.jpg"/>`
              : "";
          return `
        <button type="button" data-nid="${n.id}" class="absolute text-left w-64 p-3 bg-surface-container-low border rounded-lg ${n.lifecycle === "proposed" ? "node-proposed" : "node-live"}" style="left:${n.x}px;top:${n.y}px">
          ${face}
          <div class="font-label-caps text-label-caps text-primary">${n.kind}</div>
          <div class="font-headline-sm text-[14px] mt-1">${n.label}</div>
          ${n.lifecycle ? `<div class="font-mono-data text-[10px] mt-1">${n.lifecycle}</div>` : ""}
        </button>`;
        })
        .join("");

      $$("#g-canvas [data-nid]").forEach((b) =>
        b.addEventListener("click", () => {
          $$("#g-canvas [data-nid]").forEach((x) => x.classList.remove("node-selected"));
          b.classList.add("node-selected");
          const n = nodes.find((x) => x.id === b.dataset.nid);
          inspect.innerHTML = `
            <div class="font-label-caps text-primary mb-1">${n.kind}</div>
            <div class="font-headline-sm text-headline-sm text-on-surface mb-2">${n.label}</div>
            <div class="font-mono-data text-[11px] mb-3">${n.id}</div>
            ${n.video_id ? `<button type="button" class="text-primary underline font-mono-data text-[12px]" id="g-jump">Jump to source</button>` : ""}
            ${n.kind === "Event" ? `<a class="block mt-3 text-primary underline font-mono-data text-[12px]" href="/compare?event=${n.id}">Open compare</a>` : ""}`;
          $("#g-jump")?.addEventListener("click", () => ytJump(n.video_id, n.t));
        })
      );
    };
    $("#g-search").addEventListener("input", (e) => paint(e.target.value));
    paint();
  }

  document.addEventListener("DOMContentLoaded", wireChrome);

  return {
    pageTimeline,
    pageCatalog,
    pageReview,
    pageCompare,
    pageGraph,
    pageTranscripts,
    extractSentences,
    findClaimContext,
    highlightInSpan,
    esc,
  };
})();
