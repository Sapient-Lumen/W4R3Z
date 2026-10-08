# Resilio remedy hardening attestation successor action-envelope preflight preview, fail-closed containment, and runtime-scope fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for exposing several ingredients that help an operator anticipate that a chosen actuator may spread, download, rescan, reconnect, or continue doing work after the obvious button click.
That is useful.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say linked devices automatically make **all** folders available on **all** linked devices
- current `Synchronization Modes` docs still say disconnected folders are visible before connection, and selective-sync folders show placeholder files while later hydration still depends on an online peer
- current `Selective Sync` docs still say leaving the toggle off when connecting causes the device to **immediately start downloading all content**, including nested folders and subfolders
- current `Sync functionality in detail` docs still say remembered approval is the default, while per-peer approval-every-time is merely optional
- current `How soon does synchronization start?` docs still say rescan happens by default every 600 seconds and on Sync start
- current `How to pause syncing` docs still say pause does **not** stop everything: zero-sized files and deletions still sync, and new files are still rescanned and indexed
- current `Sharing single file` docs still say one-time transfer links may be made non-expiring and cannot be usage-limited or device-banned

## Where the current contract still fragments

The problem is not that Resilio hides all spread behavior.
The problem is that it still does not produce one first-class, case-scoped **successor action execution-envelope and fail-closed containment** object.

Today an operator can often infer only weaker truths such as:

- a linked-device action may be legitimate and proportionate in principle, but the product does not preserve one reviewed predicted touched-set before the action starts
- a manual connection dialog may expose a selective-sync toggle, but leaving it off converts the operation into an immediate full download of all content, including nested content
- approval memory can silently widen future admissions unless the operator deliberately switches to every-time approval
- background rescans and start-time rescans can continue discovering and acting on changes even when the operator is thinking in terms of one completed click-path
- pause is not a hard fail-stop, because deletions still propagate and indexing continues
- one-time single-file transfer is narrower than a folder share, but it still lacks one typed envelope object that says who may fetch, how many times, and what runtime stop condition exists beyond expiration
- the operator still reconstructs runtime containment by reading multiple feature articles instead of opening one typed action-envelope review

Those are useful clues.
They are not the same as an explicit answer to `if we start this reviewed successor-world action now, what exact slice do we predict will be touched, what automatic side-effects are armed, what guardrails will trip, and can the operation fail closed instead of continuing past the reviewed boundary?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the plan looked narrow enough when reviewed`.
It needs to support claims such as:

- the chosen actuator is proportionate, but execution is blocked because the product cannot yet preview the touched-set precisely enough
- the reviewed plan is allowed only if the action is armed with a hard stop when the touched-set exceeds the approved slice
- the safest honest sentence is `least-harm plan selected, runtime envelope not yet trusted`
- a remembered-approval lane is blocked for this case because future auto-admission would exceed the reviewed envelope
- a folder connection is blocked because the dialog would immediately hydrate all nested content instead of preserving placeholder-only exposure
- pause is insufficient as an emergency brake because deletions and indexing still flow

AnonSync therefore needs first-class objects for **predicted touched-set, inherited auto-expansion hazards, live guardrails, trip conditions, fail-open versus fail-closed behavior, abort obligations, residual side-effects after abort, and blocked stronger containment sentence** rather than leaving operators to reconstruct runtime scope from linked-device defaults, connect-dialog toggles, rescans, remembered approvals, and pause semantics.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `granted that the action is allowed and even proportionate on paper, will runtime stay inside the reviewed scope?` — only by making the operator combine several partially overlapping mechanics:

- linked-device automatic availability
- disconnected, selective, and synced modes
- connect-time toggle choice
- remembered approval versus every-time approval
- background rescans on a clock and on start
- pause semantics that still allow some propagation
- one-time file-transfer expiry and forwarding quirks

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **successor action execution-envelope and fail-closed containment** directly.
Its interface family should let the product separate at least these truths:

- action legitimate, plan proportionate, runtime envelope unreviewed
- touched-set preview generated, but guardrails not armed
- placeholder-only preview safe, full-hydration path blocked
- remembered-approval lane blocked because future admissions exceed reviewed scope
- pause unavailable as emergency brake for this action class
- runtime tripped guardrail and failed closed
- runtime exceeded reviewed boundary before abort completion
- stronger within-envelope sentence blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation successor-action-envelope contract sheet**, **successor-action-envelope review**, **successor-action-envelope proof**, **successor-action-envelope timeline**, and **successor-action-envelope lineage receipt**.
