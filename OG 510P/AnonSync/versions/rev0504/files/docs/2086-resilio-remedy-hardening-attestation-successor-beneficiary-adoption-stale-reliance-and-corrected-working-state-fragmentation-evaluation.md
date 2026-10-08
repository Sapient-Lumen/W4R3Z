# Resilio remedy-hardening attestation successor beneficiary adoption, stale reliance, and corrected working-state fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the beneficiary is legitimate
- the successor correction is legitimate
- the beneficiary remains on the right future-correction lane
- the correction can reach the beneficiary
- the correction may have surfaced to the beneficiary
- the beneficiary may even have noticed and acknowledged the correction

That is still weaker than a sharper question:

**after the later canonical correction was seen or acknowledged, did the named beneficiary actually switch to the corrected working state, or are they still relying on a stale artifact, stale path, stale export, stale local derivative, or stale habit outside the correction lane?**

A beneficiary can receive, see, and even acknowledge the right correction while still keeping the old working copy open, still pointing a downstream workflow at the superseded path, still sharing from a stale export, or still relying on an older derivative that remains locally convenient.
`beneficiary acknowledged the correction` is weaker than `beneficiary adopted the corrected working state`.
`beneficiary adopted the corrected working state` is weaker than `stale reliance was retired for the governed slice`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about ingredients that shape observable uptake, but it still spreads them across several pages:

- the desktop main view says `History` shows general syncing activity for the last 30 days, which is useful activity evidence but not an adoption receipt
- Sync preferences say notifications can be shown or hidden, which makes surfacing configurable rather than equivalent to human switch-over
- synchronization-mode and placeholder docs say a beneficiary can double-click a placeholder to sync and open a file, or manually `Sync to this device`, which is useful fetch/open evidence but still not proof that the corrected artifact became the working artifact
- mobile file-sharing docs say downloaded files appear in `Downloads` and transfer history can remain visible even after files are removed from the Sync UI, while `Shared links` can be removed from Sync UI without removing files from the system
- local-share docs say local shares only pull from the parenting folder, do not sync with remote peers directly, and can have independent Selective Sync combinations, which means one beneficiary environment can easily accumulate multiple nearby-but-not-identical working locations

This is good operational candor.
It is not yet one first-class answer to **did this named beneficiary merely receive and open the correction, or did they actually switch their working state and retire stale reliance for the governed slice?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the correction exists
- the correction synced
- a history row exists
- a placeholder was hydrated
- a downloaded copy exists somewhere on the device
- a local derivative also exists
- the beneficiary definitely switched to the corrected working state
- stale reliance definitely ended
- downstream use is therefore compliant

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **beneficiary acknowledgement is weaker than beneficiary adoption of the corrected working state**
- **download, hydration, and open events must degrade into first-class uptake evidence instead of dissolving into `the beneficiary switched` folklore**
- **coexisting stale copies, stale exports, stale derivatives, and stale downstream pointers must stay explicit instead of disappearing behind `latest bytes arrived`**
- **`the correction was seen`, `the file was downloaded`, and `the file was opened` may never impersonate `the beneficiary adopted the correction and retired stale reliance`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source beneficiary-notice receipt identifier
- named beneficiary and governed slice
- later canonical correction identifier
- required uptake class
- corrected working-artifact identifier
- current working-pointer state
- stale artifact set summary
- stale-reliance risk
- downstream pointer-switch evidence
- stale-retirement evidence
- relapse or reversion evidence
- strongest honest adoption sentence
- blocked stronger compliance sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-adoption contract sheet**
- **successor beneficiary-adoption review**
- **successor beneficiary-adoption proof**
- **successor beneficiary-adoption timeline**
- **successor beneficiary-adoption lineage receipt**
