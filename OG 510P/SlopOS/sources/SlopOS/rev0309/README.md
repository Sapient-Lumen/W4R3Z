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

Wait-set seam: `docs/30-architecture/waitset-posture-v0.md` (D-WAITSET v0: observational signal bits, explicit bindings, level-triggered by default, no packet queue/user injection, no new workflow/ACP surface).

IoQueue seam: `docs/30-architecture/ioq-posture-v0.md` (D-IOQ v0: provider-owned batching, explicit handles only, one SQE → one op, no path constructors, no chain/message-ring drift, no new workflow/ACP surface).

Request-context seam: `docs/30-architecture/reqctx-posture-v0.md` (D-REQCTX v0: sticky parent→child propagation, one absolute monotonic deadline intent, no portable detach/shield semantics, bounded tags only, no new workflow/ACP surface).

Turn-concurrency seam: `docs/30-architecture/turns-posture-v0.md` (D-TURNS v0: per-component runtime discipline, one active turn per vat, far calls stay async, no hidden inbox pumping, no portable reentrancy/interleaving knob, no new workflow/ACP surface).

CapRPC session seam: `docs/30-architecture/caprpc-session-posture-v0.md` (D-CAPRPC v0 posture: live refs stay explicit/connection-specific/session-scoped, disconnect is fail-stop, continuity requires explicit CH-CAPX/CH-SREF restore, no public session/object inventory or transparent resume surface).
CapRPC promise seam: `docs/30-architecture/caprpc-promise-posture-v0.md` (D-CAPRPC v0 adjunct: caller-local/session-scoped one-shot promise handles, capability-result-only pipelining, deterministic broken-promise/disconnect outcomes, no promise inventory/combinator/admin surface).
CapRPC oneway seam: `docs/30-architecture/caprpc-oneway-posture-v0.md` (D-CAPRPC v0 adjunct: interface-marked oneway only, no third CH-CAPRPC frame kind, enqueue-or-error semantics, payload <= 256 bytes, zero capability attachments, no durable backlog/mailbox surface).
Capability-delegation seam: `docs/30-architecture/capx-posture-v0.md` (D-CAPX v0: gateway-owned, proxy-first import only; no raw-cap binding, no ambient resolver or token inventory, no portable caveat VM on the core seam).
Local naming/delegation seam: `docs/30-architecture/namecert-posture-v0.md` (D-NAMECERT v0: issuer-local naming evidence only; user-space evaluator, no ambient resolver/fetch, no portable policy VM, no automatic view install).
Namecert projection boundary: `docs/30-architecture/namecert-projection-boundary-v0.md` (Phase 1 authority-bearing materialization is explicit `view.attach` / `view.detach` per `view.slot`; source `digest(CH-NAMECERT v0)` evidence stays visible; no bulk install/watch-sync path).
Namecert time boundary: `docs/30-architecture/namecert-time-boundary-v0.md` (CH-NAMECERT validity/freshness only gates explicit admission decisions; live `view.slot` bindings do not auto-detach on expiry or timeproof updates, and any removal stays an explicit target-seam action).
Namecert revocation boundary: `docs/30-architecture/namecert-revocation-boundary-v0.md` (later negative evidence stays evaluator-local and admission-scoped; no ambient CRL/OCSP or latest-wins semantics, and no automatic `view.detach` when revocation is learned).
Namecert selection boundary: `docs/30-architecture/namecert-selection-boundary-v0.md` (Phase 1 evaluation is set-valued; multiple admissible candidates never trigger a hidden winner-selection rule, and any live binding must identify the exact chosen candidate with retained `digest(CH-NAMECERT v0)` provenance).
Namecert search boundary: `docs/30-architecture/namecert-search-boundary-v0.md` (Phase 1 evaluation is closed-world over one explicit CH-NAMECERT bundle set: bounded local search only, no suspend/resume distributed credential discovery, deterministic cycle handling, and fail-closed bound exhaustion).
Namecert redelegation boundary: `docs/30-architecture/namecert-redelegation-boundary-v0.md` (Phase 1 delegated subjects do not implicitly gain onward delegation power; CH-NAMECERT v0 carries no propagate-bit/depth semantics, so multi-hop delegation chains reject unless each issuer is independently authorized).
Namecert trust-root boundary: `docs/30-architecture/namecert-trust-root-boundary-v0.md` (trust anchors stay explicit evaluator-local input; CH-NAMECERT is not itself a trust root, replicated bundles cannot auto-install anchors, and trust-policy changes only affect future admissions rather than live `view.slot` bindings).
Namecert normal-form boundary: `docs/30-architecture/namecert-normal-form-boundary-v0.md` (admitted CH-NAMECERT bundles use duplicate-free strictly sorted `bindings` / `delegations` arrays; statement order and repetition are non-authoritative, so there is no first/last-match or weighted-duplicate semantics).
Namecert string profile boundary: `docs/30-architecture/namecert-string-profile-v0.md` (Phase 1 `Binding.name` / `Delegation.role` labels are exact-byte lowercase ASCII identifiers only; no Unicode/PRECIS/case-folding/confusable policy seam is imported onto D-NAMECERT).
Namecert label-atom boundary: `docs/30-architecture/namecert-label-atom-boundary-v0.md` (Phase 1 admitted labels are single opaque atoms after validation: `.` / `_` / `-` remain ordinary bytes, and D-NAMECERT imports no hierarchy, wildcard, prefix/suffix, or path grammar onto `Binding.name` / `Delegation.role`).
Namecert principal profile boundary: `docs/30-architecture/namecert-principal-profile-v0.md` (Phase 1 `PrincipalRef` identities are hash-only and canonical: admitted bundles accept only `kind="key_hash"`, `alg="cose_key_thumbprint_sha256"`, exact 32-byte thumbprints, and reject raw `kind="pubkey"` admissions).
Namecert signature profile boundary: `docs/30-architecture/namecert-signature-profile-v0.md` (Phase 1 admitted bundles use exactly one inline direct Ed25519 signature over the canonical unsigned bundle bytes; wrapper-only, keyless/X.509, and multisig admissions are all out of scope).
Namecert metadata boundary: `docs/30-architecture/namecert-metadata-boundary-v0.md` (`bundle_id` and `created_ms` are signed provenance only in Phase 1: no latest-bundle-wins, implicit replacement lineage, or metadata-driven freshness/obsolescence semantics).
Namecert bearer boundary: `docs/30-architecture/namecert-bearer-boundary-v0.md` (Phase 1 admitted CH-NAMECERT bundles are never bearer-cap transport: raw CH-SREF / CH-CAPX / raw capability material is forbidden, `TargetRef.kind="sturdyref"` is reserved+rejected, and capability import stays on explicit D-CAPX / CH-SREF seams).

Privilege-bracketing seam: `docs/30-architecture/bracket-posture-v0.md` (D-BRACKET / CH-CALLCHAIN v0: borrowed-mode default, task/request-local dynamic scope, explicit exception-safe privileged blocks, bounded optional call-chain metadata, no portable stack inspection or new workflow/ACP surface).

Ordering witness seam: `docs/30-architecture/ordering-token-posture-v0.md` (CH-ORDERTOK / D-COMMUTE v0: one conflict-key stream, owner-minted witness, no portable sequencer/range-allocation/global-stream surface).

Workflow router seam: `docs/30-architecture/plumb-posture-v0.md` (D-PLUMB v0: explicit invocation only, request-local completion, no durable inbox/outbox, no callback registry, no app-visible handler/route inventory).

Portal request/session seam: `docs/30-architecture/portal-session-posture-v0.md` (D-PLUMB v0: provider-owned request/session objects, one terminal outcome, family-local live sessions only, no generic resume/list/watch/callback surface).

Consent-mediator seam: `docs/30-architecture/powerbox-posture-v0.md` (D-POWERBOX v0: designation-scoped, chooser-owned mediation; concrete capability results only; no generic remembered-grant library, inventory oracle, or callback/path result surface).

Quiesce seam: `docs/30-architecture/quiesce-posture-v0.md` (D-QUIESCE v0: cooperative component-local control, one active qid, `DRAIN|CANCEL` only, no force-kill/global freeze semantics, no new workflow/ACP surface).

Read-mostly concurrency seam: `docs/30-architecture/rcu-posture-v0.md` (D-RCU v0: QSBR-first, per-subsystem/user-space GraceDomains, no ambient/global collector, no new workflow/ACP surface).

Wait-on-address seam: `docs/30-architecture/uwait-posture-v0.md` (D-UWAIT v0: process-local only, aligned 32-bit wait word, wait+wake only, no requeue/PI/workflow surface).
Owner-death seam: `docs/30-architecture/robustlock-posture-v0.md` (D-ROBUSTLOCK v0: runtime-owned per-thread RobustSet, mutex-only, component-local, explicit `OWNER_DIED` / `NOT_RECOVERABLE`, no new workflow/ACP surface).
CPU-local fast-path seam: `docs/30-architecture/rseq-posture-v0.md` (D-RSEQ v0: runtime-owned single-slot thread registration, no ambient `getcpu`/topology oracle, explicit abort-to-slow-path, no new workflow/ACP surface).

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
- Preferred: `make handoff-release STAMP=YYYY.MM.DD.HH.MM SLUG=<slug>` runs the canonical end-to-end handoff path in one command: regenerate `out/context_pack.md`, run `make lint`, then build the canonical verified zip via `make package-release ...`.
- Optional: `make package-release STAMP=YYYY.MM.DD.HH.MM SLUG=<slug>` creates the canonical `SlopOS-rev####-...-<slug>.zip` handoff archive from the top `CHANGELOG.md` revision, refuses a stale `out/context_pack.md` unless both its header and its `## New in latest revision` bullets still mirror that top changelog entry, embeds a fresh `RELEASE-MANIFEST.json`, ignores any extracted residue copy in the workspace, normalizes member metadata to the packaging timestamp, excludes `out/_ci_*` scratch files, and self-verifies the produced bundle before reporting success.
- Optional: `make verify-release BUNDLE=/abs/path/to/SlopOS-rev####-YYYY.MM.DD.HH.MM-<slug>.zip` verifies the produced bundle against its embedded `RELEASE-MANIFEST.json`, canonical filename shape, file digests/sizes, and normalized zip metadata before handoff.
