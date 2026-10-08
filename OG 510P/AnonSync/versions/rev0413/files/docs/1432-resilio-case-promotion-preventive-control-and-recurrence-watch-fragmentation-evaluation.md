# Resilio case-promotion, preventive-control, and recurrence-watch fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- choose the least-destructive intervention
- execute that intervention safely
- close a case honestly with supported, mitigated, or unresolved language

What it still lacked was one ordinary operator answer to the next question:

> after a case closes, what durable guardrail or watch should we promote from it so the result becomes operational truth rather than folklore?

Current official Resilio material is useful here precisely because it already contains many pieces of prevention, detection, and standardization, but still across many different pages:

- `Agent run out of system notify watchers`
- `Some internal tasks are taking time to complete`
- `Collecting debug logs automatically`
- `Resilio Sync change log`
- `Running Sync on schedule`
- `Performance overview`
- `Power user preferences`
- `Running Sync in configuration mode`
- `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?`
- `Running Sync as a service on Windows`
- `My files don't sync`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Agent run out of system notify watchers` still explains a concrete environmental hazard: Linux watcher exhaustion means Sync will learn about changes only by manual or periodic rescans unless the watcher limit is raised. It also says the permanent fix requires writing the sysctl value to `/etc/sysctl.conf` and restarting Sync.
- `Some internal tasks are taking time to complete` still says the condition can be intermittent and self-recovering, which means some cases should promote a watch or threshold rather than a destructive preventive change.
- `Collecting debug logs automatically` still requires debug logging to be enabled before restart, then asks the operator to reproduce the issue and wait at least 15 minutes, which means support-artifact capture is itself a repeatable runbook element.
- `Running Sync on schedule` still exposes a weekly scheduler for bandwidth limits by day and hour. That is a real preventive or containment ingredient, but it lives as one isolated settings page rather than one guardrail object tied back to incident history.
- `Performance overview` still gives only 1 minute, 10 minute, and 1 hour windows. That is useful live evidence, but much weaker than a durable recurrence watch or escaped-control ledger.
- `Power user preferences` still says the current article covers the latest version and older versions may miss or deprecate settings. That matters because any preventive control built on those settings is version-dependent by construction.
- `Running Sync in configuration mode` still says Sync can apply the same settings on multiple machines and that Advanced Preferences parameters can also be added. That is already the seed of policy promotion, but still not a first-class case-to-control workflow.
- `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` still requires disabling tracker and relay both in share preferences and in power user settings, and then restarting Sync. That is a perfect example of one real guardrail whose complete contract spans several surfaces and an apply step.
- `Running Sync as a service on Windows` still says service install can either migrate existing settings or create a clean installation requiring re-share and reconnect. So even a seemingly standard preventive rollout can fork worlds.
- `My files don't sync` still pushes the operator through warnings, history, queue inspection, ignore-list consistency, xattr considerations, locked-file checks, permission checks, restart/rescan, disk space, `.!sync` cleanup, time-difference checks, and log collection. That is a rich troubleshooting tree, but it does not culminate in one object that says which of those findings became a permanent guardrail, which became only a watch, and which remain one-off case facts.
- `Resilio Sync change log` still shows that these ingredients arrived piecemeal over time: v2.6.0 introduced performance charts, statuses/warnings, advanced power user settings, and default ignore-list additions; v2.7.0 added force rescan, search in power user settings, and an error report when Sync consumed too much RAM; older entries added options like skipping free-space checks, manually re-checking locked files, and preserving speed settings on restart.

So current Resilio still clearly admits serious post-case truths:

- some lessons want a persistent environment fix
- some want a versioned settings standard
- some only justify a watch window
- some only justify a capture-on-repeat runbook
- some are too world-specific to promote globally
- some controls have prerequisites and restart costs
- some controls only mitigate blast radius rather than prevent the cause

But those truths still do not become one first-class operator-facing **case-to-control / case-to-watch / no-preventive-control verdict object**.

## What Resilio still gets right

### 1) It already exposes real prevention ingredients

Scheduler, power-user preferences, config mode, watcher tuning, LAN-only settings, and service-mode choices are all genuine building blocks.
That practicality is worth borrowing.

### 2) It admits some fixes need permanence work

The watcher-limit article is especially useful because it distinguishes a reboot-volatile tweak from a preserved setting in `sysctl.conf`.
That is exactly the kind of durability truth guardrail promotion must preserve.

### 3) It keeps live observation and heavier artifact capture distinct

Performance charts, warnings, and debug-log collection are different evidence classes with different costs.
That separation is good.

### 4) It quietly shows that controls are version-bound and world-bound

Between change-log evolution, power-user deprecations, config-mode scope, and service-install forks, current Resilio already proves that not every lesson cleanly generalizes.

## Where current Resilio still fragments the operator answer

### A) Prevention ingredients are not case-owned

A careful operator can discover a relevant scheduler rule, watcher bump, config stanza, ignore-list discipline, LAN-only restriction, or service posture.
But the product still does not answer in one place:

- which closed case justified this control
- whether the control prevents, detects, or merely mitigates
- what scope it should apply to
- what worlds are excluded
- what proof is required after activation

### B) `No recurrence seen` can masquerade as real prevention

Current docs let an operator try a fix or tune a setting, but they do not preserve one canonical distinction among:

- no repeat observed yet
- near miss caught
- repeated condition detected early
- repeat fully prevented
- repeat escaped the control

That distinction is essential if the product is going to claim prevention honestly.

### C) Post-case standardization is spread across settings, KBs, and memory

Config mode can spread settings.
Scheduler can constrain activity.
Power-user preferences can refine behavior.
Warnings and logs can support monitoring.
But there is still no one workflow that promotes a closed case into a named, owned, scoped guardrail or explicitly says `this case is not meaningfully preventable`.

### D) Coverage boundaries and anti-claims are mostly implicit

The LAN-only article is a good example.
It already implies all of the following:

- this is not one toggle
- both share and global surfaces matter
- restart is part of activation
- peer discovery still depends on multicast behavior

That is a real coverage contract.
But Resilio still leaves the operator to infer the anti-claims instead of publishing a durable `protects / does not protect / requires` object.

## Hard product decision unlocked by this pass

AnonSync should not merely add more troubleshooting prose after case closure.
It should promote closed-case lessons into first-class objects with typed outcomes:

- `preventive-control`
- `detective-watch`
- `containment-control`
- `capture-on-repeat-runbook`
- `non-preventable-by-product`
- `accepted-risk-with-rereview`

That is the clean next seam because it turns incident memory into operational structure.

## Replacement line for AnonSync

Borrow from Resilio:

- practical candor that some hazards are environmental and need persistent tuning
- separation between live observation, warnings, and heavyweight artifact capture
- willingness to expose real settings and rollout ingredients

Do not clone from Resilio:

- a world where the operator must stitch together scheduler pages, watcher KBs, config-mode docs, service notes, power-user settings, and changelog memory just to answer `what did we permanently change because of this case?`
- any contract that lets `we changed a setting` impersonate `we now prevent this class of repeat`
- any contract that lets `quiet period elapsed` impersonate `control proven`

AnonSync should instead ship explicit pages for:

- source-case-to-guardrail promotion
- control coverage and anti-claims
- rollout and rereview proof
- recurrence watch and escape accounting
- durable receipts showing what stronger preventive sentence is still blocked
