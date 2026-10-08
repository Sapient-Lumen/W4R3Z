# Architecture decisions

## ADR-001 — Open, inspectable behavior beats opaque convenience

**Decision:** Design for inspectability first.

**Why:** The strongest non-Resilio reason to build AnonSync is to make peer-to-peer sync more auditable and controllable.

**Implications:**

- documented protocol and schemas
- stable machine-readable state
- explicit diagnostics
- fewer hidden heuristics

## ADR-002 — Device identities are durable; linking never overwrites them

**Decision:** A device keeps its identity unless the local operator explicitly rotates or replaces it through recovery workflows.

**Why:** Resilio's documented linking behavior shows that certificate takeover can be destructive and confusing.

**Implications:**

- linking creates relationships, not mergers
- conflict resolution must be explicit
- share state cannot be silently rebound to a new certificate

## ADR-003 — Materialization state is first-class

**Decision:** Every mount/share pairing exposes a materialization mode.

**Modes:**

- `detached`
- `selective`
- `full`

**Why:** This is one of Resilio's genuinely strong product insights and should be preserved.

## ADR-004 — Encrypted-untrusted replicas are a v1 feature, not a someday add-on

**Decision:** Support encrypted-replica peers early.

**Why:** This is strategically differentiating, operationally useful, and aligned with the product thesis.

**Implications:**

- permissions must include `encrypted-replica`
- status tooling must distinguish plaintext and ciphertext holders
- fetch logic must explain when only encrypted copies exist

## ADR-005 — Placeholder semantics are optional, not foundational

**Decision:** Do not make cross-platform placeholder files the basis of v1.

**Why:** Placeholder implementation details can consume disproportionate complexity and obscure the real product value.

**Implications:**

- support virtual and sidecar strategies first
- add native placeholder integrations later where they are robust

## ADR-006 — Start with personal/small-team scope

**Decision:** Ignore enterprise fleet scope for now.

**Why:** Wide deployment support and central management can easily dominate the roadmap and bury the core product insight.

**Implications:**

- no centralized multi-tenant admin plane in v1
- no huge-job distribution story yet
- better local operator experience first

## ADR-007 — Strong diagnostics are part of the product, not support work

**Decision:** `status`, `events`, and `doctor` are first-class surfaces.

**Why:** Sync products fail hardest when users cannot tell what is happening.

**Implications:**

- the daemon tracks explanation-rich transfer states
- every blocked sync has a reason string
- the UI/TUI can be built atop the same event stream

## ADR-008 — Discovery/relay behavior is policy, not a hidden advanced setting

**Decision:** Tracker, relay, LAN discovery, known-host controls, and endpoint cache management are explicit policy objects.

**Why:** Resilio's official docs show that transport behavior materially changes privacy, reachability, and operator expectations.

**Implications:**

- shares can bind to named discovery policies
- status must show the effective path used
- LAN-only operation becomes a normal supported workflow

## ADR-009 — Linked devices do not imply owner authority by default

**Decision:** Device linking and share ownership are separate concepts.

**Why:** Resilio's linked-device model is convenient, but too broad for a system that wants auditable trust boundaries.

**Implications:**

- share grants remain explicit objects
- linked-device auto-grants are opt-in policy
- admin authority can be reviewed independently of personal-device membership

## ADR-010 — Recovery must be explicit; cloning is not the workflow

**Decision:** Support backup/export/import/replacement flows, but do not rely on opaque disk cloning.

**Why:** Operators still need hardware replacement and disaster-recovery workflows, and unsupported cloning is an unsatisfying answer.

**Implications:**

- explicit backup and recover commands
- trust reconciliation paths
- auditable identity rotation and replacement events

## ADR-011 — API and CLI are two views of one object model

**Decision:** The local daemon API is a first-class surface, not a private implementation detail.

**Why:** Resilio's split across UI/config/startup flags is precisely the kind of fragmentation AnonSync should avoid.

**Implications:**

- future UI/TUI must consume the same events and objects
- config import/export maps to the same schema family
- machine users are not second-class users

## ADR-012 — “Easy mode” behaviors must decompose into explicit policies

**Decision:** Convenience features such as linking, auto-grants, or default selective mounts must compile to inspectable policy objects.

**Why:** Hidden convenience is where trust expansion becomes hard to audit.

**Implications:**

- every auto-grant has provenance
- users can list and revoke policy-derived grants
- defaults are explainable and reversible

## ADR-013 — Observability and audit are part of the control plane

**Decision:** Expose metrics, audit, route selection, and health summaries through supported CLI/API surfaces.

**Why:** A sync product that only exposes raw logs leaves operators reconstructing the system model by hand.

**Implications:**

- `status`, `doctor`, `audit`, and `metrics` are supported interfaces
- route/cache state must be inspectable without debug builds
- security-relevant changes must leave machine-readable audit entries

## ADR-014 — High-signal mutations use plan/apply with drift detection

**Decision:** Trust-expanding, recovery-rebinding, or multi-object mutations should prefer explicit plan objects that are reviewed and then applied against checked preconditions.

**Why:** A plain `dry-run` is useful, but not strong enough when the world may change between preview and execution.

**Implications:**

- plan objects become part of the public object model
- applies can fail safely on drift instead of guessing intent
- audit can record both reviewed intent and executed change

## ADR-015 — Capability differences must be explicit and queryable

**Decision:** Local and remote capability differences should be inspectable through supported CLI/API surfaces.

**Why:** Partial feature support is inevitable across platforms, but silent degradation recreates the same black-box feeling this project is meant to avoid.

**Implications:**

- daemon exposes capability sets
- operators can tell why a requested strategy is unavailable
- CLI and future UI use the same capability facts when offering or rejecting actions


## ADR-016 — Newly visible shares are staged before local path adoption

**Decision:** Shares made visible through linking, policy, invite acceptance, or recovery should first appear as incoming objects unless the operator or policy explicitly chooses auto-adoption.

**Why:** Resilio's docs show that linked-device convenience can couple visibility, default mode, and default path placement tightly enough to create duplicate folders or require reconnect rituals.

**Implications:**

- incoming visibility becomes part of the public object model
- path choice is explicit and auditable
- visibility and mount existence are no longer conflated

## ADR-017 — Local eviction and share-wide delete use distinct verbs and scopes

**Decision:** The interface must separate local materialization actions from replicated delete actions.

**Why:** Selective-sync systems naturally sit close to a dangerous ambiguity: freeing local space and deleting shared state can look similar unless the contract is explicit.

**Implications:**

- CLI/API require explicit scope on remove actions where ambiguity exists
- plan/apply is preferred for share-wide delete on sensitive paths
- audit and events distinguish local eviction from replicated delete


## ADR-018 — File history and restore are supported surfaces, not hidden archive rituals

**Decision:** The product must expose file history and restore through supported CLI/API objects and actions.

**Why:** Resilio's Archive feature is valuable, but its documented restore path still depends on hidden directories, desktop-only affordances, and timing-sensitive manual steps.

**Implications:**

- restore candidates have stable IDs and provenance
- restore requires explicit scope (`local` vs `share`)
- share-wide restore can use plan/apply when risk warrants it
- audit and events cover restore actions like any other high-signal mutation


## ADR-019 — Ignore, conflict, and service-metadata state are supported surfaces

**Decision:** Ignore rules, conflict cases, and service-metadata health are part of the public control model.

**Why:** Resilio's docs show too much important operator state leaking through hidden `.sync` files, magic conflict filenames, and support-article warnings about what not to delete.

**Implications:**

- ignore rules become inspectable objects with provenance and drift state
- conflicts become structured records with safe resolution actions
- damaged service metadata is surfaced through health/doctor, not discovered only after breakage

## ADR-020 — Incremental rule mutation beats whole-array replacement

**Decision:** List-like policy surfaces should prefer item-level resources or explicit add/remove actions over generic whole-array replacement.

**Why:** Operators frequently mean “change one rule”, and array-replacement patch semantics are too easy to misuse when the blast radius is broader than it looks.

**Implications:**

- ignore rules get add/remove/test style operations
- CLI/API avoid accidental deletion of neighboring rules during routine edits
- future UI/TUI can use the same safe mutation model instead of inventing client-side merge logic


## ADR-021 — Compatibility and authority consequences are preflight objects

**Decision:** Link, invite-accept, grant, and adoption workflows should expose supported preflight reports with blockers, warnings, downgrade notes, and authority changes.

**Why:** Resilio's docs are clear enough that mixed-version linking and linked-device convenience can have real configuration or authority consequences, but too much of that knowledge still lives in FAQs and support notes.

**Implications:**

- preflight becomes part of the public object model
- plans may reference a preflight report and fail if it becomes stale
- UI/CLI can share one compatibility-warning vocabulary

## ADR-022 — Least privilege must survive convenient linking

**Decision:** Personal-device linking should support explicit per-device/per-share roles without requiring a separate weaker share type.

**Why:** Resilio's documented path to read-only behavior across linked devices pushes users toward Standard-folder key rituals and away from the stronger Advanced-folder model.

**Implications:**

- role templates become first-class resources
- linked-group membership never implies owner-like authority by itself
- share/grant semantics stay coherent even when one personal device is read-only, receive-only, or encrypted-only

## ADR-023 — Offers and invites require explicit claims before non-trivial local mutation

**Decision:** Visible shares and capability-bearing invites should pass through a durable claim/acceptance object before they create mounts, grants, or linked-group effects when the outcome is non-trivial.

**Why:** Resilio's current product shows that awareness, access, path choice, and authority expansion are easy to blur. AnonSync should keep “what was offered” distinct from “what this machine accepted.”

**Implications:**

- claims become part of the public object model
- invite inspection is side-effect free
- claim review can reference preflight and plan objects
- audit records can distinguish offered capability, claimed outcome, rejection, and expiry

## ADR-024 — Recovery-material sufficiency is supported state, not folklore

**Decision:** Recovery prerequisites for encrypted offline decrypt and similar workflows should be exportable, inspectable, and verifiable through supported recovery-bundle objects.

**Why:** Recovery that depends on remembered hidden database paths, debug logs, or lucky retained local state is too fragile for the product AnonSync aims to be.

**Implications:**

- recovery bundles become part of the supported surface
- doctor/status can report degraded recovery posture
- offline recovery aims to minimize database dependency where design permits
- rotation or replacement can explicitly invalidate stale recovery material


## ADR-025 — Approval memory is explicit, scoped, and revocable

**Decision:** Any remembered future-approval convenience must compile to a first-class approval object with bounded scope, approver scope, expiry, maximum role, and auditability.

**Why:** Resilio's docs make it clear that “approved before” and “can approve from any linked device” are real product concepts, but they remain too implicit for the trust model AnonSync wants.

**Implications:**

- there is no hidden ambient approval state outside the supported approval surface
- future-share convenience can be tested and reviewed before it is exercised
- linked devices may approve on one another's behalf only when explicit approver scope says so
- audit and events can explain why a later share or invite auto-approved


## ADR-026 — Path binding and relocation are explicit compared actions

**Decision:** Adopting a share into a populated path or relocating an existing mount must generate a comparison object and should usually go through plan/apply.

**Why:** Resilio's docs show permissive reconnect and pre-populated-folder workflows where default paths, duplicate-index folders, and timestamp-win replacement can decide outcomes, while Syncthing's docs react by warning that move/rename is dangerous unless the folder is already fully in sync. AnonSync should surface that risk instead of inheriting either folklore-driven extreme.

**Implications:**

- share identity and local path binding remain separate concepts
- non-empty target paths produce explicit identical/local-only/remote-only/collision findings
- service-marker or foreign-binding conflicts become health/preflight findings, not surprise later errors
- relocation is auditable as local path rebinding rather than hidden filesystem drift


## ADR-027 — Publication scope and route selection are distinct policy surfaces

**Decision:** Discovery policy must distinguish what the daemon publishes about reachability from how it later dials or relays traffic.

**Why:** Current Resilio docs make the network model reconstructable, but still mostly in the language of transport success: tracker, relay, LAN search, predefined hosts. A product centered on inspectable trust needs the language of exposure as well: who can learn that this device/share relationship exists, and through which service.

**Implications:**

- policy objects expose announce scope, dial methods, relay pool choice, and fallback order separately
- route/exposure summaries explain both the active path and the metadata disclosure that enabled it
- future UI/TUI cannot reduce topology policy back into a few unlabeled checkboxes


## ADR-028 — Decision traces are public contract, not debug garnish

**Decision:** High-signal outcomes should expose structured decision traces through supported CLI/API surfaces.

**Why:** Resilio's current docs are good enough to reconstruct route behavior, but too much explanation still arrives as a mix of peer-list symptoms, icon hints, and troubleshooting lore. A product built around inspectability should expose the decision path directly.

**Implications:**

- routes, claims, approval consumption, restore scope, and recovery rebinds can expose selected outcome plus rejected alternatives
- traces carry stable reason codes and freshness so automation can trust them
- future UI/TUI should consume the same trace objects instead of inventing its own inference layer


## ADR-029 — Temporary runtime overrides are explicit leases, not silent policy edits

Sync operators often need short-lived changes: pause during a metered connection, drain before shutdown, or temporary throttling during maintenance.
If those changes silently rewrite durable share or route policy, the product accumulates invisible drift and later surprises.

Decision:

- represent short-lived operational changes as first-class override leases
- require explicit target, effect, provenance, and expiry
- expose effective-state views that combine durable policy with active leases
- keep lease expiry reversible without manual cleanup

Consequence:

AnonSync can offer convenient maintenance controls without inheriting overloaded pause semantics or burying temporary intent inside long-lived configuration.


## ADR-030 — Destructive file mutations carry preservation reports

**Decision:** Share-wide delete, local remove, eviction, and share-scope restore should expose preservation evidence when rollback posture materially affects safety.

**Why:** Resilio's docs make destructive consequences depend too much on placeholder state, exact invocation path, hidden preferences, and Archive assumptions. AnonSync should not ask operators to reconstruct that safety model by memory.

**Implications:**

- the control plane can generate preservation reports for risky file actions
- plans for destructive mutations can reference fresh preservation evidence
- remaining plaintext replicas, encrypted-only remnants, and history gaps become visible state instead of folklore
- future UI/TUI integrations must preserve the same blast-radius model as CLI/API surfaces

## ADR-031 — Retirement, ignore, revoke, replace, and rotate are distinct public actions

**Decision:** Introduce a first-class retirement record so device exit semantics are explicit instead of inferred from disappearance, unlinking, or list hygiene.

**Why:** Current sync products too easily blur cosmetic cleanup, ignored future contact, trust revocation, hardware replacement, and identity rotation. Those intents have different security and continuity consequences and should not be bundled into one overloaded “remove device” gesture.

**Consequences:**

- CLI and API gain retirement resources and explicit intent values
- recovery workflows can reference retirement records when replacement or revocation is the real action
- audit and event streams can explain whether an old device was hidden, ignored, revoked, or replaced
- remote-lag / not-yet-observed retirement becomes supported status instead of ghost-device folklore

## ADR-032 — Share stewardship and handoff are first-class state

**Decision:** Introduce a first-class stewardship record so share governance is explicit instead of inferred from one permission bit or from share-type-specific rituals.

**Why:** Current sync products make authority either too broad (all linked devices act as owners) or too mode-dependent (Standard vs Advanced vs local-share behavior). AnonSync should keep data mutation rights, grant power, delegation, and succession visible as separate public concepts.

**Consequences:**

- CLI and API gain stewardship resources and handoff-plan workflows
- recovery and retirement workflows can say how stewardship changes, instead of leaving authority transfer implicit
- audit and event streams can explain who handed off what authority and under which review policy
- future UI/TUI layers must preserve the same separation between data rights and governance rights


## ADR-033 — Permission, propagation, and local-deviation remediation are distinct public state

Resilio's current read-only guidance still spreads a critical operator question across permission type, selective-sync caveats, overwrite toggles, and encrypted-folder special cases.
That is enough evidence that “can this target write?”, “will local changes propagate?”, and “what happens when someone edits it anyway?” should not live in one overloaded concept.

Therefore AnonSync should expose deviation policy as a first-class supported object.
Roles and mounts may reference it, plans and explain surfaces must show it, and events must report when local deviation is detected or auto-remediated.
That keeps one-way / mirror behavior inspectable without forcing operators to memorize share-type folklore.


## ADR-034 — Filesystem compatibility is first-class state, not conflict folklore

**Decision:** Case rules, Unicode normalization, prohibited names, symlink handling, metadata fidelity, and timestamp/clock safety must be exposed through supported filesystem-profile and compatibility-report surfaces.

**Why:** Resilio's docs still teach too much of this boundary through conflict examples and power-user toggles, while Syncthing's docs point toward a cleaner model of explicit capability and safety settings. AnonSync should not make operators discover pathname or metadata incompatibility only after bind or pull has already started.

**Consequences:**

- CLI and API gain filesystem-profile and filesystem-compatibility resources
- adopt / relocate / restore workflows can require a fresh fs compatibility report as a precondition
- doctor / explain surfaces can say whether the system is operating under reduced pathname or metadata fidelity
- normalization rewrites and metadata stripping become explicit policy choices instead of magic fallout


## ADR-035 — Namespace projection is first-class state, not ignore folklore

**Decision:** Introduce explicit projection-policy objects so share namespace announcement and local mount-view projection are supported state rather than inferred from hidden ignore files or placeholder timing.

**Why:** Resilio's docs make clear that `IgnoreList` edits do not retroactively hide already-synced files, that once a tree is indexed its structure continues to be passed to peers until disconnect, and that Selective Sync separately controls placeholder-visible local projection. Those are individually understandable behaviors, but they still leave operators reconstructing “who sees the name?” from folklore.

**Consequences:**

- CLI and API gain projection-policy and path-test surfaces
- share-level namespace suppression and mount-level omission/placeholder behavior become separate supported concepts
- tighten behavior for already-indexed or already-materialized paths becomes explicit reviewable state
- future UI/TUI layers must preserve the same distinction between namespace announcement, local projection, and byte materialization


## ADR-036 — Settlement confidence is first-class state, not status folklore

**Decision:** Introduce explicit convergence-report and convergence-wait surfaces so the product can distinguish idle status from trustworthy settlement confidence.

**Why:** Resilio's current docs still ask operators to combine peer counts, status warnings, excessive time-difference errors, watcher-exhaustion warnings, and hidden internal-task caveats to decide whether a share is really safe to treat as settled. That is too much inference for a product centered on inspectable control.

**Consequences:**

- CLI and API gain convergence-report and wait-for-settlement resources
- status, doctor, and explain surfaces can report `degraded-converged` instead of pretending every idle share is equally trustworthy
- cutover / backup / relocate workflows can depend on explicit readiness evidence instead of ad hoc polling
- future UI/TUI layers must preserve the same distinction between completion, health, and settlement confidence

## ADR-037 — Tor and I2P are first-class transport engines

**Decision:** Treat Tor and I2P as supported transport engines and route classes, not merely external proxy compatibility modes.

**Why:** If AnonSync wants privacy-routed operation to be central, the route model cannot remain clearnet-first with anonymity added later as an option. Tor's Arti project is explicitly embeddable and production-quality for client use, while I2P's own application guidance encourages bundling a router and using SAM for non-Java applications.

**Implications:**

- route policies can express `tor` and `i2p` directly
- bundled transport runtimes get explicit health/inspection surfaces
- CLI/API can explain when a privacy route failed because the engine was cold, unhealthy, or policy-disabled

## ADR-038 — WAN clearnet direct is a manual override, not a default

**Decision:** Keep faster WAN clearnet direct available, but require manual enablement or explicit policy opt-in.

**Why:** Direct IP-to-IP can materially improve speed, but making it the default would quietly re-center the product on the clearnet-first transport hierarchy it is trying not to inherit.

**Implications:**

- default privacy-oriented policies use Tor/I2P before public direct paths
- route/explain surfaces must say when manual speed override is active
- temporary direct enablement should expire cleanly without rewriting durable baseline policy

## ADR-039 — Linux-first quality bar beats early cross-platform parity

**Decision:** Optimize v1 design quality for Linux and common Linux filesystems before treating Windows/macOS as equal design centers.

**Why:** The archive is already deep in daemon semantics, watcher behavior, path binding, and filesystem compatibility. Spreading that effort too early across every desktop platform would dilute correctness and observability where the project most wants to be strong.

**Implications:**

- roadmap and testing center on Linux-first headless operation
- filesystem-compatibility work starts with common Linux semantics
- other platforms remain future work unless they can fit without bending the primary model



## ADR-040 — Privacy-transport session lifecycle must be explicit

Transport engines, transport runtimes, transport sessions, and route outcomes are related but not identical.
The product should expose all four.

Why:

- bundled runtimes otherwise become magical
- route debugging becomes guesswork
- I2P in particular should usually avoid per-transfer session churn
- a future UI should consume the same public transport/session model as the CLI

Consequence:

- the interface and API expose transport-session objects
- I2P defaults toward a very small number of long-lived shared sessions
- manual clearnet speed overrides create visible temporary route state rather than silently widening the base policy

## ADR-041 — Linux-first support requires explicit filesystem tiers

“Linux-first” is not a complete decision until the project publishes which filesystem environments it supports strongly.

Why:

- operators need a correctness contract before adoption or relocation
- xattr/ACL/symlink/network-filesystem behavior is part of the trust boundary
- warning-tier and blocked environments should be visible before data lands there

Consequence:

- the archive names first-class Linux filesystems for v1
- filesystem support tier is exposed as public state
- adopt / relocate / restore / selective workflows can depend on filesystem-probe results

## ADR-042 — Peer-pinned direct paths and route-speed windows are first-class state

**Decision:** Introduce first-class known-host records and route leases for transport exceptions.

**Why:** Resilio's documented `known_hosts`, tracker/relay toggles, and LAN-only cache-clearing rituals show that operators really do need fine-grained route control. But hiding that control inside preference pages and remembered endpoint state makes exposure hard to reason about.

**Consequences:**

- peer-pinned direct admission becomes distinct from ambient public direct
- temporary speed windows become auditable route leases with scope, reason, expiry, and optional byte caps
- exposure reports can explain who currently learns reachability and why a direct candidate exists at all


## ADR-043 — Contacts and pending peers are first-class state, not side effects of linking

**Decision:** Introduce explicit contact and pending-peer surfaces in the public control model.

**Why:** Resilio's linked-device behavior shows that convenience can easily smear together relationship memory, future approval, and ambient visibility. Syncthing's explicit pending-device queue validates that unknown-peer admission is a real product seam worth modeling directly.

**Consequences:**

- unknown or newly introduced peers land in a queue before trust
- ignore and quarantine become durable supported states
- future UI/TUI work gets a supported admission queue instead of inventing one from logs

## ADR-044 — Successor continuity is reviewed state, not ambient inheritance

**Decision:** Treat device succession as an explicit reviewed continuity plan.

**Why:** Linking and replacement solve different problems. The project should not recreate Resilio-style certificate takeover or ambient owner-like carry-forward just because replacing hardware needs to stay practical.

**Consequences:**

- replacement plans show which grants, approvals, contacts, and known-hosts carry forward
- some continuity may be preserved without pretending the successor is literally the same authority
- recovery, retirement, and stewardship surfaces converge on one explicit successor contract


## ADR-045 — State roots and service profiles are first-class operator state

**Decision:** Expose durable state roots, identity-root continuity, and runtime/service profiles as public objects with verification, attach, move, export, import, and profile-switch workflows.

**Why:** Resilio's docs show too much important behavior hiding in storage paths, service-account choices, migrated-versus-clean installs, and unsupported cloning warnings. A product built around inspectability should never leave the operator guessing which control universe is active.

**Consequences:**

- CLI and API gain explicit state-root and service-profile surfaces
- attach/move/profile-switch work uses reports, plans, and before/after snapshots instead of launch-time magic
- workbench gains a System State page
- “missing shares after mode switch” becomes a blocked or explained transition, not normal folklore


## ADR-046 — File intent and local deviation are first-class operator state

**Decision:** Expose explicit file-intent scope, deviation-case objects, and file-intent receipts so destructive or restorative file actions do not depend on mode-specific folklore.

**Why:** Resilio's docs still spread important file semantics across Selective Sync placeholder behavior, `Remove from this device` versus `Remove from all devices`, read-only `Overwrite any changed files`, and manual Archive restore. An inspectable product should not force operators to reconstruct that model from scattered caveats.

**Consequences:**

- CLI and API gain deviation-case and file-intent-receipt surfaces
- workbench gains a dedicated file-actions/deviation panel
- future GUI/TUI affordances must preserve the same distinction between local eviction, replicated delete, local restore, share restore, and deviation resolution


## ADR-047 — Runtime control is a phase matrix, not an overloaded pause state

**Decision:** Introduce first-class activity-phase-state and schedule-window surfaces so one-shot overrides and recurring windows render through the same public phase model.

**Why:** Resilio's current docs still show pause, scheduler, and bandwidth controls that are useful but semantically overloaded: paused states can still allow rescans and delete propagation, scheduler effects can be asymmetric, and LAN throttling can depend on a separate advanced switch. AnonSync should not clone that ambiguity.

**Consequence:**

- `activity show` and workbench activity cards expose scan/index, ingress, egress, delete propagation, announcement, and dialing separately
- recurring windows become first-class inspectable objects rather than UI-only calendar state
- stronger freezes that suspend delete propagation or announcement can require plan/apply instead of masquerading as ordinary pause
- route-class scope for throttling remains explicit so LAN, Internet, overlay, and direct-path behavior do not blur together

## ADR-048 — Projection tightening emits receipts, not folklore

**Decision:** Introduce projection-effect reports and projection receipts for high-signal namespace / local-view changes, especially when rules tighten after paths were already indexed or materialized.

**Why:** Resilio's docs say `IgnoreList` lives in hidden `.sync`, does not affect files that already synced, and still leaves indexed structure passed to peers until disconnect. Separate docs say placeholders / `.rsls` are a local-view mechanism, disconnecting a selective-sync share removes placeholders from the device, nested subfolder shares disable Selective Sync while double-indexing, and xattrs use a separate `StreamsList` control path. Those are workable behaviors, but they leave operators inferring past and future visibility from side effects instead of one public model.

**Consequences:**

- any projection-tightening action that touches already indexed or materialized state can require a projection-effect report before apply
- applied high-signal changes emit receipts explaining peer namespace change, local-view change, local-byte effect, and remaining follow-up
- detach cleanup cannot masquerade as share-wide suppression
- GUI/TUI/CLI layers must preserve the distinction between peer namespace, local view, and local byte state


## ADR-049 — Settlement readiness is a policy/barrier/receipt layer, not just one convergence report

**Decision:** Introduce first-class settlement-policy, settlement-barrier, and settlement-receipt surfaces above the existing convergence report.

**Why:** Resilio's current docs still make operators combine `X of Y peers`, sync-history clues, time-difference warnings, watcher fallback, background-task caveats, and ghost-file/source-absence warnings to judge whether a share is *actually* safe for cutover or restore. A product centered on inspectable control should not leave that translation step outside the public model.

**Consequences:**

- convergence evidence remains first-class, but no longer carries the whole readiness burden alone
- intent-specific witness/source rules, quiet windows, evidence-age limits, and degraded allowances become public policy state
- high-signal actions can require or emit settlement barriers and receipts
- later audit can prove what readiness standard an action actually used instead of only that it happened


## ADR-050 — Rollback provenance and conflict resolution are timeline objects, not support ritual

**Decision:** Introduce first-class history-entry, restore-candidate, conflict-case linkage, and rollback-receipt surfaces so rollback and conflict resolution are one public timeline model.

**Why:** Resilio's current docs still split the story across a generic 30-day History view, hidden/manual Archive restore, offline-wins overwrite behavior, `.Conflict` filename ritual, and a power-user switch that can suppress conflict-file creation while leaving syncing unpredictable. An inspectable product should not make operators reconstruct rollback truth from those fragments.

**Consequences:**

- history entries carry provenance, capture cause, retention horizon, allowed scopes, and confidence
- restore and conflict-resolution actions emit rollback receipts in addition to ordinary file-intent or audit records
- workbench gains a combined history/conflict/rollback surface rather than separate “history” and “mystery conflict” mini-products
- future GUI/TUI/CLI projections must preserve the same winner/loser/scope semantics without falling back to magic filenames or hidden archive browsing

## ADR-051 — Filesystem portability is a durable fidelity contract, not a one-time preflight

**Decision:** Introduce first-class portability-policy, fidelity-contract, drift-case, and fidelity-receipt objects so filesystem semantics remain explicit after bind and after later runtime drift.

**Why:** Resilio's current docs still distribute this boundary across SMB caveats, symlink platform rules, hidden `.sync` / `StreamsList` service files, troubleshooting for UTF-8/path-length/permission failures, and remove/re-add repair ritual after service-marker corruption. That is workable support knowledge. It is not a durable operator contract.

**Consequences:**

- the public model distinguishes previewed compatibility from the active semantics a mount is currently promising
- network-share posture and degraded notifications become explicit support-tier facts, not background folklore
- accepted downgrade becomes auditable through fidelity receipts
- later drift in permissions, notifications, or filesystem backing becomes a first-class warning object instead of a mysterious sync regression


## ADR-052 — Storage pressure is a budget/reclaim/receipt layer, not a troubleshooting afterthought

### Decision

AnonSync will model storage as first-class public state through space ledgers, budget policies, pressure cases, reclaim plans, and reclaim receipts.

### Why

Current sync products often expose useful space-saving features while still leaving the operator to reconstruct one storage story from placeholders, hidden archives, power-user thresholds, service-state paths, and manual temp-remnant cleanup. That is good troubleshooting; it is not an honest storage contract.

### Consequences

- low-space conditions can be explained by byte class rather than by generic warning strings
- reclaim can stay visibly distinct from replicated delete semantics
- retention and rollback posture can remain visible when space-saving actions would weaken them
- workbench, CLI, API, and audit can all answer what was reclaimed and what tradeoff was accepted


## ADR-053 — capability-bearing offers use one artifact grammar regardless of delivery encoding

**Decision:** AnonSync will model portable authority through first-class offer artifacts, offer policy, and claim receipts. File, URI, QR, clipboard, and local-handoff delivery are encodings of the same semantic object, not different trust systems.

**Why:** Resilio's current docs still make operators combine key-vs-link behavior, approval posture, expiry/use-count link settings, Standard-vs-Advanced re-sharing semantics, and local-share permission ritual to answer what authority an artifact really carries.

**Consequences:**

- sender-side surfaces can revoke or reissue offers without confusing that with applied local authority
- receiver-side intake can normalize portable artifacts before any local mutation
- delivery widgets stop becoming hidden semantic control surfaces
- later audit can prove offer consumption through claim receipts even after one-time artifacts expire


## ADR-054 — Transfer speed is governed by explicit policy, budget, and explanation objects

**Decision:** AnonSync will model transfer behavior through first-class transfer-policy, throughput-budget, transfer-explanation, and transfer-budget-receipt objects rather than leaving throughput truth to icons, graphs, and advanced settings.

**Why:** Resilio's current docs still spread important transfer behavior across relay/direct articles, Internet-vs-LAN bandwidth caveats, protocol and encryption knobs, queue priority semantics, per-extension delay config, and performance graphs. That is useful tuning guidance. It is not one operator-facing transfer contract.

**Consequences:**

- CLI and API gain explicit transfer-policy, throughput-budget, and transfer-explanation surfaces
- workbench transfer cards must explain queue, route, and bottleneck truth rather than only progress
- temporary metered or bulk windows emit receipts instead of disappearing into scheduler folklore
- future GUI/TUI/CLI projections must preserve the same distinction between route permission, route preference, and throughput budget


## ADR-055 — Attention is a durable policy/event/receipt layer, not a scatter of badges and notifications

**Decision:** AnonSync will model operator attention through first-class attention-policy, attention-event, and attention-receipt objects that sit above reports and review items without replacing them.

**Why:** Resilio's current docs still make operators triangulate status-column warnings, separate core-warning pages, history search, queue inspection, Linux UI-only notifications, and browser trust prompts to answer one simple question: what needs action now, and what did my acknowledgement actually change? That is workable support knowledge. It is not one trustworthy attention contract.

**Consequences:**

- workbench, CLI, and headless clients preserve the same semantic urgency even when they render through different delivery channels
- acknowledgements and snoozes become receipt-bearing public state rather than implicit local UI behavior
- delivery failure is visible and auditable instead of disappearing into best-effort notification plumbing
- future GUI/TUI/CLI projections must preserve the same distinction between report meaning, lane placement, delivery channel, and operator acknowledgement


## ADR-056 — Control access is an endpoint/session/receipt layer, not WebUI password lore

**Decision:** AnonSync will model control access through first-class control-access-policy, control-endpoint, access-token, control-session, and access-receipt objects.

**Why:** Resilio's current docs still make operators combine localhost-vs-LAN WebUI listen state, optional workstation passwords, session cookies, self-signed HTTPS trust warnings, config-file login injection, password-reset side effects, and service-profile storage-folder changes to answer one simple question: who can control this daemon right now, and what changed when I exposed or repaired that access? That is workable support knowledge. It is not one trustworthy control-access contract.

**Consequences:**

- leaving localhost becomes a reviewed exposure change rather than a casual bind tweak
- browser/workbench sessions, CLI sessions, and automation tokens remain visibly distinct
- trusted-proxy and hostcheck posture become explicit endpoint state instead of deployment folklore
- access repair and revocation emit receipts instead of mutating unrelated daemon state behind the operator's back


## ADR-057 — Recovery material is a custody/continuity/receipt contract, not just an export command

**Decision:** AnonSync will model recovery through first-class recovery posture, workflow-scoped bundles, and recovery receipts that explicitly name custody class, hidden dependencies, continuity claims, and invalidation causes.

**Why:** Resilio's current docs still spread recovery truth across unsupported cloning warnings, storage-folder lore, saved-key requirements, database continuity requirements for encrypted recovery, config-mode guidance, and password-reset or service-profile actions that mutate state roots. That is workable support knowledge. It is not one durable recovery-material contract.

**Consequences:**

- bundle export no longer implies sufficiency by itself
- device replacement, encrypted-byte recovery, and grant/identity continuity stay visibly distinct
- rotation, retirement, and state-root changes can invalidate older recovery bundles explicitly
- workbench, CLI, API, and audit can all answer which recovery artifact was current and what it could actually preserve

## ADR-058 — Release posture is a version/channel/schema/rollback contract, not package-manager folklore

**Decision:** AnonSync should expose release posture, reviewed upgrade plans, and release receipts as first-class operator state.

**Why:** Current Resilio docs still spread upgrade truth across update settings, platform-specific install pages, v2/v3 and Home/Business caveats, mixed-version linking warnings, and changelog archaeology. That is useful support material, but it is not one trustworthy operator contract.

**Consequences:**

- update availability and upgrade readiness remain visibly distinct
- edition family, release channel, schema epoch, and peer-constellation skew stay separate public facts
- cutover scope and rollback posture become part of reviewed upgrade plans rather than post-hoc support lore
- later audit can prove which compatibility boundary was accepted when a guarded or mixed release posture remained in force



## ADR-059 — Effective policy is a per-field origin/precedence contract, not settings-layer folklore

**Decision:** AnonSync will model defaults profiles, policy bindings, effective-policy explanation, and policy receipts as first-class operator state.

**Why:** Current Resilio docs still spread effective behavior across global preferences, per-folder preferences, power-user keys, config-mode injection, Linux-WebUI gaps, and manual-detach-from-default lore. That is useful support material, but it is not one trustworthy precedence contract.

**Consequences:**

- effective value and origin chain stay separate public facts
- `inherit`, `disable`, `clear`, and `pin to none` remain distinct actions rather than one ambiguous reset gesture
- defaults/profile changes become previewable by subject set instead of silently rewriting every eligible object
- later audit can prove which field was pinned, which returned to inheritance, and which defaults/profile change touched existing subjects


## ADR-060 — Diagnostics are an incident/evidence/redaction contract, not hidden-log support ritual

**Decision:** AnonSync will model troubleshooting through first-class diagnostic incidents, reviewed evidence bundles, redaction profiles, and evidence receipts.

**Why:** Current Resilio docs still spread serious diagnostics across hidden storage-folder lore, manual debug-file toggles, log-size tweaks, platform-specific dump collection, and support-form ritual. That is useful support material. It is not one trustworthy operator contract.

**Consequences:**

- diagnostic depth becomes explicit, temporary, and receipt-bearing instead of sticky hidden state
- support bundles can be previewed, redaction-reviewed, sealed, exported, and destroyed through one public model
- crashes, per-file diagnostics, recent logs, and event windows stay incident-scoped instead of becoming orphaned filesystem artifacts
- future GUI/TUI/CLI projections must preserve the same distinction between incident scope, collected evidence, redaction posture, and bundle custody


## ADR-061 — Temporary exceptions share one lease lifecycle across domains

**Decision:** AnonSync will treat temporary exceptions as first-class override leases with one shared lifecycle, even when route, activity, diagnostics, access, or other domains keep specialized fields.

**Why:** Current Resilio docs still solve several short-lived operator needs through scattered scheduler cells, power-user keys, config edits, debug toggles, and cleanup memory. That is workable, but it is not one trustworthy exception contract.

**Implications:**

- specialized temporary controls can cross-link through one `Exceptions` surface
- every lease can show baseline-versus-effective state, end condition, and receipt history
- `renew` preserves continuity instead of replacing history with a fresh opaque object
- converting a temporary exception into durable policy becomes an explicit, receipted mutation rather than hidden drift


## ADR-062 — Personal-device convenience is a constellation/authority-domain contract, not ambient owner identity

Resilio's linked-device model remains a useful warning: it is highly convenient, but it still makes ambient same-identity status do too much authority work.
AnonSync should instead model convenience-linked devices through explicit constellation records, member classes, visibility defaults, approval-scope limits, and share-scoped authority-domain explanations.

Consequences:

- “my devices” remains useful without silently implying owner merge
- phones, appliances, untrusted-storage nodes, and recovery-only members can stay inside one reviewed constellation without pretending they are equivalent
- disconnect/remove/approval actions can explain constellation-wide blast radius before apply
- later audit can prove when membership, member class, or scope boundaries changed


## ADR-063 — Discovery publication is an audience/fact/residue contract, not tracker-toggle folklore

**Decision:** AnonSync will model discovery publication through first-class disclosure profiles, disclosure reports, residual-disclosure findings, and disclosure receipts.

**Why:** Current Resilio docs still spread disclosure truth across tracker behavior, LAN announcements, predefined hosts, ports/protocols notes, and cache-clearing lore. That is useful support material. It is not one trustworthy operator contract for what audiences learn which facts and what remains after narrowing.

**Consequences:**

- route success and disclosure truth remain related but separate public state
- local discovery, named endpoints, private infrastructure, and public infrastructure all render as audience classes with fact matrices
- narrowing a policy can stop future publication without falsely claiming residue is gone
- later audit can prove both publication change and any acknowledged or cleared residual disclosure


## ADR-064 — Exit intent must be a first-class contract

**Decision:** Departure-style actions should compile to a shared exit-plan / exit-receipt model instead of relying on overloaded remove/uninstall vocabulary.

**Why:** Current sync-product support lore often makes operators infer too much from verbs like hide, disconnect, remove, unlink, or uninstall. A privacy-respecting product should be at least as explicit on the way out as it is on the way in.

**Implications:**

- exit intent stays explicit (`hide`, `detach-local`, `revoke-authority`, `replace-with-successor`, `decommission`, `erase-local-residue`)
- exit plans always show what stops, what stays, and what residue remains
- domain-specific verbs may stay for ergonomics, but their outcomes should compile to one shared receipt model


## ADR-065 — Safety-critical destructive controls need channel parity

**Decision:** Any exit, replacement, revocation, detach, or destructive file action that is considered safety-critical must preserve the same semantic review model across GUI, WebUI, TUI, CLI, and API-backed automation.

**Why:** Current Resilio docs make it unusually visible that Linux/WebUI/config-heavy operation can differ meaningfully from richer desktop paths, including destructive-action affordances and feature envelopes. A Linux-first product cannot treat that as implementation trivia.

**Implications:**

- dangerous actions get one stable review grammar (`intent`, `stops`, `stays`, `residue`, `follow-up`, `receipt`)
- channel-specific clients may change layout, but not scope truth or acknowledgement requirements
- the daemon/API contract must expose a review-ready projection rather than forcing each client to summarize raw effects ad hoc


## ADR-066 — Device joining must be a reviewed blast-radius decision, not a pairing ritual

**Decision:** Any non-trivial device join into a personal constellation must expose a fixed review model before apply.

**Why:** Current Resilio docs still make one `link device` step carry identity continuity, immediate share visibility, future approval reach, compatibility risk, and path-placement consequences. A Linux-first product should not hide that blast radius behind convenience language.

**Implications:**

- reviewed joins answer whether the action is join, migration, or replacement
- member class and default visibility posture are explicit before apply
- immediate visibility and authority deltas are explicit before apply
- GUI, WebUI, TUI, CLI, and automation all render the same join sections in the same order
- future GUI convenience work cannot silently outrun what headless or textual operators are allowed to understand before apply

## ADR-067 — Non-trivial claims and adoptions need one fixed intake grammar

**Decision:** Portable-offer acceptance, linked incoming-share adoption, and other non-trivial way-in flows must preserve the same semantic review model across GUI, WebUI, TUI, CLI, and API-backed automation.

**Why:** Current Resilio docs show that linked visibility, default-path placement, reconnect behavior, and non-empty-folder acceptance can still depend on device-wide mode switches and `Connect` ritual. A Linux-first product should not let one channel show rich intake meaning while another collapses it into a path picker.

**Implications:**

- non-trivial claims get one stable review grammar (`source`, `local outcome`, `path/filesystem`, `authority delta`, `blockers`, `receipt`)
- incoming visibility, portable offers, and prepared claims can render through the same supported intake model
- channel-specific clients may change layout, but not acceptance meaning or acknowledgement requirements
- future GUI convenience work cannot silently outrun what headless or textual operators are allowed to understand before apply



## ADR-068 — Successor cutover and state re-home need one fixed review grammar

**Decision:** Non-trivial device replacement and continuity-sensitive state-root/runtime transitions should expose one shared cutover review model before apply.

**Why:** Current Resilio docs still spread continuity meaning across unsupported cloning, service installer choices, service-account storage-root shifts, link-time certificate takeover, uninstall residue, and stolen-device ritual. A Linux-first product should not make operators reconstruct cutover truth from that archaeology.

**Implications:**

- successor replacement and same-root re-home can share one stable review order without pretending they are always the same action
- GUI, WebUI, TUI, CLI, and automation all have to render predecessor/candidate, carry-forward, target, rewrite, residue, and receipt truth in the same order
- installer or profile-switch convenience work cannot silently outrun what headless or textual operators are allowed to understand before apply
- later audit can prove which continuity claims were actually made, what authority rewrites occurred, and what residue remained unresolved


## ADR-069 — Compromise response is an incident-grade containment/rotation contract, not unlink/uninstall ritual

**Decision:** AnonSync will model trust incidents through first-class compromise cases and compromise receipts that normalize immediate freeze, later revocation, rotation, continuity choice, and residue findings into one reviewed contract.

**Why:** Current Resilio docs still spread compromise meaning across hide-offline-device behavior that does not unlink anything, local-only unlink limits, uninstall/storage cleanup notes, stolen-device reset ritual, and manual reshare memory. That is workable emergency lore. It is not one trustworthy containment contract.

**Implications:**

- freeze, revoke, rotate, replace, and clean-break decisions remain visibly distinct even when one incident touches all of them
- access tokens, portable offers, route publication, grants, and approval memory can participate in one case without collapsing into one overloaded verb
- successor preparation can remain continuity-preserving without falsely claiming compromise was fully cleared
- later audit can prove what was contained immediately, what still required observation, and what residue remained unresolved


## ADR-070 — Dormant-peer return is a reviewed state-replay decision, not ordinary online status

**Decision:** AnonSync will model long-offline or chronology-uncertain return through first-class re-entry cases and re-entry receipts that normalize dormancy facts, chronology confidence, replay authority, divergence/source reality, and escalation options into one reviewed contract.

**Why:** Current Resilio docs still spread stale return meaning across hide-only offline-device cleanup, offline-peer counters, configurable disconnect thresholds, offline-wins overwrite rules, time-difference warnings, and ghost-file/source-absence messages. Those are useful clues. They are not one trustworthy re-entry contract.

**Implications:**

- “online again” remains visibly separate from “safe to resume writable replay”
- chronology confidence and source reality stay public facts instead of archive/conflict folklore
- stale return can escalate cleanly into compromise or successor-cutover review without pretending it was benign status all along
- later audit can prove whether the subject resumed, stayed quarantined, downgraded to read-only, or was blocked/escalated


## ADR-071 — Destructive replay needs one reviewed pre-apply contract, not pause/archive folklore

**Decision:** Any non-trivial remote delete, overwrite, or receive-only revert wave should expose one shared destructive-replay review model before apply.

**Why:** Current Resilio docs still make operators combine pause-except-delete semantics, optional archive retention, potentially destructive `Overwrite any changed files` behavior, and manual restore lore to understand whether the next accepted cluster action will destroy or replace local state. That is useful support information. It is not one trustworthy consent contract.

**Implications:**

- pause, preservation, and destructive consent remain visibly separate public state
- delete, overwrite, and revert scope stay explicit before apply rather than being inferred from mode or aftermath
- archive/versioning weakness becomes a recoverability finding, not a hidden preference footnote
- GUI, WebUI, TUI, CLI, and automation all have to render the same trigger/effect/recoverability/confidence sections in the same order
- destructive waves can escalate into re-entry or compromise review without pretending they were routine sync progress all along

## ADR-072 — Conflict adjudication needs one reviewed contract, not suffix folklore

**Decision:** Any non-trivial conflict should expose one shared adjudication review model before winner selection or destructive loser handling proceeds.

**Why:** Current Resilio docs still make operators combine `.Conflict` suffix warnings, manual healthy-file dance, re-add collision examples, and power-user path toggles such as `fix_conflicting_paths` to understand what is actually colliding and what happens if they “clean it up”. That is useful support information. It is not one trustworthy adjudication contract.

**Implications:**

- conflicts keep semantic class distinct from filename artifact
- reviewed conflict pages always expose candidate posture, compatibility reality, propagation scope, and loser handling before resolution
- rollback receipts prove winner, loser handling, and unresolved caveats after the visible badge is gone
- workbench, CLI, and API-backed automation must render the same adjudication sections in the same order


## ADR-073 — Same-host derivation needs one reviewed contract, not local-share convenience

### Status
Accepted

### Context

Current Resilio docs show same-host `local share` support is useful, but it still spreads important meaning across one convenience action: target path choice, loop warnings, inherited permissions, source-coupled removal, re-share ritual, and placeholder dependence.
That is enough to build real workflows, but it is too compressed for AnonSync's thesis.

### Decision

AnonSync will treat non-trivial same-host derivation as a first-class reviewed case with one fixed grammar for source/target, topology risk, authority+lifecycle coupling, materialization+target-tier reality, admissible derivations, and receipt promise.
No channel may reduce that meaning to a path picker plus `Create local copy` semantics.

### Consequences

- same-host fanout becomes explicitly distinguishable from remote adoption, export, or cache-only branching
- loop risk and target-tier weakness are previewed before apply rather than left to warnings or failure
- lifecycle coupling to the source remains inspectable later from receipts
- Linux/WebUI/CLI parity becomes part of the safety model for same-host derivation

## ADR-074 — Live authority mutation needs one reviewed contract, not folder-class ritual

**Decision:** Non-trivial access changes should compile to one reviewed authority-mutation model rather than depending on share class, owner folklore, disconnect semantics, or remove/re-share ritual.

**Why:** Resilio's current docs still spread live permission meaning across Standard-vs-Advanced folder class, same-identity owner broadening, local-share caveats, and config-mode surface loss. AnonSync should keep write authority, delegation reach, revoke power, dependent fallout, and byte-retention consequences visible in one place.

**Consequences:**
- grant mutation gains a stable review grammar and durable mutation receipts
- workbench and CLI both need explicit current-authority and desired-boundary sections
- narrowing authority can preserve bytes without pretending revoke means erase
- imported or legacy authority representations may require visible migration rather than silent coercion


## ADR-075 — Graph overlap and containment need one reviewed contract, not nested-share folklore

**Decision:** Non-trivial nested, overlapping, moved, or root-boundary-sensitive graph relationships should compile to one reviewed topology model rather than depending on separate-share caveats, local loop warnings, reconnect ritual, or config-root restrictions.

**Why:** Resilio's current docs still spread topology meaning across nested-child limitations, double indexing, child-via-parent propagation, same-host parent/subdirectory loop warnings, move/rename limits, and `directory_root_policy` / `dir_whitelist` path rules. AnonSync should keep graph relation, propagation shape, path continuity, and root-boundary truth visible in one place.

**Consequences:**
- topology work gains a stable review grammar and durable topology receipts
- workbench and CLI both need explicit graph-subject and propagation-shape sections
- nested-share acceptance stays visibly distinct from same-host derivation, cross-share move, or root escape
- imported or policy-root path constraints may require visible rebind or root-review rather than silent coercion


## ADR-076 — Writer contention needs one reviewed coordination contract, not badges and hidden delay lore

**Decision:** Non-trivial lock pressure, burst-save delay, mixed external-writer risk, and explicit quiesce actions should compile to one reviewed contention model rather than living as separate status badges, hidden delay files, retry knobs, and SMB caveats.

**Why:** Current Resilio docs still spread coordination meaning across `Locked files`, storage-folder `FileDelayConfig`, `recheck_locked_files_interval`, and SMB warning pages about notification loss, broken locks, and mixed access outside Samba. AnonSync should keep contested scope, writer reality, filesystem posture, quiesce effect, and safe resume conditions visible in one place.

**Consequences:**
- contention work gains a stable review grammar and durable contention receipts
- workbench and CLI both need explicit contested-scope, writer-reality, notification-posture, and quiesce-effect sections
- delay profiles, upload holds, bidirectional freezes, and reader-only guards remain visibly distinct public actions
- degraded notification or mixed-access evidence can escalate visibly into fidelity, topology, or destructive-replay review instead of hiding behind retries

## ADR-077 — Host fit and scale admission need one reviewed contract, not warnings and re-add folklore

**Decision:** Non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers should compile to one reviewed capacity-fit model rather than living as separate warnings, advanced toggles, and re-add/reindex ritual.

**Why:** Current Resilio docs still spread host-fit meaning across `Out of memory`, watcher-exhaustion warnings, generic internal-task slowdown notes, huge-folder indexing preferences, free-space reserve knobs, and troubleshooting advice that can end in restart, `touch`, or remove-and-re-add. AnonSync should keep subject role, host resource posture, freshness guarantees, path blockers, and admissible local modes visible in one place.

**Consequences:**
- host-fit work gains a stable review grammar and durable fit receipts
- workbench and CLI both need explicit subject-role, local-capacity/index-cost, freshness-posture, and path-blocker sections
- full adoption, selective/materialized narrowing, metadata-only visibility, reclaim-first staging, and reject-on-this-host outcomes remain visibly distinct public actions
- intake, topology, fidelity, and storage surfaces can escalate into host-fit review instead of hiding scale pain behind generic add/connect flows


## ADR-078 — Bring-up and first control entry need one reviewed contract, not installer and config ritual

**Decision:** Non-trivial first-open work should compile to one reviewed bring-up model rather than living as separate init flows, startup flags, config files, activation steps, and bind-address lore.

**Why:** Current Resilio docs still spread bring-up meaning across v3 activation/edition notes, config-mode and Linux startup flags (`--storage`, `--identity`, `--license`, `--webui.listen`), headless license-apply ritual, local-versus-LAN WebUI choices, and unsupported clone warnings. AnonSync should keep host role, continuity choice, identity posture, control exposure, and startup blockers visible in one place.

**Consequences:**
- bring-up work gains a stable review grammar and durable bring-up receipts
- workbench and CLI both need explicit host-role, continuity-choice, identity-posture, control-posture, and blocker sections
- fresh local-only start, attach existing state, recover/import, successor-sensitive continuity, and blocked bring-up remain visibly distinct public actions
- state-root, recovery, release, and access surfaces can escalate into bring-up review instead of hiding first-open meaning behind startup convenience


## ADR-079 — Browser-mediated control must degrade into explicit capability, integrity, and repair state

**Decision:** Missing browser/workbench controls, trust/bootstrap problems, and auth-repair work should compile to explicit public capability, integrity, and repair objects rather than disappearing buttons, unsafe browser ritual, or settings-file surgery.

**Why:** Current Resilio docs still spread Linux/WebUI control truth across browser compatibility notes, ad-block caveats, self-signed warning pages, manual link-paste fallback, and password-reset paths that can reset preferences or duplicate devices. AnonSync should keep control availability, client degradation, fallback channels, and auth repair visible in one place.

**Consequences:**
- browser-rendered control becomes one projection of server-declared capability state rather than the origin of semantics
- workbench and CLI both need explicit capability-availability, integrity-finding, and auth-repair sections
- ordinary control repair must preserve the difference between access-state change and broader reviewed bring-up/state-root transition
- Linux/headless deployments gain a clearer guarantee that browser failure cannot erase the only honest path to inspect or perform high-signal control actions


## ADR-080 — High-signal mutation needs one explicit reviewed authority object, not ambient browser/session continuity

**Status:** Accepted

**Why:** Current Resilio docs still blur mutation authority across optional workstation passwords, browser-session cookies, config-defined credentials, Linux/headless startup flags, localhost/LAN bind changes, and even service-account switches that can reopen a different storage root. AnonSync should keep inspectability and mutation authority visibly distinct.

**Decision:** Browser/workbench sessions are inspect-oriented by default. Non-trivial mutation requires either a short-lived reviewed mutation grant bound to subject scope, channel, endpoint, and state root, or a separately issued explicit mutate/admin credential object whose scope is already public enough to satisfy the same gate.

**Consequences:**

- dangerous apply paths must expose gate state rather than generic confirmation ritual
- mutation grants become receipt-bearing public objects with expiry and invalidation semantics
- endpoint, integrity, or state-root drift can invalidate reviewed elevation even if the browser session itself still exists
- CLI, TUI, browser/workbench, and API-backed automation need one shared mutation-authority truth


## ADR-081 — Local target ownership needs one reviewed custody contract, not hidden-marker folklore

**Decision:** AnonSync will model host-local target ownership through first-class target-custody records, binding-collision cases, and custody receipts rather than treating hidden internal markers or non-empty-path checks as the whole contract.

**Why:** Current Resilio docs still make `.sync` markers, `already added` checks, same-folder multi-instance collision, removable-disk reuse, and delete-and-re-add repair ritual carry too much ownership meaning. AnonSync should not let same-lineage reuse, foreign-marker inspection, successor claim, and blocked collision collapse into one path picker.

**Implications:**

- risky local target claims must be reviewable before marker rewrite or cleanup
- daemon/API must expose target ownership and lineage confidence directly where it can be inferred
- preservation requirements must be explicit before cleanup destroys easy ownership evidence
- GUI, CLI, TUI, and automation clients must share one fixed custody-review grammar



## ADR-082 — Safety-critical actions need one channel-parity contract, not surface-specific semantics

**Decision:** Safety-critical actions must keep one server-declared capability identity and one stable review grammar across browser/workbench, CLI, TUI, and API-backed control, with explicit handoff objects when a degraded channel cannot continue the action honestly.

**Why:** Current Resilio docs still spread action meaning across Linux/WebUI-only control, config-mode feature loss, disappearing share controls, manual link-paste fallback, and Linux WebUI preferences that ignore one destructive-action guard. AnonSync should not let channel choice decide whether a dangerous action exists or how it is reviewed.

**Consequences:**

- degraded channels must expose capability/degradation/handoff state rather than weaker local substitutes
- review handoffs become durable public objects with auditable continuity semantics
- workbench and CLI both need the same fixed channel-parity section order for safety-critical actions
- channel change can reopen broader review when endpoint, trust, or state-root meaning changes, but it must say so explicitly


## ADR-083 — Runtime-principal and service-seat changes need one reviewed continuity/reachability contract, not install-mode folklore

**Decision:** Non-trivial execution-seat changes should compile to one reviewed continuity/reachability model rather than depending on installer choices, service-account switching, mapped-drive caveats, UNC workarounds, or re-add/re-share ritual.

**Why:** Current Resilio docs still spread same-host runtime truth across current-user vs Local System / Local Service service modes, migrated-state vs clean install choices, mapped-drive invisibility for services, UNC fallback with degraded notifications, and storage roots that vary by service account. AnonSync should keep state continuity, reachable-target delta, notification/freshness posture, and clean-seat-versus-migrated outcome visible in one place.

**Consequences:**

- execution-seat work gains a stable review grammar and durable seat-switch receipts
- workbench and CLI both need explicit continuity, reachability, freshness, and fallout sections for runtime-seat changes
- service installs or principal switches can no longer masquerade as harmless backgrounding when they actually alter the host-local world
- degraded workaround posture such as rescan-only rebinds remains visibly distinct from true same-seat continuity

## ADR-084 — Human-facing labels must stay separate from authority identity and same-person continuity

**Decision:** Non-trivial naming work should compile to one reviewed label/identity continuity model rather than depending on unlink/new-certificate ritual, convenience linking, or remembered fingerprint lore.

**Why:** Current Resilio docs still spread naming/continuity meaning across identity-name-generated certificates, rename-via-unlink behavior, linked-device auto-approval reach, configured-device takeover during linking, mixed-version linking warnings, and local-only unlink limits. AnonSync should keep mutable labels, stable subject handles, cryptographic authority, alias history, and same-person continuity visibly distinct.

**Consequences:**

- naming work gains a stable review grammar and durable identity-label receipts
- workbench and CLI both need explicit current-label/authority, peer-visible fallout, and grant/constellation-fallout sections
- harmless relabel, alias preservation, successor continuity, and authority replacement remain visibly different public actions
- convenience linking can no longer masquerade as safe continuity proof when the real effect is trust or approval blast-radius change



## ADR-085 — Live namespace and managed sync state need one reviewed share-layout contract, not hidden-dotfolder folklore

**Decision:** Non-trivial share-layout work should compile to one reviewed live-namespace/annex/residue model rather than depending on hidden `.sync` state, `Archive` browsing, xattr stub files, or temp-suffix cleanup ritual as the operator contract.

**Why:** Current Resilio docs still place share identity markers, ignore policy, rollback/history storage, xattr carry-forward state, and in-flight residue directly in or beside the live tree through `.sync`, `.sync/Archive`, `.sync/StreamsList`, `.sync/Streams`, and `.!sync` conventions. AnonSync should keep ordinary user content, managed control bytes, rollback state, portability sidecars, and cleanup fallout visibly separate.

**Consequences:**

- share-layout work gains a stable review grammar and durable layout receipts
- workbench and CLI both need explicit live-namespace, annex-placement, and residue/cleanup sections
- annex migration and legacy cleanup can no longer masquerade as harmless hidden-file deletion
- storage, rollback, fidelity, and custody surfaces gain one shared place to say where the daemon's own bytes actually live for a share


## ADR-086 — Performance and compatibility changes need one reviewed semantic-fallback contract, not power-user-toggle folklore

**Decision:** Non-trivial optimization or degraded-target work should compile to one reviewed semantic-runtime model rather than depending on advanced settings, SMB caveats, watcher warnings, or rename folklore as the operator contract.

**Why:** Current Resilio docs still let lazy indexing, whole-file fallback, direct fast paths, notification loss, and degraded network-share posture quietly alter rename continuity, detection freshness, resumability, verification timing, or conflict honesty. AnonSync should keep those guarantee changes explicit.

**Consequences:**

- semantic runtime state gains a stable contract and receipt model
- workbench and CLI both need explicit guarantee-delta sections before meaning-changing optimization can apply
- degraded-target acceptance can no longer masquerade as harmless speed tuning
- future performance work must distinguish semantic-neutral tuning from reviewed semantic downgrade



## ADR-087 — Revoke/remove language needs one reviewed retained-copy and recall contract, not disconnect folklore

**Decision:** Non-trivial access narrowing, replica retirement, or share-removal work should compile to one reviewed retained-replica/recall model rather than depending on disconnect notes, linked-device scope, or encrypted-backup caveats as the operator contract.

**Why:** Current Resilio docs still let `Disconnect` mean `future updates stop while bytes remain`, let linked-device removal say nothing about non-linked peers that already have the share, and let encrypted backup usefulness depend on saved keys and database continuity while ordinary read-only/archive behavior tells a different story. AnonSync should keep future authority, retained bytes, recovery usefulness, and stronger recall claims explicit.

**Consequences:**

- retained-copy truth gains a stable review grammar and receipt model
- workbench and CLI both need explicit byte-retention and recall-verdict sections before revoke/remove-style actions can apply honestly
- linked-surface cleanup can no longer masquerade as universal recall
- future access, exit, and backup-preservation work must distinguish future-stop, retained-copy attestation, delete request, and observed stronger recall


## ADR-088 — Share-authority change needs one reviewed epoch-rotation contract, not key/re-share folklore

**Decision:** Non-trivial share-authority changes should compile to one reviewed authority-epoch model rather than depending on folder-class caveats, key-change notes, or derivative/local-share re-share ritual as the operator contract.

**Why:** Current Resilio docs still let Standard/key-backed and Advanced/certificate-backed shares behave materially differently for permission mutation and reissue, still say key changes do not propagate automatically, and still require remove-and-re-share in some derivative/local-share cases. AnonSync should keep new authority issuance, stale capability residue, derivative migration, and mixed-epoch convergence explicit.

**Implications:**

- share authority gains stable epoch objects, rotation reviews, and rotation receipts
- workbench and CLI both need explicit epoch maps, stale-capability findings, and convergence verdicts before rotation-style actions can apply honestly
- derivative/local-share fallout can no longer masquerade as implementation trivia when it changes what must be rebuilt or reissued
- future compromise, recall, and share-class work must distinguish new-epoch issuance from observed clean retirement of old authority


## ADR-089 — Observer/read-only posture needs one reviewed contract, not permission-label folklore

**Decision:** Non-trivial observer, read-only, viewer, or receive-only semantics should compile to one reviewed observer-posture model rather than depending on permission labels, overwrite-changed-files notes, linked-device workarounds, or local-share caveats as the operator contract.

**Why:** Current Resilio docs still let `read only` mean `local edits suspend sync`, optionally `local edits are overwritten`, unavailable for some linked-device/Advanced-folder combinations, and inherited differently by local shares. AnonSync should keep byte visibility, local-write behavior, onward serving, and projection/class limits explicit.

**Implications:**

- observer posture gains stable contracts, reviews, and receipts
- workbench and CLI both need explicit visibility/write/serve/limit sections before observer-style changes can apply honestly
- local repair helpers can no longer masquerade as universal behavior when projection mode disables them
- future grant, derivation, selective-materialization, and recall work must distinguish non-authoritative writing from non-serving and from byte invisibility


## ADR-090 — Non-empty target bind work needs one reviewed reconciliation contract, not `Folder not empty` folklore

**Decision:** Adopting, repairing, or relocating a share into a populated target must expose one reviewed reconciliation contract whenever same-path divergence, ambiguous lineage, or encrypted-target mismatch is present.

**Why:** Current Resilio docs say reconnect can reuse an old directory by ignoring the non-empty warning, that pre-populated folders are hashed and merged while same-named divergent files let the latest timestamp win, and that encrypted-folder intake into a non-empty target can ignore existing plaintext bytes or archive previously encrypted ones. AnonSync should not inherit one small confirmation box as the operator contract for those materially different outcomes.

**Implications:**

- compare counts alone are not the full contract once same-path divergence exists
- timestamp freshness may contribute evidence, but it is not a hidden trustworthy winner rule
- same-lineage reuse, harmless merge, reviewed replacement, and encrypted-target mismatch remain visibly distinct outcomes
- apply emits a reconciliation receipt that proves the chosen lineage and candidate-handling result later


## ADR-091 — Visibility and retrievability are separate public contracts

**Decision:** Introduce explicit fetchability/full-copy-witness objects so placeholder visibility, names-only visibility, and durable byte retrievability never collapse into one casual `available on demand` claim.

**Why:** Current Resilio docs say Selective Sync can expose placeholders without full bytes, reverting files to placeholders can leave nobody with a real file if every peer does it, `Clear synced files` can dematerialize an entire local share, and ghost announcements can persist after no peer still has the bytes. AnonSync should not force operators to reconstruct whether a visible path is actually fetchable from placeholder state plus troubleshooting warnings.

**Consequences:**

- fetchability, full-copy witnesses, local-last-copy risk, and ghost-announcement posture become explicit reviewed state
- evict/clear/pin/fetch actions can fail closed when they would remove the last known full copy or rely on stale announcement-only visibility
- workbench, CLI, and API can render the same honest answer to `can I still get the bytes later?` without support-article archaeology



## ADR-092 — File availability must be a concrete interface contract, not only a conceptual truth

**Decision:** Every serious file/subtree availability surface must render one compact answer strip, one reviewed detail grammar, and one mixed-risk batch model rather than leaving clients to improvise around placeholder state.

**Why:** `rev0078` established that visibility, local residency, full-copy witnesses, and fetchability are different truths. Without a concrete interface contract, clients can still collapse those truths back into one optimistic `available on demand` label or one misleading bulk action.

**Consequences:**

- workbench, CLI, and API-backed clients inherit one stable availability reading order
- mixed-risk subtree actions split by witness/fetchability class before apply
- receipts can later prove not just that an action happened, but which availability truth justified it

## ADR-093 — Availability surfaces need an explicit action matrix, not just state chips

**Decision:** Availability reports must carry explicit per-row and per-selection action offers so the primary verb changes with the risk class instead of being invented independently by each client.

**Why:** `rev0079` made file availability a concrete interface contract, but an honest answer strip still leaves one dangerous gap if clients can keep rendering the same optimistic `Fetch` or `Evict` button after the posture has already changed to local-last-copy, history-backed-only, or stale visibility. The product needs an explicit action contract, not just posture chips.

**Consequences:**

- clients receive row-level action offers such as `fetch-now`, `pin-locally`, `restore-from-history`, or `retire-stale-announcement`
- mixed-selection bars may only label the safe subset they can mutate honestly
- history-backed-only rows no longer masquerade as ordinary on-demand fetch cases


## ADR-094 — Availability rows must keep state, source, and verb adjacent, and direct action must be gated by risk class

**Decision:** Availability rows and cards must expose local truth, source/recovery truth, and next honest action in one adjacent presentation contract, and only clearly safe rows may offer one-click mutation without opening review.

**Why:** `rev0080` made the action matrix explicit, but a safer model can still regress if a dense table hides source posture in one column, action in another menu, and review state somewhere else. The operator needs to see the honest verb near the row it belongs to, and the UI needs one cross-client rule for when inline action is allowed versus when review is required.

**Consequences:**

- row/action contracts gain presentation hints such as `inline-direct`, `inline-review`, and `blocked`
- workbench, CLI, and compact/mobile clients inherit the same direct-action threshold instead of inventing their own
- guarded/history-backed/stale rows pivot naturally into review instead of pretending to support the same one-click action shell as safe rows



## ADR-095 — Share announcement, local claim, and local bind must be separate durable objects

Resilio's current linked-device docs still show a useful but too-entangled convenience model:
shares become visible everywhere across the linked set, careful custom placement often routes through `Disconnected`, duplicate-index directories can appear from default-location behavior, and removing a disconnected item can affect all linked devices.
Those are not fatal flaws.
They are evidence that announcement, claim, bind, and wider withdraw still live too close together.

AnonSync therefore chooses a stricter contract:

- a share may become visible on a machine without creating a local path
- a machine may defer or hide that visibility locally without pretending wider authority changed
- claiming a share is a durable local decision object
- binding a claim into a path is a distinct act with its own compare/preflight/reconciliation hooks
- wider withdrawal must stay visibly different from local hide

Consequence:
incoming objects, claims, receipts, and workbench surfaces must preserve these distinctions explicitly, even on dense/mobile/textual surfaces.

## ADR-096 — Approval convenience must expose acting seat and horizon, not just a generic `Approve` button

Resilio's current docs still show a useful but too-entangled approval model:
linked devices act as Owners for the user's own shares, a request can be approved from any linked device where the folder is active, and a remote user can choose to auto-approve all linked devices for future sharing after approving one.
Those are not fatal flaws.
They are evidence that acting seat, current-subject approval, and future approval memory still live too close together.

AnonSync therefore chooses a stricter contract:

- every approval-worthy request names the acting seat explicitly
- `approve once` and `approve for reviewed scope` are different durable actions
- seat changes may alter admissible horizon and must render that delta explicitly
- future approval memory may never be created by implication from a generic `Approve` action
- approval receipts must later prove which seat spoke and what horizon was accepted

Consequence:
approval queues, review panes, CLI verbs, API objects, and receipts must preserve seat/horizon truth explicitly, even on dense/mobile/textual surfaces.


## ADR-097 — Remembered approval must match explicitly and admit narrowly, not silently complete later local acts

### Status

Accepted

### Context

The archive already says that acting seat and approval horizon must be explicit at the live approval moment.
What still remained too easy to blur was what happens later when a new arrival matches prior trust.
Current Resilio docs still say prior approval can make later pending folders auto-connect, prior approval may be retained with identity/certificate for later sharing, and approval can be widened to linked devices for future sharing.
That is useful convenience, but it leaves too much room for remembered trust to silently explain later local state changes.

### Decision

AnonSync will model remembered-trust reuse through explicit approval-match objects and review surfaces.
A match may authorize only narrow outcomes such as `identity-only`, `queue-admitted`, or `claim-suggested`.
A match will not, by itself, choose a path, create a bind, materialize bytes, or widen rights.
Those later local acts remain separate reviewed outcomes with their own receipts.

### Consequences

Positive:

- remembered trust remains useful without becoming magical
- incoming-share convenience stays compatible with least privilege and truthful local-claim semantics
- later audit can prove whether the product merely recognized prior trust or actually changed local state

Negative:

- some flows will feel less magical than auto-connect products
- the model adds approval-match objects and receipts that simpler products hide
- operators may sometimes feel they are doing one extra explicit claim step after a helpful match


## ADR-098 — local share posture and future-arrival policy must be decomposed, not flattened into one mode field

**Decision:** AnonSync will expose current local share posture and future-arrival policy as separate durable objects and review surfaces instead of using one monolithic mode label.

**Why:** Current Resilio docs still show `Disconnected`, `Selective Sync`, and `Synced` as useful convenience labels, but those same docs also keep using them to imply future-arrival handling, default-location behavior, custom-location workflow, and collision fallback. An inspectable product should not force operators to infer whether they changed the current share, later arrivals, or both from one `change mode` action.

**Consequences:**

- current share posture, future-arrival defaults, and path provenance become first-class public model elements
- seat-level convenience can still exist, but it must state whether it affects current subjects, future arrivals, or both
- workbench, CLI, and API can all render `change current share here` separately from `change what happens next time here`


## ADR-099 — path suggestion and collision fallback need one reviewed placement contract, not `Connect` folklore or silent duplicate suffixes

**Decision:** Treat candidate placement as an explicit suggestion/review/receipt pipeline.

**Why:** Current Resilio docs still show default roots, `Disconnected`/`Connect`, and duplicate `(1)` folders doing too much work in the operator story. AnonSync should preserve helpful path suggestions without letting suggestion, commitment, and collision fallback blur together.

**Implications:**

- candidate paths are explicit objects with suggestion basis and collision class
- same-lineage adoption and alternate-path choice are explicit reviewed outcomes
- a one-share alternate path does not silently rewrite future templates/defaults
- placement receipts must prove which candidate won, which candidates were rejected, and whether defaults changed


## ADR-100 — standing future-arrival defaults need one reviewed template-governance contract, not scattered mode/default/simple-mode folklore

### Status
Accepted

### Context

The archive already separates current share posture from future-arrival policy and one-share placement review from broader defaults.
Current Resilio docs still show standing future-arrival behavior spread across linked-device modes, default-folder settings, custom-location reconnect ritual, and Android `Simple mode`.
That is practical convenience, but it still leaves operators reconstructing one seat's future behavior from several scattered knobs.

### Decision

AnonSync will model standing future-arrival behavior as an explicit seat-template policy with explicit governance review, explicit effect buckets, explicit pinned exceptions, and explicit receipts.
Changing this template will never silently relocate already bound shares.
Refreshing existing unclaimed drafts will require its own explicit choice.

### Consequences

- clients gain one public object for standing convenience instead of inferring it from current-share actions
- policy changes can preview future unseen arrivals separately from open drafts and bound shares
- mobile/dense clients may compress wording, but they must still preserve governed scope and unchanged-subject guarantees
- the product avoids recreating `change mode` / `default folder` folklore as a hidden control plane for future arrivals


## ADR-101 — later-arrival convenience must compile to one explicit explanation surface

### Status
Accepted

### Context

The archive now separates announcement, approval memory, standing seat templates, claim, placement, and bind.
What still remained too easy to hide was the operator question that comes after those decisions already exist: why is this subject in this stage on this machine right now?
Current Resilio docs still answer that question only indirectly through linked-device visibility, remembered approvals, pending-folder auto-connect behavior, standing modes, default roots, and later `Connect` ritual.

### Decision

AnonSync will require one first-class arrival-explanation surface for later-arrival subjects.
That surface must render current stage, causal chain, governing standing state, explicit non-causes, counterfactuals, next honest verbs, and proof links in one place.
Remembered approval and standing template may explain lower friction or drafted candidates, but they must explicitly say whether they changed local state or merely influenced review posture.

### Consequences

Positive:

- later-arrival convenience becomes auditable rather than magical
- support burden falls because `why here now` has one public answer surface
- richer and denser clients can share one explanation contract without inventing new semantics

Negative:

- the model adds one more read projection family and counterfactual machinery
- some compact surfaces will need to spend space on non-causes and counterfactual entry points
- implementers have to keep explanation recomputation aligned with the underlying state graph so stale summaries do not mislead


## ADR-102 — standing-policy edits need one explicit retroactivity preview contract

### Status
Accepted

### Context

The archive now separates standing templates, remembered approval, current share posture, path bind, and later-arrival explanation.
What still remained too easy to blur was the mutation boundary when one of those standing defaults changes.
Current Resilio docs still answer that boundary only indirectly through linked-device modes, default roots, remembered approval, pending-folder auto-connect, and Android `Simple mode`, while also noting that selected mode changes apply to newly added folders and current ones remain as they are.

### Decision

AnonSync will require one first-class policy-delta preview surface for meaningful standing-policy edits.
That surface must render governed scope, proposed delta, effect buckets, named example subjects, explicit non-effects, honest apply labels, and proof links in one place.
A standing-policy mutation may alter future unseen arrivals immediately, may optionally refresh some open drafts, and may require subset review for some claimed subjects, but it must explicitly prove when bound subjects and current bytes stay untouched.

### Consequences

Positive:

- operators can review retroactivity directly instead of inferring it from folklore
- safer `future only` versus `refresh drafts` versus `subset review` labels become portable across GUI, CLI, and mobile
- the non-clone case against Resilio stays focused on contract shape rather than pretending the product lacks convenience

Negative:

- the model adds one more preview family and simulation/projection cost
- compact clients must spend space on explicit non-effects and named examples
- implementers must keep effect buckets aligned with live subject state so previews do not go stale or misleading



## ADR-103 — standing-policy families need explicit version lineage and per-subject attribution

### Status
Accepted

### Context

The archive now previews standing-policy edits before apply and explains why later-arrival subjects are here now.
What still remained too easy to lose was the link between those two surfaces after time passes.
Current Resilio docs still make this seam concrete by describing standing modes, remembered approval, later auto-connect behavior, and default-root/mobile placement semantics in ways that are useful in the moment but still leave older subjects explained mostly by reconstruction.

### Decision

AnonSync will model every meaningful standing-policy family as a versioned lineage with explicit supersession and explicit per-subject attribution.
A client must be able to show the current effective version, the applied version that handled one subject, the semantic difference between them, and the receipts that prove both the policy transition and the subject stage.

### Consequences

Positive:

- operators can tell whether a subject matches current policy or is truthfully grandfathered
- later support and audit work no longer depend on comparing current settings with memory
- policy-delta preview and arrival explanation now connect through one durable version model

Negative:

- the model adds one more read family and more historical indexing
- compact clients must spend some space on version and attribution chips
- implementers must keep lineage/attribution recomputation aligned with mutations so stale compare projections do not mislead



## ADR-104 — standing-policy families need explicit drift classification and reviewed realignment

### Status
Accepted

### Context

The archive now previews standing-policy edits, explains why subjects are here now, and preserves version lineage after policy changes.
What still remained too easy to lose was the operational step after that: deciding which current differences are intentional, which are safe to refresh, and which need stronger review.
Current Resilio docs still make this seam concrete by saying new folders follow the chosen linked-device mode while current ones remain as they are, while later auto-connect, universal visibility, and default-placement ritual can keep the estate heterogeneous over time.

### Decision

AnonSync will model post-lineage operational drift explicitly.
Every meaningful standing-policy family must expose a drift-population view, per-subject drift classes, reviewed realignment plans, and durable exception-pin receipts where intentional divergence is kept.

### Consequences

Positive:

- operators can tell whether a non-current subject is refreshable, intentionally grandfathered, pinned as an exception, or blocked
- policy lineage becomes operationally useful instead of purely historical
- mixed realignment batches no longer need one misleading umbrella action

Negative:

- the model adds another read/mutation family and more classification work
- compact clients must spend some space on drift classes and split action bars
- implementers must keep drift classification aligned with lineage, current state, and exception pins so stale rows do not mislead



## ADR-105 — intentional exceptions need explicit aging, renewal, and re-review

### Status
Accepted

### Context

The archive now previews standing-policy edits, preserves lineage, and classifies live drift with reviewed realignment.
What still remained too easy to lose was the lifecycle after an operator intentionally keeps an older outcome.
Current Resilio docs still make this seam concrete by retaining person-approval memory, allowing later auto-connect after prior approval, and allowing future linked-device approval widening, but without one explicit review-horizon contract for those remembered conveniences.

### Decision

AnonSync will model intentional non-current outcomes as aging reviewed state.
Every meaningful standing-policy family that permits `keep grandfathered` or `pin exception` must expose exception-aging rows, review horizons or explicit no-expiry acknowledgements, renewal/reconsideration review plans, and durable exception-review receipts.
Reaching a review horizon may raise urgency or queue review, but it must not silently mutate binds, bytes, or authority.

### Consequences

Positive:

- operators can tell whether an intentional exception is healthy, due soon, overdue, or explicitly acknowledged as no-expiry
- pinned exceptions stop behaving like immortal background clutter
- remembered convenience stays auditable over time instead of turning into silent forever-policy

Negative:

- the model adds another review family and more queue pressure
- compact clients must spend some space on aging class and horizon facts
- implementers must keep review-horizon computation aligned with drift, lineage, and current state so stale due-soon signals do not mislead

## ADR-106 — remembered approval needs explicit freshness, cooling, and touch-renewal

### Status

Accepted

### Context

The archive already had first-approval review, later matched-arrival guardrails, policy lineage, drift classification, and exception aging.
What still remained under-specified was remembered approval itself.
Without one explicit freshness lifecycle, old approval would keep behaving like timeless convenience memory, especially after dormancy, linked-device growth, or scope change.

Current Resilio docs still make that seam concrete in a useful way: approve-once identity retention, future auto-approval across linked devices, and later auto-connect after prior approval all remain convenient, but they still lack one first-class surface for cooling, freezing, or reviewed touch renewal of remembered trust itself.

### Decision

Every meaningful remembered-approval family that can influence later arrivals must expose approval-memory freshness rows, cooling reasons, reviewed touch-renewal or narrowing plans, and durable freshness receipts.

Freshness is not the same thing as arrival claim.
Touch renewal must therefore remain a trust-memory mutation only; it may not silently claim, bind, materialize, or widen scope.

### Consequences

- remembered approval is now a lifecycle object rather than immortal background memory
- later-arrival explanation must include the freshness posture of the matched trust, not merely the existence of a match
- dense/mobile clients must keep `fresh`, `warm`, `cooling`, `stale`, `frozen`, `revoked`, and `unknown` visibly distinct
- any batch trust-refresh surface must split rows by truthful reviewed outcome rather than flattening them into `keep approved`


## ADR-107 — remembered approval needs explicit lineage and subject-level authorization trace

### Status

Accepted

### Context

The archive already had first-approval review, later matched-arrival guardrails, approval-memory freshness, and touch renewal.
What still remained under-specified was attribution.
Without one explicit lineage and authorization-trace model, the operator could know that trust was still fresh enough to matter while still not knowing which exact old approval act or later trust mutation actually authorized the current convenience.

Current Resilio docs still make that seam concrete in a useful way: approval can be retained with identity, approvals can be issued from any linked device, future linked devices can be auto-approved after one approval, later pending folders can auto-connect after prior approval, and approval-time details are visible at request review time. That is useful provenance material, but it is still not one first-class later trace surface.

### Decision

Every meaningful remembered-approval family that can influence later arrivals must expose explicit lineage nodes, ordered authorization history, and per-subject authorization-trace explanations.
Later trust mutations must supersede by adding lineage, not by overwriting origin history.
A later subject that cites remembered trust must be able to point to one explicit authorization node or else surface `unknown` attribution posture.

### Consequences

- remembered approval is now an attributable lineage rather than only a freshness-colored memory
- later-arrival explanation must include which trust node authorized the subject, not merely that prior approval existed
- dense/mobile clients must preserve origin-versus-current-head distinctions even when they compress wording
- missing trust provenance becomes an explicit proof problem rather than a guessed success story

## ADR-108 — remembered approval must support family split/rebase after constellation mutation

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, and current-vs-historical trust comparison.
What still remained too easy to lose was the effect of identity/constellation mutation on old remembered approval itself.
Current Resilio docs still make this seam concrete by saying all linked devices act as Owners, approvals can be issued from any linked device, one approval can expand to all linked devices for future sharing, hidden offline devices can later reappear without having been unlinked, linking already-initialized devices can cause certificate takeover, and remote unlink is not available.

### Decision

AnonSync will model remembered approval as a family that may need reviewed rebase after constellation mutation.
Every meaningful remembered-approval family affected by identity/constellation change must expose a triggering mutation, descendant postures, reviewed rebase plans, and durable rebase receipts proving whether the family stayed intact, split into child families, froze descendants, or now requires fresh approval for selected descendants.

### Consequences

Positive:

- operators can tell whether hidden-device return or certificate takeover changed future trust reuse without losing historical explanation
- trust continuity becomes reviewable rather than ambient when the device set behind an identity changes
- future reuse and historical explanation stay separate after constellation mutation

Negative:

- the model adds another trust-lifecycle family and more descendant bookkeeping
- compact clients must spend some space on mutation triggers and descendant outcomes
- implementers must keep rebase logic aligned with freshness, lineage, identity epochs, and constellation membership so stale descendant posture does not mislead

## ADR-109 — remembered-trust descendants must expose liveness and confidence separately from family membership

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, family rebase, and descendant postures after constellation mutation.
What still remained too easy to overstate was present-tense descendant reality.
Current Resilio docs still make this seam concrete by saying selective-sync fetch requires at least one online peer with the files, peer lists distinguish online peers from peers ever seen, hidden offline devices may later reappear, and ghost-file guidance shows that visible names can outlive current byte sources.

### Decision

AnonSync will model descendant liveness as a first-class layer separate from remembered-family membership.
Every meaningful remembered-trust descendant must expose a liveness class, confidence class, evidence basis, current honest role, reviewed liveness-refresh outcomes, and durable receipts proving whether the descendant is live observed, recently live, reachable but unproven, hidden awaiting return, reappeared awaiting proof, historical only, or unknown.

### Consequences

Positive:

- operators can tell when remembered-trust family membership is historical explanation rather than current operational convenience
- byte-source and approval-seat claims become evidence-backed instead of implied by lineage or placeholder presence
- reappeared descendants can remain visible without silently regaining strong convenience rights

Negative:

- the model adds another per-descendant posture family and more witness bookkeeping
- compact clients must spend some space on liveness/confidence rather than only inheritance posture
- implementers must keep liveness evidence aligned with fetchability, dormant-return, and trust-lineage receipts so present-tense claims do not outrun proof

## ADR-110 — descendant liveness must stay separate from per-subject role eligibility

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, family rebase, descendant liveness, and reachability confidence.
What still remained too easy to over-claim was present-tense subject capability.
Current Resilio docs still make this seam concrete by saying approvals can be issued from any linked device where the folder is active, all linked devices act as Owners, later pending folders can auto-connect after prior approval, and selective-sync fetch still requires at least one online peer with the bytes.

### Decision

AnonSync will model descendant role eligibility as a first-class layer separate from family membership and separate from liveness.
Every meaningful remembered-trust descendant considered for a governed subject must expose a candidate role, an eligibility class, a proof basis, reviewed capability outcomes, and durable receipts proving whether that descendant may honestly count as a byte source, an approval seat, both, or neither for the subject now.

### Consequences

Positive:

- operators can tell when a live linked descendant is still not actually eligible to approve or serve the governed subject
- byte-source and approval-seat claims become explicitly per-subject instead of ambient device folklore
- remembered approval, linked ownership, and live presence remain useful evidence without silently becoming the verdict

Negative:

- the model adds another per-descendant/per-subject posture family and more proof bookkeeping
- compact clients must spend some space on candidate-role and eligibility language instead of a vague `available` badge
- implementers must keep capability proofs aligned with liveness, approval-seat review, fetchability, and policy narrowing so subject-specific claims do not outrun evidence


## ADR-111 — remembered approval reuse must stay separate from subject-level fresh-approval override policy

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, family rebase, descendant liveness, descendant capability, and per-subject role eligibility.
What still remained too easy to over-claim was approval reuse itself.
Current Resilio docs still make this seam concrete by saying later pending folders can auto-connect after prior approval, approval can be retained with a person's identity, linked devices can broaden future approval reach, and the share dialog can separately require approval from `all peers` even when they were approved before.

### Decision

AnonSync will model subject-level approval-reuse precedence as a first-class layer separate from standing remembered approval and separate from descendant capability.
Every meaningful governed subject that might inherit old approval convenience must expose a standing reuse candidate, a subject reuse policy, a precedence outcome, a winning-rule explanation, reviewed override outcomes, and durable receipts proving whether remembered approval may or may not be reused for that subject.

### Consequences

Positive:

- operators can tell when old approval still exists but this subject intentionally requires fresh approval anyway
- share/offer security policy stops being hidden folklore and becomes an inspectable part of the approval surface
- descendant eligibility remains useful evidence without silently becoming permission to skip review

Negative:

- the model adds another subject-level policy layer and more precedence bookkeeping
- compact clients must spend some space on subject-policy and winning-rule language instead of a vague `already approved` badge
- implementers must keep reuse-policy precedence aligned with freshness, lineage, capability, and actual approval actions so lower-friction paths do not outrun the governing subject policy


## ADR-112 — portable invitation lifetime must stay separate from durable trust promotion

### Status
Accepted

### Context

The archive now preserves offer-artifact semantics, approval freshness, authorization lineage, descendant capability, and subject-level reuse-policy precedence.
What still remained too easy to over-claim was the afterlife of a successful invitation.
Current Resilio docs still make this seam concrete by saying share links can expire after `N` days or `N` uses while other current docs still say approval is retained with a person's identity for later sharing and that approval mints certificate-backed access.

### Decision

AnonSync will model offer-artifact trust promotion as a first-class layer separate from artifact redemption lifetime and separate from later subject-level reuse-policy precedence.
Every meaningful portable invitation that can survive its own redemption as durable remembered approval must expose artifact terminal posture, claim outcome, promotion posture, promotion-scope basis, later-reuse posture, reviewed promotion outcomes, and durable receipts proving what trust survived the invitation and what did not.

### Consequences

Positive:

- operators can tell when a single-use or expiring invitation admitted one subject without silently creating broad remembered approval
- offer-artifact controls remain useful without having to carry all later trust semantics by implication
- later approval reuse can still exist, but only after explicit promotion and later reuse-policy checks

Negative:

- the model adds another after-claim posture family and more receipt bookkeeping
- compact clients must spend some space on artifact-lifetime versus trust-lifetime language instead of a vague `invite used` badge
- implementers must keep promotion outcomes aligned with offer policy, approval actions, subject reuse policy, and approval-memory lineage so later convenience does not outrun reviewed scope

## ADR-113 — sender intent, actual redeemer identity, and durable trust must stay separate for portable offers

### Status
Accepted

### Context

The archive now preserves portable-offer lifetime, trust-promotion boundary, approval freshness, authorization lineage, descendant capability, and subject-level reuse precedence.
What still remained too easy to over-claim was *who the offer was really redeemed by*.
Current Resilio docs still make this seam concrete by saying share links can be copied into messenger or e-mail, any peer with the link can auto-connect when approval is disabled, and approval review plus link flow identify the actual requester by name/fingerprint/public key and then mint certificate-backed access.

### Decision

AnonSync will model recipient intent and actual redeemer identity as a first-class layer separate from portable-offer lifetime and separate from durable trust promotion.
Every meaningful portable offer that can travel by possession must expose sender-intent posture, actual redeemer proof, match class, reviewed mismatch outcomes, and durable receipts proving what trust boundary followed from that exact redeemer.

### Consequences

Positive:

- operators can tell whether the person/device who redeemed the offer is actually the one the sender meant it for
- portable-offer convenience remains useful without pretending successful redemption automatically satisfied sender intent
- later remembered approval can be traced back to one exact redeemer and one explicit mismatch decision

Negative:

- the model adds another offer-side provenance layer and more receipt bookkeeping
- compact clients must spend some space on `for` versus `redeemed by` language instead of a vague `accepted` badge
- implementers must keep mismatch outcomes aligned with claim receipts, trust-promotion outcomes, and later reuse policy so broad convenience does not outrun reviewed intent


## ADR-114 — portable-offer budget and per-redemption trust must stay separate

**Status:** Accepted

**Context:** Current Resilio docs still combine useful but separable ideas: a link may be used only `N` times by whoever, some peers may auto-connect based on prior approval, and successful approval generates certificate-backed access for the actual requester. Once more than one redeemer hits the same artifact, operators otherwise have to reconstruct from use-counts, approval dialogs, and later remembered approval which identities consumed which budget and what trust survived.

**Decision:** AnonSync will model multi-use offer history through first-class redemption-ledger rows, ordered attempt entries, budget explanations, and trust-fanout receipts instead of leaving that story inside raw offer history.

**Consequences:**

- artifact budget becomes a first-class surface distinct from per-redeemer trust meaning
- `partially consumed` becomes its own stable public state
- later remembered approval can trace back to one exact successful redemption attempt rather than only to the parent artifact
- UI/API must support `reissue new artifact` as a first-class safe action when mixed attempt history exists

## ADR-115 — redemption equivalence and slot treatment must be first-class

**Status:** Accepted

**Context:** Current Resilio docs still combine bounded-use links, prior-approval reuse, and per-requester approval identity in a way that leaves one remaining accounting seam: once a familiar redeemer hits the same artifact again, operators otherwise have to reconstruct whether the later event was a replay, the same reviewed seat on the same subject, the same known peer on a new subject, or a genuinely distinct redeemer that deserves a fresh slot.

**Decision:** AnonSync will model redemption equivalence and slot treatment as a first-class layer with explicit equivalence rows, accounting explanations, reviewed outcomes, and receipts instead of leaving slot consumption to raw attempt order or vague `already approved` language.

**Consequences:**

- remaining budget becomes a first-class fact but not the only fact
- familiar redeemers still need explicit equivalence class and slot-effect language
- replay collapse, fresh-slot consumption, and `require new artifact` become distinct reviewed outcomes
- UI/API must support comparison-attempt links and accounting receipts whenever portable-offer history matters


## ADR-116 — successor artifacts must have explicit predecessor lineage and budget-reset truth

**Status:** Accepted

**Context:** Current Resilio docs still say expired links require a new link from the owner, bounded-use links fail at `N+1`, and remembered approval can still survive separately across later sharing. Once the product already knows the right answer is `require new artifact`, operators otherwise still have to reconstruct whether the replacement is just another wrapper for the same invitation story or a genuinely fresh boundary with narrower policy and reset budget.

**Decision:** AnonSync will model reissue lineage and successor-boundary review as a first-class layer with predecessor posture, successor relation, budget-reset posture, explicit carry-forward summaries, non-carry summaries, and durable successor-boundary receipts.

**Consequences:**

- `reissue new artifact` becomes a reviewable governance act rather than a shallow convenience verb
- successor artifacts can honestly say whether they are same-scope, narrowed, broadened, fresh-scope, or delivery-only
- delivery-only copies stop masquerading as fresh budget islands
- UI/API must support predecessor/successor receipts so later audit can tell what really changed at reissue time


## ADR-117 — delivery preview must stay separate from authoritative local intake

### Status

Accepted

### Context

Portable offers now have first-class objects for sender intent, actual redeemer identity, budget, multi-redemption history, slot treatment, and successor lineage.
One remaining seam still risked collapsing too much into one vague story: browser landing pages, QR overlays, clipboard intake, and external-app handoff can show useful preview information before the local app has actually performed authoritative inspection.

Current Resilio docs make that seam real in a useful way: links open a landing page that shows basic folder info, may immediately transfer into the app if protocol launch is already trusted, and keep the `#` fragment out of the landing-page request.
That is useful convenience and useful privacy posture, but it still leaves too much room for an operator surface to blur `previewed outside the app` with `authoritative inside the app`.

### Decision

AnonSync will model **delivery events** separately from offer artifacts, claim preparation, and later trust consequences.
Every portable-offer intake path must preserve at least these distinct public facts:

- delivery channel
- preview surface
- external-touch posture
- handoff posture
- preview-authority posture
- authoritative offer reference once local parsing succeeds

The interface must keep preview hints, local parse results, and authoritative review truth visibly separate.
`Opened in browser`, `auto-launched app`, or `previewed folder name` can never stand in for trust, byte availability, claim readiness, or remembered approval.

### Consequences

Positive:

- browser/app convenience remains usable without becoming trust folklore
- external-touch privacy posture becomes inspectable public state
- later audit/support work can reason from delivery receipts instead of browser-memory guesswork

Costs:

- intake surfaces gain one more layer of row/detail state
- APIs and logs need a delivery-event object family in addition to offer and claim objects
- lightweight clients must compress the story carefully without hiding the preview-versus-authority boundary

### Alternatives rejected

- treat browser landing-page preview as just another offer inspect result
- bury delivery provenance only in debug logs
- collapse `auto-opened successfully` into a generic success badge


## ADR-118 — carrier aliases must collapse into canonical artifact identity before later semantics are inferred

### Status

Accepted

### Context

Portable offers now have first-class objects for sender intent, redeemer identity, artifact budget, repeated-attempt equivalence, successor lineage, and delivery/handoff provenance.
One remaining seam still risked collapsing too much into one vague story: the same offer may appear through browser wrapper URLs, protocol rewrites, QR encodings, clipboard copies, or later file wrappers.

Current Resilio docs make that seam real in a useful way: links use an `https://link.resilio.com/...#...` wrapper, the landing page may rewrite that wrapper to `btsync://` for the app, the `#` fragment is not sent to the server, and the same share can also be delivered as copied text or QR.
That is useful convenience, but it still leaves too much room for a surface to blur carrier convenience with artifact identity.

### Decision

AnonSync will model **carrier aliases** separately from canonical offer identity, delivery events, claim objects, and successor artifacts.
Every meaningful portable-offer surface must preserve at least these distinct public facts:

- canonical artifact reference
- carrier kind
- carrier authority posture
- equivalence posture
- normalization basis
- explicit non-effects on budget/trust/lineage

Budget, trust consequence, successor lineage, and later audit attach to the canonical artifact identity, not to whichever carrier happened to be observed last.

### Consequences

Positive:

- browser wrapper, protocol handoff, QR, and copied text can all stay convenient without forking hidden artifact stories
- delivery-only re-encoding stops masquerading as reissue
- later audit/support work can reason from canonical artifact receipts instead of browser-history guesswork

Costs:

- intake surfaces gain one more layer of alias/detail state
- APIs and logs need a carrier-alias object family in addition to offer and delivery-event objects
- lightweight clients must compress the story carefully without hiding whether the current carrier is authority-bearing or merely a wrapper

### Alternatives rejected

- treat whichever carrier last reached the seat as the artifact identity
- bury alias normalization only in debug logs
- infer `same offer` from folder-name hints or familiar wrapper shape alone


## ADR-119 — preview-visible hints must remain separate from sealed and authoritative offer fields

### Status

Accepted

### Context

Portable offers now have first-class objects for delivery provenance, canonical artifact identity, carrier aliases, redemption accounting, and successor lineage.
One remaining seam still risked collapsing too much into one vague story: some surfaces may show recognition hints before local parse, while authority-bearing or policy-bearing fields stay sealed until the app ingests them.

Current Resilio docs make that seam real in a useful way: the landing page can show basic folder info, the wrapper may hand off into the app, and the `#` fragment is not sent to the server.
That is useful convenience, but it still leaves too much room for a surface to blur preview familiarity with authoritative field truth.

### Decision

AnonSync will model **offer field provenance and field partition** separately from carrier alias identity, delivery events, claim objects, and later approval artifacts.
Every meaningful portable-offer surface must preserve at least these distinct public facts:

- field semantic role
- field exposure posture
- field authority posture
- which later actions may rely on the field
- which later actions explicitly may not rely on the field
- receipts proving that partition

Alias collapse, local parse, claim review, and trust review must not erase the earlier fact that some fields were only hints while others stayed sealed until parse.

### Consequences

Positive:

- preview convenience remains useful without becoming authority folklore
- sealed authority-bearing material becomes explainable rather than mysterious
- later governance decisions can cite exact field classes instead of over-reading preview familiarity

Costs:

- intake surfaces gain one more compact strip or drawer of state
- APIs and logs need a field-provenance object family in addition to offer, delivery-event, and carrier-alias objects
- lightweight clients must compress the story carefully without hiding non-inference boundaries

### Alternatives rejected

- treat any previewed field as authoritative enough for later claim or trust steps
- bury field partition only in debug logs
- let alias collapse erase field-exposure history


## ADR-120 — preview usefulness must publish decision sufficiency and omission truth

### Status

Accepted

### Context

The archive already distinguishes delivery provenance, canonical artifact identity, and field-partition truth for portable offers.
However, one gap remained: a preview can show enough to make a human feel comfortable without actually showing the governance-bearing fields that should decide permissions, approval posture, expiry, use-count, or later trust consequences.
Current Resilio docs still make this gap concrete by showing a landing page with basic folder info while separate sharing surfaces govern permission, approval, expiration, and use-count behavior.

### Decision

AnonSync will treat preview sufficiency as a first-class public property.
Every portable-offer preview surface must be able to say:

- what it showed
- what governance-bearing fields it omitted
- what decision domains it is sufficient for
- what decision domains remain blocked
- what unsafe inferences are being refused
- what the next honest action is

The product will therefore add dedicated preview-sufficiency rows, omission explanations, review plans, and receipts.
`Recognition sufficient` must never imply `governance sufficient`.

### Consequences

Benefits:

- minimal previews can stay useful without becoming stealth governance surfaces
- omitted fields become explicit product truth rather than invisible absence
- later approval/claim receipts can prove they did not rely on preview familiarity alone

Costs:

- dense intake cards need one more compact summary strip
- APIs and CLI need one more explicit decision-domain model
- operators will see a little more `not enough yet` language during safe intake

### Rejected alternative

Treat `preview hint` versus `authoritative field` as sufficient and leave decision sufficiency implicit.
That was rejected because a user can still over-read a perfectly honest hint surface unless the product also says what the hint is *not enough* to decide.
