# Resilio operator-attestation, certainty-override, ignore/proceed, and destructive-assumption fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- a ghost-file warning can be hidden with `Ignore All`, and the warning itself can be disabled
- the same ghost-file situation may still hide a more up-to-date version on some offline peer
- the documented remediation for that unresolved situation is operator-driven: if you are certain the local version is the most up-to-date, touch the files or move them out and back in
- repairing `Service files missing` requires a stronger operator judgment: before recreating the sync instance, make sure nothing important remains in Archive, then delete `.sync`
- connecting two pre-populated trees is permitted and may merge trees, reuse equal hashes, and let latest-timestamp content replace remote content
- the `Folder not empty` warning can be a genuinely dangerous merge/overwrite situation or a harmless reconnect to the place that already hosted the folder before, and the docs tell the operator to proceed in the reconnect case

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to contribute correctness-critical assertions in several different informal styles:

- **ignore this warning because it is harmless now**
- **I am certain my local copy is the newest one**
- **I checked Archive and there is nothing important left there**
- **this non-empty path is the same previously synced tree, not a dangerous merge target**

Those are not the same assertion.
They have different blast radii, different expiry conditions, and different evidentiary floors.

Current Resilio docs still spread them across troubleshooting prose and action tips instead of one stable contract.
So the operator still has to reconstruct:

1. **what exactly am I asserting on behalf of the product?**
2. **what evidence did I rely on, and what evidence is still missing?**
3. **how destructive is the consequence if I am wrong?**
4. **when does this assertion expire or need to be reopened?**

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow three habits directly:

- **say openly when product truth is incomplete and the operator is being asked to supply judgment**
- **say openly when an action is proceeding on an assumption rather than on machine proof**
- **say openly when a warning dismissal changes visibility only, not world truth**

But AnonSync should reject four weaker habits:

- vague `if you are certain` wording with no structured evidence ledger
- `Ignore` / `Proceed` buttons that do not publish the exact assertion being made
- destructive recovery steps that rely on private human checking with no receipt
- silent expiry of human assumptions after new peers, new scans, or new chronology evidence arrives

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1235` — Operator attestation contract sheet
- `1236` — Local-truth assertion review
- `1237` — Destructive-assumption proof
- `1238` — Attestation expiry timeline
- `1239` — Operator attestation lineage receipt

These pages keep the Resilio candor and reject the casual-assumption contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that some sync incidents still require human judgment; refuse any interface contract where `ignore`, `proceed`, `touch`, `reconnect`, or `recreate` quietly depends on unstructured operator certainty rather than one explicit attestation object with evidence basis, blast radius, expiry, and blocked stronger sentence.
