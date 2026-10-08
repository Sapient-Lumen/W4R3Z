# Prior-art reading notes

This revision used the four uploaded prior-art cubes as architecture lessons, not as police-domain sources.

## DelayBasin

Useful imports:

- `START_HERE.md`, `AGENTS.md`, `context-pack.json`, `frontier-ticket.json`, and `REVISION-RECEIPT.json` make reentry cheap.
- Revision receipts explain why a revision counted and prevent changelog prose from carrying all authority.
- Transfer ledgers distinguish what was adopted from what was explicitly not adopted.
- Quarantine lanes keep fertile but unsafe/speculative ideas visible without canonizing them.
- Non-negotiables protect level distinctions: practice, observation, mechanism, speculation, disagreement, quarantine.

PoliceMisconduct adaptation:

- Reentry surfaces are imported immediately.
- Quarantine is kept small.
- The archive-method vocabulary is translated into source, privacy, adjudication, and identity-control vocabulary.

## Theory-of-Everything

Useful imports:

- Status lanes distinguish bundle head, operational head, citation head, and scientific/current posture.
- Public-record-carrier and acquisition-protocol thinking maps well to court records, FOIA releases, POST lists, news, settlements, and video.
- Defeater and rollback ledgers are directly relevant: a corrected source, sealed record, identity mismerge, or collapsed outcome must propagate.
- Evidence severity discipline prevents a passed test or strong source from promoting claims beyond the exact field it supports.

PoliceMisconduct adaptation:

- `SURFACE-STATUS.json` separates scaffold/data/public states.
- `PUBLIC-RECORD-CARRIER-LEDGER.json`, `DEFEATER-LEDGER.json`, and `ROLLBACK-PROPAGATION-LEDGER.json` are first-class from rev0001.

## TriKEM

Useful imports:

- A claim surface can be much smaller than the full archive.
- Nonclaims are release-relevant, not afterthoughts.
- Evidence debt blocks public claim promotion.
- Public/buildable does not mean operationally ready; for this cube, public/source-found does not mean ethically displayable or adjudicated.
- Source locks and artifact contracts are the right model for fragile public records.

PoliceMisconduct adaptation:

- `CLAIM-SURFACE.json` and `NONCLAIMS.json` exist before data.
- `EVIDENCE-LADDER.json` blocks promotion until source, privacy, adjudication, and identity gates are satisfied.
- The first validation tool checks surface consistency rather than pretending to validate truth.

## Parables

Useful imports:

- A corpus can start as simple collected text plus scratchpad plus already-searched memory and still support hundreds of turns.
- Curation logs should preserve rejected candidates and reasons.
- Generated/synthetic material must be separated from collected/source material.

PoliceMisconduct adaptation:

- Future revisions should add searched-source and rejected-merge ledgers.
- Synthetic schema examples will be kept separate from real records.
- Curation memory is essential: rejected leads, dead links, insufficient matches, and non-publication decisions are part of the corpus state.

## Non-imported patterns

- The full DelayBasin witness-vocabulary explosion is too heavy for rev0001.
- TriKEM’s cryptographic CI complexity is not imported; only its claim/evidence posture is.
- Theory-of-Everything’s physics route semantics are translated rather than copied.
- Parables’ flat-file corpus style is not sufficient for person-level public-record data.
