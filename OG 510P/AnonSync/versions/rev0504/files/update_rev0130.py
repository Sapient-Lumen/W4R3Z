from pathlib import Path

root = Path('/mnt/data/anonsync_rev/anonsync_rev0130')
docs = root / 'docs'

REV = 'rev0130'
STAMP = '2026.03.19.17.34'
CODENAME = 'nameplaneevictioncarrysignal'

DOC181 = '''# Case, encoding, path-length, and invalid-name portability review interface spec

## Purpose

The archive already had filesystem portability, conflict provenance, and path-collision review.
What it still lacked was one concrete interface contract for the most operator-visible portability failure of all:

> when names, encoding, case-folding, invalid symbols, or path-length limits are the real reason a share diverges, what page tells the operator that *before* the product falls back to suffixed conflict artifacts and support ritual?

Current official Resilio docs make this seam sharper than the earlier portability pass.
They still say conflict artifacts appear when peers disagree about letter case or encoding, they still warn not to simply delete a `.Conflict` file because it corresponds to a real remote file, they still tell the operator to align letter case and remove invalid symbols/links manually, and their troubleshooting docs still point to UTF-8 expectations plus OS-specific filename/path-length ceilings.
That is candid support guidance.
It is not a good public operator contract.

## Core decision

AnonSync should treat **name portability** as a first-class reviewed surface, not as a side effect of conflict filenames.

That means:

- name portability must be checked explicitly at bind time, import time, and repair time
- collisions caused by case-folding, unicode normalization, invalid symbols, or target limits must become typed review cases
- the operator must be able to see whether the honest answer is rewrite, alias, block, quarantine, or separate-subject fork
- any rewrite or block must emit a receipt that later proves what was normalized, rejected, or kept distinct

If a user still has to infer the problem from `.Conflict` suffixes or from which peer happens to lose the race, the interface is not explicit enough.

## Why this matters

Current Resilio docs still expose five truths AnonSync should not clone:

- same-path truth can still fracture on letter-case mismatch alone
- unicode/encoding mismatch can still surface only as conflict fallout or `doesn't sync` troubleshooting
- invalid symbols and link-like entries can still be part of the same conflict/repair story
- path length ceilings still depend on target OS and appear as troubleshooting constraints rather than reviewed contract data
- conflict cleanup still depends on moving one healthy copy aside, deleting the conflict-named entries, and putting the healthy copy back

AnonSync should instead keep one public rule:

> if a pathname is not portable, the product must tell you *which portability class is violated, what rewrite or split would happen, and what evidence survives the decision*.

## Fixed review order

Every non-trivial name-portability case should render the same sections in the same order:

1. **Candidate path set and affected namespace**
2. **Portability evidence**
3. **Admissible normalization or split outcomes**
4. **Repair and receipt promise**

### 1) Candidate path set and affected namespace

This section should show:

- the original candidate names exactly as observed
- the target mount and filesystem profile
- whether the issue is local-only, cross-peer, or import-time
- whether the candidates currently map to one visible path, two distinguishable paths, or a blocked path class on this target

The operator must be able to answer: **what names are actually competing here, and where?**

### 2) Portability evidence

This section should show:

- case-fold result
- unicode normalization result
- invalid-symbol result
- path-length result
- reserved-name result where relevant
- whether the problem is merely cosmetic, namespace-colliding, or fundamentally blocked on this target

The operator must be able to answer: **what exact portability class is failing?**

### 3) Admissible normalization or split outcomes

This section should show only honest next actions, such as:

- `Preserve distinct names on a capable target`
- `Normalize into one canonical portable name`
- `Fork into separate local-only paths pending adjudication`
- `Block bind on this target`
- `Quarantine invalid entry class`
- `Open wider path repair review`

The operator must be able to answer: **what safe outcome is actually being proposed?**

### 4) Repair and receipt promise

This section should show:

- what portability receipt will be emitted
- whether the result preserves one namespace, forks it, or blocks it
- whether any loser path is copied aside, quarantined, or left untouched
- whether a later wider conflict-resolution review is still required

The operator must be able to answer: **what evidence will prove what the product did to these names?**

## Public objects

### Name portability case

Fields:

- `name_portability_case_id`
- `share_ref`
- `mount_ref`
- `candidate_names[]`
- `detected_classes[]` (`case-fold-collision`, `unicode-normalization-collision`, `invalid-symbol`, `path-too-long`, `reserved-name`, `encoding-unsupported`, `mixed`)
- `target_fs_profile_ref`
- `canonical_portable_rendering` nullable
- `severity` (`watch`, `guarded`, `high`, `blocked`)
- `suggested_outcomes[]`
- `generated_at`
- `provenance_ref` nullable

### Name portability review

Fields:

- `name_portability_review_id`
- `case_ref`
- `requested_action` (`bind`, `repair`, `import`, `rename`, `reconcile`)
- `outcome_options[]`
- `chosen_outcome` nullable
- `copy_aside_plan_ref` nullable
- `linked_conflict_ref` nullable
- `generated_at`
- `expires_at` nullable

### Name portability receipt

Fields:

- `name_portability_receipt_id`
- `review_ref`
- `applied_outcome`
- `canonical_name` nullable
- `preserved_variants[]`
- `quarantined_variants[]`
- `blocked_variants[]`
- `loser_handling`
- `completed_at`
- `provenance_ref` nullable

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. subject or share
2. target mount
3. portability class
4. currently visible namespace effect
5. next honest action

Example:

```text
Design-Archive     /Volumes/NAS/Design     case-fold-collision + path-too-long     one visible path on target     Review canonicalization
```

The product should not reduce that to `Conflict file created`.

## CLI implications

A minimum public surface should include:

```text
anonsync name portability scan --share <share> --mount <mount>
anonsync name portability show <case_id>
anonsync name portability review <case_id> --plan
anonsync name portability apply <review_id>
anonsync name portability receipt show <receipt_id>
```

The CLI should let operators answer the portability question without opening hidden folders or reverse-engineering suffixes.
'''

DOC182 = '''# Presented name, disk name, and portable-artifact alias interface spec

## Purpose

The archive already separates subject identity from authority identity.
What it still lacked was one interface contract for a different naming problem:

> when a share has one on-disk name, another local presentation name, and yet another portable-artifact or invite label, what page stops those from collapsing back into one ambiguous `folder name` story?

Current Resilio docs make this seam unusually clear.
They still say a desktop share can get a custom UI name that does not rename the folder on disk and does not propagate to linked devices, while a different custom name can be inserted into a link during sharing even though the underlying share name remains unchanged.
Separate docs still say renaming the synced folder itself affects only the local device.
That means a useful product can still have at least four live name planes at once.

AnonSync should not hide that.

## Core decision

AnonSync should make **name planes** explicit:

- **subject title** — the stable human-facing title for the shared subject
- **local mount label** — the label used in one local work surface
- **disk name** — the path component on one specific target path
- **portable artifact label** — the title shown in an offer, invite, or exported artifact
- **peer-visible alias** — a chosen label intentionally announced to peers

A name-plane change must say which of those planes changes and which do not.

## Why this matters

Current Resilio docs still reveal four truths AnonSync should not clone:

- UI names and on-disk names can diverge
- link labels can diverge again from both
- those different labels do not all propagate to the same places
- local folder rename and shared-subject identity are still easy to conflate if the product only shows one name slot

So AnonSync needs a stricter rule:

> every name mutation must declare its plane, audience, propagation scope, and continuity effect.

## Fixed review order

Every non-trivial naming-plane action should render the same sections in the same order:

1. **Current name planes**
2. **Requested mutation and propagation scope**
3. **Continuity and ambiguity risks**
4. **Admissible outcomes and receipt promise**

### 1) Current name planes

This section should show at least:

- subject title
- local mount label for the active seat
- on-disk path basename for the active mount
- currently active peer-visible alias, if any
- currently active portable-artifact label, if any

The operator must be able to answer: **which names already exist here, and where do they live?**

### 2) Requested mutation and propagation scope

This section should show:

- which plane is being changed
- who will observe the change
- whether future artifacts inherit the new label
- whether existing peers or mounts are unaffected
- whether a path rename, subject relabel, and artifact alias edit are being proposed separately or together

The operator must be able to answer: **what name is changing, for whom?**

### 3) Continuity and ambiguity risks

This section should show:

- whether the requested change could be mistaken for authority continuity, path continuity, or a new subject
- whether two planes would become misleadingly equal or misleadingly divergent
- whether the action should escalate into path review, identity review, or artifact reissue review

The operator must be able to answer: **could this rename lie about what stayed the same?**

### 4) Admissible outcomes and receipt promise

This section should show only honest next actions, such as:

- `Retitle subject only`
- `Rename local mount label only`
- `Rename disk path here`
- `Set peer-visible alias`
- `Reissue artifact with new label`
- `Keep planes separate and explain why`

The receipt promise must state which planes changed and which remained untouched.

## Public objects

### Name plane profile

Fields:

- `name_plane_profile_id`
- `subject_ref`
- `subject_title`
- `peer_visible_alias` nullable
- `local_mount_labels[]`
- `disk_base_names[]`
- `artifact_labels[]`
- `last_mutated_at`
- `provenance_ref` nullable

### Name plane review

Fields:

- `name_plane_review_id`
- `subject_ref`
- `requested_plane` (`subject-title`, `local-mount-label`, `disk-name`, `peer-alias`, `artifact-label`, `mixed`)
- `requested_scope` (`local-seat`, `selected-mount`, `future-artifacts`, `peer-visible`, `mixed`)
- `ambiguity_findings[]`
- `admissible_actions[]`
- `generated_at`
- `expires_at` nullable

### Name plane receipt

Fields:

- `name_plane_receipt_id`
- `review_ref`
- `changed_planes[]`
- `unchanged_planes[]`
- `propagation_scope`
- `artifact_reissue_ref` nullable
- `completed_at`
- `provenance_ref` nullable

## Workbench rules

A share header should never compress all name planes into one unlabeled title.
At minimum, the detail page should show:

- **Subject**
- **Disk path here**
- **Peers see**
- **New invites show**

If all four values happen to match, the product may collapse them visually into one calm presentation.
If they diverge, the interface must not hide the divergence.

## CLI implications

A minimum public surface should include:

```text
anonsync subject names show <subject>
anonsync subject names review <subject> --plane artifact-label --value "Team Archive"
anonsync subject names apply <review_id>
anonsync subject names receipt show <receipt_id>
```
'''

DOC183 = '''# Rename, move, and archive-assisted continuity interface spec

## Purpose

The archive already had rehome, path repair, and layout continuity.
What it still lacked was one interface contract for a narrower but very practical seam:

> when a user says `rename`, `move`, or `rehome`, what page distinguishes a local path rename, a shared-subject relabel, a same-root move, a cross-root rehome, and a byte-costly replay that only *looks* like a rename?

Current official Resilio docs make this sharper than before.
They still say renaming a syncing folder affects only the local device, moving across partitions or outside allowed roots can require disconnect/reconnect, and remote file rename efficiency still depends on Archive being enabled because otherwise the bytes are re-synced.
That means a familiar operator word — `rename` — is still carrying several materially different continuity stories.

## Core decision

AnonSync should split rename/move intent into explicit operation classes:

- `subject-retitle`
- `local-path-rename`
- `same-root-move`
- `cross-root-rehome`
- `archive-assisted-file-rename`
- `retransmit-as-new-content`

The interface must tell the operator which class is actually being proposed.

## Why this matters

Current Resilio docs still reveal five truths AnonSync should not clone:

- local folder rename does not imply peer rename
- some moves are continuity-preserving while others fall back to reconnect ritual
- remote rename efficiency can depend on a hidden retention feature rather than one explicit cost preview
- archive posture therefore affects not just restore but rename bandwidth semantics
- the same human intention (`just rename it`) can imply either cheap metadata continuity or heavy byte replay

AnonSync should therefore keep one stronger rule:

> every rename or move review must state continuity class, byte-cost expectation, and whether any hidden retention dependency is carrying the result.

## Fixed review order

Every non-trivial rename or move case should render the same sections in the same order:

1. **Requested operation class**
2. **Continuity and scope**
3. **Byte-cost and retention dependency**
4. **Admissible outcomes and receipt promise**

### 1) Requested operation class

This section should show whether the action is:

- retitling a subject
- renaming a local path component
- moving within the same reviewed root
- moving across roots
- attempting a peer-visible rename of an actual file or subtree

The operator must be able to answer: **what kind of rename or move is this, really?**

### 2) Continuity and scope

This section should show:

- whether continuity is local-only, mount-continuous, share-continuous, or rebind-required
- whether peers will observe any new path name
- whether the action preserves lineage or creates a new bind/replay risk

The operator must be able to answer: **what stays the same after apply?**

### 3) Byte-cost and retention dependency

This section should show:

- whether the operation is metadata-cheap, archive-assisted, or full retransmit risk
- whether current retention state is helping continuity
- whether disabling retention/archive would change this outcome
- whether any low-space or policy posture makes the cheap path unavailable

The operator must be able to answer: **is this a cheap rename, or am I actually paying for replay?**

### 4) Admissible outcomes and receipt promise

This section should show only honest next actions, such as:

- `Retitle subject only`
- `Rename path here only`
- `Move within reviewed root`
- `Open cross-root rehome review`
- `Proceed knowing this becomes byte replay`
- `Block because continuity cannot be honestly claimed`

## Public objects

### Rename continuity plan

Fields:

- `rename_continuity_plan_id`
- `subject_ref` nullable
- `mount_ref` nullable
- `requested_operation_class`
- `continuity_class` (`local-only`, `mount-continuous`, `share-continuous`, `rebind-required`, `blocked`)
- `byte_cost_class` (`metadata-cheap`, `archive-assisted`, `likely-retransmit`, `full-replay`, `unknown`)
- `retention_dependency` (`none`, `helpful`, `required-for-cheap-path`, `blocked-by-policy`)
- `peer_visible_effect`
- `recommended_next_action`
- `generated_at`
- `provenance_ref` nullable

### Rename continuity receipt

Fields:

- `rename_continuity_receipt_id`
- `plan_ref`
- `applied_operation_class`
- `actual_continuity_class`
- `actual_byte_cost_class`
- `retention_state_at_apply`
- `completed_at`
- `provenance_ref` nullable

## Compact explanation strip

A truthful compact explanation should fit in one sentence, for example:

```text
This is a local path rename only; peers keep the existing subject title and no remote path rename is implied.
```

or:

```text
This move crosses the reviewed root boundary; continuity can continue only through rehome review, not as an ordinary rename.
```

or:

```text
This remote file rename can reuse existing bytes only because retention still holds the old hash; without that retention posture it becomes a replay.
```

## CLI implications

A minimum public surface should include:

```text
anonsync rename review --subject <subject> --to <name>
anonsync move review --mount <mount> --to <path>
anonsync continuity show <rename_continuity_plan_id>
anonsync continuity receipt show <rename_continuity_receipt_id>
```
'''

DOC184 = '''# Placeholder quorum, no-byte horizon, and eviction guardrail interface spec

## Purpose

The archive already had fetchability, full-copy witness, and file availability.
What it still lacked was one interface contract for the sharpest destructive-materialization question:

> before a user evicts bytes, disconnects a selectively materialized subtree, or trusts placeholder-visible content, what page proves that *some real bytes still exist somewhere* and that the action is not about to create a names-only horizon?

Current official Resilio docs make this seam sharper than the earlier availability pass.
They still say `.rsls` placeholders are 0-byte representations of shared files, they still warn that if every peer turns a file into a placeholder then only placeholders remain with no actual file, they still say disconnecting a selectively synced folder removes placeholders from the folder, and the power-user docs still note that the `disable_remove_from_all_devices` guardrail is ignored in Linux WebUI.
That is useful candor.
It is not enough for a trustworthy operator surface.

## Core decision

AnonSync should require one explicit **eviction guardrail review** whenever bytes may disappear from the currently reachable mesh or from the active local namespace.

That review must distinguish:

- `evict local bytes but witnesses remain elsewhere`
- `names remain but only weak witnesses remain`
- `this action would create a no-byte horizon`
- `this action also changes namespace visibility`
- `this action is merely disconnecting presentation, not deleting share state`

## Why this matters

Current Resilio docs still reveal five truths AnonSync should not clone:

- a visible placeholder is not proof that any full copy still exists
- eviction and deletion semantics can still be confused because both start from the same placeholder surface
- disconnecting a selectively synced folder changes local namespace, not just local bytes
- one safety toggle for `remove from all devices` is ignored in one major projection family
- subfolders and placeholder states still carry special handling nuance that is easy to miss

AnonSync should therefore insist on a stronger rule:

> any action that could turn bytes into names-only state must show witness strength, horizon risk, and namespace side effects in one place before apply.

## Fixed review order

Every non-trivial eviction or disconnect case should render the same sections in the same order:

1. **Current bytes and witnesses**
2. **Requested eviction or disconnect effect**
3. **No-byte horizon risk**
4. **Admissible outcomes and receipt promise**

### 1) Current bytes and witnesses

This section should show:

- local materialization state
- known remote full-copy witnesses
- witness freshness and confidence
- whether any witness is policy-limited, stale, or unavailable now

The operator must be able to answer: **where do real bytes still exist?**

### 2) Requested eviction or disconnect effect

This section should show:

- whether the action removes bytes only, placeholders only, or local bind visibility entirely
- whether remote peers are affected
- whether archive/preservation makes any stronger claim here or not

The operator must be able to answer: **what exactly disappears if I continue?**

### 3) No-byte horizon risk

This section should show:

- whether the product can still prove at least one durable full copy after apply
- whether the result becomes guarded because all known witnesses are placeholders or stale
- whether the action is blocked because it would strand the subject at names-only state

The operator must be able to answer: **am I about to keep names but lose bytes?**

### 4) Admissible outcomes and receipt promise

This section should show only honest next actions, such as:

- `Evict local bytes safely`
- `Pin one remote witness first`
- `Keep placeholder but do not delete remotely`
- `Disconnect local bind only`
- `Block because no full-copy witness would remain`

The receipt promise must record the witness set and the horizon verdict.

## Public objects

### Eviction guardrail review

Fields:

- `eviction_guardrail_review_id`
- `share_ref`
- `scope_ref`
- `requested_action` (`evict-local-bytes`, `disconnect-local-bind`, `remove-placeholder-view`, `delete-share-visible`, `mixed`)
- `local_materialization_state`
- `witness_summary`
- `horizon_risk` (`none`, `guarded`, `high`, `blocked`)
- `namespace_side_effects[]`
- `admissible_actions[]`
- `generated_at`
- `expires_at` nullable

### Eviction guardrail receipt

Fields:

- `eviction_guardrail_receipt_id`
- `review_ref`
- `applied_action`
- `post_apply_witness_summary`
- `post_apply_horizon_risk`
- `namespace_effect`
- `completed_at`
- `provenance_ref` nullable

## Row and card rules

A truthful compact row should keep these facts in stable order:

1. path or subtree
2. local bytes state
3. witness strength
4. horizon verdict
5. next honest action

Example:

```text
/Projects/Video/raw     local bytes present     2 full-copy witnesses / 1 stale     none     Evict local bytes
/Projects/Video/proxy   placeholder only        0 fresh full-copy witnesses          blocked  Pin a witness first
```

The product should never let a generic trash icon stand in for that distinction.

## CLI implications

A minimum public surface should include:

```text
anonsync evict review --path <path>
anonsync evict apply <eviction_guardrail_review_id>
anonsync evict receipt show <eviction_guardrail_receipt_id>
anonsync witness show --path <path>
```
'''

STATUS = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0129`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based, current, and specific not only about hidden service state, warning-tier targets, nested subtree topology, and one-way semantics, but now also about **name portability**, **name-plane ambiguity**, **rename/rehome cost honesty**, and **placeholder no-byte risk**
- spend more time on **interface specs**, especially where current sync products still ask the operator to reverse-engineer meaning from conflict suffixes, per-surface names, archive-dependent rename behavior, or placeholder-only states
- preserve the shell/workspace/value-provenance, commit barrier, reconnect/repair, local-web-first, route truth, continuity, restore, and topology decisions already made unless fresh evidence actually breaks them
- make a better explicit case for why AnonSync should not inherit Resilio's conflict-filename folklore, ambiguous name planes, archive-dependent rename semantics, or names-without-bytes materialization model even while learning from its strengths

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {REV}
- Timestamp: {STAMP} America/New_York
- Codename: {CODENAME}

- a further-tightened **Resilio evaluation** that now treats conflict-file portability ritual, diverging name planes, archive-assisted rename/replay behavior, and placeholder-only byte loss as additional non-clone reasons
- a new **case / encoding / path-length / invalid-name portability review** interface spec so case-folding, unicode, symbol, and target-limit collisions stop being learned through `.Conflict` artifacts and troubleshooting pages
- a new **presented name / disk name / portable-artifact alias** interface spec so subject title, disk basename, peer alias, and invite label stop collapsing into one ambiguous `folder name`
- a new **rename / move / archive-assisted continuity** interface spec so local rename, share retitle, same-root move, cross-root rehome, and byte replay stop hiding under the same verb
- a new **placeholder quorum / no-byte horizon / eviction guardrail** interface spec so a names-only state is detected and blocked before destructive materialization actions
- updated top-level docs so the archive now makes firmer choices about namespace portability truth, name-plane truth, rename-cost truth, and materialization-horizon truth

## The main shift

`{REV}` closes the next seam:

> it is not enough to have good filesystem fidelity, conflict provenance, path repair, and fetchability language if the operator still has to reconstruct **name portability**, **which name plane is changing**, **whether `rename` is really cheap continuity or byte replay**, and **whether placeholders still correspond to any real bytes** from suffixes, hidden retention behavior, or surface-specific labels.

That changes the archive in eight specific ways:

- name portability now has one explicit **portability review** instead of conflict-filename folklore
- path/name collisions can now say whether the true issue is case-folding, normalization, invalid symbols, reserved names, or length limits before apply
- naming can now distinguish **subject title**, **local mount label**, **disk basename**, **peer-visible alias**, and **artifact label** in one place
- rename and move can now distinguish **local-only rename**, **subject retitle**, **same-root move**, **cross-root rehome**, and **byte replay** in one continuity screen
- rename cost can now say whether current cheapness depends on retention/archive posture instead of letting replay behavior appear as a surprise
- eviction can now publish a **no-byte horizon** verdict before placeholder-heavy actions apply
- disconnect can now say whether it removes bytes, placeholders, or local visibility rather than just saying `disconnect`
- destructive-materialization actions can now carry a receipt proving witness strength and horizon safety at apply time

## Files added in this revision

- `docs/181-case-encoding-pathlength-and-invalid-name-portability-review-interface-spec.md`
- `docs/182-presented-name-disk-name-and-portable-artifact-alias-interface-spec.md`
- `docs/183-rename-move-and-archive-assisted-continuity-interface-spec.md`
- `docs/184-placeholder-quorum-no-byte-horizon-and-eviction-guardrail-interface-spec.md`
- `update_rev0130.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/20-product-direction.md`
- `docs/50-roadmap.md`
- `docs/sources.md`
'''

SOURCES_APPEND = '''
## Revision addendum — name portability, name planes, rename cost, and placeholder no-byte risk

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier hidden-state and restore passes.
The new questions were:

> where do current official docs prove that **name portability truth** still leaks through conflict suffixes and troubleshooting lore rather than one typed portability review?

> where do current docs show that **presentation names, disk names, and portable-artifact labels** can diverge without one clear public model?

> what current evidence most clearly shows that a familiar `rename` can still hide **archive-assisted continuity versus real byte replay**?

> where do current docs prove that placeholder-heavy flows can still leave operators with **names but no bytes** unless witness truth is shown explicitly?

The most load-bearing source set for this pass was the maintained v3 line together with docs on conflict files, rename behavior, custom share names, selective-sync placeholder files, disconnect/reconnect, synchronization modes, power-user guardrails, and troubleshooting for UTF-8/path-length failures.

### Additional Resilio official sources emphasized in rev0130

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync
'''

README = root / 'README.md'
text = README.read_text()
text = text.replace('- Revision: `rev0129`', f'- Revision: `{REV}`')
text = text.replace('- Timestamp: `2026.03.19.17.09` (America/New_York)', f'- Timestamp: `{STAMP}` (America/New_York)')
text = text.replace('- Codename: `statewarningsubtreetripwire`', f'- Codename: `{CODENAME}`')

start = text.index('## What changed in this revision')
end = text.index('## Current conclusion')
new_changes = f'''## What changed in this revision

This revision continues directly from `rev0129` and does twelve specific things:

1. Pushes the **Resilio Sync** evaluation further with current official evidence about conflict-file portability ritual, name-plane divergence, archive-assisted rename behavior, and placeholder no-byte risk.
2. Sharpens the non-clone reason again: the remaining problem is not missing features but too much meaning spread across `.Conflict` suffixes, troubleshooting lore, per-surface names, archive-dependent rename semantics, and placeholder-heavy destructive actions.
3. Adds a new **case / encoding / path-length / invalid-name portability review spec** so namespace portability becomes a typed review instead of suffix fallout.
4. Adds a new **presented name / disk name / portable-artifact alias spec** so subject title, disk basename, peer alias, and invite label become explicit name planes.
5. Adds a new **rename / move / archive-assisted continuity spec** so local rename, same-root move, rehome, and replay-cost truth stop hiding under the same verb.
6. Adds a new **placeholder quorum / no-byte horizon / eviction guardrail spec** so names-only state is surfaced and blocked before destructive materialization actions.
7. Refreshes the **Resilio evaluation** so the comparison now also covers case-fold and encoding collisions, local-only rename behavior, link-label divergence, and placeholder-only risk.
8. Refreshes the **product direction** so namespace portability truth, name-plane truth, continuity-cost truth, and no-byte-horizon truth become doctrine instead of scattered caution.
9. Refreshes the **roadmap** so the next tranche now emphasizes portability-review surfaces, name-plane clarity, rename-cost previews, and eviction guardrails.
10. Refreshes the **source notes** so the official evidence set now explicitly includes `Conflict files in Sync`, `What happens when file is renamed`, `What Is an RSLS File?`, `Setting custom name for sync shares`, and `My files don't sync`.
11. Keeps the archive tight by extending existing filesystem, continuity, naming, and fetchability grammar instead of creating unrelated side systems.
12. Preserves the earlier hidden-state, degraded-target, topology, restore, presence, route, and continuity decisions while giving them stronger portability, naming, replay-cost, and materialization-horizon companions.

'''
text = text[:start] + new_changes + text[end:]

old_conclusion_start = text.index('## Current conclusion')
old_reading_start = text.index('## Recommended reading order')
new_conclusion = '''## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The reason is sharper again and still evidence-based.
Current official docs still show a maintained Sync v3 line through `3.1.2.1076` in late 2025, a refreshed v3 UI, practical link/QR/app delivery, linked-device convenience, selective/disconnected materialization, and a candid help center.
That is why Resilio remains worth studying rather than dismissing.

But the better non-clone reason is now this:

> Resilio still solves many real operator problems while leaving too much meaning about *name portability, name-plane truth, rename continuity cost, and placeholder byte safety* distributed across `.Conflict` suffixes, troubleshooting pages, local-only custom names, archive-dependent rename behavior, and placeholder-heavy actions where AnonSync wants one typed portability review, one explicit name-plane ledger, one continuity-cost review, and one no-byte-horizon guardrail.

The most important current examples are now:

- conflict artifacts still arise from case, encoding, invalid-symbol, and similar namespace problems, and the docs still say not to simply delete a `.Conflict` file
- troubleshooting still asks operators to remember UTF-8 expectations and OS-specific path-length limits as separate caveats
- custom UI names, disk names, and link labels can still diverge without one common naming model
- local folder rename still affects only the local device, while file rename efficiency on other peers still depends on Archive being enabled
- placeholder files still represent names without content, and docs still warn that if every peer reverts to placeholders you can end up with placeholders only and no actual file

So the direction stays the same:

- **borrow** Resilio's practical handoff, linked-device convenience, selective/disconnected materialization, and operational candor
- **reinterpret** them through one stable shell, one subject workspace grammar, one explicit name-plane model, one continuity-cost review, and one witness/horizon guardrail
- **refuse** any interface contract where suffix artifacts, archive side effects, or surface-local labels collectively stand in for portability truth, rename truth, or byte-safety truth

'''
text = text[:old_conclusion_start] + new_conclusion + text[old_reading_start:]

# Update reading order and archive map by inserting new docs near top.
text = text.replace('3. `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md`\n4. `docs/178-warning-tier-target-notification-drift-and-out-of-band-writer-interface-spec.md`\n5. `docs/179-parent-child-subtree-topology-and-non-transitive-seeding-interface-spec.md`\n6. `docs/180-read-only-local-divergence-overwrite-and-seeding-ceiling-interface-spec.md`',
                    '3. `docs/181-case-encoding-pathlength-and-invalid-name-portability-review-interface-spec.md`\n4. `docs/182-presented-name-disk-name-and-portable-artifact-alias-interface-spec.md`\n5. `docs/183-rename-move-and-archive-assisted-continuity-interface-spec.md`\n6. `docs/184-placeholder-quorum-no-byte-horizon-and-eviction-guardrail-interface-spec.md`\n7. `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md`\n8. `docs/178-warning-tier-target-notification-drift-and-out-of-band-writer-interface-spec.md`\n9. `docs/179-parent-child-subtree-topology-and-non-transitive-seeding-interface-spec.md`\n10. `docs/180-read-only-local-divergence-overwrite-and-seeding-ceiling-interface-spec.md`')

# Renumber subsequent items a bit loosely by replacing the next chunk directly.
text = text.replace('7. `docs/173-compromise-response-identity-rotation-and-stolen-seat-review-interface-spec.md`\n8. `docs/174-restore-history-archive-and-share-safe-reintroduction-interface-spec.md`\n9. `docs/175-membership-presence-offline-aging-and-hidden-device-truth-interface-spec.md`\n10. `docs/176-snapshot-send-expiry-budget-and-post-transfer-lineage-interface-spec.md`\n11. `docs/169-subject-kind-migration-and-capability-upgrade-review-interface-spec.md`\n12. `docs/170-topology-aware-rights-editor-and-propagation-ceiling-interface-spec.md`\n13. `docs/171-cross-root-rehome-move-and-missing-path-repair-interface-spec.md`\n14. `docs/172-runtime-seat-switch-and-empty-state-attribution-interface-spec.md`\n15. `docs/165-route-policy-stack-and-effective-directness-interface-spec.md`\n16. `docs/166-share-identity-collision-and-target-preflight-interface-spec.md`\n17. `docs/167-same-machine-derivation-source-child-lineage-and-reconnect-interface-spec.md`\n18. `docs/168-route-narrowing-residue-and-clearance-review-interface-spec.md`\n19. `docs/157-reviewed-mutation-commit-barrier-and-receipt-continuity-interface-spec.md`\n20. `docs/158-adopt-rebind-reconnect-and-pre-existing-path-repair-interface-spec.md`\n21. `docs/159-local-web-first-bringup-auth-and-empty-state-interface-spec.md`\n22. `docs/160-narrow-width-proof-preservation-and-progressive-disclosure-interface-spec.md`\n23. `docs/149-interface-shell-navigation-and-persistent-context-spec.md`\n24. `docs/150-subject-workspace-and-review-stack-interface-spec.md`\n25. `docs/151-inherited-vs-excepted-value-explanation-interface-spec.md`\n26. `docs/152-command-palette-bulk-review-and-apply-boundary-interface-spec.md`\n27. `docs/38-operator-workbench-interface-spec.md`\n28. `docs/39-interface-pattern-language.md`\n29. `docs/30-interface-spec.md`',
                    '11. `docs/173-compromise-response-identity-rotation-and-stolen-seat-review-interface-spec.md`\n12. `docs/174-restore-history-archive-and-share-safe-reintroduction-interface-spec.md`\n13. `docs/175-membership-presence-offline-aging-and-hidden-device-truth-interface-spec.md`\n14. `docs/176-snapshot-send-expiry-budget-and-post-transfer-lineage-interface-spec.md`\n15. `docs/169-subject-kind-migration-and-capability-upgrade-review-interface-spec.md`\n16. `docs/170-topology-aware-rights-editor-and-propagation-ceiling-interface-spec.md`\n17. `docs/171-cross-root-rehome-move-and-missing-path-repair-interface-spec.md`\n18. `docs/172-runtime-seat-switch-and-empty-state-attribution-interface-spec.md`\n19. `docs/165-route-policy-stack-and-effective-directness-interface-spec.md`\n20. `docs/166-share-identity-collision-and-target-preflight-interface-spec.md`\n21. `docs/167-same-machine-derivation-source-child-lineage-and-reconnect-interface-spec.md`\n22. `docs/168-route-narrowing-residue-and-clearance-review-interface-spec.md`\n23. `docs/157-reviewed-mutation-commit-barrier-and-receipt-continuity-interface-spec.md`\n24. `docs/158-adopt-rebind-reconnect-and-pre-existing-path-repair-interface-spec.md`\n25. `docs/159-local-web-first-bringup-auth-and-empty-state-interface-spec.md`\n26. `docs/160-narrow-width-proof-preservation-and-progressive-disclosure-interface-spec.md`\n27. `docs/149-interface-shell-navigation-and-persistent-context-spec.md`\n28. `docs/150-subject-workspace-and-review-stack-interface-spec.md`\n29. `docs/151-inherited-vs-excepted-value-explanation-interface-spec.md`\n30. `docs/152-command-palette-bulk-review-and-apply-boundary-interface-spec.md`\n31. `docs/38-operator-workbench-interface-spec.md`\n32. `docs/39-interface-pattern-language.md`\n33. `docs/30-interface-spec.md`')

text = text.replace('- `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md` — visible rule/service-state ledger replacing hidden control-file semantics and repair folklore',
                    '- `docs/181-case-encoding-pathlength-and-invalid-name-portability-review-interface-spec.md` — typed namespace-portability review for case, encoding, invalid-symbol, and target-limit collisions\n- `docs/182-presented-name-disk-name-and-portable-artifact-alias-interface-spec.md` — explicit separation of subject title, disk basename, peer alias, and invite/artifact label\n- `docs/183-rename-move-and-archive-assisted-continuity-interface-spec.md` — continuity-cost review for local rename, rehome, and archive-assisted versus replay-heavy rename behavior\n- `docs/184-placeholder-quorum-no-byte-horizon-and-eviction-guardrail-interface-spec.md` — witness-first guardrail for placeholder-heavy eviction, disconnect, and no-byte horizon risk\n- `docs/177-hidden-service-state-rule-ledger-and-repair-review-interface-spec.md` — visible rule/service-state ledger replacing hidden control-file semantics and repair folklore')

README.write_text(text)

# Replace status
(docs / '00-status.md').write_text(STATUS)

# Append evaluation addendum
EVAL = docs / '10-resilio-sync-evaluation.md'
text = EVAL.read_text()
text += '''
## Revision addendum — name portability, name planes, rename cost, and placeholder no-byte risk

This pass found a better present-day cluster than another round of general product philosophy would have.
The strongest new reasons not to clone Resilio are no longer about visual style or even only about trust boundaries.
They are about how a modern sync product still explains namespace portability, naming, rename continuity, and placeholder eviction.

## U. Portability truth still leaks through conflict suffixes and troubleshooting lore

Current official Resilio docs still say conflict artifacts arise when peers disagree about letter case or encoding, warn operators not to simply delete `.Conflict` files because those correspond to real remote files, and tell them to move a healthy file aside, delete the conflict-named entries, and put the healthy one back.
Separate troubleshooting docs still say filenames should be UTF-8 and point to OS-specific path-length ceilings.

That is candid support guidance.
It is still a strong reason not to clone the public contract.
If portability truth is learned mainly from suffix artifacts and troubleshooting lists, the ordinary interface is not carrying enough meaning.

AnonSync should therefore keep one stricter rule:

- name portability must be a typed review surface
- case, normalization, invalid-symbol, reserved-name, and length-limit failures must be classified before bind or repair
- loser handling for portability collisions must be explicit and receipted

## V. Share names still live on several planes without one common naming model

Current official Resilio docs still say a share can have a custom UI name that does not rename the folder on disk and does not propagate to linked devices, while a different custom name can be inserted into a link during sharing.
Separate docs still say renaming a syncing folder affects only the local device.

That means a current sync product can easily have at least four live name planes at once:

- disk name here
- UI name here
- portable-artifact label for this invite
- what other peers continue to know

AnonSync should therefore keep another stronger rule:

- name planes must be explicit
- every rename must declare which plane changes and which planes do not
- subject title, disk path, peer alias, and artifact label must not collapse into one `folder name`

## W. `Rename` still hides continuity-cost differences that deserve one review

Current official Resilio docs still say local folder rename affects only one device, moving across some root boundaries falls back to disconnect/reconnect, and remote file rename efficiency depends on Archive being enabled because otherwise bytes are re-synced.

That is exactly the kind of practical behavior AnonSync should explain more explicitly.
The same human intention — `rename this` — can mean:

- a local path relabel
- a local-only folder rename
- a share-visible path mutation
- a same-root move
- a cross-root rehome
- or effectively a replay-heavy copy/delete cycle

AnonSync should therefore keep one continuity-cost rule:

- every rename or move review must publish continuity class, peer-visible scope, and byte-cost expectation
- if cheapness depends on retention/archive posture, the review must say so directly

## X. Placeholder flows still need an explicit no-byte-horizon guardrail

Current official Resilio docs still say `.rsls` placeholders are 0-byte representations, warn that if all peers revert a file to placeholders then only placeholders remain with no actual file, and say disconnecting a selectively synced folder removes placeholders from the folder.
Power-user docs still note that the `disable_remove_from_all_devices` guardrail is ignored in Linux WebUI.

That is not merely a caveat.
It is a strong reason not to clone the surface contract.
A visible placeholder is not proof that any durable full copy still exists.

AnonSync should therefore keep one stronger materialization rule:

- any byte-evicting or placeholder-heavy action must show witness strength and horizon risk first
- namespace effects and byte effects must be distinguished before apply
- `remove`, `evict`, `disconnect`, and `delete everywhere` must not share one ambiguous destructive affordance

## The interface consequences for AnonSync in this revision

This pass adds four more direct interface consequences:

### 17) Portability collisions need one namespace-portability review

Because current docs still teach case/encoding/path-limit truth through suffix artifacts and troubleshooting lore, AnonSync now requires one review page that classifies name portability failures before they become folklore.

### 18) Naming needs one explicit name-plane ledger

Because current docs still let UI labels, disk names, and invite labels diverge without one shared model, AnonSync now requires one surface that shows which name plane is changing and who will observe it.

### 19) Rename and move need one continuity-cost review

Because current docs still let archive posture decide whether a rename stays cheap or becomes replay, AnonSync now requires one continuity review that states local-only versus share-visible scope and metadata-cheap versus replay-heavy cost.

### 20) Placeholder-heavy destructive actions need a no-byte-horizon guardrail

Because current docs still warn that placeholders can outnumber real copies and leave no full data anywhere, AnonSync now requires one eviction guardrail that shows witnesses, horizon risk, and namespace side effects together.
'''
EVAL.write_text(text)

# Append doctrines
PD = docs / '20-product-direction.md'
text = PD.read_text()
text += '''
### Doctrine 59 — portability collisions are not filename trivia

Case-folding, normalization, invalid-symbol, reserved-name, and path-length failures are part of the subject contract on a target path.
The product should review them explicitly instead of letting `.Conflict` suffixes stand in for the operator model.

### Doctrine 60 — one subject may have several honest names, but each needs a declared plane

Subject title, local mount label, disk basename, peer alias, and portable-artifact label may diverge.
That is acceptable only when the interface shows which plane is changing and which audiences will observe it.

### Doctrine 61 — `rename` must publish continuity class and byte cost

A rename can be local-only, mount-continuous, share-continuous, rehome-like, or effectively replay-heavy.
The product should say which class applies before the operator commits to it.

### Doctrine 62 — placeholders are visibility, not proof of surviving bytes

A visible placeholder proves that a path is known.
It does not by itself prove that any durable full copy still exists elsewhere.
The product should guard byte-evicting actions with witness and horizon truth, not with faith.
'''
PD.write_text(text)

# Update roadmap
RM = docs / '50-roadmap.md'
text = RM.read_text()
text = text.replace('- effective-route, route-narrowing, target-preflight, and same-machine-lineage contract so route truth, route residue, duplicate-bind meaning, and local derivation stay semantically honest\n',
                    '- effective-route, route-narrowing, target-preflight, and same-machine-lineage contract so route truth, route residue, duplicate-bind meaning, and local derivation stay semantically honest\n- namespace-portability, name-plane, continuity-cost, and no-byte-horizon contract so collisions, labels, rename cost, and placeholder eviction stay semantically honest\n')
text = text.replace('- narrow-width proof-preservation model\n',
                    '- narrow-width proof-preservation model\n- name-portability case, name-plane review, rename-continuity plan, and eviction-guardrail review model\n')
text = text.replace('- operators can tell whether a target release is merely newer or actually safe for the current daemon, runtime, and peer constellation, and can prove later what compatibility boundary they accepted at cutover time\n',
                    '- operators can tell whether a target release is merely newer or actually safe for the current daemon, runtime, and peer constellation, and can prove later what compatibility boundary they accepted at cutover time\n- operators can tell whether a namespace issue is case-folding, normalization, invalid-symbol, reserved-name, or length-limit trouble before it becomes a conflict artifact\n- operators can tell which name plane they are changing — subject title, local mount label, disk basename, peer alias, or artifact label — and who will observe it\n- operators can tell whether a rename is local-only, rehome-like, or replay-heavy before committing to it\n- operators can tell whether evicting bytes would leave at least one durable full-copy witness or create a names-only horizon\n')
RM.write_text(text)

# Append sources
SRC = docs / 'sources.md'
text = SRC.read_text()
text += SOURCES_APPEND
SRC.write_text(text)

# Write new docs
(docs / '181-case-encoding-pathlength-and-invalid-name-portability-review-interface-spec.md').write_text(DOC181)
(docs / '182-presented-name-disk-name-and-portable-artifact-alias-interface-spec.md').write_text(DOC182)
(docs / '183-rename-move-and-archive-assisted-continuity-interface-spec.md').write_text(DOC183)
(docs / '184-placeholder-quorum-no-byte-horizon-and-eviction-guardrail-interface-spec.md').write_text(DOC184)

# Update root folder naming inside README/status done; nothing else needs rename.
print('updated', REV)
