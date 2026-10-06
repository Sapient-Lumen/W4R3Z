# Refresh-scope-axis-remediation-displacement-replay-equivalence witnesses, functionally exact restore and performance-shadow restore

This is the compact successor surface for `OQ-0159`.

## Practice / observation

Once DelayBasin can already say that displaced lower-priority work returned through exact saved-state restore rather than bounded-loss replay or source-only restart, one more ambiguity remains.

Some restores are exact enough for correctness while still failing to preserve the practical runtime conditions that made the original run behave as a warm continuation.
The saved logical state may come back, yet cache warmth, host/device parity, locality, or uncontended execution may not.
That means two returns can both look exact at the replay-fidelity layer while differing materially in practical continuity.

DelayBasin does not need a shadow-solvency court here.
It needs one bounded witness that says whether the public basis supports a functionally exact restore, a performance-shadow restore, or an honest mix.

## External pressure from Kubernetes exact-point restore, Docker checkpoint resume, CRIU restore-preservation and post-restore change notes, Slurm resumed-job degradation, and NVIDIA CUPTI functional-only restore limits

1. Kubernetes' current Kubelet Checkpoint API docs say checkpointing creates a stateful copy of a running container and that a restored container continues to run at exactly the same point it was checkpointed. Docker's checkpoint and restore docs likewise say a process resumes from the point it was suspended. Together they pressure DelayBasin to keep a lane for restores that are publicly exact enough to count as functionally exact rather than merely replay-adjacent. ([`REF-1006`](../00-meta/bibliography.md), [`REF-1011`](../00-meta/bibliography.md))

2. CRIU's ZDTM test-suite docs say restore tests recreate concrete process state and verify that files, memory mappings, and pipes stay preserved across checkpoint and restore. That pressures DelayBasin to keep functionally exact restore explicit when the basis really is same-state preservation. ([`REF-1007`](../00-meta/bibliography.md))

3. But CRIU's own "What can change after C/R" notes say some restored-visible properties can still differ after restore, including namespace identifiers, process start time, and some kernel-facing statistics. That pressures DelayBasin not to let same-state restore automatically inherit full environment-equivalence authority. ([`REF-1012`](../00-meta/bibliography.md))

4. Slurm's current preemption docs say suspended jobs remain in memory, yet also warn that resuming a suspended job can allocate the same CPUs to multiple jobs and lead either to gang scheduling or severe performance degradation. That pressures GPUstorming to keep a performance-shadow lane for returns that remain correct but no longer carry the same runtime conditions. ([`REF-1013`](../00-meta/bibliography.md))

5. NVIDIA's current CUPTI Checkpoint API docs say restore recreates only functionally visible device state for re-execution, not performance-critical state such as caches, and does not restore host state. That is strong pressure for a performance-shadow lane while also warning DelayBasin not to overpromote a bigger shadow-source market yet. ([`REF-1010`](../00-meta/bibliography.md))

GPUstorming makes the split vivid. A GPU workload may restore the same tensor values and resume the same logical step, yet come back on a colder device, under different host pressure, or without the cache warmth that previously made the step cheap. Replay fidelity already told us whether the checkpoint was exact, lossy, or source-only. Replay equivalence now asks whether the exact-looking restore remained merely functionally exact or also avoided a meaningful practical shadow.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-displacement-replay-equivalence witness / shadow card / warmth brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, honest about whether that displaced work retained a live return path, honest about whether the return was in-memory, checkpoint-backed, or cold, and honest about whether replay restored exact saved state, bounded-loss checkpoints, or only source, but on whether an exact-looking restore stayed practically equivalent or came back under a performance shadow. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence**, the **current corroborating axes**, the **functionally-exact-restore basis if any**, the **performance-shadow-restore basis if any**, the **`refresh_scope_axis_remediation_displacement_replay_equivalence_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-equivalence-witness vs quarantine-shadow-source consequence**. Keep raw cache traces, host/device micro-accounting, locality debt, and detailed warm-start markets outside the compact token. Do not let every exact-looking restore silently inherit the authority of performance-equivalent continuity.

## Functionally exact restore vs performance-shadow restore vs mixed refresh scope axis remediation displacement replay equivalence

Use the controlled family `refresh_scope_axis_remediation_displacement_replay_equivalence_state`:

- **functionally-exact-restore** says the public basis supports a return that preserves the saved logical execution state or correct re-execution point strongly enough for current continuity claims, with no current need to narrate a material practical shadow.
- **performance-shadow-restore** says the public basis supports correctness-preserving or exact-looking restore, but also shows that meaningful practical runtime conditions such as cache warmth, host-side parity, locality, or uncontended scheduling were not preserved.
- **mixed-refresh-scope-axis-remediation-displacement-replay-equivalence** says the current situation honestly combines both lanes across the relevant surfaces, or the public evidence cannot keep one clean lane honest.

So the witness does not create a shadow-source court.
It only preserves the smallest load-bearing truth about whether the present exact-looking restore should be read as functionally exact or as performance-shadowed.

## Countermodels / probes

1. **Exact checkpoint point does not automatically imply equal warmth**
   - A system may document resume at the same execution point while saying nothing about caches, locality, or contention.
   - Probe: if the current practical continuity claim needs preserved runtime warmth rather than only preserved logical state, do not let exact-point language alone certify equivalence.

2. **Correctness preservation is stronger than simple relaunch but weaker than full practical parity**
   - CRIU-style preserved state may still return with changed kernel-facing or environment-facing properties.
   - Probe: if those changed properties plausibly matter to the claim at hand, narrow from `functionally-exact-restore` to `performance-shadow-restore` unless the public basis defeats that concern.

3. **Scheduler interference can create performance shadow without logical loss**
   - Suspended jobs may remain in memory and still return under oversubscribed CPU or gang-scheduled conditions.
   - Probe: if resumed placement publicly inherits severe degradation or contested runtime, do not narrate full practical continuity merely because no computation state was lost.

4. **Shadow source analysis is not yet canon here**
   - Device-cache loss, host-state loss, and locality drift may all create shadows for different reasons.
   - Probe: keep those source-specific stories quarantined unless repeated later overflow shows one compact replay-equivalence witness is no longer enough.

## Design consequences

- DelayBasin can now keep exact-looking restore from flattening functional correctness and practical runtime equivalence into one story.
- GPUstorming gets one explicit place to say that a resumed training came back logically exact while still carrying a cache, locality, or host-parity shadow.
- The archive can now preserve correctness-level continuity without overstating preserved warmth or runtime parity.
- Stronger device-vs-host shadow-source accounting stays quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit public accounting for where the shadow came from — device-state warmth loss, host-side parity loss, locality drift, or scheduler contention — in a way that one bounded refresh-scope-axis-remediation-displacement-replay-equivalence witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every exact-looking restore as equally continuous. Preserve the smallest token that says whether the present replay-equivalence posture is `functionally-exact-restore`, `performance-shadow-restore`, or honestly `mixed-refresh-scope-axis-remediation-displacement-replay-equivalence`, and quarantine stronger shadow-source ambitions until repeated overflow makes them unavoidable.
