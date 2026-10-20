# Workspace storage and cleanup

Tracked IoTox source is intentionally small. Large generated state belongs only in ignored roots and
must have an explicit retention reason. `DR0Pbox/`, retained distribution artifacts, and the reusable
private test-identity cache are never cleanup candidates.

## Audit first

The cleanup tool defaults to a dry run:

```sh
python3 tools/clean-workspace.py
python3 tools/clean-workspace.py --scope all
```

The default scope covers stale, tightly allowlisted `.sandworm/home/tmp/` entries, stale strictly
named `.sandworm/home/.local/share/Trash/{files,info}/` entries, superseded Sandwurm private proof
roots and compact pair/three-writer/shadow/power-cut/metadata-corruption/dishonest-storage
exports, exact
`.sandwurm/iotox-device-repair.*` offline disk-repair
workspaces, and failed/explicitly retained `.sandwurm/operator-tor/run.*` roots. Successful
operator-Tor gates remove their private root themselves. `--scope all` also lists reproducible build
trees while retaining the current `build/gcc-debug` tree. Alternate `.build/` lanes and strictly
named top-level `build-*` trees are reproducible and never retained by the build scope. Nothing is
deleted without `--apply`.

Before deletion, the tool:

- accepts only immediate children of fixed ignored roots with strict generated-name patterns;
- treats nested sandbox Trash as generated state only for `run.*`, `pair.*`, `gcc-coverage*`,
  `tmp.*`, and `revNNNN` payload names plus their matching `.trashinfo` metadata;
- protects every compact Sandwurm pair, three-writer, shadow, power-cut, metadata-corruption, and
  dishonest-storage proof named by tracked Markdown evidence;
- retains the newest undocumented private proof root and compact export per class, plus the
  newest undocumented `operator-tor` root, by default;
- recognizes only immediate `iotox-device-repair.*` directories for one-off offline guest-disk
  postmortems and never treats other `.sandwurm/` children as cleanup candidates;
- requires sandbox temporary entries to be at least 24 hours old;
- refuses symlinks, paths outside the repository, mounted trees, and process cwd/root/open-descriptor
  references; and
- computes allocated bytes rather than misleading sparse-file apparent sizes.

Apply the reviewed default scope as the repository owner:

```sh
python3 tools/clean-workspace.py --apply
```

The cleaner first tries ordinary owner removal. If a fully validated exact candidate contains
root-owned Sandwurm files, it invokes only the host's absolute `rm` through passwordless `sudo` for
that candidate. Confinement, name, mount, symlink, and open-reference checks all run before this
fallback; the Python auditor itself does not need to run as root.

Build products are opt-in because deleting them trades disk for rebuild time:

```sh
python3 tools/clean-workspace.py --scope build --apply
```

Proof evidence should be documented before later runs can age it out. Private proof roots remain
owner-only even when retained; the small digest-bound Markdown evidence is the durable project
record. Interrupted benchmarks cannot run their in-process destructors, so the age-bounded temp lane
is the backstop for their fixtures.

Operator-Tor success receipts contain all retained claim material and no live identity. After a
failed-route diagnosis, audit or remove only that dedicated class with:

```sh
python3 tools/clean-workspace.py --scope operator-tor --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py --scope operator-tor --keep-unreferenced-proofs 0 --apply
```

Accepted pair roots should first be reduced to their exact verified evidence surface:

```sh
./tools/export-sandwurm-pair.py .sandwurm/lab/pairs/PAIR_ID
python3 tools/verify-sandwurm-pair.py .sandwurm/exports/pairs/PAIR_ID \
  --route ROUTE --scenario SCENARIO

# Qualification-only mixed-provider cells use their narrower proof schema.
./tools/export-sandwurm-provider-rolling.py .sandwurm/lab/pairs/PAIR_ID
python3 tools/verify-sandwurm-provider-rolling.py \
  .sandwurm/exports/pairs/PAIR_ID --route ROUTE

# Single-guest lifecycle and incumbent-shadow proofs have dedicated exports.
./tools/iotox-sandwurm-lab.sh export-three-writer \
  .sandwurm/lab/three-writer/RUN_ID
./tools/iotox-sandwurm-lab.sh export-sync-shadow \
  .sandwurm/lab/sync-shadow/RUN_ID
```

The exporter has no deletion option. Successful export is therefore reversible until the original
private proof is separately reviewed and selected by the cleanup policy. The sync-shadow compact
surface omits the guest disk, runtime state, Tox keys, Resilio secrets, and synchronized content;
its five independently verified receipt/launch files are capped at 2 MiB total.

After the accepted compact sync-shadow ID is cited in tracked documentation, isolate that class for
an exact dry-run/apply review without touching pair or three-writer proofs:

```sh
python3 tools/clean-workspace.py --scope sync-shadow --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py --scope sync-shadow --keep-unreferenced-proofs 0 --apply
```

Whole-VMM sync power-cut proofs follow the same verify/export/verify rule. Ten exact raw parents are
allowlisted: `sync-power-cut`, `sync-power-cut-post-exchange`,
`sync-power-cut-receive-staging`, `sync-power-cut-cas-install`,
`sync-power-cut-manifest-install`, `sync-power-cut-branch-record-install`, and
`sync-power-cut-branch-pointer-update`, plus
`sync-power-cut-manifest-directory-fsync`,
`sync-power-cut-branch-record-directory-fsync`, and
`sync-power-cut-branch-pointer-directory-fsync`. No other similarly named lab root is eligible. All profiles
share one compact export directory, and a full path cited by tracked Markdown protects that exact
compact proof. Audit this class alone with:

```sh
python3 tools/clean-workspace.py --scope sync-power-cut --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py --scope sync-power-cut --keep-unreferenced-proofs 0 --apply
```

The one-boot signed-metadata corruption gate is a separate proof class. Only
`.sandwurm/lab/sync-metadata-corruption/run.*` and
`.sandwurm/exports/sync-metadata-corruption/run.*` are eligible; a similarly
named directory anywhere else is not. Its compact evidence contains the five
strictly verified chain, launch, VM, and guest-receipt files plus a digest
manifest, with source evidence capped at 2 MiB. The exporter never removes the
raw guest disk or state.

```sh
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption \
  .sandwurm/lab/sync-metadata-corruption/RUN_ID
./tools/iotox-sandwurm-lab.sh export-sync-metadata-corruption \
  .sandwurm/lab/sync-metadata-corruption/RUN_ID
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption \
  .sandwurm/exports/sync-metadata-corruption/RUN_ID

python3 tools/clean-workspace.py \
  --scope sync-metadata-corruption --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py \
  --scope sync-metadata-corruption --keep-unreferenced-proofs 0 --apply
```

The projection-descriptor/remount gate is another separate one-boot proof
class. Only `.sandwurm/lab/sync-projection-descriptor/run.*` and
`.sandwurm/exports/sync-projection-descriptor/run.*` are eligible. Its compact
evidence contains the five strictly verified chain, launch, VM, and
projection-descriptor receipt files plus a digest manifest, with source
evidence capped at 2 MiB.

```sh
./tools/iotox-sandwurm-lab.sh verify-sync-projection-descriptor \
  .sandwurm/lab/sync-projection-descriptor/RUN_ID
./tools/iotox-sandwurm-lab.sh export-sync-projection-descriptor \
  .sandwurm/lab/sync-projection-descriptor/RUN_ID
./tools/iotox-sandwurm-lab.sh verify-sync-projection-descriptor \
  .sandwurm/exports/sync-projection-descriptor/RUN_ID

python3 tools/clean-workspace.py \
  --scope sync-projection-descriptor --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py \
  --scope sync-projection-descriptor --keep-unreferenced-proofs 0 --apply
```

The dishonest-storage drill is a compact same-host block-layer proof class.
Successful default runs remove their raw
`.sandwurm/lab/sync-dishonest-storage/run.*` root after unmounting, removing
the device-mapper snapshot, and detaching loop devices. Retained compact
receipts live under `.sandwurm/exports/sync-dishonest-storage/run.*` and are
eligible only when undocumented.

```sh
tools/iotox-repo.sh sync-dishonest-storage-drill
python3 tools/verify-sync-dishonest-storage-drill.py \
  .sandwurm/exports/sync-dishonest-storage/RUN_ID

tools/iotox-repo.sh sync-dishonest-storage-matrix
python3 tools/verify-sync-dishonest-storage-matrix.py \
  .sandwurm/exports/sync-dishonest-storage/RUN_ID

tools/iotox-repo.sh sync-log-writes-prefix-replay
python3 tools/verify-sync-log-writes-prefix-replay.py \
  .sandwurm/exports/sync-log-writes-prefix/RUN_ID

tools/iotox-repo.sh sync-production-prefix-replay
python3 tools/verify-sync-production-prefix-replay.py \
  .sandwurm/exports/sync-production-prefix/RUN_ID

python3 tools/clean-workspace.py \
  --scope sync-dishonest-storage --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py \
  --scope sync-dishonest-storage --keep-unreferenced-proofs 0 --apply
python3 tools/clean-workspace.py \
  --scope sync-log-writes-prefix --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py \
  --scope sync-log-writes-prefix --keep-unreferenced-proofs 0 --apply
python3 tools/clean-workspace.py \
  --scope sync-production-prefix --keep-unreferenced-proofs 0
python3 tools/clean-workspace.py \
  --scope sync-production-prefix --keep-unreferenced-proofs 0 --apply
```

The newest undocumented raw and compact roots remain by default, exact full
paths in tracked Markdown protect accepted proofs, and a raw root with a live
process reference is omitted. Follow the same verify, export, reverify, cite,
dry-run, apply order used for the power-cut class.

Live raw Sandwurm roots with any process cwd, process root, or open descriptor beneath them are
omitted even from the dry-run list. Apply mode repeats the live-reference and mount checks for the
complete candidate set before deleting its first entry, closing the race between enumeration and
removal. Dry-run size calculation tolerates a candidate that disappears between enumeration and
`du`; apply mode still refuses any candidate that no longer exists at validation time.

Compact exports are also immutable generated evidence, not source. Once an accepted proof path or
pair ID is named anywhere in tracked Markdown, the Sandwurm scope protects that compact directory.
Undocumented superseded compacts remain candidates under the same retention count; use zero
retention only after reviewing the exact dry-run list.

The order is therefore strict: verify raw, export, verify compact, cite the exact pair ID in an
already tracked Markdown file, and only then run a zero-retention cleanup. A newly created untracked
evidence document does not yet protect its ID because the cleaner deliberately uses `git grep` over
tracked Markdown. Update a tracked roadmap/testing record or commit the new evidence first.

## Routine policy

Run the default dry audit after a VM or benchmark campaign and before making a datacube. Apply it
when the candidate list contains no live investigation. Run the build scope after a milestone or
before a snapshot. Do not run global Git clean, recursive deletion at the repository root, or Nix
store collection as a substitute for this allowlisted policy.

## 2026-09-17 accepted 24-hour soak compaction

The fresh 24-hour three-writer soak run ID `run.9nqvO8B2` was reverified, compact-exported, and
reverified again as `.sandwurm/exports/three-writer/run.9nqvO8B2`. The compact proof is content-free,
contains five evidence files plus its manifest, and occupies about 108 KiB; the private raw source
was about 13 GiB. Tracked evidence should cite the compact proof path and the run ID, not the raw lab
path. After reviewing the dry-run list, the raw source can be reclaimed with:

```sh
python3 tools/clean-workspace.py --scope sandwurm \
  --keep-unreferenced-proofs 0 \
  --keep-unreferenced-three-writer-proofs 0
python3 tools/clean-workspace.py --scope sandwurm \
  --keep-unreferenced-proofs 0 \
  --keep-unreferenced-three-writer-proofs 0 \
  --apply
```

## 2026-09-23 precious-data-era 24-hour soak compaction

The fresh signoff-era 24-hour three-writer soak run ID `run.2nPKtCoX` was
reverified, compact-exported, and reverified again as
`.sandwurm/exports/three-writer/run.2nPKtCoX`. The compact proof is
content-free, contains five evidence files plus its manifest, and occupies
96,980 bytes. Tracked evidence should cite the compact proof path, the native
stable receipt generated by
`tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json`
(SHA-256 `6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0`),
the raw guest sync receipt SHA-256
`687b4ace878465ba733399a722d009a8d99afc616fe244ad7f2721443263356b`, and compact
manifest SHA-256
`e7e42344883152e5dde264c3b6fab0c0df5e601a56334e2c2e344754d30318f9`, not the
raw lab path.

## 2026-09-17 loopback recovery-custody receipts

`tools/run-sync-loopback-custody-drill.py` removes its temporary loop images and raw
`.sandwurm/lab/sync-recovery-custody-loopback/run.*` root by default after unmounting and detaching
the loop devices. Its retained content-free receipt lives under
`.sandwurm/exports/sync-recovery-custody/run.*`. The cleaner understands both classes: tracked
Markdown references to compact receipts are protected, while failed or deliberately retained raw
roots and undocumented compact receipts can be audited with:

```sh
python3 tools/clean-workspace.py --scope sync-recovery-custody --keep-unreferenced-proofs 0
```

As of ADR 0353, the cleaner also treats
`.sandwurm/lab/three-writer-near-ceiling-cap-{1,4,8,16,32,64}/run.*` as bounded three-writer raw
proof roots. They follow the same ritual as ordinary three-writer raw roots: verify the raw receipt,
export the compact proof, verify the compact proof, cite or commit the compact proof ID in Markdown,
then run the Sandwurm cleanup scope. The cleaner's self-test covers this cap-specific class.

## 2026-09-09 busy-republish cleanup

The rev0051 cap-4/cap-8/cap-16 busy-republish campaign first exported and independently verified
each accepted compact proof, then committed the evidence references. A reviewed Sandwurm-scope dry
run selected only unreferenced raw proof roots: five three-writer near-ceiling roots and six
superseded projection-descriptor raw roots. Applying that exact scope removed 11 ignored roots and
reclaimed 31.0 GiB. A follow-up dry run selected zero candidates. The retained compact proofs remain
under `.sandwurm/exports/three-writer/`.

## 2026-09-08 object-pipeline power-cut cleanup

The two accepted rev0048 object-pipeline campaigns were exported and independently verified before
cleanup. Raw receive-staging run `1e05ayp9` occupied 3.1 GiB, raw CAS-install run `jtiyspp_` occupied
3.1 GiB, and rejected diagnostic run `s_2l5lii` occupied 1.5 GiB. All three private roots were moved
recoverably to host Trash; the accepted compact proofs remain at 160 KiB and 216 KiB allocated and
pass strict v4 verification after the move. `.sandwurm` returned to 311 MiB.

The cleaner now owns future repetition of this ritual through an exact `sync-power-cut` scope. Its
self-test creates and selects an undocumented raw and compact fixture, while a zero-retention dry run
selects none of the four compact proofs cited by tracked evidence. It never broad-matches arbitrary
`.sandwurm/lab/sync-power-cut-*` directories.

## 2026-09-03 cap-4 sync cleanup

The cap-4 tree-v2 lane campaign left the repository at approximately 25 GiB, almost entirely in
ignored state. Accepted raw three-writer Sandwurm roots were first compacted and reverified; rejected
near-ceiling roots retained only content-free console/direct diagnostics. The raw proof roots and
thirteen old private pair roots were then moved out of the workspace. `.sandwurm/` dropped to about
310 MiB, consisting primarily of compact exports.

The remaining major leak was not active evidence but nested sandbox Trash:
`.sandworm/home/.local/share/Trash/files` held 17 GiB of old generated `run.*`, `pair.*`,
`gcc-coverage*`, `tmp.*`, and `rev0045` payloads. That exact nested Trash directory was moved to the
host Trash as `iotox-sandworm-nested-trash-20260903`, and an empty sandbox Trash skeleton was
recreated. A reviewed `--scope all --apply` then removed 2.1 GiB of stale sandbox temp fixtures and
non-current reproducible build lanes while retaining the current GCC debug build. The working
directory dropped to about 6.6 GiB. The cleanup tool now audits the same class under the default temp
scope so future nested-trash growth is visible before it reaches datacube or snapshot size.

## Founding cleanup result

The 2026-08-20 audit measured a 439 GiB working directory but only 90.8 MiB of tracked files. The
largest leak was 405 GiB under `.sandworm/home/tmp/`: interrupted toxsync benchmarks alone retained
approximately 405 GiB across three workspaces. Sandwurm runs occupied another 27 GiB and accumulated
build trees occupied 3.7 GiB.

The first guarded cleanup reclaimed approximately 425 GiB. The three accepted pair roots were then
exported from 2.3 GiB each to independently verified 96 KiB evidence sets before their private source
roots were removed. The older independent no-network boot roots remain because their historical
evidence cites them, although the stricter current smoke verifier now rejects their pre-source-link
package classification; cleanup did not create that incompatibility.

After compaction the complete working directory measures approximately 6.6 GiB. The remaining large
local classes are the two historical smoke roots, active sandbox state, DR0Pbox, and the current GCC
debug build; tracked source remains approximately 91 MiB.

## 2026-08-24 follow-up cleanup

Eleven later synchronization pair roots had accumulated another 25.0 GiB allocated. Eight accepted
cells already had strict compact exports; all eight were independently reverified against their
route/scenario contracts. The remaining three were rejected range-retry development runs whose
findings support no accepted claim. Evidence documents were changed to name compact proof as the
durable surface, and the older repair verifier was made compatible only with its exact pre-GC binary
digest while newer repair binaries still require every GC field.

The cleaner's `--scope sandwurm --keep-unreferenced-proofs 0` dry-run selected exactly those eleven
pair roots. Applying that exact set reclaimed 25.0 GiB and reduced the allocated workspace from about
34 GiB to 8.4 GiB. A second audit reported zero Sandwurm candidates. The deleted private guest disks
are recoverable only by rerunning their fixtures; all accepted compact proofs remain present.

The later seeded partial-loss campaign created two more 2.3 GiB private pair roots. Direct UDP and
forced TCP were each exported to an independently verified 152 KiB exact evidence set before an
audited two-candidate apply reclaimed another 4.5 GiB. Both compact proofs passed strict verification
again after deletion, the follow-up audit reported zero candidates, and the workspace returned to
about 8.4 GiB.

## 2026-08-25 route-scheduler cleanup

The Gate 3/4 route-scheduler campaign accumulated sixteen raw pair roots: accepted route-loss and
fixed/adaptive balance sources, counterbalance retries, and superseded development observations.
Every accepted balance cell was exported to a 229,376-byte compact proof and strictly verified in
both raw and compact form. The cleaner's exact Sandwurm audit with zero undocumented retention then
selected only those sixteen private roots and reclaimed 34.2 GiB. Compact proofs, the immutable test
identity cache, DR0Pbox, build trees, and tracked source were outside the deletion set.

## 2026-08-25 route-cancellation cleanup

The bounded route-cancellation campaign created four raw pair roots: two accepted direct-UDP and
forced-TCP cells and two rejected development observations. The accepted roots were reduced to
229,376-byte compact proofs and strictly replayed before cleanup. An audited zero-retention
Sandwurm pass removed all four raw roots and reclaimed 9.2 GiB; the same checkpoint removed 5.7 GiB
of reproducible build lanes and stale sandbox temporaries, for 14.9 GiB reclaimed in total. The
cleaner was extended to include strictly named top-level `build-*` trees, so one-off qualification
builds now follow the same dry-run/apply boundary as the canonical build lanes. Both compact proofs
passed strict verification again after deletion.

## 2026-08-25 route-population cleanup

The eight-job scheduler-population campaign created thirteen raw pair roots while the gate was being
made sampling-safe: two accepted direct-UDP/forced-TCP cells and eleven superseded development
observations. Both accepted roots were first reduced to 249,856-byte compact proofs and independently
verified in raw and compact form. The exact zero-retention Sandwurm dry run selected only those
thirteen private roots; applying it reclaimed 29.8 GiB. A second audit reported zero candidates, and
both compact proofs passed strict route-population verification again after raw-disk deletion.

## 2026-08-25 concurrent-cancellation cleanup

After direct UDP `pair.2laq038h` and forced TCP `pair.rlpuyjth` passed the bounded concurrent-route
cancellation gate, each was exported and strictly reverified as a 245,760-byte compact proof. Two
earlier direct-UDP 1 MiB/job diagnostic roots (`pair.wvg7sbs2` and `pair.x8lsgq_1`) had completed all
cancellation/survivor invariants but failed the subsequent protected Ratox `OPENED` deadline; their
content-free aggregate findings are retained in the evidence/ADR, not as accepted proofs.

An exact `--scope sandwurm --keep-unreferenced-proofs 0` audit named only those four raw roots. The
reviewed apply deleted four roots and reclaimed 9.1 GiB allocated. A second audit reported zero
candidates. Both accepted compact proofs passed strict verification before deletion; no identity
cache, unrelated Sandwurm state, or compact export was removed.

## 2026-08-25 loss-before-cancellation cleanup

Direct UDP `pair._0jwjfe6` and forced TCP `pair.o0ozmdw1` passed strict raw verification for the
loss→reassignment→replacement-progress→cancellation gate. Each was exported and independently
reverified as a 241,664-byte compact proof before cleanup.

An exact `--scope sandwurm --keep-unreferenced-proofs 0` audit named only those two private raw roots,
2.3 GiB each. The reviewed apply deleted both and reclaimed 4.5 GiB allocated. A second audit
reported zero candidates, and both compact proofs passed strict route-loss-cancel verification again
after raw-disk deletion.

## 2026-08-25 route-readiness-order cleanup

The exact readiness-order campaign created nine raw pair roots while separating simultaneous primary
replacement, construction-relative delay, and intermittent forced-TCP control startup from the
auxiliary-order result. Direct UDP `pair.nyiqwm8t` and forced TCP `pair.mdacri5e` passed the corrected
post-authentication hold on one exact binary. Each accepted root was verified raw, exported to a
241,664-byte compact proof, and independently replayed.

Guarded zero-retention Sandwurm audits selected only the nine private raw roots across the campaign.
The reviewed applies reclaimed approximately 20.5 GiB allocated. A final audit reported zero
Sandwurm candidates, and both accepted compact proofs passed strict startup-order verification after
their guest disks were deleted. Reusable identities, DR0Pbox, build trees, unrelated proofs, and
compact exports remained outside the deletion set.

## 2026-08-26 cancellation-before-loss cleanup

The opposite deterministic fault-order campaign first produced two otherwise accepted roots before
the subscriber snapshot exposed its existing settled-cleanup truth. They were compacted and their
two 2.3 GiB raw roots were removed by a reviewed apply, reclaiming 4.5 GiB. The cleanup-settled edge
was then made explicit, its failed-cleanup regression was added, and the complete carrier matrix was
rerun rather than promoting the earlier observations.

Final accepted direct-UDP `pair.yv4txv1r` and forced-TCP `pair.m2396itk` each passed strict raw
verification, exported to a 241,664-byte compact proof, and passed strict compact replay. A second
guarded zero-retention audit selected exactly those two private raw roots at 2.3 GiB each. The
reviewed apply deleted both and reclaimed another 4.6 GiB, for 9.1 GiB across the campaign. Reusable
immutable identities, compact proofs, DR0Pbox, build trees, and unrelated evidence remained outside
the deletion set. A final audit reported zero candidates, and both final compact proofs passed
strict cancel-before-loss verification again after raw-disk deletion.

## 2026-08-26 cancellation/route-loss race cleanup

The first direct-UDP shared-arm attempt exposed the typed cleanup edge: local cancellation had
terminally fenced the pull while exact-worker disappearance made transport cleanup unavailable. Its
rejected private root `pair.w2w5sgxl` was selected alone by a reviewed zero-retention dry run and
deleted, reclaiming 2.3 GiB allocated. The harness then required the typed status and one exact
nonrepeating cleanup retry rather than weakening cancellation truth.

Final direct UDP `pair.h6kg4fcr` and forced TCP `pair.z9egqd57` passed strict raw verification,
exported to 241,664-byte compact proofs, and passed strict compact replay. A reviewed
`--scope sandwurm --keep-unreferenced-proofs 0` dry run selected exactly those two 2.3 GiB private
raw roots. Apply reclaimed 4.5 GiB allocated, bringing the race campaign total to 6.8 GiB. Reusable
identity baselines, compact proofs, DR0Pbox, build trees, and unrelated Sandwurm state remained out
of scope. A final audit reported zero candidates; both compact proofs were replayed again afterward.

## 2026-08-26 loss-first shared-arm cleanup

Direct UDP `pair.5gvh__p1` and forced TCP `pair.rxb2dsge` passed strict raw verification for the
required loss-first companion, exported to 241,664-byte compact proofs, and passed strict compact
replay. A reviewed `--scope sandwurm --keep-unreferenced-proofs 0` dry run selected exactly those
two private 2.3 GiB raw roots. Apply deleted both and reclaimed 4.5 GiB allocated. Reusable identity
baselines, the four cross-outcome compact proofs, DR0Pbox, build trees, and unrelated Sandwurm state
remained outside the deletion set. A final audit reported zero candidates, and both new compact
proofs replayed again after their guest disks were removed.

## 2026-08-26 route-population-loss cleanup

The four-affected-job campaign produced accepted direct-UDP `pair.j19_uhjj` and forced-TCP
`pair.rfnsjtqb` observations plus superseded raw attempts that selected full-work route admission,
bounded transient publisher-unavailability retry, and the auxiliary event/carrier thread split.
Both accepted roots passed strict raw verification, were exported to 245,760-byte compact proofs,
and passed strict compact replay. Reviewed zero-retention Sandwurm cleanup passes removed every raw
pair root from the campaign, including rejected observations, while preserving the compact proofs
and their content-free failure interpretation. A final audit reports no pair-root candidate; the
two older tracked single-guest smoke roots remain intentionally protected as documented above.

## 2026-08-26 admission-during-route-loss cleanup

Direct UDP `pair.v3qc2kld` and forced TCP `pair.djhqe3we` passed strict raw verification for new
work admission through the sole surviving carrier, exported to 245,760-byte compact proofs, and
passed strict compact replay. Two rejected direct-UDP roots retained the content-free interpretation
of the clean-shutdown liveness defect and invalid zero-delay fixture attempt in ADR 0181/evidence.
A reviewed zero-retention dry run selected exactly those four 2.3 GiB private roots. Apply deleted
all four and reclaimed 9.1 GiB allocated. Reusable identity baselines, compact proofs, DR0Pbox,
build trees, and unrelated Sandwurm state remained outside the deletion set. A final audit reported
zero candidates, and both accepted compact proofs replayed again after raw-disk deletion. A separate
reviewed build-scope pass then removed only the reproducible Clang sanitizer and GCC ThreadSanitizer
trees after their complete passes, reclaiming another 1.3 GiB while retaining the current debug
tree.

## 2026-08-26 degraded-startup-admission cleanup

Direct UDP `pair.46f6td4j` and forced TCP `pair.2gvkqs6b` passed strict raw verification for two
large jobs admitted through one ready route after a clean same-state Agent restart. Each was
exported to a 249,856-byte compact proof and independently replayed. Rejected direct-UDP
`pair.gfm0c268` selected the fixture's one-indexed route-worker correction; `pair.namvo3gh` never
launched a guest because the manually interrupted prior runner still owned the bootstrap port.

A reviewed zero-retention dry run selected exactly those four raw roots and no other state. Apply
deleted all four and reclaimed 7.2 GiB allocated. Reusable identity baselines, compact proofs,
DR0Pbox, build trees, and unrelated Sandwurm state remained outside the deletion set. A final audit
reported zero candidates, and both compact startup-admission proofs passed strict replay again after
their private guest disks were removed.

## 2026-08-26 signed-update lifecycle cleanup

Exact-final direct-UDP `pair.7vmazf5b` and forced-TCP `pair.wrrfloqd` passed strict raw
verification for the default-off signed-update construction lifecycle. Each exported to a
147,456-byte compact proof containing neither secrets nor guest disks and passed strict compact
replay. A reviewed `--scope sandwurm --keep-unreferenced-proofs 0` dry run selected exactly those
two private 2.3 GiB raw roots. Apply deleted both and reclaimed 4.6 GiB allocated while preserving
the compact proofs, reusable identities, DR0Pbox, build trees, and unrelated evidence. A final
audit reported zero candidates, and both compact proofs passed strict signed-update replay again
after raw-disk deletion.

## 2026-08-27 operator-Tor route cleanup

The accepted actual-Tor/public-relay gate removed its own successful private run root after writing
the canonical receipt. Three failed diagnostic roots remained: one proved `SafeSocks 1` rejects the
numeric c-toxcore request shape, one public port-443 relay set did not reach Tox TCP inside 360
seconds, and one early control-parser attempt stopped after reaching Tox TCP. Each held only
ephemeral Tor cache/state, an ephemeral IoTox identity, and private diagnostic logs.

The new dedicated cleanup scope produced a reviewed exact three-root dry run totaling 121.0 MiB.
Apply removed only those roots; a repeated zero-retention audit returned zero candidates and the
committed receipt continued to pass its independent verifier. This class is deliberately separate
from Sandwurm pair retention because successful operator-Tor evidence has no private VM proof root.

## 2026-08-27 mixed private-route cleanup

The accepted native/generic-SOCKS mixed-context gate exported `pair.z948jeii` from a 2.3 GiB private
root to a 3,727,360-byte secret-free proof and passed strict compact replay. Three prior roots held
only the release-build failure, the diagnosed early-proof race, and the first successful guest run
whose outer/inner packet-field interpretation prevented host manifest acceptance. The race
postmortem also retained a 1.1 GiB reflinked, fsck-repaired copy of one uncleanly stopped guest disk.

The cleaner gained an exact immediate-child `iotox-device-repair.*` class plus offline self-test. A
reviewed zero-retention Sandwurm dry run selected exactly those four pair roots and the one repair
workspace, totaling 8.0 GiB. Apply removed that exact set. The accepted compact proof, reusable
identity baselines, DR0Pbox, build trees, and unrelated evidence were outside the candidate set; the
raw disks and failed roots are recoverable only from machine snapshots or by rerunning the fixture.

## 2026-08-27 two-peer actual-Tor cleanup

The accepted actual-Tor auxiliary-route gate exported `pair.2mycvy9n` from a 2.4 GiB private root
to a 3,764,224-byte secret-free compact proof and passed strict raw and compact verification. The
compact allowlist retains both TAP captures, authenticated Tor STREAM/CIRC events, bootstrap and
circuit-status projections, normalized configuration commitments, guest receipts, and source-linked
VMM chains. It omits guest disks, injected identities, runtime state, the bootstrap secret, and both
Tor data directories.

A reviewed zero-retention Sandwurm dry run selected exactly the one private raw root. Apply reclaimed
2.4 GiB; a repeated audit returned zero candidates and the compact proof still passed independently.
The removed VM disks and Tor cache/state are recoverable only from machine snapshots or by rerunning
the fixture.

## 2026-08-27 actual-Tor payload cleanup

The accepted payload-attribution gate exported `pair.lzsyitvy` from a 2.4 GiB private root to a
16,257,024-byte secret-free compact proof and passed strict raw and compact verification. Its
allowlist retains both TAP captures, authenticated Tor STREAM/CIRC evidence, circuit/configuration
commitments, exact carrier and pull-admission receipts, signed-tree agreement, and source-linked VMM
chains. It omits guest disks, injected identities, runtime state, the bootstrap secret, and Tor data
directories.

Two earlier raw roots remained deliberately until qualification: `pair.2ick1mfx` contained a
successful guest receipt but a verifier-rejected aggregate produced by the diagnosed host-index bug;
`pair.wfdk776_` contained the observable pre-job pull-admission failure and its copy-on-write,
journal-replayed diagnostic disk clone. A reviewed zero-retention dry run selected exactly those two
roots and the accepted raw root, totaling 8.3 GiB. Apply deleted that exact set. A repeated audit
returned zero candidates, and `pair.lzsyitvy` passed strict compact replay afterward. The removed
material is recoverable only from machine snapshots or by rerunning the documented gate.

## 2026-08-27 actual-Tor process-loss and compact-export cleanup

The accepted external process-loss gate exported `pair.iompvehf` from a 2.47 GiB private root to a
43,450,368-byte secret-free compact proof. Both roots independently passed strict verification; the
compact retains the exact guest receipts, three authenticated Tor phases, process/control identity
changes, process-loss record, both TAP captures, source-linked VMM chains, and signed-tree
commitments while omitting guest disks, injected identities, runtime state, the bootstrap secret,
and Tor data directories.

A reviewed zero-retention Sandwurm dry run selected exactly the accepted private root and one
superseded private process-loss run, reclaiming 4.9 GiB. The compact proof then passed strict replay
without the private disks. The cleaner was extended to treat only exact immediate
`.sandwurm/exports/pairs/pair.*` directories as compact-proof candidates while protecting every
pair ID cited by tracked Markdown. Its self-test passed, and a second reviewed dry run selected 28
undocumented superseded compact exports totaling 39.0 MiB, including the earlier process-loss proof
whose receipt predated the independently serialized zero-worker-restart relation. Apply removed
that exact set. A final zero-retention audit reported zero candidates and `pair.iompvehf` passed
strict compact replay again. Removed private and compact material is recoverable only from machine
snapshots or by rerunning the documented gates.

## 2026-08-27 actual-Tor Ratox process-loss cleanup

The accepted terminal process-loss gate exported `pair.2waqdpgk` from a 2,569,691,136-byte private
root to a 1,728,512-byte secret-free compact proof. Both forms independently passed strict
verification. The compact allowlist retains the exact guest receipts, frozen terminal lifecycle,
detached host-PTY state, three authenticated Tor phases, distinct pre-loss/recovered process and
control identities, both TAP captures, and source-linked VMM chains. It omits guest disks, injected
identities, runtime state, the bootstrap secret, and Tor data directories.

A reviewed zero-retention Sandwurm dry run selected exactly that one accepted private root and no
other state. Apply reclaimed 2.4 GiB allocated. A repeated audit returned zero candidates and the
compact proof passed strict replay after private-disk deletion. The removed disks and private Tor
cache/state are recoverable only from machine snapshots or by rerunning the documented gate.

## 2026-09-08 branch-publication power-cut cleanup

The repaired manifest, immutable-record, and mutable-pointer pre-rename campaigns exported accepted
content-free compact proofs `run.l2gckna4`, `run.c9xhj26a`, and `run._cphu30p`. All three strict
compact replays passed before cleanup. Four rejected roots retained the cold-build budget, unfiltered
rename-delay, tracer/tracee stop-order, and orphan-record recovery findings until those findings were
implemented and documented. Superseded pre-fix compact proofs were no longer evidence for the
repaired binary.

A reviewed dry run selected exactly eleven raw or superseded roots totaling 22.8 GiB. No target held
a nested mount or live campaign VMM. The exact roots were moved recoverably to the desktop trash;
Trash was not emptied. `.sandwurm` fell from 24 GiB to 312 MiB. A repeated zero-retention audit
reported no candidate, and all three accepted compact proofs passed strict replay afterward.

## 2026-09-08 directory-durability power-cut cleanup

The repaired manifest-, immutable-record-, and mutable-pointer-directory-fsync campaigns exported
accepted content-free compact proofs `run.dbgtc3ip`, `run.jznfzx52`, and `run.ia70ljmf`. All three
passed strict compact replay. The pre-optimization record root retained the exact 134-barrier
diagnosis until the product fix and successful repetition were documented; the earlier manifest run
and compact export were superseded when that fix changed the binary.

After the accepted paths were protected by tracked evidence, a reviewed zero-retention dry run
selected exactly six targets totaling 13.8 GiB: three accepted raw VM roots, the rejected record
root, the superseded manifest raw root, and its superseded compact proof. No target held a nested
mount or live campaign VMM. Those exact paths were moved recoverably to desktop Trash; Trash was not
emptied. The repeated audit reported zero candidates, `.sandwurm` measured 312 MiB, and all three v6
compact proofs passed strict replay afterward.

## 2026-08-31 content-lane counterbalance cleanup

The finalized order-balanced gate exported direct-UDP `pair.t6b6exf1`/`pair.ku2fxml0` and
forced-TCP `pair.70p2plez`/`pair.o_6q_m1n` to 192,512-byte allocated secret-free compact proofs.
Every raw root and compact root passed the strict pair verifier; the four compact roots then passed
the independent counterbalance analyzer and reproduced the canonical report byte for byte.

One rejected forced-TCP setup root retained the redundant-initial-publication CLI-status-3 failure
until the harness correction was documented. Two earlier UDP roots and their preliminary compact
exports were superseded by current-code repetitions. A reviewed zero-retention dry run selected
exactly seven raw pair roots plus those two superseded compact roots, totaling 17.4 GiB allocated.
Apply removed that exact set while preserving all four ADR 0266 compact roots. The canonical report,
all rev0045 checksums, and strict compact replay passed again after cleanup. Removed guest disks,
injected identities, bootstrap secrets, and rejected runtime state are recoverable only from machine
snapshots or by rerunning the documented gates.

## 2026-08-30 multi-source content cleanup

The accepted direct-UDP three-agent gate exported `pair.u80_yp7r` from a 2.3 GiB private root to a
163,840-byte secret-free compact proof. Both forms passed strict verification before cleanup. Four
complete forced-TCP roots retained the one-relay, dual-bootstrap, split-bootstrap, and common-
bootstrap/two-relay falsifications long enough to map their exact primary/secondary session
assertions into ADR 0255 and the evidence report. Three aborted or superseded calibration roots
supported no additional claim.

A reviewed zero-retention dry run selected exactly those eight raw roots and no compact proof,
totaling 13.9 GiB allocated. Apply removed that exact set. A repeated audit returned zero candidates,
and `pair.u80_yp7r` passed strict compact replay after deletion. The removed guest disks, injected
identities, rejected runtime state, and bootstrap secrets are recoverable only from machine snapshots
or by rerunning the documented gates.

## 2026-08-30 selected content-source loss cleanup

The accepted direct-UDP destructive gate exported `pair.xujufman` from a 2.4 GiB private raw root to
a 184,320-byte allocated secret-free compact proof. Raw and compact forms independently passed
strict verification before cleanup. Nine failed or superseded calibration roots captured the
foreign-writer cold-start refusal, restart-readiness fixes, and the source-add/cached-root race long
enough to turn each result into product code, ADR 0256, and the evidence report.

A reviewed zero-retention dry run selected exactly those nine rejected roots plus the accepted
private root and no compact proof, totaling 23.0 GiB allocated. Apply removed that exact set. A
repeated audit returned zero candidates, and `pair.xujufman` passed strict compact replay after raw-
disk deletion. No IoTox/Sandwurm loop devices or mounts remained. The removed guest disks, injected
identities, rejected runtime state, and bootstrap secrets are recoverable only from machine snapshots
or by rerunning the documented gate.

## 2026-08-29 range-restart cleanup

The accepted daemon-death range-restart gate exported direct-UDP `pair.xg41pthc` and forced-TCP
`pair.00992erw` to secret-free compact proofs allocating 188,416 bytes each. Raw and compact forms
independently passed strict verification before cleanup. The accepted IDs were then recorded in
tracked Markdown so the cleaner's repository-derived protection set could preserve them.

A reviewed zero-retention Sandwurm dry run selected exactly the two accepted private roots, totaling
4.7 GiB allocated, and no compact proof or unrelated state. Apply removed that exact set. A repeated
audit returned zero candidates, and both compact proofs passed strict replay after private-disk
deletion. The removed guest disks and injected runtime state are recoverable only from machine
snapshots or by rerunning the documented gate.

## 2026-08-28 actual-Tor Ratox circuit-churn cleanup

The accepted continuous-process circuit-churn gate exported `pair.k8o54n2v` from a
2,583,646,208-byte private root to a 3,129,344-byte secret-free compact proof. Both forms
independently passed strict verification. The compact allowlist retains the exact guest receipts,
120-sample terminal and heartbeat captures, controller lifecycle, authenticated before/after Tor
inventories for both requested circuit closes, raw Tor events, both TAP captures, resource
intervals, and source-linked VMM chains. It omits guest disks, injected identities, runtime state,
the bootstrap secret, and Tor data directories.

A reviewed zero-retention Sandwurm dry run selected exactly that one accepted private root and no
other state. Apply reclaimed 2.4 GiB allocated. A repeated audit returned zero candidates and the
compact proof passed strict replay after private-disk deletion. Earlier rejected circuit-churn roots
were removed separately only after each failed contract had been diagnosed and recorded in ADR
0207. The removed disks and private Tor cache/state are recoverable only from machine snapshots or
by rerunning the documented gate.

## 2026-08-30 historical VM-proof cleanup

The original two standalone Sandwurm bootstrap runs had been retained since 2026-08-20 even though
later source-linked pair gates superseded their substrate-only claim. The first strict Tox/Tor pair
also still retained its 2.3 GiB private source after its 704,512-byte compact export had passed. The
compact `pair.zyy913jf` proof passed current strict replay before cleanup.

The tracked evidence notes were changed from live private-root references to historical run IDs and
generic reproduction commands. A reviewed zero-retention dry run then selected exactly the two
standalone roots and the Tox/Tor private pair root, totaling 4.5 GiB allocated. Apply removed those
three roots. The same bounded cleanup removed the reproducible 517.1 MiB Clang build tree and 233
allowlisted stale test temporaries totaling 448 KiB; the GCC build remained. A repeated audit
reported zero candidates, and compact `pair.zyy913jf` passed strict replay again. The private disks,
injected identities, runtime state, and bootstrap secret are recoverable only from machine snapshots
or by rerunning the documented gates.

ADR 0208's distinct-record repetition exported `pair.9cx0jels` from a 2,547,585,024-byte private
root to a 3,297,280-byte secret-free compact proof with the same allowlist. Raw and compact forms
passed strict verification. A separate reviewed zero-retention dry run selected exactly that one
private root and no other state; apply reclaimed 2.4 GiB allocated, the repeated audit returned zero
candidates, and both `pair.9cx0jels` and the original `pair.k8o54n2v` compact proofs passed strict
replay after deletion.

## 2026-08-28 actual-Tor adversarial-boundary cleanup

The accepted interposer gate exported `pair.vx6z0csh` from a 2,551,435,264-byte private root to a
1,953,792-byte secret-free compact proof. Both forms independently passed strict verification. The
37-file compact allowlist retains the interposer chain audits, boundary lifecycle, Ratox heartbeat
and exact-resume records, detached host-PTY evidence, authenticated Tor control projections, both
TAP captures, resource intervals, guest receipts, and source-linked VMM chains. It omits guest disks,
injected identities, runtime state, the bootstrap secret, and Tor data directories.

A reviewed zero-retention Sandwurm dry run selected exactly that one accepted private root and no
other state. Apply reclaimed 2.4 GiB allocated. A repeated audit returned zero candidates and the
compact proof passed strict replay after private-disk deletion. The removed disks and private Tor
cache/state are recoverable only from machine snapshots or by rerunning the documented gate.
