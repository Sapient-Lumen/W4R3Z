# rev0106 to rev0107 migration map

## Baseline

rev0106 extracted evaluator evidence-summary semantics and closed the met-obligation usability seam.

## rev0107 focus

rev0107 extracts discovery result version/digest binding semantics and closes a current-use discovery bypass where freshness could bless a returned object without aligned digest binding.

## New helper

```text
tools/discovery_binding_semantics.py
```

Moved from `tools/validate_archive.py`:

```text
digest_binds
parse_semver
check_downgrade_proof_metadata
check_result_version_negotiation
check_digest_binding_metadata
```

Added in the helper:

```text
check_current_result_binding
```

## New negative fixtures

```text
examples/negative/discovery-current-result-missing-digest-binding-invalid.json
examples/negative/discovery-current-result-digest-not-current-invalid.json
examples/negative/discovery-current-result-version-not-current-invalid.json
examples/negative/discovery-current-result-missing-version-current-invalid.json
```

## New semantic vectors

```text
TV-N288
TV-N289
TV-N290
TV-N291
```

## New derivations

```text
DF-0107-001
DF-0107-002
DF-0107-003
DF-0107-004
```

## Compatibility note

Existing positive discovery fixtures already carried aligned `version_negotiation.current_use_allowed` and `digest_binding.current_use_allowed` metadata. No positive fixture needed semantic weakening or broad schema expansion.
