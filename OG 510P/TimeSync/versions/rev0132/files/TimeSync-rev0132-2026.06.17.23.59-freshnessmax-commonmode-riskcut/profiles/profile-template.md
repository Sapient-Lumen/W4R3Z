# Profile template

```text
Profile:
  id:
  version_or_revision:
  authority:
  purpose:
  dominant_timing_pressure:

  required_items:
  profile_default_items:
  requestable_items:

  control_surface_pressures:
    source_policy:
    error_acceptability_policy:
    regime_transition_policy:
    holdover_policy:
    downstream_applicability_policy:

  applicability_mapping:
    satisfied:
    fallback:
    unsatisfied:

  fallback_modes:
    - name:
      trigger:
      allowed_applicability:
      required_boundary_context:

  profile_reference_policy:
    minimum_export_tier:
    digest_required_when:
    signed_binding_required_when:

  lifecycle_policy:
    retained_assessment_requirement:
    superseded_profile_handling:
    revoked_profile_handling:
```
