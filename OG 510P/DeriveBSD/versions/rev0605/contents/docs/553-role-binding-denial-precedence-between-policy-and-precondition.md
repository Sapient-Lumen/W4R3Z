# Role-binding denial precedence between policy-window and precondition checks

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` fixed remembered-role writes as compare-and-swap against `intent.role.binding.diff.from_binding.digest`.
`docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` then fixed that non-interactive remembered-role policy decisions are short-lived and single-apply.
`docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` made separately issued decisions for the same tuple stay distinguishable.
`docs/552-role-binding-policy-window-denials-need-typed-reasons.md` split joined-policy apply failures into `policy-expired` and `policy-consumed`.

This doc makes the next narrow hard decision:

> when several remembered-role denial conditions are simultaneously true, policy-window validity wins before compare-and-swap stale-state checks.

See also:
- ADR: `adrs/ADR-0143-role-binding-denial-precedence-between-policy-and-precondition.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- compare-and-swap boundary: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- short-lived single-apply boundary: `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- unique issuance identity: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- typed policy-window denials: `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`

## Why this needs a hard decision

The archive can now say:

- which exact mutation a non-interactive remembered-role policy decision authorized,
- when that authorization expires,
- that only one successful event may consume it,
- how to keep separately issued authorizations distinct,
- and how to record stale-write denial evidence through `precondition-failed`.

But one implementation cliff remains:
a single apply attempt can satisfy more than one denial condition at once.

Examples:

- a support-import retry reaches the boundary after a previous successful event already consumed the exact decision instance,
- the same retry also happens after `must_apply_before`,
- or the joined decision is still within its window but the reviewed diff is stale against newer remembered-role state.

If the archive leaves precedence unspecified, different implementations can return different `reason_code` values for the same underlying situation.
That breaks deterministic support guidance and makes the event log less queryable than the archive intends.

## Accepted boundary

For remembered-role mutation attempts, evaluate denial reasons in this order:

1. `policy-denied`
2. `policy-consumed`
3. `policy-expired`
4. `precondition-failed`
5. otherwise apply succeeds

What that means operationally:

- non-interactive `policy_decision_digest` checks are **normal request checks** for remembered-role apply
- compare-and-swap against `diff.from_binding.digest` only matters after those policy-window checks still leave live authority to proceed
- if a joined decision is already consumed, emit `policy-consumed` even if the apply window has also elapsed by the time the retry arrives
- if a joined decision is expired, emit `policy-expired` instead of `precondition-failed`, even when the diff is also stale
- interactive `trusted-settings-ui` flows without `policy_decision_digest` skip the policy-window steps and therefore only use the consent + compare-and-swap path

## Why this order is the smallest coherent one

### Policy-window checks first

A non-interactive remembered-role write should not evaluate as a stale-write conflict before the archive has answered whether the exact joined authority is still live.
That keeps local admin, reconcile, and support-import behavior on the same authority-first lane rather than leaking into implementation-defined branch order.

### `policy-consumed` before `policy-expired`

A single-use authorization that has already been spent should stay evidence of replay/reuse, not decay into a mere “too old” story later.
That keeps replay evidence stable over time: once the exact decision instance is consumed, later retries keep that fact as the primary explanation.

### `precondition-failed` last

Compare-and-swap is still required, but it is only the winning denial reason once the caller still has a live authorization to attempt the mutation.
That keeps `observed_binding` focused on the stale-state story instead of turning it into a catch-all companion to every denied apply.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile loops can distinguish “re-issue policy” from “re-read state” instead of guessing from a generic failure.
- **B / secure workstation:** interactive flows remain simple because they skip the non-interactive policy-window ladder entirely.
- **C / general-purpose OS:** host-local admin tooling can compile through the same policy lane and still produce deterministic denial evidence.
- **D / appliance factory / regulatory:** support-import and dedicated-device reconcile keep replay/expiry/stale-state evidence sharp for audits and operator bundles.

## Support / evidence effect

When remembered-role behavior matters to a postmortem, the durable event trail should now answer one primary denial question per attempt:

- `policy-denied` — no live exact authorization ever existed for this apply
- `policy-consumed` — the exact authorization existed but was already spent by an earlier success, and `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` now requires `consumed_by_event_id` so the winning success is explicit
- `policy-expired` — the exact authorization existed but was too old at apply time
- `precondition-failed` — the authorization was still live, but current remembered state no longer matched the reviewed diff

This keeps retry guidance small and deterministic:

- `policy-consumed` / `policy-expired` → mint or fetch a fresh exact-mutation policy decision
- except that `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` allows `policy-consumed` to collapse to **already-applied** when the pointed-to consuming success proves it was the same exact mutation tuple
- `precondition-failed` → re-read current state and build a fresh diff

## What this does **not** decide

This doc does **not** decide:

- distributed/global consumption coordination,
- whether implementations record secondary non-winning denial facts outside the typed event surface,
- or any larger request-transaction family.

## References

- RFC 9110 evaluation of request preconditions (normal request checks happen first; preconditions are evaluated afterward in a defined order): https://www.rfc-editor.org/rfc/rfc9110
- Kubernetes admission control phases (mutating, then validating, with immediate rejection on first failing controller): https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
- Vault response wrapping (single-use wrapping tokens with TTL and distinct invalid states such as already unwrapped or expired): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping
- Use temporary credentials with AWS resources (temporary credentials fail after expiry and require a fresh set): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-18r285
