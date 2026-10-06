# Refresh-scope-axis-remediation-displacement-aftercare witnesses, resumable displacement, terminal displacement, and mixed aftercare

This is the compact successor surface for `OQ-0156`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, and honest about whether the restored placement reused free capacity or only came back by displacing unrelated lower-priority work, one more ambiguity remains.

Some displacement-backed repairs are still comparatively reversible.
The lower-priority work that paid the bill is suspended, paused, or requeued with a live path back into execution.
Progress may still be slowed or partially lost.
But the archive can still honestly say that the aftercare posture was resumable rather than sacrificial.

Other displacement-backed repairs are terminal.
The displaced work is canceled, deactivated after retry limits, dropped, or otherwise abandoned.
Those cases should not silently inherit the same legitimacy as a temporary suspension or queue detour.
The repaired placement now rests on a stronger sacrifice than mere reversible borrowing.

Some cases are honestly mixed.
A scheduler may suspend one victim, requeue another, and cancel a third.
A workload may be requeued several times and only later deactivated.
Those cases should not be flattened into a clean resumable story or a clean sacrifice story.

DelayBasin does not need a standing restitution court here.
It needs one bounded witness that says whether displacement aftercare is still resumable, terminal, or honestly mixed.

## External pressure from Slurm suspend, requeue, and cancel modes, Kubernetes Jobs suspend/resume and disruption handling, Kueue requeue and deactivation limits, and NVIDIA Run:ai automatic resume with checkpointing

1. Slurm's preemption docs say `REQUEUE` preempts jobs by requeuing them if possible or canceling them, while `SUSPEND` suspends jobs and later the Gang scheduler resumes them; Slurm's configuration docs separately say `CANCEL` cancels the preempted job. That pressures DelayBasin to distinguish resumable displacement from terminal sacrifice even when both free room for a higher-priority job. ([`REF-0991`](../00-meta/bibliography.md), [`REF-0993`](../00-meta/bibliography.md))

2. Kubernetes Job docs say suspending a Job deletes its active Pods until the Job is resumed again, and the controller will start a new Pod if a Pod fails or is deleted. That pressures DelayBasin to treat some disruption paths as resumable controller-managed continuation rather than immediate abandonment. ([`REF-0994`](../00-meta/bibliography.md))

3. Kubernetes Pod failure policy docs show that a Job can be configured so Pod disruptions do not count toward failure and the Job resumes and succeeds, while without that policy and with `backoffLimit: 0` the same disruption would terminate the entire Job. That pressures DelayBasin not to narrate all displacement or eviction aftermath as the same aftercare class. ([`REF-0995`](../00-meta/bibliography.md))

4. Kueue's configuration API says timeouts can evict and requeue a Workload in the same ClusterQueue, and a recovery timeout can suspend it again and requeue it after backoff delay. Kueue's wait-for-pods-ready task docs also say repeated requeues continue until `backoffLimitCount`, after which the Workload is deactivated. That pressures DelayBasin to distinguish live requeue paths from aftercare that eventually becomes terminal. ([`REF-0996`](../00-meta/bibliography.md), [`REF-0997`](../00-meta/bibliography.md))

5. NVIDIA Run:ai docs say preemptible workloads may be paused while resources are reassigned to higher-priority workloads and are automatically resumed when resources become available, with checkpointing recommended to preserve progress. That pressures GPUstorming not to flatten automatic resume and checkpoint-backed return into outright sacrifice, while still keeping stronger restart accounting out of canon for now. ([`REF-0998`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. Two repaired GPU placements can both be preemption-backed. In one case, lower-priority work is merely suspended or requeued and remains on a believable path back. In another, the work is canceled, deactivated, or quietly sacrificed. Capacity-source truth alone does not say what kind of aftercare bill was actually imposed.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-displacement-aftercare witness / reversibility card / sacrifice brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, and honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, but on what happened to the displaced work afterward. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-capacity-source evidence**, the **current corroborating axes**, the **resumable-aftercare basis if any**, the **terminal-aftercare basis if any**, the **`refresh_scope_axis_remediation_displacement_aftercare_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-aftercare-witness vs quarantine-resume-credit consequence**. Keep raw eviction events, retry counters, checkpoint traces, suspend/resume logs, and controller histories outside the compact token. Do not let outright sacrifice silently inherit the authority of reversible priority borrowing.

## Resumable displacement aftercare vs terminal displacement aftercare vs mixed refresh scope axis remediation displacement aftercare

Use the controlled family `refresh_scope_axis_remediation_displacement_aftercare_state`:

- **resumable-displacement-aftercare** says the displaced lower-priority work was suspended, paused, requeued, retried, or otherwise kept on a live public path back into execution rather than deliberately abandoned.
- **terminal-displacement-aftercare** says the displaced lower-priority work was canceled, deactivated, abandoned, or otherwise left without a live public resumption path.
- **mixed-refresh-scope-axis-remediation-displacement-aftercare** says the current situation honestly combines resumable and terminal aftercare, or the public evidence cannot keep one clean class honest.

So the witness does not create a full restitution ledger.
It only preserves the smallest load-bearing truth about whether preemption-backed repair borrowed work temporarily or sacrificed it outright.

## Countermodels / probes

1. **Requeue is not always cheap forever**
   - A workload may be requeued several times and only later deactivated or abandoned.
   - Probe: if the live public story needs both phases, keep the mixed state rather than flattering the case as purely resumable.

2. **Resumable is not the same as lossless**
   - Slurm suspend/resume, Run:ai checkpoint-backed return, and controller-driven pod recreation all preserve different amounts of progress.
   - Probe: keep the current canon question narrow. This witness only classifies whether aftercare stayed live or went terminal. Finer distinctions about in-memory resume, checkpoint replay, and cold restart belong to the next frontier unless repeated overflow says otherwise.

3. **Free-capacity restoration should not import aftercare debt**
   - If the restoration did not actually displace unrelated work, aftercare language should not be forced in by atmosphere.
   - Probe: require prior refresh-scope-axis-remediation-capacity-source evidence before applying this witness.

## Design consequences

- DelayBasin can now keep displacement-backed repair from sounding equally reversible when some repairs merely pause lower-priority work and others permanently discard it.
- The archive gets one explicit place to record when a repaired GPU placement borrowed time from lower-priority work versus consumed that work entirely.
- GPUstorming can now distinguish reversible queue borrowing from sacrificial preemption without inflating a broader restitution board.
- Stronger resume-credit, checkpoint-escrow, or restart-tax stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit public accounting for in-memory resume versus checkpoint-backed replay versus cold restart, compensation or restitution rules for sacrificed work, or branch-wide restart taxation that one bounded refresh-scope-axis-remediation-displacement-aftercare witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat all displacement-backed repair as if the lower-priority work paid the same kind of bill. Preserve the smallest token that says whether the present aftercare is `resumable-displacement-aftercare`, `terminal-displacement-aftercare`, or honestly `mixed-refresh-scope-axis-remediation-displacement-aftercare`, and quarantine stronger resume-credit ambitions until repeated overflow makes them unavoidable.
