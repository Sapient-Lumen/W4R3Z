# Rust microkernel / micro-hypervisor living archive

**North star:** see [`docs/00-meta/charter.md`](docs/00-meta/charter.md).

Revision notes: [`CHANGELOG.md`](CHANGELOG.md).

This repo is a **living archive** for designing a *from-scratch* Rust microkernel / micro-hypervisor with **explicit assurance claims** and an **evidence trail** (RFC → ADR, Claim → Invariant → Evidence). We do **not** clone seL4 or inherit its proofs; we learn from it.

## How to navigate
0. Mile-high map (profiles + non-negotiables): [`docs/00-meta/trajectory-map.md`](docs/00-meta/trajectory-map.md)
0.5 Editing runbook (LLM amnesia guardrail): [`docs/00-meta/llm-runbook.md`](docs/00-meta/llm-runbook.md)
1. Threat model: [`docs/10-threat-model/threat-model.md`](docs/10-threat-model/threat-model.md)  
2. Assurance (claims + invariants + TCB): [`docs/20-assurance/`](docs/20-assurance/)  
3. Architecture (incl. hypervisor-first): [`docs/30-architecture/`](docs/30-architecture/)  
4. Verification program: [`docs/40-verification/`](docs/40-verification/)  
5. LLM-assisted control: [`docs/70-llm-control/`](docs/70-llm-control/)  
6. OS inspirations mapped to specs: [`docs/90-inspirations/`](docs/90-inspirations/)  
7. Decisions: [`adrs/`](adrs/) and proposals: [`rfcs/`](rfcs/)

## Archive discipline (size control)
- Cite with REF-IDs; register our artifacts as EVID-IDs; avoid pasting upstream texts.  
- Prefer editing existing docs over creating new ones; follow [`docs/00-meta/archive-policy.md`](docs/00-meta/archive-policy.md).

Note: LLM-assisted control is treated as non-TCB. We still specify an ACP validator semantics slice (CH-ACP/CH-LOG) so we can model-check “propose→validate→authorize→execute→log” and later mechanize it.

Key deep-dives: capability semantics and exit/entry surface budget live under `docs/30-architecture/`; side-channel posture is explicit in `docs/10-threat-model/sidechannels.md`.

Workflow/portal taxonomy: `docs/30-architecture/portal-family-registry.md` (closed `portal.*` set; policy-killable lanes), `docs/30-architecture/notification-request-schema-v0.md` (CH-NOTIF v0; D-ATTN), `docs/30-architecture/job-request-schema-v0.md` (CH-JOBREQ v0; D-JOBS; no ambient cron/alarms; ACP kind `portal.jobs.submit`), and `docs/30-architecture/background-request-schema-v0.md` (CH-BGREQ v0; D-BGLEASE; no ambient background daemons/autostart registries; ACP kind `portal.background.request`).

Network lease workflow seam: `docs/30-architecture/network-request-schema-v0.md` (CH-NETREQ v0; ACP kind `portal.net.request`) and `docs/30-architecture/network-lease-schema-v0.md` (CH-NETLEASE v0; D-NETLEASE; no ambient sockets).

Entropy workflow seam: `docs/30-architecture/entropy-request-schema-v0.md` (CH-ENTREQ v0; ACP kind `portal.entropy.request`) and `docs/30-architecture/entropy-descriptor-schema-v0.md` (CH-ENTROPY v0; D-NONDET; no ambient RNG APIs).

Commutativity/ordering artifacts: `docs/30-architecture/commutativity-and-interface-scalability.md`, `docs/30-architecture/serialization-boundary-registry.md` (closed `validator`/`svc:<name>`/`none` token set), `docs/30-architecture/hot-action-surface-v0.md`, `docs/30-architecture/hot-action-boundaries-v0.md`, and `docs/30-architecture/conflict-key-family-registry.md` (closed CH-CONFLICTKEY family allowlist).


Scope discipline: explicit exclusions live in `docs/20-assurance/non-claims.md`; key refs are indexed in `docs/00-meta/bibliography.md`.

## Repo checks
- Run `make lint` before/after edits to catch undefined IDs, broken links, and schema drift (ADR-0001; EVID-2026-003).
- `make lint` includes drift gates that keep assurance IDs (A-/C-/I-/PO-) registry-closed (EVID-2026-173), preventing typo'd/orphan IDs from weakening traceability.
- `make lint` also enforces CH-PLEDGE token/mapping coherence: `pledge-token-mapping.md` must cover the closed CH-PLEDGE v0 token set exactly (EVID-2026-179), preventing “shadow promise tokens” from drifting into the least-authority surface.
- `make lint` also enforces retry-safety wiring for ACP kinds: any kind claiming **at-least-once-safe** must name an explicit stable dedupe/id key (e.g., CH-EFFCON `contract_id`, CH-JOBREQ `job_id`, CH-TIMEREQ `req_id`, CH-NOTIF.id) so validator semantics remain implementable and duplicate effects are avoidable (EVID-2026-181).
- `make lint` also enforces D-COMMUTE predicate explicitness for the ACP surface: every CH-ACP kind must have an explicit commutation predicate + normalized observation boundary entry in `docs/70-llm-control/acp-commutativity-predicate-registry.md` (EVID-2026-184), preventing planner-unsafe “commutes” drift into prose.
- `make lint` also enforces CH-ACPOUT retry visibility: outcome receipts must be able to distinguish applied vs deduped accepts by wiring `effect="duplicate_suppressed"` (CH-ACPOUT v0) across ACP semantics + PO-RETRY-DEDUP (EVID-2026-182), preventing retry ambiguity drift.
- `make lint` also enforces workflow hardening knob profiling: any `cfg.params.capshell.*` workflow posture knob (e.g., `cfg.params.capshell.minimal_context`) must be registry-closed and have A–D defaults pinned in `docs/30-architecture/profile-workflow-defaults.md` (EVID-2026-183), preventing drift back into prose-only “strict profile” workflow rules.
- `make lint` also enforces capshell explicit-budget wiring: when `cfg.params.capshell.require_budget_lease` is present, it must be registry-closed, profiled (A–D defaults pinned), and referenced from ACP semantics/kind registry/deny-code vocabulary so “no implicit sponsorship” (D-BUDGET) can’t drift back into ad-hoc implementation state (EVID-2026-185).
- `make lint` also enforces CH-PLUMBMSG schema formality: `docs/30-architecture/plumb-message-schema-v0.md` must stay marked as a schema surface (no “informal” regression), include explicit bounds/validation anchors, and reference the canonical `intent-kind` registry (EVID-2026-191), preventing workflow plumbing drift into prose-only surfaces.
- `make lint` also enforces lane-deny key binding: `lane-disabled`/`cfg-deny` denials must bind `reason.ref_key=<cfg.params.* key>` so kill-switch evidence stays reviewable and doesn't drift into unbound tokens (EVID-2026-186).
- `make lint` also enforces ordering-deny digest binding: ordering-related CH-DENY denials (`conflict-key-invalid` / `order-witness-*`) must be digest-bound (`conflict_key_digest`/`order_digest`) with `reason.kind="ordering"` so D-COMMUTE ordering failures stay reviewable without ambient/prose-only logs (EVID-2026-187).
- `make lint` also enforces policy/authority-deny digest binding: policy-related CH-DENY denials (`missing-approval` / `expired-approval` / `policy-deny`) must bind `reason.kind="policy"` and `reason.ref_digest = digest(CH-POLICY v0)` **or** `digest(CH-POLICYHANDLE v0)` so “which policy was in force?” stays reviewable without ambient/log-only explanations (EVID-2026-189).
- `make lint` also enforces lane-gated ACP kind discoverability: any lane-gated ACP kind (`portal.*`, `capshell.exec`, `fcell.*`) must explicitly name its required `cfg.params.lane.*` kill switch key in the ACP kind registry, and the key must exist in the config-toggle registry + profile lane defaults (EVID-2026-195), preventing “lane-gated but unnamed” drift.
- `make lint` also enforces the continuation prompt surface contract for `out/context_pack.md`: the context pack header must match the top CHANGELOG revision/date and include non-negotiables, must-read set, profile matrix, and open questions (EVID-2026-180), preventing context-pack drift that causes archive amnesia.
- Optional: `make context-pack` writes `out/context_pack.md` for copy/paste-friendly continuation prompts.
