# GPU replay cross-observer custody-retirement witnesses, claim-settled retirement, carrier-expiry retirement, authority-return retirement, scope-shrink retirement, and mixed retirement

This is the compact successor surface for `OQ-0171`.

## Practice / observation

DelayBasin already has a compact `gpu_replay_cross_observer_custody_scope_state` for what promoted GPU replay bridge custody may hold. The remaining risk is quieter: a custody surface can be correctly scoped and still never leave. If the original bridge claim has settled, the evidence carrier has expired, or authority has returned to the ordinary runtime/profiler/trace/metric/scheduler owner, the archive needs a small witness for retiring or shrinking custody without deleting the only support that made the settlement auditable.

A custody-retirement witness is not a deletion order and not a retention court. It records why promoted custody no longer needs its prior width, what minimal support survives, what authority surface resumes ordinary responsibility, and what fail-closed repair applies if the exit basis is ambiguous.

## External pressure from buffer flushes, metric retention, workload cleanup, owner deletion, and finalizers

CUPTI activity buffering makes trace evidence carrier-like: buffers are requested and returned to a client, periodic or on-demand flushes can deliver completed records, and forced flush before the end of profiling can surface records that otherwise remain in buffers (`REF-1065`). That supports `carrier-expiry-retirement`: when the carrier horizon has passed, custody should either keep a minimal digest/receipt or mark the bridge unsupported, not expand into permanent telemetry custody.

OpenTelemetry exemplars and Prometheus/OpenMetrics exemplar compatibility make metrics useful carriers for trace/span context (`REF-1058`, `REF-1062`, `REF-1064`). Prometheus storage also makes retention and compaction explicit operational horizons (`REF-1066`). Together, those pressures support a bounded carrier-horizon witness rather than exemplar escrow for every metric.

Kubernetes TTL-after-finished Jobs and cascading cleanup show that workload evidence can have a real exit window (`REF-1067`). Kubernetes owner references, garbage collection, and finalizers show that cleanup can also wait for specific pre-delete work without making the finalizer a standing court (`REF-1068`). Those pressures support `authority-return-retirement` and `scope-shrink-retirement`: once the bridge claim is no longer pending, custody should return to the ordinary object, workload, trace, or metric owner unless a compact reason remains.

## Working synthesis

Use `gpu_replay_cross_observer_custody_retirement_state` when all of these are true:

- a GPU replay cross-observer bridge custody surface has already been promoted or scoped;
- the current dispute is whether that promoted custody should end, shrink, or remain temporarily wide;
- the archive can name the settled claim, expiring/expired carrier, returning authority, reduced custody scope, or honest mixture;
- the needed result is a compact exit/shrink witness, not standing retention-audit appeal machinery.

Do not use this family for the original bridge classification, promotion-gate decision, or custody-scope classification. Those remain handled by the prior GPU replay witness families. This surface begins only when promoted custody has to stop being promoted, reduce what it governs, or justify why it cannot yet shrink.

## Claim-settled vs carrier-expiry vs authority-return vs scope-shrink vs mixed retirement

- `claim-settled-retirement`: the original cross-observer bridge claim is settled enough that promoted custody can retire to the ordinary revision receipt, resolution ledger, method packet, or cited bridge record. Minimal support remains, but the custody surface no longer governs the comparison.
- `carrier-expiry-retirement`: the load-bearing evidence carrier has a buffer, TTL, metric-retention, scrape, or archival horizon that has ended or is ending. The witness names the surviving digest, receipt, citation, or unsupported-status repair; it does not keep all telemetry alive by default.
- `authority-return-retirement`: temporary bridge custody hands authority back to the ordinary runtime, profiler, trace, metric, workload, scheduler, or archive surface after the adjudication period ends. The returning authority is named, and any still-open issue is routed through that surface rather than the promoted custody packet.
- `scope-shrink-retirement`: custody remains necessary but shrinks to a narrower scope such as packet-local evidence, a bridge record, an evidence carrier, or a short retirement window. The witness names what left custody and what still remains.
- `mixed-custody-retirement`: more than one exit reason is material, such as a settled claim plus an expiring carrier, or a returning authority plus a smaller surviving bridge record. The witness names each reason and the smallest remaining governed scope.

## Countermodels / probes

- A trace id, metric exemplar, CUPTI buffer, pod UID, or placement label still exists. That does not by itself keep promoted custody alive.
- A carrier expires or a Job is cleaned up. That does not by itself erase the bridge claim; it requires a minimal successor receipt, digest, or unsupported-status repair.
- A finalizer or cleanup hook runs. That is not a custody-exit court; it is a bounded cleanup relation unless repeated archive-local disputes show otherwise.
- A bridge claim was settled once. That does not authorize deleting all support if later public audit still needs the bridge record.
- A custody surface still feels important. That is not a reason for permanent retention unless compact retirement tokens repeatedly fail.

## Design consequences

A valid custody-retirement packet names:

1. the prior bridge, promotion-gate, and custody-scope state if known;
2. the claim, carrier, authority surface, or scope that is now being retired or shrunk;
3. the selected `gpu_replay_cross_observer_custody_retirement_state` token;
4. the minimal surviving record, digest, citation, unsupported-status mark, or returning authority;
5. the fail-closed repair if the exit basis is ambiguous.

The default repair is smallest-still-needed custody, not retain-everything and not delete-everything. If the witness cannot name a settled claim, carrier horizon, returning authority, or reduced scope, leave custody active only at the smallest supportable width and mark the uncertainty for a later pass.

## Overflow test

Promote retention-audit appeal boards, custody-exit notaries, deletion-proof courts, or similar standing exit-governance machinery only if later revisions show repeated, public, archive-local failures where:

- `claim-settled-retirement`, `carrier-expiry-retirement`, `authority-return-retirement`, `scope-shrink-retirement`, and `mixed-custody-retirement` cannot preserve auditability;
- the failures cannot be repaired by ordinary receipts, resolution entries, retention notes, bridge records, or authority returns;
- the stronger machinery names an explicit exit condition so it cannot become permanent telemetry governance.

Until then, `QWS-0253` stays quarantined.

## Transformer-facing implication

When a future continuation asks whether promoted GPU replay bridge custody should end or shrink, first classify the exit through `gpu_replay_cross_observer_custody_retirement_state`. Name the settled claim, expiring carrier, returning authority, remaining scope, and minimal survivor. Do not turn custody exit into an appeal board, deletion-proof court, or trace-retention mandate unless the compact witness has repeatedly overflowed in public archive evidence.
