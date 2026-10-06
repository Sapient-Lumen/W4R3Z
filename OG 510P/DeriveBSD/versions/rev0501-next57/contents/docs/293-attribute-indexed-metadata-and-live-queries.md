# Attribute-indexed metadata and live queries (Haiku/BeOS BFS lessons)

Some ecosystems treat “files are just bytes” as a leaky abstraction and instead make **metadata** a first-class substrate.
Haiku (and historically BeOS) uses BFS attributes + indexes to enable *database-like* queries directly over filesystem metadata.

DeriveBSD already cares about **origin labels**, **quarantine**, **evidence receipts**, and **portable capabilities**.
The BFS lesson is: *make the metadata queryable and subscribe-able early*, or the ecosystem will reinvent ad-hoc scanners and fragile conventions.

## Prior art (what BFS got right)

BFS supports:
- arbitrary per-file attributes stored alongside file data
- optional indexes over chosen attributes
- queries that can be *fast* because they hit indexes rather than scanning directories
- “live queries” (a saved query can behave like a dynamic folder)

References:
- Haiku “Mastering queries” overview (attributes + query workflows): https://www.haikuinsider.org/mastering-queries
- Ars Technica retrospective on BFS querying: https://arstechnica.com/information-technology/2018/07/the-beos-filesystem/
- Dominic Giampaolo, *Practical File System Design with the Be File System* (attributes/indexing/query model): https://nobius.org/~dbg/practical-file-system-design.pdf

## Why this matters for DeriveBSD

DeriveBSD already introduces metadata concepts that will otherwise be *folklore*:

- origin labels and quarantine metadata (`docs/280-origin-labels-and-quarantine-attributes.md`)
- persistent file capabilities / bookmarks (`docs/198-persistent-file-capabilities-bookmarks.md`)
- evidence objects that must be searchable during incidents (`docs/229-evidence-spine-overview.md`)

If we don’t provide a first-class query substrate, we’ll get:
- brittle “scan the disk for JSON sidecars” tools
- silent metadata loss (“origin laundering”)
- weak incident ergonomics (“find all files imported from USB before X” becomes heroics)

## DeriveBSD direction: make metadata queryable *without* making it ambient

The BFS trap is that “powerful query” can become *ambient* and privacy-invasive.
DeriveBSD should treat metadata search as **capability-gated**.

### 1) A narrow set of blessed attribute classes

Start with the metadata that is already security-relevant:
- `origin.*` (source URL/device/share, import receipt digest)
- `quarantine.*` (state machine: imported → sanitized → promoted)
- `cap.bookmark.*` (persistent file capability ids)
- optional: `evidence.ptr.*` (links to evidence objects relevant to this file)

Everything else is opt-in by policy. In particular, **full-text body text from foreign-derived inspection artifacts is not a blessed baseline metadata class** just because OCR/searchable reconstruction exists; `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md` now fixes that workstation-side boundary explicitly.

### 2) Dual-layer storage: xattrs for locality, CAS objects for durability

This is now the accepted boundary (`docs/484-origin-label-authority-and-anti-laundering-boundary.md`):
- store the **minimal** security-critical labels as filesystem xattrs (fast, local UX)
- treat those labels as a local **pointer/cache** only
- store the **authoritative** metadata records as CAS objects referenced by digest
  - the xattr carries the digest pointer
  - exported bundles can carry the CAS objects with stable digests
  - query indexes remain **derived surfaces**, never the provenance authority itself

This helps with:
- preserving metadata across moves/copies/exports (`docs/253-bundle-plans-and-deterministic-exports.md`)
- making “what did this label mean?” answerable during incidents

### 3) An indexer service that emits snapshots as evidence

Instead of “the filesystem is the database”, prefer:
- a small, sandboxed indexer that watches *only blessed paths*
- emits an indexed **snapshot** object (a digestable map from attribute→file ids)
- consumes authoritative `content.origin` digests plus current label pointers
- can be verified and included in incident bundles

This makes the index:
- explicit (it can be enabled/disabled)
- auditable (snapshots are signed / receipted)
- reproducible-ish (index content is derivable from file metadata)

### 4) Queries and subscriptions are portals

Queries can leak a lot.
Treat them like other mediated operations:
- a “metadata query portal” returns results bound to an approval/grant
- a “live query subscription” is a lease (timeboxed, revocable)

This mirrors the networking/export/remote-assistance posture:
- no ambient authority
- everything has a receipt trail

## Concrete “greenfield” wins

- **Origin dashboards:** “show me all files from USB device X not yet sanitized.”
- **Policy linting:** alert if an origin label is missing/stripped where required.
- **Incident triage:** “list all artifacts that executed unverified binaries” can join evidence receipts with file origin pointers.
- **Safe sharing:** exports can include a deterministic selection of files *plus* their label/evidence context.

## First concrete lane: removable-media post-detach query projection

r507 makes the caution above executable for the first host-local removable-media fallback. The lane now carries `typed-post-detach-query-projection-positive-and-negative-fixture-guarded` and `known-bad-query-projection-shapes-must-fail-validation` through `spec/removable.media.local.post_detach.query.projection.schema.json`.

The projection is deliberately not the authority. It is a `derived-snapshot-not-authority` surface behind `lease-required-no-ambient-index-read`; authoritative receipt digests remain the join points. The first projection excludes raw media paths, observed attach hints, device labels/serials, host paths, host user/home identity, untrusted filenames, and body text. That keeps queryability useful for incident/support workflows without turning receipt search into ambient telemetry.

## Open questions

- Where do we store attributes on non-ZFS filesystems (or inside AppVM disks) while preserving policy semantics?
- How do we prevent “metadata laundering” by apps that rewrite files without copying labels?
- What is the minimum query language that is useful without becoming an ambient data-exfil surface?

See also: `docs/266-open-questions-and-risk-register.md`.

## r508 redacted export bundles

r508 extends the removable-media queryability rule from indexes into support and incident handoff: `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded` keeps raw debug bundles from bypassing the redacted projection. Exportable evidence starts from a lease-bound query projection plus digest references, not from raw receipt payloads or raw index state.



## Removable-media tombstone note

For the removable-media local fallback, `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded` makes stale query handles an explicit denial case. Query indexes may expose a redacted tombstone reason and digest subject, but they must not keep a live subscription, raw locator, raw path, host identity, recipient text, or full-text payload alive after revocation.


## r510 stale-handle denial receipts

r510 adds `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded` so the index treats stale-handle denial receipts as observation authority. The index may expose redacted digest/reason-code denial summaries, but raw handle values, raw locators, original filenames, host identity, recipient text, receipt payloads, and body text remain out of searchable metadata.

## r511 fresh-authority receipts

r511 adds `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` so the metadata/query layer can represent renewed access without resurrecting stale handles. A fresh-authority receipt is searchable only as redacted digest/purpose/fresh-lease evidence; raw handles, locators, filenames, host identity, recipient text, body text, and receipt payloads remain outside the index.

Last updated: 2026-05-25r520
## r512 fresh-authority consumption receipts

r512 adds `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded` so the metadata/query layer can represent fresh-authority consumption without turning a fresh lease into a reusable renewal token. Fresh-authority consumption is searchable only as redacted digest/purpose/consumed-once evidence; raw handles, locators, filenames, host identity, recipient text, body text, and receipt payloads remain outside the index.

## r513 removable-media successor-index cutover

`typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded` treats the r512 successor-index update as observation authority. Fresh successor rows are not live merely because a consumption receipt names them; `removable.media.local.post_detach.successor.index.cutover.receipt` must prove old tombstoned rows are terminal, exact successor rows are live, no dual-active window or rollback exists, and raw locator, filename, host identity, full-text, receipt-body, recipient, and secret values stay out of the query projection.


## r514 removable-media successor-index checkpoint

`typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded` treats post-cutover checkpoint state as observation authority. A query/export/rehydration broker may expose only a digest-purpose checkpoint summary and must reject any index root below the checkpoint sequence, restored old-handle root, or dual-active snapshot. The successor-index checkpoint keeps raw locators, filenames, host identity, full text, receipt bodies, recipient text, and secret values out of the searchable projection.

## r517 removable-media reader-use ledger

`typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded` treats the reader-use ledger root as observation authority too. After r516 reader use, a broker may release a result only after `removable.media.local.post_detach.reader.use.ledger.receipt` commits the debit to a monotonic compare-and-swap ledger root. The ledger projection is digest/root/sequence/budget evidence only: no raw locator, filename, host identity, full text, body text, recipient text, raw receipt payload, live subscription, or secret-bearing state may become searchable metadata.

Last updated: 2026-05-25r520
## r515 removable-media reader admission

`typed-post-detach-reader-admission-positive-and-negative-fixture-guarded` treats reader admission as observation authority. After the successor-index checkpoint, a query/export/rehydration broker may act only after `removable.media.local.post_detach.reader.admission.receipt` proves it observed the checkpoint digest, marker, sequence, and accepted root for one exact successor subject. The reader-admission projection remains digest-and-purpose only: no raw locators, filenames, host identity, full text, receipt bodies, recipient text, live subscriptions, or secrets are admitted into the searchable surface.

## r516 removable-media reader use

`typed-post-detach-reader-use-positive-and-negative-fixture-guarded` treats each admitted reader use as observation authority. After r515 admission, a broker may return only the redacted result described by `removable.media.local.post_detach.reader.use.receipt`: one use sequence, one budget debit, one result digest, and one projection digest. Admission alone is not a reusable search token, live subscription, export path, raw locator lookup, filename lookup, body/full-text query, host-identity query, or secret-bearing debug view.

## r518 removable-media reader-use ledger retention

`typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded` treats ledger retention as query authority. Reader-use ledger rows may be compacted only into redacted, bounded summaries with proof carry-forward; future queries must use the compacted root and must not recover raw paths, filenames, body/full text, host identity, or secret material from retention state.
## r519 removable-media reader-use ledger retention expiry

The metadata/query surface now treats expired compacted roots as denied-or-fresh-authority-only. `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded` prevents a retained ledger summary from becoming a silent, indefinite observation index after the r518 retention window closes.

## r520 removable-media reader-use ledger retention expiry enforcement

The metadata/query surface now treats post-expiry attempts as denial evidence rather than search authority. `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded` allows only digest-level enforcement summaries: expired root, denial digest, rate-limit debit, and fresh-authority requirement. Raw handles, locators, filenames, host identity, body/full text, receipt payloads, and secret material remain outside the index.

Last updated: 2026-05-25r520
