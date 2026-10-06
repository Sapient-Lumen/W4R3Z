# Role-binding policy decisions must bind the exact mutation

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

`docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` already fixed that non-interactive remembered-role changes join to `policy.decision` through `policy_decision_digest`.
`docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` then fixed compare-and-swap for reviewed updates.
`docs/547-role-binding-support-import-join-via-content-import-receipt.md` and `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md` kept import provenance and authority lanes explicit.

This doc makes the next small hard decision:

> when a remembered-role event points at `policy_decision_digest`, that policy decision must bind the exact mutation tuple instead of a vague class of “allowed role-binding changes”.

See also:
- ADR: `adrs/ADR-0139-role-binding-policy-decisions-bind-exact-mutation.md`
- generic policy decisions: `docs/93-policy-decision-records.md`
- non-interactive role-binding lane: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- stale-write boundary: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- authority-lane normalization: `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- schema: `spec/intent.role.binding.policy.profile.schema.json`
- example: `spec/examples/intent.role.binding.policy.profile.json`
- freshness / consumption boundary: `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- issuance-identity boundary: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`

## Why this needs a hard decision

The archive already answers several important remembered-role questions cleanly:

- what state is authoritative? `intent.role.binding`
- how do humans review a change? `intent.role.binding.diff`
- what durable event proves the mutation? `intent.role.binding.event`
- what joined authority surfaces explain why it happened? `consent_receipt_digest`, `policy_decision_digest`, `import_receipt_digest`

But one ambiguity was still expensive:
`policy_decision_digest` named the policy artifact, yet the archive did not say how narrowly that policy decision had to bind the exact mutation.

Without that narrowing, implementation pressure drifts toward broad allow records such as:

- "this host may reconcile remembered roles"
- "this admin flow may apply defaults"
- "support import may restore role bindings"

Those are useful ideas, but they are too wide for evidence and replay.
They do not say which host/profile was in scope, which resulting binding digest was allowed, which precondition digest guarded the update, or which import receipt the policy actually considered.

That is the gap between an auditable concept and a spec worth coding. `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` then makes one more small cut on top of this one by fixing how long that exact tuple stays valid and how many successful writes it may authorize. `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` makes the next one by ensuring later re-issuance of the same exact tuple does not collapse to the same digest as an earlier decision instance.

## Accepted boundary

The archive now ships a constrained profile over `policy.decision`:

- `spec/intent.role.binding.policy.profile.schema.json`

It keeps the generic `kind = policy-decision` record, but requires two remembered-role-specific subobjects:

1. `inputs.intent_role_binding_request`
2. `effective_constraints.intent_role_binding_apply`

The request block captures the policy-relevant facts presented to the engine.
The apply block captures the exact mutation tuple the decision allowed.

## Canonical request facts

`inputs.intent_role_binding_request` must identify the exact remembered-role request shape the policy saw:

- `trigger` — `policy-reconcile` or policy-governed `support-import`
- `subject.host_id` and `subject.profile_id`
- `roles_touched`
- `requested_binding_digest`
- `from_binding_digest` for `requested_action = updated`
- `import_receipt_digest` when `trigger = support-import`

This keeps the policy input compact while still answering the questions operators actually ask later:

- which host/profile was in scope?
- which roles were changing?
- was this an initialize or an update?
- if it was an update, what current binding did policy expect?
- if it was import-driven, which typed intake artifact did policy see?

## Canonical apply constraints

`effective_constraints.intent_role_binding_apply` must identify the exact mutation tuple the system is allowed to perform:

- `apply_mode` — `initialized` or `updated`
- `subject.host_id` and `subject.profile_id`
- `require_event_trigger` — `policy-reconcile` or `support-import`
- `roles_touched`
- `binding_digest`
- `from_binding_digest` and `diff_digest` for `apply_mode = updated`
- `import_receipt_digest` when `require_event_trigger = support-import`

This is the actual implementation payoff.
The joined policy decision no longer just says "policy allowed something in this area".
It says which exact remembered-role mutation may land, under which authority lane, against which expected old state.

## Why this is the right cut

This is intentionally narrower than a full admin transaction system.
It is just enough structure to keep A–D coherent:

- **A / secure fleet host:** background reconcile can still be non-interactive, but the decision must bind the exact host/profile/binding tuple instead of a daemon-shaped blanket permission.
- **B / secure workstation:** org-managed or restore-driven changes can use the non-interactive lane without pretending a background prompt happened and without weakening the interactive consent lane.
- **C / general-purpose OS:** host-local admin tooling stays viable because it can compile a host-local remembered-role request to the same exact-mutation `policy.decision` profile instead of inventing a shell-shaped authority family.
- **D / appliance factory / regulatory:** baseline or recovery imports remain audit-friendly because the allow record binds the exact resulting binding and, when relevant, the exact `content.import.receipt` digest.

## Review rule

When a remembered-role event carries `policy_decision_digest`, reviewers should be able to answer all of these from the joined policy record without shell folklore:

1. Which host/profile was the decision about?
2. Which trigger lane was allowed?
3. Which roles were in scope?
4. Which resulting binding digest was allowed?
5. If this was an update, which prior binding digest and diff digest formed the precondition?
6. If this was support/import-driven, which import receipt digest did the decision bind?

If the answer to any of those questions is "somewhere else" or "implicit in the tool", the policy record is too loose.

## Event semantics after this cut

`intent.role.binding.event` does not gain new fields in this iteration.
Instead, the meaning of `policy_decision_digest` becomes stricter:

- the event still carries the digest join,
- the joined `policy.decision` must now conform to the remembered-role policy profile,
- the joined profile is now also expected to be short-lived single-apply through `must_apply_before` plus `max_successful_events = 1`,
- the joined profile must also carry `decision_instance_id` so independently issued authorizations for the same tuple remain distinguishable,
- and support/import policy decisions must bind the same `import_receipt_digest` the event reports.

That keeps the event family small while making the policy object worth enforcing.

## What this does **not** decide

This doc does **not** decide:

- the full language for distributing remembered-role baselines across fleets,
- richer org-shared actor/quorum graphs,
- whether multiple remembered-role objects may later batch into one higher-order transaction,
- or transport/auth details for admin tools.

Those remain later bounded choices.

## References

- DeriveBSD policy decision records: `docs/93-policy-decision-records.md`
- Android Enterprise managed configurations (IT admins remotely specify app settings): https://developer.android.com/work/managed-configurations
- Microsoft ApplicationDefaults policy CSP (admins set default file/protocol associations through policy): https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-applicationdefaults
- Windows default application association XML import/export guidance: https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/export-or-import-default-application-associations?view=windows-11
- Kubernetes Mutating Admission Policy (mutations can be defined as apply configuration or JSON patch): https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/
- Kubernetes admission request schema (`object` and `oldObject` on admission requests): https://kubernetes.io/docs/reference/config-api/apiserver-admission.v1/

## Related docs

- `docs/93-policy-decision-records.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `spec/intent.role.binding.policy.profile.schema.json`

Last updated: 2026-03-18r281
