# 275. Election data interoperability and schema registry (digest-first)

**Track:** Shared

This doc defines a **bounded** way to publish machine-readable election data schemas and mappings
*without* dumping sensitive configurations or voter-linked data.

## Why this exists

Election programs routinely need to move data across:
- ballot definition / ballot styles
- election management systems (EMS)
- scanners/tabulators
- election night reporting (ENR)
- audits (e.g., RLAs) and canvass reconciliation
- public releases (CVR / ballot images / results feeds)

Interoperability breaks most often at the boundaries, and “fixes” tend to become ad-hoc, hard to audit,
and hard to reproduce. NIST’s Voting **Common Data Formats (CDFs)** are an anchor here, especially:
- **Election Results Reporting (ERR) CDF** (SP 1500-100 / v2.0)  
  https://pages.nist.gov/ElectionResultsReporting/  
- **Implementation Guidance for CDFs** (NIST GCR 24-058)  
  https://nvlpubs.nist.gov/nistpubs/gcr/2024/24-058/NIST.GCR.24-058.html  

For broader “end-to-end election process” interoperability, OASIS **Election Markup Language (EML)**
is another reference point (often relevant in non‑US contexts):
https://www.oasis-open.org/standard/eml/

## The deliverable: Schema Registry Digest (SRD)

Publish a **Schema Registry Digest (SRD)** as a small, checkable artifact that points to authoritative
schemas and *declares* what your program actually uses.

**SRD should include (minimal):**
- `srd_id`, `election_id`, `jurisdiction_id` (see `262-jurisdictional-policy-surface-registry.md`)
- **Schema set**: `{name, version, canonical_uri, sha256, canonicalization}`  
  - canonicalization should follow `265-canonicalization-signing-timestamping-and-proof-packaging.md`
- **Profile**: what subset you actually use (bounded; no vendor secret sauce)
- **Mapping notes**: pointers to mapping docs + hashes (not raw mapping tables if sensitive)
- **Change linkage**: links to CommitLog entries (`261`) and Change Control Packets (`256`)
- **Release posture**: what’s public vs restricted, and the reason

### What to publish vs not publish

Publish (safe, useful):
- schema URIs + hashes
- transform tool version hashes (binary or container digest)
- “profile constraints” (field required/forbidden lists)
- aggregate validation outcomes (counts of pass/fail by category)

Do **not** publish by default:
- precinct/ballot-style assignment tables
- device identifiers or network topology
- per-voter / voter-linked transaction records
- anything that enables targeting of facilities or processes

When in doubt, route through:
- `253-public-records-requests-retention-and-access-bounds.md`
- `274-cvr-ballot-images-and-public-data-release-governance.md`

## Validation surface

A minimal, public validation surface can be:
- `SRD` (signed + timestamped via `265`)
- `ValidationDigest` (counts-only), e.g.:
  - number of files validated
  - number of schema violations by class
  - tool + ruleset hashes

This composes with:
- ENR snapshot packs (`252`)
- Canvass reconciliation ledgers (`251`, `273`)
- Audit Publication Packs (`260`)

## Stop conditions (anti-weaponization)

Stop and re-scope if a proposed “interoperability release” would:
- expose precinct/style mapping or operational targeting data
- expose voter identifiers or linkable transaction trails
- create an easy path to harass workers, intimidate voters, or disrupt operations
- publish vendor secrets under the guise of transparency (procurement + disclosure needs a lane)

## Primary anchors

- NIST Election Results Reporting CDF (SP 1500-100 / v2.0): https://pages.nist.gov/ElectionResultsReporting/
- NIST Implementation Guidance for Common Data Formats (NIST GCR 24-058): https://nvlpubs.nist.gov/nistpubs/gcr/2024/24-058/NIST.GCR.24-058.html
- EAC Election Results Reporting Quick Start Guide: https://www.eac.gov/sites/default/files/electionofficials/QuickStartGuides/Election_Results_Reporting_EAC_Quick_Start_Guide_508.pdf
- OASIS Election Markup Language (EML) standard: https://www.oasis-open.org/standard/eml/
