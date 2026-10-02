# IoTox roadmap

Updated 2026-10-01. This is the ordered product plan for the official repository. A milestone is
complete only when its implementation, failure behavior, documentation, and named evidence gates
are all present. Historical revision plans remain useful design records, but this file owns current
priority.

## Product northstar

IoTox is one sovereign device-agent binary: Tox provides peer transport, IoTox establishes stable
identity and capability authority above friendship, and an ordinary private Unix surface makes the
agent scriptable. No project-controlled key can reassign a device.

For a human-facing entrance into the documentation, start with
`docs/README.md`, `docs/quickstart.md`, and `docs/product-page.md`; use this
roadmap for product order and evidence boundaries rather than first contact.

## Shipped foundation

The maintained tree currently has:

- one `iotox` executable with local client and daemon modes;
- pinned source-linked c-toxcore, libsodium, and Argon2 standalone construction;
- a genuine two-peer Tox/native smoke proven on the founding bare-metal host;
- stable device identity, RecallRoot owner identity, signed authority-ledger v1/v2, and
  transcript-bound proof with explicit non-widening migration;
- durable read commands with bounded offline admission, restart replay, and deduplication;
- exact-HEAD remote signed-update staging through the same authority-bound durable command journal
  plus owner-local release-signer revocation policy;
- ratox-style friendship, text, action, command, and finite-file surfaces;
- `--mode self`, which selects Ratox host/controller roles for self-owned machines while preserving
  profile, binding, `interactive.terminal`, and sudo gates;
- strict unit/process/provider tests, sanitizers, fuzzers, stress tests, and a coverage floor;
- canonical terminal profile v7 with frozen login-account groups, default-denied privilege gain,
  and exact optional SHA-256 pins for the shell and rescue Toybox payloads,
  default baseline seccomp, opt-in fail-closed MDWE/Landlock ABI 10 strict confinement, and a
  separately explicit host-authorized sudo compatibility profile;
- an optional separately versioned static oksh/Toybox rescue payload and disabled baseline rescue
  profile for machines whose ordinary dynamic shell/tool userland is unavailable.

This is pre-release security-sensitive software. A successful founding-host smoke is not yet a
repeatable network- or target-verification program.

The sole-machine network laboratory is standardized in `sandwurm-two-node-lab.md`. Planned operator
commands are frozen separately in `future-cli-contract.md`; presence there does not imply current
implementation. `multi-route-plan.md` owns the route-set, protected-Ratox, and immutable-object
scheduler sequence; ADR 0108 prevents construction striping from being mislabeled as transparent
bonding.

On 2026-08-20 the Sandwurm construction gates passed for two distinct NixOS closures. Independent
`client` and `device` guests first booted with networking absent. The pair gate then kept both stock
Cloud Hypervisor guests live on distinct prepared-bridge TAPs and positively observed genuine
source-linked Tox friendship, confirmed IoTox sessions, private L2 reachability, and bidirectional
text under direct UDP and forced TCP. Both routes used the identical pinned production binary and an
ephemeral local c-toxcore bootstrap/relay fixture. This proves the controlled two-VM transport
baseline. A subsequent forced-TCP cell killed that fixture only after both sessions were confirmed,
required both guests to observe offline, restarted the same relay identity, and proved fresh
bidirectional traffic at online epoch 2 after initial epoch 1 on each side. This proves the relay
interruption/recovery slice of route-fault behavior. Another forced-TCP cell kept both guests and the
relay live, stopped and replaced the device daemon from savedata, required the stable client to
observe transport and application offline, preserved the exact device identity, advanced the stable
client epoch from 1 to 2, and exchanged fresh text. A controlled packet-blackhole cell then kept
carriers and processes live, required bilateral offline observation, restored both TAP paths, advanced
both epochs from 1 to 2, and exchanged fresh forced-TCP text. A distinct seeded 5% partial-loss gate
then kept both sessions at epoch 1 and delivered ordinary text during impairment on direct UDP and
forced TCP. Direct UDP exposed 20 lossy-probe misses across 256 samples; forced TCP exposed none
despite 26 observed TAP drops, demonstrating retransmission below the Tox carrier. These gates do not
prove Ratox PTY survival, public bootstrap, or provider-upgrade behavior. The device guest was
then rebooted from its persisted disk across two bounded Sandwurm VMM epochs; boot identity changed,
device identity did not, and the stable client recovered at epoch 2 after initial epoch 1.

## Current priority

All milestones M0--M8 are complete for the founding-machine scope frozen by ADR 0277. The checklist
has zero open items and retains exactly six struck out-of-scope gates. Future work is product
expansion or downstream evidence, not unfinished founding-roadmap work. ADR 0284 separates this
completion from precious-data trust; `sync-trust-graduation.md` names the next recovery,
extended-soak, abrupt-storage, capacity, and operator-rehearsal work. ADR 0318 closes the bounded
filesystem-contract preflight mechanism while retaining platform and runtime qualification as
explicit nonclaims. ADR 0319 closes the read-only exact external-restore comparison inside the
recovery-rehearsal gate; ADR 0323 adds bounded one-node/all-live-node identity recreation, reseed,
verification, and obsolete-writer retirement without claiming recovery custody or provenance.
A clean retained Sandwurm run now composes that recovery with the 512-file/24-cycle persistent
lifecycle and completes one-node plus all-node reconstruction without a watchdog restart. An earlier
VM campaign exposed consecutive authority challenges overtaking an unfinished proof;
ADR 0324 now permits only a strictly newer head from the same verifier/session to supersede that
round while preserving same-head conflict refusal. ADR 0360 adds strict operator provenance labels to
restore verification and strict custody labels to witness-checkpoint verification while retaining
`backup-independence=not-assessed` and `operational-independence=not-assessed`. ADR 0361 adds
duration-bound writable soaks, short/24-hour Sandwurm profiles, and retained recovery drill receipts.
ADR 0362 keeps exact terminal cutoff replays out of live frontiers after the first soak-smoke
recovery run exposed that edge. ADR 0364 retains content-free partial-soak receipts for ordinary
interruption of long soaks, and ADR 0365 retains content-free witness checkpoint custody drill
receipts without promoting them to independence claims. ADR 0366 adds fail-closed local requirement
flags for retained recovery and witness custody drills. ADR 0369 makes live long-soak status
cadence-aware, ADR 0370 hardens rejected-receipt writing against shutdown signals, ADR 0371
keeps the 24-hour profile passive on slow cycles, ADR 0372 moves scheduled restarts before
the synthetic cycle edit, ADR 0373 defers periodic repair away from restart cycles, ADR 0374
adds an explicit restart-settle sync-repair pass before post-restart edits, and ADR 0375
turns the active VM-only 24-hour gate back to bounded, recorded stalled-cycle recovery after a
long passive window. ADR 0376 makes the sparse 24-hour live log per-cycle so ordinary progress and
hidden stalls are distinguishable while watching. Compact proof
`.sandwurm/exports/three-writer/run.UFBCMzt9` accepts the short same-host KVM/ext4 smoke with
recovery provenance and storage-fault follow-up. Compact proof
`.sandwurm/exports/three-writer/run.9nqvO8B2` accepts the 24-hour bounded same-host KVM/ext4
three-writer soak:
289 writable cycles over `32h13m01s`, 12 scheduled restart-settle passes, 12 deferred repairs with
no pending repair, 4 bounded stalled-cycle recoveries, maintenance lifecycle, writer cutoff,
recovery rehearsal, storage-fault rehearsal, and read-only startup refusal.
Versioned recovery custody and restore evidence remain scoped operator gates.
ADR 0403 refreshes the current
accepted long-soak receipt after the native precious-data signoff porches:
`.sandwurm/exports/three-writer/run.2nPKtCoX` verifies with 288 cycles over
`27h04m13s`, 11 restart-settle passes, zero stalled-cycle recoveries or stalled
cycle restarts, recovery rehearsal, storage-fault rehearsal, ENOSPC observation,
and `contains_secrets=false`.

New significant architectural additions do not enter this queue merely by being
useful. They first need an intake dossier using
`docs/architectural-change-intake.md`, then an ADR/evidence plan that names the
affected authority, storage, route, terminal, diagnostics, and documentation
boundaries. The roadmap can accept the work only after its nonclaims are as
clear as its intended power.

ADR 0382 names the product frontier: self-machine multidevice, not Tox
multidevice. The Ratox/SSH-like surface defaults on only inside `--mode self`;
a machine that possesses/proves the owner's IoTox self key can join the
owner's self domain through ADR 0383's signed roster v1. The native
`iotox self-swarm` surface creates, joins, retires, inspects, verifies, plans,
grants, and revokes narrow self-machine entries while stale generation floors,
wrong owners, wrong stable principals, wrong route keys, and retired members
fail closed in tests. ADR 0384 adds native self-swarm floor records,
`fanout-plan`/`fanout`, and optional live alias-route proof before grant/fanout
work, plus Ratox daily-driver and sync dataset-readiness porches. ADR 0385 adds
the first person layer above the private self roster: `iotox person` creates a
public owner-signed delivery card, signs bounded person-message envelopes, plans
exact `message-hex key:...` fanout, live-sends the same envelope to every
current route after resolving all routes first, and verifies received payloads
independent of transport route. ADR 0386 makes the first multidevice
conversation substrate coherent: person-signed device sender delegations,
contact-side delivery-card floors, local seen stores for duplicate suppression,
signed group descriptors, direct/delegated group-message envelopes, and a
review-only group fanout plan through member person cards. ADR 0387 adds the
first native messenger stores: contact book, local transcript, delegated device
receipt, and durable reviewed outbox planning/route accounting. ADR 0388 adds a
native one-shot outbox sender plus executable storage and Ratox activation
evidence gates. ADR 0389 makes the daily front doors ordinary: `person receive`
idempotently verifies/commits local receive state, `person messenger-status`
reports content-free store health, `sync trust-plan` renders the trust runbook,
and `terminal daily-status` gives operators a non-failing dashboard that points
at the strict activation gate. ADR 0390 adds the normal Tox compatibility
bridge: ordinary Tox friend text/action remains the outside carrier, while
IoTox self devices exchange signed delegated observations of those normal Tox
messages through a separate bridge store. The Toxic live gates now cover both
the default route and forced-TCP route on the founding workstation, including
the three-device bridge/fanout/status proof; the default route is the strong
ordinary claim, while forced-TCP compatibility is kept as a separate
follow-up-soak claim after repair rather than folded silently into the default
claim; current readiness continues to name that lane
`default-qualified-forced-tcp-degraded` until retained smooth follow-up
evidence graduates it. ADR 0391 graduates the two most important operator porches:
`iotox sync graduation-check` aggregates per-dataset working-copy evidence
while refusing precious-data certification, and
`iotox terminal graduation-check` aggregates daily-driver Ratox evidence while
keeping the claim host/route/operator bounded. ADR 0392 adds the release brake:
`iotox ship-check` fails closed for stable/no-concern sync or Ratox shipping
and permits only an explicit founder-preview channel with attached nonclaims.
ADR 0393 adds the repository release trail around that brake:
`tools/iotox-repo.sh release-plan founder-preview` prints the command path, and
`tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox`
requires clean-tree/script/native-gate alignment while preserving the
stable/no-concern block. ADR 0395 then replaces “hardcoded forever blocked”
with an evidence-gated stable dossier: `tools/iotox-repo.sh
stable-evidence-plan` prints every required sync/Ratox receipt class, and
`iotox ship-check all stable --evidence-manifest stable-evidence.manifest` can
graduate only when every required gate is accepted and bound to a receipt file
whose SHA-256 matches the manifest. ADR 0396 makes long soaks first-class
stable evidence: sync stable now names `sync.long-soak`, and
`terminal.long-soak` must be an accepted native terminal long-soak receipt
covering at least 86,400 observed seconds with bounded sampling gaps and zero
failures. ADR 0398 hardens the precious-data side of that intake: stable sync
evidence now hash-binds and shape-checks every sync receipt class, including
storage-readiness, long-soak, versioned recovery custody, retained
restore drill, and recovery runbook, so placeholder prose cannot pass the
native release brake. ADR 0401 makes the precious-data operator path native:
`sync backup plan|verify|receipt`, `sync retention set|status`,
`evidence collect sync`, `evidence manifest`, and `sync precious-status`
turn the backup/restore/retention/sign-off ceremony into ordinary
content-free commands. ADR 0402 adds the final local acceptance receipt:
`sync precious-signoff` writes only after `precious-status` would pass and the
operator explicitly accepts responsibility, binding hashes rather than dataset
contents or the literal dataset path. ADR 0404 strengthens the recovery-runbook
gate: `sync runbook plan|receipt|status` now makes runbook review native,
hash-binds the reviewed runbook and dataset selector, and rejects old minimal
four-line runbook receipts. ADR 0414 closes the resident-service side of the
stable dossier: `iotox service status-plan|status-receipt` records explicit
active/enabled-or-managed/log-reviewed/health-passed/upgrade-passed service
observations, and `evidence collect terminal --service-reality` accepts that
receipt as the preferred `terminal.service-supervision` gate while preserving
cgroup, route, sudo, sync-folder, and human-read nonclaims.
Native messenger maintenance now includes card freshness, outbox retry/expiry,
aggregate receipt status, a bounded background runner suitable for service
supervision, local human-read state, transcript convergence checks, and group
status summaries. ADR 0412 adds the native graduation dashboards that make the
current boundary ordinary: stable
`evidence dossier-plan|dossier-status`, sync precious-status signoff commands,
self-swarm daily-status, and person messenger-plan. ADR 0413 adds resident
services and messenger-readiness polish; the resident-service porch drafts
Agent/sync/Ratox and person-worker units for systemd, NixOS, and MonsterNix
adapter review. ADR 0414 adds service reality receipts for stable evidence.
ADR 0415 adds the missing native graduation
surfaces for the operational layer: `iotox person graduation-check`,
`iotox person tox-bridge-graduation-check`, and
`iotox route-qualification-check` aggregate the person messenger, Toxic bridge,
and Tor/I2P lane evidence without certifying anonymity, silent fallback, or
normal-Tox understanding of IoTox person identity. The current accepted stable
dossier was also refreshed to use a native `iotox.service-reality.v1`
`terminal.service-supervision` receipt:
`.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest`.
See `docs/self-mode.md`, `docs/person-multidevice.md`, and ADRs 0383--0415.
Future product expansion remains delivery guarantees for devices that never
return online, a global conversation-order story beyond message-id/digest
convergence, independent witness custody for person/group freshness, private
roster/contact sync, and optional Tox group/conference transport adapters.
The public handoff path has also been slimmed: `tools/iotox-repo.sh datacube
--public` creates the current GitHub/reviewer artifact, while
`--conversation` remains for richer internal provenance; see
`docs/revision-packaging.md` and `docs/conversation-datacubes.md`.
ADRs 0320--0322 add the
first persistent-ext4, three-writer capacity result: 512 16-KiB files converge and repair across the
full mesh, projection durability uses one filesystem barrier per derived tree, and an interrupted
exchange preserves a live path-based edit across restart. Near-ceiling/cold repetition, the remaining
power-cut/corruption matrix, and broad open-descriptor writers remain open; the same-host 24-hour
soak is now accepted separately. ADR
0325 closes the first bounded real-filesystem slice: three separate ext4 node volumes recover from
live `ENOSPC`, refuse read-only startup without changing durable state, and join an abrupt Agent
death at a signed pending-workspace boundary. ADR 0328 separately closes the direct scan/store
source-mutation case for a held writer descriptor. ADR 0332 then closes one corrected true whole-VMM
workspace-exchange cut: raw phase byte 2 binds the pending journal, the exact task-owned crash disk
boots under a second kernel, only permitted prior/completed projections appear before Agent restart,
identities persist, and all writers converge. The phase-reversed v1 predecessor is withdrawn. Other
transition cuts and the dishonest-storage boundary remain open.
ADR 0333 closes the immediately adjacent post-exchange/pending cell using raw workspace and
projection identities rather than timing. The accepted crash retained the completed projection,
pending journal/marker, and old stage before exact recovery. Both workspace exchange sides now pass;
the next cut must target a different transaction family rather than repeat this pair. ADR 0334 makes
receive and CAS-temporary cleanup durably idempotent, freezes v4 object-pipeline evidence, and adds
semantic `receive-staging-partial` and `cas-install-temporary` Sandwurm cells. Source-linked runs
`1e05ayp9` and `jtiyspp_` now pass: each stops the Agent at the exact temporary before host VMM
`SIGKILL`, boots the crash disk, admits only exact prior/completed offline views and absent-or-exact
CAS state, then preserves identity, converges, restores three branches per node, and repairs. The
next abrupt-storage family is manifest/branch publication, not another timing variant of these cuts.
ADR 0335 now constructs three proof-v5 pre-rename cells around exact metadata-prefix commitments and
the real ptrace-stopped sync worker. Its first genuine pointer-prefix cut found and now has a direct
regression for an orphan-record recovery stall: reusable immutable state is no longer confused with
an incorporated mutable pointer. Repaired-source runs `l2gckna4`, `c9xhj26a`, and `_cphu30p` now
pass all three prefixes from one binary. The next transaction cells are each
post-rename/pre-directory-fsync side. ADR 0336 freezes those three cells as proof v6: exact
path-filtered parent-directory `fsync` entry fences, explicit live post-rename prefixes, and bounded
old-or-new offline directory outcomes. Repaired-source runs `dbgtc3ip`, `jznfzx52`, and `ia70ljmf`
now pass from one optimized binary. Its first record-directory attempt exposed and removed five
unconditional steady-state preparation barriers. The next abrupt-storage family is durable-record
corruption. ADR 0337 now makes all five present live signed tree-v2 metadata
roots fail closed at startup and `sync-repair`, preserves corrupt bytes, and
qualifies exact operator restoration on the founding Sandwurm/KVM/ext4 stack.
Run `mixJ9VUp`, source-linked to commit `08e4179`, passes all five ordered
cells, exact-byte retention/restoration, identity/worktree preservation,
`[3,3,3]` convergence, and repair. ADR 0339 now adds direct valid-old
external-witness refusal for branch/workspace/maintenance semantic roots and
a receipt-v2 co-resident-corruption construction. Source-linked KVM/ext4 run
`MG27auOK`, bound to commit `2be7a2a`, passes the all-five stopped-task cell,
ordered cold-start restoration, convergence, and strict compact verification.
ADR 0338 closes the deterministic descriptor write
between final scan and directory exchange and makes projection-marker policy
transitions authenticated, but writes after final old-tree validation begins
remain open. ADR 0340 now qualifies the production descriptor/remount frontier
for its bounded ordinary-file class on founding Sandwurm/KVM/ext4 raw proof.

### Active frontier, in priority order

The following is the operative queue after the closed founding roadmap. Items in one tier may be
developed together, but a later tier must not be used to obscure an earlier trust boundary.

1. **Graduate synchronization recovery and storage behavior.** Extend ADR 0320's accepted
   512-file/8-MiB persistent three-writer cell toward cold and near-ceiling populations; carry the
   accepted 24-hour writable soak forward as a baseline and complete the named abrupt-storage matrix.
   ADR 0325 supplies one bounded
   real `ENOSPC`, read-only-root, and abrupt-Agent exchange slice; ADR 0332 now boots the exact durable
   disk after one corrected whole-VMM raw-byte-2 pending-exchange cut and proves old-or-new projection
   atomicity before restart. Its phase-reversed v1 predecessor is withdrawn. Repeat the corrected
   method at every other named transition and both linearizations. ADR 0334 now closes the partial
   generic receive and partial CAS-install boundaries with two source-linked v4 campaigns. ADR 0335
   constructs exact pre-rename cuts for immutable manifest installation, immutable branch-record
   installation, and mutable branch-pointer replacement; all three repaired-source-linked campaigns
   now pass and are retained as compact proofs. ADR 0336 closes their three
   post-rename/pre-directory-fsync sides with another same-source compact-proof set. ADR 0337
   implements the next five-family live signed-metadata corruption cell: branch
   pointer, immutable branch record, manifest, workspace, and maintenance all
   refuse without mutation until exact external restoration. Source-linked run
   `mixJ9VUp` qualifies that exact cell and retains a strict compact proof.
   ADR 0339 adds deterministic valid-old witness refusal and v2 simultaneous
   co-resident corruption construction; `MG27auOK` qualifies it on Sandwurm
   and retains a strict compact proof. ADR 0338 preserves held-descriptor
   writes up to immediate old-tree
   validation and authenticates sparse projection transitions. ADR 0340 now
   proves real post-exchange descriptor retention across controlled restart
   and closed-descriptor ext4 remount in source-linked run `1fq3WhIY`; compact
   proof `.sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY`
   independently verifies. ADR 0378 now accepts the first same-host
   dm-snapshot dishonest-storage drill: run `run.UbmYPe1X` writes generation 2
   through an acknowledged ext4 snapshot COW, discards that COW, cold-reads the
   older valid generation 1 origin, and refuses mutation against the external
   generation-2 witness floor. This covers branch-pointer, workspace, and
   maintenance shaped records as a content-free substrate gate. ADR 0379 then
   extends the matrix to ext4 and btrfs with six production-shaped families:
   branch pointer, immutable branch record, manifest, workspace, maintenance,
   and projection marker. Run `run.qGwEvF17` passes eight cells covering
   valid-old rollback, manifest/branch-record cross-family rollback, torn
   manifest content, and `dm-flakey drop_writes` masked write loss. ADR 0380
   then accepts the first exact block-prefix replay substrate: run
   `run.90LCC7ra` uses `dm-log-writes` plus the `xfstests` `replay-log`
   helper to replay three marked ext4 and btrfs prefixes
   (`generation-1-stable`, `manifest-record-prefix`, and
   `generation-2-stable`) onto fresh cold-mounted images. The new
   ADR 0381 production adapter then wraps a real Agent namespace:
   `run.HYXJnDzI` starts the Agent with sync enabled, runs real
   `sync-create`, `sync-publish`, and `sync-repair`, and replays ext4 and
   btrfs `dm-log-writes` transaction marks
   (`sync-create-generation-1` and `sync-publish-generation-2`). The
   `tools/iotox-repo.sh storage-readiness` report accepts this local storage
   science while keeping versioned recovery custody and
   precious-data readiness blocked; the dishonest-storage plan is in
   `docs/dishonest-storage-plan.md` and the executable graduation definitions
   are in `docs/storage-readiness-gates.md`. ADR 0400 removes
   storage-media certification from IoTox's roadmap; ADR 0399's planner now
   prepares backup-custody and recovery-runbook templates only. ADR 0401 adds
   native backup-custody receipt generation, reviewed retention-policy
   records, stable sync evidence collection, and `sync precious-status` so a
   dataset can become operator-signable without pretending IoTox is the only
   archive. ADR 0402 adds `sync precious-signoff` as the durable content-free
   owner receipt over that green evidence bundle. ADR 0404 adds the native
   hash-bound `sync runbook` receipt and makes old minimal runbook receipts
   invalid for precious-data signoff.
   ADR 0328 closes the narrower
   post-scan source-descriptor mutation gate. Repeat ADR 0323's
   now-VM-qualified loss-of-node/all-live-nodes restore, re-authority, reseed, verification, and
   obsolete-writer retirement ceremony against an actually independent retained backup. ADR 0360 now
   records the backup system, generation, failure domain, restore provenance, and same/different
   device observation inside the verifier report. ADR 0361 adds an explicit duration-bound
   three-writer soak mode, fast/24-hour Sandwurm profiles, and a retained recovery drill wrapper
   that preserves verifier-report hashes and operator-provenance bindings without promoting them to
   backup proof. ADR 0362 prevents exact terminal cutoff replays from reintroducing a retired writer
   to the live frontier while preserving historical records for validation. ADR 0364 now keeps
   ordinary interrupted long-soak attempts as rejected partial-soak receipts with cycle, restart,
   repair, timing, and digest progress. Compact proof
   `.sandwurm/exports/three-writer/run.UFBCMzt9` accepts the short soak-smoke plus retained recovery
   and storage-fault composition. ADR 0366 lets the retained recovery wrapper reject unlabeled or
   same-device receipts when the operator is exercising an independence-oriented gate. Compact proof
   `.sandwurm/exports/three-writer/run.9nqvO8B2` now accepts the same-host KVM/ext4 24-hour
   soak with 289 cycles, 12 scheduled restart-settle passes, 12 repair deferrals, and no pending
   repair. ADR 0403 refreshes the current signoff-era proof to
   `.sandwurm/exports/three-writer/run.2nPKtCoX`, which verifies with 288 cycles
   over `27h04m13s`, 11 restart-settle passes, zero stalled-cycle recoveries,
   and content-free compact evidence. The same-host loopback custody helper now passes local provenance and different-device
   prerequisites in run `run.9xP4yW5T`, retaining content-free receipt
   `.sandwurm/exports/sync-recovery-custody/run.9xP4yW5T/retained-recovery-drill.json`. That narrows
   the operator ceremony but does not prove disk-loss, host-compromise, or
   filesystem-wide corruption protection. The remaining graduation gate is
   proving that the recovery labels name real immutable/versioned custody
   outside normal IoTox sync write/delete/GC mutation and that restore drills
   remain repeatable. This is the work that separates “useful synchronized
   working copy” from a recommendation for important working sets. It still
   does not turn synchronization into disaster recovery.
2. **Make protected-state freshness operationally independent.** Deploy the authenticated witness
   and its signed checkpoint outside the Agent disk/admin/snapshot domain; freeze executable
   witness replacement, epoch handoff, emergency re-anchor, data-key custody/rotation, and exact-
   current restore ceremonies; then extend/fault-test freshness for the remaining effect-bearing
   namespace closure. ADR 0360 adds `witness-service-checkpoint-custody` so a signed checkpoint can
   be verified as authentic, outside the service root, and accompanied by custody labels and
   same/different device observation. ADR 0365 adds a retained drill wrapper and repository-helper
   entry point that preserve hashes, bounded counts, and custody-label bindings without exposing
   paths or checkpoint contents. ADR 0366 lets that wrapper reject unlabeled or same-device receipts
   when local custody prerequisites are required. Near-term qualification may use VM-only local
   failure domains because this project currently has one physical computer. Those receipts are
   useful protocol and ceremony evidence, but the remaining nonclaim is unchanged: they do not prove
   operational independence from the host, its administrator, or its snapshot domain.
3. **Qualify the SSH-like Ratox product for daily control.** Run long interactive/reconnect soak,
   repeated Tor and I2P route-loss cells, additional production-kernel cgroup/PSI qualification, and
   an independent security/operations review before a deliberate activation ADR. ADR 0326 closes the
   first real NixOS PAM/password-prompt sudo PTY case while retaining the noninteractive branch; host-
   specific policies and alternate PAM conversations still require deployment qualification. ADR 0327
   closes the first positive NixOS Linux 6.6.94/systemd `Delegate=yes` cgroup/PSI slice across
   lifecycle, memory/pids, CPU, I/O, and pressure admission. The intended product remains an
   owner-approved login shell with privilege denied by default and explicit host-authorized sudo—not
   remote-selected exec, SSH agent forwarding, or general port forwarding.
   On 2026-09-09 the local daily-control subset was rerun against the current tree and passed for
   POSIX process control, terminal controller lifecycle, restart fencing, R7 analysis, terminal
   probing, and CLI reconnect probing. The delegated cgroup/PSI CTest entries skipped in the
   ordinary shell. ADR 0343 adds the local delegated-service helper and reruns the same process
   oracles through transient `systemd-run --user --property=Delegate=yes` services: lifecycle,
   memory/pids, CPU, and PSI pressure admission passed; I/O skipped because this qualification
   filesystem did not expose cgroup-attributed block I/O. This is useful current-host evidence, not
   a new fleet or production-activation claim. The same current tree also reran the bounded
   production-CLI repeated reconnect Sandwurm gate: compact proof `pair.h25zpony` passed direct UDP,
   compact proof `pair.sduwsbg8` passed forced TCP, both bound IoTox binary SHA-256
   `b447f6fd0445f16b3bb9acca76bc413faf12b9b779ba7d20f5c8d95a128ed6b7`, and both reverified from
   compact export. This proves the bounded mechanism still holds on current native/relay routes; it
   does not replace long soak, actual Tor/I2P continuity, daemon-death PTY supervision, or a
   production activation review. `iotox terminal activation-check` now makes that review an
   explicit fail-closed native porch: missing daily-control, profile-freshness, service-supervision,
   reconnect-continuity, cgroup-delegation, or route-loss evidence returns blocked, while fully
   labeled operator custody still keeps `repo-certified=0`. On 2026-09-17
   `./tools/ratox-daily-control-gate.sh --build`
   passed the same focused 6/6 CTest set and the delegated cgroup helper again reported
   `passes=4 skips=1 failures=0`; see
   `docs/evidence/2026-09-17-ratox-daily-control-rerun.md`.
4. **Close real-target construction evidence.** Execute the digest-pinned AArch64 rescue capsule
   through the production PTY on one named physical ABI/kernel target. Add other constrained Linux
   targets only when an actual deployment needs them.
5. **Remove measured scale bottlenecks.** Extend the new native filesystem-watch wake path into
   deeper incremental branch/build and projection work, bounded parallel object transfer, and
   route-aware auxiliary-lane scheduling;
   preserve the current exact manifests, conflict semantics, sparse custody, and frozen peer
   framing. Optimize only against retained latency, memory, disk-amplification, and catch-up data.
   A rejected direct near-ceiling diagnostic on 2026-09-03 reached graph convergence but timed out
   with followers still receiving objects and no follower projection. ADR 0329 implements the first
   response: a bounded tree-v2 exact-object lane window over the unchanged primary Tox object frames.
   The first source-linked four-lane direct retry passed the same 3,500-file population and retained
   conflict lifecycle in 1,050.374 seconds. A fresh 512-file networkless Sandwurm rerun verifies the
   default cap-4 receipt path with recovery and storage-fault follow-ups. The near-ceiling Sandwurm
   comparison is now accepted for cap 4, cap 8, and cap 16: cap 1 reached graph setup but timed out
   without an accepted receipt; cap 4 passed 3,500 files, repair, conflict convergence, and explicit
   resolution in 1,361.936 seconds; cap 8 repeated the same gate in 1,198.824 seconds; cap 16
   repeated it in 1,138.904 seconds with 1,059.715 seconds of capacity catch-up. Cap 32 then timed
   out at 1,823.048 seconds with followers still below 200 tree-v2 objects and no follower
   projection; cap 64 timed out at 1,822.462 seconds with followers receiving only the empty-file
   object. Both are retained as compact rejected evidence. The lane-width improvement is real but
   has peaked for this guest shape. ADR 0330 identifies the first local cause: each completed file
   used the general CAS importer and therefore reverified the complete existing object store.
   Complete file windows now share one bounded import, with exact late-offer retirement so cancelled
   request IDs cannot leak paused transfers. A source-linked direct cap-16 retry passed the
   3,500-file gate in 478.624 seconds, including 387.085 seconds of catch-up, with 219 batches and a
   largest batch of 16 on each follower. The exact 2-vCPU/2-GiB networkless Sandwurm repeat then
   passed in 788.317 seconds overall with 654.214 seconds of catch-up, improving on the prior cap-16
   VM result by 30.8% and 38.3% respectively. It caught 7/8 real late offers and ended with zero
   retained IDs or evictions. ADR 0331 removes the residual full inventory pass per batch without
   trusting stale state: each file-bearing pull builds one strict private CAS view, reuses it across
   batches, and re-hashes the complete in-quota store under the final branch/projection transaction.
   A clean source-linked direct cap-16 run completed the same gate in 478.979 seconds with 379.948
   seconds of catch-up; followers performed only 7 and 5 full scans across intermediate automation
   pulls instead of 219 scans implied by their 219 commit batches. This removes the measured
   amplification but leaves whole-run time effectively flat against ADR 0330's prior direct sample.
   The exact 2-vCPU/2-GiB Sandwurm repeat passed in 634.194 seconds overall with 554.077 seconds of
   catch-up, 19.5% and 15.3% below the ADR 0330 VM baseline. Its followers retained the same 219
   batches but performed only 21 and 15 aggregate full scans, ended with no staged/retired state or
   watchdog restart, and independently verify as compact proof
   `.sandwurm/exports/three-writer/run.yDPmVYg6`. The constrained guest therefore confirms a material
   contention reduction while the direct result prevents overclaiming a universal latency win.
   ADR 0341 adds the first native filesystem-watch latency shortcut: Linux inotify source changes
   wake local publish/reconcile work for `publish`, `writable`, and `bidirectional` automation
   without changing signed policy or removing the periodic fallback. ADR 0342 adds the 250 ms
   non-sliding Agent debounce, preserves source changes observed during an active publish, and skips
   the old implicit CAS refresh plus second marker-only worktree scan on unchanged stable workspaces.
   ADR 0344 adds the first volatile source-scan cache: stable selected regular files reuse digests
   only when namespace, source, projection policy, inode/device, mode, owner, link count, size,
   mtime, and ctime all match a prior verified scan, while restart/projection exchange/mismatch fall
   back to hashing. ADR 0345 then removes repeated per-path extraction inside source-scan
   reconciliation, merge summarization, multi-writer dominance checks, and ordinary projection
   selection by grouping canonical manifest paths once per phase. ADR 0346 adds directory-ancestor
   validation indexing for nested manifests. ADR 0347 indexes branch transition validation for
   carried-history authentication and dropped-value refusal. ADR 0348 groups retained-history
   `sync-diff` path comparisons. ADR 0350 then targets positive sparse source walks: selected
   ancestor directories are observed without descending unrelated siblings, and included roots are
   scanned directly while complete-interest scans keep the prior full-tree behavior. ADR 0351 skips
   empty unselected-preservation and unselected-compare walks for complete projection policy while
   retaining all baseline, visible, and old-side validation. ADR 0352 exposes content-free
   preservation counters through reconcile and `sync-publish`, so complete-policy skips and sparse
   local preservation costs can be measured directly. ADR 0354 adds matching content-free CAS
   inspection, install, byte, and reuse counters. ADR 0355 then adds selected projection and conflict
   material counters, completing the ordinary `sync-publish` view of source, CAS, projection, and
   sparse-preservation work. ADR 0356 carries the same final reconcile/apply shape into retained
   tree-v2 pull status, making transfer and local-apply bottlenecks separable during near-ceiling
   runs. ADR 0357 carries that status shape into future three-writer Sandwurm capacity receipts.
   A fresh cap-8 receipt then showed `source-reused=0` on retained final applies even after object
   transfer had converged; ADR 0358 gives subscriber completion its own volatile source digest cache
   so recurring no-op pull/apply cycles can reuse unchanged selected file digests. The first
   post-cache cap-8 VM repeat rejected at 1,825.073 seconds with followers only at 194/3,500
   capacity files, so this optimization is not yet near-ceiling throughput evidence. ADR 0359 adds
   content-free rejected-receipt pull frontier summaries for the next timeout so active job, lane,
   source, batch, and CAS state is visible at failure. A source-linked ADR 0359 cap-8 repeat then
   passed with 940.891 seconds of catch-up and proved subscriber digest reuse in the VM, but also
   showed follower full-inventory scans and late-offer churn returning to high levels.
   ADR 0353 then remeasures the current rev0051
   near-ceiling cell and adds a tree-v2-only busy-republish cooldown: pre-throttle cap 8 regressed
   to 1,084.185 seconds of capacity catch-up with 74/81 follower scans, while post-throttle cap 8
   passes in 480.819 seconds of capacity catch-up with 23/25 scans. Current cap 4 also passes in
   512.569 seconds of catch-up, and current cap 16 passes but regresses to 1,271.565 seconds with
   90/111 scans and 20/39 late-offer cancellations. A later counter-retaining cap-8 repeat passed
   with 538.809 seconds of capacity catch-up and confirmed that completed apply work was projection
   and source-hash dominated, not CAS dominated. Cap 8 remains viable and has the best accepted
   sample in this exact VM profile, but cap 4 versus cap 8 is not closed as a stable operational
   default. Complete selected projection rebuilds,
   sparse unselected-preservation walks, deeper intermediate-head/pull coalescing, tree-v2 range or
   bundle transfer and auxiliary route distribution are the next measured bottlenecks rather than
   wider lane caps. Future direct and compact Sandwurm harness failures now
   emit/verifiably retain
   content-free rejected receipts with partial capacity/store shapes so rejected science runs stay
   structured.
6. **Polish ordinary operation.** Add service-manager deployment examples, guided invite/share/
   retirement and disaster-recovery ceremonies, richer status without secret leakage, a public
   Bash/Nix script for doctor/build/test/run/sync/terminal/datacube/cleanup, and a separate inert
   MonsterNix adapter for exact source/package admission and host projection. Dynamic completion is
   acceptable only where it can remain local and authority-safe. The typed command registry and
   command-name completion are already complete. ADR 0363 freezes the public-script/Monsternix split
   so neither layer becomes a second device-authority root. This revision lands the first binary-native
   human porch: topic help, `overview [--json]`, `init plan/write-config`, guided sync
   `plan-pair`/`plan-mesh`/`start`/`share`, and terminal `doctor` plus profile planning for shell,
   sudo, and rescue profiles. The follow-up native ergonomics gate adds table-driven
   `iotox explain`, blunt `iotox readiness`, pair-card create/inspect/accept,
   support-bundle plan/create/inspect, and conflict summary/explain porches,
   plus systemd/NixOS deployment examples. ADR 0389 extends that ordinary layer
   to local messenger receive/status, sync trust planning, and terminal daily
   status without widening the proof claims. The remaining detailed backlog in
   `docs/human-ergonomics-plan.md` is now a recovery-plan shortcut, broader structured output modes,
   word fingerprints, support-service packaging polish, and richer authority-safe completion.
7. **Expand portability deliberately.** Decide whether ownership, ACLs, xattrs, timestamps,
   symlinks, case-insensitive filesystems, and non-Linux hosts deserve explicit versioned semantics.
   Refusal remains preferable to silent lossy translation.
8. **Return to physical effects only with hardware.** Additional mutable operations, boot/flash
   application of signed updates, and safety-relevant actuation wait for a named device, an
   idempotent effect contract, rollback/recovery evidence, and defense in depth at the hardware
   boundary. Mutorr/Small Circles remains intentionally dormant unless separately reactivated.

The first four are finite qualification or ceremony gates. Items five through eight are product
expansion and should be pulled forward only when measurements or a concrete deployment justify
them.

ADR 0285 also closes the immediate owner-local Ratox ergonomics slice without reopening peer
framing: canonical profile template/lint/install/show/list/remove/bind/unbind, content-free retained
session list, authenticated close, batch attachment, and live host capability inspection are now in
the binary. ADR 0290 now supplies shared `run-check`/file-backed deployment preflight. Remaining
Ratox work is additional kernel/service-manager qualification, longer soak, repeated overlay-route
loss, independent review, and an explicit production-activation decision—not an SSH compatibility
layer or remote-selected exec request. ADR 0327 closes the first named Linux/systemd delegated-cgroup
gate.

ADR 0286 closes the owner-workstation shell prerequisite. `terminal-shell-discover` now resolves and
qualifies a deterministic canonical ELF login shell; the disabled shell template freezes the
account's primary and supplementary groups plus a NixOS/conventional PATH. Privilege gain remains
false by default. `--allow-sudo` creates a distinct non-root compatibility profile only after finding
a privileged sudo helper, while reporting that sudoers/PAM policy was not probed. The native process
gate proves both `no_new_privs` branches, and the isolated `ratox-sudo-vm` flake check proves the
non-root production PTY can execute a real setuid-root sudo child and return to the non-root Ratox
identity. ADR 0326 retains that noninteractive branch and adds a password-requiring UID-1000
operator whose real NixOS PAM prompt crosses the production PTY without echo, reaches a UID-0 child,
and returns to the non-root login shell. ADR 0349 makes that password branch wait across the
sudo/PAM terminal handoff and retain useful PTY timeout diagnostics. The remote still selects no
path, argv, profile, account, or privilege bit; typed commands may be entered *inside* the
owner-approved shell, which is the intended SSH-like machine-control experience.

ADR 0327 adds the corresponding positive NixOS/systemd kernel gate for the optional delegated-cgroup
path. `ratox-cgroup-vm` runs the lifecycle, memory/pids, CPU, I/O, and PSI admission process oracles
under transient `Delegate=yes` services on Linux 6.6.94. This proves the first named service-manager
delegation slice and keeps broader deployment kernels, long soaks, overlay-route loss, and review
explicitly open.

ADR 0287 closes the bounded x86 rescue-userland slice without changing Ratox framing. ADR 0301 later
adds canonical profile v7 payload pins and the first AArch64 construction slice. The
separate `iotox-rescue-toolbox` package pins static oksh 7.9 plus Toybox 0.8.14, excludes Toybox's
pending shell, carries its own provenance/notices, and totals approximately 1.22 MiB of resolved ELF
payload on x86_64-linux. `terminal-profile-toolbox-template` emits a disabled non-root baseline
profile with the qualified toolbox first in PATH; sudo remains a separate explicit compatibility
choice. The approximately 1.22 MiB ELF payload has no dynamic or embedded Nix-store dependency.
Owned CLI checks plus the `ratox-rescue-toolbox-vm` production-PTY gate prove interactive
shell, applet resolution, identity, file/hash/list work, and clean exit with no host tools in PATH.
This is prepared fallback, not automatic failover, an initramfs, a backup, or a claim that IoTox can
survive a missing kernel, Agent, profile store, authority path, PTY, filesystem, or retained payload.

### Product-expansion program

The founding roadmap is closed, but the product is not finished. The following nine workstreams are
accepted in this order. They are product expansion above the frozen peer protocols unless a later ADR
explicitly proves that a protocol revision is necessary. Each item must retain the distinction between
implemented mechanism, bounded evidence, and deployment recommendation.

1. **Synchronization doctor and health signal.** ADR 0288 ships a read-only pre-creation inventory using the
   production content-v2, treepack-v1, and tree-v2 source rules. It reports policy transformations,
   selected entries, bytes, objects, manifest/staging estimates, configured bounds, and anything it
   did not inspect. ADR 0297 adds one content-free green/yellow/red tree-v2 namespace health record covering
   verified convergence, conflicts, repair coverage, automation stalls, store pressure, membership,
   and writer cutoffs. ADR 0315 completes the configured admission half: the exact signed automation
   source and nondefault namespace policy are joined to live immutable-store/staging occupancy,
   remaining quotas, and filesystem headroom under the existing namespace transaction. This work
   closes the first two repository mechanisms in `sync-trust-graduation.md`; it does not certify a
   backup, reserve space, or replace the long-soak and abrupt-storage gates. ADR 0318 adds the
   separately required source filesystem-contract gate: both doctor paths refuse unsupported
   link/special/ACL/xattr/sparse and ASCII-collision state and render ownership/mode/timestamp
   transformations explicitly. This is point-in-time Linux preflight, not cross-filesystem
   portability or continuous enforcement. The product's read-write
   engine now has the complete signal; older one-writer engines retain repair/status rather than
   receiving invented weak parity.
2. **Mosh-like Ratox continuity.** ADR 0289 implements the first bounded owner-local reconnect mode: it preserves one local
   terminal invocation across carrier loss, waits for a strictly higher authenticated online epoch,
   and resumes only the exact retained session/incarnation/profile. Server-side PTY survival remains
   the existing truth; stale-epoch attach, silent new-shell creation, and cross-principal migration
   remain forbidden. ADR 0300 closes the first genuine-route operator gate: one actual production
   CLI process crosses seeded total loss over direct UDP and forced TCP, retains PID/start-time and
   exact PTY identity, then resumes generation 1-to-2 without a replacement shell. Durable
   supervision across Agent or host restart is a later, separately threat-modeled tier. ADR 0316
   extends that exact production process through two sequential losses on both carriers: the same
   shell advances generation 1-to-2-to-3 with exact terminal progress between faults. Long-duration
   soak, overlay-route cells, and deployment qualification remain.
3. **Deployable Agent configuration and preflight.** ADR 0290 implements `run-check`, one strict
   owner-only canonical argument record, `config-lint`, and `run --config` with exact-option CLI
   replacement. The check and live paths share parsing, derived-path normalization, provider/path/
   policy/profile/route/cgroup preflight, while the check creates no listener, identity, PTY, cgroup,
   lock, or durable state. Recovery-capable authority/command/incarnation opens and final kernel-child
   confinement remain explicitly deferred to `run`; success means ready for start, not started.
4. **Content-free flight recorder and evidence bundle.** ADR 0291 implements the authenticated,
   crash-atomic 16..256-record tail, closed state/counter grammar, path/key/endpoint-free structural
   commitment, local-control export, no-clobber private bundle, and offline inspect-before-share
   step. The shareable bundle deliberately drops device identity/signature and is integrity-framed,
   not remote attestation. ADR 0298 joins ADR 0297 health as anonymous verified/absent/invalid,
   green/yellow/red, custody, conflict, repair, pressure, automation, and source aggregates without
   namespace handles. ADR 0299 then adds normalized passive pidfd, seccomp, MDWE, Landlock, sudo,
   privilege-prerequisite, and cgroup capability grades/masks without paths or raw kernel text.
   Arbitrary logs/config remain forbidden inputs.
5. **Human peer names and explicit invitations.** ADR 0292 implements the alias half: one-to-one
   stable-device-signed owner-local mappings, fixed `friend:`/`key:`/`alias:` escapes and bare
   precedence, consistent main/terminal CLI resolution, collision refusal, atomic rename, explicit
   idempotent removal, and retention across peer deletion. Aliases bind Tox keys and grant nothing.
   ADR 0293 completes the invitation half with one fixed stable-device-signed address/expiry/nonce/
   alias/requested-capability artifact, untrusted inspect, pinned nonmutating import, and explicit
   replay-safe accept. Acceptance may create friendship and an exact alias but always grants zero
   authority; requested capabilities remain reviewable intent.
6. **Synchronization time machine.** ADR 0294 implements retained signed-revision inventory,
   provenance-aware canonical diffs, current/historical conflict inspection, existing signed pins,
   and an exact optimistic-concurrency restore plan. Restoration re-authors the selected conflict-free
   projection at the next local generation against the exact current frontier; it never moves a
   branch backward. History remains bounded operational recovery material, never an independent
   backup or rollback witness.
7. **Sparse and on-demand synchronization.** ADRs 0295--0297 implement the custody, source, and
   durable-health vertical slices. A
   subscriber declares recipient-local canonical path-prefix interest, retains the complete signed
   metadata graph, fetches only selected immutable file objects, and reports complete versus partial
   custody in pull status, repair, GC, conflicts, and worktree projection. Policy-bound projection
   markers make narrowing/widening safe across restart, and widening plus an ordinary pull is the
   on-demand fetch path. Authenticated primary-lane sources now satisfy one primary's frozen frontier
   through the existing exact offered/absent/unavailable result, without new peer frames or branch
   authority. The signed health record distinguishes verified selected custody, expected sparse
   omission, and exhausted sources across restart. Remote globs and remote-selected destination
   paths remain out of scope. Range/auxiliary and parallel tree transfer are optional performance
   follow-ups, not unfinished correctness gates.
8. **Protected local state and rollback witness.** ADR 0302 freezes the deployable boundary and ADR
   0303 implements its first deployable tier: an externally unlocked fscrypt-v2 root must contain the complete configured
   security-bearing state closure and runtime must be tmpfs or equivalently protected. IoTox accepts
   no secret through argv, environment, config, or a peer and starts no network/effect surface until
   the public policy-ID pin, key presence, mount identity, every derived companion, and every configured state root
   pass descriptor-safe verification. The Agent now enforces that closure before even its runtime
   tree, and a retained ext4-fscrypt VM covers correct/wrong/re-added keys, raw-media secrecy, and
   adversarial path/mount shapes. A separately controlled authenticated monotonic witness coordinator
   now pilots the authority lane with durable exact signed intent plus pending/committed compare-and-
   swap and deterministic lost-reply recovery. ADR 0305 adds a production-capable authenticated
   remote service with dedicated pinned identity, explicit device-signed no-replace enrollment,
   signed crash-atomic store, bounded fixed records, and fail-closed Agent integration before runtime.
   A retained two-guest gate advances real authority, rejects complete local rollback while the
   service remains current, and crosses outage/restart/wrong-key recovery. ADR 0306 adds separately
   enrolled application and Ratox incarnation lanes: every opted-in startup commits one exact next
   signed namespace before runtime, and older valid records refuse independently. The two-guest gate
   restores old application and Ratox records separately while their service lanes stay current.
   ADR 0307 adds exact signed route-generation witnessing and refuses a complete artifact/checkpoint
   rollback plus skipped history; the retained gate advances one reviewed route generation and then
   restores the old pair. ADR 0308 adds explicit complete Ratox profile/binding-tree commits and
   refuses restoration of an old sudo-capable profile plus its matching signed checkpoint before
   runtime. ADR 0309 commits the exact signed mutable-command `STARTED` frontier before provider or
   update effects, retains effect identities against selective journal rollback, and refuses when
   the authenticated service cannot resolve the transition. ADR 0310 commits the complete canonical
   namespace and stable-device-signed automation policy tree, freezes that exact snapshot before
   runtime, automatically witnesses Agent-mediated changes before live activation, and refuses a
   coordinated old-tree plus old-checkpoint restore. ADR 0311 binds the exact canonical update
   policy plus absent-or-complete signed lifecycle state, carries the exact successor in a signed
   intent, and makes the selected-slot pointer a repairable effect after external commit. Stage,
   apply, health admission, confirmation, and rollback now advance one exact lane generation and a
   complete old state or policy substitution refuses before RuntimeTree. ADR 0312 adds one
   namespace-derived lane per non-tree-v2 namespace and externally anchors the exact signed
   published, accepted, activated, and retained roots. It requires the witnessed complete policy
   tree, serializes every covered read and mutation under the namespace transaction, and refuses a
   coordinated old four-root/guard restore while the service record remains current. ADR 0313 adds
   a bounded service-signed checkpoint over the complete selector population and lets a separately
   retained artifact enforce a restart floor before the listener binds. ADR 0314 gives each tree-v2
   namespace its own derived lane over the signed live branch frontier, workspace exchange state,
   and maintenance pins/cutoffs; all root-derived Agent reads and effects are transaction-fenced,
   and a complete old tree-state restore refuses before RuntimeTree. Operationally independent
   deployment and retention of that checkpoint, rollback-resistant hardware/service persistence,
   replacement/re-anchor ceremonies, broader namespace journals/object/quarantine/projection/
   current-pointer freshness, and the exhaustive crash/rollback campaign remain follow-on
   implementation and external qualification work. Encryption without a witness does not stop
   replay of an older valid ciphertext; a same-disk witness is only a test double.
9. **Multi-architecture rescue capsules.** ADR 0301 reproduces static oksh 7.9 and Toybox 0.8.14 for
   AArch64, emits and validates complete SPDX 2.3 records, executes both payloads under qemu-user, and
   adds canonical profile v7 SHA-256 pins that are rechecked on the exact descriptor immediately
   before spawn. An x86-kernel binfmt VM executes and discovers the AArch64 payload but intentionally
   records the descriptor-only `fexecve`/binfmt incompatibility; the security boundary is not weakened
   to make emulation pass. ADR 0304 now boots AArch64 Linux 6.6.94 under QEMU system emulation and
   passes the unchanged digest-pinned production PTY qualifier as UID 1000. The remaining acceptance
   gate is one named real-target ABI/kernel qualification. Later constrained Linux targets remain
   optional. A capsule is never automatic execution, an initramfs, or a replacement for the
   Agent/kernel/filesystem.

The first vertical sequence is workstreams 1--3 because they make later operation measurable and
deployable. Workstream 4 now makes sparse Agent faults exportable without copying content; its
health grammar is closed by ADR 0297, its privacy-preserving export join by ADR 0298, and the
normalized host-capability appendix by ADR 0299.

ADR 0317 also closes the accepted command-discovery follow-up above these workstreams: one typed
registry now drives terminal/admin/control classification, an exhaustive help index,
canonical alias edges, and deterministic Bash/Zsh/Fish command-name completion. Dynamic state and
positional argument guessing remain deliberately absent. ADR 0319 adds its recovery verifier through
that same registry, ADR 0360 adds witness checkpoint custody, and the second native ergonomics gate
brings the current population to 210.
ADR 0363 adds the accepted public page and script-boundary direction: one publishable human entrance,
one Bash/Nix repository helper for ordinary operators, and one separate MonsterNix adapter for exact
source/package/proof admission and host-specific service projection. ADR 0365 adds the first
retained protected-state evidence wrapper to that helper; ADR 0366 adds the retained sync recovery
drill helper and local requirement flags. These deliberately add no new device protocol, signer,
route, terminal privilege, or backup claim.
Workstreams 5--6
are implemented; workstream 7 now closes safe sparse custody, exact-probe complementary sources, and
   durable tree-v2 health without another projection or framing shortcut. Workstream 8 now ships
   fail-closed fscrypt-v2 closure enforcement, the authority-lane witness coordinator, and its first
   authenticated remote-service backend, plus application/Ratox startup-incarnation, signed
   route-generation, complete terminal-policy, mutable-command effect, complete sync-policy,
   update-lifecycle, per-namespace four-root, and tree-v2 semantic-state lanes, plus an enforceable
   complete-store service checkpoint floor. Independent deployment/checkpoint-retention
   qualification, hardware-monotonic
   persistence, witness replacement/re-anchor, broader namespace-state freshness,
   and the exhaustive rollback campaign remain. Workstream
9 has reproducible AArch64 bytes, validated metadata, payload pins, qemu-user execution, retained
negative binfmt evidence, and a positive AArch64-kernel production-PTY system gate; one named real
target remains. These workstreams harden
and widen deployments without weakening the default local authority model.

The foundation milestones M1, M2, M3, M4, and M5 are complete. M3 has accepted direct-UDP, forced-TCP,
stream-scaling, carrier-interference, relay-restart, daemon-replacement, forced-TCP link-loss, seeded
partial-loss, persisted-disk guest-restart, and live mixed-provider evidence. Exact 0.2.22 savedata
survives 0.2.23 fixture and real-product load/rewrite in both directions, while simultaneous
Sandwurm guests exchange bilaterally with old client/current device over direct UDP and forced TCP.
M5A has a
complete default-off local/Agent Ratox construction boundary and accepted 40-sample direct-UDP and
forced-TCP idle keypress-to-render cells. Its bounded route-impairment matrix now adds 120-sample
direct-UDP, forced-TCP, and strict generic-SOCKS cells: one unchanged authenticated terminal session
crosses baseline, seeded 75 ms +/- 15 ms delay plus 2% loss, and exact recovery while heartbeat and
PTY output are measured separately. All cells recover without session mutation; direct UDP exposes
the lowest impaired median and one 2.158-second loss tail, while Agent queue/render work remains
small. ADR 0196 therefore keeps partial impairment warning-only. ADR 0197 now closes the corresponding
100%-loss gate on direct UDP, forced TCP, and strict generic SOCKS: a roughly two-second heartbeat
miss leaves the confirmed session untouched, authoritative offline arrives at 30–31 seconds and
detaches the controller with typed `unavailable`, the device retains the exact live PTY, and explicit
resume after a higher authenticated epoch preserves session/incarnation/byte positions while moving
generation one-to-two. Automatic cross-route migration remains unqualified. The upstream provider
passed the direct-UDP 1/8/16/32/64 construction ladder. The named `iotox-file-rr1-tcp-connect120`
provider retains the scheduler repair and adds bounded slow-overlay TCP establishment; it repaired
forced-TCP sender starvation,
passes direct UDP through the ordinary 32-stream limit, and passes forced TCP through 16. Its direct
UDP 64-stream opt-in and one-route forced-TCP 32-stream cell do not advance every lane inside their
construction bounds. Four independent forced-TCP routes now pass 32 aggregate streams twice, while
40 is not repeatable and 48/56/64 violate terminal or lifecycle bounds. Bounded savedata-preserving
route restarts now recover a deliberately replaced auxiliary route before the 32-stream gate while
refusing partial-route degradation. Live lane-loss science proved exact eight-transfer purge,
no reassignment, and same-identity empty-state recovery, but a repeated shared-route cell exposed
intermittent Ratox starvation. The protected-route 24-stream gate now passes with CPU isolation and
explicit worker fencing; authenticated route inventory now precedes reassignment and the
1,000-sample matrix. The first 1,000-sample idle attempt exposed the 128-control replay lifetime;
ADR 0154 replaces per-output-ACK retention with one attachment-local cumulative fence, and the
corrected direct-UDP construction run completes and closes. A clean idle rerun then localized its
83.115 ms p95 render tail outside the sub-millisecond owner queue. Diagnostic isolation found an
independent 20 ms Agent service sleep after toxcore iteration; ADR 0156 now applies 5 ms transport and
service caps only while Ratox state is live, wakes local terminal work, restores idle cadence, and
captures process-resource intervals for both roles. Exact-commit direct-UDP idle now passes at
23.943 ms p95; forced-TCP idle completes at 99.010 ms p95 and is treated as a distinct route class.
The first direct-UDP `bulk-1` rerun reached 599 exact renders before exposing a cycle between required
file-event backpressure and Ratox service on the event consumer. ADR 0157 gives Ratox an independent
cadence worker without weakening bounded required delivery or the sole toxcore owner. The exact retry
then completed all 1,000 samples and closed, but p95 71.698 ms and owner p99 7.114 ms miss the direct
budgets. The ADR 0158 coalescing experiment reduced owner work but exposed a more severe shared-carrier
head-of-line failure: p95 became 505.064 ms and 991/1,000 samples reached 250 ms. ADR 0159 restores
required per-chunk bookkeeping until explicit pacing exists, while retaining the pinned receive
descriptor and exact backpressure diagnostics. Remaining load cells, canonical balanced co-signing,
and full two-guest terminal qualification were still incomplete at that boundary. ADR 0160 then
implemented a 64/16-event, 5 ms high/low-water pacer while preserving the 1,024-entry semantic
reserve and required-event fail-safe. Its exact first qualification passes direct-UDP `bulk-1` at render p95
42.727 ms and owner p99 1.499 ms with zero required waits or pacing failures; forced TCP also passes
the route-independent owner gate. The first direct-UDP `bulk-8` attempt completed all 1,000 terminal
samples but exposed an active-only harness assertion after pacing. ADR 0161 now proves exact
`present = active + paused` workload state. Its clean v6 rerun is a valid performance failure:
owner p99 0.420 ms and event high-water 134/138 pass, while render p95 144.120 ms and one 250 ms miss
do not. Multi-transfer pacing fairness/shared-carrier burst science now precedes acceptance of this
load point. ADR 0162 implements oldest-paused-first, one-resume-per-iteration default scheduling with
strict batch telemetry. Its activated exact A/B improves p95/p99/max to
124.811/161.242/188.401 ms and removes 250 ms misses without meeting the 50 ms p95 target. A second
valid run never reaches the event trigger and stalls at about 5% CPU with p95 504.428 ms, proving
that reactive queue-watermark pacing alone cannot govern the shared carrier. ADRs 0163 and 0164 now
admit and rotate one runnable incoming file per peer with explicit pause ownership. The exact
1,000-sample direct-UDP and forced-TCP rows pass at 8, 16, and 32 transfers; both 64-transfer rows
complete lifecycle but fail latency in distinct low-utilization and high-pressure modes. ADR 0165
therefore freezes 32 as the single-Agent ceiling, and ADR 0166 retains excess exact sync offers
outside accepted transfer state for bounded fair retry. The local two-guest Ratox qualification and
route-fault campaign are complete. Multi-route immutable-object reassignment now passes both the
deterministic two-worker Agent gate and genuine two-guest direct-UDP/forced-TCP loss. Each accepted
cell stops one bulk carrier only after positive object progress, records one loss and one
reassignment, rejects two stale terminals, converges through the other bulk route, restores the
stopped savedata identity within its one-restart budget, and completes 40 protected Ratox samples
below 250 ms. Gate 3 is closed. Gate 4's first genuine fixed/adaptive topology A/B now also passes
on both native carriers: fixed reuses one eligible route for two overlapping jobs, while adaptive
places the later job on the idle route; four revisions activate and protected Ratox remains below
250 ms. Fixed-first and adaptive-first cells now pass on both native carriers. This qualifies
placement without policy phase-order bias, not performance. The next Gate 4 row also closes bounded
single-pull cancellation tails on an exact auxiliary worker: direct UDP reaches quiescence in 70 ms
and forced TCP in 80 ms with work two-to-zero, no reassignment, and protected Ratox afterward (ADR
0172). An eight-job population row now fills the complete signed work budget on both bulk routes:
fixed produces `00001111`, adaptive produces `01010101`, every job progresses and activates, phase
resource intervals remain bounded, and protected Ratox passes afterward over direct UDP and forced
TCP (ADR 0173). This closes bounded population fairness/resource observation, not larger-object
throughput. Eight-job/four-withdrawal concurrent cancellation now also passes both carriers with
balanced route selection, four survivor activations, zero reassignment/work, a bounded resource
interval, and protected Ratox (ADR 0174). The repeated 1 MiB/job UDP `OPENED` miss separates shared
physical-queue QoS from logical route protection. ADR 0241 now closes its controlled positive
companion on both carriers: the same 1 MiB/job load and 4 Mbit shared edge pass balanced
cancellation, four survivor activations, zero work/reassignment, and protected Ratox when the live
edge is HTB/`fq_codel`; exact qdisc structure and counters are manifest-bound. This qualifies one
flow-aware queue mechanism, not strict priority or a universal default. One ordered fault
combination now also passes:
loss after artifact progress, reassignment and replacement progress, cancellation without a second
reassignment, then bounded recovery of the stopped identity (ADR 0175). Both exact corresponding
auxiliary readiness orders now pass over direct UDP and forced TCP: each named identity is the sole
ready route for ten samples before both routes return, the signed tree converges, and protected Ratox
passes (ADR 0176). ADR 0177 also closes the opposite deterministic cancellation→loss order with
zero reassignment and one bounded route recovery on both carriers. ADR 0178 closes one shared-arm
cancellation/loss collision on each carrier: both linearize as cancel-first, expose typed transport
cleanup unavailability, settle through one exact retry, avoid reassignment, and recover the route
without reviving the pull. ADR 0179 makes fault lead from that same armed state without polling for
reassignment; both carriers perform exactly one fresh assignment, cancel the replacement on the
first request, and recover capacity. Both shared-arm authority outcomes are now genuine. Random
startup/fault delay distributions and startup during faults remain open. ADR 0180 now closes one
deterministic multi-job same-carrier row: eight fixed-policy jobs fill both routes, one four-job
carrier is stopped after positive progress, all four affected jobs move as complete remaining work
sets, stale truth is fenced, every revision activates, the identity recovers once, and protected
Ratox passes on direct UDP and forced TCP. The campaign also repairs transient publisher-capacity
skew and separates auxiliary carrier service from required-event draining. ADR 0181 then proves
two genuinely new jobs can enter through the sole survivor after loss. ADR 0182 proves two live
16 MiB jobs can enter through one ready route after a clean Agent restart and stay there when the
held route joins. Randomized startup/fault timing, larger-object throughput distributions, strict
traffic-class priority/reservation, and relay diversity are next.
M5B now has a
default-off authorized Agent publisher/subscriber path, durable object attempts, bounded off-callback
work, typed `sync-namespaces`/`sync-pull`/`sync-status` controls, real range-v1 local publication, and
exact-token manual activation. Its full mock-provider gate commits two immutable objects and the
accepted signed HEAD last without implicit activation, then activates only after the artifact and
index are reverified together. Genuine two-IoTox Sandwurm guests now converge and explicitly activate
the same 4 MiB revision over direct UDP and forced TCP. They also recover an interrupted 8 MiB
revision after an unclean receiver-daemon restart on both carriers. That gate exposed and repaired
pre-rename transport-temporary leakage: startup now validates and removes only the exact
signed-attempt-scoped private file before journal clearance and exact-revision retry. Explicit
process-local pull cancellation now also passes after positive provider progress on both carriers.
Authenticated-epoch retirement after bilateral TAP blackhole now passes on both carriers: the old
job and staging are terminally cleared, both peers advance and stabilize, and only an explicit fresh
whole-object pull may converge and activate. A separate genuine-provider gate pauses one live
receive without changing its job, FileId, epoch, staging, or authority identity, proves a stable
positive partial position, resumes that same transfer, and converges on both carriers. Same-process
cross-carrier whole-object continuation now also passes direct UDP and forced TCP: two concurrent
positive prefixes survive one auxiliary carrier loss, move only into fresh authenticated attempts,
receive only their suffixes, and converge with exact retained/resumed byte equality and zero
fallback (`evidence/2026-08-28-sandwurm-sync-byte-resume.md`). A real client-Tor process-loss cell
also retains/resumes two positive prefixes and 102,825 bytes exactly through its native survivor,
with zero IoTox worker restart, before recovering the same Tor member
(`evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md`). A
persisted-disk publisher-guest-restart cell now also passes on both carriers: the stable subscriber
terminally clears its old job and staging, the successor guest retains the exact publisher identity,
policy, immutable objects, and signed HEAD, and only an explicit pull after 50 stable samples of a
higher authenticated epoch may converge and activate. Live namespace
update/removal now provides
quiescence-gated membership and activation replacement plus policy-only retirement through local
control v1.29; root, engine, and quotas remain immutable. The negotiated range extension now has both
a complete deterministic Agent gate and genuine direct-UDP/forced-TCP provider evidence: the latter
fetches one 128-byte range, reuses 4,194,176 verified bytes, commits the exact 4 MiB generation-2
artifact, accepts its HEAD last, and activates only that exact token. The missing/corrupt accepted-
basis fallback now passes deterministic tests and genuine direct-UDP/forced-TCP Sandwurm cells: it
requests the complete successor, verifies it, accepts HEAD last, activates explicitly, and leaves the
unusable prior object untouched. The original partial-range fault baseline passes deterministic and
genuine direct-UDP/forced-TCP gates: one incomplete attempt is fully discarded and fenced before the
unchanged plan receives fresh durable and transport identities. ADR 0230 now qualifies the optimized
path on both carriers: the initial receive owns an exact private inode from byte zero, the old signed
attempt finishes and fences, a fresh attempt/FileId inherits the strict prefix, and the replacement
seeks to it before suffix-only completion. Explicit corrupt target-object repair now also
passes genuine direct-UDP and forced-TCP gates: the exact mismatch is quarantined, signed state is
unchanged, the same authorized revision is restored, and the quarantine evidence survives a clean
rescan. Signed `treepack-v1` directory publication, bounded canonical packing, post-commit atomic
materialization, abandoned-staging recovery, current-only derived projection, and exact retry now pass
deterministic tests plus genuine direct-UDP/forced-TCP two-guest gates. Canonical abandoned pointer
recovery and an eight-boundary separate-process `_exit` matrix now prove complete old-or-new visibility
and fresh-process convergence. A three-generation genuine-provider gate now also refuses stale
rollback and a distinct valid equal-generation fork on direct UDP and forced TCP while preserving
the accepted HEAD, activation record, and visible generation-2 tree. The same cells use a dedicated
64 MiB ext4 namespace to commit generation-3 activation under real ENOSPC, preserve the old visible
tree, and materialize generation 3 by exact duplicate retry after removing only the filler. A separate
queue-of-one gate now holds a real publisher transaction, fills active and queued work, refuses one
additional namespace job, preserves the toxcore event pump, and converges both retained namespaces by
exact retry over both carriers. A whole-store byte-quota cell now starts from 4,981,169 retained
bytes under a 5,242,880-byte subscriber ceiling, refuses a valid successor whose artifact and
manifest each exceed the exact remainder, cleans staging, and preserves signed/visible generation-1
truth on both carriers. A separate cell reaches a six-object ceiling with four valid filler objects
plus the accepted artifact/manifest while retaining enough bytes for the complete successor, then
refuses either candidate object without state change on both carriers. A dedicated loop-backed ext4
cell now also refuses pull before object requests and refuses activation without changing signed or
visible truth while read-only, then completes each exact retry after a read-write remount over both
carriers. A maximum-entry successor now also binds publisher/subscriber process-lifetime `VmHWM`
through publication, transfer, and activation on both carriers, peaking at 13,132 KiB under a 65,536
KiB construction ceiling. Publisher-source corruption now also fails before offer on both carriers,
quarantines both bad objects explicitly, reconstructs the same signed generation through duplicate
publication, and converges only after explicit retry. Subscriber-destination corruption now also
fails at complete staged digest verification on both carriers, preserves a valid sibling manifest,
and selectively retries only the missing artifact before HEAD-last acceptance and explicit
activation. The final bounded single-source control cell now replays both object requests after their
offers are admitted, replays the HEAD after both object results, and injects one same-ID/different-
payload conflict. Both carriers return retained controls without repeated offers or request cascades,
refuse the conflict, and converge through the original attempts. Genuine complementary-source
content-v2 now passes direct UDP (ADR 0255); forced TCP remains an explicit gate after thirteen
bounded relay/admission/rendezvous cells. The strongest hybrid confirms the secondary only
transiently and loses it before v3 authority or object work.
ADR 0256 qualifies fail-closed selected-source loss plus distinct-job recovery, and ADR 0257 removes
its last construction-only seam: the partial source now cold-starts from a foreign-writer,
device-custodied availability record while local publication stays absent and replica GC remains
consistent.
ADR 0258 then separates primary writer/HEAD authority from exact auxiliary carriage. ADR 0259
accepts the genuine mixed-route multi-source gate: two native authority sessions contribute
complementary objects through distinct actual-Tor worker identities in one atomic pull, with exact
per-source carrier commitments and zero unexpected-context packets. ADR 0260 closes its first
destructive boundary: selected-worker loss after positive progress fails the whole job with no
downgrade or reassignment, recovers only the exact signed route under a fresh incarnation, preserves
both native epochs, and converges only through a distinct explicit pull. ADR 0261 repeats that exact
gate through a second compiled public relay record with new worker, job, circuit, stream, and packet
capture identities. It reduces single-relay accident risk but does not qualify exit/operator,
time-window, independent-bottleneck, or long-running diversity. Multi-source remains an
evidence-driven optimization rather than an M5 integration prerequisite.
M5B's first collector slice is now complete without purge: local-control v1.32 exposes
`sync-gc NAMESPACE dry-run|quarantine`, authenticates the complete guarded live-root set, freezes a
descriptor-pinned inventory, and moves only exact unreachable identities by contained no-replace
rename. Deterministic tests cover links, root/inode substitution, cancellation, and post-rename fsync
failure. A genuine two-guest Sandwurm cell additionally refuses real bind mounts, preserves four
outside-root sentinels, moves one exact 32 KiB inode per role, and observes an empty retry (ADR 0149
and `evidence/2026-08-24-sandwurm-sync-gc-quarantine.md`). Purge remains absent pending an independent
monotonic witness or separately accepted operator-risk policy.
M5C's tree-v2 collector now follows the same no-purge discipline with multi-branch semantics.
ADR 0275 adds negotiated conflict-free checkpoint floors, explicit exact-record pins, signed
workspace roots, recoverable quarantine/restore, and terminal per-writer cutoffs. Quiet convergence
no longer emits acknowledgement-only branches. The native three-daemon lifecycle passes checkpoint
propagation, pin/unpin, exact ancestor quarantine and authenticated restore, two-survivor cutoff, and
retired-writer re-entry refusal. The accelerated networkless Sandwurm and long/adversarial
qualifications remain distinct evidence gates. The accelerated 24-cycle Sandwurm/KVM lifecycle now
passes end to end, including remote checkpoint copies, pin/unpin, two-object quarantine/restore,
two-survivor cutoff, and refused retired-writer re-entry
(`evidence/2026-09-01-sandwurm-sync-three-writer-lifecycle.md`). A preceding constrained cell exposed
one intermittent pending worktree exchange; bounded watchdog/restart recovery is now wired into the
VM harness. ADRs 0280--0281 close the finite adversarial/scale matrix, and ADR 0283 accepts the
two-hour incumbent shadow after the replay-window defect it exposed was repaired by ADR 0282.
The earlier one-writer automation gap is now closed independently of tree-v2. ADR 0276 adds a
first-class two-guest `sync-automation` route: owner setup installs policy once, the publisher and
replica Agents restart independently, and three exact source-only generations automatically publish,
pull, accept, and verified-activate over direct UDP and forced TCP. Both compact proofs bind one
restart and signed-policy reload per role plus zero manual publish/pull/activate commands after setup
(`evidence/2026-09-01-sandwurm-sync-automation.md`).
Canonical namespace template/lint
and atomic live
installation/update/removal now remove the out-of-band policy administration requirement. ADR 0277
retires M0's hosted-CI observation from repository scope. M6's presentation-state slice is complete
for the supported founding-machine boundary; representative hardware is explicitly unsupported. M7 now
has a qualified authority-gated remote staging path into its default-off inert-slot lifecycle and a
policy-v2 release-signer revocation denial for future staging. No-clobber release-key creation,
reviewable overlap/retirement epochs, and bounded recoverable slot quarantine now close the local
release-operations gate without adding purge. Physical boot/flash targets remain unsupported. M8 now
has strict local construction, two-guest generic-SOCKS
containment, authority-private mixed native/generic-SOCKS membership, one bounded operator-owned
Tor/public-relay route gate, and two-peer actual-Tor readiness plus payload-carrier evidence. The
single-agent actual-Tor gate binds
configured-target success from new Agent source ports to two three-hop linked-Conflux circuits
across proxy restart with no IoTox UDP/direct fallback; it is one host, relay, Tor build, and time
sample. Separate compact proofs now bind two exact Tor members to distinct three-hop circuits, bind
a complete signed tree job to the exact Tor member with zero reassignment, and externally kill that
Tor process after positive progress before exact loss, native reassignment, and real carrier return
without an IoTox worker restart. These remain one-host bounded route claims, not anonymity. The
content corpus now also includes one two-publisher actual-Tor result: both authority sessions remain
native while distinct worker identities carry complementary objects before one verified activation
(ADR 0259). The device-side workers share one Tor process, so this adds source/carrier mechanism
evidence rather than per-source circuit or physical-path diversity. The
generic-SOCKS Ratox impairment and total-loss cells do not widen them. Accepted compact proof
`pair.2waqdpgk` now closes the bounded actual-Tor Ratox process-loss cell: a real client Tor
`SIGKILL` produces heartbeat warning before authoritative offline, the device retains one detached
live PTY, and explicit higher-epoch resume preserves the exact session/incarnation while generation
and byte sequences advance from 1 to 2. Three authenticated Tor phases, zero IoTox daemon restarts,
and TCP-only guest TAP containment independently reverify (ADR 0206).

M8's stewardship surface is now locally complete: ADR 0240 exports an inert-by-default NixOS module
for the pinned bootstrap/TCP-relay daemon, requires an explicit reviewed package, keeps the firewall
closed unless requested, confines persistent identity under a dynamic system user, and applies
memory/CPU/task ceilings. Its NixOS/KVM test proves both fixed-port listeners, exact identity
retention across restart, resource settings, and explicit firewall rules. The operator runbook
freezes backup/rotation, publication, observability, update, decommissioning, authority separation,
and public-operation nonclaims without creating an IoTox service or catalog.

ADR 0207's duration/circuit-churn cell is now accepted as compact proof `pair.k8o54n2v`. One Ratox
session completed 120 paced heartbeat/PTTY samples while authenticated control closed the exact
client and device Tor application circuits. The client stream reattached on a distinct circuit with
same-epoch/generation continuity after 123.813 ms; the device stream reopened, reached authoritative
loss, and explicitly resumed the same session/incarnation/PTY at a higher epoch and generation after
30.220 seconds. The v3 verifier joins authenticated before/after inventories, raw requested-close
ordering, Conflux same-stream close attribution, exact byte sequences, unchanged Tor/IoTox/guest
processes, and TCP-only TAP containment. A rejected pre-mutation run through a stale public record
still keeps relay freshness and public-relay reliability separate from churn semantics. The next M8
step has begun: ADR 0208 repeats the unchanged cell through a second public record as accepted
compact proof `pair.9cx0jels`. Both Tor streams reopen but both Ratox checkpoints remain
same-epoch/generation continuous, confirming that a Tor transition label cannot drive application
state. ADR 0209 is now live-qualified as compact proof `pair.vx6z0csh`: a reachable interposer and a
fresh successful target CONNECT coexist with withheld established bytes, a 2.578-second Ratox
warning, 27.241-second authoritative offline transition, detached PTY retention, and exact
higher-epoch resume without any Tor/interposer/IoTox restart. ADR 0210 now strictly accounts the
eight compact proofs as 30 target-circuit declarations resolving to 24 normalized three-hop paths,
20 first hops, and 23 last hops with no cross-proof complete-path or last-hop reuse. That closes
content-free corpus accounting, not reviewed exit/operator or independently separated time-window
diversity; ADR 0243 contributes the later operator-window repetition while preserving that strict
nonclaim. ADR 0211 closes I2P's strict SAM-adapter prerequisite; ADR 0212 closes a bounded
two-live-router actual-I2P STREAM seam and exposes an i2pd 2.60.0 queued-accept defect. ADRs
0213–0215 close the persistent service, slow establishment, and same-host three-front
Tox/application E2E edges. ADR 0216 accepts the two-guest Sandwurm containment baseline, and ADR
0217 now accepts exact client-router loss, listener-positive/SAM-negative separation, bilateral
authoritative offline, preserved-state router replacement, higher-epoch text recovery, and continued
no-fallback containment as compact proof `pair.v_11i2me`.
ADR 0218 adds exact Linux router-socket ownership and accepts three-front replacement over unchanged
Destination keys with bilateral higher-epoch recovery as compact proof `pair.6rrdsdc_`. ADR 0219
accepts compact proof `pair.5xjf2n4d`: private route-binding v2 admits the exact actual-I2P member,
one 131,369-byte signed tree is assigned to it and activated with zero reassignment while native
fallback stays ready. Rejected 512 KiB and 4 MiB attempts selected I2P before authoritative carrier
loss moved complete remaining work to native despite stable routers/fronts. This closes one bounded
member-bound payload, exposes whole-object failover as a privacy-policy boundary, and makes
digest-bound auxiliary chunk/range plus signed route-class constraints the next protocol gate.
ADR 0225 now closes the signed-class implementation prerequisite with route-set v2: each member key
is bound to native, Tor, or construction-I2P, and primary startup, worker construction, coordinator
authentication, CLI authoring, and private digest binding fail closed on disagreement. Accepted
compact proof `pair.q2pka1fm` closes the genuine positive path: both guests observe all signed
classes and one fail-closed 131,369-byte tree converges through the exact actual-I2P member with
native ready and zero reassignment. ADR 0226 and compact proof `pair.jbr89_gc` now close the
destructive companion: router loss after 69,921 bytes blocks the pinned job without native
reassignment, the same member recovers under a distinct router process with zero worker restart,
and only an explicit fresh job completes (`evidence/2026-08-28-sandwurm-fail-closed-i2p-loss.md`).
ADR 0227 and compact proof `pair.ej_4507n` then close the positive auxiliary-range gate without new
wire framing: both sessions negotiate the existing range-v1 feature, a native 4 MiB basis is followed
by a class-pinned I2P successor, 4,194,176 verified bytes are reused, and only the changed 128-byte
artifact range crosses the exact I2P member with zero reassignment. ADR 0228 and compact proof
`pair.a9zwongf` now close the bounded live-range loss/fresh-recovery edge: the router stops after
86,373 bytes of a concrete 1 MiB bundle; IoTox removes the partial, blocks the fail-closed job, and
makes zero reassignment; the same signed member recovers once with zero worker restart; and explicit
cancellation plus a distinct job refetches that 1 MiB, reuses the verified remaining 3 MiB, and
activates the exact 4 MiB target. Same-handle and I2P carrier-loss/explicit-fresh-job prefix resume
remain open
(`evidence/2026-08-29-sandwurm-actual-i2p-range-loss.md`).
ADR 0229 and compact proof `pair.ip5q0at9` then remove the redundant fresh-job manifest transfer:
the exact 786,496-byte durable manifest is locally reverified, corruption fails without a request,
and the qualified recovery emits one 1 MiB range request while committing both immutable objects.
This reduces that phase's transported object bytes from 1,835,072 to 1,048,576 without retaining the
failed 71,292-byte range prefix or changing signed/wire semantics.
ADR 0230 and compact proofs `pair.cj5y5vgt`/`pair.qeb99i4o` close a separate ordinary-retry edge:
one same-process, same-job, same-carrier range retry retains/resumes 15,081 UDP or 24,678 TCP bytes
under fresh attempt/message/FileId identities, with zero discard/fallback and unchanged complete
verification/activation. It does not change the I2P loss/fresh-job nonclaim above.
ADR 0231 and compact proofs `pair.urbhf0je`/`pair.n76biwao` now close the native available-policy
carrier-loss edge. A concrete 1 MiB range loses its first carrier at 283,797 UDP or 293,394 TCP
bytes; the old attempt and FileId are fenced, the exact prefix moves to a fresh attempt on the other
authenticated range-capable carrier, and retained/resumed bytes match with zero discard/fallback.
Both cells reconstruct and explicitly activate the same 4 MiB generation 2, reject stale terminal
truth, and recover the stopped identity once. Fail-closed I2P remains a discard-and-block path;
the deterministic service boundary now repeats handoff through four distinct carriers after the
prefix grows from 50% to 75% to 87.5%, with cumulative exact accounting and no range retry. The
fifth scheduler record is admitted only under an explicit five-record namespace ceiling. ADR 0232
closes the genuine bounded two-fault native row under recovery-before-refault ordering and
256-kbit/s range
shaping. Compact proofs `pair.le38qcl5` and `pair.8u14ddcy` retain/resume 542,916 direct-UDP or
564,852 forced-TCP bytes across two handoffs, with zero discard/fallback and full reconstruction,
HEAD-last acceptance, and activation. ADR 0233 also closes one 15/16 late-loss row: compact proofs
`pair.tev4u3rs` and `pair.1z7_d0jn` preserve 984,378 UDP or 995,346 TCP bytes and fetch only the
remaining suffix after fresh-carrier reassignment, with zero discard/fallback. ADR 0234 separately
implements explicit-fresh-job whole-object prefix reuse after daemon restart; genuine qualification
passes as compact proofs `pair.f20ma62y` and `pair.lj0pdz6a`, resuming two exact prefixes totaling
115,164 direct-UDP or 159,036 forced-TCP bytes. Repeated-late/final-chunk races, four-plus loss, and
multi-source striping remain open. ADR 0235 now accepts the separate bounded
three-loss native gate: compact proofs `pair.3iufekzy` and `pair.zleebk2k` retain/resume 862,359
direct-UDP or 871,956 forced-TCP bytes through three handoffs, exhaust one signed two-restart budget,
and converge with zero discard/fallback
(`evidence/2026-08-29-sandwurm-sync-range-triple-route-loss.md`). Its instrumented fourth calibration exposed
an asymmetric application-handshake reconnect race rather than a range scheduler defect. ADR 0236
now retries the exact frozen HELLO and CAPABILITIES records at a bounded cadence and projects their
attempt counters; deterministic accepted-but-unobserved packet coverage passes without changing
framing or authority. The subsequent UDP diagnostic reached the next explicit limit at 542,916
retained/resumed bytes: four scheduler tombstones could not represent one manifest plus four range
incarnations. ADR 0237 now binds that fence history to host-local namespace policy and gives only the
triple fixture its exact five-record budget. ADR 0238 makes the final restart state unambiguous by
rendering the immutable ceiling, consumed count, and derived remaining capacity separately. ADR
0239 now closes range restart end to end. A bounded chained commitment handles useful plans larger
than one 64 KiB hash payload; ATM1 plan-bound records retain only a strict incomplete bundle prefix;
and a fresh authorized pull deriving the same manifest/basis plan resumes under fresh
attempt/message/FileId identities. Direct-UDP proof `pair.xg41pthc` resumes 281,055 bytes and
forced-TCP proof `pair.00992erw` resumes 276,942 bytes, each fetching only the exact suffix after a
bilateral authority barrier, then verifying, accepting HEAD last, and activating
(`evidence/2026-08-29-sandwurm-sync-range-restart-resume.md`).

### Completion accounting

ADR 0277 permanently retires the six hosted, independent-party, physical-target, and independently
witnessed public-history checkboxes from the repository completion definition. They are struck
through below rather than mislabeled as passed evidence. ADR 0278 closes selective sync and ADR 0279
closes the founding route-policy population. ADRs 0280--0281 close the finite M5C adversarial/scale
campaign, and ADRs 0282--0283 repair and accept the M5C one-writer shadow. Zero founding-machine
completion obligations remain.

Sandwurm remains the accepted multi-node mechanism substrate. It is still described accurately as
same-machine VM evidence; the scope decision does not manufacture physical diversity, hosted
execution, external review, or independent public-network history.

## M0 — release truth and reproducibility (complete for founding-machine scope)

Make every distributable claim reproducible outside the founding shell.

- [x] Add a CI job for the pinned source-linked standalone binary and its verification.
- [x] Package binary verification, dependency digests, licenses, the repository commit, and exact
  upstream source archives in one checksummed artifact.
- [x] Verify same-builder incremental binary hash stability on the founding bare-metal host.
- ~~Observe the first hosted CI run after an official remote is connected.~~ **Retired from the
  repository completion scope by ADR 0277; local workflow and package verification remain owned.**
- ~~Require an independent builder comparison for repository completion.~~ **Retired from the
  repository completion scope by ADR 0277; it remains optional downstream distribution evidence.**
- [x] Generate and strictly verify a deterministic executable-bound SPDX 2.3 source-component SBOM
  in both standalone and Nix source-linked distributions (ADR 0150).
- [x] Run and retain a same-toolchain comparison from two empty product build roots. The complete
  release surface is byte-identical on the founding host
  (`evidence/2026-08-24-reproducible-standalone.md`).
- Signed tags, publication checksums/release notes, vulnerability-reporting intake, and the final
  GPL-compliant binary-distribution act belong to the owner-managed distribution process, not the
  repository completion boundary. The tree already packages exact licenses and source inputs.

Exit: a clean checkout on the founding machine produces and verifies the traceable source-linked
release candidate. Hosted execution and independent-builder comparison are downstream distribution
evidence, not repository gates (ADR 0277).

## M1 — ordinary self-profile mutation (complete)

The typed local protocol already reads and mutates Tox presentation state and persists it through
c-toxcore savedata. Finish the ordinary Unix façade without confusing presentation with identity:

- [x] Private, no-follow, inode-checked name, status-message, and presence ingress lanes.
- [x] Exact empty-value, LF framing, status-token, and c-toxcore byte-limit contracts.
- [x] Ordinary and structured entrances converging on the same control/Agent path.
- [x] Provider readback, atomic projection, savedata persistence, and process restart proof.

Exit: shell writes and the one-binary CLI produce the same persisted profile and failure evidence.

## M2 — second harmless machine read (complete)

Add one useful read-only operation beyond `device.describe`, initially `system.summary`.

- [x] Freeze a bounded canonical result schema and privacy classification.
- [x] Use a replaceable typed input so executor tests never depend on the CI host.
- [x] Require signed `read_telemetry` authority, distinct from every mutation capability.
- [x] Omit unstable or identifying host details by construction.
- [x] Generalize outbound durable issuance, restart recovery, and typed result projection beyond
  `device.describe`.
- [x] Prove command/result durability, exact duplicate handling, process operation, and terminal
  record persistence across restart.

Exit: an authorized peer can retrieve useful non-secret system health without gaining mutation.

## M3 — repeatable genuine-network laboratory (complete)

Turn the successful ad-hoc two-peer smoke into retained, controlled evidence.

- [x] Operate a disposable pinned bootstrap/TCP-relay fixture and archive content-free verified
  Sandwurm pair receipts for direct UDP and forced TCP.
- [x] Exercise request/accept, authority proof, text, both harmless commands, exact finite files,
  bilateral removal, re-add, and process restart with two genuine source-linked peers.
- [x] Emit only hashed peer identifiers in the shareable report; disposable state remains secret.
- [x] Measure initial/reconnect convergence, resident memory, CPU ticks, context switches, open
  descriptors, application-protocol journal bytes, and savedata size in the genuine lab report.
- [x] Prove the full genuine-peer lifecycle with native UDP disabled, using TCP relays only.
- [x] Prove a genuine peer process restart creates a higher online epoch, fresh confirmed
  transcript, and fresh authority proof without changing transport or stable device identity.
- [x] Reject an in-flight proof for an invalidated ledger head without poisoning the fresh
  challenge round; qualify the bootstrap-then-grant ordering on both genuine carriers.
- [x] Reuse a private test-only Tox/device identity pair by default while copying it into fresh
  authority, command, runtime, friendship, and transfer state for each run (ADR 0056).
- [x] Retain an explicit from-scratch key-generation lifecycle as a separate qualification gate.
- [x] Apply independently seeded 5% packet loss to both live Sandwurm TAP paths, require positive
  kernel drops, complete 128 exact lossy probes per role, preserve the confirmed epoch, and exchange
  ordinary text during and after impairment over direct UDP and forced TCP (ADR 0151).
- [x] Qualify the actual previous-stable 0.2.22 to current 0.2.23 savedata boundary with two mutually
  friended identities, exact profile/friend preservation, bilateral real-IoTox load/rewrite, backward
  readability evidence, malformed-state refusal, and a byte-reproducible content-free flake receipt
  (ADR 0152).
- [x] Complete live mixed-provider rolling sequencing in two Sandwurm guests over direct UDP and
  forced TCP, with 0.2.22-created mutual friendship, old client/current device bilateral exchange,
  exact friend-route truth, post-exchange rewrite, and cross-provider semantic readback. Backward
  readability does not authorize an old-provider security rollback (ADR 0153).
- [x] Kill the controlled forced-TCP relay after bilateral confirmation, require bilateral offline
  observation, then prove same-key relay recovery, strictly higher online epochs, and fresh
  bidirectional traffic in the concurrent Sandwurm guests.
- [x] Replace the device daemon inside a live forced-TCP pair, require the stable client to observe
  transport and application offline, preserve the exact device identity from savedata, advance the
  stable-client epoch, and exchange fresh bidirectional text after confirmation.
- [x] Blackhole both live TAP packet paths without lowering carrier, require bilateral offline
  observation, restore the default qdiscs, advance both epochs, and exchange fresh forced-TCP text.
- [x] Reboot the device guest from its exact persisted writable disk across bounded Sandwurm VMM
  epochs, bind changed device/unchanged client boot identities, preserve the device Tox identity,
  advance the stable-client epoch, and exchange fresh confirmed text.
- [x] Export accepted pair proofs through an exact content-free verifier allowlist, bind the source
  manifest and every retained file digest, reverify compact form, and remove private guest disks from
  routine retention.
- [x] Add a test-verified native TCP-only mode that disables UDP, local discovery, DHT
  announcements, and hole punching instead of relying on topology assumptions.
- [x] Add a reusable 1x/2x/4x genuine-provider file laboratory, repair synchronous c-toxcore chunk
  service, remove local progress-projection amplification, and retain the founding-host result
  showing 1.62x median four-route scaling while four streams on one route remain flat (ADR 0057).
- [x] Sweep 8/16/32/64 simultaneous files over one versus four routes under observed direct UDP and
  forced TCP, remove quadratic transfer projection, and retain 48 exact phases showing a stable
  roughly 1.5x four-route data-window advantage without provider failure through 64 (ADR 0058).
- [x] Compare normal-text receipts, custom-lossless echo, and custom-lossy echo while idle and
  beside bulk under observed UDP and forced TCP; retain owner-queue, iteration, deadline, CPU, and
  context-switch evidence (ADR 0059).

Exit: Tox/native can be called network-verified for a named topology and provider version.

## M4 — owner re-entry and delegation (complete)

Complete the founding sovereignty promise:

- [x] Freeze the domain-separated RecallRoot owner hierarchy.
- [x] Freeze RecallRoot owner derivation and transcript-bound remembered-owner proof.
- [x] Freeze remote self-delegation as an exact owner-signed ledger append bound to the connected
  controller and challenged device head (ADR 0052).
- [x] Implement the recall-owner CLI ceremony, exact request/result transport, receiver-side
  binding validation, conflict denial, and idempotent duplicate append handling.
- [x] Retain genuine two-peer denial, success, exact-duplicate, and receiver-restart evidence in
  both normal native and TCP-only modes.
- [x] Add proven-owner remote delegated-controller revocation, exact duplicate handling, receiver
  restart replay, and explicit recalled-owner re-delegation.
- [x] Preserve explicit in-epoch owner succession: grant a successor owner before revoking the old
  owner, and never permit implicit owner demotion or last-owner removal.
- [x] Define and implement the adjacent current-owner nomination plus successor-signed
  ownership-epoch transition for phrase compromise or planned ownership transfer (ADR 0054).
- [x] Distinguish phrase compromise, planned ownership transfer, and destructive physical reclaim.
- [x] Retain the absolute rule that IoTox has no vendor reassignment key.
- [x] Retain genuine normal-native and TCP-only transition, exact-replay, retired-owner denial,
  successor re-entry, fresh delegation, and receiver-restart evidence.

Exit: a reconstructed owner can securely re-enter and delegate on a fresh controller.

## M5 — durable offline lifecycle (complete)

Add bounded persistent outboxes and synchronization with explicit identity, expiry, uncertain-clock
behavior, cancellation-before-start, retry/backoff, priority, quota, shutdown, and full-disk rules.
FIFOs remain ingress and never become the durable queue themselves.

- [x] Freeze signed store v3, strict lifecycle/schedule invariants, and verified atomic v2 migration.
- [x] Admit current-version read requests for existing Tox keys while disconnected.
- [x] Persist independent request, receipt, and result attempts, errors, and next-attempt times.
- [x] Retry exact request bytes through bounded exponential backoff and stable jitter until an
  application receipt/result; preserve schedules across restart.
- [x] Provide a one-second pre-attempt cancellation window and refuse cancellation after any
  committed possibly peer-visible attempt.
- [x] Add local high/normal/low priority and total, per-peer/direction, and canonical-byte quotas.
- [x] Require explicit rollback-checked wall-clock trust for TTL, checkpoint trusted startup time,
  guard the live process with monotonic elapsed time, hold expiring work when time is uncertain,
  and distinguish local `expired` from `timed-out-unconfirmed`.
- [x] Close admission and new retry attempts during orderly shutdown; keep prior memory/disk
  generation authoritative on quota, size, or persistence failure.
- [x] Expose typed CLI cancellation, TTL/priority admission, v3 store records, clock state, lane
  schedules, and atomic runtime projections.
- [x] Prove deterministic schedules, open-time quotas, cancellation boundary, full-store write
  failure, monotonic signed clock checkpoints, successful and size-refused atomic v2 migration,
  SENDQ recovery, offline zero-attempt admission, restart, and process cancellation.

Exit: disconnect and restart cannot turn timeouts, retries, or duplicates into ambiguous effects.

## M5A — Ratox interactive foundation (complete for founding-machine scope)

Prepare latency-sensitive Ratox work before adding an Eternal Terminal/Mosh-style remote session.
The complete order and measurable targets live in `ratox-interactive-plan.md`.
The implementation dependency graph and activation rule live in
`ratox-service-implementation-plan.md`; `security-ratox-v1.md` owns the focused threat model, and
`ratox-ssh-status.md` records the exact implemented SSH-shaped boundary and nonclaims.

- [x] Add explicit interactive/control/bulk owner classes with bounded weighted service and
  per-class wait telemetry.
- [x] Add attachment-generation fencing, bounded unacknowledged byte replay, and monotonic RTT/RTO
  primitives without advertising a terminal feature.
- [x] Consume genuine c-toxcore lossless and lossy custom-packet APIs and add a fixed,
  no-amplification, confirmed-session-only diagnostic echo.
- [x] Establish the Ratox-first carrier sweet spot: custom lossless by default; text stays chat;
  lossy remains experimental because it showed no direct-UDP benefit and more forced-TCP misses.
- [x] Qualify controlled loss, duplication, reorder, delay, and queue pressure; separate local
  admission rejection from path misses and measure
  head-of-line blocking before choosing any replaceable lossy state lane.
- [x] Qualify pacing/coalescing intervals and congestion response; keep reliable control/input
  sparse and permit lossy only for sequenced replaceable output with snapshot/resync semantics.
- [x] Freeze versioned terminal frames, authority capability, quotas, PTY lifecycle, and audit
  semantics in a new ADR.
- [x] Complete the independent R3 local process prerequisite: canonical owner-only profiles and
  principal bindings, atomic generation-bound resolution, exact environment sealing, fake-backed
  lifecycle control, and a readiness-proven Linux PTY/`fexecve` adapter with native process tests.
- [x] Implement and unit/integration-test at-most-once input, stale attachment fencing, bounded
  replay/gap behavior, resize, exit, exact authority denial/revocation, retained SENDQ responses,
  round-robin service, offline detachment, and finite shutdown behind a default-off Agent gate.
- [x] Add a separate owner-only `terminal.sock` SOCK_SEQPACKET surface, canonical local protocol,
  controller-side route fencing and bounded replay, and one-binary `terminal`/`terminal-resume`
  operation with raw-mode restoration, resize forwarding, explicit detach/close escapes, and typed
  local errors. The endpoint remains absent unless the independent client gate is enabled.
- [x] Add one-host separate-process local-controller contention, abrupt-death, replacement-resume,
  render-before-ACK, clean-detach, and explicit empty-restart failure evidence.
- [x] Complete the first deterministic-provider R6 contract: route reconnect, exact SENDQ retry,
  controller replacement, live revocation denial, daemon-restart `not found`, failed-start evidence,
  and signed durable incarnation advancement.
- [x] Construct the R7 measurement boundary: exact-at-the-gate owner queue histograms, coherent
  typed sensitive-send outcomes, lane-separated retained-head streak/age, monotonic lifecycle time,
  a bounded canonical two-route/six-load-cell analyzer, and deterministic sanitizer shards.
- [x] Bind the R7 run to raw same-clock timestamps, a reconstructable balanced schedule, exact
  content-free Ratox event/byte spans, route and load artifact digests, and two distinct ephemeral
  capture-role signatures with local boot-ID and key-consistency checks.
- [x] Remove the hidden 128-render session lifetime exposed by the 1,000-sample gate: cumulative
  `OUTPUT_ACK` now uses one exact attachment-local high-water fence, while side-effecting controls
  retain never-evicted pre-effect replay. A 1,001-ack/one-control-slot regression closes cleanly.
- [x] Add explicit 1,000-sample Sandwurm cell names, retain both sides of a rotated host journal,
  bind sample count in raw/compact proof, and require every controller row to join one exact remote
  stage/commit/output triple. These prerequisites do not complete the twelve-cell signed matrix.
- [x] Re-run the bounded repeated production-CLI reconnect gate against the current tree on direct
  UDP and forced TCP. Compact proofs `pair.h25zpony` and `pair.sduwsbg8` verify the same product
  binary hash, expected UDP/TCP carrier truth, two total-loss interruptions, production
  `terminal --reconnect` control, and detached PTY retention. This is a current-regression recheck,
  not a long-soak or overlay-route qualification.
- [x] Remove runtime-projection freshness from the measurement path. A first loaded 1,000-sample
  attempt reached 457 exact renders before the probe waited on a stale projected counter even though
  all 914 owner operations had executed with a 1.047 ms p99 bound. Live authenticated inspection now
  supplies exact queue deltas after local render, and explicit probe failures reach the pair driver.
- [x] Remove the two independent idle sleeps from the live terminal steady state without imposing a
  permanent high-frequency poll. Active host/controller state uses configurable 5 ms transport and
  service defaults plus coalesced local wakes, then restores the ordinary idle cadence. Runtime and
  two-role process-resource evidence expose the selected policy and observed cost (ADR 0156).
- [x] Separate periodic Ratox service from ordered transport-event application after the loaded gate
  exposed required-file-event/owner-command dependency at sample 599. Preserve one event-state owner,
  one toxcore owner, bounded required delivery, and frozen Ratox framing (ADR 0157).
- [x] Accept exact-commit 1,000-sample idle observations with complete process-resource intervals:
  direct UDP p95 23.943 ms and forced TCP p95 99.010 ms. Forced TCP's remote stage-to-output p95 is
  11.515 ms versus direct UDP's 12.764 ms, so the route classes are reported separately.
- [x] Re-run direct-UDP `bulk-1` after the service split and retain its strict compact proof. It
  completes 1,000/1,000 with zero 250 ms misses, but p95 71.698 ms and owner p99 7.114 ms fail the
  direct budgets; this is a valid failed qualification cell, not a pass.
- [x] Run the proposed 256 KiB outgoing-progress coalescing A/B. It cut owner p99 to 0.103 ms but
  exposed shared reliable-carrier head-of-line blocking: render p95 505.064 ms and 991/1,000 samples
  at or above 250 ms. Reject the optimization and preserve the failed proof (ADR 0159).
- [x] Keep the separable per-chunk improvements: one pinned receive descriptor and exact event
  high-water/backpressure counters. Bind final Agent status from both guests into new raw and compact
  Ratox proofs while accepting both-or-neither for historical proof compatibility.
- [x] Requalify descriptor-only direct-UDP `bulk-1`. The exact compact proof `pair.y__zgt1p`
  recovers p95 to 51.146 ms but owner p99 remains 3.972 ms. The client reaches event high-water 1,024
  and records 1,227 required waits; the device reaches 765 with none. This selects explicit pacing.
- [x] Add a bounded high/low-water file-event pacer with a 5 ms minimum hold, 64/16 event thresholds,
  semantic queue reserve, bilateral pause/resume/failure counters, and ordinary pause/cancel
  ownership (ADR 0160). Provider controls execute only outside callbacks.
- [x] Repeat direct-UDP `bulk-1` from exact clean pacing commit `5305e7d`. Compact proof
  `pair.a4j1uirz` passes 1,000/1,000 at render p95 42.727 ms and owner p99 1.499 ms, with zero 100/250
  ms misses, event high-water 180/130, zero required waits, 853/876 matched pacing cycles, and zero
  failures. Do not require the protected route for this cell.
- [x] Accept exact forced-TCP `bulk-1` proof `pair.0vkhkq96`: 1,000/1,000, owner p99 1.452 ms,
  reported route p95/p99 57.594/70.044 ms, zero 250 ms misses, event high-water 183/102, 248/278
  matched pacing cycles, and zero required waits or pacing failures.
- [x] Repair paced workload accounting after the first direct-UDP `bulk-8` attempt completed all
  1,000 samples but treated a scheduler-paused transfer as missing. Observation v6 proves exact
  present/active/paused populations and progress; older proof schemas retain their original meaning
  (ADR 0161).
- [x] Retain the clean direct-UDP `bulk-8` lifecycle proof `pair.y0d97_ng`: all eight transfers are
  present and progressed, cancel-to-empty and close pass, owner p99 is 0.420 ms, and event high-water
  is 134/138 with zero required waits. Classify it as a failed performance cell because render p95
  is 144.120 ms and one sample reaches 250 ms.
- [x] Implement the bounded fair/desynchronized multi-transfer resume policy (ADR 0162): oldest
  eligible pause first, one resume per owner iteration by default, configurable bounded batch,
  complete status/proof accounting, and deterministic three-producer completion.
- [x] Run that policy against the exact direct-UDP `bulk-8` cell. `pair.xs9phpya` exercises
  3,167/2,658 singleton batches with zero failures or required waits and improves p95/p99/max from
  144.120/179.491/264.277 to 124.811/161.242/188.401 ms, but p50 worsens to 56.349 ms and p95 still
  fails. Retain the valid zero-activation outlier `pair.dwo77gs0` separately; it must not be mistaken
  for an ADR 0162 treatment result.
- [x] Implement proactive receiver-owned per-peer carrier admission (ADR 0163): one runnable incoming
  file per peer, oldest-first 20 ms rotation, manual-pause ownership, file-only/sync service cadence,
  complete status/proof accounting, deterministic three-receive fairness, and preserved two-object
  sync convergence.
- [x] Run exact clean-commit direct-UDP `bulk-8` with ADR 0163. `pair.qrggya8w` progresses all eight
  files, records 1,454 rotations, improves p95 from 124.811 to 56.247 ms, and passes owner p99 at
  1.488 ms, but rejects the cell because p95 is not below 50 ms and 141 reactive pause collisions
  remain undifferentiated.
- [x] Implement ADR 0164 ownership coordination: typed external-pause handoff, strict new-generation
  zero-failure proof semantics, bounded harmless post-cancel events, and a 50 ms default quantum to
  reduce rotation churn without changing the one-file window or Ratox framing.
- [x] Accept exact ADR 0164 direct-UDP `bulk-8` proof `pair.bo6l0der`: all eight files progress,
  507 rotations and 77 typed external-owner handoffs have zero true failures, event high-water is
  228/168 with zero required waits, render p95 is 39.634 ms, owner p99 is 1.917 ms, and strict raw
  plus compact verification passes without a terminal file diagnostic.
- [x] Accept exact forced-TCP `bulk-8` proof `pair.pitcu1pk`: all eight files progress, 739 rotations
  and 58 typed handoffs have zero true failures, event high-water is 141/139 with zero required
  waits, owner p99 is 1.525 ms, no render reaches 250 ms, and strict raw/compact verification passes.
- [x] Accept exact direct-UDP `bulk-16` proof `pair.xphist_e`: all 16 files progress, 524 rotations
  and 60 typed handoffs have zero true failures, maximum fair wait is 890.887 ms, event high-water is
  203/183 with zero required waits, render p95 is 40.591 ms, owner p99 is 1.894 ms, and no render
  reaches 100 or 250 ms.
- [x] Accept exact forced-TCP `bulk-16` proof `pair.qk3d51k6`: all 16 files progress, 782 rotations
  and 84 typed handoffs have zero true failures, maximum fair wait is 885.574 ms, event high-water is
  190/136 with zero required waits, owner p99 is 1.013 ms, and no render reaches 250 ms.
- [x] Accept exact direct-UDP `bulk-32` proof `pair.ktcwivx_`: all 32 files progress, 590 rotations
  and 78 typed handoffs have zero true failures, maximum fair wait is 1.744 seconds, event high-water
  is 162/152 with zero required waits, render p95 is 47.765 ms, owner p99 is 1.811 ms, and no render
  reaches 100 or 250 ms.
- [x] Accept exact forced-TCP `bulk-32` proof `pair.lanpv3u7`: all 32 files progress, 670 rotations
  and 56 typed handoffs have zero true failures, maximum fair wait is 1.736 seconds, event high-water
  is 185/147 with zero required waits, owner p99 is 0.798 ms, and no render reaches 250 ms.
- [x] Retain exact rejected direct-UDP `bulk-64` proof `pair.t736zqqh`: all 64 files progress with
  zero true failures and owner p99 is 0.118 ms, but render p95/p99 is 331.081/446.692 ms and 108
  renders reach 250 ms. Queues peak at 50/50, reactive pacing never activates, CPU is low, and remote
  stage-to-output p95 is 10.293 ms, locating the cliff in the shared Tox carrier before owner service.
- [x] Retain exact rejected forced-TCP `bulk-64` proof `pair.swij6mj9`: all 64 files progress with
  zero true failures, but event high-water reaches 711, owner p99 is 2.199 ms, and one render reaches
  560.528 ms. This is a high-throughput pressure failure distinct from direct UDP's low-use stall.
- [x] Freeze the evidence-backed boundary in ADR 0165: one Agent qualifies at 32 accepted sends and
  receives; larger explicit limits remain experimental, excess offers stay unaccepted, and the
  failed frozen 64-stream R7 cells are not weakened or relabeled as passes.
- [x] Qualify the single-Agent excess-work scheduler with at most 32 accepted transfers per Agent while
  preserving attempt identity, bounded retry/cancellation, fairness, and both route latency classes.
  The ADR 0166 boundary retains a full-ledger sync offer with the same immutable
  attempt/FileId/file number outside accepted transport state, bounded service rotates across at
  most 32 records per pass, and pending cancellation is one-shot. Genuine direct-UDP
  `pair.xrl6_7gv` and forced-TCP `pair.dqbsp21_` cells each held the receive limit at one, retried the
  paused second object ten times, admitted exactly two sequential offers, and converged with zero
  pending. Separate accepted 1,000-sample `bulk-1` cells bind each route's latency class. This closes
  by explicit composition, not a claim of simultaneous Ratox-under-sync-deferral latency.
- [x] Add the genuine serialized terminal capture path and Sandwurm `ratox-idle` construction cell:
  exact one-byte INPUT, remote PTY output, local pseudoterminal render, per-INPUT owner-queue delta,
  and content-free host stage/commit/output joins. Release sampling and the bulk matrix remain open.
- [x] Accept the first two-guest direct-UDP idle construction observation: 40/40 exact renders,
  keypress-to-render p50 45.442 ms / p95 63.941 ms / p99 67.435 ms, zero 250 ms misses, and owner
  queue p99 0.115 ms. The small cell is diagnostic and does not replace 1,000-sample qualification.
- [x] Accept the matched forced-TCP idle construction observation: 40/40 exact renders,
  keypress-to-render p50 65.454 ms / p95 104.139 ms / p99 109.183 ms, zero 250 ms misses, and owner
  queue p99 0.081 ms. Remote stage-to-output p95 stayed near 27.45 ms on both routes.
- [x] Accept the direct-UDP 1/8/16/32/64 bulk construction ladder with 40/40 exact renders in every
  cell, zero 250 ms misses, render p95 at or below 35.443 ms, and owner queue p99 at or below
  0.394 ms. Preserve the ordinary 32-transfer default, require an explicit 64-transfer lab opt-in,
  and retain first-byte fairness plus retry-to-empty cancellation evidence. Forced TCP and the
  1,000-sample matrix remain open.
- [x] Identify and repair pinned c-toxcore's low-slot file-service starvation with a source-tracked
  per-friend round-robin cursor, explicit `iotox-file-rr1-tcp-connect120` runtime/receipt provenance,
  and an unchanged
  forced-TCP 16-stream before/after gate: 4/16 stock became 16/16 patched while Ratox remained exact.
- [x] Defeat the forced-TCP single-route 17/32 delivery boundary at construction scale: four
  independently keyed routes bound to the same stable principals advanced 32/32 streams twice while
  Ratox stayed exact. The current compact proof is `.sandwurm/exports/pairs/pair.hb491hc_`.
- [x] Bound the first four-route saturation interval: 40 streams completed one full client workload
  but failed repeat cancellation, 48 and 56 missed durable interactive evidence, and 64 exceeded a
  five-second terminal-output deadline. Retain eight bulk streams per route as the qualified point;
  do not advertise 10–16 per route as reliable capacity.
- [x] Make four-route establishment resilient: retain each route's savedata and transport identity,
  permit at most two staggered automatic restarts per auxiliary route, and fail closed without
  starting work until all four expected TCP routes confirm. A deliberate one-sided route-process
  replacement recovered and completed the full 32-stream/Ratox gate; ADR 0107 records the boundary.
- [x] Freeze live lane-loss semantics: with transfers already active, prove an explicit pause or
  cancellation outcome before any reassignment. Current c-toxcore/process behavior is now observed:
  losing route three purges its eight transfers, leaves the others active, performs no reassignment,
  and same-savedata recovery starts empty. The shared-route configuration failed because Ratox was
  not repeatable while route zero also carried eight bulk transfers. The terminal/control-only
  route-zero gate now
  passes with 24 bulk transfers on routes one through three: 8 faulted, 16 unaffected/progressed,
  zero reassigned, 40/40 exact Ratox samples below 250 ms, same-identity recovery, and explicit
  control-then-worker-restart cleanup. ADR 0109 freezes the default policy and compact proof
  `.sandwurm/exports/pairs/pair.0xk33kco`. A future scheduler must preserve immutable object identity,
  bound duplicate delivery, retain eight-stream
  route headroom, and never move Ratox implicitly.
- [x] Implement one stable-principal-bound route inventory and coordinator with explicit
  `connecting`, `authenticated`, `ready`, `recovering`, and `unavailable` states. Preserve the
  current single-route path when no route-set policy is configured. The canonical signed artifact,
  coordinator lifecycle, member/work/restart budgets, hostile admission matrix, strict pre-network
  loader, signed generation/artifact high-water state, and `routes`/`routes-watch` projection are
  implemented. Auxiliary owner supervision and the bounded signed route-set plus transcript-binding
  frame are implemented. Coordinator-owned primary-principal association, remote generation/fork
  retention, and exact-epoch replay admission are implemented. The worker has a construction-gated
  one-send/one-reciprocal live exchange path. Agent construction installs the restricted signer,
  derives trust from exact primary authority state, and drives reciprocally verified workers to
  `ready`; authentication loss fails back to `connecting` without consuming restart budget.
- [x] Qualify immutable sync objects as the first reassignment unit on genuine two-guest routes. The transport-neutral scheduler now
  uses canonical kind/digest/size identity, exact bulk-worker attempts, bounded fence tombstones,
  late-completion rejection, verification-before-idempotent-commit, coordinator accounting, and
  fail-closed close. Exact attempt IDs now also derive private no-clobber staging destinations whose
  completed files are size/digest verified and exclusively object-committed under the namespace
  transaction, with shape-safe fenced discard. Namespace-scoped schedulers now reserve each object's
  full byte count across all routes until fence or commit. Auxiliary workers now own bounded
  file-transfer managers and expose receive/cancel only for exact reciprocally authenticated bulk
  incarnations. Each admitted receive now owns preallocated bounded terminal capacity; a
  namespace-scoped bridge binds its live file number to one attempt, commits independently verified
  staged bytes, and fences failure or replay without disturbing another route peer. Gate 3 includes
  a stable-device-signed high-water/active-attempt journal and conservative startup recovery that
  commits complete verified staging or fences incomplete work without reviving Tox handles. Fixed
  HEAD/object request/result records now bind an exact signed-HEAD digest to a nonzero explicit Tox
  FileId; auxiliary sends share the bounded terminal ledger and verify the provider retained that ID.
  The scheduler now also accepts a bounded transport-capacity adapter, so a single-route slice need
  not fabricate coordinator proofs. Production object verification reuses toxsync SHA-256 through a
  descriptor-stable hasher. A transport-neutral publisher dispatcher now enforces exact v3 subscribe
  authority, namespace membership, signed-HEAD pinning, a bounded rolling exact-replay window, authority-
  head fencing, local object derivation, verification, and pre-retained exact-FileId offers. Gate 3
  now includes default-off Agent construction, strict namespace/attempt recovery, subscriber
  orchestration, bounded off-callback dispatch, exact request retry, paused-offer FileId joins, and
  content-free local pull/status controls. Auxiliary workers now have a separate default-off,
  pre-reserved bounded application queue for only canonical object request/result records; every
  record binds route/worker, friend/epoch, remote generation, and stable principal, while trust loss
  purges queued work (ADR 0167). Parent dispatch now separates real primary authority/HEAD state from
  an exact auxiliary object carrier, joins FileId offers and terminal truth through that incarnation,
  charges signed coordinator capacity, fences loss, and reissues missing immutable objects with fresh
  identities on another ready worker. A deterministic two-worker Agent gate forces the first carrier
  offline and converges/activates through the second (ADR 0168). Genuine direct-UDP and forced-TCP
  Sandwurm cells now force loss after positive progress, observe stale old-worker truth, converge and
  activate through a different bulk route, restore the lost route under a fresh incarnation, and
  complete protected Ratox with zero 250 ms misses (ADR 0169 and
  `evidence/2026-08-25-sandwurm-sync-route-loss.md`).
  Raw toxcore file numbers and terminal frames are never scheduler identities.
- [x] Qualify the coordinator through Gate 4 in the order frozen by `multi-route-plan.md`: live loss
  without reassignment, authenticated inventory, immutable-object reassignment, and fixed/adaptive
  scheduling. Gate 4 compares fixed
  and conservative adaptive selection under varied route startup/fault order. Its
  deterministic prerequisite is implemented: `--sync-route-policy adaptive` selects the lowest exact
  admitted-work/budget ratio only at new admission or mandatory reassignment, with restart/key ties
  and live decision counters (ADR 0170). The first genuine two-guest topology A/B passes direct UDP
  and forced TCP with exact fixed carrier reuse, adaptive idle-carrier placement, four activations,
  zero residual work, zero HEAD retries, and subsequent protected Ratox (ADR 0171 and
  `evidence/2026-08-25-sandwurm-sync-route-balance.md`). Independent adaptive-first counterbalance
  cells also pass on both carriers, so policy phase order is closed. ADR 0220 now separates loss
  permission from placement: `--sync-route-failover fail-closed` fences and counts a lost
  exact-carrier job without selecting an available replacement, while the compatibility default
  retains existing reassignment. ADR 0221 adds `sync-pull FRIEND NAMESPACE
  [available|fail-closed]`, freezes the choice on the job, rejects conflicting retries, and makes
  loss/reassignment consult that value. The full mock-Agent first-byte-loss gate passes with the
  process default deliberately opposite the job in both directions. ADR 0222 then freezes an
  owner-local `any|tox/native|tox/tor|tox/i2p` class per pull and filters both admission
  and replacement against the exact constructed worker context; named classes never fall back to
  primary. The actual-I2P guest now requests the I2P class explicitly. Authentication of that class
  in a stable-device-signed artifact is now implemented by route-set v2 (ADR 0225); its genuine
  actual-I2P loss cell is accepted as compact proof `pair.jbr89_gc` under ADR 0226. ADR 0223 freezes
  the transport prerequisite, and ADR 0224 now integrates same-process whole-object resume through
  the scheduler: initial sync receives own canonical private partials; available-policy loss fences
  the old attempt; a fresh attempt/FileId/carrier atomically inherits the exact prefix and seeks;
  full digest verification still precedes commit; stale old terminals cannot commit. Content-free
  status reports retained partials, resumed attempts, and resumed bytes. The deterministic full-Agent
  gate resumes exactly three bytes across two authenticated workers, while its fail-closed twin
  retains and resumes zero. Signed high-water cleanup closes handoff crash debris. ADR 0234 now
  retains only strict positive whole-object prefixes across daemon restart, then requires a fresh
  authorized signed-HEAD pull and fresh transport identities to claim the identical digest/size;
  deterministic three-byte suffix-only continuation and unmatched-prefix pruning pass. Genuine
  direct-UDP/forced-TCP compact proofs `pair.f20ma62y` and `pair.lj0pdz6a` resume two exact prefixes
  with interrupted/resumed equality and full convergence. Genuine two-guest direct-UDP and forced-TCP
  live-loss cells now retain and resume two concurrent positive object attempts with exact aggregate
  byte equality, zero
  fallback/residual partials, complete digest/HEAD/activation convergence, stale-terminal fencing,
  savedata-identity recovery, and protected Ratox (`pair.jlcr7zms`, `pair.okks1io5`, ADR 0224, and
  `evidence/2026-08-28-sandwurm-sync-byte-resume.md`). The actual-Tor process-loss cell now also
  retains/resumes two prefixes and 102,825 bytes exactly through its native survivor after host
  `SIGKILL`, without an IoTox worker restart, then recovers the identical Tor member
  (`pair.3u5cjbci` and
  `evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md`). Positive I2P range transport now
  passes as `pair.ej_4507n`: the existing range-v1 framing fetches one changed 128-byte region through
  the signed construction-I2P member and reuses the remaining 4,194,176 verified bytes (ADR 0227).
  Its destructive companion now passes as `pair.a9zwongf`: live loss discards a positive partial
  1 MiB bundle without downgrade, the same member requalifies without worker restart, and a distinct
  explicit pull refetches that range and activates from the 3 MiB verified basis (ADR 0228). I2P
  same-handle or I2P carrier-loss byte resume, Tor-to-Tor qualification, I2P repeated/late loss,
  and attributable resource science remain open. Whole-object daemon-restart
  continuation is accepted under ADR 0234 on direct UDP and forced TCP. First single-pull
  cancellation-tail cells also pass on both carriers with exact positive auxiliary progress, work
  release, no reassignment, and subsequent protected Ratox (ADR 0172 and
  `evidence/2026-08-25-sandwurm-sync-route-cancel.md`). The eight-job population row now also passes
  on both carriers. Fixed fills one route before spillover (`00001111`), adaptive alternates
  (`01010101`), all 16 jobs per cell progress and explicitly activate, route work drains to zero,
  and process-incarnation resource intervals plus protected Ratox are retained (ADR 0173 and
  `evidence/2026-08-25-sandwurm-sync-route-population.md`). The bounded concurrent-cancellation row
  also passes both carriers: eight adaptive jobs bind as `01010101`; four simultaneous withdrawals
  are balanced two-per-route and reach terminal cancellation in 150 ms UDP / 100 ms TCP; four
  survivors commit and activate; work drains 16-to-zero without reassignment; resource and protected
  Ratox evidence remain intact (ADR 0174 and
  `evidence/2026-08-25-sandwurm-sync-route-concurrent-cancel.md`). Two 1 MiB/job direct-UDP cells
  completed cancellation but missed the first protected Ratox `OPENED` deadline behind the shared
  4 Mbit FIFO-shaped TAP. ADR 0241's controlled companion keeps the 1 MiB/job load and 4 Mbit edge
  but substitutes a live-proved HTB/`fq_codel` hierarchy. Direct UDP `pair.am47s4qe` and forced TCP
  `pair.78uagrhw` pass four balanced cancellations, four survivor activations, work 16-to-zero, no
  reassignment, and protected Ratox with 17.067/112.817 ms maxima; compact proofs bind the rate,
  handles, active-flow count, traffic, and drop counters
  (`evidence/2026-08-29-sandwurm-common-link-fairness.md`). This is a same-host mechanism result, not
  strict priority, reserved bandwidth, or a universal qdisc default. The loss-before-cancel row then
  passes both carriers: the active worker is
  fenced after ≥65,536 bytes, the pull reassigns and progresses on its replacement, cancellation
  drains work two-to-zero in 80 ms without another reassignment, the stopped identity spends one
  restart-budget unit and returns ready, and protected Ratox remains intact (ADR 0175 and
  `evidence/2026-08-25-sandwurm-sync-route-loss-cancel.md`). Both exact corresponding auxiliary
  readiness orders then pass over both carriers with ten sole-ready samples per phase, final
  two-route readiness, signed tree convergence, and protected Ratox (ADR 0176 and
  `evidence/2026-08-25-sandwurm-sync-route-startup-order.md`). Random startup/fault delays, startup
  during faults, and opposite or simultaneous loss/cancel order remained at that point. The opposite
  deterministic cancellation→loss order now also passes: cancellation drains work and staging
  before one exact carrier loss, zero reassignment, two stale-terminal fences, one recovery, restored
  route inventory, and protected Ratox (ADR 0177 and
  `evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md`). One shared-arm cancellation/loss race
  per carrier now also passes. Both 500/500 ms cells linearize as cancel-first with one loss, zero
  reassignment, one exact cleanup retry, one recovery, and protected Ratox (ADR 0178 and
  `evidence/2026-08-26-sandwurm-sync-route-cancel-race.md`). The 250/1,000 ms loss-first companion
  also passes both carriers with one reassignment to the terminal replacement, zero cleanup retries,
  one recovery, and protected Ratox (ADR 0179 and
  `evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md`). Both shared-arm outcomes are
  closed. The eight-job population-loss companion also passes both carriers against one corrected
  binary: fixed pattern `00001111`, four exact affected jobs, one loss, four full-work-aware
  reassignments, at least four stale-terminal fences, 12 fixed selections, eight activations, one
  recovery, work 16-to-zero, resource evidence, and protected Ratox (ADR 0180 and
  `evidence/2026-08-26-sandwurm-sync-route-population-loss.md`). This closes one deterministic
  multi-job same-carrier loss row and the discovered steady-state auxiliary event/carrier liveness
  cycle. The degraded-admission companion now also passes: two pre-loss jobs reassign, then two
  genuinely new jobs are created while exactly one bulk route is ready and both select that
  survivor; all four activate, work drains four-to-zero, the route recovers once, and protected
  Ratox passes on direct UDP and forced TCP (ADR 0181 and
  `evidence/2026-08-26-sandwurm-sync-route-loss-admission.md`). Clean Agent restart now quiesces
  carrier service while required-event draining remains alive. The controlled startup-admission
  companion now also passes: after a clean same-state subscriber Agent restart, one exact bulk route
  remains solely ready for ten samples; two 16 MiB jobs start there and remain live on that carrier
  when the held route joins; both activate with zero reassignment and work four-to-zero on direct UDP
  and forced TCP (ADR 0182 and
  `evidence/2026-08-26-sandwurm-sync-route-startup-admission.md`). This closes degraded admission
  after controlled Agent startup and supplies one larger-object topology/liveness observation. The
  first larger-object ABBA throughput row now also passes both carriers. Four fresh-Agent phases pull
  two 16 MiB trees each; fixed selects `00`, adaptive selects `01`, all eight revisions activate,
  work drains four-to-zero, and protected Ratox remains intact. Direct UDP observes 179.940 s fixed
  versus 154.060 s adaptive (16.80% gain); forced TCP observes 168.410 s versus 158.040 s (6.56%).
  The forced-TCP prerequisite exposed a continuous transport epoch across Agent replacement, so
  `application-epoch-restart-v1` now advances only a negotiated strictly greater durable
  process/connection generation, retires all old application authority/work, and re-confirms without
  weakening exact-generation HELLO conflicts (ADR 0183 and
  `evidence/2026-08-26-sandwurm-sync-route-throughput.md`). Random delay distributions,
  machine/guest cold startup with a physically absent route, startup concurrent with a real fault,
  repeated larger-object throughput distributions, strict traffic-class priority/reservation,
  independent bottlenecks, and relay diversity remain open. Keep
  direct UDP benefit, proportional throughput, logical route protection, and physical-path/QoS
  diversity as separate claims.
- [x] Qualify Gate 5 operator policy over the complete founding-machine substrate. ADR 0279's seeded
  integrity audit joins 16 accepted direct-UDP/forced-TCP cells, 2.73 cumulative observation-hours,
  six exact startup/fault strata, five object-size strata through 16 MiB, and 16 counterbalanced
  throughput phase samples. Adaptive is now the ordinary initial selector; fixed remains diagnostic,
  and neither moves healthy work. The random value orders the evidence audit; the fault clocks use
  reproducible stratified values rather than pretending a small random sample is exhaustive.
  Physical-path independence, strict traffic-class reservation, bandwidth bonding, universal QoS,
  and public-relay diversity remain explicit nonclaims under ADR 0277.
- [x] Rerun direct UDP on the patched provider through the ordinary 32-transfer limit: 1/8/16/32 all
  advanced every lane, rendered 40/40 exact terminal samples, and canceled to empty. The explicit
  64-transfer opt-in captured all terminal samples but did not advance every lane inside the global
  bound; retain 32 as the ordinary limit and revisit 64 after route striping.
- [x] Construct the first R8 terminal hardening boundary: profile v2, runtime capability-ceiling
  discovery, zero active/ambient capabilities, privileged securebits and bounding-set sealing,
  baseline seccomp, strict MDWE/Landlock ABI 10, and native success-or-named-fail-closed evidence.
- [x] Close the baseline argument gaps: deny reviewed terminal/console ioctl requests, inspect legacy
  clone namespace flags, force clone3 through the inspected fallback, prove ordinary thread creation,
  freeze the established session/parent-death contract, prove high-descriptor closure, and require
  pidfd-revalidated session-wide teardown for baseline/strict.
- [x] Add an explicit delegated cgroup-v2 lifecycle option for hardened PTYs: validate one
  supervisor-owned delegation, create and inode-pin a private leaf, attach the blocked helper before
  manifest release, use `cgroup.kill`, and require recursive `populated=0` before exact removal/reap.
- [x] Bind each delegated leaf to canonical boot ID plus exact daemon PID/start time, serialize
  startup recovery under the durable host-incarnation lease, preflight a bounded reserved namespace,
  reclaim only proven-stale versioned leaves, refuse populated PID-only legacy leaves, and exercise
  the positive kill/quiescence/removal lifecycle in a fresh isolated cgroup-v2 hierarchy.
- [x] Add an optional host-owned pids/memory/swap/CPU controller envelope, require each controller to
  be available and active, preflight every distinct enabled payload identity before recovery/network
  activation, apply and exactly read back controls before helper attachment, and retain independent
  lifecycle and controller process-oracle routes.
- [x] Add canonical profile v3 resource budgets beneath that host ceiling, compose scalar maxima and
  exact CPU ratios monotonically, preflight each distinct `(identity, effective budget)` pair, and
  recompute the effective policy inside the production factory before cgroup or process work.
- [x] Advance canonical profiles to v4 with monotone `memory.high`, exact write/read-back, and
  teardown-time PID/memory/CPU controller outcomes accumulated as content-free private runtime truth.
- [x] Advance canonical profiles to v5 with one exact `MAJOR:MINOR`, monotone read/write BPS and
  IOPS ceilings, semantic `io.max` read-back, and teardown-time saturating `io.stat` totals.
- [x] Retain optional zero-baseline per-session CPU, memory, and I/O PSI totals after proved
  quiescence, with strict bounded parsing, explicit whole-interface/`full` availability counts,
  saturation, and owner-private projection without rolling averages or labels.
- [x] Complete Sandwurm two-node keypress-to-render latency, interference, guest-reboot, and route-fault
  qualification on the founding machine. The 1,000-sample matrix classifies every frozen load/route
  cell, the restart and route-fault slices retain exact identity/epoch recovery, and rejected
  64-stream cells remain retained failures rather than weakened gates.
- [x] Boot and receipt-verify distinct client/device Sandwurm closures with networking absent before
  constructing the simultaneous controlled-network topology.
- [x] Keep both source-linked guests live concurrently on distinct prepared-bridge TAPs and prove
  confirmed friendship plus bidirectional text under direct UDP and forced TCP using one binary.
- [x] Prove the forced-TCP relay-fault slice with bilateral offline observation, preserved relay
  identity, strictly advancing online epochs, and post-recovery bidirectional text.
- [x] Prove device-daemon replacement with both VMs and the relay live, exact saved identity,
  stable-client offline observation and epoch advancement, and fresh confirmed bidirectional text.
- [x] Prove forced-TCP link interruption with live carriers/processes, bilateral offline observation,
  strictly advancing epochs, restored default qdiscs, and fresh bidirectional text.
- [x] Prove persisted-disk device guest restart with a changed boot identity, exact preserved Tox
  identity, stable-client epoch advancement, and fresh bidirectional text.
- [x] Re-run both routes beside 1/8/16/32/64 bulk streams with 1,000 samples per cell and decide
  whether an authenticated dedicated Tox route is required for latency isolation. One Agent passes
  the direct-UDP strict and forced-TCP common gates through 32 accepted transfers; both 64-stream
  cells fail in distinct transport modes. A dedicated route is not required inside the qualified
  single-Agent ceiling, but aggregate capacity beyond it must use bounded multi-route scheduling
  with a protected interactive/control route and fresh evidence.

Current execution point: R0 framing/carrier work, the complete pure R1 session engine, R2 signed
authority-ledger v2 migration, R3 local PTY/profile adapter, R4 default-off Agent coordinator, R5
private controller stream, the first R6 restart/fault contract, and R7 two-guest latency,
interference, bounded-impairment, and exact-resume qualification are finished at the construction
boundary. R4 validates a secure profile
store and process factory before transport, freezes bit 23 only for an explicitly enabled process,
requires bilateral negotiation and exact current bit-7 authority, dispatches only packet `0xA2`,
retains outbound packets across retryable rejection, rotates bounded PTY service, and fences
offline/revoked/shutdown routes. R5 adds a separately enabled same-user local socket and a pure
controller state machine; it does not advertise host authority or bypass the remote transcript and
ledger gates. Default configurations continue to advertise no Ratox feature and expose no terminal
socket. R6 adds bounded controller admission, a signed pre-network incarnation lease, and real
process gates. rev0026 additionally completes the constructed local seqpacket sender review: both
request and response records are bound to kernel credentials and optional pidfds, ancillary descriptor
injection is rejected, terminal ownership follows the sender process, and administrative silent-client
and socket-inode lifecycles are bounded. rev0027 replaces serial administrative admission and shared
terminal contender waits with bounded multiplexed pending sets, independent leases, global/per-process
quotas, accept/refill and per-cycle work budgets, and active-stream-first terminal service. Blocking-
callback isolation and hostile multi-process coalition stress remain future hardening. Independent
audit and broad deployment qualification are optional downstream evidence rather than repository
completion gates. rev0029 retains lease-serialized delegated-cgroup recovery and adds
fail-closed process, memory, swap, and CPU controller budgets after the signed host lease. rev0030 adds
canonical profile-scoped budgets composed monotonically beneath the administrator ceiling, exact CPU
ratio selection, pair-keyed preflight, and production-factory recomposition. rev0031 adds one exact
factory-wide reservation ledger over effective process, memory, and swap maxima. rev0032 extends it to
exact average CPU bandwidth at an administrator-selected accounting period, rejects nonrepresentable
ratios and capacity before mutation, rolls back proved-cleanup partial spawns through move-only RAII,
strands the complete charge when post-spawn teardown cannot prove reap plus leaf removal, and retains
owner-private quota/period/current/peak/rejection/stranding evidence through complete teardown. rev0033
adds canonical profile v4 `memory.high`, cross-layer clamp, protected zero-baseline controller records,
and one-shot cumulative teardown outcomes without content or labels. rev0034 advances canonical
profiles to v5 with exact-device read/write BPS and IOPS ceilings, semantic `io.max` verification, and
saturating teardown-time `io.stat` totals. rev0035 adds protected optional CPU, memory, and I/O PSI
records, exact zero-baseline and post-quiescence absolute microsecond capture, and explicit capability
counts without changing profile v5. rev0036 adds independently optional zero-baseline PID, memory, and
swap lifetime peaks plus quota-independent CPU usage/user/system accounting with complete optional
bandwidth and burst tuples. rev0037 adds protected zero-baseline memory fault/reclaim/swap work,
swap high/max/fail events, local freezer duration, and current-kernel IRQ `full` pressure with explicit
interface and tuple capability counts. rev0038 adds exact delegated-root CPU/memory/I/O `avg10` PSI
admission with hysteresis before aggregate reservation or spawn mutation, controller construction
before recovery/network mutation, fail-closed sampling, and typed private last-sample evidence through
ADR 0089. rev0039 adds dedicated per-resource PSI trigger descriptors, one bounded poll/eventfd monitor,
minimum-window holds, exact avg10-hysteresis reopening, fail-closed monitor health, and private trigger
evidence through ADR 0090. Every new leaf remains bound to the Linux boot and exact daemon process
incarnation. Independent local namespace oracles retain positive lifecycle and resource branches. The
rev0039 construction host positively passes the expanded default source suite; controller-dependent
routes retain named skips where a writable delegation or per-cgroup PSI is absent. ADR 0327 adds one
positive NixOS Linux 6.6.94/systemd `Delegate=yes` gate for lifecycle, memory/pids, CPU, I/O, and PSI
admission/quiet-trigger registration. ADR 0343 adds a fast founding-host delegated-user-service
helper that currently passes lifecycle, memory/pids, CPU, and PSI pressure admission while skipping
I/O accounting on this filesystem. Named service-manager/kernel fleet qualification, positive live
trigger-delivery latency qualification, adaptive threshold tuning, live peak/fault/reclaim/freeze
policy, positive IRQ-pressure policy, parent CPU policy, and additional named-host controller oracles
remain open. rev0025 retains
the rev0022 R7 sample shape, local tail/pressure instrumentation,
balanced schedule, raw timestamp derivation, exact host joins, auxiliary provenance digests, and
two-party capture signatures. It retains the rev0024 argument-aware terminal/namespace/lifecycle
fences, descriptor proof, procfd-pinned/pidfd-backed PTY-session containment, repeated quiescent
teardown, payload process-handle denial, and enabled-host dump/core seal, and adds an opt-in delegated
cgroup-v2 leaf with helper-before-manifest attachment, `cgroup.kill`, and recursive populated-state
completion without broadening feature activation. The Sandwurm two-node matrix and ADR 0196/0197
route-fault cells are retained. The delegated-cgroup path and each claimed confinement tier retain
founding-host plus Sandwurm evidence. Named deployment-fleet qualification and independent/
operational R8 review are not established and are outside repository completion. A
dedicated route is evaluated only when complete-service bulk
tests miss the direct-route latency target while the owner interactive queue remains below its 2 ms
p99 target.

Exit: one explicitly authorized reconnectable terminal session survives controller replacement
without lost/duplicated accepted input, stale attachment writes, unbounded history, or silent route
fallback, and meets the named direct-route latency budget.

## M5B — verified file synchronization (data-integrity and lifecycle-fault gates complete)

Turn the preserved toxsync 0.7.0 engine into an explicit IoTox service without confusing file
arrival, revision acceptance, or activation authority. The ordered design and evidence gates live in
`toxsync-integration-plan.md`.

- [x] Preserve the complete transport-neutral engine as ordinary tracked source.
- [x] Pin its Nix development input and pass its 125 native checks with warnings fatal under GCC
  Debug/Release, dependency-minimum portable Release, Clang Debug, and Clang ASan/UBSan.
- [x] Re-audit the complete standalone component on 2026-09-01: close offline-source accounting,
  atomic retained-publication retry, Unix key no-clobber/partial-pair rollback, and two false test
  premises; add a backend-aware command transaction and repeatable TSan lane; retain exact matrix
  and nonclaims in `evidence/2026-09-01-toxsync-deep-audit.md`.
- [x] Reconcile the historical IoToxsync embedding against current IoTox identity, authority-ledger
  v2, durable command, file-transfer, owner-thread, and runtime-tree contracts.
- [x] Freeze namespace/writer/subscriber authority, HEAD acceptance, wire framing, storage quotas,
  restart recovery, and activation policy before enabling network service.
  Current local gates cover namespace policy/load, accepted-HEAD persistence, no-activation artifact
  installation with injected crypto/cancellation seams, and an exact-HEAD manual activation pointer
  with object re-verification and rollback/fork refusal. Authority-ledger v3 now implements the four
  ADR 0091 sync capabilities through a signed non-widening v2 transition, independent domains,
  exact-head proof, and explicit later grant without changing v2. A pure admission gate now combines
  that exact-head proof with the operation-specific capability, stable namespace membership, and
  activation mode. A fixed stable-device-signed HEAD now derives exact generation/parent linkage,
  converts to acceptance state only after verification, and persists through a bounded serialized
  publisher transaction. Its local publication job now commits and reverifies both immutable artifact
  and manifest objects before advancing that HEAD. The default-off Agent now wires these gates into
  publisher/subscriber entrances, frozen transport framing, durable attempts, bounded worker
  orchestration, and content-free local status. Local `sync-publish` now builds the real bounded
  toxsync range-v1 index, commits both objects before its signed HEAD, and exact-token
  `sync-activate` rechecks both immutable objects plus their semantic pair under the namespace
  transaction. Content-v2 publication now builds a bounded flat/paged fabric, admits and verifies its
  complete CAS, and signs its HEAD last without enabling remote dispatch or activation. Canonical
  namespace template/lint plus atomic live create, quiescent update, and
  policy-only removal now exist. ADR 0136 adds separately negotiated manifest-first bounded range
  reconstruction with a zero-copy publisher range view, durable target attempt, exact reconstruction,
  full SHA-256 verification, and accepted-HEAD-last ordering. Its genuine two-guest successor cell
  fetches one 128-byte range and reuses 4,194,176 bytes of a verified 4 MiB generation-1 basis before
  exact generation-2 activation over both direct UDP and forced TCP. The one-source genuine baseline
  passes over direct UDP and forced TCP with identical artifact, manifest, and signed-HEAD identities.
  An 8 MiB rate-shaped follow-up kills the receiver after positive c-toxcore progress and passes
  unclean daemon restart, exact attempt-temporary recovery, exact-revision retry, convergence, and
  explicit activation over both carriers.
  Signed-HEAD writers are now serialized across local processes, and a strict object inventory
  enforces sequential whole-store byte/object admission. Authenticated quarantine reachability is
  implemented; automatic retention policy and permanent purge remain open. A canonical bounded
  retained-revision snapshot now persists explicit accepted-record pins with process-serialized
  pin/unpin and exact restart behavior. Its v2 form is stable-device-signed and hash-links monotonic
  mutations; unsigned v1, foreign-key, and altered state fail closed. Restart-safe whole-record
  coordinated-replay resistance and permanent purge remain open. A bounded mark-only
  planner now merges every current local published, accepted, activated, and retained object root
  against an exact canonical inventory, reporting missing, mismatched, and unreferenced objects.
  One private namespace transaction now spans every implemented local mutation and a stored-state
  root-plus-inventory scan, with acquiring-process/thread-bound nested-operation tokens and
  cross-process exclusion. Accepted HEAD persistence is now stable-device-signed and rejects unsigned,
  foreign, or altered state before install, activation, or reachability. Activation persistence now
  has an independent stable-device signature with the same fail-closed guarantees. Restart-safe
  independent monotonic rollback evidence remains open before that evidence can participate in deletion. A signed
  four-root committed/pending rollback guard and exact two-sided crash reconciliation now exist under
  the namespace transaction. Publication, accepted-HEAD advance, activation, retention pin, and
  retention unpin now execute its begin/replace/finish protocol. Stored reachability checks the guard
  under the same transaction, and a fresh-process oracle rejects isolated root or guard rollback.
  Coordinated replay of guard plus state remains an explicit hardware/external-witness nonclaim.
- [x] Wrap every implemented local root mutation in the signed rollback guard and require stored
  reachability to check the exact guarded root set. ADR 0103 keeps coordinated replay and deletion out
  of scope.
- [x] Prove guarded mutation uncertainty on both sides of root replacement and make every exact
  idempotent retry reconcile pending signed state. Freeze workspace-contained, quarantine-first GC
  construction and require its destructive acceptance fixture to run in the Sandwurm device guest.
- [x] Implement one default-off, one-binary publish/subscribe path using bounded workers and existing
  c-toxcore finite-file primitives; friendship alone grants no namespace access. The process-local
  terminal-event/attempt/object-commit bridge, signed restart journal, canonical HEAD/object wire
  records, explicit-FileId sender/receiver bridges, authorized Agent entrances, bounded worker, and
  epoch-scoped exact retry/replay are complete. A full mock-provider Agent gate commits both objects
  and the accepted HEAD last; owner-local publication and exact-token manual activation now use the
  same typed socket. Owner-local canonical template/lint and live no-clobber namespace installation
  now use local control v1.27. Pulls expose a stable process-local job ID and explicit local
  cancellation uses v1.28 to fence the job, live receives, staging, and signed attempt records before
  any late event can commit. Quiescence-gated policy update and policy-only removal use v1.29; update
  freezes root, engine, and quotas, while removal deliberately preserves every content and signed-state
  root.
- [x] Prove byte-identical one-source immutable-file convergence and exact-token manual activation
  across two source-linked Sandwurm guests over observed direct UDP and forced TCP.
- [x] Prove unclean receiver-process restart after positive transport progress over direct UDP and
  forced TCP, including signed active-attempt survival, fail-closed private temporary recovery,
  identity preservation, exact-revision retry, accepted-HEAD-last ordering, and explicit activation.
- [x] Prove explicit process-local cancellation after positive provider progress and admitted FileId
  receives over direct UDP and forced TCP, with terminal job fencing, empty staging, and no accepted
  or activated HEAD. Retain the exact clean-source bindings in
  `evidence/2026-08-21-sandwurm-sync-cancel.md`.
- [x] Prove bilateral live-link loss after positive provider progress over direct UDP and forced TCP.
  Retire the old authenticated epoch, job, FileIds, signed attempt truth, and partial staging; require
  both peers to advance and stabilize before an explicit fresh whole-object pull may accept and
  activate the exact revision. Retain the bindings in
  `evidence/2026-08-21-sandwurm-sync-disconnect.md`.
- [x] Prove local pause and resume of the same live receive after positive provider progress over
  direct UDP and forced TCP. Retain one exact file number/FileId, unchanged partial position for 20
  consecutive samples, absent acceptance/activation while paused, and ordinary convergence after
  resume. Retain the bindings in `evidence/2026-08-21-sandwurm-sync-pause.md`.
- [x] Prove controlled publisher-guest restart from its persisted disk after positive provider
  progress over direct UDP and forced TCP. Require a bounded initial VMM reboot exit, changed
  publisher boot identity, unchanged subscriber boot identity, exact publisher identity/policy/object/
  HEAD preservation, terminal old-job cleanup, 50 stable samples on a higher authorized epoch, and
  explicit whole-object retry before acceptance and activation. Retain the bindings in
  `evidence/2026-08-22-sandwurm-sync-guest-restart.md`.
- [x] Prove one-source incremental file reconstruction through the complete deterministic Agent and
  provider boundary: negotiate bit 26, verify the candidate manifest first, reuse only the exact
  accepted artifact basis, fetch one bounded canonical range bundle, verify the complete target,
  clear durable attempt truth, accept generation 2 last, and expose exact content-free savings.
  Retain the construction evidence in `evidence/2026-08-22-sync-range-reconstruction.md`.
- [x] Prove the same incremental path on the genuine provider over direct UDP and forced TCP. Retain
  cross-guest range accounting, exact revision identity, accepted-HEAD-last ordering, activation,
  and independently reverified compact proofs in `evidence/2026-08-22-sandwurm-sync-range.md`.
- [x] Recover when the exact accepted range basis is absent or corrupt: reverify the candidate
  manifest, issue a fresh whole-artifact attempt, verify its complete SHA-256, and accept the successor
  HEAD last without deleting or replacing the unusable prior object. The deterministic subscriber and
  genuine direct-UDP/forced-TCP provider cells pass (ADR 0137 and
  `evidence/2026-08-22-sandwurm-sync-corrupt-basis.md`).
- [x] Establish the safe full-discard baseline for one partial range failure: discard exact staging,
  finish signed attempt truth, and fence scheduler state; retry the identical plan once under a fresh attempt,
  message ID, and FileId without reusing prefix bytes. Deterministic and genuine direct-UDP/forced-TCP
  gates pass (ADR 0138 and `evidence/2026-08-22-sandwurm-sync-range-retry.md`).
- [x] Reuse one exact failed-range prefix across the fresh-attempt fence for the same bounded job and
  carrier. Initial receives own a strict private inode from byte zero; one admission deferral
  preserves its exact empty state; positive incomplete bytes hand off atomically to a fresh attempt
  and FileId; and c-toxcore seeks before receiving only the suffix. Deterministic 524,288-byte
  coverage and genuine 15,081-byte UDP/24,678-byte TCP cells pass with exact retained/resumed
  equality, zero discard/fallback, complete artifact verification, HEAD-last acceptance, and explicit
  activation (ADR 0230 and `evidence/2026-08-22-sandwurm-sync-range-retry.md`).
- [x] Retain and resume one exact bounded-range prefix across native auxiliary carrier loss under
  `available` policy. Deterministic coverage fences old offer/result/terminal truth, refuses a
  replacement without range negotiation, and hands the inode to a distinct authenticated carrier
  under fresh attempt/FileId identities. Genuine direct-UDP/forced-TCP cells retain and resume
  283,797/293,394 bytes exactly with one loss/reassignment/stale-terminal/recovery, zero
  discard/fallback, full reconstruction, HEAD-last acceptance, and explicit activation (ADR 0231 and
  `evidence/2026-08-29-sandwurm-sync-range-route-loss.md`). Deterministic coverage also loses three
  carriers as the inherited prefix grows from 50% to 75% to 87.5%, then hands it to a fourth
  attempt/carrier; all stale generations remain fenced and ordinary range-retry accounting stays
  zero.
- [x] Qualify two sequential native carrier losses with exact cumulative prefix accounting. The
  direct-UDP and forced-TCP cells require two loss/reassignment/stale-terminal/recovery/restart
  cycles, one bounded request-hold release, final return to the initially stopped identity, zero
  discard/fallback, and complete reconstruction/activation (ADR 0232 and
  `evidence/2026-08-29-sandwurm-sync-range-repeated-route-loss.md`).
- [x] Qualify three sequential native carrier losses as a separate bounded topology. The
  `sync-file-range-triple-route-loss` gate requires three complete handoffs, two request-hold
  releases, final carrier inequality with the initially stopped identity, and that identity ready
  after two restarts with its restart budget exactly exhausted. Direct-UDP proof `pair.3iufekzy`
  retains/resumes 862,359 bytes and forced-TCP proof `pair.zleebk2k` retains/resumes 871,956 bytes;
  both pass strict raw and compact verification with zero discard/fallback. Diagnostics successively
  exposed the inherited restart/deadline
  bound, recovery rearm latch, and finally the one-shot auxiliary handshake race; ADR 0236 closes
  the latter with exact-record retransmission. A fifth diagnostic then reached the hidden four-entry
  scheduler fence-history ceiling; ADR 0237 makes that policy-bounded and grants this cell exactly
  five records. ADR 0238 separates signed restart ceiling from derived remaining capacity (ADR 0235
  and `evidence/2026-08-29-sandwurm-sync-range-triple-route-loss.md`).
- [x] Bind a range-bundle prefix to its exact locally derived plan across daemon restart. One formerly
  reserved ATM1 byte distinguishes historical route/worker records from plan-bound range records;
  the latter commit the complete plan digest and bundle length without changing record size or wire
  framing. Startup retains only strict positive incomplete plan-bound bytes, a fresh authorized pull
  must derive the identical plan, and mismatch/legacy/final-bundle cases fence. Deterministic
  persistence and subscriber convergence pass (ADR 0239).
- [x] Qualify range-bundle daemon-restart continuation on genuine direct UDP and forced TCP. Require
  a positive prefix before unclean receiver exit, stable device/Tox/savedata identities, a distinct
  explicit authorized pull, fresh attempt/message/FileId identities, exact retained/resumed equality,
  suffix-only transfer, complete target verification, HEAD-last acceptance, and explicit activation
  (`sync-file-range-restart-resume`, ADR 0239). Compact proofs `pair.xg41pthc` and `pair.00992erw`
  retain/resume 281,055 direct-UDP or 276,942 forced-TCP bytes and fetch only their exact suffixes
  after both peers re-establish authority; both raw and compact forms pass strict verification
  (`evidence/2026-08-29-sandwurm-sync-range-restart-resume.md`).
- [x] Add deterministic corrupt target-object repair as an explicit local maintenance action.
  `sync-repair NAMESPACE` verifies the strict digest-named object store and quarantines only private
  regular final objects whose content digest conflicts with their identity. Ambiguous entries remain
  terminal errors, and pull convergence never deletes optimization bases automatically.
- [x] Prove genuine corrupt target-object repair over direct UDP and forced TCP. Fsync the deliberate
  mismatch, quarantine it without changing signed acceptance or activation, explicitly recover the
  same authorized revision, preserve the quarantine copy, and require a clean second scan. Retain
  exact bindings in `evidence/2026-08-23-sandwurm-sync-repair.md`.
- [x] Implement and qualify quarantine-only unreachable-object collection. `sync-gc NAMESPACE
  dry-run|quarantine` accepts no path and has no unlink/purge mode; it authenticates guarded roots,
  freezes and revalidates descriptor identities, refuses links/substitution/mount crossings, reports
  exact moved versus durable prefixes, and passes the genuine two-guest outside-sentinel gate (ADR
  0149 and `evidence/2026-08-24-sandwurm-sync-gc-quarantine.md`).
- [x] Publish one deterministic directory under signed `treepack-v1` policy, reject unsafe or
  unbounded source trees, transfer the whole canonical artifact, commit signed activation before
  derived projection, atomically switch a verified read-only tree, reconcile exact retry, recover
  abandoned staging, and prune noncurrent projections. Deterministic and genuine direct-UDP/
  forced-TCP gates pass (ADR 0139 and `evidence/2026-08-24-sandwurm-sync-tree.md`).
- [x] Recover canonical abandoned pointer temporaries without partial cleanup and terminate a real
  child process after each of eight projection effects. Every cell exposes only the complete old or
  complete new tree, and exact retry from a fresh child leaves one canonical current revision (ADR
  0140).
- [x] Prove genuine directory rollback/fork refusal and ENOSPC recovery over direct UDP and forced
  TCP. Stale and equal-generation fork HEADs preserve signed and visible truth; an exact duplicate
  activation recovers projection after removing only the disk filler.
- [x] Prove bounded publisher-worker saturation and recovery over both carriers. A queue bound of one
  retains active and queued jobs, refuses one additional namespace job without stalling the transport
  pump, then converges both retained namespaces by exact retry (ADR 0141 and
  `evidence/2026-08-24-sandwurm-sync-tree-pressure.md`).
- [x] Prove whole-store byte-quota refusal over both carriers. Each new candidate object individually
  exceeds the exact remaining byte budget; failure leaves no candidate object or staging residue and
  preserves accepted, activated, and visible predecessor truth
  (`evidence/2026-08-24-sandwurm-sync-tree-quota.md`).
- [x] Prove whole-store object-count refusal over both carriers with independent byte headroom. The
  accepted tree reaches the six-object ceiling exactly; neither successor object lands and all
  signed/visible predecessor truth survives (ADR 0142 and
  `evidence/2026-08-24-sandwurm-sync-tree-object-quota.md`).
- [x] Prove real read-only-storage refusal and exact recovery over both carriers. Pull fails at
  persistent transaction setup before object requests; activation fails without moving signed or
  visible truth; explicit retries after read-write remount converge and activate the exact successor
  (ADR 0143 and `evidence/2026-08-24-sandwurm-sync-tree-read-only.md`).
- [x] Measure genuine directory publication/convergence/projection process high-water over both
  carriers. A 128-entry, 7,616,908-byte successor remains below the 65,536 KiB construction ceiling;
  both receipts bind phase values and exact baseline deltas (ADR 0144 and
  `evidence/2026-08-24-sandwurm-sync-tree-memory.md`).
- [x] Prove publisher-source corruption refusal and exact recovery over both carriers. Request-time
  verification emits no corrupt offer, subscriber generation 1 remains authoritative, explicit
  repair quarantines 2 objects/4,981,169 bytes, duplicate publication reconstructs the same signed
  generation 2, and explicit retry converges (ADR 0145 and
  `evidence/2026-08-24-sandwurm-sync-tree-source-corrupt.md`).
- [x] Prove destination-corruption refusal and selective retry for directory convergence and
  projection. Pause after positive artifact progress, fsync-corrupt the exact private transport
  temporary, reject it at complete staged SHA-256 verification, preserve signed/visible predecessor
  truth and the independently committed valid manifest, then request only the missing artifact on an
  explicit fresh pull before HEAD-last acceptance and exact-token activation (ADR 0146 and
  `evidence/2026-08-24-sandwurm-sync-tree-destination-corrupt.md`).
- [x] Prove exact duplicate/reordered-control handling and conflicting replay refusal over both
  carriers. Two replayed object requests return retained results behind already-admitted file lanes
  without additional offers; a later replayed HEAD returns its retained result without cascading new
  object requests; same-ID/different-payload HEAD reuse is refused exactly once without poisoning
  convergence. Both roles bind exact journal/counter deltas, HEAD-last acceptance, and explicit
  activation (ADR 0147 and
  `evidence/2026-08-24-sandwurm-sync-tree-control-replay.md`).
- [x] Qualify one complete source on the genuine provider over direct UDP and forced TCP. One paged
  4 MiB revision converges in a single pull with zero failure, canonical whole-artifact/root CAS,
  signed-HEAD-last acceptance, and explicit activation in both simultaneous source-linked Sandwurm
  guests (ADR 0252 and `evidence/2026-08-29-sandwurm-sync-content.md`).
- [x] Qualify multiple sources on the genuine provider over direct UDP. Multi-route striping remains
  an evidence-driven optimization, not an integration prerequisite. ADR 0242 freezes source authority;
  ADR 0244 freezes the initially dark feature bit 29, canonical types 28/29, exact local CAS resolution, a
  bounded flat/paged coordinator, subscriber-gated publisher service, deterministic two-source
  scheduling, disappearance fencing, and exact reconstruction. ADR 0245 adds dark exact sparse
  availability types 30/31 and deterministic even/odd complementary-store convergence. ADR 0246
  adds strict physical CAS inventory and combined flat-plus-CAS quota enforcement. ADR 0247 derives
  canonical private roots and makes both standalone root-manifest commits and coordinator page/chunk
  commits verify exact staging bytes under prospective combined quotas. ADR 0248 adds the signed
  CTA1 restart journal: every assignment binds its frozen HEAD, object, FileId, source, and carrier
  before effect; restart commits only exact complete staging and fences partial/absent work without
  reviving a carrier. ADR 0249 now gives `sync-publish` a real flat/paged content product path: it
  preflights the complete deduplicated fabric, imports every object through verified-copy CAS commit,
  and signs HEAD last. Startup recovers both exact abandoned local publication workspaces and CTA1
  state. ADR 0250 adds root-manifest kind 3 and a bounded one-source subscriber which persists CTA1
  before every receive, holds early offers until their result, reconstructs whole-artifact CAS, and
  advances accepted HEAD last. ADR 0251 closes the deterministic Agent product gate: startup
  authenticates the complete persisted live graph before dynamic bit-29 advertisement; primary
  packet/FileId/terminal dispatch converges one paged revision through real Agent control and mock
  toxcore; accepted HEAD still lands last; exact-token activation rechecks content CAS; and
  engine-aware repair plus authenticated quarantine-only GC are live. ADR 0254 adds the explicit
  owner-local `sync-source-add JOB_ID FRIEND` entrance, consumes exact sparse windows from every
  independently authorized primary peer, and binds each selected request/FileId/CTA1/terminal chain
  to that source while the original HEAD remains frozen. Two complementary authenticated stores now
  converge through the product receiver. The owned registry had 670 checks at that boundary and
  contains 711 at the current tree. ADR 0252 qualifies the one-source product path through genuine c-toxcore on direct UDP and
  forced TCP with exact paged-fabric evidence retained in strict compact proofs. ADR 0255 accepts
  genuine direct-UDP convergence from two complementary live sources: both answer exact availability
  and contribute object traffic before reconstruction, HEAD-last acceptance, and explicit activation.
  The same bounded three-agent construction does not qualify over forced TCP: one common discovery
  domain and two publisher-specific relays produce four stable relay sockets and a confirmed primary
  friendship, but the secondary friendship does not confirm within 900 seconds. This is a topology-
  specific falsification, not a universal c-toxcore limit. Nine later bounded variants separate
  relay count, serialized admission, ordinary pending-request acceptance, reusable-key
  pre-provision, full-address rendezvous, and bootstrap/relay placement. Instrumented failures prove
  the secondary is Tox-offline with zero IoTox HELLO attempts, not merely missing authority. The
  strongest hybrid briefly crosses the secondary TCP/confirmed checkpoint, then stays offline for
  the complete 300-second authority window. No content pull begins. These variables are therefore
  falsified as sufficient fixes; the remaining boundary is durable second-session rendezvous for
  one subscriber identity in this local c-toxcore construction (ADR 0255).
  ADR 0256 adds local-control v1.41's
  atomic `sync-pull-multi` entrance and accepts a destructive direct-UDP companion: selected-source
  loss fails and cleans the whole first job, the same secondary identity reconnects at a higher
  epoch, and only a distinct explicit atomic pull may converge. Two verified CAS objects and 528
  verified bytes survive as immutable prerequisites; accepted HEAD, activation, staging, and
  ambiguous attempt truth do not. ADR 0257 adds local-control v1.42 operation 89 and a separately
  device-authenticated `replica-heads/` store. A partial source may now retain one exact foreign-
  writer chain as availability-only state, advertise its present immutable objects after cold
  start, and root those present objects for GC without becoming publisher, accepted HEAD, or
  activation authority. ADR 0258 now construction-enables exact auxiliary content carriers without
  changing content framing: every source keeps a primary authority/HEAD session, while pre-HEAD
  owner-local binding freezes its availability/object/FileId/CTA1 lane to one independently proved
  route-worker incarnation. Deterministic complementary-source convergence uses two auxiliary
  carriers, rejects principal substitution and post-HEAD rebinding, and fails closed on exact carrier
  loss. Local-control v1.43 operation 90 exposes one atomic named-class entrance. The first genuine
  routed-content cell now passes: direct-UDP primary authority/HEAD remains native while one exact
  `tox/tor` worker carries and activates the paged 4 MiB revision through two actual Tor processes
  in one pull with zero failures or reassignment. Compact proof `pair.fahovlrg` keeps the two route
  claims separate (ADR 0258).
- [x] Qualify the one-source named-class entrance before expanding the topology. Two simultaneous
  Sandwurm guests negotiate bit 29 on exact reciprocal Tor workers, keep primary authority and HEAD
  on direct UDP, bind the pulling carrier key, converge four chunks/one page/four objects, accept
  HEAD last, and explicitly activate. The gate also found and repaired startup-order suppression of
  worker bit 29; service-derived capability is now finalized before worker start and immutable
  afterward. See `evidence/2026-08-30-sandwurm-sync-content-actual-tor.md`.
- [x] Qualify genuine mixed-route multi-source convergence without confusing the primary authority
  path with the auxiliary byte path. Use direct native primary sessions for every independently
  authorized source and distinct `tox/tor` or `tox/i2p` route-worker identities for content. Retain
  primary HEAD dispatch, exact route-worker incarnations, both positive availability/object source
  contributions, FileId/CTA1 joins, HEAD-last acceptance, and explicit activation. Do not repeat the
  thirteen single-subscriber forced-TCP rendezvous variants from ADR 0255: that topology's durable
  second friendship is no longer the byte-carrier prerequisite. The positive gate must prove one
  named auxiliary class end to end; selected-worker loss is its now-qualified destructive companion. The
  required one-source `tox/tor` precursor is complete. Accepted compact
  proof `pair.j0z04_2i` now closes the positive gate: two independently authorized native publishers
  contribute five-plus-one objects through distinct exact Tor worker identities in one atomic pull;
  strict per-source status binds both principals/carriers, the primary alone supplies HEAD, explicit
  activation succeeds, and both TAP captures show zero unexpected-context packets (ADR 0259 and
  `evidence/2026-08-30-sandwurm-sync-content-multi-route-actual-tor.md`). The device-side workers
  share one Tor process, so this does not claim circuit or physical-path diversity.
- [x] Fault one selected actual-Tor content worker after positive complementary-source progress.
  Compact proof `pair.w31xqgd_` stops lane 2 at 72,663 bytes, records two committed objects and 528
  fetched bytes, fails the whole job with clean staging/no accepted HEAD/no activation, reports one
  carrier loss and zero reassignment, recovers the same signed route under a different worker with
  both native epochs unchanged, and converges only through a distinct explicit pull (ADR 0260 and
  `evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss.md`). Compact proof `pair.i8ar90tx`
  repeats the unchanged gate through `205.185.115.131:443`, faults at 76,776 bytes, and independently
  verifies the same boundary with new worker/job/circuit identities (ADR 0261 and
  `evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss-second-relay.md`).
- [x] Freeze and qualify bounded same-source content concurrency without changing framing. The
  default remains one lane; `--max-sync-content-lanes 2` may opt a process into two, while the signed
  namespace `maximum-lanes` and `maximum-outstanding-requests` can only tighten that ceiling. Root
  manifest and signed HEAD remain serial; only immutable page/chunk receives overlap. Deterministic
  tests prove out-of-order completion, immediate slot refill, exact request/FileId attribution, and
  whole-job sibling cancellation on one lane failure. Genuine source-linked Sandwurm proofs
  `pair.895m5lwy` (direct UDP) and `pair.bcecui0l` (forced TCP) each observe two simultaneously
  admitted lanes from one authenticated source, two distinct request IDs/FileIds, no root lane, and
  exact convergence plus activation (ADR 0262 and
  `evidence/2026-08-30-sandwurm-sync-content-same-source-lanes.md`). This is object concurrency on
  one Tox session, not byte striping or physical-path diversity.
- [x] Measure same-source lane caps `1/2/4/8` without daemon/session churn. One stable cap-8 client,
  four isolated signed namespace ceilings, the same deterministic high-entropy 8 MiB/24-chunk graph,
  and the same 4 Mbit/s subscriber shaping pass over direct UDP and forced TCP. Direct UDP records
  378,035/325,771/399,838/443,138 B/s; forced TCP records
  301,423/375,833/420,481/415,072 B/s. Cap 4 is the smallest observed forced-TCP sweet spot (+39.5%
  over cap 1); cap 8 adds no TCP gain, and the non-monotonic one-sample direct result is not a default
  argument. Keep default one. Compact proofs `pair.amcrp0_3` and `pair.805kzu4a` independently
  reverify (ADR 0263 and
  `evidence/2026-08-30-sandwurm-sync-content-lane-science.md`). Counterbalanced repetition,
  multi-lane client-daemon restart, and same-source auxiliary-path distribution are qualified
  separately below.
- [x] Measure competing Ratox latency on the same shaped content session without replacing the
  terminal. One 720-sample attachment spans content caps 1, 4, and 8; cap 2 remains a transfer-only
  control during a deliberate pause. Direct UDP and forced TCP retain one terminal identity and
  Tox epoch through all phases. Cap 4 is the smallest simultaneous-Ratox throughput winner in both
  accepted cells; cap 8 regresses against cap 4 and worsens p95 terminal latency on both routes.
  Owner-queue p95
  remains far below end-to-end p95, localizing the dominant observed tail beyond local command
  scheduling without assigning a single carrier cause. Keep default one and Ratox framing frozen.
  Compact proofs `pair.af873531` and `pair.a3nglkh3` independently reverify (ADR 0264 and
  `evidence/2026-08-30-sandwurm-sync-content-ratox-latency.md`).
- [x] Repeat lane/load phases in counterbalanced orders before naming a bulk recommendation. The
  finalized `1,2,4,8` and `8,4,2,1` cells pass on direct UDP and forced TCP with one process/session,
  identical 8 MiB content, 4 Mbit/s shaping, exact signed caps, zero restarts, and four activations.
  Paired UDP means are 406,943/423,197/439,476.5/443,054.5 B/s; paired TCP means are
  295,899/370,799/354,623/294,106.5 B/s. Cap 2 and cap 4 differ by only 0.013% in the four-cell
  aggregate, while cap 2 uses 14.8% fewer CPU ticks. Keep default one; recommend explicit cap 2 for
  latency-insensitive mixed/relay-heavy bulk, cap 4 for controlled direct UDP, and cap 8 only as a
  stress bound. No automatic profile is qualified. Compact proofs `pair.t6b6exf1`, `pair.ku2fxml0`,
  `pair.70p2plez`, and `pair.o_6q_m1n` feed the verifier-backed canonical report (ADR 0266 and
  `evidence/2026-08-31-sandwurm-sync-content-lane-counterbalance.md`).
- [x] Qualify fresh Ratox OPEN admission after reliable bulk backlog as a separate lifecycle gate.
  Compact proofs `pair.614f4nje` (direct UDP) and `pair.oengulmm` (forced TCP) send a new OPEN within
  149/825 ms of cap-8 completion, return OPENED in 42/75 ms on unchanged carrier-specific epoch 1,
  start fresh generation and byte positions at one, and complete 40 exact samples below 22/162 ms
  maximum RTT. The ordinary five-second admission deadline remains unchanged; Ratox framing stays
  frozen (ADR 0265 and
  `evidence/2026-08-30-sandwurm-sync-content-ratox-post-bulk-admission.md`).
- [x] Qualify client-daemon restart with cap 2 and cap 4 while multiple immutable-object lanes are
  live. Four final-tree Sandwurm cells reach the exact cap with distinct request/FileId rows, then
  `SIGKILL` only the subscriber Agent while two or four c-toxcore transport temporaries contain
  positive bytes. Startup preserves the exact two-object/1,328-byte verified CAS inventory, removes
  every exact transport temporary, leaves zero canonical partials, fences the old signed attempt
  set, and accepts no HEAD or activation. After both roles independently recover authority, only a
  distinct explicit job converges and activates. Compact proofs `pair.8j7v2irm` and `pair.9q9hsx40`
  cover direct UDP; `pair.8ulddb9t` and `pair.ol5goyug` cover forced TCP (ADR 0267 and
  `evidence/2026-08-31-sandwurm-sync-content-restart.md`). Partial-prefix resume, same-job
  continuation, and power-cut behavior remain unclaimed.
- [x] Measure persistent Ratox at cap 2 and freeze an interactive SLA before naming an interactive
  bulk profile. Before either carrier cell, freeze at least 40 exact-overlap samples, p50 at most
  250 ms, p95 at most 500 ms, p99 at most 1,000 ms, maximum at most 1,500 ms, and owner-queue p95
  at most 10 ms. One 960-sample attachment then spans ordered caps `1/2/4/8` under unchanged
  4 Mbit/s shaping and one Tox epoch. Cap 2 passes every bound over both direct UDP and forced TCP;
  cap 4 and cap 8 miss p95 on both. Cap 2 improves rate over cap 1 by 2.75%/9.92%, while cap 4 adds
  only 1.11%/2.86% over cap 2. Keep default one; name explicit cap 2 only as the bounded native
  interactive-bulk construction profile. No pacing change is justified by this gate. Compact proofs
  `pair.rpblreul` and `pair.rwiyixfh` independently reverify (ADR 0268 and
  `evidence/2026-08-31-sandwurm-sync-content-ratox-cap-2-sla.md`).
- [x] Qualify same-source content object distribution across independently authenticated auxiliary
  paths. Repeated source selectors in `sync-pull-multi-route` now atomically choose distinct exact
  ready carriers for one stable principal and primary authority session. Compact proof
  `pair.iiuhmhy0` commits one 272-byte object on route A and five objects/4,194,560 bytes on route B,
  returns all four availability results, accepts the original HEAD last, activates explicitly, and
  preserves two legitimate route-local `friend=0` values without aliasing. Both workers per guest
  share one Tor process and relay target; this is whole-object logical-carrier distribution, not
  one-session lane concurrency, byte striping, balancing, speedup, circuit/physical diversity, or
  failover (ADR 0269 and
  `evidence/2026-08-31-sandwurm-sync-content-same-source-multi-route.md`).
- [x] Design and qualify durable authenticated replica HEAD persistence distinct from locally
  published HEAD state. `sync-replica-import NAMESPACE SIGNED_HEAD_PATH` verifies the foreign
  signature, complete manifest graph, current writer policy, same-writer linked advance, and one
  fixed device custody signature. Publication remains absent; accepted/activated state remains
  separate; replica-only missing chunks are lawful while missing metadata closes GC. The selected-
  source-loss Sandwurm gate cold-starts the partial source from this store with no reinjection,
  requires a consistent zero-candidate GC plan, then completes only through the already-qualified
  higher-epoch distinct-job recovery. Raw and compact proof `pair.w_ws202c` passes strict replay
  (ADR 0257 and
  `evidence/2026-08-30-sandwurm-sync-content-replica-restart.md`).

Exit: two authorized IoTox Sandwurm guests converge one named immutable file or deterministic directory
revision after disconnect and restart, verify its signed HEAD and complete bytes, and atomically
activate it without friendship-derived authority, rollback, partial publication, or unbounded state.

## M5C — everyday synchronization (complete for founding-machine scope)

Turn M5B's explicit immutable-revision machinery into unattended one-writer/read-only replicas, then
add a causal pairwise writable directory without weakening authority, HEAD-last/CAS-first ordering,
or recipient-local path control. The complete contract and ordered qualification gates live in
`everyday-sync-plan.md`.

- [x] Freeze and implement one stable-device-signed, generation-bound automation record per
  namespace. Support `disabled`, periodic local `publish`, and stable-principal-bound `follow` modes;
  make exact reload idempotent and replacement explicit.
- [x] Add a deterministic bounded scheduler with one periodic and one activation action per
  namespace, immediate first reconciliation, exponential retry, stale-generation completion fencing,
  content-free counters, and no work on the Agent service thread.
- [x] Expose owner-only `sync-auto-publish`, `sync-follow`, `sync-automation`, and
  `sync-automation-remove`. A follower must capture a current authorized stable principal rather than
  a friend number; `verified` may invoke only the existing exact-accepted-HEAD activation transaction.
- [x] Add `sync-create NAMESPACE PATH [INTERVAL_SECONDS]` as the ordinary managed sole-writer
  entrance and `sync-share NAMESPACE FRIEND read-only` as a RecallRoot-signed exact-principal grant
  plus subscriber-membership transaction. Preserve recipient-local path/activation choice and keep
  the linear peer framing unchanged (ADR 0271).
- [x] Wire automatic publication, pull, and optional verified activation through the existing bounded
  sync worker. Keep peer framing, sync authority, primary-route defaults, and manual controls
  unchanged.
- Local restart qualification now proves automatic duplicate-safe publication and successor scans
  through the live Agent. The complete-path test also proves stable-principal capture, automatic
  paged-CAS pull, HEAD-last acceptance, and exact verified activation without a manual pull or
  activate command. ADR 0270 records the 674-check baseline.
- [x] Prove codec/store tamper refusal, unsafe-path refusal, backoff bounds, duplicate scans,
  principal rebinding refusal, stale activation tokens, policy replacement during work, and restart
  recovery in deterministic tests.
- [x] Qualify a two-guest Sandwurm source-mutation/restart cell with no manual publish, pull, or
  activation command after policy installation. Direct-UDP compact proof `pair.7vk1u4wn` and
  forced-TCP compact proof `pair.s67dd_2e` each join three exact generations, one independent Agent
  restart and signed automation-policy reload per role, and zero post-setup manual transfer commands
  (ADR 0276 and `evidence/2026-09-01-sandwurm-sync-automation.md`).
- [x] Run an hours-long shadow mirror beside the incumbent synchronizer and compare canonical
  manifests before using IoTox as the sole synchronization path for one noncritical directory.
  Networkless Sandwurm proof `run.XXdpLNPh` records 240 exact IoTox/Resilio cycles over 7,200,096 ms,
  twelve alternating Agent restarts, zero post-setup transfer commands, and 356 replay-window
  evictions (ADRs 0282--0283 and
  `evidence/2026-09-01-sandwurm-iotox-resilio-shadow.md`). Versioned recovery
  custody remains required.
- [x] Freeze and implement the local `tree-v2` construction: canonical per-file CAS manifests,
  independent signed writer branches, exact retained observation proofs, order-independent causal
  merge, provenance-bearing conflicts, signed tombstones, visible-frontier workspace causality,
  atomic whole-directory exchange, and signed pending-exchange recovery (ADR 0272).
- [x] Prove locally that concurrent edits and delete-versus-edit preserve both outcomes, invented
  foreign provenance is refused, and an ordinary later edit resolves a conflict causally. Keep
  delete-everywhere and permanent purge disabled.
- [x] Freeze bounded tree-v2 inventory/record/manifest/object peer frames and authority-gated durable
  receive state. A branch is accepted only after every referenced proof, manifest, and required CAS
  object is locally verified. Exact request replay binds the authority/session epoch; failed lanes
  clean their staging and bounded terminal jobs cannot exhaust admission.
- [x] Add bounded tree-v2 exact-object pipelining without changing the frozen frames. ADR 0329 lets
  one pull keep up to the minimum of process `--max-sync-tree-lanes`, namespace `maximum-lanes`, and
  namespace `maximum-outstanding-requests` active file-object requests, with `sync-status` exposing
  `tree-lane-cap`, `active-lanes`, and `tree-lane-job=` bindings.
- [x] Add recipient-local read-write setup, pair-bound bidirectional automation, content-free status,
  unique-object repair, and the actual `sync-create ... read-write` plus reciprocal
  `sync-share ... read-write` ceremonies (ADR 0273). Neither peer selects the other's path.
- [x] Replace the pair-only local automation binding with signed format v2: a canonical bounded set
  of at most 15 remote stable principals, additive idempotent shares, one serialized namespace lane,
  fair due-peer selection, and independent retry clocks. Keep all tree-v2 peer framing unchanged
  (ADR 0274).
- [x] Prove three-writer merge order independence across all six frontier arrival orders, then run
  three genuine source-linked daemons through three friendship edges, six directional RecallRoot
  grants, concurrent offline edits, deterministic two-alternative conflict preservation, and one
  explicit causal resolution. Retain only content-free identity commitments (ADR 0274 and
  `evidence/2026-08-31-sandwurm-sync-three-writer.md`).
- [x] Add negotiated format-2 checkpoint floors, multi-branch/conflict/tombstone reachability,
  explicit pins, workspace-manifest roots, recoverable quarantine/restore, exact terminal writer
  cutoffs, and one-candidate-per-writer/16-candidate-per-path bounds. Preserve ordinary format-1
  branch and peer-frame bytes, refuse checkpoint inventory without feature bit 31, and retain no
  permanent-purge command (ADR 0275).
- [x] Stop acknowledgement-only branch echo. A remote-only merge retains its derived manifest under
  the signed workspace journal without claiming a new authored event; the next real edit observes
  that journal's exact frontier (ADR 0275).
- [x] Run the accelerated networkless three-writer lifecycle in one 2-vCPU/2-GiB Sandwurm/KVM cell:
  24 rotating edits, remote checkpoint propagation, exact pin/unpin, recoverable graph quarantine
  and restore, matching local cutoff on both survivors, and refused retired-writer re-entry. Retain
  compact proof `run.XXiFEDeB` and the exact intermittent pending-exchange nonclaim
  (`evidence/2026-09-01-sandwurm-sync-three-writer-lifecycle.md`).
- [ ] Accept the real 24-hour three-writer writable soak before promoting sync beyond noncritical
  working directories. ADR 0361 added the duration-bound soak, ADR 0364 retained interrupted partial
  evidence, and ADR 0367 hardened late-soak rejected evidence plus stalled-cycle recovery. The first
  24-hour attempt reached 72 completed soak cycles before rejecting at cycle 73 with one node behind
  the synthetic projection. The first clean hardened rerun exposed that the original five-second
  cadence was a high-churn stress profile, not the desired 24-hour reliability soak; ADR 0368 moves
  `soak-24h` to a four-minute cadence and leaves high-churn stress as separate future science. ADR
  0369 fixes cadence-aware live status. The first retuned candidate reached cycle 10 cleanly, then
  stalled at cycles 19 and 20 and exposed a shutdown-time rejected-receipt bug fixed by ADR 0370.
  ADR 0371 disables emergency stalled-cycle restarts in the primary 24-hour profile and raises the
  hard per-cycle timeout to 900 seconds. That passive candidate reached 71 completed cycles and one
  full planned restart rotation before rejecting when the cycle-72 restart hit the active writer
  immediately after its fresh edit; ADR 0372 moves scheduled restarts before the cycle edit and
  records `soak_restart_phase`. A restart-before-edit smoke from
  `290023c8fef1a858952ed12e4eb2eea0e5d142fe` accepted, but the representative 24-hour rerun at
  `.sandwurm/lab/three-writer-soak-24h/run.Ym8xWhvm` rejected shortly after the cycle-48 restart
  because periodic `sync-repair` landed on the same cycle as scheduled daemon churn and node `c`
  hit a local control-response deadline. Its retained receipt showed aligned content-free
  projections and no data divergence. ADR 0373 makes `sync-repair` control deadlines explicit and
  defers soak repair from scheduled-restart cycles in the primary 24-hour profile, while requiring
  accepted receipts to drain deferred repair before completion. A clean ADR 0373 `soak-smoke`
  accepted at `.sandwurm/lab/three-writer-soak-smoke/run.cnowmx9v` from source commit
  `7dc73d1690696435ae91891b82ac83c14609cfc7`. The following clean candidate at
  `.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC` reached cycle 23 and then rejected after the
  cycle-24 restart-before-edit of node `a`; its retained receipt showed nodes `a`/`b` aligned on
  cycle 23 and node `c` holding cycle 24, with matching store shape and zero conflict alternatives.
  ADR 0374 therefore adds explicit `repair-before-edit` restart-settle evidence before each
  post-restart synthetic edit. A clean ADR 0374 `soak-smoke` accepted at
  `.sandwurm/lab/three-writer-soak-smoke/run.dvdqSlPg` from source commit
  `a403ebc6608305ec2ea29c9f6f9832c298e6f691`, with two restart-settle passes,
  two deferred repairs drained, zero stalled-cycle recoveries, retained recovery, storage-fault,
  and VM-smoke verification. The corrected 48-hour-budget 24-hour candidate
  `.sandwurm/lab/three-writer-soak-24h/run.hlBeElr6` reached cycle 143 with six restart-settle
  passes and then rejected at cycle 144 with node `a` one projection behind nodes `b`/`c`, zero
  conflict alternatives, and no stalled-cycle recovery because the ADR 0371 profile disabled it.
  ADR 0375 changes the active VM-only gate to use a recorded 600-second stalled-cycle recovery
  threshold before the 900-second hard timeout while still requiring exact convergence and
  `soak_stalled_restart_after_ms = 600000` in accepted receipts. Compact proof
  `.sandwurm/exports/three-writer/run.9nqvO8B2` supplied the first accepted
  24-hour receipt; ADR 0403 refreshes the current proof to
  `.sandwurm/exports/three-writer/run.2nPKtCoX`.
- [x] Add versioned recipient-local selective sync and richer metadata policy. ADR 0278 freezes
  canonical component-prefix includes/excludes with exclude-wins semantics, preserves excluded local
  files and hidden baseline causality across atomic exchange, and adds manifest-v2 exact private
  owner `r/w/x` modes. Existing namespace/manifest v1 bytes and complete-tree defaults remain valid;
  local/CLI/live-Agent tests cover the projection boundary. ADR 0295 now applies the same policy to
  content acquisition and graph GC while retaining and verifying the complete signed metadata
  graph. ADR 0296 then combines complementary authorized primary-lane sources through the existing
  exact object-result dispositions while keeping one primary frontier authoritative. ADR 0297
  persists the resulting selected-custody, convergence, conflict, automation, pressure, cutoff, and
  source facts as one content-free signed health record without backup or rollback-witness claims.
- [x] Finish the dedicated two-guest `sync-bidirectional` Sandwurm cell: reciprocal owner setup,
  both daemons stopped for concurrent unequal edits, restart, deterministic conflict preservation,
  later causal resolution, deletion, zero-byte object, and repair without manual publish/pull.
  Retained compact proof `pair.ms5zsk9l` passes the independent verifier (ADR 0273 and
  `evidence/2026-08-31-sandwurm-sync-bidirectional.md`).
- [x] Qualify every named durable crash edge, same-writer malicious forks, bounded conflict storms,
  the 4,096-entry tree ceiling, long-offline/cutoff writers, reconnect-order permutations, and an
  hours-long real-directory shadow. ADR 0281 freezes the finite adversarial matrix; ADR 0283 accepts
  its shared duration proof. No wall-clock last-writer-wins rule is used.

Exit: after owner-local setup, the one-writer product survives disconnect/restart and the bounded
full-mesh writable product preserves concurrent offline changes, converges a deterministic ordinary
tree, retains losing values with provenance, and resolves only through a later causal edit. Both
operate without manual publish/pull and without friendship-derived authority or remote path
selection.

## M6 — safe mutable device state (complete for founding-machine scope)

Choose one low-consequence target and one idempotent desired-state mutation. The construction slice
uses Tox presence because it exercises a real provider effect and savedata without claiming a
physical output:

- [x] Freeze `profile.status.set available|away|busy` as one bounded durable operation with
  `write.settings`, fixed ICQ1/IPS1 records, provider readback, and no expiry.
- [x] Commit lifecycle before effect, propagate atomic provider-savedata failure before success,
  leave uncertain effects `STARTED`, replay terminal duplicates without effect, and permit
  interrupted recovery to reapply only the exact desired value.
- [x] Fence interrupted recovery to the same stable principal and ownership epoch under a fresh
  exact-head authorization proof.
- [x] Stop the separate-process mock inside the post-effect/pre-savedata window, kill it, restart,
  and prove exact desired-state convergence plus terminal evidence.
- [x] Prove bilateral authorized provider convergence between two genuine source-linked Sandwurm
  guests over direct UDP and forced TCP (ADR 0148 and
  `evidence/2026-08-24-sandwurm-mutable-profile-status.md`).
- ~~Select and qualify representative physical hardware, including power-cut, rollback, resource,
  latency, and wear.~~ **Retired from repository scope by ADR 0277.**
- ~~Require a focused independent safety/security review for repository completion.~~ **Retired
  from repository scope by ADR 0277; it remains welcome downstream evidence.**

No lock, medical, fire, vehicle, or industrial-safety claim belongs in this milestone. Tox presence
is presentation state and does not satisfy the representative-hardware exit.

Exit: the source-linked presentation-state identity-to-effect path passes deterministic, process,
and two-guest Sandwurm qualification. Physical and safety-adjacent effects remain unsupported rather
than becoming repository gates (ADR 0277).

## M7 — signed bulk data and OTA (complete for founding-machine scope)

Layer immutable artifact identity, signed manifests, digest verification, reservation, resume,
anti-rollback, staged install, health confirmation, and recovery above Tox file transfer. Received
bytes never gain execution authority merely by arriving.

- [x] Keep update intent separate from sync delivery and activation; freeze a canonical fixed-size
  release-signed manifest over namespace, target, sequence, version, payload kind, size, and digest
  (ADR 0184).
- [x] Pin release signers, target, slot root, payload ceiling, and health interval in strict
  owner-private local policy; remote content cannot nominate its own trust or effect policy.
- [x] Bind staging to one exact accepted sync HEAD and artifact, independently reverify the bundle,
  and copy only inert payload bytes into a digest-named immutable inactive slot.
- [x] Commit stable-device-signed staged, pending-restart, awaiting-health, confirmed, and rollback
  state; recover both directions of the pointer/state crash window and refuse rollback below the
  confirmed sequence (ADR 0185).
- [x] Require a later durable Agent incarnation and exact one-use token for bounded health
  confirmation; automatically return to the last confirmed slot on expiry or a second restart.
- [x] Expose default-off local policy/bundle/stage/apply/status/confirm controls and deterministic
  unit, process-exit, CLI, and real-Agent lifecycle tests.
- [x] Qualify one exact 4 MiB inert update lifecycle between genuine Sandwurm guests over direct UDP
  and forced TCP while proving feature bit 20 remains dark
  (`evidence/2026-08-26-sandwurm-signed-update.md`).
- [x] Freeze `ICQ2`/`IUS1` and implement remote `update.stage` with exact current
  `install.firmware` authority, bilateral feature dependencies, durable replay/restart, existing
  admission quotas, pre-first-send cancellation truth, and signed audit records (ADR 0186).
- [x] Advertise `signed-ota-v1` only after local update construction succeeds, reject unnegotiated
  execution, and qualify the exact remote-stage-to-local-confirm lifecycle between genuine
  Sandwurm guests over direct UDP and forced TCP
  (`evidence/2026-08-26-sandwurm-remote-update-stage.md`).
- [x] Add owner-local update policy v2 with a positive signer-policy epoch and bounded revoked
  release-signer set. Active and revoked keys must be canonical and disjoint; a rotated policy rejects
  future bundles signed by a retired key without changing the signed bundle format or retroactively
  reinterpreting already staged/confirmed state (ADR 0187).
- [x] Add no-clobber release signer creation/public inspection, reviewable add/overlap/retire policy
  transitions, and the documented offline custody ceremony. Add explicit dry-run/recoverable
  quarantine for historical slots while protecting signed confirmed/candidate state, bounding the
  recovery directory, resuming partial moves, and keeping purge absent (ADR 0188).
- [x] Freeze linux-service-v1 as a distinct signed payload/policy/state kind; reverify a mode-0400
  selected slot into a sealed anonymous executable image, launch it through a no-new-privileges
  parent-death helper, require an exact sequence-bound readiness record before confirmation, and
  immediately recover a failed candidate to the confirmed service (ADR 0189).
- [x] Retain the dual-carrier Sandwurm process-interruption matrix inside simultaneous VMs for
  adapter exec, pre-readiness exit, exact readiness, confirmation, Agent death plus parent-death,
  health expiry, three signed rollbacks, and confirmed-service recovery
  (`evidence/2026-08-27-sandwurm-linux-service-update.md`). This does not claim an abrupt whole-VMM
  or host power cut.
- ~~Name and qualify a representative physical OTA target, power-cut matrix, flash-wear boundary,
  secure boot, and hardware witness.~~ **Retired from repository scope by ADR 0277; the supported
  claim ends at the qualified inert-slot and Linux-service Sandwurm lifecycle.**

The authenticated multi-route immutable-object scheduler is qualified under M5B and may deliver the
same exact bundle without becoming update authority. Randomized larger-object route science remains
useful optimization evidence, not permission to install bytes.

Cross-client work is not an IoTox repository gate; this project qualifies the source-linked tool it
ships and leaves other clients to their maintainers.

Exit: interrupted and adversarial update scenarios fail closed and recover predictably.

## M8 — routed privacy and stewardship (complete for founding-machine scope)

Contribute useful Tox bootstrap/relay capacity without creating mandatory IoTox infrastructure.
Then research Tox/Tor and Tox/I2P with explicit identity and leak-containment policy. Direct
IoTox-over-Tor/I2P transports remain a separate design axis.

- [x] Read the pinned c-toxcore 0.2.23 proxy/bootstrap path and freeze the provider constraints:
  TCP-only bootstrap still installs onion path nodes while its UDP branch stays disabled, and
  SOCKS5 relay requests carry resolved IP addresses rather than remote-DNS names (ADR 0190).
- [x] Construction-enable explicit `tox/tor` with one numeric SOCKS5 endpoint, nonempty explicit
  numeric bootstrap and TCP-relay records, UDP/discovery/announcements/hole-punching/native-DNS off,
  no compiled native catalogs, and no native fallback. Proxy/route confusion, hostnames, omissions,
  and UDP-required auxiliary members fail before durable/runtime mutation.
- [x] Add exact mock-option/topology tests, a separately tested bounded numeric-only SOCKS5 lab
  forwarder, and a repeatable source-linked local provider gate. The gate observes TCP through only
  the proxy, no IoTox UDP or direct-relay socket, explicit proxy-loss offline state, and same-endpoint
  recovery. Its accepted evidence records 8.038-second initial construction, 77.993-second
  proxy-loss detection, and 4.921-second exact-endpoint recovery; its receipt is explicitly
  `source-linked-local-construction-not-actual-tor`.
- [x] Construct and live-qualify the adversarial local boundary without changing the historical
  forwarder digest. A distinct numeric SOCKS-over-SOCKS interposer binds exact client/target/upstream
  endpoints and can hold established relay bytes behind a still-reachable listener before exact
  release. Its process test remains adapter evidence. Accepted compact proof `pair.vx6z0csh` joins
  the live two-guest fault to authenticated Tor control, exact process/socket identities, TCP-only
  TAP containment, heartbeat-before-offline separation, detached PTY state, and explicit exact
  resume without Tor/interposer/IoTox restart (ADR 0209).
- [x] Preserve c-toxcore connection truth while adding a distinct content-free on-demand
  `route-health [FRIEND]` signal. It separately reports exact carrier truth, a 250 ms local numeric
  SOCKS-listener connection for `Tox/Tor`, and an optional transcript-confirmed lossless peer echo.
  A reachable listener leaves upstream `unresolved`; Agent and whole-binary tests prove the
  observation does not mutate the complete protocol session or its epoch (ADR 0192).
- [x] Add strict canonical report parsing plus finite/signal-driven `route-health-watch [FRIEND]`.
  Keep independent local-boundary and application latches with bounded 1..64 failure/recovery
  thresholds, inconclusive samples that fabricate no state, saturating evidence counters, and no
  Agent persistence, carrier relabel, epoch change, or session effect (ADR 0193).
- [x] Reuse one exact frozen-v1 Ratox PING per attachment so periodic liveness cannot exhaust the
  never-evicted replay store. Cross the installed local controller, real Agent, authority/session
  gates, remote Ratox peer, authoritative route loss, exact generation-two RESUME, and post-resume
  PONG. The terminal CLI samples once per second and warns after three misses without mutating the
  retained session (ADR 0193).
- [x] Add explicit one-shot `route-target-health`: a complete bounded SOCKS5 negotiation and numeric
  CONNECT only to index zero of the already validated Tox/Tor TCP-relay list. Strict content-free
  results separate proxy-connect, method, target, and complete stages; no caller-selected target,
  watch integration, carrier relabel, epoch change, or session effect exists (ADR 0194).
- [x] Bind initial and recovered `route-target-health` to authenticated Tor control, one new
  Agent-owned SOCKS source, the exact configured relay-zero stream lifecycle, and a built three-hop
  `GENERAL` or `CONFLUX_LINKED` application circuit. Keep strict canonical independent verification
  and content-free path/stream commitments; never infer anonymity or carrier/session state from
  auxiliary success (ADR 0195).
- [x] Qualify Ratox heartbeat and PTY-output latency under bounded impairment on direct UDP,
  forced TCP, and strict generic SOCKS. Three 120-sample cells cross baseline, seeded
  `75ms +/- 15ms` delay plus 2% loss on both TAPs, and exact recovery without changing the Ratox
  session. Keep carrier presence, heartbeat, PTY progress, and visible stall distinct; partial
  impairment warns but cannot mutate an authenticated attachment (ADR 0196).
- [x] Qualify exact total route loss and freeze the mutation policy. Separately evidence carrier
  loss, Ratox heartbeat loss, local controller outcome, detached PTY retention, authenticated epoch
  recovery, exact session resume, and post-resume PTY progress on native and strict-SOCKS routes.
  Accepted compact proofs `pair.0cnril1l`, `pair.qoty7j1x`, and `pair.8jjawnwp` close direct UDP,
  forced TCP, and strict generic SOCKS under ADR 0197. Repeat bounded impairment and total loss
  through actual Tor separately; generic SOCKS is not Tor.
- [x] Run two source-linked Sandwurm guests through the strict SOCKS boundary with host/TAP packet
  capture proving that each guest contacts only the proxy, then repeat proxy loss/recovery while a
  confirmed IoTox session and fresh application traffic cross the restored route. Accepted
  `pair.zyy913jf` observes 913 TCP-only guest-egress IPv4 packets to the proxy, zero UDP/direct
  packets, two clean forwards per proxy incarnation, epoch 1-to-2 recovery, and post-recovery text.
- [x] Qualify an operator-owned Tor daemon separately from generic SOCKS plumbing. Accepted clean
  commit `715e1c8` binds Tor 0.4.8.11, its exact normalized loopback policy, one current public
  numeric relay, initial and recovered three-hop `GENERAL` carrier plus `CONFLUX_LINKED` exact-target
  circuits, Tor-owned public sockets, and IoTox-only loopback TCP with zero UDP/direct sockets. The
  repeated gate observes local refusal in 35 ms while carrier truth remains TCP, authoritative
  offline in 74.602 seconds, a 30.290-second/30-sample no-bypass outage, and 3.913-second recovery
  (ADRs 0191/0192/0194/0195).
- ~~Require independently witnessed Tor relay/exit/operator/time diversity as a repository completion
  gate.~~ **Retired from repository scope by ADR 0277.** Bounded actual-Tor repetition and the
  long-running two-IoTox application topology with packet capture and adversarial proxy behavior
  remain accepted mechanism evidence.
  Do not infer this from the separate generic-SOCKS pair and single-IoTox public-route gates.
  The first two-IoTox cell is accepted as compact proof `pair.2mycvy9n`: two source-linked Sandwurm
  guests retain native
  fixture control routes while independent exact-key workers use separate Tor processes, policies,
  control sockets, and circuit populations. Its verifier binds exact guest sources and the supplied
  public Tox endpoint through authenticated STREAM/CIRC evidence, Tor-owned public-socket
  commitments, TAP containment, private-v2 readiness, and signed 4,194,389-byte tree convergence.
  Each role recorded two successful exact-target streams on a distinct three-hop
  `CONFLUX_LINKED` circuit and zero unexpected context packets. A distinct stable-key cell now closes
  payload attribution as accepted compact proof `pair.lzsyitvy`: the lowest founding client
  auxiliary key is the Tor member, the complete signed tree job names that exact carrier, no
  reassignment occurs, and initial pull admission succeeds in one attempt. Both Tor/control and TAP
  evidence sets independently reverify. Accepted compact proof `pair.iompvehf` closes the next
  bounded cell: after at least
  65,536 exact-carrier object bytes, the host kills only the client Tor process, holds it down until
  the guest proves one loss and native-member reassignment, then restarts the same Tor instance and
  requires genuine carrier recovery without an IoTox worker restart. Its strict proof joins the
  stopped carrier across guest, host PID/control, and private-route commitments. The accepted run
  faults at 74,034 bytes and records one loss, one reassignment, two stale terminals, one recovery,
  two ready bulk members, zero route-worker restarts, and zero unexpected-context TAP packets. The
  distinct ADR 0206 terminal cell is accepted as compact proof `pair.2waqdpgk`: both primary agents
  run through actual Tor, the host kills only client Tor after PTY progress, the device retains its
  detached PTY through authoritative offline, and explicit generation-2 resume preserves the exact
  session/incarnation after exact Tor restart. Three authenticated Tor phases, zero IoTox daemon
  restarts, and TCP-only guest TAP containment independently reverify. The wider
  ADR 0207 accepts compact proof `pair.k8o54n2v` for a 120-sample no-process-loss terminal soak with
  exact client/device circuit replacement. One checkpoint proves same-epoch PONG continuity after
  same-stream reattachment; the other proves explicit higher-epoch resume after stream reopening and
  authoritative loss. ADR 0208 repeats the gate as `pair.9cx0jels` through a second public Tox
  record; both exact streams reopen while the Ratox attachment remains continuous. This begins
  relay-record sampling but does not establish Tor exit or time-window diversity. The wider
  relay/exit/time population is optional downstream evidence, not a repository gate (ADR 0277).
  The first adversarial-proxy cell is now accepted as compact proof `pair.vx6z0csh`: client and
  device use separately attributed SOCKS-over-SOCKS/Tor chains; the held client listener remains
  reachable and admits a fresh exact-target CONNECT; Ratox warns at 2.578 seconds while carrier and
  session truth remain unchanged; authoritative offline follows at 27.241 seconds; and removal of
  only the hold file permits exact generation-2 resume at online epoch 3. All Tor, interposer, IoTox,
  guest, PTY, session, incarnation, and byte identities required to remain stable do so, with zero
  UDP/direct TAP packets. This closes ADR 0209's bounded local-deception gate but not independently
  separated time/exit populations, anonymity, availability, automatic migration, or latency claims.
  ADR 0210 closes the accounting part of this item. After ADR 0243 adds later operator-window compact
  proof `pair.wbsef5tp` against the third public record, eight accepted compact proofs resolve 30
  exact-target/churn declarations to 24 distinct normalized three-hop paths, 20 first hops, 23 last
  hops, and 24 first/last pairs. No two proofs reuse a complete path or last hop. The new proof's two
  requested closes exercise both
  attachment-continuous and explicit-resume outcomes, and its four normalized paths share no first
  hop, last hop, or complete path with any prior proof. Because the compact schema does not
  independently witness UTC or map operators, strict time-window and independent exit/operator
  qualification are not established and are outside repository completion.
  ADR 0261 adds a content-v2 destructive repetition through a second compiled public TCP-relay
  record as compact proof `pair.i8ar90tx`. Both Tor roles reach 100% bootstrap, the exact worker
  fault/recovery contract holds, and both TAPs retain zero unexpected-context packets. Because it is
  another bounded same-day run and the evidence does not review exit operators, no exit/time-window/
  long-running diversity claim is made. ADR 0277 permanently retires that repository requirement.
- [x] Use independent random Tox savedata identities for native, Tor, and future I2P contexts by
  default while retaining one stable device principal and authority ledger above them. Route-scoped
  default filenames are implemented. Full cross-route inventory must move over an already
  authority-authenticated primary association and auxiliary routes must disclose only an expected
  member proof before mixed-context operation can satisfy the M8 privacy exit; route-binding v1 is
  frozen and explicitly not that private discovery protocol (ADR 0198). Feature bit 28 and message
  types 26/27 now implement the canonical primary-inventory/member-proof codecs with exact
  authority-epoch, transcript, inventory-digest, fork, and mutation checks. The explicit
  `--enable-private-route-bindings` path now adds bounded one-epoch delivery/replay, process-lifetime
  generation/digest high-water, worker handoff, member-only exchange, and primary-loss readiness
  withdrawal (ADRs 0199/0200).
- [x] Bind each exact auxiliary key to a fully validated local network context before any worker
  starts, then qualify v2 across a native UDP primary, native UDP bulk member, and strict
  generic-SOCKS/TCP bulk member in two simultaneous Sandwurm guests. Accepted compact proof
  `pair.z948jeii` reaches two ready bulk members per role, converges and activates one signed
  4,194,389-byte tree, admits four proxy connections with zero denials, and confines every TCP
  packet to the configured local proxy/relay endpoints. Preserve an early reciprocal member proof
  across primary-context adoption, reverify it exactly, and discard a stale proof without authority
  so the peer can replace it (ADR 0201). This closes generic-SOCKS mixed-context operation, not the
  separately open actual-Tor multi-peer matrix or anonymity.
- [x] Let an exact auxiliary route replace inherited bootstrap and TCP-relay catalogs with bounded
  repeatable local records. Require the same key's network override, reject duplicates and more than
  16 records per list, and validate all derived transports before any starts. This keeps native lab
  routes pinned while an actual-Tor worker uses independently reachable public numeric records
  without adding mutable infrastructure to the signed route set (ADR 0202).
- [x] Add route-set v2 without widening v1: sign each exact member's coarse native, Tor, or
  construction-I2P class; require the coordinator to be the protected member; fail primary startup,
  worker construction, and coordinator admission on disagreement; and transitively bind the class
  through the existing private complete-artifact digest. New Sandwurm multi-route receipts expose
  whether both guests observed the signed projections while historical proofs remain verifiable
  (ADR 0225). The genuine positive path is accepted as `pair.q2pka1fm`.
- [x] Qualify fail-closed actual-I2P member loss after positive immutable-object bytes. The
  `sync-tree-route-private-actual-i2p-loss` construction keeps native ready, requires one blocked
  job and zero reassignment, replaces the exact i2pd process over preserved state, explicitly
  cancels the old job, and starts a distinct fail-closed pull on the recovered signed member.
  Accepted compact proof `pair.jbr89_gc` reaches 69,921 bytes, records one block and zero
  reassignment with native ready, recovers the same member with zero worker restart, and completes
  only through that explicit fresh pull (ADR 0226). The first live attempt proved the decisive
  no-downgrade interval at 71,292 bytes and restored all three generation-two I2P fronts, but the
  signed member did not return to authenticated-ready inside 900 seconds. It is rejected evidence;
  the gate now exports a content-free recovery heartbeat before repetition. The instrumented run
  then proved same-worker authenticated recovery with zero reassignment, but showed that a fresh
  16 MiB pull at the observed few-kilobyte-per-second I2P rate cannot fit the recovery deadline.
  The gate now uses the already-qualified 131,369-byte I2P tree; router loss after the required
  65,536-byte checkpoint preserves the same deterministic fault window.
- [x] Carry the frozen range-v1 request/result frames over an exact authenticated auxiliary without
  inventing a second range protocol. Require bilateral range-feature negotiation on the primary
  authority session and selected route worker, retain FileId/attempt/authority/carrier fencing, and
  keep HEAD acceptance last plus activation explicit. Accepted compact proof `pair.ej_4507n` builds
  a 4 MiB basis over native, pins generation 2 to the signed construction-I2P member, reuses
  4,194,176 verified bytes, fetches one 128-byte range on that exact member, and converges with zero
  reassignment or router/front restart (ADR 0227).
- [x] Qualify destructive loss during a concrete auxiliary I2P range without confusing its manifest
  prerequisite for the range itself. Accepted compact proof `pair.a9zwongf` faults at 86,373 of
  1,048,576 range bytes, proves strict staging cleanup, one fail-closed block and zero reassignment,
  recovers the same member once with zero worker restart, then permits only explicit cancellation
  and a distinct fresh job. The fresh job fetches the complete 1 MiB range, reuses 3 MiB, verifies
  the 4 MiB artifact and linked HEAD, and explicitly activates it (ADR 0228). Failed range-prefix
  reuse, implicit old-job revival, and cross-process resume remain excluded.
- [x] Reuse an exact durable range-manifest prerequisite on explicit recovery. Deterministic tests
  require same-size corrupt bytes to fail locally with zero requests, then prove the restored exact
  object produces a fresh FileId-bound range immediately. Accepted compact proof `pair.ip5q0at9`
  reports one requested object, two committed objects, and local manifest reuse before exact
  reconstruction/activation on the recovered I2P member (ADR 0229). Those carrier-loss bytes remain
  discarded; same-handle, I2P carrier-loss, and explicit-fresh-job prefix continuation stay open.
  ADR 0230 separately qualifies one ordinary same-job/same-carrier retry, while ADR 0231 qualifies
  one native `available` cross-carrier range continuation without changing this I2P policy.
- [x] Design and source-verify `Tox/I2P`; enable selection only after its stream tunnel,
  endpoint naming, leak containment, reconnect, and identity policy have equivalent evidence.
  ADR 0211 closes the first construction prerequisite with a lab-only exact-record SOCKS-to-SAM
  v3.1 adapter. Canonical b32 naming, numeric-loopback SAM confinement, one transient session,
  eight-stream concurrency, loss-closed admission, higher-generation recovery, and content-free
  destination commitments pass an independent process double. At this stage product selection
  remained unsupported. ADR 0212 adds two distinct source-attributed i2pd 2.60.0 processes and one warm-up
  plus four simultaneous byte-verified actual-I2P STREAMs. Its strict content-free receipt joins the
  server and adapter Destination commitment and rehashes the exact router executable/source when
  supplied. This closes the real-router stream seam only.
  ADR 0213 closes the next construction boundary: an owner-only persistent Destination, exact
  numeric-loopback `STREAM FORWARD SILENT=true`, raw-service bytes, process-loss recovery, and
  content-free audit pass independently and through two live routers. The distinct lab spelling
  `tox/i2p-construction` now installs the frozen strict SOCKS/TCP-only c-toxcore options and its own
  savedata path; production `tox/i2p` remained unsupported at that construction stage.
  The first c-toxcore attempt reached both I2P boundaries and the pinned relay but stayed offline;
  its direct strict-SOCKS control passed. Instrumentation separated 0.468-second SAM admission from
  roughly 34-second arrival of the complete relay response, beyond c-toxcore's ten-second combined
  proxy/relay establishment timer. ADR 0214 pins only that establishment budget at 120 seconds,
  retains all onion and established-carrier lifetimes, selects interactive I2P streaming, and names
  the combined provider `iotox-file-rr1-tcp-connect120`. A later three-front, address-preserving
  falsification reached `tcp` with that exact provider; no onion-retention patch is justified.
  ADR 0215 then closes the same-host Tox/application edge: a direct three-record control exposed the
  minimum useful fresh TCP-only population; three fake-address I2P fronts proved that Tox embeds
  node addresses in onion paths; and three exact address-preserving persistent fronts carried two
  fresh peers through friendship, authority, text, durable command, exact file, two receiver
  restarts, ownership transition, and friendship removal/re-add. The TCP-only provider repeated the
  carrier pass, so the experimental onion-lifetime patch was removed. ADR 0216 accepts compact proof
  `pair.k_vopzf5` for the next baseline: two source-linked Sandwurm/KVM guests, two pinned routers,
  three persistent fronts, TCP friendship, canonical session confirmation, bidirectional text,
  strict TCP-only bridge containment, and independently verified raw plus secret-free compact
  evidence. ADR 0217 accepts compact proof `pair.v_11i2me`: the adapter stays reachable while client
  SAM disappears, both guests observe c-toxcore-authoritative offline, a new i2pd PID reuses the
  exact private datadir, both authenticated epochs advance 1-to-2, fresh text crosses bilaterally,
  and the TAPs remain TCP-only to the adapter. The source-matched 21-file certificate bundle and
  signed reseed policy are independently committed. ADR 0218 accepts compact proof
  `pair.6rrdsdc_`: exact router PIDs own their SAM listeners and established public TCP socket sets;
  both remain live while all three server fronts are replaced; the new processes load unchanged
  private Destination keys; and both guests again advance 1-to-2 with fresh bilateral text and no
  fallback. ADR 0219 accepts compact proof `pair.5xjf2n4d` for the next exact layer: both roles admit
  the private-v2 topology, the client's exact I2P auxiliary carries and activates one 131,369-byte
  signed tree with zero reassignment, and native fallback remains available. Diagnostic 512 KiB and
  4 MiB attempts selected I2P first but crossed an authoritative carrier epoch and safely reassigned
  the complete missing object to native while both routers/fronts remained live. This closes one
  bounded private member-bound sync payload, not large privacy-pinned objects. ADRs 0225–0226 now
  implement and qualify signed member classes plus fail-closed loss/recovery. ADR 0227 qualifies the
  unchanged digest-bound range-v1 transport over the signed I2P auxiliary with a 4 MiB successor and
  128 fetched artifact bytes. ADR 0228 qualifies live range loss, no-downgrade cleanup, same-member
  recovery, and an explicit fresh 1 MiB range fetch; same-handle and I2P
  carrier-loss/explicit-fresh-job prefix resume, larger-object distributions, and later record/time
  repetition remained open after that range gate.
  ADR 0253 closes the product-spelling gate without changing the signed or local-control bytes:
  class 3 and constraint 4 now render canonical `tox/i2p`, use the same I2P savedata and strict
  provider policy, and accept `tox/i2p-construction` only as a deprecated reproduction alias.
  Production-spelling compact proof `pair.btm5vwr9` repeats the two-guest actual-I2P baseline with
  three fronts, TCP friendship/session/text, and zero native UDP, direct-bootstrap, or direct-peer
  packets. The 2.3 GiB private raw root and 1.2 MiB secret-free compact root independently verify.
  This closes supported selection on the available VM substrate, not anonymity, public-route
  availability, operator/geographic diversity, physical-host diversity, broad record/time samples,
  large-object performance, or fleet qualification.
- [x] Publish reproducible owner/community bootstrap-relay operations and contribution guidance
  without an IoTox-operated mandatory service, account plane, reassignment key, or silent default.
  ADR 0240 exports the opt-in `nixosModules.toxBootstrap` module and source-pinned single-port
  package. A NixOS/KVM check proves TCP/UDP listeners, strict private-state shape, byte-identical
  identity over restart, configured cgroup ceilings, `DynamicUser`, and exact opt-in firewall rules.
  `docs/bootstrap-relay-operations.md` freezes deployment, backup/rotation, endpoint publication,
  monitoring, update, decommissioning, and community stewardship while keeping public reachability,
  abuse resistance, uptime, and geographic/operator diversity as external evidence.

Exit: selected routed modes are route-verified and cannot silently fall back to native networking.

## Parallel quality tracks

Every milestone ratchets, rather than replaces:

- coverage, sanitizer, fuzz, stress, fault-injection, and long-running soak evidence;
- threat modeling, protocol review, dependency updates, and external security review;
- constrained Linux hardware, power-loss, flash-wear, and resource measurements;
- operator documentation, migration, backup, observability, and support policy;
- accessibility and safe phrase/recovery UX.

## Incubator boundary

Mutorr/Small Circles remains compilable research. It does not enter the default product until the
ratox successor, owner re-entry, durable lifecycle, and target-verified device semantics are working.
