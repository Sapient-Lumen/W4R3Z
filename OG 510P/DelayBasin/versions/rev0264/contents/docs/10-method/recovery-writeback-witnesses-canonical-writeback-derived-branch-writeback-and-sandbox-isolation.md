# Recovery-writeback witnesses, canonical writeback, branch-local writeback, and sandbox-only restore

This is the compact successor surface for `OQ-0135`.

## Practice / observation

Once DelayBasin already distinguishes recovery anchor and recovery identity, one further failure mode stays live: a current row can honestly say that restored work is the same run or a branch and still fail to say whether that restored lineage is allowed to write back into canon.

A row can truthfully say that work resumed, a tuner continued, or a container was restored from checkpoint, yet that phrase can still hide whether the resumed lineage keeps writing to the canonical run, writes only to a derived branch, or must remain an isolated sandbox.

The archive does not need a standing recovery-writeback court for that.
It needs one bounded witness that says where write authority actually lands once a restore exists.

## External pressure from same-location experiment restore, existing-run result tables, experiment-directory autoresume, repeated named restores, and forensic sandbox copies

1. Ray Train keeps canonical continuation explicit at the storage lane. Its `BaseTrainer.restore()` docs say that the restored run continues writing results to the same cloud storage location. That pressures DelayBasin to keep same-run canonical writeback distinct from merely checkpoint-derived continuation. ([`REF-0884`](../00-meta/bibliography.md))

2. Ray Tune keeps existing-run writeback explicit. Its `Tuner.restore()` docs say all trials from the existing run are added to the result table, unfinished trials are continued, and the restored run continues writing results to the same cloud storage location. That pressures DelayBasin to keep existing-run canonical writeback distinct from branch-local retries or clones. ([`REF-0885`](../00-meta/bibliography.md))

3. BioNeMo keeps experiment-directory writeback explicit. Its ESM2 training docs say `experiment_name` is the sub-directory of `result_dir` that stores logs and checkpoints, and `resume_if_exists` attempts to resume if the checkpoint exists. That pressures DelayBasin to keep resumed same-experiment writeback distinct from noncanonical derivative runs that merely reuse checkpoint state. ([`REF-0886`](../00-meta/bibliography.md))

4. Podman keeps branch-local restore explicit. Its restore docs say a checkpoint tarball can be restored multiple times with different names and different IP identities, and `--keep` is needed if the checkpoint should remain reusable rather than consumed. That pressures DelayBasin to keep repeated named restores from silently inheriting canonical writeback authority. ([`REF-0883`](../00-meta/bibliography.md))

5. Kubernetes forensic checkpointing keeps sandbox isolation explicit. Its blog says the copy of a container can be analyzed and restored in a sandbox environment multiple times without the original container being aware of it. That pressures DelayBasin to keep sandbox-restored output from silently counting as authoritative continuation. ([`REF-0880`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems increasingly mix interrupted-run autoresume into the same experiment directory, branch-like restores for debugging or replay, and sandbox checkpoint analysis. If DelayBasin only says that restored work "continued," later passes can still overclaim by letting branch-local output or sandbox artifacts leak back as canonical writeback.

## Working synthesis

> DelayBasin should preserve one compact **recovery-writeback witness / canon-write card / sandbox-isolation brake** whenever a current continuity claim depends not only on restore identity, but on whether restored output may update the canonical lineage. Name the **governed row or surface**, the **restore / resume / write path**, the **prior recovery-writeback evidence**, the **current recovery-writeback evidence**, the **recovery_writeback_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-writeback-witness vs quarantine-recovery-writeback-governance consequence**. Keep exact run ids, trial ids, object-store URIs, experiment directories, container names, branch names, checkpoint tarball paths, sandbox labels, and hostnames outside the compact token. Do not let “restored” or “continued” silently count as canonical write authority without explicit support.

## Canonical writeback vs branch-local writeback vs sandbox-only vs mixed recovery writeback

Use the controlled family `recovery_writeback_state`:

- **canonical-writeback** says the restored lineage is allowed to keep writing into the canonical run or authoritative result surface itself.
- **branch-local-writeback** says the restored lineage may keep writing, but only into a derived branch, clone, retry lane, or other noncanonical result surface.
- **sandbox-only** says the restored lineage is isolated to forensic, debugging, rehearsal, or sandbox use and should not count as an authoritative writeback lane.
- **mixed-recovery-writeback** says the current situation honestly combines canonical-writeback, branch-local-writeback, or sandbox-only layers such that no single recovery-writeback class stays honest.

So the witness does not create a standing promotion senate.
It only says where write authority lands once a restore exists.

## Countermodels / probes

1. **Recovery identity already covers this countermodel**
   - Maybe once DelayBasin already tracks same-run versus branch identity, writeback adds nothing.
   - Probe: compare later rereads that preserve only `recovery_identity_state` against rereads that also preserve one compact recovery-writeback witness and inspect whether later passes still confuse branch-local output or sandbox artifacts with canonical continuation.

2. **Writeback authority is too implementation-local countermodel**
   - Maybe output-directory or result-table details are too stack-specific for one compact token.
   - Probe: keep the witness at the coarse level of canonical-writeback vs branch-local-writeback vs sandbox-only vs mixed-recovery-writeback and inspect whether later passes still need per-system arbitration rather than one bounded write-authority card.

3. **Any honest writeback story needs standing governance countermodel**
   - Maybe once the archive starts separating canonical writeback from derived-branch or sandbox-only restore, one compact witness will always overflow into broader promotion governance.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing recovery-writeback governance rather than ordinary clarification of write authority.

## Design consequences

- add one controlled `recovery_writeback_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `canonical-writeback`, `branch-local-writeback`, `sandbox-only`, and `mixed-recovery-writeback`;
- use the witness only where a current continuity claim depends on whether restored output may update canonical lineage rather than merely existing as a resumed or derived branch;
- keep exact run ids, trial names, cloud/object-store URIs, result directories, checkpoint paths, container names, and sandbox labels outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-recovery-writeback-witness` when the current claim honestly only supports branch-local or sandbox-only output rather than canonical writeback;
- and quarantine any stronger recovery-writeback court, promotion senate, or sandbox board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact recovery-writeback witness is no longer enough — for example, if the archive honestly needs standing governance over branch promotion, sandbox-to-canonical carryover, cross-row merge arbitration, or writeback admission policy that cannot be expressed as one bounded witness plus the existing recovery-anchor and recovery-identity surfaces.

Until then, prefer this compact successor surface over a recovery-writeback court, promotion senate, or sandbox board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the system restored and continued.”
It is also preserving whether restored output may keep writing into canon, only into a derived branch, or only into an isolated sandbox.
That matters because later stateless passes can preserve all the nearby recovery and lineage prose and still silently overclaim authority just by sounding continuation-consistent.
