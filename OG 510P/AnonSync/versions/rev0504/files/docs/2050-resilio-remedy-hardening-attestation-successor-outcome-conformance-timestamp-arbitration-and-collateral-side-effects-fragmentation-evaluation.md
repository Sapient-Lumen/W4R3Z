# Resilio remedy-hardening attestation successor outcome conformance, timestamp arbitration, and collateral side-effects fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a risky successor-world action was legitimate
- the chosen actuator looked least-broad
- an execution envelope was reviewed
- a preview was bound to commit with freshness discipline
- the run that actually fired can be attributed
- the attributable run can be described as started, partial, suspended, resumed, or terminally disposed with explicit residue

That is still weaker than answering a sharper question:

**did the completed attributable run actually land the reviewed result class for the intended slice, or did it only converge to a different-but-plausible substitute outcome with collateral effects that must stay visible?**

That deserves its own family because `the run completed`, `the bytes converged`, `the folder looks current`, `the other side now matches`, and `the queue is quiet` are not enough to justify `the reviewed result landed as intended with an acceptable collateral budget`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many result-shaping behaviors, but it still leaves outcome truth spread across unrelated articles:

- pre-populated folder connection can keep same-hash files, merge other files, and let the latest timestamp win when same-path content differs
- read-only overwrite behavior can restore locally deleted files, revert edited files, and re-download old names while leaving locally added files unsynced instead of deleting them
- if read-only overwrite is disabled, locally changed files can become invalidated and stop syncing entirely until special repair behavior occurs
- Archive restore can succeed only if timing lines up with Sync being active; otherwise the restored older-timestamp file can be sent back into Archive on the next rescan
- conflict handling can produce `.Conflict` artifacts rather than one clean landed result
- archive semantics preserve prior versions locally but do not by themselves prove that the reviewed intended result class won rather than merely some converged state

That is useful candor, but it means the operator still reconstructs `did the reviewed intended result actually land, or did timestamp arbitration, overwrite policy, invalidation, merge rules, or conflict fallback produce a narrower or different result class?` from several folder-preference, one-way-sync, archive, pre-populated-folder, and conflict pages rather than from one typed outcome-conformance object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the run completed
- a same-path file exists on both sides
- timestamp arbitration picked a winner
- a read-only local edit got reverted
- a locally deleted file got restored
- a locally added file survived but never synced
- a restored archived version got pushed back into Archive later
- extra files merged into the tree
- one or more `.Conflict` artifacts survived
- the system later speaks as if the reviewed result itself simply landed cleanly

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **execution completion integrity is weaker than reviewed-outcome conformance**
- **completed step-set is weaker than reviewed result class landed**
- **same-path convergence, timestamp-selected winner, read-only revert, restored deletion, unsynced local add, merge surplus, archive bounce-back, conflict residue, and reviewed result match are different public truths**
- **`bytes ended up somewhere`, `the folder looks synchronized`, `a file exists again`, and `the queue finished` may never impersonate `the reviewed result landed with acceptable collateral effects`**
- **timestamp arbitration, read-only overwrite policy, read-only invalidation, archive restore timing, merge-surplus behavior, and conflict fallback must degrade into outcome-conformance hazards instead of support folklore**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- execution-run identifier
- source execution-completion receipt identifier
- reviewed result-class summary
- acceptable collateral-effects budget
- actual landed result-class summary
- actual overwrite, restore, revert, merge, and invalidation summary
- conflict or substitute-result summary
- result-equivalence class
- strongest honest sentence and blocked stronger conformance sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor outcome-conformance contract sheet**
- **successor outcome-conformance review**
- **successor outcome-conformance proof**
- **successor outcome-conformance timeline**
- **successor outcome-conformance lineage receipt**
