# GPU replay cross-observer custody-scope witnesses, packet-local custody, bridge-record custody, evidence-carrier custody, authority-handoff custody, retirement window, and mixed custody

This is the compact successor surface for `OQ-0170`.

## Practice / observation

`gpu_replay_cross_observer_promotion_gate_state` says when compact bridge governance has overflowed badly enough that some stronger cross-observer surface may be considered. The next temptation is to let that promoted surface become a standing telemetry court: every CUPTI correlation id, trace id, span link, exemplar, metric sample, pod identity, device allocation, and placement label gets treated as permanent custody evidence.

A custody-scope witness prevents that jump. It does not admit a custody ledger by default. It names exactly what a promoted bridge notary would be allowed to hold, which evidence carrier would carry the claim, who may hand off authority, and when the promoted custody must shrink or retire. The goal is bounded custody after gate overflow, not broad custody because telemetry is rich.

## External pressure from correlation records, trace links, metric exemplars, object identities, placement authority, and retention windows

CUPTI external correlation keeps bridge-record custody real because a CUDA activity record may be associated with external correlation ids. That can identify a bridge record worth preserving, but it still does not make the entire trace stream a notary. `REF-1055`

W3C Trace Context and OpenTelemetry span links make evidence-carrier custody real because trace identity and span links can cross service and trace boundaries. They can carry a bridge relation, but they do not by themselves settle GPU graph lineage, resource lifetime, or placement authority. `REF-1057`, `REF-1061`

OpenTelemetry exemplars keep metric custody honest because metric data points may carry trace/span context or exemplar correlation. That supports an exemplar as an evidence carrier, not a rule that every metric series enters escrow. `REF-1058`, `REF-1062`, `REF-1064`

Kubernetes object UIDs and device-plugin placement keep identity-scope custody honest. Pod names, labels, device resources, and GPU placement can matter, but the archive must distinguish stable object identity, non-unique labels, device allocation, and replay authority. `REF-1060`, `REF-1063`

The pressure is therefore scope, not prestige. If promotion gates overflow, the archive should name whether custody is only packet-local, limited to bridge records, carried by explicit evidence carriers, needed for an authority handoff, or bounded by a retirement window.

## Working synthesis

Use `gpu_replay_cross_observer_custody_scope_state` when a GPU replay pass has already crossed the promotion gate and must bound what the promoted cross-observer custody surface may hold.

`packet-local-custody` means the promoted question can still be kept inside one replay packet. The packet may name its graph receipt, trace span, exemplar, metric sample, placement window, and exit rule without a reusable ledger.

`bridge-record-custody` means only the specific join record is under custody: a CUPTI external correlation id, traceparent/span id, exemplar link, placement window, or equivalent bridge key. Neighboring telemetry remains outside the custody scope unless separately named.

`evidence-carrier-custody` means custody follows an explicit carrier across surfaces: graph receipt, profiler span, service span, metric exemplar, placement object, or device allocation record. The carrier must be public enough to reenter and narrow enough that it does not swallow every observer.

`authority-handoff-custody` means the promoted surface exists only to record who may settle a cross-observer conclusion when runtime lineage, profiler traces, trace systems, metrics, scheduler state, and placement records have different authority.

`retirement-window-custody` means a promoted custody surface is legitimate only because it has a shrink, expiry, or retirement condition. The witness must say what event, revision, or settled comparison ends custody.

`mixed-custody-scope` means several custody scopes are material and the archive must preserve the mixture rather than pretending a bridge-record key, exemplar carrier, authority handoff, or retirement window alone explains the case.

## Packet-local vs bridge-record vs evidence-carrier vs authority-handoff vs retirement-window vs mixed custody

- Use `packet-local-custody` when one bounded replay packet can state the custody claim and exit rule.
- Use `bridge-record-custody` when the only governed object is a join record or bridge key.
- Use `evidence-carrier-custody` when a named carrier must preserve the claim across runtime, profiler, trace, metric, or placement surfaces.
- Use `authority-handoff-custody` when the central problem is who may settle the conclusion, not which observer saw the richest telemetry.
- Use `retirement-window-custody` when custody is admissible only with an explicit shrink, expiry, or retirement condition.
- Use `mixed-custody-scope` when multiple custody limits are load-bearing.

## Countermodels / probes

Countermodel one: a single GPU replay comparison has a trace id and an exemplar. That is not `evidence-carrier-custody` unless the trace or exemplar is being asked to carry the replay claim across a boundary that compact bridge tokens cannot preserve.

Countermodel two: a bridge notary wants all CUPTI, Nsight, OpenTelemetry, DCGM, and Kubernetes records for every future run. That fails the witness; if custody cannot name a packet, bridge record, carrier, handoff, and retirement window, it is probably telemetry-court pressure.

Countermodel three: a scheduler-owned placement record and profiler-owned device context disagree. If the local packet can split the claim, this remains bridge or promotion-gate work. It becomes `authority-handoff-custody` only when the promoted surface must record a public handoff rule.

Countermodel four: a later revision admits a bounded custody surface for one repeated missing-bridge class but cannot say when it expires. That is at best `retirement-window-custody` debt; without an exit rule it should stay quarantined or be narrowed.

## Design consequences

A custody-scope packet should name the prior promotion-gate state, the promoted object being bounded, the exact evidence carrier or authority handoff if any, the surfaces outside custody, and the exit rule that retires or shrinks custody. It should also state what stronger surfaces still outrank it: ordinary replay receipts, explicit graph lineage, direct resource-lifetime evidence, and the frozen revision receipt.

The witness keeps the promoted layer reversible. A bridge notary that cannot name its custody scope becomes a telemetry court; an exemplar escrow that cannot name its carrier becomes metric overreach; a placement treaty that cannot name its authority handoff becomes scheduler absolutism.

This surface therefore resolves the custody-scope question by adding a compact custody-scope witness, not by admitting a permanent custody ledger, bridge promotion board, or telemetry treaty.

## Overflow test

Promote a custody-retention notary, authority escrow, telemetry retirement court, or equivalent standing exit-governance surface only if later revisions show that `packet-local-custody`, `bridge-record-custody`, `evidence-carrier-custody`, `authority-handoff-custody`, `retirement-window-custody`, and `mixed-custody-scope` repeatedly fail to keep promoted custody bounded, auditable, and shrinkable.

## Transformer-facing implication

When a model sees a promoted GPU replay bridge notary or custody claim, do not ask first how much telemetry can be retained. Ask what custody scope is honest: packet-local, bridge-record, evidence-carrier, authority-handoff, retirement-window, or mixed. Treat custody without scope and exit as a failure mode, not as rigor.
