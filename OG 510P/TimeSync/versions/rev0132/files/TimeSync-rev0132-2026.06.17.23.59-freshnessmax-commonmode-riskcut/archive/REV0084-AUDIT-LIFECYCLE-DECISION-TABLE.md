# rev0084 audit — lifecycle decision table hardening

The rev0084 archive had correct lifecycle concepts but relied too heavily on prose and local checks. Several incoherent combinations could still validate, including:

```text
active lifecycle + active emergency withdrawal + current interpretation
active lifecycle + revoked revocation status
contested lifecycle + contestation none
emergency withdrawal + not_applicable scope
resolved_upheld contestation without digest
notification observed after aggregate artifact creation
pending_rotation + unguarded current decision
unknown_or_redacted lifecycle + current interpretation
revocation_status not_checked + current interpretation
```

rev0085 adds a decision table and negative fixtures for each of these cases.

## Validator changes

`check_aggregate_correction_authority_lifecycle(...)` now derives an expected `current_interpretation_decision` from actual posture and rejects mismatches.

`check_aggregate_correction_authority_reference(...)` now evaluates notification and authorization observations against `aggregate_record_created_at`.

`check_aggregate_lifecycle_rollup(...)` rejects rollups that claim current-supported interpretation while suppressed decision populations are present.

## Boundary result

The hardening closes semantic gaps without adding new authority registries, notification systems, incident workflows, or provenance surfaces.
