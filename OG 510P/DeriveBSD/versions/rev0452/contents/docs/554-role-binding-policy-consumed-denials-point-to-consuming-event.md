# Role-binding policy-consumed denials point to the consuming event

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` fixed that remembered-role exact-mutation policy decisions are consumed by the first successful apply.
`docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` fixed that separately issued authorizations for the same tuple stay distinguishable.
`docs/552-role-binding-policy-window-denials-need-typed-reasons.md` then fixed that already-spent authorization stays typed as `policy-consumed` instead of collapsing into generic denial.
`docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` fixed that `policy-consumed` remains the winning denial when multiple denial conditions are simultaneously true.

This doc makes the next narrow hard decision:

> when remembered-role apply fails with `reason_code = policy-consumed`, the denial must point at the exact earlier successful event that spent the authorization.

See also:
- ADR: `adrs/ADR-0144-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- single-apply boundary: `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- unique instance identity: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- typed policy-window denials: `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`

## Why this needs a hard decision

The archive can now say:

- which exact mutation tuple a non-interactive remembered-role policy decision authorized,
- how long that exact authorization remains live,
- that only one successful event may consume it,
- that independently issued authorizations remain distinguishable,
- and that retries after consumption stay typed as `policy-consumed`.

But one support/evidence cliff remains:
`policy-consumed` tells operators **what kind of failure happened**, but not yet **which success actually spent the authorization**.
Without that join, postmortems and retry logic still have to reconstruct the winner by scanning recent events heuristically.
That is exactly the kind of small ambiguity that later turns into divergent implementations and support folklore.

## Accepted boundary

For remembered-role `intent.role.binding.event` objects:

- `reason_code = policy-consumed` requires `consumed_by_event_id`
- `consumed_by_event_id` names the earlier successful `intent.role.binding.event.event_id` that consumed the joined `policy_decision_digest`
- `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` now also requires `consumed_by_event_digest` so detached bundles can verify the winner bytes
- the referenced event must be an `initialized` or `updated` event in the same remembered-role mutation family
- `reason_code = policy-expired` does not require this field

This is intentionally small.
It does not invent a separate consume receipt or transaction family.
It only adds one winner pointer to the denial event that already exists.

## Why event id is the right first pointer

The event log already treats `event_id` as the stable per-event correlation handle.
Using that handle here keeps the implementation burden low:

- support bundles can carry the winner id and the winner event together,
- reconcile/admin logs can answer “who already spent this?” without custom history scans,
- and the denial remains readable even when operators are not looking at raw canonical event bytes.

That proved to be the right first cut, but not the final one. `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` now adds the verifier next to the locator: `policy-consumed` denials also carry `consumed_by_event_digest`, so offline bundles can verify the exact winner bytes rather than trusting only the id pointer. `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` then fixes how callers may interpret that digest-bound winner during recovery: only an exact tuple match may collapse the retry to **already-applied**. `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` adds the next support/export cut: `policy-consumed` denials now also carry `recovery_interpretation` so the derived retry story is stable and queryable instead of hidden inside local join logic.

## Event rule

`intent.role.binding.event` now adds one more narrow rule for non-interactive denial evidence:

- `policy-denied` — no exact joined authorization was available to apply
- `policy-expired` — exact joined authorization existed but was too old at apply time
- `policy-consumed` — exact joined authorization existed but had already been spent, and the denial must carry `consumed_by_event_id`
- `precondition-failed` — live authority remained, but compare-and-swap still lost against newer remembered-role state

That keeps the denial ladder from ADR-0143 intact while making the replay/spent branch materially more actionable.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile can name the winning success event and decide whether it merely lost a race or needs fresh policy issuance.
- **B / secure workstation:** support-driven import/recovery failures can point straight at the earlier successful role-binding mutation instead of forcing bundle readers to infer it from timing.
- **C / general-purpose OS:** host-local admin tooling can emit deterministic spent-authorization evidence without growing a separate shell-transaction story.
- **D / appliance factory / regulatory:** exportable bundles can show exactly which success consumed the authorization, which is better audit material than “it must have happened somewhere earlier.”

## Review rule

When a remembered-role event says `reason_code = policy-consumed`, reviewers should be able to answer all of these from the event plus its joined winner:

1. which exact policy decision instance was spent?
2. which earlier successful event spent it?
3. was that winner an `initialized` or `updated` mutation?
4. does the denial therefore call for fresh policy issuance rather than stale-state rebasing?

If question 2 still requires freehand log archaeology, the evidence contract is too loose.

## What this does **not** decide

This doc does **not** decide:

- distributed/global winner election for multi-replica consume races,
- a generic consume-receipt family,
- digest-addressed joins for every event type,
- or richer retry envelopes.

Those remain later bounded choices.

## References

- kube-apiserver Admission (v1) (`uid` distinguishes otherwise identical request/response pairs and keeps request/response correlation explicit): https://kubernetes.io/docs/reference/config-api/apiserver-admission.v1/
- Vault response wrapping (single-use wrapping tokens stay distinct and retries after first use are meaningfully different from fresh unwrap): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.write-denied.policy-window.schema.json`

Last updated: 2026-03-18r287
