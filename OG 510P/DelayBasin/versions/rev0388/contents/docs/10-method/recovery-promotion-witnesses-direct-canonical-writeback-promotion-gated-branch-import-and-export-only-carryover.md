# Recovery-promotion witnesses, direct canonical writeback, promotion-gated branch import, and export-only carryover

This is the compact successor surface for `OQ-0136`.

## Practice / observation

Once DelayBasin already distinguishes recovery identity and recovery writeback, one further failure mode stays live: a current row can honestly say where restored output writes **now** and still fail to say how noncanonical output may later re-enter canon.

A row can truthfully say that a branch kept writing to its own lane or that a sandbox export stayed isolated, yet that phrase can still hide whether the output is already canonical, needs an explicit promotion act before canon may inherit it, or should remain export-only carryover.

The archive does not need a standing recovery-promotion court for that.
It needs one bounded witness that says whether branch or sandbox output is already authoritative, promotion-gated, or only portable residue.

## External pressure from DVC experiment lineage, workspace apply, branch promotion, merge import, patch import, and exported checkpoint restore

1. DVC's experiments overview keeps experiment lineage distinct from ordinary Git history. Its docs say experiments preserve a connection to the latest commit in the current branch as their parent or baseline but do not form part of the regular Git tree. That pressures DelayBasin to keep noncanonical experiment lineage distinct from already-canonical history. ([`REF-0887`](../00-meta/bibliography.md))

2. DVC's `exp apply` keeps promotion explicit. Its docs say `dvc exp apply` restores an experiment into the workspace, and the result can then be made persistent with ordinary Git commit flow. That pressures DelayBasin to distinguish branch or experiment output that has been surfaced for promotion from output that is already canonical. ([`REF-0888`](../00-meta/bibliography.md))

3. DVC's `exp branch` keeps promotion-gated branch import explicit. Its docs say `dvc exp branch` makes an experiment persistent as a Git branch, and one may later `git merge` that branch to combine it with the current project version. That pressures DelayBasin to keep derived-branch success distinct from already-promoted canonical writeback. ([`REF-0889`](../00-meta/bibliography.md))

4. Git's merge docs keep canonical branch import explicit. `git merge` merges named branches into the current branch and advances the current branch to the result of the merge. That pressures DelayBasin to treat branch-to-canon promotion as a named act rather than ambient sameness. ([`REF-0890`](../00-meta/bibliography.md))

5. Git's cherry-pick docs keep patch import explicit. `git cherry-pick` applies the change a commit introduces and records a new commit on the current branch. That pressures DelayBasin to keep selective import into canon distinct from simple branch existence or checkpoint descent. ([`REF-0891`](../00-meta/bibliography.md))

6. Podman's restore docs keep exported checkpoint carryover explicit. `podman container restore --import` restores from an exported checkpoint tarball and does not require the original container name or ID as input. That pressures DelayBasin to keep portable exported restore artifacts from silently counting as already-promoted canonical lineage. ([`REF-0892`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU and experiment systems increasingly mix same-run autoresume, branch-local trial continuation, branch promotion through explicit apply or merge acts, and export-only artifacts used for debugging or migration. If DelayBasin only says that restored output “exists” or “was good,” later passes can still overclaim by letting noncanonical success sound like already-promoted canon.

## Working synthesis

> DelayBasin should preserve one compact **recovery-promotion witness / branch-import card / export-only brake** whenever a current continuity claim depends not only on where restored output writes **now**, but on how noncanonical output may later re-enter canonical lineage. Name the **governed row or surface**, the **source branch / experiment / export path**, the **prior recovery-promotion evidence**, the **current recovery-promotion evidence**, the **recovery_promotion_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-promotion-witness vs quarantine-recovery-promotion-governance consequence**. Keep exact commit hashes, branch names, experiment ids, workspace diffs, checkpoint tarball paths, container names, and merge or cherry-pick commands outside the compact token. Do not let “good branch output” or “portable export” silently count as already-promoted canonical authority without explicit support.

## Direct canonical writeback vs promotion-gated branch import vs export-only carryover vs mixed recovery promotion

Use the controlled family `recovery_promotion_state`:

- **direct-canonical-writeback** says the current output is already on the canonical authoritative lane; no later promotion act is required for canon to inherit it.
- **promotion-gated-branch-import** says the current output lives on a derived branch, experiment, or noncanonical lane and needs an explicit apply / merge / cherry-pick / import act before canon may inherit it.
- **export-only-carryover** says the current output is portable residue, forensic export, or analysis-only carryover and should not count as canonical or promotion-ready authority without a fresh separate admission path.
- **mixed-recovery-promotion** says the current situation honestly combines direct canonical, promotion-gated, or export-only layers such that no single promotion class stays honest.

So the witness does not create a standing promotion senate.
It only says whether noncanonical output is already canonical, promotion-gated, or export-only.

## Countermodels / probes

1. **Recovery writeback already covers this countermodel**
   - Maybe once DelayBasin already tracks canonical-writeback vs branch-local-writeback, promotion adds nothing.
   - Probe: compare later rereads that preserve only `recovery_writeback_state` against rereads that also preserve one compact recovery-promotion witness and inspect whether later passes still confuse branch-local success with already-promoted authority.

2. **Promotion is too workflow-specific countermodel**
   - Maybe apply, merge, cherry-pick, and import are stack-local details that do not belong in one compact token.
   - Probe: keep the witness at the coarse level of direct-canonical-writeback vs promotion-gated-branch-import vs export-only-carryover vs mixed-recovery-promotion and inspect whether later passes still need richer workflow law rather than one bounded promotion card.

3. **Any honest promotion story needs a standing court countermodel**
   - Maybe once the archive starts separating branch success from promoted authority, one compact witness will always overflow into standing merge or promotion governance.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require a broader promotion court rather than ordinary clarification of promotion status.

## Design consequences

- add one controlled `recovery_promotion_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `direct-canonical-writeback`, `promotion-gated-branch-import`, `export-only-carryover`, and `mixed-recovery-promotion`;
- use the witness only where a current continuity claim depends on how noncanonical restored output may later re-enter canon rather than merely where it currently writes;
- keep exact commit ids, branch names, experiment ids, workspace diffs, checkpoint tarballs, container names, and export handles outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-recovery-promotion-witness` when the current claim honestly only supports promotion-gated or export-only status rather than already-canonical authority;
- and quarantine any stronger recovery-promotion court, merge senate, or export-admission board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen stronger machinery only if one compact recovery-promotion witness is no longer enough — for example, if the archive honestly needs standing governance over branch admission criteria, conflict arbitration, export-to-canon adjudication, or selective import policy that cannot be expressed as one bounded witness plus the existing recovery-writeback surface.

Until then, prefer this compact successor surface over a recovery-promotion court, merge senate, or export-admission board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the branch produced good output.”
It is also preserving whether that output is already canonical, still requires a named promotion act, or should remain export-only residue.
That matters because later stateless passes can preserve all the nearby success and continuity prose and still silently overclaim authority just by sounding canon-compatible.
