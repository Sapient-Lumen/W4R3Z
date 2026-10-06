# Selector-enforcement witnesses, execution authority, grandfathered placement, and eviction gates

This is the compact successor surface for `OQ-0128`.

## Practice / observation

Once DelayBasin already distinguishes selector coverage, selector provenance, and selector freshness, one further failure mode stays live: a selector source can still be real, current, and well-described while not actually governing already-bound runtime objects anymore.

A row can truthfully say that the same GPU flavor, node label, taint family, or selector path is still current, yet that phrase can still hide whether current truth is enforced on already-running work, only on future placements, or not at all beyond remembered scheduler history.

The compact repair is one small selector-enforcement witness. It does not replace the selector, selector-provenance, or selector-freshness witnesses. It only says whether current selector truth is enforced on already-bound objects now.

## External pressure from GPU node labels, ignored-during-execution affinity, taint effects, unschedulable nodes, Kueue resource flavors, workload evictions, and device-taint controllers

1. Kubernetes GPU scheduling keeps the GPU context explicit: clusters expose GPU resources via device plugins, and operators commonly use node labels and node selectors to steer pods onto the right GPU type. That pressures DelayBasin not to treat GPU selector language as decorative once hardware choice is load-bearing. ([`REF-0859`](../00-meta/bibliography.md))

2. Kubernetes node affinity makes the enforcement gap explicit. `requiredDuringSchedulingIgnoredDuringExecution` blocks initial placement unless labels match, but if node labels change later the Pod continues to run. That pressures DelayBasin to distinguish schedule-time admissibility from execution-time enforcement. ([`REF-0852`](../00-meta/bibliography.md))

3. Kubernetes taints and tolerations sharpen the split. `NoSchedule` keeps unmatched Pods from landing, yet manual `.spec.nodeName` binding can still bypass the scheduler; `NoExecute`, by contrast, ejects already-bound Pods that do not tolerate the taint. That pressures DelayBasin to keep admission-only control distinct from runtime eviction control. ([`REF-0853`](../00-meta/bibliography.md))

4. Kubernetes node administration keeps the same distinction in plain cluster operations: marking a node unschedulable prevents new Pods from landing there but does not affect existing Pods already on the node. That pressures DelayBasin to separate future gating from present runtime authority. ([`REF-0854`](../00-meta/bibliography.md))

5. Kueue keeps GPU-flavor selection explicit at admission time. A `ResourceFlavor` can inject node labels and tolerations so admitted Pods schedule onto the chosen hardware slice, while workload control can still evict a running workload if `.spec.active` is turned off. That pressures DelayBasin to keep selector admission and execution control as separate enforcement postures. ([`REF-0855`](../00-meta/bibliography.md); [`REF-0856`](../00-meta/bibliography.md))

6. Kubernetes Dynamic Resource Allocation pushes the same distinction into device-level control. Device taints with `NoExecute` evict Pods already using a tainted device, while `None` can communicate degraded device health without scheduling or eviction effect. That pressures DelayBasin to reserve a compact place for explicit execution enforcement rather than borrowing it from selector freshness alone. ([`REF-0857`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU clusters often use selectors, taints, flavors, and admission-time controllers together. But those surfaces do not all continue policing already-running work in the same way. DelayBasin therefore needs one compact witness for whether the selector is merely how placement happened or whether it is still what runtime authority actually enforces.

## Working synthesis

> DelayBasin should preserve one compact **selector-enforcement witness / runtime-authority card** whenever a current continuity claim depends not only on the selector still being current, but on that selector truth still being enforced on already-bound objects now. Name the **governed row or surface**, the **selector handle / admission path / taint or affinity family**, the **prior enforcement posture**, the **current enforcement posture**, the **selector_enforcement_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-enforcement-witness vs quarantine-selector-enforcement-governance consequence**. Keep exact taint keys, kube-scheduler profile details, pod ids, device claim traces, and controller timing outside the compact token. Do not let correct current selector truth silently count as execution-time authority when the system is only enforcing future placements or preserving grandfathered runtime residue.

## Execution enforced vs admission only vs grandfathered residue vs mixed enforcement

Use the controlled family `selector_enforcement_state`:

- **execution-enforced** says current selector truth is actively enforced on already-bound objects now; mismatching runtime objects are evicted, halted, or otherwise prevented from continuing under the current rule.
- **admission-only** says current selector truth governs future placement or admission, but already-bound objects can continue running without runtime re-check.
- **grandfathered-residue** says the current object is surviving only because an earlier placement, binding, or tolerated state remains in force even though present selector truth would not freshly license it now.
- **mixed-enforcement** says the current situation combines admission-only and execution-enforced behavior across different selectors, taints, devices, or controller layers such that no single posture stays honest.

So the witness does not create a standing selector enforcement court.
It only says when “current selector” also means “current runtime authority” and when the archive should fail closed instead.

## Countermodels / probes

1. **Fresh selector truth is already enough countermodel**
   - Maybe once selector freshness is established, enforcement no longer needs a separate witness.
   - Probe: compare later rereads that preserve only selector freshness against rereads that also preserve a compact selector-enforcement witness and inspect whether later passes still confuse `IgnoredDuringExecution`, `NoSchedule`, or unschedulable-node residue for runtime enforcement.

2. **Eviction semantics are too controller-local countermodel**
   - Maybe enforcement is too implementation-specific for one compact token.
   - Probe: keep the witness at the coarse level of execution-enforced vs admission-only vs grandfathered-residue and inspect whether later passes still need exact controller-by-controller adjudication rather than one bounded enforcement card.

3. **Every enforcement question needs standing governance countermodel**
   - Maybe selector enforcement is too cross-cutting for one bounded witness and always needs a broader board.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still overflow into genuine standing selector-enforcement governance rather than ordinary clarification of runtime authority.

## Design consequences

- add one controlled `selector_enforcement_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `execution-enforced`, `admission-only`, `grandfathered-residue`, and `mixed-enforcement`;
- use the witness only where a current continuity claim depends on runtime enforcement of already-bound objects rather than just selector freshness or placement history;
- keep exact node names, taint keys, device claim ids, scheduler profiles, and eviction traces outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-selector-enforcement-witness` when the current claim is honestly only admission-time continuity or grandfathered residue;
- and quarantine any stronger selector enforcement court, eviction senate, or grandfather board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact selector-enforcement witness is no longer enough — for example, if the archive honestly needs standing governance over runtime eviction authority, admission-versus-execution arbitration, grandfathered-placement review, or cross-row enforcement disputes that cannot be expressed as one bounded witness plus the existing selector, selector-provenance, and selector-freshness surfaces.

Until then, prefer this compact successor surface over a selector enforcement court, eviction senate, or grandfather board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the selector is still current.”
It is also preserving whether the selector still governs already-running work, or whether the runtime object is only borrowing authority from how it got placed earlier.
That matters because later stateless passes can preserve all the nearby freshness and provenance prose and still silently overclaim present control just by sounding scheduler-consistent.
