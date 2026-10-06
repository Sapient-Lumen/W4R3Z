# Enforcement-regime witnesses, bootstrap-only gating, continuous enforcement, and dry-run rehearsal

This is the compact successor surface for `OQ-0129`.

## Practice / observation

Once DelayBasin already distinguishes selector coverage, selector provenance, selector freshness, and selector enforcement, one further failure mode stays live: a rule can still be real, current, and even genuinely enforced somewhere while the archive still cannot say whether that rule only gated entry, keeps policing runtime conditions, or is only rehearsing impact without acting.

A row can truthfully say that the same GPU readiness condition, startup gate, admission policy, device-binding precondition, or workload check is still part of the current system, yet that phrase can still hide whether the rule stopped mattering once admission or startup succeeded, kept monitoring the running object, or only simulated what enforcement would do.

The compact repair is one small enforcement-regime witness. It does not replace the selector, selector-provenance, selector-freshness, or selector-enforcement witnesses. It only says whether the current rule is bootstrap-only, continuously enforced, dry-run only, or mixed.

## External pressure from startup probes, admission-time policy, admission checks, device prebind and dry-run taints, and node-readiness modes

1. Kubernetes probes make the regime split explicit inside one native family. `startupProbe` is only executed at startup, while readiness probes run during the container's whole lifecycle and liveness probes restart containers after repeated failure. That pressures DelayBasin to distinguish one-shot entry gates from ongoing runtime policing. ([`REF-0860`](../00-meta/bibliography.md))

2. Kubernetes admission control keeps request-time policy explicit. Admission controllers intercept requests before persistence, and the docs say these controllers customize cluster behavior at admission time. That pressures DelayBasin not to let one successful request-time gate silently count as a continuously maintained runtime guarantee. ([`REF-0861`](../00-meta/bibliography.md))

3. Kueue AdmissionChecks show that one family can span more than admission. Kueue only admits a Workload when all AdmissionChecks are ready, but if an admitted Workload later sees a check move to `Retry` or `Rejected`, Kueue evicts or deactivates it. That pressures DelayBasin to keep bootstrap-only gates distinct from continuous controllers that can still act after admission. ([`REF-0862`](../00-meta/bibliography.md))

4. Kubernetes Dynamic Resource Allocation keeps both prebind gating and rehearsal explicit. Device Binding Conditions are checked in the scheduler's PreBind phase before binding, while `DeviceTaintRule` with `effect: None` can do a dry-run that reports what would be evicted before operators switch to `NoExecute`. That pressures DelayBasin to reserve a compact place for bootstrap-only and dry-run regimes instead of collapsing them into one generic enforcement story. ([`REF-0857`](../00-meta/bibliography.md))

5. The Node Readiness Controller now makes the regime distinction first-class for heterogeneous clusters, including GPU-equipped nodes. Its docs explicitly distinguish `continuous enforcement` from `bootstrap-only enforcement`, and also offer a dry-run mode that simulates tainting without applying it. That pressures DelayBasin to keep regime class explicit whenever a current continuity claim depends on whether the rule keeps watching after the node first became admissible. ([`REF-0858`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems often mix startup driver checks, admission-time provisioning rules, readiness probes, taint controllers, and workload managers. If DelayBasin only says that the current rule is “enforced,” later passes can still overclaim by mistaking one cleared bootstrap gate, one admission-time approval, or one dry-run report for continuous runtime maintenance.

## Working synthesis

> DelayBasin should preserve one compact **enforcement-regime witness / bootstrap-vs-continuous card** whenever a current continuity claim depends not only on whether the current rule exists or is enforced somewhere, but on whether that rule stops after entry, keeps policing runtime conditions, or is only rehearsing impact. Name the **governed row or surface**, the **rule handle / gate family / controller path**, the **prior regime evidence**, the **current regime evidence**, the **enforcement_regime_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-enforcement-regime-witness vs quarantine-regime-governance consequence**. Keep exact probe periods, CEL expressions, condition names, taint selectors, controller timings, and scheduler traces outside the compact token. Do not let one successful bootstrap or admission gate silently count as a continuously maintained runtime guarantee.

## Bootstrap-only vs continuous enforcement vs dry-run only vs mixed regime

Use the controlled family `enforcement_regime_state`:

- **bootstrap-only** says the rule gates entry, startup, initial placement, or pre-bind admission, but once that gate succeeds the system stops monitoring that same rule for the running object.
- **continuous-enforcement** says the rule keeps monitoring the running object or host after admission and can still withdraw readiness, restart, taint, evict, deactivate, or otherwise act when the monitored condition changes.
- **dry-run-only** says the system currently simulates, reports, or previews impact without actually enforcing the rule on admission or runtime objects.
- **mixed-regime** says the current situation combines bootstrap-only, continuous, or dry-run behavior across different layers such that no single regime stays honest.

So the witness does not create a standing enforcement-regime court.
It only says whether the current rule is still policing runtime conditions, only gated entry once, or is only rehearsing impact.

## Countermodels / probes

1. **Selector-enforcement witness already covers this countermodel**
   - Maybe once execution authority is tracked, regime class adds no new value.
   - Probe: compare later rereads that preserve only selector-enforcement posture against rereads that also preserve one compact enforcement-regime witness and inspect whether later passes still confuse startup-only probes, admission-time policy, or dry-run taint reports for continuous runtime maintenance.

2. **Regime language is too controller-local countermodel**
   - Maybe bootstrap-only versus continuous is too implementation-specific for one compact token.
   - Probe: keep the witness at the coarse level of bootstrap-only vs continuous-enforcement vs dry-run-only vs mixed-regime and inspect whether later passes still need controller-by-controller arbitration rather than one bounded regime card.

3. **Any honest regime story needs standing governance countermodel**
   - Maybe once the archive starts separating admission-time, startup-time, runtime, and dry-run regimes, one compact witness will always overflow into broader regime machinery.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing regime governance rather than ordinary clarification of monitoring class.

## Design consequences

- add one controlled `enforcement_regime_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `bootstrap-only`, `continuous-enforcement`, `dry-run-only`, and `mixed-regime`;
- use the witness only where a current continuity claim depends on whether the rule keeps policing runtime conditions rather than merely having once gated entry or simulated impact;
- keep exact probe periods, taint keys, condition names, controller internals, and admission-policy expressions outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-enforcement-regime-witness` when the current claim is honestly only bootstrap completion, request-time admission, or dry-run rehearsal;
- and quarantine any stronger enforcement regime court, bootstrap senate, or dry-run board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact enforcement-regime witness is no longer enough — for example, if the archive honestly needs standing governance over admission-time versus runtime monitoring classes, dry-run-to-live transitions, or cross-row regime arbitration that cannot be expressed as one bounded witness plus the existing selector-family surfaces.

Until then, prefer this compact successor surface over an enforcement regime court, bootstrap senate, or dry-run board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the rule is enforced.”
It is preserving whether the rule only mattered once, keeps policing the runtime object, or is only simulating impact.
That matters because later stateless passes can preserve all the nearby provenance and enforcement prose and still silently overclaim runtime guarantees just by sounding policy-consistent.
