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

## Open questions

- Where do we store attributes on non-ZFS filesystems (or inside AppVM disks) while preserving policy semantics?
- How do we prevent “metadata laundering” by apps that rewrite files without copying labels?
- What is the minimum query language that is useful without becoming an ambient data-exfil surface?

See also: `docs/266-open-questions-and-risk-register.md`.

Last updated: 2026-03-22r386
