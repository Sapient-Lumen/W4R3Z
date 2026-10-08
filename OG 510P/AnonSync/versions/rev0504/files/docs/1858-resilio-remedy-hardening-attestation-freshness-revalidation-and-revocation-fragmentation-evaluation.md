# Resilio remedy hardening attestation freshness, revalidation, and revocation fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still admirably candid that `a verifier bundle was once honest`, `the same bundle is still current enough now`, and `no later identity, approval, cache, or evidence-horizon change has weakened it` are not one flat truth.
That candor matters.

The strongest present ingredients are:

- current `Sync Main View (Desktop)` docs still say History shows only general syncing activity for the last 30 days and that peers offline for 7 days get disconnected by default
- current `Sync Private Identity & Linking My Devices` docs still say peer identity is tied to a certificate fingerprint, new identities are created by unlinking and recreating identity, remote users may automatically approve all linked devices for future sharing, and linked devices can auto-populate all folders
- current `Collecting debug logs manually` docs still say meaningful debug evidence requires enabling logging, restarting Sync, and letting it collect for at least 15 minutes
- current `Increasing Debug Log size` docs still say logs rotate, `sync.log` rolls into `sync.log.old`, and the existing rotated file is discarded at the next rotation
- current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` docs still say old peer cache can survive until peer expiration is forced to `0` and the client is restarted
- current `Resilio Sync change log` still says new installations switched WebUI certificates to SHA-256 and still records history-loss and duplicate-offline-peer fixes

## Where the current contract still fragments

The problem is not that Resilio lacks *time-sensitive ingredients*.
The problem is that it still lacks a first-class, case-scoped **attestation freshness and revalidation** object.

Today an operator can often infer only weaker truths such as:

- the bundle was sealed once
- the logs looked sufficient when captured
- history still exists for a short window
- the current identity name and fingerprint look familiar
- the peer cache was probably cleared eventually
- old approvals probably still mean something
- no obvious contradictory event is visible right now

Those are useful clues.
They are not the same as an explicit answer to `is this sealed verifier bundle still current enough, as of now, with identity, approval, cache, and evidence horizons rechecked, to support the strongest live sentence rather than only a historical one?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-seal claims than `the bundle is tamper-evident later`.
It needs to support claims such as:

- the bundle is still tamper-evident, but only as a historical proof because freshness horizon expired
- the seal still stands, but the stronger `current enough to trust now` sentence is blocked until identity, approval, and cache-sensitive facts are revalidated
- old operational evidence remains honest, but only as-of its capture time because history and logs have already rolled forward
- a new identity, relink, restart, or peer-expiration event forces revalidation rather than allowing stale verifier trust to coast forward
- the case is now not only sealed, but also freshness-bounded and revocation-aware for the required verifier cohort

AnonSync therefore needs a first-class object for **attestation freshness, revalidation, expiry, and revocation-aware claim ceilings** rather than merely borrowing history, logs, fingerprints, approvals, and cache-clearing folklore.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `is this sealed verifier bundle still current enough right now?` — only by making the operator combine several separately decaying operational surfaces:

- short-window History
- rotating logs with discard
- restart-gated debug capture
- peer identity fingerprints
- linked-device auto-approval and auto-population behavior
- peer-expiration and cache-clearing knobs
- old change-log memory about certificate or duplicate-peer behavior

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **remedy-hardening attestation freshness** directly.
Its interface family should let the product separate at least these truths:

- sealed historical bundle only
- sealed and fresh for named lanes only
- freshness horizon near expiry
- freshness expired but history still honest
- revalidation pending
- revalidation passed for required cohort
- revocation or identity challenge open
- freshness-aware verifier readiness collapsed

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-freshness contract sheet**, **Remedy-hardening-attestation-freshness review**, **Remedy-hardening-attestation-freshness proof**, **Remedy-hardening-attestation-freshness timeline**, and **Remedy-hardening-attestation-freshness lineage receipt**.
