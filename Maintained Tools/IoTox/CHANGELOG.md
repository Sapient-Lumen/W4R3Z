# IoTox changelog

## Official repository — unreleased

### Product expansion

- Slim the public source snapshot by retiring tracked rev0020--rev0043
  prebuilt binaries, fuzz executables, CTest logs, matrix logs, and bulky
  retained-artifact transcripts from `artifacts/`. The tracked artifact tree
  now keeps only small rev0045 route/privacy receipts that are still
  source-referenced, with an ignore fence against accidental re-growth. The
  datacube builder adds a `--public` profile that omits nested founding cubes,
  keeps `--conversation` for the richer internal handoff, scans packaged source
  for private-key PEM markers and full reachable history when packaging a
  full-history bundle, and labels historical tracked artifacts as provenance
  rather than current distribution.
- Tighten repository datacube packaging so `dist/standalone/` is included only
  when its recorded `source-commit` matches the exact clean repository commit
  being packaged. Stale host binary/source-input artifacts are now skipped and
  called out in the cube manifest instead of silently riding along with a newer
  source snapshot.
- Harden the stock-Toxic compatibility soak harness after the 2026-09-29 and
  2026-09-30 keep-going campaigns. Toxic and IoTox friendship setup now
  retries during the existing request window; IoTox-originated retries first
  remove the pending peer by exact route key so the retry is a real fresh
  request instead of a toxcore duplicate rejection. IoTox self-mesh setup gets
  the same remove-and-request retry hook, retry errors are retained as
  diagnostics instead of aborting the wait, and the lab-local Toxic
  `DHTnodes.json` is refreshed to a numeric-only set of current official
  TCP-capable bootstrap nodes. Fresh one-iteration default and forced-TCP
  multidevice Toxic smokes passed with the updated harness; the 24h
  forced-TCP route remains soak-gated rather than reclassified from one smoke.
- Promote the product identity to IoTox 0.51.0 rev0051,
  “Freshness-Explicit Projection Recovery,” and add ADRs 0338--0339.
  Successful tree-v2 `sync-repair` now renders `rollback-witness=0|1`, so
  signature/closure verification cannot be confused with external freshness.
  Direct witness tests replay valid-old branch, workspace, and maintenance
  roots together with their matching old local guards while the external
  witness remains current; live and cold verification refuse without changing
  either side, and exact-current restoration recovers.
- Close one bounded open-descriptor projection-loss window. The exchange path
  revalidates the newly visible projection and the obsolete staged projection,
  including an exact bidirectional comparison of preserved unselected paths.
  A write through a held descriptor immediately after the final scan and
  before `RENAME_EXCHANGE` now returns `protocol_error`, retains both trees and
  the signed pending workspace for operator recovery, and recovery refuses to
  erase the changed staging tree. Canonical prior projection markers admit an
  explicit recipient-local policy transition; missing, malformed, or
  unrelated markers fail before effect. This remains bounded: a write after
  final old-tree validation begins can still race deletion.
- Add the companion deterministic post-exchange descriptor cell. A test-only
  observation point after real `RENAME_EXCHANGE` but before either tree is
  validated proves that a held selected-file descriptor still names the staged
  inode, causes `protocol_error`, and survives ordinary recovery. ADR 0340
  now freezes the remaining source-linked KVM/ext4 restart/remount gate.
- Extend the signed-metadata corruption gate with receipt v2. The harness
  stops and verifies every Agent task, applies all five mutations sequentially
  while the Agent cannot observe them, proves all corrupt roots are
  co-resident before resume, and requires live repair to refuse the first
  branch-pointer error without changing any root. Controlled exit and cold
  startup then refuse, and exact ordered restoration exposes each next family
  through fresh startup until the namespace recovers. The strict verifier
  preserves rev0050/v1 replay, distinguishes receipt maturity in its output,
  rejects non-integral evidence numbers, and has v1/v2 exporter regressions.
  Source-linked rev0051 run `MG27auOK` now qualifies this v2 gate on
  networkless KVM/ext4 and retains compact proof
  `.sandwurm/exports/sync-metadata-corruption/run.MG27auOK`; the accepted
  rev0050/v1 compact proof remains separate historical evidence.
- Promote the product identity to IoTox 0.50.0 rev0050, “Fail-Closed Metadata
  Restoration,” and add ADR 0337. Agent startup now authenticates every present
  live tree-v2 signed semantic root—current branch pointer, its exact immutable
  record and manifest, workspace, and maintenance—before worker/network
  exposure. `sync-repair` validates the same closure before reporting
  `metadata=verified`; family-specific errors propagate the actual corrupt
  root. Neither path deletes, quarantines, rewrites, or overwrites corrupt
  signed metadata. Exact operator-supplied restoration must pass the ordinary
  signature, namespace, and closure checks before the namespace reopens.
- Construct a strict source-linked signed-metadata corruption gate. Three
  read/write nodes run over loopback Tox inside one networkless
  Cloud-Hypervisor/KVM/ext4 guest. With both peers stopped, the rehearsal
  applies one durable same-size final-bit mutation to each of the five families
  in order; live repair must return protocol-error exit 4, cold startup must
  return exit 3 with the exact family classification, and both must preserve
  the corrupt bytes. File-plus-parent-fsynced restoration must preserve
  identity/worktree and finish at `[3,3,3]` with repair on all nodes. The
  verifier uses bounded duplicate-key-rejecting loads, closed receipt schemas,
  exact rev0050/VMM/substrate/nonclaim checks, and authenticated compact
  manifests. Compact export projects extensible Sandwurm records into closed
  content-free summaries and publishes durably with no-replace semantics.
  Source-linked run `mixJ9VUp` passes from commit `08e4179` and binary SHA-256
  `449107ef7152547ededabd378c6298cda2963169527e2912f79676209fcef5bf`
  in 26.429 seconds. It preserves the five-file tree, converges to `[3,3,3]`,
  repairs all nodes, and retains strict compact proof
  `.sandwurm/exports/sync-metadata-corruption/run.mixJ9VUp`.
- Preserve the fail-closed first campaign as diagnostic provenance rather than
  qualification. Run `BB5I3Ow1` exposed that virtiofs retained the host UID on
  a mode-0700 proof directory. The rehearsal still requires a guest-owned
  private evidence parent; the NixOS service now creates and validates the
  primary receipt on guest-private ext4, then publishes an `O_EXCL`, file- and
  parent-fsynced copy to the Sandwurm channel.
- Extend guarded workspace retention with exact raw and compact
  `sync-metadata-corruption/run.*` roots, tracked-Markdown protection,
  live-reference refusal, a dedicated dry-run/apply scope, and raw/compact
  self-tests. Correct the documented power-cut allowlist from seven to ten
  exact parents after adding the three proof-v6 directory-fsync classes.
- Freeze proof v6 for tree-v2's three post-rename/pre-parent-directory-fsync publication windows.
  The guest uses exact-directory `strace -P` filtering and an `fsync` entry delay, proves the selected
  final metadata and stopped worker at arm, and accepts only that directory transaction's bounded
  old-or-new crash state. The host runner, strict verifier, compact exporter, Nix guests, and lab
  commands cover manifest, immutable-record, and mutable-pointer cells while preserving v2--v5
  compatibility. Source-linked runs `dbgtc3ip`, `jznfzx52`, and `ia70ljmf` pass from commit
  `0686cba` and one binary. Each recovered the old selected directory state with one exact temporary,
  then removed staging, converged to exact/exact/successor, restored `[3,3,3]`, and repaired all
  nodes; all three compact proofs pass strict replay.
- Stop issuing five redundant directory `fsync`s on every tree-v2 frontier preparation. Preparation
  now records which private directories it actually created, persists newly created children before
  their parent, and persists the namespace root only when `tree-v2` itself is new. A rejected v6
  record-directory campaign exposed 134 unrelated barriers serializing one writer; the
  focused and complete owned registry remains green after removing them.
- Repair tree-v2 recovery after a cut between immutable branch-record installation and mutable
  pointer replacement. Local record presence is now reusable authenticated graph input rather than
  assumed pointer incorporation; a peer's signed frontier replays an orphan successor through the
  normal dependency and acceptance path. A deterministic reproduction preserves the exact
  manifest, record, and CAS content beside the prior pointer, then proves zero object requests,
  successor-pointer advancement, and projection convergence. The direct registry passes 835/835.
  The rejected real pointer-prefix VM attempt that exposed this defect remains non-qualification;
  repaired-source run `_cphu30p` repeats that exact prefix and passes whole-VMM recovery.
- Promote the product identity to IoTox 0.49.0 rev0049, “Semantic Branch-Publication Recovery,” and
  add ADR 0335's strict proof-v5 construction. Three networkless Sandwurm cells bind the exact
  manifest, immutable branch-record, and mutable branch-pointer pre-rename prefixes. A
  qualification-only `strace` syscall-entry delay holds the real sync worker before commit; the
  harness verifies that exact ptrace-stopped TID and every Agent thread under a process-group
  scheduler fence before the host kills the task-owned VMM. A redacted three-target commitment object
  cross-binds hashed names, sizes, successor hashes, and the prior-pointer hash across both boots.
  Second-boot inspection requires the
  selected durable prefix, permits only an absent-or-exact selected temporary, excludes every
  unrelated temporary, and demands exact successor convergence and repair. Strict runner,
  verifier, exporter, NixOS, cleanup, and synthetic compatibility gates are present. Source-linked
  runs `l2gckna4`, `c9xhj26a`, and `_cphu30p` pass all three boundaries from commit `2b2cc85` and one
  byte-identical binary: each starts recovery `[completed, completed, prior]`, admits its exact
  metadata prefix, preserves identity, converges to branches `[3,3,3]`, and repairs all three nodes.
  Their content-free compact proofs independently verify. Earlier rejected runs corrected cold-build
  timing, exact-path syscall filtering, scheduler-stop ordering, and the product's orphan-record
  recovery semantics without weakening the accepted contract.
- Promote the product identity to IoTox 0.48.0 rev0048, “Durable Object-Pipeline Recovery,” and add
  ADR 0334. Canonical receive-staging and exact generic transport-temporary cleanup now persist one
  incoming-directory barrier per bounded batch,
  and recovered CAS `.install.tmp` cleanup persists its exact fanout, without returning to one
  full-store scan or one fsync per file object. Power-cut proof v4 adds strict
  `receive-staging-partial` and `cas-install-temporary` cells: both bind a stable prior workspace,
  private canonical temporary, absent digest final, expected 32-MiB object, and an immediate
  follower `SIGSTOP` before host `SIGKILL` of the exact VMM. Second-boot offline inspection permits
  only absent-or-exact CAS state, and normal startup must remove staging, converge, restore three
  branches, and repair. Source-linked runs `1e05ayp9` and `jtiyspp_` now pass. The receive cut
  recovered one zero-length generic temporary; the CAS cut recovered the complete canonical incoming
  file after its partial install copy vanished. Both started `[completed, completed, prior]`, removed
  every temporary, installed the exact object, preserved identity, converged the
  18-file/33,619,995-byte successor, restored branches `[3,3,3]`, and repaired all nodes. Their
  content-free compact proofs independently verify. The rejected first receive attempt also exposed
  and motivated exact cleanup of the real generic file-manager temporary.
- Extend the guarded workspace cleaner across the seven exact sync power-cut lab parents and their
  shared compact-export directory. A dedicated dry-run scope retains the newest undocumented run by
  default, protects every exact compact proof cited by tracked Markdown, refuses live/open roots,
  and never broad-matches arbitrary similarly named directories. Its self-test covers raw and compact
  selection. The two accepted and one rejected rev0048 raw campaigns were moved recoverably to host
  Trash after export and re-verification, reducing active `.sandwurm` state to 311 MiB while keeping
  both accepted v4 proofs.
- Add ADR 0333's v3 semantic cut selector. The guest now double-reads raw pending workspace state
  around the visible canonical projection marker and distinguishes `pre-exchange-pending` (marker
  names active) from `post-exchange-pending` (marker names pending). Arm, campaign, recovery, NixOS
  guest, and strict verifier bind the requested boundary, orientation, stage presence, raw phase, and
  encoding. Post-exchange recovery must retain the completed follower projection. A separate
  networkless Sandwurm configuration and `up-sync-power-cut post-exchange` command are included;
  failure to observe the short real window times out closed. Source-linked run `nhjaizl2` captured
  pending orientation with the old stage still present, then recovered all-completed offline views,
  the pending journal/marker/stage tuple, identities, convergence, and three-branch repair after a
  second boot. Compact proof `.sandwurm/exports/sync-power-cut/run.nhjaizl2` independently verifies.
  Together with accepted v2 run `4hto8rll`, both workspace-exchange sides now pass.
- Correct and qualify ADR 0332's whole-VMM power-cut observer. Source audit found that harness v1
  reversed C++'s durable workspace phase values (`stable=1`, `pending_exchange=2`), so run
  `wjlem1i2` armed on a stable journal; its workspace-exchange claim and compact proof are withdrawn
  even though narrower reboot/recovery checks passed. The v2 arm, campaign, recovery, verifier,
  exporter, and guest contract carry and require raw phase byte 2 plus the named encoding, and the
  regression test refuses byte 1. Corrected source-linked run `4hto8rll` then cut the exact VMM with
  pending byte 2, rebooted the crash lineage, found `[completed, completed, prior]` with C still
  pending, preserved identities, and converged/repaired three branches to the exact
  18-file/33,619,995-byte successor. Compact proof
  `.sandwurm/exports/sync-power-cut/run.4hto8rll` independently verifies. This closes one
  workspace-exchange cut, not the remaining power-loss matrix or dishonest-storage boundary.
- Promote the product identity to IoTox 0.47.0 rev0047, “Effect-Fenced CAS Inventory,” and add ADR
  0331. A file-bearing tree-v2 pull now strictly inventories its CAS once, reuses an opaque verified
  in-memory view across every bounded file commit, and performs a fresh full digest/quota scan under
  the same namespace transaction that accepts branches and projects the worktree. Concurrent jobs
  may add fully verified immutable objects, but cached removal, replacement, corruption, malformed
  state, or final quota drift fails before effects. `sync-status` and three-writer receipts expose
  full-scan/object counts. The owned registry proves cached batches, safe additive concurrency, and
  fail-closed corruption. A clean source-linked direct cap-16 run completed the 3,500-file lifecycle
  in 478.979 seconds and reported 7/5 full scans versus 219 commit batches per follower; overall time
  was effectively flat against the prior direct sample. The exact 2-vCPU/2-GiB Sandwurm repeat then
  passed in 554.077 seconds of catch-up and 634.194 seconds overall, 15.3% and 19.5% below the ADR
  0330 VM baseline. Followers reported 21/15 scans across their intermediate jobs, retained the same
  219 batches, and ended with zero staged objects, late cancellations, retained IDs, evictions, or
  watchdog restarts. Compact proof `.sandwurm/exports/three-writer/run.yDPmVYg6` independently
  verifies.
- Add ADR 0330's bounded tree-v2 file-object commit batches. Completed file lanes remain in private
  staging until their current lane window can enter the existing strict CAS importer under one
  namespace transaction, reducing complete-store inventory verification from once per received file
  to once per batch without changing peer framing, signed state, or projection order. Exact bounded
  late-offer retirement now catches and cancels Tox offers that arrive after a pull is settled, and
  `sync-status` plus three-writer receipts expose batch, staged-object, late-cancel, retained-ID, and
  eviction counters. The owned pipeline test proves one four-object batch and the cancel-before-offer
  race. A source-linked direct cap-16 retry passed 3,500 files with 219 batches per follower in
  387.085 seconds of catch-up and 478.624 seconds overall. The exact 2-vCPU/2-GiB networkless
  Sandwurm repeat then passed in 654.214 seconds of catch-up and 788.317 seconds overall: 38.3% and
  30.8% below the prior cap-16 VM result. It observed 7/8 late cancellations and ended with zero
  retained FileIds or evictions; compact proof `.sandwurm/exports/three-writer/run.WoveT4SE`
  independently verifies.
- Add ADR 0329's bounded tree-v2 exact-object lane pipeline. Tree-v2 pulls now use a vector of active
  object lanes capped by the process `--max-sync-tree-lanes` value and the signed namespace
  `maximum-lanes`/`maximum-outstanding-requests` quotas. `sync-status` reports `tree-lane-cap`,
  per-pull `active-lanes`, and `tree-lane-job=` bindings while preserving the old single-lane
  `active-file` projection only when unambiguous. A new owned service test proves four file-object
  requests can be active after one manifest expansion, bringing the direct registry to 833 passing
  checks under the proper mock harness. The first source-linked four-lane near-ceiling direct
  diagnostic passed 3,500 16-KiB files in 1,050.374 seconds after the corrected one-lane baseline
  timed out; the cap-4, cap-8, and cap-16 near-ceiling Sandwurm VM repeats are now retained as
  accepted evidence, and the cap-32/cap-64 timeouts are retained as compact rejected evidence.
- Add ADR 0328's direct open-descriptor source-mutation sync gate. A new owned tree-v2 check scans a
  file, rewrites it through an already-open writer descriptor before CAS installation, and requires
  the stale store to fail with `protocol_error` while installing no object and removing `.install.tmp`.
  A fresh rescan of the new bytes then installs normally. The direct registry is now 832 checks and
  passed under GCC and Clang. This closes one scan/store descriptor race, not projection-exchange
  descriptor behavior, power-cut recovery, corrupt-record coverage, dishonest storage, or backup
  suitability.
- Record one rejected near-ceiling sync capacity diagnostic. A direct three-writer run with 3,500
  16-KiB files reached confirmed friendship, all six read-write shares, and three branch files on
  every node, but timed out after the 1,800-second capacity wait with followers at only 2,124 and
  2,139 object files and no follower projection. This is not a Sandwurm qualification result; it
  localizes the next scale bottleneck to object transfer/projection before repeating a VM gate.
- Reduce observer interference in the three-writer capacity harness. Capacity polling now checks
  per-node file count and total bytes before hashing full file contents, so a slow follower no
  longer makes the harness rehash the complete source tree every 100 ms. A fresh 16-file smoke passed
  after the change.
- Parameterize the three-writer harness with `--max-sync-tree-lanes` and record `tree_lane_cap` in
  receipts. The default Sandwurm guest now asserts cap 4 explicitly, while the next near-ceiling
  qualification can run an apples-to-apples cap-1 baseline and cap-4 default comparison. The lab
  wrapper exposes those as `up-three-writer near-ceiling-cap-1` and
  `up-three-writer near-ceiling-cap-4`; the default `up-three-writer` command still runs the
  established 512-file qualification with recovery/storage follow-ups.
- Split three-writer lane science into process and namespace caps. The direct helper now has
  `--namespace-maximum-lanes N`, requires a fresh/empty state root for nondefault namespace-lane
  experiments, and records process, namespace, and effective caps separately. Sandwurm near-ceiling
  profiles now exist for cap 8/16/32/64 as stable commands, without changing the product
  `sync-create` surface or default cap-4 policy.
- Run the cap-8 near-ceiling Sandwurm science profile. Raising both process and signed namespace
  caps to eight passed the same 3,500-file/57.344-MiB three-writer gate in 1,198.824 seconds, with
  1,106.351 seconds of capacity catch-up. Compared with cap 4, catch-up improved by 170.697 seconds
  (13.4%) and total elapsed improved by 163.112 seconds (12.0%) without a material memory increase;
  compact proof `.sandwurm/exports/three-writer/run.fEPzg6G1` verifies independently.
- Run the cap-16 near-ceiling Sandwurm science profile. Raising both process and signed namespace
  caps to sixteen passed the same gate in 1,138.904 seconds, with 1,059.715 seconds of capacity
  catch-up. Compared with cap 8, catch-up improved by 46.636 seconds (4.2%) and total elapsed
  improved by 59.920 seconds (5.0%), confirming that lane-width gains are flattening; compact proof
  `.sandwurm/exports/three-writer/run.LFDsNpxz` verifies independently.
- Support compact rejected three-writer Sandwurm evidence. The three-writer verifier now accepts
  networkless `status=rejected` IoTox receipts when the failure string is hash-bound, lane caps are
  coherent, partial capacity/store shapes are bounded, and the receipt is content-free. The exporter
  now retains those rejected proofs without requiring a vm-smoke receipt, so failed lane science does
  not require keeping large raw VM roots.
- Run the cap-32 near-ceiling Sandwurm science profile. Raising both process and signed namespace
  caps to thirty-two regressed into timeout after 1,823.048 seconds; the source projected all 3,500
  files, but followers had projected 0 files and only 132/158 tree-v2 objects. Compact rejected proof
  `.sandwurm/exports/three-writer/run.RTfmt0r2` verifies independently and points to cap 16 as the
  measured lane-width sweet spot for this guest shape.
- Run the cap-64 near-ceiling Sandwurm science profile. Raising both process and signed namespace
  caps to sixty-four also timed out after 1,822.462 seconds; the source projected all 3,500 files,
  but followers had projected 0 files and only the 16-byte empty-file object. Compact rejected proof
  `.sandwurm/exports/three-writer/run.kM0Wu7VQ` verifies independently and completes the requested
  8/16/32/64 lane series.
- Re-run the established networkless three-writer Sandwurm qualification on source revision
  `f5078bd482381915f011634727b6621b07175127` with the default tree-v2 cap 4 lane window. The
  primary 512-file phase passed with 37.090 seconds of capacity catch-up and no stalled restart, then
  the recovery and storage-fault follow-up rehearsals passed from the same compact proof root
  `.sandwurm/exports/three-writer/run.5OJVbUl2`.
- Run the near-ceiling Sandwurm comparison profiles. The cap-1 baseline reached friendship, all six
  shares, and three signed branches before timing out in capacity catch-up without an accepted guest
  receipt. The cap-4 default profile passed 3,500 16-KiB files, full object custody, repair,
  three-way conflict convergence, and explicit resolution in a networkless 2-vCPU/2-GiB KVM guest;
  compact proof `.sandwurm/exports/three-writer/run.f3q2rjxM` verifies independently.
- Emit content-free rejected receipts from the direct three-writer harness. Future failed science
  runs now keep stage history, lane cap, capacity parameters, partial projected capacity shape,
  partial tree-v2 store shape, branch/conflict counts, and Agent high-water RSS without recording
  paths, keys, savedata, ledgers, file contents, or CAS objects.
- Extend the workspace cleaner to cover stale nested Sandworm Trash payloads. The default dry-run
  temp scope now audits strictly named `.sandworm/home/.local/share/Trash/{files,info}/` entries
  alongside ordinary sandbox temporaries, preventing old VM/proof trash from becoming hidden
  repository bulk. The 2026-09-03 cleanup moved a 17 GiB nested trash tree out of the workspace and
  then removed 2.1 GiB of audited stale temp/build products, reducing the working directory from
  roughly 25 GiB to 6.6 GiB while retaining compact evidence.
- Add ADR 0327's first positive named Ratox cgroup/PSI kernel qualification. A new
  `ratox-cgroup-vm` flake check boots NixOS Linux 6.6.94 under KVM and runs all five process oracles
  inside transient systemd `Delegate=yes` services: boot-bound orphan recovery, memory/pids with a
  real pids-controller rejection, CPU throttling, real block-device I/O accounting, and PSI
  admission/trigger registration. The VM exposed two portability fixes now covered by tests: fresh
  delegated namespaces may need an anchor leaf before controller activation, and zero `io.stat`
  device lines may be emitted as `MAJOR:MINOR` or `MAJOR:MINOR `. This is one named kernel/service-
  manager gate, not fleet, physical-device, trigger-latency, route-traversal, or production-
  activation evidence.
- Add ADR 0326's real password-prompt sudo qualification. The existing NixOS KVM check now keeps a
  separate test-only NOPASSWD account for the deterministic set-ID branch while its UID-1000
  operator starts canonical Nix-store Bash through the production IoTox PTY, receives a unique sudo
  prompt, submits a PAM-accepted synthetic password with echo disabled, reaches UID 0 only in the
  sudo child, and returns to the non-root shell. The first symlinked-shell attempt was correctly
  refused by descriptor-pinned spawn. This qualifies one NixOS sudo/PAM conversation, not arbitrary
  PAM plugins, hardware tokens, a user's host policy, remote Tox traversal, or default activation.
- Add ADR 0325's first bounded real-filesystem storage-fault campaign. One 2-vCPU/2-GiB Sandwurm
  guest places three fresh nodes on separate 192-MiB loop-backed ext4 volumes, forces live `ENOSPC`
  after 178,147,328 filler bytes, proves an explicit mutation refusal, kills and recovers that Agent,
  proves read-only startup refusal without a durable-state change, and kills a second Agent at the
  signed `pending-workspace` side of a 32-MiB exchange. Restart reconciliation converges and repairs
  all three views to the exact 19-file/33,620,017-byte tree. The combined compact proof passes both
  independent verifiers. This is same-host process/filesystem evidence, not a whole-VM power cut,
  exhaustive transition/corruption matrix, dishonest-storage result, backup, or precious-data
  qualification.
- Add ADR 0324's forward authority-round supersession rule. A strictly newer ownership
  epoch/sequence from the same verifier and confirmed session, without a ledger-format downgrade,
  may replace a challenge whose proof has not yet reached toxcore. Equal/older heads, changed
  same-head bytes, verifier replacement, transcript change, and downgrade remain conflicts; the
  verifier still admits only a proof matching its exact current ledger. The retained 831-check
  registry now covers two rapid durable grants before proof preparation. A two-vCPU recovery VM
  exposed the original asymmetric stall and was correctly rejected before guest evidence. The
  clean replacement crosses all rapid-grant and survivor re-proof boundaries, completes one-node
  plus all-node recovery, and retains a verified compact Sandwurm proof.
- Add ADR 0323's bounded tree-v2 node-loss recovery ceremony. Completed replay responses can now be
  retired by namespace only for an additive share while the Agent holds the network authority/effect
  fence; destructive mutations retain their stronger drain rule. The harness converges three
  writers, verifies an ordinary selected backup/restore, erases and replaces one writer after
  separate revocation/cutoff/friendship removal and two ordered checkpoint barriers, then erases all
  live roots and reconstructs three fresh identity/authority/namespace states from the restored
  ordinary tree. The final direct source-linked gate passes 33 files, 131,099 bytes, six repair
  checks, four exact verifier matches, and disjoint obsolete/replacement principal hashes in 81.771
  seconds. A clean 2-vCPU/2-GiB Sandwurm cell retains the same recovery result in 97.238 seconds
  after its 512-file capacity and 24-cycle lifecycle, with zero watchdog restarts. The owned registry
  remains 831. This is bounded same-machine recovery orchestration, not backup
  independence/provenance, storage-fault evidence, or precious-data readiness.
- Add ADRs 0320--0322's first persistent-ext4 three-writer capacity and restart-recovery gate. A
  fresh 2-vCPU/2-GiB Sandwurm cell converges and repairs 512 16-KiB files (8 MiB logical), records
  70.997-second catch-up, 163/318/75-ms repairs, 16--18-MiB Agent high-water RSS, and about 20--21
  MiB allocated growth per node, then completes the existing conflict, 24-cycle, checkpoint,
  quarantine/restore, and writer-cutoff lifecycle. Derived projections retain close/hash/mode
  validation but use one filesystem barrier before atomic directory exposure; immutable CAS objects
  keep per-file `fsync`. Startup now reconciles signed pending workspaces, and recovery preserves a
  path-based edit made after exchange while refusing ambiguous pre-exchange or inexact-staging
  layouts. A second byte-identical-binary pressure cell crosses the watchdog and proves restart
  recovery of the intact local edit. One existing owned recovery check gains the regression while
  the direct registry remains 831. This is same-host bounded
  construction evidence, not near-ceiling, cold-cache, 24-hour, power-cut, ENOSPC/read-only,
  open-descriptor, dishonest-storage, backup, or precious-data evidence.
- Record the first representative-capacity controls without closing the gate: a 4,096-file
  scan/CAS/branch/merge/projection cell and a 3,621-entry, 53,477,376-byte mixed-size doctor/restore
  cell now have elapsed and peak-process-RSS evidence. Both ran hot on tmpfs, so persistent-disk
  amplification, cold scans, conflicts, repair, and three-node catch-up remain explicitly open.
- Add ADR 0319's bounded independent-restore comparison. `sync-recovery-verify BACKUP_ROOT
  RESTORED_ROOT [MAXIMUM_BYTES [MAXIMUM_ENTRIES]]` requires two disjoint canonical trees, reuses the
  strict filesystem contract, refuses unresolved `.iotox-conflicts`, alternates stable scans, and
  compares exact relative paths, bytes, entry kinds, and private owner modes without opening live
  IoTox state. Four owned checks bring the direct registry to 831 and the command vocabulary to 200
  spellings. This closes the comparison mechanism, not backup provenance/independence, atomic
  snapshotting, storage durability, or the precious-data recommendation. ADR 0323 subsequently
  adds bounded node-loss orchestration, authority recreation, reseeding, and writer retirement.
- Add ADR 0318's bounded source-filesystem contract to both synchronization doctor paths. Two
  read-only walks now refuse foreign/mutable ownership, symlinks, hard links, special files, any
  ACL/xattr state, sparse allocation, and ASCII case-fold collisions; new strict v3/v4 reports name
  the exact byte-case requirement plus local ownership, normalized mode, and discarded timestamp
  semantics. Two owned checks bring the registry to 827. This is point-in-time Linux preflight, not
  cross-filesystem portability, continuous enforcement, metadata support, storage qualification, or
  backup evidence.
- Add ADR 0317's complete typed CLI command registry and deterministic
  `completion bash|zsh|fish`. All 199 accepted spellings now carry a closed dispatcher class; eleven
  compatibility forms name their canonical target; terminal, terminal-admin, and control
  recognition consult the registry; and `--help` prints its generated exhaustive index. Four owned
  checks bring the registry to 825, and all emitted scripts pass their native syntax parser. This
  completes stable command-name discovery without querying peers, guessing paths/arguments, or
  modifying shell configuration.
- Add ADR 0316's bounded repeated production Ratox reconnect gate. One real
  `terminal PEER --reconnect` process now crosses two sequential seeded 100% route losses while
  retaining one PID/start time, remote session/incarnation, and shell; exact authenticated epochs,
  generations, and terminal positions advance 2-to-3-to-4 and 1-to-2-to-3. Direct UDP and forced TCP
  raw and 252 KiB compact proofs independently pass, with positive drops on both TAPs in both
  intervals and no relay-only carrier fallback. The original one-loss receipt remains verifiable,
  Ratox framing remains frozen, and long-soak, overlay-route, Agent-restart, independent review, and
  production-activation claims remain open. Final validation passes 821 direct checks, all 55 GCC
  CTest entries, and all 70 Clang ASan/UBSan entries; it also corrects two reversed v1/v2
  sync-doctor assertions while retaining the already-correct production/report contract.
- Add ADR 0315's configured synchronization admission check. `sync-doctor-configured --config PATH
  NAMESPACE` joins the exact stable-device-signed automation source and nondefault namespace policy
  to live immutable-store and incoming-staging occupancy, remaining byte/object quotas, and current
  source/managed filesystem headroom under the existing namespace transaction. It creates no missing
  state, rereads both policy stores before success, and emits a new strict v2 report while preserving
  pre-creation v1. Four owned checks bring the registry to 821.
  A ready result is a point-in-time conservative preflight, not reserved space, convergence,
  storage-durability evidence, backup certification, or a precious-data recommendation.
- Add ADR 0314's per-tree-v2-namespace semantic-state witness. A collision-separated lane-10 record
  binds immutable storage identity, the writer-sorted live branch frontier, and exact signed
  workspace and maintenance state. A dedicated signed two-head guard joins branch, workspace,
  pin/unpin, and writer-cutoff mutations to authenticated pending/committed CAS; startup reconciles
  every namespace before RuntimeTree, and root-derived Agent reads remain transaction-fenced.
  Thirteen owned checks bring the registry to 817, including the crash-join matrix, both lost-reply
  boundaries, old complete-state replay, metadata/fork refusal, stale early-return fencing, and a
  concurrent-reader barrier. The 11-record two-guest gate advances tree-v2, refuses a complete old
  namespace snapshot while the service remains current, restores exact-current state, and restarts.
  This is semantic startup/mutation freshness, not content custody, backup, safe purge, operational
  independence, or a continuously renewed live-clone lease.
- Add ADR 0313's complete witness-service checkpoint floor. `IOTXWCP1` signs the pinned service
  key and complete sorted population of up to 4,096 exact committed or pending lane records.
  Operators can export, verify, retain, and require that artifact on `witness-service-serve`; a
  missing selector, selective rollback, same-position fork, wrong key, malformed record, or byte
  substitution refuses before bind while exact and later states remain usable. Service startup now
  verifies every stored record even without a floor. Four owned checks bring the registry to 804,
  and the two-guest gate exports/verifies ten records, rejects one authentic old authority-service
  record against the advanced floor, restores current state, and restarts. This supplies executable
  independently checkpointed persistence, but a same-disk checkpoint is not independent and it is
  not a live lease, hardware counter, replacement, handoff, or emergency re-anchor protocol.
- Add ADR 0312's per-namespace synchronization four-root witness. Each opted-in non-tree-v2
  namespace derives a collision-separated service domain and externally commits its exact signed
  published, accepted, activated, and retained roots plus immutable storage identity. Complete
  sync-policy witnessing is mandatory; quiescent enrollment verifies that policy first, and live
  namespace add/remove or, in that first slice, tree-v2 refused rather than silently downgrading;
  ADR 0314 now gives tree-v2 its separate semantic-state lane. The signed local
  two-head guard drives crash-forward remote CAS recovery, and root-derived reads remain fenced by
  the namespace transaction until external commit. Thirteen owned checks bring the registry to 800;
  the nine-lane two-guest gate enrolls two namespaces and rejects a complete old four-root/guard
  restore before RuntimeTree. This is startup/mutation freshness, not a live clone lease, content or
  backup certification, full namespace-state freshness, safe purge, or operational independence.
- Add ADR 0311's separately enrolled update-lifecycle frontier. One exact head binds the canonical
  release-signer policy and absent-or-complete stable-device-signed state; a signed intent carries
  the exact successor across authenticated pending/committed CAS. Every stage, apply, health-window,
  confirm, and rollback transition advances exactly one state generation before the derived
  `current` pointer changes. Interrupted apply repairs forward, complete old state and policy
  substitution refuse before RuntimeTree, and the enrolled policy stays frozen until an explicit
  replacement/re-anchor ceremony exists. Four owned checks bring the registry to 787, and the
  eight-lane two-guest gate enrolls and verifies the lane through the actual service. Per-namespace
  sync state, exhaustive recovery, independent deployment, and witness replacement remain.
- Add ADR 0310's separately enrolled synchronization-policy frontier. One deterministic digest now
  commits every canonical namespace policy and stable-device-signed automation record under the
  configured policy root. Startup authenticates that exact head and freezes the reviewed snapshot
  before RuntimeTree. Agent-mediated namespace and automation mutations durably write a candidate,
  advance it through signed intent and authenticated pending/committed CAS, then—and only then—make
  it live. Offline edits require an explicit quiescent `witness-sync-policy-commit` and restart.
  One owned check brings the registry to 783; the seven-lane two-guest gate performs a live
  `sync-create`, restores the complete enrolled-empty policy plus checkpoint, and refuses before
  runtime. Diagnostic structural commitment v7 records the opt-in. ADRs 0311 and 0312 subsequently
  add update lifecycle and the exact non-tree-v2 four-root slice, and ADR 0314 adds tree-v2's
  semantic roots; broader namespace state/content,
  exhaustive recovery, independent deployment, and witness replacement remain separate work.
- Add ADR 0309's separately enrolled mutable-command effect frontier. Every retained incoming
  non-read-only command that crosses the signed `STARTED` boundary contributes its exact sender,
  principal, authority head, operation, and canonical request to one stable digest. The Agent
  advances that digest through durable intent and authenticated pending/committed CAS before it
  calls either mutable provider; witness outage, rollback, deletion, or disagreement prevents the
  effect. Result/delivery churn and read-only commands do not consume witness positions. Effect
  identities are retained until a future witnessed compaction protocol, making the configured
  record ceiling a deliberate fail-closed lifetime bound. One owned check brings the registry to
  782, and the two-guest gate enrolls and starts all six lanes through the real service. Diagnostic
  structural commitment v6 records the opt-in. This prevents erased-start replay; it does not claim
  generic exactly-once physical effects. Sync/update freshness, exhaustive recovery, independent
  deployment, and witness replacement remain.
- Add ADR 0308's separately enrolled Ratox terminal-policy witness. The complete validated
  profile/binding tree has one path-free canonical semantic digest; ordinary offline edits remain
  unusable until `witness-terminal-policy-commit --config PATH` binds the exact next signed local
  checkpoint through durable intent and authenticated pending/committed CAS. Startup completes only
  an already prepared exact transaction and otherwise requires the external committed digest before
  it advances startup incarnations or creates RuntimeTree; it caches that verified policy for live
  activation. Five owned checks bring the registry to 781. The two-guest gate replaces a reviewed
  sudo-capable UID-1000 profile with a no-escalation profile, proves pre-commit refusal, commits it,
  and then refuses restoration of both the old sudo profile and old signed checkpoint. Diagnostic
  structural commitment v5 records terminal-policy witnessing. Sync, update, command-effect,
  exhaustive-recovery, independent deployment, and witness replacement gates remain.
- Add ADR 0307's separately enrolled route-generation witness lane. The enrollment ceremony anchors
  the newest reviewed stable-device-signed route artifact; live adoption then requires the exact next
  generation, writes a device-signed intent before external pending CAS, verifies the local signed
  high-water checkpoint, and commits the remote head before routes can reach runtime. Complete
  artifact-plus-checkpoint rollback, forks, deletions, skipped generations, missing intents, and
  unresolved service state fail closed. Four owned checks bring the registry to 776, including the
  actual authenticated TCP service and interrupted-final-CAS recovery. The two-guest gate advances
  generation one to two, restores the complete valid generation-one local pair, and refuses before
  RuntimeTree. Diagnostic structural commitment v4 records route witnessing. Terminal policy, sync,
  update, effect, exhaustive-recovery, independent deployment, and witness-replacement gates remain.
- Add ADR 0306's separately enrolled application-protocol and Ratox-host incarnation witness lanes.
  Each opted-in startup durably binds the exact signed next record through the authenticated
  pending/committed service before runtime creation; older valid local records, deletion, fork,
  missing intent, and unresolved service state fail closed. Recovery completes an exact pending
  transition forward before the new process consumes another namespace. Five owned checks bring the
  registry to 772, including injected final-CAS interruption and real remote-service traversal. The
  expanded two-guest gate uses a UID-1000 Ratox profile and independently restores older application
  and Ratox records while the witness stays current. Diagnostic structural commitment v3 records
  both opt-ins without disclosing endpoints or paths. Terminal policy, route, sync, update, effect,
  exhaustive-recovery, and physically independent service gates remain open.
- Add ADR 0305's authenticated remote authority-witness service. A dedicated witness-role Ed25519
  identity signs durable exact-CAS records and nonce-bound replies; stable devices sign every fixed
  query/CAS and explicit no-replace enrollment. Complete host/port/key/domain/epoch selection now
  fails closed before runtime on absence, wrong key, stale state, or fork. Truncated clients and port
  probes cannot terminate the daemon. Eight owned checks bring the registry to 767, and a retained
  two-guest NixOS gate commits real RecallRoot bootstrap, rejects a complete valid local rollback,
  then crosses exact-current recovery, outage, restart, wrong-key refusal, and final recovery. The
  guests share one host/admin; production still requires independently administered,
  rollback-resistant or separately checkpointed witness persistence.
- Add ADR 0304's retained AArch64-kernel rescue gate. A minimal locked Linux 6.6.94 guest under QEMU
  `virt`/TCG runs the cross-built current production PTY qualifier as UID 1000; profile-v7 pins,
  descriptor-only oksh launch, capsule applet resolution, identity, file/hash/list work, and clean
  exit all pass. This closes the construction-host kernel/PTY slice without weakening the retained
  x86-binfmt negative boundary; one named real device ABI/kernel qualification remains.
- Implement ADR 0303's optional required fscrypt-v2 state boundary. `run-check` and live `run`
  descriptor-pin one externally unlocked policy root, its explicit public master-key-identifier pin,
  exact live key and mount identity, recursively
  verify every extant inode, close over every configured/derived durable root and file-backed config,
  and require tmpfs or same-policy runtime. Live startup now completes security/witness recovery
  before creating its runtime tree. Atomic state writes seal every newly created parent component
  `0700`, preventing Agent-authored nested state from violating that closure on restart. The redacted
  structural configuration commitment v2 distinguishes protected-state and authority-witness presence
  without committing paths, endpoints, or policy IDs. The retained ext4 VM crosses real savedata creation, wrong-key
  refusal, exact-key recovery, raw-media canary absence, no swap, and prefix/symlink/hardlink/FIFO/
  nested-mount attacks.
- Add the authority lane's rollback-witness transaction coordinator. One canonical durable intent
  binds the exact owner-signed next record, old/new record-count heads, device/domain/epoch/lane, and
  random nonce around an authenticated pending/committed exact CAS. Lost replies recover only forward;
  missing intent, rollback/deletion/fork, mismatch, or outage fails closed. Production rejects a
  same-domain backend outside the explicit test exception, and no CLI flag can assert independence.
  Twelve new owned checks bring the registry to 759; the added interruption cells cover unapplied
  intent cleanup, pending-with-local-new completion, final committed-CAS lost reply, and an actual
  pre-revocation ledger/guard snapshot replay. ADR 0305 subsequently supplies the authenticated
  remote-service backend; operationally independent deployment and broader witness lanes remain open.
- Add ADR 0301's reproducible AArch64 rescue capsule from the same pinned oksh 7.9 and Toybox 0.8.14
  sources. Both architecture packages reject dynamic dependencies and embedded Nix-store paths,
  carry exact manifests/provenance/notices, and emit SPDX 2.3 tag-value documents validated during
  construction. qemu-user executes AArch64 oksh and Toybox; an x86-kernel binfmt VM proves non-root
  direct execution and IoTox discovery while retaining the expected sealed-`fexecve` `ENOENT` as a
  negative boundary. Native-AArch64-kernel production-PTY qualification remains open.
- Add canonical owner-local terminal profile v7 with optional SHA-256 pins for the shell and rescue
  Toybox ELF. Generated shell/toolbox templates pin the qualified payload automatically; the POSIX
  backend rehashes the exact descriptor-pinned files immediately before spawn and refuses mutation
  without executing the target. Canonical v1--v6 records remain readable and unpinned. One new owned
  check brings the registry to 747; the default CTest surface contains 55 targets.
- Accept ADR 0302's protected-local-state architecture before implementing it. An externally
  unlocked fscrypt-v2 root must close over every configured security-bearing state path and derived
  companion before any network/effect surface starts; secrets never enter argv, environment,
  config, or peer input. A separately controlled authority-lane witness uses durable local intent and
  pending/committed compare-and-swap. Migration, recovery, clone, replacement, key-loss, rollback,
  and unavailable-witness ceremonies are explicit; no same-disk test double may claim independence.
- Accept nine ordered post-founding workstreams: synchronization doctor/health, Mosh-like Ratox
  continuity, deployable Agent configuration/preflight, a content-free flight recorder, human
  aliases/invitations, forward-only sync history/restore, sparse custody, encrypted local state plus
  an independent rollback witness, and multi-architecture rescue capsules. The roadmap and owning
  sync, Ratox, CLI, threat-model, and rescue documents freeze their dependencies and nonclaims.
- Add read-only `sync-doctor` source preflight (ADR 0288). It shares `sync-create` policy grammar,
  hashes every selected file, invokes the production tree-v2 scanner/manifest encoder, and reports
  bounded first-revision inventory/store/staging estimates without contacting an Agent or writing a
  namespace. Managed-store headroom and backup quality remain explicitly unassessed. Four new owned
  checks bring the direct registry to 727; the default CTest surface remains 54 targets.
- Add interactive `terminal PEER --reconnect` (ADR 0289). After authoritative loss it retains the
  exact session/incarnation, retries `resume_only` at a fixed signal-interruptible cadence, and
  accepts only a higher attachment generation. A separate-process gate refuses two early attempts,
  resumes generation 1-to-2, renders retained output, proves there was only one new-session OPEN, and
  detaches cleanly. Ratox and local terminal framing are unchanged; daemon restart still loses PTYs.
- Qualify that public production-client path across genuine two-guest total route loss (ADR 0300).
  The new Sandwurm `ratox-cli-reconnect` cell executes one real CLI under a PTY, binds unchanged
  PID/start ticks and exact remote session/incarnation, observes warning-before-offline truth,
  retained zero-attached host state, and generation/sequence continuation after higher-epoch
  recovery. Direct UDP and forced TCP raw and 248 KiB compact proofs pass independently with one
  identical source-linked binary; no Ratox or local-controller frame changes.
- Add canonical owner-private `iotox-agent-config-v1`, `config-lint`, `run --config` exact-option
  overrides, and non-mutating `run-check` (ADR 0290). Live `run` and the check share parsing,
  derived-path normalization, provider/path/policy/profile/route/cgroup preflight; signed route
  inspection neither locks nor advances its high-water record. Recovery-capable durable stores and
  final PTY-child kernel enforcement remain visibly deferred. Five owned checks bring the direct
  registry to 732; the binary lifecycle now restarts through a real config file.
- Add the ADR 0291 stable-device-signed diagnostic flight recorder, bounded to a configurable
  16..256-record content-free tail. Closed event/phase/network/feature fields, structural redacted-
  config commitments, coarse counters, canonical signature verification, private stable reads, and
  crash-atomic writes keep payload, identities, paths, endpoints, raw config, and timestamps out.
- Add local-control v1.49 empty-payload operation 108 plus `diagnostics-export PATH` and standalone
  `diagnostics-inspect PATH`. Export validates the Agent redaction, builds and revalidates a <=64 KiB
  versioned digest-framed bundle, writes mode 0600 with no-follow/no-clobber durability, and warns
  that metadata still correlates activity. The identity-free bundle is not device attestation and
  the signed ring has no independent rollback witness. Two owned checks bring the registry to 734;
  the one-binary gate crosses live export, offline inspection, redaction, mode, bound, and no-clobber.
- Add ADR 0292's stable-device-signed owner-local peer alias store and `peer-aliases`,
  `peer-alias-set`, `peer-alias-rename`, and `peer-alias-remove`. The 256-entry one-to-one registry
  refuses collision/rebinding, atomically renames, idempotently removes, and retains names across Tox
  peer deletion so a network event cannot silently release a trusted name.
- Freeze shared established-peer selector precedence with explicit `friend:`, `key:`, and `alias:`
  escapes plus unambiguous bare compatibility forms. Main CLI operations and Ratox terminal
  open/resume/list/close resolve through the same grammar. Local-control v1.50 operations 109--113
  expose bounded list/mutation/resolve without changing friendship, authority, or peer framing. Two
  owned checks bring the registry to 736; the one-binary gate proves real alias-selected operations,
  restart persistence, peer-removal retention, and explicit retry-safe release.
- Complete workstream 5 with ADR 0293's exact 320-byte signed peer invitation. Live
  `peer-invitation-create` binds stable device identity to the current full Tox address, bounded
  expiry, random nonce, optional canonical alias, and the closed authority-v3 requested-capability
  vocabulary, then verifies before a private no-clobber write.
- Add untrusted `peer-invitation-inspect`, pinned nonmutating `peer-invitation-import`, and explicit
  replay-safe `peer-invitation-accept`. Acceptance composes the existing friend-request and alias
  operations, never installs authority or sync policy, and reports partial alias failure for safe
  retry. Local-control v1.51 operation 114 creates artifacts without changing peer/Ratox framing.
  Two owned checks bring the registry to 738; the one-binary gate crosses wrong-pin, expiry-ready
  import, no-clobber, distinct-Agent friendship/alias creation, exact retry, and empty authority.
- Complete workstream 6 with ADR 0294's tree-v2 synchronization time machine. `sync-history` reloads
  every live retained signed record and separates current/checkpoint/pin facts; `sync-diff` compares
  exact causal candidates and visible content; `sync-conflicts` exposes bounded provenance without
  content. Hexadecimal paths and explicit omission counts keep output unambiguous and below local
  control limits.
- Add read-only `sync-restore-plan` and exact-token `sync-restore-forward`. The plan commits to policy,
  authenticated maintenance, current frontier, signed workspace generation, clean worktree, target,
  and required objects. Apply re-derives the token and re-authors the historical projection at the
  next local writer generation against the current frontier. It never rewinds HEAD; stale/dirty,
  missing-object, conflicted-target, quota, already-current, and replay cases refuse. Local-control
  v1.52 operations 115--119 do not change peer or Ratox framing. Two direct checks bring the registry
  to 740, and the live Agent test crosses checkpoint/pin/history/diff/conflict/plan/forward restore.
- Add ADR 0295's first tree-v2 sparse-custody vertical slice. `sync-interest` inspects or atomically
  replaces recipient-local canonical prefix rules; `sync-interest-clear` restores complete intent.
  Local-control v1.53 operations 120--121 change no peer/Ratox frame and grant the remote no path or
  destination authority.
- Retain and verify the complete signed branch/manifest graph while requesting only selected unique
  file objects. Tree pull status, repair, and GC now expose complete/partial custody and exact
  declared/selected/skipped coverage. Policy-bound projection markers prevent widened interest from
  manufacturing deletion events; an ordinary pull backfills and atomically establishes the new
  projection. Sparse GC quarantines unselected bytes recoverably and pins no longer imply a complete
  backup. Two new checks bring the registry to 742. Authenticated tree-v2 source availability and
  complementary multi-source scheduling remain open.
- Add ADR 0296 tree-v2 complementary-source recovery without changing peer framing. The existing
  `sync-pull-multi` and `sync-source-add` controls now admit tree-v2 jobs: one primary freezes the
  frontier, then authenticated exact `absent`/`unavailable` results advance only that immutable
  object through the bounded source set. Status exposes aggregate and per-source content-free facts;
  every supplied object retains exact FileId, size, digest, canonical decode, and CAS checks. One
  deterministic missing-primary/complementary-source check brings the registry to 743.
- Add ADR 0297 and `sync-health NAMESPACE [cached|refresh]`. Local-control v1.54 operation 122
  refreshes the authenticated tree-v2 frontier, selected object coverage, workspace/worktree,
  conflicts, writer cutoffs, automation streak, active-store headroom, and last source evidence,
  derives green/yellow/red, and atomically commits one content-free stable-device-signed record.
  Sparse selected custody can be green but stays explicitly partial; every response freezes
  `rollback-witness=0 backup-certified=0`. Two checks bring the registry to 745, and the live Agent
  test crosses refresh plus verified cached reload after forward restore.
- Add ADR 0298 and redacted diagnostics v2. Local-control v1.55 operation 108 now locally verifies
  cached tree-v2 health and emits only anonymous eligible/verified/absent/invalid, color, custody,
  repair, automation, pressure, and source aggregates. Namespace names, paths, commitments, keys,
  content, signatures, and stable slots remain absent; legacy v1 payloads remain inspectable. The
  fixed 48/64 KiB bounds and outer bundle framing remain, as do explicit no-witness/no-backup
  qualifiers. One new check brings the registry to 746 and the live Agent gate joins a signed green
  partial-custody record without naming it.
- Add ADR 0299 and redacted diagnostics v3. The existing administrative host probe is now one reusable
  snapshot: the explicit CLI keeps live child confinement probes, while the running Agent uses a
  passive/no-fork sample and exports only closed pidfd/seccomp/MDWE/Landlock, privilege, sudo, and
  cgroup grades, masks, ABI, and unknown-controller count. Paths and raw kernel/controller text stay
  local; v1/v2 payloads remain inspectable. Expanded existing gates keep the registry at 746.
- Repair a real fallback-shell discovery lifetime bug diagnosed by Clang: PATH components now view
  the retained PATH string instead of a destroyed `std::string::substr()` temporary.

### Founding-machine roadmap completion

- Add a separately reproducible `iotox-rescue-toolbox` package: static oksh 7.9 plus Toybox 0.8.14,
  240 command names, exact source hashes, and bundled notices in about 1.22 MiB of resolved ELF
  payload. Toybox's partially implemented shell is excluded; oksh curses integration is disabled so
  the package contains no dynamic or embedded Nix-store dependency (ADR 0287).
- Add toolbox qualification to `terminal-shell-discover` and disabled
  `terminal-profile-toolbox-template` generation. Rescue profiles start the fixed shell with `-i`,
  prefix the qualified toolbox PATH, freeze the real non-root account, and retain baseline/default-
  denied privilege gain; sudo remains an explicit separate compatibility profile. Ordinary fallback
  discovery now checks eleven known shell names across the deterministic per-user/NixOS/Unix PATH.
- Cross the exact static payload through the production PTY as a non-root account with no host tools
  in PATH, proving interactive shell startup, applet resolution, identity, file creation, SHA-256,
  listing, and clean exit. Repeat discovery/profile/process proof in an isolated NixOS VM. The owned
  registry then contained 723 checks; Ratox framing and profile v6 bytes are unchanged.

- Add canonical terminal profile v6 with a frozen real-account identity, exact supplementary groups,
  and an explicit default-deny privilege-escalation field. V1-v5 remain readable and always migrate
  to denied escalation (ADR 0286).
- Add deterministic `terminal-shell-discover` and disabled `terminal-profile-shell-template`
  generation. The ordinary shell retains baseline no-new-privileges confinement; `--allow-sudo`
  creates a visibly separate non-root compatibility profile and delegates every elevation decision
  to existing sudoers/PAM policy.
- Prove both privilege branches at final exec and add an isolated NixOS KVM check that crosses the
  production PTY with a real set-ID-root noninteractive sudo child; it observes root only in that
  child and return to the frozen non-root account. The guest's passwordless rule is deterministic
  scaffolding, not PAM-prompt qualification. No Ratox framing or remote profile-selection surface
  changes.

- Freeze recipient-local component-prefix include/exclude rules with exclude-wins semantics and
  private regular-file owner `r/w/x` manifest metadata while preserving namespace/manifest v1 bytes
  and complete-tree defaults (ADR 0278).
- Accept a 16-cell direct-UDP/forced-TCP route-policy population, 16-way/128-order conflict matrix,
  candidate-17 refusal, named durable crash/fork layouts, and a 4,096-file tree-v2 path. Oversized
  manifests use indexed 60 KiB commitments without changing formerly valid identities (ADRs
  0279--0281).
- Roll synchronization publisher reads through bounded FIFO exact-replay windows. Recent duplicates
  retain byte-identical replay and no duplicate offer; retired immutable reads re-authorize as fresh
  work. This repairs the 256-result lifetime exhaustion exposed by the first long shadow without
  changing framing or side-effecting replay rules (ADR 0282).
- Accept the networkless two-hour IoTox/Resilio shadow: 240 exact convergence cycles over
  7,200,096 ms, six restarts per IoTox role, zero post-setup manual transfer commands, and 356 replay-
  window evictions. Compact proof `run.XXdpLNPh` contains no content, keys, runtime state, or Resilio
  secret (ADR 0283).
- Permanently retire six hosted, independent-party, physical-target, and independently witnessed
  public-history gates from repository completion. All four founding-machine gates now pass; the
  roadmap contains zero open checkboxes and six explicit strikethroughs. The complete owned registry
  contains 718 checks and the default CTest surface contains 54 targets.
- Separate synchronization confidence from backup trust. ADR 0284 requires independently versioned,
  independently restorable recovery outside IoTox writer authority and names operator inventory,
  restore-drill, rehearsal, repair, capacity, and retirement checks plus eight engineering graduation
  gates before a precious-working-set recommendation.
- Add an outsider-facing Ratox/SSH explanation: Tox supplies reachability, the authority ledger
  supplies permission, and an owner-bound profile supplies the exact executable and confinement.
  Clarify where SSH remains the better tool and what an Eternal/Mosh-shaped future would still need.

### Bounded shared history and exact writer retirement

- Freeze negotiated tree-v2 checkpoint format 2 behind feature bit 31. A conflict-free authorized
  writer may compact an authenticated frontier into one signed graph floor; ordinary format-1
  branch and peer-frame bytes remain unchanged, and old peers fail closed across the complete
  reachable lineage.
- Stop acknowledgement-only branch echo. Remote convergence retains the deterministic merged
  manifest beneath the signed workspace journal, while only initialization or a visible worktree
  edit advances a local writer branch.
- Add stable-device-signed exact record pins and terminal writer cutoffs. Cutoff freezes one admitted
  `(writer, generation, record)`, removes its current pointer and local automation source, and
  refuses later records. It is owner-local policy repeated on every survivor, not consensus or
  general authority revocation.
- Add graph-aware `sync-gc NAMESPACE dry-run|quarantine` and `sync-restore NAMESPACE` for tree-v2.
  Current branches, pins, and active/pending workspace manifests/frontiers are roots; traversal
  stops only at authenticated checkpoints. Quarantine uses exact no-replace moves, restore
  reauthenticates every object, and no purge mode exists.
- Add local-control v1.47 operations 100--105 and the explicit `sync-checkpoint`, `sync-pin`,
  `sync-unpin`, `sync-retention`, `sync-restore`, and `sync-writer-cutoff` commands. Bound candidate
  sets to one value per writer and 16 values per path.
- Extend the networkless three-writer Sandwurm gate through 24 rotating edits, remote checkpoint
  propagation, pin/unpin, two-object quarantine/restore, two-survivor cutoff, and refused retired-
  writer re-entry. Compact proof `run.XXiFEDeB` passes both strict verifiers. A preceding constrained
  cell's intermittent pending exchange remains documented as an availability observation; the
  harness now has bounded stage telemetry and writer-restart recovery.
- The complete owned registry now contains 711 checks and the default CTest surface remains 50
  targets. GCC, Clang, and ASan/UBSan matrices pass; the accelerated VM cell is not an hours-long or
  adversarial deployment claim (ADR 0275).

### Bounded full-mesh tree-v2 synchronization

- Replace the pair-only automation binding with a fixed 4,808-byte stable-device-signed v2 record
  containing a canonical set of up to 15 remote stable principals. Continue to verify 4,328-byte v1
  records and migrate only on an explicit policy mutation; exact retries remain generation-stable.
- Make repeated `sync-share NAMESPACE FRIEND read-write` additive and idempotent. Every added peer is
  preflighted against the 16-writer tree-v2 wire bound and local automation capacity before its
  signed authority mutation is accepted. Peer framing and negotiated feature bits are unchanged.
- Serialize writable namespace work while selecting due peers fairly with independent retry clocks,
  so one unavailable writer cannot push healthy writers behind its exponential backoff.
- Prove deterministic three-writer convergence in all six arrival orders and run a real full-mesh
  three-daemon gate through three friendship edges, six directional grants, three concurrent offline
  values, two retained alternatives per node, and explicit causal resolution. The direct registry
  now contains 699 checks; dedicated networkless Sandwurm verifier and compact-exporter tests bring
  the default CTest surface to 50 targets (ADR 0274).

### Owner sync creation and read-only sharing

- Add local-control v1.45 operations 95--97 and the ordinary owner commands
  `sync-create NAMESPACE PATH [INTERVAL_SECONDS]` and
  `sync-share NAMESPACE FRIEND read-only`. Peer framing and negotiated feature bits are unchanged.
- Make `sync-create` infer content-v2 for a regular file or treepack-v1 for a directory, prepare a
  private managed state root, install the local stable device as sole writer under manual activation,
  and enable periodic publication atomically enough for exact retry. Refuse source/state containment
  in either direction and refuse policy drift instead of editing an existing namespace implicitly.
- Make `sync-share` reconstruct the active owner from RecallRoot, bind the selected application-ready
  friend to its exact-v3 stable principal, prepare and client-sign only a required
  `sync.subscribe` grant, then add subscriber membership. A durable grant followed by deferred
  membership is safe and retryable because both checks remain independently mandatory.
- Recognize and refuse `read-write` rather than mislabeling two capability grants as a convergent
  filesystem. ADR 0271 freezes the per-file CAS, writer-branch, causal merge, conflict, tombstone,
  writable-projection, GC, revocation, and qualification work that remains.
- Extend the live automatic publisher/follower gates through managed creation and the exact
  read-only prepare/sign/commit ceremony. The complete owned registry passes 675 checks.

### Everyday one-writer synchronization automation

- Add local-control v1.44 operations and the owner commands `sync-auto-publish`, `sync-follow`,
  `sync-automation`, and `sync-automation-remove`. No peer framing or feature bit changes.
- Persist one strict stable-device-signed generation per namespace. Publisher policies bind a
  canonical absolute path; follower policies resolve a live friend once and retain only its proven
  stable principal; removal writes a signed disabled tombstone.
- Run immediate reconciliation, bounded exponential retry, stale-generation fencing, and separate
  activation admission through the existing bounded sync worker. The Agent service thread performs
  no scan, hash, network, or activation work.
- Reuse existing HEAD-last publication, exact-v3 publisher authorization, accepted-HEAD, and
  exact-token activation transactions. Received bytes still grant no activation or execution
  authority.
- Qualify automatic duplicate-safe publication and signed-policy restart locally, plus one complete
  v3-proven stable-principal follow, paged-CAS convergence, HEAD-last acceptance, and exact verified
  activation with no manual pull/activate command. The complete owned registry passes 674 checks.
  Two-guest unattended restart and a long shadow mirror remain explicit gates before any
  Resilio-replacement claim (ADR 0270).

### Same-source exact-carrier content distribution

- Extend the existing local-control v1.43 routed atomic entrance so a repeated source selector means
  another distinct exact auxiliary carrier for the same stable principal and primary authority
  session. Ordinary `sync-pull-multi` still rejects duplicates; operation 90 encoding and all peer
  framing remain unchanged (ADR 0269).
- Select the complete repeated-principal carrier set atomically, refuse insufficient distinct ready
  workers, freeze every binding before HEAD dispatch, and fail the whole job on exact carrier loss
  without downgrade, reassignment, or post-HEAD rebinding.
- Correlate content terminals by the full authenticated carrier tuple rather than route-local
  friend/file numbers. The deterministic test and genuine VM gate now cover two isolated workers
  that both legitimately assign their peer `friend=0`.
- Add owner-private per-source-path requested-object, committed-object, and fetched-byte counters.
  These make positive path contribution and skew inspectable without copying content into evidence.
- Add `sync-content-same-source-multi-route-actual-tor` and strict raw/compact verification. Accepted
  proof `pair.iiuhmhy0` distributes six immutable objects across two exact Tor workers, accepts the
  original HEAD last, explicitly activates, and preserves a 15 MiB secret-free compact bundle.
- Keep whole-object placement distinct from same-session lane concurrency and byte striping. Default
  lane cap one, fail-closed loss, no automatic route count, and all framing remain frozen.
- The direct owned unit/integration registry now contains 670 checks; the default CTest surface
  remains 48 targets.

### Counterbalanced content lanes, restart recovery, and cap-two interactive SLA

- Counterbalance the stable-session `1/2/4/8` lane experiment with a genuine `8/4/2/1` order on
  direct UDP and forced TCP. Strict aggregation retains default one, recommends explicit cap 2 for
  efficient mixed/relay-heavy bulk, cap 4 for fixed direct UDP, and cap 8 only as a stress bound;
  automatic tuning remains unqualified (ADR 0266).
- Qualify fresh Ratox OPEN after reliable cap-8 completion as a separate lifecycle boundary. Both
  native carriers meet the ordinary five-second deadline on the unchanged Tox epoch and complete a
  fresh 40-sample terminal exchange without changing frozen Ratox framing (ADR 0265).
- Add `sync-content-restart-cap-2` and `sync-content-restart-cap-4`. Four two-guest Sandwurm cells
  kill only the subscriber Agent with exactly two or four non-root object lanes live, then preserve
  the exact complete CAS inventory, fence the old signed attempt set, and converge plus activate
  only through a distinct pull after two-sided recovered authority (ADR 0267).
- Classify c-toxcore's private pre-rename
  `.iotox-REST.REQUEST_ID.part.part-XXXXXX` files as transport residue rather than CTA1 progress.
  Startup accepts only the exact private canonical grammar, removes and fsyncs it after signed
  journal loading, and fails closed on malformed or unsafe entries. Partial-prefix resume and
  same-job continuation remain unclaimed.
- Retain independently replayable compact restart proofs `pair.8j7v2irm`, `pair.9q9hsx40`,
  `pair.8ulddb9t`, and `pair.ol5goyug`. All four bind the same final-tree binary, contain no private
  keys or payload content, and pass strict raw/exported replay. Default lane cap one and all peer
  framing remain unchanged.
- Add `sync-content-ratox-cap-2-sla`, keeping one 960-sample Ratox attachment and one Tox epoch live
  across ordered content caps `1/2/4/8` under the existing 4 Mbit/s subscriber shaping. Both guest
  and host verifier independently enforce the predeclared cap-two bounds: at least 40 exact-overlap
  samples, p50/p95/p99/max at most 250/500/1,000/1,500 ms, and owner-queue p95 at most 10 ms
  (ADR 0268).
- Qualify explicit cap 2 as the bounded native interactive-bulk construction profile. It passes
  every frozen bound over direct UDP and forced TCP while improving rate over cap 1 by 2.75% and
  9.92%. Caps 4 and 8 miss the p95 ceiling on both carriers; cap 4 adds only 1.11%/2.86% rate over
  cap 2. Default one, frozen framing, and manual selection remain unchanged.
- Retain independently replayable 18-file compact proofs `pair.rpblreul` and `pair.rwiyixfh`.

### Bounded same-source content lanes and scaling evidence

- Add `--max-sync-content-lanes N` (`1..64`, default `1`). Signed namespace
  `maximum-lanes` and `maximum-outstanding-requests` can only reduce the process ceiling; root and
  signed-HEAD phases remain serial while independently digest-addressed pages/chunks may overlap
  with exact request/FileId/CTA1 attribution (ADR 0262).
- Make content status multi-lane-aware and fail the whole pull on one permanent lane/source/storage
  error after attempting to cancel and durably fence every sibling. Deterministic coverage proves
  out-of-order completion, immediate slot refill, and sibling cancellation without changing peer or
  local-control framing.
- Qualify two same-source object lanes over genuine direct UDP and forced TCP in compact Sandwurm
  proofs `pair.895m5lwy` and `pair.bcecui0l`.
- Add neutral `sync-content-lane-science` runner, verifier, and compact-export support. One stable
  cap-8 process/session consumes the same deterministic high-entropy 8 MiB/24-chunk revision from
  four isolated namespaces with signed effective caps `1/2/4/8`, retaining per-phase duration,
  bytes/second, coherent maximum lanes, CPU, HWM, transport iterations, and exact resource digests.
- Direct UDP records 378,035/325,771/399,838/443,138 B/s. Forced TCP records
  301,423/375,833/420,481/415,072 B/s, identifying cap 4 as the smallest observed relay-heavy knee
  while cap 8 adds no TCP gain (ADR 0263). Keep default one; repetition and competing Ratox-latency
  evidence remain required before accepting a bulk profile or automatic tuning.
- Retain independently verified compact science proofs `pair.amcrp0_3` and `pair.805kzu4a`; each
  contains 14 secret-free files and allocates 188,416 bytes.
- Add `sync-content-ratox-latency-science`. One 720-sample Ratox attachment remains on the same
  authenticated Tox epoch across content caps 1, 4, and 8; cap 2 is a transfer-only pause. The
  verifier independently reconstructs overlap and p50/p95/p99/max latency, binds one session and
  timeline digest, and requires exact Ratox-active resource boundaries (ADR 0264).
- Direct UDP records cap-1/4/8 content rates 385,683/440,555/374,090 B/s and Ratox p95
  258.241/815.429/880.790 ms. Forced TCP records 259,942/418,050/397,866 B/s and p95
  412.735/525.400/739.272 ms. Cap 8 regresses against cap 4 on both routes; keep default one and
  treat cap 4 only as an explicit direct-UDP bulk setting. ADR 0266 now supplies the counterbalanced
  cap-2 mixed/relay-heavy recommendation.
- Retain 18-file, 270,336-byte compact proofs `pair.af873531` and `pair.a3nglkh3`. Fresh Ratox OPEN
  admission and multi-lane daemon restart are now qualified separately by ADRs 0265 and 0267;
  persistent Ratox at cap 2 is now qualified separately by ADR 0268. Frozen Ratox framing is
  unchanged.

### Exact auxiliary carriers and actual-Tor multi-source content

- Add local-control v1.43 operation 90 and
  `sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]`.
  Every source keeps an independently authenticated primary authority session; Agent binds its
  content lane to one exact ready native/Tor/I2P route-worker incarnation before releasing the
  primary HEAD request (ADR 0258).
- Permit only frozen content object/availability types 28--31 on a bit-29-negotiated worker. HEAD,
  activation, authority, coordination, and reconstruction remain in the parent Agent. FileId, CTA1,
  offer, terminal, cancellation, and retirement retain the exact carrier fence.
- Add deterministic two-source auxiliary-carrier convergence, wrong-principal and post-HEAD bind
  refusal, exact loss fail-closed behavior, and route-worker content-frame negotiation coverage. The
  owned registry now contains 665 checks.
- Finalize worker bit-29 construction after both content services exist but before worker startup;
  changing the gate after `start()` is refused. This repairs a real fail-closed VM result in which
  primary Agent advertisement was correct but workers had frozen `content-negotiated=0`.
- Qualify the one-source mixed-route product path in two simultaneous Sandwurm VMs. Direct-UDP
  primary authority and signed HEAD stay native while one exact `tox/tor` worker carries a paged
  4 MiB revision through two real Tor 0.4.8.11 processes in one pull with zero failures or
  reassignment. Compact proof `pair.fahovlrg` independently verifies (ADR 0258).
- Keep the network claim split: this is actual-Tor content-carrier evidence, not a claim that the
  authority session used Tor or an anonymity result.
- Expose one bounded owner-private `content-source-job=` record per pull source, binding its stable
  principal and primary authority route to the exact primary or auxiliary carrier incarnation. This
  makes distinct-carrier contribution independently inspectable without changing peer framing.
- Qualify genuine complementary multi-source content over two exact actual-Tor worker identities.
  Native primary sessions retain both publishers' authority and the original HEAD; one atomic pull
  receives five objects from the primary source and one from the secondary, verifies and activates
  the 4 MiB revision, and records zero pull failures. Both TAP captures contain mixed native/proxy
  traffic with zero unexpected-context packets. Compact proof `pair.j0z04_2i` independently
  verifies (ADR 0259).
- Make strict CLI worker preflight apply exact per-worker bootstrap/TCP-relay replacements before
  validating the effective route. CLI and runtime construction now share the same transformation;
  empty lists inherit and nonempty lists replace the primary template. The multi-source VM gate
  exposed this mismatch before authority readiness.
- Teach the compact exporter the new scenario and self-test exact completion, packet-capture,
  containment, and Tor-control inventory. The verifier keeps an independent exact-inventory check.

### Selected content-source loss and atomic recovery

- Add owner-local `sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]` over local-control v1.41
  operation 88. The Agent authenticates every source and registers all auxiliaries before it can
  dispatch the primary HEAD, eliminating the retry race between a cached root manifest and a later
  `sync-source-add`. Admission or dispatch failure cancels and cleans the new job (ADR 0256).
- Add the destructive three-agent/two-VM `sync-content-multi-source-loss` direct-UDP gate. It stops
  the selected secondary after positive object work, requires the first job to fail with staging,
  accepted HEAD, and activation fenced, then restarts the same identity at a higher epoch and
  converges only through a distinct explicit atomic pull.
- Retain two verified objects and 528 verified immutable bytes from the failed attempt without
  retaining ambiguous transfer state. Both sources answer four exact availability windows and
  contribute objects to the replacement job before HEAD-last acceptance and explicit activation.
- Preserve the local-publisher writer guard. The construction replica HEAD is held out of the
  secondary's publication tree during cold start and explicitly reinjected after readiness; durable
  authenticated replica-head persistence remains a separate gate rather than being mistaken for
  local authorship.
- Retain secret-free compact proof `pair.xujufman`; both its 2.4 GiB raw source and 180 KiB allocated
  export pass strict replay with the same binary and receipt commitments.

### Exact multi-source content product gate

- Add owner-local `sync-source-add JOB_ID FRIEND` over local-control v1.40 operation 87. Every added
  peer must negotiate content-v2 and independently satisfy exact-v3 `sync.publish` plus namespace
  writer membership; the original source's signed HEAD remains frozen and activation authority is
  unchanged (ADR 0254).
- Consume exact sparse availability windows in the live content subscriber, bind each selected
  object request/FileId/CTA1/terminal chain to its chosen primary peer, and retain the one-source
  fast path. Status exposes bounded source and availability request/result counters.
- Add deterministic end-to-end convergence from two complementary authenticated stores. Both
  providers contribute real availability and object traffic before the byte-identical artifact is
  reconstructed and the original HEAD is accepted last. The owned registry now contains 660 checks.
- Add the genuine three-agent/two-VM `sync-content-multi-source` Sandwurm gate. Accepted direct-UDP
  compact proof `pair.u80_yp7r` binds two live authorized sources, four exact availability requests/
  results, positive object traffic from both, whole-artifact reconstruction, HEAD-last acceptance,
  and explicit activation (ADR 0255).
- Correct the lab's logical-versus-physical content assumption: four logical chunk positions contain
  only two distinct physical chunk digests, so complementary stores are partitioned by authenticated
  digest identity and evidence counts logical occurrences separately.
- Retain forced TCP as an explicit failed gate. One common discovery fixture plus two independently
  keyed publisher-specific relays produces four stable relay sockets and confirms the primary
  friendship, but the secondary friendship does not confirm within the bounded 900-second window.
  The harness and strict verifier preserve that boundary without claiming a universal c-toxcore
  limit or treating transport sockets as authenticated sessions.

### VM-qualified Tox/I2P product route

- Promote `tox/i2p` from reserved to the canonical VM-qualified spelling for the already qualified
  strict SOCKS-to-SAM route. Preserve signed route-set-v2 class 3, local route-constraint byte 4,
  `device.tox-i2p.toxsave`, framing, authority, and fail-closed provider policy; retain
  `tox/i2p-construction` as a deprecated input/reproduction alias (ADR 0253).
- Add source-linked `client-tox-i2p` and `device-tox-i2p` Sandwurm configurations plus production
  route support in the runner, strict verifier, compact exporter, operator wrapper, and real-peer
  smoke. Historical construction bundles keep their original labels.
- Accept raw and 1.2 MiB secret-free compact proof `pair.btm5vwr9`. Two Cloud Hypervisor guests pass
  through two pinned i2pd routers and three persistent fronts while both TAPs show zero native UDP,
  zero direct bootstrap/peer packets, and only TCP to the numeric bridge adapter.

### Genuine content-v2 product gate

- Activate the bounded content-v2 publisher/subscriber in the Agent only after startup recovery and
  authenticated live-graph validation. Route canonical packets, exact FileId offers, and terminal
  truth through one primary-carrier job; accept signed HEAD last; require exact-token activation;
  and add signed reachability, repair quarantine, and quarantine-only GC (ADR 0251).
- Add the 4 MiB paged `sync-content` Sandwurm scenario. Independent source-linked c-toxcore guests
  pass in one pull with zero failure over direct UDP and forced TCP and agree on the exact artifact,
  root-manifest, signed-HEAD, CAS, and activation truth (ADR 0252).
- Retain the ordered four-chunk/one-page/four-object completion record in compact pair evidence and
  make strict replay bind it to the manifest. Classify only forced-TCP content authority startup in
  the existing 480-second slow-construction window after a calibration reached both ready markers at
  the old 240-second edge.

### Route identity privacy boundary (rev0045)

- Add the lab-only `tox/i2p-construction` spelling while keeping production `tox/i2p` unsupported.
  Reuse the strict numeric SOCKS/bootstrap/relay TCP-only contract, route-scoped I2P savedata, route
  health, and route-worker validation without mislabeling I2P experiments as Tor.
- Add an owner-side persistent I2P SAM service forward. Exact DEST/SESSION/FORWARD process tests
  cover canonical padded Destination keys, mode-0600 restart reuse, `SILENT=true` raw loopback bytes,
  loss/recovery, no-clobber audit, and content-free commitments (ADR 0213).
- Let the genuine real-peer smoke accept explicit strict route inputs; routed runs require fresh
  identities so the reusable native key cache cannot collapse route contexts. Resolve the SPDX
  inventory from either an explicit path or the Nix source-linked package layout.
- Preserve and falsify the early Tox/I2P construction hypotheses. Pin only c-toxcore's combined
  SOCKS/SAM/relay establishment timer at 120 seconds, name the provider
  `iotox-file-rr1-tcp-connect120`, select i2pd's interactive streaming profile, and audit exact SAM
  setup microseconds. The later three-front control proved no onion-lifetime patch was needed;
  request cadence, onion state, and established-carrier ping loss remain upstream-exact (ADR 0214).
- Preserve real numeric Tox node addresses across I2P maps and require at least three explicit
  bootstrap/relay records in fresh construction smoke. Two fresh source-linked peers now pass the
  complete friendship, authority, text, durable-command, exact-file, restart, ownership-transition,
  and removal/re-add lifecycle through two live routers and three persistent service fronts
  (ADR 0215).
- Add the fail-fast three-front I2P topology supervisor and Sandwurm baseline route. Pin and hash
  i2pd 2.60.0 plus its 315-file source tree, boot two source-linked KVM guests, retain both TAP
  captures, and export only content-free topology/audit commitments. Accepted compact proof
  `pair.k_vopzf5` reaches TCP friendship, canonical session confirmation, and bidirectional text
  while every guest IPv4 packet is TCP to the bridge adapter and no UDP/direct-peer packet appears.
  Bound initial `denied-stream` convergence retries and require all three Destinations to admit
  before the topology can pass (ADR 0216).
- Add the `i2p-router-restart` Sandwurm gate. Pin the source-matched 21-file i2pd certificate bundle,
  require signed reseed verification, preserve the bridge listener across client-router loss, and
  distinguish adapter/SAM state from c-toxcore-authoritative offline. Accepted compact proof
  `pair.v_11i2me` replaces the exact router over its private datadir, advances both guests from
  authenticated epoch 1 to 2, exchanges fresh text bilaterally, and retains TCP-only/no-fallback TAP
  containment. Calibrate bounded outage retries without requiring c-toxcore to reopen every
  redundant bootstrap front after connectivity returns (ADR 0217).
- Add the `i2p-service-restart` Sandwurm gate and exact Linux router-socket attribution. Accepted
  compact proof `pair.6rrdsdc_` leaves both i2pd processes, SAM listeners, the client adapter, and
  egress shims live while replacing all three server fronts. Replacement audits load the same three
  mode-0600 Destination keys, both guests advance authenticated epoch 1-to-2 and exchange fresh
  text, and TCP-only TAP containment remains intact. The compact exporter/verifier now binds the
  exact seven-audit inventory (ADR 0218).
- Add `sync-tree-route-private-actual-i2p-payload` and principal-specific route-readiness evidence.
  Accepted compact proof `pair.5xjf2n4d` assigns one exact 131,369-byte signed tree to the
  authenticated actual-I2P member with zero reassignment while native fallback remains ready.
  Rejected 512 KiB and 4 MiB attempts expose the whole-object carrier-epoch boundary and make
  digest-bound auxiliary chunk/range plus signed privacy-class failover policy the next gate
  (ADR 0219).
- Correct compact pair export so actual-I2P payload scenarios retain I2P pcaps, topology, and audits
  instead of selecting Tor artifacts. Register a reciprocal I2P/Tor evidence-selection regression;
  the default suite now contains 46 CTest entries.
- Separate initial sync placement from carrier-loss policy. Add explicit
  `--sync-route-failover available|fail-closed`, status policy/blocked-job truth, and a full-Agent
  first-byte-loss gate proving fail-closed retains the original awaiting job with zero reassignment.
  Actual-I2P payload qualification now selects this safer local prerequisite (ADR 0220).
- Freeze `available|fail-closed` on each admitted sync pull instead of consulting process policy
  after carrier loss. Add backward-compatible local-control v1.38 operation 85, the optional
  `sync-pull FRIEND NAMESPACE [available|fail-closed]` CLI value, per-job status truth,
  conflicting-retry rejection, and a full-Agent opposite-default loss proof (ADR 0221). Peer
  framing remains unchanged; signed route-class intent remains open.
- Add per-pull `any|tox/native|tox/tor|tox/i2p-construction` carrier constraints, local-control
  v1.39 operation 86, exact constructed-worker filtering at initial placement and replacement,
  named-class no-primary-fallback behavior, status truth, and selector/full-Agent coverage. The
  actual-I2P guest now explicitly requests `fail-closed tox/i2p-construction` (ADR 0222). This is an
  owner-local prerequisite; signed route-class authentication remains open.
- Distinguish range intent from a concrete live range lane. A carrier loss during the prerequisite
  manifest now follows whole-object cleanup; only an exact lane with an attempt and bundle size may
  take range cleanup. `sync-status` exposes those local-only facts, and deterministic tests prove
  prerequisite loss, strict cleanup, restart, and genuine range loss independently.
- Extend `iotox routes` with one content-free auxiliary-worker line containing exact key/incarnation,
  constructed network class, transport and application state, reciprocal binding state, online
  epoch, range negotiation, sync frame counters, and last failure. This is local observability and
  does not alter frozen peer framing.
- Add and accept `sync-file-range-actual-i2p-loss` (ADR 0228). Compact proof `pair.a9zwongf` stops
  only the client router after 86,373 bytes of a concrete 1 MiB range, proves empty staging, one
  fail-closed block and zero reassignment, recovers the same signed member with zero worker restart,
  then completes only after explicit old-job cancellation and a distinct fresh job. The new job
  fetches the complete 1 MiB range, reuses the verified remaining 3 MiB, reconstructs the exact
  4 MiB artifact, accepts its linked HEAD last, and explicitly activates it. Raw and secret-free
  compact forms independently pass.
- Correct the strict verifier's router-restart classification for the range-loss scenario and bind
  its pre-fault position to the scenario's fetched range size. Self-tests reject native
  reassignment and a position at or beyond the complete bundle.
- Reuse an exact durable manifest when an explicit fresh range job follows loss (ADR 0229). Local
  size/digest/shape verification occurs under the namespace transaction and releases that
  non-recursive lock before scheduler assignment. Malformed existing bytes fail locally rather than
  being overwritten; a valid object triggers range planning directly from the HEAD result. No wire,
  authority, digest, acceptance-order, activation, or failed-range-retention rule changes.
- Accept compact proof `pair.ip5q0at9`: after 71,292 live range bytes and exact I2P router recovery,
  a distinct same-carrier job requests one object, commits two, reuses the 786,496-byte manifest
  locally, fetches the complete 1 MiB range, reconstructs the exact 4 MiB target from 3 MiB basis,
  and explicitly activates it. This removes 786,496 bytes (42.86%) from the qualified fresh-recovery
  transfer while retaining zero failed-prefix bytes. Raw and 23,199,744-byte compact proofs pass.
- Resume one bounded same-process/same-job/same-carrier range retry from an exact private prefix
  (ADR 0230). Initial seek-capable range receives now stage in the canonical attempt inode from byte
  zero; receive-ceiling deferral preserves and revalidates the exact empty inode. An incomplete
  attempt may finish/fence, hand its strict prefix to a fresh durable attempt, allocate a fresh
  message ID/FileId, and seek before suffix-only receive. Mismatch falls back to discard.
- Add `range-retained-bytes`, `range-resumed-bytes`, and `range-retention-fallbacks` status/evidence
  alongside the existing discarded count. Deterministic coverage proves a 524,288-byte handoff and
  an admission deferral. Clean compact Sandwurm proofs `pair.cj5y5vgt` and `pair.qeb99i4o` retain and
  resume exactly 15,081 UDP and 24,678 TCP bytes with zero discard/fallback, full 4 MiB verification,
  HEAD-last acceptance, and explicit activation. Carrier-loss, cross-carrier, explicit-new-job, and
  restart range-prefix continuation remain excluded.
- Extend exact bounded-range prefixes across authenticated native auxiliary carrier loss under the
  existing `available` policy (ADR 0231). Loss retires transport truth, finishes and fences the old
  signed attempt, hides its FileId, and leaves one inert lane; a distinct range-capable carrier gets
  a fresh attempt/message/FileId and atomically inherits only a strict positive prefix. Duplicate
  loss and stale old offer/result/terminal truth are inert. Cleanup failures retain owned state for
  terminal disposal. Fail-closed policy still discards and blocks.
- Add the default-off `--qualify-route-stop-file-bytes N` selector so byte-threshold route science
  can target an exact complete transfer size instead of consuming its one-shot fault on a manifest
  prerequisite. The new `sync-file-range-route-loss` gate selects the 1 MiB bundle and passes direct
  UDP `pair.urbhf0je` at 283,797 retained/resumed bytes and forced TCP `pair.n76biwao` at 293,394,
  each with zero discard/fallback and one loss/reassignment/stale-terminal/recovery before exact
  reconstruction, HEAD-last acceptance, and activation.
- Extend deterministic range-loss coverage through a second sequential carrier death. A 50% prefix
  moves from the first to the second attempt, grows to 75%, then moves to a third attempt; both old
  FileIds, attempts, offers, terminals, and duplicate-loss observations stay fenced. Cumulative
  retained/resumed accounting matches, no retry budget is consumed, and final verification remains
  unchanged.
- Add a bounded default-off `--qualify-route-stop-count 1|2` laboratory seam and the
  `sync-file-range-repeated-route-loss` Sandwurm gate. Count two will not stop the replacement until
  the first savedata identity has spent one recovery unit and returned to the ready set; after the
  second migration, ordinary terminal convergence releases the second recovery. The fixture shapes
  the 1 MiB range at 256 kbit/s. Between faults, the qualification-only subscriber holds the bounded
  reassigned request frames until the stopped identity is authenticated and ready, then records the
  exact release; it no longer depends on a host packet-size classifier or a timing race against
  successor completion. No product default, route policy, or wire byte changes.
- Accept the repeated-loss gate on both native carriers (ADR 0232). Compact direct-UDP proof
  `pair.le38qcl5` retains/resumes 542,916 cumulative bytes; forced-TCP `pair.8u14ddcy` retains/resumes
  564,852. Each records two losses/reassignments/stale terminals/recoveries/worker restarts, zero
  discard/fallback/final partials, one qualification-frame release, exact 4 MiB reconstruction,
  signed HEAD-last acceptance, and explicit activation.
- Add and accept the 15/16 late-loss gate (ADR 0233). It binds a 983,040-byte threshold plus
  256-kbit/s selected-range shaping, then requires one fresh-carrier suffix receive. Compact UDP
  `pair.tev4u3rs` retains/resumes 984,378 bytes; TCP `pair.1z7_d0jn` retains/resumes 995,346. Both
  record one loss/reassignment/stale terminal/recovery, zero discard/fallback, and full exact
  reconstruction/activation. The first unshaped calibration completed before the threshold could be
  observed and was rejected. Repeated-late/final-chunk races, three-plus loss, process restart,
  explicit-new-job prefix reuse, and multi-source striping remain unqualified.

- Freeze independent random Tox savedata identities for native, Tor, and future I2P contexts while
  keeping the stable device identity, RecallRoot ownership, authority ledger, and durable
  application state above route replacement (ADR 0198).
- Make the no-override CLI defaults route scoped: `device.toxsave` for native,
  `device.tox-tor.toxsave` for Tor, and a reserved `device.tox-i2p.toxsave` for I2P. Explicit
  `--state` or `IOTOX_STATE_PATH` remains an operator linkability choice. Add the 592nd owned C++
  check for exact route defaults and override behavior.
- Record the route-binding-v1 disclosure boundary instead of overstating it: the existing auxiliary
  exchange carries the complete signed roster and remains a same-context construction. Mixed
  native/privacy operation requires authority-confirmed primary inventory delivery plus a future
  member-scoped auxiliary proof; no public stable-principal route lookup is permitted.
- Implement that default-off v2 construction codec without changing v1: feature bit 28 requires the
  authority/v1 lineage; message type 26 carries the signed roster only with an exact live primary
  authority snapshot; type 27 carries a fixed 256-byte member, transcript, and full-inventory-digest
  proof. Stale authority epochs, unlisted auxiliary peers, same-generation inventory forks, and
  altered frames fail closed (ADR 0199). The owned C++ registry is now 594 checks.
- Complete the default-off live v2 path behind `--enable-private-route-bindings`: freeze one primary
  send per authority epoch, admit bounded exact-replay inventory with process-lifetime generation/
  digest high-water, hand only current inventory to matching workers, exchange fixed member proofs,
  and withdraw worker work/readiness when the primary authority edge disappears (ADR 0200). Direct
  registry, worker-provider, and full-Agent provider tests bring the owned registry to 597 checks.
- Bind repeatable `--route-worker-network KEY=tox/native|KEY=tox/tor@NUMERIC_PROXY` overrides to
  exact signed auxiliary members. Validate the complete derived topology before starting any worker;
  strict Tor members require TCP plus an explicit numeric proxy and cannot inherit native fallback.
- Close the private-context adoption race found by the first genuine mixed run. Retain one inert
  early reciprocal member proof across primary inventory handoff, reverify it against the exact new
  context, and discard a stale proof without authority so a fresh one can arrive. Extend the owned
  registry to 598 checks (ADR 0201).
- Accept two-guest `sync-tree-route-private-mixed` compact proof `pair.z948jeii`. Both roles combine
  native primary/native bulk/strict generic-SOCKS bulk identities, reach two ready routes, and
  converge one signed 4,194,389-byte tree. Four proxy requests are admitted and zero denied; every
  TCP packet stays on the configured local endpoints while native UDP/related ICMP remain explicitly
  non-contained. This is generic-SOCKS mixed-context evidence, not actual Tor or anonymity.
- Teach the guarded workspace cleaner to recognize only exact immediate
  `.sandwurm/iotox-device-repair.*` postmortem roots, cover the class in its offline self-test, and
  reclaim the reviewed four raw pair roots plus repaired disk copy after compact verification.
- Add bounded exact-key `--route-worker-bootstrap` and `--route-worker-tcp-relay` replacement lists.
  They let a Tor auxiliary use independently reachable public numeric Tox records while the native
  primary/workers remain pinned to private fixtures, without adding deployment endpoints to the
  signed route inventory. All records are joined to an explicit network override and every derived
  topology still validates before the first worker starts (ADR 0202); the owned registry remains
  598 checks.
- Construct and accept the first two-IoTox actual-Tor auxiliary-route cell. Two source-linked
  Sandwurm guests keep
  native primary/control routes on the local fixture while each exact-key Tor worker uses a
  separate Tor process, source-only SOCKS policy, control socket, and circuit population. The
  strict offline verifier reparses authenticated STREAM/CIRC evidence, exact guest-source/target
  joins, Tor-owned public-socket commitments, configuration commitments, and both TAP captures
  before it can accept private-v2 readiness and signed 4,194,389-byte tree convergence. Accepted
  compact proof `pair.2mycvy9n` records two successful target streams and a distinct three-hop
  `CONFLUX_LINKED` circuit per role, 583/531 role-specific proxy packets, and zero unexpected
  context packets. The operator must supply the public IPv4 Tox record explicitly. Object-byte
  attribution to Tor remains a later gate (ADR 0203).
- Construct a distinct actual-Tor payload-attribution cell. It binds the founding reusable client
  route-key ordering, assigns the lowest exact auxiliary key to Tor in both guests, and requires the
  completed sync job's carrier commitment to equal that Tor member with zero reassignment. This is
  a fail-closed qualification seam, not a production route-force option.
- Make initial sync-pull admission evidence-bearing after a transient pre-job local-control rejection
  exposed the old harness's discarded stderr. Retry the idempotent operation for at most 120 seconds,
  retain attempts/failures plus a content-free first-error digest in passing or failure receipts, and
  bind those values through the aggregate manifest and strict verifier. Add a runner regression for
  digest-indexed guest-receipt aggregation.
- Accept actual-Tor payload compact proof `pair.lzsyitvy` from clean commit `38aa432`. The client
  completes the signed 4,194,389-byte tree on the exact Tor-member commitment with zero reassignment
  and one-attempt/zero-failure admission. Both independent Tor instances bind two successful exact-
  target streams to distinct three-hop `CONFLUX_LINKED` circuits; the client/device TAP captures
  contain 2,469/4,341 proxy packets and zero unexpected context packets (ADR 0204).
- Construct and accept the external actual-Tor process-loss cell. It waits for at least 65,536 object bytes on
  the exact Tor member, captures authenticated process/control/circuit evidence, kills only that
  host Tor process, requires one loss and native-member reassignment, then restarts the identical
  Tor binary and requires genuine carrier recovery with zero IoTox worker restarts. Move
  `auxiliary-recoveries` from the synthetic restart request to the production carrier-return
  lifecycle so the counter describes real transports as well. Accepted compact proof
  `pair.iompvehf` records the host `SIGKILL` after 74,034 Tor-carried bytes, one loss, one native
  reassignment, two stale terminals, one real Tor-carrier recovery, two ready bulk routes, and zero
  IoTox route-worker restarts. Three authenticated Tor phases and both TAP captures independently
  reverify with zero unexpected-context packets (ADR 0205).
- Extend the guarded workspace cleaner to exact immediate compact-pair exports. Pair IDs cited by
  tracked Markdown are immutable retention roots; only undocumented `pair.*` directories enter the
  normal bounded keep-count policy. Self-test the new confinement, reclaim the two reviewed private
  process-loss roots plus 28 superseded compact exports, and strictly reverify `pair.iompvehf`
  afterward.
- Construct the distinct actual-Tor Ratox process-loss gate. Both primary agents use independent
  real Tor processes and the reviewed public Tox record. After initial PTY progress the host kills
  only client Tor, requires heartbeat warning before authoritative offline, verifies one detached
  live host PTY, restarts the exact Tor instance, and permits only explicit higher-epoch resume of
  the same session/incarnation at generation 2. Strict proof joins three authenticated Tor phases,
  zero-daemon-restart process evidence, raw terminal/heartbeat captures, and TCP-only TAP
  containment (ADR 0206).
- Qualify that gate as compact proof `pair.2waqdpgk`. A real client Tor `SIGKILL` produces the
  warning-only heartbeat miss after 2.204 seconds and authoritative offline after 27.379 seconds;
  the device retains one detached PTY. Exact-session generation-2 resume succeeds after the same
  Tor instance returns under a distinct PID/control inode. Both IoTox daemon restart counts and all
  direct/UDP guest packet counts are zero. The 2.39 GiB private proof and 1.65 MiB secret-free
  compact proof independently pass strict verification.
- Construct the distinct actual-Tor Ratox duration/circuit-churn gate. One terminal performs 120
  one-second-paced heartbeat/PTTY exchanges while authenticated Tor control closes the exact client
  circuit after sample 20 and device circuit after sample 100. The verifier requires raw requested-
  close-to-replacement joins, unchanged Tor process/control identities, one contiguous Ratox
  session/byte timeline, zero daemon restarts, and strict TCP-only TAP containment. Live Sandwurm
  qualification remained pending at construction (ADR 0207).
- Preserve the first soak attempt as a rejected proof after the circuit selector encountered a
  non-application candidate before mutation. Join event-attributed guest streams to Tor's current
  authenticated stream/circuit inventories and skip irrelevant circuits; only a currently
  successful qualifying application circuit may be closed.
- Record the corrected live result instead of weakening it: closing the exact client application
  circuit leaves Tor and IoTox alive and produces a replacement Tor stream/circuit, but breaks the
  Tox TCP carrier. IoTox reaches authoritative offline and returns exact resumable error 4. Revise
  the gate to require two explicit higher-epoch resumes, generation 1 to 2 to 3, one preserved
  session/incarnation/remote PTY, and contiguous byte positions across all 120 samples.
- Record the complementary no-error attempt: after exact circuit replacement the controller emitted
  no `unavailable`, so a probe that only waited for loss timed out. Finalize a two-branch checkpoint:
  send a canonical post-replacement PING and accept only same-epoch/generation PONG continuity or
  exact `unavailable` plus higher-epoch explicit resume. The retained session/PTY/byte contract is
  identical in both branches.
- Reject the next live attempt at the device checkpoint when the verifier demanded a new Tor stream
  ID even though the attributed guest stream had moved to a distinct live circuit without closing
  its guest-to-SOCKS TCP connection. Revise the churn envelope to distinguish raw same-ID stream
  reattachment from new-ID stream reopening while continuing to require a distinct qualifying
  circuit and exact requested-close ordering.
- Reject a subsequent baseline at sample 14, before any deliberate mutation, when the peer went
  authoritatively offline through a public record no longer present in the contemporaneous official
  TCP-ready node inventory. Keep unplanned loss fatal and require a freshly reviewed numeric relay;
  this is relay-availability evidence, not permission to weaken the churn gate.
- Reject the next freshly routed run after it completed 120 samples and both circuit mutations but
  failed to seal the controller lifecycle because of an undefined serializer local. Snapshot the
  initial generation and byte positions explicitly, move lifecycle construction behind a pure
  helper, and exercise the complete envelope in the probe self-test; transport success without its
  required receipt remains a failed proof.
- Reject the following fully sealed 120-sample run during final Tor role attribution: both churns
  truthfully caused explicit resumes (epochs 2→3→4, generations 1→2→3), but the summary selected an
  earlier successful stream whose historical Conflux circuit was not yet linked. Select the newest
  successful stream backed by a qualifying current/event application circuit, skip irrelevant
  purposes/hop counts, and cover the rejection path in the runner self-test.
- Reject another transport-complete run when device Conflux reattached one established stream from
  circuit 23 to 24 without a second `SUCCEEDED` event. Add a v3 churn envelope retaining exact
  authenticated before/after stream and circuit inventories; require a different qualifying circuit,
  bind each inventory by path and digest, and use the eventual STREAM `CLOSED` circuit ID as raw
  corroboration for same-stream reattachment. Final role attribution may use a later raw circuit
  close carrying the post-build linked Conflux purpose.
- Accept actual-Tor Ratox churn compact proof `pair.k8o54n2v` from clean commit `77a0200`. One
  120-sample terminal remains exact across client same-stream reattachment in 123.813 ms and device
  stream reopening plus authoritative-loss explicit resume in 30.220 seconds. The lifecycle keeps
  one session/incarnation/PTY, advances generation only from 1 to 2 on the higher-epoch resume, and
  records zero Tor/IoTox/guest restarts. Both requested circuit closes, authenticated inventories,
  raw control events, and 5,823 TCP-only guest-egress packets independently reverify. The 2.58 GB
  private proof and 3.13 MB secret-free compact proof pass the same strict verifier (ADR 0207).
- Restore `verify-pair` wrapper parity for the three accepted private-route actual-Tor sync
  scenarios and enforce their `direct-udp` route constraint before dispatch. All three retained
  compact proofs pass through the public lab command again; a mismatched `tox-tor` invocation fails
  before verification.
- Repeat the frozen actual-Tor Ratox churn gate through a second current public Tox record. Accepted
  compact proof `pair.9cx0jels` completes 120 samples and two requested stream reopenings in 17.273
  and 17.174 seconds with same-epoch/generation attachment continuity, zero resumes, zero process
  restarts, and 5,890 TCP-only guest-egress packets. Together with `pair.k8o54n2v`, the evidence
  proves Tor `stream-reopened` can accompany either Ratox continuity or authoritative-loss explicit
  resume; Tor transition type remains evidence, never session authority (ADR 0208).
- Construct the next adversarial-route prerequisite as a separate bounded SOCKS5-over-SOCKS
  interposer. It preserves a reachable listener and open TCP streams while an explicit host-owned
  hold file stops relay bytes, then resumes them exactly. A process test binds the client, target,
  upstream source/destination, hold ordering, and byte-exact release without changing the frozen
  forwarder digest used by historical proofs. Live Tor/Ratox qualification remains separate
  (ADR 0209).

### Strict routed privacy boundary (rev0045)

- Construction-enable explicit `Tox/Tor` without changing the `Tox/native` default. Require one
  numeric SOCKS5 endpoint plus nonempty explicit numeric bootstrap and TCP-relay records; suppress
  compiled native catalogs and reject proxy/route confusion, hostnames, missing endpoints, and
  UDP-required auxiliary route members before durable/runtime mutation.
- Set c-toxcore UDP, local discovery, DHT announcements, and hole punching off; install SOCKS5; and
  disable native DNS before `tox_new()`. Keep TCP-only `tox_bootstrap()` for onion path nodes and
  `tox_add_tcp_relay()` for the carrier, with no native fallback.
- Add exact parser, capability, option-audit, invalid-topology, CLI, Agent, and reserved-I2P tests.
  Extend the mock option audit to bind proxy type/host/port and DNS state. The owned registry is 591
  checks.
- Add a bounded numeric-only allowlisted SOCKS5 lab forwarder and separate CTest process gate. It
  refuses domain-address requests and unlisted numeric targets while forwarding the exact admitted
  stream. Add offline self-tests for the operator-Tor runner and independent receipt verifier; the
  default CTest surface is now 34 targets.
- Add a repeatable source-linked local route gate. The pinned c-toxcore provider reaches TCP through
  only SOCKS5, owns no UDP or direct-relay socket, observes proxy loss, and recovers only after the
  same endpoint returns. Label this strictly as local SOCKS construction—not actual Tor, anonymity,
  public routed-network qualification, or Sandwurm packet containment.
- Retain its clean-source receipt and exact hashes. Initial TCP took 8.038 seconds, proxy loss took
  77.993 seconds to reach authoritative `offline`, and exact-endpoint recovery took 4.921 seconds.
  Record the slow loss signal as an M8 design input: route health/application liveness may be faster,
  but cannot falsify c-toxcore connection truth or reset a session epoch.
- Add a `tox-tor proxy-restart` two-guest Sandwurm cell and compact export. Accepted
  `pair.zyy913jf` establishes a confirmed session, offline observation, epoch-advancing proxy
  recovery, and fresh text; both TAPs capture 913 total guest-egress IPv4 packets, all TCP to the
  proxy, with zero UDP/direct packets. Both proxy incarnations admit exactly two allowlisted targets
  and deny zero. Preserve the strict nonclaim that this generic SOCKS forwarder is not Tor.
- Add an opt-in clean-source operator-Tor public-route gate and an independent canonical receipt
  verifier. Bind the exact Tor binary/version/digest, normalized loopback SOCKS/control policy,
  explicit current public numeric relay records, Tor-control stream-to-three-hop-circuit evidence,
  and exact IoTox/Tor Linux socket ownership before and after Tor restart.
- Freeze c-toxcore's numeric-destination consequence: operator Tor uses explicit `SafeSocks 0`
  because `SafeSocks 1` rejects numeric SOCKS requests, while IoTox continues to prohibit hostnames
  and native DNS. The runner never downloads or substitutes a public node catalog.
- Record the first accepted actual-Tor sample from clean commit `3753422`. Tor 0.4.8.11 reached public
  Tox TCP in 9.124 seconds, became authoritatively offline 77.955 seconds after Tor death, remained
  absent across 30 checks/30.301 seconds, and recovered in 4.413 seconds on another three-hop
  circuit. IoTox owned no UDP or direct-relay socket.
- Freeze the operator-route claim and nonclaims in ADR 0191. Actual Tor/public relay routing is now
  bounded evidence for one host/relay/Tor/time sample; anonymity, two-IoTox actual-Tor application
  traffic, multi-relay/exit soak, private member-scoped cross-route proof, I2P, and non-sovereign
  infrastructure stewardship remain explicit M8 gates.
- Extend the guarded workspace cleaner with a dedicated `operator-tor` scope and offline CTest.
  Failed route roots are strictly named immediate children, mount/symlink/live-reference checked,
  retained newest-first by default, and removable independently of accepted canonical receipts.
- Add local-control v1.36 operation 39 and `route-health [FRIEND]`. Keep c-toxcore's exact carrier
  state separate from a bounded local SOCKS-listener connection and optional transcript-confirmed
  lossless peer echo. The content-free report exposes no endpoint, peer, nonce, or payload and
  cannot mutate the runtime carrier label or session epoch (ADR 0192).
- Qualify the observational seam through a real loopback listener/refusal test, Agent control-path
  echo with a byte-identical before/after protocol session, and both CLI forms in the separate
  whole-binary lifecycle fixture.
- Repeat the clean-source operator-Tor gate with four independently verified route-health phases.
  Local listener refusal appears 34 ms after Tor loss while c-toxcore still reports TCP;
  authoritative offline remains separate at 76.990 seconds; held outage and recovered three-hop
  route evidence still pass. This is a measured trigger seam, not an automatic recovery policy.
- Add strict canonical route-report parsing and `route-health-watch [FRIEND]`. The operator process
  maintains separate bounded local-boundary and application latches, defaults to three decisive
  failures and two recoveries, treats pre-send/unmeasured results as inconclusive, and can neither
  relabel the carrier nor mutate a session (ADR 0193).
- Make frozen Ratox v1 PING/PONG safe for indefinite sampling by reusing one exact PING identity per
  attachment. Prove 2,048 cycles without replay-store or message-ID growth, exact PONG correlation,
  real Agent/controller traversal, authoritative route-loss detach, exact generation-two resume,
  and post-resume heartbeat.
- Add one-second warning-only sampling to the installed terminal client. Three unanswered deadlines
  expose an unresponsive attachment without closing, detaching, changing carrier truth, or initiating
  recovery; a later PONG reports recovery.
- Add local-control v1.37 operation 84 and explicit one-shot `route-target-health`. The Agent selects
  only the first numeric TCP relay in its already validated Tox/Tor configuration, completes bounded
  SOCKS5 no-auth negotiation/CONNECT, sends no application bytes, and exposes only stage, typed
  result, RTT, reply code, and unchanged carrier truth (ADR 0194).
- Add a whole-binary strict-SOCKS process gate. It proves configured-target success, SOCKS reply-5
  target refusal, and local-proxy refusal while the mock carrier remains TCP; the independent proxy
  audit contains exactly the sole allowlisted target. Native routes reject the command. The owned
  registry is 591 checks and the default suite is 35 CTest targets.
- Extend the opt-in operator-Tor runner and independent receipt verifier for the next public gate.
  Authenticated extended Tor STREAM events must bind one NEW source through the same stream ID's
  SUCCEEDED event for each initial/recovered `route-target-health`, join it to configured relay zero
  and a built three-hop application circuit, and retain target success/proxy-loss observations
  separately. This constructs the
  gate; no new public-network result is claimed until it runs from a clean commit.
- Complete that public gate from clean commit `715e1c8`. Correctly correlate `SOURCE_ADDR` from
  STREAM `NEW` through the same ID's `SUCCEEDED`, accept only Tor's `GENERAL` and modern
  `CONFLUX_LINKED` application circuit purposes, record the exact purpose, and keep unrelated or
  unlinked purposes fail-closed (ADR 0195). Initial/recovered target CONNECTs took 266,385/237,701 us
  on distinct three-hop linked-Conflux circuits; proxy refusal appeared in 67 us, local route loss
  in 35 ms, authoritative offline in 74.602 seconds, and recovery in 3.913 seconds after a
  30.290-second held no-bypass outage. Replace the canonical receipt and independently verify it.
- Add the exact two-guest `ratox-route-impairment` scenario for direct UDP, forced TCP, and strict
  generic SOCKS. Each cell keeps one authority-bound Ratox attachment through 20 baseline, 80
  seeded `75ms +/- 15ms` plus 2% loss, and 20 recovered heartbeat-plus-PTY observations, with
  positive drops on both TAPs and unchanged session identity.
- Add an independent scenario analyzer and self-test. It binds exact source/binary identity, qdisc
  parameters, route containment, capture hashes, ordinals, clocks, sequences, and phase statistics
  across the three compact proofs. The default CTest surface is now 36 targets.
- Accept ADR 0196: carrier presence, Ratox heartbeat, PTY progress, and user-visible stall remain
  different facts. Partial impairment is warning-only and cannot mutate an authenticated terminal;
  exact total-loss retention/resume is the next recovery-policy gate. The strict SOCKS cell is not
  actual-Tor evidence.
- Add the exact two-guest `ratox-route-loss` scenario across direct UDP, forced TCP, and strict
  generic SOCKS. Seeded 100% loss on both TAPs must first miss a two-second heartbeat while the
  route remains confirmed, then produce authoritative offline plus local `unavailable`, retain one
  detached live PTY remotely, recover at a higher authenticated epoch, and resume the same
  session/incarnation at generation two and byte position two.
- Add strict raw/compact verification and a three-cell route-loss analyzer. The accepted cells warn
  at 2.139–2.248 seconds, become authoritatively offline at 30.322–31.145 seconds, and restore
  authenticated readiness in 0.769/2.155/4.996 seconds on direct UDP/forced TCP/strict SOCKS. The
  default CTest surface is now 37 targets.
- Accept ADR 0197. Heartbeat loss remains warning-only; authoritative peer-offline detaches the
  controller and retains the bounded host PTY; only explicit exact-session resume after a higher
  authenticated epoch may mutate attachment generation. Automatic migration remains unqualified.
  Compact proofs are `pair.0cnril1l`, `pair.qoty7j1x`, and `pair.8jjawnwp`.

### Sealed Linux service deployment (rev0044)

- Assign signed manifest payload kind 2 to `linux-service-v1` and bind it through canonical update
  policy v3 and stable-device-signed lifecycle state. Policy v1/v2, manifest kind 1, and historical
  opaque state remain byte-compatible and permanently inert; policy/state/kind drift fails closed.
- Add the default-off Linux service adapter. It reopens and rehashes the exact mode-`0400` selected
  slot into a mode-`0700` anonymous memfd, verifies the complete write/grow/shrink/seal set, and
  executes only that descriptor through an exact root/daemon-owned IoTox helper.
- Make the helper parent-death armed and no-new-privileges, start a fresh session/process group,
  require `close_range`, remove ambient descriptors, and expose only fixed release metadata plus
  readiness descriptor 3. Remote paths, argv, environment, extraction, scripts, and shell execution
  remain absent.
- Freeze readiness as `IOTOXSR1 || release-sequence-u64be`. Confirmation re-polls and requires the
  same live ready candidate plus the existing one-use local health token. Exec failure, malformed or
  closed readiness, early exit, and timeout sign rollback immediately and relaunch the prior
  confirmed service through the same sealed path.
- Add direct policy/manifest/state/slot/adapter tests and a genuine Agent E2E fixture that proves
  delayed-readiness denial, live promotion, exit-before-readiness rollback, and confirmed-service
  relaunch. Make a latent fork-inherited-response test exception-safe so a failing assertion cannot
  call `std::terminate` through a still-joinable responder. The owned registry is 584 checks.
- Add the `update-service` Sandwurm lifecycle and strict compact export. Direct UDP
  (`pair.pwpgv4si`) and forced TCP (`pair.rntpawny`) each prove authority-gated remote staging,
  pre-readiness service death, Agent death plus parent-death cleanup, health-expiry rollback, exact
  readiness/confirmation, confirmed-service recovery, six Agent restarts, three signed rollbacks,
  and a sealed image against one exact binary.
- Correct the release-signer rendezvous parser to consume the CLI's structured record and give the
  slow forced-TCP service cell a 480-second authority/960-second receipt bound inside its existing
  900-second guest deadline. Document the exact service contract and retain abrupt whole-VMM/host
  power loss, production whole-cgroup management, physical recovery/wear/secure-boot qualification,
  and hardware monotonic witnesses as explicit open gates.

### Release operations and recoverable retention (rev0043)

- Add explicit no-clobber `update-signer-keygen` and read-only `update-signer-show`. Creation requires
  an existing owner-private directory, synchronizes a mode-`0600` fixed Ed25519 identity record with
  an explicit release-role byte, and commits with Linux no-replace rename so it cannot adopt or
  overwrite a release secret. Device/release loaders and bundle creation reject role confusion.
- Add `update-policy-rotate` as a reviewable stdout transform. Every successful add/retire transition
  increments `signer-policy-epoch`; additions must be new, retirements active, mutation sets unique
  and disjoint, revoked keys cannot return, and at least one active signer remains. Document the
  routine two-epoch overlap/canary/retirement ceremony and emergency tradeoff.
- Add local-control v1.35 operation 83 and `update-gc dry-run|quarantine`. Stable-device-signed
  confirmed and live candidate slots are protected; only historical slots may move by canonical
  no-replace rename into a strict owner-private 256-file recovery directory. No purge or remote
  retention operation exists.
- Make partial quarantine a valid resumable crash state, synchronize both directories after each
  completed move set, and fail closed on unsafe entries, destination collisions, or exhausted
  recovery capacity. Quarantine frees the eight-slot hot bound without deleting historical bytes or
  lowering the confirmed release sequence.
- Extend direct state, CLI, local-control, and real-Agent tests through no-clobber key creation,
  two-epoch rotation, last-signer refusal, dry-run immutability, protected-slot selection, full-store
  recovery, deliberately interrupted quarantine continuation, and unsafe-entry refusal. The direct
  owned registry is 578 checks; executable boot/service deployment remains the final M7 target gate.

### Release signer revocation policy (rev0042)

- Add owner-local update policy v2 with a positive `signer-policy-epoch` and a bounded canonical
  `revoked-signer=` list. Policy v1 remains byte-compatible and is still emitted unless an epoch or
  revocation set is present.
- Require active and revoked release signer sets to be sorted, unique, nonzero, bounded, and
  disjoint. A revoked signer list without a signer-policy epoch is invalid, and canonical decode
  refuses active signers after the revoked-signer section.
- Extend `update-policy-template` and `update-policy-lint` with signer-policy epoch and revoked-signer
  visibility while rejecting duplicate epoch flags. Bundles signed by a retired signer remain valid
  only under old policies that still pin that signer; a rotated v2 policy rejects future staging of
  those bundles.
- Add direct policy/bundle and CLI coverage plus a libFuzzer seed for the v2 policy grammar. The
  direct owned registry is 577 checks. This does not add release-key operations, retroactive
  reinterpretation of already staged state, slot pruning, or executable OTA deployment.

### Remote signed update staging (rev0041)

- Add durable operation `update.stage` with exact 40-byte `ICQ2` request and 80-byte `IUS1`
  evidence. Preserve the frozen `ICQ1` read/presence records and existing 41-byte outer frame.
- Require bilateral `signed-ota-v1`, its durable/sync/range feature dependencies, a current
  transcript-bound `install.firmware` grant, and the receiver's exact current accepted HEAD before
  any effect. Advertise feature bit 20 and operation bit 3 only after local update construction
  succeeds.
- Reuse the signed command journal's commit-before-send/effect, peer/epoch/message replay identity,
  ownership-epoch authority binding, quotas, backoff, restart recovery, exact duplicate evidence,
  conflict refusal, and cancellation only before the first committed attempt.
- Serialize local and remote update mutation. Reverify the range-v1 artifact and release-signed
  bundle through the existing inactive-slot adapter; interrupted `STARTED` recovery adopts only the
  same already-staged immutable candidate. Remote apply, restart, health token, confirmation, and
  execution remain absent.
- Extend the structured CLI and private peer command FIFO with
  `command FRIEND update.stage HEAD_RECORD_HEX [PRIORITY]`; expose exact accepted-HEAD, release
  sequence, manifest, duplicate, lifecycle, and delivery evidence through the existing store views.
- Add canonical/malformed codec, executor, journal reopen/tamper, session dependency, CLI, mock-peer,
  exact duplicate, and real-Agent tests. The direct registry is 576 checks, the default surface is
  30 CTest entries, and the fuzz topology remains 12 targets with `ICQ2`/`IUS1` coverage added to the
  command fuzzer.
- Qualify the exact 4 MiB remote-stage-to-local-apply/restart/confirm lifecycle between simultaneous
  source-linked Sandwurm guests over direct UDP (`pair.6ebmw2t_`) and forced TCP (`pair.m_1e_fio`).
  Both compact cells prove bilateral feature selection and matching sender epoch/message ID, HEAD,
  manifest, payload, sequence, one restart, and health confirmation against one exact binary (ADR
  0186).

### Signed update health-gated rollback (rev0040)

- Freeze `signed-update-bundle-v1`: one canonical 320-byte Ed25519 manifest binds an inert payload's
  digest, byte count, namespace, target, release sequence, version, kind, and signer. Owner-private
  canonical policy pins the acceptable release keys, root, size, and health bound independently of
  sync publication authority.
- Add no-clobber local bundle creation, policy template/lint, strict stable-file verification, and
  same-user status/stage/apply/confirm controls. Staging joins one accepted sync HEAD to its exact
  artifact and independently verifies release intent before installing a mode-`0400` inactive slot.
- Add fixed-size stable-device-signed lifecycle state. Apply commits before switching the exact
  pointer; only a later durable Agent incarnation may confirm the one-use health token. Expiry,
  second restart, and both pointer/state crash-window directions recover by deterministic rollback;
  invalid slot/state/token evidence fails closed.
- Keep the eight-slot store non-destructive and fail closed on exhaustion. Keep feature bit 20 dark:
  remote `install.firmware`, executable deployment, key operations, hardware anti-rollback, power-cut
  behavior, and destructive retention remain explicit later gates.
- Add canonical/failure/process/real-Agent coverage, a dedicated manifest/policy fuzzer, and deep
  static analysis of both update units. The owned registry is 573 checks, the default surface is 30
  CTest entries, and the fuzz topology is 12 targets.
- Qualify one exact 4 MiB stage/apply/restart/confirm lifecycle between simultaneous source-linked
  Sandwurm guests over observed direct UDP and forced TCP. Compact content-free proofs bind the exact
  bundle, accepted HEAD, selected slot, Agent restart, health confirmation, and absent feature bit.

### Genuine immutable-object multi-route qualification

- Add `sync-tree-route-startup-admission`: cleanly restart the same subscriber Agent, hold one exact
  authenticated auxiliary route for 20 seconds, prove ten stable one-route observations, admit two
  independent 16 MiB tree jobs there, and require both to remain live and retain that carrier when
  the delayed route joins. Both revisions activate, adaptive selections remain exactly two with
  zero reassignment, work drains four-to-zero, and protected Ratox passes. Direct UDP
  (`pair.46f6td4j`) and forced TCP (`pair.2gvkqs6b`) pass strict raw and compact verification against
  one binary (ADR 0182). This qualifies controlled same-state Agent startup readiness, not a
  physically absent route at machine boot.
- Add `sync-tree-route-loss-admission`: fault one fixed-policy carrier with two active two-object
  jobs, require both to reassign, then start two new jobs while exactly one bulk route is ready and
  require both to select that survivor. All four revisions activate, work drains four-to-zero, the
  stopped identity recovers once, stale terminals remain fenced, and protected Ratox passes. Direct
  UDP (`pair.v3qc2kld`) and forced TCP (`pair.djhqe3we`) pass strict raw and compact verification
  against one binary (ADR 0181).
- Make auxiliary shutdown quiesce and join synchronous carrier service while the ordered event
  consumer remains alive; only then stop event draining and transports. This removes the clean-stop
  reverse liveness cycle exposed by a same-state Agent restart.
- Harden Sandwurm daemon restart readiness: require a correlated `status` round trip from a live
  non-zombie PID instead of accepting a socket-shaped pathname, and use the fault option's minimum
  valid one-millisecond delay for the immediate degraded-admission cell.
- Add `sync-tree-route-population-loss`: eight fixed-policy two-object jobs fill two four-job bulk
  routes as `00001111`; one exact carrier stops after positive progress plus 750 ms; all four
  affected jobs must reassign, all eight revisions activate, work drains 16-to-zero, stale terminals
  are fenced, the savedata identity recovers once, and protected Ratox remains below 250 ms. Direct
  UDP (`pair.j19_uhjj`) and forced TCP (`pair.rfnsjtqb`) pass strict raw and compact verification
  against one binary (ADR 0180).
- Make route eligibility reserve a job's complete remaining object work instead of testing one unit,
  preventing partial two-object admission during reassignment.
- Retry a pre-offer publisher `unavailable` result with bounded fresh message/FileId identity while
  preserving the scheduler attempt; stale old replies cannot fail the job, post-offer unavailable is
  a protocol error, and exhaustion remains terminal.
- Split auxiliary ordered event draining from receiver-carrier pause/resume service, retain worker
  incarnations explicitly across concurrent replacement, and release the supervisor snapshot mutex
  before synchronous exact sync-frame owner waits. This removes the TCP population-load control-plane
  liveness cycle without dropping required events or changing framing.
- Add bounded `--qualify-route-fault-delay-ms` to the default-off exact-byte fault seam. Freeze one
  route key, worker incarnation, receive position, and monotonic deadline at the observable arm edge;
  expose `qualification-fault-armed` without changing immediate historical behavior or production
  defaults.
- Add `sync-tree-route-cancel-race`. From one armed ≥65,536-byte receive, independently schedule
  exact-worker stop and ordinary cancellation at 500 ms; bind terminal outcome to reassignment and
  final-carrier truth; allow one exact cleanup retry only after typed transport unavailability; and
  require work two-to-zero, route recovery, and protected Ratox. Direct UDP (`pair.h6kg4fcr`) and
  forced TCP (`pair.z9egqd57`) both pass raw and compact verification as cancel-first with zero
  reassignment (ADR 0178).
- Add required-outcome `sync-tree-route-cancel-race-loss-first` without production changes. Stop the
  frozen worker 250 ms after arm and issue ordinary cancellation at 1,000 ms without polling for
  reassignment; require one loss, one fresh carrier, first-request cancellation, one recovery, and
  protected Ratox. Direct UDP (`pair.5gvh__p1`) and forced TCP (`pair.rxb2dsge`) pass raw and compact
  verification, giving both shared-arm authority outcomes genuine evidence (ADR 0179).
- Add default-off `--qualify-route-stop-after-cancel`. It stops only the exact auxiliary incarnation
  retained by the first settled cancelled pull, is mutually exclusive with the progress-first seam,
  forbids post-cancellation reassignment, and permits one signed-budget route recovery without
  reviving the pull.
- Add `sync-tree-route-cancel-loss` with positive exact-carrier progress, ordinary bounded
  cancellation and cleanup first, then one loss, zero reassignment, two fenced terminals, one
  recovery, restored two-route readiness, and protected Ratox. Direct UDP (`pair.yv4txv1r`) and
  forced TCP (`pair.m2396itk`) pass raw and compact verification against one binary (ADR 0177).
- Add default-off exact auxiliary readiness-order qualification without changing signed route or
  wire framing. `--qualify-route-first-worker` holds every other worker fail-closed until the named
  worker is application-ready and reciprocally bound; `--qualify-route-other-delay-ms` then provides
  a bounded observation window. Detached, negative, zero, over-limit, primary, and unknown targets
  fail before service.
- Add `sync-tree-route-startup-order` with explicit rolling primary-restart barriers, both exact
  corresponding worker orders, ten sole-ready samples per phase, final two-route readiness, signed
  4 MiB tree convergence, protected Ratox, strict compact verification, and content-free receipts.
  Direct UDP (`pair.nyiqwm8t`) and forced TCP (`pair.mdacri5e`) pass against one exact binary (ADR
  0176). Random timing distributions, fault races, common-link QoS, and relay diversity remained
  open at that boundary; ADR 0178 later closes one shared-arm race cell per carrier.
- Add offline creation-only `route-set-create` authoring for canonical stable-device-signed
  route-set-v1 artifacts. Require an existing identity, strict member grammar, two through sixteen
  members, canonical self-verification, owner-private no-replace output, and content-free reporting.
- Add a default-off exact-byte qualification seam that stops only the running auxiliary bulk carrier
  after real incoming object progress. Preserve the protected primary, fence the old attempt before
  fresh reassignment, and expose exact loss, reassignment, stale-terminal, and fault-position truth.
- Retire the stopped worker binding, spend its signed restart budget, reconstruct the same savedata
  identity under a fresh worker incarnation, and require reciprocal authentication before reporting
  recovery. Preserve all fault counters through recovery.
- Compose sync and Ratox authority in one least-privilege device-side `operator` grant containing
  only `sync.subscribe,interactive.terminal`; route membership remains transport rather than
  authority.
- Add the two-guest `sync-tree-route-loss` Sandwurm scenario, compact export, and strict verifier.
  Direct UDP (`pair.gqw1gzkd`) and forced TCP (`pair.9i62wfpa`) each observe one loss, one
  reassignment, two stale terminals, one recovery, exact tree convergence/activation, both bulk
  routes restored, and 40 protected Ratox samples below 250 ms (ADR 0169). Gate 3 is complete;
  fixed-versus-adaptive scheduler qualification is next.
- Begin Gate 4 without changing framing: add explicit `--sync-route-policy fixed|adaptive`, keep
  fixed stable-key selection as default, and make adaptive choices only at new admission or mandatory
  post-fence reassignment. Minimize exact admitted-work/signed-budget ratio, then restart history and
  route key; never migrate healthy work. Publish per-policy decision counters and cover the selector
  plus a real mock-backed two-worker adaptive loss/convergence path (ADR 0170).
- Add the genuine two-guest `sync-tree-route-balance` topology A/B. Begin the second two-object pull
  only after the first owns positive work on an eligible 8-slot route; require fixed to reuse that
  carrier and adaptive to select the idle carrier after a clean same-state Agent restart. Both phases
  require two decisions, exact object convergence, explicit activation, empty staging/work, bounded
  idempotent HEAD retry, and subsequent protected Ratox. Direct UDP (`pair.ul1pdq7m`) and forced TCP
  (`pair.pz9aapaj`) pass raw and compact verification with zero retries (ADR 0171). This qualifies
  load-aware topology, not throughput. Adaptive-first counterbalance cells direct UDP
  (`pair.hhmma27l`) and forced TCP (`pair.jn5aqbr6`) also pass against the exact binary, closing
  policy phase-order bias. Exact corresponding readiness order is closed later by ADR 0176; random
  startup/fault delays, larger-load fairness/resources, cancellation tails, and relay diversity
  remain open.
- Add `sync-tree-route-cancel` and qualify one live auxiliary withdrawal on direct UDP and forced
  TCP. Bind cancellation to positive progress on one exact worker, release work two-to-zero without
  reassignment, retain no accepted HEAD/activation/staging, and pass protected Ratox afterward (ADR
  0172).
- Add `sync-tree-route-population` with eight jobs per policy. Require fixed `00001111`, adaptive
  `01010101`, all-object convergence/activation, zero final route work, process-resource intervals,
  and protected Ratox on both carriers (ADR 0173).
- Add `sync-tree-route-concurrent-cancel`. Admit eight 262,211-byte artifacts as `01010101`, issue
  four simultaneous balanced withdrawals, preserve four survivor activations, and require work
  16-to-zero with no reassignment. Direct UDP (`pair.2laq038h`) and forced TCP (`pair.rlpuyjth`)
  pass raw and compact verification with 150 ms and 100 ms cancellation tails (ADR 0174).
- Require controller-side Ratox capability, authority, and carrier readiness for three consecutive
  samples after host restart. Retain the five-second `OPEN` deadline. Record two 1 MiB/job UDP cells
  that completed cancellation but missed `OPENED` behind the common shaped TAP as a separate
  physical-QoS/common-link gate; logical route protection is not NIC queue priority.
- Add `sync-tree-route-loss-cancel`. Force one active auxiliary loss after 65,536 bytes, require
  reassignment plus replacement progress, then cancel without a second reassignment and recover the
  stopped identity under one restart-budget unit. Direct UDP (`pair._0jwjfe6`) and forced TCP
  (`pair.o0ozmdw1`) pass with 80 ms cancellation tails and protected Ratox (ADR 0175).
- Permit the explicit qualification worker-restart seam after an auxiliary pull becomes
  either `complete` or `cancelled`; injected loss, one reassignment, stale-terminal evidence, and
  signed restart capacity remain mandatory. This does not add production automatic restart.

### Bounded long-session Ratox acknowledgements and 1,000-sample gate

- Add explicit `ratox-matrix-idle` and `ratox-matrix-bulk-{1,8,16,32,64}` Sandwurm scenarios with
  1,000 serialized complete-service samples. Preserve the 40-sample construction cells for fast
  regression coverage, bind sample count in pair manifests, and capture the ordered previous/current
  Ratox journal across its 1 MiB rotation boundary.
- The first two direct-UDP attempts completed all 1,000 renders but could not close: one permanent
  exact-control replay entry was consumed by every cumulative `OUTPUT_ACK`, exhausting the 128-entry
  session cache. Replace that unbounded-in-duration behavior with one attachment-local exact
  cumulative high-water fence while retaining never-evicted replay for side-effect controls
  (ADR 0154).
- Add a 1,001-ack deterministic regression with an exact-control cache of one entry. Require exact
  latest replay, conflict/backward refusal, and successful close. Strengthen pair verification so
  every controller row joins one same-session host stage/commit/output triple instead of accepting
  population counts alone.
- Add `export-pair` to the lab wrapper and teach the compact exporter/verifier about the named matrix
  cells. A clean-commit 12-cell R7 qualification and its two-role signed balanced bundle remain open.
- Correct the loaded-cell evidence boundary after a one-stream run reached 457 exact renders but
  waited on a stale coalesced status projection. Authenticated inspection now overlays live transport
  counters; a fixed 16-byte local operation supplies only the exact interactive execution/wait pair.
  Local PTY render is timestamped before evidence work, and probe failures reach the pair driver
  immediately (ADR 0155). Ratox v1 framing remains unchanged.
- Localize the remaining clean idle p95 miss to two independent 20 ms sleeps. While a Ratox host or
  controller transition is live, cap toxcore iteration and PTY service at configurable 5 ms defaults,
  wake local terminal work immediately, and restore the ordinary cadence when idle (ADR 0156).
  Publish active/idle state and retain process-incarnation-fenced CPU, memory, descriptor, I/O,
  context-switch, fault, and transport-iteration intervals for both Sandwurm roles.
- Accept exact-commit idle observations: direct UDP renders 1,000/1,000 at p50/p95/p99
  16.345/23.943/31.308 ms; forced TCP renders 1,000/1,000 at 88.810/99.010/128.852 ms. Their remote
  stage-to-output p95 values remain close at 12.764 and 11.515 ms, respectively, so forced-TCP idle
  latency is a separate route class rather than remote queue/PTY congestion.
- Preserve the first loaded rerun as a failed gate after 599 renders: saturated required file events
  could make the event consumer wait on Ratox service while the toxcore owner waited for event-queue
  space. Move only periodic Ratox progress and active-cadence selection to an independently woken
  Agent worker; retain the ordered event consumer, bounded required delivery, and sole toxcore owner
  unchanged (ADR 0157). Exact committed `bulk-1` requalification remains required.
- Retain the repaired direct-UDP `bulk-1` compact proof after 1,000/1,000 samples and clean close. It
  has zero 250 ms misses but fails the formal p95 and owner-p99 budgets at 71.698 and 7.114 ms.
- Test coalescing already-accepted inline file-send progress at 256 KiB high-water crossings. The
  exact two-guest A/B disproved that design: owner p99 fell to 0.103 ms, but render p95 regressed to
  505.064 ms and 991/1,000 samples crossed 250 ms because unpaced reliable file traffic blocked the
  shared carrier. Restore required per-chunk bookkeeping until an explicit bulk scheduler reserves
  interactive headroom (ADR 0159).
- Retain the independent parts of ADR 0158: one pinned receive descriptor replaces per-1,371-byte
  duplicate/write/close churn, and runtime status publishes event high-water plus required-event
  backpressure count/total/maximum. Sandwurm now binds both guests' final content-free status into
  their receipts and compact proof.
- The exact descriptor-only direct-UDP `bulk-1` rerun recovers render p95 from 505.064 to 51.146 ms
  and owner p99 from 7.114 to 3.972 ms, but still misses both strict targets. Bilateral evidence now
  shows the client at the 1,024-event ceiling with 1,227 required waits while the device peaks at 765
  without backpressure. This selects a bounded high/low-water file pacer before route isolation.
- Add that explicit pacer at 64/16 pending events with a 5 ms minimum hold, leaving the 1,024-entry
  queue as semantic reserve. Provider PAUSE runs only after callbacks return; interactive/control
  owner work precedes low-water RESUME, explicit pause ownership is preserved, and required-event
  delivery remains the fail-safe. Runtime and strict bilateral proof status expose all scheduler
  settings, pause/resume/failure counts, and hold totals (ADR 0160).
- Accept its exact clean-commit direct-UDP `bulk-1` qualification: 1,000/1,000 renders, p95
  42.727 ms, owner p99 1.499 ms, zero 100/250 ms misses, event high-water 180/130, zero required
  waits, and 853/876 matched pacing cycles with no failures. Retain strict compact proof
  `pair.a4j1uirz`; the protected route is not required for this cell.
- Accept the matched forced-TCP `bulk-1` cell at owner p99 1.452 ms. Report its distinct route p95/p99
  at 57.594/70.044 ms with one 100 ms sample and zero 250 ms misses; retain zero required waits,
  248/278 matched pacing cycles, zero failures, and strict compact proof `pair.0vkhkq96`.
- Correct the higher-load matrix contract after the first paced direct-UDP `bulk-8` attempt completed
  1,000 terminal samples but treated an intentionally scheduler-paused transfer as absent. New v6
  observations prove `present = active + paused` before and after sampling, retain all three counts,
  and require every present transfer to progress. Older v1--v5 proofs keep their strict historical
  meaning (ADR 0161).
- Preserve that incomplete private run only as diagnostic science: render p50/p95/p99/maximum was
  50.090/194.160/499.049/1,012.296 ms with 37 samples at or above 250 ms, while owner p99 remained
  1.023 ms and recovered final status showed 2,705 matched pacing cycles, zero control failures, and
  zero required-event waits.
- Retain the clean v6 direct-UDP `bulk-8` rerun as a valid failed performance cell. It proves all
  eight transfers present/progressed, one-round eight-control cancellation, close, bilateral status
  and resources, and strict raw/compact verification. Owner p99 is 0.420 ms and event high-water is
  only 134/138, but render p95/p99 is 144.120/179.491 ms with one 250 ms miss. This selects
  multi-transfer pacing fairness/shared-carrier burst science; compact proof `pair.y0d97_ng` is
  retained and its 2.4 GiB private raw root was reclaimed.
- Add the selected multi-transfer pacing A/B: resume the oldest eligible scheduler pause first and
  bound each owner-iteration batch to one transfer by default. Expose `--file-pacing-resume-batch`,
  retain configured/observed batch accounting in runtime status and strict proofs, and cover three
  concurrently paused producers completing through singleton batches without semantic backpressure
  (ADR 0162). Two exact clean-commit `bulk-8` runs preserve both outcomes: `pair.dwo77gs0` exposes a
  zero-pacing, low-CPU carrier-starvation outlier, while `pair.xs9phpya` exercises 3,167/2,658
  singleton batches and improves p95/p99/max to 124.811/161.242/188.401 ms with zero 250 ms misses.
  The lifecycle-safe partial improvement remains above the 50 ms direct-route gate and selects
  proactive carrier admission/rotation before reactive event pressure.
- Add proactive per-peer incoming-file carrier scheduling (ADR 0163): one runnable receive per peer
  by default, oldest-first 20 ms rotation, explicit window/quantum controls, manual-pause ownership,
  an always-live service cadence for file-only/sync agents, complete runtime/proof telemetry, and a
  deterministic three-receive fairness gate. Its first exact two-guest result is documented below.
- Retain the first ADR 0163 `bulk-8` near-pass (`pair.qrggya8w`): all eight files progress and owner
  p99 passes, while render p95 improves to 56.247 ms but remains above 50 ms. Coordinate reactive and
  proactive pause ownership (ADR 0164), classify exact already-paused handoff separately, ignore only
  bounded post-cancel late chunks, and raise the default fair rotation quantum from 20 to 50 ms.
- Accept ADR 0164 direct-UDP `bulk-8` proof `pair.bo6l0der`: render p95 39.634 ms and owner p99
  1.917 ms pass, all eight files progress, carrier rotations fall 65% to 507, event high-water falls
  to 228/168, 77 external-pause handoffs remain owner-correct, and all true control failures,
  required-event waits, terminal diagnostics, and 100/250 ms misses are zero.
- Accept matched forced-TCP `bulk-8` proof `pair.pitcu1pk`: render p95/p99/max is
  76.249/98.314/119.607 ms, owner p99 is 1.525 ms, no render reaches 250 ms, all eight files progress,
  739 rotations plus 58 typed handoffs have zero true failures, and event high-water is 141/139 with
  zero required waits. The balanced eight-stream route row is complete.
- Accept direct-UDP `bulk-16` proof `pair.xphist_e`: render p95 40.591 ms and owner p99 1.894 ms
  pass, all 16 files progress, 524 rotations plus 60 typed handoffs have zero true failures, maximum
  fair wait is 890.887 ms without starvation, and event high-water is 203/183 with zero required
  waits.
- Accept matched forced-TCP `bulk-16` proof `pair.qk3d51k6`: render p95/p99/max is
  75.704/87.867/106.025 ms, owner p99 is 1.013 ms, no render reaches 250 ms, all 16 files progress,
  782 rotations plus 84 typed handoffs have zero true failures, and event high-water is 190/136 with
  zero required waits. The balanced 16-stream route row is complete.
- Accept direct-UDP `bulk-32` proof `pair.ktcwivx_`: render p95 is 47.765 ms and owner p99 is
  1.811 ms, all 32 files progress, 590 rotations plus 78 typed handoffs have zero true failures,
  maximum fair wait is 1.744 seconds without starvation, and event high-water is 162/152 with zero
  required waits.
- Accept matched forced-TCP `bulk-32` proof `pair.lanpv3u7`: render p95/p99/max is
  76.331/95.608/163.533 ms, owner p99 is 0.798 ms, no render reaches 250 ms, all 32 files progress,
  670 rotations plus 56 typed handoffs have zero true failures, and event high-water is 185/147 with
  zero required waits. The balanced 32-stream route row is complete.
- Retain rejected direct-UDP `bulk-64` proof `pair.t736zqqh`: all 64 files progress and cancel
  cleanly, owner p99 is only 0.118 ms, remote stage-to-output p95 is 10.293 ms, queues peak at only
  50/50, and no reactive pacing activates, but transport render p50/p95/p99 is
  220.897/331.081/446.692 ms with 108 misses at or above 250 ms. This locates a low-utilization
  single-carrier cliff between 32 and 64 accepted transfers rather than an Agent/PTY/CPU bottleneck.
- Retain rejected forced-TCP `bulk-64` proof `pair.swij6mj9`: all 64 files progress by 168,951,072
  aggregate bytes, but event high-water reaches 711, owner p99 is 2.199 ms, and one render reaches
  560.528 ms. ADR 0165 freezes the existing 32-send/32-receive single-Agent default as the qualified
  ceiling, leaves larger explicit limits experimental, and keeps excess work outside live Tox state.
- Preserve an exact synchronization attempt when the final receive entrance reports only
  `resource_exhausted` (ADR 0166). Undo provisional staging/journal state, keep the immutable object,
  FileId, file number, route and byte reservation, then retry paused offers outside callbacks in
  cyclic passes of at most 32 records. Expose pending/retry truth and cancel admitted plus pending
  offers without repeating effects.
- Add the genuine two-guest `sync-tree-admission` gate. Direct UDP `pair.xrl6_7gv` and forced TCP
  `pair.dqbsp21_` each constrain the subscriber to one accepted receive, observe ten bounded retries
  of the paused second immutable-object offer, admit exactly two offers sequentially, and converge
  with zero pending. Strict compact proofs pass. By composition with the accepted 1,000-sample
  `bulk-1` route rows, the single-Agent excess-work prerequisite is qualified without claiming a
  simultaneous Ratox-under-deferral latency measurement.
- Add the default-off ADR 0167 auxiliary sync-frame boundary. An explicitly enabled authenticated
  bulk worker negotiates `state-sync-v1`, accepts/sends only canonical object request/result records,
  and retains inbound frames in a pre-reserved bounded parent queue tagged with route incarnation,
  auxiliary epoch, remote generation, and stable principal. Queue overflow does not evict established
  work; trust/connection loss purges it. Agent dispatch and feature advertisement stay off until the
  parent can bind primary authority to an auxiliary carrier without forging an authority session.
- Add the ADR 0168 parent dispatcher. Primary authority and HEAD discovery stay on the proven primary
  session while one exact auxiliary carrier owns whole-object frames, FileId offers, file operations,
  terminal truth, replay identity, and signed route-capacity accounting. Loss fences the old
  incarnation before another ready route receives fresh attempt/message/FileId/staging identities;
  accepted HEAD still commits last and activation stays explicit.
- Extend the complete mock Agent gate to one protected primary plus two authenticated bulk workers,
  force the first object carrier offline, reject its stale domain, converge both objects through the
  second exact worker, and activate through local control. Service each auxiliary file manager's
  bounded carrier window so a later admitted receive cannot remain paused forever.
- Make the one-slot required-event backpressure test deterministic under TSan by allowing the owner
  to fill its slot and block on the successor before the consumer begins draining.

### Live mixed-provider rolling qualification

- Extend the exact 0.2.22 and 0.2.23 warnings-as-errors fixtures with a bounded live exchange mode,
  explicit native-UDP/forced-TCP selection, exact friend-route observation, bilateral fixed-message
  proof, and post-exchange savedata rewrite.
- Add a two-Sandwurm-guest `provider-rolling` scenario. Both identities and friendships originate in
  0.2.22; the client stays on 0.2.22 while the device runs 0.2.23. Both route modes pass, and both
  versions read identical post-exchange semantic state (ADR 0153).
- Add strict raw/compact verification and a provider-specific exporter. Retain the direct-UDP
  `pair.bkvx0lo1` and forced-TCP `pair.lknnctzw` content-free proofs at 96 KiB each; private guest
  disks, provider savedata, keys, messages, runtime state, and bootstrap secrets remain omitted.

### Previous-provider savedata qualification

- Pin c-toxcore 0.2.22 as a qualification-only input and build separate warnings-as-errors fixtures
  against exact old and current provider sources. It is never linked into the product or added to the
  product SBOM.
- Generate two disposable mutually friended old-provider identities; require 0.2.23 and the real
  source-linked IoTox Agent to preserve both Tox identities, profiles, and friendships across load and
  rewrite; require 0.2.22 to read the rewritten state and both providers to reject malformed state
  (ADR 0152).
- Add the content-free `toxcore-provider-upgrade` flake check. Its exact receipt is byte-reproducible
  across repeated disposable identities and retained at
  `docs/evidence/2026-08-24-toxcore-provider-upgrade.json`. The separately retained live route gate
  now completes the local 0.2.22-to-0.2.23 transition evidence.

### Seeded partial-loss continuity

- Add a distinct two-guest Sandwurm `packet-loss` gate with independent 5% `netem` profiles and
  fixed seeds on both private TAP paths. Require positive kernel drops, 128 exact 1,200-byte lossy
  probes per role, ordinary text during impairment, unchanged confirmed epochs, and fresh text after
  exact qdisc removal (ADR 0151).
- Retain direct-UDP evidence with 119/128 and 117/128 probe delivery and forced-TCP evidence with
  128/128 delivery in both directions despite observed lower-layer drops. This distinguishes native
  lossy-carrier behavior from TCP retransmission without weakening the separate 100% outage gate.
- Extend strict pair verification and compact export to bind every probe row and impairment counter.
  Reverify both ~152 KiB content-free exports, then reclaim 4.5 GiB of private VM roots through the
  audited workspace cleaner.

### Release component and clean-build truth

- Generate and strictly verify a deterministic SPDX 2.3 source-component SBOM for every standalone
  and Nix source-linked binary. It binds the executable and the locked c-toxcore, cmp, libsodium,
  Argon2, and EFF word-list records without claiming the host runtime closure.
- Replace CI's incremental relink comparison with a disposable second empty product build root and
  require byte-identical binary, SBOM, provenance, verification, notices, and licenses. Add a local
  two-clean-root comparator that removes both roots after use (ADR 0150).
- Retain the founding-host two-empty-root pass: executable
  `d2d5845957535652d29f2624bc9e0e0419fd753b2385a90d13cc6f691bd0f824` and SPDX
  `235c2cb1f1d2c8d0dc0932868c57b3e66f3a85d2892ed9b88d39606122400798` are byte-identical across
  roots. Independent-builder comparison remains open.
- Reverify eight accepted compact synchronization proofs, retain binary-pinned compatibility for the
  pre-GC repair schema without weakening current repair requirements, and remove eleven superseded
  private pair roots through the audited cleaner. The exact cleanup reclaimed 25.0 GiB and left zero
  Sandwurm candidates; accepted compact proofs remain.

### Quarantine-only synchronization GC

- Add local-control v1.32 operation 77 and `sync-gc NAMESPACE dry-run|quarantine`. Dry-run reports
  guarded rooted/candidate counts without creating quarantine; execution always recomputes the plan.
- Freeze the complete strict inventory with root/object directory and per-object device/inode,
  owner/group, link, mode, kind, digest-name, and size evidence. The namespace transaction now pins
  its root descriptor and identity and rejects root/transaction/lock substitution.
- Move only exact unreferenced identities through Linux `openat2` containment and
  `renameat2(RENAME_NOREPLACE)` into same-filesystem `gc-quarantine`. No API accepts an object path;
  no unlink, `apply`, remote GC, or purge mode exists.
- Distinguish moved from durably fsynced prefixes across cancellation and injected directory-sync
  failure. Deterministic cells also refuse inconsistent roots, hard links, symlinks, and immediate
  inode substitution (ADR 0149).
- Extend `sync-file-repair` so both source-linked Sandwurm guests refuse a real bind-mounted object
  directory, preserve two outside-root sentinels each, dry-run and quarantine one exact 32 KiB
  unreachable inode, and prove an empty retry. The strict compact proof is retained as
  `.sandwurm/exports/pairs/pair.ci0p3t6f`.

### Deterministic directory synchronization

- Allocate stable-device-signed HEAD engine `3` as `treepack-v1` and add the canonical
  `sync-namespace-template-tree` policy surface. Directory publication reuses the preserved toxsync
  codec, commits a canonical range index, and keeps the existing object-before-HEAD ordering.
- Bound complete treepack bytes, entries, paths, file size, and in-memory sorting. Require an
  owner-controlled source tree and reject symlinks, hard links, special files, shared-write entries,
  unsafe outputs, and artifact overflow before publication.
- Make materialization a post-signed-activation derived projection. Unpack privately, repack and
  verify the signed artifact digest, fsync and freeze files/directories, rename the complete revision,
  and atomically switch a relative `current` symlink. Exact activation retry reconciles an interrupted
  projection after signed state is already durable.
- Recover only exact canonical abandoned staging directories and retain only the current derived
  revision. Cleanup classifies and validates every selected tree before mutation, refuses ambiguous
  or linked state, makes frozen owner-only directories removable, and fsyncs the affected roots.
- Recover exact abandoned `.current.part.PID.SEQUENCE` symlinks as well as unpack staging. Pointer
  cleanup validates every top-level entry and canonical relative target before the first unlink, so
  ambiguity cannot produce a partial cleanup and repeated interruption cannot grow pointer debris.
  Pointer candidates are bounded by the namespace object ceiling; revision cleanup additionally
  permits the one predecessor needed for an atomic switch. Excess state fails before mutation.
- Add eight named post-effect projection checkpoints and a dedicated separate-process crash oracle.
  The oracle uses `_exit` after every boundary from unpack through stale-tree pruning, requires the
  visible tree to be wholly old or wholly new, then proves exact fresh-process retry leaves one
  revision and no derived temporary (ADR 0140).
- Add the destructive derived-tree classifier to the default deep Clang path-sensitive analysis set
  and teach retained-artifact validation to require the resulting five-unit clean marker.
- Add deterministic component/product/Agent tests and the genuine `sync-tree` Sandwurm gate. The same
  source-linked binary converges and activates the same three-directory/three-file 4 MiB tree over
  observed direct UDP and forced TCP; both raw and compact proofs independently verify (ADR 0139).

### Synchronization repair

- Add local-control v1.30 operation 76 and CLI verb `sync-repair NAMESPACE`. It verifies the strict
  digest-named object store for one local namespace and quarantines only private regular final
  objects whose bytes no longer match their filename identity.
- Refuse malformed names, unsafe file shapes, public modes, links, and unexpected store entries as
  terminal errors rather than cleanup candidates. The deterministic storage and Agent socket tests
  cover both quarantine and refusal.
- Add the `sync-file-repair` two-guest Sandwurm gate and strict compact-proof verification. Direct
  UDP and forced TCP each fsync a deliberate 4 MiB target-object mismatch, quarantine only that
  object, preserve signed acceptance and activation, recover the same authorized revision, preserve
  the quarantine copy, and pass a clean two-object rescan.
- Add bounded content-free guest failure receipts so pair runs terminate on the exact failed phase
  with optional repair job status and local-control diagnostics instead of exhausting the outer
  evidence timeout.

### Bounded range reconstruction

- Continue one partially failed range plan after completely discarding its staging, finishing signed
  attempt truth, and fencing the scheduler reservation. The retry retains the exact HEAD/ranges and
  authenticated epoch but allocates a fresh durable attempt, message ID, and Tox FileId; no partial
  bytes or transport handle are reused (ADR 0138).
- Deliver locally initiated generic file cancellation into the sync subscriber's terminal-work path.
  This repairs the public `file-control ... cancel` fault seam without changing terminal
  `sync-cancel JOB_ID` or disconnect semantics. `sync-status` now separates final fetched bytes from
  `range-retries` and saturating `range-discarded-bytes`.
- Add `sync-file-range-retry` and strict compact verification. Genuine direct UDP and forced TCP each
  cancel a rate-shaped live 1 MiB range after positive progress, observe a different second FileId,
  reuse 3 MiB, refetch the full missing 1 MiB, accept generation 2 last, and activate explicitly.
- Fix the route-worker startup/stop snapshot race exposed by the full GCC ThreadSanitizer lane.
  Auxiliary worker population is now published under the snapshot mutex, and stop joins the service
  thread before tearing down worker-owned transports under the same lock.
- Put Clang and clang-tidy in the default Nix development shell so the documented clean source matrix
  can actually reach its Clang, sanitizer, and focused-analysis lanes from that shell.
- Teach `tools/build-matrix.sh` to discover `libargon2` from Nix-provided `LD_LIBRARY_PATH` before
  falling back to `ldconfig`, so the source-linked Argon2 lane works inside the default shell.

- Recover from a missing or corrupt accepted range basis by requesting the complete signed successor
  through a new whole-object attempt. The manifest is reverified first, the full artifact still needs
  its exact SHA-256, and HEAD acceptance remains last. `sync-status` exposes `range-fallback`; no
  corrupt object is deleted, quarantined, or overwritten by this recovery path (ADR 0137).
- Add the genuine `sync-file-corrupt-basis` Sandwurm cell. Direct UDP and forced TCP both preserve an
  intentionally corrupted 4 MiB generation-1 basis, fetch and activate the exact signed generation-2
  successor through whole-object fallback, and independently reverify compact content-free proofs.

- Add optional `state-sync-ranges-v1` feature bit 26, requiring base `state-sync-v1`, with canonical
  message types 24/25 for 1..64 sorted, nonoverlapping, nonadjacent target ranges bound to the exact
  current signed HEAD and request-selected FileId.
- Add descriptor-pinned zero-copy file offers for canonical range concatenations. The publisher
  revalidates authority, current HEAD, immutable artifact, range bounds, staging quota, and replay
  before offering; no server-side bundle file is created.
- Add manifest-first subscriber planning against the exact artifact named by its accepted HEAD.
  Missing bytes land under a durable target attempt, reconstruction revalidates the manifest/basis/
  plan and complete SHA-256, and immutable object commit plus attempt clearance precede accepted-HEAD
  advance. No completion implies activation.
- Add range request/offer/byte and per-pull reuse/fetch/count telemetry to `sync-status`, plus strict
  whole-artifact fallback when no reusable basis or bounded plan exists.
- Extend the source-linked mock toxcore through range negotiation, response, and finite-file delivery.
  The full Agent gate advances a 16 KiB generation-2 successor while fetching 4 KiB and reusing
  12 KiB. Four GCC Debug shards pass all 519 owned checks, and all 16 runnable process/restart/CLI
  gates pass; five delegated-cgroup gates remain explicit capability skips on this host.
- Add the genuine `sync-file-range` Sandwurm scenario and independent compact-proof verification.
  Direct UDP and forced TCP each advance an activated 4 MiB generation-1 basis to the same signed
  generation 2 through one genuine c-toxcore range transfer: 128 bytes fetched and 4,194,176 bytes
  reused, followed by exact artifact verification and explicit exact-token activation.
- Record ADR 0136, the extended frozen synchronization wire, construction evidence, updated threat
  boundary, genuine two-route provider evidence, and the remaining directory/fault roadmap gates.

### Multi-route immutable-object scheduling

- Add a bounded transport-neutral scheduler whose only work identity is canonical synchronization
  object kind, digest, and byte count. Exact ready bulk-worker incarnations reserve coordinator
  capacity; the protected Ratox route is never eligible.
- Retain unique attempt IDs as fence tombstones, reject late completion after reassignment, separate
  exact verification from idempotent commit, and release capacity exactly once across mismatch,
  route authentication loss, commit, and explicit close.
- Document ADR 0118 and the v1 state machine, keeping transport callbacks and filesystem effects
  outside the pure scheduling boundary.
- Derive one private no-clobber staging destination from each attempt ID. Transaction-bound commit
  verifies the completed file's strict shape, size, and digest before exclusive double-checked object
  publication; fenced discard is idempotent for absence and refuses links or unexpected shapes.
  This filesystem boundary remains separate from scheduler admission and live transfer events.
- Make the scheduler namespace-scoped for staging admission and reserve every assigned object's full
  byte count together with route work. Concurrent routes share one ceiling; verification retains the
  reservation, while fence, mismatch, commit, close, and authentication-loss cleanup release it
  exactly once. Live transfer-event binding and restart reconstruction remained open at this slice.
- Give every auxiliary worker a file-transfer manager bounded by its signed active-work count and the
  configured finite-file ceiling. Route-scoped receive/cancel requires the exact reciprocally
  authenticated bulk incarnation; protected, stale, and merely connected routes cancel offers and
  fail before effect. Primary-trust replacement cancels retained transfers before revocation.
- Reserve one preallocated, non-evicting worker terminal slot before every receive resume and retain
  an exact route/worker/file outcome across completion, cancellation, peer loss, trust loss, and file
  failure. Full terminal capacity refuses new effects.
- Add the namespace-scoped transfer bridge from an active reserved attempt through its derived private
  staging path to strict object-store verification and exact scheduler commit. Corrupt or conflicting
  completion discards and fences only that attempt; unknown and replayed outcomes stay stale. Four
  checks grow the owned registry from 475 to 479. At this slice, signed wire mapping, restart
  reconstruction, Agent activation, and genuine multi-worker transfer remained open.
- Add a canonical bounded stable-device-signed active-attempt journal. IDs are durably burned before
  assignment; immutable object and exact route incarnation state lands before receive resume, while
  terminal processing retains retryable completion truth until the journal and filesystem agree.
- Add idempotent startup recovery that verifies an already committed object, commits complete staged
  bytes, or safely discards and fences absent/corrupt staging without persisting a Tox file number.
  Five checks grow the registry from 479 to 484. Full older-record replay remains an external-witness
  nonclaim; at that slice, wire mapping and Agent recovery invocation remained open.
- Allocate fixed message types 20–23 for signed-HEAD discovery and immutable-object offer negotiation
  while keeping `state-sync-v1` unadvertised. Four canonical codec/envelope checks grow the registry
  from 484 to 488; the Agent still handles none of these messages.
- Bind each object request to an exact signed-HEAD digest and nonzero request-selected Tox FileId.
  Outgoing file offers read the ID back from c-toxcore, and authenticated bulk workers preallocate
  bounded sender records so send and receive completion/cancellation/failure share one non-evicting
  terminal ledger. Remote filenames remain presentation only. A live provider-backed worker-send
  proof grows the registry from 488 to 489.
- Generalize scheduler capacity behind an exact admit/release/already-withdrawn adapter while
  preserving the ready-bulk coordinator policy. A single-route vertical slice can now reuse every
  attempt, staging-byte, fence, verification, and commit invariant without inventing route evidence.
- Reuse toxsync's portable SHA-256 primitive through a production descriptor-based file hasher.
  Canonical vectors pass; relative paths, symlinks, non-files, replacement, mutation, and byte-count
  drift fail closed. Artifact/manifest identities are now explicitly distinguished from IoTox's
  domain-separated metadata hashes in ADR 0125.
- Add the default-off publisher admission service. Exact current v3 `sync.subscribe` authority,
  subscriber membership, signed-HEAD pinning, object verification, and requested FileId precede an
  offer. Bounded non-evicting replay is retained before the effect, exact duplicates do not reoffer,
  conflicts fail, authority changes fence cached responses, and unknown namespaces do not enumerate
  policy. Four checks grow the registry from 489 to 493; Agent and receiver wiring remained closed at
  that checkpoint.
- Add the transport-neutral subscriber for one signed writer and one complete source. Exact current
  v3 `sync.publish` authority and namespace membership precede signed-HEAD transition evaluation;
  artifact and manifest receive attempts use distinct request-selected FileIds, survive restart in a
  signed journal, verify SHA-256 before object commit, and commit accepted HEAD state last without
  activation. Exact retries reuse retained unanswered frames, and filenames never select identity.
- Construct the complete path behind `iotox run --enable-sync`. Strict startup loads owner-only
  namespace policy, recovers attempt journals before networking, constructs both dispatchers, and
  advertises `state-sync-v1` only after every seam exists. A bounded ordinary queue and reserved
  priority terminal queue keep blocking verification off the toxcore owner callback and reconstruct
  current session/authority context before each effect.
- Add typed same-user `sync-namespaces`, `sync-pull FRIEND NAMESPACE`, and content-free `sync-status`
  commands. A full Agent/mock-provider check traverses real lossless frames, ordinary c-toxcore file
  offers/callbacks, two immutable object commits, and accepted-HEAD-last ordering. Five checks grow the
  registry from 493 to 498. Genuine two-IoTox Sandwurm convergence, local publication/activation,
  range reuse, and multi-source scheduling remain release gates.
- Integrate the preserved toxsync range-index builder and verifier into the product boundary.
  `sync-publish NAMESPACE ABSOLUTE_PATH` builds a quota-bounded canonical index, semantically binds it
  to the exact artifact, commits both objects, and advances the stable-device-signed HEAD last.
- Add exact-token `sync-activate NAMESPACE HEAD_RECORD_HEX`. Activation holds the namespace
  transaction while rechecking strict artifact and manifest shapes, sizes, SHA-256 identities, and
  their range-v1 semantic binding before moving the independently signed activation pointer.
- Make the subscriber perform the same range-v1 semantic check before accepted-HEAD persistence;
  non-range-v1 namespaces fail explicitly in this first slice. Six checks grow the owned registry
  from 498 to 504. The complete 26-target GCC/CTest suite and 41-target Clang 21 ASan/UBSan suite
  pass; namespace administration, cancellation, and range reconstruction remain gates.
- Add a `sync-file` Sandwurm pair gate and content-free verifier/export support. Two distinct
  source-linked guests establish bilateral least-capability v3 authority, publish and converge a
  genuine 4 MiB file through exact Tox FileIds, accept HEAD last, and explicitly activate its exact
  token. Direct UDP and forced TCP both pass with identical artifact, range-index, and signed-HEAD
  identities; interruption and restart qualification were the next fault boundary at that slice.
- Add the `sync-file-restart` Sandwurm gate. It rate-shapes an 8 MiB transfer, kills the receiving
  daemon only after authoritative c-toxcore position advances, proves signed active state exists
  without acceptance or activation, restarts the same identity, and requires an empty recovered
  staging directory before exact-revision retry. Direct UDP and forced TCP both pass.
- Repair the defect that gate exposed: an interrupted `FileTransferManager` owns a private
  pre-rename `.part.part-XXXXXX` file that the attempt journal previously could not clean. Recovery
  now recognizes only the exact attempt-derived prefix, validates one owner-private singly linked
  regular file, removes and directory-fsyncs it before journal clearance, and fails closed on
  malformed, multiple, or linked candidates. Positive recovery coverage plus one new refusal check
  grow the registry from 504 to 505; the full
  GCC and Clang 21 ASan/UBSan CTest matrices, flake check, source-linked build, and both genuine
  carrier cells pass.
- Add owner-local synchronization namespace authoring without introducing another policy language.
  `sync-namespace-template` emits a canonical range-v1/manual record from an exact local root and
  stable principals; `sync-namespace-lint` verifies a bounded no-follow file offline; and
  `sync-namespace-install` carries the canonical bytes through same-user local control v1.27.
- Installation serializes on the namespace-directory inode, writes and fsyncs an unnamed mode-0600
  file, atomically links the final policy name without clobber, fsyncs the directory, reloads the
  complete strict store, and replaces the live registry. Exact retry is a generation-stable
  duplicate; conflicting replacement is refused.
  Two checks grow the owned registry from 505 to 507. Full GCC and Clang 21 ASan/UBSan CTest matrices
  pass; update, removal, and cancellation remain explicit gates.
- Add a nonzero process-local job identity to every pull, return it from `sync-pull`, and expose it in
  the content-free `sync-status` record. `sync-cancel JOB_ID` enters same-user local control v1.28 and
  terminally marks the exact job before any transport or filesystem cleanup.
- Cancellation closes each admitted c-toxcore receive at most once, discards attempt-derived staging,
  finishes the stable-device-signed active-attempt record, and fences offered and unoffered scheduler
  work. A transport CANCEL enqueue failure cannot prevent local cleanup; it is reported, and an exact
  retry settles the already-fenced job without repeating the transport effect. Late HEADs, object
  results, file offers, and completion callbacks cannot accept a HEAD after cancellation. One new
  direct check grows the registry from 507 to 508.
- Add the `sync-file-cancel` Sandwurm cell and strict compact verifier/export support. A rate-shaped
  8 MiB pull must expose its job ID, admit both FileId receives, and show positive provider position
  before cancellation. Direct UDP and forced TCP both pass with identical artifact, manifest, and
  signed-HEAD identities, zero convergence/activation, empty staging, and terminal cancelled status.
  The complete GCC and Clang 21 ASan/UBSan matrices pass. Clean-commit observations and exact compact
  bindings are retained in `docs/evidence/2026-08-21-sandwurm-sync-cancel.md`.
- Freeze disconnect handling at the authenticated epoch boundary in ADR 0132. The old job fails and
  clears receives, staging, durable attempt truth, and scheduler reservations; a higher confirmed
  epoch requires an explicit new pull with new job/FileId identities. Add the rate-shaped
  `sync-file-disconnect` Sandwurm gate and strict verifier fixtures without claiming partial-byte
  resume. Its first direct-UDP cell reached cleanup and a higher epoch but retried on the first
  confirmed callback; a second connection flap safely failed that new job. Require 50 consecutive
  100 ms same-epoch authorized samples before retry, retain the stability count in both receipts,
  and hold the converged client behind an evidence-release barrier until the publisher checkpoint is
  secured.
- Repair the publisher-side evidence loop to resample authority with session and route truth after
  disconnect, and retain an atomic recovery probe for opaque laboratory failures. Direct UDP and
  forced TCP now both pass: each role advances from epoch 1 to 2, the subscriber terminally clears
  the old job and partial staging, and an explicit stabilized whole-object retry converges and
  activates the identical revision. Strictly verified compact bindings and nonclaims are retained in
  `docs/evidence/2026-08-21-sandwurm-sync-disconnect.md`.
- Add quiescence-gated `sync-namespace-update PATH` and policy-only
  `sync-namespace-remove NAMESPACE` through same-user local control v1.29. Update may replace only
  activation and canonical writer/subscriber membership; namespace identity, root, engine, and all
  quotas remain immutable. Removal leaves content and every signed namespace state root untouched.
- Serialize live install/update/remove, refuse mutation while publisher replays or target subscriber
  cleanup can retain effects, recover only strict canonical owner-private update temporaries, and
  reconcile disk truth after every possibly committed result. A failed reload empties the live
  registry rather than retaining stale permissions. Exact duplicate/absent retries are
  generation-stable. One new direct check grows the owned registry from 508 to 509; the existing
  Agent and CLI/protocol checks now cover the full administration lifecycle. ADR 0133 freezes the
  boundary.
- Add the `sync-file-pause` Sandwurm cell and strict compact verifier/export support. A rate-shaped
  8 MiB pull records one active receive's exact file number and request-selected FileId after
  positive provider progress, pauses it through the public finite-file control, and requires the
  same positive partial position for 20 consecutive 100 ms samples with no accepted or activated
  HEAD. Resume must return that exact FileId with the local pause cleared before ordinary
  accepted-HEAD-last convergence and exact-token activation. Direct UDP and forced TCP both pass;
  ADR 0134 keeps pause process-local and separate from cancellation, disconnect, or restart.
- Add the `sync-file-guest-restart` Sandwurm cell and strict compact verifier/export support. A
  rate-shaped 8 MiB pull reaches positive provider progress before the publisher guest reboots. The
  subscriber terminally clears the old job, receives, staging, and attempt truth without accepting
  or activating the HEAD. A successor Sandwurm chain reuses the exact persisted disk and prelaunch
  receipt, changes the publisher boot ID while preserving Tox/stable identity, policy, source,
  immutable objects, and signed HEAD, then serves an explicit fresh pull only after 50 stable samples
  of a higher authorized epoch. Direct UDP and forced TCP both pass at clean commit `f26126e`; ADR
  0135 freezes whole-object retry rather than transport-handle or partial-byte resurrection.

### Authority-ledger v3 synchronization capabilities

- Add the one-way, owner-self-signed `migrate-v3` transition from an exact v2 head. Migration
  preserves every existing grant and requires a separate additive owner grant before any new right
  becomes active; v1/v2 masks and the historical `all`/`all-v2` spellings remain frozen.
- Allocate independent `sync.admin`, `sync.publish`, `sync.subscribe`, and `sync.activate`
  capabilities at bits 8 through 11 with explicit v3 role ceilings, record/header domains, replay,
  rollback-guard coverage, and strict unknown-bit refusal.
- Add session feature bit 25, v3 challenge/proof domain separation, v2-lineage negotiation, exact-head
  authorization, remote delegation and idempotent retry handling, plus local and remote RecallRoot
  migration ceremonies that require the exact current v2 capability set.
- Qualify migration, non-widening failure cases, explicit activation, role ceilings, restart/guard
  behavior, proof domain separation, negotiation dependencies, remote application, and CLI process
  signing in the complete 19-route CTest suite.
- Add a pure sync-service admission gate that combines the exact current v3 proof with the distinct
  operation capability, stable writer/subscriber membership, and manual activation policy. Eight
  direct negative/positive checks grow the owned registry from 385 to 393 before any network service
  entrance or packet allocation exists.
- Add a fixed 296-byte stable-device-signed synchronization HEAD, independent signature/record hash
  domains, verified accepted-candidate conversion, and a bounded private publisher store. Exact retry
  is idempotent, same-writer successors derive their parent, and one live store serializes concurrent
  publication. Twelve checks grow the owned registry from 393 to 405 without introducing the old
  toxsync parallel HEAD key or enabling network service.
- Add the ordered local revision publisher: artifact and manifest are independently bounded, hashed,
  no-clobber committed, and reverified at their private final object paths before the signed HEAD can
  advance. Source mutation, symlink inputs, corrupt/public/linked objects, quota failure, and late
  cancellation fail before HEAD mutation. Ten checks grow the owned registry from 405 to 415.
- Serialize signed-HEAD publication across separate local processes with one strict private advisory
  lock, and add canonical whole-object-store inventory plus prospective byte/object admission for
  publication and installation. Three checks grow the owned registry from 415 to 418, plus a clean
  dedicated eight-process contention oracle; retention and garbage collection remain deliberately
  unimplemented.
- Add a canonical bounded retained-revision snapshot with exact accepted record, artifact, manifest,
  size, generation, restart, idempotency, fork, capacity, and private process-lock semantics. Eight
  checks grow the owned registry from 418 to 426. Destructive GC remains prohibited until retention is
  authenticated and one transaction lock covers every live-root transition.
- Replace the pre-integration unsigned retention format with a stable-device-signed, domain-separated
  v2 record. Every real mutation advances a counter and commits the prior signed record digest; wrong
  devices, altered signatures, and unsigned v1 state fail closed. Two checks grow the registry from
  426 to 428, plus a clean eight-process pin oracle. Whole-chain rollback after restart remains
  possible, so deletion is still prohibited.
- Add a strict canonical kind/digest/size object inventory and a bounded mark-only reachability planner
  across stable-device-signed publication, accepted HEAD, activation, and authenticated retention
  roots. Five checks grow the registry from 428 to 433. Missing and size-mismatched live objects remain
  distinct from unreferenced candidates; inventory sizes come from no-follow opened descriptors and no
  deletion API exists.
- Replace separate sync mutation locks with one private per-namespace transaction. Move-only,
  acquiring-process/thread-bound tokens span object admission/commit, signed and accepted HEAD
  transitions, activation, retention, and stable root-plus-inventory planning without nested flock.
  Five checks grow the registry from 433 to 438, plus a blocking cross-domain process oracle. Deletion
  remains absent.
- Authenticate every persisted accepted HEAD with the stable device identity. The store now rejects
  unsigned legacy state, foreign device keys, and altered bodies/signatures before an accepted root
  can drive installation, activation, or reachability. One check grows the registry from 438 to 439;
  activation-pointer authentication and restart anti-rollback remain open.
- Authenticate every persisted activation pointer with its own stable-device signature domain. All
  implemented reachability roots now reject unsigned legacy, foreign, or altered state. One check
  grows the registry from 439 to 440; restart-safe whole-record anti-rollback remains the blocker
  before destructive collection.
- Add a canonical 496-byte stable-device-signed namespace rollback guard. Four exact root heads are
  represented as committed plus optional pending state; begin/state/finish power cuts reconcile on
  either valid side, while missing guards, third heads, foreign keys, tampering, weak files, and weak
  directories fail closed. Five checks grow the registry from 440 to 445. Mutation-path wiring and
  coordinated guard-plus-state replay resistance remain open, so deletion stays absent.
- Wrap every implemented local synchronization root mutation—publication, accepted-HEAD advance,
  activation, retention pin, and retention unpin—in the guard's begin/atomic-replace/finish protocol.
  Stored reachability now checks the exact guarded root set under the same namespace transaction. A
  new fresh-process CTest route independently replays an old publication root and an old guard and
  proves both incoherent states fail closed before coherent generation advancement. Coordinated
  replay remains outside the local claim and no deletion API is added.
- Inject guarded root-commit uncertainty both before replacement and after a real landed replacement.
  Exact duplicate publication, acceptance, activation, pin, and already-applied unpin retries now
  reconcile pending signed state before returning. One check grows the registry from 445 to 446.
- Freeze a VM-independent GC containment plan: caller paths never become deletion authority, initial
  execution is quarantine-only, tests use workspace-contained disposable roots plus outside sentinels,
  and Sandworm SAFE supplies the host-escape oracle. Purge remains unimplemented.

### rev0039 bare-metal import and qualification

- Fast-forward the official history through the complete rev0039 payload recovered from the
  externally named rev0026 repository cube. The payload contributes 67 linear commits without
  replacing or diverging from the former official tip.
- Reject inherited-identity PTY profiles that configure `RLIMIT_NPROC`. Linux accounts that limit
  across the complete real UID, so it cannot safely represent a Ratox-session process budget; use
  delegated-cgroup `pids.max` instead.
- Make local Unix-socket tests independent of long temporary-directory prefixes, preserve the Ratox
  analyzer's module path explicitly, tolerate only Nix wrapper linker injection during non-linking
  Clang analysis, and remove two GCC 15 false-positive constructions without weakening warnings.
- Pin the standalone toxsync Nix input and qualify its 121-check registry under GCC Debug/Release,
  dependency-minimum GCC portable Release, Clang Debug, and Clang ASan/UBSan. This qualifies the
  preserved engine itself; integration into IoTox remains a separate fail-closed milestone.
- Standardize remaining two-node qualification on two sibling Sandwurm Cloud Hypervisor guests and
  define the receipt-bound lab command shape without adding another VM implementation.
- Freeze the planned host-preflight, terminal-administration, diagnostics, and synchronization CLI
  vocabulary. Integrated sync HEADs use the stable IoTox device signing identity plus separately
  authorized ledger capabilities rather than introducing a second ambient ownership root.

### Continuous PSI trigger tripwire (rev0039)

#### Proactive delegated-root load shedding

- Extend the rev0038 synchronous `avg10` admission gate with optional per-cgroup PSI triggers for CPU
  `some`, memory `full`, and I/O `full`. Each trigger uses one independently opened `O_RDWR` pressure
  descriptor and one common validated tracking window in `2000000..10000000` microseconds, constrained
  to exact 2,000,000-microsecond quanta so activation never silently depends on `CAP_SYS_RESOURCE` or
  requests a kernel realtime PSI poll worker. Cumulative stall thresholds must be positive, no larger
  than the window, and paired with the corresponding `avg10` threshold required for deterministic
  reopening.
- Register the exact kernel trigger record, including its terminating NUL, before service activation.
  A typed, directly tested encoder uses bounded locale-independent integer formatting, rejects undefined
  classes and nonportable windows, emits no newline, and freezes the complete binary ABI before any
  descriptor mutation.
  Poll all configured sources and one `eventfd` shutdown source in one bounded monitor thread. A trigger
  atomically publishes its metric event, closes the gate between admission attempts, and extends a
  minimum hold through one complete tracking window. Reopening still requires a later complete
  descriptor-pinned sample at every exact `maximum-hysteresis` boundary.
- Treat poll failure, invalidation, hangup, monitor construction failure, or unexpected monitor exit as
  fail-closed host unavailability. Monitor teardown signals and joins before releasing the descriptor-
  pinned registrations. Counter transfer and aggregate arithmetic saturate rather than wrap.
- Reserve the complete trigger-descriptor vector before the first kernel registration so allocation
  failure cannot leave a partially registered trigger set. Validate the monitor's poll-set cardinality,
  exact ready-descriptor count, and every stop/trigger readiness bit; unknown masks, dead sources, and
  impossible zero-ready returns fail closed through a directly tested pure classifier.

#### Operator surface and proof

- Add four CLI options for the common trigger window and three resource-specific stall thresholds.
  Publish trigger configuration, monitor health, active/remaining hold, typed monitor failure, total and
  per-resource trigger counts, monitor failures, trigger-caused close transitions, and admissions rejected
  while a trigger hold is active through the owner-private content-free runtime status surface.
- Add policy-boundary, held-gate, CLI-rejection, Agent-projection, runtime-rendering, and capability-aware
  live registration coverage. The direct owned registry grows from 356 to 359 checks; all 19 default
  CTest routes pass on the construction host, with the four privileged private-cgroup routes retaining
  explicit capability skips where delegation is unavailable.
- Harden exact aggregate CPU normalization at every division boundary. Reassert the validated positive
  period and GCD-derived scale invariants locally, fail closed on an impossible zero or out-of-range
  divisor, and freeze zero aggregate/session-period rejection through the public resolver.
- Add a required focused Clang static-analysis lane for the profile resolver, cgroup pressure controller,
  Agent, and runtime tree. It derives exact Clang Debug commands from CMake, runs the explicit deep
  analyzer for all four units, treats any emitted diagnostic as a failed lane even when the compiler
  exits zero, and records one canonical marker that retained-artifact refresh validates exactly once
  before the terminal matrix marker.
- Bind retained Agent/session stress evidence to the exact current owned registry. Artifact refresh now
  rejects a syntactically valid 100-run transcript whose shard denominator is stale, validates the
  zero-based shard range, and records both values in the machine-readable validation summary.
- Add ADR 0090 and applied Linux PSI/poll plus Clang analyzer reviews. Trigger delivery is proactive
  host-local load shedding, not a real-time deadline, atomic cross-resource snapshot, capacity forecast,
  tuned default, existing-session preemption, or target-fleet qualification.

### PSI admission hysteresis and load shedding (rev0038)

#### Exact host-local pressure policy

- Add an optional delegated-root cgroup-v2 PSI admission gate for new Ratox PTYs. Configure independent
  CPU `some avg10`, memory `full avg10`, and I/O `full avg10` maxima as exact integer basis points in
  `0..10000`, plus one common validated hysteresis width. Keep the policy host-local, default-off, and
  outside terminal profiles, authority records, and the Ratox wire protocol.
- Extend the PSI parser to retain exact `avg10`, `avg60`, and `avg300` values without floating point
  while preserving the rev0035 cumulative-total parser. Require canonical two-decimal percentages,
  reject values above `100.00`, duplicate/missing current fields, malformed spacing, truncation,
  overflow, and oversized evidence, and grammar-check future numeric fields/classes without assigning
  them current semantics.
- Close only when any enabled metric is strictly above its maximum. Once closed, reopen only when every
  enabled metric is at or below `maximum-hysteresis`; equality remains exact at both boundaries.
  Any read, parse, or accounting-state failure rejects and latches closed until a later complete sample
  satisfies every reopen boundary.

#### Descriptor-pinned startup and mutation ordering

- Build the pressure controller before Agent listener/network exposure. Require the normalized
  daemon-owned cgroup-v2 delegation, pin `cgroup.pressure` and each configured PSI file by descriptor,
  require exact enabled accounting before and after each sample, and preflight one complete sample.
  Construct the controller under the signed host lease before resource-policy probes or orphan-recovery
  mutation. Capability/configuration failure aborts host activation, while a valid high-pressure startup
  sample remains a live admission decision.
- Sample synchronously under one controller mutex before aggregate reservation, cgroup-leaf creation,
  PTY/helper creation, or payload mutation. A rejected request therefore consumes no aggregate budget
  and creates no child or session cgroup; later profile, aggregate, cgroup, PTY, confinement, and
  supervision checks remain unchanged.
- Add CLI policy options and owner-private runtime projection for configuration, thresholds, latch state,
  saturation-safe check/admit/reject/failure/transition counts, last-sample validity and typed local
  failure class, and last valid configured observations. Normalize an admission-time sample/evaluation
  failure to local `unavailable` rather than misclassifying kernel evidence as a peer protocol error.
  Keep the projection unlabeled and content free.

#### Proof surface and qualification boundary

- Add exact parser/evaluator boundary tests, malformed decimals, missing observations, zero/full-range
  thresholds, policy validation, CLI rejection, Agent startup validation, runtime projection, ordinary
  filesystem refusal, and no-mutation configuration failure. The direct owned registry grows from 351
  to 356 checks.
- Add a nineteenth default CTest route for a real private-cgroup PSI controller. Where the kernel exposes
  per-cgroup PSI, it accepts a valid sample, forces `cgroup.pressure=0`, proves fail-closed latching and
  exact counters, restores accounting, proves one reopen, serializes a concurrent admission burst, and
  proves disabled-accounting startup refusal. The construction host lacks `cgroup.pressure`, so this
  route records a named capability skip rather than synthetic positive evidence.
- Harden the exclusive Agent/session stress proof after prequalification exposed a scheduler-sensitive
  one-second deterministic-mock probe deadline at repetition 78. Preserve exact six-reply and arrival-
  rank assertions, but allow five seconds for the real owner/event/control thread path so construction-
  host scheduling pauses cannot be mislabeled as transport loss.
- Bound retained replay payloads by applying `strip --strip-unneeded` only to copied product, test,
  provider, and fuzzer binaries before checksumming and prebuilt replay. Preserve dynamic symbols and
  executable behavior, keep unstripped build trees outside the archive, and retain full raw matrix,
  sanitizer, race, fuzz, stress, and process transcripts. This removes redundant debug bulk instead of
  relaxing the repository datacube's strict 128,000,000-byte ceiling.
- Add ADR 0089 and a current Linux PSI/cgroup-v2/source review. PSI averages remain recent trends rather
  than atomic cross-resource capacity, forecasts, service guarantees, tuned defaults, or production
  qualification. The canonical terminal profile remains v5 and the Ratox wire protocol remains
  unchanged.

### Memory-work, swap-failure, freeze, and IRQ accounting (rev0037)

#### Descriptor-pinned memory and swap work

- Open protected `memory.stat` before payload attachment for every session when available, and require
  it when any memory or swap policy is configured. Require unique canonical `pgfault` and
  `pgmajfault`; accept `pgscan`/`pgsteal` and `pswpin`/`pswpout` only as complete optional tuples;
  reject partial, duplicate, malformed, unterminated, oversized, or overflowing evidence while
  accepting unrelated future canonical numeric fields.
- Open protected `memory.swap.events` and retain exact `high`, `max`, and `fail` counters. Make the
  interface mandatory when an IoTox swap ceiling is configured and optional otherwise, without
  conflating system-wide swap-allocation failure with a cgroup-limit event.
- Require exact zero fresh-leaf baselines, then read the same pinned descriptors after recursive
  quiescence and before exact leaf removal. Any protected read or parse failure makes the whole
  session outcome incomplete and suppresses all partial controller evidence.

#### Freezer duration and IRQ/SOFTIRQ stalls

- Open independently optional protected `cgroup.stat.local` and retain cumulative `frozen_usec`.
  Extend the live private-cgroup oracle to freeze and thaw an attached payload, require positive
  duration where the interface exists, and compare the exact final kernel record with the one-shot
  outcome.
- Open independently optional protected `irq.pressure`. Add a dedicated bounded PSI parser requiring
  the current kernel's complete `full` class rather than fabricating a nonexistent IRQ `some` class;
  validate rolling averages but retain only absolute total microseconds. Accept well-formed future
  classes without assigning them current semantics.
- Extend the live lifecycle workload with post-attachment anonymous page faults and require positive
  fault accounting when `memory.stat` is available. The construction host does not expose
  `irq.pressure`, so no positive live IRQ PSI result is claimed.

#### Capability-aware private projection and proof surface

- Add whole-interface and nested-tuple observed-session counts plus saturating page-fault,
  major-fault, page-scan, page-reclaim, swap-in, swap-out, swap-high, swap-max, swap-fail,
  freezer-microsecond, and IRQ-full-microsecond totals to owner-private runtime status. Keep the
  projection unlabeled and outside authorization, admission, enforcement, alerting, adaptive policy,
  and causal attribution.
- Extend direct valid/malformed parser tests, optional-capability semantics, one-shot duplicate
  suppression, whole-outcome incompleteness, saturation, runtime projection, live descriptor equality,
  and the cgroup-record fuzzer. The direct owned registry grows from 348 to 351 checks while the
  18-entry default CTest surface remains unchanged.
- Add ADR 0088 and a current Linux cgroup-v2/PSI/source review. The terminal profile remains canonical
  v5 and the Ratox wire protocol remains unchanged.

### Peak-resource kernel accounting (rev0036)

#### Descriptor-pinned lifetime high-water marks

- Open independently optional protected `pids.peak`, `memory.peak`, and `memory.swap.peak` descriptors
  before payload attachment. Require canonical zero in the fresh leaf, then retain each exact lifetime
  high-water mark after recursive quiescence and before exact inode removal. Preserve interface absence
  explicitly rather than manufacturing zero support.
- Add a strict 64-byte single-value parser requiring canonical unsigned decimal plus LF. Reject signs,
  padding, leading zeroes, overflow, truncation, extra lines, and oversized evidence. Read only; IoTox
  never resets peak files.
- Aggregate each peak interface with a saturation-safe observed-session count, sum, and maximum. These
  are independent session high-water marks, not simultaneous host demand, working sets, or reservations.

#### Quota-independent complete CPU outcomes

- Attempt protected `cpu.stat` observation for every session, including sessions without configured CPU
  quota. Keep the interface mandatory when quota policy is present and optional otherwise.
- Require the complete `usage_usec`/`user_usec`/`system_usec` work tuple. Accept the bandwidth
  `nr_periods`/`nr_throttled`/`throttled_usec` tuple only all-or-none, and accept the nested
  `nr_bursts`/`burst_usec` tuple only all-or-none. Reject partial or detached tuple evidence while
  remaining compatible with controller-disabled and older-kernel records.
- Publish explicit work, bandwidth, and burst capability counts plus saturation-safe user, system,
  usage, period, throttle, and burst totals. Keep all projection owner-private, unlabeled, and outside
  authorization, admission, adaptive policy, and causal attribution.

#### Proof surface

- Extend bounded parser, malformed-record, optional-capability, one-shot aggregation, saturation, runtime
  projection, and fuzz coverage. The lifecycle private-cgroup oracle proves nonzero CPU work retention
  without IoTox quota policy and exact post-exit preservation of every available peak file.
- Make the whole-binary asynchronous lifecycle oracle sanitizer-aware without weakening its assertions:
  normal builds retain the original deadlines, while ASan and TSan builds apply a compile-time bounded
  multiplier to callback, projection, FIFO, and shutdown waits and extend only the enclosing CTest
  watchdog. This removes host-load false negatives while keeping every expected journal record exact.
- Preserve the 18-entry default CTest surface. The construction host passes the expanded lifecycle and
  default suites; memory, CPU-bandwidth, and I/O controller qualification routes retain named skips when
  writable preactivated delegation is unavailable.
- Add ADR 0087 and an applied current Linux cgroup-v2 review. The terminal profile remains canonical v5
  and the Ratox wire protocol remains unchanged.

### Pressure-stall kernel accounting (rev0035)

#### Exact completed-session PSI outcomes

- Add `CgroupPressure` and a bounded LF-terminated parser for cgroup-v2 PSI records. Require one
  canonical `some` class and accept one optional `full` class; validate all three rolling percentages
  plus absolute `total`, reject duplicate/malformed/overflowing evidence, and accept only well-formed
  future numeric fields/classes.
- Open protected optional `cpu.pressure`, `memory.pressure`, and `io.pressure` descriptors before
  helper attachment for every session leaf. When `cgroup.pressure` exists, require exact enabled state.
  Require a zero cumulative baseline, then capture absolute microsecond totals after recursive
  quiescence and before exact inode removal.
- Preserve whole-interface and `full` absence explicitly rather than converting unsupported metrics to
  zero. Any protected read/parse failure makes the outcome incomplete and contributes no partial PID,
  memory, CPU, I/O, or PSI counters while proved-empty cleanup may still finish.

#### Saturating private projection

- Aggregate CPU, memory, and I/O `some` and `full` stall microseconds independently with saturating
  arithmetic. Add per-resource observed-session and observed-`full` counts so zero totals do not imply
  universal support.
- Publish twelve new owner-private status fields without session, profile, payload identity, process,
  device, command, path, peer, error-string, or terminal-content labels. Validate but deliberately do
  not retain `avg10`, `avg60`, or `avg300`.
- Keep PSI out of enforcement and admission. rev0035 does not register threshold triggers, sample live
  rates, adapt policy, infer capacity, guarantee latency/throughput, or diagnose causal operations.

#### Proof surface

- Extend the direct owned registry from 344 to 346 tests with valid/invalid PSI grammar, optional
  `full`, future-field compatibility, one-shot aggregation, saturation, and runtime projection.
- Extend the terminal-cgroup fuzzer with PSI input and the capability-aware live memory, CPU, and I/O
  routes with exact pre-removal-record versus one-shot-outcome comparisons when the kernel interfaces
  exist. The construction host passes the lifecycle route; controller-specific routes retain named
  skips where writable preactivated delegation is unavailable.
- Add ADR 0086 and an applied Linux kernel PSI/cgroup-v2 review. Correct the stale public profile API
  comment to identify v5 emission and v1-v4 decoding; the canonical profile format and Ratox wire
  protocol remain unchanged.

### I/O bandwidth and kernel accounting (rev0034)

#### Canonical device-rate policy

- Emit canonical `iotox-terminal-profile-v5` with one exact numeric block-device identity and ordered
  read/write BPS and IOPS fields. Continue strict decoding of canonical v1 through v4 records;
  migration never invents an I/O device or ceiling. Add a current v5 fuzz seed while retaining all
  historical seeds.
- Add `CgroupIoDevice` and four optional positive I/O ceilings to host/profile policy, plus
  `--ratox-cgroup-io-device`, `--ratox-cgroup-io-rbps`, `--ratox-cgroup-io-wbps`,
  `--ratox-cgroup-io-riops`, and `--ratox-cgroup-io-wiops`. Reject `0:0`, noncanonical device
  numbers, device-only policy, ceiling-only policy, zero ceilings, and values above `INT64_MAX`.
- Compose host/profile I/O policy only for the same exact `MAJOR:MINOR`, selecting the lower
  configured value independently in each direction. A device mismatch fails activation rather than
  redirecting or unioning policy. Request the delegated `io` controller, write one complete `io.max`
  line with explicit `max` values, and require semantic kernel readback before payload attachment in
  both startup probes and production sessions.

#### Teardown-time I/O outcomes

- Add strict bounded nested-key parsers for `io.max` and `io.stat`. Device and key order is irrelevant;
  duplicate/noncanonical data fails closed; all standard `io.max` keys and all read/write `io.stat`
  counters are required; discard byte/operation counters must either both appear or both be absent,
  with an absent pair mapping to zero; unrelated future well-formed fields are
  accepted.
- Open a protected read-only `io.stat` descriptor before attachment and require a zero known-counter
  baseline. After recursive quiescence and before exact inode removal, retain saturating cumulative
  read/write/discard bytes and operations alongside the existing PID, memory, and CPU outcome. A
  statistics failure contributes one incomplete outcome without obstructing proved-empty cleanup.
- Publish six new cumulative owner-private runtime counters without device, profile, process, command,
  path, peer, or terminal-content labels. I/O rates remain outside aggregate reservation because
  `io.max` limits traffic but does not reserve physical media service.

#### Proof surface and retained limits

- Keep the direct owned registry at 344 tests while extending profile migration/composition, CLI,
  nested controller parsing, malformed-record, overflow, one-shot aggregation, and runtime projection
  cases. The 18-entry default CTest suite passes on the construction host; live memory/PID, CPU, and I/O
  controller routes retain their named environmental skips.
- Add ADR 0085, the canonical profile v5 contract, and an applied Linux kernel/systemd review. The
  construction host exposed the `io` controller and real `io.stat` data but mounted cgroup v2
  read-only, so no synthetic positive `io.max` result is reported. A target deployment still requires
  a writable exclusive delegation and a device-specific load oracle.
- Correct retained-artifact metadata generation to derive the current default CTest entry and fuzzer
  target counts instead of preserving obsolete hard-coded values; add a dedicated nested cgroup-record
  fuzzer, bringing the retained parser/state surface to eleven targets.
- Bind retained evidence to an exact committed source tree: artifact refresh now refuses tracked,
  staged, or untracked source changes outside `artifacts/`, authenticates the current binary/report
  surface before executing it, and emits a checksummed revision-owned transcript snapshot without
  duplicating the large executable payload.

### Memory-high and kernel outcome telemetry (rev0033)

#### Canonical soft-memory policy

- Emit canonical `iotox-terminal-profile-v4` with ordered
  `cgroup-memory-high-bytes=none|<u64>` between process and hard-memory fields. Continue strict
  decoding of canonical v1, v2, and v3 records; migration never invents a high threshold. Add a v4
  fuzz seed while retaining earlier-version seeds.
- Add `maximum_memory_high_bytes` to host/profile cgroup policy and
  `--ratox-cgroup-memory-high-bytes N` to the host CLI. Require positive page-aligned values and reject
  a high threshold above a hard maximum within one envelope.
- Compose host/profile high thresholds by monotone minimum and clamp the effective high value to the
  effective hard maximum across policy layers. Request the memory controller, set whole-session OOM
  grouping, write `memory.high`, and require exact kernel readback during both startup preflight and
  production session construction. Aggregate memory admission remains based on finite hard
  `memory.max`, not the throttle boundary.

#### Teardown-time kernel outcomes

- Prefer protected read-only `pids.events.local` and `memory.events.local` descriptors, falling back
  to their hierarchical counterparts only when the local kernel interfaces are unsupported; open
  `cpu.stat` only for configured CPU bandwidth. Require a zero known-counter baseline before attaching
  the blocked helper.
- Add bounded future-key-compatible flat-counter parsers. Required keys, canonical unsigned decimal,
  complete LF termination, and uniqueness are strict; unknown keys are accepted; older kernels may
  omit `oom_group_kill`.
- After recursive `populated=0` and before exact leaf removal, capture one content-free outcome with
  PID-limit hits, memory high/max/OOM activity, CPU usage, and CPU throttling. Return it once and
  aggregate complete outcomes with saturating arithmetic. A statistics failure contributes an
  incomplete-outcome count without obstructing proved-empty cleanup; unproved teardown claims no
  completed outcome.
- Keep the factory-owned telemetry accumulator available when aggregate reservation ceilings are
  disabled. Publish only cumulative owner-private counters, without profile/session labels, payload
  identity, command, path, peer, error string, or terminal content.

#### Proof surface and retained limits

- Expand the direct owned registry from 337 to 340 tests with profile v4 migration/composition,
  memory-high validation, keyed controller parser, saturating one-shot outcome aggregation, CLI, and
  runtime projection coverage. Split the real-kernel resource oracle into independent memory/PID and
  CPU routes, growing the default CTest surface from sixteen to seventeen entries. The memory route
  requires exact `memory.high` readback, live high-threshold pressure, and preservation of observed
  PID rejection and memory throttling; the CPU route preserves observed bandwidth throttling.
- Add ADR 0084, the canonical profile v4 contract, and an applied Linux kernel/systemd review.
  `memory.high` is a reclaim/throttling boundary rather than a hard reservation or OOM guarantee;
  cumulative outcomes are not sampled rates, PSI, adaptive control, per-session history, or
  target-fleet qualification.
- Lock release identity at CMake configure time: project version, numeric components, `REVISION`,
  revision number, codename, and the executable's constexpr header must agree. This turns the stale
  binary stamp found during rev0033 qualification into an immediate configuration failure.

### Exact rational CPU reservation admission (rev0032)

#### Canonical rational accounting

- Extend the host-only aggregate cgroup reservation policy with an optional CPU quota and accounting
  period. An omitted period uses 100000 microseconds, matching the documented `cpu.max` default; a
  period without a quota is invalid. Every enabled effective session policy must provide a finite CPU
  quota when aggregate CPU admission is configured.
- Treat CPU bandwidth as the exact positive rational `quota / period`. Compare session and aggregate
  ratios with the existing continued-fraction algorithm, avoiding floating point and overflowing
  cross-products. Normalize a session quota to the administrator-selected aggregate period only after
  GCD reduction. Ratios requiring fractional quota microseconds fail closed rather than being rounded.
- Resolve process, memory, swap, and normalized CPU quota into one canonical aggregate charge. The
  production ledger checks and charges the complete vector atomically under one mutex with
  subtraction-based remaining-capacity arithmetic.

#### Lifecycle and activation enforcement

- Carry normalized CPU quota through the move-only reservation token, move construction/assignment,
  exact rollback, proved-teardown release, conservative stranding, current totals, and peak totals. A
  capacity refusal remains `resource_exhausted`; missing, oversized, or nonrepresentable policy remains
  `invalid_argument` without changing admission counters.
- Validate every enabled profile's composed CPU envelope during Agent activation before delegated-tree
  recovery or networking. Independently recompute the same exact charge inside the production POSIX
  factory before helper validation, filesystem opening, PTY/cgroup creation, or process spawn. Failed
  spawns release the normalized CPU charge while preserving peak ordering evidence.
- Add `--ratox-cgroup-aggregate-cpu-quota-us` and
  `--ratox-cgroup-aggregate-cpu-period-us`. Publish configured CPU presence, quota, accounting period,
  current normalized quota, and peak normalized quota in the owner-private runtime status.

#### Proof surface and retained limits

- Expand the direct owned registry from 336 to 337 tests. A bounded rational lattice checks more than
  one thousand quota/period combinations against an independent small-integer oracle, alongside exact
  normalization, rounding rejection, concurrent saturation, release/strand, Agent, factory rollback,
  CLI, and runtime projection coverage.
- Add ADR 0083 and an applied Linux kernel/systemd review. Aggregate CPU accounting is conservative
  average-bandwidth admission; it does not align session period boundaries, enforce a parent
  `cpu.max`, model burst concurrency, reserve processor time, cover CPU weights/real-time/deadline
  scheduling, or establish production readiness.

### Aggregate cgroup reservation admission (rev0031)

#### Exact host-wide admission ledger

- Add an optional administrator-owned aggregate reservation ceiling for process count, memory bytes,
  and swap bytes across all simultaneously live production Ratox PTY sessions. Each configured
  dimension requires a finite effective per-session cgroup maximum; one session that cannot fit even
  on an otherwise idle host fails activation rather than becoming a permanently impossible policy.
- Reserve the exact effective maxima after host/profile composition. The ledger uses one mutex and
  overflow-safe remaining-capacity comparisons, so concurrent claims are all-or-nothing and can never
  transiently over-admit. Capacity refusal is surfaced as `resource_exhausted`; malformed or
  unaccountable policy remains `invalid_argument`.
- Represent admission ownership as a move-only RAII reservation. Pre-spawn failures and post-spawn
  failures whose cleanup proves both direct-child reap and exact cgroup removal release automatically,
  while a successful PTY retains its charge through descendant termination, delegated-cgroup
  quiescence/removal, and leader reap. If cleanup cannot prove that boundary, the token strands its
  exact charge instead of under-accounting possible live work; subsequent admissions remain
  conservatively fail closed until restart recovery. Explicit release and stranding are idempotent.

#### Pre-network and production-path enforcement

- Add `--ratox-cgroup-aggregate-pids-max`,
  `--ratox-cgroup-aggregate-memory-max-bytes`, and
  `--ratox-cgroup-aggregate-swap-max-bytes`. Aggregate policy is host-only, never appears in a local
  profile record or Ratox packet, requires an explicit delegated cgroup-v2 root, and cannot be paired
  with an injected process factory that cannot prove enforcement.
- Validate every enabled profile's effective composed envelope before acquiring a listener or exposing
  Ratox networking. A configured aggregate dimension with no matching per-session maximum, an
  unaligned byte ceiling, or a per-session maximum above the aggregate ceiling fails closed with the
  profile context.
- Independently reconstruct and enforce the same admission contract inside the production POSIX PTY
  factory. Capacity is charged before helper validation, executable/directory opening, PTY/socket
  construction, cgroup-leaf creation, or process spawn, closing activation-only and early-failure
  bypasses.

#### Bounded evidence and retained scope

- Publish configuration-presence bits, exact configured aggregate maxima, current and peak active
  reservations, current and peak reserved pids/memory/swap, capacity-rejection count, and stranded-
  reservation count in the
  private runtime status. Final peaks and rejections survive factory withdrawal during shutdown;
  profile IDs, identities, commands, paths, and terminal bytes remain absent.
- Expand the direct owned registry from 332 to 336 checks with aggregate validation, exact RAII
  accounting, conservative stranded-charge retention, concurrent saturation, factory rollback
  ordering, CLI, Agent pre-network, and runtime
  projection coverage. The sixteen-route CTest surface remains unchanged; privileged
  controller-enforcement evidence still records a named skip when this host lacks the complete
  delegated controller topology.
- Add ADR 0082 and an applied Linux cgroup-v2/systemd review. The new ledger is conservative
  application admission over configured maxima, not physical memory preallocation or a replacement
  for a parent service cgroup. rev0031 intentionally excludes aggregate CPU rationals, `io.max`,
  PSI-adaptive admission, privileged co-writer defense, target-fleet qualification, physical-host R7
  qualification, independent audit, and production readiness.

### Profile-scoped cgroup budget ceilings (rev0030)

#### Canonical local profile policy

- Add `CgroupResourceLimits` to the local terminal `Profile` model and advance the canonical encoder
  to `iotox-terminal-profile-v3`. Five ordered `none|u64` fields carry profile-local process, memory,
  swap, CPU-quota, and CPU-period policy. Canonical v1/v2 records remain readable and migrate to v3
  with an empty profile budget; no Ratox wire or remote selector changes.
- Reuse one public validator for host and profile envelopes. Preserve the fail-closed `pid_t`, signed
  quota, page-alignment, meaningful zero-swap, and quota/period invariants so profile decoding, Agent
  activation, CLI parsing, and factory admission cannot drift.
- Add a current v3 fuzz seed while retaining v1 migration coverage and strict byte-canonical
  decoder checks. Update the terminal-profile fuzz oracle to treat semantic v1/v2-to-v3 migration,
  rather than unchanged source byte length, as the public-encoder invariant.

#### Monotone host/profile composition

- Compose the administrator-owned host ceiling and resolved local profile budget before startup
  preflight and again inside the production POSIX factory. Process, memory, and swap maxima select the
  smaller configured value; an absent side inherits the configured side. A profile can tighten or add
  policy but can never weaken host policy.
- Select CPU bandwidth by the lower exact `quota/period` rational, treating an omitted period as
  100,000 microseconds. The implementation uses a continued-fraction comparison rather than floating
  point or overflow-prone 64-bit cross-products; equal ratios retain the host representation.
- Reject any enabled profile whose effective budget lacks an explicit delegated cgroup-v2 root. The
  production factory independently recomputes and validates the effective policy before filesystem or
  spawn work, closing activation-only bypasses.

#### Exact preflight and bounded observability

- Compute every enabled profile's effective policy after acquiring the signed host-incarnation lease
  and before orphan recovery, PTY-factory construction, or network activation. Deduplicate disposable
  controller probes by `(payload identity, effective budget)`, not identity alone, so two profiles
  sharing a uid but carrying different limits are each proved.
- Publish only aggregate configuration truth: host-budget configured, enabled profile-budget count,
  and distinct preflight-policy count. Profile IDs, identities, limits, paths, commands, and terminal
  bytes remain absent from runtime status.
- Expand the direct owned registry from 330 to 332 checks with v1/v2 migration, v3 round-trip, exact
  CPU-composition/overflow, invalid canonical form, Agent pre-network, production-factory, and runtime
  metric coverage. The default CTest surface remains sixteen routes; privileged real-controller
  evidence still records a named skip when this host does not delegate the complete requested
  controller set.
- Add ADR 0081 and an applied Linux cgroup-v2/systemd delegation review. rev0030 still does not claim
  `io.max`, PSI-based or aggregate admission, protection from privileged co-writers, target-fleet
  controller qualification, physical-host R7 qualification, independent audit, or production
  readiness.

### Controller-enforced cgroup resource budgets (rev0029)

#### Fail-closed host policy

- Add one optional global `CgroupResourceLimits` envelope for every production hardened PTY session.
  It maps process count, memory, swap, and CPU bandwidth to `pids.max`, `memory.max`,
  `memory.swap.max`, `memory.oom.group=1`, and `cpu.max`; empty policy preserves rev0028
  lifecycle-only cgroups.
- Add one-binary flags for pids, page-aligned memory/swap bytes, CPU quota, and CPU period. Shared
  validation rejects limits without a delegated root, zero/out-of-range task counts, ambiguous CPU
  pairs, sub-millisecond bandwidth, oversized periods, and unaligned memory before filesystem access.
- Require every requested controller to be both advertised in `cgroup.controllers` and activated in
  `cgroup.subtree_control`. Missing, inactive, malformed, unsafe, unwritable, or inexact controls fail
  closed instead of silently degrading containment.

#### Pre-network and pre-attachment proof

- After the signed host-incarnation lease but before orphan recovery, create one disposable normal
  session leaf for each distinct enabled payload identity. Apply/read back the complete policy and
  remove the exact empty leaf before recovery mutation, production PTY-factory construction, or Ratox
  network activation.
- Repeat the controller proof for every real session and apply every value before moving the blocked
  helper into the leaf. Preserve the literal non-threaded `domain` invariant required by
  `cgroup.kill`; do not accept `domain threaded` as a lifecycle-compatible substitute.
- Thread the policy through Agent configuration and the production POSIX PTY factory while rejecting
  alternate unrooted call paths. No Ratox wire, profile, authority, or local protocol version changes.

#### Executable evidence and scope

- Add parser, CLI, Agent, factory, controller-activation, exact read-back, and cleanup coverage. The
  direct owned registry grows from 329 to 330 checks.
- Split lifecycle recovery and controller enforcement into independent process-oracle routes so an
  unsupported controller topology cannot suppress otherwise-runnable lifecycle evidence. The default
  suite grows from fifteen to sixteen CTest entries.
- Expand the controller route with exact preflight removal, `pids.max`/`EAGAIN`,
  `pids.events:max`, `cpu.stat:nr_throttled`, memory/swap/OOM-group state, inactive-controller
  refusal, recursive kill, and exact removal. On this cloudtainer the fresh hierarchy is
  `domain threaded`, so both routes record named skip code 77 rather than fabricating a non-threaded
  lifecycle or controller-enforcement pass.
- Add ADR 0080 and an applied Linux cgroup-v2/CFS/systemd delegation review. rev0029 does not claim
  I/O or PSI policy, per-profile budgets, aggregate host-wide resource admission, protection from
  privileged co-writers, target-fleet qualification, physical-host R7 qualification, independent
  audit, or production readiness.

### Boot-bound delegated-cgroup orphan recovery (rev0028)

#### Exact daemon-incarnation ownership

- Replace PID-only delegated PTY leaf names with canonical versioned names that bind the creating
  daemon's Linux boot ID, positive PID, pinned `/proc/<pid>/stat` field-22 start time, and local
  sequence. Strict parsing rejects noncanonical, zero, overflow, malformed, and reserved-prefix
  variants.
- Classify owners through verified procfs, descriptor-relative process reads, `pidfd_open`, a second
  start-time witness, task-state validation, and a nonblocking pidfd poll. Boot mismatch, process
  absence, exact start-time mismatch, or terminal task state proves staleness; unreadable or malformed
  evidence never authorizes cleanup.

#### Serialized bounded startup recovery

- Acquire the durable signed Ratox host-incarnation lease before delegated-root recovery, PTY-factory
  construction, listener publication, or network startup. A competing legitimate daemon therefore
  cannot concurrently mutate the delegated namespace.
- Open and validate genuine procfs and cgroup-v2 roots without following links. Pin every reserved
  candidate to one inode and validate daemon ownership, restrictive mode, domain type, empty subtree
  controls, and absence of child cgroups. Preflight the complete bounded set before the first mutation.
- Preserve exact live versioned owners. For proved-stale versioned leaves, issue recursive
  `cgroup.kill`, wait on kernel `cgroup.events` change notifications until bounded recursive
  `populated 0`, revalidate the exact inode, and remove it. The recovery and destructor paths avoid
  millisecond sleep polling. Remove empty legacy PID-only leaves, but fail closed on populated legacy
  or malformed reserved entries.
- Publish only aggregate recovery counters. Boot IDs, PIDs, paths, profiles, commands, and terminal
  bytes remain absent from runtime status.

#### Kernel-backed evidence and scope

- Add strict boot-ID/session-name/owner-incarnation parser checks, live/exited/zombie/mismatch owner
  classification, bounded policy validation, ordinary-filesystem refusal, and Agent pre-transport plus
  host-lease ordering tests. The direct owned registry grows from 322 to 329 checks.
- Add a fifteenth default CTest route that mounts a fresh cgroup-v2 hierarchy inside isolated user,
  mount, and cgroup namespaces. It proves live preservation, deliberate creator-crash reclamation,
  recursive payload death, exact removal, empty-legacy cleanup, populated-legacy refusal, malformed
  refusal, and no premature mutation when the scan bound is exceeded.
- Treat `dirfd()` as fallible in both the cgroup child scan and fallback procfs session sweep. The
  daemon now refuses cleanup or signaling before any descriptor-relative operation when an adopted
  directory stream cannot expose a valid descriptor; focused Clang static analysis is clean after
  the correction.
- Add ADR 0079 and an applied boot-bound cgroup recovery review. rev0028 does not claim protection
  from root or an equivalent delegated-root writer, cgroup resource policy, namespace isolation,
  populated-legacy migration, PTY state continuity, power-cut durability, target-fleet qualification,
  independent audit, or production readiness.

### Process-pinned bounded fair local IPC admission (rev0027)

#### Exact connection-process lifetime

- Obtain `SO_PEERPIDFD` immediately after accepting each control client and the active terminal
  controller when Linux 6.5+ and the build headers expose it. The returned pidfd identifies the
  process that established that exact Unix-domain connection without reopening a reusable numeric
  PID.
- Poll control-client sockets beside their connection pidfds. A silent descriptor inherited or
  passed to another process can no longer keep a pending admission lease alive after the exact
  connector exits. Socket readability wins when a final complete request and process exit become
  visible in the same poll cycle.
- Pin the active terminal connection before its first `OPEN`. The single-controller slot is released
  promptly when the connector exits even when another process deliberately retains the connected
  file description; the existing per-record sender pidfd remains the post-`OPEN` authority fence.
- Pin the control server from the client side and poll its pidfd beside response readiness. A server
  process that exits after exporting its accepted descriptor can no longer hold a CLI request until
  the full response timeout. A complete response already queued before exit remains consumable.
- Preserve a runtime-probed compatibility path: kernels or headers without `SO_PEERPIDFD` retain the
  rev0026 credential, lease, and sender-pidfd protections rather than failing product startup.

#### Multiplexed administrative requests

- Replace the serial `control.sock` worker with one bounded readiness loop over the listener, stop
  event, and all accepted pending clients. Every client retains an independent complete-record lease,
  so a silent peer no longer serializes ready requests behind its timeout.
- Add explicit global and per-process pending-client quotas, accept-refill and request-per-cycle
  budgets, and startup validation for every bound. Overload responses are best-effort nonblocking and
  decode an already queued record only to preserve request correlation; they never reach the handler.
- Preserve ready-before-expiry ordering, message-bound credential/pidfd verification, ancillary-rights
  rejection, exact socket-inode ownership, and callback-safe stop semantics.

#### Nonblocking active-terminal contention

- Replace the active terminal stream's synchronous shared contender grace with a persistent bounded
  contender set polled alongside the active client, owner pidfd, wake event, and listener. Silent
  contenders now expire independently without pausing active input or outbound drain.
- Add global and per-process contender quotas, accept-refill and first-record-decode budgets, and a
  finite configurable contender lease. A complete contender packet is authenticated and decoded only
  to correlate the busy response; it is never dispatched into the controller state machine.
- Keep active death ahead of listener work so a successor still queued in the kernel when HUP is
  observed remains eligible for normal admission. DETACH continues to suppress new acceptance during
  the bounded OUTPUT_ACK drain.

#### Evidence and scope

- Add silent-control coexistence, independent concurrent expiry, global/per-process quota and
  recovery, exact connector-exit release, client-side server-exit release, active-terminal latency,
  terminal pre-`OPEN` connector-exit release, and invalid-limit tests. The direct owned registry grows
  from 313 to 322 checks while retaining fourteen default CTest routes and all rev0026 sender-evidence
  and process-exit cases.
- Add ADRs 0077 and 0078 plus applied Linux readiness/admission and connection-pidfd reviews. rev0027
  improves finite availability inside the owner-private same-UID boundary; it does not claim
  cryptographic isolation among same-UID processes, starvation freedom against an unlimited process
  coalition, callback preemption, namespace isolation, target-fleet qualification, or independent
  production review.

### Message-bound local IPC and process-lifetime fencing (rev0026)

#### Bidirectional kernel sender evidence

- Add one shared Linux `SOCK_SEQPACKET` security layer for administrative `control.sock` and Ratox
  `terminal.sock`. Every request and response now requires a single valid per-record
  `SCM_CREDENTIALS` identity and exact agreement with connection-time `SO_PEERCRED`.
- Enable optional `SO_PASSPIDFD`/`SCM_PIDFD` when supported by the running kernel and require exact
  PID/UID/GID agreement for the delivered process handle. Unsupported pidfd delivery preserves the
  mandatory credential path rather than silently weakening credential checks.
- Parse ancillary data with a fixed 4 KiB ceiling, `MSG_CMSG_CLOEXEC`, duplicate/malformed/truncation
  rejection, and exhaustive closure of received `SCM_RIGHTS` descriptors before fail-closed denial.
- Authenticate response records on both clients, preventing a fork-inherited accepted server
  descriptor from impersonating the original accepting process. No protocol payload or wire-version
  change is required.

#### Terminal ownership and administrative availability

- Bind the terminal controller slot to the process that sends the first valid record. Retain its
  delivered pidfd or an exact `pidfd_open` fallback and release the slot when that process exits, even
  when the socket descriptor survives in another process.
- Add a finite 1 ms..60 s complete-request lease to `control.sock`, poll stop and client readiness
  together, and prevent a silent accepted process from holding the administrative worker forever.
- Preserve reachable owned control listeners, recheck stale device/inode identity before unlink,
  retain replacement inodes at shutdown, and make start/stop cleanup callback-safe and exact-inode
  owned.

#### Adversarial evidence and scope

- Add fork-inherited request/response, request/response descriptor injection, pidfd handoff, silent
  control client, active-listener, replacement-inode, unsafe-path, and lease-boundary process tests.
- Expand the direct owned registry from 303 to 313 checks while retaining fourteen default CTest
  routes and the complete rev0025 cgroup/confinement surface.
- Add ADR 0076 and an applied Linux local-IPC review. This revision does not claim authorization
  between processes sharing one UID, fairness against a hostile same-UID flood, namespace isolation,
  or independent production security review.

### Delegated cgroup kill and recursive PTY quiescence (rev0025)

#### Kernel-owned hardened-session lifecycle

- Add explicit `--ratox-cgroup-root PATH` configuration for one administrator-delegated cgroup-v2
  subtree. Empty configuration preserves the rev0024 pidfd/procfs contract; any configured failure is
  surfaced and never silently downgraded.
- Resolve the root descriptor-relatively without symlinks, require `CGROUP2_SUPER_MAGIC`, daemon-UID
  ownership, restrictive modes, payload-inaccessible mutation controls, and writable common-ancestor
  migration permission.
- Create one underscore-prefixed, inode-pinned domain cgroup for each hardened PTY; require empty
  process/thread/controller state and recursive `populated 0` before spawn. All controls are
  close-on-exec.
- Attach the still-waitable helper before sending its sealed manifest, then require exclusive initial
  membership and `populated 1`, preventing target code from forking before cgroup membership.
- Route explicit KILL and natural-leader orphan cleanup through `cgroup.kill`; retain HUP/TERM
  pidfd/procfs sweeps; wait for recursive `cgroup.events` quiescence; remove the exact leaf inode; and
  only then reap and report the leader status.

#### Fail-closed profile, parser, and evidence boundary

- Require every enabled configured profile to use baseline/strict confinement, an exact non-root UID
  distinct from the daemon, and cleared supplementary groups. Reject injected factories and malformed
  roots before transport startup.
- Add a bounded strict `cgroup.events` parser with mandatory unique Boolean `populated`, optional
  Boolean `frozen`, duplicate/malformed rejection, and forward-compatible unknown numeric fields.
- Reject ordinary-directory lookalikes, unsupported compatibility profiles, inherited/root/same-UID
  identities, relative roots, and unsafe factory combinations.
- Expand the direct owned registry from 295 to 303 checks while retaining fourteen default CTest
  targets and every rev0024 process-domain/confinement oracle.
- Add ADR 0075, an applied delegated-cgroup review, and explicit nonclaims for crash-restart garbage
  collection, resource quotas, same-UID single-writer violations, and target-fleet qualification.

### Procfd quiescence and terminal process-domain hardening (rev0024)

#### Identity-pinned PTY-session supervision

- Open and verify the actual procfs inventory with `O_NOFOLLOW` plus `PROC_SUPER_MAGIC`, then open
  each numeric member directory descriptor-relatively rather than repeatedly resolving mutable
  `/proc/<pid>` pathnames.
- Parse and validate the reported PID, fixed PTY session, live state, and field-22 start time. After
  `pidfd_open(2)`, re-read through the same pinned process directory and require the session/start-time
  witnesses to match before `pidfd_send_signal(2)`.
- Keep the exited leader waitable and require three consecutive complete inventories with no live
  executable session member before reap. Any observed member resets the quiescence count.
- Add a direct zombie oracle proving that the first and second empty inventories do not reap and the
  third preserves exact status, plus a bounded separate-process-group fork-churn oracle that starts
  shutdown while descendants are still being created.

#### Payload and host process-handle reduction

- Deny `pidfd_open`, `pidfd_send_signal`, `process_madvise`, and `process_mrelease` in baseline/strict
  final payloads while retaining the supervisor's already-open process handles.
- Extend the final-exec report and baseline fence probe with exact compiled syscall count and `EPERM`
  interception evidence before ordinary descriptor/argument validation.
- Seal the long-lived Agent process only when the explicit terminal-host gate is enabled: set and
  verify `PR_SET_DUMPABLE=0`, then set and verify both soft and hard `RLIMIT_CORE=0` before constructing
  Agent state. The operation is idempotent and fail closed.
- Add a child-local process-hardening registry check that proves the seal and confirms the parent
  process policy is unchanged.

#### Evidence and boundaries

- Expand the direct owned registry from 294 to 295 checks while retaining fourteen default CTest
  targets and every rev0023 process/confinement oracle.
- Run the sanitizer whole-binary lifecycle oracle serially so parallel CTest qualification measures
  queue/coalescing behavior rather than contention from unrelated shadow-instrumented registries.
- Add ADR 0074, the applied procfs/pidfd/cgroup comparison, and explicit nonclaims: repeated userspace
  procfs quiescence is not delegated cgroup ownership, `cgroup.kill` atomicity, or proof against every
  adversarial schedule.

### Session-swept argument-fence hardening (rev0023)

#### Argument-aware baseline seccomp

- Added native-endian classic-BPF argument loads with reusable exact-value and bit-mask rules; every
  allowed path restores the syscall-number accumulator before later checks.
- Added one shared, compile-time-checked terminal/console ioctl request table covering controlling-
  terminal detach/reassignment, `TIOCSTI`, line discipline, console, keyboard/font, virtual-terminal,
  and hangup mutations while excluding ordinary PTY window query/resize requests. Production and the
  final-exec oracle consume the same 29-entry build-header-derived table.
- Denied reviewed namespace flags in the architecture-correct legacy `clone(2)` argument, excluded the
  ambiguous legacy `CLONE_NEWTIME` signal-field bit, and made `clone3(2)` return `ENOSYS` so libc can
  retry the inspected path. Real `fork()` and `std::thread` probes prove ordinary creation remains.
- Froze the helper-established lifecycle after final exec by denying `setsid(2)`, controlling-terminal
  detach/reassignment, and `prctl(PR_SET_PDEATHSIG, ...)`.

#### Descriptor and PTY-session containment

- Replaced the `RLIMIT_NOFILE`-bounded descriptor fallback with `close_range(2)` plus two-pass
  `/proc/self/fd` inventory. A non-CLOEXEC descriptor duplicated above 255 is now an explicit native
  negative control, and startup fails before exec if closure cannot be proved.
- Made baseline and strict fail closed unless `pidfd_open(2)`, `pidfd_send_signal(2)`, readable procfs
  identity, and readable procfs inventory work in the actual supervisor environment. Compatibility
  preserves its historical process-group lifecycle.
- Required a close-on-exec child-leader pidfd immediately after spawn. Exit observation prefers
  `waitid(P_PIDFD, ..., WNOWAIT)` and uses the still-waitable direct-child path only for the narrow
  `EINVAL`/`ENOSYS` pidfd-wait compatibility boundary.
- Replaced original-PGID-only shutdown with session-wide PID-identity-aware sweeps. Each candidate is
  selected by `/proc/<pid>/stat` session ID, opened by pidfd, revalidated after acquisition, and
  signaled by pidfd. Repeated SIGKILL sweeps converge across separate shell process groups.
- Kept a naturally exited leader waitable until the remainder of its session is gone, pinning the
  numeric session ID and preserving the leader's original exit status. Startup-failure and destructor
  paths use the same bounded best-effort session cleanup.
- Added native process oracles for every lifecycle fence, high inherited descriptor closure, forced
  separate-process-group shutdown, and natural-leader orphan cleanup; repeated process stress covers
  the full boundary.

#### Evidence and release coherence

- Extended the sanitizer helper exception from ASan to TSan: only those instrumented process lanes omit
  the test profile's finite `RLIMIT_AS`; ordinary debug/release lanes still enforce 512 MiB and the
  final payload remains native.
- Added textual/numeric version and revision coherence through protocol HELLO fields.
- Expanded the direct owned registry from 293 to 294 checks while retaining fourteen default CTest
  targets and the complete rev0022 confinement/R7 evidence surface.
- Added ADR 0073, the applied Linux review, explicit compatibility/nonclaim language, and revision-owned
  compiler, sanitizer, process, and stress evidence.

### Attested evidence and tiered terminal confinement (rev0022)

#### R7 attested raw-evidence chain

- Replaced the historical R7 v1 asserted-duration input with a canonical v2 chain that retains raw
  controller-local and host-local steady-clock timestamps and derives every qualification duration
  without cross-host clock subtraction.
- Added deterministic balanced schedule generation: every twelve-trial block contains all two-route
  by six-load cells once, Fisher-Yates order is reconstructed from a run-ID-and-seed-bound SHA-256
  counter stream, and every trial carries a run-bound token.
- Added exact content-free Ratox event joins. INPUT admission and whole-frame PTY commit now retain the
  same message ID and byte span; OUTPUT append retains its exact produced span. Runtime journals still
  exclude terminal bytes, argv, environment, paths, profiles, and error payloads.
- Added canonical schedule/sample digests and mandatory sizes/digests of retained route and bulk-load
  evidence. Qualification requires distinct nonempty regular files again and rejects aliasing,
  mutation, symlink substitution, size mismatch, or digest mismatch.
- Added two distinct ephemeral Ed25519 capture attestations. Role-separated payloads bind the complete
  unsigned run; signing verifies the local Linux boot ID and derives the advertised public key from
  the owner-only secret before signing; sealing and analysis verify both signatures independently.
- Added `tools/prepare-ratox-r7.py`, shared bounded implementation
  `tools/ratox_r7_evidence.py`, the v2 operator workflow, ADR 0071, and a full 12,000-row self-test that
  rejects sample edits, signature substitution, global event reordering, changed auxiliary evidence,
  and symlink inputs.
- Tightened cross-row invariants so controller timestamps, host timestamps, host event ordinals,
  per-session input spans, and per-session output spans cannot move backward or overlap.
- Removed the v1 cross-clock local-stage sum and added independent p50/p95/p99 diagnostics for every
  same-clock stage and owner queue wait.
- Reworded the evidence claim as `provenance-artifacts-bound=1`, `capture-role-count=2`, and
  `distinct-kernel-boots=1`; physical topology, route topology, and bulk-load semantics are explicitly
  external-review obligations rather than cryptographic claims.
- Hardened exclusive publication with descriptor-relative output creation plus file and parent-directory
  fsync before success is reported.

#### Terminal capability seal and tiered confinement

- Added canonical terminal profile v2 with explicit `compatibility`, `baseline`, and `strict`
  confinement modes. New profiles default to baseline; byte-canonical v1 records remain readable and
  map to compatibility without silent policy strengthening.
- Added bounded runtime capability-ceiling discovery instead of relying on the build header's
  `CAP_LAST_CAP`, with fail-closed refusal if a future ceiling exceeds the reviewed `capget` layout.
- Added a common final-exec capability floor: ambient, effective, permitted, and inheritable sets are
  cleared and read back after identity handling. Privileged contexts that cannot establish the
  required boundary are rejected before target code runs.
- Added privileged securebits and bounding-set sealing: root semantics, set-ID fixup, keep-caps, and
  ambient raising are locked into the safe state; every bounding member is dropped and verified when
  effective `CAP_SETPCAP` is available.
- Added a helper-handoff `PR_SET_DUMPABLE=0` guard before and after credential work, while explicitly
  reporting that ordinary exec may reset final-target dumpability.
- Added the default architecture-checked classic-BPF seccomp baseline. It kills architecture
  confusion, rejects x32 on x86-64, denies a reviewed bounded set of high-risk process, kernel, mount,
  namespace, module, keyring, privileged-I/O, host-identity, and time-mutation interfaces, and verifies
  filter mode.
- Added fail-closed strict mode requiring verified MDWE and Landlock ABI 10. It grants ordinary
  mutation only beneath the non-root working directory, keeps device-node creation denied, grants no
  TCP/UDP port, restricts external pathname/abstract Unix sockets and signals, and never silently
  downgrades when a kernel primitive is unavailable.
- Extended the child startup protocol with named dumpable, securebits, bounding-set, active-capability,
  MDWE, Landlock, and seccomp stages; preserved exact capability substage failures instead of
  collapsing them; and fixed the prior validator ceiling that could reject the existing ambient stage
  as malformed.
- Strengthened the native oracle to prove zero active/ambient capability sets, root bounding-set and
  securebits sealing, baseline syscall denial, inherited-ambient destruction, and either complete
  strict runtime isolation or a named strict fail-closed startup result. The strict enforcement branch
  now covers allowed in-tree rename/socket mutation and denied external file mutation, TCP/UDP
  bind/connect/send, pathname/abstract Unix connect, signals, MDWE, and seccomp.
- Added ADR 0072, terminal profile v2, the applied Linux confinement review, current source index, and
  exact nonclaims for read/execute access, namespaces, cgroups, mount isolation, whole-descendant
  ownership, target-kernel qualification, and production sandboxing.
- Expanded the direct owned registry from 292 to 293 checks while retaining fourteen default CTest
  targets and the rev0021 R7 observability/analyzer surface.
- Removed release-number pinning from the separate-process mock fixtures: they now parse the exact
  tested `iotox --version` identity, preventing a correct revision bump from invalidating or masking
  the full-path gate.

### R7 observability and bounded evidence gate (rev0021)

- Added a fixed-allocation cumulative owner queue-wait histogram with exact 0..4,096 us buckets,
  conservative power-of-two upper bounds above that range, deterministic nearest-rank p50/p95/p99,
  exactness flags, maximum, and an exact count at or above the strict 2 ms gate.
- Added coherent typed accounting for validated sensitive custom-lossless calls, provider attempts,
  acceptance, SENDQ full, peer-not-connected, peer-not-found, provider-contract rejection, and other
  failure. Concurrent runtime readers cannot observe a counter vector that violates its accounting
  invariant.
- Added separate controller and host retained-send pressure telemetry: lifetime retryable rejections,
  current and maximum streak, and live steady-clock age, with active state cleared on success, fatal
  rejection, purge, route loss, and shutdown.
- Added nonzero nondecreasing service-relative steady time to Ratox lifecycle records and projected the
  complete latency, send-outcome, retained-head, and lifecycle evidence through the private runtime
  tree without terminal content.
- Added `tools/analyze-ratox-r7.py`, a bounded fail-closed ASCII TSV parser and deterministic
  qualification report for observed direct UDP and forced TCP beside 0/1/8/16/32/64 bulk streams.
  It enforces exact metadata, finite input/cell bounds, canonical uint64 values, contiguous ordinals,
  feasible stages, one commit, one render, completion, strict owner p99, and direct-UDP tail gates.
- Added opt-in deterministic owned-registry sharding (`IOTOX_TEST_SHARD_COUNT=1..64`). The default
  remains one contamination-sensitive process; ASan/UBSan and TSan presets use sixteen bounded shards.
- Expanded the owned registry from 284 to 292 checks and added the analyzer self-test to the default
  CTest surface, increasing it from thirteen to fourteen targets.
- Fixed stale rev0020 process-fixture assertions discovered by the final rev0021 matrix: the mock and
  one-binary oracle now require the actual revision-21 device description.

### Signed Ratox restart fence and R6 process gates (rev0020)

- Added a move-only process-lifetime Ratox host-incarnation lease acquired before terminal service,
  local listener, or toxcore startup. Client-only activation remains lease-free.
- Added one exact 128-byte `IOTXRIN1` record bound to the stable Ed25519 device identity. It carries a
  nonzero incarnation, its complement, and a signature; first allocation is random below the high bit
  and every successor advances exactly once.
- Hardened the default `<savedata-parent>/ratox/incarnation.state` lane with descriptor-relative
  no-follow traversal, rejected `..`, exact owner/type/mode/link/size checks, a private final 0700
  directory, a 0600 fixed-purpose lock, post-`flock` inode/path revalidation, and fail-closed tamper,
  wrong-device, malformed-record, and exhaustion handling.
- Hardened atomic commit by retaining the private temporary descriptor through `renameat`, verifying
  the installed pathname still names that inode, synchronizing file and directory, and strictly
  reopening and verifying the signed record before returning the lease.
- Closed the first-start hierarchy durability gap: each newly created private directory is fsynced
  after mode enforcement, then its containing directory is fsynced so the new name is durable before
  descendant state is trusted. Descriptor synchronization now retries interruption consistently.
- Changed the enabled-service API default to the unreserved zero incarnation sentinel. Disabled
  construction remains valid, but every enabled direct caller must explicitly inject a reserved
  nonzero lease value.
- Separated authenticated online-epoch route identity from current signed effect authority. A revoked
  ATTACH/RESUME may receive one explicit replayable denial, but cannot spawn, resume, write, resize,
  close, or otherwise affect a PTY.
- Added mock exact-byte Ratox SENDQ retry injection and friend-deletion cleanup for queued epoch,
  session, frozen-packet, and command state so friend-number reuse cannot inherit stale transport
  evidence.
- Added `iotox.ratox-restart-fence-process`, which runs the shipped binary and proves lease exclusion,
  failed-start truth, no contender increment, clean release, signed record shape, and exact successor
  `+1`.
- Retained a full-path R6 separate-process oracle crossing the real Agent, private controller socket,
  mock Tox owner thread, native PTY helper, reconnect, controller replacement, SENDQ pressure, signed
  revocation, explicit denial, daemon restart, and stale-session refusal.
- Preserved `phase=failed` across cleanup after startup failure while still releasing the incarnation
  lease, transport, terminal socket, service, and process resources.
- Expanded the direct owned registry to 284 checks and the default CTest surface to thirteen targets.
- Recorded ADR 0068, the restart-fence source review, process evidence, and exact nonclaims: advisory
  same-host exclusion is not storage rollback protection, power-cut qualification, PTY survival, or
  public-network evidence.

### Controller fault gate (rev0020)

- Added a finite, configurable first-`OPEN` lease to the private terminal server. A connected but
  silent same-user process now receives a typed timeout and releases the sole controller slot without
  publishing a stream or invoking attachment cleanup.
- Added a bounded contender consume-and-deny handshake. While a controller is active, a small fixed
  batch of waiting clients may submit only their first canonical record; the record is never
  dispatched, but its exact stream ID is retained in the typed `resource_exhausted` response.
- Added `iotox.terminal-controller-process`, which drives the installed `iotox` CLI across winner and
  loser contention, abrupt winner death, replacement resume, retained-output rendering, exact output
  acknowledgement, clean detach, and explicit post-server-restart `not_found` behavior.
- Added a bounded two-phase `DETACH`: final output and `DETACHED` drain first, then only exact-stream
  cumulative `OUTPUT_ACK` is admitted for 1 ms..5 s (250 ms default). The listener is omitted during
  this phase so queued successors remain in the kernel backlog rather than spinning or receiving a
  denial for a stream already closing.
- Bound every post-detach socket send to the same absolute drain deadline and reject any non-ACK
  packet before the Agent handler. This keeps the configured availability lease honest even under a
  non-reading local client.
- Added socket tests for silent-OPEN expiry, successor admission, contention detail, exact stream
  identity, invalid admission/drain bounds, final-output ACK commitment, ACK-only post-detach
  dispatch, and admission of a queued successor when active death and listener readiness occur in the
  same service cycle.
- Prioritized terminal active-descriptor data and death over listener contention, preventing a queued
  replacement from being denied on behalf of a controller that has already closed.
- Changed the terminal CLI to accept a connection-scoped `ERROR` before `OPENED`; this is required
  when the single-client server rejects a contender before that contender becomes an admitted
  stream. Every progress or success packet remains bound to the requested random stream ID.
- Eliminated the normal contention race that could surface `Broken pipe` or false stream-ID
  corruption instead of the server's explicit busy result.
- Recorded ADR 0067, the applied Linux socket/poll source review, and the rev0020 protocol,
  architecture, threat, roadmap, and evidence boundaries.
- Expanded the controller-fault slice before the restart-fence work; the completed rev0020 registry
  has 284 checks and thirteen default CTest targets.
- Evidence boundary: the process gate proves local controller replacement and explicit local restart
  semantics. It does not claim that a remote PTY, Agent Ratox client state, or replay buffers survive
  daemon restart, and it does not complete the remote transport/revocation/storage portions of R6.

### Private Ratox controller stream and one-binary terminal (rev0019)

- Added a pure controller-side Ratox v1 state machine with exact confirmed-route and authenticated-
  principal binding, OPEN/RESUME attachment fencing, bounded unacknowledged-input and retained-output
  replay, immutable retained transport packets, cumulative ACK and latest-resize coalescing, ordered
  lifecycle events, and fail-closed duplicate/overlap/gap/generation/message-ID handling.
- Added an independent `--enable-ratox-terminal-client` Agent gate. Client-only activation needs no
  local profile store or PTY factory and creates no process; it constructs the controller before
  transport startup and creates the private local stream only after the Agent reaches its normal
  runtime boundary. Host and controller roles can be enabled independently or together.
- Added local terminal protocol v1: a canonical 32-byte header, a 16 KiB packet payload bound, exact
  OPEN/OPENED/GAP/EXIT structured payloads, strict packet direction and stream-ID rules, typed errors,
  cumulative byte positions, and malformed/noncanonical/overflow rejection.
- Added an owner-private Linux pathname `AF_UNIX` `SOCK_SEQPACKET` server at
  `<runtime>/terminal.sock`. It validates the private real parent, authenticates accepted clients with
  `SO_PEERCRED`, uses close-on-exec/nonblocking descriptors and an `eventfd` wake, admits one local
  stream, never steals a live listener, reclaims only an unchanged stale owned inode, and unlinks only
  the exact socket it bound.
- Added `iotox terminal PEER_PUBLIC_KEY_HEX` and
  `iotox terminal-resume SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]`. The one-binary client restores raw
  terminal state and signal handlers, propagates `SIGWINCH`, writes output before ACK, detaches on
  stdin EOF, and implements beginning-of-line `~.`, `~d`, `~~`, and `~?` escapes.
- Joined the local stream to Agent route truth. OPEN requires an exact live friend, confirmed and
  bilaterally negotiated Ratox session, matching authority online epoch, and a nonzero authenticated
  remote principal. RESUME cannot change peer or principal. Remote replies are accepted only on that
  same route and are ordered into a finite local delivery queue.
- Added controller unit tests for route fencing, exact output overlap, ACK atomicity/coalescing,
  retained input under queue pressure, route-loss resume, generation and gap rejection, exit, close,
  and resource exhaustion. Added protocol and socket tests for canonical shapes, path ownership, peer
  credentials, first-OPEN enforcement, concurrent-client denial, stale reclamation, and inode-safe
  shutdown. Added an Agent boundary test for explicit socket activation, mode/owner checks, typed
  unknown-peer denial, and unlink-on-stop, plus one-binary CTest checks for invalid keys and an absent
  daemon.
- Added a tenth sanitizer-backed fuzzer for the local terminal protocol and seed corpus. Updated the
  build matrix, retained evidence contract, architecture/security/threat documentation, and ADR 0066.
- Froze the exact 32-byte `ITTS` local wire image with a golden vector, including the two-byte payload
  length and four reserved zero bytes, so implementation and protocol documentation cannot drift.
- Hardened pathname connection against aliasing and replacement: terminal endpoints must be absolute,
  embedded NUL bytes are rejected, and the client rechecks owner, mode, socket type, device, and inode
  after `connect(2)` and `SO_PEERCRED`.
- Tightened reliable local-stream state: duplicate OPENED, inconsistent pre-open gaps, duplicate or
  out-of-position OUTPUT, and other impossible `SOCK_SEQPACKET` transitions now fail closed instead of
  being treated as retryable network replay.
- Made RESUME_RESULT replay commitment transactional across all peer-controlled coordinates. A reply
  with a valid input acknowledgement but contradictory output bounds now fails closed without
  releasing any retained input or changing either replay cursor.
- Rejected negative local send deadlines before the first `send(2)` attempt, and publish a local
  terminal stream only after its OPEN handler commits. A policy-rejected OPEN therefore cannot write
  opportunistically or trigger disconnect cleanup for an attachment that never existed.
- Removed a PTY-helper startup classification race. If the configuration socket closes while the
  manifest is being sent, the parent now consults the independent startup-status channel before
  reaping the helper, preserving a deterministic protocol/setup error instead of timing-dependent
  `EPIPE` or `ECONNRESET` reporting.
- Split the exhaustive 1,157,776 two-packet input-window combinations across eight registry entries.
  Coverage is unchanged, but sanitizer sharding can now distribute the finite proof instead of
  trapping one disproportionately long test in a single shard.
- Made PTY helper startup failure deterministic across the independent manifest and status sockets.
  A helper that closes during manifest handoff can no longer race between an I/O error and the
  readiness protocol result; the parent preserves structured setup records and classifies a closed
  wrong helper at the protocol boundary. The optimized process suite passed 100 consecutive runs.
- Removed a scheduler-timing assumption from the concurrent terminal-profile registry regression.
  Every reader now reaches an explicit ready point and the released reader set completes a minimum
  observation before the optimized publisher loop begins, so the test continues to verify coherent
  generations without depending on the operating system scheduling a reader opportunistically.
- Fixed the fuzz-enabled all-target build graph. The instrumented static product archive now exports
  its ASan/UBSan runtime link requirement to ordinary consumers while libFuzzer's main remains private
  to fuzzer targets, so a complete fuzz build no longer leaves product/test executables unresolved.
- Qualified the final owned surface at 269/269 fixture-aware direct checks and 11/11 default CTest
  targets before packaging.
- Kept release claims narrow: rev0019 does not preserve PTYs or controller replay across Agent
  restart, support multiple simultaneous local terminals, establish two-physical-host terminal
  qualification, enable Ratox by default, or claim complete namespace/cgroup/seccomp/LSM isolation.

### Live default-off Ratox Agent dispatcher and bounded PTY coordinator (rev0018)

- Joined the completed Ratox session engine, authority-ledger v2 capability, sealed terminal profile
  registry, and PTY controller into a live Agent service on custom-lossless packet ID `0xA2`. The
  service remains disabled by default; ordinary upgrades continue to omit feature bit 23.
- Added fail-closed pre-network activation. Explicit enablement now requires a normalized secure
  owner-only profile store, at least one enabled profile and principal binding, a valid bounded
  service configuration, and either an injected process factory or an absolute helper path with a
  bounded startup timeout. Any failure stops Agent startup before toxcore begins.
- Made HELLO feature advertisement runtime-selectable and immutable after peer admission. Runtime
  projection now separates local supported/required, peer supported/required, and negotiated feature
  masks so one-sided rollout cannot be mistaken for a usable service.
- Added exact live dispatch gates for transcript confirmation, bilateral Ratox negotiation, current
  online epoch, authenticated stable principal, and exact-head `interactive.terminal` authority. A
  v1 owner can authenticate but receives a retained OPEN denial and cannot trigger profile lookup or
  PTY spawn.
- Added a bounded `RatoxService` coordinator that handles OPEN/ATTACH/RESUME/DETACH, staged whole-
  frame INPUT commitment, ACKs, output replay/gaps, resize, ping, close, exit, duplicate admission
  replay, bounded tombstones, and explicit outbound ownership.
- Added retained transport delivery: successful toxcore enqueue pops exactly one packet; `SENDQ` and
  retryable unavailable outcomes retain the identical packet; stale or nonretryable routes detach the
  exact online epoch instead of silently rerouting bytes.
- Shortened terminal-byte lifetime at both transport crossings. Ratox sends now use a dedicated
  owner-thread command payload whose single heap allocation is securely wiped after success,
  cancellation, queue rejection, or failure instead of being duplicated into ordinary closure
  vectors. Incoming Ratox event storage remains available through metadata journaling and is then
  securely wiped on normal and exceptional dispatch exits.
- Added round-robin PTY servicing under global write/read/frame budgets so a permanently busy low-
  index process cannot starve another live session. Peer disconnect detaches routing while preserving
  resumable process state, exact-head authority loss begins closure, and Agent shutdown drains the PTY
  lifecycle through bounded HUP/TERM/KILL escalation.
- Hardened the route/authority join after adversarial review. Live-session control replay keys now
  include a local domain plus authenticated friend number and online epoch; invalid-route controls
  cancel their reservations instead of consuming replay IDs; and a rejected route can no longer
  retarget a session's later revocation owner. Exact-route proof loss now fences only that route, while
  durable principal revocation remains the separate transition that closes every detached or attached
  session for the principal. Unauthorized absent ATTACH/RESUME probes receive retained `DENIED` rather
  than a session-existence oracle, and queue compaction wipes inactive packet storage. Signed authority-
  head mutation is now serialized with Ratox receive, bounded PTY progress, and transport admission;
  every retained packet records whether it depends on terminal authority, preserves that bit through
  exact replay, and is revalidated before send. Only explicit unauthorized admission denials cross the
  transport without an interactive-terminal grant.
- Added private aggregate status and a bounded `ratox-events` journal containing lifecycle metadata
  only. Terminal input/output, argv, environment, paths, profile identifiers, and error strings are
  deliberately excluded; current and previous journals remain owner-only.
- Added live exact-mock coverage for default-off advertisement, fail-closed activation before
  transport, one-sided negotiation, bilateral feature negotiation, transcript-bound principal proof,
  v1 capability denial, real OPEN dispatch and returned denial, plus no-spawn assertions. Added
  service fairness and runtime privacy/rotation coverage. A dedicated toxcore lane now pins an
  authority-bound OPEN_RESULT behind repeated `SENDQ`, commits a signed revocation, and proves Agent
  purges the retained packet before another transport attempt. The direct C++ registry now contains
  223 checks and the complete nine-target GCC debug CTest suite passes.
- Added a ninth sanitizer-backed stateful fuzzer for the complete `RatoxService` coordinator. It
  mutates authenticated and stale routes, canonical and malformed packets, replay, outbound
  retention, offline/revocation/shutdown transitions, and an injected PTY that can partially write,
  block, close, fail, misreport bounds, emit output, or exit. Snapshot, event, principal, packet,
  sequence, replay, tombstone, and queue invariants are checked after every operation.
- Added a service-level uncertain-input regression: when a PTY accepts only a prefix and the next
  write fails, no INPUT_ACK is emitted, the process is discarded, and the session becomes a bounded
  tombstone with an explicit failure exit result.
- Hardened the final evidence path itself. Retained-artifact qualification now derives the current
  nine-fuzzer topology, requires all named 5,000-unit completions, records the exact 223-check
  registry, and reports source-linked c-toxcore/libsodium/Argon2 success only from a zero-exit build,
  a revision-matched build record, and the standalone verifier's exact pass marker. It no longer
  carries forward a stale DNS-failure claim after a verified cached-source build.
- Removed a sanitizer-sensitive timing dependency from the file-transfer pause/resume state-machine
  regression while preserving a finite scheduler deadline and separate bulk-transfer coverage; the
  exact affected ASan/UBSan shard passed 20 consecutive fresh repetitions.
- Kept release claims narrow: rev0018 has no local streaming terminal client, no daemon-restart PTY
  supervisor, no two-physical-host complete-service qualification, and no namespace/seccomp/cgroup/
  LSM sandbox guarantee. Production-default advertisement remains prohibited.

### Sealed local terminal profiles and Linux PTY boundary

- Added a strict local terminal-profile v1 policy grammar and fail-closed owner-only store. Profiles
  freeze executable, argv, working directory, environment, terminal type, dimensions, identity,
  resource limits, and shutdown timing; bindings map one stable principal to one local profile.
- Added canonical byte encoders/decoders with exact field order, lowercase hexadecimal, bounded
  records, locale-independent decimal rendering, canonical re-encode checks, and a dedicated
  sanitizer-backed fuzzer corpus. Remote data never becomes a path, argument, environment entry,
  identity, or resource limit.
- Added an atomic generation-bound profile registry. Replacement validates the complete candidate
  before swapping it into service, preserves the prior generation on failure, and publishes coherent
  profile/binding snapshots under concurrent resolve, replace, and observation.
- Added a bounded nonblocking terminal controller with immutable resolved policy, resize clamps,
  saturating evidence counters, output draining, observe-before-signal close, fresh HUP/TERM/KILL
  grace windows, idempotent exit observation, and an explicit unreaped-SIGKILL timeout.
- Added a Linux UNIX98 PTY backend using the installed IoTox binary as one hidden reviewed child
  entrance. The parent passes canonical configuration plus already-open target/cwd descriptors; the
  child verifies fixed descriptor types, peer credentials, one exact parent PID, and readiness plus
  close-on-exec EOF before the parent treats startup as successful.
- Hardened child execution with a new session and controlling terminal, foreground process group,
  exact window size, complete catchable-signal reset, core-dump disablement, configured soft resource
  limits, supplementary-group clearing for exact identity, verified real/effective/saved IDs,
  set-and-read-back `PR_SET_NO_NEW_PRIVS`, verified ambient-capability clearing, parent-death
  re-arming after credential changes, umask 077, descriptor closure, and descriptor-based `fexecve`.
- Added real PTY process tests for canonical cwd/environment/window state, descriptor hygiene,
  no-new-privileges, inherited-signal reset, inherited ambient-capability removal, parent-death
  behavior, exact UID/GID drop when privileged, destructor-free controller loss against an
  HUP/TERM-ignoring target, direct backend bounds,
  byte-exact binary echo, resize clamping, HUP/TERM/KILL escalation, setup-stage errors, insecure
  executable rejection, and reap. The direct owned registry now contains 189 checks.
- Kept the security claim narrow: Ratox feature bit 23 remains unset; no Agent dispatch, local
  terminal client, remote OPEN handler, restart survival, namespace sandbox, or network terminal
  service is implemented or advertised.

### Authority-ledger v2 and explicit terminal capability

- Added a signed, replayed authority-ledger v1-to-v2 migration. The transition uses an independent
  `IAL2` record format, `IOTOXAL2` file header, v2 signature/digest domains, and one self-signed
  `migrate-v2` action that must extend the exact active v1 owner and tail.
- Preserved every v1 capability meaning. `kAllCapabilities`, CLI `all`, `all-v1`, and `legacy-all`
  remain bits 0–6; only explicit `all-v2`, `all-with-terminal`, or a named capability list may include
  durable bit 7 `interactive.terminal`.
- Made migration non-widening: the active owner remains exactly `0x7f`, every other principal keeps
  its exact prior mask, and terminal authority appears only in a later, separate signed v2 grant.
  Owner succession and epoch transition preserve the nominated successor's exact capabilities.
- Added mixed-history replay with a single valid v1-to-v2 boundary, strict header/history agreement,
  rejection of v1 records after migration, unknown-bit and role-ceiling checks, independent proof
  domains, sequence/epoch exhaustion handling, restart recovery, and explicit local-guard versus
  coordinated-snapshot rollback boundaries.
- Added negotiated capability-session feature bit 24 `authorization-ledger-v2`. V2 challenges and
  proofs carry the ledger format explicitly, bind it into the transcript-confirmed session, reject
  downgrade to v1 within a continuing authority round, and require the negotiated v2 feature for
  local proof construction and remote migration.
- Added local and remote RecallRoot migration ceremonies, control operation 64, local protocol minor
  22, runtime format/negotiation projections, exact-head remote preparation/application, proof
  invalidation after mutation, and content-addressed duplicate acknowledgement without a second
  append.
- Added a private 192-byte `IOTOXAG2` rollback guard beside the signed ledger. Each append publishes
  committed and pending exact heads before the atomic ledger replace, then promotes the pending head.
  Startup and live append recover only the two exact interrupted states and reject every third head as
  ledger-only rollback, deletion, or fork. Existing unguarded v1 ledgers are adopted; persisted v2
  ledgers without their guard fail closed. Coordinated rollback of both files remains outside this
  local witness and requires hardware, replication, or an owner-observed checkpoint.
- Made RecallRoot signing verify the daemon-prepared unsigned record semantically before any signature
  is produced or transmitted. Action, role, capability set, issuer, subject, zero time fields, and v2
  migration format must exactly equal the requested ceremony, preventing prepared-body substitution.
- Replaced the Agent custom-packet probe burst's scheduling-sensitive fixed wait with an exact
  successful-send/reply completion predicate. Repeated lifecycle stress now exercises the repaired
  asynchronous boundary instead of accepting or manufacturing partial timing evidence.
- Removed a process-fixture `SIGPIPE` race by preloading each bounded RecallRoot phrase into its
  empty stdin pipe before `posix_spawn` or `fork`. Commands that reject arguments before reading
  stdin can now be asserted by exit status and output instead of intermittently terminating the
  test harness; both process fixtures enforce the atomic `PIPE_BUF` ceiling.
- Added deterministic coverage for canonical v2 bytes, signature-domain separation, exact migration,
  explicit owner/operator terminal grants, role ceilings, stale and downgraded histories, v1/v2
  challenge/proof negotiation, remote denial/application/retry, ownership transition, restart, and
  one-binary CLI signing ceremonies. After the rev0017 additions, the direct C++ registry contains
  189 checks.
- At the rev0016 authority gate, Ratox feature bit 23 remained unadvertised and no PTY, child process,
  remote-selected profile, terminal stream, or Agent dispatcher existed. rev0017 completes that R3
  prerequisite locally without changing the network activation state.

### Ratox interactive foundation and carrier science

- Completed the transport-independent R1 session engine without exposing a service. Added exact
  fail-closed control-result replay with pre-effect storage reservations, atomic ATTACH/RESUME
  output-position application, one-writer generation fencing, terminal incarnation replacement,
  post-close exact replay without fresh terminal effects, configured sequence-origin propagation,
  bounded nonce/event retention, content-free lifecycle evidence, and atomic two-per-principal /
  eight-per-device quotas.
- Removed the replay cache's post-effect convenience insertion path. Every fresh control now uses
  an explicit reserve/commit-or-cancel transaction; exact duplicates replay before validating an
  irrelevant new capacity, and commit releases unused preallocated result budget while retaining
  exact request-plus-result accounting.
- Added content-free attachment-denial facts and stale-input-token evidence, exposed both principal
  and device quota invariants in directory snapshots, and extended the state fuzzer through live
  directory open/close/erase sequences rather than claiming quota coverage from unit tests alone.
- Added exact duplicate/in-progress/conflict/cache-full tests, controller-fencing and close-wipe
  lifecycle tests, generation/incarnation/nonce/quota failure atomicity, every valid two-packet v1
  input split through 2,152 bytes, exact 64 KiB/1 MiB boundaries, and complete-session state fuzzing
  under Clang AddressSanitizer and UndefinedBehaviorSanitizer. Feature bit 23 remains unset and no
  PTY, process, authority migration, Agent dispatch, or network advertisement was added.
- Kept strict GCC release builds warning-clean by constructing the fixed Ratox header in fixed
  storage before bounded vector publication and by avoiding a libstdc++ iterator false positive in
  the TCP-only audit test; canonical frame bytes and test semantics are unchanged.
- Made the seven-target fuzz launcher validate and decode its reviewed hexadecimal Ratox seed with
  `xxd`, Python 3, or Perl, removing a nonessential single-tool portability failure without
  weakening malformed-seed rejection.
- Refreshed the active roadmap/security dates for the completed R1 byte-state slice, taught future
  conversation datacubes to retain milestone-qualified matrix/fuzzer logs, and updated retained
  artifact qualification from five legacy fuzzers to all seven current parser/state targets.
- Implemented the first R1 service primitives without exposing a service: whole-frame staged input
  commitment with duplicate/overlap/gap classification and terminal partial-write failure, plus
  independently sequenced bounded output history with ACK release and explicit eviction gaps.
  Added exhaustive frame/partial-write boundary tests and a seventh stateful sanitizer fuzzer.
- Split the post-framing Ratox work into eight dependency-ordered service phases, with exact
  receiver, output-history, authority migration, PTY/profile, agent, local-client, reconnect,
  physical-host, and activation gates. Added a focused threat model and made feature advertisement
  the final reviewed action rather than an incidental consequence of partial implementation.

- Swept 64-packet custom-carrier bursts at 2/5/10/20/40 ms with 64-byte and full 1,200-byte
  packets under adverse direct UDP and forced TCP beside exact bulk transfers. Added deterministic
  sized probe padding, an atomic pacing-matrix harness, and retained admission/path evidence.
- Added a transport-independent admission pacer that coalesces at a 20 ms base, retains an offered
  packet across SENDQ rejection, exponentially backs off to 320 ms, and cautiously recovers after
  accepted sends without silently advancing input.
- Froze Ratox framing 1.0 on unadvertised custom-lossless ID `0xA2`: a canonical 124-byte header,
  1,200-byte packet ceiling, complete attachment identity, cumulative byte positions, 17 strict
  frame types, explicit output gaps, an unadvertised negotiation bit, a reserved terminal-authority
  bit, exact parser tests, and a sixth fuzz lane. No PTY or shell service is advertised.
- Added a safe two-network-namespace netem laboratory that crosses observed direct UDP and forced
  TCP relay through baseline, delay/jitter, loss/duplicate/reorder, and rate/queue-pressure profiles
  without attaching a qdisc to any host or physical interface. It retains deterministic seeds,
  qdisc counters, report hashes, and exact cleanup evidence.
- Added randomized single-carrier order and a bounded 64-probe research burst that records every
  ordinal, RTT/miss, arrival rank, duplicate count, and local send error. This separates toxcore
  admission collapse from post-admission path deadlines instead of discarding partial evidence.
- Retained the corrected 2x4 matrix. Direct UDP showed lossless ordering with queue/admission tails
  versus faster but missing/reordered lossy survivors; forced TCP made both carriers ordered and
  collapsed admission under adverse bulk. ADR 0060 now requires pacing, keeps indispensable
  control/input lossless, and reserves lossy only for sequenced replaceable state with resync.

- Added starvation-safe interactive/control/bulk admission above the single c-toxcore owner,
  bounded each visit before `tox_iterate`, capped provider-requested idle sleep at a configurable
  20 ms, and exposed per-class queue waits plus requested/effective iteration evidence.
- Added transport-independent attachment-generation fencing, bounded cumulative byte replay with
  explicit backpressure/history gaps, and an overflow-safe monotonic RTT/RTO estimator. These are
  prerequisites only; no terminal or remote-shell feature is advertised.
- Consumed the official custom-lossy c-toxcore send/callback ABI alongside custom lossless, with
  exact mock coverage and reserved-range rejection. Added fixed, unadvertised, confirmed-session
  10-byte carrier probes that are nonce-correlated, size-symmetric, and carry no user data.
- Extended the genuine four-route fixture with interleaved normal-text receipt, custom-lossless,
  and custom-lossy RTT samples while idle and beside bulk, in observed direct-UDP and forced-TCP
  modes. The corrected 40-sample gate selected custom lossless for Ratox-first work: it tied lossy
  on direct UDP without lossy semantics and had materially fewer forced-TCP deadline misses.
- Added the ordered Ratox/reconnect plan, ADR 0059, exact experiment report and artifact hashes,
  CLI research probes, a repeatable UDP/TCP latency wrapper, and explicit controlled-impairment,
  PTY, reconnect, two-host, and stream-coexistence gates.

### Four-route Tox file science

- Extended the genuine-provider laboratory through 8, 16, 32, and 64 simultaneous files, comparing
  one route with four evenly loaded routes under explicitly observed direct UDP and forced native
  TCP. All 48 retained 16 MiB phases completed byte-identically with zero dropped events.
- Removed quadratic live-transfer projection work by caching exact unchanged global and per-peer
  records while retaining atomic changed records and immediate terminal withdrawal. A one-route,
  64-stream 1 MiB shakedown fell from 71.018 to 6.184 seconds and from 9,719 to 549 CPU ticks.
- Measured a stable four-route data-window gain throughout the sweep: 1.49–1.59x over UDP and
  1.47–1.56x over TCP. Extra streams did not increase one connection's aggregate carrier rate;
  route distribution, not tiny-stripe count, is the useful scaling lever on this host.
- Added direct fail-closed tests for every resource ceiling used by the 64-stream laboratory,
  broader network-route and state-store failure coverage, and an explicit matching-gcov override
  for split Nix toolchains. The maintained-product coverage gate remains enforced and passes at
  70.0% lines without lowering its floor or excluding source.
- Added a bare-metal 1x/2x/4x genuine-provider laboratory with eight distinct Tox identities bound
  to two stable test device identities, immutable reusable baselines by default, fresh-key mode,
  constant-byte rotated topology trials, exact payload comparison, per-process and host deltas, and
  redacted retained reports.
- Fixed the first experiment's 74,034-byte `SENDQ` failure by installing a transfer-scoped file
  source atomically with `tox_file_send` and answering each c-toxcore request synchronously inside
  its callback. Exact error typing, source cleanup, immediate failure cancellation, inline-event
  evidence, and a strict mock regression prevent the receiver-stranding defect from returning.
- Coalesced only healthy nonterminal progress journals and atomic runtime projections to 250 ms
  while retaining every required event, exact manager state, immediate failures/terminals, event
  counts, and on-demand exact `files` projection. This removed the shared local instrumentation
  ceiling exposed by the first run.
- Retained three rotated 8 MiB trials: one route/four streams was 0.97x the single-stream control,
  two independent routes were 1.33x, and four independent routes were 1.62x with zero dropped
  events and exact destinations. Bonding remains research pending authenticated route membership,
  immutable stripe manifests, failure/restart behavior, and two-host/relay qualification.
- Added a pre-network expected-public-key fence to the Tox transport and bound configured primary
  savedata to the signed route set's coordinator key. A valid inventory can no longer start a
  cross-wired or substituted Tox identity.
- Allocated message type 19 and implemented the exact 224-byte route-binding-v1 attestation. The
  stable device signs the route member, policy, generation, and locally derived confirmed-session
  transcript digest; stale, foreign, modified, and replayed bindings fail closed. Feature bit 21
  remains unadvertised until the live worker exchange is complete.
- Added explicit in-process auxiliary worker activation with strict private key-named savedata,
  exact pre-network identity checks, independent toxcore owner threads, signed connection-class
  enforcement, random worker incarnations, one-peer ambiguity refusal, and canonical application
  handshake progression. Constructed members stop at `connecting`; no work is admitted before the
  route-binding exchange.
- Add direct supervisor startup and cross-wired-savedata checks plus an Agent-level control-surface
  check proving a real auxiliary owner receives a nonzero worker incarnation and enters only
  `connecting`.
- Froze the route-binding-v1 exchange as one canonical message-type-19 frame carrying the complete
  signed route set plus its transcript binding. Verification requires a locally expected remote
  stable principal and minimum generation, rejects noncanonical envelopes and self-anchored foreign
  sets, and remains below the existing payload ceiling. Feature bit 21 stays unadvertised pending
  replay-safe supervisor integration.
- Added a bounded coordinator-owned route-binding registry. Authority-authenticated primary trust
  now binds the expected remote stable principal to its exact coordinator Tox key and online epoch;
  accepted remote inventories retain generation and same-generation-fork state, while worker and
  message replay is exact-epoch idempotent and explicit-retirement fenced. Live worker dispatch
  remains unadvertised.
- Added the construction-gated auxiliary binding exchange. A worker advertises bit 21 only with a
  restricted parent signing callback and verifier, freezes one outbound proof after confirmation,
  retains one reciprocal proof while primary trust catches up, and latches invalid verification
  until trust changes. Ordinary and single-route Agent sessions remain unadvertised.
- Completed Agent-side authenticated route readiness. Explicit workers receive the restricted local
  signer, primary authority sessions populate exact principal/coordinator/epoch trust, and only a
  sent local binding plus verified reciprocal binding advances `connecting` through `authenticated`
  to `ready`. Authentication loss closes readiness and work without spending restart budget; the
  deterministic provider now proves the full transition.

### Reusable genuine test identities

- Made the genuine source-linked peer harness reuse a private, provider-versioned pair of test-only
  Tox savedata and stable device identities by default. Each run copies those immutable baselines
  into fresh authority, command, runtime, friendship, and transfer state.
- Added atomic first-use provisioning, exact key-only cache layout checks, owner/mode/symlink
  hardening, distinct-peer checks, whole-run locking, clean-friendship admission, and an end-of-run
  digest assertion that the cache was not changed.
- Added `--prepare-keys`, explicit `--reuse-keys`/`--fresh-keys` modes, environment overrides, and
  report fields that distinguish reused-baseline from fresh-generated evidence. Fresh identity
  generation remains a release/network qualification gate; focused creation/tamper tests remain
  isolated.

### M5 durable offline lifecycle

- Replaced the signed `IOTXCMD2` write format with `IOTXCMD3`: request, receipt, and result now own
  independent persisted attempts, typed errors, last-attempt times, and next-attempt times. Correctly
  signed private v2 stores are strictly decoded and atomically migrated before transport starts.
- Added key-bound offline command admission for existing Tox friendships. New work freezes current
  protocol bytes, waits through a one-second cancellation window, and retries the exact request with
  exponential one-second-to-five-minute backoff plus stable 0–25% jitter until application receipt
  or terminal result. Steady-clock scheduling and a signed restart anchor prevent untrusted wall
  jumps or restarts from accelerating retry state.
- Added safe `command-cancel` semantics: only an outgoing `reserved` record with zero committed
  attempts may be cancelled. Post-attempt cancellation is refused because delivery may be
  peer-visible after a crash or ambiguous provider return.
- Added immutable high/normal/low priority; default unfinished quotas of 256 total records, 32 per
  peer/direction, and 256 KiB canonical bytes per peer/direction; fully-delivered-terminal-only
  pruning; open-time quota revalidation; and authoritative-memory preservation when persistence or
  configured file bounds fail.
- Added optional TTL admission guarded by `--trust-wall-clock` and a signed-history rollback check.
  Uncertain clocks hold existing expiring work, refuse new TTLs, and continue non-expiring work.
  Trusted expiry distinguishes unattempted `expired` from attempted `timed-out-unconfirmed` without
  inventing a remote result; a retained uncertain timeout can still resolve from one exact late
  peer result.
- Closed command admission before local ingress shutdown and blocked new delivery attempts after
  the event-stop gate. FIFO writes remain ingress records, never a second durable queue.
- Kept scheduling and rollback checks bounded at store scale by reading the signed clock high-water
  scalar under the store lock instead of copying the complete, potentially 8 MiB snapshot for each
  record serviced.
- Extended command/store/runtime projections with priority, clock requirement, expiry, three lane
  schedules, clock high-water state, due-artifact counts, and held-expiring counts. Added CLI
  priority/TTL arguments and exact durable-key cancellation.
- Expanded the direct owned C++ registry from 131 to 137 checks with schedule determinism,
  cancellation boundary, quotas, bounded persistence failure, signed clock checkpointing, and
  successful plus size-refused signed v2 migration with original-file preservation. Runtime
  rollback detection is also anchored to monotonic elapsed time.
  Extended the one-binary fixture through delayed admission, untrusted-TTL refusal, online cancellation, a
  restored but deliberately offline friendship, zero-attempt persistence beyond the delay, and
  safe offline cancellation.

### Repository conversation datacube

- Added `tools/make-repository-datacube.sh` to produce a clean-commit, one-root ZIP for discussion
  and recovery. The cube carries the ordinary source tree, a full Git bundle, available standalone
  distribution and raw validation evidence, and budget-admitted founding cubes.
- Enforced a strict default ceiling below decimal 128 MB, payload and outer checksums, extraction and
  bundle verification, clean-worktree packaging, sensitive-path/private-key guards, safe archive
  paths, refusal of archive symlinks, and no-padding size utilization.
- Added an embedded ChatGPT entrance that records the exact commit, current roadmap headings, recent
  history, evidence boundaries, and a suggested opening prompt without transferring authority away
  from the owning IoTox repository.


## rev0015 — Ordinary Request

### Exact ratox-style outgoing invitation

- Added the private root `request` FIFO and `request.help`, completing the ordinary friendship loop.
  One record is exactly 76 hexadecimal complete-Tox-address characters, one literal TAB, a
  1..921-byte request message, and LF framing. Upper/lower address hex is accepted; all non-LF
  message bytes are preserved. No whitespace search, shell quoting, trimming, Unicode normalization,
  or hidden default message is applied.
- Kept the complete 38-byte address intact through `tox_friend_add`: 32-byte public key, 4-byte
  nospam, and 2-byte checksum. IoTox decodes exact hex; pinned c-toxcore remains authoritative for
  checksum, own-key, duplicate/already-sent, changed-nospam, and provider errors.
- Unified the root FIFO and existing structured `transport-peer-request` operation on one Agent
  method, one friendship lifecycle mutex, and one serialized toxcore owner-thread call. The ordinary
  façade creates no second friendship state machine or retry policy.
- Made evidence deliberately narrow. `request-send disposition=requested` means local
  `tox_friend_add` state was accepted. It does not prove remote receipt, remote acceptance, online
  state, IoTox session confirmation, or authority.

### Generalized hardened root-lane service

- Extended `PeerFifoServer` with explicit `public_key_directories` and `root_lanes` layouts while
  retaining one framing/path-hardening implementation. Unknown layout values fail closed.
- Applied owner, mode, type, no-follow, opened-inode, actual `_PC_PIPE_BUF`, bounded-buffer, partial
  timeout, rescan, and safe replacement rules to the root lane. The 999-byte maximum including LF
  must fit atomically.
- Distinguished dynamic per-peer lanes from promised process-wide entrances. Startup now fails when
  a configured root FIFO is absent/invalid, and live readiness drops if `request` is no longer
  monitored instead of leaving status falsely green.
- Added an exact `FriendRequestFifoRecord` decoder with finite compile-time bounds and no C-string
  discovery.

### Honest identity and lifecycle integration

- Added explicit keyless friendship lifecycle events. A malformed root record with no trustworthy
  public-key prefix is journaled as `public-key=unknown`; IoTox never fabricates an all-zero peer to
  satisfy an event shape. A valid 64-hex prefix may be retained only as a diagnostic hint when the
  remaining record is malformed.
- Reconciled successful outgoing admission into the canonical uppercase public-key peer projection,
  then exercised exact key-bound removal through the existing `remove` FIFO. Friendship continues to
  leave the independent signed authorization ledger unchanged.
- Added `request-send-fifo-count` and integrated the root service into Agent start, stop, failure
  unwind, status, and separate-process lifecycle.

### Tests, construction defects, research, and governance

- Added `tests/test_friend_request_fifo.cpp` for exact bytes, lower/upper hex, min/max records,
  separator/hex/size failures, binary message preservation, root-lane startup, replacement,
  `PIPE_BUF`, inode/path hardening, partial expiry, stats, and invalid layout.
- Extended Agent/runtime tests and the actual one-binary process fixture through malformed and valid
  root writes, explicit keyless evidence, local provider admission, resulting peer projection, and
  exact public-key removal. Extended `tools/run-mock-node.sh` through the same literal path.
- Increased the direct owned C++ registry from 113 to 121 checks; the preserved Mutorr-enabled
  registry contains 134.
- Found that a process-global one-shot mock send failure could be consumed by the newly created peer
  before the intended session. The fixture now removes the temporary request peer before deliberate
  fault injection; future fault plans are required to become peer/operation-bound.
- Recovered an ephemeral unfinished worktree from the immutable rev0014 cube, replayed the validated
  changes, and reran the owned tests. Unreleased workspace state is not handoff evidence.
- A clean GCC Release lane proved that the lossless-send path could call `vector::front()` without an
  explicit non-empty precondition. Debug tests happened to supply non-empty packets, but warnings-as-errors
  correctly rejected the source. The branch now guards the access, records the invariant in code, and requires
  a fresh clean full-matrix rerun rather than blessing the earlier partial transcript.
- The first foreground 100-run stress invocation exceeded its external wrapper limit. The stress tool's
  private staging and atomic publication worked as designed: no partial green transcript or zero exit evidence
  escaped. A detached run reacquired the exclusive lock and published one self-validated 100/100 transcript.
- Retained-artifact regeneration exposed a stale prose boundary: binaries and reports were rev0015,
  while `artifacts/README.md` still named rev0014. The refresh tool now renders that README from current
  revision/version codename and registered-check metadata before checksums are frozen.
- Added ADR 0049, a pinned c-toxcore/ratox/FIFO source review, a rev0015 historical entrance, and
  rewrote the active architecture, lifecycle, protocol, threat, testing, roadmap, assessment, and
  wake-from-amnesia prose around the exact ordinary request contract.


## rev0014 — Ordinary Friendship

### Ratox-style transport-friend lifecycle

- Added private mode-`0600` `accept` and `reject` FIFOs to every live incoming-request directory and
  a private mode-`0600` `remove` FIFO to every established public-key peer directory. Each lane
  accepts one exact lowercase token plus LF in one atomic write.
- Added root `friendship.help` and a bounded rotating `friend-events` journal. FIFO write success
  remains kernel evidence only; the journal records request arrival, local decision admission,
  provider result, observed add/remove callbacks, and the unchanged authorization boundary.
- Kept incoming requests as transient IoTox callback projections. Accept requires the same public
  key to remain pending and calls `tox_friend_add_norequest`; reject only withdraws the IoTox record
  because c-toxcore has no persistent pending-request object or remote rejection operation.
- Kept outgoing request send on the typed one-binary control path using a complete 38-byte Tox
  address and bounded request message. No root request FIFO was added merely to invent an ambiguous
  address/message delimiter; the one-binary operation is the ordinary outgoing entrance for v1.
- Kept friendship transport-only. Accept, reject, outgoing request, and removal neither grant nor
  revoke stable IoTox principals, roles, capabilities, ownership, firmware authority, or effects.

### Public-key-bound destructive mutation

- Added the exact consumed `tox_friend_by_public_key` ABI to runtime-loaded, official-header-linked,
  and mock providers.
- Added `ToxTransport::remove_friend_by_public_key`. Lookup and `tox_friend_delete` execute in one
  queued operation on the exclusive toxcore owner thread, so a delayed delete cannot target a later
  peer that inherited a reused numeric friend-number gap.
- Advanced the local control protocol minor version from 14 to 15 and froze operation 30 as
  `transport-peer-remove-key`. The public CLI resolves a numeric compatibility selector to its
  current public key before requesting the key-bound operation.
- Captured the deleted public key before provider mutation and retained the numeric friend number
  only as lifecycle evidence. Peer cleanup, runtime withdrawal, and diagnostics therefore remain
  bound to the intended key.
- Extended the exact mock to implement public-key lookup and deliberate lowest-gap friend-number
  reuse. Regression tests remove friend zero, create a different peer in the reused slot, remove the
  replacement by key, and reject a duplicate removal.

### Construction, evidence, and governance

- Extended the generalized FIFO service with a second request-tree instance while retaining one
  product executable and one typed Agent implementation. FIFO workers still own framing/path
  hardening only and never call toxcore or mutate the authorization ledger directly.
- Added Agent integration tests that literally accept a request, remove the resulting peer, and
  reject another request through the new FIFOs. Added private projection, exact-token, journal
  rotation, protocol-code, owner-thread deletion, and numeric-gap reuse checks.
- Extended the separate-process one-binary fixture through outgoing request evidence, incoming
  accept/reject, a malformed uppercase removal that must not mutate, and an exact public-key removal
  after restart, while preserving the full session/authority/command/file path.
- Increased the direct C++ registry from 110 to 113 checks before final matrix retention.
- A clean rebuild exposed stale retained-object trust: an old process fixture still expected
  revision 13 while current source emitted revision 14. Final evidence now requires clean build
  directories; the process and mock-node fixtures assert the current compiled description.
- Corrected two timing-sensitive tests without weakening product semantics: one request assertion
  now owns a fresh deadline, and bounded journal follow requires the prior snapshot as a prefix
  because required lifecycle evidence may append concurrently.
- Repeated the complete one-binary fixture under scheduling variation and exposed two fixture-only
  false atomicity assumptions. A successful `reject` FIFO write could precede request-directory
  withdrawal, and peer-directory withdrawal could precede the adjacent best-effort `friend-events`
  append. The fixture now polls each semantic projection independently, requires the node to remain
  alive, and treats the journal as separate later evidence instead of treating `write(2)` success or
  one filesystem change as completion. Product ordering was not weakened. The clean rebuilt fixture
  then passed ten sequential fresh-runtime lifecycle repetitions.
- Added an exclusive lock to the repeated Agent/session stress harness after overlapping invocations
  were shown to interleave one evidence file. Concurrent stress attempts now fail closed with status
  75 instead of manufacturing an invalid run count.
- Hardened retained stress validation to require every ordered run number 001–100 exactly once and
  exactly one canonical terminal summary; a count-only or duplicated-summary log now fails closed.
- After a legacy overlapping writer truncated an otherwise successful transcript at run 67, changed
  the producer to stage privately, self-validate order/count/final summary, and atomically publish;
  exit zero can no longer bless a destination log that was externally damaged during the run.
- Replaced the direct `recall-generate` CTest invocation with an in-process CMake verifier that
  validates one exact eight-word LF-terminated record while emitting only `phrase suppressed`; a
  generated sovereign phrase no longer appears in ordinary CTest output or retained test logs.
- Completed semantic handlers that an interrupted inherited draft had projected but not finished,
  removed a duplicate command dispatch, and consolidated duplicate draft ADR/contract/research
  files into one governing artifact of each kind.
- Added ADR 0048, the friendship lifecycle v1 contract, and a pinned review of c-toxcore 0.2.23 and
  ratox request/remove semantics. The review records that c-toxcore deletion is local and silent,
  rejection is client-side ignore, and friend numbers are not durable identity.
- Reworked the lone BOOTSTRAPROSE entrance, architecture, roadmap, threat model, testing doctrine,
  and product assessment around the executable friendship surface, the next ordinary outgoing
  request entrance, and the following useful harmless machine read.
- Preserved the evidence boundary: the owned lifecycle is compiled and process-tested against the
  exact consumed ABI. Official source-linked c-toxcore, genuine bootstrap/NAT/relay behavior,
  Tox/Tor, and Tox/I2P remain external or reserved gates.


## rev0013 — Ordinary Cargo

### Ratox-style finite-file surface

- Added private per-peer mode-`0600` `file-send`, `file-receive`, and `file-control` FIFOs plus
  `file.help`, bounded `file-events`, and atomic `files/incoming` and `files/outgoing` projections.
- Preserved ratox's ordinary one-write operation while changing the FIFO contract from bulk stream
  bytes to one finite local path record. The same `FileTransferManager` serves structured CLI and
  FIFO callers; no second transfer engine or executable exists.
- Froze exact grammars: absolute source path; decimal file number plus TAB plus absolute destination;
  and decimal file number plus TAB plus `pause|resume|cancel`. The FIFOs perform no shell parsing,
  globbing, remote path selection, or overwrite-by-default.
- Kept evidence boundaries explicit: FIFO write success is kernel acceptance, `file-events` is local
  semantic/callback evidence, live transfer directories are disposable projections, and atomic
  destination appearance is receive-completion truth.
- Retained finite-file protections already present in the manager: no-follow regular-file source,
  exact positional chunk service, mutation detection, bounded size/chunk policy, private
  same-directory receive staging, exact-size validation, file and directory synchronization, and
  no-clobber publication.

### Complete two-sided file control

- Completed the previously reserved generic local control path through the one-binary control
  protocol and Agent dispatch. `iotox file-control FRIEND FILE pause|resume|cancel` now reaches
  c-toxcore; `file-cancel` remains a compatibility alias.
- Advanced the local control protocol minor version from 13 to 14 and froze operation 36 as generic
  file control without repurposing the older operation 34 cancellation form.
- Added independent `local_paused` and `peer_paused` facts. Effective transfer state is active only
  when neither side is paused; local RESUME cannot erase a peer-owned pause.
- Required pending incoming offers to enter through `file-receive` before RESUME so destination
  policy and resources exist. Repeated local PAUSE is idempotent; RESUME without a local pause is
  rejected; CANCEL releases local resources even when the provider can no longer send control.
- Preserved the complete c-toxcore file number as an opaque provider handle. The pinned
  implementation currently encodes incoming handles at values of at least 65536, but IoTox does not
  depend on that publically unspecified pattern.

### Process evidence, research, and governance

- Extended the separate-process one-binary fixture through malformed path rejection, finite source
  send, incoming paused offer, unsafe pre-destination RESUME rejection, destination admission,
  exact-byte publication, structured pause, journal inspection, and terminal projection convergence.
- Expanded the direct C++ registry from 106 to 110 checks with local/peer pause ownership,
  idempotent pause, invalid resume, cancel/reuse, control-protocol, private runtime-surface, and
  file-journal assertions.
- Added `tools/agent-session-stress.sh`. It requires a complete passing linked registry, discovers
  the principal Agent test's current shard index instead of freezing translation-unit order, runs
  the shard in fresh processes, and emits bounded pass plus exit evidence for strict retention.
- Corrected the `file-control` FIFO lane from printable ASCII to byte-line policy after strict testing
  showed that the required literal TAB delimiter was rejected before the semantic parser. The exact
  parser now admits TAB only as grammar and continues to reject malformed records.
- Corrected a test-only provider assumption: local `tox_file_control(RESUME)` does not invoke the
  remote `file_recv_control` callback on the same client. The callback remains peer-originated
  evidence.
- Added ADRs 0046–0047, a complete finite-file FIFO v1 contract, and a pinned source review of
  c-toxcore file-number, chunk, pause, completion, disconnect, and ratox stream semantics.
- Rewrote the lone BOOTSTRAPROSE entrance around the now-executable file surface and moved immediate
  product work to ordinary friend lifecycle, additional harmless reads, and the first official
  source-linked real-peer run.
- Preserved the evidence boundary: final-source behavior is exercised against the exact consumed ABI
  provider and local filesystem/process fixtures. Official c-toxcore, public bootstrap/relay/NAT,
  real client interoperability, Tox/Tor, and Tox/I2P remain unclaimed.


## rev0012 — Living Text

### Ordinary ratox-style human communication

- Added private mode-`0600` `message` and `action` FIFOs for every projected Tox peer, alongside
  exact `message.help`, bounded `message-events` ingress evidence, and the existing `messages`
  transport lifecycle journal.
- Reused the one C++ text-send path and one serialized toxcore owner thread for structured CLI and
  literal FIFO writes; no second daemon, transport client, or chat protocol was introduced.
- Kept three local write meanings explicit: `message` is live normal Tox text, `action` is live Tox
  action text, and `command` is signed durable machine intent.
- Preserved every non-LF body byte at the local adapter boundary, including NUL, CR, and high bytes.
  Current c-toxcore copies the bounded span without UTF-8 validation, while the Tox protocol defines
  interoperable human text as UTF-8; arbitrary machine bytes remain custom-packet or file data.
- Bounded human bodies to c-toxcore's 1372-byte limit and required one complete body-plus-LF write
  no larger than the FIFO's queried `_PC_PIPE_BUF`.
- Made evidence strength visible: kernel FIFO acceptance, IoTox ingress acceptance, toxcore-assigned
  outgoing id, incoming text, and remote read receipt are separate observations.
- Added no hidden offline spool, reconnect retry, application acknowledgement, or machine authority
  to live text.

### Typed c-toxcore text semantics

- Added exact consumed `Tox_Err_Friend_Send_Message` ABI constants and stable status mapping:
  absent friend to `not_found`, disconnected friend to `unavailable`, full local send queue to
  `resource_exhausted`, malformed/empty/oversized body to `invalid_argument`, and unknown values to
  `library_error`.
- Represented successful message id zero with an explicit presence flag instead of using zero as an
  unassigned sentinel.
- Extended the exact c-toxcore mock with deterministic one-shot disconnected and text-`SENDQ`
  failures and proved that failed sends do not consume the first valid message id zero.
- Mirrored c-toxcore's receipt lifetime: friend disconnect now clears all pending local
  message-kind correlations for that friend and emits the abandoned count. Added a deterministic
  disconnect-before-receipt regression so stale receipt metadata cannot survive reconnect.
- Added `peer-message-events` and `peer-message-events-watch` inspection while retaining
  `peer-messages`/`peer-watch` for the transport journal.

### Generalized and hardened peer FIFO service

- Replaced the command-specific FIFO monitor with a configurable multi-lane `PeerFifoServer` used by
  `command`, `message`, and `action` while keeping lane framing and policy separate.
- Retained nonblocking Linux `eventfd`/`poll` service, bounded rescans, partial-record expiry,
  `lstat`/`O_NOFOLLOW`/`fstat` path verification, same-owner/mode checks, device/inode equality, and
  fail-closed replacement handling.
- Added actual `_PC_PIPE_BUF` discovery and refused a lane when its configured maximum record cannot
  be emitted atomically.
- Added per-lane runtime counts and status fields for command and human-text FIFO availability,
  accepted records, and rejected records.
- Split peer-directory scan errors from lane errors and cleared stale fingerprints when a missing or
  repaired path changes state.

### Tests, defects, and governance

- Expanded the direct C++ registry from 98 to 106 checks, including independent lane framing,
  binary preservation, invalid-record recovery, pre-start statistics, late peer discovery, path
  substitution, actual `PIPE_BUF` refusal, typed text failures, and message-id-zero behavior.
- Extended the separate-process fixture and mock-node lifecycle through a structured binary action,
  a literal binary `message` FIFO write, outgoing/incoming/read-receipt evidence, durable command
  admission, retry, terminal result, stop, and restart.
- Repeated process starts exposed an out-of-bounds pre-start statistics read because per-lane counter
  storage was created only in `start()`. Allocated the immutable lane-stat shape in the constructor,
  reset values at start, bounds-checked lookup, and added a pre-start regression test.
- Packaging verification exposed a second boundary defect: agents with no savedata path could derive
  identity, authority-ledger, and command-store paths from the caller's current directory, so an
  offline retained test could dirty the datacube root. `Agent::start()` now refuses an empty savedata
  path before side effects, dependent default-path helpers preserve emptiness, transient tests choose
  explicit temporary state, retained direct runs use a disposable working directory, and a 105th
  regression plus root-clean assertions preserve the lone-entrance invariant.
- Corrected the compiled semantic-version minor field after the process test detected a stale
  numeric `0.11.0` component beneath rev0012 strings.
- Repeated the canonical session fixture under scheduling pressure and found a semantic race: a
  copied friend-list snapshot could report offline, then be applied after a newer online callback,
  manufacturing a false second epoch and erasing the first HELLO retry evidence. Friend inventory
  refresh now reconciles existence and presentation only; required ordered connection callbacks
  alone open/close epochs, the collect/apply path is serialized, and unit/process assertions require
  `online-epoch=1` with the injected first-HELLO `SENDQ` still recorded as exactly two attempts. The
  exact Agent integration shard passed 100 consecutive executions after the correction.
- The same audit found that the bounded transport queue still classified the now-authoritative
  friend-connection edge as disposable observation. Reclassified it as required backpressured
  evidence and added a one-slot saturation regression proving the exact online edge survives. The
  regression permits an already-published observational self/backend event to win a consumer race,
  but forbids any later required friend event from overtaking the connection edge.
- Release-scheduled process verification found that a four-byte incoming file could complete and
  leave the live transfer map between successful `TOX_FILE_CONTROL_RESUME` and the local
  `file-receive` response lookup. The command then falsely returned `not_found` after safe
  publication. The receive path now returns its frozen admitted record after successful RESUME;
  completion remains separate asynchronous evidence. Added ADR 0045 and a pinned c-toxcore
  admission/completion research note.
- Aligned the Agent's pre-provider oversized-text rejection with the typed c-toxcore boundary: empty and over-1372-byte text are `invalid_argument`, while only actual send-queue pressure is `resource_exhausted`; extended the transport regression with an explicit oversized body.
- Narrowed the malformed-command integration assertion to the exact outgoing message id. The exact
  peer may independently send a valid authorized `device.describe`; unrelated incoming commands no
  longer make the framing test nondeterministic.
- Added ADRs 0043–0045, the ratox message FIFO contract, c-toxcore/ratox receipt-boundary research,
  callback-owned online epochs, a revised evidence manual, and a rewritten lone
  BOOTSTRAPROSE office entrance.
- Corrected the separate-process file fixture to start the publication deadline at successful
  incoming admission rather than reuse the earlier offer/outgoing-transfer deadline. Slow valid
  scheduling can no longer manufacture a missing-publication failure; the exact body remains
  mandatory.
- Preserved the evidence boundary: live text and commands are exercised against the exact consumed
  c-toxcore ABI mock; official source-linked c-toxcore, genuine Tox peers, native-network receipts,
  Tox/Tor, and Tox/I2P remain unclaimed until their dedicated gates pass.



## rev0011 — Ordinary Write

### Literal ratox-successor command surface

- Added a daemon-owned mode-`0600` `peers/<TOX_PUBLIC_KEY>/command` FIFO for every current
  transport peer, plus exact `command.help` and bounded `command-events` observation files.
- Made `printf '%s\n' device.describe > command` enter the same generic one-binary command path as
  `iotox command FRIEND device.describe`; no second queue, product process, or protocol exists.
- Kept the admission order exact: frame and parse the local record, resolve the current public-key
  peer, reserve and commit one signed durable outgoing command, then attempt toxcore delivery.
- Recorded admitted FIFO writes with their nonzero durable sender epoch, message id, initial state,
  and detail; recorded malformed, unsupported, stale-peer, and storage/transport failures as
  explicitly not admitted.
- Clarified that `command-events` is transient ingress evidence, while the signed command store,
  `commands/` projection, and peer `iotox/description` hold durable or terminal truth.

### FIFO framing and filesystem hardening

- Added a Linux C++20 FIFO monitor using `eventfd`, `poll`, nonblocking read, a separate hold-writer
  descriptor, bounded peer rescans, and clean shutdown before the control socket and transport.
- Froze v1 to newline-delimited printable ASCII, a 256-byte body, and one implemented operation. A
  conforming producer can emit the complete record plus LF in one at-most-257-byte write, below the
  POSIX minimum `PIPE_BUF`.
- Rejected non-printable and oversized records, expired abandoned partial/discard fragments, and
  recovered framing for later writers without silently concatenating records across processes.
- Required a real same-user mode-`0600` FIFO under a real same-user peer directory; rejected
  symlinks, wrong ownership/mode, regular-file substitution, and path/inode replacement using
  `lstat`, `O_NOFOLLOW`, `fstat`, and device/inode comparison.
- Added bounded rotation for peer command ingress journals and atomic rename publication for
  disposable runtime projections without falsely giving them `fsync` durability.

### Command engine and process evidence

- Extracted `device.describe` execution behind a transport- and storage-blind command-engine
  boundary receiving only validated request and immutable execution context.
- Extended the separate-process fixture to write the literal FIFO, observe exact admitted durable
  identity under injected toxcore `SENDQ`, follow the eventual frozen result, restart the daemon,
  and verify durable continuity.
- Added direct tests for FIFO framing, multiple records, malformed recovery, partial-record expiry,
  late peer discovery, regular-file substitution and repair, private runtime surface publication,
  exact command-event rendering, and journal rotation.
- The default unit/integration executable now registers 98 C++ checks; the default CTest surface
  remains eight entries.

### Research and governance

- Re-read ratox's FIFO-first history, the pinned c-toxcore v0.2.23 public threading and packet
  contracts, and POSIX/Linux FIFO and `PIPE_BUF` semantics before freezing the adapter.
- Added ADRs 0040–0042 and a standalone ratox command FIFO v1 contract.
- Archived rev0010 `BOOTSTRAPROSE.md` and rewrote the lone entrance around the now-executable
  ordinary write path.
- Made `iotox --help` name the private per-peer command FIFO and state that it enters the same
  signed durable engine as the structured client.
- ThreadSanitizer found a startup race between the event pump's runtime publication and assignment
  of the FIFO service pointer. Constructed both service objects before the event thread can observe
  them and kept them alive through event-thread cleanup; the corrected TSan lane passes 8/8.
- Retained final-source GCC debug/release, Clang debug, ASan+UBSan, TSan, five 5,000-unit fuzzer
  runs, system-linked Argon2, Mutorr preservation, 98-check, process, mock-node, install, checksum,
  and prebuilt-smoke success.
- Preserved the larger evidence boundary: the exact ABI mock and local process fixture are green,
  while official source-linked c-toxcore and genuine Tox-network behavior still require a
  networked CLI.


## rev0010 — Durable First Word

### Durable command identity and state

- Added a private stable-device-signed command store in format v2 with atomic replacement,
  directory/file synchronization, strict ownership/mode checks, duplicate rejection, and bounded
  record/file limits.
- Defined restart-stable command identity as remote Tox public key plus a persistent nonzero sender
  epoch and sender message id; direction remains part of the local journal key.
- Added monotonic outgoing and incoming lifecycles, independent receipt/result delivery states,
  exact canonical request/receipt/result retention, authority-head evidence, send attempts, and
  terminal pruning rules.
- Refused mutation of immutable command fields, lifecycle regression, delivery regression,
  terminal-outcome rewriting, conflicting key reuse, invalid signatures, foreign device signatures,
  malformed files, and non-private storage.
- Kept the store signed but plaintext and documented whole-file rollback, metadata disclosure, and
  full-snapshot flash-wear limits.

### Application receipts, replay, and restart

- Advertised `durable_commands_v1` only after the exact session, store, process, and restart paths
  existed.
- Added the fixed eight-byte `ICA1` application receipt and distinguished committed `RECEIVED` from
  authority admission, execution start, terminal result, and toxcore local queue acceptance.
- Committed outgoing `device.describe` bytes before the first toxcore send; retryable `SENDQ` now
  reuses the exact persistent sender epoch, message id, and frame across reconnect or restart.
- Committed incoming requests before receipt, authority/start transitions before execution, and
  terminal result bytes before send.
- Replayed exact frozen receipts/results for exact duplicates and returned conflict for changed
  bytes reusing a durable key.
- Recovered unfinished read-only incoming and outgoing operations after restart without inventing a
  second logical command.
- Made durable record timestamps nondecreasing so ordinary wall-clock rollback cannot regress one
  record's audit ordering; trustworthy expiry remains unresolved.

### One-binary and ratox-style surface

- Added `--command-store`, `--max-command-records`, and `--max-command-store-bytes` agent options.
- Added one-binary `command-store` and `command-record DIRECTION PEER EPOCH MESSAGE` inspection.
- Added generic one-binary `command FRIEND OPERATION`; `device.describe` is the first registered operation and the older command name remains an alias.
- Added signed-journal generation, sender epoch, incoming/outgoing/pending counts to status and a
  transactional `commands/` runtime projection keyed by peer and durable command identity.
- Preserved the one installed `iotox` executable and kept the filesystem surface a projection over
  structured local control and durable state.

### Tests, mock peer, and governance

- Upgraded the exact c-toxcore mock into a durable peer with its own persistent sender epoch,
  receipt-before-result behavior, exact duplicate replay, and audit of received acknowledgements.
- Extended the one-binary process fixture through denial, authorized success, local request,
  injected `SENDQ`, receipt/result observation, journal inspection, restart, and exact-record
  equality.
- Added command-store tests for create/reload, stable sender epoch, signing, tamper and foreign-key
  rejection, frozen fields, transitions, deduplication, bounds, and terminal pruning.
- Extended the command fuzzer to decode receipts and increased the unit/integration registry to 88
  C++ checks while retaining eight default CTest entries.
- Added an exclusive `flock` guard to the destructive build matrix so overlapping verifiers fail
  with status 75 instead of deleting one another's active build directories.
- Added ADRs 0036–0039, source-contract and durable-boundary research, a rev0010 build report,
  and a rewritten lone BOOTSTRAPROSE office manual.
- Split the generated embedded RecallRoot word list into bounded translation-unit literals after
  Clang rejected the original oversized literal; the exact word-list bytes and vectors remain fixed.
- Closed the authority fuzzer's production dependency set after the clean Clang matrix exposed a
  missing stable-identity implementation, then completed all five bounded fuzz lanes.

### Evidence boundary

- The durable command path is compiled and exercised through an exact-mock one-binary process and
  restart fixture; it is not yet demonstrated between two official source-linked c-toxcore peers.
- Only read-only `device.describe` uses the durable engine. Cancellation, safe expiry, rollback
  resistance, encrypted storage, effect-specific idempotency, settings, actuators, and OTA remain
  unclaimed.


## rev0009 — Sovereign Ledger

### Stable identities and local constitution

- Added a random persistent Ed25519 device principal independent of the Tox savedata identity.
- Froze RecallRoot-v1 domain separation into a deterministic Ed25519 owner principal while
  keeping the permanent phrase/root/secret entirely in the short-lived local client.
- Added fixed-size canonical signed authority records, deterministic replay, atomic persistence,
  bootstrap/grant/revoke/succession, role ceilings, capability delegation limits, and
  last-owner protection.
- Added one-binary authority inspection and RecallRoot signing ceremonies plus transactional
  runtime projections.

### Transcript-bound directional authority

- Added canonical fixed-size authority challenges and Ed25519 proofs bound to the exact mutually
  confirmed online-epoch session transcript, device identity, ownership epoch, and challenge.
- Kept authority directional: each endpoint independently challenges and verifies the other.
- Made the stable device principal answer peer challenges automatically without exporting its
  secret; recalled-owner/controller proof remains an explicit lane.
- Advertised `authorization-ledger-v1` only after codec, policy, persistence, runtime, negative,
  and exact-mock process paths existed.
- Preserved `proof-sent` as local toxcore enqueue acceptance rather than inventing a remote
  verification receipt.

### First authorized machine operation

- Added a canonical bounded `device.describe` request, correlated result, and fixed device
  description carrying protocol, revision, feature, and stable-principal data.
- Required `read.telemetry`; the exact peer fixture proves denial before principal proof and
  success after proof against the current signed ledger.
- Added one-binary `device-describe` and `peer-description` commands and a ratox-style peer
  description projection.
- Bound accepted descriptions to the principal named by the peer challenge and the already
  confirmed protocol session.
- Kept this operation read-only, process-local, and explicitly non-durable; no actuator or
  setting mutation is exposed.

### Exact fixture, parsers, and verification

- Replaced the synthetic authority fixture with a distinct signed mock IoTox endpoint that owns
  its own stable Ed25519 principal, signs its proof, verifies the agent proof independently, and
  enforces byte-identical retry after injected toxcore `SENDQ`.
- Added strict command/result/description codecs, command and authority-session tests, local
  control operations, runtime-tree checks, and a fifth owned libFuzzer target.
- Increased the default unit/integration executable to 81 C++ checks while retaining eight
  CTest entries and one installed product executable.
- Added ADRs for transcript-bound directional proof and capability-gated `device.describe`,
  plus fresh c-toxcore 0.2.23 source research and a rewritten wake-from-amnesia entrance.

### Evidence boundary

- The owned C++/exact-mock path now crosses signed authority and one harmless authorized
  application request in both process directions.
- No genuine c-toxcore peer, public bootstrap/NAT/relay topology, durable command store,
  proof-acknowledgement protocol, safe physical effect, or Tor/I2P route is claimed.


## rev0008 — Transcript Confirmed

### Machine-session construction

- Added a fixed 256-byte canonical `ICF1` CAPABILITIES confirmation after the existing
  64-byte `IHL1` HELLO.
- Canonically ordered endpoints by raw 32-byte Tox public key and bound both endpoint keys,
  both exact HELLO payloads, both session nonces, selected protocol version, shared feature
  mask, frame limit, finite-file limit, and sender role.
- Froze the first local HELLO/confirmation message IDs during canonical record construction,
  before toxcore enqueue, and froze the first accepted peer HELLO/confirmation bodies for one
  true online epoch.
- Made byte-identical retries idempotent and changed same-epoch transcript material a
  fail-closed protocol conflict.
- Mapped c-toxcore custom-packet errors precisely and added automatic same-record recovery when
  a transient `SENDQ`/offline condition prevented a handshake packet from entering toxcore's
  queue; already accepted packets are not blindly resent.
- Added explicit states for awaiting confirmation, confirmed, malformed/conflicting
  confirmation, and confirmation-send failure.
- Added a post-confirmation application-frame gate enforcing exact negotiated version,
  nonzero message ID, and negotiated payload ceiling.
- Applied that gate to incoming frames and locally injected raw IoTox frames so the generic
  lossless seam cannot bypass session establishment.

### One-binary and runtime surface

- Added `iotox confirm FRIEND` and local-control operation 29 while retaining `hello` as an
  explicit frozen-record retry.
- Distinguished aggregate HELLO-compatible sessions from mutually established sessions.
- Projected `transcript-confirmed`, `established`, `application-ready`, confirmation IDs,
  sender role, per-record send-attempt counters, and transient send-error class under each
  public-key peer directory.
- Kept `authorization=none-transport-session-only` visible after establishment.

### Exact mock and tests

- Changed the toxcore ABI mock from packet echo behavior into a distinct IoTox peer with its
  own transport-key perspective and HELLO nonce.
- Made the mock validate the local canonical confirmation and answer with the opposite
  canonical sender role.
- Added independent, type-specific `SENDQ` injection for HELLO and CAPABILITIES so both retry
  paths are exercised rather than inferred from one generic packet failure.
- Added canonical codec, mutation, ordering, correlation, failure-before-success ID
  reservation, retry, rejected-transcript replay, `SENDQ` recovery, state-machine,
  raw-bypass rejection, and application-gate tests.
- Extended the session libFuzzer to drive both HELLO and confirmation payload/frame paths.
- Updated the process fixture and prepared real-peer fixture to require `state=confirmed` in
  both directions.
- The unit/integration executable now registers 64 checks; seven default CTest entries remain.

### Research and governance

- Rechecked current c-toxcore release/project status and retained 0.2.23 as the pinned target.
- Studied ToxExt negotiation and transcript-bound handshake barriers in TLS 1.3, DTLS 1.3,
  and Noise, adopting only the state-machine lessons applicable above Tox.
- Added ADR 0028 for mutual transcript confirmation, ADR 0029 for local-enqueue acceptance
  and retry, the exact session contract, and rev0008 research notes.
- Preserved rev0007 `BOOTSTRAPROSE.md` and rewrote the root entrance so the next office holder
  cannot confuse compatibility, establishment, application readiness, or authorization.

### Evidence boundary

- Mutual confirmation proves agreement on the current Tox online-epoch IoTox transcript. It
  is not an application signature or authorization grant.
- No official source-linked c-toxcore binary or genuine Tox peer was executed in this
  cloudtainer.
- Retained-evidence refresh can consume an isolated completed matrix in place, avoiding false
  rebuilds and invalid copied CMake caches while still rerunning the product and prebuilt
  smoke surfaces.
- The independent authorization ledger is the immediate next product boundary.

## rev0007 — Peers Speak First

### Ratox-successor product work

- Added a canonical automatic IoTox HELLO whenever a Tox friend enters a real online epoch.
- Added deterministic version, feature, frame-limit, and finite-file-limit negotiation with a
  fresh operating-system CSPRNG nonce per epoch.
- Added a per-peer session registry that freezes the first remote HELLO, accepts byte-identical
  retries, fails closed on changed advertisements, and distinguishes offline, negotiating,
  compatible, incompatible, malformed, conflict, and send-failure states.
- Added one-binary `sessions`, `session`, and `hello` operations plus a private per-peer
  session projection and commit marker.
- Added a live incoming-friend-request inbox keyed by Tox public key, exact message-byte
  preservation, private transactional request directories, and one-binary list/accept/reject.
- Split `request-accept` from direct `transport-peer-accept`: the former requires a matching
  live request; the latter intentionally adds a known key without claiming a request existed.
- Kept every session and request record explicitly transport-only. Neither friendship nor
  protocol compatibility grants IoTox ownership, roles, commands, firmware, or actuator
  authority.

### Protocol and implementation

- Froze the 64-byte `IHL1` HELLO payload, its 41-byte outer frame invariants, and the 1,332-byte
  payload budget under c-toxcore's 1,373-byte reliable custom-packet limit.
- Advertised only implemented session, human-text-lane, and finite-file features; future
  authorization, durable commands, state sync, RecallRoot, OTA, route binding, and Mutorr bits
  remain named but unset.
- Added strict reserved-zero, version-range, feature-subset, nonce, and file-limit validation.
- Added OS-CSPRNG generation through `getrandom` with `/dev/urandom` fallback and no
  deterministic production fallback.
- Gated non-HELLO machine dispatch on a compatible session while continuing to preserve
  bounded protocol evidence.
- Raised the private local control protocol to 1.6 for request and session operations.
- Strengthened the source-linked provider so official c-toxcore headers are mandatory when
  canonical upstream source is selected.
- Restricted the install graph to the single public `iotox` executable; optional research
  programs remain build/test instruments and a clean-prefix install verified executable count one.

### Reliability and operator surface

- Session state is keyed by current friend number internally but always bound to and projected
  under the current 32-byte public key.
- The runtime tree writes detailed session fields first and atomically replaces the root
  `session` marker last, making it the observable complete-record commit.
- Incoming request callback bytes are copied before callback return; same-key publish,
  accept, and reject transitions are serialized.
- The request inbox is honestly labeled live and transient. It is not savedata, an audit log,
  or an authorization ledger.
- The mock operator fixture now waits for the real connection-status callback before expecting
  HELLO, exercises automatic negotiation and explicit idempotent retry, and makes an explicit
  incoming-request decision.
- Made `files` an authoritative local read barrier: the agent refreshes the live transfer
  snapshot and commits aggregate counts plus the ratox-style transfer tree before replying.
- Hardened the product-process fixture with bounded asynchronous observation, a longer agent
  watchdog, and unconditional child termination/reaping on both success and failure.

### Research and governance

- Re-read pinned c-toxcore 0.2.23 friend-request, public-key lookup, connection-status,
  custom-packet, options, and CMake contracts from official source.
- Re-read ratox's incoming-request surface and retained its explicit Unix decision model.
- Added ADRs for canonical HELLO, mandatory official linked headers, and the live explicit
  friend-request inbox.
- Rewrote `BOOTSTRAPROSE.md` as the rev0007 wake-from-amnesia office and preserved rev0006 in
  history.

### Verification

- 60 registered C++ tests and seven default CTest entries pass in the GCC debug lane.
- Three Clang libFuzzer targets cover the outer frame, HELLO/session decoder, and local control
  decoder.
- Replaced mutable checked-in fuzzer work corpora with four reviewed canonical seeds; every
  smoke run copies them into disposable build-local corpora before libFuzzer mutation.
- The one-binary process fixture crosses the Unix socket, owner thread, exact loadable C ABI
  mock, callbacks, event pump, session registry, journals, runtime tree, and savedata restart.
- The prepared source-linked fetch was attempted and retained; shell DNS failure prevented the
  pinned archives from being downloaded in this cloudtainer.

### Evidence boundary

- No official c-toxcore source-linked binary or real Tox network was executed here.
- No public bootstrap, NAT, relay-only topology, Tor route, I2P route, or target hardware was
  exercised.
- `compatible` means negotiated transport capability only; authorization remains unbuilt.

## rev0006 — One Binary Speaks

### Ratox-successor product work

- Added current c-toxcore self/peer profile, presence, typing, normal text, action text, and
  read-receipt behavior to the C++ owner-thread adapter.
- Extended the exact loadable toxcore mock so the same lifecycle is deterministic without
  pretending to be a Tox network.
- Added one-binary profile inspection and mutation commands, including bounded raw-stdin and
  hexadecimal byte forms.
- Added one-binary normal/action text and typing commands.
- Made the Tox public key the preferred stable selector for all existing-peer operations;
  local friend numbers remain accepted as a convenience.
- Added private, bounded, byte-preserving per-peer text journals and one-binary read/follow
  commands.
- Added strict per-peer IoTox frame journals for valid incoming and successfully queued
  outgoing lossless frames, plus one-binary read/follow commands.
- Kept the global event journal payload-free so ordinary diagnostics do not copy human text
  or IoTox packet contents.
- Extended the process fixture through profile persistence, NUL/newline text, action echo,
  read receipt, typing, HELLO encode/decode, public-key file operations, restart, and removal.

### Protocol and local surface

- Raised the local control protocol to 1.3.
- Froze the distinction between Tox presentation/text and IoTox device-control frames.
- Froze stdin as the first exact-byte Unix write path while writable FIFOs remain a later
  compatibility façade over structured requests.
- Added `MessageType` rendering and decoded protocol metadata projection.

### Reliability and security

- Runtime message and protocol journals are owner-only, escaped into one-line records, and
  rotate to one previous segment at bounded thresholds.
- Hardened the end-to-end echo test against slow instrumented filesystems while preserving
  the complete owner/callback/queue/journal visibility requirement; runtime projection
  latency remains an explicit optimization gate rather than a hidden flaky assumption.
- Peer runtime mappings are rebuilt from current toxcore state rather than retaining stale
  friend-number entries.
- Profile and text fields are bounded by the reviewed 0.2.23 API limits.
- Tox receipts are explicitly described as transport receipts, never command execution.

### Research and governance

- Re-ran the current c-toxcore 0.2.23 profile/text/custom-packet source reading and ratox
  interface reading against primary sources.
- Added ADRs 0020–0024 for presentation semantics, journals, public-key selectors, stdin,
  and decoded protocol observation.
- Rewrote `BOOTSTRAPROSE.md` as the rev0006 wake-from-amnesia office.
- Preserved rev0005 BOOTSTRAP history and Mutorr as a non-default incubator.

### Verification

- 48 registered C++ tests and seven default CTest entries pass.
- The retained matrix covers GCC debug/release, Clang debug, Clang ASan/UBSan, GCC TSan,
  process lifecycle, both libFuzzer decoders, and Mutorr preservation.
- The mock-node operator fixture now demonstrates profile, binary action text, receipts,
  public-key selection, and decoded HELLO traffic through one executable.
- The operator fixture now builds by absolute configured-directory path and succeeds from an
  arbitrary caller working directory.

### Evidence boundary

- Official c-toxcore source could not be fetched and built in this cloudtainer.
- No real Tox peer, public bootstrap, NAT, TCP relay, Tor route, or I2P route was exercised.
- rev0006 is intentionally implementation-forward while retaining exact claim labels.

## rev0005 — One Binary, File Road

Merged the public daemon/client pair into one `iotox` executable; added dual toxcore
providers, bounded queues, mutation persistence, bootstrap/relay controls, friendship,
finite regular-file transfer, transactional runtime projections, pinned standalone scripts,
and a one-binary process fixture.

## rev0004 — Wake From Amnesia

Established the lone `BOOTSTRAPROSE.md` entrance and first executable ratox-successor slice.
