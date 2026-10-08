# Resilio remedy-hardening attestation successor execution provenance, background auto-run, and causal attribution fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a risky successor-world action is legitimate
- the chosen actuator looked least-broad
- an execution envelope was reviewed
- a preview was bound to commit with a freshness window and execute-if-unchanged discipline

That is still weaker than answering a sharper question:

**what exactly fired the run that actually happened, and was it the bound reviewed commit or some background or adjacent mechanism that only looked equivalent after the fact?**

That question deserves its own family because `same successor world`, `same actor identity`, `same folder visible`, `same result eventually appeared`, and `the operator meant for it to happen` are not enough to justify `this exact bound run executed as reviewed`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many auto and background behaviors, but it still leaves causal attribution spread across unrelated articles:

- linked devices can automatically make all folders available across the linked set
- approvals are remembered by default unless operators deliberately require approval every time
- pending folders can auto-connect later if the sharer had already approved that person before
- rescans happen on start and every 600 seconds by default
- pause still allows delete propagation, rescanning, and indexing
- linked-device mode gives Owner semantics automatically, while some alternate permission shapes require detours through different folder architecture

That is useful candor, but it means the operator still reconstructs `did the reviewed commit fire, or did convenience/background behavior effectively fire something adjacent?` from several convenience, approval-memory, background-scan, and folder-architecture pages rather than from one typed execution-provenance object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- commit token existed
- operator intended the run
- some actor in the controller set clicked something
- a background auto-connect or auto-arrival widened the touched-set
- a start-time or scheduled rescan surfaced the delta
- pause left enough motion alive that deletes or index updates still traveled
- a different permission lane or architecture detour produced the visible effect
- the system later presented the outcome as if the bound reviewed run itself had fired cleanly

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **bound preview/commit legitimacy is weaker than attributable execution legitimacy**
- **a commit token is weaker than proof of which actor, process, and actuator path actually fired**
- **visible outcome is weaker than causal-chain provenance for the named run**
- **`the operator meant this to happen` may never impersonate `this exact bound run executed through the reviewed lane`**
- **background automation, remembered approval, pending auto-connect, and start-time or scheduled rescans must degrade into attribution hazards instead of convenience details**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- execution-run identifier
- source bound-preview receipt identifier
- initiating actor set
- initiating process or subsystem
- reviewed actuator versus actual actuator
- runtime world of execution
- auto-behavior participants
- causal-chain summary
- substitution or widening events
- strongest honest sentence and blocked stronger attributable-execution sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor execution-provenance contract sheet**
- **successor execution-provenance review**
- **successor execution-provenance proof**
- **successor execution-provenance timeline**
- **successor execution-provenance lineage receipt**
