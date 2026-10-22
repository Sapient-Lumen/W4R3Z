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
4. Verification: [`docs/40-verification/`](docs/40-verification/)
5. Research / inspirations: [`docs/90-inspirations/`](docs/90-inspirations/)
6. Decisions: [`adrs/`](adrs/) and proposals: [`rfcs/`](rfcs/)

## Current posture
- Steward is **not** a systemd clone.
- Steward keeps the **component run** public and leaves host process-group / job-object / cgroup machinery under the membrane.
- Steward is **not yet** a final architecture; it is a research-and-posture archive with a small set of deliberately chosen seams.
- Phase 1 emphasis is on:
  - explicit component identity,
  - foreground, accountable lifecycle roots,
  - supervisor-owned activation,
  - exact request-carried activation where the first meaningful request may wake a component without turning Steward into a giant bus or focus-control plane,
  - explicit activation admission so one exact wake/start/demand attempt can be admitted, denied, deferred, narrowed, throttled, shed, or unknown without pretending execution or service happened,
  - explicit activation-demand episodes so a cold-start request can be accepted, buffered, delivered, timed out, canceled, or shed without pretending the component was already running, ready, or serving,
  - explicit activation-custody witnesses so the system can say who currently holds one activation demand, event, descriptor, or background obligation, whether handoff was acknowledged, and whether cancellation, expiry, redelivery, or duplicate risk exists without claiming completion,
  - explicit activation-work disposition witnesses so admitted work can end as acknowledged, redeliverable, redelivered, expired, dead-lettered, discarded, abandoned, detached, superseded, or unknown without pretending admission, custody, restart, readiness, or serving means completion,
  - explicit activation-effect boundary witnesses so work disposition, retry, redelivery, and idempotency can stay separate from local commit, outbox record, external submit, external confirmation, compensation, irreversible side effects, and unknown effect fate,
  - explicit activation-incarnation lineage witnesses so stable component identity, concrete runtime cycles, predecessor/successor overlap, hot-restart drain, replacement, clone/restore, and stale-action fences do not collapse into recycled names or PID folklore,
  - explicit activation-residency witnesses so placement, nomination, warm idle, frozen/snapshotted, restore-in-progress, eviction, loss, and unknown residency stay separate from identity, readiness, serving, custody, work fate, and effects,
  - explicit activation-state attachment witnesses so scratch space, projected material, runtime/state directories, sticky volumes, persistent storage, snapshot-derived bytes, cleanup, and detach truth do not masquerade as readiness, currentness, custody, work fate, or effect success,
  - explicit activation-material freshness witnesses so config, secrets, tokens, trust bundles, leases, and snapshot-restored material can say whether they are version-pinned, projected, static-for-incarnation, renewable, expired, revoked, reload-pending, reacquire-required, or unknown without becoming a vault or config plane,
  - explicit activation-probe vantage witnesses so startup, readiness, liveness, gRPC health, balancer, mesh, and outside-in checks can say who probed what, from where, with what scope and freshness, without turning one green/red result into service truth,
  - explicit activation-control verdict witnesses so controllers, balancers, rollout loops, DNS-health systems, deployment circuit breakers, and operator adapters can expose issuer, scope, basis, freshness, and effect class without turning observations into automatic policy action,
  - explicit activation-traffic binding witnesses so route, alias, service, gateway, proxy, DNS, target-group, and test-tag surfaces can show desired/observed/applied, weighted, sticky, mirrored, draining, stale, or unknown new-demand mapping without becoming a load balancer, mesh, or rollout controller,
  - explicit activation-live channel witnesses so existing connections, streams, subscriptions, watches, WebSockets, server-sent event streams, multiplexed RPCs, and drainable message clients can show holder, layer, no-new-work fence, drain deadline, close/reset fate, cursor/resume hints, gap ambiguity, and force-close truth without becoming route binding, readiness, custody, work disposition, or effect truth,
  - explicit activation-retry attempt witnesses so retries, replays, transparent retries, hedges, reconnect resends, and post-drain attempts can show original demand, canonical-intent match, safety basis, pushback/backoff, budget, commitment boundary, and duplicate ambiguity without becoming an RPC framework, retry engine, or exactly-once plane,
  - explicit retry-settlement witness packets so retry advice, retry budgets, retry attempts, and hedge fates can be checked without confusing not-before hints, local quota, response winners, duplicate ambiguity, or commitment boundaries with success, safety, or exactly-once effects,
  - explicit activity-accounting packets so activity brackets, idle hints, stop deferral, and usage accounting can be checked without confusing in-flight work, idleness, stop grace, or meters with readiness, serving, drain, billing, work completion, or effect success,
  - explicit governance authorization packets so lifecycle delegation warrants, request reviews, approval decisions, and authorization checks can stay separate from owner labels, operation receipts, component state, and effect success,
  - explicit rollout-generation packets so generation plans, reconfiguration apply attempts, scoped generation readiness, and promotions/rollbacks can stay separate from material freshness, reload success, serving, drain, work completion, rollback success, and external effect truth,
  - explicit receipt-transport packets so receipt chains, redaction commitments, export bundles, and replay observations can support recovery and handoff without becoming authority, current state, freshness, complete history, or effect success,
  - explicit local-observation provenance packets so host-manager, orchestrator, runtime, shell, watcher, cursor, and adapter observations can support explanation and recheck without becoming native currentness, readiness, serving, authority, execution, drain, or effect success,
  - explicit witness-surface packets so rendered cards, action affordances, status barriers, and surface audits preserve non-implications instead of turning weak evidence into readiness, currentness, authorization, execution, release, or effect success,
  - executable proof-slice checks for CH-COMP, CH-ACTSET, activation receipts, restart replay, stale-cycle fences, stop/quiesce boundaries, adapter weakness, retry intent matching, and effect-boundary separation,
  - executable control-operation request/receipt checks for exact targets, stale-cycle fences, idempotency-key widening, receipt/request digest binding, operation-result non-implications, and manager-recovery downgrade,
  - executable route/channel witness checks for traffic-binding and live-channel packets, route-as-readiness rejection, no-new-work versus existing-channel separation, channel-as-effect-success rejection, resume gap ambiguity, endpoint redaction, and bounded drain-deadline truth,
  - executable work-path witness checks for ST-DEMAND, ST-CUSTODY, ST-WORKDISP, and ST-EFFECT packets, accepted-demand-as-work-complete rejection, custody-as-effect-success rejection, local-completion-as-effect-success rejection, effect-before-work rejection, same-effect-key mismatch rejection, retention-window inversion rejection, and exactly-once flattery rejection,
  - executable currentness/control witness checks for ST-STATEATT, ST-MATFRESH, ST-PROBE, and ST-CTRLVERDICT packets, attachment-as-freshness rejection, freshness-as-reload rejection, probe-pass-as-serving rejection, verdict-as-route-authority rejection, stale-material traffic-gate rejection, raw path/secret redaction, and duplicate-key rejection,
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
  - lifecycle observations, compact status, optional exact status barriers for crossing manager/shell currentness boundaries honestly, bounded subscription views that stay separate from logs, and optional exact observation cursors so shells/UIs can resume or admit continuity loss honestly,
  - explicit readiness, narrow activity accounting, bounded stop deferral, and cooperative quiesce,
  - bounded continuity escrow,
  - optional tiny continuity-escrow truth so preserved/redelivered continuity can stay separate from runtime-cycle identity, serving state, and takeover proof,
  - optional tiny liveness-evidence semantics so watchdog/probe/check-in truth can stay separate from readiness, useful work progress, and later repair policy,
  - explicit activation receipts so delivered startup material and any acknowledgement barrier stay exact-run-scoped instead of dissolving back into descriptor or wrapper folklore,
  - explicit named activation material so delivered startup objects are keyed, receipted, and restartable without descriptor-order folklore,
  - explicit tiny wake-memory witnesses so alarms, reminders, queued triggers, and hibernated/inactive continuity can explain later wake without pretending the component is currently running, ready, or current,
  - shell/terminal integration that uses semantic side channels rather than PTY folklore,
  - optional exact output-slice objects so `copy output`, `select output`, `attach last failure`, and exact handoff can bind to one bounded region instead of nearby-text folklore,
  - optional exact command-verdict objects so one exact command result can drive decorations, reveal/watch UX, and `attach last failure` selection without smearing together exit code, output, and transcript guesswork,
  - optional exact command-evidence bundles so `attach last failure`, `share this exact command interaction`, and proposal/chat escalation can package one bounded command interaction without whole-scrollback export,
  - optional exact evidence-draft objects so one outbound reviewed subset can be trimmed, masked, or lightly annotated before attach / share without mutating the source evidence,
  - optional exact current-command objects beside live prompt leases so reveal / assist / copy / diff can bind to what is truly being edited without pane-wide guessing,
  - optional exact injection-receipt objects so reviewed insert / replace / env-load actions can leave one exact shell-visible receipt over what changed without pretending execution already happened,
  - optional exact command-patch objects so repair / assist / history-backed rewrites can stage one reviewable mutation over one stronger command anchor without ambient fix-up magic,
  - optional exact detour-outcome objects so chooser/open/auth/approval completions can return one typed shell-visible result without mistaking pending requests, live grants, or return tickets for the same truth,
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
  - explicit component-shell entry so `shell into this exact component scope` stays a reviewed, expiring helper action distinct from attach, control, and debugger folklore,
  - explicit remembered shelves so recent commands, directories, and Steward objects remain keyed, freshness-labeled, and clearly separate from live state truth,
  - explicit retention surfaces so persisted command/directory/paste/host memory stays scopeable, erasable, and clearly remembered instead of becoming ambient retained authority,
  - explicit workspace snapshots so saved layouts, restored panes, reconnected processes, revived processes, and content-only restores stay visibly distinct instead of collapsing into session folklore,
  - explicit replay gates so remembered, restored, or suspended commands can reopen as reviewed pending actions instead of silently rerunning from stale shell folklore,
  - explicit chooser surfaces so file pickers, visible-text selectors, and context pickers can return exact reviewed targets or selectors instead of ambient pasted-text folklore,
  - explicit assist surfaces so quick fixes, suggestion menus, and current-input help stay advisory, anchored, and policy-bounded instead of becoming an ambient second shell,
  - explicit repair-card seams so failed or blocked commands/components can surface reviewable likely-next-fix cards with exact anchors, disabled reasons, and honest downgrade instead of transcript folklore or auto-remediation,
  - explicit state-explainer seams so exact frames, runs, requests, or repair gates can answer why something is waiting, blocked, repair-required, or rebind-required without becoming a diagnosis empire,
  - explicit surface diagnostics so shell/terminal affordances can explain why they are enabled, degraded, denied, or stale instead of behaving like magic,
  - explicit bounded context handoff so exact command frames, output slices, receipts, and concrete runs can be attached or exported without ambient whole-scrollback sharing,
  - explicit transfer surfaces so uploads, downloads, remote-file actions, and drag/drop handoff stay reviewed, direction-labeled, and clearly separate from pasted shell text or ambient cwd folklore,
  - explicit media surfaces so inline images, plots, doc previews, and background media stay exact-targeted, budgeted, and clearly separate from transfer/open folklore,
  - explicit link surfaces so detected text, declared hyperlinks, semantic file links, and exact object opens stay provenance-labeled, action-bounded, and clearly separate from generic open folklore,
  - explicit label surfaces so titles, badges, right-status text, and similar chrome labels stay provenance-labeled, override-scoped, and clearly separate from transcript or policy truth,
  - explicit automation surfaces so scripts, hooks, remote-control APIs, and helper CLIs stay exact-targeted, permissioned, and inspectable instead of becoming an ambient second control plane,
  - explicit input surfaces so key events, composed text, armed-versus-active capture, modal key tables, prompt-local affordances, and injected bytes stay distinct, inspectable, and policy-bounded instead of becoming timing-hack folklore,
  - explicit paste-firewall semantics so pasted payloads can be previewed, staged, literalized, or denied with visible reasons instead of masquerading as typed fresh intent or being silently rewritten,
  - explicit repair-gate semantics so repeated failures can cool down, become repair-required, and stay explainable without a giant retry-policy language.

## Archive discipline
- Cite external work with **reference IDs** from [`docs/00-meta/bibliography.md`](docs/00-meta/bibliography.md).
- Register local evidence/process artifacts as **evidence IDs** in [`docs/00-meta/evidence-index.md`](docs/00-meta/evidence-index.md).
- Prefer **posture docs and open questions** over prematurely multiplying detailed singleton docs.
- Keep `out/context_pack.md` fresh using `make context-pack`.
- Refresh the external-source review queue using `make source-review-queue`.
- Ship revisions using `make handoff-release STAMP=YYYY.MM.DD.HH.MM SLUG=<slug>`.

## What the latest revision adds
- Added closed ST-DEPSPEC v0, ST-DEPCHECK v0, ST-DEPGATE v0, and ST-DEPFALLBACK v0 schema profiles for scoped dependency declarations, dependency condition checks, dependency-informed lifecycle request gates, and fallback/degraded-mode witnesses.
- Added deterministic dependency-gate corpus plus `tools/steward_dependency_gate_harness.py`, wired through the shared harness registry, covering topology-authority flattery, dependency-as-readiness rejection, stale dependency checks, gate-as-execution rejection, allow-with-unavailable-hard-dependency, degrade-without-active-fallback, spec/check mismatch, fallback-as-repair rejection, and duplicate gate-id drift.
- Added dependency-gate proof posture and human packet specs so dependency facts explain lifecycle gating without becoming topology authority, start order, readiness, serving, component failure, operation execution, work completion, repair, rollback success, or effect truth.
- Audited and refactored verification-index maintenance: added `tools/gen_verification_readme.py`, a `verification-readme` Makefile target, handoff-release regeneration, and a lint guard proving `docs/40-verification/README.md` exactly matches the harness-registry-generated output instead of being manually maintained.
- Updated schema/interface registries, verification docs, minimum proof slice, assurance registries, traceability, roadmap, trajectory map, decision map, non-claims, tools/schema/verification indexes, README, changelog, and context pack for the new dependency-gate proof slice and audit/refactor pass.
