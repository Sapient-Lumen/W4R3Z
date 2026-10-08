# Operator workbench interface spec

## Purpose

The archive already had a growing object model and a CLI/API contract.
What it still lacked was a concrete answer to a more human question:

> when an operator opens AnonSync, what should they actually see first, and how should the surface prevent the same confusion that existing sync tools still create?

This document answers that question.

The intent is **not** to design a flashy consumer UI.
The intent is to specify a high-signal local workbench that can later be realized as GUI, TUI, or richer CLI summaries while staying faithful to the same daemon model.
The more detailed interaction rules live in `39-interface-pattern-language.md` and `41-report-and-intervention-language.md`; this document stays focused on the workbench surfaces themselves.

## Core stance

1. The interface is a **workbench**, not a folder browser with scattered warning badges.
2. The home surface is an **attention organizer**, not a raw device/share table.
3. A share page must separate at least five things that sync products often blur together:
   - share visibility
   - local path adoption
   - local materialization state
   - authority / grant posture
   - destructive-risk posture
4. Derived queue items are summaries, not hidden authority objects.
5. High-risk actions must carry their proof panels with them.
6. Temporary overrides must be visibly temporary.
7. “Idle” is not good enough language when the real question is whether the share is settled enough for cutover, backup, or maintenance.

## Home surface

The home surface should organize work into three lanes:

- `Now` — action is blocked, risky, or time-sensitive
- `Soon` — review is warranted, but not currently burning
- `Quiet` — useful facts and completed or low-risk background state

The goal is to stop the operator from scanning every share and every device just to answer:

- what is blocked
- what is newly visible
- what changed trust posture
- what could widen authority if accepted
- what destructive action is awaiting proof or apply

## Review item types

The home surface should be able to summarize at least these kinds of review items:

- pending peer admission
- newly visible incoming share
- offered capability artifact nearing expiry or awaiting claim
- compatibility or preflight blocker
- plan awaiting apply
- conflict awaiting review
- deviation detected on a non-authoritative mount
- transport runtime degraded
- convergence degraded for an important intent
- settlement barrier stale or blocked for an active plan
- retirement / successor review
- route lease or override nearing expiry
- recurring activity window activating soon or affecting a surprising phase
- release skew, blocked upgrade plan, or accepted compatibility boundary needing review

Each review item should show:

- a concise title
- a stable object kind and ID
- report type, severity, and freshness
- why it is in this lane now
- the primary recommended action
- any attached proof objects (`preflight`, `convergence`, `settlement`, `preservation`, `exposure`, `comparison`)
- whether dismissing/snoozing the card changes real state or only queue presentation

## Global navigation

A minimal workbench should have these primary sections:

1. `Home`
2. `Shares`
3. `Constellation`
4. `Exits & Replacement`
5. `Peers`
6. `Transfers`
7. `Policies`
8. `Disclosure`
9. `Exceptions`
10. `Attention`
11. `Events & Audit`
12. `Health`
13. `Diagnostics`
14. `Access`
15. `Releases`
16. `System State`

This is intentionally smaller than the raw object graph.
The interface should compress the model **only where the compression stays honest**.

## Report shelf

The workbench should also expose a dedicated `Reports` shelf or filterable report board.
A mature workbench should pair this with an `Offers` shelf for sender-side artifact inventory and receiver-side intake, so portable authority does not disappear into whatever widget happened to export the QR or copied the URI.
This is not because operators should browse reports all day.
It is because proof-bearing state needs one stable home that is not tied to whichever page first surfaced the issue.

The report shelf should support:

- filter by type (`preflight`, `comparison`, `preservation`, `convergence`, `settlement`, `exposure`, `disclosure-scope`, `disclosure-residue`, `authority-delta`, `plan-drift`, `activity-effect`, `rollback-conflict`)
- filter by severity and freshness
- jump from report to underlying subject
- jump from subject to its most relevant active report
- distinguish active, superseded, and dismissed reports

A report shelf is especially important on textual and narrow surfaces, where operators may need to move between several risky or degraded states without losing the proof context for each one.


## Attention center

The workbench should also expose an `Attention` center distinct from both the Home board and the Reports shelf.
Its job is not to invent a second semantic model.
Its job is to answer three operator questions cleanly:

- what currently demands action and why
- which channels already carried that condition
- what acknowledgement or snooze changed only presentation versus real subject state

The Attention center should support:

- filter by lane, severity, channel, and delivery outcome
- filter by disposition (`new`, `acknowledged`, `snoozed`, `resolved`)
- jump from attention event to its backing report and subject
- inspect acknowledgement or snooze receipts
- inspect policy and recent delivery failures without leaving the workbench

This page matters most on Linux-first and headless-heavy deployments, where desktop shell affordances are uneven and the product cannot let one notification channel become the semantic source of truth.


## Disclosure page

The workbench should expose a `Disclosure` page distinct from `Policies`, `Transfers`, and `Access`.
Its job is not to become another routing dashboard.
Its job is to answer:

- what audiences currently learn about this daemon, share, or constellation
- whether the learned fact is identity, share-membership, endpoint, or relay-reachability information
- what residual disclosure remains after a recent narrowing change
- what change would widen or narrow that boundary next

The page should support:

- filtering by subject, audience class, fact class, and residual-risk state
- one disclosure drawer showing audience/fact matrix, mechanisms, and decay-or-clearance truth
- comparing baseline and effective disclosure when temporary exceptions are active
- reviewed widening/narrowing changes with direct jumps to receipts
- direct jumps from a share or policy to its latest disclosure report

This page matters because a Linux-first workbench should not force the operator to reverse-engineer what tracker, LAN search, or named endpoints disclose from route success alone.

## Exceptions page

The workbench should also expose an `Exceptions` page distinct from `Policies`, `Attention`, and subject detail pages.
Its job is not to add a second settings hierarchy.
Its job is to answer one operational question cleanly:

- what temporary exceptions are active right now
- what baseline each one is masking or widening
- what ends each one
- which ones overlap in surprising ways

The Exceptions page should support:

- filter by family (`activity`, `route`, `diagnostic-depth`, `access-exposure`, `transfer-budget`, `fidelity-exception`)
- filter by expiry horizon, risk tier, and `no-expiry` acknowledgement
- jump from a subject page to all active exceptions affecting that subject
- show one consistent lease drawer with baseline, active effect, end condition, and receipts
- show cross-domain conflict or overlap findings without forcing page-to-page archaeology

This page matters because a Linux-first workbench should not require the operator to remember that one risky temporary state lives in route, another in diagnostics, and a third in access.

## Report detail drawer / pane

Opening a report from Home, Shares, Peers, or Health should land on one consistent report detail view.
That view should show, in order:

1. current answer
2. severity and freshness
3. scope summary
4. top findings and evidence refs
5. safest next action
6. unresolved aftermath

This is intentionally repetitive.
The operator should not have to relearn one explanation style for convergence, another for delete safety, and another for path binding.

## Frame and persistent regions

Across desktop GUI, local web UI, TUI, and richer CLI summaries, the workbench should preserve the same frame even if the layout collapses differently.

Persistent regions should be:

- a navigation rail or section chooser
- a primary content pane showing the current board, list, or detail page
- a proof / explanation side panel or expandable drawer
- a compact report header strip for active guarded/high-risk findings when relevant
- a compact global status strip for active leases, degraded transports, blocked plans, failed attention deliveries, or high-signal offer artifacts nearing expiry

On narrow surfaces these regions may stack, but they should not disappear conceptually.
The operator should not have to learn one product model for wide screens and a different one for narrow or textual surfaces.

## Exits page

A cross-cutting surface for departure-style actions.
It should not replace domain pages, but it should unify them.

Entry points should exist from:

- device detail / peer detail
- share danger zone
- recovery and replacement views
- disclosure or access pages when a narrow-by-exit action is recommended
- report cards that are fundamentally about decommission, revocation, or replacement

The page should group items into:

- `needs review now`
- `applied with unresolved residue`
- `awaiting peer observation`
- `continuity preserved`
- `fully cleared`

List rows should show at minimum:

- subject label and kind
- reviewed intent label
- freshness / drift state
- residue state (`none`, `time-bound`, `remote`, `unknown-offline`)
- whether continuity is being preserved, transferred, or intentionally destroyed
- one safest next action

A detail drawer should always show, in this fixed order:

1. intent and scope
2. what stops now
3. what stays intentionally
4. what residue remains and where
5. what follow-up can still clear it
6. which exit receipt proves the outcome later

The drawer should not hide any of those sections behind tabs on narrow surfaces.
Layout may collapse, but order and meaning should remain stable.
The richer, narrower rules live in `65-exit-review-and-replacement-interface-spec.md`.

## Access page

The workbench should expose one page for control access: current endpoints, exposure posture, active sessions, token inventory, and recent access receipts.
This page is not deployment garnish.
It is where the product proves that CLI, browser/workbench, automation, SSH-forwarded access, and any reviewed reverse-proxy posture are all talking about explicit public state.

The page should show at least:

- current control access policy summary
- active endpoints with exposure class and risk state
- active sessions by client kind, scope, and expiry posture
- issued tokens with audience, scope, and revocation state
- active mutation grants with scope, binding, batch budget, and expiry posture
- recent mutation-gate results for blocked or elevated dangerous actions
- capability availability by action and channel
- current control-integrity findings for browser compatibility, content blocking, trust/bootstrap posture, and session expiry
- active review handoffs and pending cross-channel parity transitions
- trusted-proxy / hostcheck posture
- recent access and repair receipts and any degraded exposure findings

Its primary actions should be:

- issue interactive or automation access tokens
- inspect a mutation gate for a dangerous action
- issue or revoke a short-lived mutation grant
- revoke a stale session
- prepare a reviewed exposure change
- inspect capability availability and fallback channels
- prepare a review handoff into CLI, TUI, or API-backed control while preserving the same action identity
- open a bounded auth-repair case
- inspect recent access/repair receipts
- inspect why an endpoint or action is blocked or degraded

No mutation on this page should bypass a report, plan, or receipt.

## System State page

The workbench should expose one page for durable operator state: active root, runtime profile, verification posture, and recent state transitions.
This page is not advanced-user ornament. It is where the product proves that background service, local web workbench, maintenance mode, export/import, and recovery are all talking about explicit public state.
When no verified root is open yet, this page should hand off to the bring-up surface rather than pretending startup is already ordinary state.

The page should show at least:

- active state root ID and path
- active service profile, execution seat, and user/principal context
- current path-reachability and notification posture summary
- identity fingerprint summary
- verification freshness and integrity state
- recent attach/move/import/switch transitions
- export/backup/recovery readiness

Its primary actions should be:

- verify active root
- export state
- prepare root move
- attach known root
- prepare profile switch
- prepare reviewed execution-seat switch
- inspect recent transition receipts

No mutation on this page should bypass a report or plan.

## Semantic guarantees and optimization surface

The workbench should expose one dedicated surface whenever a requested speed, compatibility, or troubleshooting change would also weaken an operator-visible guarantee.
This page is not advanced-performance garnish.
It is where the product proves that `faster`, `good enough here`, and `semantically weaker` are not the same conclusion.

The page should show at least:

- current optimization profile and runtime scope
- current detection, rename, delta-transfer, verification, and conflict-honesty posture
- target/runtime findings explaining any current weakness
- guarantee deltas for the requested profile
- restoration requirements and recent optimization receipts

Its primary actions should be:

- inspect current semantic runtime contract
- prepare reviewed degraded-target acceptance
- prepare a stronger-verify / stronger-freshness restoration
- inspect why a proposed optimization is blocked
- inspect recent optimization receipts

No action on this page should collapse into `Advanced`, `Performance`, or `Compatibility` toggles without a report, plan, or receipt when semantics would weaken.


## Retained copies and recall surface

The workbench should expose one dedicated surface whenever an operator changes access and also needs to know what already-delivered bytes still exist.
This page is not merely share membership hygiene.
It is where the product proves that `revoked`, `removed`, and `recalled` are not synonyms.

The page should show at least:

- known peers or peer sets retaining bytes for the share
- current authority posture and future-update posture for each one
- byte posture (`materialized`, `encrypted-only`, `metadata-only`, `unknown`)
- recovery usefulness and any continuity-material dependency
- current recall verdict and outstanding observation requirements
- recent recall receipts and retention attestations

Its primary actions should be:

- inspect retained replica posture
- prepare revoke-future-updates with retained-copy attestation
- prepare request-remote-delete as a stronger, separate action
- preserve encrypted backup while freezing ordinary participation
- inspect why a stronger recall claim is blocked or still unobserved

No action on this page should collapse into a generic `Remove`, `Disconnect`, or `Revoke` button without a report, plan, or receipt when retained-copy meaning is in scope.


## Share authority epochs and rotation surface

The workbench should expose one dedicated surface whenever share authority material changes or is about to change.
This page is not merely about `new key` or `re-share`.
It is where the product proves that `new epoch issued`, `old authority still exists`, `mixed epoch`, and `clean convergence` are not synonyms.

The page should show at least:

- current share-authority epoch and prior known epochs
- authority class for each epoch and current status
- peers, offers, and derivatives still referencing each epoch
- stale-capability posture and convergence verdict
- derivative/local-share migration obligations and follow-on reviews
- recent rotation receipts and any blocked retirement/quarantine follow-up

Its primary actions should be:

- inspect current epoch map
- prepare rotate-authority-material
- prepare upgrade-share-class
- inspect why stale capability cannot yet be retired
- inspect which derivatives or downstream offers still need reissue

No action on this page should collapse into `Rotate`, `Re-share`, or `Upgrade` without a report, plan, or receipt when mixed-epoch or stale-capability meaning is in scope.

## Identity and naming continuity page

The workbench should expose one page for naming a subject without lying about authority continuity.
This page is not profile polish.
It is where the product proves that a typo fix, a peer-visible rename, alias history, and a same-person continuity claim are not the same action.

The page should show at least:

- current label and stable subject handle
- current peer-visible label and visibility scope
- current authority fingerprint summary
- previous labels / aliases
- continuity verdict (`same-authority`, `same-person-new-authority`, `uncertain`, `replacement`)
- current and candidate grant / constellation fallout when relevant
- recent identity-label receipts and any pending peer observation

Its primary actions should be:

- relabel locally only
- prepare peer-visible relabel
- add or retire an alias
- compare a candidate same-person authority claim
- escalate into successor / compromise / constellation review when the continuity story is no longer cosmetic
- inspect recent identity-label receipts

No editable label field on this page should silently regenerate authority, inherit future approvals, or merge subjects just because their names look similar.

## Execution-seat and runtime-profile switch surface

The workbench should expose one dedicated surface whenever a runtime/service-seat change could alter what the same host can actually see or manage: current-user to background service, named-service user to Local System, maintenance or recovery seat, containerized seat, or any switch that weakens notification quality or path reachability.
This page is not installer garnish.
It is where the product proves that `same state, same world`, `same state, rebind required`, `same state but degraded freshness`, and `clean-seat start` are different outcomes.

The page should show at least:

- source seat and target seat with service-profile and principal class
- current state-root/identity continuity expectation
- reachable-target delta and any path-resolution workaround posture
- notification/freshness delta and any rescan-only downgrade
- admissible actions and recent seat-switch receipts

Its primary actions should be:

- keep current seat
- prepare reviewed same-root switch
- prepare reviewed rebind for affected targets
- open a clean-seat start intentionally
- inspect why the switch is blocked or guarded

No mutation on this page should bypass a report, plan, or receipt.

## Target-custody and exclusive-bind surface

The workbench should expose one dedicated surface whenever a local target may already belong to another managed lineage: discovered `.sync`-style markers, removable-media reuse, foreign state-root/service-profile ownership, degraded marker state, or same-host collision suspicion.
This page is not a fancier non-empty-path warning.
It is where the product proves that `ordinary adopt here`, `same-lineage attach`, `successor claim`, `inspect-only preserve`, and `clear abandoned marker` are different actions.

The page should show at least:

- target path, storage tier, and discovered marker state
- current custody and lineage references when ownership can be proven
- requested bind intent and claimed continuity story
- collision/fork/corruption risk and preservation requirement
- admissible custody actions and recent custody receipts

Its primary actions should be:

- reuse verified same-lineage bind
- prepare reviewed attach or successor claim
- preserve evidence and inspect only
- inspect why cleanup is blocked or guarded
- apply reviewed cleanup only when preservation truth is explicit

No mutation on this page should bypass a report, receipt, or explicit preservation acknowledgement where evidence could be lost.

## Share-layout and residue surface

The workbench should expose one dedicated surface whenever a share contains imported legacy managed bytes, reviewed in-tree managed areas, cleanup-sensitive residue, or a requested annex migration.
This page is not advanced troubleshooting garnish.
It is where the product proves that live user content, rollback/history bytes, temp-transfer residue, and metadata-carry sidecars are different byte classes.

The page should show at least:

- share and mount summary
- live-root path and current layout class
- annex location and managed byte classes
- history/temp/metadata-carry posture
- cleanup risk state and preservation blockers
- recent layout receipts and any pending migration steps

Its primary actions should be:

- inspect layout only
- prepare annex migration
- prepare reviewed cleanup of one residue class
- preserve legacy evidence and keep inspect-only
- inspect recent layout receipts

No action on this page should collapse into `show hidden files` as the main operator model.

## Bring-up and control-entry surface

The workbench should expose one dedicated surface whenever local bring-up is not ordinary: no verified active root exists yet, startup discovered prior state, recovery/import is about to become live state, or first control exposure is being widened.
This page is not installer garnish.
It is where the product proves that fresh init, attach-known-root, recover/import, successor-sensitive continuity, and first control access are all explicit operator state.

The page should show at least:

- host role and runtime target
- state/continuity choice with candidate root or artifact
- identity posture and relationship consequences
- current and requested control/network posture
- blockers and bootstrap dependencies
- bring-up receipt promise and recent bring-up receipts

Its primary actions should be:

- create fresh local-only state
- attach a known verified root
- prepare recover/import into reviewed live state
- prepare reviewed LAN/SSH/proxy exposure
- inspect why bring-up is blocked

No mutation on this page should bypass a plan, report, or receipt.

## Diagnostics page

The workbench should expose one page for incident-scoped troubleshooting, evidence collection, redaction review, and bundle custody.
This page is where the product proves that “we have logs somewhere” and “we collected the right evidence for this incident and know what left the machine” are not the same claim.

The page should show at least:

- open diagnostic incidents by subject, reason, current depth, and collection status
- active temporary diagnostic-depth changes and their expiry
- staged or sealed evidence bundles with included classes, size, seal state, and retention horizon
- redaction findings for paths, peer identities, addresses, and blocked secret material
- recent evidence receipts for collection, sealing, export, destruction, and incident close

Its primary actions should be:

- open an incident from a report, transfer, share, or health finding
- raise diagnostic depth temporarily with explicit expiry
- collect a reviewed evidence bundle for the incident
- inspect or adjust redaction posture before sealing/export
- destroy staging material or close the incident once the evidence window is over

No mutation on this page should bypass a report, receipt, or explicit redaction review where sensitive material is present.


## Recovery page

The workbench should expose one page for recovery posture, bundle custody, and continuity consequences.
This page is where the product proves that “we have backups” and “we can actually recover under stress” are not the same claim.

The page should show at least:

- recovery posture by workflow (`encrypted-offline-decrypt`, `device-replacement`, `grant-reconciliation`, `identity-rotation`)
- current bundles with custody class, sufficiency state, and verification freshness
- explicit hidden dependencies such as daemon-bound database state or split-secret requirements
- invalidated or superseded bundles and what change weakened them
- recent recovery receipts for export, verification, invalidation, replacement, and byte import

Its primary actions should be:

- export a reviewed bundle for one workflow
- re-verify an older bundle
- inspect continuity claims before replacement or restore
- inspect why a bundle is partial, blocked, or stale
- jump from a receipt to the affected device, share, or state root

No mutation on this page should bypass a report, receipt, or plan.


## Releases page

The workbench should expose one page for release posture, upgrade plans, and compatibility boundaries.
This page is where the product proves that “a newer build exists”, “this peer constellation is compatible”, and “rollback is still honest” are different claims.

The page should show at least:

- current release posture for daemon, bundled runtimes, and important peer constellations
- edition family, release channel, schema epoch, and compatibility family
- mixed-version or mixed-edition findings that remain operationally relevant
- current upgrade plans with cutover scope, rollback posture, and blockers
- recent release receipts for checks, accepted boundaries, applied upgrades, and recorded rollbacks

Its primary actions should be:

- refresh release posture
- compare current posture against a target release
- prepare a reviewed upgrade plan
- inspect why a target is blocked or guarded
- inspect receipts for prior cutovers or recorded rollbacks

No mutation on this page should bypass a report, receipt, or plan.


## Constellation page

The workbench should expose a `Constellation` page distinct from peer detail, policies, and recovery.
Its job is not to become another device grid.
Its job is to answer:

- which members belong to the reviewed convenience-linked set
- what class and default visibility each member has
- where approval or successor scope may travel
- what authority a chosen member actually has on an important share
- whether any mixed-version, mixed-capability, or scope-risk finding weakens the constellation story

The page should support:

- a member table with class chips, visibility defaults, approval-reach chips, and compatibility findings
- a share-scoped authority-domain comparison drawer
- direct jumps to receipts for membership, class, visibility, and scope changes
- reviewed change actions for member class and visibility defaults

No mutation on this page should bypass a report, receipt, or plan.


## Policies page

The workbench should expose a `Policies` page distinct from both generic settings and subject detail pages.
Its job is not to become another preferences maze.
Its job is to answer:

- what important policy domains apply to this subject
- what the effective value is for each important field
- where that value came from
- which fields are inheriting versus pinned
- what would change if a defaults/profile change were applied

The page should support:

- a per-subject effective-policy table with origin chips on every important field
- filters for domain, origin kind, pinned-versus-inheriting, and temporary-override masking
- a drawer that expands one field into its full origin chain and superseded candidates
- side-by-side preview for defaults/profile changes affecting future-only, eligible-existing, or explicitly selected subjects
- direct links to policy receipts and to any reports describing unsupported surfaces or precedence drift


## Share list

The share list should not just show names and progress bars.
Each row should expose compact answers to four questions:

- is this share merely visible here, or adopted into a path?
- how much data is actually local here right now?
- what route posture is effective right now?
- is there any destructive or settlement risk that should stop a cutover or cleanup action?

Suggested share-row chips:

- `Incoming`
- `Detached`
- `Selective`
- `Full`
- `Encrypted only`
- `Lease active`
- `Deviation`
- `Blocked`
- `Settled`
- `Degraded`

## Share detail page

A share detail page should have a stable summary header and then several cards or tabs.

### Share header should answer

- what this share is
- who currently governs it
- whether it is visible only or mounted locally
- which materialization mode is active locally
- whether current route posture differs from baseline policy
- whether the share is settled enough for the current operator intent

### Required cards

#### 1) Local presence

Shows:

- incoming visibility vs adopted mount
- bound path
- materialization mode
- placeholder strategy if any
- filesystem-compatibility, fidelity, or binding warnings

#### 2) Peers and authority

Shows:

- which peers have which roles
- who can mutate data
- who can re-share or delegate
- whether any authority is policy-derived rather than manual
- whether any successor or handoff plan is active

#### 3) Routes and exposure

Shows:

- baseline discovery policy
- effective route posture now
- active leases or overrides
- what infrastructure classes can currently learn reachability
- the current winning route and the key rejected alternatives

#### 4) Settlement and transfers

Shows:

- convergence report for the selected intent
- active or most recent settlement barrier for the selected intent
- outstanding local and remote need
- background work still in progress
- selected route class for active transfers and any higher-ranked rejected alternative
- active transfer lane, queue state, and suspension cause
- active durable transfer policy plus any temporary throughput budgets affecting this scope
- transfer blockers, failed readiness clauses, bottleneck kinds, and reason codes

#### 5) Activity and windows

Shows:

- current phase matrix (`scan-index`, `ingress`, `egress`, `delete-propagation`, `announce`, `dial`)
- active one-shot overrides
- active or upcoming recurring schedule windows
- which route classes are capped or unaffected
- whether the current state differs from baseline policy only temporarily

#### 6) Layout, residue, and cleanup posture

Shows:

- current layout class and annex location
- whether the live tree is clean, mixed-managed, legacy-imported, or inspect-only
- current history/temp/metadata-carry byte classes
- cleanup risk state and any preservation blockers
- the last layout receipt touching this share or mount

#### 7) History, conflicts, and rollback

Shows:

- history candidates, provenance, and retention posture
- active conflict cases affecting the selected path if any
- whether restore is local-only or share-wide
- whether a restore or conflict resolution requires plan/apply
- the last rollback receipt touching this path or share

#### 8) File actions and local deviation

Shows:

- the current selected file-action intent
- whether the action is mount-local, device-local, or share-wide
- active deviation cases for the selected path if any
- the preservation report or deviation proof attached to the next action
- the file-intent receipt that would or did explain the last scope-sensitive action

#### 9) Danger zone

Shows dangerous actions with proof panels attached.
A destructive action should not be presented as a naked button.

The danger zone must distinguish:

- evict local bytes
- remove local mount
- delete from replicated share
- restore to replicated share
- revoke peer authority
- retire or replace this device relationship

## Peer / contact detail page

A peer page should unify three related but distinct ideas:

- who this peer/contact is
- what trust relationship exists
- what authority or future approval exists

The page should make it impossible to confuse:

- linked-group membership
- share grants
- remembered future approval
- successor carry-forward policy
- temporary route or maintenance overrides

The primary cards should be:

- identity and trust
- linked groups
- active grants
- future approvals
- successor / retirement posture
- route posture and known-host records

## Incoming share detail

Incoming share detail exists so “I can see it” is not treated as “I already mounted it”.

The page should show:

- source of visibility
- suggested label/path if any
- default mode offer
- path comparison result if the target is non-empty
- filesystem compatibility report
- filesystem fidelity contract / drift summary
- adopt / defer / reject actions

The page should never silently collapse into a mount page until adoption actually happens.

## Claim / adoption intake surface

A claim-intake surface exists so portable offers, incoming linked visibility, and manual invite acceptance all compile to one reviewed local decision instead of several different `Connect` rituals.

The page should show, in this order:

1. source and offered capability
2. intended local outcome
3. target path and filesystem fit
4. authority delta
5. blockers or drift
6. receipt promise

The page should make three differences visually unavoidable:

- **Offered to this machine**
- **Accepted locally on this machine**
- **Authority widened beyond local adoption**

Those three lines may align, but the product should never force operators to assume they do.

## Constellation join intake surface

A reviewed join surface exists so `link device` does not collapse relationship add, migration, replacement, visibility expansion, and approval widening into one vague act.

The page should show, in this order:

1. identity and continuity
2. membership and defaults
3. visibility delta
4. authority delta
5. compatibility and migration
6. receipt promise

The page should make three differences visually unavoidable:

- **this candidate keeps or does not keep its local identity**
- **this candidate joins the constellation under this member class and default posture**
- **this join does or does not widen approval/re-share/successor authority**

If the surface cannot answer those three questions before apply, it has recreated pair-device ritual under a friendlier name.

## Approval queue and acting-seat surface

A reviewed `Approvals` surface exists so pending requests do not collapse acting seat, future memory, and current-subject approval into one generic button.

The page should show, in this order:

1. requested subject
2. candidate acting seat
3. current approval horizon
4. next honest action
5. review / overflow

Opening a row should reveal one fixed review drawer showing:

- requested approval action
- acting seat and present authority
- approval horizon and blast radius
- share / constellation fallout
- admissible actions
- receipt promise

The surface should support:

- filtering by acting seat, horizon, share, blocker class, and future-memory risk
- switching candidate seats inside the same drawer without hiding changed blast radius
- approving once, denying, or escalating broader scope review from the same place
- inspecting recent approval receipts that prove who spoke and for what horizon

No row in this page may use a bare `Approve` verb if the horizon is not obvious.


## Standing-approval match and auto-admit-guardrail surface

A reviewed `Standing approval matches` surface exists so prior trust can stay useful without silently becoming local claim, bind, or materialization.

The page should show, in this order:

1. arrived subject
2. matched memory
3. local outcome now
4. next honest action
5. review / overflow

Opening a row should reveal one fixed review drawer showing:

- arrival and match evidence
- what prior trust actually covers
- local claim and bind effects
- admissible actions
- memory tighten / revoke options
- receipt promise

The surface should support:

- filtering by matched approval, scope class, drift/staleness, and local-claim state
- turning one matched arrival into `claim-suggested` without hiding that no bind exists yet
- requiring fresh review when the match is stale, broader than before, or would create new rights
- tightening or revoking standing memory from the same drawer without forcing a different hidden admin page
- inspecting recent approval-match receipts that prove whether the product only recognized prior trust or actually changed local state

No row on this page may use `Connect`, `Auto-connect`, or `Approved before` as if those phrases already explained the local outcome.

## Announcement inbox and local-claim surface
A reviewed announcement inbox exists so newly visible shares can stay pathless until this machine explicitly claims them.

The page should show, in this order:

1. subject and origin
2. local claim posture
3. path/bind requirement
4. authority and visibility consequences
5. local-only versus wider-scope actions
6. receipt promise

The page should make three differences visually unavoidable:

- **this share is visible here, but not yet claimed here**
- **this action hides it only on this machine, or instead withdraws it more widely**
- **this claim creates a local bind now, or still leaves path choice unresolved**

If the surface cannot answer those three questions before apply, it has recreated `Connect` folklore under a friendlier name.

## Path-compare surface

Whenever adoption or relocation touches a non-empty path, the compare view should show five explicit counts:

- identical
- local only
- remote only
- same-path divergent
- collision

It should also say whether the action is:

- safe to bind directly
- allowed only via plan/apply
- blocked pending manual resolution

If `same-path divergent` is non-zero or the target-lineage posture is not plainly same-lineage, the compare view should link directly into a dedicated reconciliation sheet rather than pretending compare counts alone are the full contract.

## Reconciliation surface

A reviewed reconciliation surface exists so `Destination folder is not empty` never has to stand in for real operator meaning.

The page should show, in this order:

1. target lineage and intent
2. compared material classes
3. same-path divergent candidates and chronology posture
4. admissible reconciliation actions
5. preservation / quarantine / annex effects
6. receipt promise

The page should make three differences visually unavoidable:

- **this is same-lineage reuse or it is not**
- **these bytes merely merge or they actually disagree at the same path**
- **this target is ordinary plaintext reuse or an encrypted/annex mismatch that cannot be treated as ordinary bind work**

If the surface cannot answer those three questions before apply, it has recreated `folder not empty` folklore under a friendlier name.

## Deviation surface

For read-only, receive-only, mirror, and encrypted-replica situations, the interface should show local deviation as a dedicated state card.

The card should answer:

- what local action happened
- what policy says should happen next
- whether remote progress is continuing, paused, or awaiting review
- whether local data was preserved, quarantined, reverted, or copied aside
- which file-intent receipt will explain the chosen resolution later

## Namespace & local-view surface

Projection needs its own stable workbench surface.
It should not be scattered between ignore editors, placeholder context menus, and mount detail folklore.

A projection page should show:

- share-level namespace defaults
- peer-announcement posture
- mount-by-mount local-view posture
- one path-test panel that answers peer namespace, local view, local byte posture, and visibility history together
- review-required previously indexed/materialized paths
- recent projection receipts so detach cleanup is not mistaken for share-wide suppression

The page should make one difference visually unavoidable:

- **Peers learn the name**
- **This mount shows the name**
- **This device currently has bytes**

Those three lines may align, but the product should never force operators to assume they do.

## Space & retention surface

Storage truth needs its own stable workbench surface.
It should not be scattered between placeholder gestures, low-disk warnings, hidden archive lore, and uninstall notes.

A space page should show:

- one class ledger for the current system, share, or mount
- materialized bytes versus placeholder-visible state
- archive/history bytes and their retention policy
- temp/remnant bytes that are reclaimable
- daemon/state/log/runtime bytes that belong to local service state
- active pressure state and budget policy
- one safe-first reclaim action plus a link to prior reclaim receipts

The page should make one difference visually unavoidable:

- **Free local bytes only**
- **Trim retention/history**
- **Mutate replicated share state**

Those three lines may all affect disk use, but the product should never force operators to assume they are interchangeable.

## Recovery and replacement surface

Recovery should be its own operator surface, not a hidden support mode.

A replacement/cutover page should show one fixed review grammar in this order:

1. predecessor and candidate
2. continuity carry-forward
3. state-root and runtime target
4. share / grant / authority rewrite
5. residue and revocation
6. receipt promise

Inside those sections the page should still answer at least:

- old device and new device
- what state would carry forward
- what grants would be rebound or frozen
- what approval memory would carry forward or be revoked
- whether route/exposure state is cleared
- what proof or recovery bundle the action depends on
- whether this is same-root re-home, successor continuity, or a blocked takeover/migration case



## Compromise and trust-rotation surface

A compromise surface exists so theft, leaked authority, stale identity reappearance, and other trust incidents compile to one reviewed containment decision instead of several different unlink, revoke, uninstall, and replacement rituals.

A compromise page should show one fixed review grammar in this order:

1. trigger and scope
2. immediate freeze
3. revocation and rotation
4. continuity and successor
5. residue and observation
6. receipt promise

Inside those sections the page should still answer at least:

- what triggered the case and how confident the system/operator is
- which sessions, tokens, offers, routes, approvals, or grants can freeze immediately
- which revocations and rotations are proposed, already executed, or still blocked
- whether successor continuity is recommended, available, or intentionally rejected
- what residue remains due to offline peers, provider TTLs, unknown remote bytes, or preserved local state
- what receipt will later prove containment versus unresolved residue

The page should make one difference visually unavoidable:

- **Freeze now**
- **Revoke or rotate**
- **Prepare successor / clean break**

Those three lines may all belong to one stressful incident, but the product should never force operators to assume they are the same action.

## Re-entry and stale-state surface

A re-entry surface exists so long-offline return, chronology uncertainty, ghost announcements, and other stale-return questions compile to one reviewed decision instead of a mix of peer counters, warning rows, archive aftermath, and hide/reappear folklore.

A re-entry page should show one fixed review grammar in this order:

1. subject and dormancy
2. chronology and evidence
3. authority and scope
4. divergence and availability
5. admissible actions
6. receipt promise

Inside those sections the page should still answer at least:

- which subject came back, after how long, and in what prior posture
- whether modification-time/clock evidence is trustworthy enough to accept its recency claims
- whether the subject would resume as writer, reader, quarantined observer, or blocked subject
- which shares, paths, or announcements diverged and whether bytes are still actually obtainable
- whether the safest next action is guarded resume, read-only resume, merge review, successor diversion, or containment escalation
- what receipt will later prove the chosen outcome and any unresolved chronology or observation caveats

The page should make one difference visually unavoidable:

- **Resume with this authority**
- **Quarantine or downgrade**
- **Escalate to compromise or successor review**

Those three lines may all start from “this device came back”, but the product should never force operators to assume they are the same action.

## Destructive-replay and delete-wave surface

A destructive-replay surface exists so high-signal remote delete, overwrite, or revert waves compile to one reviewed consent decision instead of a mix of pause semantics, archive settings, read-only overwrite ritual, and restore-after-the-fact folklore.

A destructive-replay page should show one fixed review grammar in this order:

1. trigger and scope
2. destructive effect summary
3. preservation and recoverability
4. authority and source confidence
5. admissible actions
6. receipt promise

Inside those sections the page should still answer at least:

- which share, path set, and source window triggered the review
- how many deletes, overwrites, or receive-only reverts are proposed and how much local state they would touch
- what preserved copy or rollback witness still exists, where it exists, and which paths would become unrecoverable if surrendered
- whether the contributing source set is ordinary, stale-returning, weakly witnessed, or suspicious enough to escalate
- whether the safest next action is freeze, non-destructive-only progress, stronger witness collection, narrowed apply, or incident/re-entry escalation
- what receipt will later prove the destructive scope that was accepted, frozen, or diverted

The page should make one difference visually unavoidable:

- **Allow this destructive scope**
- **Freeze or narrow it**
- **Escalate to re-entry or compromise review**

Those three lines may all start from “sync wants to make the trees match again”, but the product should never force operators to assume they are the same action.

## Conflict-adjudication and path-collision surface

A conflict-adjudication surface exists so non-trivial conflicts compile to one reviewed decision instead of a mix of suffix filenames, portability caveats, and after-the-fact rollback folklore.

A conflict-adjudication page should show one fixed review grammar in this order:

1. trigger and semantic class
2. candidates and authority posture
3. path, materialization, and compatibility reality
4. resolution scope and loser handling
5. admissible resolutions
6. receipt promise

Inside those sections the page should still answer at least:

- what class of conflict this really is and why it surfaced now
- which candidates exist, who supplied them, and how trustworthy their chronology/authority posture is
- whether the real blocker is bytes, case, unicode, placeholder/materialization state, symlink behavior, or portability tier
- whether the chosen winner is local-only, replicated, or blocked by compatibility risk
- what will happen to the loser and whether a preserved copy is the last easy recovery path
- what receipt will later prove the chosen winner, loser handling, and any unresolved caveats

The page should make one difference visually unavoidable:

- **Choose this winner and loser handling**
- **Defer or narrow the adjudication**
- **Escalate to portability, re-entry, or compromise review**

Those three lines may all start from “two versions disagree”, but the product should never force operators to assume they are the same action.

## Local-derivation and self-edge surface

A local-derivation surface exists so same-host fanout compiles to one reviewed topology/lifecycle decision instead of a mix of path picking, loop warnings, inherited permissions, and source-removal folklore.

A local-derivation page should show one fixed review grammar in this order:

1. source and target
2. topology and loop risk
3. authority and lifecycle coupling
4. materialization and target-tier reality
5. admissible derivations
6. receipt promise

Inside those sections the page should still answer at least:

- what source share or mount is being derived and onto what target tier/path
- whether the proposed relationship is disjoint, sibling, child, parent, overlapping, or otherwise topology-sensitive
- what permissions and mutability the derivative inherits and whether source detach or permission downgrade changes the derivative later
- whether the source is fully materialized enough to support the target's byte promise
- whether the target tier weakens durability, archive/history, or fidelity expectations
- what receipt will later prove the created source/target relationship, topology posture, authority coupling, and target-tier caveats

The page should make one difference visually unavoidable:

- **Create this derivative with stated coupling**
- **Narrow to a safer derivative or stronger target**
- **Reject as unsafe self-edge**

Those three lines may all start from “I want another local copy here”, but the product should never force operators to assume they are the same action.

## Authority-mutation and grant-boundary surface

An authority-mutation surface exists so non-trivial live access changes compile to one reviewed boundary decision instead of a mix of Owner folklore, peer-list dropdowns, disconnect semantics, folder-class limits, and remove/re-share ritual.

An authority-mutation page should show one fixed review grammar in this order:

1. trigger and current authority
2. desired boundary delta
3. active subject state and coupled dependents
4. authority-substrate and compatibility effects
5. admissible mutations
6. receipt promise

Inside those sections the page should still answer at least:

- what authority the subject currently holds, including write, delegation, and revoke reach
- what boundary is being widened or narrowed and whether bytes already present are intentionally preserved
- whether local derivatives, linked members, approval memory, or dependent grants narrow automatically, remain unchanged, or need follow-up review
- whether the requested result can be expressed directly or requires imported/legacy authority-substrate migration
- whether the safest next action is widen, narrow, freeze, revoke, or divert into stewardship/cutover review
- what receipt will later prove the pre/post authority boundary, dependent fallout, and byte-retention outcome

The page should make one difference visually unavoidable:

- **Apply this reviewed authority boundary**
- **Narrow or freeze it differently**
- **Divert to stewardship, cutover, or stronger review**

Those three lines may all start from “change this member's access”, but the product should never force operators to assume they are the same action.

## Writer-contention and quiescence surface

A contention surface exists so non-trivial lock pressure, burst-save delay, mixed SMB/NAS writers, and explicit quiesce actions compile to one reviewed coordination decision instead of a mix of locked-file badges, hidden delay JSON, retry knobs, and filesystem caveats.

A contention page should show one fixed review grammar in this order:

1. trigger and contested scope
2. writer and lock reality
3. notification and filesystem posture
4. quiesce and propagation effects
5. admissible actions
6. receipt promise

Inside those sections the page should still answer at least:

- what exact share, mount, path set, or subtree is contested and what triggered the review
- what evidence exists for another writer, whether the lock is confirmed or only suspected, and how strong that evidence is
- whether notifications are continuous, mixed, or periodic-rescan only, and whether the path is local-native, network-reviewed, warning-tier, or already blocked
- what protection is active now: delay profile, upload hold, bidirectional freeze, or reader-only guard
- whether the present risk is harmless delay, overwrite / rollback risk, or genuine corruption risk on warning-tier storage
- whether the safest next action is wait, freeze, preserve local writes, or divert into filesystem-fidelity / topology / destructive-replay review
- what receipt will later prove the reviewed scope, writer evidence, applied quiesce effect, and any remaining follow-up

The page should make one difference visually unavoidable:

- **Apply this reviewed quiesce action**
- **Keep coordinating with a narrower hold**
- **Escalate because current freshness or storage posture is not honest enough**

Those three lines may all start from “some files are locked”, but the product should never force operators to assume they are the same action.

## Capacity-fit and scale-admission surface

A capacity-fit surface exists so non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers compile to one reviewed host-fit decision instead of a mix of generic warnings, advanced toggles, and re-add folklore.

A capacity-fit page should show one fixed review grammar in this order:

1. subject and intended local role
2. local capacity and index cost
3. freshness and notification posture
4. portability and path blockers
5. admissible modes and mitigations
6. receipt promise

Inside those sections the page should still answer at least:

- what exact share, subtree, mount, or incoming claim is being reviewed and what local role is being asked of this host
- estimated entry count and byte scale when available
- whether RAM, watcher budget, indexing/verification cost, and storage headroom are comfortable, guarded, or blocked
- whether freshness is expected to stay continuous, become mixed, degrade to periodic-rescan only, or already be blocked
- whether path-length, encoding, merge-tree, filesystem, or mount-tier blockers are part of the host-fit story
- whether the safest next action is full adoption, selective/materialized narrowing, metadata-only visibility, reclaim-first staging, subtree narrowing, or escalation into topology / fidelity review
- what receipt will later prove the reviewed scale, accepted local mode, degraded posture, and any remaining follow-up

The page should make one difference visually unavoidable:

- **Accept this host-fit decision**
- **Narrow the local mode and keep scale honest**
- **Escalate because this path or host is not honest enough yet**

Those three lines may all start from “large share” or “slow indexing”, but the product should never force operators to assume they are the same action.


## Observer/read-only and local-write-containment surface

An observer surface exists so non-authoritative, read-only, names-only, placeholder, or viewer-style access compiles to one reviewed posture instead of a vague permission badge.

An observer page should show one fixed review grammar in this order:

1. requested access posture
2. visibility and materialization reality
3. local-write and repair behavior
4. onward serving and redistribution posture
5. projection, share-class, and runtime limits
6. receipt promise

Inside those sections the page should still answer at least:

- what exact share/peer, derivative, mount, or replica is being reviewed and whether the request is authority narrowing, projection change, repair, or inspect-only
- whether the subject currently sees names only, placeholders, full bytes, or a mixed local/materialized state
- what happens if someone edits locally: blocked, path suspended, auto-reverted, or escalated into reviewed deviation handling
- whether a revert helper exists, whether it is disabled by the current local mode, and whether repair is path-scoped or requires a wider review
- whether the subject may serve clean bytes onward, may not serve, or still matters for reseed/settlement despite being non-authoritative
- which parts of the posture are intrinsic rights and which parts are artifacts of share class, local derivation, runtime seat, or client/materialization limits
- what receipt will later prove the exact observer bundle that was accepted, repaired, or refused

The page should make one difference visually unavoidable:

- **Accept this observer posture**
- **Repair or redesign this broken read-only posture**
- **Escalate because the current label is hiding real write, serve, or projection differences**

Those three lines may all start from `read only`, but the product should never force operators to assume they are the same action.

## Fetchability and full-copy-witness surface

A fetchability surface exists so placeholder-visible, names-only, selectively materialized, or recently evicted content compiles to one reviewed truth instead of a vague `available on demand` label.

A fetchability page should show one fixed review grammar in this order:

1. requested materialization intent
2. visibility and local-residency reality
3. source backing and full-copy witnesses
4. fetchability, ghost risk, and admissible actions
5. collateral effects on eviction, pinning, and serve value
6. receipt promise

Inside those sections the page should still answer at least:

- what exact share/path/subtree is being reviewed and whether the request is inspect-only, fetch, evict, clear, pin, or stale-announcement handling
- whether the subject is visible by full bytes, placeholder, names-only projection, or tree announcement only
- whether the current device holds the only known full copy, one of several confirmed full copies, or no confirmed full copy at all
- whether remote witnesses are online now, merely last-known, or absent entirely
- whether the honest retrievability posture is `fetchable now`, `fetchable when source returns`, `local last copy`, `ghost-risk`, or `not fetchable`
- whether the requested action would remove the easiest remaining recovery path or merely change local residency without risk
- what receipt will later prove the reviewed fetchability truth and the action taken

The page should make one difference visually unavoidable:

- **Proceed because another full-copy witness exists**
- **Proceed only after preserving or pinning the last known full copy**
- **Escalate because this path is visible but not honestly fetchable anymore**

Those three lines may all start from `placeholder` or `available on demand`, but the product should never force operators to assume they are the same action.

A concrete fetchability surface should also include:

### Answer strip

A compact strip rendered above the detail sections in this order:

1. visibility
2. local residency
3. witness summary
4. fetchability posture
5. safest next step

Example classes:

- `Placeholder visible`
- `11 files local only`
- `3 remote-confirmed witnesses`
- `Mixed: local-last-copy + fetchable-now`
- `Re-witness 11 files before bulk evict`

### Subtree table

For subtree review, the default table should include at least:

- path
- visibility
- local bytes
- witness summary
- fetchability posture
- primary next action

Rows should be grouped by risk bucket rather than alphabetically by default when a requested action is safety-sensitive.
A mixed subtree should therefore naturally split into groups such as `safe to evict now`, `re-witness or pin first`, and `ghost/stale visibility`.

### Batch-action rule

Bulk actions from this surface should inherit the most conservative meaning that still stays honest.
That means:

- `Evict safe rows now` may be primary for a mixed subtree
- `Create witnesses for guarded rows` should be a separate companion action
- `Retire stale announcements` should never be silently bundled into ordinary evict

The workbench should prefer three explicit groups over one big cheerful `Apply to all` button.


### Selection bar

Whenever the operator multi-selects rows from this surface, the selection bar should summarize risk classes before it offers any mutation.
At minimum it should show:

- selected row count
- safe-now row count
- guarded / re-witness row count
- history-restore row count
- stale-visibility row count

Primary destructive labels should name only the rows they can honestly affect, for example:

- `Evict 24 safe rows`
- `Review 3 guarded rows`
- `Restore 2 history-backed rows`
- `Retire 1 stale row`

The bar should not collapse those into one misleading `Apply to 30 rows` affordance.

### Dense-view rule

A dense list row may compress counts and provenance, but it must still keep three truths separate:

- whether bytes are local
- whether another current witness exists
- what the safest next action is

A small client may shorten `3 remote-confirmed witnesses` to `remote-confirmed`, but it may not collapse `history-backed-only` into `fetchable later`.


### Availability row anatomy

Every table row or card in this surface should keep five things in stable order:

1. path / subject
2. visibility + local-bytes phrase
3. source/recovery phrase
4. primary next action
5. review / overflow affordance

A `safe-now` row may place a direct action in slot 4.
A `re-witness-first`, `history-restore`, or `stale-visibility` row should instead place a review-opening action in slot 4 or slot 5.

The workbench should never require the operator to open a hidden menu just to learn whether the honest next step is `Fetch now`, `Pin locally`, `Restore from history`, or `Retire stale announcement`.

See `94-availability-row-anatomy-and-review-pane-spec.md` for the stricter row and drawer contract.

## Danger-zone rules

1. Every dangerous action must display its scope in plain language.
2. Every destructive action must attach its preservation evidence.
3. Every trust-expanding action must attach its authority delta.
4. Every compatibility-sensitive action must attach preflight findings.
5. Every path-binding action must attach a comparison report when the path is not obviously empty.
6. Every discovered managed marker or foreign lineage on a target path must surface a reviewed custody sheet instead of collapsing into generic non-empty-path or retry language.
7. Cleanup of ambiguous or abandoned marker state must say what evidence or continuity claims will be lost if apply proceeds.
8. Every warning-tier or downgraded filesystem posture must stay visible as a fidelity contract after apply, not disappear with the preview report.
9. Every route-widening action must show whether it is durable policy or temporary lease.
10. Every temporary exception surface must show the baseline it is masking, its end condition, and whether `no expiry` was explicitly acknowledged.
11. Every pause/drain/throttle surface must say which runtime phases remain active.
12. Every projection-tightening action must say whether it changes peer namespace, local view, local bytes, or only future announcement.
13. Every reclaim action must say which byte classes it touches and whether retention or rollback posture changes.
14. Every exit or replacement action must keep stop/stay/residue/follow-up truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
15. Every non-trivial claim or adoption action must keep source/outcome/path/authority/blockers/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
16. Every incoming/inbox action must keep `visible here`, `claimed here`, `hidden here only`, and `withdrawn wider` visibly distinct; `remove` must not stand in for all four.
17. Every non-trivial successor cutover or state re-home action must keep predecessor/candidate, carry-forward, target, rewrite, residue, and receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
17. Every non-trivial compromise case must keep trigger/freeze/revoke-continuity/residue/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
18. Every non-trivial conflict must keep class/candidates/compatibility/loser-handling/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
19. Every non-trivial same-host derivation must keep source/target/topology/lifecycle/target-tier/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
20. Every non-trivial authority mutation must keep current-authority/boundary-delta/dependent-fallout/substrate-effect/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
21. Every non-trivial writer-contention case must keep contested-scope/writer-reality/notification-posture/quiesce-effects/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
22. Every non-trivial capacity-fit case must keep subject-role/local-capacity/freshness-posture/path-blocker/admissible-mode/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.
23. Every non-trivial cross-channel handoff must keep requested-action/subject, semantic-parity, current-channel degradation, safe handoff, apply continuity, and receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.

## Action hierarchy inside the workbench

Within any page, actions should be ordered like this:

1. one primary safe-next action
2. at most two nearby secondary actions
3. danger-zone actions separated visually and semantically

Examples:

- for an incoming share: `Adopt` or `Prepare claim` may be primary, while `Defer` is secondary and `Reject` belongs in the danger/rejection area
- for a portable offer artifact: `Inspect`, `Prepare claim`, and `Show constraints` should dominate; `Open link` or `Scan` must never bypass the semantic intake view
- for a pending peer: `Review` or `Trust as contact` may be primary, while `Ignore future contact` and `Quarantine` are clearly distinct higher-consequence actions
- for a destructive file operation: `Preview preservation` is primary before any delete-like action is allowed to become primary
- for a suspected stolen device: `Apply containment` or `Review containment` is primary, `Prepare successor` is secondary, and `Erase local residue` belongs in the danger zone unless separately proven possible

The workbench should strongly prefer proof-first progression over direct dangerous buttons.

## Batch-action rules

Batch operations are allowed only when they preserve honesty.
The interface should allow batching for things like:

- snoozing multiple review cards
- dismissing quiet informational cards
- approving several low-risk incoming shares that all passed equivalent preflight and target-policy checks

The interface should **not** batch together mixed-risk operations such as:

- trust expansion plus data deletion
- retirements plus successor binding
- route widening plus share adoption

If a batch action touches multiple underlying subjects, the proof panel must show per-subject scope and any outliers that force the batch to split.

## Command/API mapping

This workbench should be buildable from the existing model, especially:

- `anonsync review ...`
- `anonsync incoming ...`
- `anonsync mount ...`
- `anonsync share ...`
- `anonsync grant ...`
- `anonsync approval ...`
- `anonsync route ...`
- `anonsync exposure ...`
- `anonsync converge ...`
- `anonsync file ...`
- `anonsync projection ...`
- `anonsync doctor ...`
- `anonsync audit ...`
- `anonsync recover ...`
- `anonsync exit ...`

The important part is that the workbench should not need its own hidden model.
It is a projection of the same public object graph.

## Why this matters

Resilio's convenience proves that operators do want strong defaults, low-friction linking, and easy visibility.
Its remaining rough edges also show what happens when too many important distinctions are collapsed behind one convenience seam.

AnonSync only justifies its extra complexity if the interface makes the safer, more inspectable model feel **clearer**, not merely more correct on paper.


## Share-local posture cards and seat-default cards

The workbench should expose current-share posture and future-arrival policy as two adjacent but non-identical card families.

A **share-local posture** card should answer, in compact stable order:

1. subject
2. announcement / claim / bind truth
3. path provenance
4. local byte posture
5. next honest action

A **seat-default** card should answer, in compact stable order:

1. seat + reviewed scope
2. future-arrival default outcome
3. path template / collision policy
4. whether current shares will remain untouched
5. next honest action

The workbench should never let one generic `Mode` chip stand in for both cards.
If a user is changing what future arrivals will do on `Home-NAS`, the surface should say that plainly and should separately show that today's `Photos-2026` bind remains unchanged.


## Placement suggestion cards

The workbench should expose path-placement review as its own compact card family rather than hiding it inside a generic connect row.

A **placement suggestion** card should answer, in compact stable order:

1. subject
2. current bind truth
3. suggested candidate path
4. collision class
5. next honest action

A secondary line should answer:

1. suggestion basis
2. whether future defaults will remain unchanged
3. whether compare/adopt evidence exists

Example:

```text
Photos-2025   Announced • Unbound   /srv/family/Photos-2025   occupied-unrelated   Review placement
From family template • defaults unchanged • no same-lineage evidence
```

The workbench should never let a duplicate-path problem degrade into `Folder exists`, `Connect`, or a silent `(1)` suffix outcome.
If a candidate path is unsafe, the card should say *why* and whether the honest next action is alternate-path review, compare/adopt review, or deferral.


## Seat templates view

The workbench should expose a first-class `Seat templates` view for standing future-arrival policy.
This view exists so operators do not have to infer durable future behavior from one current share card, one mode selector, or one mobile simplification toggle.

### Required columns

- seat + governed scope
- admission posture
- path template / default root
- collision default
- draft-refresh posture
- pinned exception count
- next honest action

### Review-pane rule

Opening one row should preserve the fixed standing-template order from `100-standing-arrival-template-and-default-root-review-interface-spec.md`:

1. reviewed seat and governed scope
2. current standing template
3. proposed standing template
4. effect buckets
5. exceptions and pinned subjects
6. admissible actions
7. receipt promise

### Compact-row example

```text
Home-NAS / family arrivals   announce-only   /tank/family/{{share_name}}   always-review   drafts unchanged   Review template
```


## Arrival explanation drawer

The workbench should expose a first-class `Explain` drawer for incoming, matched, claimed-unbound, and newly bound subjects.
This drawer exists so the operator does not have to reconstruct later-arrival causality from inbox state, approval history, template settings, and placement review separately.

### Required compact-row columns

- subject
- current local stage
- strongest governing explanation
- strongest explicit non-cause
- next honest action

Example:

```text
Photos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain
```

### Drawer rule

Opening the row should preserve the fixed explanation order from `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`:

1. subject and current stage
2. why it is here now
3. governing standing state
4. what did not happen
5. counterfactuals
6. next honest actions
7. receipts and proofs

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one explicit non-cause and one counterfactual entry point.
The workbench should never force the operator to leave the row just to learn that prior approval lowered friction but did not yet create a bind.


## Policy delta preview sheet

The workbench should expose a first-class `Preview impact` sheet for any standing-policy mutation that can alter later-arrival handling.
This sheet exists so the operator does not have to infer retroactivity from one settings toggle, one arrival row, and remembered support-article caveats.

### Required compact-row columns

- seat + governed scope
- proposed delta summary
- strongest effect bucket
- strongest explicit non-effect
- next honest action

Example:

```text
Home-NAS / family arrivals   announce-only + new default root   future-only unless drafts refreshed   bound shares unchanged   Preview impact
```

### Sheet rule

Opening the row should preserve the fixed preview order from `102-policy-delta-preview-and-arrival-simulation-interface-spec.md`:

1. acting seat and governed scope
2. current policy and proposed delta
3. effect buckets
4. example subjects
5. explicit non-effects
6. admissible actions
7. receipt promise

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one strongest effect bucket, one explicit non-effect, and one entry point to example subjects.
The workbench should never force the operator to apply a standing-policy change just to learn whether current binds or current bytes stay untouched.



## Standing policy lineage view

The workbench should expose a first-class `Policy lineage` view for any standing seat policy that meaningfully affects later arrivals.
This view exists so operators do not have to compare one current settings page with memory of prior defaults.

### Required compact-row columns

- seat + governed scope
- current effective version
- previous version summary
- grandfathered subject count
- next honest action

Example:

```text
Home-NAS / family arrivals   v7 announce-only /tank/family   prev v6 claim-suggested /srv/family   3 grandfathered   View lineage
```

### View rule

Opening the row should preserve the fixed inspection order from `103-standing-policy-lineage-and-subject-attribution-interface-spec.md`:

1. seat, scope, and current effective version
2. version lineage
3. subject attribution
4. current-versus-applied compare
5. what did not change
6. admissible actions
7. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve the current version summary, one older-version summary or `no prior versions`, and one visible grandfathering fact.
The workbench should never force the operator to infer from today's current setting whether an older draft or bind reflects a superseded policy.



## Standing policy drift view

The workbench should expose a first-class `Policy drift` view for any standing seat policy that meaningfully affects later arrivals.
This view exists so operators do not have to compare lineage, subject cards, and current settings mentally just to decide whether drift is intentional or actionable.

### Required compact-row columns

- seat + governed scope
- current effective version
- refresh-eligible count
- subset-review count
- pinned/grandfathered count
- next honest action

Example:

```text
Home-NAS / family arrivals   current v8 announce-only /tank/family   4 refresh-eligible   2 subset review   3 pinned/grandfathered   Review drift
```

### View rule

Opening the row should preserve the fixed inspection order from `104-subject-policy-drift-and-realignment-review-interface-spec.md`:

1. seat, scope, and target current policy
2. drift population summary
3. per-subject drift classes
4. proposed realignment effects
5. what will stay grandfathered or pinned
6. admissible actions
7. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one current-policy summary, one explicit drift count, one visible drift class on each selected subject, and one honest next action.
The workbench should never force the operator to infer from today's current policy whether an older subject is stale clutter, a safe refresh candidate, or an intentional exception.



## Exception aging and re-review view

The workbench should expose a first-class `Exception review` view for any standing seat policy that allows intentional non-current outcomes.
This view exists so operators do not have to treat pinned exceptions or kept-grandfathered subjects as permanent background memory.

### Required compact-row columns

- subject + governed scope
- current divergence summary
- aging class
- next review horizon or `no expiry acknowledged`
- next honest action

Example:

```text
Invoices-2025   pinned exception vs current v8 announce-only   due-soon   review in 10d   Renew exception
```

### View rule

Opening the row should preserve the fixed inspection order from `105-exception-aging-renewal-and-rereview-interface-spec.md`:

1. subject and current divergence
2. why this exception exists
3. review horizon and aging
4. what horizon reach does not do
5. admissible outcomes
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible aging class, one visible review-horizon fact or `no expiry acknowledged`, and one honest next action.
The workbench should never force the operator to infer whether an old exception is still healthy, quietly overdue, or effectively immortal without acknowledgement.

## Approval-memory freshness view

The workbench should expose a first-class `Approval memory freshness` view for any remembered-approval family that can influence later arrivals.
This view exists so operators do not have to infer from old approvals and later arrivals whether remembered trust is still live, merely cooling, or no longer allowed to authorize shortcut reuse.

### Required compact-row columns

- remembered approval + governed scope
- granted scope summary
- freshness class
- last used or last reviewed
- next honest action

Example:

```text
Maya / photos-collab   Maya + linked devices / Photos family   cooling   last used 214d ago   Touch-renew
```

### View rule

Opening the row should preserve the fixed inspection order from `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`:

1. remembered approval and granted scope
2. freshness evidence
3. what this memory may still do now
4. touch-renewal and narrowing options
5. freeze / require-fresh / revoke options
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible freshness class, one visible cooling reason or last-use fact, and one honest next action.
The workbench should never force the operator to infer whether old trust is still healthy, quietly cooling, effectively frozen, or fully revoked.


## Approval-memory trace view

The workbench should expose a first-class `Approval memory trace` view for any remembered-approval family that can still explain later arrivals or lower-friction matches.
This view exists so operators do not have to reconstruct from old approvals, freshness rows, and later arrivals which exact trust act is actually being reused.

### Required compact-row columns

- remembered approval + governed scope
- current head summary
- freshness class
- latest mutation
- next honest action

Example:

```text
Maya / photos-collab   head: narrowed-to-home-nas/photos-only   cooling   last mutation 21d ago   Show trace
```

### View rule

Opening the row should preserve the fixed inspection order from `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`:

1. remembered approval family and current head
2. origin approval act
3. lineage mutations since origin
4. which node authorized this later subject
5. how current trust differs now
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible current head, one visible last-mutation fact, one visible freshness class, and one honest next action.
The workbench should never force the operator to infer whether a later convenience came from the original approval, a later narrowed head, or a trust version that would no longer authorize the same subject today.

## Approval-memory rebase view

The workbench should expose a first-class `Approval memory rebase` view for any remembered-approval family whose safe reuse is affected by identity or linked-device constellation mutation.
This view exists so operators do not have to reconstruct from device lists, hidden-member return, or old approvals whether remembered trust still applies monolithically.

### Required compact-row columns

- remembered approval + governed scope
- mutation trigger
- current family posture
- affected descendant count
- next honest action

Example:

```text
Maya / photos-collab   certificate takeover 3d ago   split recommended   2 descendants affected   Rebase trust family
```

### View rule

Opening the row should preserve the fixed inspection order from `108-approval-memory-constellation-mutation-and-family-rebase-interface-spec.md`:

1. remembered approval family and trigger
2. what constellation or identity changed
3. which descendants still inherit what
4. what definitely does not happen automatically
5. admissible outcomes
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible trigger class, one visible family posture, one visible descendant-count fact, and one honest next action.
The workbench should never force the operator to infer from linked-device churn alone whether hidden-device return, certificate takeover, or re-link caused old remembered trust to split, cool, freeze, or require fresh approval.

## Approval-memory descendant-liveness view

The workbench should expose a first-class `Approval memory descendants` view for any remembered-trust family whose descendant liveness matters to later convenience.
This view exists so operators do not have to reconstruct from peer lists, hidden-device memory, or stale lineage whether a descendant is actually alive enough to count as a byte source or approval-capable seat.

### Required compact-row columns

- descendant identity
- family/inheritance posture
- liveness class
- confidence class or witness age
- next honest action

Example:

```text
tablet-citrine   inherits frozen   reappeared awaiting proof   guarded confidence   Freeze reuse until live
```

### View rule

Opening the row should preserve the fixed inspection order from `109-approval-memory-descendant-liveness-and-reachability-confidence-interface-spec.md`:

1. descendant identity and family posture
2. current liveness and confidence
3. what roles this descendant may honestly fill now
4. what definitely is not being claimed
5. admissible reviewed outcomes
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible inheritance posture, one visible liveness class, one visible confidence or witness-age fact, and one honest next action.
The workbench should never force the operator to infer from family membership alone whether a descendant is currently live, byte-capable, approval-capable, historical only, or simply unknown.

## Approval-memory descendant-capability view

The workbench should expose a first-class `Approval memory capability` view for any remembered-trust family whose descendants may still matter to a governed subject.
This view exists so operators do not have to reconstruct from linked ownership, liveness, remembered approval, or peer presence whether a descendant may actually serve bytes or approve this subject now.

### Required compact-row columns

- descendant identity
- governed subject
- candidate role
- eligibility class
- next honest action

Example:

```text
desktop-ash   incoming:photos-2026   approval-seat   eligible after proof   Require fresh approval
```

### View rule

Opening the row should preserve the fixed inspection order from `110-approval-memory-descendant-role-eligibility-and-capability-proof-interface-spec.md`:

1. governed subject and descendant identity
2. candidate role and current eligibility
3. proof basis and blockers
4. what definitely is not being claimed
5. admissible reviewed outcomes
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible governed-subject fact, one visible candidate-role fact, one visible eligibility class, and one honest next action.
The workbench should never force the operator to infer from family membership, current liveness, or linked ownership alone whether a descendant may actually act as byte source, approval seat, both, or neither for the governed subject.


## Approval-memory reuse-policy view

The workbench should expose a first-class `Approval memory reuse policy` view for any governed subject whose lower-friction approval depends on remembered trust.
This view exists so operators do not have to reconstruct from old approvals, linked-device reach, share-dialog settings, or pending-folder behavior whether this one subject still permits approval reuse.

### Required compact-row columns

- governed subject
- standing reuse candidate
- subject reuse policy
- precedence outcome
- next honest action

Example:

```text
incoming:photos-2026   memory match with descendant   fresh approval all peers   fresh approval required   Open approval review
```

### View rule

Opening the row should preserve the fixed inspection order from `111-approval-memory-reuse-policy-and-subject-override-precedence-interface-spec.md`:

1. governed subject and standing match candidate
2. subject reuse policy and current precedence outcome
3. winning rule and blocker details
4. what definitely is not being claimed
5. admissible reviewed outcomes
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible standing-match fact, one visible subject-policy fact, one visible precedence outcome, and one honest next action.
The workbench should never force the operator to infer from `approved before`, descendant eligibility, or linked ownership alone whether this subject still permits reuse of remembered approval.


## Offer trust-promotion view

The workbench should expose a first-class `Offer trust promotion` view for any portable invitation whose successful claim might otherwise be mistaken for broad remembered approval.
This view exists so operators do not have to reconstruct from old share links, claim receipts, remembered approval, or later auto-connect behavior whether a one-time or expiring invitation created durable trust beyond its first governed subject.

### Required compact-row columns

- artifact posture
- claim outcome
- promotion posture
- later reuse posture
- next honest action

Example:

```text
offer consumed   claim applied   subject only   fresh approval next time   Keep this subject only
```

### View rule

Opening the row should preserve the fixed inspection order from `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`:

1. offer artifact and current redemption posture
2. claim outcome and promotion candidate
3. current durable-trust posture and later reuse posture
4. what definitely is not being claimed
5. admissible reviewed outcomes
6. receipts and proof links

### Compactness rule

Dense surfaces may compress prose, but they must still preserve one visible artifact-lifetime fact, one visible claim fact, one visible promotion posture, and one honest next action.
The workbench should never force the operator to infer from `invite used`, `approved before`, or expired-link history alone whether a successful claim created durable remembered approval for later unrelated subjects.

## Offer recipient-intent review surface

The workbench should expose one dedicated offer-redemption card wherever portable offers, actual redemption, and later trust promotion might otherwise blur together.

Required sections:

- `For` — sender-intent posture and intended-recipient label
- `Redeemed by` — actual redeemer identity and proof basis
- `Match result` — exact match, family match, hint-only match, unexpected redeemer, forwarded redeemer, or unknown
- `Trust survived` — none, subject only, reviewed seat only, broader candidate, explanation only
- `Next honest action` — review mismatch, accept subject only, reject mismatch, reissue for named recipient, freeze to explanation only

Rules:

- dense cards must keep `For` and `Redeemed by` adjacent; they must never collapse into one generic `Accepted by Noah` phrase when the proof only identifies a different redeemer or only a weaker hint-level match
- a successful claim badge must never outrun the mismatch outcome; `claim applied` without `who redeemed it` is incomplete truth
- the detail drawer must link separately to the offer artifact receipt, the claim/approval receipt, and the mismatch/trust-boundary receipt


## Offer redemption-ledger cards

Dense cards for partially or fully consumed portable artifacts should render:

- `Budget` — e.g. `2/3 consumed`, `0 remaining`, `expired`, `revoked`
- `Attempts` — ordered short ledger such as `tablet-lapis approved`, `desktop-ash broader`, `phone-cedar budget denied`
- `Trust fanout` — whether successful attempts stayed subject-only, seat-only, broader, frozen, or none
- `Next action` — often `Review ledger`, `Freeze fanout`, or `Reissue new artifact`

Rules:

- dense cards must keep `Budget` and `Trust fanout` adjacent but distinct
- dense cards must not compress several attempts into one vague `accepted by 2 peers` badge when the trust outcomes differ
- when remaining budget is zero, the card should prefer `Reissue new artifact` over generic `Share again`

## Offer redemption-equivalence cards

Dense cards for repeated or familiar redemption attempts should render:

- `Budget` — e.g. `1/2 consumed`, `1 remaining`
- `Compare to` — e.g. `tablet-lapis #1`
- `Equivalence` — replay-equivalent, same reviewed seat, same family, known peer new subject, distinct seat, or unknown
- `Slot effect` — collapse, consume new slot, blocked pending reissue
- `Next action` — often `Record replay`, `Review slot use`, or `Require new artifact`

Rules:

- dense cards must keep `Compare to`, `Equivalence`, and `Slot effect` adjacent
- dense cards must not compress repeated or familiar attempts into one vague `already used by this person` badge
- when equivalence proof is weak and remaining budget is low, the card should prefer `Require new artifact` over generic `Approve again`


## Offer reissue-lineage cards

Dense cards for artifacts that reached a real `reissue` threshold should render:

- `Predecessor` — expired, exhausted, mismatch-cooled, or policy-tightened
- `Successor relation` — same-scope successor, narrowed successor, broadened successor, fresh-scope successor, or delivery-only copy
- `Budget reset` — fresh island, same family, carried cap, no budget until review
- `Next action` — often `Issue narrowed successor`, `Review carry-forward`, or `Record delivery-only copy`

Rules:

- dense cards must keep `Predecessor`, `Successor relation`, and `Budget reset` adjacent
- dense cards must not compress genuine successor issuance into one vague `New link created` badge
- when the successor is narrowed or freshly scoped, the card should prefer that truthful label over generic `Reissued`


## Revision addendum — intake must keep delivery provenance adjacent to authority truth

Offer-intake surfaces should now reserve one compact strip or drawer for:

- `Received via`
- `Preview said`
- `External touch`
- `Parsed locally`
- `Authoritative now`

The workbench should not require opening raw logs to answer whether a browser landing page merely previewed a folder name, whether the app was auto-launched by remembered permission, or whether the local app has actually parsed the artifact yet.

Dense rows should still preserve at least:

- one delivery-channel chip
- one preview-authority chip
- one external-touch chip
- one `Inspect locally` or `Review handoff` verb when the current state is still ambiguous


## Revision addendum — dense intake cards must keep canonical artifact adjacent to carrier truth

Offer-intake surfaces should now reserve one compact strip or drawer for:

- `Canonical artifact`
- `Carrier observed here`
- `Other aliases`
- `Why same/not same`
- `Next action`

The workbench should not require opening raw logs to answer whether a browser wrapper, protocol handoff, and QR code are the same offer, which one is authority-bearing, or whether a familiar-looking new link is actually a successor.

Dense rows should still preserve at least:

- one canonical-artifact chip
- one carrier-kind chip
- one equivalence-posture chip
- one `Compare carriers` or `Treat as successor` verb when the current state is still ambiguous


## Revision addendum — dense intake cards must keep hint/sealed/authoritative field truth adjacent

Offer-intake surfaces should now reserve one compact strip or drawer for:

- `Preview hints`
- `Sealed until parse`
- `Authoritative now`
- `Not enough yet`
- `Receipts`

The workbench should not require opening raw logs to answer whether a folder label or approximate size was merely a recognition hint, whether authority-bearing fields stayed sealed until local parse, or whether the current surface is still missing claim/trust/budget prerequisites.

Dense rows should still preserve at least:

- one preview-hints chip
- one sealed-fields chip
- one authoritative-now chip
- one `Why not enough yet` verb or drawer link when any user could otherwise over-read the preview


## Revision addendum — dense intake cards must keep sufficiency adjacent to omissions

Offer-intake surfaces should now reserve one compact strip or drawer for:

- `Preview showed`
- `Missing governance`
- `Enough for`
- `Not enough for`
- `Next action`

The workbench should not require opening raw logs or secondary docs to answer whether a familiar preview is enough only for recognition or also enough to start any governed action.

Dense rows should still preserve at least:

- one preview-fields chip
- one omitted-governance chip
- one sufficiency chip
- one `Why not enough yet` verb or drawer link when the preview would otherwise look deceptively complete
