from pathlib import Path
import re

ROOT = Path('/mnt/data/anonsync_rev0137/anonsync_rev0137')
DOCS = ROOT / 'docs'

rev = 'rev0137'
timestamp = '2026.03.19.18.23'
codename = 'sleepledgerverbcacheharbor'

# --- new interface specs ---
(DOCS / '209-battery-saver-auto-sleep-and-participation-honesty-interface-spec.md').write_text('''# Battery saver, auto-sleep, and participation-honesty interface spec

## Purpose

The archive already had pause semantics, suspended-seat resume, and constrained-seat capability language.
What it still lacked was one explicit contract for another very common but semantically slippery case:

> a seat whose participation in the mesh is intentionally intermittent because of battery policy, sleep cadence, charging state, or platform resource posture.

Current official Resilio docs make this seam sharper than a generic `mobile background is limited` shrug.
They still say Android Auto Sleep can stop Sync when no transfers are in progress, can wake only on a configured interval, and can use a different interval while charging.
They also still say peers do not see the device as online while the core is asleep, and that Battery Saver can force Sync to stop below a chosen charge threshold.

That is all operationally real.
It is still not a good participation contract.
An operator should not have to infer whether a seat is live, sleeping on purpose, power-blocked, or merely broken from a single `offline` badge.

## Core decision

AnonSync should treat power policy as part of the public participation contract.
Every seat must therefore publish four separate truths:

- whether it is technically capable of continuous participation
- whether local policy currently allows continuous participation
- what cadence it will use when conserving power
- what other peers should infer when the seat is absent

A sleeping seat must never masquerade as a mysterious failed seat, and a battery-blocked seat must never masquerade as an operator-approved semantic pause.

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- power conservation can deliberately take the core offline while looking externally like an ordinary disappearance
- wake cadence can change by charging state, which means `online enough` is conditional rather than one stable property
- battery floor can force a stop without one shared participation receipt that other operators can inspect later
- background availability, sleep cadence, and power stop can all affect freshness and confidence even before any explicit conflict is visible

AnonSync should therefore keep one stronger rule:

> power policy is not just device preference; it is a shared liveness contract.

## Fixed review order

Every constrained or power-managed seat should render the same sections in the same order:

1. **Participation class now**
2. **Cadence and wake promises**
3. **Absence interpretation**
4. **Power-policy receipt**

### 1) Participation class now

This section should show:

- continuous participation supported or not
- current power mode:
  - continuous
  - idle-sleep eligible
  - scheduled wake only
  - charging-boosted cadence
  - battery-blocked
  - runtime-killed / unplanned suspension
- whether the seat is currently visible to peers
- which policy or runtime fact set that state

The operator must be able to answer: **is this seat absent because it is conserving power, because it is blocked, or because it is actually unhealthy?**

### 2) Cadence and wake promises

This section should show:

- idle-to-sleep threshold if any
- wake interval while on battery
- wake interval while charging
- whether local changes wake the seat immediately or only on schedule
- whether remote arrivals wait for the next wake cycle

The operator must be able to answer: **how stale can this seat honestly become before that is surprising?**

### 3) Absence interpretation

This section should show:

- what peers should infer from the seat being absent
- freshness confidence under the current cadence
- whether conflict or resume review is likely if local edits accumulate during absence
- whether alerts should classify absence as expected, overdue, or suspicious

The operator must be able to answer: **what does `offline` mean for this seat right now?**

### 4) Power-policy receipt

This section should show:

- policy chosen
- cadence chosen
- battery stop floor if any
- charging override if any
- effect on visibility and freshness promises
- whether the policy is seat-wide or subject-scoped

The operator must be able to answer: **what participation promise did I actually configure?**

## Main surface

AnonSync should expose a compact seat row such as:

- `continuous participant`
- `scheduled-wake seat · every 30m on battery`
- `charging boost · every 5m while plugged in`
- `battery floor active below 20%`
- `absence currently expected under power policy`

The product must never let `offline` be the only public truth when the real cause is reviewed power cadence.

## Object model implications

AnonSync should add or strengthen these objects:

- `seat_participation_class`
- `power_policy_review`
- `wake_cadence_contract`
- `absence_interpretation`
- `power_policy_receipt`

Suggested fields for `wake_cadence_contract`:

- `seat_id`
- `continuous_supported`
- `idle_sleep_enabled`
- `battery_wake_interval`
- `charging_wake_interval`
- `battery_stop_floor_percent`
- `peer_visibility_when_sleeping`
- `freshness_confidence_budget`

## Event language

Use explicit phrases such as:

- `seat entered scheduled sleep under reviewed power policy`
- `seat hidden from peers while core is asleep`
- `battery floor stopped participation`
- `charging cadence override enabled`
- `absence remains expected under current wake contract`

Avoid vague lines such as:

- `device offline`
- `background disabled`
- `sync may be delayed`

## CLI shape

Example commands:

```text
anonsync seat power show <seat>
anonsync seat power review <seat>
anonsync seat power apply <review> --wake 30m --charging-wake 5m --stop-below 20
anonsync seat power receipt <id>
```

The CLI must expose the same cadence and absence-meaning truth as the local web UI.

## Failure and edge cases

### Charging cadence differs from battery cadence

The product must show both, not just the currently active one.
Otherwise operators will misread resumed bursts as mysterious intermittence.

### Runtime was killed outside reviewed policy

That is not `scheduled sleep`.
It should be classified as unplanned suspension and may feed directly into the resume-quarantine flow.

### Operator wants aggressive battery saving

That is allowed.
The product must still publish the resulting freshness and visibility downgrade before apply.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still leave too much meaning about wake cadence, battery floors, and peer visibility scattered across mobile settings pages.
AnonSync should instead publish one participation contract where power policy, absence meaning, and freshness cost stay visible together.
''')

(DOCS / '210-file-send-ledger-expiry-retention-and-byte-truth-interface-spec.md').write_text('''# File-send ledger, expiry, retention, and byte-truth interface spec

## Purpose

The archive already had snapshot-send lineage and staged-transfer visibility language.
What it still lacked was one explicit contract for a smaller but very common seam:

> the difference between a transfer record, a still-redeemable offer, and local bytes that happen to remain on disk.

Current official Resilio docs make this seam sharper than a generic `shared links history` feature.
They still say mobile `Shared links` lists both uploaded and downloaded transfers, that received files also appear in a `Downloads` folder, that file-send links are valid for three days and currently cannot be changed, that iOS can remove a downloaded file from the device while its transfer history still remains visible, and that removing an item from `Shared links` can remove it only from Sync UI while the file remains on the system.
Current power-user preferences also still define how many expired transfers or how many days of expired transfers remain in the UI.

That is all useful.
It is still not a good object model.
A visible row in history is not the same thing as a redeemable offer, and neither is the same thing as bytes still resident on the seat.

## Core decision

AnonSync should split one-time handoff state into three explicit objects:

- **offer window** — can anyone still redeem this handoff?
- **ledger row** — what historical record remains visible?
- **byte residency** — do local payload bytes still exist on this seat?

Any action that changes one of those must say whether the other two change too.

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- expiry and retention can be different but are easy to read as the same thing
- a row can remain visible after bytes are gone
- bytes can remain after the row is hidden from one surface
- fixed mobile inboxes make it even easier to confuse `download history`, `downloaded bytes`, and `share offer`

AnonSync should therefore keep one stronger rule:

> a transfer list row is never the canonical truth about where the bytes are or whether the handoff is still live.

## Fixed review order

Every one-time handoff surface should render the same sections in the same order:

1. **Offer window**
2. **Ledger retention**
3. **Local byte presence**
4. **Removal consequence**

### 1) Offer window

This section should show:

- whether the handoff is still redeemable
- expiry time
- whether expiry is fixed or operator-chosen
- whether reissue creates a new offer or extends the same one

The operator must be able to answer: **can anyone still use this handoff?**

### 2) Ledger retention

This section should show:

- whether the row is active, expired, hidden, or archived from view
- how long expired rows remain visible
- what evidence the row preserves after expiry
- whether hiding the row is cosmetic or destructive

The operator must be able to answer: **what historical proof remains even if the transfer is over?**

### 3) Local byte presence

This section should show:

- whether bytes still exist locally
- where they live
- whether they are ordinary subject bytes, receipt-inbox bytes, or temporary transfer bytes
- whether deleting them changes the ledger or the offer window

The operator must be able to answer: **do the bytes still exist here, and what kind of local copy are they?**

### 4) Removal consequence

This section should show distinct actions such as:

- `hide row only`
- `delete local payload only`
- `revoke live offer`
- `purge row and local payload`

Each must declare which of the three objects changes.

The operator must be able to answer: **what exactly disappears if I press this?**

## Main surface

AnonSync should show one compact state stack for each handoff:

- `offer expired`
- `ledger retained 30d`
- `local payload still present`

or:

- `offer revoked`
- `ledger hidden from Home`
- `payload removed from this seat`

The product must never make the operator infer byte truth from a lingering history row.

## Object model implications

AnonSync should add or strengthen these objects:

- `snapshot_offer_window`
- `transfer_ledger_entry`
- `transfer_payload_presence`
- `transfer_removal_review`
- `transfer_retention_receipt`

Suggested fields for `transfer_ledger_entry`:

- `transfer_id`
- `subject_kind`
- `offer_state`
- `expiry_at`
- `ledger_visibility`
- `retention_until`
- `local_payload_presence`
- `payload_path`

## Event language

Use explicit phrases such as:

- `offer expired; ledger retained`
- `payload removed from receipt inbox; ledger preserved`
- `row hidden from UI only; local payload unchanged`
- `live offer revoked; bytes on this seat unchanged`

Avoid vague lines such as:

- `removed`
- `cleared`
- `expired item deleted`

## CLI shape

Example commands:

```text
anonsync transfer show <id>
anonsync transfer retention review <id>
anonsync transfer remove <id> --row-only
anonsync transfer remove <id> --payload-only
anonsync transfer receipt <id>
```

The CLI must expose the same split between offer, ledger, and bytes as the local web UI.

## Failure and edge cases

### Expired offer but bytes still local

The product should say exactly that.
No resurrection or cleanup action should pretend the payload vanished merely because redemption ended.

### Row hidden but bytes remain on disk

This must be classified as visibility change, not deletion.

### Bytes deleted but ledger retained for audit

That is allowed and often useful.
The row must clearly say that the payload is gone.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still let expiry, history retention, UI removal, and on-disk bytes drift apart across several surfaces.
AnonSync should instead expose one transfer ledger where offer truth, row truth, and byte truth are visibly separate.
''')

(DOCS / '211-ingress-verb-taxonomy-and-mobile-source-capture-interface-spec.md').write_text('''# Ingress verb taxonomy and mobile source-capture interface spec

## Purpose

The archive already had offer/claim, snapshot-send, and capture-ingest language.
What it still lacked was one explicit contract for another common interface failure:

> too many entry verbs that all sound like `add` or `share` even though they create different subject kinds, rights, and retention promises.

Current official Resilio docs make this seam sharper than a generic menu-layout complaint.
They still say Android exposes `Send file`, `Create folder`, `Add backup`, `Scan QR code`, and `Enter a key or link` from one `+` menu.
They still say mobile initiation can mean creating a new folder or adding an existing folder from the filesystem on Android, while Android file-manager guidance separately warns users to use `Send via Sync` instead of `Add to Sync` when they want to ship a pack of files.
They also still say backup is a distinct workflow whose desktop side keeps copies even after source-side deletion and whose destination has read-only posture.

That is all useful capability.
It is still not a good verb contract.
Operators should not need support lore to tell whether they are creating a live collaborative subject, adopting an existing tree, shipping a bounded snapshot, or attaching a capture-only source.

## Core decision

AnonSync should expose a fixed ingress verb taxonomy.
Every entry action must declare, before apply:

- what kind of subject it creates or joins
- what the source of truth is
- whether downstream edits are live, bounded, or prohibited
- what source-side deletion means later

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- one `+` cluster mixes collaboration, backup, receipt, and bounded send under adjacent verbs
- external file-manager verbs can look deceptively similar while creating different outcomes
- `backup` sounds storage-like but still creates a share with its own rights and lifecycle
- operators can still end a flow with the wrong subject kind merely because the verb family was overloaded

AnonSync should therefore keep one stronger rule:

> every ingress verb must state its subject kind and authority shape before bytes move.

## Fixed review order

Every ingress action should render the same sections in the same order:

1. **Source material**
2. **Subject kind**
3. **Authority and retention**
4. **Carrier and destination**

### 1) Source material

This section should show:

- whether the source is a single file, selected pack, existing folder, or recurring capture source
- whether the material already belongs to another subject
- whether the action is packaging, binding, or merely offering

The operator must be able to answer: **what material am I acting on?**

### 2) Subject kind

This section should show one of:

- live collaborative subject
- adopted existing subject
- bounded snapshot handoff
- capture-only ingest source
- receipt/claim of external subject

The operator must be able to answer: **what kind of thing will exist after I confirm this?**

### 3) Authority and retention

This section should show:

- who may mutate upstream
- whether downstream edits return live, by reviewed replacement, or never
- what happens if the source later deletes content
- whether landed bytes on the sink persist after source-side cleanup

The operator must be able to answer: **what authority and retention rules come with this verb?**

### 4) Carrier and destination

This section should show:

- whether the action uses QR, link, local handoff, or direct bind
- whether the destination chooses a root now or later
- whether a linked device, named sink, or ordinary recipient is expected

The operator must be able to answer: **where does this go, and how will the recipient experience it?**

## Main surface

AnonSync should keep verbs visibly separate, for example:

- `Create live subject`
- `Adopt existing folder`
- `Send bounded snapshot`
- `Attach capture source`
- `Claim incoming subject`

The product must not collapse those into one `Add` family and hope the later steps teach the difference.

## Object model implications

AnonSync should add or strengthen these objects:

- `ingress_intent`
- `source_material_claim`
- `subject_kind_review`
- `authority_shape_notice`
- `ingress_receipt`

Suggested fields for `ingress_intent`:

- `intent_id`
- `source_material_type`
- `subject_kind`
- `authority_shape`
- `retention_floor`
- `carrier`
- `destination_class`

## Event language

Use explicit phrases such as:

- `created live subject from new folder`
- `adopted existing folder as subject root`
- `sent bounded snapshot; no live mutation return`
- `attached capture source with sink retention floor`
- `claimed incoming subject via portable offer`

Avoid vague lines such as:

- `added`
- `shared`
- `synced`

## CLI shape

Example commands:

```text
anonsync create subject --path <dir>
anonsync adopt folder --path <dir>
anonsync send snapshot --files <paths>
anonsync attach capture-source --path <dir> --sink <seat>
anonsync claim incoming --artifact <offer>
```

The CLI must keep the same verb taxonomy as the local web UI.

## Failure and edge cases

### External file-manager invocation

If the system receives an intent from another app or file manager, it must still stop at the same subject-kind review before commit.

### Backup-like source with no linked sink yet

The product should say `capture source prepared; sink delivery pending`, not masquerade as completed collaboration.

### Multi-file package from mobile

The product should classify it as bounded snapshot unless the operator explicitly chooses to create a live subject.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still spread real semantic differences across adjacent mobile verbs and external file-manager advice.
AnonSync should instead keep one ingress taxonomy where subject kind, authority shape, and retention promise are named up front.
''')

(DOCS / '212-constrained-seat-storage-reclaim-bulk-clear-and-local-copy-truth-interface-spec.md').write_text('''# Constrained-seat storage reclaim, bulk clear, and local-copy truth interface spec

## Purpose

The archive already had placeholder guardrails, storage budgets, and constrained-seat path consent.
What it still lacked was one explicit contract for a frequent follow-on action:

> clearing space on a constrained seat without lying about what disappears locally, what remains fetchable, and what merely leaves one UI surface.

Current official Resilio docs make this seam sharper than a generic `clear cache` option.
They still say iOS keeps files inside the app sandbox, splits storage into `App data` and `User data`, can remove all downloaded file-share receipts at once from the Storage menu, requires the `Downloads` folder for selective per-item deletion, and only allows clearing local copies from sync shares when Selective Sync is enabled.
Current Android share details also still say `Clear` turns all synced files on the device into placeholders and is available only when Selective Sync is on, while `Disconnect` preserves the folder in the system.

That is practical.
It is still not a good reclaim contract.
Local copy removal, placeholder reversion, receipt inbox cleanup, and subject departure are different actions and should not be inferred from whichever surface happened to expose the button.

## Core decision

AnonSync should treat local storage reclaim as a reviewed scope matrix.
Every reclaim action must explicitly declare:

- what byte class is being removed
- whether names remain visible afterward
- whether the bytes are still fetchable later
- whether the subject relationship itself changes

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- one surface can only bulk-clear a class of downloads while another does per-item cleanup
- reclaim ability can depend on subject posture such as Selective Sync being enabled
- `clear` and `disconnect` can sit near each other while changing very different things
- sandbox storage menus and subject-local menus can each tell only part of the byte-truth story

AnonSync should therefore keep one stronger rule:

> reclaim is not one button; it is a scoped local-byte decision with an explicit recovery floor.

## Fixed review order

Every reclaim action should render the same sections in the same order:

1. **Byte class targeted**
2. **Visibility after reclaim**
3. **Recovery floor**
4. **Reclaim receipt**

### 1) Byte class targeted

This section should show whether the action targets:

- receipt-inbox payloads
- materialized shared-file copies
- cached placeholders and metadata only
- whole local subject residency
- app/service data

The operator must be able to answer: **what class of local bytes am I deleting?**

### 2) Visibility after reclaim

This section should show:

- whether names remain visible as placeholders
- whether the subject stays mounted
- whether history rows remain
- whether the path still exists in the local filesystem or app sandbox

The operator must be able to answer: **what will still be visible after the cleanup?**

### 3) Recovery floor

This section should show:

- whether bytes can be fetched again from peers
- whether the local seat still has rights to re-materialize them
- whether the action needs Selective Sync or another posture precondition
- whether some cleanup is bulk-only or can be itemized

The operator must be able to answer: **what can I get back later, and under what conditions?**

### 4) Reclaim receipt

This section should show:

- byte classes removed
- placeholder or mount effect
- recovery prerequisites
- any remaining ledger or history records
- whether subject membership changed

The operator must be able to answer: **what local space action actually happened here?**

## Main surface

AnonSync should expose reclaim actions as explicit rows such as:

- `remove local receipt payloads`
- `evict materialized copies; keep placeholders`
- `leave subject mounted`
- `disconnect subject; keep filesystem copy`
- `purge app cache only`

The product must never let `clear` stand in for all of those.

## Object model implications

AnonSync should add or strengthen these objects:

- `local_reclaim_review`
- `byte_residency_class`
- `reclaim_scope_matrix`
- `reclaim_recovery_floor`
- `reclaim_receipt`

Suggested fields for `reclaim_scope_matrix`:

- `seat_id`
- `subject_id`
- `byte_classes[]`
- `placeholder_after`
- `path_persists`
- `history_persists`
- `rematerialization_allowed`
- `preconditions[]`

## Event language

Use explicit phrases such as:

- `receipt payloads removed; transfer ledger retained`
- `materialized files evicted; placeholders preserved`
- `subject disconnected; local path kept`
- `reclaim blocked because re-materialization posture is unavailable`

Avoid vague lines such as:

- `storage cleared`
- `downloads removed`
- `share cleaned up`

## CLI shape

Example commands:

```text
anonsync reclaim review --seat <seat> --subject <subject>
anonsync reclaim apply <review> --evict materialized
anonsync reclaim apply <review> --remove receipt-payloads
anonsync reclaim receipt <id>
```

The CLI must expose the same scope matrix as the local web UI.

## Failure and edge cases

### Reclaim requested on a non-placeholder posture

The product should explain the missing precondition and offer a reviewed posture change if appropriate, not just hide the action.

### Bulk-only cleanup surface

If a platform only supports bulk cleanup for a byte class, the review must say so plainly before apply.

### History row survives cleanup

That must be presented as a retained ledger fact, not as evidence that bytes still exist.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still split reclaim truth across storage menus, download folders, share details, and posture prerequisites.
AnonSync should instead expose one reclaim matrix where local byte class, placeholder effect, and recovery floor stay visible together.
''')

# README rewrite
readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0136` and does twelve specific things:

1. Pushes the **Resilio Sync** evaluation further with current official evidence about battery-saver / auto-sleep participation cadence, file-send ledger-versus-byte truth, overloaded mobile ingress verbs, and constrained-seat storage reclaim semantics.
2. Sharpens the non-clone reason again: the remaining problem is not missing features but too much operator-meaningful truth spread across power-policy pages, transfer-history retention, mobile `+` menus, file-manager advice, storage menus, and posture-gated cleanup actions.
3. Adds a new **battery saver / auto-sleep / participation honesty** interface spec so constrained-seat liveness is published as a reviewed cadence contract instead of looking like random offline drift.
4. Adds a new **file-send ledger / expiry / retention / byte truth** interface spec so transfer rows, redeemable offers, and surviving payload bytes stop masquerading as one thing.
5. Adds a new **ingress verb taxonomy / mobile source-capture** interface spec so `create`, `adopt`, `send snapshot`, `attach capture source`, and `claim incoming` become visibly different subject-creation acts.
6. Adds a new **constrained-seat storage reclaim / bulk clear / local copy truth** interface spec so local cleanup becomes a reviewed byte-scope action instead of whichever button happened to be available on that surface.
7. Refreshes the **Resilio evaluation** so the comparison now also covers Android Auto Sleep / Battery Saver, three-day fixed file-send expiry, transfer-row retention after expiry, mobile `Shared links` versus `Downloads` drift, mobile `+` verb overload, and selective-sync-gated reclaim.
8. Refreshes the **product direction** so power cadence, ledger-versus-byte truth, verb taxonomy, and reclaim-scope honesty become doctrine rather than support lore.
9. Refreshes the **roadmap** so the next tranche now explicitly includes power-policy receipts, transfer-ledger split, ingress-intent review, and reclaim-scope review.
10. Refreshes the **source notes** so the official evidence set now explicitly includes `Configuring Auto Sleep & Battery Saver (Android)`, `Sharing files (Android)`, `Sharing files (iOS)`, `Storage Management on iOS`, `Sync interface on Android`, `Initiate sharing on mobile platforms`, and `How to Back up data (Android only)`.
11. Keeps the archive tight by extending existing pause, constrained-seat, snapshot-send, capture-ingest, placeholder, and resume grammar instead of inventing unrelated subsystems.
12. Preserves the earlier storage-truth, identity-salvage, host-custody, compatibility-gate, mobile-seat, roundtrip-edit, shell-equivalence, resume-quarantine, work-ledger, repair-ladder, metadata, route, restore, naming, and topology decisions while giving them stronger power-cadence, transfer-ledger, ingress-taxonomy, and reclaim companions.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The reason is sharper again and still evidence-based.
Current official docs still show a maintained Sync v3 line through `3.1.2.1076` in late 2025, practical link and arrival flows, selective materialization, mobile support, and a large body of support material.
That is why Resilio remains worth studying rather than dismissing.

But the better non-clone reason is now this:

> Resilio still solves many real operator problems while leaving too much meaning about **when a seat is truly participating versus sleeping on policy**, **whether a file-send row proves a live offer or only history**, **which `add/share/send/backup` verb is creating which subject kind**, and **whether local cleanup removes bytes, rows, placeholders, or membership** distributed across battery settings, shared-links history, mobile `+` menus, external file-manager caveats, and storage screens where AnonSync wants one power receipt, one transfer ledger, one ingress taxonomy, and one reclaim scope matrix.

The most important current examples are now:

- current Android docs still say Auto Sleep can take the core offline when idle, wake only on a configured interval, and use a different interval while charging
- current Android docs still say Battery Saver can force Sync to stop below a chosen charge level
- current mobile file-send docs still say one-time file links are valid for three days and currently cannot be changed
- current iOS/mobile docs still say a downloaded file can be removed from the device while transfer history remains visible, and removing an item from `Shared links` may only remove it from Sync UI while the file stays on the system
- current Android docs still expose `Send file`, `Create folder`, `Add backup`, `Scan QR code`, and `Enter a key or link` from one menu while separate file-manager guidance says `Send via Sync` is not the same as `Add to Sync`
- current iOS/Android docs still split local cleanup across Storage, Downloads, and share-detail surfaces, with some reclaim paths available only when Selective Sync is enabled

So the direction stays the same:

- **borrow** Resilio's practical handoff, linked-device convenience, selective materialization, and candid operational guidance
- **reinterpret** them through one explicit power-participation contract, one transfer-ledger split, one ingress verb taxonomy, and one local-reclaim scope matrix
- **refuse** any interface contract where battery policy, history rows, overloaded verbs, or storage menus stand in for participation truth, transfer truth, subject-kind truth, or reclaim truth

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/209-battery-saver-auto-sleep-and-participation-honesty-interface-spec.md`
4. `docs/210-file-send-ledger-expiry-retention-and-byte-truth-interface-spec.md`
5. `docs/211-ingress-verb-taxonomy-and-mobile-source-capture-interface-spec.md`
6. `docs/212-constrained-seat-storage-reclaim-bulk-clear-and-local-copy-truth-interface-spec.md`
7. `docs/205-constrained-seat-path-consent-and-removable-storage-capability-interface-spec.md`
8. `docs/206-external-editor-roundtrip-import-copy-and-replacement-review-interface-spec.md`
9. `docs/207-shell-extension-loss-and-in-app-capability-equivalence-interface-spec.md`
10. `docs/208-suspended-seat-resume-quarantine-and-offline-precedence-interface-spec.md`
11. `docs/201-storage-budget-scope-staging-headroom-and-actual-drive-truth-interface-spec.md`
12. `docs/202-identity-root-health-folder-list-salvage-and-relink-ladder-interface-spec.md`
13. `docs/203-host-ownership-claim-dual-instance-collision-and-safe-branching-interface-spec.md`
14. `docs/204-release-cohort-compatibility-control-plane-migration-and-link-gate-interface-spec.md`
15. `docs/197-hidden-work-phase-ledger-and-honest-progress-interface-spec.md`
16. `docs/198-preseed-reuse-dedup-proof-and-local-block-witness-interface-spec.md`
17. `docs/199-integrity-rebuild-reindex-and-subject-repair-ladder-interface-spec.md`
18. `docs/200-disconnect-remove-and-placeholder-eviction-contract-interface-spec.md`
19. `docs/193-ignore-rule-agreement-drift-and-visible-rule-ledger-interface-spec.md`
20. `docs/194-metadata-stream-policy-xattr-carriage-and-bundle-fidelity-interface-spec.md`
21. `docs/195-transfer-staging-partial-artifacts-and-finalize-visibility-interface-spec.md`
22. `docs/196-capture-only-ingest-sink-and-retention-floor-interface-spec.md`
23. `docs/189-clock-authority-drift-budget-and-invalid-time-quarantine-interface-spec.md`
24. `docs/190-locked-writer-delay-profile-and-quiescent-commit-interface-spec.md`
25. `docs/191-link-node-alias-edge-and-target-boundary-admission-interface-spec.md`
26. `docs/192-pause-scheduler-and-destructive-signal-separation-interface-spec.md`
27. `docs/156-projection-parity-and-surface-capability-contract-interface-spec.md`
28. `docs/149-interface-shell-navigation-and-persistent-context-spec.md`
29. `docs/38-operator-workbench-interface-spec.md`
30. `docs/39-interface-pattern-language.md`
31. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and interface doctrine
- `docs/209-battery-saver-auto-sleep-and-participation-honesty-interface-spec.md` — power-cadence and seat-visibility contract for constrained or battery-managed participants
- `docs/210-file-send-ledger-expiry-retention-and-byte-truth-interface-spec.md` — transfer-ledger contract for offer expiry, retained history, and surviving local payload bytes
- `docs/211-ingress-verb-taxonomy-and-mobile-source-capture-interface-spec.md` — ingress-intent contract for live subjects, adopted folders, bounded snapshots, and capture sources
- `docs/212-constrained-seat-storage-reclaim-bulk-clear-and-local-copy-truth-interface-spec.md` — local-reclaim scope contract for constrained-seat cleanup, placeholder reversion, and subject-preserving space recovery
- `docs/205-constrained-seat-path-consent-and-removable-storage-capability-interface-spec.md` — seat-capability and storage-consent contract for constrained/mobile binds and removable-storage ceilings
- `docs/206-external-editor-roundtrip-import-copy-and-replacement-review-interface-spec.md` — explicit roundtrip-edit contract for exported copies, returned candidates, and replacement continuity
- `docs/207-shell-extension-loss-and-in-app-capability-equivalence-interface-spec.md` — shell-health and in-app-equivalence contract for Finder/Explorer action loss without semantic loss
- `docs/208-suspended-seat-resume-quarantine-and-offline-precedence-interface-spec.md` — chronology-confidence contract for suspended-seat return and late offline mutations
- `docs/50-roadmap.md` — near-term phases and exit criteria
- `docs/sources.md` — current external source notes for this revision
'''
(ROOT / 'README.md').write_text(readme)

# Status rewrite
status = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0136`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based, current, and specific not only about constrained/mobile seats, imported copies, shell dependence, and resumed seats, but now also about **power-managed participation cadence**, **transfer-ledger versus byte truth**, **mobile ingress verb overload**, and **constrained-seat storage reclaim semantics**
- spend more time on **interface specs**, especially where current sync products still ask the operator to infer participation, transfer state, subject kind, or cleanup scope from battery settings, history rows, overloaded menus, and posture-gated buttons
- preserve the shell/workspace, projection-parity, arrival-placement, path-comparison, quiescence, clock, repair, capture-ingest, and re-entry decisions already made unless fresh evidence actually breaks them
- make a better explicit case for why AnonSync should not inherit Resilio's sleep/offline ambiguity, transfer-row ambiguity, mobile `+` menu ambiguity, or cleanup-surface ambiguity

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {rev}
- Timestamp: {timestamp} America/New_York
- Codename: {codename}

- a further-tightened **Resilio evaluation** that now treats power-managed participation, file-send ledger truth, ingress verb taxonomy, and constrained-seat reclaim scope as additional non-clone reasons
- a new **battery saver / auto-sleep / participation honesty** interface spec so power policy becomes a visible liveness contract instead of mysterious offline behavior
- a new **file-send ledger / expiry / retention / byte truth** interface spec so offer state, history visibility, and local payload presence stop collapsing into one row
- a new **ingress verb taxonomy / mobile source-capture** interface spec so create/adopt/send/backup/claim become visibly different subject-creation acts
- a new **constrained-seat storage reclaim / bulk clear / local copy truth** interface spec so cleanup becomes a reviewed scope matrix instead of surface folklore
- updated top-level docs so the archive now makes firmer choices about power cadence, ledger-versus-byte truth, ingress taxonomy, and reclaim honesty

## The main shift

`rev0137` closes the next seam:

> it is not enough to have strong seat-capability, roundtrip-edit, shell-parity, resume-quarantine, and capture-ingest language if the operator still has to reconstruct **whether a seat is absent by policy or by failure**, **whether a file-send row proves a still-live offer or only old history**, **which ingress verb is creating which subject kind**, and **whether local cleanup removes bytes, rows, placeholders, or membership** from battery pages, transfer lists, overloaded menus, and storage screens.

That changes the archive in eight specific ways:

- power management can now publish continuous participation, scheduled wake, charging override, battery-blocked stop, and peer-visibility meaning separately
- freshness and absence can now be interpreted through one reviewed cadence contract instead of generic offline status
- snapshot/file-send history can now separate redeemable offer, retained ledger row, and surviving local payload bytes
- transfer cleanup can now distinguish row hiding, offer revocation, payload deletion, and combined purge with receipts
- mobile ingress can now declare live subject, adopted folder, bounded snapshot, capture-only source, and incoming claim as visibly different actions
- file-manager and in-app entrypoints can now land in one shared ingress review instead of semantic drift between `Send via` and `Add`
- constrained-seat cleanup can now classify receipt payload removal, placeholder reversion, local-copy eviction, and full disconnect separately
- reclaim actions can now publish recovery floor and posture preconditions instead of hiding them behind whichever menu exposes the action

## Files added in this revision

- `docs/209-battery-saver-auto-sleep-and-participation-honesty-interface-spec.md`
- `docs/210-file-send-ledger-expiry-retention-and-byte-truth-interface-spec.md`
- `docs/211-ingress-verb-taxonomy-and-mobile-source-capture-interface-spec.md`
- `docs/212-constrained-seat-storage-reclaim-bulk-clear-and-local-copy-truth-interface-spec.md`
- `update_rev0137.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/20-product-direction.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## The current stance in one paragraph

Resilio remains worth studying because current official docs still show a maintained Sync v3 line, practical linked-device and file-send flows, selective materialization, and extensive operational guidance.
But those same docs still show power-managed participation hidden inside Auto Sleep/Battery Saver settings, transfer truth hidden across Shared links and Downloads surfaces, subject kind hidden behind overloaded mobile verbs, and local cleanup hidden across storage and share-detail menus with posture-dependent behavior.
That is enough reason for AnonSync to prefer one power-participation receipt, one transfer-ledger split, one ingress taxonomy, and one reclaim scope matrix instead of cloning Resilio's support-lore-driven contract.
'''
(DOCS / '00-status.md').write_text(status)

# Update docs/10 title and intro
p10 = DOCS / '10-resilio-sync-evaluation.md'
text10 = p10.read_text()
text10 = re.sub(r'^# .*$', '# Resilio Sync evaluation (power, transfer-ledger, ingress, and reclaim pass)', text10, count=1, flags=re.M)
text10 = text10.replace('It now adds another cluster that matters just as much for a non-clone decision: **constrained/mobile seat capability**, **external-editor roundtrip truth**, **shell-extension dependence**, and **suspended-seat precedence after background gaps**, while preserving the earlier work on storage truth, control-plane salvage, path continuity, projection honesty, opaque custody, and repair ladders.',
                      'It now adds another cluster that matters just as much for a non-clone decision: **power-managed participation cadence**, **file-send ledger versus byte truth**, **mobile ingress verb taxonomy**, and **constrained-seat reclaim semantics**, while preserving the earlier work on constrained seats, external-editor roundtrips, shell equivalence, resume quarantine, storage truth, control-plane salvage, path continuity, projection honesty, opaque custody, and repair ladders.')
append10 = '''

## Revision addendum — power cadence, transfer ledgers, ingress verbs, and reclaim truth

This pass found another current Resilio cluster worth treating as a first-class non-clone reason.
The strongest new seams are no longer only about storage roots, repair, or shell dependence.
They are now also about how a modern sync product explains **when a seat is actually participating**, **whether a history row proves a still-live handoff**, **which entry verb is creating which subject kind**, and **what a cleanup action truly removes**.

## AV. Power policy still changes liveness truth without one shared participation contract

Current official Resilio docs still say Android Auto Sleep can take Sync offline when there are no transfers in progress, can wake only every chosen interval, can use a separate interval while charging, and can make peers stop seeing the device as online because the core is actually off. The same docs still say Battery Saver can force Sync to stop below a chosen charge level.

That is a real capability. It is still not a good liveness contract. `Offline` becomes an overloaded status unless the product also tells operators whether the seat is absent by policy, by low battery, by runtime death, or by actual fault.

AnonSync should therefore keep another stronger rule:

- power policy is part of participation truth
- absence meaning must be published alongside cadence and battery floor
- a sleeping seat is not the same thing as a broken seat

## AW. File-send history rows still blur offer truth, ledger truth, and byte truth

Current official Resilio docs still say mobile `Shared links` surfaces show uploaded and downloaded file transfers, that downloads also appear in a `Downloads` folder, that file-send links are valid for three days and currently cannot be changed, that removing a file from the iOS `Downloads` folder removes it from the device while transfer history still shows it, and that removing an item from `Shared links` can remove it from Sync UI while leaving the file on the system. Current power-user preferences also still expose retention of expired file transfers in the UI by count or age.

That is useful history. It is still not a clean object model. A row in history is not the same thing as a live redeemable handoff, and neither is the same thing as payload bytes still resident on the seat.

AnonSync should therefore keep another stronger rule:

- every snapshot-like handoff must publish offer window, ledger retention, and local payload presence separately
- row removal must declare whether it is cosmetic, byte-destructive, or both
- expiry must not masquerade as deletion

## AX. Mobile ingress still overloads verbs that create different subject kinds

Current official Resilio docs still say one Android `+` menu exposes `Send file`, `Create folder`, `Add backup`, `Scan QR code`, and `Enter a key or link`. A current initiation page still says mobile can create a new folder or, on Android, add an already existing folder from the filesystem. Separate current Android sharing guidance still warns operators to use `Send via Sync` instead of `Add to Sync` when selecting files from a file manager. Current backup docs still say backup is a different workflow with storage retention on the destination even after source-side deletion and with read-only posture on the desktop side.

That is exactly the kind of verb cluster AnonSync should not clone. Different subject kinds should not be discovered after the operator is already halfway through a flow.

AnonSync should therefore keep another stronger rule:

- ingress verbs must declare subject kind up front
- live collaboration, adopted folders, bounded snapshots, capture sources, and incoming claims are separate acts
- file-manager entrypoints must still land in the same subject-kind review

## AY. Constrained-seat cleanup still depends on surface, posture, and local folklore

Current official Resilio docs still say iOS storage management splits `App data` and `User data`, can remove all file-share downloads at once from Storage, requires the `Downloads` folder for selective per-item removal, and only allows clearing local copies from sync shares when Selective Sync is enabled. Current Android share details still say `Clear` turns synced files into placeholders and is available only when Selective Sync is on, while `Disconnect` preserves the folder in the filesystem.

That is practical. It is still not a good reclaim contract. Local copy eviction, placeholder reversion, transfer-payload cleanup, and subject departure are different actions even when the UI puts them near one another.

AnonSync should therefore keep another stronger rule:

- reclaim must classify the local byte class being removed
- placeholder effect, path persistence, and re-materialization rights must be visible before apply
- cleanup surfaces must not stand in for scope truth

## The interface consequences for AnonSync in this revision

This pass adds four more direct interface consequences:

### 33) Power-managed seats need one participation-cadence surface

Because current docs still let Auto Sleep, charging cadence, and Battery Saver change whether peers see a seat at all, AnonSync now requires one power-policy surface that publishes wake cadence, visibility semantics, and freshness cost together.

### 34) Snapshot-like transfers need one ledger-versus-byte split

Because current docs still let expiry, retained transfer rows, and on-disk bytes drift apart across `Shared links`, `Downloads`, and power-user retention knobs, AnonSync now requires one transfer-ledger surface that keeps offer truth, history truth, and payload truth separate.

### 35) Entry verbs need one subject-kind taxonomy

Because current docs still place `Send file`, `Create folder`, `Add backup`, external file-manager verbs, and incoming claims close together despite creating different outcomes, AnonSync now requires one ingress taxonomy that declares subject kind and authority shape before bytes move.

### 36) Constrained-seat reclaim needs one scope matrix

Because current docs still split cleanup across storage menus, download views, share-detail actions, and selective-sync posture, AnonSync now requires one reclaim review that publishes local byte class, placeholder effect, membership effect, and recovery floor together.
'''
if '## Revision addendum — power cadence, transfer ledgers, ingress verbs, and reclaim truth' not in text10:
    text10 += append10
p10.write_text(text10)

# Update docs/20 with new doctrines
p20 = DOCS / '20-product-direction.md'
text20 = p20.read_text()
append20 = '''

### Doctrine 71 — power policy must publish participation cadence and absence meaning

A battery-managed seat is not merely `offline` when the product itself chose a wake cadence, charging override, or low-battery stop floor.
AnonSync should publish power policy as part of the public liveness contract.

### Doctrine 72 — transfer ledgers are not payload truth

A history row, a still-live offer window, and local bytes on disk are separate truths.
AnonSync should never let one visible row stand in for all three.

### Doctrine 73 — ingress verbs must declare subject kind and authority shape

`Create`, `adopt`, `send`, `attach capture source`, and `claim incoming` may all begin with user-selected files or folders, but they do not create the same kind of thing.
AnonSync should declare the resulting subject kind before bytes move.

### Doctrine 74 — local reclaim must publish byte class, placeholder effect, and recovery floor

Clearing receipt payloads, evicting materialized copies, reverting to placeholders, and disconnecting a subject are different actions.
AnonSync should publish a reclaim scope matrix instead of hiding those differences behind `clear` or `remove`.

## Revision addendum — four more doctrine choices

This revision adds four doctrine-level decisions that make the interface stricter without making the product broader:

### 1) Power-saving is part of participation truth

If the product chooses to sleep, wake periodically, or stop below a charge floor, that is no longer merely local device preference.
It is part of what other peers can honestly expect about freshness.

### 2) Snapshot history is still not the payload

A retained row can be useful evidence after expiry or local cleanup.
That evidence should survive without pretending the payload still exists.

### 3) Entry verbs teach the product model

Users learn the product from its first verbs.
If those verbs blur live subjects, adopted folders, bounded sends, and capture sources, the whole product model becomes harder to recover later.

### 4) Cleanup is a scoped residency decision

A serious sync product should let operators reclaim local space without guessing whether they just removed cache, names, bytes, or membership.
'''
if '### Doctrine 71 — power policy must publish participation cadence and absence meaning' not in text20:
    text20 += append20
p20.write_text(text20)

# Update roadmap
p50 = DOCS / '50-roadmap.md'
text50 = p50.read_text()
needle = '- explicit suspended-seat resume / chronology-confidence / offline-precedence quarantine surfaces for late-return local edits\n'
insert = needle + '- explicit power-policy / wake-cadence / absence-meaning surfaces for battery-managed or intermittently participating seats\n- explicit transfer-ledger / offer-window / payload-presence surfaces for one-time handoffs whose history can outlive bytes\n- explicit ingress-intent / subject-kind / authority-shape surfaces for create-adopt-send-capture-claim verbs\n- explicit local-reclaim / byte-class / recovery-floor surfaces for constrained-seat cleanup and placeholder-preserving eviction\n'
if '- explicit power-policy / wake-cadence / absence-meaning surfaces' not in text50:
    text50 = text50.replace(needle, insert)
exitneedle = '- operators can tell the current share posture on one seat apart from that seat\'s future-arrival defaults instead of treating both as one `mode`\n'
exitinsert = exitneedle + '- operators can tell whether a seat is absent by power policy, runtime death, or actual failure instead of inferring all three from `offline`\n- operators can tell whether a one-time transfer row proves a live offer, retained audit history, or surviving local payload bytes instead of guessing from one list view\n- operators can tell which ingress verb creates a live subject, adopted folder, bounded snapshot, capture source, or incoming claim before bytes move\n- operators can reclaim local space without guessing whether they removed receipt payloads, materialized copies, placeholders, or subject membership\n'
if 'operators can tell whether a seat is absent by power policy' not in text50:
    text50 = text50.replace(exitneedle, exitinsert)
p50.write_text(text50)

# Update sources
ps = DOCS / 'sources.md'
texts = ps.read_text()
texts = re.sub(r'^# Source notes through rev\d+', '# Source notes through rev0137', texts, count=1, flags=re.M)
append_sources = '''

## Revision addendum — power cadence, transfer rows, ingress verbs, and reclaim scope

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier seat, shell, and resume passes.
The new questions were:

> where do current official docs prove that **power-saving policy** still changes whether a seat is actually visible and participating, not just how much battery it uses?

> what current documentation most clearly proves that **file-send history rows** still diverge from live offer state and from bytes on disk?

> where do current official docs show that **mobile ingress verbs** still mix live collaboration, adopted folders, bounded sends, and capture-style backup under one adjacent menu family?

> how do current docs prove that **local cleanup and reclaim** still depend on surface and posture rather than one explicit scope matrix?

The most load-bearing source set for this pass was the maintained v3 change log together with docs on Android Auto Sleep/Battery Saver, mobile sharing on Android and iOS, storage management on iOS, Sync interface on Android, mobile initiation, Android backup, and power-user transfer retention preferences.

### Additional Resilio official sources emphasized in rev0137

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Sharing files (Android)  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- Sharing files (iOS)  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Initiate sharing on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/207370636-Initiate-sharing-on-mobile-platforms

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only
'''
if '## Revision addendum — power cadence, transfer rows, ingress verbs, and reclaim scope' not in texts:
    texts += append_sources
ps.write_text(texts)

