# Resilio remedy-hardening attestation successor beneficiary continuity, update enrollment, and detached-snapshot fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the successor-world action was legitimate
- the action envelope was reviewed tightly enough to justify execution
- the actual run can be attributed and judged for completion
- the landed result can be judged for outcome conformance
- the named beneficiary can be judged able to use the result now
- the named beneficiary can be judged to hold a durable, self-sufficient copy now

That is still weaker than a sharper question:

**does the named beneficiary remain enrolled in the canonical future-correction lane for this result, or do they only hold a detached snapshot that will not reliably receive later fixes, supersessions, withdrawals, or recall-worthy corrections?**

That deserves its own family because `the beneficiary has it`, `the file is durable`, and `the copy is self-sufficient` are not enough to justify `the beneficiary will stay current with the canonical successor truth`. Durable custody and durable continuity are different truths.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many continuity-shaping details, but it still leaves continuity truth spread across unrelated articles:

- linked devices automatically receive every folder and do so with full owner-style continuity inside the linked family
- manual sharing is a different lane where folder-level access is chosen device by device rather than inherited as one universal future-update relation
- single-file sharing is explicitly a one-time one-way transfer, later source changes do not continue syncing through that transfer, recipients can share the received files further, and removing the transfer from Sync UI is different from removing the device copy
- disconnecting a folder leaves the local file-system copy available while ending active sync, and reconnect can come back through a different default path or newly indexed directory
- removing a folder from linked devices may still leave it alive on remote devices outside the linked identity
- local shares only sync with the parenting share through self, not directly with remote peers, disappear when the source is disconnected or removed, do not automatically reconnect when the source returns, and cannot carry continuity if the source only has placeholders
- read-only peers can keep local modifications, but doing so can stop future updates for those files, which means `still has bytes` and `still stays on the canonical update lane` are not the same thing

That is useful candor, but it means the operator still reconstructs `does the beneficiary keep receiving future fixes and withdrawals, or are they now living on a detached snapshot?` from several linking, sharing, local-share, disconnect, and read-only articles rather than from one typed beneficiary-continuity object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the beneficiary has a durable copy now
- the beneficiary is still on the canonical future-update lane
- the beneficiary holds only a one-time received snapshot
- the beneficiary holds a disconnected or locally diverged copy that will not stay current
- the beneficiary is attached only through a fragile local-share topology
- the beneficiary can manually reconnect later, but is not continuously enrolled now
- the system later speaks as though detached possession and live continuity were the same thing

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **beneficiary self-sufficient custody is weaker than beneficiary continuity enrollment in the canonical successor lane**
- **holding durable bytes is weaker than staying attached to future fixes, supersessions, withdrawals, and recall-worthy corrections**
- **single-file transfer, detached export, disconnected-folder residue, local-share attachment, and read-only local divergence must degrade into continuity hazards instead of living as support folklore**
- **`the beneficiary has it`, `the recipient downloaded it`, `the folder is still on disk`, and `the file can be reopened later` may never impersonate `the beneficiary will stay current with the canonical successor truth`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source beneficiary-custody receipt identifier
- named beneficiary and intended continuity class
- canonical successor source or update lane identifier
- current enrollment state
- detached-snapshot versus live-subscription state
- supersession and withdrawal reach
- local divergence or stop-updating risk
- reconnect or path-rebind sensitivity
- forwardability or onward-fork risk
- strongest honest continuity sentence and blocked stronger continuity sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-continuity contract sheet**
- **successor beneficiary-continuity review**
- **successor beneficiary-continuity proof**
- **successor beneficiary-continuity timeline**
- **successor beneficiary-continuity lineage receipt**
