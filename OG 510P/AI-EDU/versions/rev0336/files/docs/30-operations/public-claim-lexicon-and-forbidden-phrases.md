# Public claim lexicon and forbidden phrases

## Purpose

Public-facing summaries are often where evidence laundering happens. A schema can be valid, a release can be lint-clean, and a pilot summary can still overclaim. This lexicon gives maintainers a small phrase-level guardrail for ready-but-not-closed releases and early pilot reports.

## Allowed phrase families

Use bounded language when real evidence is missing or incomplete:

- "ready-but-not-closed"
- "synthetic example"
- "schema-backed rehearsal"
- "pre-import control"
- "not real pilot evidence"
- "requires `SRC2+` source data before closure"
- "claim limited to internal consistency"
- "public summary is redacted and non-evidentiary"

## Conditional phrase families

Use only when the named artifact exists and the evidence grade supports the claim:

- "local pilot evidence" only with `SRC2+` source truth and accepted review;
- "improved learning" only with a learning-effect claim family and appropriate evidence grade;
- "reduced workload" only with workload evidence, not only teacher impressions;
- "safe for scale" only after security, protected-route, lifecycle, and stop-rule review;
- "validated" only when the validation method and scope are named.

## Forbidden phrase families before `FT-0181` closes

Do not say:

- "proves learning"
- "validated pilot"
- "real pilot evidence imported"
- "all followthrough closed"
- "FT-0181 closed"
- "safe to scale"
- "evidence complete"
- "automation approved"
- "waived by exception"

## Repair rule

If a forbidden phrase appears in a public summary or release note, repair the claim before release. If it was already published, route through the recovery drill for public overclaim and update the decision-delta log.

Related: [`public-summary-render-smoke-tests.md`](public-summary-render-smoke-tests.md), [`public-pilot-summary-examples.md`](public-pilot-summary-examples.md), [`ready-but-not-closed-assurance-case.md`](ready-but-not-closed-assurance-case.md), [`release-invariants-and-claim-boundaries.md`](release-invariants-and-claim-boundaries.md).
