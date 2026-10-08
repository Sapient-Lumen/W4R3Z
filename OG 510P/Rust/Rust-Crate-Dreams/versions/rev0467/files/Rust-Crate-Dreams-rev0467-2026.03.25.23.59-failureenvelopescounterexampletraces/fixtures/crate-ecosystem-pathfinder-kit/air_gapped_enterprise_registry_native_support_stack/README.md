# Scenario stub — air-gapped enterprise registry + native support stack

Decision question:
> Which crates should a team choose when the environment is bandwidth-constrained, firewalled, registry-sensitive, and likely to involve native prerequisites?

This scenario exists because many otherwise reasonable crate recommendations silently assume public registries, easy internet access, and hosted build surfaces.

## Roles to fill
- registry / source acquisition posture
- docs / knowledge availability
- native prerequisite handling
- build reproducibility / cache posture
- review / support packet export

## Expected artifacts
- `decision-brief.md`
- `external-prerequisite.report.json`
- `starter-set.bundle.json`
- `manual-review.note.md`
- `offramp-bundle.manifest.json`

## Guardrail
Do not treat crates.io visibility or docs.rs success as proof that the stack is viable offline.
