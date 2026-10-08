from pathlib import Path
import shutil
import textwrap

src = Path('/mnt/data/work_rev0062')
dst = Path('/mnt/data/work_rev0063')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

def rw(rel):
    return dst / rel

def replace(path, old, new):
    p = rw(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f'Pattern not found in {path}: {old[:80]!r}')
    p.write_text(text.replace(old, new, 1))

# 1) New spec doc
new_doc = textwrap.dedent('''\
# Writer-contention, lock pressure, and quiescence review spec

The archive already has transfer policy, activity phases, filesystem fidelity, destructive replay review, and topology review.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show when files are actively contested by another writer, burst-save delay is being used as collision control, or mixed SMB/NAS access means sync progress is no longer just “network activity” but a live coordination problem?

This is the external-writer companion to `53-transfer-policy-and-throughput-budget-spec.md`, the local-quiesce companion to `45-activity-phase-and-scheduling-spec.md`, the notification-reality companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Locked files` says the status column can show locked files and open their paths, but Sync cannot tell which application actually holds the lock and the operator is pushed toward Process Monitor plus restart ritual.
`Setting Delay Time For Syncing` says Office/AutoDesk/Adobe-style save contention is handled by editing a `FileDelayConfig` JSON file inside the storage folder and restarting Sync, with a default 10-second delay.
`Power user preferences` adds `recheck_locked_files_interval` and warns that too-frequent checking of many locked files may drive high CPU usage.
`Sync and SMB file shares` says SMB-backed paths may lose notifications and fall back to full rescans unless both sides support SMB 3.0, that locked files can persist after broken network or app failure, and that mixed direct access outside Samba can damage files or roll changes back.

The lesson is not that writer contention is rare.
The lesson is that a useful product can still compress too many coordination decisions into one status badge, one hidden delay file, one retry interval, and one separate SMB warning page.

AnonSync should therefore make these differences explicit before apply or continue:

- local app lock versus network-client lock versus only suspected contention
- explicit temporary delay versus upload hold versus bidirectional freeze versus reader-only guard
- continuous notifications versus periodic rescans while contested writes are still occurring
- harmless burst-save delay versus real overwrite / rollback / corruption risk
- ordinary transfer slowdown versus contention that should divert into filesystem-fidelity or topology review
- same-path coordination issue versus whole-subtree or whole-share quiesce question

## Core rule

A non-trivial writer-contention situation should always compile to a reviewed contention surface.
That includes at least:

- any path where another writer is known or strongly suspected to be holding files open
- any scope where a delay profile, retry loop, rescan fallback, or quiesce action is being used to keep sync and local writers from colliding
- any mount where current notification posture, network-share posture, or mixed-access warning changes how trustworthy freshness and replay safety are
- any action whose safest next step may actually be upload hold, bidirectional freeze, reader-only guard, fidelity escalation, or topology change rather than ordinary transfer continuation
- any incident where the product would otherwise hide the real coordination meaning behind `locked`, `delayed`, `syncing slowly`, or `just restart`

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `Retry`, `Resume syncing`, `Wait`, or `Increase delay` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench status card `Review contention`
- workbench path warning `Why is this delayed?`
- workbench SMB/fidelity warning `Review mixed-writer risk`
- CLI `contention review --share ... --path ... --plan`
- CLI `contention show <contention_case_id> --view review`
- CLI `activity quiesce --plan` when the real action is coordinating with another writer, not merely changing bandwidth posture

But these must all converge on the same public contention model.
The operator should never have to wonder whether one surface is merely showing a stalled transfer while another is actually explaining lock reality, notification weakness, and propagation risk.

## Fixed review order

Every non-trivial contention review should render the same sections in the same order:

1. **Trigger and contested scope**
2. **Writer and lock reality**
3. **Notification and filesystem posture**
4. **Quiesce and propagation effects**
5. **Admissible actions**
6. **Receipt promise**

### 1) Trigger and contested scope

This section should show:

- which share, mount, path set, or subtree is being reviewed
- whether the trigger was locked files, delay-profile hit, mixed SMB access, rescan-only freshness, or manual quiesce intent
- whether the scope is one file, one directory, one subtree, or an entire mount/share
- whether the review was initiated by a warning, by policy, by operator action, or by a higher-signal destructive-replay / fidelity concern

The operator must be able to answer: **what is actually contested here, and why did the product stop to review it?**

### 2) Writer and lock reality

This section should show:

- what evidence exists for another writer, including likely local app, likely network client, service-side writer, mixed sources, or unknown holder
- whether files are presently locked, were only recently locked, or are only delay-profile candidates with no confirmed lock
- whether the product can name exact paths, only a subtree, or only a risk class
- whether the lock or writer evidence is strong enough to trust or weak enough that the real issue may be stale handles, broken notifications, or filesystem drift instead

The operator must be able to answer: **who or what appears to be writing here, and how certain is that?**

### 3) Notification and filesystem posture

This section should show:

- whether the mount still has continuous notifications, mixed coverage, or only periodic rescans
- whether the path is local-native, network-reviewed, warning-tier, or already degraded enough to block honest continuation
- whether mixed direct-access risk, broken locks, or transport-induced stale handles are part of the current finding
- whether this contention should stay in contention review or really be escalated into filesystem-fidelity or topology review

The operator must be able to answer: **how trustworthy is freshness here while another writer may still be active?**

### 4) Quiesce and propagation effects

This section should show:

- what protection is active now: delay profile, upload hold, delete-propagation hold, bidirectional freeze, reader-only guard, or none
- what that protection actually changes for uploads, downloads, delete propagation, and local evidence retention
- whether current risk is merely delayed propagation or something stronger such as overwrite, rollback, or corruption risk
- whether the present posture expires automatically, waits for another writer to clear, or depends on explicit operator release

The operator must be able to answer: **what is paused or delayed right now, and what danger is it preventing?**

### 5) Admissible actions

This section should show:

- keep the current delay profile and wait
- hold uploads while preserving local evidence
- freeze bidirectional propagation until the writer clears
- narrow the subject to reader-only / observe-only posture
- escalate into filesystem-fidelity, topology, or destructive-replay review
- reject continuation because current freshness or mixed-access posture is not honest enough

The operator must be able to answer: **what safe coordination actions are actually available here?**

### 6) Receipt promise

This section should show:

- which contention receipt will exist after apply or release
- what it will later prove about trigger scope, writer evidence, filesystem/notification posture, applied quiesce effect, and any remaining follow-up
- whether the receipt remains provisional because the writer is still active, evidence was weak, or the mount stayed on warning-tier storage
- what later audit survives after the visible warning or delay clears

The operator must be able to answer: **what later evidence will prove how the product coordinated this contested path and what still remained unresolved?**

## Action hierarchy inside contention review

The primary action should be the safest meaningful next step.
Examples:

- burst-save pressure on a local-native Office document → `Keep delay profile and monitor`, not `Resume syncing`
- confirmed SMB mixed-access risk with weak notifications → `Freeze bidirectional propagation`, not `Retry now`
- lock evidence is weak but filesystem posture drifted to network-reviewed → `Review filesystem fidelity`, not `Just wait`
- one writer should keep local evidence but stop publishing new edits → `Hold uploads and preserve local writes`, not `Pause everything`

Convenience labels such as `Retry`, `Resume`, or `Increase delay` should be visually separate and usually not primary.

## What the surface must never imply

The contention surface must never imply that these are the same thing:

- transient burst-save delay versus confirmed lock contention
- local-app coordination versus mixed SMB writer risk
- upload hold versus full bidirectional freeze
- delayed propagation versus overwrite / rollback / corruption risk
- stale notifications versus active writer evidence
- ordinary transfer throttling versus explicit contention coordination

If the product compresses those differences, it has recreated the folklore it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed contention grammar must survive across those channels.
It is not acceptable for one richer surface to show writer evidence, notification weakness, and quiesce truth while Linux/WebUI falls back to a `locked files` badge plus a generic `retry later` action.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync contention show <contention_case_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether the system is seeing transient burst-save delay, confirmed lock pressure, mixed SMB access risk, rescan-only freshness, or a reason to freeze propagation until another writer clears.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed contention grammar is how the archive avoids rebuilding a system where locked-file badges, hidden delay profiles, retry intervals, SMB warnings, and manual restart folklore are all individually documented, yet the full meaning of “who is writing here, what is currently held back, what danger is being prevented, and when may safe propagation resume?” still depends on which warning, storage path, or support article the operator happened to notice first.
''')
rw('docs/76-writer-contention-and-quiescence-review-spec.md').write_text(new_doc)

# README updates
readme = rw('README.md').read_text()
readme = readme.replace('- Revision: `rev0062`', '- Revision: `rev0063`')
readme = readme.replace('- Timestamp: `2026.03.17.15.43` (America/New_York)', '- Timestamp: `2026.03.17.16.12` (America/New_York)')
readme = readme.replace('- Codename: `graphproofcontainmentharbor`', '- Codename: `contentionproofquiesceledger`')
old_changed = textwrap.dedent('''\
## What changed in this revision

This revision continues directly from `rev0061` and does seven things:

1. Re-checks **Resilio Sync** again with extra emphasis on graph and path topology: separately shared nested folders require read-write-or-owner posture, disable Selective Sync, double-index the child, and still propagate child edits onward through the parent share, while same-host local shares warn against parent/subdirectory loops and move/rename guidance still falls back to reconnect-style path continuity limits.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let “this share is inside that share”, “move it over there”, or “fan it out locally” blur together graph overlap, propagation shape, root-boundary policy, and continuity risk.
3. Adds a dedicated **overlap, containment, and graph-topology review interface spec** so the archive now says what a real pre-apply topology surface must literally show before consent.
4. Extends the **interface and daemon/API contract** so non-trivial nested, overlapping, loop-prone, or root-boundary-sensitive share/path actions can expose one stable review model instead of scattered FAQ caveats, path pickers, reconnect rituals, and config-mode restrictions.
5. Extends the **workbench/interface pattern language** with sharper topology-review verbs and fixed review sections for graph subjects, containment/propagation shape, path/root-boundary effects, admissible actions, and receipts.
6. Adds additional **canonical interface flows** for reviewed topology decisions and cross-surface parity instead of leaving nested-share and cross-share move meaning to memory.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep topology honesty tied to surface parity, graph proof, and explicit containment boundaries.
''')
new_changed = textwrap.dedent('''\
## What changed in this revision

This revision continues directly from `rev0062` and does seven things:

1. Re-checks **Resilio Sync** again with extra emphasis on writer contention: locked-file status still cannot name the locking application, save-burst coordination still lives in a storage-folder `FileDelayConfig` JSON plus restart ritual, retry behavior is still tuned through power-user preferences, and SMB/NAS mixed-access caveats still live in a separate troubleshooting article.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let “locked”, “delayed”, “rescan-only”, and “mixed SMB access” blur together ordinary slowdown, local-writer coordination, notification weakness, and real overwrite / rollback / corruption risk.
3. Adds a dedicated **writer-contention, lock-pressure, and quiescence review interface spec** so the archive now says what a real pre-apply contention surface must literally show before an operator keeps waiting, delays propagation, freezes sync, or escalates to stronger review.
4. Extends the **interface and daemon/API contract** so non-trivial lock pressure, burst-save delay, mixed external-writer risk, and quiesce actions can expose one stable review model instead of scattered status badges, hidden JSON knobs, retry intervals, and SMB caveats.
5. Extends the **workbench/interface pattern language** with sharper contention-review verbs and fixed review sections for contested scope, writer reality, notification/filesystem posture, quiesce effects, admissible actions, and receipts.
6. Adds additional **canonical interface flows** for reviewed contention decisions and cross-surface parity instead of leaving lock pressure and quiesce meaning to memory.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, **sources**, and **reading order** so future revisions keep contention honesty tied to surface parity, explicit quiesce truth, and durable coordination receipts.
''')
if old_changed not in readme:
    raise SystemExit('README changed block not found')
readme = readme.replace(old_changed, new_changed)
readme = readme.replace(
    '- a fixed topology-review pane that renders graph subjects, containment/propagation shape, path/root-boundary effects, admissible topology actions, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n',
    '- a fixed topology-review pane that renders graph subjects, containment/propagation shape, path/root-boundary effects, admissible topology actions, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n- a fixed contention-review pane that renders contested scope, writer/lock reality, notification/filesystem posture, quiesce effects, admissible actions, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n'
)
readme = readme.replace(
    '- access-change behavior that still depends on Standard-vs-Advanced folder class, owner folklore, disconnect semantics, local-share re-share ritual, or config-mode surface limits instead of one reviewed authority-mutation contract\n- control-plane access that still depends on bind-address folklore, browser-session cookies, config-file passwords, or trust-warning workarounds instead of one durable public endpoint/session contract\n',
    '- access-change behavior that still depends on Standard-vs-Advanced folder class, owner folklore, disconnect semantics, local-share re-share ritual, or config-mode surface limits instead of one reviewed authority-mutation contract\n- contention handling that still depends on locked-file badges, hidden `FileDelayConfig` JSON, retry-interval power-user knobs, and separate SMB caveats instead of one reviewed coordination/quiescence contract\n- control-plane access that still depends on bind-address folklore, browser-session cookies, config-file passwords, or trust-warning workarounds instead of one durable public endpoint/session contract\n'
)
readme = readme.replace(
    '- `docs/75-overlap-containment-and-graph-topology-review-spec.md` — fixed topology-review pane anatomy for graph subjects, containment/propagation shape, path/root-boundary effects, safe topology actions, and topology receipts\n',
    '- `docs/75-overlap-containment-and-graph-topology-review-spec.md` — fixed topology-review pane anatomy for graph subjects, containment/propagation shape, path/root-boundary effects, safe topology actions, and topology receipts\n- `docs/76-writer-contention-and-quiescence-review-spec.md` — fixed contention-review pane anatomy for contested scope, writer/lock reality, notification/filesystem posture, quiesce actions, and contention receipts\n'
)
rw('README.md').write_text(readme)

# Status updates
status = rw('docs/00-status.md').read_text()
status = status.replace('This revision is an in-place continuation of `rev0061`', 'This revision is an in-place continuation of `rev0062`')
status = status.replace(
    '- make sure the archive has a better reason not to clone nested-share and overlap behavior that still hides graph topology, child propagation, double indexing, root-boundary policy, move/reconnect limits, and loop risk behind separate FAQs, local-share warnings, and config-mode path restrictions\n',
    '- make sure the archive has a better reason not to clone nested-share and overlap behavior that still hides graph topology, child propagation, double indexing, root-boundary policy, move/reconnect limits, and loop risk behind separate FAQs, local-share warnings, and config-mode path restrictions\n- make sure the archive has a better reason not to clone writer-contention handling that still hides coordination meaning behind locked-file badges, storage-folder delay JSON, retry-interval tuning, and separate SMB/NAS caveats\n'
)
old_out = textwrap.dedent('''\
The archive now contains:

- a deeper Resilio-derived warning that current nested-share and overlap behavior still depends on separate-share caveats, local-share loop warnings, move/reconnect limitations, and config-mode root restrictions
- a dedicated **overlap, containment, and graph-topology review interface spec** that says what a real reviewed topology surface must literally show before nesting, overlapping, moving, or rebinding graph-related subjects
- stronger CLI/API requirements so non-trivial topology work can expose one stable review model instead of falling back to folder creation, reconnect prompts, or config-only path restrictions
- stronger workbench and pattern-language rules for reviewed topology so rich and textual surfaces keep the same graph-subject, containment-shape, root-boundary, action, and receipt truth
- additional canonical flows for rendering the same topology review in workbench and CLI without semantic drift
- roadmap, ADR, status, and open-question updates so future revisions keep topology honesty tied to surface parity and explicit graph proof
''')
new_out = textwrap.dedent('''\
The archive now contains:

- a deeper Resilio-derived warning that current writer-contention handling still depends on locked-file status badges, hidden `FileDelayConfig` JSON, retry-interval tuning, and separate SMB/NAS caveats
- a dedicated **writer-contention, lock-pressure, and quiescence review interface spec** that says what a real reviewed coordination surface must literally show before waiting, delaying, freezing, or escalating contested paths
- stronger CLI/API requirements so non-trivial lock pressure, burst-save delay, mixed external-writer risk, and quiesce actions can expose one stable review model instead of falling back to badges, retries, or hidden config files
- stronger workbench and pattern-language rules for reviewed contention so rich and textual surfaces keep the same contested-scope, writer-reality, notification-posture, quiesce-effect, action, and receipt truth
- additional canonical flows for rendering the same contention review in workbench and CLI without semantic drift
- roadmap, ADR, status, open-question, and source updates so future revisions keep contention honesty tied to surface parity and explicit quiesce proof
''')
status = status.replace(old_out, new_out)
status = status.replace(
    '`rev0062` applies the same discipline to graph overlap and containment topology:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define bindings, derivations, grants, projection, and continuity in the abstract, yet still leave the actual “is this share nested inside that share, does it double-index, who propagates to whom, can I move it safely, and did I just escape the allowed root?” surface vague enough that GUI, WebUI, TUI, and CLI might drift back into different products.\n\nThat changes the archive in six specific ways:\n\n- non-trivial nested, overlapping, loop-prone, and root-boundary-sensitive topology decisions are now specified as a fixed review pane rather than only a mix of FAQs, warnings, and reconnect/path folklore\n- graph subjects, containment and propagation shape, path/root-boundary effects, admissible topology actions, and receipt promise now have a stable render order across channels\n- nested-share creation, same-host fanout, and cross-share move/rebind work can project one review model instead of falling back to generic `add folder`, `move`, or `connect in new location` ritual\n- the daemon/API model is now held to a clearer requirement that topology changes be previewable as graph-changing work rather than ambient convenience\n- the Resilio comparison now lands a sharper non-clone argument: nested folders, child propagation, double indexing, move limits, and config-mode root restrictions still hide too much meaning behind separate articles and surface loss\n- future interface work now has a narrower quality bar for reviewed topology parity on Linux-first deployments\n',
    '`rev0063` applies the same discipline to writer contention and quiescence:\n\n> a serious Linux-first workbench still is not specified tightly enough if the archive can define transfer budgets, filesystem fidelity, destructive replay, and activity phases in the abstract, yet still leave the actual “who is writing this file, what is currently delayed or frozen, how trustworthy are notifications on this mount, and when may bidirectional sync safely resume?” surface vague enough that GUI, WebUI, TUI, and CLI might drift back into different products.\n\nThat changes the archive in six specific ways:\n\n- non-trivial lock pressure, burst-save delay, mixed SMB/NAS writer risk, and explicit quiesce actions are now specified as a fixed review pane rather than only a mix of status badges, hidden delay files, and troubleshooting lore\n- contested scope, writer/lock reality, notification/filesystem posture, quiesce effects, admissible actions, and receipt promise now have a stable render order across channels\n- transfer slowdown, activity override, and filesystem warning work can project one review model instead of falling back to generic `Retry`, `Resume syncing`, or `Increase delay` ritual\n- the daemon/API model is now held to a clearer requirement that contention changes be previewable as coordination work rather than ambient background retries\n- the Resilio comparison now lands a sharper non-clone argument: locked files, hidden delay config, retry tuning, and SMB caveats still hide too much meaning behind separate articles and hidden storage paths\n- future interface work now has a narrower quality bar for reviewed contention parity on Linux-first deployments\n'
)
status = status.replace(
    '- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path\n',
    '- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path\n- when writer contention, burst-save delay, or mixed external-writer risk should always force full contention review instead of a safely compressed path\n'
)
rw('docs/00-status.md').write_text(status)

# Evaluation updates
section_insert = textwrap.dedent('''\
### 16u) Writer contention and quiescence still depend too much on status badges, hidden delay files, and separate SMB caveats

Resilio's current docs make one more seam unusually explicit.

`Locked files` says the status column can show locked files and open their paths, but Sync cannot tell which application actually holds the lock and the operator is pushed toward Process Monitor plus restart ritual.
`Setting Delay Time For Syncing` says Office/AutoDesk/Adobe-style save contention is handled by editing a `FileDelayConfig` JSON file in the storage folder and restarting Sync, with a default delay of 10 seconds.
`Power user preferences` adds `recheck_locked_files_interval` and warns that too-frequent rechecks of many locked files may cause high CPU usage.
`Sync and SMB file shares` says SMB-backed folders may lose immediate notifications and fall back to full rescans unless both sides support SMB 3.0, that broken locks can persist after network or app failure, and that mixed direct access outside Samba can damage files or roll changes back.

That is not one trustworthy contention model.
It is a mixture of lock-status badges, hidden delay JSON, retry tuning, notification downgrade, and mixed-writer caveats.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a path is merely waiting behind an intentional delay profile or is actually blocked by another writer
- whether the present protection is delay-only, retry-only, upload hold, or a stronger freeze that should stop dangerous propagation
- whether freshness is still trustworthy or only periodic-rescan best effort while contested writes continue
- whether the current risk is ordinary slowdown, overwrite/rollback risk, or genuine corruption risk on warning-tier storage
- whether the safest next step is wait, preserve local writes, freeze propagation, or move the workload off a mixed SMB/NAS topology entirely

AnonSync should not clone that shape.
A serious control surface should instead publish one writer-contention and quiescence review model with:

- one explicit review grammar for trigger/scope, writer+lock reality, notification+filesystem posture, quiesce+propagation effects, admissible actions, and receipt promise
- explicit separation between transient burst-save delay, confirmed lock pressure, mixed external-writer risk, and degraded-notification uncertainty
- explicit quiesce truth before apply instead of after-the-fact retry, restart, or hidden-delay folklore
- explicit escalation points into filesystem-fidelity, topology, or destructive-replay review when contention is only a symptom of a larger risk
- explicit receipts proving which contention was reviewed, what coordination action was chosen, what propagation was held back, and what follow-up still remained

### Requirement 58 — writer contention and quiescence must share one reviewed coordination contract

If the operator still has to combine locked-file badges, hidden delay JSON, retry-interval tuning, and SMB mixed-access caveats to answer “who is writing here, what is currently delayed or frozen, and when may safe propagation resume?”, the product has not actually exposed its contention contract.

AnonSync should instead publish one public contention-review model with explicit contested scope, explicit writer and lock reality, explicit notification/filesystem posture, explicit quiesce and propagation effects, explicit admissible actions, and durable contention receipts that preserve the difference between harmless burst-save delay, guarded upload hold, full bidirectional freeze, and escalation because current freshness or mixed-access posture is not honest enough.

''')
replace('docs/10-resilio-sync-evaluation.md', '## Where Resilio is still probably the better choice\n', section_insert + '## Where Resilio is still probably the better choice\n')
replace('docs/10-resilio-sync-evaluation.md', 'and explicit topology-review contracts that keep graph overlap, containment, propagation shape, path/root-boundary consequences, and safe rebind versus blocked-loop decisions visible instead of leaving nested, overlapping, or moved shares to separate FAQs and reconnect folklore.\n', 'and explicit topology-review contracts that keep graph overlap, containment, propagation shape, path/root-boundary consequences, and safe rebind versus blocked-loop decisions visible instead of leaving nested, overlapping, or moved shares to separate FAQs and reconnect folklore, and explicit contention/quiescence contracts that keep contested scope, writer reality, notification weakness, quiesce posture, and safe resume conditions visible instead of leaving lock pressure and mixed external-writer risk to badges, hidden delay files, retry knobs, and SMB troubleshooting lore.\n')

# Interface spec additions
iface = rw('docs/30-interface-spec.md').read_text()
insert_after = textwrap.dedent('''\
### Topology review case

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
''')
new_block = insert_after + textwrap.dedent('''\

### Contention review case

A durable plan-bearing record for coordinating contested paths where another writer, degraded notifications, or mixed access means sync progress is no longer just “transfer activity.”
This exists so operators can inspect the difference between “retry later” and “a reviewed contention situation with specific quiesce, propagation, and freshness consequences.”

Fields:

- `contention_case_id`
- `primary_subject_ref`
- `path_refs[]`
- `trigger_kind` (`locked-files`, `delay-profile-hit`, `external-writer-suspected`, `notification-loss-with-write-pressure`, `smb-mixed-access`, `manual-quiesce`, `unknown`)
- `writer_posture` (`none-confirmed`, `likely-local-app`, `likely-network-client`, `likely-service-writer`, `mixed`, `unknown`)
- `lock_scope` (`none`, `path-set`, `subtree`, `share-wide`, `unknown`)
- `notification_posture` (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- `filesystem_risk_posture` (`local-native`, `network-reviewed`, `warning-tier`, `blocked`, `unknown`)
- `quiesce_posture` (`none`, `delay-profile-active`, `upload-hold`, `bidirectional-freeze`, `maintenance-freeze`, `reader-only-guard`, `blocked`)
- `propagation_risk` (`none`, `delayed-only`, `overwrite-risk`, `rollback-risk`, `corruption-risk`, `blocked`)
- `delay_profile_ref` nullable
- `status` (`draft`, `preflighted`, `planned`, `applied`, `released`, `rejected`, `expired`)
- `review_model` nullable
- `evidence_refs[]`
- `provenance_ref` nullable

### Contention receipt

A durable explanation record proving what coordination action was applied to a contested path and what propagation it intentionally held back.

Fields:

- `contention_receipt_id`
- `contention_case_ref`
- `action_kind` (`delay-profile-applied`, `upload-held`, `bidirectional-frozen`, `reader-guard-applied`, `escalated-review`, `released`, `cancelled`)
- `scope_ref`
- `effective_quiesce_posture`
- `propagation_expectation` (`local-writes-preserved`, `remote-writes-held`, `delete-propagation-held`, `rescan-required`, `review-pending`)
- `expires_at` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `released`, `cancelled`, `blocked`)
- `provenance_ref` nullable
''')
if insert_after not in iface:
    raise SystemExit('Topology case block not found in interface spec')
iface = iface.replace(insert_after, new_block, 1)
rw('docs/30-interface-spec.md').write_text(iface)

# Daemon API section
api_insert = textwrap.dedent('''\
## Contention / quiesce resources

These resources keep locked files, burst-save delay, mixed external-writer risk, and explicit quiesce actions visible as one coordination model.
They answer what scope is contested, what writer evidence exists, whether notifications are trustworthy enough, and what propagation is being delayed, held, or frozen.

```text
GET    /v1/contention-cases
POST   /v1/contention-cases
GET    /v1/contention-cases/{contention_case_id}
POST   /v1/contention-cases/{contention_case_id}/apply
POST   /v1/contention-cases/{contention_case_id}/release
GET    /v1/contention-receipts/{contention_receipt_id}
```

`POST /v1/contention-cases` should accept one or more share/mount/path refs plus an explicit intent such as `inspect`, `delay-writes`, `quiesce-upload`, `freeze-bidirectional`, `narrow-reader`, or `escalate-fidelity`.
The resulting case or referenced plan should always include:

- trigger facts and contested-scope summary
- writer and lock evidence with confidence posture
- notification and filesystem-posture findings
- quiesce and propagation-effect summary
- admissible next actions and any escalation path into fidelity, topology, or destructive-replay review
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `trigger_and_contested_scope`
- `writer_and_lock_reality`
- `notification_and_filesystem_posture`
- `quiesce_and_propagation_effects`
- `admissible_actions`
- `receipt_promise`

Transfer, activity, fidelity, and topology endpoints may still exist for narrower domain actions, but when the operator-visible outcome is coordinating around another writer or mixed-access uncertainty, those endpoints should reference or emit the same contention-case / contention-receipt model.

''')
replace('docs/31-daemon-api-spec.md', '## Topology-review resources\n', api_insert + '## Topology-review resources\n')

# Flows append
flows_append = textwrap.dedent('''\

## Flow 109 — review writer contention on a mixed-access path before silent overwrite or rollback folklore takes over

Problem: a Linux operator sees a busy project subtree alternately appear as delayed, rescanned, and locked while a local editor and SMB users both touch the same files. The product must explain coordination truth directly instead of asking the operator to infer it from badges and retries.

Goal:

- prove that lock pressure, delay profiles, notification weakness, and mixed-writer risk can render as one reviewed contention case
- make the safe next action read like coordination policy rather than troubleshooting lore

Workbench expectations:

- clicking `Review contention` from a transfer delay badge, filesystem warning, or workbench report opens one contention review page
- the page renders sections in this order:
  1. trigger and contested scope
  2. writer and lock reality
  3. notification and filesystem posture
  4. quiesce and propagation effects
  5. admissible actions
  6. receipt promise
- the primary action inherits the reviewed intent, for example `Freeze bidirectional propagation` or `Hold uploads and preserve local writes`, instead of generic `Retry` or `Resume syncing`

CLI expectations:

```text
$ anonsync contention show cnt_01J... --view review
Contention review
-----------------
1. Trigger and contested scope
   Trigger: smb-mixed-access
   Scope: share design-lab / subtree /srv/design/current

2. Writer and lock reality
   Writer posture: mixed
   Locked paths: 12 confirmed, 4 recently cleared
   Evidence confidence: guarded

3. Notification and filesystem posture
   Notifications: periodic-rescan only
   Filesystem posture: network-reviewed
   Mixed-access risk: direct local writes outside Samba may roll back remote edits

4. Quiesce and propagation effects
   Current posture: upload-hold
   Delete propagation: held
   Propagation risk if released now: rollback-risk

5. Admissible actions
   - Freeze bidirectional propagation
   - Keep upload hold and re-evaluate after quiet window
   - Escalate into filesystem fidelity review

6. Receipt promise
   Receipt will prove trigger scope, writer evidence, notification posture, applied quiesce effect, and any required follow-up.
```

Expected operator answers from CLI alone:

- whether the contested state is just burst-save delay or a stronger mixed-writer problem
- whether freshness is continuous or rescan-only while the conflict exists
- what propagation is actively being held back right now
- which safer action exists before the operator lets bidirectional sync continue again

## Flow 110 — render the same contention review in CLI and workbench without semantic drift

Problem: a WebUI operator freezes propagation for a contested Office-heavy subtree; later a headless operator checks the same case over SSH. Both surfaces must show the same writer, notification, quiesce, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed contention case
- make contested scope, writer reality, notification posture, and quiesce effects read like one product

Cross-surface success criteria:

- both surfaces answer the same question: **who appears to be writing here, what is currently delayed or frozen, how trustworthy is freshness, and when may safe propagation resume?**
- neither surface falls back to generic `Retry`, `Resume syncing`, or `Increase delay` language when the real decision is a reviewed coordination action
''')
rw('docs/32-interface-flows.md').write_text(rw('docs/32-interface-flows.md').read_text() + flows_append)

# Workbench additions
wb = rw('docs/38-operator-workbench-interface-spec.md').read_text()
wb_insert_after = textwrap.dedent('''\
The page should make one difference visually unavoidable:

- **Apply this reviewed authority boundary**
- **Narrow or freeze it differently**
- **Divert to stewardship, cutover, or stronger review**

Those three lines may all start from “change this member's access”, but the product should never force operators to assume they are the same action.
''')
wb_new = wb_insert_after + textwrap.dedent('''\

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
''')
if wb_insert_after not in wb:
    raise SystemExit('Workbench insertion point not found')
wb = wb.replace(wb_insert_after, wb_new, 1)
wb = wb.replace(
    '18. Every non-trivial authority mutation must keep current-authority/boundary-delta/dependent-fallout/substrate-effect/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.\n',
    '18. Every non-trivial authority mutation must keep current-authority/boundary-delta/dependent-fallout/substrate-effect/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.\n19. Every non-trivial writer-contention case must keep contested-scope/writer-reality/notification-posture/quiesce-effects/receipt truth visible in a fixed order across GUI, WebUI, TUI, and CLI-backed surfaces.\n'
)
rw('docs/38-operator-workbench-interface-spec.md').write_text(wb)

# Pattern language additions
pl = rw('docs/39-interface-pattern-language.md').read_text()
pattern_insert = textwrap.dedent('''\
## Pattern 22g — contention and quiescence review need a fixed grammar

Every non-trivial contention review should render the same sections in the same order:

1. trigger and contested scope
2. writer and lock reality
3. notification and filesystem posture
4. quiesce and propagation effects
5. admissible actions
6. receipt promise

This matters because a product can define good transfer, activity, and fidelity objects on paper and still regress in practice if one client offers a rich coordination sheet while another falls back to a locked-files badge, a retry timer, or `increase delay` folklore.

''')
replace('docs/39-interface-pattern-language.md', '## Pattern 23 — dangerous verbs should inherit the reviewed intent label\n', pattern_insert + '## Pattern 23 — dangerous verbs should inherit the reviewed intent label\n')
replace('docs/39-interface-pattern-language.md', 'A reviewed authority-mutation case should not end with a generic `Apply` or `Disconnect` button if the real action is `Grant write without delegation`, `Narrow to read-only and preserve bytes`, or `Strip delegation but keep read access`.\n', 'A reviewed authority-mutation case should not end with a generic `Apply` or `Disconnect` button if the real action is `Grant write without delegation`, `Narrow to read-only and preserve bytes`, or `Strip delegation but keep read access`.\nA reviewed contention case should not end with a generic `Retry`, `Resume syncing`, or `Increase delay` button if the real action is `Hold uploads and preserve local writes`, `Freeze bidirectional propagation`, or `Escalate to filesystem-fidelity review`.\n')

# ADR append
adr_append = textwrap.dedent('''\

## ADR-076 — Writer contention needs one reviewed coordination contract, not badges and hidden delay lore

**Decision:** Non-trivial lock pressure, burst-save delay, mixed external-writer risk, and explicit quiesce actions should compile to one reviewed contention model rather than living as separate status badges, hidden delay files, retry knobs, and SMB caveats.

**Why:** Current Resilio docs still spread coordination meaning across `Locked files`, storage-folder `FileDelayConfig`, `recheck_locked_files_interval`, and SMB warning pages about notification loss, broken locks, and mixed access outside Samba. AnonSync should keep contested scope, writer reality, filesystem posture, quiesce effect, and safe resume conditions visible in one place.

**Consequences:**
- contention work gains a stable review grammar and durable contention receipts
- workbench and CLI both need explicit contested-scope, writer-reality, notification-posture, and quiesce-effect sections
- delay profiles, upload holds, bidirectional freezes, and reader-only guards remain visibly distinct public actions
- degraded notification or mixed-access evidence can escalate visibly into fidelity, topology, or destructive-replay review instead of hiding behind retries
''')
rw('docs/40-architecture-decisions.md').write_text(rw('docs/40-architecture-decisions.md').read_text() + adr_append)

# Roadmap additions
road = rw('docs/50-roadmap.md').read_text()
road = road.replace(
    '- review-model projection for overlap, containment, and graph topology so rich and textual clients render the same graph-subject/propagation/root-boundary sections\n',
    '- review-model projection for overlap, containment, and graph topology so rich and textual clients render the same graph-subject/propagation/root-boundary sections\n- review-model projection for writer contention and quiescence so rich and textual clients render the same contested-scope/writer-reality/notification-posture/quiesce-effect sections\n'
)
road = road.replace(
    '- operators can preview the same same-host-derivation truth in workbench and CLI without semantic drift\n',
    '- operators can preview the same same-host-derivation truth in workbench and CLI without semantic drift\n- operators can preview the same contention/quiesce truth in workbench and CLI without semantic drift\n'
)
road = road.replace(
    '- operators can preview the same authority-mutation truth in workbench and CLI without semantic drift\n',
    '- operators can preview the same authority-mutation truth in workbench and CLI without semantic drift\n- operators can tell whether a contested path is just burst-save delay, active lock pressure, rescan-only freshness, or a reason to freeze propagation before sync continues\n'
)
rw('docs/50-roadmap.md').write_text(road)

# Open questions append
oq_append = textwrap.dedent('''\

## 45) How much low-risk contention automation is safe before coordination honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial lock pressure, burst-save delay, mixed external-writer risk, and quiesce actions should use first-class reviewed contention cases and receipts, but one policy seam remains open:

- when an obviously local-native burst-save delay may use a safely compressed review versus always opening the full contention sheet
- whether warning-tier network-reviewed mounts with mixed SMB access should always force stronger quiesce or fidelity escalation by default
- how much automatic release is acceptable once locks clear before the product starts hiding meaningful resume conditions
- when repeated contested writes should escalate from coordination nuisance to destructive-replay, topology, or compromise-adjacent review because the writer story has stopped being honest enough

This matters because weak defaults recreate locked-file, retry, and SMB folklore, while overly strict defaults could make harmless editor save bursts feel ceremonial instead of trustworthy.
''')
rw('docs/64-critical-open-questions.md').write_text(rw('docs/64-critical-open-questions.md').read_text() + oq_append)

# Sources add Locked files
sources = rw('docs/sources.md').read_text()
sources = sources.replace(
    '- Power user preferences  \n  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences\n\n- Sync Storage folder  \n',
    '- Power user preferences  \n  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences\n\n- Locked files  \n  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files\n\n- Sync Storage folder  \n'
)
rw('docs/sources.md').write_text(sources)

print('rev0063 workspace prepared at', dst)
