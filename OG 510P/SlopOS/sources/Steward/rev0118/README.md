# Steward living archive

**One-line summary:** Steward is SlopOS's component lifecycle and activation fabric, keeping services explicit, restartable, and policy-bounded without ambient Unix folklore.

Revision notes: [`CHANGELOG.md`](CHANGELOG.md)

This repo is a **living archive** for designing Steward while SlopOS itself is still in design. The goal is to preserve the best parts of the SlopOS datacube discipline—explicit claims, source locks, context packs, packaged revisions, and narrow posture docs—without prematurely freezing a giant service-manager worldview.

## How to navigate
0. Mile-high map: [`docs/00-meta/trajectory-map.md`](docs/00-meta/trajectory-map.md)
0.5 Editing runbook: [`docs/00-meta/llm-runbook.md`](docs/00-meta/llm-runbook.md)
1. Threat model: [`docs/10-threat-model/`](docs/10-threat-model/)
2. Assurance: [`docs/20-assurance/`](docs/20-assurance/)
3. Architecture: [`docs/30-architecture/`](docs/30-architecture/)
4. Research / inspirations: [`docs/90-inspirations/`](docs/90-inspirations/)
5. Decisions: [`adrs/`](adrs/) and proposals: [`rfcs/`](rfcs/)

## Current posture
- Steward is **not** a systemd clone.
- Steward keeps the **component run** public and leaves host process-group / job-object / cgroup machinery under the membrane.
- Steward is **not yet** a final architecture; it is a research-and-posture archive with a small set of deliberately chosen seams.
- Phase 1 emphasis is on:
  - explicit component identity,
  - foreground, accountable lifecycle roots,
  - supervisor-owned activation,
  - exact request-carried activation where the first meaningful request may wake a component without turning Steward into a giant bus or focus-control plane,
  - optional exact-run observation tricks under the membrane so runtime-cycle witnesses can be backed by non-reused host handles where available without making those handles the public contract,
  - optional exact orphan-adoption and execution-group tricks under the membrane so supervisors can keep accountability for descendant work without freezing subreapers, job objects, or cgroup paths into the public contract,
  - tiny exact request-context semantics so activation, chooser detours, and automation can carry optional deadlines and explicit cancellation without a giant RPC metadata plane,
  - exact closeable grant handles for live transient powers such as pending requests, stop deferral, capture, or shortcut sessions instead of sticky ambient mode bits,
  - optional compact effect-key semantics so reviewed non-commutative actions may collapse duplicate retries, surface mismatch honestly, and stay smaller than a durable exactly-once plane,
  - optional compact retry-advice semantics so denials, cooldowns, or explicit pushback may carry exact earliest-follow-up hints without freezing a quota or giant retry-policy family,
  - optional exact precondition-witness semantics so reviewed actions can stale-fence themselves against wrong-cycle, stale-anchor, or moved-epoch drift without ambient latest-lookups,
  - optional compact consumable-grant semantics so some transient powers can be spent by use and become visibly `consumed` instead of replayable from stale history,
  - optional compact attenuated-grant semantics so an exact live grant may derive a narrower helper or follow-on grant without exposing the parent raw or freezing a generic token-exchange/delegation plane,
  - optional compact holder-bound-grant semantics so some exact live grants can require current holder proof instead of behaving like replayable bearer history,
  - optional compact fresh-intent witness semantics so some higher-risk or foreground-sensitive actions can require recent local one-shot intent evidence instead of replayable history or ambient automation,
  - explicit denial/delay reasons with optional retry-after / try-again-at hints so the shell can show honest countdown rails without guessing from hidden cooldown policy,
  - optional compact renewal-window semantics so live claims can expire, renew, or degrade honestly without a giant portable watchdog or lease plane,
  - optional exact fence-token semantics so reassignable live claims can reject stale holders without freezing a distributed lock, leader-election, or global sequencer plane,
  - request-carried activation may include freshness-scoped attention or activation tokens, but those remain advisory, one-shot, and clearly separate from lifecycle truth,
  - explicit non-ambient launch context so restartable services do not depend on login-shell or session folklore,
  - explicit launch-boundary crossing so handles, startup material, and helper-shell context stay held-here unless a reviewed launch or activation path selects them for child delivery,
  - explicit authority narrowing with visible configuring-versus-locked state so reviewed allowlists or delivered capabilities can reduce ambient authority without a giant sandbox DSL,
  - deterministic restart and stop semantics,
  - lifecycle observations, compact status, bounded subscription views that stay separate from logs, and optional exact observation cursors so shells/UIs can resume or admit continuity loss honestly,
  - explicit readiness, narrow activity accounting, bounded stop deferral, and cooperative quiesce,
  - bounded continuity escrow,
  - optional tiny continuity-escrow truth so preserved/redelivered continuity can stay separate from runtime-cycle identity, serving state, and takeover proof,
  - optional tiny liveness-evidence semantics so watchdog/probe/check-in truth can stay separate from readiness, useful work progress, and later repair policy,
  - explicit activation receipts so delivered startup material and any acknowledgement barrier stay exact-run-scoped instead of dissolving back into descriptor or wrapper folklore,
  - explicit named activation material so delivered startup objects are keyed, receipted, and restartable without descriptor-order folklore,
  - shell/terminal integration that uses semantic side channels rather than PTY folklore,
  - command-frame observations with explicit trust/confidence rather than buffer-guess magic,
  - optional runtime-cycle witnesses for correlating concrete runs and avoiding stale shell actions,
  - compact end-of-cycle / termination-cause observations that explain why a concrete run ended without a giant host-specific failure API,
  - explicit repeated-failure cooldown / repair-gate semantics so crash loops become visible and bounded instead of ambient retry folklore,
  - explicit precision fences so shell/terminal affordances can admit when hops or fallback paths downgraded what they really know,
  - explicit capability handshakes so richer shell/terminal features come from fresh observed support instead of `TERM` folklore,
  - explicit shell/terminal hop lineage so remote-aware semantics stay scoped to the actual path instead of collapsing into flat PTY folklore,
  - explicit provisional-state semantics so predictive local echo, incomplete frame metadata, and later refinements can stay useful without masquerading as confirmed lifecycle truth,
  - explicit attention hints so command-finished, needs-input, warning, and progress-like shell/terminal cues can stay user-filterable, freshness-scoped, and non-authoritative,
  - explicit notification surfaces so OS toasts, mark-alert wakeups, and exact reveal actions stay focus-aware, anchor-bound, and action-bounded instead of becoming a hidden approval path,
  - explicit approval rungs so proposal-only help, ask-before-run, scoped auto-approval, and run-until-completion stay visibly different powers instead of one ambient automation mood,
  - explicit exception witnesses so bypass-under-review, waived-under-expiry, and satisfied-gate truth stay visibly different instead of flattering one-off exceptions into ordinary success,
  - explicit preflight lanes so explain, diff, speculative preview, reviewed saved plan, and apply stay visibly different moves instead of ambient dry-run folklore,
  - explicit revision-settlement truth so reviewed desired revision, observed revision, and last settled/stable revision do not collapse into one flattering updated bit,
  - explicit headroom witnesses so allowed, approved, and ready stay visibly separate from currently spendable restart / quota / rate-window headroom,
  - explicit serve-state witnesses so `serving`, `serving+terminating`, `draining`, `maintenance`, `degraded`, and `not serving` stay visibly separate from process liveness, readiness folklore, and discoverability,
  - explicit pressure witnesses so scoped `ok` / `some` / `full` / `warning` / `critical` pressure truth can stay visibly separate from serving mode, headroom, and failure,
  - explicit backpressure witnesses so `queued`, `retry-after`, `shed`, and `stop-accepting` truth can stay visibly separate from pressure, headroom, and failure,
  - explicit adaptation witnesses so cache trim, reduced concurrency, optional-work deferral, and other protective response truth can stay visibly separate from pressure, backpressure, and vague degraded folklore,
  - explicit target anchors so shell/terminal affordances can bind to exact frames, receipts, transcript spans, and concrete runs without visible-text scraping or raw-capability leakage,
  - explicit command-guide semantics so visible rails, sticky headers, and prompt-local command chrome stay exact-object-backed, filterable, and clearly separate from the canonical transcript,
  - explicit transcript landmarks so marks, annotations, alerts, and exact jump targets stay anchor-bound, provenance-labeled, and clearly separate from transcript truth or ambient control,
  - explicit context inheritance so tabs, splits, reruns, and action-launched shells can inherit cwd or domain context per action without ambient pane folklore,
  - explicit spawn selectors so tabs, splits, reruns, and helper shells can choose reviewed program/profile/domain/cwd recipes instead of ambient `$SHELL` or profile folklore,
  - explicit remembered shelves so recent commands, directories, and Steward objects remain keyed, freshness-labeled, and clearly separate from live state truth,
  - explicit retention surfaces so persisted command/directory/paste/host memory stays scopeable, erasable, and clearly remembered instead of becoming ambient retained authority,
  - explicit workspace snapshots so saved layouts, restored panes, reconnected processes, revived processes, and content-only restores stay visibly distinct instead of collapsing into session folklore,
  - explicit replay gates so remembered, restored, or suspended commands can reopen as reviewed pending actions instead of silently rerunning from stale shell folklore,
  - explicit chooser surfaces so file pickers, visible-text selectors, and context pickers can return exact reviewed targets or selectors instead of ambient pasted-text folklore,
  - explicit assist surfaces so quick fixes, suggestion menus, and current-input help stay advisory, anchored, and policy-bounded instead of becoming an ambient second shell,
  - explicit surface diagnostics so shell/terminal affordances can explain why they are enabled, degraded, denied, or stale instead of behaving like magic,
  - explicit bounded context handoff so exact command frames, output slices, receipts, and concrete runs can be attached or exported without ambient whole-scrollback sharing,
  - explicit transfer surfaces so uploads, downloads, remote-file actions, and drag/drop handoff stay reviewed, direction-labeled, and clearly separate from pasted shell text or ambient cwd folklore,
  - explicit media surfaces so inline images, plots, doc previews, and background media stay exact-targeted, budgeted, and clearly separate from transfer/open folklore,
  - explicit link surfaces so detected text, declared hyperlinks, semantic file links, and exact object opens stay provenance-labeled, action-bounded, and clearly separate from generic open folklore,
  - explicit label surfaces so titles, badges, right-status text, and similar chrome labels stay provenance-labeled, override-scoped, and clearly separate from transcript or policy truth,
  - explicit automation surfaces so scripts, hooks, remote-control APIs, and helper CLIs stay exact-targeted, permissioned, and inspectable instead of becoming an ambient second control plane,
  - explicit input surfaces so key events, composed text, armed-versus-active capture, modal key tables, prompt-local affordances, and injected bytes stay distinct, inspectable, and policy-bounded instead of becoming timing-hack folklore,
  - explicit repair-gate semantics so repeated failures can cool down, become repair-required, and stay explainable without a giant retry-policy language.

## Archive discipline
- Cite external work with **reference IDs** from [`docs/00-meta/bibliography.md`](docs/00-meta/bibliography.md).
- Register local evidence/process artifacts as **evidence IDs** in [`docs/00-meta/evidence-index.md`](docs/00-meta/evidence-index.md).
- Prefer **posture docs and open questions** over prematurely multiplying detailed singleton docs.
- Keep `out/context_pack.md` fresh using `make context-pack`.
- Refresh the external-source review queue using `make source-review-queue`.
- Ship revisions using `make handoff-release STAMP=YYYY.MM.DD.HH.MM SLUG=<slug>`.

## What the latest revision adds
- a new adaptation-witness posture so cache trim, reduced concurrency, optional-work deferral, and other protective responses stay visibly different instead of collapsing into one vague degraded bit,
- deeper research around pressure-versus-adaptation honesty, protective-response patterns from Envoy/systemd/Fuchsia/Kubernetes, SlopOS D-PRESSURE alignment, and terminal adaptation receipts,
- refreshed repo hygiene through updated note-level synthesis, regenerated review/context artifacts, linting, and a clean packaged release.
