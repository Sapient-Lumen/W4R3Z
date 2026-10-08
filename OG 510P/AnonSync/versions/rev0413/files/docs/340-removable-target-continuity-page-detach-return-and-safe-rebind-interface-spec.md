# Removable target continuity page: detach, return, and safe rebind interface spec

The archive already has path-continuity pages, target-custody review, and blocked-path repair.
What it still lacked was one ordinary page for the continuity question removable or weakly bound targets create:

> when a USB/network/provider-backed target disappears and later returns, is the product looking at the same target with preserved continuity, a safe rebind candidate, or a new-world merge hazard?

Current Resilio docs still make the seam visible but scattered.
They say USB and network paths can back same-host local shares, that cross-volume or moved shares often require disconnect/reconnect, that local shares are removed with the source and do not auto-reattach when the source returns, that SMB-backed paths can lose notifications or suffer provider-specific hazards, and that returning to an existing non-empty path can be either ordinary reconnect or risky overwrite territory depending on lineage.
That deserves one stable continuity page.

## Page promise

The Removable target continuity page should make five answers adjacent:

1. last-known target identity now
2. disappearance cause and continuity grade now
3. return evidence now
4. strongest honest rebind verdict now
5. strongest honest next action

The page exists so the operator no longer has to guess whether `it came back` means `same world`, `safe rebind`, or `dangerous merge`.

## Fixed page order

Every removable-target continuity page should render the same sections in the same order:

1. **Target snapshot**
2. **Disappearance and continuity grade**
3. **Return evidence and environmental fit**
4. **Rebind versus recreate verdict**
5. **Admissible actions**
6. **Receipt promise**

### 1) Target snapshot

This section should show:

- target subject or edge in scope
- media/provider class
- last-known path and host
- whether the target was independent, same-host local edge, or provider-bound mobile target
- whether the page is evaluating absence, return, or already-live rebind

The operator should be able to answer: **which target continuity story am I looking at?**

### 2) Disappearance and continuity grade

This section should show:

- why the target became absent (`device detached`, `provider grant lost`, `source removed`, `path moved`, `network share unavailable`, `unknown`)
- whether continuity is `intact but offline`, `detached with recoverable lineage`, `ambiguous`, or `broken`
- whether the product still trusts prior subject ID / lineage evidence
- whether any warning-tier medium characteristics already weaken the continuity claim

The operator should be able to answer: **how much continuity survived the disappearance?**

### 3) Return evidence and environmental fit

This section should show:

- what evidence says the medium/provider has returned
- whether notifications, permissions, provider grants, or path provenance are still strong enough
- whether the returning environment is meaningfully the same as before
- whether the target is empty, pre-populated with matching lineage, or pre-populated without strong lineage proof

The operator should be able to answer: **did the same target really return under acceptable conditions?**

### 4) Rebind versus recreate verdict

This section should show:

- whether the honest next state is `resume as same target`, `safe rebind`, `guarded adopt`, or `recreate as new target`
- whether non-empty contents are safe prior bytes, warning-tier merge material, or conflicting unrelated material
- whether same-host/local-edge rules force manual reattach instead of silent resume
- whether the product can preserve history/continuity receipts across the action

The operator should be able to answer: **is this a continuation or a new world?**

### 5) Admissible actions

Example actions:

- `Resume when medium returns`
- `Regrant provider and rebind`
- `Manual reattach as same local edge`
- `Guarded adopt existing target`
- `Recreate as new target`
- `Reject because lineage proof is insufficient`

The page must not collapse all of these into one `Reconnect` button.

### 6) Receipt promise

A removable-target continuity receipt should preserve:

- target and medium/provider in scope
- disappearance cause and continuity grade
- return evidence used
- rebind/recreate verdict
- chosen action or abstention
- whether continuity was preserved, weakened, or intentionally severed

The operator should be able to answer: **what later evidence will prove whether this was the same target continuing or a newly adopted target?**

## Compact continuity row contract

A trustworthy compact continuity row should preserve the following order:

1. target subject
2. continuity phrase
3. return-evidence phrase
4. strongest blocker or hazard
5. next honest action

Example:

```text
USBMirror   detached with recoverable lineage   medium returned, target non-empty with matching lineage proof   hazard: notifications still weak on network-backed path   Review
```

## What this page must never imply

The page must never imply that:

- returned path automatically means returned continuity
- any non-empty returning target is either always safe or always unsafe
- same-host local-edge return is automatic after source return
- provider/network weakness is only a performance issue rather than a continuity-confidence issue
- `Reconnect` explains whether lineage was preserved or recreated

## Result

This page is how AnonSync borrows Resilio's practical candor about returning targets without cloning the weaker habit of scattering continuity truth across move/reconnect FAQs, network-path caveats, and local-share footnotes.
