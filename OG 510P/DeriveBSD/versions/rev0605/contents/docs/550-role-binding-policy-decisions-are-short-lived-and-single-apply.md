# Role-binding policy decisions are short-lived and single-apply

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed that remembered-role non-interactive writes join to `policy.decision` through `policy_decision_digest`.
`docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` then fixed compare-and-swap.
`docs/549-role-binding-policy-decisions-bind-exact-mutation.md` then fixed that the joined policy record must bind the exact remembered-role mutation tuple.

This doc makes the next small hard decision:

> an exact-mutation remembered-role policy decision is still too broad unless it is short-lived and single-apply.

See also:
- ADR: `adrs/ADR-0140-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- policy-decision lane: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- stale-write boundary: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- exact-mutation policy profile: `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- issuance-identity boundary: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- typed policy-window denials: `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- generic policy decisions: `docs/93-policy-decision-records.md`
- schema: `spec/intent.role.binding.policy.profile.schema.json`
- example: `spec/examples/intent.role.binding.policy.profile.json`

## Why this needs a hard decision

After ADR-0139, a remembered-role policy decision can already answer:

- which host/profile was in scope,
- which trigger lane was allowed,
- which roles were touched,
- which resulting binding digest was allowed,
- which precondition and diff guarded an update,
- and which import receipt was involved when support/import policy governed the mutation.

That is a big improvement, but it still leaves one implementability cliff:
**how long does that allow record stay valid, and how many successful writes may it authorize?**

If the answer is “until something outside the archive notices otherwise,” the exact-mutation profile still degrades into ambient authority.
A reconciler can cache it forever.
A support/import flow can replay it later.
A local-admin path in profile C can accidentally become a standing remembered-role capability rather than a bounded decision.

## Accepted boundary

The exact-mutation remembered-role policy profile now requires two more apply constraints on
`effective_constraints.intent_role_binding_apply`:

- `must_apply_before`
- `max_successful_events`

For v0, `max_successful_events` is fixed at `1`.
That is a deliberate product boundary: remembered-role policy decisions behave like a small apply grant, not a reusable background permission.

## Consumption rule

A remembered-role `policy_decision_digest` is consumed only by a **successful** mutation event:

`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` now tightens the denial side of that same rule: if a later retry loses because the authorization was already spent, the `policy-consumed` denial must point back to the earlier successful winner through `consumed_by_event_id`.


- `action = initialized`
- `action = updated`

The event must land no later than `must_apply_before`.
After one successful event, that same `policy_decision_digest` may not authorize another successful remembered-role mutation.

Non-success paths do **not** consume the allow record:

- `write-denied`
- failed validation
- stale precondition failures
- policy import checks that refused to apply

Those outcomes still leave evidence, but they do not count as the one allowed successful mutation. `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` now sharpens one more detail: if the joined authorization existed but was too late or already spent, the denial should remain typed as `policy-expired` or `policy-consumed` instead of collapsing into generic `policy-denied`. `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` sharpens the next edge: once an authorization is spent, `policy-consumed` stays the winning denial even if the apply window has also elapsed by the time of a later retry.

## Why this is the right cut

This keeps the archive small while making implementation behavior sharper:

- **A / secure fleet host:** background reconcile can stay non-interactive, but each successful remembered-role write still consumes a bounded policy decision instead of inheriting a daemon-shaped standing permission.
- **B / secure workstation:** org-managed or support-driven writes stay distinct from the interactive consent lane while still leaving a compact freshness/consumption story in support bundles.
- **C / general-purpose OS:** host-local admin tooling stays viable because it can compile to the same exact-mutation policy profile without silently creating a durable host-local superpower.
- **D / appliance factory / regulatory:** restore/baseline flows stay auditable because the allow record is now tied to both the exact tuple and a bounded apply window.

This is intentionally smaller than a full request-uid or transaction family.
The archive does not yet need a replayable multi-step admin workflow object.
It only needs one more rule so that a policy decision is worth enforcing. `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` then makes the next small cut by requiring `decision_instance_id`, so separately issued single-apply decisions for the same tuple do not collapse to the same digest.

## Review rule

When a remembered-role event carries `policy_decision_digest`, reviewers should now be able to answer all of these from the joined policy record plus the event journal:

1. Which exact mutation tuple was authorized?
2. By what time did it have to be applied?
3. Has a successful remembered-role event already consumed it?
4. Which `decision_instance_id` did the successful event consume?

If those answers still require daemon folklore, shell history, or an out-of-band ticket note, the policy record is too loose.

## Event semantics after this cut

`intent.role.binding.event` does not gain new fields in this iteration.
Instead, the meaning of an existing `policy_decision_digest` gets narrower again:

- the joined policy record must conform to the exact-mutation remembered-role profile,
- the profile must carry `must_apply_before` plus `max_successful_events = 1`,
- the profile must also carry `decision_instance_id` so a fresh re-issuance stays distinguishable from a reused authorization,
- and successful `initialized` / `updated` events are the consumption evidence for that authorization.

That keeps the event family stable while making the non-interactive policy lane more implementation-shaped.

## What this does **not** decide

This doc does **not** decide:

- broader request/replica coordination details beyond the minimal `decision_instance_id` contract,
- replica/distributed coordination mechanics for consumption enforcement,
- broader remembered-role baseline distribution language,
- or richer actor/quorum receipts.

Those remain later bounded choices.

## References

- DeriveBSD policy decision records: `docs/93-policy-decision-records.md`
- Vault response wrapping (single-use wrapping tokens with separate TTL): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping
- AWS IAM temporary security credentials (short-lived and unusable after expiry): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html
- Kubernetes admission request schema (`uid` distinguishes otherwise identical request/response pairs): https://kubernetes.io/docs/reference/config-api/apiserver-admission.v1/
- etcd transactions (`If`/`Then`/`Else` compare-and-swap primitive): https://etcd.io/docs/v3.4/learning/api/

## Related docs

- `docs/93-policy-decision-records.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `spec/intent.role.binding.policy.profile.schema.json`

Last updated: 2026-03-18r284
