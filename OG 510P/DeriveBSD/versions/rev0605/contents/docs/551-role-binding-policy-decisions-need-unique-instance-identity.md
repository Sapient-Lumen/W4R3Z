# Role-binding policy decisions need unique instance identity

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/549-role-binding-policy-decisions-bind-exact-mutation.md` fixed that remembered-role policy joins must bind the exact mutation tuple.
`docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` then fixed freshness and successful-consumption semantics.

This doc makes the next small hard decision:

> independently issued remembered-role policy decisions must have unique instance identity, even when the exact mutation tuple and apply window are otherwise identical.

See also:
- ADR: `adrs/ADR-0141-role-binding-policy-decisions-need-unique-instance-identity.md`
- policy-decision join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- exact-mutation boundary: `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- short-lived single-apply boundary: `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- generic policy decisions: `docs/93-policy-decision-records.md`
- schema: `spec/intent.role.binding.policy.profile.schema.json`
- example: `spec/examples/intent.role.binding.policy.profile.json`
- typed failure boundary: `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`

## Why this needs a hard decision

After ADR-0140, remembered-role `policy.decision` records are already much tighter:

- they bind the exact host/profile/trigger/binding tuple,
- they carry compare-and-swap preconditions for updates,
- they may bind the relevant import receipt,
- and they expire after `must_apply_before` with `max_successful_events = 1`.

That still leaves one non-obvious replay cliff:
if two independently issued allow records have identical content, they hash to the same `policy_decision_digest`.
Then the archive cannot tell whether a successful remembered-role event consumed an earlier issuance or a later re-issued authorization for the same tuple.

That ambiguity makes single-apply enforcement less implementable than it first appears.
A host-local admin path in profile C cannot safely re-mint the same exact mutation after expiry without perturbing unrelated fields.
A support/import flow cannot cleanly distinguish “freshly re-authorized” from “same allow record reused.”

## Accepted boundary

The remembered-role exact-mutation policy profile now requires a top-level:

- `decision_instance_id`

This field is part of the canonical policy record itself, not extra sideband metadata.
That means it participates in the content-addressed digest and keeps independently issuable remembered-role allow records from collapsing to the same `policy_decision_digest`.

## Semantics

`decision_instance_id` means:

1. each independently issuable remembered-role policy decision gets its own instance identity
2. if the same exact mutation tuple is re-issued later, the new record must carry a fresh `decision_instance_id`
3. successful remembered-role events still only join through `policy_decision_digest`; reviewers learn the instance identity by opening the joined policy record
4. `decision_instance_id` does **not** replace `must_apply_before` or `max_successful_events = 1`; it makes those rules distinguishable across re-issuance

`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` adds the next small evidence join on top of that identity rule: when a later retry loses because a distinct decision instance was already spent, the `policy-consumed` denial must carry `consumed_by_event_id` so support can name the earlier successful consuming event rather than inferring it from timing alone.

## Why this is the right cut

This keeps the archive small while making the previous decision worth enforcing:

- **A / secure fleet host:** a reconciler can re-issue the same exact baseline mutation after a stale/precondition failure without pretending it is the same already-consumed allow record.
- **B / secure workstation:** org-managed or support-driven remembered-role changes stay auditable when the same tuple needs to be re-authorized after a prompt race or expiry.
- **C / general-purpose OS:** host-local admin tooling stays viable because it can mint a fresh instance id for the same exact mutation tuple instead of inventing a separate shell-shaped transaction surface.
- **D / appliance factory / regulatory:** offline replay/recovery evidence can distinguish first authorization from later re-authorization for the same exact baseline target.

This is intentionally smaller than adding a broader request-transaction family to `intent.role.binding.event`.
The event join already exists.
The missing piece was only that the joined allow record needed one more bit of identity.

## Review rule

When a remembered-role event carries `policy_decision_digest`, reviewers should now be able to answer all of these from the joined policy record plus the event journal:

1. Which exact mutation tuple was authorized?
2. By what time did it have to be applied?
3. Was it a single-apply authorization?
4. Which issuance instance did this event actually consume?

If the fourth answer still requires daemon memory or shell history, the policy record is too loose.

## Event semantics after this cut

`intent.role.binding.event` does not gain new fields in this iteration.
The archive still joins remembered-role non-interactive authority through `policy_decision_digest`.
What changed is the contract for the joined policy record:

- it must bind the exact mutation tuple,
- it must be short-lived and single-apply,
- it must leave later failure semantics sharp enough that expiry can become typed `policy-expired` evidence instead of collapsing into generic `policy-denied`,
- it must also make later replay evidence stable enough that a spent authorization can continue to report `policy-consumed` rather than decaying into a mere expiry story,
- and it must also carry `decision_instance_id` so separately issued authorizations remain separately digestable.

That keeps the event family stable while moving the non-interactive remembered-role lane closer to code-worthiness.

## What this does **not** decide

This doc does **not** decide:

- the exact formatting scheme for `decision_instance_id`
- global replica coordination or distributed lock mechanics
- richer actor/quorum receipts
- or any larger remembered-role transaction family

Those remain later bounded choices.

## References

- DeriveBSD policy decision records: `docs/93-policy-decision-records.md`
- kube-apiserver Admission (v1) (`uid` distinguishes otherwise identical request/response pairs): https://kubernetes.io/docs/reference/config-api/apiserver-admission.v1/
- Vault response wrapping (single-use wrapped responses are materialized as distinct single-use tokens): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping

## Related docs

- `docs/93-policy-decision-records.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `spec/intent.role.binding.policy.profile.schema.json`

Last updated: 2026-03-18r284
