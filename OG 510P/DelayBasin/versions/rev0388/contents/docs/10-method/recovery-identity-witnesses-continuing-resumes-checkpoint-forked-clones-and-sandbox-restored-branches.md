# Recovery-identity witnesses, continuing resumes, checkpoint-forked clones, and sandbox-restored branches

This is the compact successor surface for `OQ-0134`.

## Practice / observation

Once DelayBasin already distinguishes recovery loss and recovery anchor, one further failure mode stays live: a current row can honestly say that work resumed from its own checkpoint lineage and still fail to say whether that restore counts as the same continuing run or as a new branch.

A row can truthfully say that training resumed, a tuner came back, or a container was restored from its own checkpoint lineage, yet that phrase can still hide whether the current object is the interrupted run continuing, a new clone restored from the same checkpoint artifact, or an isolated sandbox copy.

The archive does not need a standing recovery-identity court for that.
It needs one bounded witness that says whether the restored lineage is still one continuing resume or a branch.

## External pressure from interrupted-run restore, unfinished-experiment autoresume, repeated named checkpoint restores, and forensic sandbox copies

1. Ray Train keeps continuing resumes distinct from new seeded runs. Its `BaseTrainer.restore()` docs say restore is for a previously interrupted or failed run, while a run that already completed successfully will not be resumed from that API and instead should continue in a new run launched with `resume_from_checkpoint`. That pressures DelayBasin to keep same-run continuation distinct from derived checkpoint branches. ([`REF-0877`](../00-meta/bibliography.md))

2. Ray Tune keeps existing-run continuation explicit. Its `Tuner.restore()` docs say all trials from the existing run are added to the result table, unfinished trials are continued, and errored trials can either resume from their latest checkpoints or restart from scratch. That pressures DelayBasin to preserve the difference between continuing the existing run and creating derivative retry branches. ([`REF-0881`](../00-meta/bibliography.md))

3. NVIDIA NeMo keeps unfinished-experiment resume distinct from other checkpoint uses. Its checkpoint docs say loading checkpoints with `restore_from()` or `from_pretrained()` is for evaluation or fine-tuning, while resuming an unfinished training experiment should use `resume_if_exists=True`. That pressures DelayBasin to keep same-experiment continuation distinct from derived fine-tune or evaluation branches that merely reuse checkpoint state. ([`REF-0882`](../00-meta/bibliography.md))

4. Podman keeps checkpoint-forked clones explicit. Its restore docs say a checkpoint tarball can be restored multiple times with different names, and the restored container gets another IP address when `--name` is used. That pressures DelayBasin to keep repeated restore capability from silently counting as one continuing runtime identity. ([`REF-0883`](../00-meta/bibliography.md))

5. Kubernetes forensic checkpointing keeps sandbox branches explicit. Its blog says a stateful copy of a running container can be analyzed and restored in a sandbox environment multiple times without the original container being aware. That pressures DelayBasin to keep sandbox-restored branches distinct from one continuing canonical resume. ([`REF-0880`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems increasingly mix interrupted-run autoresume, seeded continuation from prior checkpoints, clone-like checkpoint restores for debugging, and sandboxed state copies for forensics or experimentation. If DelayBasin only says that work “resumed from checkpoint,” later passes can still overclaim continuity by treating continuing resumes, cloned restores, and sandbox branches as the same recovery identity.

## Working synthesis

> DelayBasin should preserve one compact **recovery-identity witness / continuation card / clone brake** whenever a current continuity claim depends not only on a checkpoint or self-lineage anchor existing, but on whether the restored lineage is still the same continuing run. Name the **governed row or surface**, the **interruption / checkpoint / restore path**, the **prior recovery-identity evidence**, the **current recovery-identity evidence**, the **recovery_identity_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-identity-witness vs quarantine-recovery-identity-governance consequence**. Keep exact experiment ids, trial ids, checkpoint URIs, container names, pod names, image ids, sandbox names, hostnames, and output directories outside the compact token. Do not let “restored from its own checkpoint” silently count as one unbroken run identity.

## Continuing resume vs checkpoint fork vs sandbox branch vs mixed recovery identity

Use the controlled family `recovery_identity_state`:

- **continuing-resume** says the restored object still counts as the interrupted run or lineage continuing, rather than as a new named branch or analysis copy.
- **checkpoint-fork** says a checkpoint or saved run state seeded a new object, run, or clone that descends from earlier state but does not count as the same continuing run identity.
- **sandbox-branch** says the restored state lives in an explicitly isolated forensic, debugging, rehearsal, or sandbox branch that should not inherit canonical continuation identity.
- **mixed-recovery-identity** says the current situation honestly combines continuing-resume, checkpoint-fork, or sandbox-branch layers such that no single recovery-identity class stays honest.

So the witness does not create a standing continuity-lineage court.
It only says whether the restore is still the same run or a branch.

## Countermodels / probes

1. **Recovery anchor already covers this countermodel**
   - Maybe once DelayBasin already tracks what resumed state was anchored to, identity adds nothing.
   - Probe: compare later rereads that preserve only `recovery_anchor_state` against rereads that also preserve one compact recovery-identity witness and inspect whether later passes still confuse same-anchor continuation with cloned or sandboxed branches.

2. **Any self-lineage checkpoint is already the same run countermodel**
   - Maybe once a restore comes from the same run's own checkpoint lineage, that already proves one continuous run identity.
   - Probe: inspect whether later rereads still confuse interrupted-run restore with Podman-style repeated named restores or Kubernetes sandbox copies when only checkpoint lineage is preserved.

3. **Any honest identity story needs standing governance countermodel**
   - Maybe once the archive starts separating continuing resumes from clone or sandbox branches, one compact witness will always overflow into broader lineage governance.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing recovery-identity governance rather than ordinary clarification of restore identity.

## Design consequences

- add one controlled `recovery_identity_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `continuing-resume`, `checkpoint-fork`, `sandbox-branch`, and `mixed-recovery-identity`;
- use the witness only where a current continuity claim depends on whether a restored lineage is still the same run or instead a derived branch;
- keep exact run ids, trial names, pod/container names, checkpoint URIs, output paths, sandbox labels, and hostnames outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-recovery-identity-witness` when the current claim honestly only supports a cloned or sandboxed branch rather than one continuing resume;
- and quarantine any stronger recovery-identity court, clone senate, or sandbox board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact recovery-identity witness is no longer enough — for example, if the archive honestly needs standing governance over branch promotion, clone-versus-canonical arbitration, sandbox-to-production carryover, or cross-row writeback authority that cannot be expressed as one bounded witness plus the existing recovery-loss and recovery-anchor surfaces.

Until then, prefer this compact successor surface over a recovery-identity court, clone senate, or sandbox board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the system resumed from checkpoint.”
It is also preserving whether the restore still counts as the same interrupted run continuing, as a checkpoint-forked branch, or as an isolated sandbox copy.
That matters because later stateless passes can preserve all the nearby recovery and lineage prose and still silently overclaim continuity just by sounding checkpoint-consistent.
