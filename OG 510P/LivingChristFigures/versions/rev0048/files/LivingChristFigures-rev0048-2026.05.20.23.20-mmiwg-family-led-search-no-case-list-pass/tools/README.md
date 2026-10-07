# tools

`qa_cube.py` runs package-level structural checks for rev0024+ packages:

```bash
python tools/qa_cube.py .
```

It checks no archive directories or bundled zips, required front matter, current ledger/index counts, public/longform infrastructure files, live-referral safety fields, final SHA256SUMS verification, and rev0025+ identity-coherence checks across candidate front matter, Candidate-Ledger, Claim-Ledger, Evidence-Debt, public index, Candidate-Index, and CUBE-MAP labels.

rev0026 adds checks for candidate office_ids pointing to existing office cards, claim source IDs pointing to Source-Registry rows, duplicate source IDs, and duplicate candidate IDs.

rev0027: qa_cube.py now checks source candidate references, evidence-debt candidate references, refresh related-candidate references, source seen-in-files paths, and front-matter office_ids agreement.


`redaction_scan.py` was added in rev0030:

```bash
python tools/redaction_scan.py . --write-report --fail-on-high
```

It scans the working cube for configured public-export hazards: contact digits near helpline/hotline/toll-free/contact language, email-like strings, exact coordinate pairs, address-like strings, and grave/case/Medical-Examiner-number-like identifiers. It is deliberately conservative about operational digits and deliberately incomplete about narrative privacy; manual review remains required.

rev0030: qa_cube.py now calls the redaction-risk scan and fails on open configured high-risk findings.

## schema_validate.py

Added in rev0031. Validates the schema/contract layer:

```bash
python tools/schema_validate.py . --write-report --fail-on-high
```

It checks front-matter contracts, ledger headers, CSV/JSON mirror parity,
source-type controlled vocabulary, and public-manifest revision agreement.
`tools/qa_cube.py` imports and runs this validator as part of normal QA.

## evidence_lifecycle.py

Added in rev0032. Generates `META/Claim-Evidence-Strength-current.*` and `META/Refresh-Priority-Queue-current.*`. These reports route refresh/caution labor; they are not truth scores.

Usage:

```bash
python tools/evidence_lifecycle.py . --write-report
```


## rev0033 meta-instrument checks

`qa_cube.py` now also checks that the negative-case ledger, online-research intake, and operator-update audit files exist, have unique IDs, and contain the fields needed for behavior-change/source-promotion review.

## rev0034 QA extensions

`qa_cube.py` now checks the source-promotion decision ledger, public-claim quarantine, refresh-sprint matrix, and rules 31-32 coverage. It also verifies that quarantine claim IDs are drawn from lifecycle rows classified as `now_or_before_any_public_claim`.


## rev0035 QA extensions

`qa_cube.py` now checks the source-promotion transaction audit, public-claim release ledger, and rule 33 coverage. It also verifies that released claims are not still present in `META/Public-Claim-Quarantine-current.*` and that release source IDs exist in `Source-Registry-current.csv`.


## rev0036 QA extensions

`qa_cube.py` now checks boundary-rule coverage through rule 34. Rev0036 promotes a counterevidence source without releasing any public current-capacity claim, so QA continues to require transaction source IDs to exist and quarantine coverage to match lifecycle-now claims.


## rev0037-0038 QA extensions

rev0037 checks boundary-rule coverage through rule 35 for conflict-zone mutual-aid no-map gates. Rev0038 extends boundary-rule coverage through rule 36 for border counterpressure / no-route observation gates.


## rev0039 QA extensions

rev0039 extends boundary-rule coverage through rule 37 for survivor-service standards/funding no-referral gates.

## rev0040 QA addition
QA now expects boundary-rule coverage through rule 38, the family-led missing-person search / no-field-map rule.


## rev0041 QA note

`qa_cube.py` now requires boundary-rule coverage through rule 39, including the protection-order / legal-framework is not a survivor-service door rule.


## rev0041 lifecycle note

`evidence_lifecycle.py` now treats explicit public-claim quarantine rows as safety overrides, keeping those claims in the now-or-before-public-claim lane even when new source counts would otherwise lower derived freshness risk.
