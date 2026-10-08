# Resilio remedy hardening attestation corroboration and independent-plane fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still admirably candid that one visible surface is not the whole truth.
That candor matters.

The strongest present ingredients are:

- current `Sync Main View (Desktop)` docs still say History shows only general syncing activity for the last 30 days and the bell is only a notification surface
- current `Configuring WebUI` docs still say WebUI is its own rendering surface and is the default UI on Linux, NAS, and Windows service installs
- current `Sync Storage folder` docs still say the storage folder contains configuration, identity details, databases, dumps, and logs
- current `Collecting debug logs manually` and `Collecting debug logs automatically` docs still say useful log evidence often requires enabling debug logging, restarting Sync, reproducing the issue, and waiting at least 15 minutes
- current `Running Sync as a service on Windows` and `Sync Service Troubleshooting on Windows` docs still say changing service user or storage world can produce a different storage root and can require re-adding or reconnecting folders
- current `Resilio Sync change log` still says visible surfaces sometimes needed fixes for stale or blank UI behavior, missing progress, duplicate offline peers, and other presentation or state-reporting problems

## Where the current contract still fragments

The problem is not that Resilio lacks *evidence planes*.
The problem is that it still lacks a first-class, case-scoped **cross-plane corroboration** object.

Today an operator can often infer only weaker truths such as:

- the main UI looked calm
- the WebUI looked similar
- the storage folder seems present
- the logs seemed plausible once collected
- the service world probably matches the app world
- the current world probably still reflects the same share state
- no obvious contradiction appeared across the surfaces an operator happened to check

Those are useful clues.
They are not the same as an explicit answer to `is the strongest verifier sentence corroborated across independent evidence planes, or is it still resting on one dominant surface with the others only loosely suggestive?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-seal claims than `a fresh sealed bundle exists`.
It needs to support claims such as:

- the bundle is sealed and current, but still only single-plane credible
- the UI and storage planes agree, but the runtime/log plane has not yet corroborated the stronger sentence
- the storage plane and log plane agree, but the presentation plane is stale enough that the stronger consumer-facing sentence stays blocked
- the service world and app world disagree, so the corroborated sentence collapses back to a weaker floor
- the case is now not only sealed and fresh, but also independently corroborated across the required evidence planes

AnonSync therefore needs a first-class object for **attestation corroboration, plane diversity, independence scoring, contradiction handling, and claim ceilings** rather than merely borrowing scattered UI, WebUI, storage, service, log, and changelog surfaces.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `is this strong verifier sentence corroborated across independent planes rather than merely not-yet-contradicted?` — only by making the operator combine several partially overlapping operational surfaces:

- short-window History and bell signals in the desktop UI
- a separate WebUI rendering surface
- storage-folder state, databases, logs, and config
- restart-gated debug capture workflows
- service-user and storage-world branching
- change-log memory about stale, blank, or fixed visible surfaces

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **remedy-hardening attestation corroboration** directly.
Its interface family should let the product separate at least these truths:

- single-plane fresh bundle only
- two-plane corroborated for named lanes only
- required plane missing
- plane contradiction open
- same-world corroboration only
- cross-world corroboration pending
- corroborated for required verifier cohort
- corroboration collapsed

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-corroboration contract sheet**, **Remedy-hardening-attestation-corroboration review**, **Remedy-hardening-attestation-corroboration proof**, **Remedy-hardening-attestation-corroboration timeline**, and **Remedy-hardening-attestation-corroboration lineage receipt**.
