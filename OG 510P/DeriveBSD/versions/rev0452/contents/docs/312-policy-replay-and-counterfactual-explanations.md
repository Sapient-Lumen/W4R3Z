# Policy replay + counterfactual explanations (avoid policy-as-magic)

DeriveBSD’s policy posture is only credible if it stays **explainable** under pressure.
In most systems, the first time policy is hard, people bypass it because:
- denials are opaque (“computer says no”)
- approvals are unreviewable (“trust me, it passed CI”)
- drift is invisible (inputs changed but nobody noticed)

Greenfield advantage: bake in **policy replay** and **counterfactual explanations** early so policy is a tool, not a wall.

## Goals

- **Replayability**: given `plan_digest` and its bound `policy_decision_digest`, re-run the policy engine and prove it matches.
- **Drift detection**: if replay differs (because external inputs changed), produce a typed “policy drift report”.
- **Counterfactuals**: for common denials, offer *minimal actionable deltas* ("what would make this allowed?") without weakening the authority model.
- **Safety**: counterfactuals are hints, not permissions.

## Existing building blocks

- Policy decision records bind policy identity + inputs to the plan (`docs/93-policy-decision-records.md`).
- Lint reports and blast-radius diffs already exist as pre-merge guardrails (`docs/237-lint-reports-and-contract-testing.md`, `docs/106-blast-radius-diff.md`).

This doc tightens the runtime/ops loop.

## 1) `derive policy replay`

A command that reconstructs the decision:

- input: `plan_digest` (or `policy_decision_digest`)
- rehydrate policy inputs referenced by the decision record (dataset digests)
- run policy on the compiled IR (service graph, cap routes, mount views, budgets)
- verify the new decision record matches the stored one (canonical hashing)

Outputs:
- **match**: replay proves the decision record is internally consistent
- **mismatch**: emit a drift report describing *which inputs changed* and *which rules diverged*

This becomes an incident primitive: “why is this node behaving differently?”

## 2) Policy drift reports (new concept)

Drift should be a first-class, typed object so it can be:
- stored
- diffed
- monitored
- included in incident bundles

A drift report should include:
- old vs new policy engine identity (if different)
- old vs new input digests (vuln DB snapshot, allowlists, etc.)
- summary of decision deltas (allow→deny, deny→allow, tightened constraints)
- stable pointers to rule traces

(We can reuse `lint.report` shape for v0.1, or introduce `policy.drift.report` later.)

## 3) Counterfactual explanations ("what would make this allowed?")

For common denials, we want a *useful* output like:

- “egress denied because `net.egress.policy` lacks class `telemetry.upload` for component X”
- “file access denied because mount.view does not include dataset Y; add a bookmark or explicit preopen”
- “export denied because `export.policy` requires consent/quorum for scope Z”

Counterfactuals should:
- be computed by the policy engine (not heuristics outside it)
- be **bounded** (top-N minimal changes)
- be **typed** (machine-readable hints)

This keeps policy authoring ergonomic without turning policy into a “wizard UI”.

## 4) Counterfactuals must not become a side-channel

Counterfactual output can leak information (e.g., “there exists a class named `prod-secrets`”).
So:
- scope counterfactual detail to the requester’s authority
- default to high-level categories unless elevated
- treat detailed traces as export-governed artifacts

## 5) Where it plugs in

- CI: attach policy replay + counterfactual summaries to lint reports for reviewers.
- Runtime: on denial events, emit a minimal reason code plus a pointer to a trace artifact.
- Ops: include drift reports in support bundles and fleet monitors.

See also:
- `docs/95-explainability-contract.md`
- `docs/215-structured-event-log-as-evidence.md`
- `docs/298-authority-budgets-and-permission-drift-alarms.md`

Last updated: 2026-02-26
