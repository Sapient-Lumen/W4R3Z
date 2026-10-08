# Resilio remedy-hardening attestation successor beneficiary usability, materialization, and access-prerequisite fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the risky successor-world action was legitimate
- the chosen actuator looked least-broad enough to review
- the execution envelope was previewed and guarded
- preview was bound to commit with freshness discipline
- the run that actually fired can be attributed
- the attributable run can be described as started, partial, resumed, aborted, or terminally disposed
- the completed run can be judged against the reviewed result class and collateral-effects budget

That is still weaker than a sharper question:

**can the named beneficiary actually open, use, modify, or otherwise exercise the landed result now, in the intended way, from the intended world, without hidden placeholder, online-source, permission, handler, or filesystem blockers?**

That deserves its own family because `the path exists`, `the folder is visible`, `the file list is present`, `the run completed`, and `the reviewed result landed` are not enough to justify `the named beneficiary can actually use this result now as intended`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many usability-shaping details, but it still leaves beneficiary-usable truth spread across unrelated articles:

- placeholder files in Selective Sync or Connected mode are still 0-byte stand-ins that show only names and types until actual bytes are fetched
- entering Selective Sync at connect time or while linking devices can leave the destination with placeholders instead of full files even though the share is plainly visible
- double-clicking a placeholder only auto-opens if the file arrives within about one minute; otherwise the user must take another step
- placeholder hydration still depends on at least one online peer that has the bytes
- reverting files to placeholders is reversible only if some other peer still has a full copy; placeholder-only swarms can strand the beneficiary with names but no usable bytes
- WebUI has no file-system integration, so placeholder management moves into separate UI flows instead of one uniform file-browser contract
- missing Finder or Explorer integration removes shell actions that are part of the ordinary selective-sync usability path
- local read-only changes can stop future updates to those files, producing a visible local copy that is no longer a live beneficiary-usable sync participant
- locked files, missing write access, path-length limits, non-UTF-8 naming, and filesystem errors can still stop syncing or make the landed result unusable in the beneficiary world
- source-peer absence can leave announced files as ghosts that look discoverable but are not actually retrievable anymore

That is useful candor, but it means the operator still reconstructs `can the named beneficiary really use the landed result now, or is it only visible, placeholdered, blocked, stale, shell-unintegrated, permission-rejected, or source-dependent?` from several selective-sync, mode, file-browser, troubleshooting, and warning pages rather than from one typed beneficiary-usability object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the landed result exists somewhere in the mesh
- the destination folder is visible
- the file name is present locally
- the local object is only a placeholder or disconnected announcement
- actual bytes still depend on an online source peer
- the shell affordance required to fetch or evict is missing
- a local copy exists but cannot receive future updates because of read-only mutation posture
- the file is blocked by permissions, path rules, encoding rules, locks, or filesystem failure
- a warning can be hidden even though the beneficiary still does not have usable bytes
- the system later speaks as if the beneficiary simply has the result and can use it

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **reviewed-outcome conformance is weaker than beneficiary-usable materialization**
- **landed result class is weaker than named-beneficiary usable result state**
- **path visibility, folder presence, placeholder presence, and metadata-only arrival are different public truths from beneficiary-usable bytes**
- **online-source dependency, shell-integration dependency, permission dependency, and live-update dependency must degrade into usability hazards instead of support folklore**
- **`the file is there`, `the folder is connected`, `the result landed`, and `you can see it in the tree` may never impersonate `the named beneficiary can actually use it now as intended`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- execution-run identifier
- source outcome-conformance receipt identifier
- named beneficiary and intended beneficiary action class
- intended usable-result class
- current materialization state
- online-source dependency state
- shell or handler dependency state
- access and update-receipt posture
- path, encoding, lock, and filesystem blocker summary
- strongest honest usable sentence and blocked stronger usable sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-usability contract sheet**
- **successor beneficiary-usability review**
- **successor beneficiary-usability proof**
- **successor beneficiary-usability timeline**
- **successor beneficiary-usability lineage receipt**
