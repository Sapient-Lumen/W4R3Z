# Meta: Portfolio Conformance Protocol

## Goal
This protocol defines the **minimum mechanically enforced checks** for the archive's shared portfolio-envelope grammar.

It exists to answer a narrow question:

> before a revision claims that a shared pack / brief / diff / verify receipt / lineage receipt is “well-formed enough” for routing, reuse, or specimen refresh, what should the repo actually check?

This protocol owns only the **cross-cutting honesty contract**.
It does **not** own seam-local payload semantics.

## Canonical files
Read and maintain together:
- `design/portfolio-conformance-validation-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`
- `design/portfolio-reference-specimens-2026Q1.md`
- `specimens/README.md`
- `specimens/portfolio-envelope-v0/README.md`
- `fixtures/portfolio-envelope-v0/README.md`
- `fixtures/portfolio-envelope-v0/portfolio-envelope-hygiene-checks.json`
- `tools/check_portfolio_envelope_contract.py`

## Required command
Run:

`python tools/check_portfolio_envelope_contract.py`

And, for the broader repo hygiene entry point:

`python tools/hygiene.py`

A revision that changes shared-grammar, routing, role minimums, or specimen posture should not be treated as complete until the checker passes.

## What the checker must enforce
The first checker must enforce only the archive's **thin outer grammar**.

### Required common fields
Each checked artifact must contain:
- `schema_family`
- `specimen_role`
- `seam`
- `subject`
- `scope`
- `authority`
- `freshness`
- `partiality`
- `imports`
- `attachments`
- `payload`
- `lineage`
- `handoff`

### Required role minimums
- **canonical_pack**
  - `handoff.lossiness_budget` must be `none_for_canonical_pack`
- **routed_brief**
  - `scope.brief_for` must be present
  - `payload.allowed_decisions` must be non-empty
  - `payload.prohibited_decisions` must be non-empty
  - `handoff.escalation_target` must be non-empty
- **verify_receipt**
  - `payload.verdict` must be present
  - `payload.prohibited_conclusions` must be non-empty
- **diff**
  - `subject.left_pack` and `subject.right_pack` must be present
- **lineage_receipt**
  - `payload.transform` must be present
  - `payload.preserved_truths` must be non-empty
  - `payload.omitted_truths` must be non-empty

### Required lineage / escalation discipline
- non-canonical artifacts must declare at least one lineage parent;
- all checked artifacts must declare a non-empty `handoff.escalation_target`;
- and child views must not silently claim canonical losslessness.

## What the checker must NOT enforce
The cross-cutting checker must **not**:
- validate seam-local subject semantics;
- validate whether imported evidence is factually correct;
- enforce one universal payload schema across all seams;
- or treat a passing envelope check as proof that the underlying artifact is operationally sound.

Those belong to:
- seam-local validators;
- importer-level checks;
- pilot scorecards;
- and human review.

## Negative fixtures are mandatory
The checker must validate both:
- **positive specimens** that pass; and
- **negative fixtures** that fail for named reasons.

A revision that changes the contract without updating negative fixtures is incomplete.

## When this protocol must be touched
Update this protocol in the same revision if any of the following change materially:
- required common envelope fields;
- role names or role minimums;
- lineage or escalation requirements;
- specimen directory conventions;
- negative fixture expectations;
- or the hygiene entry point.

## LLM / assistant rule
If an assistant is extending or refreshing the shared portfolio-envelope grammar, it should:
- start from the nearest specimen;
- preserve the existing hard honesty rules;
- update fixtures when it changes those rules;
- and avoid inventing a new role or stronger conclusion without updating this protocol.

If it cannot do that, it should not pretend the new artifact is conformant.
