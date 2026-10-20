# Synchronization trust and backup graduation

Status: founding synchronization construction complete; 24-hour bounded three-writer soak accepted; precious-data recommendation not yet made.
Updated 2026-09-22.

## The distinction that must survive

IoTox keeps authorized peers converged. A backup lets an owner recover when convergence did exactly
the wrong thing for the owner's intent.

If an authorized writer deletes a directory, writes damaged bytes, or is controlled by an attacker,
IoTox may correctly authenticate and propagate that event. Another writable IoTox peer, a conflict
copy, a checkpoint, a pin, CAS history, or GC quarantine is therefore not automatically a backup.
A true backup is independently versioned, has a different failure and authority domain, and has
passed a restore drill after the live synchronized copies are treated as unavailable.

The founding operator keeps real backups of the drives, including this machine. That is the right
containment posture. It makes careful experimentation recoverable; it does not by itself turn the
current construction into a precious-data recommendation.

## Current trust level

The present evidence supports:

- disposable and reproducible test trees;
- noncritical private Linux regular-file directories;
- important *working copies* when the authoritative recovery copy is independently backed up and
  its restore has been tested; and
- bounded one-writer/read-only or up-to-16-writer full-mesh use whose data fits the documented file,
  mode, conflict, and 4,096-entry limits.

It does not support making IoTox the only recovery path for precious originals. The two-hour
IoTox/Resilio shadow, 4,096-file gate, 16-candidate conflict gate, deterministic crash layouts, and
Sandwurm restart campaigns are meaningful synchronization evidence, not universal storage evidence.

## Operator checklist before using a real working directory

1. Run `iotox sync-doctor` with the intended access, interval, metadata, and selection policy. After
   creating the noncritical namespace, run `iotox sync-doctor-configured --config PATH NAMESPACE`
   against every node's exact deployment before promotion. Inventory anything these commands cannot
   represent. Use only private regular files and directories whose semantics fit the
   selected policy. Exclude symlinks, sockets, devices, FIFOs, ACL/xattr-dependent data, ownership
   translation, case-fold-sensitive names, and metadata whose meaning is not represented.
2. Keep a versioned backup outside the synchronized namespace and outside every IoTox writer's
   authority. Another always-writable peer is not enough.
3. Restore that backup into a separate empty location and verify it without reading any IoTox live
   tree or store. `iotox sync-recovery-verify BACKUP_ROOT RESTORED_ROOT` now performs the exact
   bounded external-tree comparison. ADR 0360 adds optional all-or-none provenance labels:
   `backup-system=TEXT backup-generation=TEXT backup-failure-domain=TEXT restore-provenance=TEXT`.
   `tools/run-sync-retained-recovery-drill.py` wraps that command and writes a retained content-free
   receipt binding the report hash, counts, manifests, root-device observation, and label hashes.
   ADR 0366 adds `--require-operator-provenance` and `--require-different-device` to that wrapper so
   independence-oriented drills can reject same-device or unlabeled receipts instead of merely
   recording them. Record when the drill passed and which backup generation was used; none of these
   commands assesses whether the selected backup is actually independent.
4. Rehearse with a representative noncritical copy first. Exercise edits, concurrent edits,
   deletion, empty files, disconnect, daemon restart, conflict resolution, and replacement of one
   node from empty state.
5. On every member, inspect `iotox sync-status`, run `iotox sync-repair NAMESPACE`, and resolve every
   unexpected `.iotox-conflicts` entry before promotion. A quiet scheduler is not equivalent to a
   verified graph.
6. Check capacity headroom for the complete tree, CAS store, incoming staging, projection staging,
   conflict alternatives, and backup retention. Do not operate at the 4,096-entry or quota edge.
7. Document the membership and retirement ceremony. Revoking capabilities and applying
   `sync-writer-cutoff` to every survivor are distinct operations; missing either can leave a former
   writer effective.
8. Keep the backup schedule and restore drills after promotion. Passing once does not protect later
   generations.

For data that would be painful or impossible to recreate, failure of any item means IoTox remains a
secondary working copy only.

## Engineering gates before recommending precious working sets

These gates are deliberately concrete. They are the next trust work, not a claim that the founding
roadmap was incomplete.

1. **Preflight and inventory (implemented by ADRs 0288, 0290, 0297, and 0315):** `sync-doctor` refuses
   unsupported source shapes and reports policy transformations, selected entry/object/byte counts,
   conservative first-revision store/staging minima, and default bounds before a namespace is created.
   That entrance deliberately labels managed-store headroom as not probed. The configured command
   strictly loads the exact Agent configuration, namespace and signed automation, inventories live
   immutable-store and incoming-staging occupancy under the existing transaction, applies nondefault
   quota headroom, and checks source/managed filesystem availability without creating state. Namespace
   health separately authenticates active graph, object, conflict, repair, automation, and cutoff
   truth against the namespace ceiling. These are point-in-time mechanisms, not reserved capacity,
   storage-durability evidence, or backup certification.
2. **Observable health (implemented by ADRs 0297 and 0298):** one stable-device-signed content-free
   record defines green/yellow/red over convergence, conflicts, repair coverage, automation stalls,
   store pressure, writer membership, and cutoffs. `diagnostics-export` joins that record by exact
   device identity, namespace, generation, and digest without exposing paths or content. This closes
   the observability mechanism, not any recovery, backup, capacity, or long-soak gate.
3. **Extended writable soak (mechanism implemented by ADRs 0361, 0364, 0367, 0368, 0369, 0370, 0371, 0372, 0373, 0374, 0375, and 0376; 24-hour bounded same-host KVM/ext4 evidence accepted):**
   the three-writer harness now has `--soak-seconds`, `--soak-minimum-cycles`,
   `--soak-restart-every`, `--soak-repair-every`, and
   `--soak-stalled-restart-after` knobs, plus `--soak-restart-settle-policy`,
   `--soak-final-boundary-restart-policy`, `--soak-repair-restart-policy`, and
   `--sync-repair-control-timeout-ms` for separating representative
   post-restart readiness and repair cadence from sharper restart stress. The
   24-hour profile uses `skip-if-floor-satisfied` only at a final scheduled
   restart boundary after the wall-clock and cycle floors are already satisfied;
   the receipt records skip counts and cycles so this cannot be mistaken for an
   untested restart-settle pass.
   Sandwurm exposes
   `tools/iotox-sandwurm-lab.sh up-three-writer soak-smoke` for a short validation cell and
   `tools/iotox-sandwurm-lab.sh up-three-writer soak-24h` for the real 24-hour gate.  The
   content-free host-side watch loop is:

   ```sh
   tools/iotox-sandwurm-lab.sh watch-three-writer PROOF_ROOT \
     --jsonl PROOF_ROOT/host-watch.jsonl \
     --print-mode changes \
     --heartbeat-samples 10
   ```

   The receipt
   records elapsed time, cycle count, delete cycles, scheduled restart targets,
   final-boundary restart skips, stalled-cycle recoveries, restart-settle
   passes, repair passes, timing bounds, final digest commitment, and high-water
   RSS without content. Compact proof
   `.sandwurm/exports/three-writer/run.UFBCMzt9` accepts the short same-host KVM/ext4 smoke with 4
   soak cycles over 34.235 seconds, 2 daemon restarts, 2 repair passes, retained recovery provenance,
   and the storage-fault follow-up. ADR 0364 now makes ordinary `SIGINT`/`SIGTERM` interruption
   retain a rejected partial-soak receipt, so a time-boxed or operator-stopped long run still
   preserves cycle, restart, repair, timing, and final-digest progress without content. The first
   24-hour attempt reached 72 completed writable soak cycles before rejecting at cycle 73 with one
   node behind the synthetic projection. ADR 0367 keeps that as useful rejected evidence, records
   content-free projection shape for future late-soak rejects, rotates scheduled restarts across all
   three writers, and enables a bounded 120-second stalled-cycle restart/repair path for the 24-hour
   profile. The first clean rerun used the original five-second edit cadence, reached 68 cycles, and
   needed two stalled-cycle recoveries before operator stop; ADR 0368 preserves that as high-churn
   stress evidence and changes `soak-24h` to a representative four-minute edit cadence. ADR 0369
   makes live status cadence-aware so the retuned sparse-progress run is not misreported as stale.
   The first retuned candidate reached cycle 10 cleanly, then hit stalled-cycle recovery at cycles
   19 and 20 and exposed a rejected-receipt shutdown bug; ADR 0370 hardens last-gasp rejected
   evidence so future interrupted candidates remain machine-verifiable. ADR 0371 then keeps the
   primary 24-hour profile passive on slow cycles by disabling emergency stalled-cycle restarts and
   using a 900-second hard cycle timeout. That passive candidate reached 71 cycles and completed one
   full scheduled restart rotation before rejecting at cycle 72, where the scheduled restart killed
   the active writer immediately after its fresh edit; ADR 0372 moves scheduled restarts before the
   cycle edit and records `soak_restart_phase`. A restart-before-edit smoke from commit
   `290023c8fef1a858952ed12e4eb2eea0e5d142fe` accepted, but the following 24-hour candidate
   `.sandwurm/lab/three-writer-soak-24h/run.Ym8xWhvm` rejected shortly after the cycle-48 restart
   because periodic `sync-repair` coincided with scheduled daemon churn and node `c` hit a local
   control-response deadline. Its rejected receipt showed aligned content-free projections rather
   than data divergence. ADR 0373 makes the `sync-repair` control deadline explicit and defers
   periodic repair from scheduled-restart cycles in the representative 24-hour profile; accepted
   receipts must also prove that no deferred repair is still pending at completion. The clean
   ADR 0373 smoke accepted at `.sandwurm/lab/three-writer-soak-smoke/run.cnowmx9v`. The following
   24-hour candidate `.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC` rejected after the first
   restart-before-edit: nodes `a`/`b` stayed on cycle 23 while node `c` held cycle 24, with matching
   store shape and zero conflict alternatives. ADR 0374 adds `repair-before-edit` restart-settle
   evidence before each post-restart synthetic edit. The clean ADR 0374 smoke accepted at
   `.sandwurm/lab/three-writer-soak-smoke/run.dvdqSlPg` with two restart-settle passes and drained
   deferred repairs. The corrected 48-hour-budget candidate
   `.sandwurm/lab/three-writer-soak-24h/run.hlBeElr6` then reached cycle 143 with six
   restart-settle passes before rejecting at cycle 144 with one lagging node, zero conflict
   alternatives, and recovery disabled by ADR 0371. ADR 0375 makes the active VM-only gate use a
   recorded 600-second stalled-cycle recovery threshold before the 900-second hard timeout; a future
   accepted receipt must bind `soak_stalled_restart_after_ms = 600000` and still prove exact
   convergence. ADR 0376 then makes representative long soaks emit content-free per-cycle edit and
   convergence progress so live watching does not depend on a 10-cycle sparse checkpoint. The fresh
   post-ADR 0377 compact proof `.sandwurm/exports/three-writer/run.9nqvO8B2` accepted after 289 writable
   soak cycles over `115981467` ms (`32h13m01s`): 24 shadow cycles, 12 scheduled daemon restarts
   rotating `a,b,c` four times, 12 restart-settle passes, 28 repair passes, 12 deferred repairs with
   no pending repair at completion, 4 bounded stalled-cycle recoveries, maintenance lifecycle,
   writer cutoff, recovery rehearsal, storage-fault rehearsal, and read-only startup refusal all
   verified. This closes the same-host 24-hour soak graduation gate. It still does not claim
   precious-data readiness or versioned recovery custody. ADR 0397 retains a later, harder rejected
   candidate, `.sandwurm/exports/three-writer/run.WAb1ARs9`, as negative evidence: it crossed the
   24-hour wall-clock floor and reached 287/288 writable cycles with 12 scheduled restarts, 11
   restart-settle passes, 28 repair passes, 11 repair deferrals, and 5 stalled-cycle recoveries, then
   rejected during final scheduled restart-settle because node `c` hit a `sync-repair field-notes`
   control-response deadline. Its projections still matched and the compact proof verifies as
   rejected. This does not demote the accepted `run.9nqvO8B2` gate; it names the next long-soak
   frontier: final scheduled-restart repair near the minimum-cycle boundary must become boring.
   ADR 0398 separately hardens the release intake for this evidence: stable sync manifests now
   reject wrong-shape local-preflight, storage-readiness, long-soak, backup-custody,
   restore-drill, and recovery-runbook files instead of accepting arbitrary prose whose hash matches
   the manifest.
   ADR 0403 refreshes the current accepted long-soak proof after the native
   precious-data signoff porches landed. Compact proof
   `.sandwurm/exports/three-writer/run.2nPKtCoX` verifies as accepted with
   24 shadow cycles, 288 writable soak cycles, `97453767` ms (`27h04m13s`)
   of soak elapsed, 11 restart-settle passes, 11 repair deferrals, zero
   stalled-cycle recoveries, zero stalled-cycle restarts, maintenance lifecycle,
   writer cutoff, recovery rehearsal, storage-fault rehearsal, live ENOSPC
   observation, and read-only startup refusal. The compact export has five
   content-free files, total size 96,980 bytes, manifest SHA-256
   `e7e42344883152e5dde264c3b6fab0c0df5e601a56334e2c2e344754d30318f9`,
   and raw guest sync receipt SHA-256
   `687b4ace878465ba733399a722d009a8d99afc616fe244ad7f2721443263356b`.
   `tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json`
   turns that proof into the native `sync.long-soak` verifier receipt with
   SHA-256 `6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0`.
   This refreshes the `sync.long-soak` gate for precious-data signoff, but it
   still does not create recovery custody or a sole-system-of-record
   recommendation.
4. **Abrupt-storage campaign (bounded filesystem, workspace, publication,
   and signed-metadata slices implemented by ADRs 0325 and 0332--0339):** three
   separate 192-MiB loop-backed ext4 node roots now cross real live `ENOSPC`, read-only startup
   refusal with an unchanged durable-state digest, and abrupt Agent death at a signed
   `pending-workspace` side of a 32-MiB exchange; restart convergence and repair pass in every case.
   A separate corrected two-boot Sandwurm campaign now kills the exact Cloud Hypervisor process after
   binding raw workspace phase byte 2, boots a copy of its task-owned crash disk, admits only exact
   prior/completed offline projections, preserves identities, and converges all writers. The
   phase-reversed v1 predecessor is withdrawn and rejected. The remaining gate is larger: repeat the
   whole-VMM cut at every other named durable tree-v2
   transition and both old/new linearizations, extend corruption beyond the
   five present live signed tree-v2 roots, and cover
   projection/remount open descriptors plus cold/near-ceiling populations. ADR 0328 separately closes
   the direct scan/store case where a source is mutated
   through a writer descriptor opened before the scan. Even the larger campaign is crash evidence,
   not a claim that lying hardware honors `fsync`. See
   `evidence/2026-09-04-sync-whole-vmm-power-cut.md`.
   ADR 0333 additionally qualifies the paired post-exchange side: all offline views remain completed
   while C retains pending byte 2, pending marker orientation, and the old projection stage. See
   `evidence/2026-09-04-sync-whole-vmm-post-exchange-power-cut.md`.
   ADR 0334 makes receive- and CAS-temporary cleanup itself durable and constructs two strict v4
   whole-VMM cells. Each freezes the follower with `SIGSTOP` at an exact semantic observation before
   host `SIGKILL`, then inspects absent-or-exact CAS state offline. Source-linked runs `1e05ayp9`
   and `jtiyspp_` pass with independently verified compact proofs: recovery begins exactly
   `[completed, completed, prior]`, removes all temporaries, installs the exact object, preserves
   identities, converges, restores three branches per node, and repairs. See
   `evidence/2026-09-08-sync-whole-vmm-object-pipeline-power-cut.md`. ADR 0335 constructs the three
   exact manifest/immutable-record/mutable-pointer pre-rename cells. Its first pointer attempt found
   a real recovery stall when an exact orphan record was treated as an incorporated pointer; the
   repaired subscriber now replays that record through ordinary acceptance with zero retransfers in
   a deterministic regression. All three repaired-source-linked campaigns now pass from one binary;
   see `evidence/2026-09-08-sync-whole-vmm-branch-publication-power-cut.md`. ADR 0336 also closes the
   three post-rename/pre-directory-fsync sides from one optimized binary; see
   `evidence/2026-09-08-sync-whole-vmm-directory-durability-power-cut.md`.
   ADR 0337 adds exact nonmutation/refusal and external byte-for-byte
   restoration for current branch pointer, manifest, immutable record,
   workspace, and maintenance records. Source-linked run `mixJ9VUp` passes all
   five ordered cells on the founding networkless KVM/ext4 stack, retains
   corrupt bytes across live repair and cold startup, restores exact originals,
   preserves identity/worktree, and finishes at `[3,3,3]` with repair on all
   nodes. See `evidence/2026-09-08-sync-tree-v2-metadata-corruption.md`.
   ADR 0339 now adds direct valid-old branch/workspace/maintenance witness
   refusal and a receipt-v2 all-five-co-resident construction. Source-linked
   KVM/ext4 run `MG27auOK` qualifies it with a strict compact proof; see
   `evidence/2026-09-08-sync-tree-v2-co-resident-metadata-corruption.md`.
   ADR 0338 preserves deterministic held-descriptor writes both before and
   immediately after exchange and authenticates projection-policy transitions.
   The next production gate is ADR 0340: post-exchange
   descriptor retention across restart/remount. ADR 0378 now accepts the first
   same-host dm-snapshot dishonest-storage drill:
   `.sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X` proves one
   acknowledged-write valid-old rollback is detected and refused against an
   external witness floor for branch-pointer, workspace, and maintenance shaped
   records. ADR 0379 extends that same-host science to ext4 and btrfs across
   six production-shaped families and four scenarios: valid-old rollback,
   cross-family rollback, torn manifest, and `dm-flakey drop_writes` masked
   write loss. Source-linked proof
   `.sandwurm/exports/sync-dishonest-storage/run.qGwEvF17` independently
   verifies. ADR 0380 adds the first exact block-prefix replay substrate:
   `.sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra` independently
   verifies ext4 and btrfs `dm-log-writes` replay for valid-old,
   mixed-manifest/branch-record, and complete-current marks. ADR 0381 then
   accepts the live-Agent production transaction-prefix gate:
   `.sandwurm/exports/sync-production-prefix/run.HYXJnDzI` independently
   verifies real `sync-create` and `sync-publish` transaction marks on ext4
   and btrfs. The `storage-readiness` report now accepts local storage science
   while keeping versioned recovery custody, precious-data
   readiness, second-cut cleanup, and physical-power boundaries open.
5. **Representative-capacity campaign (first persistent full-mesh cell recorded 2026-09-03):** the
   local controls retain a 4,096-file structural lifecycle and a 3,621-entry, 53,477,376-byte
   doctor/restore population. ADR 0320 additionally runs 512 16-KiB files (8,388,608 logical bytes)
   through three real daemons on persistent ext4: the clean-source cell caught up in 70.997 seconds,
   repaired in 163/318/75 ms, used 16--18 MiB Agent high-water RSS, and grew allocated state by about
   20--21 MiB per node. ADRs 0321--0322 then complete the ordinary conflict/lifecycle; a second
   byte-identical-binary pressure cell recovers one interrupted exchange without losing the
   path-based local edit. Cold repetition, the near-ceiling mixed-size
   population, 4,096 files across three stores, conflict amplification at those sizes, and the
   remaining abrupt-power/corruption gates remain open. The 24-hour same-host soak was first
   accepted by `.sandwurm/exports/three-writer/run.9nqvO8B2` and is now
   refreshed by `.sandwurm/exports/three-writer/run.2nPKtCoX`. ADR 0350 removes avoidable
   sparse source-walk descent into unrelated siblings, ADR 0351 removes empty complete-policy
   unselected-preservation/compare walks, and ADR 0352 reports the remaining preserved-unselected
   shape through content-free counters, but incremental projection/rebuild work should still replace
   complete-tree projection costs before large ordinary directories are recommended. See
   `evidence/2026-09-03-sync-capacity-controls.md` and
   `evidence/2026-09-03-sandwurm-sync-persistent-capacity.md`.
   A later direct-host 3,500-file/57,344,000-byte diagnostic timed out after the 1,800-second
   capacity wait with branch convergence complete but follower object stores still partial and no
   follower projection. The corrected observer retry still timed out, which motivated ADR 0329's
   bounded tree-v2 exact-object lane window. The first source-linked four-lane direct retry passed
   the same population and conflict lifecycle in 1,050.374 seconds; it must still be repeated next
   to an explicit one-lane baseline in Sandwurm before it becomes qualification evidence. Details
   live in
   `evidence/2026-09-03-sync-near-ceiling-timeout.md`. ADR 0331 removes the remaining full CAS
   inventory pass per received lane batch while retaining a strict final effect fence. Its first
   clean 3,500-file direct run reduced 219 batch-implied store scans to 7 and 5 scans across
   multiple automation pulls, while leaving overall direct elapsed time effectively flat. The exact
   2-vCPU/2-GiB VM repeat reduced aggregate follower scans to 21 and 15 and completed in 634.194
   seconds, 19.5% below ADR 0330's VM baseline. ADRs 0341--0348 now add bounded Linux source-watch
   wakeups, a 250 ms non-sliding debounce, preservation of busy source changes, safe no-op refresh
   skips for unchanged stable workspaces, volatile digest reuse for stable regular files, and grouped
   scan/merge/projection path work plus directory-ancestor and branch-transition validation
   indexing plus retained-history diff grouping. ADR 0350 removes avoidable sparse source-walk
   descent into unrelated siblings, ADR 0351 removes empty complete-policy unselected work, and ADR
   0352 reports preserved sparse projection work without paths or contents. ADR 0353 adds a
   tree-v2 busy-republish cooldown after current rev0051 cap-8 regressed from repeated intermediate
   pulls; the post-fix Sandwurm series makes cap 8 the current measured sweet spot
   (480.819 seconds of capacity catch-up), with cap 16 retained as a negative scaling proof
   (1,271.565 seconds and 90/111 follower scans).
   True path-level incremental projection, sparse-preservation optimization, deeper
   intermediate-head coalescing, and the remaining storage gates above remain necessary.
6. **Filesystem contract (preflight mechanism implemented by ADR 0318):** both doctor paths now
   refuse unsafe ownership/mutability, ASCII case-fold collisions, symlinks, hard links, ACL/xattr
   state, sparse allocation, and special files. Their additive contract record says byte-exact
   case-sensitive paths are required and that ownership, directory modes, and timestamps are local
   or normalized rather than synchronized. This is a point-in-time Linux source gate, not Unicode or
   case-insensitive portability, runtime immutability, or filesystem/hardware
   qualification.
7. **Recovery rehearsal tooling (bounded mechanism and same-host VM gate implemented by ADRs 0319,
   0323, 0324, 0360, 0361, and 0362):**
   `sync-recovery-verify` now compares an operator-selected backup view with a disjoint restored tree
   using strict bounded tree-v2 owner-mode-v2 semantics, refuses unresolved conflict projections,
   and reads no live IoTox state. ADR 0360 adds explicit optional backup-system, backup-generation,
   backup-failure-domain, and restore-provenance labels plus same/different-device observation while
   retaining `backup-independence=not-assessed`. ADR 0361 adds a wrapper that writes retained
   content-free drill receipts and makes the Sandwurm node-loss follow-up bind same-VM drill labels
   into all restore-verifier hashes. ADR 0362 keeps exact terminal cutoff replays in retired history
   rather than the live frontier, so a valid terminal record cannot silently re-enable an obsolete
   writer during replacement. ADR 0364 keeps interrupted long-soak evidence as a rejected receipt
   rather than promoting it to backup or soak success. ADR 0366 makes retained recovery receipts fail
   closed when requested operator provenance or different-device observations are absent. The
   three-daemon rehearsal now erases and replaces one writer,
   performs separate revocation/cutoff/friendship removal plus two ordered checkpoint barriers,
   reseeds it, then erases every live node and rebuilds fresh identity/authority/namespace state
   from the restored ordinary tree. All replacement views are verified and obsolete principal
   hashes must be absent. A clean 2-vCPU/2-GiB Sandwurm run composes this with the 512-file capacity
   and 24-cycle persistent lifecycle, then completes recovery with zero watchdog restarts. The
   command and harness do not call sync history a backup or infer independence from two paths.
   On 2026-09-17 the loopback custody helper added one stricter same-host prerequisite: accepted
   run `run.9xP4yW5T` mounted the selected generation read-only on one ext4 loop device, restored it
   onto another, required bound provenance plus `root-devices-differ=1`, and retained a content-free
   receipt. It still does not prove off-machine custody, append-only retention, backup software
   correctness, storage honesty, or administrative independence. Independent immutable backup
   retention, append-only provenance custody, repeated
   generation-selection drills, and the longer storage/soak gates remain. See
   `sync-recovery-rehearsal.md`.
8. **Threat-dependent local protection (partially implemented by ADRs 0303, 0305, and 0310--0314):** the optional required
   fscrypt-v2 mode now protects the complete declared Agent-state closure against offline media
   inspection when its externally held key is absent. The authority-lane witness transaction
   coordinator and authenticated remote-service backend are implemented and fault-tested. ADR 0310
   adds the exact namespace/automation policy lane, automatic pre-activation commits, and whole-policy
   rollback refusal. ADR 0312 adds one optional per-namespace lane for the signed published,
   accepted, activated, and retained roots and refuses a complete old four-root/guard snapshot. ADR
   0314 separately anchors tree-v2's live branch frontier plus signed workspace and maintenance state.
   Attempts, objects/quarantine, content, worktree bytes, projections, health, and current pointers
   still lack external freshness, and same-host/same-snapshot service deployment
   is not independent. Therefore sync still lacks full protection against replay of the broader
   encrypted namespace closure or coordinated Agent/service restoration.
   These mechanisms are not prerequisites for every private machine, but their exact absence/presence
   must remain visible.

Invitation UX, sparse custody, tree-v2 range/auxiliary lanes, and richer metadata improve the
product, but they do not substitute for the recovery and failure gates above.

The roadmap additionally accepts revision history/diff/forward-restore planning, sparse path-prefix
custody, encrypted local state plus an independent rollback witness, human aliases/invitations, and a
content-free flight recorder. ADRs 0295--0297 implement selected custody, complementary exact
sources, and signed tree-v2 namespace health but not backup recovery. ADR 0291 implements the
recorder/export core and ADR 0298 joins the closed health record to that export. Neither surface
satisfies recovery, restore, or backup evidence. Their ordering and
nonclaims are frozen in the product-expansion program in `roadmap.md`.

## Graduation rule

IoTox may be promoted from noncritical synchronization to an important working-set tool when the
operator checklist passes for that exact dataset and independent recovery remains available. The
project should recommend it for precious working sets only after the applicable engineering gates
pass with retained evidence.

Even then, no synchronized system becomes the only copy. The final recovery question is simple:
can the owner erase or lose every IoTox node and still restore the required generation? If the answer
has not been demonstrated, there is no proven backup.
