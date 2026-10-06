# Repair-scope witnesses, in-place repair, substrate reset, and workload replacement

This is the compact successor surface for `OQ-0131`.

## Practice / observation

Once DelayBasin already distinguishes selector truth, enforcement regime, and response class, one further failure mode stays live: a current row can honestly say that some controller restarts, resets, or recovers work, yet still fail to say whether that repair keeps the same running object, resets the device or host substrate underneath it, or replaces the workload altogether.

A row can truthfully say that a GPU job recovered, a Pod restarted, a node came back healthy, or a job retried, yet that phrase can still hide whether the same runtime object stayed in place, the surrounding substrate had to be reset or rebooted, or a brand new workload instance had to be scheduled.

The compact repair is one small repair-scope witness. It does not replace the selector, selector-provenance, selector-freshness, selector-enforcement, enforcement-regime, or response witnesses. It only says how far the system had to reach in order to recover once some active response path fired.

## External pressure from container restarts, in-place Pod restarts, GPU resets, node reboots, Job retries, and shutdown recovery

1. Kubernetes liveness probes keep the narrowest repair scope explicit. Their docs say liveness probes determine when to restart a container, and repeated liveness failures cause the kubelet to restart that container. That pressures DelayBasin to keep in-place repair distinct from broader reset or replacement claims. ([`REF-0860`](../00-meta/bibliography.md))

2. Kubernetes v1.35 makes the same boundary even sharper. The new Restart All Containers feature is described as a full, in-place restart of the Pod and explicitly contrasts that with deleting and recreating the entire Pod. That pressures DelayBasin to preserve in-place repair as a separate scope rather than collapsing it into workload replacement. ([`REF-0866`](../00-meta/bibliography.md))

3. NVIDIA DCGM keeps device-substrate repair explicit. Its config API docs say target configuration is automatically enforced after a GPU reset or reinitialization is completed. That pressures DelayBasin to distinguish device-level reset from ordinary in-process or in-container repair. ([`REF-0867`](../00-meta/bibliography.md))

4. NVIDIA's `nvidia-smi` docs keep reset versus reboot explicit. They describe recovery actions where some GPU faults require `nvidia-smi -r` reset while others require rebooting the operating system because the OS may be inconsistent and the application cannot restart without node reboot. That pressures DelayBasin to keep substrate reset or reboot separate from both simple in-place restart and workload replacement. ([`REF-0868`](../00-meta/bibliography.md))

5. Kubernetes Jobs keep workload replacement explicit. The docs say a Job starts a new Pod if the first Pod fails or is deleted, including due to node hardware failure or node reboot. That pressures DelayBasin to keep replacement of the workload object distinct from recovery that stayed on the same running object or merely reset the substrate. ([`REF-0869`](../00-meta/bibliography.md))

6. Kubernetes non-graceful node shutdown handling keeps cross-node recovery explicit. The docs say Pods on an out-of-service or shutdown node can be forcefully deleted so they recover quickly on a different node. That pressures DelayBasin not to let node- or storage-level failover sound like the same repair scope as a local restart. ([`REF-0870`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems often combine watchdog restarts, Pod restarts, full in-place Pod restarts, device resets, host reboots, taint-and-drain workflows, and controller-created replacement Pods. If DelayBasin only says that a system “recovered” or “restarted,” later passes can still overclaim by mistaking one container restart, one GPU reset, one node reboot, and one new workload instance for the same kind of continuity.

## Working synthesis

> DelayBasin should preserve one compact **repair-scope witness / repair-boundary card / replacement brake** whenever a current continuity claim depends not only on whether some active response exists, but on how far that response had to reach to recover work. Name the **governed row or surface**, the **repair / controller / recovery path**, the **prior repair-scope evidence**, the **current repair-scope evidence**, the **repair_scope_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-repair-scope-witness vs quarantine-repair-governance consequence**. Keep exact container ids, Pod names, GPU UUIDs, node names, reset commands, reboot procedures, checkpoint locations, and job submission handles outside the compact token. Do not let any recovery-sounding act silently count as the same repair scope without explicit support.

## In-place repair vs substrate reset vs workload replacement vs mixed repair scope

Use the controlled family `repair_scope_state`:

- **in-place-repair** says the current mechanism repairs or restarts the same running object in place without requiring a broader device, driver, node, or workload replacement boundary.
- **substrate-reset** says the current mechanism recovers by resetting, reinitializing, reloading, or rebooting the device, driver, host, or comparable substrate underneath the workload rather than only restarting the same running object.
- **workload-replacement** says the current mechanism recovers by deleting, recreating, resubmitting, or rescheduling a new workload object rather than continuing the original runtime object.
- **mixed-repair-scope** says the current situation honestly combines in-place repair, substrate reset, or workload replacement across different layers such that no single repair scope stays honest.

So the witness does not create a standing repair court.
It only says how far recovery had to reach once some response path actually fired.

## Countermodels / probes

1. **Response witness already covers this countermodel**
   - Maybe once DelayBasin tracks response class, nothing more is needed.
   - Probe: compare later rereads that preserve only response_state against rereads that also preserve one compact repair-scope witness and inspect whether later passes still confuse in-place restarts, GPU resets, node reboots, and fresh workload creation.

2. **Repair scope is too implementation-local countermodel**
   - Maybe repair scope is too controller-specific for one compact token.
   - Probe: keep the witness at the coarse level of in-place-repair vs substrate-reset vs workload-replacement vs mixed-repair-scope and inspect whether later passes still need controller-by-controller recovery arbitration rather than one bounded repair-scope card.

3. **Any honest repair story needs standing governance countermodel**
   - Maybe once the archive starts separating container restart, device reset, host reboot, and workload replacement, one compact witness will always overflow into broader repair machinery.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing repair governance rather than ordinary clarification of recovery scope.

## Design consequences

- add one controlled `repair_scope_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `in-place-repair`, `substrate-reset`, `workload-replacement`, and `mixed-repair-scope`;
- use the witness only where a current continuity claim depends on how far a recovery action had to reach, not merely on whether some response path existed;
- keep exact Pod names, reset commands, reboot workflows, node ids, GPU UUIDs, checkpoint paths, and job handles outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-repair-scope-witness` when the current claim honestly only supports in-place repair, substrate reset, or workload replacement alone;
- and quarantine any stronger repair court, substrate senate, or replacement board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact repair-scope witness is no longer enough — for example, if the archive honestly needs standing governance over restart-versus-reset arbitration, reboot-versus-replacement policy, or cross-row recovery-boundary review that cannot be expressed as one bounded witness plus the existing response, regime, and selector-family surfaces.

Until then, prefer this compact successor surface over a repair court, substrate senate, or replacement board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the system recovered.”
It is also preserving whether recovery stayed on the same object, had to reset the substrate underneath it, or had to replace the workload entirely.
That matters because later stateless passes can preserve all the nearby monitoring, enforcement, and remediation prose and still silently overclaim continuity just by sounding recovery-policy consistent.
