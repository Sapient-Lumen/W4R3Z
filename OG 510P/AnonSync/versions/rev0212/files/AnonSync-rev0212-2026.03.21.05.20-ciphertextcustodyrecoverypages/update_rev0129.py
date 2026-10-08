from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

README = '''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0129`
- Timestamp: `2026.03.19.17.09` (America/New_York)
- Codename: `statewarningsubtreetripwire`

## What changed in this revision

This revision continues directly from `rev0128` and does twelve specific things:

1. Pushes the **Resilio Sync** evaluation further with current official evidence about hidden service-state dependence, hidden rule files, warning-tier SMB targets, subtree-sharing topology quirks, and read-only seeding/local-divergence semantics.
2. Sharpens the non-clone reason again: the remaining problem is not missing features but too much meaning spread across hidden `.sync` state, `IgnoreList`, `StreamsList`, service-file repair ritual, warning-only degraded targets, subtree graph caveats, and overloaded `Read Only` language.
3. Adds a new **hidden service state / rule ledger / repair review spec** so operator-meaningful semantics stop living in hidden control files and remove-and-re-add folklore.
4. Adds a new **warning-tier target / notification drift / out-of-band writer spec** so NAS/SMB and similar targets stay visible as contracts, not as one-time warnings.
5. Adds a new **parent-child subtree topology / non-transitive seeding spec** so nested shares are reviewed as graph mutations instead of tolerated side effects.
6. Adds a new **read-only local divergence / overwrite / seeding ceiling spec** so one-way behavior stops collapsing write denial, local repair, and relay capability into one badge.
7. Refreshes the **Resilio evaluation** so the comparison now also covers hidden service-state contract, warning-tier target semantics, subtree graph behavior, and read-only seeding ambiguity.
8. Refreshes the **product direction** so hidden control state, degraded targets, nested topology, and one-way truth become doctrine instead of scattered caution.
9. Refreshes the **roadmap** so the next tranche now emphasizes rule-ledger surfaces, warning-tier steady-state reporting, nested-topology review, and one-way/relay honesty.
10. Refreshes the **source notes** so the official evidence set now explicitly includes `Cloning Sync`, `Service files missing`, `Ignoring files in Sync`, `Alt Streams and Xattrs in Sync`, `Soft links, hard links and symbolic links`, `Sync and SMB file shares`, `Is it possible to share a nested folder separately?`, and `Is one-way synchronization possible?`.
11. Keeps the archive tight by extending existing filesystem, projection, rights, topology, and continuity grammar instead of creating separate admin-only exception paths.
12. Preserves the earlier compromise, restore, presence, route, kind-migration, rights-editor, and rehome decisions while giving them stronger hidden-state, degraded-target, subtree-graph, and one-way-truth companions.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The reason is sharper again and still evidence-based.
Current official docs still show a maintained Sync v3 line through `3.1.2.1076` in late 2025, a refreshed v3 UI, practical link/QR/app delivery, linked-device convenience, sync modes, share dialogs, route settings, WebUI on Linux and service installs, and a candid help center.
That is why Resilio remains worth studying rather than dismissing.

But the better non-clone reason is now this:

> Resilio still solves many real operator problems while leaving too much meaning about *service-state continuity, degraded-target semantics, subtree topology, and one-way behavior* distributed across hidden `.sync` internals, editable control files, warning banners, topology caveats, and overloaded permission labels where AnonSync wants one visible rule ledger, one service-state repair review, one warning-tier target contract, one topology review page, and one explicit write-vs-seed-vs-repair truth model.

The most important current examples are now:

- `.sync` is still critical to sync identity/state and the documented fix for corruption is still remove the share, delete `.sync`, and add it back
- `IgnoreList` and `StreamsList` are still hidden per-share text files, `IgnoreList` sameness across peers is only advisory, and xattr control lives outside ordinary ignore semantics
- SMB targets can still lose continuous notifications and fall back to periodic rescans, while out-of-band access outside Samba can damage files or roll changes back
- symlink handling still differs materially by platform, which means warning-tier target truth is not reducible to one generic compatibility banner
- nested child shares are still separate sync folders with double indexing, selective-sync restrictions, and non-transitive seeding rules
- read-only still means local changes can break per-file synchronization, `Overwrite any changed files` repairs only some classes of divergence, and read-only peers can still relay unmodified bytes to newly joined peers

So the direction stays the same:

- **borrow** Resilio's practical handoff, linked-device convenience, selective/disconnected materialization, and operational candor
- **reinterpret** them through one stable shell, one subject workspace grammar, one visible rule/service-state ledger, one warning-tier target contract, one topology review surface, and one explicit write-vs-seed-vs-repair model
- **refuse** any interface contract where hidden control files, remove-and-re-add ritual, one-time warnings, topology footnotes, or overloaded permission badges collectively stand in for continuity truth, degraded-target truth, graph truth, or one-way semantics

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md`
4. `docs/178-warning-tier-target-notification-drift-and-out-of-band-writer-interface-spec.md`
5. `docs/179-parent-child-subtree-topology-and-non-transitive-seeding-interface-spec.md`
6. `docs/180-read-only-local-divergence-overwrite-and-seeding-ceiling-interface-spec.md`
7. `docs/173-compromise-response-identity-rotation-and-stolen-seat-review-interface-spec.md`
8. `docs/174-restore-history-archive-and-share-safe-reintroduction-interface-spec.md`
9. `docs/175-membership-presence-offline-aging-and-hidden-device-truth-interface-spec.md`
10. `docs/176-snapshot-send-expiry-budget-and-post-transfer-lineage-interface-spec.md`
11. `docs/169-subject-kind-migration-and-capability-upgrade-review-interface-spec.md`
12. `docs/170-topology-aware-rights-editor-and-propagation-ceiling-interface-spec.md`
13. `docs/171-cross-root-rehome-move-and-missing-path-repair-interface-spec.md`
14. `docs/172-runtime-seat-switch-and-empty-state-attribution-interface-spec.md`
15. `docs/165-route-policy-stack-and-effective-directness-interface-spec.md`
16. `docs/166-share-identity-collision-and-target-preflight-interface-spec.md`
17. `docs/167-same-machine-derivation-source-child-lineage-and-reconnect-interface-spec.md`
18. `docs/168-route-narrowing-residue-and-clearance-review-interface-spec.md`
19. `docs/157-reviewed-mutation-commit-barrier-and-receipt-continuity-interface-spec.md`
20. `docs/158-adopt-rebind-reconnect-and-pre-existing-path-repair-interface-spec.md`
21. `docs/159-local-web-first-bringup-auth-and-empty-state-interface-spec.md`
22. `docs/160-narrow-width-proof-preservation-and-progressive-disclosure-interface-spec.md`
23. `docs/149-interface-shell-navigation-and-persistent-context-spec.md`
24. `docs/150-subject-workspace-and-review-stack-interface-spec.md`
25. `docs/151-inherited-vs-excepted-value-explanation-interface-spec.md`
26. `docs/152-command-palette-bulk-review-and-apply-boundary-interface-spec.md`
27. `docs/38-operator-workbench-interface-spec.md`
28. `docs/39-interface-pattern-language.md`
29. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and interface doctrine
- `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md` — visible rule/service-state ledger replacing hidden control-file semantics and repair folklore
- `docs/178-warning-tier-target-notification-drift-and-out-of-band-writer-interface-spec.md` — steady-state contract for degraded NAS/SMB-style targets and warning-tier semantics
- `docs/179-parent-child-subtree-topology-and-non-transitive-seeding-interface-spec.md` — explicit topology review for nested shares, double indexing, and propagation boundaries
- `docs/180-read-only-local-divergence-overwrite-and-seeding-ceiling-interface-spec.md` — explicit one-way contract for local edits, overwrite repair, and relay/seeding truth
- `docs/173-compromise-response-identity-rotation-and-stolen-seat-review-interface-spec.md` — reviewed trust-boundary response for stolen seats, successor replacement, and identity rotation
- `docs/174-restore-history-archive-and-share-safe-reintroduction-interface-spec.md` — provenance-first file recovery and explicit local-vs-share-visible reintroduction
- `docs/175-membership-presence-offline-aging-and-hidden-device-truth-interface-spec.md` — one membership ledger for live presence, remembered absence, cosmetic hiding, retirement, and revocation
- `docs/176-snapshot-send-expiry-budget-and-post-transfer-lineage-interface-spec.md` — first-class snapshot-transfer subject with expiry, redemption, collision, and retention truth
- `docs/sources.md` — current external source notes for this revision
'''

STATUS = '''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0128`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based, current, and specific not only about compromise, restore, presence, and snapshot send, but also about **hidden service state**, **warning-tier targets**, **nested subtree topology**, and **one-way/read-only semantics**
- spend more time on **interface specs**, especially where current sync products still ask the operator to reason from hidden control files, service-file corruption ritual, degraded notifications, graph caveats, or overloaded permission labels
- preserve the already-established shell, subject workspace, offer/claim ladder, effective-value grammar, commit barrier, reconnect/repair workflow, local-web-first doctrine, future-arrival boundary, route truth, kind migration, rights-editor truth, rehome truth, compromise truth, restore truth, membership truth, and snapshot-send truth unless fresh evidence actually breaks them
- make a better explicit case for why AnonSync should not inherit Resilio's hidden `.sync` contract, hidden rule-file semantics, warning-only degraded-target posture, nested-share caveat model, or ambiguous `Read Only` meaning even while learning from its strengths

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: rev0129
- Timestamp: 2026.03.19.17.09 America/New_York
- Codename: statewarningsubtreetripwire

- a further-tightened **Resilio evaluation** that now treats hidden service-state dependence, editable hidden rule files, warning-tier SMB targets, subtree graph caveats, and overloaded read-only behavior as additional non-clone reasons
- a new **hidden service state / rule ledger / repair review** interface spec so `.sync`, `IgnoreList`, and `StreamsList` stop functioning as the public operator model
- a new **warning-tier target / notification drift / out-of-band writer** interface spec so degraded targets become durable contracts rather than warning banners
- a new **parent-child subtree topology / non-transitive seeding** interface spec so nested shares are reviewed as graph mutations instead of tolerated quirks
- a new **read-only local divergence / overwrite / seeding ceiling** interface spec so one-way sharing no longer collapses write denial, local repair, and relay capability into one badge
- updated top-level docs so the archive now makes firmer choices about visible rule/service-state truth, degraded-target truth, nested-topology truth, and one-way semantics

## The main shift

`rev0129` closes the next seam:

> it is not enough to have good compromise response, restore provenance, membership truth, and snapshot-send grammar if the operator still has to reconstruct **service-state continuity**, **degraded-target semantics**, **subtree graph behavior**, and **one-way/read-only truth** from hidden control files, service-file corruption ritual, warning banners, topology caveats, and overloaded permissions.

That changes the archive in eight specific ways:

- hidden rule and service state now have one explicit **rule/service-state ledger** instead of hidden-file folklore
- degraded NAS/SMB-style targets now have one explicit **warning-tier steady-state contract** instead of one-time setup warnings
- nested child shares now have one explicit **topology review** instead of graph caveats buried in support prose
- one-way sharing now has one explicit **write-vs-seed-vs-repair** model instead of overloaded `Read Only` behavior
- repair can now preserve continuity while still showing when hidden state loss truly creates a new subject epoch
- degraded targets can now say whether the risk is notification loss, out-of-band writers, blocked entry classes, or runtime drift
- topology can now say whether a child subtree is a graph fork, a transit boundary, or an inadmissible overlap before apply
- one-way surfaces can now distinguish denied write propagation, local divergence outcome, and allowed relay behavior in one place

## Files added in this revision

- `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md`
- `docs/178-warning-tier-target-notification-drift-and-out-of-band-writer-interface-spec.md`
- `docs/179-parent-child-subtree-topology-and-non-transitive-seeding-interface-spec.md`
- `docs/180-read-only-local-divergence-overwrite-and-seeding-ceiling-interface-spec.md`
- `update_rev0129.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/20-product-direction.md`
- `docs/50-roadmap.md`
- `docs/sources.md`
'''

DOC177 = '''# Hidden service state, rule ledger, and repair review interface spec

## Purpose

The archive already had filesystem fidelity, projection policy, and continuity repair.
What it still lacked was one concrete interface contract for the oldest kind of sync folklore:

> when critical state lives in hidden service folders and editable text files, what page tells the operator what that state means, whether it drifted, and whether a repair preserves continuity or starts a new subject epoch?

Current Resilio docs make this seam sharper than before.
They still say `.sync` is critical, that deleting or corrupting it suspends synchronization, that the fix for `Service files missing` is remove the share, delete `.sync`, and add it back, that `IgnoreList` and `StreamsList` live in hidden `.sync` files, and that cloning a Sync instance is unsupported because copied internal state can produce strange behavior.
That is candid and useful support guidance.
It is not the user contract AnonSync should inherit.

## Core decision

Hidden service artifacts may exist internally, but they must never be the only public explanation for operator-meaningful behavior.
Anything that changes tracking, visibility, xattr propagation, subject identity, or repair outcome must surface through one explicit **rule and service-state ledger**.

That ledger must answer at least four distinct questions:

1. **What hidden state exists?**
2. **Which parts are operator-meaningful policy versus daemon-owned machinery?**
3. **What continuity would be preserved or broken by repair?**
4. **Which durable receipt proves what happened?**

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- `.sync` is critical enough that losing it suspends sync entirely
- share identity lives partly in hidden service state such as the ID file
- ignore behavior and xattr behavior are configured through hidden text files
- xattrs are governed by `StreamsList`, not ordinary ignore semantics
- same `IgnoreList` across peers is only advisory, so two peers can truthfully differ while looking superficially aligned
- cloning/copied internals and service-file corruption still fall back to `remove and add back` style repair

AnonSync should therefore make hidden service state visible as **classified contract data** instead of leaving it as support-lore background radiation.

## Ledger sections

Every share or subject should expose one **Rules and service state** page with these sections in fixed order:

1. **Subject continuity identity**
2. **Operator-visible policy ledgers**
3. **Daemon-owned service state**
4. **Repair classification**
5. **Receipt shelf**

### 1) Subject continuity identity

Show:

- subject label and stable handle
- current continuity epoch
- mount/bind count
- whether service identity is fresh, drifted, missing, foreign, or cloned-risk
- whether the current path owns the live service state or merely contains copied residue

The operator should be able to answer:

> is this still the same subject with damaged internals, or has continuity already forked?

### 2) Operator-visible policy ledgers

Show policy objects that may have hidden implementations but explicit public truth:

- ignore/project rules
- namespace suppression rules
- xattr/stream policy
- special-entry policy
- archive/history policy
- portability or warning-tier target policy

Each row should say:

- effective behavior
- scope
- source
- peer-visibility consequences
- whether the daemon stores implementation copies in hidden files

The operator should never have to inspect `IgnoreList` or `StreamsList` directly just to understand what the product will do.

### 3) Daemon-owned service state

Show service-owned machinery separately from policy:

- identity markers
- indexing state
- materialization markers
- in-flight temp material
- archive service paths
- repair blockers or corruption warnings

This section is visible because it matters, but editable only through reviewed actions.
It should not masquerade as user-authored policy.

### 4) Repair classification

When hidden state is missing, foreign, or cloned-risk, the page must classify the repair options:

- `Reconstruct daemon-owned state and preserve continuity`
- `Seal evidence and fork into new continuity epoch`
- `Detach copied residue from this path`
- `Import as historical evidence only`
- `Abort because active overlap or loop risk exists`

The review must say explicitly whether the result will:

- preserve subject handle
- preserve grants and approvals
- preserve archive/history continuity
- require reissue of offers or lineage receipts
- create a new epoch with a continuity break receipt

### 5) Receipt shelf

Every high-signal repair emits one durable receipt proving:

- prior state class (`healthy`, `missing`, `foreign`, `cloned-risk`, `corrupt`, `mixed`)
- chosen repair class
- preserved continuity versus broken continuity
- preserved policy ledgers versus regenerated daemon state
- whether hidden artifacts were quarantined, reused, or discarded

A later operator should be able to answer:

> did we repair the same subject, or did we create a new one after hidden-state loss?

## What must never happen automatically

The product must never automatically:

- require direct hidden-file editing to understand ordinary semantics
- treat daemon-owned service state as if it were user-authored policy
- silently promote copied service residue into live continuity
- silently discard archive/history material during service-state repair
- claim continuity was preserved when the repair actually minted a new epoch

## Why this is worth the trouble

The moment a sync product teaches hidden control files as the real explanation, the public interface has already ceded too much ground.
AnonSync can do better by giving hidden state one visible ledger, one repair classifier, and one receipt model that keeps continuity honest.
'''

DOC178 = '''# Warning-tier target, notification drift, and out-of-band writer interface spec

## Purpose

The archive already had filesystem fidelity and degraded-target flows.
What it still lacked was one concrete steady-state interface contract for targets that are *allowed* but semantically weaker:

> when a share is bound onto NAS, SMB, network, or translation-heavy storage, what page keeps the operator aware of notification loss, locked-file risk, blocked entry classes, and out-of-band writer danger after setup day?

Current Resilio docs sharpen this seam.
They still say SMB targets may lack notifications and then rely on periodic rescans, that permissions loss can halt delivery, that locked files can linger depending on the SMB implementation, and that direct access outside Samba can damage files or roll back changes.
Separate docs still show platform-dependent symlink behavior.
That is valuable honesty.
It should become a first-class target contract, not a warning banner the operator forgets after bind.

## Core decision

Any target whose semantics are knowingly weaker than local-native fidelity must publish one persistent **warning-tier target contract**.
The operator should not have to reconstruct target risk from setup-time warnings, background logs, or platform trivia.

That contract should answer five questions at all times:

1. **What kind of target is this?**
2. **Which semantics are fully trusted, degraded, blocked, or unknown?**
3. **What runtime drift has been observed?**
4. **Which outsider behaviors can damage truth?**
5. **What reviewed actions are admissible now?**

## The target contract card

Every non-local-native mount should surface one target contract card with these rows:

- target class (`local-native`, `network-reviewed`, `warning-tier`, `blocked`)
- notification posture (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- lock posture (`ordinary`, `stale-lock-risk`, `implementation-defined`)
- out-of-band writer posture (`safe`, `unsafe`, `unknown`, `blocked`)
- blocked entry classes (`symlink`, `junction`, `xattr-full`, `special-file`, `case-risk`, etc.)
- last verified time
- drift severity

A target card is not a one-time preflight echo.
It is the steady-state public truth.

## The fixed review order

When the operator opens the card, the detail page should render sections in this order:

1. **Current semantics promised here**
2. **Observed drift since bind**
3. **Out-of-band writer and lock risk**
4. **Blocked or virtualized entry classes**
5. **Admissible next actions**
6. **Receipt shelf**

### 1) Current semantics promised here

Show explicitly whether this mount promises:

- continuous notifications or only periodic discovery
- strong rename/move observation or delayed reconciliation
- full metadata/xattr fidelity or portable subset only
- local-native special-entry handling or blocked classes
- exclusive target custody or shared-outside-writer risk

The operator should be able to answer:

> what exactly is trustworthy on this target right now?

### 2) Observed drift since bind

Show runtime drift such as:

- notification watchers exhausted or absent
- permissions narrowed
- target moved from local-native to network-reviewed
- lock behavior now stale or inconsistent
- recent rescans replacing event-driven confidence

The page should classify each drift as `watch`, `guarded`, `high`, or `blocked`.

### 3) Out-of-band writer and lock risk

This section should make outsider risk impossible to miss.
It should answer:

- can other apps or users write here through a path the daemon cannot coordinate safely?
- are there stale lock risks that can stall delivery or reconciliation?
- is this target only safe if all writes traverse one protocol boundary?

The product should never flatten `SMB works` into `all write paths are equally safe`.

### 4) Blocked or virtualized entry classes

Show classes that cannot be represented faithfully on this target:

- symlinks/junctions
- hard links
- full xattrs or streams
- special files
- case-folding hazards
- path-normalization hazards

For each, say whether the product will:

- block
- omit with receipt
- virtualize with side storage
- preserve only on other mounts

### 5) Admissible next actions

Primary actions should be explicit:

- `Keep current warning-tier contract`
- `Narrow to safer behavior`
- `Move to local-native target`
- `Acknowledge drift and continue`
- `Freeze writes pending review`
- `Retire target and rehome subject`

The product should not suggest `everything is fine` when the honest answer is `allowed, but weaker and watched`.

### 6) Receipt shelf

Every reviewed target acceptance or drift acknowledgement must emit a receipt proving:

- target class
- promised semantics
- active degradations and blocked classes
- outsider-risk acknowledgement
- drift state at time of review
- chosen action

## What must never happen automatically

The product must never automatically:

- downgrade a target from event-driven to periodic without public drift state
- imply outsider writes are safe simply because syncing still appears to work
- hide blocked entry classes behind later conflict artifacts
- treat a warning-tier target as fully local-native in summaries or receipts

## Why this is worth the trouble

A serious sync product can support weaker targets without pretending they are ordinary.
AnonSync can do better than one-time warnings by keeping warning-tier targets legible as durable contracts with visible drift and outsider-risk truth.
'''

DOC179 = '''# Parent-child subtree topology and non-transitive seeding interface spec

## Purpose

The archive already had overlap containment, local derivation, and graph-aware flows.
What it still lacked was one dedicated interface contract for the deceptively simple request:

> can I share a child subtree separately without pretending it is just another ordinary subject?

Current Resilio docs sharpen this seam.
They still say nested sharing is possible only with limitations: parent and child must both have Read & Write or Owner permissions, both become separate sync folders, the child gets indexed and rescanned twice, parent peers do not seed data to peers that only have the child, and both parent and child must have Selective Sync disabled.
That is candid and useful.
It also proves nested subtree sharing is a graph decision, not an ordinary share action.

## Core decision

Creating or accepting a child subject inside a parent subject must always open a first-class **topology review**.
The product should never flatten `share this subfolder too` into a generic publish flow.

The review must classify at least these truths:

1. **Graph shape**
2. **Indexing and rescan cost**
3. **Propagation boundaries**
4. **Materialization constraints**
5. **Dependent fallout on parent and child**

## Why this matters

Current Resilio docs still reveal four truths AnonSync should not clone:

- child subtree sharing is a separate sync subject, not a lightweight alias
- the shared machine can pay duplicate indexing/rescan cost
- parent-only peers are not equivalent seeders for child-only peers
- changes arriving through the child can still propagate onward via the parent graph

That is not a corner-case implementation detail.
It is core topology truth that deserves one visible page.

## The topology review page

Every nested-subtree decision should render sections in this order:

1. **Graph preview**
2. **Propagation matrix**
3. **Cost and custody**
4. **Admissibility rules**
5. **Receipt promise**

### 1) Graph preview

Show:

- parent subject
- candidate child subject path
- members of parent and child
- which member is shared between them
- whether the child already exists as its own subject
- whether the proposal would create overlap, loop risk, or duplicate bind

The operator should be able to answer:

> what exact graph am I creating if I accept this child subtree as a separate subject?

### 2) Propagation matrix

Show explicitly:

- who can seed parent bytes
- who can seed child bytes
- whether parent-only peers can satisfy child-only demand
- whether child-originated mutations will later propagate into parent peers through shared members
- which flows are direct, transitive, or impossible

This is the heart of the review.
The page must make non-transitive seeding and onward propagation legible in one place.

### 3) Cost and custody

Show:

- duplicate indexing/rescan burden on shared members
- local storage duplication or lineage reuse
- custody concentration on the shared bridge member
- whether the bridge member becomes a required transit point for some flows

Operators should not discover after the fact that one NAS or laptop silently became the topology hinge.

### 4) Admissibility rules

The review must classify the proposal as:

- `ordinary child derivation`
- `bridge-required subtree`
- `overlap-risk child`
- `illegal loop or ancestor/descendant bind`
- `blocked due to materialization/posture conflict`

It should also show any constraints such as:

- selective materialization or observer-only posture not admissible for this graph
- source-right ceiling for the child
- requirement that the shared bridge member stay healthy for some paths to converge

### 5) Receipt promise

The resulting receipt must prove:

- graph shape accepted
- bridge members
- non-transitive seeding boundaries acknowledged
- indexing/cost warning accepted
- admissibility constraints applied
- whether the child is independent, transit-bound, or blocked

## What must never happen automatically

The product must never automatically:

- flatten nested subtree sharing into a generic `share subfolder` action
- imply parent peers can seed child-only peers when they cannot
- hide duplicate indexing/rescan cost on the shared bridge member
- allow ancestor/descendant loops or ambiguous overlap through convenience defaults

## Why this is worth the trouble

Nested subtree sharing is useful, but it is not ordinary.
AnonSync can keep it powerful without copying the caveat-driven model by making topology, propagation, cost, and admissibility visible before apply.
'''

DOC180 = '''# Read-only local divergence, overwrite, and seeding ceiling interface spec

## Purpose

The archive already had rights doctrine and helper-role discussion.
What it still lacked was one dedicated interface contract for the overloaded phrase `Read Only`:

> if a member may not write back, can it still edit locally, can those edits be repaired automatically, and can it still relay bytes to others?

Current Resilio docs make this seam sharper.
They still say read-only peers can make local changes but those changes are not synced back, that changed files can stop synchronization for that file, that `Overwrite any changed files` can restore deleted or edited content and re-download the old name after a rename, that added files are neither deleted nor synced, and that read-only peers can still transfer unmodified files to newly joined peers.
That is useful operational candor.
It is not one clean public truth.

## Core decision

One-way or read-only posture must be modeled through three separate public axes:

1. **Write propagation right**
2. **Local divergence handling**
3. **Seeding/relay capability**

A single `Read only` badge is not enough.
The operator should never have to infer seeding ability or local-repair outcome from a permission label alone.

## The fixed review order

Any one-way/right-limited subject or member page should render sections in this order:

1. **Granted authority**
2. **Local divergence policy**
3. **Relay/seeding posture**
4. **Current local exceptions**
5. **Receipt shelf**

### 1) Granted authority

Show clearly:

- may read namespace?
- may fetch bytes?
- may materialize locally?
- may publish edits upstream?
- may issue offers or grants?
- may relay already-held bytes to other authorized members?

This prevents `read-only` from hiding network-participation truth.

### 2) Local divergence policy

Show exactly what happens if the restricted member:

- edits a file
- deletes a file
- renames a file
- adds a new file
- creates a new directory

For each case, say whether the result is:

- local-only fork retained
- automatic revert to upstream truth
- restored old name / old bytes
- blocked pending review
- divergence that stops sync for that path

The product should never require support-article memory to answer basic local-edit questions.

### 3) Relay/seeding posture

Show separately whether the member can:

- seed unchanged bytes it already possesses
- satisfy new member fetches
- serve as a transit/helper for ordinary replication
- relay only while policy epoch remains current

This is a network role, not a write right.
It deserves its own row.

### 4) Current local exceptions

If the member already has local divergent paths, the page should list them as classified exceptions:

- `local rename retained`
- `local edit diverged`
- `deleted locally, restore pending`
- `new local file unsynced`
- `local fork sealed`

Primary actions should include:

- `Restore upstream truth here`
- `Keep local fork sealed`
- `Promote through reviewed authority change`
- `Exclude from local mount only`

### 5) Receipt shelf

Every relevant mutation or repair must emit a receipt proving:

- authority posture at time of action
- divergence class
- whether overwrite/revert policy acted
- whether local-only bytes were preserved, restored, or sealed
- relay/seeding posture in effect

A later operator should be able to answer:

> was this member merely forbidden to write upstream, or also unable to seed, and what happened to its local edits?

## What must never happen automatically

The product must never automatically:

- imply that `may not write upstream` also means `cannot relay authorized bytes`
- silently destroy local divergent bytes without a receipt
- pretend a rename or delete behaved like an edit when the consequences differ
- hide per-path sync stoppage behind a generic read-only badge

## Why this is worth the trouble

One-way sharing is valuable, but it becomes misleading when one label stands in for rights, repair policy, and network role all at once.
AnonSync can do better by separating write denial, local divergence handling, and relay/seeding truth into one explicit contract.
'''

EVAL_APPEND = '''

## Revision addendum — hidden service state, warning-tier targets, subtree graphs, and one-way truth

This pass found a better cluster of current Resilio evidence than another round of abstract doctrine would have.
The strongest new reasons not to clone the interface are no longer about visual preference.
They are about where the product still keeps meaning today: hidden control state, warning-tier targets, subtree graph caveats, and overloaded one-way semantics.

## Q. Hidden service state still acts as part of the operator contract

Current official Resilio docs still say `.sync` is critical, that deleting or corrupting it suspends synchronization, that the fix for `Service files missing` is remove the share, delete `.sync`, and add it back, and that cloning a Sync instance is unsupported because copied internal state can produce strange behavior.
Separate docs still say `IgnoreList` and `StreamsList` live as hidden text files inside `.sync`, that same `IgnoreList` on all peers is advisable but not compulsory, and that xattrs are governed through `StreamsList`, not through ordinary ignore rules.

That is candid support guidance.
It is still a strong reason not to clone the operator contract.
If hidden service files are carrying subject identity, rule truth, and repair semantics, then the public interface is not yet the whole truth.

AnonSync should therefore keep one stricter rule:

- hidden service artifacts may exist internally, but anything operator-meaningful must appear on one visible rule and service-state ledger
- repair must classify whether continuity is preserved, forked, quarantined, or rebuilt
- copying residue or foreign hidden state must never silently inherit continuity

## R. Warning-tier targets still need a steady-state contract, not a setup warning

Current official Resilio docs still say SMB targets can lose continuous notifications and then rely on full rescans, that permissions loss can stop delivery, that lock behavior depends on the SMB implementation, and that direct access outside Samba can damage files or roll back changes.
Separate docs still show materially different symlink behavior by platform and still force xattr handling through whitelisted hidden streams state.

Again, that is useful honesty.
But it still teaches degraded-target semantics through scattered warnings rather than one steady-state contract the operator can revisit later.

AnonSync should therefore keep a stronger requirement:

- any knowingly weaker target must publish one durable warning-tier contract
- notification posture, outsider-writer risk, blocked entry classes, and runtime drift must stay visible after bind day
- `allowed but weaker` should never read like `ordinary local-native path`

## S. Nested child sharing still bends topology and propagation

Current official Resilio docs still say nested child sharing is possible only with limitations: parent and child must both hold stronger rights, both become separate sync folders, the child is indexed and rescanned twice on the shared machine, parent-only peers do not seed child-only peers, and both parent and child must have Selective Sync disabled.
The same docs also say child-originated changes can still propagate onward through the parent graph when a shared member bridges both.

That is a genuine graph contract.
It should not be learned from caveats alone.

AnonSync should therefore keep another stronger rule:

- nested subtree publishing must open one topology review
- the review must make non-transitive seeding, shared-bridge transit, and duplicate indexing cost explicit
- graph admissibility is not the same thing as ordinary share creation

## T. Read-only still hides three different truths under one label

Current official Resilio docs still say read-only peers cannot sync local changes back, that local changes can stop synchronization for a file, that `Overwrite any changed files` restores or re-downloads some classes of local divergence but not added files, and that read-only peers can still transfer unmodified files to newly joined peers because of the P2P protocol.

That is exactly the kind of overloaded meaning AnonSync should avoid.
`Read only` is doing too much work at once:

- write propagation denied
- local divergence behavior
- relay/seeding role

AnonSync should therefore keep one clearer split:

- authority to write upstream
- policy for local divergent edits, deletes, renames, and additions
- right or ability to relay already-held bytes onward

## The interface consequences for AnonSync

This pass adds four more direct interface consequences:

### 13) Hidden service state must be replaced by a visible rule/service-state ledger

Because current docs still require operators to reason from `.sync`, `IgnoreList`, `StreamsList`, and remove/re-add repair ritual, AnonSync now requires one ledger that separates operator-authored policy from daemon-owned state and classifies repair continuity honestly.

### 14) Warning-tier targets must publish steady-state semantics and drift

Because current degraded-target docs still teach too much through setup warnings, AnonSync now requires one target contract page that keeps notification posture, outsider-writer risk, blocked entry classes, and runtime drift adjacent.

### 15) Nested subtree publishing must be reviewed as graph mutation

Because current child-share docs still make propagation and seeding caveats visible only after you understand the graph, AnonSync now requires one topology review page that previews bridge members, non-transitive seeding, and indexing cost.

### 16) One-way posture must split write denial, local repair, and relay capability

Because current read-only docs still collapse those truths into one permission label plus caveats, AnonSync now requires one explicit write-vs-seed-vs-repair model on every limited-right member or subject surface.
'''

PD_APPEND = '''

### Doctrine 55 — hidden service state must not be the public contract

Hidden folders, marker files, stream allowlists, and other daemon artifacts may exist internally.
They must never be the only place where operator-meaningful policy, identity, or repair truth lives.
A serious product should surface those meanings on one visible rule/service-state ledger and classify whether repair preserved or forked continuity.

### Doctrine 56 — warning-tier targets need steady-state truth, not setup-time warnings

If a target is allowed but weaker — for example because notifications degrade, outsider writers can bypass coordination, or some entry classes are blocked — the product should keep that weakness visible after bind day.
The operator should be able to answer what semantics are promised here now, what drift has occurred, and what is merely tolerated.

### Doctrine 57 — nested subtree sharing is a graph decision, not an ordinary publish action

A child subtree inside a parent subject changes propagation, transit, indexing cost, and admissibility.
The product should therefore review nested topology explicitly instead of teaching it through side effects and support caveats.

### Doctrine 58 — one-way rights, local divergence, and relay role are separate truths

A member that may not write upstream can still have local edits, local forks, restore policy, and even some relay/seeding capability.
The product should not compress those into one overloaded `Read only` badge.
'''

ROADMAP_APPEND = '''

## Revision addendum — next interface tranche after hidden state and one-way reassessment

The next high-value interface tranche after this pass should now explicitly prioritize:

1. rule-ledger and service-state work so hidden control files stop carrying the public explanation for ignore, streams/xattrs, and continuity repair
2. warning-tier target work so NAS/SMB-style binds keep notification posture, outsider-writer risk, blocked entry classes, and drift visible after setup day
3. nested-topology work so parent/child subtree publishing receives one graph review instead of overlap caveats and non-transitive seeding surprises
4. one-way/right-limited work so write denial, local divergence handling, and relay/seeding truth become separate inspectable rows with durable receipts
'''

SOURCES_APPEND = '''

## Revision addendum — hidden service state, warning-tier targets, subtree graphs, and one-way truth

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier offer/route/restore passes.
The new questions were:

> if current sync products still feel tempting to clone, where do their official docs show that **hidden service state** is still part of the practical operator contract?

> where do current docs prove that **warning-tier targets** still need a durable semantic contract rather than a one-time warning?

> what current evidence most clearly shows that **nested subtree sharing** is a graph mutation with propagation and seeding caveats, not an ordinary share action?

> how do current docs prove that **read-only** still overloads write denial, local repair, and relay/seeding truth?

The most load-bearing source set for this pass was the maintained v3 line together with docs on hidden `.sync` service state, `IgnoreList`, `StreamsList`, cloning, service-file corruption, SMB behavior, symlink behavior, nested subtree sharing, and one-way synchronization.

### Additional Resilio official sources emphasized in rev0129

- Cloning Sync  
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- Is it possible to share a nested folder separately?  
  https://help.resilio.com/hc/en-us/articles/205506159-Is-it-possible-to-share-a-nested-folder-separately

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible
'''


def write(path: Path, text: str):
    path.write_text(text, encoding='utf-8')


def append_once(path: Path, marker: str, addition: str):
    text = path.read_text(encoding='utf-8')
    if marker in text:
        return
    if not text.endswith('\n'):
        text += '\n'
    text += addition.strip('\n') + '\n'
    path.write_text(text, encoding='utf-8')


write(ROOT / 'README.md', README)
write(DOCS / '00-status.md', STATUS)
write(DOCS / '177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md', DOC177)
write(DOCS / '178-warning-tier-target-notification-drift-and-out-of-band-writer-interface-spec.md', DOC178)
write(DOCS / '179-parent-child-subtree-topology-and-non-transitive-seeding-interface-spec.md', DOC179)
write(DOCS / '180-read-only-local-divergence-overwrite-and-seeding-ceiling-interface-spec.md', DOC180)
append_once(DOCS / '10-resilio-sync-evaluation.md', '## Revision addendum — hidden service state, warning-tier targets, subtree graphs, and one-way truth', EVAL_APPEND)
append_once(DOCS / '20-product-direction.md', '### Doctrine 55 — hidden service state must not be the public contract', PD_APPEND)
append_once(DOCS / '50-roadmap.md', '## Revision addendum — next interface tranche after hidden state and one-way reassessment', ROADMAP_APPEND)
append_once(DOCS / 'sources.md', '## Revision addendum — hidden service state, warning-tier targets, subtree graphs, and one-way truth', SOURCES_APPEND)
print('Applied rev0129 updates')
