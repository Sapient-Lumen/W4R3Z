# Resilio health, repair, and evidence page evaluation

## Purpose

The archive already has stronger answers for trust, intake, custody, route truth, helper policy, capability source, and subject-kind choice.
What still remained under-specified was another ordinary but load-bearing non-clone seam:

> current Resilio docs are often practical when something is broken, but the operator still has to reconstruct one coherent answer from warning rows, troubleshooting articles, hidden storage/service paths, and manual log or dump rituals.

This document tightens that line.
It does not argue that Resilio lacks good troubleshooting material.
It argues that the health and repair truth is still too article-shaped to deserve direct interface cloning.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- warnings are concrete enough that operators can usually tell whether the issue is locks, database damage, missing service files, source absence, or generic slowness
- the product is candid that mixed SMB/direct access, broken notifications, and file locks are real operational hazards
- there are workable repair suggestions for restart, reconnect-to-same-path, remove-and-re-add, and service-file reset
- the docs tell operators where logs, storage state, and crash artifacts actually live instead of pretending diagnosis is magical

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Symptom truth is still scattered across warnings, columns, and troubleshooting pages

Current official docs still say all of the following at once:

- operators are expected to inspect the `Peers` and `Status` columns and click warning rows for hints
- `Some internal tasks are taking time to complete` can be recoverable slowness rather than hard failure
- `My files don't sync` fans diagnosis back out across peer connectivity, file warnings, local file-system errors, and re-add ritual
- the troubleshooting tree lives partly in UI rows and partly in separate KB articles

That is useful.
It is still not one ordinary page answering:

> what family of problem is this, what evidence floor already exists, what is the first safe action, and which stronger repair rung only becomes honest after that action fails?

### 2) Environment conflict truth is still support-lore shaped

Current official docs still say all of the following at once:

- locked files are visible, but Sync cannot identify which application owns the lock
- editor-friendly delay behavior lives in `FileDelayConfig` inside the storage folder and requires restart
- SMB-backed paths can lose notifications and mixed direct access outside Samba can damage files or roll changes back
- change detection can fall back from notifications to periodic rescan depending on storage class and watcher state

That is strong operational candor.
It is still not one ordinary page answering:

> is this ordinary local-write contention, a foreign-writer topology problem, weak notification confidence, or a combination — and what topology or timing rule would actually make this safe?

### 3) Repair truth is still ladder-shaped but not one stable page

Current official docs still say all of the following at once:

- `Database error` recommends restart first, then disconnect/reconnect to the same destination, then full re-add if needed
- `Service files missing` recommends remove and re-add, warns about Archive review, and may require deleting `.sync`
- `My files don't sync` recommends re-add or re-index when trees cannot merge
- some repair recipes also warn that two instances touching the same folder can corrupt internal files

That is practical.
It is still not one ordinary page answering:

> what is the least-destructive repair ladder here, what copy-safety proof is required before each rung, and which environment precondition must be fixed before retrying the product action?

### 4) Crash/evidence export truth is still hidden-path and support-mode shaped

Current official docs still say all of the following at once:

- v3 direct technical support is not available, so self-serve diagnosis matters more
- debug logging can be enabled in UI or by creating `debug.txt` in the storage folder
- restart is required to ensure logging is enabled and the docs recommend reproducing the issue for at least 15 minutes
- crash reports, dumps, and log locations vary by OS and by service account, and NAS dump collection can require SSH-driven ritual

That is honest.
It is still not one ordinary page answering:

> what evidence can I collect privately right now, what extra reproduction or restart is required, where did those artifacts come from, and when does this become a frozen packet for outside disclosure?

## What AnonSync should copy

AnonSync should copy the useful parts more boldly:

- concrete issue families instead of vague `sync problem` buckets
- candid environment-risk language for locks, SMB/direct mixed access, and watcher weakness
- least-destructive repair ladders rather than magical retry buttons
- explicit local evidence and crash-capture provenance

## What AnonSync should refuse to clone

AnonSync should refuse the exact current page contracts where:

- symptom meaning is split between list columns, warning links, and KB archaeology
- environment conflict truth depends on combining lock rows, hidden delay files, SMB caveats, and detection lore
- repair truth depends on memorizing article order instead of one product-owned ladder
- crash/evidence export still begins with discovering hidden paths or service-account-specific locations

## The replacement pages this revision adds

This revision therefore adds four ordinary replacement pages:

1. **Issue home** — what family this problem belongs to, what evidence floor already exists, and the first safe next action
2. **Environment conflict** — whether the issue is lock pressure, foreign-writer access, weak notifications, or mixed topology risk
3. **Repair plan** — the least-destructive repair ladder with copy-safety proof and environment preconditions
4. **Crash capture** — what local evidence exists, what additional capture needs restart or reproduction, and what may later be frozen for outside disclosure

## Result

The Resilio stance is now tighter again:

> borrow the candor and the repair pragmatism; refuse the article-scattered page contracts; replace each refusal with one ordinary page that makes health and repair truth local, exact, and reviewable.
