# Policy analysis as evidence (automated reasoning complements tests)

Unit tests catch regressions in *known* cases.
But policy failures often happen in the gaps: a selector accidentally widens, a new subject class appears, or a legacy exception becomes reachable.

This doc proposes an **optional high-assurance lane**: treat policy analysis results as evidence objects, produced by automated reasoning tools.

## The idea

For a given policy surface, run analyzers that can answer questions like:

- “Did this change expand the set of allowed requests?”
- “Are there any subjects that now have authority they previously lacked?”
- “Are there unreachable rules / dead exceptions / shadowed denies?”
- “Is there a path that allows a sensitive operation without the expected prerequisite receipt?”

The output should be:

- diffable (so reviewers can see what changed)
- attributable (tool + version + inputs)
- referenceable in promotion/rollout policy

## Why this fits DeriveBSD

DeriveBSD already forces many scary changes to become **typed drift surfaces**:

- interfaces: `contract.diff`
- kernel edges: `uapi.diff`
- parsers: `parser.diff`
- crypto choices: `crypto.diff`
- authority: `authority.diff`
- threat boundaries: `trust.boundary.diff`

Policy analysis is the same meta-pattern applied to *authorization surfaces*.

## Suggested shape (future work)

A minimal set of artifacts (not yet standardized here):

- `policy.analysis.report` — “what changed?”, “what’s newly reachable?”, “what invariants were checked?”
- `policy.analysis.diff` — a summarized delta between two reports

These should plug into:
- `blast_radius.diff` as another optional section
- CI gating (“policy drift requires passing tests + analysis”) for high-assurance channels

## External lessons worth stealing

- Cedar analysis toolkit: a concrete example of policy analysis designed for automated reasoning.
  - https://aws.amazon.com/blogs/opensource/introducing-cedar-analysis-open-source-tools-for-verifying-authorization-policies/
  - https://docs.cedarpolicy.com/

This lane is optional: tests + review may be enough for most surfaces.
But for “fleet admission”, “secrets unseal”, “remote assist”, and other high-blast-radius policy, automated reasoning is a sensible wedge.

See also:
- policy tests as artifacts: `docs/393-policy-tests-suites-and-mutation.md`
- design rubric (requires explicit test plans): `docs/348-design-review-rubric-and-feature-intake.md`

Last updated: 2026-02-27r112
