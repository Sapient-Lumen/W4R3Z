# Role-binding event as durable mutation evidence

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Registry→Diff→Gate, Bundles  

`docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed the authoritative remembered state as `intent.role.binding`.
`docs/542-role-binding-diff-as-review-surface.md` fixed the compact review surface as `intent.role.binding.diff`.
This doc fixes the next practical question:

> when remembered browser/mail role ownership changes, what durable event should the evidence journal and support bundles keep?

The answer should not be “grep a GUI settings log” or “hope shell history captured it.”
The archive now standardizes a bounded Event Journal artifact:

- `intent.role.binding.event`

See also:
- ADR: `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md`
- remembered state boundary: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- compact review surface: `docs/542-role-binding-diff-as-review-surface.md`
- structured event journal: `docs/215-structured-event-log-as-evidence.md`
- support bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- stale-write denial boundary: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- authority-lane normalization: `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- exact-mutation policy profile: `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- issuance-identity boundary: `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- typed policy-window denials: `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`

## Why this needs a hard decision

Without a typed durable event, the archive still leaves a real implementation cliff:

- trusted settings/admin UX can review a change,
- route receipts can prove which remembered snapshot routed a request,
- but postmortems still lack one compact answer to **when** that remembered state changed.

That gap is where systems usually regress into folklore:

- ad-hoc settings logs,
- desktop shell databases,
- shell history,
- or an oversized settings journal introduced too early.

A smaller answer is better here.
DeriveBSD already uses snapshot + diff + event in other lanes, and remembered role/default state is important enough to deserve the same treatment.

## The artifact

Schema: `spec/intent.role.binding.event.schema.json`  
Example: `spec/examples/intent.role.binding.event.json`

`intent.role.binding.event` is the durable mutation-trace artifact for remembered role/default state.
It should be emitted by trusted settings/admin implementations and stored in the event journal.

### v0 action vocabulary

Keep the action set intentionally small:

- `initialized` — first authoritative binding snapshot was created
- `updated` — remembered role/default state changed
- `write-denied` — a mutation attempt was rejected by boundary/policy; stale reviewed diffs carry typed `reason_code` plus `observed_binding`, while non-interactive policy-window failures now stay distinct as `policy-expired` or `policy-consumed` instead of collapsing into generic denial, and `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` now fixes that those policy-window reasons win before `precondition-failed` in the non-interactive lane

### What the event should carry

For v0, the event should stay focused on high-signal joins:

- which host/profile the event applies to
- the resulting binding snapshot digest
- the previous binding digest when one existed
- the diff digest when a compact posture diff exists
- the touched roles (`browsing`, `communications`)
- stable `risk_flags` copied or derived from the diff when appropriate
- bounded trigger/source metadata plus narrow authority joins (`consent_receipt_digest`, `policy_decision_digest`, `import_receipt_digest`), not a universal actor/approval model; trigger names the authority lane while concrete invokers stay in `source.*`

## Noise rule (keep this smaller than a settings journal)

`intent.role.binding.event` is **not** the full trusted-settings receipt family.
Do not overload it with:

- arbitrary GUI state,
- full transaction replay,
- ambient desktop-registry dumps,
- chooser MRU history,
- or a mandatory actor/approver graph.

If later work needs a replayable settings-operation receipt family, add that as a separate typed artifact family.
For now, the product boundary stays small:

- `intent.role.binding` — authoritative remembered snapshot
- `intent.role.binding.diff` — compact posture review surface
- `intent.role.binding.event` — durable time-ordered mutation evidence

## Where it plugs in

### 1) Structured event journal

Remembered-role/default changes belong in the host event journal alongside service, fault, sysctl, kmod, and other mutation evidence.
That makes the question “when did browser/mail ownership change?” queryable without a desktop-specific side channel.

See: `docs/215-structured-event-log-as-evidence.md`.

### 2) Incident/support bundles

When workstation routing/default behavior matters to an incident, bundles should include:

- the current `intent.role.binding` digest,
- recent `intent.role.binding.event` digests,
- and the latest `intent.role.binding.diff` digest when applicable.

That keeps remembered-role drift exportable without dumping shell or GUI settings internals. When the mutation came from non-interactive reconcile/import policy, the supporting bundle slice should also carry the joined `policy_decision_digest`. That digest now implies the exact-mutation `intent.role.binding.policy.profile` rather than a broad class of remembered-role allowances, and the joined policy record now also carries `decision_instance_id` so separately issued single-apply authorizations for the same tuple stay distinguishable. When the mutation came from a support/import/recovery lane, the same slice should also carry `import_receipt_digest` so operators can prove which typed `content.import.receipt` actually produced or attempted the remembered-role change.

See: `docs/216-incident-snapshots-and-support-bundles.md`.

### 3) Trusted settings/admin UX

Trusted settings/admin implementation now has a small evidence trio instead of a giant platform requirement:

- write the new remembered snapshot,
- generate the compact diff when the snapshot changed,
- emit the durable event that points at both.

That is enough to start implementation work while deferring richer actor/approval receipts. For the profile **B** trusted-settings lane, `intent.role.binding.event` may also carry `consent_receipt_digest` so the durable event trail joins back to the generic consent substrate when interactive approval authorized or denied the change. For non-interactive `policy-reconcile` mutations, it may instead carry `policy_decision_digest` so the same event family points back to the exact `policy.decision` record that authorized the reconcile. `docs/549-role-binding-policy-decisions-bind-exact-mutation.md` now narrows that join further: the policy record must describe the exact request/apply tuple through `spec/intent.role.binding.policy.profile.schema.json` rather than a vague “role-binding reconcile allowed” claim. `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` narrows it again: that exact-mutation policy record is also a short-lived single-apply authorization with `must_apply_before` plus `max_successful_events = 1`, so successful remembered-role writes do not inherit a reusable background permission. `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` adds one more implementation detail without expanding the event family: the joined policy record must also carry `decision_instance_id`, so a later re-issuance of the same exact tuple does not collapse to the same digest as an earlier consumed authorization. `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` adds the next operational cut: if a non-interactive apply reaches the boundary too late or after prior consumption, the event keeps `policy_decision_digest` but now reports `reason_code = policy-expired` or `reason_code = policy-consumed` instead of hiding those cases inside generic `policy-denied`. `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` then removes the remaining branch-order ambiguity: in the non-interactive lane, policy-window validity is evaluated before compare-and-swap, `policy-consumed` wins before `policy-expired`, and both win before `precondition-failed`, so the durable event tells operators whether to re-issue authority or re-read state. `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` adds the next small join: when the winning denial is `policy-consumed`, the event must also carry `consumed_by_event_id` so support and retry logic can point at the earlier successful consuming event instead of reconstructing it from timing alone. `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` tightens that join one more notch: the same denial must also carry `consumed_by_event_digest`, so detached bundles can verify the exact consuming event bytes rather than trusting only an id pointer. `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` adds the next result summary: the same denial must also carry `consumed_binding_digest`, exposing the earlier winner's `binding.digest` as evidence-only summary data instead of forcing support/export/retry clients to reopen the winner event body first. `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` adds the next review summary: the same denial must also carry `consumed_diff_digest`, exposing the earlier winner's `diff.digest` as evidence-only summary data instead of forcing support/export/retry clients to reopen the winner event body just to learn which reviewed change actually landed. `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` adds the next old-edge summary for updated winners: the same denial may also carry `consumed_previous_binding_digest`, exposing the earlier winner's `previous_binding.digest` as evidence-only summary data instead of forcing support/export/retry clients to reopen the winner event body just to learn which compare-and-swap starting point that winner replaced. `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` adds the next winner-shape summary: the same denial must also carry `consuming_event_action`, so detached readers can tell whether the earlier success was an `initialized` first-write or an `updated` compare-and-swap and can mechanically interpret whether `consumed_previous_binding_digest` should exist. `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` then fixes the recovery interpretation: only when that digest-bound consuming success proves the same exact mutation tuple may the retry collapse to **already-applied** rather than remain an ordinary spent-authority denial. `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` adds the next small operability cut on top: when the denial is `policy-consumed`, the event must also carry `recovery_interpretation` so support bundles and retry views can read a stable evidence-only summary (`policy-consumed` or `already-applied`) instead of re-deriving it from notes or local heuristics. For `support-import` mutations, it should carry `import_receipt_digest` so the event trail joins back to the exact typed import receipt rather than forcing support operators to infer provenance from paths or shell history. `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md` now tightens one more ambiguity: a local CLI, remote management wrapper, or daemon belongs in `source.*`, while `trigger` still names the authority/apply lane rather than the transport that invoked it.

## Product-shape fit without forks

- **A / secure fleet host:** usually has thin or absent interactive role bindings, but maintenance/operator surfaces can still emit the same event family if those bindings exist.
- **B / secure workstation:** primary beneficiary; remembered browser/mail ownership gets a real mutation timeline instead of settings folklore.
- **C / general-purpose OS:** can reuse the same event family even if later compatibility layers broaden handler options.
- **D / appliance factory / regulatory:** production images may compile to little or no role state, but maintenance images and support workflows can still benefit from the same typed event.

## References

- Android RoleManager (explicit roles and explicit role-request flow): https://developer.android.com/reference/android/app/role/RoleManager
- XDG AppChooser backend (chooser from a provided list, including optional `last_choice` hint): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.AppChooser.html
- XDG Settings backend (read-only; not for general purpose settings): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Settings.html
- Qubes OS backup/restore guide (explicit restore workflow and verify-only restore path): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-back-up-restore-and-migrate.html

## Related docs

- `docs/215-structured-event-log-as-evidence.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`
- `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`
- `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`
- `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-18r291
