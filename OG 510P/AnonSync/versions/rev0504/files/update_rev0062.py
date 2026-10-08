from pathlib import Path
import re

root = Path('/mnt/data/anonsync_rev0061')
docs = root / 'docs'


def read(p):
    return Path(p).read_text()

def write(p, s):
    Path(p).write_text(s)

# README
p = root / 'README.md'
s = read(p)
s = s.replace('- Revision: `rev0061`\n- Timestamp: `2026.03.17.15.18` (America/New_York)\n- Codename: `grantproofboundaryledger`\n',
              '- Revision: `rev0062`\n- Timestamp: `2026.03.17.15.43` (America/New_York)\n- Codename: `graphproofcontainmentharbor`\n')
old_block = """This revision continues directly from `rev0060` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on live permission changes and folder-class ritual: Advanced folders support on-the-fly permission changes while Standard folders do not, Standard folders cannot be upgraded in place, linked same-identity devices act as Owners, local-share permission changes can require remove-and-re-share ritual, and config mode can express only Standard folders while configured shares disable WebUI.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let “change who can read, write, delegate, or re-share this live share” blur together write authority, grant reach, local-derivative fallout, byte residue, and share-class/surface migration.\n3. Adds a dedicated **authority-mutation and grant-boundary review interface spec** so the archive now says what a real pre-apply permission-change surface must literally show before consent.\n4. Extends the **interface and daemon/API contract** so non-trivial grant mutations can expose one stable review model instead of scattered user-management menus, disconnect rituals, folder-class switches, and remove/re-share folklore.\n5. Extends the **workbench/interface pattern language** with sharper authority-mutation verbs and fixed review sections for current authority, desired delta, active subject state, authority-substrate effects, admissible mutations, and receipts.\n6. Adds additional **canonical interface flows** for reviewed grant mutation and cross-surface parity instead of leaving live access changes as one convenience dropdown with hidden boundary changes.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, **sources**, and **reading order** so future revisions keep authority-mutation honesty tied to surface parity and explicit boundary proof.\n"""
new_block = """This revision continues directly from `rev0061` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on graph and path topology: separately shared nested folders require read-write-or-owner posture, disable Selective Sync, double-index the child, and still propagate child edits onward through the parent share, while same-host local shares warn against parent/subdirectory loops and move/rename guidance still falls back to reconnect-style path continuity limits.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let “this share is inside that share”, “move it over there”, or “fan it out locally” blur together graph overlap, propagation shape, root-boundary policy, and continuity risk.\n3. Adds a dedicated **overlap, containment, and graph-topology review interface spec** so the archive now says what a real pre-apply topology surface must literally show before consent.\n4. Extends the **interface and daemon/API contract** so non-trivial nested, overlapping, loop-prone, or root-boundary-sensitive share/path actions can expose one stable review model instead of scattered FAQ caveats, path pickers, reconnect rituals, and config-mode restrictions.\n5. Extends the **workbench/interface pattern language** with sharper topology-review verbs and fixed review sections for graph subjects, containment/propagation shape, path/root-boundary effects, admissible actions, and receipts.\n6. Adds additional **canonical interface flows** for reviewed topology decisions and cross-surface parity instead of leaving nested-share and cross-share move meaning to memory.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep topology honesty tied to surface parity, graph proof, and explicit containment boundaries.\n"""
s = s.replace(old_block, new_block)
s = s.replace('- `docs/74-authority-mutation-and-grant-boundary-review-spec.md` — fixed authority-mutation pane anatomy for current authority, desired boundary delta, active subject fallout, substrate effects, and mutation receipts\n',
              '- `docs/74-authority-mutation-and-grant-boundary-review-spec.md` — fixed authority-mutation pane anatomy for current authority, desired boundary delta, active subject fallout, substrate effects, and mutation receipts\n- `docs/75-overlap-containment-and-graph-topology-review-spec.md` — fixed topology-review pane anatomy for graph subjects, containment/propagation shape, path/root-boundary effects, safe topology actions, and topology receipts\n')
s = s.replace('then `74-authority-mutation-and-grant-boundary-review-spec.md`, then `41-report-and-intervention-language.md`',
              'then `74-authority-mutation-and-grant-boundary-review-spec.md`, then `75-overlap-containment-and-graph-topology-review-spec.md`, then `41-report-and-intervention-language.md`')
write(p, s)

# Status
p = docs / '00-status.md'
s = read(p)
s = s.replace('This revision is an in-place continuation of `rev0060`, driven by the current request:',
              'This revision is an in-place continuation of `rev0061`, driven by the current request:')
s = s.replace('- make sure the archive has a better reason not to clone permission-mutation behavior that still depends on Standard-vs-Advanced folder class, linked-device ambient owner power, local-share re-share ritual, disconnect semantics, or config-mode surface limits\n',
              '- make sure the archive has a better reason not to clone permission-mutation behavior that still depends on Standard-vs-Advanced folder class, linked-device ambient owner power, local-share re-share ritual, disconnect semantics, or config-mode surface limits\n- make sure the archive has a better reason not to clone nested-share and overlap behavior that still hides graph topology, child propagation, double indexing, root-boundary policy, move/reconnect limits, and loop risk behind separate FAQs, local-share warnings, and config-mode path restrictions\n')
s = s.replace('`rev0031` through `rev0060` progressively turned state roots, binding, file intent, activity, projection, settlement, rollback, fidelity, storage, offers, transfer truth, attention, control access, recovery, release posture, policy origin, diagnostics, temporary exceptions, personal constellations, exit/replacement, intake, joining, cutover, compromise, stale re-entry, destructive replay, conflict adjudication, and same-host derivation into explicit public contracts.\n\n`rev0061` applies the same discipline to live authority mutation:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define grants, stewardship, constellation limits, local derivation, and successor handoff in the abstract, yet still leave the actual “change this subject from read-only to writable, or from writable to delegating, or strip delegation while preserving bytes” surface vague enough that GUI, WebUI, TUI, and CLI might drift back into different products.\n\nThat changes the archive in six specific ways:\n\n- live permission changes are now specified as a fixed review pane rather than only a mix of peer-list dropdowns, disconnect actions, share-class constraints, and remove/re-share ritual\n- current authority, desired boundary delta, active subject fallout, authority-substrate effects, admissible mutations, and receipt promise now have a stable render order across channels\n- non-trivial grant mutations can project one review model instead of falling back to generic `change access`, `disconnect`, or `re-share with different key` folklore\n- the daemon/API model is now held to a clearer requirement that authority mutation be previewable as boundary-changing work rather than ambient convenience\n- the Resilio comparison now lands a sharper non-clone argument: access changes still hide too much meaning behind Standard-vs-Advanced class, linked-device owner broadening, local-share caveats, and config-mode surface loss\n- future interface work now has a narrower quality bar for reviewed authority-mutation parity on Linux-first deployments\n',
              '`rev0031` through `rev0061` progressively turned state roots, binding, file intent, activity, projection, settlement, rollback, fidelity, storage, offers, transfer truth, attention, control access, recovery, release posture, policy origin, diagnostics, temporary exceptions, personal constellations, exit/replacement, intake, joining, cutover, compromise, stale re-entry, destructive replay, conflict adjudication, same-host derivation, and live authority mutation into explicit public contracts.\n\n`rev0062` applies the same discipline to graph overlap and containment topology:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define bindings, derivations, grants, projection, and continuity in the abstract, yet still leave the actual “is this share nested inside that share, does it double-index, who propagates to whom, can I move it safely, and did I just escape the allowed root?” surface vague enough that GUI, WebUI, TUI, and CLI might drift back into different products.\n\nThat changes the archive in six specific ways:\n\n- non-trivial nested, overlapping, loop-prone, and root-boundary-sensitive topology decisions are now specified as a fixed review pane rather than only a mix of FAQs, warnings, and reconnect/path folklore\n- graph subjects, containment and propagation shape, path/root-boundary effects, admissible topology actions, and receipt promise now have a stable render order across channels\n- nested-share creation, same-host fanout, and cross-share move/rebind work can project one review model instead of falling back to generic `add folder`, `move`, or `connect in new location` ritual\n- the daemon/API model is now held to a clearer requirement that topology changes be previewable as graph-changing work rather than ambient convenience\n- the Resilio comparison now lands a sharper non-clone argument: nested folders, child propagation, double indexing, move limits, and config-mode root restrictions still hide too much meaning behind separate articles and surface loss\n- future interface work now has a narrower quality bar for reviewed topology parity on Linux-first deployments\n')
s = s.replace('- the daemon/API model is now held to a clearer requirement that authority mutation be previewable as boundary-changing work rather than ambient convenience\n- the Resilio comparison now lands a sharper non-clone argument: access changes still hide too much meaning behind Standard-vs-Advanced class, linked-device owner broadening, local-share caveats, and config-mode surface loss\n- future interface work now has a narrower quality bar for reviewed authority-mutation parity on Linux-first deployments\n', '')
s = s.replace('- a deeper Resilio-derived warning that current access-change behavior still depends on folder class, owner-like linkage, disconnect semantics, local-share re-share ritual, and config-mode surface limits\n- a dedicated **authority-mutation and grant-boundary review interface spec** that says what a real reviewed access-change surface must literally show before widening, narrowing, or delegating live authority\n- stronger CLI/API requirements so non-trivial grant mutations can expose one stable review model instead of falling back to peer-list dropdowns, disconnect actions, share-class migration, or folder-class migration\n- stronger workbench and pattern-language rules for reviewed authority mutation so rich and textual surfaces keep the same current-authority, desired-delta, active-subject, substrate-effect, and receipt truth\n- additional canonical flows for rendering the same authority-mutation review in workbench and CLI without semantic drift\n- roadmap, ADR, status, sources, and open-question updates so future revisions keep authority-mutation honesty tied to surface parity and explicit boundary proof\n',
              '- a deeper Resilio-derived warning that current nested-share and overlap behavior still depends on separate-share caveats, local-share loop warnings, move/reconnect limitations, and config-mode root restrictions\n- a dedicated **overlap, containment, and graph-topology review interface spec** that says what a real reviewed topology surface must literally show before nesting, overlapping, moving, or rebinding graph-related subjects\n- stronger CLI/API requirements so non-trivial topology work can expose one stable review model instead of falling back to folder creation, reconnect prompts, or config-only path restrictions\n- stronger workbench and pattern-language rules for reviewed topology so rich and textual surfaces keep the same graph-subject, containment-shape, root-boundary, action, and receipt truth\n- additional canonical flows for rendering the same topology review in workbench and CLI without semantic drift\n- roadmap, ADR, status, and open-question updates so future revisions keep topology honesty tied to surface parity and explicit graph proof\n')
s = s.replace('- when live authority changes should always force full authority-mutation review instead of a safely compressed access-change path\n',
              '- when live authority changes should always force full authority-mutation review instead of a safely compressed access-change path\n- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path\n')
write(p, s)

# Evaluation
p = docs / '10-resilio-sync-evaluation.md'
s = read(p)
insert_before = '\n## Where Resilio is still probably the better choice\n'
new_eval = """
### 16t) Nested shares, overlap, and topology transitions still hide too much graph meaning behind separate caveats

Resilio's current docs make one more seam unusually explicit.

`Is it possible to share a nested folder separately?` says a parent and child folder can both be shared, but only if both have Read & Write or Owner permissions, both disable Selective Sync, the child is indexed separately in addition to as a subfolder of the parent, and peers with only the parent do not seed peers that only have the child. It also says child edits still propagate onward through the parent share, and that the nesting creates heavy load because the child is indexed and rescanned twice.
`Sharing a folder locally` separately warns not to create a local share in a source subdirectory or parent because that creates syncing loops.
`Can I move or rename a syncing folder?` says rename affects only the local device, Windows and macOS moves are limited to the same drive, Linux moves are limited to within the Sync parent folder, and otherwise the operator falls back to disconnect/reconnect-style path repair.
`Running Sync in configuration mode` adds Linux-only `directory_root_policy`, `dir_whitelist`, and the rule that preconfigured shares disable WebUI entirely.

That is not one trustworthy topology model.
It is a mixture of nested-share exception, double indexing, propagation side effects, local self-edge loop warnings, path continuity limits, and config-root ritual.

The operator still has to reconstruct several separate truths from scattered docs:

- whether two graph subjects are truly disjoint, nested, overlapping, or only apparently separate
- whether changes propagate independently, piggyback through a parent, or require full re-download / rebind behavior after a move
- whether Selective Sync, placeholder behavior, or target/root policy is silently disallowed by the chosen topology
- whether a requested path change is ordinary local rename, reviewed rebind, blocked overlap, or escape from an allowed root
- whether the safest next step is nest intentionally, flatten, rebind, split the graph, or reject as loop risk

AnonSync should not clone that shape.
A serious control surface should instead publish one overlap, containment, and graph-topology review model with:

- one explicit review grammar for trigger/graph subjects, containment+propagation shape, path+root-boundary effects, admissible topology actions, and receipt promise
- explicit separation between nested-share topology, same-host derivation, cross-share move, and root-boundary escape
- explicit propagation-shape truth before apply instead of after-the-fact double-indexing or child-via-parent folklore
- explicit root-boundary and surface-availability truth before apply instead of config-mode path ritual after the fact
- explicit receipts proving which graph relation was accepted, which propagation semantics were expected, what path/root restrictions were reviewed, and what follow-up still remained

### Requirement 57 — overlap, containment, and topology transitions must share one reviewed graph contract

If the operator still has to combine nested-share caveats, parent/child loop warnings, move/reconnect folklore, and config-mode root restrictions to answer “what exactly is the graph relationship here, how will changes propagate, and is this path transition actually safe?”, the product has not actually exposed its topology contract.

AnonSync should instead publish one public topology-review model with explicit graph subjects, explicit containment and propagation shape, explicit path/root-boundary effects, explicit admissible topology actions, and durable topology receipts that preserve the difference between safe nesting, blocked overlap, reviewed rebind, and rejected root escape.
"""
s = s.replace(insert_before, '\n' + new_eval + insert_before)
# extend final judgment long list
s = s.replace('and explicit authority-mutation contracts that keep current authority, desired boundary delta, dependent fallout, substrate migration, and byte-retention consequences visible instead of leaving live access changes to folder-class and remove/re-share ritual.\n\n\n\n',
              'and explicit authority-mutation contracts that keep current authority, desired boundary delta, dependent fallout, substrate migration, and byte-retention consequences visible instead of leaving live access changes to folder-class and remove/re-share ritual, and explicit topology-review contracts that keep graph overlap, containment, propagation shape, path/root-boundary consequences, and safe rebind versus blocked-loop decisions visible instead of leaving nested, overlapping, or moved shares to separate FAQs and reconnect folklore.\n\n\n\n')
write(p, s)

# 30 interface spec
p = docs / '30-interface-spec.md'
s = read(p)
marker = '### Approval memory\n'
new_obj = """### Topology review case

A durable plan-bearing record for accepting, rejecting, or repairing a graph relationship among shares, mounts, and local paths.
This exists so operators can inspect the difference between “another folder here” and “a new nested, overlapping, moved, or root-boundary-sensitive topology with specific propagation consequences.”

Fields:

- `topology_case_id`
- `primary_subject_ref`
- `related_subject_refs[]`
- `candidate_path` nullable
- `topology_kind` (`nested-share`, `overlap`, `parent-child`, `cross-share-move`, `same-host-self-edge`, `root-boundary`, `ambiguous`)
- `containment_relation` (`disjoint`, `child`, `parent`, `overlap`, `ambiguous`, `outside-allowed-root`)
- `propagation_shape` (`independent`, `double-indexed`, `piggyback-via-parent`, `self-edge`, `re-download-likely`, `blocked`)
- `path_continuity_posture` (`stable`, `rename-local-only`, `rebind-required`, `disconnect-reconnect-like`, `blocked`)
- `selective_sync_posture` (`allowed`, `disabled-required`, `blocked`, `n/a`)
- `root_boundary_posture` (`within-root`, `needs-root-expansion`, `violates-root-policy`, `unknown`)
- `status` (`draft`, `preflighted`, `planned`, `applied`, `rejected`, `expired`)
- `review_model` nullable
- `compatibility_report_id` nullable
- `provenance_ref` nullable

"""
s = s.replace(marker, new_obj + marker)
write(p, s)

# 31 daemon api
p = docs / '31-daemon-api-spec.md'
s = read(p)
marker = '## Event stream\n'
new_api = """## Topology-review resources

These resources keep nested shares, overlapping graph subjects, cross-share moves, and root-boundary-sensitive path work explicit.
They answer which graph subjects are involved, how containment changes propagation, whether the path stays within allowed roots, and whether the safest next step is accept, rebind, flatten, or reject.

```text
GET    /v1/topology-cases
POST   /v1/topology-cases
GET    /v1/topology-cases/{topology_case_id}
POST   /v1/topology-cases/{topology_case_id}/apply
GET    /v1/topology-receipts/{topology_receipt_id}
```

`POST /v1/topology-cases` should accept one or more share/mount refs plus an optional candidate path and explicit intent such as `nest`, `flatten`, `rebind`, `move-across-boundary`, or `reject-overlap`.
The resulting case or referenced plan should always include:

- trigger and graph-subject summary
- containment relation and propagation-shape findings
- path continuity and root-boundary findings
- admissible topology actions and any safer narrowing path
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `trigger_and_graph_subjects`
- `containment_and_propagation_shape`
- `path_and_root_boundary_effects`
- `admissible_topology_actions`
- `receipt_promise`

Binding, derivation, claim, and filesystem endpoints may still exist for narrower domain actions, but when the operator-visible outcome is accepting or repairing a nested, overlapping, moved, or root-boundary-sensitive graph relationship, those endpoints should reference or emit the same topology-case / topology-receipt model.

"""
s = s.replace(marker, new_api + marker)
# add event types
s = s.replace('-- `state.transition_prepared`\n-- `state.transition_applied`\n', '-- `state.transition_prepared`\n-- `state.transition_applied`\n-- `topology.case_created`\n-- `topology.case_applied`\n')
write(p, s)

# 32 flows
p = docs / '32-interface-flows.md'
s = read(p)
flows = """
## Flow 107 — review a nested child share without pretending the graph is ordinary

Problem: an operator already shares `/srv/projects` with a small team and now wants to share `/srv/projects/blue` separately with a narrower subgroup. The product must not make this look like just “add another folder” when the graph is no longer disjoint.

Goal:

- preview nested-share topology as one reviewed graph decision
- surface double-indexing, propagation shape, selective-sync constraints, and root/path continuity before apply
- avoid child-share folklore, loop warnings, and reconnect memory as the primary explanation

Suggested flow:

```text
anonsync topology review \
  --subject share:projects \
  --subject path:/srv/projects/blue \
  --intent nest --plan
anonsync topology show top_01J... --view review
anonsync topology apply top_01J...
```

Expected semantics:

- the review states whether the candidate is child, parent, overlap, or ambiguous relative to existing graph subjects
- the review states whether propagation would be independent, piggyback through the parent, or create blocked/self-edge behavior
- the review states whether selective materialization or root-boundary policy forbids the chosen topology or requires a narrower action
- the review states whether the safest next step is accept nesting, flatten the structure, rebind elsewhere, or reject as unsafe

Expected operator answers from CLI alone:

- whether the new share is truly separate or only separately addressed inside an already replicated parent
- whether edits in the child will still flow onward through the parent graph
- whether the topology increases indexing or replay cost enough to matter operationally
- whether path continuity and allowed-root policy remain honest after apply

## Flow 108 — render the same topology review in CLI and workbench without semantic drift

Problem: a Linux/WebUI operator previews a cross-share move that would relocate one mount near another shared tree; later a headless operator checks the same plan over SSH. Both surfaces must show the same graph and root-boundary truth.

Goal:

- prove that rich and textual surfaces render the same reviewed topology case
- make graph subjects, containment shape, path/root-boundary effects, and admissible actions read like one product

Workbench expectations:

- opening `Review topology` from a path compare, bind repair, nested-share warning, or local-derivation sheet lands on one topology review page
- the sheet renders sections in this order:
  1. trigger and graph subjects
  2. containment and propagation shape
  3. path and root-boundary effects
  4. admissible topology actions
  5. receipt promise
- the primary action inherits the reviewed intent, for example `Accept nested child with explicit propagation caveat` or `Rebind outside parent graph`, instead of generic `Apply`

CLI expectations:

```text
$ anonsync topology show top_01J... --view review
Topology review
---------------
1. Trigger and graph subjects
   Primary subject: mount blue-team
   Related subject: share projects
   Requested action: move candidate path to /srv/projects/blue

2. Containment and propagation shape
   Relation: child within existing share
   Propagation shape: piggyback-via-parent
   Indexing cost: child path will be scanned twice if accepted separately

3. Path and root-boundary effects
   Path continuity: rebind-required, not local-only rename
   Allowed-root posture: within approved root
   Selective-sync posture: disabled-required for this topology

4. Admissible topology actions
   - Rebind outside parent graph
   - Accept reviewed nested topology
   - Flatten by keeping only the parent share
   - Reject overlap

5. Receipt promise
   Receipt will prove the accepted graph relation, propagation posture, root-boundary findings, and any required follow-up.
```

Cross-surface success criteria:

- both surfaces answer the same question: **what graph relationship is being created or repaired here, how will changes propagate, and is this path transition actually safe?**
- neither surface falls back to generic `add folder`, `move`, or `connect in new location` language when the real decision is a reviewed topology change
"""
s = s + '\n' + flows
write(p, s)

# 39 pattern language
p = docs / '39-interface-pattern-language.md'
s = read(p)
old = '- successor handoff: primary action is `Preview handoff`, not `Apply replacement`\n- state-root/runtime re-home: primary action is `Prepare cutover`, not `Migrate now`\n'
new = old + '- nested or overlapping path work: primary action is `Review topology`, not `Add anyway`\n'
s = s.replace(old, new)
resilio_old = '- conflict semantics still drift between suffix folklore, cleanup dance, and path toggles unless the interface pins adjudication explicitly\n- pause/scheduler semantics can still drift between transfer stop, delete propagation, rescans, and LAN-vs-Internet caps unless the interface pins phase truth explicitly\n'
resilio_new = resilio_old + '- nested and overlapping graph changes still drift between child-share caveats, local loop warnings, path-move limits, and config-root rules unless the interface pins topology truth explicitly\n'
s = s.replace(resilio_old, resilio_new)
write(p, s)

# ADR
p = docs / '40-architecture-decisions.md'
s = read(p)
adr = """
## ADR-075 — Graph overlap and containment need one reviewed contract, not nested-share folklore

**Decision:** Non-trivial nested, overlapping, moved, or root-boundary-sensitive graph relationships should compile to one reviewed topology model rather than depending on separate-share caveats, local loop warnings, reconnect ritual, or config-root restrictions.

**Why:** Resilio's current docs still spread topology meaning across nested-child limitations, double indexing, child-via-parent propagation, same-host parent/subdirectory loop warnings, move/rename limits, and `directory_root_policy` / `dir_whitelist` path rules. AnonSync should keep graph relation, propagation shape, path continuity, and root-boundary truth visible in one place.

**Consequences:**
- topology work gains a stable review grammar and durable topology receipts
- workbench and CLI both need explicit graph-subject and propagation-shape sections
- nested-share acceptance stays visibly distinct from same-host derivation, cross-share move, or root escape
- imported or policy-root path constraints may require visible rebind or root-review rather than silent coercion
"""
s = s.rstrip() + '\n\n' + adr + '\n'
write(p, s)

# Roadmap
p = docs / '50-roadmap.md'
s = read(p)
s = s.replace('- review-model projection for authority mutation and grant-boundary changes so rich and textual clients render the same current-authority/boundary-delta/dependent-fallout sections\n',
              '- review-model projection for authority mutation and grant-boundary changes so rich and textual clients render the same current-authority/boundary-delta/dependent-fallout sections\n- review-model projection for overlap, containment, and graph topology so rich and textual clients render the same graph-subject/propagation/root-boundary sections\n')
s = s.replace('- operators can preview the same authority-mutation truth in workbench and CLI without semantic drift\n',
              '- operators can preview the same authority-mutation truth in workbench and CLI without semantic drift\n- operators can preview the same topology-review truth in workbench and CLI without semantic drift\n')
write(p, s)

# Open questions
p = docs / '64-critical-open-questions.md'
s = read(p)
q = """
## 44) How much low-risk topology convenience is safe before graph honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial nested, overlapping, moved, or root-boundary-sensitive graph relationships should use first-class reviewed topology cases and receipts, but one policy seam remains open:

- when an obviously disjoint or same-root path change may use a safely compressed review versus always opening the full topology sheet
- whether any child-inside-parent or overlap relation should always force full review even when the operator is intentionally building it
- how much propagation-shape automation is acceptable before the product starts hiding double-indexing, piggyback, or re-download consequences behind reassuring summaries
- when allowed-root or whitelist expansion should be reviewed as ordinary topology work versus escalated into stronger filesystem or policy review

This matters because weak defaults recreate nested-share, loop-warning, and reconnect folklore, while overly strict defaults could make harmless path organization feel ceremonial instead of trustworthy.
"""
s = s.rstrip() + '\n\n' + q + '\n'
write(p, s)

# New spec file
spec = docs / '75-overlap-containment-and-graph-topology-review-spec.md'
spec.write_text("""# Overlap, containment, and graph-topology review spec

The archive already has mount binding, local derivation, filesystem fidelity, authority mutation, and claim review.
This document answers the narrower practical question those abstractions still left open:

> what must a real topology surface literally show before an operator nests one share inside another, moves a bound path across graph boundaries, or accepts an overlap that changes propagation shape, so AnonSync does not drift back into child-share caveats, loop warnings, and reconnect folklore?

This is the graph-topology companion to `43-mount-binding-repair-and-preservation-spec.md`, the overlap companion to `73-local-derivation-and-self-edge-review-spec.md`, the path-boundary companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Is it possible to share a nested folder separately?` says a parent and child folder can both be shared, but only if both have Read & Write or Owner permissions, both disable Selective Sync, the child is indexed and rescanned separately in addition to as part of the parent, peers with only the parent do not seed peers that only have the child, and child edits still reach parent-share peers through the parent topology.
`Sharing a folder locally` separately warns not to choose a subdirectory or parent of the source because that creates syncing loops.
`Can I move or rename a syncing folder?` says rename is local-only, Windows/macOS moves are limited to the same drive, Linux moves are limited to within the Sync parent folder, and otherwise the operator falls back to disconnect/reconnect-style repair.
`Running Sync in configuration mode` adds `directory_root_policy`, `dir_whitelist`, and the rule that configured shares disable WebUI.

The lesson is not that graph complexity is bad.
The lesson is that a useful product can still compress too many topology decisions into “add another folder”, “move it”, or “reconnect it here”.

AnonSync should therefore make these differences explicit before apply:

- disjoint graph subject vs child-inside-parent vs ambiguous overlap
- independent propagation vs piggyback-via-parent vs self-edge or blocked loop
- local-only rename vs reviewed rebind vs root-boundary escape
- allowed topology vs topology that disables selective/materialization options
- same-host derivation vs true separate share graph vs move across graph boundaries
- safe nesting vs strong enough blast radius that flattening or rejection is the more honest action

## Core rule

A non-trivial topology change should always compile to a reviewed topology surface.
That includes at least:

- any child-inside-parent or overlapping relation among shares, mounts, or candidate paths
- any path move whose continuity depends on rebind, disconnect/reconnect-like behavior, or changed root policy rather than ordinary local rename
- any graph relationship that changes propagation shape, indexing cost, or source/seed expectations
- any action whose current or requested path posture depends on configured allowed roots, whitelists, or other policy-root restrictions
- any action whose safest next step may actually be flattening, rebind review, filesystem-policy review, or rejection rather than ordinary bind/add

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `Add folder`, `Move`, `Reconnect`, or `Use this path` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench bind page `Review topology`
- workbench nested-share warning `Explain overlap`
- workbench local-derivation or claim page `Topology changes if accepted`
- CLI `topology review --subject ... --intent ... --plan`
- CLI `topology show <topology_case_id> --view review`
- CLI `bind repair --plan` when the real action changes graph relation rather than only restoring the same path

But these must all converge on the same public topology model.
The operator should never have to wonder whether one surface is merely picking a path while another is actually explaining double indexing, propagation shape, and root-boundary fallout.

## Fixed review order

Every non-trivial topology review should render the same sections in the same order:

1. **Trigger and graph subjects**
2. **Containment and propagation shape**
3. **Path and root-boundary effects**
4. **Admissible topology actions**
5. **Receipt promise**

### 1) Trigger and graph subjects

This section should show:

- which share, mount, candidate path, or existing graph subjects are involved
- whether the requested action is nest, flatten, rebind, move-across-boundary, or reject-overlap
- which existing graph relation currently holds and what relation is being requested
- whether the action was initiated directly, by repair workflow, by derivation workflow, or by policy-root warning

The operator must be able to answer: **what objects are actually being related or moved here, and what graph change is being requested?**

### 2) Containment and propagation shape

This section should show:

- whether the relation is disjoint, child, parent, overlap, self-edge, or ambiguous
- whether propagation would be independent, piggyback through a parent, double-indexed, re-download-likely after move, or blocked
- whether Selective Sync, placeholder posture, or other materialization behavior becomes disabled or constrained under this relation
- whether indexing cost, replay shape, or seed expectations change enough to matter operationally

The operator must be able to answer: **how will changes actually flow through this graph if I accept it?**

### 3) Path and root-boundary effects

This section should show:

- whether the path transition is a local-only rename, reviewed rebind, disconnect/reconnect-like continuity break, or blocked move
- whether the path remains inside allowed root, needs reviewed root expansion, or violates current root policy
- whether any surface loses expressive power because the requested topology exists only in config or only with reduced UI support
- whether the right next step is continue here, choose another path, expand root policy, or abandon the requested topology

The operator must be able to answer: **is this path transition really safe and supported, on this root policy and on this channel?**

### 4) Admissible topology actions

This section should show:

- accept reviewed nested topology
- flatten by keeping only parent or only child graph subject
- rebind outside the conflicting parent graph
- reject overlap or self-edge
- review root expansion separately before proceeding
- divert into local-derivation, bind repair, or filesystem-policy review when ordinary topology acceptance is not the honest frame

The operator must be able to answer: **what safe graph actions are actually available here?**

### 5) Receipt promise

This section should show:

- which topology receipt will exist after apply or reject
- what it will later prove about accepted graph relation, propagation shape, path/root-boundary findings, and any remaining follow-up review
- whether the receipt remains provisional because some related subject was offline or root policy was only partially changed
- what later audit survives after the topology is already active

The operator must be able to answer: **what later evidence will prove what graph relation I accepted, how it was expected to propagate, and what still needed follow-up?**

## Action hierarchy inside topology review

The primary action should be the safest meaningful next step.
Examples:

- candidate child path sits inside an existing broader share → `Review nested topology`, not `Add share`
- move would escape allowed root → `Review root expansion`, not `Reconnect here`
- overlap is ambiguous and propagation cannot be stated honestly → `Reject overlap`, not `Apply anyway`
- a safe disjoint sibling path is available → `Rebind outside parent graph`, not `Accept double-indexed child`

Convenience labels such as `Add folder`, `Move`, or `Reconnect` should be visually separate and usually not primary.

## What the surface must never imply

The topology surface must never imply that these are the same thing:

- child-inside-parent share vs ordinary disjoint second share
- same-host derivation vs separate replicated graph subject
- local-only rename vs reviewed rebind across graph boundaries
- allowed-root move vs root-boundary escape
- independent propagation vs piggyback-via-parent delivery
- nested acceptance vs loop-safe flattening

If the product compresses those differences, it has recreated the folklore it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed topology grammar must survive across those channels.
It is not acceptable for one richer surface to show graph relation, propagation shape, and root-boundary truth while Linux/WebUI falls back to a path picker plus generic `Apply` or `Reconnect` button.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync topology show <topology_case_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a child path is truly separate, whether a move becomes a reviewed rebind, whether propagation piggybacks through a parent, or whether the requested path actually violates current allowed-root policy.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed topology grammar is how the archive avoids rebuilding a system where nested-share caveats, local loop warnings, move limitations, allowed-root policy, and config-surface restrictions are all individually documented, yet the full meaning of “what graph did I just create, how will it propagate, and is this path transition actually safe?” still depends on which FAQ, warning, or support article the operator happened to notice first.
""")

