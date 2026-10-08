from pathlib import Path
import re

root = Path('/tmp/anonsync_rev72')

def read(p):
    return (root / p).read_text()

def write(p, s):
    (root / p).write_text(s)

def must_replace(text, old, new, path):
    if old not in text:
        raise SystemExit(f'missing in {path}: {old[:120]!r}')
    return text.replace(old, new, 1)

# --- new doc 86 ---
doc86 = """# Semantic fallback and optimization review spec

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
"""
write('docs/86-semantic-fallback-and-optimization-review-spec.md', doc86)

# README
p='README.md'
text=read(p)
text=must_replace(text,
"- Revision: `rev0072`\n- Timestamp: `2026.03.17.18.11` (America/New_York)\n- Codename: `annexproofdatabarrier`\n",
"- Revision: `rev0073`\n- Timestamp: `2026.03.17.18.17` (America/New_York)\n- Codename: `speedproofsemanticguard`\n",p)
text=must_replace(text,
"This revision continues directly from `rev0071` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on the share-root seam: current docs still put critical share identity, ignore policy, archive/history bytes, xattr carry-forward state, and in-flight residue directly in or beside the ordinary live tree through `.sync`, `.sync/Archive`, `.sync/StreamsList`, `.sync/Streams`, and `.!sync` conventions.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not make the user's ordinary file tree double as the hidden control plane for share identity, rollback state, portability stubs, and cleanup ritual.\n3. Adds a dedicated **share-annex and live-data separation spec** so the archive now says what a real operator surface must literally show before exposing managed bytes in-tree, migrating them out to an annex, or cleaning legacy residue safely.\n4. Extends the **interface and daemon/API contract** with explicit share-layout contracts, layout reviews, and layout receipts rather than treating hidden directories, temp residue, and history bytes as implementation trivia.\n5. Extends the **workbench/interface pattern language** so operators can inspect annex placement, metadata-carry posture, and cleanup fallout without needing `show hidden files` as the primary model.\n6. Adds additional **canonical interface flows** for migrating a legacy in-tree layout toward an external annex and for proving CLI/workbench parity on the same layout review.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep live data and managed sync state visibly separate.\n",
"This revision continues directly from `rev0072` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on the `performance knob` seam: current docs still allow speed, compatibility, and troubleshooting settings to quietly change semantics around change detection, rename continuity, diff behavior, conflict honesty, and verification timing.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not market a setting as `faster` or `more compatible` when it actually weakens meaning and operator trust guarantees.\n3. Adds a dedicated **semantic fallback and optimization review spec** so the archive now says what a real operator surface must literally show before accepting watcher loss, lazy proof, whole-file fallback, degraded network-share posture, or other meaning-changing accommodations.\n4. Extends the **interface and daemon/API contract** with explicit semantic-runtime contracts, optimization reviews, and optimization receipts rather than leaving these tradeoffs in power-user toggles and support notes.\n5. Extends the **workbench/interface pattern language** so operators can see which guarantees stay strong, which become weaker, and what target/runtime condition caused that change before apply.\n6. Adds additional **canonical interface flows** for accepting a degraded network-share profile honestly and for restoring stronger guarantees later without semantic drift between CLI and richer surfaces.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep semantic guarantees explicit whenever optimization or compatibility pressure appears.\n", p)
text=must_replace(text,
"- a first-class share-layout / annex / residue surface so operators can tell which bytes in a mounted tree are ordinary files, which are managed sync state, where rollback/temp/metadata-carry bytes live, and what any cleanup or migration actually changed\n",
"- a first-class share-layout / annex / residue surface so operators can tell which bytes in a mounted tree are ordinary files, which are managed sync state, where rollback/temp/metadata-carry bytes live, and what any cleanup or migration actually changed\n- a first-class semantic-runtime / optimization / fallback surface so operators can tell when a `performance` or `compatibility` change really weakens freshness, rename continuity, diff behavior, or verification guarantees\n", p)
text=must_replace(text,
"- access-change behavior that still depends on Standard-vs-Advanced folder class, owner folklore, disconnect semantics, local-share re-share ritual, or config-mode surface limits instead of one reviewed authority-mutation contract\n",
"- access-change behavior that still depends on Standard-vs-Advanced folder class, owner folklore, disconnect semantics, local-share re-share ritual, or config-mode surface limits instead of one reviewed authority-mutation contract\n- speed, compatibility, or troubleshooting knobs that silently trade away rename fidelity, notification freshness, diff efficiency, resumability, or conflict honesty without one reviewed semantic-fallback contract\n", p)
text=must_replace(text,
"- `docs/85-share-annex-and-live-data-separation-spec.md` — fixed share-layout review anatomy for live namespace guarantees, annex placement, residue/history posture, cleanup classes, and layout receipts\n",
"- `docs/85-share-annex-and-live-data-separation-spec.md` — fixed share-layout review anatomy for live namespace guarantees, annex placement, residue/history posture, cleanup classes, and layout receipts\n- `docs/86-semantic-fallback-and-optimization-review-spec.md` — fixed semantic-optimization review anatomy for requested profile, guarantees at risk, detection/verification posture, degraded-target findings, and optimization receipts\n", p)
text=must_replace(text,
"then `85-share-annex-and-live-data-separation-spec.md`, then `41-report-and-intervention-language.md`",
"then `85-share-annex-and-live-data-separation-spec.md`, then `86-semantic-fallback-and-optimization-review-spec.md`, then `41-report-and-intervention-language.md`", p)
write(p, text)

# status
p='docs/00-status.md'
text=read(p)
text=must_replace(text,
"This revision is an in-place continuation of `rev0071`, driven by the current request:\n\n- continue research and tighten the archive without letting it sprawl\n- evaluate Resilio Sync further with enough care that the non-clone case stays evidence-based\n- spend more time on interface specs rather than letting hidden share markers, history storage, xattr spillover, and temp residue hide inside the ordinary file tree\n- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them\n- keep turning support-lore seams into explicit product contracts\n- make sure the archive has a better reason not to clone current Resilio share layout behavior as though user data, control markers, rollback bytes, metadata-carry state, and cleanup ritual were one harmless directory\n- make sure live namespace, share annex, residue classes, migration, and cleanup stay visibly separate\n",
"This revision is an in-place continuation of `rev0072`, driven by the current request:\n\n- continue research and tighten the archive without letting it sprawl\n- evaluate Resilio Sync further with enough care that the non-clone case stays evidence-based\n- spend more time on interface specs rather than letting performance, compatibility, or troubleshooting knobs quietly change semantic guarantees\n- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them\n- keep turning support-lore seams into explicit product contracts\n- make sure the archive has a better reason not to clone current Resilio optimization behavior as though watcher loss, lazy proof, whole-file fallback, and degraded network-share posture were just harmless speed tuning\n- make sure semantic guarantees, degraded accommodations, and optimization receipts stay visibly separate\n", p)
text=must_replace(text,
"The archive now contains:\n\n- a deeper Resilio-derived warning that current share layout still couples user-visible content trees to critical service markers, ignore policy, rollback bytes, xattr spillover, and in-flight residue\n- a dedicated **share-annex and live-data separation spec** that says what a real operator surface must show before exposing managed bytes in-tree, migrating them to an annex, or cleaning them safely\n- stronger interface and daemon/API requirements so share-layout contracts, layout reviews, and layout receipts become explicit public objects rather than side effects of hidden dotfolders and cleanup folklore\n- stronger workbench and pattern-language rules so operators can see live-namespace guarantees, annex placement, metadata-carry posture, and cleanup fallout before apply\n- additional canonical flows for legacy in-tree layout migration and for cross-surface rendering of the same layout review without semantic drift\n- roadmap, ADR, status, open-question, and README updates so future revisions keep ordinary data and managed sync state explicit\n",
"The archive now contains:\n\n- a deeper Resilio-derived warning that current optimization and compatibility behavior still lets speed-oriented settings quietly rewrite semantic guarantees around detection, rename fidelity, diff behavior, verification, and conflict handling\n- a dedicated **semantic fallback and optimization review spec** that says what a real operator surface must show before accepting watcher loss, lazy proof, whole-file fallback, degraded network-share posture, or other meaning-changing accommodations\n- stronger interface and daemon/API requirements so semantic-runtime contracts, optimization reviews, and optimization receipts become explicit public objects rather than side effects of power-user toggles and support lore\n- stronger workbench and pattern-language rules so operators can see which guarantees are preserved, which weaken, and what target/runtime condition caused the downgrade before apply\n- additional canonical flows for accepting a degraded profile honestly and later restoring stronger guarantees without semantic drift\n- roadmap, ADR, status, open-question, and README updates so future revisions keep semantic guarantees explicit whenever optimization pressure appears\n", p)
text=must_replace(text,
"`rev0071` proved that names, aliases, and authority continuity needed one explicit reviewed contract rather than unlink/new-certificate ritual and convenience linking folklore.\n\n`rev0072` applies the same discipline one layer closer to the data tree itself:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define custody, projection, fidelity, rollback, and storage budgets, yet still leave one ordinary operator question loose: which bytes in a mounted tree are actually my files, which bytes are managed sync machinery, and what exactly am I cleaning, migrating, or preserving when those classes collide?\n\nThat changes the archive in six specific ways:\n\n- ordinary live namespace is now separated from managed share-control/state bytes as its own reviewed contract\n- rollback/history storage, temp-transfer residue, metadata-carry sidecars, and legacy marker state now render as explicit residue classes instead of hidden-file lore\n- annex placement is now a first-class product choice rather than an implementation accident\n- cleanup can no longer masquerade as harmless hidden-file deletion when preservation-sensitive evidence is still present\n- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely hidden dotfolders, but the lack of one honest reviewed boundary between user data and sync control state\n- future interface work now has a narrower quality bar for annex migration, residue cleanup, portable metadata handling, and legacy-layout import\n",
"`rev0072` proved that ordinary live namespace and managed sync state needed one explicit reviewed boundary rather than hidden-dotfolder and cleanup folklore.\n\n`rev0073` applies the same discipline one layer closer to runtime meaning itself:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define custody, fidelity, layout, contention, and transfer budgets, yet still leave one ordinary operator question loose: when a setting claims to make sync faster or more compatible, which guarantees stay strong, which become weaker, and what exactly am I accepting when detection, rename continuity, diff behavior, or verification changes?\n\nThat changes the archive in six specific ways:\n\n- semantic guarantees now render as their own reviewed runtime contract instead of hiding behind `advanced` settings\n- watcher loss, degraded storage, lazy proof, whole-file fallback, and conflict suppression can no longer masquerade as harmless speed tuning\n- optimization profiles are now first-class product choices rather than loose knob collections\n- workbench and CLI now have one explicit place to compare stronger versus weaker semantic posture\n- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely many knobs, but the lack of one honest reviewed contract for meaning-changing optimization\n- future interface work now has a narrower quality bar for acceleration, degraded-target support, and semantic restoration\n", p)
text=must_replace(text,
"- how much low-risk layout cleanup or annex migration may stay compressed before the product starts hiding meaningful data/control separation fallout behind harmless-looking hidden-file cleanup affordances\n",
"- how much low-risk layout cleanup or annex migration may stay compressed before the product starts hiding meaningful data/control separation fallout behind harmless-looking hidden-file cleanup affordances\n- how much low-risk semantic optimization may stay compressed before the product starts hiding meaningful guarantee weakening behind harmless-looking speed or compatibility affordances\n", p)
text=must_replace(text,
"## Files added in this revision\n\n- `docs/85-share-annex-and-live-data-separation-spec.md`\n",
"## Files added in this revision\n\n- `docs/86-semantic-fallback-and-optimization-review-spec.md`\n", p)
text=must_replace(text,
"- `docs/85-share-annex-and-live-data-separation-spec.md`\n",
"- `docs/85-share-annex-and-live-data-separation-spec.md`\n- `docs/86-semantic-fallback-and-optimization-review-spec.md`\n", p)
write(p, text)

# evaluation
p='docs/10-resilio-sync-evaluation.md'
text=read(p)
insert = """\n### 16ae) Speed, compatibility, and troubleshooting knobs still rewrite semantics too quietly\n\nResilio's current docs expose one more seam that is easy to underestimate because the settings look `advanced` rather than dangerous.\n`Power user preferences` says `lazy_indexing` means a remote placeholder rename will not work and the file will not be renamed accordingly on the source peer.\nThe same page says `prefer_net_over_disk_operations` re-downloads files instead of counting differences, `direct_torrent_enabled` can make small transfers faster but interrupted transfers start again from the beginning, `enable_file_system_notifications` can be disabled, `fix_conflicting_paths` can suppress conflict-file creation while leaving the share unsynced and `unpredictable`, and `prioritize_initial_indexing` delays syncing for huge pre-seeded folders until rescans finish.\n`What happens when file is renamed` says rename preservation depends on `Archive`; without it, bytes are re-synced again.\n`How soon does synchronization start?` and `Agent run out of system notify watchers` say immediate detection depends on filesystem notifications and that watcher loss forces periodic or manual rescan.\n`Sync and SMB file shares` says notifications may not work on older SMB setups and that mixed access outside SMB can damage files or roll changes back.\n\nThat is useful support knowledge.\nIt is not yet one public semantic-fallback contract.\n\nThe practical consequence is that five different truths keep collapsing together:\n\n- faster operation\n- weaker or slower change detection\n- rename continuity versus delete-plus-new-copy fallback\n- diff-preserving transfer versus whole-file resend or non-resumable fast path\n- honest conflict/verification posture versus suppressed or deferred proof\n\nIf the operator still has to remember that one `performance` setting affects rename fidelity, another affects resumability, another weakens detection freshness, and another can suppress conflict artifacts while the share quietly stops being trustworthy, the interface is not explicit enough.\n\nAnonSync should instead publish one public semantic-runtime model with:\n\n- one explicit contract describing current detection, rename continuity, delta-transfer, verification, and degraded-target posture\n- one reviewed optimization/fallback case for any non-trivial change marketed as speed or compatibility work\n- one explicit difference between semantic-neutral tuning and meaning-changing downgrade\n- explicit degraded-target findings so network-share, watcher, or mixed-access realities cannot masquerade as ordinary local semantics\n- durable optimization receipts proving which guarantees were preserved, weakened, or later restored\n\n### Requirement 67 — non-trivial optimization and compatibility changes must share one reviewed semantic-fallback contract\n\nIf the operator still has to combine power-user toggles, watcher warnings, SMB caveats, rename folklore, and troubleshooting notes to answer `what guarantee got weaker when I accepted this faster or more compatible mode?`, the product has not actually exposed its semantic-runtime contract.\n\nAnonSync should instead publish one public model with explicit semantic-runtime contracts, explicit optimization reviews, explicit guarantee deltas, explicit degraded-target scope, and durable receipts that preserve the difference between harmless tuning, reviewed semantic downgrade, and later restoration of stronger guarantees.\n\n"""
text=must_replace(text, "## Final judgment\n", insert + "## Final judgment\n", p)
write(p, text)

# interface spec
p='docs/30-interface-spec.md'
text=read(p)
block = """### Semantic runtime contract\n\nA durable contract describing what semantic guarantees the daemon currently makes for a subject under the current runtime/target posture.\nThis exists so operators do not have to guess whether an `optimization` really preserved freshness, rename continuity, diff behavior, verification, and conflict honesty.\n\nFields:\n\n- `semantic_runtime_contract_id`\n- `subject_ref`\n- `mount_ref` nullable\n- `runtime_seat_ref` nullable\n- `optimization_profile` (`balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`)\n- `detection_posture` (`notifications-primary`, `notifications-plus-rescan`, `rescan-biased`, `rescan-only`, `unknown`)\n- `rename_continuity_posture` (`preserved`, `preserved-with-history`, `uncertain`, `degraded-to-recopy`, `blocked`, `unknown`)\n- `delta_transfer_posture` (`diff-preferred`, `whole-file-fallback`, `whole-file-only`, `direct-nonresumable-fastpath`, `unknown`)\n- `verification_posture` (`eager`, `lazy`, `post-write-verify`, `database-only-for-some-fields`, `unknown`)\n- `conflict_honesty_posture` (`normal`, `suppressed-but-blocking`, `degraded`, `unknown`)\n- `target_degradation_class` (`none`, `network-share`, `watcher-exhausted`, `mixed-access-risk`, `path-semantics-risk`, `unknown`)\n- `guarantee_warnings[]`\n- `last_verified_at`\n- `provenance_ref` nullable\n\n### Semantic optimization review\n\nA reviewed case for changing runtime behavior that may weaken meaning while improving speed or compatibility.\nThis exists so lazy proof, rescan-only detection, whole-file fallback, or degraded-target acceptance do not collapse into reassuring speed language.\n\nFields:\n\n- `semantic_optimization_review_id`\n- `subject_ref`\n- `mount_ref` nullable\n- `current_semantic_runtime_contract_ref`\n- `requested_profile` (`balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`)\n- `requested_change_class` (`profile-switch`, `degraded-target-acceptance`, `one-off-mitigation`, `restore-stronger-guarantees`, `inspect-only`)\n- `guarantee_deltas[]`\n- `detection_findings[]`\n- `verification_findings[]`\n- `target_findings[]`\n- `action_options[]`\n- `semantic_runtime_report_ref`\n- `generated_at`\n- `expires_at` nullable\n\n### Semantic optimization receipt\n\nA durable record proving which guarantees were preserved, weakened, or later restored by a reviewed optimization change.\n\nFields:\n\n- `semantic_optimization_receipt_id`\n- `review_ref`\n- `subject_ref`\n- `profile_summary`\n- `guarantees_preserved[]`\n- `guarantees_weakened[]`\n- `restoration_requirements[]`\n- `actor_ref`\n- `created_at`\n- `provenance_ref` nullable\n\n"""
text=must_replace(text, "### Conflict item\n", block + "### Conflict item\n", p)
cli = """### `anonsync semantics`\n\nInspect and mutate semantic-impacting optimization posture without pretending that performance tuning and guarantee weakening are the same thing.\n\n```text\nanonsync semantics show workdocs\nanonsync semantics show workdocs --mount mnt_01J...\nanonsync semantics explain workdocs\nanonsync semantics prepare workdocs --profile degraded-network-share --reason smb-fallback --plan\nanonsync semantics prepare workdocs --profile full-verify --plan\nanonsync semantics review show sor_01J...\nanonsync semantics apply sor_01J...\nanonsync semantics receipt list --share workdocs\nanonsync semantics receipt show sorc_01J...\n```\n\nSemantics:\n\n- `show` should answer which guarantees are currently strong, weak, or uncertain for detection, rename continuity, diff behavior, verification, and conflict honesty\n- `prepare` should be required whenever a requested speed or compatibility change weakens one of those guarantees\n- degraded-target acceptance should say whether the weakness is share-scoped, mount-scoped, seat-scoped, or host-scoped\n- restoration back to a stronger profile should remain explicit rather than silently disappearing when conditions improve\n- receipts must prove whether the result was harmless tuning, reviewed downgrade, or restored stronger guarantees\n- future UI/TUI layers may render this differently, but they should not invent a different model\n\n"""
text=must_replace(text, "### `anonsync conflict`\n", cli + "### `anonsync conflict`\n", p)
write(p, text)

# daemon api spec
p='docs/31-daemon-api-spec.md'
text=read(p)
api_intro = """### Semantic runtime and optimization reviews\n\n```text\nGET  /v1/semantic-runtime/contracts\nGET  /v1/semantic-runtime/contracts/{semantic_runtime_contract_id}\nPOST /v1/semantic-runtime/reviews\nGET  /v1/semantic-runtime/reviews/{semantic_optimization_review_id}\nPOST /v1/semantic-runtime/reviews/{semantic_optimization_review_id}/apply\nGET  /v1/semantic-runtime/receipts\nGET  /v1/semantic-runtime/receipts/{semantic_optimization_receipt_id}\n```\n\nThese resources exist so clients can answer one ordinary operator question without advanced-toggle folklore:\n\n- which guarantees are currently strong, weak, or uncertain for detection, rename continuity, delta-transfer behavior, verification, and conflict honesty\n- whether a requested profile change is harmless tuning, reviewed degraded-target acceptance, or restoration of stronger guarantees\n- which target/runtime condition caused the weakness and whether it is share-, mount-, seat-, or host-scoped\n- which receipt proves later that the downgrade was accepted or that the stronger posture was restored\n\nCase creation should be preferred whenever a requested optimization weakens an operator-visible guarantee even if the request sounds like speed tuning.\n\n"""
text=must_replace(text, "## Event stream\n", api_intro + "## Event stream\n", p)
# add earlier endpoint listing after layout section
text=must_replace(text, "### Share layout and annex separation\n",
"### Share layout and annex separation\n", p)  # no-op for anchor check
text=must_replace(text,
"- which residue classes are safe to clean, blocked, or preservation-sensitive\n",
"- which residue classes are safe to clean, blocked, or preservation-sensitive\n\n### Semantic runtime and optimization\n\n```text\nGET  /v1/semantic-runtime/contracts\nGET  /v1/semantic-runtime/contracts/{semantic_runtime_contract_id}\nPOST /v1/semantic-runtime/reviews\nGET  /v1/semantic-runtime/reviews/{semantic_optimization_review_id}\nPOST /v1/semantic-runtime/reviews/{semantic_optimization_review_id}/apply\nGET  /v1/semantic-runtime/receipts\nGET  /v1/semantic-runtime/receipts/{semantic_optimization_receipt_id}\n```\n\nThese resources exist so clients can answer one ordinary operator question without advanced-toggle folklore:\n\n- which semantic guarantees are currently strong, weak, or uncertain for detection, rename continuity, delta-transfer behavior, verification, and conflict honesty\n- whether a requested profile is harmless tuning, reviewed degraded-target acceptance, or restoration of stronger guarantees\n- which target/runtime findings caused the weakness and whether they are share-, mount-, seat-, or host-scoped\n- which receipt proves that the operator knowingly accepted or later reversed the semantic downgrade\n", p)
# add review model section before topology-review resources
review_section = """## Semantic-runtime review resources\n\nThese resources keep speed and compatibility work honest.\nThey answer which guarantees are strong or weak right now, what target/runtime condition caused the weakness, and whether the safest next step is accept the degraded profile, restore a stronger profile, move to a stronger target, or block.\n\n```text\nGET    /v1/semantic-runtime/reviews\nPOST   /v1/semantic-runtime/reviews\nGET    /v1/semantic-runtime/reviews/{semantic_optimization_review_id}\nPOST   /v1/semantic-runtime/reviews/{semantic_optimization_review_id}/apply\nGET    /v1/semantic-runtime/receipts/{semantic_optimization_receipt_id}\n```\n\n`POST /v1/semantic-runtime/reviews` should accept one or more share/mount refs plus an explicit requested profile such as `balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, or `full-verify`.\nThe resulting case or referenced plan should always include:\n\n- requested optimization or degraded-target summary\n- guarantee-delta findings for detection, rename continuity, delta behavior, verification, and conflict honesty\n- target/runtime findings explaining why the weaker posture exists or would exist\n- admissible actions and any safer restoration path\n- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics\n\nThe `review_model` should at minimum group facts into:\n\n- `requested_optimization_or_degraded_target`\n- `semantic_guarantees_at_risk`\n- `detection_diff_and_verification_posture`\n- `target_and_runtime_findings`\n- `admissible_actions`\n- `receipt_promise`\n\nTransfer, fidelity, contention, and capacity-fit endpoints may still exist for narrower domain actions, but when the operator-visible outcome is accepting or reversing a meaning-changing optimization or compatibility downgrade, those endpoints should reference or emit the same semantic-runtime-review / semantic-optimization-receipt model.\n\n"""
text=must_replace(text, "## Topology-review resources\n", review_section + "## Topology-review resources\n", p)
write(p, text)

# flows
p='docs/32-interface-flows.md'
text=read(p)
flows = """\n## Flow 125 — accept a degraded network-share profile without pretending it is only a speed tweak\n\nProblem: an operator wants to keep syncing a large share onto a network-mounted path that lacks reliable notifications and has weaker locking semantics. They need to see whether the product is merely slower or whether rename continuity, detection freshness, and corruption risk are weaker too.\n\n```text\n$ anonsync semantics show media-archive\nSemantic runtime contract: src_01PA...\n\nProfile: balanced\nDetection posture: notifications-plus-rescan\nRename continuity: preserved-with-history\nDelta transfer: diff-preferred\nVerification: eager\nTarget degradation: none\n\n$ anonsync semantics prepare media-archive --profile degraded-network-share --reason smb-fallback --plan\nSemantic optimization review: sor_01PB...\n\nRequested optimization or degraded target:\n  profile: degraded-network-share\n  reason: SMB target lacks trustworthy notifications\n\nSemantic guarantees at risk:\n  detection freshness -> weakens to rescan-biased\n  rename continuity -> uncertain under target interruption\n  conflict honesty -> unchanged\n  verification -> unchanged\n\nTarget and runtime findings:\n  target class: network-share\n  notification posture: unreliable\n  mixed-access risk: present\n  safer alternative: move share to local tier and re-export via ordinary file service\n\nAdmissible actions:\n  - accept degraded profile with receipt\n  - keep balanced profile and block this target\n  - move to stronger local target\n\nReceipt promise:\n  sorc_01PC... will prove accepted degraded-network-share posture\n\n$ anonsync semantics apply sor_01PB...\nApplied.\nReceipt: sorc_01PC...\n```\n\nWhat this proves:\n\n- degraded storage is rendered as weaker semantics, not just slower sync\n- the operator sees which guarantees changed and why\n- the receipt preserves that this was a reviewed downgrade, not an invisible speed tweak\n\n## Flow 126 — restore stronger guarantees after watcher repair without semantic drift\n\nProblem: a large pre-seeded subject temporarily used lazy proof and rescan-biased detection during intake. Later the operator repairs watcher limits and wants to restore stronger rename and verification guarantees without guessing what still needs to catch up.\n\n```text\n$ anonsync semantics show workdocs\nSemantic runtime contract: src_01PD...\n\nProfile: large-preseeded-intake\nDetection posture: rescan-biased\nRename continuity: uncertain\nDelta transfer: diff-preferred\nVerification: lazy\nTarget degradation: watcher-exhausted\n\n$ anonsync semantics prepare workdocs --profile full-verify --plan\nSemantic optimization review: sor_01PE...\n\nRequested optimization or degraded target:\n  profile: full-verify\n  restore stronger guarantees: yes\n\nSemantic guarantees at risk:\n  none weaken\n  detection freshness -> strengthens to notifications-plus-rescan\n  rename continuity -> strengthens to preserved-with-history\n  verification -> strengthens to eager\n\nTarget and runtime findings:\n  watcher exhaustion: repaired\n  catch-up requirement: one verification pass still pending\n\nAdmissible actions:\n  - restore stronger profile now\n  - defer until quiet window\n\nReceipt promise:\n  sorc_01PF... will prove stronger guarantees restored after catch-up\n```\n\nWhat this proves:\n\n- stronger semantics are restored through the same reviewed model that accepted the earlier downgrade\n- the product keeps catch-up obligations visible instead of silently flipping a switch back\n- CLI and richer surfaces can render the same guarantee delta without drift\n"""
text += flows
write(p, text)

# workbench
p='docs/38-operator-workbench-interface-spec.md'
text=read(p)
surface = """## Semantic guarantees and optimization surface\n\nThe workbench should expose one dedicated surface whenever a requested speed, compatibility, or troubleshooting change would also weaken an operator-visible guarantee.\nThis page is not advanced-performance garnish.\nIt is where the product proves that `faster`, `good enough here`, and `semantically weaker` are not the same conclusion.\n\nThe page should show at least:\n\n- current optimization profile and runtime scope\n- current detection, rename, delta-transfer, verification, and conflict-honesty posture\n- target/runtime findings explaining any current weakness\n- guarantee deltas for the requested profile\n- restoration requirements and recent optimization receipts\n\nIts primary actions should be:\n\n- inspect current semantic runtime contract\n- prepare reviewed degraded-target acceptance\n- prepare a stronger-verify / stronger-freshness restoration\n- inspect why a proposed optimization is blocked\n- inspect recent optimization receipts\n\nNo action on this page should collapse into `Advanced`, `Performance`, or `Compatibility` toggles without a report, plan, or receipt when semantics would weaken.\n\n"""
text=must_replace(text, "## Identity and naming continuity page\n", surface + "## Identity and naming continuity page\n", p)
write(p, text)

# pattern language
p='docs/39-interface-pattern-language.md'
text=read(p)
pattern = """## Pattern 22m — semantic downgrade must not hide inside speed language\n\nEvery non-trivial optimization review should render, in this order:\n\n1. requested optimization or degraded target\n2. semantic guarantees at risk\n3. detection/diff/verification posture\n4. target and runtime findings\n5. admissible actions\n6. receipt promise\n\nThis matters because a product can define good transfer, fidelity, and capacity objects on paper and still regress in practice if one client says `Performance mode` while another reveals that rename continuity, freshness, or verification actually weakened.\nHeadless and GUI surfaces need one semantic-fallback grammar, not one speed toggle and one troubleshooting article.\n\n"""
text=must_replace(text, "## Pattern 23 — dangerous verbs should inherit the reviewed intent label\n", pattern + "## Pattern 23 — dangerous verbs should inherit the reviewed intent label\n", p)
write(p, text)

# ADR
p='docs/40-architecture-decisions.md'
text=read(p)
text += """\n\n## ADR-086 — Performance and compatibility changes need one reviewed semantic-fallback contract, not power-user-toggle folklore\n\n**Decision:** Non-trivial optimization or degraded-target work should compile to one reviewed semantic-runtime model rather than depending on advanced settings, SMB caveats, watcher warnings, or rename folklore as the operator contract.\n\n**Why:** Current Resilio docs still let lazy indexing, whole-file fallback, direct fast paths, notification loss, and degraded network-share posture quietly alter rename continuity, detection freshness, resumability, verification timing, or conflict honesty. AnonSync should keep those guarantee changes explicit.\n\n**Consequences:**\n\n- semantic runtime state gains a stable contract and receipt model\n- workbench and CLI both need explicit guarantee-delta sections before meaning-changing optimization can apply\n- degraded-target acceptance can no longer masquerade as harmless speed tuning\n- future performance work must distinguish semantic-neutral tuning from reviewed semantic downgrade\n"""
write(p, text)

# roadmap
p='docs/50-roadmap.md'
text=read(p)
text=must_replace(text,
"- subject-alias-record, identity-continuity-review, and identity-label-receipt object model\n",
"- subject-alias-record, identity-continuity-review, and identity-label-receipt object model\n- semantic-runtime-contract, semantic-optimization-review, and semantic-optimization-receipt object model\n", p)
text=must_replace(text,
"- operators can tell who or what can currently control the daemon, through which endpoint, and what receipt proved any exposure or revocation change\n",
"- operators can tell who or what can currently control the daemon, through which endpoint, and what receipt proved any exposure or revocation change\n- operators can tell when a requested optimization or compatibility change would actually weaken freshness, rename continuity, diff behavior, or verification guarantees\n", p)
text=must_replace(text,
"- explicit mutation-gate / short-lived mutation-grant / elevation-receipt surfaces that keep inspect sessions separate from dangerous apply authority\n",
"- explicit mutation-gate / short-lived mutation-grant / elevation-receipt surfaces that keep inspect sessions separate from dangerous apply authority\n- explicit semantic-runtime / optimization / fallback surfaces that keep meaning-changing acceleration or degraded-target acceptance from hiding behind `performance` language\n", p)
write(p, text)

# open questions
p='docs/64-critical-open-questions.md'
text=read(p)
text += """\n\n## 54) How much low-risk semantic optimization can stay compressed before guarantee honesty becomes either noisy or too magical?\n\nThe archive is now clearer that detection freshness, rename continuity, diff behavior, verification posture, and degraded-target accommodations should use first-class semantic-runtime reviews and receipts, but one policy seam remains open:\n\n- when should an obviously semantic-neutral tuning change stay inline versus always opening the full optimization sheet\n- whether some temporary degraded-target acceptances may stay one-step while others always force full reviewed downgrade\n- how much automatic restoration to a stronger profile is safe before the product starts hiding meaningful catch-up or re-verification work\n- when repeated semantic downgrades should escalate into broader fidelity, capacity-fit, or support review because the subject is no longer in an ordinary operating posture\n\nThis matters because weak defaults recreate advanced-toggle, watcher-warning, and SMB-folklore ergonomics, while overly strict defaults could make harmless tuning feel ceremonial instead of trustworthy.\n"""
write(p, text)

# sources add missing refs if absent
p='docs/sources.md'
text=read(p)
if 'What happens when file is renamed' not in text:
    text = must_replace(text,
    "- File download priority  \n  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority\n",
    "- File download priority  \n  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority\n\n- What happens when file is renamed  \n  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed\n\n- How soon does synchronization start?  \n  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start\n", p)
write(p, text)
