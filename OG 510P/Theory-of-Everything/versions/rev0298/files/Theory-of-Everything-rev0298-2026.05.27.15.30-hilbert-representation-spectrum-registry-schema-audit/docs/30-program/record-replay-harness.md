# Record replay harness

## Purpose

This surface defines the replay test a future session should run before treating a public artifact as route evidence.

## Minimal replay packet

A route-relevant replay packet should include:

```yaml
route_id:
carrier_ids:
acquisition_protocol_ids:
claim_binding_ids:
artifact_locator:
artifact_version:
metadata_record:
provenance_statement:
input_records:
output_records:
calibration_or_convention:
nuisance_controls:
negative_controls:
fresh_host_requirement:
expected_route_field_delta:
rollback_trigger:
```

## Replay outcomes

- **navigation-only:** artifact helps find literature but lacks carrier/protocol support;
- **carrier-public:** artifact is findable/versioned but not replayed;
- **replay-public:** fresh-host replay succeeds at the bounded target;
- **challenge-public:** replay plus hostile controls or independent challenge succeeds;
- **candidate-native-public:** the candidate supplies the native record/update/challenge grammar itself.

The current archive has no candidate-native-public route.
