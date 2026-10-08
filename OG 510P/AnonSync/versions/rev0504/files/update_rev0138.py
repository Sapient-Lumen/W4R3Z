from pathlib import Path
import re

ROOT = Path('/mnt/data/anonsync_rev0138/anonsync_rev0138')
DOCS = ROOT / 'docs'

rev = 'rev0138'
timestamp = '2026.03.19.22.33'
codename = 'servicebranchconfigclosurebeacon'

# --- new interface specs ---
(DOCS / '213-service-promotion-migrate-clean-and-principal-continuity-interface-spec.md').write_text('''# Service promotion, migrate/clean branching, and principal-continuity interface spec

## Purpose

The archive already had bring-up review, execution-seat reachability, and runtime-seat switch language.
What it still lacked was one explicit interface contract for a narrower but very real transition:

> turning an already-lived local node into a background service seat without letting the operator confuse **background the same node** with **start a different local world and reconnect it by hand**.

Current official Resilio docs make this seam clearer than a generic `run as a service` feature.
They still say Windows service install can either **migrate settings and uninstall the existing Sync client** or perform a **clean installation**.
They also still say the service can run as the current user, Local System, or Local Service; and when the runtime principal changes far enough, the operator can land in a different storage folder and an empty-looking service world instead of the old one.

That is not just install trivia.
It is a continuity contract.

AnonSync should therefore treat service promotion as a reviewed branch point with a first-class continuity receipt.

## Core decision

A service-promotion action must declare one of four intents before apply:

- **promote same node**
- **promote same node with reviewed path/runtime losses**
- **start clean background seat**
- **inspect only; do not mutate continuity**

The product must never compress these into one checkbox like `run in background`.
If the new seat will not open the same state root, the action is not a promotion of the same node.
It is a branch or clean-seat start.

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- installer-time `migrate settings` versus `clean installation` decides continuity, but reads like a convenience choice
- service principal choice can decide whether the old shares appear at all
- a successful service start can still mean `different storage root, different identity-view, no old inventory`
- the next honest action may be `re-share / reconnect`, yet the surface can still look like `backgrounding`

So AnonSync should keep one harder rule:

> a service seat is not a launch mode; it is a continuity-bearing execution world that must be reviewed as such.

## Fixed review order

Every service-promotion surface should render the same sections in the same order:

1. **Requested service posture**
2. **State-root continuity**
3. **Inventory continuity**
4. **Principal and capability delta**
5. **Next-step branch**
6. **Promotion receipt**

### 1) Requested service posture

This section should show:

- source seat (`interactive current user`, `daemon current user`, `named service user`, `system seat`, etc.)
- target seat
- whether the operator asked for `promote same node`, `clean background seat`, or `inspect`
- whether migration evidence is already present

The operator must be able to answer: **am I backgrounding the existing node, or creating another one?**

### 2) State-root continuity

This section should show:

- current state root
- proposed state root
- whether identity material, policy state, and subject inventory are opening from the same root
- whether continuity is proven, ambiguous, or broken

The operator must be able to answer: **does this service seat open the same durable node?**

### 3) Inventory continuity

This section should show:

- currently known subjects on the source seat
- which will remain visible on the target seat
- whether the target seat starts empty because it is clean, not because shares were lost
- whether any subject can be reattached later only by reviewed reconnect

The operator must be able to answer: **will the new service seat show the same lived inventory, a clean branch, or an ambiguous partial world?**

### 4) Principal and capability delta

This section should show:

- runtime principal change
- path classes widened or narrowed by that principal
- control-surface change (loopback-only, local workbench, other)
- whether service startup changes who can see or mutate the node locally

The operator must be able to answer: **what changed because of the service principal, not merely because the app kept running after logout?**

### 5) Next-step branch

This section should show one explicit next branch:

- `apply as same-node promotion`
- `apply as same-node promotion with follow-up rebind review`
- `start clean service branch`
- `stop and inspect only`

If the honest next step is reconnect / re-share / reattach, the product must say that before apply.

### 6) Promotion receipt

This section should show:

- source seat
- target seat
- continuity class
- state-root proof
- inventory continuity summary
- follow-up obligations

The operator must be able to answer: **what evidence later proves whether this was a promotion, a branch, or a clean start?**

## Public objects

### `service_promotion_review`

Fields:

- `service_promotion_review_id`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `requested_intent`
- `continuity_class` (`same-node`, `same-node-with-followup`, `clean-branch`, `inspect-only`, `blocked`)
- `state_root_findings[]`
- `inventory_findings[]`
- `principal_delta_findings[]`
- `recommended_branch`
- `generated_at`

### `service_promotion_receipt`

Fields:

- `service_promotion_receipt_id`
- `review_ref`
- `outcome`
- `continuity_class`
- `state_root_ref_before`
- `state_root_ref_after`
- `inventory_summary`
- `followup_review_refs[]`
- `created_at`

## Main surface

A compact row should read like one of these, not just `service enabled`:

- `same-node service promotion · continuity proven`
- `same-node service promotion · 2 targets require follow-up rebind`
- `clean service branch · no prior inventory attached`
- `service seat opened different state root · inspect before reconnect`

## Event language

Use phrases such as:

- `service promotion preserved the current node`
- `service seat opened a different state root`
- `inventory continuity not proven; reconnect review required`
- `clean background branch created by operator choice`

Avoid phrases such as:

- `service started successfully`
- `existing shares not found`
- `run in background enabled`

Those lines are too operational and not truthful enough.

## CLI shape

```text
anonsync seat promote review --to service-current-user
anonsync seat promote review --to service-system
anonsync seat promote apply <review>
anonsync seat promote receipt <receipt>
```

The CLI must make `same-node` versus `clean-branch` explicit before the daemon changes seats.

## Edge cases

### Installer can migrate settings

That is evidence, not proof.
The product may preselect `same-node promotion`, but it must still show state-root and inventory continuity evidence.

### Clean service start on purpose

That is legitimate.
The product must still call it a clean branch rather than a failed migration.

### Principal widened path access but opened a different state root

That is not a continuity win.
The product must show both truths at once: **more path reach, different node**.

## Non-clone reason

Current official Resilio docs still treat service install choice, runtime principal, storage-root shift, and reconnect follow-up as several separate pieces of knowledge.
AnonSync should instead give the operator one reviewed promotion page and one durable receipt proving whether the same node actually survived the move into background service life.
''')

(DOCS / '214-remote-volume-path-class-and-notification-confidence-interface-spec.md').write_text('''# Remote-volume path class, notification confidence, and rescan-honesty interface spec

## Purpose

The archive already had change-detection coverage, degraded-target semantics, and execution-seat reachability language.
What it still lacked was one tight contract for a narrower but common operational lie:

> a path that is still reachable enough to sync some bytes, but no longer reachable with the same **change-detection confidence**, **permission posture**, or **settlement freshness**.

Current official Resilio docs make this seam unusually concrete.
They still say a Windows service cannot use mapped drive letters created by interactive logon, that the UNC-style workaround loses system file-update notifications and falls back to learning changes only during rescan or after restart, and that watcher exhaustion on Linux similarly downgrades truth to manual or periodic rescan until the limit is raised.

That is not a mere transport detail.
It is a local-path contract.

## Core decision

AnonSync should classify every bound or candidate path by **path class** and **detection grade**.
A path is not merely `reachable` or `not reachable`.
It must carry at least:

- path class
- permission grade
- detection grade
- freshness cost
- settlement risk

## Path classes

At minimum the product should distinguish:

- `native-local`
- `interactive-mapped`
- `service-visible-remote`
- `namespace-local`
- `external-removable`
- `degraded-visible`
- `unreachable-from-current-seat`

## Detection grades

At minimum the product should distinguish:

- `native-watch`
- `degraded-watch`
- `rescan-periodic`
- `rescan-manual-only`
- `unknown`

The product must never let an operator infer those grades from support folklore.

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- mapped-drive letters can disappear for the service seat even though the human believes the folder `still exists`
- UNC-like fallback can keep bytes flowing while silently dropping immediate change notifications
- watcher exhaustion can degrade freshness without changing the subject into an obvious hard failure
- restart or touch ritual becomes the practical meaning of `sync` if the surface does not publish the downgrade clearly

So AnonSync should keep one harder rule:

> any path admitted under degraded detection must carry that downgrade as a first-class truth on every relevant subject surface.

## Fixed review order

Every path-bind or path-recheck surface should render the same sections in the same order:

1. **Path class now**
2. **Permission and visibility**
3. **Detection confidence**
4. **Freshness and settlement cost**
5. **Allowed intents**
6. **Detection-grade receipt**

### 1) Path class now

This section should show:

- literal path or normalized target label
- current path class
- seat-relative visibility
- whether the class changed because of runtime-seat switch, mount loss, or operator retargeting

The operator must be able to answer: **what kind of storage is this path from the current seat’s point of view?**

### 2) Permission and visibility

This section should show:

- read permission
n- write permission
- create/rename/delete confidence
- whether the path is discoverable, manually typable, or fully browsable only from another seat

The operator must be able to answer: **can this seat really operate this target, or only partly reach it?**

### 3) Detection confidence

This section should show:

- detection grade
- watcher substrate or scan substrate
- what events are learned immediately versus only on scan/restart
- any known system budget problem causing the downgrade

The operator must be able to answer: **how does the daemon learn about local changes here?**

### 4) Freshness and settlement cost

This section should show:

- expected freshness window
- whether writer contention or restore flows become less trustworthy under this grade
- whether `ready` can still be asserted strongly
- whether a degraded grade increases risk of surprise archive/revert/recheck behavior

The operator must be able to answer: **what semantic cost comes with keeping this path under the current grade?**

### 5) Allowed intents

This section should show:

- continue with warning
- narrow to inspect-only
- require periodic-rescan posture explicitly
- block for high-fidelity subjects
- move to healthier storage class

The product must not treat all subject kinds equally here.
A degraded path that may be acceptable for loose backup may be unacceptable for tight collaborative work.

### 6) Detection-grade receipt

This section should show:

- path class
- detection grade
- why the grade is what it is
- which intents were allowed or blocked under that grade
- follow-up obligations (raise watchers, move path, switch seat, etc.)

## Public objects

### `bound_path_fact`

Fields:

- `bound_path_fact_id`
- `subject_ref`
- `execution_seat_ref`
- `path_label`
- `path_class`
- `permission_grade`
- `detection_grade`
- `freshness_window_budget`
- `observed_limitations[]`
- `verified_at`

### `path_detection_receipt`

Fields:

- `path_detection_receipt_id`
- `bound_path_fact_ref`
- `review_ref` nullable
- `allowed_intents[]`
- `blocked_intents[]`
- `followup_actions[]`
- `created_at`

## Main surface

A compact status row should read like:

- `native-local · native watch`
- `service-visible remote · periodic rescan only`
- `interactive-mapped · unreachable from current seat`
- `native-local · watch budget exhausted; periodic rescan until fixed`

Not just `available`.

## Event language

Use phrases such as:

- `path detection downgraded from native watch to periodic rescan`
- `mapped path unavailable to current service seat`
- `remote-volume workaround keeps bytes flowing but not immediate local-change notices`
- `watcher budget exhausted; freshness now scan-bound`

Avoid phrases such as:

- `folder okay`
- `share connected`
- `path accessible`

Those are not truthful enough.

## CLI shape

```text
anonsync path inspect <subject>
anonsync path review <subject> --seat <seat>
anonsync path detection receipt <subject>
```

## Edge cases

### Path is writable but not watchable

The product must show that as degraded, not healthy.
Bytes alone are not the whole contract.

### Watchers are exhausted temporarily

A reviewed temporary downgrade is allowed, but the surface must publish the freshness cost and the exit condition.

### Same path class, different intent

A low-priority archival subject may accept a weaker grade than a latency-sensitive shared workspace.
That policy difference should be explicit.

## Non-clone reason

Current official Resilio docs still let meaningful local-path truth hide behind mapped-drive lore, UNC fallback, watcher tuning, and restart/rescan ritual.
AnonSync should instead publish one path-class and detection-grade contract so the operator can tell exactly what kind of local truth they still have before pretending a degraded seat is healthy.
''')

(DOCS / '215-declared-config-subject-set-and-interactive-control-boundary-interface-spec.md').write_text('''# Declared-config subject set and interactive-control boundary interface spec

## Purpose

The archive already had settings-layer collapse, baseline rollout, and channel-parity language.
What it still lacked was one dedicated interface contract for a sharper seam exposed by current official Resilio docs:

> when a declarative config file names the subjects and policies up front, what exactly is the relationship between that declared world and the operator’s live interactive control surface?

Current official Resilio docs still say configuration mode is useful for applying the same settings across many machines.
They also still say config mode can set up only **Standard** folders, that non-default `storage_path` creates settings there, and that if shared folders are specified in the config file the **WebUI is disabled** and those configured folders override what was previously added from WebUI.

That is not just `headless is different`.
It is a branch in authority and mutability.

## Core decision

AnonSync should treat declarative control as a **declared branch**, not as an invisible override of the live interactive world.
A declaration may be authoritative, advisory, or import-only — but it must never silently replace the interactive subject set.

At minimum the product should distinguish:

- `declared-authoritative`
- `declared-advisory`
- `declared-import-preview`
- `interactive-live`
- `mixed-with-reviewed-overrides`

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- config-declared subjects can override earlier interactive subjects
- interactive control may disappear once config-declared shares exist
- declarative mode is limited to a narrower capability family than the full product surface
- moving `storage_path` can quietly create another settings world while still feeling like `the same app with a config`

So AnonSync should keep one harder rule:

> a declarative branch may constrain or drive the live node, but the operator must always be able to inspect the declared-vs-live diff before that branch becomes effective.

## Fixed review order

Every declaration import or activation surface should render the same sections in the same order:

1. **Declaration origin**
2. **Declared-vs-live subject graph**
3. **Capability envelope delta**
4. **Mutability boundary**
5. **Activation choice**
6. **Declaration receipt**

### 1) Declaration origin

This section should show:

- declaration source (file, bundle, generated baseline, imported service profile)
- declared root / declared state scope
- whether the declaration is fresh, already active, or only previewed
- who authored or supplied it if known

The operator must be able to answer: **where did this declared world come from?**

### 2) Declared-vs-live subject graph

This section should show:

- subjects currently live
- subjects declared
- overlaps
- declared additions
- declared removals
- declared replacements or policy narrowing

The operator must be able to answer: **what would this declaration add, remove, replace, or shadow?**

### 3) Capability envelope delta

This section should show:

- capabilities expressible in the declaration
- capabilities already used by the live set that the declaration cannot represent directly
- whether any live subject would be degraded, frozen, or converted by activation

The operator must be able to answer: **does the declaration speak the full language of the live node, or only a narrower subset?**

### 4) Mutability boundary

This section should show:

- what remains interactively editable after activation
- what becomes declaration-owned
- whether the declaration is strict, mergeable, or advisory
- what later local changes would become drift instead of ordinary edits

The operator must be able to answer: **what can I still change interactively after this branch becomes active?**

### 5) Activation choice

This section should offer only explicit choices such as:

- `activate as authoritative baseline`
- `activate as advisory baseline`
- `import for diff only`
- `activate on empty state only`
- `block because live capabilities would be degraded silently`

The product must not use a vague `run with config` control as the only explanation.

### 6) Declaration receipt

This section should show:

- declaration identity
- live graph before activation
- live graph after activation or refusal
- mutability class
- drift policy
- capability losses accepted or blocked

## Public objects

### `declaration_branch`

Fields:

- `declaration_branch_id`
- `source_ref`
- `declared_subjects[]`
- `declared_policy_refs[]`
- `declared_state_root_ref`
- `mutability_class`
- `capability_envelope`
- `created_at`

### `declaration_activation_review`

Fields:

- `declaration_activation_review_id`
- `declaration_branch_ref`
- `live_graph_ref`
- `graph_delta_summary`
- `capability_delta_summary`
- `mutability_boundary_summary`
- `recommended_activation_mode`
- `generated_at`

## Main surface

A compact banner should read like:

- `declared branch preview · 3 adds · 1 removal · 2 live-only capabilities blocked`
- `authoritative declaration active · local drift reviewed, not silently overwritten`
- `import refused · declaration cannot represent current live capabilities honestly`

## Event language

Use phrases such as:

- `declaration would shadow 4 live subjects`
- `declaration is narrower than current live capability envelope`
- `interactive editing remains allowed for local overrides only`
- `declaration imported for diff, not activated`

Avoid phrases such as:

- `Web UI disabled`
- `config applied`
- `settings overridden`

Those describe mechanics, not trustworthy meaning.

## CLI shape

```text
anonsync declaration preview ./node.baseline.json
anonsync declaration review ./node.baseline.json
anonsync declaration activate <review> --mode advisory
anonsync declaration receipt <id>
```

## Edge cases

### Declaration points at another state root

That is a branch boundary, not a simple config apply.
It must reopen continuity review.

### Live node is empty

The product may streamline activation, but still must state whether the declaration becomes authoritative or merely seeds live state.

### Declaration cannot express live subject class

Activation should block unless the operator explicitly accepts a reviewed degradation or conversion path.

## Non-clone reason

Current official Resilio docs still make declarative control feel like a useful rollout trick while letting it disable interactive control, override prior interactive inventory, and narrow the representable capability set.
AnonSync should instead keep declarations and live control in one inspectable relationship so operators never have to guess whether a config file quietly replaced the world they thought they were operating.
''')

(DOCS / '216-uninstall-offboard-peer-tombstone-and-hidden-residue-attestation-interface-spec.md').write_text('''# Uninstall, offboard, peer tombstone, and hidden-residue attestation interface spec

## Purpose

The archive already had exit review, replacement, recall, and residue-clearance language.
What it still lacked was one tight interface contract for the final and often most misleading transition:

> when the operator believes they are `removing the app`, what exact peer, subject, hidden-state, and leftover-byte truths are they actually closing — and which ones remain?

Current official Resilio docs still make that seam sharp.
They still say that before uninstall the operator should unlink identity and remove remaining Standard shares, otherwise the uninstalled instance will simply continue showing as `offline` on other peers.
They still say Windows service uninstalls require manual deletion of the service storage folder, and macOS/Linux guidance still points at manual cleanup of storage roots and hidden `.sync` folders with Archive inside.
They also still say uninstallation removes the program but does **not** delete folders that were previously shared, while iOS/Windows Phone removals do remove synced files from the device because of platform architecture.

That is not one action.
It is four or five different closures happening at once.

## Core decision

AnonSync should never offer a bare `uninstall` path for a node that has live or remembered relationships.
Instead it should require a reviewed **closure plan** that separates:

- peer-visible tombstone intent
- control-plane residue cleanup
- per-subject hidden residue cleanup
- ordinary shared-folder survival
- platform-forced local-copy loss

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- removing the app can leave the node visible elsewhere as merely offline
- removing the app can leave control-plane storage behind
- removing the app can leave hidden per-share Archive bytes behind
- removing the app can leave ordinary shared folders intact on some platforms but remove synced files on others

So AnonSync should keep one harder rule:

> program removal is not the same as peer departure, subject residue cleanup, or byte destruction, and the UI must say which of those did or did not happen.

## Fixed review order

Every closure/uninstall surface should render the same sections in the same order:

1. **Peer-visible departure**
2. **Control-plane residue**
3. **Per-subject hidden residue**
4. **Ordinary folder fate**
5. **Platform-forced local-copy fate**
6. **Closure receipt**

### 1) Peer-visible departure

This section should show:

- whether the node will publish a deliberate tombstone, a quiet retirement, or no peer-visible exit at all
- whether linked-constellation relationships are being revoked, retired, or simply abandoned
- whether other peers would otherwise keep seeing this node as offline

The operator must be able to answer: **what will others think happened to this node?**

### 2) Control-plane residue

This section should show:

- state roots that remain after program removal unless explicitly cleared
- credentials, logs, databases, and settings that would remain or be deleted
- service-profile storage that needs separate removal if applicable

The operator must be able to answer: **what daemon/control traces will still exist on this machine?**

### 3) Per-subject hidden residue

This section should show:

- subjects that have hidden annex/service bytes on disk
- Archive/history/temp or other managed residue that remains unless explicitly cleared
- subjects whose residue matters for future restore or audit

The operator must be able to answer: **what hidden share-local material survives even if the program goes away?**

### 4) Ordinary folder fate

This section should show:

- ordinary folders that remain untouched
- folders that are simply no longer managed
- whether any folder contents are about to be deleted by reviewed choice rather than as an uninstall side effect

The operator must be able to answer: **what ordinary user data remains browseable after program removal?**

### 5) Platform-forced local-copy fate

This section should show:

- platforms or seats where removing the app also removes locally synced copies
- whether that is platform architecture, not product promise
- what export or recovery step is needed before closure if local copies matter

The operator must be able to answer: **what bytes vanish because of the platform, not because I explicitly asked for destruction?**

### 6) Closure receipt

This section should show:

- departure class
- tombstone publication summary
- control-plane residue summary
- hidden-residue summary
- folder survival summary
- platform-forced deletion summary

## Public objects

### `node_closure_plan`

Fields:

- `node_closure_plan_id`
- `node_ref`
- `peer_departure_mode`
- `control_plane_cleanup_mode`
- `hidden_residue_cleanup_mode`
- `ordinary_folder_mode`
- `platform_forced_copy_loss[]`
- `generated_at`

### `node_closure_receipt`

Fields:

- `node_closure_receipt_id`
- `plan_ref`
- `peer_tombstone_summary`
- `control_plane_cleanup_summary`
- `hidden_residue_summary`
- `folder_survival_summary`
- `platform_forced_copy_loss_summary`
- `created_at`

## Main surface

A compact summary should read like:

- `retire node with peer tombstone · keep ordinary folders · keep hidden archives`
- `remove app only · no peer tombstone · other peers will continue to remember this node as absent`
- `full closure · clear control plane and hidden residues after export`
- `platform warning · local copies on this seat will be removed with the app`

## Event language

Use phrases such as:

- `node retired with explicit tombstone`
- `program removed; ordinary folders left intact`
- `hidden subject residue preserved for later audit/restore`
- `control-plane storage remained because cleanup was not requested`
- `local copies removed due to seat platform architecture`

Avoid phrases such as:

- `Sync uninstalled`
- `device removed`
- `all data cleared`

Those are too ambiguous.

## CLI shape

```text
anonsync node closure review
anonsync node closure apply <review>
anonsync node closure receipt <id>
```

## Edge cases

### Operator wants only program removal

That is allowed, but the surface must say that peers may still remember the node and that hidden residues may remain.

### Operator wants destruction but some residues are needed for audit/restore

The product should force an export or explicit waiver before destruction.

### Platform removes local copies with app removal

The product should warn early and offer export, not teach this later as support lore.

## Non-clone reason

Current official Resilio docs still spread uninstall meaning across unlink instructions, share-removal instructions, service-storage cleanup, hidden `.sync/Archive` cleanup, and platform-specific copy-loss notes.
AnonSync should instead compile those into one reviewed closure plan and one receipt so the operator can prove exactly what ended, what remained, and why.
''')

# --- update status ---
status = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0137`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based, current, and specific not only about power cadence, transfer-ledger truth, ingress taxonomy, and constrained-seat reclaim, but now also about **service-promotion continuity**, **remote-volume / rescan honesty**, **declared config versus live control**, and **uninstall/offboard closure truth**
- spend more time on **interface specs**, especially where current sync products still ask the operator to infer continuity, local detection quality, declaration authority, or final departure semantics from installer choices, service-account shifts, config files, and uninstall notes
- preserve the shell/workspace, projection-parity, arrival-placement, path-comparison, quiescence, clock, repair, capture-ingest, and re-entry decisions already made unless fresh evidence actually breaks them
- make a better explicit case for why AnonSync should not inherit Resilio's service-install ambiguity, remote-path notification ambiguity, config-override ambiguity, or uninstall/offboard ambiguity

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {rev}
- Timestamp: {timestamp} America/New_York
- Codename: {codename}

- a further-tightened **Resilio evaluation** that now treats service promotion, runtime principal, mapped/remote path detection downgrade, declaration-vs-live control, and uninstall/offboard closure as additional non-clone reasons
- a new **service promotion / migrate-clean / principal continuity** interface spec so backgrounding a lived node becomes a reviewed branch instead of installer folklore
- a new **remote-volume path class / notification confidence / rescan honesty** interface spec so writable-but-degraded paths stop masquerading as healthy local targets
- a new **declared config subject set / interactive control boundary** interface spec so declarative rollout becomes an inspectable branch instead of a silent override of live interactive state
- a new **uninstall / peer tombstone / hidden residue attestation** interface spec so program removal, peer departure, hidden residue cleanup, and platform-forced local-copy loss stop collapsing into one verb
- updated top-level docs so the archive now makes firmer choices about service-world continuity, path-class detection grade, declaration authority, and closure receipts

## The main shift

`{rev}` closes the next seam:

> it is not enough to have strong seat-switch, repair, reclaim, and access language if the operator still has to reconstruct **whether background service startup preserved the same node**, **whether a reachable path still has strong change-detection truth**, **whether a declaration is advisory or authoritative**, and **whether uninstall actually published departure or only removed a binary** from installer branches, service troubleshooting, config-file notes, and hidden cleanup instructions.

That changes the archive in eight specific ways:

- service promotion now publishes same-node promotion, same-node-with-followup, clean branch, and inspect-only outcomes separately
- runtime principal and storage-root changes now compile into one promotion receipt instead of looking like a successful start with missing inventory
- bound paths now publish path class and detection grade, not merely `reachable`
- degraded remote/service-visible paths now carry explicit freshness cost instead of relying on rescan folklore
- declaration import now renders declared-vs-live graph diff before activation
- declarative baselines can now be authoritative, advisory, import-preview, or blocked for capability loss
- uninstall/offboard now distinguishes peer tombstone, control-plane residue, hidden share-local residue, ordinary folder survival, and platform-forced local-copy loss
- closure receipts can now prove exactly what ended and what remained, instead of leaving `offline` ghosts or hidden archives to be rediscovered later

## Files added in this revision

- `docs/213-service-promotion-migrate-clean-and-principal-continuity-interface-spec.md`
- `docs/214-remote-volume-path-class-and-notification-confidence-interface-spec.md`
- `docs/215-declared-config-subject-set-and-interactive-control-boundary-interface-spec.md`
- `docs/216-uninstall-offboard-peer-tombstone-and-hidden-residue-attestation-interface-spec.md`
- `update_rev0138.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/20-product-direction.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## The current stance in one paragraph

Resilio remains worth studying because current official docs still show a maintained Sync v3 line, practical service and config workflows, selective materialization, and extensive operational guidance.
But those same docs still show service promotion meaning hidden across migrate-versus-clean install choices and service principals, remote path truth hidden across mapped-drive and rescan workarounds, declarative rollout hidden across config-file side effects and live-surface disappearance, and uninstall truth hidden across unlink notes, service-storage cleanup, and hidden `.sync` residue.
That is enough reason for AnonSync to prefer one service-promotion receipt, one path-class/detection-grade contract, one declaration branch review, and one closure receipt instead of cloning Resilio's support-lore-driven contract.
'''
(DOCS / '00-status.md').write_text(status)

# --- update README ---
readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0137` and does twelve specific things:

1. Pushes the **Resilio Sync** evaluation further with current official evidence about service-promotion continuity, runtime-principal/storage-world drift, mapped/remote path notification downgrade, declaration-vs-live control, and uninstall/offboard closure truth.
2. Sharpens the non-clone reason again: the remaining problem is not missing features but too much operator-meaningful truth spread across installer branches, service-account changes, config-file side effects, and uninstall notes.
3. Adds a new **service promotion / migrate-clean / principal continuity** interface spec so promoting a lived node into a background service becomes a reviewed branch instead of install folklore.
4. Adds a new **remote-volume path class / notification confidence / rescan honesty** interface spec so a path that is writable-but-degraded cannot masquerade as a healthy native local target.
5. Adds a new **declared config subject set / interactive control boundary** interface spec so declarative rollout becomes an inspectable branch instead of a silent override of live interactive state.
6. Adds a new **uninstall / peer tombstone / hidden residue attestation** interface spec so program removal, peer departure, hidden residue cleanup, and platform-forced local-copy loss become visibly different closure facts.
7. Refreshes the **Resilio evaluation** so the comparison now also covers service installer `migrate settings` versus `clean installation`, current-user versus Local System / Local Service service seats, mapped-drive invisibility to services, UNC fallback with lost notifications, config-declared share sets disabling WebUI and overriding prior interactive inventory, and uninstall guidance that leaves peers offline-visible and hidden `.sync/Archive` bytes behind unless explicitly cleaned.
8. Refreshes the **product direction** so service-world continuity, detection-grade honesty, declaration branching, and closure receipts become doctrine rather than support lore.
9. Refreshes the **roadmap** so the next tranche now explicitly includes service-promotion reviews, path-class detection receipts, declared-baseline activation diffs, and closure/offboard receipts.
10. Refreshes the **source notes** so the official evidence set now explicitly includes `Running Sync as a service on Windows`, `Sync Service Troubleshooting on Windows`, `Running Sync in configuration mode`, `Sync Storage folder`, `How to uninstall Sync?`, and the Linux watcher-budget warning page.
11. Keeps the archive tight by extending existing runtime-seat, bring-up, target-custody, settings-layer, change-detection, exit, and residue grammar instead of inventing unrelated subsystems.
12. Preserves the earlier storage-truth, identity-salvage, host-custody, compatibility-gate, power-cadence, transfer-ledger, shell-equivalence, resume-quarantine, work-ledger, repair-ladder, metadata, route, restore, naming, and topology decisions while giving them stronger service-world, path-class, declaration-branch, and closure companions.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The reason is sharper again and still evidence-based.
Current official docs still show a maintained Sync v3 line through `3.1.2.1076` in late 2025, practical service and configuration workflows, selective materialization, and a large body of operational guidance.
That is why Resilio remains worth studying rather than dismissing.

But the better non-clone reason is now this:

> Resilio still solves many real operator problems while leaving too much meaning about **whether service startup preserved the same node**, **whether a reachable path still carries strong change-detection truth**, **whether a declaration is advisory or authoritative**, and **whether uninstall actually published departure or only removed a program** distributed across installer branches, service-account changes, config-file overrides, storage-root caveats, and uninstall notes where AnonSync wants one promotion receipt, one path-class/detection-grade contract, one declaration branch review, and one closure receipt.

That stronger conclusion is what this revision tries to preserve.

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/213-service-promotion-migrate-clean-and-principal-continuity-interface-spec.md`
4. `docs/214-remote-volume-path-class-and-notification-confidence-interface-spec.md`
5. `docs/215-declared-config-subject-set-and-interactive-control-boundary-interface-spec.md`
6. `docs/216-uninstall-offboard-peer-tombstone-and-hidden-residue-attestation-interface-spec.md`
7. `docs/209-battery-saver-auto-sleep-and-participation-honesty-interface-spec.md`
8. `docs/210-file-send-ledger-expiry-retention-and-byte-truth-interface-spec.md`
9. `docs/211-ingress-verb-taxonomy-and-mobile-source-capture-interface-spec.md`
10. `docs/212-constrained-seat-storage-reclaim-bulk-clear-and-local-copy-truth-interface-spec.md`
11. `docs/205-constrained-seat-path-consent-and-removable-storage-capability-interface-spec.md`
12. `docs/206-external-editor-roundtrip-import-copy-and-replacement-review-interface-spec.md`
13. `docs/207-shell-extension-loss-and-in-app-capability-equivalence-interface-spec.md`
14. `docs/208-suspended-seat-resume-quarantine-and-offline-precedence-interface-spec.md`
15. `docs/201-storage-budget-scope-staging-headroom-and-actual-drive-truth-interface-spec.md`
16. `docs/202-identity-root-health-folder-list-salvage-and-relink-ladder-interface-spec.md`
17. `docs/203-host-ownership-claim-dual-instance-collision-and-safe-branching-interface-spec.md`
18. `docs/204-release-cohort-compatibility-control-plane-migration-and-link-gate-interface-spec.md`
19. `docs/197-hidden-work-phase-ledger-and-honest-progress-interface-spec.md`
20. `docs/198-preseed-reuse-dedup-proof-and-local-block-witness-interface-spec.md`
21. `docs/199-integrity-rebuild-reindex-and-subject-repair-ladder-interface-spec.md`
22. `docs/200-disconnect-remove-and-placeholder-eviction-contract-interface-spec.md`
23. `docs/156-projection-parity-and-surface-capability-contract-interface-spec.md`
24. `docs/149-interface-shell-navigation-and-persistent-context-spec.md`
25. `docs/38-operator-workbench-interface-spec.md`
26. `docs/39-interface-pattern-language.md`
27. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and interface doctrine
- `docs/213-service-promotion-migrate-clean-and-principal-continuity-interface-spec.md` — reviewed service-promotion contract for installer branching, principal continuity, and state-root preservation
- `docs/214-remote-volume-path-class-and-notification-confidence-interface-spec.md` — path-class and detection-grade contract for service-visible remotes, scan-bound freshness, and degraded local truth
- `docs/215-declared-config-subject-set-and-interactive-control-boundary-interface-spec.md` — declaration-branch contract for declared subject sets, live-graph diff, and interactive mutability boundaries
- `docs/216-uninstall-offboard-peer-tombstone-and-hidden-residue-attestation-interface-spec.md` — reviewed closure contract for peer tombstones, control-plane cleanup, hidden per-subject residue, and platform-forced local-copy loss
- `docs/50-roadmap.md` — near-term phases and exit criteria
- `docs/sources.md` — current external source notes for this revision
'''
(ROOT / 'README.md').write_text(readme)

# --- append/update evaluation ---
eval_path = DOCS / '10-resilio-sync-evaluation.md'
eval_text = eval_path.read_text()
eval_text = re.sub(r'^# .*$', '# Resilio Sync evaluation (service worlds, declared branches, and closure pass)', eval_text, count=1, flags=re.M)
insert = '''\n\n### Additional current pass: four more present-day seams still worth diverging from\n\nCurrent official docs still expose four more interface contracts AnonSync should not inherit as-is.\n\n#### 1) Service install still conflates backgrounding the same node with starting a different service world\n\nCurrent official docs still say Windows service install can either **migrate settings and uninstall the existing Sync client** or perform a **clean installation**.\nThey also still say the service can run as current user, Local Service, or Local System.\nThat means `make this run in background` is not one stable action.\nIt can mean: preserve current state, start a clean seat, or start a seat whose principal opens a different storage world.\n\nAnonSync should therefore treat service promotion as a reviewed continuity branch with one explicit receipt, not as installer convenience.\n\n#### 2) A reachable path can still lose strong local-truth semantics\n\nCurrent official docs still say a Windows service does not receive interactive mapped drives, that a UNC-style workaround keeps the path usable but loses system file-update notifications, and that Sync then learns about changes only during rescan or after restart.\nA separate watcher-budget warning still says Linux can likewise drop to periodic/manual rescan when watcher limits are exhausted.\n\nThat means `path still reachable` is not enough truth.\nAnonSync should therefore classify bound targets by path class and detection grade, not just path string and reachability.\n\n#### 3) Declarative config still overrides live interactive reality in ways the operator can miss\n\nCurrent official docs still say configuration mode can apply the same settings across many machines, but they also still say it can configure only Standard folders and that if shared folders are specified in the config file the WebUI is disabled and the configured directories override folders previously added from WebUI.\n\nThat is not a harmless rollout mechanism.\nIt is a declaration branch with a narrower capability envelope and a different mutability boundary.\nAnonSync should therefore review declaration-vs-live graph delta explicitly before activation.\n\n#### 4) Uninstall still collapses departure, cleanup, and leftover-state truth into one verb\n\nCurrent official docs still say the operator should unlink identity and remove remaining Standard shares first or the removed instance will continue to show as `offline` elsewhere.\nThey still say service storage may need manual deletion, that hidden `.sync/Archive` bytes remain unless cleaned separately, and that ordinary shared folders remain after uninstall on desktop-class systems even though some mobile platforms remove local copies with app removal.\n\nThat is enough reason for AnonSync to prefer one reviewed closure plan and one closure receipt instead of a generic uninstall verb.\n'''
# insert after bottom line section intro paragraphs
marker = '### Additional current pass: four present-day seams still worth diverging from'
if insert.strip() not in eval_text:
    eval_text = eval_text.replace(marker, insert + '\n\n' + marker, 1)
eval_path.write_text(eval_text)

# --- append product direction addendum ---
pd_path = DOCS / '20-product-direction.md'
pd_text = pd_path.read_text()
addendum = '''\n\n## Revision addendum — service worlds, declaration branches, and closure receipts\n\nThis revision settles four tighter product decisions that current official Resilio docs still leave too distributed:\n\n- **daemonization is a reviewed seat promotion, not an install-mode checkbox**\n- **target admission publishes path class and detection grade, not merely reachability**\n- **declarative rollout is a declaration branch, not a silent override of live interactive state**\n- **program removal compiles to a closure plan and receipt, not a generic uninstall verb**\n\nThese decisions intentionally make AnonSync heavier than convenience folklore at the moment the operator changes runtime world, tolerates rescan-bound storage, activates a declaration, or retires a node.\nThat extra explicitness is the point.\n'''
if addendum.strip() not in pd_text:
    pd_text += addendum
pd_path.write_text(pd_text)

# --- append roadmap addendum ---
roadmap_path = DOCS / '50-roadmap.md'
roadmap_text = roadmap_path.read_text()
road_add = '''\n\n## Revision addendum — next tranche after rev0138\n\nThe next tranche should now assume the following are non-optional:\n\n- a first-class **service-promotion review** that distinguishes same-node promotion, same-node-with-followup, clean branch, and inspect-only outcomes\n- a first-class **path-class and detection-grade receipt** so scan-bound or service-visible remotes do not masquerade as healthy native targets\n- a first-class **declaration activation review** that shows declared-vs-live graph delta and capability-envelope loss before a baseline becomes authoritative\n- a first-class **closure receipt** that separates peer tombstone, control-plane cleanup, hidden share-local residue cleanup, ordinary folder survival, and platform-forced local-copy loss\n'''
if road_add.strip() not in roadmap_text:
    roadmap_text += road_add
roadmap_path.write_text(roadmap_text)

# --- append sources addendum ---
sources_path = DOCS / 'sources.md'
sources_text = sources_path.read_text()
sources_add = '''\n\n## Revision addendum — service promotion, remote-path honesty, declaration branching, and closure truth\n\nThis revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier power, reclaim, and mobile-seat passes.\nThe new questions were:\n\n> where do current official docs prove that **service promotion** still branches between same-node continuity and clean background world creation rather than a simple `run in background` toggle?\n\n> what current documentation most clearly proves that **a reachable path** can still lose strong local-change detection and fall back to rescan or restart ritual?\n\n> where do current official docs show that **declarative configuration** still narrows capability and can override or disable the ordinary live control surface?\n\n> how do current docs prove that **uninstall/offboard** still mixes peer departure, storage cleanup, hidden share-local residue, and platform-forced copy loss rather than one explicit closure plan?\n\nThe most load-bearing source set for this pass was the maintained v3 change log together with docs on Windows service install and troubleshooting, configuration mode, storage folder paths, watcher-budget exhaustion, and uninstall guidance.\n\n### Additional Resilio official sources emphasized in rev0138\n\n- Resilio Sync 3.0 change log  \n  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log\n\n- Running Sync as a service on Windows  \n  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows\n\n- Sync Service Troubleshooting on Windows  \n  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows\n\n- Running Sync in configuration mode  \n  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode\n\n- Sync Storage folder  \n  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder\n\n- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  \n  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan\n\n- How to uninstall Sync?  \n  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync\n'''
if sources_add.strip() not in sources_text:
    sources_text += sources_add
sources_path.write_text(sources_text)

print('updated to', rev)
