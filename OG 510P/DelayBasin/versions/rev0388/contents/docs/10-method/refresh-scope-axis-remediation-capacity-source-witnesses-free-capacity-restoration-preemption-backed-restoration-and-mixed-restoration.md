# Refresh-scope-axis-remediation-capacity-source witnesses, free-capacity restoration, preemption-backed restoration, and mixed restoration

This is the compact successor surface for `OQ-0155`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, explicit about who restored them after drift, and honest about whether that repair stayed local or spent a drain or fence, one more ambiguity remains.

Some restored decoupling comes back through free-capacity restoration.
A controller, scheduler, or repair loop finds spare room that was already available when the violating workload is recreated or admitted again.
That spare room might be literal idle node or GPU capacity.
It might also be unused quota or cohort slack that can be borrowed without evicting anybody.
The restoration is real, and its capacity source stays comparatively clean because unrelated lower-priority work did not have to be displaced to make it happen.

Some restored decoupling comes back through preemption-backed restoration.
The repair succeeds only because a scheduler or queue controller evicts, suspends, requeues, or otherwise displaces lower-priority work to make room.
That may be the correct operational choice.
But it should not silently inherit the authority of free-capacity recovery, because the restored placement is now spending a priority bill paid elsewhere.

Some cases are honestly mixed.
A restoration might partly reuse idle capacity and partly rely on preemption or quota reclamation once the easy slack is exhausted.
Those cases should not be flattened into the clean free-capacity story.

DelayBasin does not need a standing priority tariff board for these cases.
It needs one bounded witness that says whether restored decoupling currently depends on free capacity, preemption-backed capacity, or an honest mix.

## External pressure from Kubernetes scheduling fallback and non-preempting Pods, Kueue cohort borrowing and preemption, Slurm backfill and preemption, and RayJob priority scheduling with Kueue

1. Kubernetes Scheduling Framework says `postFilter` plugins are invoked only when no feasible nodes were found, and a typical `postFilter` implementation is preemption that tries to make the Pod schedulable by preempting other Pods. That pressures DelayBasin to keep free-capacity fits distinct from fallback placement that succeeds only after displacement. ([`REF-0986`](../00-meta/bibliography.md))

2. Kubernetes Pod Priority and Preemption says Pods with `preemptionPolicy: Never` still sit ahead of lower-priority Pods in the queue but cannot preempt others and must wait until sufficient resources are free. That pressures DelayBasin to distinguish waiting-for-free-capacity recovery from recovery that actively evicts somebody else. ([`REF-0987`](../00-meta/bibliography.md))

3. Kueue ClusterQueue docs say ClusterQueues in the same cohort can borrow unused quota from each other. That pressures DelayBasin to treat some restored admission paths as capacity reuse or slack borrowing rather than as displacement by default. ([`REF-0988`](../00-meta/bibliography.md))

4. Kueue Preemption docs say preemption evicts admitted Workloads to accommodate another Workload, and the API explicitly distinguishes when borrowing may also preempt lower-priority workloads in a cohort. That pressures DelayBasin not to flatten borrowed slack and preemption-backed admission into one vague capacity story. ([`REF-0989`](../00-meta/bibliography.md))

5. Slurm's scheduling configuration docs say backfill starts lower-priority jobs when doing so does not delay higher-priority jobs, while Slurm preemption docs say pending jobs can begin by canceling, suspending, or requeueing lower-priority jobs as needed. That pressures DelayBasin to separate spare-hole reuse from displacement-backed recovery in cluster scheduling stories. ([`REF-0990`](../00-meta/bibliography.md), [`REF-0991`](../00-meta/bibliography.md))

6. Ray's Kueue integration docs show a higher-priority RayJob taking precedence over a lower-priority RayJob and Kueue preempting the lower-priority job to admit the higher-priority one. That pressures GPUstorming not to narrate restored GPU placement as cheap slack reuse when the queue actually paid for it by displacement. ([`REF-0992`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. Two GPU jobs can both end with the same anti-affinity, rack, quota, or queue picture repaired. One returns because a previously idle accelerator or borrowable quota slice was simply available. Another only returns because a lower-priority workload was suspended, evicted, or requeued. Collateral width and remediation provenance do not by themselves say who paid the capacity bill.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-capacity-source witness / priority-bill card / displacement brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, and honest about collateral width, but on whether the restored placement reused already-available capacity or succeeded only by displacing unrelated lower-priority work. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-collateral evidence**, the **current corroborating axes**, the **free-capacity basis if any**, the **preemption-backed basis if any**, the **`refresh_scope_axis_remediation_capacity_source_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-capacity-source-witness vs quarantine-displacement-debt consequence**. Keep raw queue traces, quota ledgers, eviction events, scheduler logs, and priority-class dumps outside the compact token. Do not let preemption-backed restoration silently inherit the cheap authority of free-capacity recovery.

## Free capacity restoration vs preemption-backed restoration vs mixed refresh scope axis remediation capacity source

Use the controlled family `refresh_scope_axis_remediation_capacity_source_state`:

- **free-capacity-restoration** says the documented restoration succeeds using idle capacity, spare quota, or borrowable unused quota without evicting, suspending, requeueing, or canceling unrelated lower-priority work.
- **preemption-backed-restoration** says the documented restoration succeeds only because unrelated lower-priority work is evicted, suspended, requeued, canceled, or otherwise displaced to free room.
- **mixed-refresh-scope-axis-remediation-capacity-source** says the current situation honestly combines free-capacity reuse and preemption-backed restoration such that no single capacity-source class stays honest.

So the witness does not create a priority tariff board.
It only says whether the present restoration reused free capacity, spent displacement, or is honestly mixed.

## Countermodels / probes

1. **Collateral width already captures enough countermodel**
   - Maybe once DelayBasin knows whether restoration stayed local or spent a drain, the capacity source adds only operational color.
   - Probe: compare rereads that preserve only collateral width against rereads that also preserve one compact free-vs-preempt token and inspect whether preemption-backed local repairs still get narrated as cheap slack reuse.

2. **Borrowed slack is still a different lane countermodel**
   - Maybe borrowed but non-preemptive quota deserves its own public class rather than living inside free-capacity restoration.
   - Probe: keep borrowed-unused-quota evidence inside free-capacity restoration unless later revisions repeatedly need to separate idle local slack from explicit non-displacing quota borrowing.

3. **Displacement aftercare is the real next question countermodel**
   - Maybe capacity source is still not enough because the archive next needs to say whether displaced lower-priority work is suspended and resumed, requeued, or simply canceled and abandoned.
   - Probe: keep that next question explicit as frontier work unless later revisions show that free-vs-preempt truth itself is still insufficient.

## Design consequences

- DelayBasin can now keep repaired decoupling from sounding as if it reused free slack when it only returned by displacing unrelated work.
- The archive gets one explicit place to record when a repaired GPU or scheduler topology recovered on spare capacity versus by priority-backed queue action.
- GPUstorming can now distinguish "there was room" from "we made room by evicting somebody else" without opening a full displacement-debt court.
- Stronger displacement-debt, priority-tariff, or resumability-escrow stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit capacity exchange rates, preemption tariffs, debt restitution rules, or displacement-accounting machinery that one bounded refresh-scope-axis-remediation-capacity-source witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every repaired or rebalanced decoupling surface as if restored capacity came from the same place. Preserve the smallest token that says whether the present restoration is `free-capacity-restoration`, `preemption-backed-restoration`, or honestly `mixed-refresh-scope-axis-remediation-capacity-source`, and quarantine stronger displacement-debt ambitions until repeated overflow makes them unavoidable.
