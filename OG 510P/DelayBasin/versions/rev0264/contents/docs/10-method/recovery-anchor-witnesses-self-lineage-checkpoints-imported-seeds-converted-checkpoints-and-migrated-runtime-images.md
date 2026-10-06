# Recovery-anchor witnesses, self-lineage checkpoints, imported seeds, converted checkpoints, and migrated runtime images

This is the compact successor surface for `OQ-0133`.

## Practice / observation

Once DelayBasin already distinguishes repair scope, recovery loss, and resumed continuity, one further failure mode stays live: a current row can honestly say that work resumed from a checkpoint and still fail to say what that checkpoint was actually anchored to.

A row can truthfully say that training resumed, a container came back from a checkpoint, or a workload restarted from saved state, yet that phrase can still hide whether the resumed state came from the same run's own checkpoint lineage, a supplied seed checkpoint from elsewhere, a converted checkpoint artifact, or a migrated runtime image.

The archive does not need a standing continuity-lineage court for that.
It needs one bounded witness that says what kind of anchor the resumed state actually came from.

## External pressure from experiment-directory autoresume, restore-versus-seeded restarts, format conversion bridges, migration archives, and sandbox-restored runtime copies

1. BioNeMo Evo2 keeps self-lineage resume distinct from imported seeds. Its docs say `--ckpt-dir` supplies a pre-trained checkpoint while an existing `--experiment-dir` automatically resumes from the most recent checkpoint in that experiment directory instead of starting from `--ckpt-dir`. That pressures DelayBasin to distinguish same-lineage checkpoints from imported seeds. ([`REF-0876`](../00-meta/bibliography.md))

2. Ray keeps restore-versus-seeded restart explicit. The `BaseTrainer.restore()` docs say restore resumes a previously interrupted experiment from its experiment directory, while continuing a successful run should launch a new run with `resume_from_checkpoint`. That pressures DelayBasin to distinguish self-lineage experiment restore from a new seeded run. ([`REF-0877`](../00-meta/bibliography.md))

3. Megatron Bridge keeps checkpoint conversion explicit. Its guide documents bidirectional conversion between Hugging Face and Megatron plus one-call `import_ckpt` and `export_ckpt` flows. That pressures DelayBasin to keep converted checkpoints distinct from checkpoints that remain inside one native lineage. ([`REF-0878`](../00-meta/bibliography.md))

4. Podman keeps migrated runtime images explicit. Its checkpoint docs say exported checkpoints include original container and runtime metadata and can be imported on another system to enable container live migration. That pressures DelayBasin to keep migrated runtime images distinct from ordinary same-run checkpoint lineage. ([`REF-0879`](../00-meta/bibliography.md))

5. Kubernetes forensic checkpointing keeps clone-like restore pressure explicit. Its blog says a checkpointed container copy can be restored in a sandbox multiple times without the original container being aware and that checkpointing can also migrate a container between nodes without losing internal state. That pressures DelayBasin to keep current recovery-anchor truth explicit now and points toward a later identity question rather than silently treating every restored copy as one continuing lineage. ([`REF-0880`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems increasingly combine local autoresume, pre-trained checkpoint seeding, cross-framework checkpoint conversion, and live migration or sandboxed restore experiments. If DelayBasin only says that work resumed from “a checkpoint,” later passes can still overclaim lineage by treating self-lineage checkpoints, imported seeds, converted artifacts, and migrated runtime images as the same anchor class.

## Working synthesis

> DelayBasin should preserve one compact **recovery-anchor witness / lineage-anchor card / checkpoint-origin brake** whenever a current continuity claim depends not only on some checkpoint or resume path existing, but on where that resumed state was actually anchored. Name the **governed row or surface**, the **checkpoint / restore / migration path**, the **prior recovery-anchor evidence**, the **current recovery-anchor evidence**, the **recovery_anchor_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-anchor-witness vs quarantine-recovery-anchor-governance consequence**. Keep exact experiment-directory paths, image ids, conversion scripts, runtime annotations, container names, and checkpoint URIs outside the compact token. Do not let any generic “resumed from checkpoint” phrase silently count as the same lineage anchor.

## Self-lineage checkpoint vs imported seed vs converted checkpoint vs migrated runtime image vs mixed recovery anchor

Use the controlled family `recovery_anchor_state`:

- **self-lineage-checkpoint** says the resumed state comes from the same run's own checkpoint lineage or experiment directory rather than from an external seed, conversion artifact, or migrated runtime image.
- **imported-seed** says the resumed state comes from a supplied checkpoint or prior model artifact that seeds a new run rather than continuing the same run's own checkpoint lineage.
- **converted-checkpoint** says the resumed state depends on an explicitly converted checkpoint artifact or format-translation bridge rather than on the same native checkpoint lineage.
- **migrated-runtime-image** says the resumed state comes from a migrated runtime image or checkpointed runtime copy moved across hosts or restored into another environment.
- **mixed-recovery-anchor** says the current situation honestly combines self-lineage, imported, converted, or migrated anchor classes such that no single anchor class stays honest.

So the witness does not create a standing checkpoint-lineage court.
It only says what kind of anchor the resumed state actually came from.

## Countermodels / probes

1. **Recovery loss already covers this countermodel**
   - Maybe once DelayBasin already tracks state-preserving versus checkpoint-resume versus replay, the anchor no longer matters.
   - Probe: compare later rereads that preserve only recovery-loss class against rereads that also preserve one compact recovery-anchor witness and inspect whether later passes still confuse same-lineage resume with imported or converted seeding.

2. **Any checkpoint path is already enough countermodel**
   - Maybe the phrase “resumed from checkpoint” already proves all the lineage continuity that matters.
   - Probe: inspect whether later rereads still confuse experiment-directory autoresume, pretrained-seed restarts, bridge-converted checkpoints, and migrated runtime copies when only checkpoint presence is preserved.

3. **Any honest anchor story needs standing governance countermodel**
   - Maybe once the archive starts separating self-lineage, imported, converted, and migrated anchor classes, one compact witness will always overflow into broader continuity-lineage machinery.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing recovery-anchor governance rather than ordinary clarification of checkpoint origin.

## Design consequences

- add one controlled `recovery_anchor_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `self-lineage-checkpoint`, `imported-seed`, `converted-checkpoint`, `migrated-runtime-image`, and `mixed-recovery-anchor`;
- use the witness only where a current continuity claim depends on what anchored resumed state, not merely on whether some checkpoint or restore path existed;
- keep exact experiment names, checkpoint directories, bridge scripts, runtime annotations, image ids, hostnames, and migration commands outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-recovery-anchor-witness` when the current claim honestly only supports imported, converted, or migrated anchoring rather than self-lineage checkpoints;
- and quarantine any stronger recovery-anchor court, conversion senate, or migration board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact recovery-anchor witness is no longer enough — for example, if the archive honestly needs standing governance over checkpoint-lineage provenance, conversion-chain arbitration, migrated-runtime anchor review, or cross-row fork-versus-continuation disputes that cannot be expressed as one bounded witness plus the existing recovery-loss, repair-scope, response, and selector-family surfaces.

Until then, prefer this compact successor surface over a recovery-anchor court, conversion senate, or migration board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the system resumed from checkpoint.”
It is also preserving whether resumed state stayed anchored to the same run's own checkpoint lineage, came in as an imported seed, crossed a conversion bridge, or arrived as a migrated runtime image.
That matters because later stateless passes can preserve all the nearby recovery and continuity prose and still silently overclaim lineage just by sounding checkpoint-consistent.
