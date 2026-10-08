# oasdiff_warn_level_change_must_not_masquerade_as_definite_breaking_proof

An OpenAPI diff surfaced a `WARN`-level finding under oasdiff.
That should stay visibly weaker than a mechanically definite breaking change.

This scenario exists to keep “OpenAPI diff found a problem” from silently collapsing into one certainty class.
