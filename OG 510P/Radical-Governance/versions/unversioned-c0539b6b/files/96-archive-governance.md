# Archive Governance (How the Research Program Stays Coherent)

This archive is designed to grow *slowly* while remaining decision-useful.

## A. What belongs here
A memo belongs here only if it:
- introduces a **new reusable primitive** (toolkit module, interface, metric loop), or
- clarifies a **scope boundary** (who owns what), or
- adds a **new failure mode** with a concrete mitigation.

Everything else SHOULD be a refactor of existing text.

## B. Size and structure constraints
- A memo SHOULD fit on ~1–3 pages (roughly 1,000–2,000 words).
- Prefer **bullet specs** over essays.
- Cite primary sources and summarize implications; avoid long quotations.

## C. Evidence discipline
- Every strong claim SHOULD have either:
  - a citation to a credible anchor, or
  - an explicit “assumption” tag.
- Measurement proposals MUST specify the decision loop they serve (see `03-metrics-and-evidence.md`).

## D. Refactoring rules (anti-archive-bloat)
- If a concept appears in 3+ places, extract it into:
  - the toolkit (`02-...`), metrics (`03-...`), threats (`04-...`), or interoperability (`70-...`).
- When adding a new primitive, update at least **two** scope memos to reference it (or don’t add it).

## E. Change control (lightweight)
- Treat each edit as an “RFC” in miniature:
  - what changed
  - why it matters
  - what it replaces
  - how we’ll know it worked (metric / falsification)
- Keep the bibliography compact and high-trust (`90-bibliography.md`).

## F. Default stance
- Prefer **polycentric** systems with clear interfaces over “one ring” solutions.
- Prefer **reversible** changes (sunsets, pilots, evaluation) over irreversible leaps.
