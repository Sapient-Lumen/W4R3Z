# Policy tests as first-class artifacts (suites, regression vectors, mutation testing)

DeriveBSD’s policy posture is **policy-as-pure-function**: policies are deterministic, reviewable inputs to decisions.
That only works long-term if policy changes are guarded by **repeatable tests** that evolve with the policy.

This doc adds a disciplined lane:

- policies ship with **test suites** (golden vectors)
- CI produces **test reports** as evidence
- optional **mutation testing** measures whether the test suite would catch common “oops” mistakes (weakening/over-broadening rules)

## Artifacts

Two lightweight, diffable objects:

- `policy.test.suite` — the canonical set of cases for a policy surface
- `policy.test.report` — evidence from running a suite (and optional mutants)

Schemas:
- `spec/policy.test.suite.schema.json`
- `spec/policy.test.report.schema.json`

These artifacts are deliberately generic: they can test *any* policy surface (network egress, sandbox profiles, trust policy, portal permissions, etc.) as long as the decision can be represented as a request + context → decision.

## What a suite contains

A suite is a list of test cases.
Each case defines:

- **request**: the decision being asked for (e.g., “allow net egress?”, “allow portal operation?”, “allow kmod load?”)
- **facts/context**: the minimum evidence + attributes needed to evaluate the request
- **expected**: allow/deny + optional obligations/notes

The suite should focus on:

- “deny-by-default” invariants (the *absence* of grants is still deny)
- the few intended allows (minimize the allow surface)
- regression cases for prior incidents (a test is the long-term memory)

## Mutation testing (optional but high ROI)

Policy mistakes are often tiny edits with huge consequences:

- changing `deny` to `allow`
- widening a selector
- removing a constraint
- adding a legacy/exception path

Mutation testing generates small “mutant” policies (or applies mutation operators to the AST/IR), then checks whether the suite **kills** the mutant (i.e., fails a test that should fail). A high mutant survival rate means the test suite is not guarding the scary edges.

This is not “formal verification”; it’s a practical guardrail that catches the most common policy blunders.

## How this plugs into the system

- Policy repos can require: “`policy.test.report` must be present and passing for any policy changes.”
- `policy.suggestion` workflows should propose updating suites alongside patches.
- `blast_radius.diff` may optionally link to changed policy suites and their latest report digest.

See also:
- policy engine: `docs/30-policy-engine.md`, `docs/85-policy-engine-options-and-traces.md`
- denial-driven patches: `docs/378-denial-driven-policy-suggestions.md`
- test receipts and promotion gates: `docs/166-test-receipts-and-promotion-gates.md`
- policy replay/counterfactuals: `docs/312-policy-replay-and-counterfactual-explanations.md`

## Practical conventions (so this stays cheap)

- Keep suites small.
  - Prefer **one file per policy surface**.
  - Prefer **table-driven cases** over imperative scripts.
- Use stable case ids so diffs are meaningful.
- When a new policy surface lands, it should ship with:
  - at least one “deny-by-default” case
  - at least one intended allow
  - at least one regression case for an edge condition

## External lessons worth stealing

- OPA/Rego: built-in unit test ergonomics; policy changes ship with tests.
  - https://openpolicyagent.org/docs/policy-testing
- Qubes qrexec policy: cross-domain RPC is governed by explicit policy files; operationally, mistakes are costly, so policy review discipline matters.
  - https://doc.qubes-os.org/en/latest/user/advanced-topics/rpc-policy.html
- Cedar analysis: automated reasoning for policy changes (complements tests; great fit for “high-assurance lanes”).
  - https://aws.amazon.com/blogs/opensource/introducing-cedar-analysis-open-source-tools-for-verifying-authorization-policies/
- Access control policy mutation testing (research lineage; useful operators and fault models).
  - https://dl.acm.org/doi/10.1145/1242572.1242663

Last updated: 2026-02-27r112
