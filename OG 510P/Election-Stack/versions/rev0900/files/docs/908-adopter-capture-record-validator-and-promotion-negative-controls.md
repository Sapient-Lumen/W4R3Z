# rev0870 adopter capture-record validator and promotion negative controls

**Track:** Shared / adopter readiness / public-answer promotion safety / verifier drift control  
Status: synthetic release-maintenance artifact  
Release date: 2026-06-10

## What changed

rev0869 made quarantined state/local rows into an adopter authority-capture no-go queue. rev0870 makes the next step machine-checkable: capture records now have a deterministic validator and negative-control fixtures.

New files:

- `tools/adopter_capture_record_validator.py`
- `scripts/check_adopter_capture_record_validator.py`
- `artifacts/examples/adopter_authority_capture_records/README.md`
- `artifacts/examples/adopter_authority_capture_records/valid-shape-no-promotion.synthetic.json`
- `artifacts/examples/adopter_authority_capture_records/negative/*.json`
- `artifacts/reports/adopter-capture-record-validation-report.json`

The validator checks capture-record shape before any quarantined state/local source can be considered for public-answer promotion. It requires the same core evidence as the adopter capture matrix: capture id, UTC capture time, capture role, source URL or official-channel id, byte/text SHA-256, responsible office, human help route, jurisdiction scope, election/effective-date scope, conflict-check closure, human approver role, and approval time.

## Negative controls added

The fixture set intentionally exercises failures that would be dangerous in a live promotion path:

| Fixture | Expected failure |
|---|---|
| `invalid-missing-hash.json` | Missing or invalid byte/text SHA-256 |
| `invalid-global-scope.json` | Global/cross-jurisdiction scope instead of adopter-local scope |
| `invalid-no-human-approval.json` | Missing human approver role |
| `invalid-nonquarantined-source.json` | Capture record points at a source outside the quarantined state/local set |
| `invalid-synthetic-promotion-allowed.json` | Fixture tries to set `promotion_allowed=true` inside a synthetic archive |

The one shape-valid fixture is deliberately non-promoting: it demonstrates the required fields while keeping `promotion_requested=false` and `promotion_allowed=false`.

## Go/no-go integration

The release go/no-go pack now includes the capture validator in the offline drill and current-signal summary. It also stops saying the current-authority no-go is only about due-soon source-review rows. The 30-day source-review queue is currently zero, but public-authority reliance is still no-go until relevant sources are refreshed/pinned or backed by valid adopter capture records and human approval.

Current validator result for this synthetic archive:

| Measure | rev0870 |
|---|---:|
| Capture-record fixtures | `6` |
| Negative fixtures | `5` |
| Shape-valid fixture records | `1` |
| Fixture expectation failures | `0` |
| Shape-valid records authorizing promotion | `0` |
| Missing adopter captures in matrix | `70` |

## Why this is a practical risk cut

Before this pass, an adopter operator could see the required fields but had no executable way to reject bad capture records. That left a dangerous seam: a malformed record with a missing hash, broad jurisdiction scope, no human approval, or synthetic promotion flag could be copied into a future workflow and look plausible.

rev0870 closes that seam with code and fixtures rather than more doctrine. The release gate now fails if the validator report is stale, if negative fixtures stop failing for expected reasons, or if any shape-valid shipped record authorizes public guidance in the synthetic archive.

Boundary: rev0870 remains synthetic-only. Capture-record validation checks evidence shape only. It is not current voter instruction, legal advice, source-byte cache completeness, accessibility certification, independent validation, production signer authority, public-release authorization, certification, or live-pilot approval.
