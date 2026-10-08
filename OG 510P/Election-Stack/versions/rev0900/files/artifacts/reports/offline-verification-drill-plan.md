# Offline verification drill plan

Archive version: `v900`  
Synthetic-only. This drill plan is not live election evidence, not certification, and not legal advice.

The goal is to prove that a reviewer can verify the carrier ZIP, safely extract it, recheck the manifest, and inspect the synthetic Example County outputs without network access.

## Steps

### `OVD-001`

```bash
python3 scripts/verify_release_zip.py /path/to/The-Election-Stack-rev0900-YYYY.MM.DD.HH.MM-codename.zip
```

Expected result: PASS release ZIP verified; version and manifest counts match the carrier.

Evidence output: terminal transcript or release maintainer handoff record

### `OVD-002`

```bash
python3 scripts/extract_release_zip.py /path/to/The-Election-Stack-rev0900-YYYY.MM.DD.HH.MM-codename.zip /tmp/election-stack-v900-extract
```

Expected result: PASS safe extraction into a new concrete directory; no symlink or traversal side effects.

Evidence output: extractor transcript plus extracted tree path

### `OVD-003`

```bash
python3 scripts/verify_manifest.py /tmp/election-stack-v900-extract
```

Expected result: PASS extracted tree matches MANIFEST.sha256.

Evidence output: manifest-verifier transcript

### `OVD-004`

```bash
python3 tools/example_county_output_pack.py --json
```

Expected result: PASS JSON reports the current v900 synthetic scenario and packet count.

Evidence output: artifacts/examples/example_county_2026_municipal_pilot/evidence-map.json

### `OVD-005`

```bash
python3 tools/example_county_negative_control_runner.py --json
```

Expected result: PASS only when temporary tampered packets fail with expected public problem codes.

Evidence output: artifacts/examples/example_county_2026_municipal_pilot/negative-control-report.json

### `OVD-006`

```bash
python3 tools/release_go_no_go_pack.py --json
```

Expected result: GO for synthetic release; NO-GO for live pilot, certification, current-authority, and legal-use claims.

Evidence output: artifacts/reports/release-go-no-go-decision.json

### `OVD-007`

```bash
python3 tools/redaction_publication_pack.py --json
```

Expected result: PASS JSON reports the current synthetic redaction/publication no-go matrix and policy count.

Evidence output: artifacts/reports/redaction-publication-matrix.json

### `OVD-008`

```bash
python3 tools/accessibility_language_pack.py --json
```

Expected result: PASS JSON reports the current synthetic accessibility/language publication no-go matrix and policy count.

Evidence output: artifacts/reports/accessibility-language-matrix.json

### `OVD-009`

```bash
python3 tools/evidence_custody_provenance_pack.py --json
```

Expected result: PASS JSON reports the current synthetic custody/provenance no-go matrix and policy count.

Evidence output: artifacts/reports/evidence-custody-provenance-matrix.json

### `OVD-010`

```bash
python3 tools/independent_review_conflict_pack.py --json
```

Expected result: PASS JSON reports the current synthetic independent-review/conflict no-go matrix and policy count.

Evidence output: artifacts/reports/independent-review-matrix.json

### `OVD-011`

```bash
python3 tools/adopter_authority_capture_pack.py --json
```

Expected result: PASS JSON reports quarantined state/local rows as missing adopter capture with promotion blocked.

Evidence output: artifacts/reports/adopter-authority-capture-matrix.json

### `OVD-012`

```bash
python3 tools/adopter_capture_record_validator.py --json
```

Expected result: PASS JSON reports capture-record fixtures, expected negative failures, and zero shape-valid promotion approvals.

Evidence output: artifacts/reports/adopter-capture-record-validation-report.json

### `OVD-013`

```bash
python3 tools/mission_kernel_live_evidence_intake.py --json
```

Expected result: PASS JSON reports the current live-evidence intake as no-go with zero shipped live objects.

Evidence output: artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.json

### `OVD-014`

```bash
python3 scripts/check_mission_kernel_evidence_submitter.py
```

Expected result: PASS non-production drill hashes external temporary records, rejects governed synthetic-tree paths, and reports zero live evidence objects.

Evidence output: release-gate slice transcript

### `OVD-015`

```bash
python3 scripts/check_mission_kernel_full_drill_replay.py
```

Expected result: PASS full seven-work-item non-production drill replay digest-binds every required evidence class, reports zero live objects, and makes no live-readiness claim.

Evidence output: artifacts/reports/mission-kernel-full-drill-replay-audit-rev0900.json

### `OVD-016`

```bash
python3 scripts/check_cdf_export_replay.py
```

Expected result: PASS synthetic BD/CVR/ERR minimal projection replay recomputes option totals, emits a CRO, and negative controls fail on mismatch/unknown ID/overvote without claiming full NIST conformance.

Evidence output: artifacts/reports/cdf-export-replay-report-rev0900.json

### `OVD-017`

```bash
python3 scripts/check_cdf_independent_replay_verifier.py
```

Expected result: PASS separately implemented synthetic verifier recomputes BD/CVR/ERR totals, agrees with the primary replay report and CRO, and negative controls fail on mismatch/unknown ID/overvote/report drift/CRO drift without claiming full NIST conformance or external review.

Evidence output: artifacts/reports/cdf-independent-replay-verifier-rev0900.json

### `OVD-018`

```bash
python3 scripts/check_ballot_accounting_reconciler.py
```

Expected result: PASS synthetic ballot-accounting ledger reconciles to BD/CVR reporting-unit counts, contest selection slots, undervotes, and overvote rows; negative controls fail on count drift, undervote drift, and unknown units without claiming live custody evidence.

Evidence output: artifacts/reports/ballot-accounting-reconciliation-rev0900.json

### `OVD-019`

```bash
python3 scripts/check_election_event_log_reconciler.py
```

Expected result: PASS synthetic event-chain witness digest-binds BD/CVR/ERR/accounting, replay reports, CRO, and public boundary outputs; negative controls fail on broken previous hashes, digest drift, timestamp regression, and missing required roles without claiming live EEL/CDF conformance.

Evidence output: artifacts/reports/election-event-log-reconciliation-rev0900.json

### `OVD-020`

```bash
python3 scripts/release_gate.py --from check_release_go_no_go_pack.py --to check_release_go_no_go_pack.py
```

Expected result: PASS go/no-go registry, reports, source burn-down, and public boundary language are fresh.

Evidence output: release-gate slice transcript
