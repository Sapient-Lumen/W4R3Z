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
