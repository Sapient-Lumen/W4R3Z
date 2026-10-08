# build_dir_layout_v2_sidecar_relocation

This scenario exists because Cargo’s Build Dir Layout v2 work makes it increasingly clear that artifact **location churn** and debuggability **support truth** are different things.

The fixture should model a build where:
- primary artifacts and sidecars move because build-dir / target-dir behavior changed, but
- the actual support posture may be unchanged *if* the handoff manifest preserved the right files.

Expected contract behavior:
- `artifact-handoff.manifest` records canonical and copied locations separately.
- `support-posture.report` does not overreact merely because paths changed.
- `doctor` warns only when relocation caused a real support regression, such as lost sidecars or unverifiable copies.
