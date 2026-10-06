# Role-binding policy-decision join for non-interactive mutations

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`docs/542-role-binding-diff-as-review-surface.md` fixed the compact review surface as `intent.role.binding.diff`.
`docs/543-role-binding-event-as-durable-mutation-evidence.md` fixed the durable mutation trail as `intent.role.binding.event`.
`docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md` fixed the interactive workstation approval lane by joining remembered-role changes to constrained `consent.request` / `consent.receipt` profiles.

This doc makes the next narrow hard decision:

> non-interactive remembered role/default mutations join to `policy.decision` instead of inheriting workstation prompts or drifting into admin folklore.

See also:
- ADR: `adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- authority-lane normalization: `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- exact-mutation policy profile: `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- apply-window / consumption boundary: `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- issuance-identity boundary: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- typed policy-window denials: `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- policy decisions: `docs/93-policy-decision-records.md`
- approval posture by profile: `docs/474-high-risk-approval-posture-by-profile.md`
- remembered state: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- review surface: `docs/542-role-binding-diff-as-review-surface.md`
- durable event trail: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- interactive lane: `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`

## Why this needs a hard decision

The archive now has a good answer for profile **B** interactive remembered-role changes:

- review a typed `intent.role.binding.diff`
- get a constrained `consent.receipt`
- emit a durable `intent.role.binding.event`

But that is not the whole product.
A / C / D still need a compact answer for policy-shaped, non-interactive changes such as:

- fleet reconcile applying an approved remembered-role baseline,
- maintenance or admin tooling reconciling a dedicated-device image,
- import/recovery flows restoring remembered-role state under explicit policy,
- or a general-purpose install applying an explicit local policy profile.

If those changes are just “whatever the reconcile daemon wrote,” the archive still loses a practical question:

- which authority object allowed this non-interactive remembered-role mutation?

DeriveBSD already has the right generic artifact for machine-authorized changes:

- `policy.decision`

So the smallest coherent move is not a new role-binding approval family, but a join back to the existing policy-decision record.

## Accepted boundary

For non-interactive remembered role/default mutations, the official authority/provenance joins are now:

- `intent.role.binding.event.policy_decision_digest` for policy-governed reconcile/apply
- `intent.role.binding.event.import_receipt_digest` for support/import/recovery mutations

This keeps the event family small while making both non-interactive authority and import provenance explicit. The joined remembered-role policy profile is now also bounded as a short-lived single-apply authorization: `effective_constraints.intent_role_binding_apply` must carry `must_apply_before` plus `max_successful_events = 1`, so a successful remembered-role write consumes the allow record instead of turning reconcile/import/admin policy into standing authority. The joined policy record must now also carry `decision_instance_id`, so a later re-issuance of the same exact tuple stays distinguishable from an already-consumed earlier authorization. When such a joined authorization exists but fails at apply time, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` now requires `reason_code = policy-expired` or `reason_code = policy-consumed` rather than collapsing those cases into generic `policy-denied`. `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` then fixes the branch order: these policy-window checks are normal request checks for the non-interactive lane and therefore win before any `precondition-failed` compare-and-swap denial.

## Event rule

`intent.role.binding.event` now carries optional:

- `policy_decision_digest`
- `import_receipt_digest`

For v0:

- `trigger = policy-reconcile` requires `policy_decision_digest`
- `trigger = trusted-settings-ui` stays on the interactive consent lane and does not require either field
- `trigger = support-import` requires `import_receipt_digest` and may also attach `policy_decision_digest` when import/replay policy explicitly governed the mutation
- admin tooling, local CLI, remote orchestration, or reconcile-daemon identity lives in `source.name` / `source.service_id`; it is not a separate trigger vocabulary item

This is the whole join:

- snapshot: `intent.role.binding`
- review surface: `intent.role.binding.diff`
- durable mutation event: `intent.role.binding.event`
- interactive authority proof: `consent_receipt_digest`
- non-interactive authority proof: `policy_decision_digest`
- support/import provenance proof: `import_receipt_digest`

## Why reuse `policy.decision`

The archive already uses `policy_decision_digest` elsewhere to answer “why was this allowed?”
Reusing it here has three advantages:

1. it keeps role-binding mutations on the same evidence language as other DeriveBSD runtime and promotion decisions,
2. it keeps A / C / D coherent without forcing workstation prompts onto fleet/factory/maintenance images,
3. it avoids inventing a separate role-binding policy receipt family or another one-off authority artifact before implementation pressure proves it is needed.

## Product-shape fit without forks

- **A / secure fleet host:** this is the main fit for baseline reconcile. Fleet policy can pin remembered-role state where it exists, and the event answers which `policy.decision` authorized it.
- **B / secure workstation:** ordinary personal changes stay on the consent lane, but org-controlled reconcile can still use the policy-decision join without pretending a background prompt happened.
- **C / general-purpose OS:** local-admin viability stays real because a trusted CLI can compile host-local policy to `policy.decision` and still emit `trigger = policy-reconcile`.
- **D / appliance factory / regulatory:** dedicated devices and regulated images usually want policy-governed non-interactive state application rather than workstation prompts. This join keeps that path explicit and auditable.

## Incident / support effect

When remembered-role/default behavior matters to an incident, support surfaces should now be able to show:

- the current `intent.role.binding` digest,
- the latest `intent.role.binding.diff` digest when posture changed,
- recent `intent.role.binding.event` records,
- joined `consent.receipt` digests for interactive workstation changes,
- joined `policy_decision_digest` values for non-interactive reconcile/import changes,
- `import_receipt_digest` values when support/import/recovery workflows actually carried the remembered-role mutation,
- and the joined remembered-role apply window (`must_apply_before`, `max_successful_events = 1`) plus `decision_instance_id` for successful non-interactive writes.

That keeps support bundles and event-journal exports explainable across all product shapes instead of only for the workstation prompt case. The apply rule is still compare-and-swap against the current binding digest, but only after the joined policy-window checks still leave live authority to proceed: if reconcile races with a newer remembered-role mutation after passing those policy checks, it must emit `write-denied` with `reason_code = precondition-failed` and `observed_binding` rather than silently rebasing. When the winning denial is `policy-consumed`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` now requires `consumed_by_event_id` so the same event trail can identify the earlier successful event that already spent the joined authorization. `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` then makes that winner portable: the denial must also carry `consumed_by_event_digest`, so detached support bundles can verify the exact consuming event bytes without trusting a live journal lookup. `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` adds the winner's resulting state handle next to that verifier: the same denial must now also carry `consumed_binding_digest`, exposing the earlier success's `binding.digest` as evidence-only summary data. `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` adds the winning review-surface handle next to that result summary: the same denial must now also carry `consumed_diff_digest`, exposing the earlier success's `diff.digest` as evidence-only summary data. `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` then constrains retry semantics further: only when that digest-bound consuming success matches the same exact mutation tuple may reconcile/import/admin tooling collapse the retry to **already-applied** instead of leaving it as an ordinary spent-authority denial. `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` then makes that answer queryable: `reason_code = policy-consumed` must now also carry `recovery_interpretation`, with `already-applied` allowed only when the exact-match replay proof exists and `policy-consumed` used otherwise.

## What this does **not** decide

This doc does **not** decide:

- a full replayable settings/admin transaction log,
- broader role-binding baseline distribution language beyond the exact mutation tuple,
- richer actor/quorum graphs for organization-shared mutations,
- or transport/auth details for admin tooling.

Those remain later bounded choices.

## References

- DeriveBSD policy decision records: `docs/93-policy-decision-records.md`
- Android Enterprise managed configurations (IT admins remotely specify app settings): https://developer.android.com/work/managed-configurations
- Android Enterprise dedicated devices overview (fully managed devices for a specific purpose): https://developer.android.com/work/dpc/dedicated-devices
- Android RoleManager API reference: https://developer.android.com/reference/android/app/role/RoleManager
- XDG Desktop Portal AppChooser backend (chooser from a provided list): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.AppChooser.html
- XDG Desktop Portal Settings backend (read-only; not for general purpose settings): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Settings.html
- RFC 9110 conditional requests / `If-Match` (preventing the lost-update problem): https://www.rfc-editor.org/rfc/rfc9110
- Kubernetes admission controllers (mutating/validating policy is distinct from the requesting client): https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/

## Related docs

- `docs/93-policy-decision-records.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/474-high-risk-approval-posture-by-profile.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-18r289
