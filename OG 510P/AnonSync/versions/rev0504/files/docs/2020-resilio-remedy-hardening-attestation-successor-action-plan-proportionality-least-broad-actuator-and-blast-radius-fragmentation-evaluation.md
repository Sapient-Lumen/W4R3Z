# Resilio remedy hardening attestation successor action-plan proportionality, least-broad actuator, and blast-radius fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for exposing several ingredients that help an operator choose *some* narrower way to accomplish a successor-world action.
That is useful.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say linked-device mode automatically makes **all** folders available on **all** linked devices and lets approvals happen from any device where the folder is present
- current `How to create a Read Only folder while syncing across linked devices?` docs still say getting a read-only result on a linked device requires a **Standard-folder manual-key detour**, not the default linked-device lane
- current `Sync Share Dialog (Desktop)` docs still say manual folder sharing lets the operator choose Read Only, Read & Write, or Owner for Advanced folders, and also add approval, expiration, and use-count controls for link-based sharing
- current `Sharing single file` docs still say there is a distinct one-time one-way file-transfer lane with its own expiration behavior, non-expiring option, and forwarding caveat
- current `Running Sync in configuration mode` docs still say config mode can materialize settings across multiple machines, but only for Standard folders
- current `Sharing a folder locally` docs still say there is a same-device local-share lane that does not propagate through normal peer discovery and is not itself propagated to linked devices

## Where the current contract still fragments

The problem is not that Resilio lacks any narrower and broader actuators.
The problem is that it still does not produce one first-class, case-scoped **successor action-plan proportionality and least-broad actuator legitimacy** object.

Today an operator can often infer only weaker truths such as:

- an action is authorized, but the product does not preserve whether the chosen lane was the narrowest one that could have satisfied the purpose
- linked-device convenience can spread the folder to every linked device, while a manual read-only Standard-key detour or one-time single-file transfer would have touched a smaller slice
- folder-share links can be bounded with approvals, expiry, and use limits, but single-file links have different ceilings and different forwarding consequences
- config mode can apply settings across multiple machines, but that estate-scale actuator is not surfaced as a higher blast-radius class than a one-object manual share
- local sharing is a distinct same-device actuator, but the product does not elevate `local only` versus `remote peers` versus `all linked devices` into one comparative plan verdict
- the operator still reconstructs least-harm choice by reading multiple topology and feature articles instead of opening one typed action-plan review

Those are useful clues.
They are not the same as an explicit answer to `this action may be legitimate, but is this chosen mechanism the narrowest legitimate way to achieve the intended result, for the intended slice, with the lowest acceptable spillover and future-forwarding risk?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `this action is authorized`.
It needs to support claims such as:

- the action is legitimate, but the chosen linked-device actuator is too broad because a one-target read-only detour exists
- a folder-level share is legitimate, but the safer plan is a one-time single-file transfer with expiry because the beneficiary only needs one artifact once
- a remote share is legitimate, but a same-device local share is the least-broad actuator for this purpose
- config rollout is legitimate, but estate-wide propagation is blocked because the purpose is slice-limited
- the strongest honest sentence is `action authorized, least-harm actuator not yet proved`

AnonSync therefore needs first-class objects for **candidate actuator family, purpose fit, beneficiary slice, expected spread set, delegation side-effects, future-auto-expansion exposure, forwardability risk, reversibility class, expiry or use-budget, and blocked stronger least-harm sentence** rather than leaving operators to reconstruct proportionality from linked-device defaults, manual read-only detours, link checkboxes, and topology folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `granted that this action may happen, what is the narrowest legitimate actuator that can do it?` — only by making the operator combine several partially overlapping mechanics:

- linked-device automatic spread
- manual folder share with permission and approval controls
- Standard-folder read-only key detours
- one-time single-file transfer lanes
- same-device local-share lanes
- config-mode multi-machine rollout

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **successor action-plan proportionality and least-broad actuator legitimacy** directly.
Its interface family should let the product separate at least these truths:

- action authorized, actuator family unreviewed
- broader actuator chosen for convenience only
- same-device-only actuator available and preferred
- one-object transfer sufficient, folder-level share blocked
- read-only narrow lane available, linked-device full-spread lane blocked
- estate-wide rollout legitimate for named population only
- chosen actuator proportionate for named slice only
- safer alternative still available, stronger least-harm sentence blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation successor-action-plan contract sheet**, **successor-action-plan review**, **successor-action-plan proof**, **successor-action-plan timeline**, and **successor-action-plan lineage receipt**.
