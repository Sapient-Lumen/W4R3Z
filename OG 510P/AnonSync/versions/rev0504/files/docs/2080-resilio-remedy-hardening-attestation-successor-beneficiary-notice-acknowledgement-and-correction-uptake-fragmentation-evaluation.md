# Resilio remedy-hardening attestation successor beneficiary notice, acknowledgement, and correction-uptake fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the beneficiary is legitimate
- the successor action was legitimate
- the landed result conforms closely enough
- the beneficiary can use the result now
- the beneficiary can hold a durable self-sufficient copy
- the beneficiary may remain attached to a live future-update lane
- the product may even know whose lane that is and what governance aperture governs it

That is still weaker than a sharper question:

**when a later canonical correction, supersession, withdrawal, or beneficiary-specific warning exists, did the named beneficiary actually notice it, and was any required acknowledgement completed?**

A beneficiary can stay on the right authority-governed lane and still not have one explicit, bounded answer to **whether the correction merely existed, merely synced, merely surfaced in UI, was actually seen by the beneficiary, or was explicitly acknowledged**.
`future updates are live` is weaker than `the named beneficiary noticed the later canonical correction`.
`the beneficiary noticed it` is weaker than `the beneficiary acknowledged the correction under the required policy`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about ingredients that shape notice, but it still spreads them across several pages:

- desktop Sync preferences expose a `Show notifications` toggle, so the product openly admits that approval requests and other sync notifications can be shown or not shown
- the desktop main view says the bell icon lights up for approval requests or other notifications, history shows general syncing activity for the last 30 days, and a green checkmark means files are synced with all connected peers — all useful machine-state facts, but still not a human notice or acknowledgement receipt
- mobile settings likewise treat notifications as a surface setting, not as a durable beneficiary-attention proof primitive
- debug logging exists for issue analysis, with bounded storage and retention settings, which is useful evidence but still not beneficiary acknowledgement
- on SMB shares or when system notify watchers are exhausted, Sync may fail to receive file-update notifications and instead learn changes only during full-folder or periodic rescans
- scheduled rescans are configurable and can even be disabled, which means later correction discovery timing can widen or degrade without producing any beneficiary-facing `seen` receipt

This is good operational candor.
It is not yet one first-class answer to **did the beneficiary actually notice the later canonical correction, through what carrier, under what deadline, and with what acknowledgement state?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the canonical correction exists
- the correction reached the beneficiary's device mesh
- the UI could have shown some notification
- the history view records general syncing activity
- the runtime stayed healthy enough to discover the change eventually
- the beneficiary definitely noticed the correction
- the beneficiary definitely acknowledged the correction
- the beneficiary definitely accepted or acted on the correction

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **authority-correct future delivery is weaker than beneficiary notice of later canonical correction**
- **beneficiary notice is weaker than beneficiary acknowledgement**
- **machine sync status, bell-state, history rows, and debug logs must degrade into first-class notice evidence instead of dissolving into `the beneficiary was informed` folklore**
- **`the correction existed`, `the files synced`, `the warning could have appeared`, and `history shows activity` may never impersonate `the named beneficiary noticed and acknowledged the correction`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source beneficiary-authority receipt identifier
- named beneficiary and governed slice
- later canonical correction identifier
- notice policy class
- required acknowledgement class
- allowed carrier set
- observed carrier actually used
- carrier health / degradation state
- surfaced-to-device evidence
- beneficiary-seen evidence
- beneficiary-acknowledged evidence
- reminder / expiry posture
- strongest honest notice sentence
- blocked stronger uptake sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-notice contract sheet**
- **successor beneficiary-notice review**
- **successor beneficiary-notice proof**
- **successor beneficiary-notice timeline**
- **successor beneficiary-notice lineage receipt**
