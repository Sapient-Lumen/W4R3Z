# MC/DC Coverage Workbench Kit fixtures

This fixture set makes **P-0433 MC/DC Coverage Workbench Kit** concrete.

## First-class artifacts

- `decision-authority.receipt.json` — records what decision inventory was authoritative.
- `construct-support.matrix.json` — records which construct classes were supported, unsupported, or excluded.
- `independence-pair.report.json` — records whether each condition has witnessed independence-pair evidence.
- `campaign-scope.receipt.json` — records which packages, targets, test families, and execution lanes were actually in scope.
- `caveat-basis.receipt.json` — records unstable/toolchain/known-limitation posture.
- `comparison-basis.receipt.json` — records whether two bundles are honestly comparable.
- `qualification-basis.receipt.json` — records what assurance story the evidence can conservatively support.
- `profile-compatibility.receipt.json` — records whether the underlying profile artifacts are safe for the intended use.
- `campaign-policy.receipt.json` — records the explicit construct/support/execution policy the campaign adopted.
- `manual-review-debt.report.json` — records unresolved review obligations that automation did not discharge.
- `evidence-lineage.receipt.json` — records which concrete runs and merged profiles back the verdict.
- `mcdc-drift.diff.json` — records conservative change classes across runs or revisions.
- `mcdc-support-bundle.manifest.json` — portable manifest joining the review artifacts.

## Core review question

Can another engineer or assessor tell:

1. what decisions were actually in scope,
2. which construct classes were unsupported or policy-excluded,
3. whether each condition has independence evidence,
4. what caveats constrained the result,
5. and which runs produced the evidence?
6. whether the profile inputs are actually durable for the intended claim?
7. what unresolved review debt still remains even after automation?

If not, the crate still lives in coverage folklore more than in reviewable contract territory.


## Additional review question

Can another engineer tell whether a trend claim is actually like-for-like, whether the retained inputs are durable enough for that use, and what unsupported construct or host/target debt still blocks a stronger assurance story?
