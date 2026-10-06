# Role-binding policy-window denials need typed reasons

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/549-role-binding-policy-decisions-bind-exact-mutation.md` fixed that remembered-role policy joins must bind the exact mutation tuple.
`docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` then fixed freshness and successful-consumption semantics.
`docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` then fixed that separately issued authorizations for the same tuple remain distinguishable.

This doc makes the next small hard decision:

> when a remembered-role non-interactive apply fails because a joined policy decision is too late or already spent, the event must say so explicitly instead of collapsing into generic `policy-denied`.

See also:
- ADR: `adrs/ADR-0142-role-binding-policy-window-denials-need-typed-reasons.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- apply-window boundary: `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- issuance-identity boundary: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`

## Why this needs a hard decision

After ADR-0140 and ADR-0141, remembered-role non-interactive policy is much tighter:

- it binds the exact mutation tuple,
- it expires at `must_apply_before`,
- it permits only one successful apply,
- and re-issued authorizations stay distinguishable through `decision_instance_id`.

That still leaves one forensics/operability cliff:
when an apply attempt reaches the boundary with `policy_decision_digest` in hand, the archive still needs a typed answer for *why* the write was refused.
If expired or already-consumed decisions collapse into `policy-denied`, operators cannot distinguish:

- policy never allowed this write,
- policy allowed it, but too late,
- or policy allowed it earlier and that allowance was already consumed by a different successful event.

## Accepted boundary

`intent.role.binding.event.reason_code` now includes two more typed non-interactive denial outcomes:

- `policy-expired`
- `policy-consumed`

These are write-denied outcomes for events that already joined a concrete `policy_decision_digest`.
They do **not** replace generic `policy-denied`.
They split one ambiguous bucket into three implementable cases.

## Semantics

### `policy-expired`

Use `reason_code = policy-expired` when:

- the joined remembered-role `policy.decision` instance existed,
- it matched the attempted apply tuple,
- but the apply reached the boundary after `effective_constraints.intent_role_binding_apply.must_apply_before`.

This is a freshness failure, not a fresh policy evaluation denial.
A new authorization may still be issuable later.

### `policy-consumed`

Use `reason_code = policy-consumed` when:

- the joined remembered-role `policy.decision` instance existed,
- it matched the attempted apply tuple,
- but an earlier successful `initialized` or `updated` event had already consumed its single allowed success.

This is a consumption failure, not a class-level deny.
A later retry must use a freshly issued policy decision with a fresh `decision_instance_id` and therefore a fresh `policy_decision_digest`.
`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` now makes one more narrow evidence cut on top of this: the denial must also carry `consumed_by_event_id` so operators can name the earlier successful event that spent the authorization. `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` then fixes the recovery interpretation: only when that consuming success matches the same exact mutation tuple may the retry collapse to **already-applied** rather than remain an ordinary `policy-consumed` denial.

## Precedence against stale-write denial

`docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` now fixes one more branch-order detail for implementations:

- `policy-consumed` wins before `policy-expired`
- both policy-window reasons win before `precondition-failed`
- `precondition-failed` is only the winning denial once the joined exact authorization is still live

That keeps replay evidence stable over time and keeps compare-and-swap as the stale-state answer instead of a catch-all failure bucket.

## Event rule

For v0, remembered-role write-denied events now follow this narrower split:

- `policy-denied` — policy evaluation refused to authorize the write
- `policy-expired` — the exact joined authorization existed but was too old at apply time
- `policy-consumed` — the exact joined authorization existed but had already been spent by an earlier successful event
- `precondition-failed` — the diff was stale against newer remembered-role state

The event family does not gain a new object.
The existing `intent.role.binding.event` remains the durable mutation evidence lane.
The typed reason code is the minimum additional surface needed.

## Why this is the right cut

- **A / secure fleet host:** reconcile loops can tell the difference between “baseline no longer allowed”, “authorization expired before apply”, and “another worker already won consumption” without inventing a daemon-specific retry protocol in the archive.
- **B / secure workstation:** support-driven or org-managed remembered-role changes keep a compact support-bundle story when a queued apply reaches the boundary too late.
- **C / general-purpose OS:** host-local admin policy compilation stays viable because expired or spent local policy decisions can be explained with the same evidence vocabulary rather than shell-only errors.
- **D / appliance factory / regulatory:** offline recovery/import flows can distinguish outdated authorization from replayed already-spent authorization in deterministic exports.

This is smaller than a distributed consumption protocol.
It only sharpens the evidence contract around the boundary already chosen.

## Review rule

When a non-interactive remembered-role `write-denied` event carries `policy_decision_digest`, reviewers should now be able to answer:

1. did policy refuse to authorize this mutation at all?
2. did an exact authorization exist but expire before apply?
3. did an exact authorization exist but get consumed by an earlier successful event?
4. which policy decision instance did the failure concern?

If answers 2–4 still require daemon folklore or shell logs, the event reason surface is too loose.

## What this does **not** decide

This doc does **not** decide:

- replica/distributed coordination mechanics for deciding which contender wins a single-apply decision
- any write-back mutation of policy records to mark them consumed
- richer actor/quorum receipts
- or any larger remembered-role transaction family

Those remain later bounded choices.

## References

- Vault response wrapping (lookup distinguishes already-unwrapped / expired / revoked wrapping tokens): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping
- Vault Agent tutorial (additional unwrap attempts on an already-unwrapped token return an error): https://developer.hashicorp.com/vault/tutorials/vault-agent/agent-aws
- Temporary security credentials in IAM (expired temporary credentials cannot be reused): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html
- Use temporary credentials with AWS resources (calls fail after temporary credentials expire and a new set must be generated): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.write-denied.policy-window.schema.json`

Last updated: 2026-03-18r285