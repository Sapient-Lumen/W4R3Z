# Resilio remedy hardening attestation, verifier-ready evidence, and handoff fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still admirably candid that `the current world looks safe`, `a fresh world can probably be rebuilt`, and `an outside reviewer can independently verify that claim later` are not one flat truth.
That candor matters.

The strongest present ingredients are:

- current `Sync Main View (Desktop)` docs still say History shows only general syncing activity for the last 30 days and the bell is a notification surface rather than a full attestation ledger
- current `Sync Storage folder` docs still say settings, auxiliary files, shares' database, dumps, and logs all live in the storage folder
- current `Collecting debug logs automatically` docs still say debug logging must be turned on, Sync must be restarted, the issue must be reproduced, and logs should keep collecting for at least 15 minutes
- current `Collecting debug logs manually` docs still say support evidence lives in named log files in the storage folder and that the service world has its own storage location
- current `Increasing Debug Log size` docs still say log rotation is ordinary operational behavior with a default 100 MB log size and replacement of older rotated material
- current `Running Sync in configuration mode` docs still say Sync can apply pre-configured parameters at startup on a number of machines, but only for Standard folders
- current `Running Sync as a service on Windows` docs still say a service install can migrate settings or instead perform a clean installation that requires folders to be re-shared and reconnected

## Where the current contract still fragments

The problem is not that Resilio lacks *evidence*.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening-attestation** object.

Today an operator can often infer only weaker truths such as:

- the main UI looks calm right now
- a short history exists
- a storage folder can be copied
- some logs were collected for support
- a startup recipe exists
- a service world or clean install was made to work
- the rebuilt world seems equivalent
- the hardening claim is probably portable to the next operator

Those are useful operational clues.
They are not the same as an explicit answer to `could an independent verifier or successor operator inspect one durable bundle and honestly confirm the strongest supported hardening sentence without folklore, missing logs, or current-world memory?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-bootstrap claims than `the baseline is safe now and reproducible later`.
It needs to support claims such as:

- the baseline is safe and bootstrap-reproducible, but the stronger `independently verifier-ready` sentence is still blocked because key evidence depends on volatile current-world surfaces
- a successor can inspect the claim bundle, but only for named lanes because history horizon, log provenance, or folder-type coverage still cap the sentence
- support-style logs were gathered, but the stronger attestation sentence remains blocked because operator-controlled capture timing leaves too much ambiguity
- the rebuilt world is honest, but attestation is still blocked until invariants, scars, blocked stronger sentences, and evidence expiry are exported together
- the hardened baseline is now not only reproducible but independently attestable through one portable receipt-and-proof bundle

AnonSync therefore needs a first-class object for **verifier-ready safety attestation and handoff evidence** rather than merely borrowing logs, storage, history, config, and support workflows.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `can someone other than the current operator independently verify this hardened and reproducible baseline later?` — only by making the operator combine several operational surfaces:

- short-window History
- notification surfaces
- storage-folder copying
- optional debug logging
- restart-and-reproduce support workflows
- rotating log-size behavior
- startup configuration files
- service migrate-versus-clean-install branches

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **remedy-hardening attestation** directly.
Its interface family should let the product separate at least these truths:

- current-world-safe
- bootstrap-reproducible
- evidence bundle present
- evidence bundle verifier-ready for named lanes only
- successor-handoff-safe with scars preserved
- independently verifier-ready for the required cohort
- attestation stale, challenged, or collapsed

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation contract sheet**, **Remedy-hardening-attestation review**, **Remedy-hardening-attestation proof**, **Remedy-hardening-attestation timeline**, and **Remedy-hardening-attestation lineage receipt**.
