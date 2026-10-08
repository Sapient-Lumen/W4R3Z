# Structural audit — rev0376

## Highest-risk issue worked

The post-exercise acquisition path was still vulnerable to a term mismatch. A current public Columbiana County plan says WENS was replaced with ENS in Revision 38, while the proofcut language needs to cover ENS/IPAWS/EAS/WEA/siren/public-warning evidence. Requests that say only IPAWS or old WENS language could miss live exercise logs and after-action records.

Rev0376 adds a terminology alias gate and two sharper packets that ask specifically for exercise-day ENS/IPAWS messages, logs, failures, exceptions, CAP/retest items, screenshots/reports, and withheld-record indexes.

## Derived-table defect fixed

Before rev0376:

- `cube/index.csv` had 583 rows, ending at file 582.
- `cube/file.csv` had 580 rows and omitted files 580, 581, and 582.
- `cube/file-field-value.csv` and `cube/file-tag-edge-normalized.csv` also had stale tail coverage.

Rev0376 regenerates the derived file tables from `cube/index.csv` and adds row 583 for this revision. The new audit files record the before/after counts.

## Evidence posture

The current plan, route pages, public-records portal, request packets, and dispatch payloads are acquisition controls. They are not exercise performance evidence and cannot close readiness proofcuts.

## Remaining blockers

- No official FEMA Region 3 preliminary findings packet has been imported.
- No official FEMA Region 5 / Ohio / Columbiana 11:00 results packet has been imported.
- No response packet with custodian, hash, DLP status, proofcut mapping, and adjudication has been imported.
- No EOF EN58200 repair/retest/CAP proof has been imported.
