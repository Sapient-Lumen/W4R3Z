# Resilio remedy hardening attestation observer integrity, witness provenance, and evidence-trustworthiness fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being unusually candid that `the UI looked calm`, `History did not show a problem`, `we have logs`, `we have a dump`, `we restarted and reproduced`, `we looked in the storage folder`, and `the resulting evidence set is strong enough to justify a present-tense conformance or breach sentence` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Collecting debug logs automatically` docs still say debug logging must be enabled, Sync must be restarted to make sure logging is enabled, the issue must be reproduced, and logs should be collected for at least 15 minutes afterward
- current `Collecting debug logs manually` docs still say large file sets may require increasing log size before capture, which is an explicit admission that the default evidence window may be too short
- current `Increasing Debug Log size` docs still say log rotation backs `sync.log` up to `sync.log.old` when the size threshold is reached and discards an existing old file at rotation time
- current `Sync Main View (Desktop)` docs still say History covers only the last 30 days and peer presence disappears after 7 days offline, which is an explicit horizon on surface-visible evidence
- current `Guide to Linux, and Sync peculiarities` docs still say Linux has no operating-system integration, notifications do not appear outside Sync UI, configuration is manual through a web interface, and multiple instances can be started if ports are assigned manually
- current `Sync Storage folder` docs still say configuration, auxiliary files, shares' database, and logs live in the storage folder, whose location depends on platform, service mode, launch location, or configured storage path
- current `Where to collect logs on NAS?` docs still say NAS log locations vary by vendor, container identifier, installation volume, and configured storage
- current `Collecting crash reports, mini-dumps and core dumps` docs still say dump locations vary by platform and by service user, and Linux dumps may land near the binary or in another directory depending on startup script
- current `Collecting core dump on NAS devices` docs still say capture can require stopping Sync from WebUI, switching to SSH, starting Sync from terminal instead of WebUI, waiting for another crash, and then moving the dump back into a downloadable location
- current `Resilio Sync change log` still records that some important information such as API key expiration was not mentioned in debug log and that several UI, detection, and migration issues have required fixes

## Where the current contract still fragments

The problem is not that Resilio hides evidence collection.
The problem is that it still does not produce one first-class, case-scoped **observer-integrity and evidence-trustworthiness** object.

Today an operator can often infer only weaker truths such as:

- debug logging was probably on after the restart
- a capture happened after reproduction for some amount of time
- one log survived rotation and another did not
- one calm desktop or WebUI surface showed no alarm inside its visible horizon
- one service user or one storage world was inspected
- one NAS dump was captured through a terminal path rather than the ordinary surface
- one changelog entry explains why a missing field or delayed detection might have affected the evidence

Those are useful clues.
They are not the same as an explicit answer to `is this witness set trustworthy enough, continuous enough, world-scoped enough, retention-complete enough, and blind-spot-bounded enough to justify the current conformance or breach sentence?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `we have fresh evidence`.
It needs to support claims such as:

- the witness is fresh, but capture protocol was incomplete because restart confirmation is missing
- the logs are present, but rotation may have discarded the earliest relevant evidence
- the observed UI is calm, but Linux notification and surface coverage leave an out-of-band blind spot
- the dump came from a sibling storage world or service user, so scope continuity is not proved
- the evidence is strong enough for a narrow slice or one world only, but not for the broader still-governing claim
- the absence of observed breach is weaker than a trusted observer set that would have been able to see the breach if it existed

AnonSync therefore needs first-class objects for **observer set, witness provenance, capture protocol completeness, world scope, storage-world continuity, retention horizon, rotation loss risk, blind-spot axes, tamper or mutation suspicion, evidence trust class, highest honest sentence, and blocked stronger sentence** rather than leaving operators to infer evidentiary strength from restarted logging, surviving files, calm surfaces, platform folklore, or manual dump workflows.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `do we trust this evidence set enough to say the stronger thing now?` — only by making the operator combine several partially overlapping mechanics:

- restart-gated debug enablement and reproduction windows
- rotating logs with bounded retention and discard behavior
- short-horizon history and disappearing peer visibility
- Linux and WebUI surface limitations
- storage paths that change with service user, platform, launch method, or configured storage
- NAS-specific or script-specific forensic collection branches
- changelog memory about what logs or UI did not previously expose

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **observer integrity, witness provenance, and evidence trustworthiness** directly.
Its interface family should let the product separate at least these truths:

- evidence present, protocol incomplete
- fresh witness from one world only
- retention or rotation gap blocks stronger sentence
- calm visible surfaces but blind-spot budget exceeded
- dump or log captured from sibling world only
- trusted witness for named slice only
- observer integrity under challenge
- evidence trust restored after fresh re-capture
- broader still-governing or breach-cleared sentence blocked
