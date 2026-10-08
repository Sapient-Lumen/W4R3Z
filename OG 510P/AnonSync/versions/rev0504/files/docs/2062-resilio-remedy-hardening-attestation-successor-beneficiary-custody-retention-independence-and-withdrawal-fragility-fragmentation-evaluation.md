# Resilio remedy-hardening attestation successor beneficiary custody, retention independence, and withdrawal-fragility fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the successor-world action was legitimate
- the chosen actuator was narrow enough to justify review
- the reviewed envelope was bound to execution tightly enough to reason about drift
- the actual run can be attributed
- the run can be judged for completion
- the landed result can be judged for outcome conformance
- the named beneficiary can be judged able to open, read, modify, or otherwise use the landed result now

That is still weaker than a sharper question:

**does the named beneficiary actually hold a retainable, self-sufficient copy under their own control, or are they only borrowing present usability from placeholders, online peers, upstream shares, app sandboxes, or revocable local-share wiring?**

That deserves its own family because `the beneficiary can use it now`, `the file opens`, `the folder is present`, and `the bytes were materialized once` are not enough to justify `the beneficiary now has durable custody of the result`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many custody-shaping details, but it still leaves custody truth spread across unrelated articles:

- disconnected and Selective Sync modes can expose names, paths, and even temporarily hydrated bytes without making retention independence the default truth
- `Remove from this device` still reverts a local copy to a placeholder and explicitly warns the operator to make sure some other peer still has a copy if later re-download matters
- removing a Selective Sync share still removes placeholders from the local file system on that device
- local shares only pull from the source share, do not sync with remote peers directly, disappear when the source is disconnected or removed, do not automatically reconnect with the source, and can cease syncing entirely when the license disappears
- local shares also do not help when the source itself only has placeholders
- single-file transfer is explicitly one-time and one-way, later file changes invalidate the transfer, recipients can share the files further, and removing the transfer from Sync UI is different from removing the resulting device copy
- iOS storage management still lets Sync-held local files be removed from the app sandbox or cleared through storage controls, which means `downloaded once into Sync` is not the same thing as `durably retained in an independently governed place`

That is useful candor, but it means the operator still reconstructs `does the beneficiary actually hold a durable copy now, or only a presently usable but upstream-fragile, revocable, sandbox-bound, placeholder-revertible, or source-tethered state?` from several mode, local-share, single-file, and mobile-storage pages rather than from one typed beneficiary-custody object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the beneficiary can currently see the object
- the beneficiary can currently open the object
- the beneficiary can currently fetch the object from another online peer
- the beneficiary once hydrated bytes locally but can revert to placeholder or lose them on local storage cleanup
- the beneficiary holds bytes only inside an app sandbox or local-share topology whose continued existence depends on upstream state
- the beneficiary received a one-time transfer whose later source changes no longer flow
- the beneficiary has an independently retained copy they can keep using even if upstream actors disconnect, revoke, remove, or change mode
- the system later speaks as though custody is settled merely because present use succeeded

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **beneficiary-usable materialization is weaker than beneficiary self-sufficient custody**
- **beneficiary can currently use the result is weaker than beneficiary holds durable bytes under their own control**
- **placeholder reversibility, upstream-share fragility, sandbox-only possession, and source-dependent re-fetch risk must degrade into custody hazards instead of living as support folklore**
- **single-file handoff, local-share attachment, sync-mode choice, and device-storage cleanup must stop impersonating one flat `recipient has it now` sentence**
- **`the user opened it`, `the bytes were local once`, `the file is in Downloads`, and `the share is still visible` may never impersonate `the beneficiary now has a durable, self-sufficient copy`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source beneficiary-usability receipt identifier
- named beneficiary and intended custody class
- current byte-possession class
- self-sufficiency versus upstream-dependency class
- local retention anchor and storage world
- export or handoff state
- source-withdrawal sensitivity
- mode-reversion or eviction sensitivity
- app-sandbox or license-bound fragility
- strongest honest custody sentence and blocked stronger custody sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-custody contract sheet**
- **successor beneficiary-custody review**
- **successor beneficiary-custody proof**
- **successor beneficiary-custody timeline**
- **successor beneficiary-custody lineage receipt**
