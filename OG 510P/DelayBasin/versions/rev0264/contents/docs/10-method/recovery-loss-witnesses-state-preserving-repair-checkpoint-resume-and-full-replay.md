# Recovery-loss witnesses, state-preserving repair, checkpoint resume, and full replay

This is the compact successor surface for `OQ-0132`.

## Practice / observation

Once DelayBasin already distinguishes selector truth, enforcement regime, response class, and repair scope, one further failure mode stays live: a current row can honestly say that work recovered after a failure, yet still fail to say how much of the prior working state actually survived that recovery.

A row can truthfully say that a GPU workload resumed, a Pod came back, a job recovered, or training continued, yet that phrase can still hide whether the same live state was preserved, the workload restarted from a saved checkpoint, or the work replayed from the beginning.

The compact repair is one small recovery-loss witness. It does not replace the selector, selector-provenance, selector-freshness, selector-enforcement, enforcement-regime, response, or repair-scope witnesses. It only says how much prior working state survived once recovery happened.

## External pressure from container checkpoints, checkpoint-backed worker recovery, local distributed checkpoints, requeued jobs, and AI/ML checkpoint-restore work

1. Kubernetes now keeps state-preserving recovery explicit. The Kubelet Checkpoint API docs say checkpointing creates a stateful copy of a running container and that, on a computer able to restore it, the restored container continues to run at exactly the same point it was checkpointed. That pressures DelayBasin to keep preserved live state distinct from checkpoint resume or replay. ([`REF-0871`](../00-meta/bibliography.md))

2. Ray Train keeps checkpoint resume versus replay explicit in one place. Its fault-tolerance docs say that when a worker process or node failure is detected, all workers are shut down, a new set of workers is started, and the restarted workers can resume training by loading the latest checkpoint. The same docs also say that without checkpoint save/load logic, training just starts from scratch. That pressures DelayBasin to distinguish checkpoint-backed continuation from full replay. ([`REF-0872`](../00-meta/bibliography.md))

3. NVIDIA NeMo keeps checkpoint resume explicit for GPU training. Its resiliency docs say fault tolerance automatically resumes training from the last checkpoint in case of interruptions, and that local checkpointing saves checkpoints directly to local storage on each node. That pressures DelayBasin to keep checkpoint resume distinct from both preserved live state and replay from the beginning. ([`REF-0873`](../00-meta/bibliography.md))

4. Slurm keeps replay explicit. The `sbatch` docs say that when a job is requeued, the batch script is initiated from its beginning, including after node failure or preemption. That pressures DelayBasin to keep replay-from-start explicit rather than letting requeue or restart language inherit equivalent continuity. ([`REF-0874`](../00-meta/bibliography.md))

5. Kubernetes' new Checkpoint/Restore Working Group keeps the frontier honest. Its announcement explicitly points to coordinated checkpoint/restore tooling and to AI + ML discussions around transparent checkpointing. That pressures DelayBasin to treat preserved-state portability as a real emerging case while still distinguishing it from ordinary checkpoint resume and replay. ([`REF-0875`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems often combine sidecar-triggered in-place restarts, cluster replacement of workers, last-checkpoint autoresume, local shard checkpoints, and early checkpoint/restore experiments for faster restart or migration. If DelayBasin only says that work “recovered” or “resumed,” later passes can still overclaim by treating preserved runtime state, resumed-from-checkpoint training, and replay-from-start retries as equivalent continuity.

## Working synthesis

> DelayBasin should preserve one compact **recovery-loss witness / state-survival card / replay brake** whenever a current continuity claim depends not only on whether work recovered, but on how much prior live state survived that recovery. Name the **governed row or surface**, the **recovery / checkpoint / resume path**, the **prior recovery-loss evidence**, the **current recovery-loss evidence**, the **recovery_loss_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-loss-witness vs quarantine-recovery-governance consequence**. Keep exact checkpoint paths, epoch counters, step numbers, optimizer shards, memory-page details, Pod names, and job handles outside the compact token. Do not let any “recovered,” “resumed,” or “continued” phrase silently count as equivalent state continuity without explicit support.

## State preserving vs checkpoint resume vs full replay vs mixed recovery loss

Use the controlled family `recovery_loss_state`:

- **state-preserving** says the current mechanism preserves or restores the live runtime state itself, so work continues from the same captured execution state rather than from a later saved checkpoint or a fresh replay.
- **checkpoint-resume** says the current mechanism restarts work from a previously saved checkpoint, so some prior state survives but not the full live runtime state at the moment of interruption.
- **full-replay** says the current mechanism starts from the beginning or from equivalent cold-start initialization rather than preserving live state or resuming from a saved checkpoint.
- **mixed-recovery-loss** says the current situation honestly combines preserved-state recovery, checkpoint resume, or replay across layers such that no single recovery-loss class stays honest.

So the witness does not create a standing continuity court.
It only says how much prior working state survived once some recovery path actually happened.

## Countermodels / probes

1. **Repair scope already covers this countermodel**
   - Maybe once DelayBasin tracks repair scope, nothing more is needed.
   - Probe: compare later rereads that preserve only repair_scope_state against rereads that also preserve one compact recovery-loss witness and inspect whether later passes still confuse live-state restoration, checkpoint resume, and replay.

2. **Checkpoint resume is too implementation-local countermodel**
   - Maybe recovery-loss class is too training-stack-specific for one compact token.
   - Probe: keep the witness at the coarse level of state-preserving vs checkpoint-resume vs full-replay vs mixed-recovery-loss and inspect whether later passes still need tool-specific checkpoint arbitration rather than one bounded recovery-loss card.

3. **Any honest state-survival story needs standing governance countermodel**
   - Maybe once the archive starts separating preserved runtime state, checkpoint resume, and replay, one compact witness will always overflow into broader continuity machinery.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing recovery governance rather than ordinary clarification of state survival.

## Design consequences

- add one controlled `recovery_loss_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `state-preserving`, `checkpoint-resume`, `full-replay`, and `mixed-recovery-loss`;
- use the witness only where a current continuity claim depends on how much prior state survived recovery, not merely on whether some response or repair path existed;
- keep exact checkpoint URIs, page-level runtime details, optimizer shards, epoch numbers, step counters, Pod names, and job handles outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-recovery-loss-witness` when the current claim honestly only supports checkpoint resume or full replay rather than preserved live state;
- and quarantine any stronger continuity court, checkpoint senate, or replay board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact recovery-loss witness is no longer enough — for example, if the archive honestly needs standing governance over transparent-checkpoint lineage, checkpoint-versus-import arbitration, or cross-row state-survival review that cannot be expressed as one bounded witness plus the existing repair-scope, response, regime, and selector-family surfaces.

Until then, prefer this compact successor surface over a continuity court, checkpoint senate, or replay board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the system resumed.”
It is also preserving whether recovery kept the same captured live state, fell back to a saved checkpoint, or replayed work from the beginning.
That matters because later stateless passes can preserve all the nearby recovery and repair prose and still silently overclaim continuity just by sounding recovery-policy consistent.
