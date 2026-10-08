# Resilio remedy hardening attestation integrity, tamper evidence, and verifier-seal fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still admirably candid that `evidence exists`, `evidence can be collected`, `evidence can be exported`, and `the same exported evidence is tamper-evident later` are not one flat truth.
That candor matters.

The strongest present ingredients are:

- current `Sync Storage folder` docs still say the storage folder holds current configuration, auxiliary settings files, shares' database, dumps, and logs
- current `Collecting debug logs automatically` docs still say debug logging can be enabled from settings or by creating `debug.txt` with `FFFFFFFF` in the storage folder, and then requires restart plus timed issue reproduction
- current `Increasing Debug Log size` docs still say logs rotate normally, `sync.log` rolls into `sync.log.old`, and existing rotated material is discarded at the next rotation
- current `Running Sync in configuration mode` docs still say `sync.conf` is an editable JSON file placed in the storage folder or launched by command-line parameter, and that storage path itself can be redirected
- current `Running Sync as a service on Windows` docs still say service install can migrate settings or instead do a clean installation, and config mode for the service works by placing `sync.conf` into the service storage folder and restarting
- current `Cloning Sync` docs still say plain copying or drive-cloner copying of a Sync instance is unsupported and can lead to strange behavior instead of clean state continuity

## Where the current contract still fragments

The problem is not that Resilio lacks *bytes*.
The problem is that it still lacks a first-class, case-scoped **attestation-integrity** object.

Today an operator can often infer only weaker truths such as:

- a storage copy exists
- a log pack exists
- debug logging was probably enabled in time
- a service world or clean install branch was taken
- a config file was exported
- a later verifier received the bundle
- the copied state looks plausible
- no obvious contradiction has appeared yet

Those are useful clues.
They are not the same as an explicit answer to `is this verifier-ready bundle itself tamper-evident, custody-preserved, and still strong enough that later edits, rotations, copies, or clone-like state handling cannot silently impersonate the stronger sentence?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-verifier claims than `a later verifier can probably inspect this bundle`.
It needs to support claims such as:

- the bundle is verifier-ready, but the stronger `tamper-evident verifier-ready` sentence is still blocked because provenance remains operator-shaped
- the evidence was exported, but ordinary mutable storage and log rotation still cap the claim ceiling
- a successor received the package, but seal breakage or custody ambiguity still blocks the stronger sentence
- the case is now not only independently verifier-ready but also sealed tightly enough that later alteration attempts become explicit first-class events

AnonSync therefore needs a first-class object for **attestation seal, bundle integrity, and custody-preserved verifier readiness** rather than merely borrowing storage, logs, config files, restart workflows, and unsupported clone warnings.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `is this exported verifier bundle itself tamper-evident and custody-preserved later?` — only by leaving the operator to reason across several mutable operational surfaces:

- storage-folder copies
- editable config files
- debug toggles placed in storage
- restart-driven support logging
- rotating and discarded old logs
- service-world storage forks
- migrate-versus-clean-install branching
- unsupported plain-copy cloning

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **remedy-hardening-attestation integrity** directly.
Its interface family should let the product separate at least these truths:

- verifier-ready bundle present
- verifier-ready bundle sufficient but unsealed
- seal drafted but not yet activated
- sealed for named lanes only
- custody-preserved and tamper-evident for required verifier cohort
- integrity challenged or seal broken
- attestation collapsed because integrity floor failed

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-integrity contract sheet**, **Remedy-hardening-attestation-integrity review**, **Remedy-hardening-attestation-integrity proof**, **Remedy-hardening-attestation-integrity timeline**, and **Remedy-hardening-attestation-integrity lineage receipt**.
