# 553 — Nuclear emergency preparedness: synthetic payload intake dry run, hash/custody/redaction QA and loss-cap proof

## Revision

`rev0346` adds a synthetic event-day payload drill on top of the rev0345 packout filesystem. It does not import real Beaver Valley exercise evidence and it does not make any real readiness or unreadiness claim.

## Main correction

Rev0345 created the 60-packet packout filesystem and materialized the `raw/`, `redacted/`, `custody/`, and `qa/` subfolders. That fixed the physical folder problem, but it still left an unproven operational question: can the cube ingest payload-like files, hash them, pair original and redacted surrogates, record custody, run QA, classify the packet state, and still refuse automatic readiness credit?

Rev0346 answers that with a synthetic payload drill. Twenty-four high-risk packets are populated with deliberately marked synthetic artifacts. Each seeded packet has an original payload, a redacted/public-safe surrogate, a custody record, and a QA/adjudication note. The payloads cover alert authority, PAR/PAD, CAP lineage, EAS/WEA, field receipt, public information, call-center feedback, action uptake, AFN movement, CRC/decon, first receivers, dose/field monitoring, ingestion, sustainment, cyber/data, lifelines, COP/handoff, and exercise realism.

## Hard claim boundary

A folder, README, placeholder, label, synthetic payload, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, redacted surrogate, warroom row, owner acknowledgement, packet skeleton, or complete-looking local packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

The only states admitted by the rev0346 intake validator are:

- `rejected_closure_attempt`
- `hold_no_upgrade`
- `candidate_for_adjudication_not_closure`
- `accepted_reopen_signal`
- `context_no_upgrade`

There is still no `auto_close`, `ready`, `green`, `passed`, `sufficient`, `certified`, or `closed` state.

## Synthetic payload scope

The seeded payloads are useful for testing the mechanics of:

1. original-file hashing,
2. redacted-surrogate pairing,
3. custody-form presence,
4. QA/adjudication note presence,
5. packet classification,
6. loss-cap retention for unseeded packets,
7. public-claim release blocking,
8. SQLite query views for intake triage.

They are not evidence that any real alerting authority, evaluator, controller, EOC, EOF, JIC, public warning system, CRC, hospital, lab, utility, or county performed successfully.

## Operational result

The 60-packet board now has three distinct payload states:

- 24 packets are `synthetic_payload_loaded_not_real_evidence`.
- 36 packets are still `no_payload_loaded`.
- 0 packets are ready to claim.

The loaded packets are deliberately distributed across the highest-risk branch gates so the scanner is not merely proving one happy-path case. Several synthetic packets carry reopen or hold states, such as nonreceipt, broken public link, lifeline insufficiency, stale COP, and controller/simcell artificiality.

## Query route

The intended route is now:

`event-day folder skeleton → synthetic/local payload files → sha256 index → redaction pair check → custody and QA check → intake classification → loss-cap board → adjudication docket → CAP/retest/verifier → integrated claim kernel`

## Missing real evidence

The revision remains `REAL_BVPS_PUBLIC_ONLY`. No real/anonymized June 2026 exercise packets have been imported. Any future real packet must pass the same intake gates but must be clearly separated from synthetic drill files.
