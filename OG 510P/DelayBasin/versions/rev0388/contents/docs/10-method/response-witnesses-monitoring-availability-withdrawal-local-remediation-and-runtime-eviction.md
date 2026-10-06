# Response witnesses, monitoring, availability withdrawal, local remediation, and runtime eviction

This is the compact successor surface for `OQ-0130`.

## Practice / observation

Once DelayBasin already distinguishes selector truth, selector enforcement, and enforcement regime, one further failure mode stays live: a rule can still be continuously monitored while the archive still cannot say what that monitoring actually does once the watched condition goes bad.

A row can truthfully say that a GPU health condition, readiness path, workload check, or node monitor is still live, yet that phrase can still hide whether the system only reports the bad state, withdraws availability, tries an in-place repair, or ejects the runtime object entirely.

The compact repair is one small response witness. It does not replace the selector, selector-provenance, selector-freshness, selector-enforcement, or enforcement-regime witnesses. It only says what class of action follows once a continuously watched condition fails.

## External pressure from passive node monitors, readiness withdrawal, liveness restarts, workload drain controls, device-taint eviction, and GPU health reporting

1. Kubernetes Node Problem Detector keeps watch-only monitoring explicit. Its docs describe it as a daemon for monitoring and reporting node health, collecting information and reporting Node Conditions or Events. That pressures DelayBasin to keep observation distinct from active runtime intervention. ([`REF-0863`](../00-meta/bibliography.md))

2. Kubernetes readiness probes make a softer response class explicit. When readiness fails, Kubernetes removes the Pod from matching Service endpoints while the probe continues through the container lifecycle. That pressures DelayBasin to distinguish availability withdrawal from both pure monitoring and stronger runtime disruption. ([`REF-0860`](../00-meta/bibliography.md))

3. Kubernetes liveness probes make local remediation explicit. When liveness fails repeatedly, the kubelet restarts the container. That pressures DelayBasin to distinguish in-place repair attempts from mere endpoint withdrawal or full eviction. ([`REF-0860`](../00-meta/bibliography.md))

4. Kueue makes stronger workload responses explicit. `ClusterQueue.stopPolicy: Hold` stops new admissions while already admitted workloads finish, but `HoldAndDrain` triggers eviction of admitted workloads. AdmissionChecks can likewise evict or deactivate an already admitted Workload when the check later moves to `Retry` or `Rejected`. That pressures DelayBasin to preserve stronger runtime-discontinuation responses instead of collapsing them into generic monitoring language. ([`REF-0864`](../00-meta/bibliography.md); [`REF-0862`](../00-meta/bibliography.md))

5. Kubernetes Dynamic Resource Allocation keeps eviction explicit at the device layer. Device taints with `NoExecute` cause eviction of already scheduled Pods by deleting affected Pods. That pressures DelayBasin not to let one monitored hardware condition borrow stronger response authority than the controller actually owns. ([`REF-0857`](../00-meta/bibliography.md))

6. NVIDIA DCGM keeps GPU health reporting and downstream action distinct. Its background health checks are passive monitoring that report warnings or errors; warnings need later examination, while critical errors usually indicate the need for job termination and GPU health analysis. That pressures DelayBasin to keep GPU monitoring, advisory escalation, and enforced termination from sounding like one undifferentiated response. ([`REF-0865`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems often combine passive health daemons, readiness withdrawal, liveness restarts, controller drains, and device- or workload-level eviction. If DelayBasin only says that a current monitor is “live” or “continuously enforced,” later passes can still overclaim by mistaking one watch-only signal, one endpoint withdrawal, or one restart loop for full runtime discontinuation authority.

## Working synthesis

> DelayBasin should preserve one compact **response witness / response-ladder card / remediation brake** whenever a current continuity claim depends not only on whether a condition is still monitored, but on what the system actually does when that condition fails. Name the **governed row or surface**, the **monitor / controller / response path**, the **prior response evidence**, the **current response evidence**, the **response_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-response-witness vs quarantine-response-governance consequence**. Keep exact endpoint names, restart policies, taint keys, event reasons, drain timers, job ids, and reset commands outside the compact token. Do not let continuous monitoring silently count as restart, eviction, or job termination authority without explicit response support.

## Monitor only vs availability withdrawal vs local remediation vs runtime eviction vs mixed response

Use the controlled family `response_state`:

- **monitor-only** says the current mechanism observes, reports, scores, or flags the bad condition, but does not itself withdraw availability, restart the governed object, or evict it.
- **availability-withdrawal** says the current mechanism keeps the governed object running but removes it from traffic, routing, admission, or comparable availability paths when the condition fails.
- **local-remediation** says the current mechanism actively tries to restore health in place by restarting or resetting the governed object without treating the higher-level runtime object as evicted.
- **runtime-eviction** says the current mechanism evicts, deactivates, drains, deletes, or otherwise forcibly discontinues the running object when the condition fails.
- **mixed-response** says the current situation combines watch-only, withdrawal, remediation, or eviction behavior across different layers such that no single response class stays honest.

So the witness does not create a standing response court.
It only says what class of action follows once a live monitored condition actually trips.

## Countermodels / probes

1. **Enforcement-regime witness already covers this countermodel**
   - Maybe once bootstrap-only versus continuous enforcement is tracked, nothing more is needed.
   - Probe: compare later rereads that preserve only enforcement-regime posture against rereads that also preserve one compact response witness and inspect whether later passes still confuse watch-only monitors, readiness withdrawal, liveness restarts, and runtime eviction.

2. **Response language is too controller-local countermodel**
   - Maybe response class is too implementation-specific for one compact token.
   - Probe: keep the witness at the coarse level of monitor-only vs availability-withdrawal vs local-remediation vs runtime-eviction vs mixed-response and inspect whether later passes still require controller-by-controller response arbitration rather than one bounded response card.

3. **Any honest response story needs standing governance countermodel**
   - Maybe once the archive starts separating report-only monitors, soft withdrawal, restart loops, and eviction, one compact witness will always overflow into broader response machinery.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing response governance rather than ordinary clarification of consequence class.

## Design consequences

- add one controlled `response_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `monitor-only`, `availability-withdrawal`, `local-remediation`, `runtime-eviction`, and `mixed-response`;
- use the witness only where a current continuity claim depends on what a live monitored condition actually triggers once it fails, not merely on whether the condition is still observed;
- keep exact endpoint names, restart loops, taint keys, workload ids, deactivation reasons, and GPU reset procedures outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-response-witness` when the current claim is honestly only watch-only reporting or advisory escalation;
- and quarantine any stronger response court, remediation senate, or eviction board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact response witness is no longer enough — for example, if the archive honestly needs standing governance over response escalation ladders, restart-versus-eviction arbitration, or cross-row action-policy review that cannot be expressed as one bounded witness plus the existing enforcement-regime and selector-family surfaces.

Until then, prefer this compact successor surface over a response court, remediation senate, or eviction board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the monitor is still live.”
It is also preserving whether a bad condition only becomes visible, narrows reachability, triggers an in-place repair, or ejects the runtime object entirely.
That matters because later stateless passes can preserve all the nearby monitoring and enforcement prose and still silently overclaim runtime consequence just by sounding health-policy consistent.
