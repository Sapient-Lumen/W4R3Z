# Semantic fallback and optimization review spec

The archive already has transport/runtime policy, filesystem fidelity, contention, capacity fit, channel parity, and share-layout separation.
This document answers a narrower seam those abstractions still leave too loose:

> what must a real operator surface literally show when a so-called performance, compatibility, or troubleshooting change would also weaken freshness, rename fidelity, diff behavior, conflict handling, or verification truth, so AnonSync does not let semantic downgrade hide behind a reassuring speed knob?

This is the semantic-runtime companion to `47-settlement-barrier-and-readiness-spec.md`, the fidelity companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, the transfer companion to `53-transfer-policy-and-throughput-budget-spec.md`, the contention companion to `76-writer-contention-and-quiescence-review-spec.md`, and the capacity-fit companion to `77-capacity-fit-and-scale-admission-review-spec.md`.

## Why this needs its own spec

Resilio's current docs make the seam unusually concrete.
`Power user preferences` says `lazy_indexing` means a remote placeholder rename will not work and the file will not be renamed accordingly on the source peer.
The same page says `prefer_net_over_disk_operations` re-downloads a file instead of counting differences, `direct_torrent_enabled` can reduce transfer time but causes interrupted transfers to restart from the beginning, `enable_file_system_notifications` can be disabled entirely, `fix_conflicting_paths` can suppress conflict-file creation while leaving the share unsynced and `unpredictable`, and `prioritize_initial_indexing` delays syncing on pre-seeded folders until peers finish rescanning.
`What happens when file is renamed` says rename preservation depends on `Archive`; otherwise bytes are re-synced again.
`How soon does synchronization start?` says notifications are fastest but do not reliably exist on some storage, including SMB2 and similar mounted shares.
`Agent run out of system notify watchers` says watcher exhaustion means changes are only discovered during manual or periodic rescan.
`Sync and SMB file shares` says SMB notifications may not work before SMB 3.0 and that mixed access outside SMB can damage files or roll changes back.

That is useful support knowledge.
It is not yet one honest semantic-fallback contract.

The practical consequence is that one seemingly simple operator gesture — `make it faster`, `make it work on this storage`, `quiet this warning`, `use this compatibility mode` — can really change five different truths at once:

- how quickly local change detection happens
- whether rename/move is preserved as continuity or degrades into delete-plus-new-copy behavior
- whether bandwidth is saved by diff logic or spent on full re-download
- whether integrity is verified eagerly, lazily, or only after later demand
- whether path/collision trouble is surfaced honestly or merely suppressed until the share stops being trustworthy

If the operator still has to infer those tradeoffs from advanced toggles, SMB caveats, watcher warnings, or rename folklore, the product is not explicit enough.

## Core rule

AnonSync should treat semantic-impacting optimization and degraded-target accommodations as first-class public state.
A so-called optimization may be:

- semantic-neutral and directly admissible
- performance-positive but review-required because one guarantee weakens
- degraded-target accommodation for a known path or seat
- inspect-only because current evidence is insufficient
- blocked

The product may not advertise a change as mere speed tuning when it actually weakens freshness, rename continuity, diff behavior, conflict honesty, or verification posture.

## Which actions are in scope

This spec is about any action where a performance or compatibility choice can silently alter meaning.
That includes at least:

- changing detection from immediate notifications to rescan-only or rescan-biased modes
- enabling or accepting lazy or deferred indexing that weakens rename continuity or proof timing
- preferring re-download over local diff/counting to save CPU or disk work
- enabling direct transfer modes that trade resumability for speed
- weakening path/collision handling or suppressing conflict artifacts
- accepting degraded storage such as SMB/NFS/FUSE-like targets where notifications, locking, or single-writer assumptions weaken
- changing verification posture for downloaded or derived bytes
- applying target-specific optimization profiles for very large, pre-seeded, or degraded subjects

Low-risk inspection can stay lighter.
Any change that weakens an operator-visible guarantee cannot.

## Vocabulary

### Semantic runtime contract

A durable contract describing what the daemon currently promises about detection, rename continuity, delta behavior, verification, and degraded-target handling for a subject on a particular host/runtime path.

### Detection posture

How the daemon expects to learn about relevant changes.
Examples: `notifications-primary`, `notifications-plus-rescan`, `rescan-biased`, `rescan-only`, `unknown`.

### Optimization profile

A named bundle of runtime choices intended to improve performance or compatibility.
Examples: `balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`.

### Semantic fallback

A reviewed downgrade where the product keeps operating but one guarantee weakens.
Examples: rename preservation becomes uncertain, diff falls back to whole-file transfer, or immediate detection falls back to periodic scan.

### Optimization receipt

A durable record proving which guarantees were preserved, weakened, or restored when a reviewed optimization or degraded-target accommodation was applied.

## Fixed review order

Every non-trivial semantic optimization review should render the same sections in the same order:

1. **Requested optimization or degraded-target accommodation**
2. **Semantic guarantees at risk**
3. **Detection, diff, and verification posture**
4. **Target and runtime findings**
5. **Admissible actions**
6. **Receipt promise**

### 1) Requested optimization or degraded-target accommodation

This section should show:

- subject, mount, and current runtime path/seat
- current optimization profile and requested profile
- whether the action is profile switch, degraded-target acceptance, one-off mitigation, or inspect-only comparison
- whether the current posture is fresh and verified, degraded but accepted, or degraded without reviewed acceptance

The operator must be able to answer: **am I just making this faster, or am I accepting weaker semantics so it keeps working here?**

### 2) Semantic guarantees at risk

This section should show:

- rename continuity posture
- delta-transfer posture
- detection freshness posture
- conflict/path honesty posture
- verification/integrity posture
- which guarantees remain unchanged, weaken, or become uncertain after apply

The operator must be able to answer: **which user-visible truths stay the same, and which become weaker if I accept this?**

### 3) Detection, diff, and verification posture

This section should show:

- notification support and current watcher health
- current fallback to periodic scan or manual scan
- whether the subject uses eager proof, lazy proof, post-write verify, or other bounded verification posture
- whether transfer prefers diff, whole-file resend, or direct non-resumable fast path
- whether rename preservation depends on supporting state such as local history/rollback availability

The operator must be able to answer: **how will this host actually notice change, prove byte identity, and preserve continuity under this profile?**

### 4) Target and runtime findings

This section should show:

- storage tier and target kind (`local`, `network-share`, `removable`, `degraded`, `unknown`)
- whether locking, atomic-rename, or notification assumptions are weakened here
- whether mixed-access or out-of-band writers create rollback/corruption risk
- whether the degraded posture is path-scoped, seat-scoped, host-scoped, or subject-scoped

The operator must be able to answer: **is this weakness really about the share itself, or about where and how it is currently mounted and run?**

### 5) Admissible actions

This section should show:

- whether the honest next step is keep balanced profile, accept reviewed degradation, switch to safer slower profile, move the subject to a stronger target, or block
- which shortcuts are forbidden because they would market a semantic downgrade as harmless acceleration
- whether the product can offer a safely compressed path because the requested change is semantically neutral
- what follow-up remains if the operator accepts degradation only temporarily

The operator must be able to answer: **what can I safely do right now without lying to myself about what got weaker?**

### 6) Receipt promise

This section should show:

- which optimization receipt will exist after apply, defer, or refusal
- what it will later prove about guarantees preserved, guarantees weakened, and the scope of the accepted degraded posture
- whether later restoration to a stronger profile still depends on a target move, watcher repair, or verification catch-up
- where later audit survives if the action resumes from another channel

The operator must be able to answer: **what later evidence will prove this really was only a performance change — or prove that I knowingly accepted weaker semantics?**

## Public objects

### Semantic runtime contract

Fields:

- `semantic_runtime_contract_id`
- `subject_ref`
- `mount_ref` nullable
- `runtime_seat_ref` nullable
- `optimization_profile` (`balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`)
- `detection_posture` (`notifications-primary`, `notifications-plus-rescan`, `rescan-biased`, `rescan-only`, `unknown`)
- `rename_continuity_posture` (`preserved`, `preserved-with-history`, `uncertain`, `degraded-to-recopy`, `blocked`, `unknown`)
- `delta_transfer_posture` (`diff-preferred`, `whole-file-fallback`, `whole-file-only`, `direct-nonresumable-fastpath`, `unknown`)
- `verification_posture` (`eager`, `lazy`, `post-write-verify`, `database-only-for-some-fields`, `unknown`)
- `conflict_honesty_posture` (`normal`, `suppressed-but-blocking`, `degraded`, `unknown`)
- `target_degradation_class` (`none`, `network-share`, `watcher-exhausted`, `mixed-access-risk`, `path-semantics-risk`, `unknown`)
- `guarantee_warnings[]`
- `last_verified_at`
- `provenance_ref` nullable

### Semantic optimization review

Fields:

- `semantic_optimization_review_id`
- `subject_ref`
- `mount_ref` nullable
- `current_semantic_runtime_contract_ref`
- `requested_profile` (`balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`)
- `requested_change_class` (`profile-switch`, `degraded-target-acceptance`, `one-off-mitigation`, `restore-stronger-guarantees`, `inspect-only`)
- `guarantee_deltas[]`
- `detection_findings[]`
- `verification_findings[]`
- `target_findings[]`
- `action_options[]`
- `semantic_runtime_report_ref`
- `generated_at`
- `expires_at` nullable

### Semantic optimization receipt

Fields:

- `semantic_optimization_receipt_id`
- `review_ref`
- `subject_ref`
- `profile_summary`
- `guarantees_preserved[]`
- `guarantees_weakened[]`
- `restoration_requirements[]`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable

## What the surface must never imply

The semantic-optimization surface must never imply that these are the same thing:

- faster detection versus trustworthy detection
- rescan-only fallback versus healthy notifications
- whole-file resend versus diff-preserving transfer
- direct fast path versus resumable transfer
- lazy proof versus already-verified content truth
- hidden conflict suppression versus resolved conflict
- tolerated degraded storage versus ordinary local semantics

If the product compresses those differences, it has recreated the advanced-toggle folklore it is trying to replace.

## CLI shape

Examples:

```text
anonsync semantics show workdocs
anonsync semantics show workdocs --mount mnt_01J...
anonsync semantics explain workdocs
anonsync semantics prepare workdocs --profile degraded-network-share --reason smb-fallback --plan
anonsync semantics prepare workdocs --profile full-verify --plan
anonsync semantics review show sor_01J...
anonsync semantics apply sor_01J...
anonsync semantics receipt list --share workdocs
anonsync receipts show sorc_01J...
```

The point is not the exact spelling.
The point is that performance work and semantic-fallback work remain visibly different verbs from ordinary transfer tuning.

## Relation to the rest of the archive

This spec does not replace transfer policy, filesystem fidelity, contention, or capacity-fit work.
It narrows one recurring failure mode:

- transfer policy explains route and budget
- fidelity explains what a target can honestly represent
- capacity fit explains whether a host should carry the subject at all
- contention explains how writers and locks behave under pressure
- semantic-optimization review explains when a supposedly helpful runtime change would also weaken meaning

That difference should stay visible everywhere.
