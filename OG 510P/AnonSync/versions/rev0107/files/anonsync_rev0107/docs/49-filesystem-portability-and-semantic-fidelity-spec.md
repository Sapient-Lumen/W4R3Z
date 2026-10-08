# Filesystem portability and semantic fidelity spec

## Problem this spec resolves

The archive already had important pieces of this territory:

- filesystem profiles
- filesystem compatibility reports
- Linux-first support tiers
- path comparison and mount binding flows
- activity/readiness language that can already describe degraded notifications and periodic rescan

What it still lacked was one dedicated answer to the operator question:

> after this share is adopted here, what semantics are actually promised on this path over time, what gets rewritten/dropped/virtualized, what drift would weaken that promise, and what durable receipt proves I accepted those tradeoffs?

A further Resilio pass makes that gap much sharper.
Current official docs still spread filesystem truth across several separate support surfaces:

- SMB shares may work, but notifications can fall back to full rescan unless both sides support SMB 3.0, and mixed direct access outside Samba can damage files or roll changes back
- Windows does not support soft links, hard links, or symbolic links and can produce `.Conflict` artifacts; Unix syncs symbolic links but not the target folders behind them
- xattrs sync only through a whitelist in hidden `.sync/StreamsList`, and unsupported xattrs may spill into `.sync/Streams` service storage so they can later propagate onward
- the hidden `.sync` folder is critical, and deleting or corrupting it suspends syncing and leads to remove/re-add style repair guidance
- troubleshooting guidance still asks operators to remember filename/path limits, UTF-8 requirements, permission failures, merge-tree failures, and notification loss as separate caveats

Those are not minor documentation quirks.
They are evidence that portability and semantic fidelity are still not one public operator contract.

AnonSync should not clone that shape.

## Core rule

Filesystem portability is a **durable fidelity contract**, not a one-time preflight warning.

That means:

1. adoption should choose an explicit portability policy, not just emit a warning and proceed
2. each mount should publish a fidelity contract describing the semantics it promises on the target path
3. accepted rewrites, downgrades, virtualization, and omissions should emit a fidelity receipt
4. later runtime drift should surface as an explicit drift case instead of mysterious “sync got weird” behavior
5. local-first, network-share, and degraded-notification postures should stay visible as support-tier choices, not troubleshooting folklore

If the operator still has to combine one compare report, one SMB article, one symlink article, one hidden control-file rule, and one troubleshooting page to answer “what semantics survive on this mount?”, the public model is not explicit enough.

## Vocabulary

### Portability policy

A durable policy describing how pathname, metadata, special-file, and notification differences should be handled for a mount or adoption workflow.

### Fidelity contract

A durable mount-scoped object describing the semantics the daemon currently promises on the selected path, given the active portability policy and observed filesystem profile.

### Fidelity receipt

A durable explanation record proving which portability/fidelity tradeoffs were accepted or applied during adoption, relocation, repair, or later policy change.

### Fidelity drift case

A public warning object describing how the previously verified fidelity contract no longer matches current reality.
Examples include notification loss, permissions loss, filesystem-type change, or a path that is now backed by a network share with weaker guarantees.

## Non-negotiable design rules

1. **No hidden control-file API.**  
   Hidden files may still exist as implementation detail, but operators should never need to edit hidden allowlists, service folders, or marker files to understand ordinary portability decisions.

2. **No preflight-only honesty.**  
   Compatibility warnings at bind time are not enough. The product must keep publishing the active contract afterward.

3. **Downgrade must be chosen, not inferred.**  
   Rewrites, dropped metadata, blocked link classes, placeholder substitutions, or special-file omissions should be explicit policy outcomes.

4. **Network-share posture must stay visible.**  
   If a mount relies on a network filesystem or a target with degraded notifications, the system should say so directly and tie that fact into activity/readiness truth.

5. **Runtime drift must be surfaced.**  
   If permissions narrow, notifications disappear, the underlying filesystem changes, or support tier weakens, the system should emit a public drift case.

6. **Receipts should prove accepted tradeoffs.**  
   Later audit should be able to answer not merely that adoption succeeded, but what fidelity contract was accepted at the time.

## Object-model additions

### Portability policy

Fields:

- `portability_policy_id`
- `name`
- `scope` (`share-default`, `mount-default`, `mount-specific`, `system`)
- `path_policy` (`strict-native`, `portable-rewrite`, `portable-block`, `review-required`)
- `case_policy` (`native`, `portable-fold-safe`, `block-collision`)
- `normalization_policy` (`native`, `rewrite-nfc`, `rewrite-nfd`, `portable-utf8`, `block-mismatch`)
- `symlink_policy` (`preserve-link`, `omit`, `block`)
- `junction_policy` (`preserve`, `flatten`, `block`)
- `xattr_policy` (`preserve-full`, `portable-subset`, `copy-aside-when-unsupported`, `drop-with-receipt`)
- `acl_policy` (`preserve-full`, `portable-subset`, `drop-with-receipt`, `block`)
- `special_file_policy` (`block`, `preserve-subset`, `omit-with-receipt`)
- `notification_requirement` (`continuous-required`, `continuous-preferred`, `periodic-ok`)
- `network_share_posture` (`forbid`, `warn`, `allow-reviewed`)
- `created_at`
- `provenance_ref` nullable

### Fidelity contract

Fields:

- `fidelity_contract_id`
- `mount_ref`
- `share_ref`
- `fs_profile_ref`
- `fs_compat_report_ref`
- `portability_policy_ref`
- `support_tier` (`linux-first`, `best-effort`, `warning-tier`, `blocked`)
- `path_semantics` (`native`, `rewritten`, `mixed`, `blocked`)
- `metadata_semantics` (`full`, `portable-subset`, `best-effort`, `none`)
- `notification_semantics` (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- `network_path_state` (`local-native`, `network-reviewed`, `network-unreviewed`, `unknown`)
- `active_downgrades[]`
- `blocked_classes[]`
- `virtualized_classes[]`
- `last_verified_at`
- `verification_state` (`fresh`, `stale`, `drifted`, `blocked`)
- `provenance_ref` nullable

### Fidelity receipt

Fields:

- `fidelity_receipt_id`
- `mount_ref`
- `share_ref`
- `action_kind` (`adopt`, `relocate`, `repair`, `policy-change`, `drift-accept`)
- `portability_policy_ref`
- `fidelity_contract_ref`
- `accepted_downgrades[]`
- `blocked_classes[]`
- `network_share_acknowledged` boolean
- `notification_posture_acknowledged` boolean
- `decision_trace_ref` nullable
- `completed_at`
- `provenance_ref` nullable

### Fidelity drift case

Fields:

- `fidelity_drift_case_id`
- `fidelity_contract_ref`
- `mount_ref`
- `detected_change` (`permissions-loss`, `notification-loss`, `filesystem-type-change`, `network-share-detected`, `xattr-capability-drop`, `clock-precision-drop`, `path-encoding-risk`, `service-marker-risk`)
- `severity` (`watch`, `guarded`, `high`, `blocked`)
- `effect_summary`
- `affected_semantics[]`
- `recommended_actions[]`
- `generated_at`
- `provenance_ref` nullable

## Report implications

The existing filesystem-compatibility report family should grow enough to support both:

- **preview** — what would happen if I adopted or relocated here?
- **contract** — what semantics are currently promised here?
- **drift** — what changed since the contract was verified?

Operators should not have to learn one vocabulary for preflight and another for later fidelity loss.

## CLI implications

A minimum public surface should include:

```text
anonsync fs policy list
anonsync fs policy show <policy>
anonsync fs contract prepare --share <share> --path <path> --policy <policy>
anonsync fs contract show <mount|contract_id>
anonsync fs contract verify <mount|contract_id>
anonsync fs drift list
anonsync fs drift show <drift_case_id>
anonsync fs receipt list --mount <mount>
anonsync fs receipt show <fidelity_receipt_id>
```

Semantics:

- `fs contract prepare` should not mutate a mount; it should synthesize the contract the operator would be accepting
- `fs contract show` should answer the durable question “what semantics are promised here right now?”
- `fs contract verify` should re-check underlying reality and emit a drift case if the contract no longer holds
- `fs receipt show` should answer what downgrade and support-tier tradeoffs were knowingly accepted

## Daemon API implications

A minimum public surface should include:

```text
GET  /v1/fs/policies
POST /v1/fs/policies
GET  /v1/fs/policies/{portability_policy_id}
POST /v1/fs/contracts:prepare
GET  /v1/fs/contracts/{fidelity_contract_id}
POST /v1/fs/contracts/{fidelity_contract_id}:verify
GET  /v1/fs/drift-cases
GET  /v1/fs/drift-cases/{fidelity_drift_case_id}
GET  /v1/fs/receipts
GET  /v1/fs/receipts/{fidelity_receipt_id}
```

The API should make it possible for any client — CLI, TUI, local web workbench, or audit automation — to answer portability and drift questions without scraping warnings or hidden files.

## Workbench implications

The share detail page should expose one combined **Filesystem fidelity** card.

It should answer:

- what target path and filesystem profile are active
- what portability policy is in effect
- whether pathname semantics are native, rewritten, mixed, or blocked
- whether metadata fidelity is full, portable-subset, best-effort, or none
- whether notifications are continuous or degraded to periodic rescan
- whether the mount is local-native or network-reviewed
- whether any drift case currently weakens the contract
- which receipt last recorded an accepted downgrade or policy change

The point is not to add another warning badge.
The point is to keep “what semantics survive here?” in one place instead of distributing it across support lore.

## Canonical operator questions this spec should make easy

- “If I bind this share here, what semantics will be rewritten, dropped, or blocked?”
- “Is this mount still operating under the same fidelity contract it had at adoption time?”
- “Did notifications degrade to periodic rescan, and does that matter for my readiness policy?”
- “Am I relying on a network share that the product only treats as warning-tier?”
- “What proof do I have that I knowingly accepted portable-subset metadata or path rewrites?”

## Why this is a real non-clone requirement

Resilio's current docs are candid and useful.
But they still leave filesystem semantics spread across:

- SMB caveats and notification downgrade guidance
- platform-specific symlink rules
- hidden `.sync`, `StreamsList`, and `Streams` service files
- troubleshooting pages for UTF-8, path length, permission, and merge-tree failures
- remove/re-add repair rituals after service-marker corruption

That is workable support knowledge.
It is not the right public contract for AnonSync.

AnonSync should instead publish a durable portability/fidelity contract from day one.
