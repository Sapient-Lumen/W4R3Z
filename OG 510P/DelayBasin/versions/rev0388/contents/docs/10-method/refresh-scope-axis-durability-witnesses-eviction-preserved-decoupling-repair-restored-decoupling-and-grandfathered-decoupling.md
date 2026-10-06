# Refresh-scope-axis-durability witnesses, eviction-preserved decoupling, repair-restored decoupling, and grandfathered decoupling

This is the compact successor surface for `OQ-0152`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, and hard-enforced rather than merely preferred, one more ambiguity remains.

Some decoupling keeps policing itself.
If the separation condition stops holding while the workload is already running, the platform evicts or deletes the affected placement.
That is stronger than merely refusing the next scheduling attempt.
It means the present corroboration keeps defending itself during execution.

Some decoupling does not keep itself true, but it can be restored by a repair loop.
The scheduler or controller re-applies the separation on fresh placements, or an explicit rebalance loop can move the workload back into the desired spread.
That still matters.
But it should not inherit the force of a decoupling rule that actively ejects drifted runtime residue.

Some decoupling is grandfathered.
The initial placement had to satisfy the rule, yet already-running objects can remain bound after labels drift or the world around them changes.
That is not no durability at all.
But it is weaker than either self-preserving eviction or explicit repair-restoration.

DelayBasin does not need a durability lease ledger for these cases.
It needs one bounded witness that says whether the present decoupling is eviction-preserved, repair-restored, grandfathered, or honestly mixed.

## External pressure from Kubernetes NoExecute eviction, device taint eviction controllers, topology spread drift and descheduler repair, scheduling-vs-eviction separation, and IgnoredDuringExecution affinity

1. Kubernetes taints and tolerations say `NoExecute` affects pods already running on a node: non-tolerating pods are evicted immediately, tolerant pods can remain only for a bounded `tolerationSeconds`, and `NoSchedule` plus `PreferNoSchedule` are weaker because they do not evict current pods. That pressures DelayBasin to separate runtime-preserved decoupling from merely prospective or soft gating. ([`REF-0971`](../00-meta/bibliography.md))

2. Kubernetes Dynamic Resource Allocation says device taints with `NoExecute` imply `NoSchedule` and additionally evict already scheduled pods through the device taint eviction controller. That pressures DelayBasin to treat device-level and GPU-facing decoupling durability as a real continuation question rather than as mere node-label rhetoric. ([`REF-0972`](../00-meta/bibliography.md))

3. Pod topology spread constraints say they instruct the scheduler how to place each incoming pod, but there is no guarantee the constraints remain satisfied when pods are removed; the docs explicitly point to descheduler-based rebalancing. That pressures DelayBasin to distinguish self-preserving decoupling from decoupling that only comes back through a later repair loop. ([`REF-0968`](../00-meta/bibliography.md))

4. Kubernetes separates scheduling from eviction as distinct control-plane acts. That pressures DelayBasin not to let a hard scheduling gate silently count as a runtime durability guarantee when eviction or repair policy is the actual mechanism that would keep the decoupling true later. ([`REF-0973`](../00-meta/bibliography.md))

5. Kubernetes' `requiredDuringSchedulingIgnoredDuringExecution` docs say a pod will still run if node labels change and the affinity rules are no longer met. That pressures DelayBasin to distinguish grandfathered decoupling from runtime-preserved decoupling even when the initial gate was hard. ([`REF-0974`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. An open search can surface zones, racks, MIG partitions, topology spread, and taints that look beautifully separated at admission. But some of those separations keep policing themselves, some only come back after rebalance or replay, and some simply let drifted placements continue running. Durability is the missing compact truth.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-durability witness / drift-survival brake / repair-loop card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, and hard-enforced, but on whether that decoupling stays preserved once execution begins or after the world drifts. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-enforcement evidence**, the **current corroborating axes**, the **eviction-preserved basis if any**, the **repair-restored basis if any**, the **grandfathered basis if any**, the **`refresh_scope_axis_durability_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-durability-witness vs quarantine-durability-lease-ledger consequence**. Keep raw event timelines, descheduler traces, taint dumps, controller logs, and cluster-specific remediation scripts outside the compact token. Do not let an admission-time hard gate silently inherit the authority of self-preserving runtime decoupling.

## Eviction-preserved decoupling vs repair-restored decoupling vs grandfathered decoupling vs mixed refresh scope axis durability

Use the controlled family `refresh_scope_axis_durability_state`:

- **eviction-preserved-decoupling** says the documented platform actively evicts, deletes, or otherwise removes already-running placements when the decoupling condition is no longer satisfied.
- **repair-restored-decoupling** says the current decoupling can drift in runtime or after ordinary changes, but documented repair or rebalance mechanisms can restore it on later passes or new placements.
- **grandfathered-decoupling** says already-running placements can remain bound even after the decoupling condition stops holding, so the present separation is tolerated residue rather than actively preserved runtime truth.
- **mixed-refresh-scope-axis-durability** says the current situation honestly combines eviction-preserved, repair-restored, and grandfathered elements such that no single class stays honest.

So the witness does not create a durability lease ledger.
It only says whether the present decoupling keeps itself true, needs repair to come back, tolerates grandfathered residue, or is honestly mixed.

## Countermodels / probes

1. **Enforcement already does enough countermodel**
   - Maybe once the archive knows whether decoupling is hard-enforced, a separate durability witness only restates obvious scheduler prose.
   - Probe: compare later rereads that preserve only refresh-scope-axis-enforcement truth against rereads that also preserve one compact durability token and inspect whether schedule-time hard gates still get narrated as lasting runtime protection.

2. **Repair-restored and grandfathered collapse countermodel**
   - Maybe any non-evicting posture is just "not durable" and does not deserve two public states.
   - Probe: look for later cases where an explicit rebalance or recreate path changes downstream trust differently from cases where drifted placements simply remain bound with no public repair route.

3. **Remediation authority is the real issue countermodel**
   - Maybe the archive's real next need is not durability class but whether restored decoupling comes from native controllers, sidecar repair loops, descheduler sweeps, or operator replay.
   - Probe: keep that next question explicit as frontier work unless later revisions show that eviction-vs-repair-vs-grandfathered truth itself is still insufficient.

## Design consequences

- DelayBasin can now separate hard gates that keep policing runtime from hard gates that merely got the initial placement right.
- The archive gets one explicit place to say when a decoupled-looking topology only stays healthy because a later repair loop may rebalance it.
- GPUstorming can import taints, spread constraints, and repair controllers without letting every hard admission gate inherit the authority of runtime durability.
- Stronger durability-lease, repair-debt, or rebalancing-escrow stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need lease clocks, repair-debt accounting, remediation-authority matrices, or quantitative durability discounts that one bounded refresh-scope-axis-durability witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every hard-enforced decoupling surface as if it stayed true through runtime drift. Preserve the smallest token that says whether the present decoupling is `eviction-preserved-decoupling`, `repair-restored-decoupling`, `grandfathered-decoupling`, or honestly `mixed-refresh-scope-axis-durability`, and quarantine stronger durability-ledger ambitions until repeated overflow makes them unavoidable.
