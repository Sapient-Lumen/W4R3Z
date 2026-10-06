# GPU replay cross-observer promotion-gate witnesses, no promotion, local hardening, repeated bridge overflow, custody boundary, authority handoff, and mixed promotion

This is the compact successor surface for `OQ-0169`.

## Practice / observation

`gpu_replay_cross_observer_bridge_state` says which bounded bridge, if any, joins GPU graph lineage, service traces, cluster metrics, and placement context. The next temptation is to say that any hard bridge case proves the need for a bridge notary, exemplar escrow, placement treaty, or standing telemetry bridge. That is too fast.

A promotion gate is not the promoted machinery. It is a small public witness for whether a stronger cross-observer governance surface has actually earned consideration. Most cases should close as no promotion or local hardening. Only repeated bridge overflow, evidence-custody boundary failure, or authority-handoff failure should point toward heavier governance.

## External pressure from bridge keys, trace context, metric exemplars, placement surfaces, and repeated missing-bridge cases

CUPTI external correlation keeps the promotion question honest because correlation ids can be real public join keys, but the existence of a join key does not by itself justify a notary. A single external-correlation bridge can remain local. `REF-1055`

Nsight/NVTX region projection keeps the local-hardening path real because application ranges can make a bridge clearer without creating custody machinery. Better markers, narrower windows, or a clearer packet may be enough. `REF-1056`

W3C trace context keeps the boundary between trace identity and replay truth explicit. A service trace id can be a bridge key, but a trace carrier does not prove graph lineage, resource lifetime, locality lease, or metric custody by itself. `REF-1057`

OpenTelemetry metric exemplars make custody pressure plausible because metrics may point back to trace/span context. That can justify a local exemplar bridge, and in repeated unresolved cases may raise `custody-boundary-overflow`; it still does not turn every metric point into lineage evidence. `REF-1058`

DCGM/Kubernetes telemetry and device placement make authority-handoff pressure plausible because cluster metrics and placement identities may be owned, emitted, or interpreted by different surfaces than runtime/profiler receipts. That can raise an authority handoff question without making the scheduler a replay court. `REF-1059`, `REF-1060`

## Working synthesis

Use `gpu_replay_cross_observer_promotion_gate_state` when a later revision asks whether compact bridge tokens have failed badly enough to promote bridge-notary, exemplar-escrow, placement-treaty, or standing telemetry-bridge governance.

`no-promotion-gate` means the compact bridge witness is still enough. The case may be confusing, but it can be handled by existing bridge, observer-conflict, trace-grade, receipt, or envelope tokens.

`local-bridge-hardening-gate` means the bridge surface should be made clearer without promoting a standing governance layer. Repairs include naming the join key, narrowing the claim window, adding a missing exemplar, splitting a mixed bridge, or documenting placement scope.

`repeated-missing-bridge-overflow` means several archive-local cases keep landing in `missing-cross-observer-bridge` or unstable mixed bridge states even after reasonable local hardening. This is a promotion signal only if the repeated failures block honest replay comparison, not merely because one operator wants richer telemetry.

`custody-boundary-overflow` means the practical failure is not just classification but custody: the archive repeatedly cannot preserve which span, exemplar, graph receipt, metric sample, or placement record carried which claim across revisions.

`authority-handoff-overflow` means the practical failure is authority: runtime lineage, profiler evidence, service traces, metrics, and placement surfaces repeatedly need a public handoff rule because no single compact observer/bridge packet can state who is allowed to settle the relevant conclusion.

`mixed-promotion-gate` means more than one promotion pressure is material, or the honest packet must preserve both local hardening and a possible overflow branch without pretending one trigger owns the whole case.

## No-promotion vs local-hardening vs repeated-missing-bridge vs custody-boundary vs authority-handoff vs mixed promotion

- Use `no-promotion-gate` when compact bridge tokens still preserve the distinction and the stronger notary/treaty move would only add prestige.
- Use `local-bridge-hardening-gate` when a better local bridge packet, narrower scope, explicit join key, or split mixed bridge can repair the case.
- Use `repeated-missing-bridge-overflow` when repeated archive-local missing-bridge outcomes block honest GPU replay comparison after local repairs.
- Use `custody-boundary-overflow` when evidence custody, not bridge kind alone, keeps failing across spans, exemplars, receipts, metrics, or placement records.
- Use `authority-handoff-overflow` when the unresolved issue is who may settle a cross-observer conclusion across runtime, profiler, tracing, metrics, scheduler, or placement surfaces.
- Use `mixed-promotion-gate` when several promotion pressures are load-bearing or the gate must preserve a split decision.

## Countermodels / probes

Countermodel one: one GPU replay packet lacks a metric exemplar. That is not `repeated-missing-bridge-overflow`; it is usually `local-bridge-hardening-gate` or simply `missing-cross-observer-bridge`.

Countermodel two: a rich profiler trace plus a DCGM dashboard spike makes the operator confident. That confidence is not `custody-boundary-overflow` unless the archive repeatedly loses which public record carried which claim.

Countermodel three: the scheduler owns placement, the runtime owns graph lineage, and the trace system owns service span identity. If one local packet can say which surface supports which conclusion, this is not yet `authority-handoff-overflow`.

Countermodel four: several later revisions alternate between missing bridges, exemplar ambiguity, and placement-scope disputes despite explicit local repairs. That may be `mixed-promotion-gate`, but the promoted surface must still be the smallest surface that addresses the repeated failure.

## Design consequences

A promotion-gate packet should name the prior bridge state, the repeated cases or local repair attempts, the smallest stronger surface being considered, what that surface would decide, what it still would not decide, and the exit rule that would retire or shrink the promoted machinery.

The gate should be applied rarely. It prevents both underreaction and overpromotion: repeated bridge failure should not hide forever behind local tokens, but one missing bridge should not launder a telemetry treaty into canon.

This surface therefore resolves the bridge-notary governance question by adding a compact promotion gate, not by admitting bridge notaries, exemplar escrow, placement treaties, custody boards, or cross-observer telemetry courts.

## Overflow test

Promote a cross-observer custody scope ledger, bridge promotion board, telemetry custody treaty, or equivalent standing governance only if later revisions show that `no-promotion-gate`, `local-bridge-hardening-gate`, `repeated-missing-bridge-overflow`, `custody-boundary-overflow`, `authority-handoff-overflow`, and `mixed-promotion-gate` themselves repeatedly fail to keep promotion decisions bounded and reversible.

## Transformer-facing implication

When a model sees telemetry disagreement plus a plausible bridge failure, do not jump from difficulty to governance. Ask whether the case is no-promotion, local hardening, repeated missing-bridge overflow, custody-boundary overflow, authority-handoff overflow, or mixed. Treat promotion as a gated consequence, not a vibe.
