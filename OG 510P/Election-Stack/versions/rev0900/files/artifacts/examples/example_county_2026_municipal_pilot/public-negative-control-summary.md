# Example County negative-control verifier summary

**Synthetic example only. This is not live election evidence.**

Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`  
Archive version: `v900`  
Negative controls: `8`  
Expected-failure status: `PASS`

## What this checks

These fixtures deliberately mutate temporary copies of otherwise valid synthetic packets. A PASS means the verifier rejected the tampered temporary packet with the expected publishable problem code. It does not certify any election, does not prove an outcome, and does not prove intent or fraud.

## Expected failures

- `ECF-001` / `append_payload_object`: PASS (manifest_url_hash_mismatch, object_hash_mismatch, payload_digest_mismatch, payload_pointer_hash_mismatch, payload_pointer_json_parse_failed, payload_pointer_size_mismatch)
- `ECF-002` / `tamper_payload_pointer_digest`: PASS (payload_pointer_hash_mismatch)
- `ECF-003` / `tamper_payload_digest`: PASS (payload_digest_mismatch, tbs_digest_mismatch)
- `ECF-004` / `tamper_tbs_digest`: PASS (tbs_digest_mismatch)
- `ECF-005` / `tamper_manifest_digest`: PASS (manifest_url_hash_mismatch)
- `ECF-006` / `remove_manifest`: PASS (manifest_missing)
- `ECF-007` / `unsupported_envelope_version`: PASS (envelope_version_unsupported_major, tbs_digest_mismatch)
- `ECF-008` / `missing_payload_object`: PASS (manifest_url_missing, payload_digest_mismatch, payload_pointer_object_missing)

## Operator command

```bash
python3 tools/example_county_negative_control_runner.py --json
```

## Boundary

Synthetic expected-failure rehearsal only; not live election evidence, not certification, not proof of outcome correctness, not proof of intent or fraud, and not legal advice.
