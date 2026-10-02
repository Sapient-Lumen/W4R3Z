# IoTox

IoTox is a C++20, one-binary, self-owned device agent and modern ratox successor. Tox remains the
primary connection fabric. IoTox adds stable device identity, owner-reconstructible authority,
explicit authorization, a negotiated machine protocol, durable command semantics, and an ordinary
Unix surface above Tox friendship.

```text
From memory, you can reach your devices.
The outside should be ordinary; the inside must tell the truth.
```

## What it is

IoTox is for machines you own: pair them over Tox, prove durable authority above
friendship, sync ordinary directories when they are not the only copy, and open
owner-approved shells without handing control to a vendor account. The product
sentence is deliberately small:

```text
from memory:      recover ownership
from Tox:         reach peers
from IoTox:       prove exact authority
from Unix:        operate through boring files, commands, services, and shells
from evidence:    know what passed, what failed, and what is not claimed
```

## What works now

- stable device identity plus RecallRoot-derived owner recovery;
- signed authority ledgers where Tox friendship is reachability, not power;
- ratox-style peer/text/file/command surfaces and durable offline commands;
- self mode for owner machines, with Ratox host/controller enabled by default
  but still gated by terminal profiles, bindings, capabilities, and host sudo
  policy;
- one-writer and bounded read-write sync with signed branches, conflicts,
  sparse custody, retention, recovery rehearsal, health, and precious-data
  signoff receipts inside IoTox's real scope;
- person multidevice messaging foundations: delivery cards, device fanout,
  delegated send, duplicate suppression, receipts, read-status, group
  descriptors, a Toxic-compatible bridge, and a supervised background worker;
- service porches for systemd, NixOS, and MonsterNix-adapter review; and
- slim public repository datacube export, full-history upload datacubes, and
  richer conversation/recovery datacubes for exact-state handoff.

## Boundaries that matter

IoTox sync is a synchronized working-copy system, not a backup product or a
disaster-recovery boundary. Disk-loss survival, host-compromise survival,
filesystem-wide corruption repair, and storage-media certification are outside
IoTox's goal by design; they belong to backups, storage, operating-system
security, and operator recovery practice. Precious-data signoff means IoTox
has checked the sync-layer discipline it can own for a chosen folder:
versioned recovery custody, restore rehearsal, retention policy, delete
quarantine, runbooks, and operator acceptance.

Ratox is SSH-shaped remote control, not arbitrary SSH. The remote side does not
choose a surprise executable, argv, sudo mode, agent forwarding, or port
forwarding. Sudo is denied by default and only crosses through an explicit
host-reviewed profile plus the host sudo/PAM policy.

Tor and I2P are named route classes with fail-closed construction and bounded
evidence. They are not silent fallback, anonymity certification, or a promise
that every network will behave.

## Start here

- [`docs/product-page.md`](docs/product-page.md): the publishable human front
  page.
- [`docs/README.md`](docs/README.md): the documentation map.
- [`docs/quickstart.md`](docs/quickstart.md): the first safe hour.
- [`docs/replace-resilio-sync.md`](docs/replace-resilio-sync.md): what it would
  mean to use IoTox for everyday folder sync.
- [`docs/ratox-ssh-status.md`](docs/ratox-ssh-status.md): the SSH-like control
  story.
- [`docs/person-multidevice.md`](docs/person-multidevice.md): one person key,
  many devices, and the normal-Tox bridge.
- [`docs/ship-readiness.md`](docs/ship-readiness.md): what “stable” requires.

The first high-value native human porches are:

```text
iotox help
iotox help quickstart|sync|terminal|service|pairing|self|person
iotox help routes|evidence|shipping|support|storage-readiness
iotox help all
iotox doctor binary
iotox version --source
iotox overview [--json]
iotox readiness [sync|terminal|storage|routes|privacy] [--json]
iotox explain TOPIC
iotox init plan|write-config
iotox sync plan-pair|plan-mesh|start|share
iotox terminal doctor
iotox terminal profile plan shell|sudo|rescue
iotox service plan|render|receipt|status-plan|status-receipt
iotox person quickstart
iotox person graduation-check
iotox person tox-bridge-graduation-check
iotox route-qualification-check --scope all
iotox evidence dossier-plan --scope all --out DIR
iotox ship-check all founder-preview
iotox support-bundle plan ./iotox.support
```

For the ideal, see [`docs/edge-of-hope.md`](docs/edge-of-hope.md). For the
counterweight, see
[`docs/pragmatic-guardrails.md`](docs/pragmatic-guardrails.md). Significant
architectural additions start with
[`docs/architectural-change-intake.md`](docs/architectural-change-intake.md) so
new subsystems do not accidentally blur reachability, authority, storage,
routes, terminal execution, support export, or backup boundaries.

## Public package and exact handoff

The official working object is this ordinary Git repository. For the clean
public/GitHub seed artifact:

```sh
tools/iotox-repo.sh release-plan founder-preview
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
```

Use `tools/iotox-repo.sh datacube --upload` only when the recipient deliberately
needs full local Git history. Use `tools/iotox-repo.sh datacube --conversation`
when the recipient needs the richer internal conversation cube with nested
founding-cube provenance. See
[`PACKAGE.md`](PACKAGE.md),
[`docs/revision-packaging.md`](docs/revision-packaging.md), and
[`docs/conversation-datacubes.md`](docs/conversation-datacubes.md).

This is the founding official development repository, currently IoTox 0.51.0 rev0051
“Freshness-Explicit Projection Recovery.” `BOOTSTRAPROSE.md` remains the governing wake-from-amnesia
entrance and executable evidence remains authoritative. The independently buildable toxsync 0.7.0
line is preserved under `components/toxsync/`; its 125-check native registry plus backend-aware CLI
transaction now pass the compiler/sanitizer/portable/package matrix on the founding bare-metal host.
IoTox-owned integration includes namespace/HEAD/install/activation
state, v3 authorization composition, and a fixed stable-device-signed publication HEAD whose artifact
and manifest are durably verified first. An explicit default-off `--enable-sync` gate now constructs
the Agent publisher/subscriber, durable attempt recovery, bounded worker, exact FileId file join, and
typed synchronization controls. Operators can now generate and lint the canonical namespace record,
atomically install a new no-clobber policy, replace only its activation and principal-membership
fields while the namespace is quiescent, and remove policy without deleting content or signed state.
Exact update and removal retries are generation-stable. Root, engine, and quota changes remain
explicit migrations rather than live edits. The full mock-provider path commits
both immutable objects and the accepted HEAD last and never activates content implicitly. Local
pulls now return a stable process-local job ID, `sync-status` projects it, and `sync-cancel JOB_ID`
terminally fences a live pull before cancelling receives and clearing its private staging and signed
attempt truth. Late HEAD, object, offer, and completion events cannot revive a cancelled job. Local
`sync-publish` now builds a genuine bounded toxsync range-v1 index and commits both objects before its
signed HEAD; `sync-activate` requires the exact accepted HEAD token and revalidates the complete
artifact/index pair under the namespace transaction. M5C now adds a locally qualified unattended
one-writer layer. The ordinary `sync-create NAMESPACE PATH [INTERVAL_SECONDS]` command creates a
managed sole-writer namespace and begins publication; `sync-share NAMESPACE FRIEND read-only`
reconstructs the owner from RecallRoot, binds the live friend to its proven stable principal, and
adds only subscriber authority and membership. The recipient still chooses and installs its local
root, writer authorization, follow mode, and activation policy. The expert
`sync-auto-publish NAMESPACE PATH` command periodically reconciles a source through that same
HEAD-last transaction, while `sync-follow FRIEND NAMESPACE pull|verified` stores the peer's currently
proven stable principal and drives the existing authority-gated pull path. `verified` can invoke only
the namespace-permitted exact-accepted-HEAD activation transaction; `pull` never activates. Policies are
stable-device-signed, generation-bound, restart-safe, and disabled by a signed tombstone. The live
Agent test advances a changed source before and after restart without another synchronization
command; a second test captures an exact-v3-proven publisher, pulls and accepts its paged CAS, and
activates the exact HEAD under `verified` without manual pull/activation. The bounded multi-writer
path also passes a real three-daemon full-mesh convergence gate; the pairwise path retains its
dedicated two-guest unattended restart proof. Separate direct-UDP and forced-TCP one-writer cells
and the two-hour networkless IoTox/Resilio shadow now pass.

ADRs 0273--0274 activate the bounded read-write path. On each peer,
`sync-create NAMESPACE DIRECTORY read-write [INTERVAL_SECONDS]` installs a tree-v2 workspace; each
owner then runs `sync-share NAMESPACE FRIEND read-write` for every other writer. The ceremony grants only the
transcript-proven stable peer `sync.publish|sync.subscribe`, adds bounded writer/subscriber
membership, and additively binds durable bidirectional automation to the sorted exact-principal set.
Each bilateral direction remains an independent owner act; a three-node full mesh therefore has six
share ceremonies. Per-file CAS,
independent signed branches, exact causal observations, tombstones, and visible-frontier workspace
journaling preserve concurrent offline values instead of applying arrival-time last-writer-wins.
The ordinary path is deterministic; losing values remain under `.iotox-conflicts/by-origin` until a
later ordinary edit causally resolves them. Immutable objects commit before signed branch pointers,
and workspace projection is the final atomic effect. Tree-v2 object transfer now uses a bounded
exact-object lane window over the authenticated primary Tox lane: the process
`--max-sync-tree-lanes` cap defaults to four and is tightened by signed namespace
`maximum-lanes`/`maximum-outstanding-requests`. A retained Sandwurm proof exercises simultaneous pairwise
offline edits, deterministic conflict preservation, later causal resolution, deletion, an empty
file, restart, and repair without a manual publish or pull. A distinct three-node gate exercises
three concurrent writers and explicit causal resolution. ADR 0275 now adds negotiated
conflict-free checkpoint floors, explicit history pins, signed-workspace-aware reachability,
recoverable quarantine/restore, and exact terminal writer cutoffs. Quiet convergence no longer
authors acknowledgement-only branches. ADR 0278 adds recipient-local component-prefix selection,
excluded-local-file preservation, and exact private owner `r/w/x` manifest metadata while retaining
v1 defaults. ADRs 0280--0283 close the founding-machine adversarial/scale and two-hour incumbent-
shadow gates. The bounded private-Linux regular-file path can now replace the incumbent synchronizer
for a noncritical directory, but it is not a backup and important data still needs an independent
copy. ADRs 0295--0297 now add recipient-local path-prefix sparse custody, widening/on-demand fetch,
complementary authenticated sources, and restart-durable health. ADRs 0341--0352 add bounded Linux
source-watch wakeups, debounce, safe no-op skips, volatile digest reuse, grouped local tree-v2
path/ancestor/branch-validation/diff work, empty complete-projection preservation skips, and
content-free sparse preservation counters for synchronization scale. Remote-selected globs or
destination paths, metadata beyond private owner mode, case-folding portability, symlinks, deeper
incremental projection, and permanent purge remain absent. ADR 0284 separates synchronization
confidence from precious-data trust and freezes the independent-recovery rule (ADRs 0270--0284,
`docs/everyday-sync-plan.md`, `docs/sync-trust-graduation.md`, and
`docs/evidence/2026-09-01-sandwurm-iotox-resilio-shadow.md`).

Before creating a namespace, the owner can now run a read-only source preflight:

```text
iotox sync-doctor /absolute/path [one-writer|read-write] [INTERVAL_SECONDS]
iotox sync-doctor-configured --config /etc/iotox/agent.conf NAMESPACE
```

ADR 0288 reuses the production source rules and reports transformations, selected population,
hash-backed byte/object counts, and conservative first-revision store/staging estimates without an
Agent or mutation. ADR 0315 adds the second command for an already initialized namespace: it joins
the exact signed automation source and nondefault policy to live immutable-store/staging occupancy,
remaining quotas, and actual filesystem headroom under the existing namespace transaction. It
reserves no space and explicitly does not assess backup quality. ADR 0318 makes both paths refuse
ACL/xattr state, sparse allocation, links, special files, and ASCII case collisions while rendering
the required byte-case model plus ownership/mode/timestamp transformations; this is point-in-time
Linux source preflight, not metadata support or portability. See
[`docs/sync-doctor.md`](docs/sync-doctor.md). The nine accepted post-founding product
workstreams, beginning with synchronization health, Mosh-like Ratox continuity, and deployable Agent
configuration, are ordered in [`docs/roadmap.md`](docs/roadmap.md).

An owner can now verify one independently restored ordinary tree without reading any live IoTox
state:

```text
iotox sync-recovery-verify BACKUP_ROOT RESTORED_ROOT [MAXIMUM_BYTES [MAXIMUM_ENTRIES]]
```

ADR 0319 performs bounded strict owner-mode-v2 scans of two disjoint roots, refuses unresolved
`.iotox-conflicts`, and requires exact path, content, and private owner-mode equality. The report
explicitly does not assess recovery custody or restore provenance. This closes the comparison
mechanism; the separate bounded loss/reseed/authority/retirement rehearsal is described below.
Neither result closes the precious-data recommendation; see
[`docs/sync-recovery-rehearsal.md`](docs/sync-recovery-rehearsal.md).

ADRs 0320--0322 retain the first persistent-ext4, three-writer capacity/recovery cell. A fresh
2-vCPU/2-GiB Sandwurm guest converged and repaired 512 files (8 MiB logical), preserved the ordinary
lifecycle, and recovered one writer whose restart landed between an atomic projection exchange and
its stable signed workspace record. ADR 0329's default cap-4 tree-v2 lane window has since re-run
that 512-file Sandwurm gate from clean source revision `f5078bd482381915f011634727b6621b07175127`.
The larger 3,500-file near-ceiling Sandwurm comparison now has accepted cap-4, cap-8, and cap-16
proofs, plus compact retained cap-32/cap-64 rejections: cap 4 finished in 1,361.936 seconds, cap 8
finished in 1,198.824 seconds, cap 16 finished in 1,138.904 seconds, cap 32 timed out with the
followers still below 200 tree-v2 objects, and cap 64 timed out with the followers receiving only the
empty-file object. The lane-width gain is real but peaked at cap 16 for this guest shape, leaving
per-object catch-up/projection as the measured bottleneck. ADR 0330 removes one concrete local
amplifier without changing those frames: completed file lanes now enter the strict CAS importer one
bounded window at a time instead of causing one full immutable-store inventory per file. A direct
cap-16 retry finished catch-up in 387.085 seconds and the complete gate in 478.624 seconds, with 219
batches per follower. The exact 2-vCPU/2-GiB Sandwurm repeat then passed in 654.214 seconds of
catch-up and 788.317 seconds overall, 38.3% and 30.8% below the prior cap-16 VM result. It caught 7/8
late offers and ended with no retired IDs or evictions.
ADR 0331 removes the remaining complete CAS re-hash per batch while keeping storage state outside
the trust base: one pull caches a strictly verified inventory, verifies every exact install/reuse,
then re-hashes and quota-checks the complete store under the final branch/projection transaction.
Valid immutable additions from another serialized job are allowed; a cached removal, replacement,
corruption, malformed entry, or quota violation fails before a visible effect. The first direct
cap-16 run reduced 219 batch-implied follower scans to 7 and 5 across several intermediate
automation pulls, while completing the full gate in 478.979 seconds. That direct time was effectively
flat against the prior sample. The exact 2-vCPU/2-GiB Sandwurm repeat passed in 554.077 seconds of
catch-up and 634.194 seconds overall, 15.3% and 19.5% below ADR 0330's VM baseline. It retained 219
batches per follower while reducing aggregate full scans to 21 and 15, with no staging residue,
retired IDs, evictions, or watchdog restart. Compact proof
`.sandwurm/exports/three-writer/run.yDPmVYg6` verifies independently. The remaining
per-object/source-publication work is still open. ADR 0350 removes one source-side sparse-scan
amplifier: positive include rules now observe required ancestor directories and scan only included
roots/subtrees instead of enumerating unrelated siblings below every selected ancestor. Complete
interest scans remain full. ADR 0351 removes empty unselected-preservation and unselected-compare
walks for complete projection policy while keeping projection exchange semantics unchanged. ADR
0352 reports preserved unselected projection entries/directories/files/bytes through reconcile and
`sync-publish` without exposing paths or contents.
Derived projection writes now use one filesystem barrier before atomic exposure while immutable CAS
objects retain per-file durability. This capacity cell is bounded same-host construction evidence,
not itself a 24-hour, abrupt-power, ENOSPC, dishonest-storage, or precious-data result; the later
24-hour same-host soak is tracked separately in the roadmap and sync trust graduation notes. See
[`docs/evidence/2026-09-03-sandwurm-sync-persistent-capacity.md`](docs/evidence/2026-09-03-sandwurm-sync-persistent-capacity.md)
and
[`docs/evidence/2026-09-03-sync-near-ceiling-timeout.md`](docs/evidence/2026-09-03-sync-near-ceiling-timeout.md).

ADR 0323 adds the bounded recovery ceremony around the verifier. It erases and replaces one writer,
requires separate cutoff/revocation/friendship retirement and two ordered checkpoint barriers,
then erases every live node and reconstructs fresh identities, authority, namespace membership, and
the ordinary tree from the selected restore. The direct gate and a clean 2-vCPU/2-GiB Sandwurm run
match all three replacement views and reject obsolete principals. The VM first crosses the 512-file
capacity and 24-cycle persistent lifecycle, then completes recovery in 97.238 seconds without a
watchdog restart. Its backup remains on the same machine and administration domain,
so this is executable recovery evidence—not recovery custody, provenance, or permission to make
IoTox the sole copy of precious data. See
[`docs/sync-recovery-rehearsal.md`](docs/sync-recovery-rehearsal.md).

ADR 0325 adds the first bounded storage-fault cell. Three fresh nodes run on separate 192-MiB
loop-backed ext4 volumes inside one Sandwurm guest. The gate forces real live `ENOSPC`, requires an
explicit mutation refusal, kills and restarts that Agent after reclaiming only the filler, proves
read-only startup refusal without a durable-state change, and kills another Agent at the signed
`pending-workspace` side of a 32-MiB exchange. All three views converge and repair afterward. This
is process/filesystem recovery evidence, not a whole-VM power cut, dishonest-device result,
versioned recovery custody, or precious-data approval; see
[`docs/evidence/2026-09-03-sync-storage-fault-recovery.md`](docs/evidence/2026-09-03-sync-storage-fault-recovery.md).

ADR 0332 crosses the next storage boundary with a corrected two-boot whole-VMM cut. A networkless
Sandwurm guest exposes the interrupted follower's signed raw workspace phase byte `2`
(`pending-exchange`), and the host sends `SIGKILL` only to the exact task-owned Cloud Hypervisor
process. A second kernel boots a reflink of that crash disk. Before any Agent restart, the two
survivor views are exactly completed and the follower is exactly prior with pending byte `2`; after
restart all identities survive, converge to the 18-file/33,619,995-byte successor, retain three
branches, and pass repair. Compact proof `.sandwurm/exports/sync-power-cut/run.4hto8rll`
independently verifies. The phase-reversed v1 predecessor is withdrawn and rejected. This closes one
workspace-exchange cut, not the full transition matrix, physical or lying storage, backup
independence, or precious-data approval; see
[`docs/evidence/2026-09-04-sync-whole-vmm-power-cut.md`](docs/evidence/2026-09-04-sync-whole-vmm-power-cut.md).

ADR 0333 qualifies the opposite workspace linearization without adding a product crash hook. Proof v3
double-reads raw pending state around the canonical visible projection marker: active identifies the
pre-exchange side, pending identifies the post-exchange side. Post-exchange recovery must retain the
completed follower projection. The accepted run retained pending byte 2, pending orientation, and the
old stage across reboot; all offline views were completed, then recovery stabilized and repaired.
Compact proof `.sandwurm/exports/sync-power-cut/run.nhjaizl2` verifies. The distinct cells are
`up-sync-power-cut pre-exchange` and `up-sync-power-cut post-exchange`.

ADR 0334 qualifies two earlier object-pipeline boundaries. Source-linked run `1e05ayp9` stopped the
follower during the real private generic transfer temporary; after reboot its inode survived with
zero payload and startup removed it durably. Run `jtiyspp_` stopped during the private CAS install
copy; after reboot the copy was absent, the complete canonical receive survived, and startup imported
the exact object. Both preserved exact prior/completed offline views, identity, three branches per
node, convergence, and repair. Compact proofs under `.sandwurm/exports/sync-power-cut/` independently
verify. See
[`docs/evidence/2026-09-08-sync-whole-vmm-object-pipeline-power-cut.md`](docs/evidence/2026-09-08-sync-whole-vmm-object-pipeline-power-cut.md).

ADR 0335 qualifies all three pre-rename metadata-publication prefixes. Repaired-source runs
`l2gckna4`, `c9xhj26a`, and `_cphu30p` cut manifest installation, immutable branch-record
installation, and mutable pointer replacement respectively. Each reboot began
`[completed, completed, prior]` with the exact permitted metadata prefix, then removed staging,
preserved identity, converged to branches `[3,3,3]`, and repaired every node. The first pointer
attempt found a real orphan-record recovery stall; rev0049 now distinguishes reusable immutable
records from pointer incorporation, and the accepted repeat proves recovery. Compact proofs under
`.sandwurm/exports/sync-power-cut/` independently verify. See
[`docs/evidence/2026-09-08-sync-whole-vmm-branch-publication-power-cut.md`](docs/evidence/2026-09-08-sync-whole-vmm-branch-publication-power-cut.md).

ADR 0336 qualifies the adjacent post-rename/pre-parent-directory-fsync proof-v6 cells for the
manifest, immutable record, and mutable pointer. Runs `dbgtc3ip`, `jznfzx52`, and `ia70ljmf` pass
from one optimized binary; each recovered the old selected directory state with its exact temporary,
then cleaned, converged, and repaired. See
[`docs/evidence/2026-09-08-sync-whole-vmm-directory-durability-power-cut.md`](docs/evidence/2026-09-08-sync-whole-vmm-directory-durability-power-cut.md).

ADR 0337 makes byte-invalid signed tree-v2 metadata a complete fail-closed
startup and repair boundary. Current branch pointer, referenced immutable
record and manifest, signed workspace, and signed maintenance state must all
authenticate before work begins or `sync-repair` reports
`metadata=verified`. Corrupt bytes are retained rather than deleted,
quarantined, or replaced; only externally supplied byte-exact restoration can
reopen the namespace. A strict source-linked, networkless KVM/ext4 gate,
verifier, compact exporter, and guarded retention class cover the five
families. Source-linked run `mixJ9VUp` passes all five cells and retains a
strict compact proof; see
[`docs/evidence/2026-09-08-sync-tree-v2-metadata-corruption.md`](docs/evidence/2026-09-08-sync-tree-v2-metadata-corruption.md).
This detects
byte corruption, not valid-old rollback, backup provenance, dishonest storage,
or precious-data fitness.

ADR 0378 adds the first same-host block-layer dishonest-storage drill. The new
`sync-dishonest-storage-drill` helper writes generation 2 through an ext4
device-mapper snapshot, confirms it was visible, discards the snapshot COW, and
cold-reads the older valid generation 1 origin. The retained external floor
remembers generation 2 and refuses mutation. Source-linked run `run.UbmYPe1X`
retains a content-free receipt at
`.sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X/receipt.json`; see
[`docs/evidence/2026-09-17-sync-dishonest-storage.md`](docs/evidence/2026-09-17-sync-dishonest-storage.md).
This is a first substrate liar gate, not storage-media certification, full
production write-prefix replay, versioned recovery custody, or precious-data
readiness.

ADR 0379 extends the dishonest-storage drill into an ext4+btrfs matrix. The new
`sync-dishonest-storage-matrix` helper runs eight same-host block-layer cells:
valid-old rollback, cross-family rollback, torn manifest content, and
`dm-flakey drop_writes` masked write loss on both ext4 and btrfs. Source-linked
run `run.qGwEvF17` retains
`.sandwurm/exports/sync-dishonest-storage/run.qGwEvF17/matrix.json`; see
[`docs/evidence/2026-09-17-sync-dishonest-storage-matrix.md`](docs/evidence/2026-09-17-sync-dishonest-storage-matrix.md).
This is the first accepted btrfs liar matrix. Exact live Agent production
transaction-prefix replay, versioned recovery custody, and
precious-data readiness remain separate gates.

ADR 0380 adds the first exact block-prefix replay substrate. The new
`sync-log-writes-prefix-replay` helper puts ext4 and btrfs on
`dm-log-writes`, marks three IoTox-shaped synchronization boundaries, replays
those exact block-log prefixes with the `xfstests` `replay-log` helper, and
cold-mounts the replay images. Source-linked run `run.90LCC7ra` retains
`.sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra/prefix-replay.json`;
see
[`docs/evidence/2026-09-17-sync-log-writes-prefix-replay.md`](docs/evidence/2026-09-17-sync-log-writes-prefix-replay.md).
ADR 0381 adds the first live-Agent production transaction-prefix replay. The
new `sync-production-prefix-replay` helper starts the real Agent with sync
enabled, places durable Agent state plus source and sync-policy roots on
`dm-log-writes`, runs ordinary `sync-create`, `sync-publish`, and
`sync-repair`, then replays the exact ext4+btrfs block prefixes at those
transaction marks. Committed-source run `run.HYXJnDzI` retains
`.sandwurm/exports/sync-production-prefix/run.HYXJnDzI/production-prefix-replay.json`;
see
[`docs/evidence/2026-09-17-sync-production-prefix-replay.md`](docs/evidence/2026-09-17-sync-production-prefix-replay.md).
`tools/iotox-repo.sh storage-readiness` now reports the combined storage
truth: local same-host storage science including production transaction-prefix
replay is accepted; versioned recovery custody has a content-free receipt
verifier (`sync-backup-custody-verify`), but precious-data readiness remains
blocked until custody, restore, and runbook evidence are genuinely supplied by
a deployment. That custody gate is scoped to IoTox sync-layer recovery; it does
not claim disk-loss, host-compromise, or filesystem-wide corruption protection.
IoTox does not certify storage media. The read-only
`sync-precious-data-gates-plan` helper inventories backup/restore capabilities
and writes invalid-by-default custody/runbook templates without formatting or
mounting anything. See
[`docs/storage-readiness-gates.md`](docs/storage-readiness-gates.md).
ADR 0401 adds the native operator path around that boundary:
`iotox sync backup plan|verify|receipt` runs content-free restore comparison
and mints backup-custody / restore-drill receipts only when the custody shape
is honest, `iotox sync retention set|status` records a reviewed guarded-GC /
delete-propagation policy, `iotox evidence collect sync` gathers the
shape-checked receipts into a stable evidence directory, and
`iotox sync precious-status` is the read-only dashboard that can say
`operator-signable` without claiming IoTox is the only archive. ADR 0402 adds
`iotox sync precious-signoff`, which freezes that green state into a
content-free operator receipt binding the evidence hashes and a hashed dataset
selector. That receipt is local acceptance, not repo certification.
ADR 0403 records the current accepted sync long-soak proof for that path:
compact proof `.sandwurm/exports/three-writer/run.2nPKtCoX` verifies with
288 soak cycles, 27h04m13s of soak elapsed, zero stalled-cycle recoveries, and
`contains_secrets=false`. Use
`tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json`
to mint the native `sync.long-soak` receipt consumed by
`iotox evidence collect sync`; the raw guest receipt inside the proof is kept
as lab evidence, not as the stable gate input.

ADR 0382 flips the Ratox product default in a bounded way: `--mode self` is now
the explicit self-machine mode that selects Ratox host/controller roles while
leaving profile binding, `interactive.terminal`, route policy, and sudo
explicit. This is the start of IoTox-owned multidevice above Tox, not a Tox
multidevice dependency. See [`docs/self-mode.md`](docs/self-mode.md).
ADR 0383 implements the first self-swarm layer above that mode: an
owner-signed roster with native create/join/retire/inspect/verify/plan/apply
commands. It can render and apply narrow self grants through the existing
authority ledger and retire lost machines, while stale generations, wrong
owners, wrong stable principals, wrong route keys, and retired grant targets
fail closed. ADR 0384 adds local self-swarm generation/digest floors,
explicit `fanout-plan`/`fanout`, and optional live alias-route proof before
grant/fanout work. It is still a reviewed roster workflow, not a background
authority daemon or a second authority ledger.
ADR 0385 adds the first person layer above that private roster:
`iotox person` creates a public owner-signed delivery card with active Tox
route keys only, signs bounded person-message envelopes, plans exact
`message-hex key:...` fanout, live-sends only after all routes resolve to
current friends, and verifies received payloads independent of the route. ADR
0386 adds the daily-use/group substrate: person-signed sender delegations for
stable device principals, contact-side delivery-card floors, local seen stores,
signed group descriptors, direct/delegated group-message envelopes, and
review-only group fanout plans through member cards. ADR 0387 adds the first
native messenger stores: a contact book that pins delivery-card floors, a local
contentful transcript, delegated device receipts, and a durable reviewed
outbox. The outbox can now be driven by `person outbox-send`, a one-shot
native sender that marks each route only after local Tox transport acceptance.
`person receive` is the ordinary receive porch for local devices: it verifies a
payload, commits transcript and duplicate-suppression state idempotently, and
can create one delegated device receipt without overwriting an existing file or
commit it into the aggregate receipt store. `person receipts-status` answers a
content-free explicit-expected-device rollup, and `person messenger-status`
reports local store health, receipts, and outbox route accounting. Normal Tox
compatibility is now a bridge, not identity
interop: `person tox-bridge-plan-in-delegated`,
`tox-bridge-plan-out-delegated`, live `tox-bridge-fanout-in-delegated`,
`tox-bridge-send-out-delegated`, `tox-bridge-receive`, and
`tox-bridge-status` wrap ordinary Tox text/action messages as delegated self
device observations for internal self-device fanout. External Tox public keys
remain external route identities, not IoTox person keys. The bridge is
qualified against stock Toxic for the default native route. Forced-TCP/native-relay
compatibility works repeatedly and the lab now retries slow friendship
propagation while using a refreshed numeric TCP-capable Toxic bootstrap set;
it still remains degraded pending a boring follow-up soak. Tor/I2P bridge
qualification is a separate evidence-gated route check, not a silent fallback
or anonymity claim.
It is still not a finished human messenger, but the background lane is now
native enough to run as an ordinary resident service: `person
quickstart`, `person outbox-retry-plan`, `person card-refresh-plan`,
`person outbox-expire`,
`person background-plan`, and `person background-run` cover bounded retry,
attempt accounting, receipt rollup, freshness review, and dead-letter
expiration. `iotox service plan|render|receipt|status-plan|status-receipt`
now drafts systemd, NixOS, and MonsterNix-adapter shapes for the
Agent/sync/Ratox service and the person background worker together, then
records observed active/enabled/log/health/upgrade status when the operator
has checked it. `person read-mark`, `person read-status`,
`person transcript-convergence`, `person group-status`,
`person graduation-check`, `person tox-bridge-graduation-check`, and
`route-qualification-check` make local human-read UX, transcript set
convergence, group summaries, lived messenger readiness, normal Toxic bridge
readiness, and route claims explicit.
Guaranteed delivery to never-online devices, global transcript total order,
independent freshness custody, and automatic Tox group/conference adapters
remain open.
See
[`docs/person-multidevice.md`](docs/person-multidevice.md).

For one sync candidate directory, `iotox sync trust-plan PATH ...` now prints
the ordinary non-mutating trust runbook, `tools/iotox-repo.sh
sync-precious-data-gates-plan --dataset PATH ...` prepares the repo-level
backup-custody and recovery-runbook checklist without touching disks, and
`iotox sync-dataset-readiness PATH ...` joins local source preflight,
backup/restore command planning, optional inline restore
verification with `verify-recovery=1`, and the explicit
`precious-data-repo-certified=0` nonclaim. These help operators decide
“working-copy candidate,” not “delete every other recovery path.”
The more ordinary precious-data path is now native too:
`iotox sync backup verify PATH ...` proves the restored tree matches the backup
tree, `iotox sync backup receipt PATH ... --out DIR` writes content-free
backup-custody and restore-drill receipts when the labels satisfy the scoped
versioned recovery-custody shape, `iotox sync retention set NAMESPACE ... --out PATH`
records the reviewed retention/GC policy, `iotox sync runbook receipt PATH ...
--runbook FILE --accept-reviewed-runbook --out PATH` hash-binds a reviewed
content-free recovery-runbook receipt to the dataset selector, and
`iotox evidence collect sync PATH read-write 30 --out DIR ...` copies only
shape-checked receipts before writing a stable manifest. `iotox sync
precious-status PATH read-write 30 --evidence-dir DIR` is the one human
answer: blocked until storage-readiness, long-soak, backup custody, restore
drill, runbook, and retention policy are all accepted; then
`operator-signable`, still with `repo-certified=0`. `iotox sync
precious-signoff PATH read-write 30 --evidence-dir DIR --reviewer LABEL
--accept-operator-responsibility --out PATH` is the durable handoff receipt:
it refuses to write unless `precious-status` would pass, stores hashes instead
of dataset contents or the literal dataset path, and repeats the nonclaims.
`iotox sync graduation-check PATH ...` is the stricter fail-closed porch: it
requires labels for local preflight, storage-readiness, recovery
custody, restore drill, and recovery runbook before it records
`working-copy-graduation=operator-attested`, while still keeping
`precious-data-readiness=blocked`.
The release gate is explicit: `iotox ship-check sync stable` fails closed for
no-concern shipping, while `iotox ship-check sync founder-preview` is the
bounded working-copy channel with versioned recovery custody. ADR 0398 makes the
stable sync gate stricter than label collection: the manifest must hash-bind
receipt-shaped storage-readiness, long-soak, backup-custody,
restore-drill, and recovery-runbook evidence, and placeholder prose is rejected
before it can become a precious-data claim.

ADR 0326 upgrades the isolated `ratox-sudo-vm` gate without widening privilege defaults. It retains
one test-only noninteractive sudo branch and adds a UID-1000 owner login shell that receives a real
NixOS PAM password prompt through the production PTY, reaches UID 0 only in the sudo child, returns
to UID 1000, and never echoes the submitted password. This proves one concrete sudo/PAM
conversation—not arbitrary host policy, hardware tokens, or remote Tox traversal. ADR 0349 hardens
that VM qualification against shell/termios handoff timing and adds bounded PTY timeout diagnostics;
it changes no product privilege semantics.

ADR 0327 adds the first positive named Ratox cgroup/PSI kernel gate. The `ratox-cgroup-vm` NixOS KVM
check runs all five delegated-cgroup process oracles under transient systemd `Delegate=yes` services:
boot-bound orphan recovery, memory/pids, CPU throttling, actual I/O accounting, and PSI pressure
admission/trigger registration. This qualifies one Linux 6.6.94 NixOS/systemd slice, not arbitrary
distros, parent cgroup policy, physical devices, trigger latency, Tox traversal, or production
activation.

ADR 0328 closes a narrow synchronization storage race: a source file changed through an already-open
writer descriptor after tree scan now has an owned fail-closed CAS installation test. Stale scanned
bytes do not become an immutable object and install temporaries are removed before a fresh rescan can
publish the new content. This is direct descriptor-race coverage, not power-cut, corrupt-record, or
backup evidence.

The running Agent now keeps a bounded stable-device-signed, content-free diagnostic tail. Export
creates a new private support bundle and offline inspection validates its closed grammar and digest:

```sh
iotox --runtime /run/user/$UID/iotox diagnostics-export /absolute/path/iotox.diagnostics
iotox diagnostics-inspect /absolute/path/iotox.diagnostics
```

The complete stable command vocabulary is also available as deterministic shell source:

```sh
source <(iotox completion bash)
iotox completion zsh
iotox completion fish
```

ADR 0317 established the registry at 199 spellings; ADR 0319's recovery verifier makes the current
population 200. All three generators use that same registry as the help index and parser
classification. They do not query peers or complete paths, secrets, namespaces, or remote state;
installation examples are in [`docs/cli-completion.md`](docs/cli-completion.md).

The v3 payload contains event classes, coarse counts, feature/state bits, product identity, anonymous
aggregate tree-v2 health, normalized passive host-confinement capability grades, and a
path/key/endpoint-free structural configuration commitment. It
contains no peer identity, Tox address, messages, terminal/command content, filenames, namespace
names or commitments, paths, endpoints, credentials, raw config,
signatures, or timestamps. It can still correlate activity and configuration. The local ring is
device-authenticated; the deliberately identity-free shareable bundle is only integrity-checkable,
not remote attestation. See [`docs/diagnostics.md`](docs/diagnostics.md) and ADRs 0291/0298/0299.

Human names can now replace friend numbers and hex in established-peer commands without replacing
their key binding:

```sh
iotox peer-alias-set workstation key:PEER_PUBLIC_KEY_HEX
iotox action workstation maintenance-starting
iotox terminal alias:workstation --reconnect
iotox peer-aliases
```

Aliases are lowercase owner-local names in a stable-device-signed one-to-one store. Explicit
`friend:`, `key:`, and `alias:` forms remove ambiguity. Collisions and implicit rebinding fail;
transport peer removal retains the name until `peer-alias-remove`, preventing silent takeover.
Aliases grant no authority and bind the Tox key, not a claimed hostname or stable device principal.
See [`docs/peer-aliases.md`](docs/peer-aliases.md) and ADR 0292.

Initial introduction now has an equally explicit signed artifact:

```sh
iotox peer-invitation-create ./workstation.iotox-invitation 86400 \
  workstation interactive.terminal,sync.subscribe
iotox peer-invitation-import ./workstation.iotox-invitation EXPECTED_DEVICE_KEY
iotox peer-invitation-accept ./workstation.iotox-invitation EXPECTED_DEVICE_KEY
```

The fixed artifact binds the inviter's stable device identity to its exact current Tox address,
expiry, random nonce, optional alias, and closed requested-capability set. Inspect establishes no
trust; dry import requires the independently pinned inviter and mutates nothing. Accept creates only
ordinary Tox friendship and an optional exact alias, is retry-idempotent while valid, and always
grants zero authority. See [`docs/peer-invitations.md`](docs/peer-invitations.md) and ADR 0293.

The tree-v2 lifecycle commands are explicit and owner-local:

```text
iotox sync-checkpoint NAMESPACE
iotox sync-pin NAMESPACE BRANCH_RECORD_HEX
iotox sync-unpin NAMESPACE BRANCH_RECORD_HEX
iotox sync-retention NAMESPACE
iotox sync-gc NAMESPACE dry-run|quarantine
iotox sync-restore NAMESPACE
iotox sync-writer-cutoff NAMESPACE WRITER_PUBLIC_KEY_HEX
```

`quarantine` is recoverable and there is no purge mode. A cutoff must be performed on every
survivor and does not replace general authority revocation. See
[`docs/everyday-sync-plan.md`](docs/everyday-sync-plan.md) for the operational sequence.

ADR 0294 adds a bounded forward-only time machine above those retained records:

```text
iotox sync-history NAMESPACE [LIMIT]
iotox sync-diff NAMESPACE FROM_RECORD_HEX TO_RECORD_HEX
iotox sync-conflicts NAMESPACE [RECORD_HEX]
iotox sync-restore-plan NAMESPACE RECORD_HEX
iotox sync-restore-forward NAMESPACE RECORD_HEX PLAN_ID_HEX
```

The plan binds the exact current frontier, policy, signed maintenance/workspace state, clean
worktree, target, and required objects. Apply refuses any stale or incomplete plan and authors a new
higher local generation; it never rewinds a signed branch. This retained history is not a backup or
independent rollback witness. The older `sync-restore` command repairs GC quarantine only. See
[`docs/sync-time-machine.md`](docs/sync-time-machine.md).

ADR 0295 adds sparse custody and on-demand widening without giving the peer path authority:

```text
iotox sync-interest NAMESPACE [include=PATH|exclude=PATH...]
iotox sync-interest-clear NAMESPACE
iotox sync-pull PEER NAMESPACE
iotox sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]
```

No rules inspects the current local interest; supplied rules atomically replace both rule sets;
clear restores complete intent. Tree-v2 still fetches and verifies the complete signed metadata
closure, but transfers only selected file objects. Status, repair, and GC say `custody=partial` and
report selected/skipped coverage rather than calling the node a complete replica. Widening plus an
ordinary pull fetches newly selected bytes without translating formerly unprojected absence into a
deletion. See [`docs/sync-sparse-custody.md`](docs/sync-sparse-custody.md).
ADR 0296 lets multiple authenticated primary-lane sources satisfy the primary's frozen tree-v2
frontier: exact `absent`/`unavailable` results advance only that digest to the next source, while
every received byte remains digest-verified and no source gains branch, path, or activation
authority. ADR 0329 adds bounded same-source tree-v2 object pipelining over those frozen frames and
projects `tree-lane-cap`, `active-lanes`, and `tree-lane-job=` status. ADR 0330 batches complete file
windows through one existing strict CAS admission pass and retains exact late FileIds long enough to
cancel offers that arrive after pull settlement. Aggregate and per-job status expose batch width,
staged objects, late cancellations, retained IDs, and bounded-retirement evictions. Tree-v2 routed
transfer and intra-object striping remain later work. ADR 0331 reuses an opaque verified CAS view
across those local batches and requires a fresh strict effect-fence scan before signed branch or
projection state can advance. `sync-status` exposes full-scan and inspected-object counts so this
optimization remains falsifiable. Completed tree-v2 pull snapshots also report the final local
reconcile/apply counters with `reconcile-` prefixes, separating network/object transfer from
source/CAS/projection work.

The running Agent can now turn those scattered facts into one durable health observation:

```text
iotox sync-health NAMESPACE
iotox sync-health NAMESPACE cached
```

ADR 0297 refreshes the tree-v2 frontier, selected content, workspace/worktree, conflicts, cutoffs,
automation, store headroom, and last source evidence, then atomically commits a content-free
stable-device-signed green/yellow/red record. Expected sparse custody can be green while remaining
explicitly partial. Every result says `rollback-witness=0 backup-certified=0`; see
[`docs/sync-health.md`](docs/sync-health.md).

Content-v2 namespaces now build a real bounded
flat or paged content-addressed fabric, prospectively admit the complete object set, import every
verified object, and sign HEAD last. A bounded one-source subscriber now bootstraps the signed root,
persists every FileId/object join, reconstructs whole-artifact CAS, and accepts HEAD last. Agent
dispatch, exact-token activation, reachability, repair, and quarantine-only GC are live, and the
same paged 4 MiB revision passes independent source-linked Sandwurm guests over direct UDP and
forced TCP. Exact multi-source consumption is now live behind the same content gate:
`sync-source-add JOB_ID FRIEND` attaches an independently authorized writer to one active pull,
consumes exact sparse availability, and binds selected object traffic to that primary peer while the
original signed HEAD remains frozen. When the complete set is known up front,
`sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]` authenticates and installs every source before
the primary HEAD can dispatch. Two complementary deterministic stores both contribute before
whole-artifact reconstruction and HEAD-last acceptance. The same three-agent path now passes genuine
c-toxcore over direct UDP: both live sources answer availability and contribute objects before
activation. A destructive companion stops the selected secondary during object work, proves the
first job fails with no accepted HEAD or activation, restarts the same identity at a higher epoch,
and converges only through a distinct explicit atomic pull. The secondary now uses
`sync-replica-import NAMESPACE SIGNED_HEAD_PATH`: the original foreign signature is wrapped in
device-authenticated availability custody, `published-heads` stays absent, present partial-graph
objects remain GC-rooted, and compact proof `pair.w_ws202c` cold-starts without HEAD reinjection.
ADR 0258 additionally
implements `sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]`. Every source
retains its independently authenticated primary writer/HEAD session, while availability, object,
FileId, CTA1, and terminal effects freeze before HEAD to one exact content-capable auxiliary worker
in the named native/Tor/I2P class. The deterministic complementary-store path converges across two
auxiliary identities, refuses principal substitution and post-HEAD rebinding, and fails the whole
job on exact carrier loss. The one-source product path now also passes genuine mixed-route Sandwurm:
direct-UDP primary authority and the signed HEAD remain native while an exact `tox/tor` worker moves
the paged 4 MiB revision through two actual Tor processes in one pull with zero failure or
reassignment. Compact proof `pair.fahovlrg` preserves the separate authority/carrier commitments.
The routed multi-source companion now also passes. Two independently authorized native publisher
sessions contribute five-plus-one complementary objects through two distinct exact `tox/tor` worker
identities in one atomic pull; per-source status binds each principal to its worker, HEAD stays on the
primary, activation remains explicit, and both TAP captures report zero unexpected-context packets.
Compact proof `pair.j0z04_2i` independently verifies (ADR 0259). This does not claim that the primary
authority sessions traverse Tor, that the two source lanes use independent Tor circuits or physical
paths, anonymity, or a performance win.
The destructive companion now also passes. Compact proof `pair.w31xqgd_` stops the selected second
Tor worker at 72,663 bytes after positive immutable-object progress, fails the original job with no
downgrade or reassignment and no HEAD/activation effect, recovers the same signed route under a new
worker incarnation while both native epochs remain unchanged, then converges only through a distinct
explicit pull (ADR 0260). Compact proof `pair.i8ar90tx` repeats that unchanged contract through a
second compiled public Tox relay record on port 443. It faults at 76,776 bytes and preserves the
same fail-closed outcome, while deliberately leaving exit/operator diversity, separated time
windows, long-running policy, anonymity, and performance unclaimed (ADR 0261).
ADR 0262 now enables bounded same-source object concurrency without changing content framing.
`--max-sync-content-lanes N` remains default `1`; signed namespace lane and outstanding-request
quotas can only tighten it. Root and HEAD phases remain serial while independently verified pages
and chunks may overlap with exact per-lane request/FileId/CTA1 attribution. Compact Sandwurm proofs
`pair.895m5lwy` and `pair.bcecui0l` observe two admitted non-root lanes from one source over direct
UDP and forced TCP, then exact convergence and activation. This is one-session object concurrency,
not byte striping or multiple physical paths. ADR 0263 adds stable-session `1/2/4/8` lane science on
one deterministic 8 MiB revision. Direct UDP is non-monotonic; forced TCP improves from
301,423 B/s at cap 1 to 420,481 B/s at cap 4, then plateaus at cap 8. The ordinary default remains
one; that first ordered result is retained as historical evidence. Compact proofs are
`pair.amcrp0_3` and `pair.805kzu4a`.
Tree-v2 now has the separate `--max-sync-tree-lanes N` process cap (`1..64`, default `4`) for exact
file-object lanes after the signed manifest expands. It preserves one FileId/source/staging/terminal
proof per object. Complete file lanes are held only within that bounded window and share one strict
CAS inventory/quota/import pass; signed state and projection still wait for the complete verified
closure. It does not claim byte striping, auxiliary-route distribution, ACID multi-object commit, or
backup readiness.
ADR 0264 now closes that first competing-terminal gate without session churn. One 720-sample Ratox
attachment spans content caps 1, 4, and 8 while cap 2 runs as a transfer-only pause. Direct UDP and
forced TCP retain the same terminal identity and Tox epoch through all phases. Cap 4 is the smallest
simultaneous-Ratox throughput winner in both accepted cells; cap 8 regresses against cap 4 and
worsens p95 terminal latency on both routes. Owner-queue p95 stays far below end-to-end p95, so
local command scheduling does not explain most of the observed tail. Default one and frozen Ratox
framing remain unchanged. Compact
proofs are `pair.af873531` and `pair.a3nglkh3`.
ADR 0265 separately proves a fresh terminal OPEN after cap-8 reliable completion on both carriers.
ADR 0266 then closes phase-order bias with genuine `1,2,4,8` and `8,4,2,1` cells. The paired UDP
winner is cap 8 by only 0.81% over cap 4 while using 21.3% more CPU ticks; forced TCP instead favors
cap 2 over cap 4 by 4.56% with 21.0% fewer ticks. Across both routes cap 4 leads cap 2 by just 0.013%,
while cap 2 uses 14.8% fewer ticks. Default one remains; explicit cap 2 is the efficient
mixed/relay-heavy bulk recommendation, cap 4 is the controlled direct-UDP option, cap 8 is
stress-only, and automatic tuning remains unqualified. Compact proofs are `pair.t6b6exf1`,
`pair.ku2fxml0`, `pair.70p2plez`, and `pair.o_6q_m1n`.
ADR 0267 closes the corresponding unclean client-restart gate at explicit caps 2 and 4. Four
final-tree cells over direct UDP and forced TCP kill only the subscriber while exactly two or four
object lanes are live. Startup preserves the exact verified CAS inventory, removes transport-owned
pre-rename residue, leaves no canonical partial, and permits convergence plus activation only after
two-sided authority recovery and a distinct fresh pull. Compact proofs are `pair.8j7v2irm`,
`pair.9q9hsx40`, `pair.8ulddb9t`, and `pair.ol5goyug`; default one and all framing remain unchanged.
ADR 0268 now freezes and passes the missing cap-two interactive gate. Before either carrier cell,
the construction SLA required at least 40 exact content-overlap samples, p50/p95/p99/max no greater
than 250/500/1,000/1,500 ms, and owner-queue p95 no greater than 10 ms. One 960-sample Ratox
attachment then spans ordered caps 1, 2, 4, and 8 on one Tox epoch under the existing 4 Mbit/s
subscriber shaping. Explicit cap 2 passes every bound over direct UDP and forced TCP, improving
content rate over cap 1 by 2.75% and 9.92%. Caps 4 and 8 miss the p95 ceiling on both carriers.
Default one remains; cap 2 is a deliberately selected native interactive-bulk construction profile,
not an automatic or bandwidth-independent policy. Compact proofs are `pair.rpblreul` and
`pair.rwiyixfh`; Ratox and content framing remain unchanged.
ADR 0269 now closes the same-source auxiliary-carrier construction gate without changing framing.
Repeating one source selector in `sync-pull-multi-route` asks Agent to bind that same principal and
primary authority session to another distinct ready worker in the named class. Whole immutable
objects, never object-byte ranges, are assigned to the frozen exact carriers. Owner-private
per-path counters prove positive contribution; terminal correlation uses the full carrier tuple, so
the accepted cell safely contains `friend=0` on both isolated workers. Actual-Tor compact proof
`pair.iiuhmhy0` commits 272 bytes on one route and 4,194,560 bytes on the other, receives all four
availability results, accepts the original HEAD last, and explicitly activates. Default one,
fail-closed exact-carrier loss, and every peer/local-control frame remain unchanged. Both workers per
guest share one Tor process and relay target, so this is logical whole-object distribution—not byte
striping, balancing, a speedup claim, circuit independence, physical bonding, or failover.
Three-agent multi-source forced TCP remains unqualified after thirteen bounded cells separated relay
count, admission order,
pending-request delivery, reusable-key pre-accept, full-address rendezvous, and A/B route placement.
The strongest hybrid briefly confirmed the secondary TCP/application session, then lost it before
v3 authority and object work. Relay sockets and transient confirmation are not durable source proof.
Same-source auxiliary-path distribution is now qualified only in the bounded ADR 0269 construction.
A separately negotiated
`state-sync-ranges-v1` extension now verifies the successor manifest first, plans only against the
exact artifact named by the current accepted HEAD, and transfers one bounded canonical missing-range
bundle through an explicit FileId. Its deterministic full-Agent proof fetches 4 KiB, reuses 12 KiB,
reconstructs an exact 16 KiB generation-2 artifact, and accepts the linked HEAD last. The deterministic
path now also treats an absent or corrupt accepted basis as a failed optimization: it requests and
fully verifies the complete successor, exposes `range-fallback=1`, and still accepts HEAD last without
deleting or replacing the unusable prior object. The genuine single-file baseline now passes in
two concurrent Sandwurm guests over direct UDP and forced TCP. An 8 MiB follow-up now also passes
after an unclean receiver-daemon restart on both carriers: recovery fences lost transport handles,
removes only exact signed-attempt-scoped private temporaries, preserves identity, retries the exact
revision, and still accepts HEAD last before explicit activation. Live cancellation after positive
c-toxcore progress also passes on both carriers without acceptance or activation. A genuine
TAP-blackhole gate fails the interrupted pull, clears its partial staging, advances both
authenticated online epochs, waits through a five-second stability window, and converges only after
an explicit fresh whole-object pull. A separate rate-shaped gate pauses one admitted receive at a
positive partial provider position, holds the same file number and FileId stable for two seconds,
resumes it, and converges normally on both carriers. ADR 0223 now adds the lower transport primitive
for cross-carrier byte resume: an exact caller-owned private prefix survives loss, c-toxcore seeks to
its size, and completion rechecks the same inode. ADR 0224 now integrates that primitive for
same-process whole-object reassignment. A fresh attempt, FileId, and authenticated worker inherit the
prefix while the complete digest still gates commit; deterministic Agent evidence resumes three
bytes across two workers, and fail-closed policy retains none. Startup cleans strict inactive
burned-ID handoff debris but still restarts incomplete transfers from zero. Genuine direct-UDP and
forced-TCP two-guest cells now retain and resume both positive concurrent object prefixes with exact
aggregate byte equality, zero fallback/residual partials, full convergence, and protected Ratox
afterward. An actual-Tor process-loss cell now does the same after the host kills the real client Tor
process and reassigns to a native auxiliary, with zero IoTox worker restart. Positive I2P range
transport and explicit fresh recovery after live I2P range loss are now qualified separately below;
I2P same-handle/carrier-loss prefix resume, Tor-to-Tor, and repeated-late or four-plus loss remain
open. Native two-loss, 15/16 late-range, bounded three-loss, and daemon-restart range continuation
are qualified below.

Route-set v2 now signs each member's exact coarse native, Tor, or construction-I2P class. Agent
startup, worker construction, and coordinator authentication all require agreement; v1 remains
byte-compatible and explicitly class-unspecified. Existing private inventory/member frames need no
change because their complete-artifact digest already binds the new byte. Accepted compact proof
`pair.q2pka1fm` observes the signed classes on both genuine guests and converges one fail-closed
signed tree through the exact actual-I2P member with native ready and zero reassignment (ADR 0225).
Its destructive companion `pair.jbr89_gc` stops that router after 69,921 bytes, proves one blocked
job and zero native reassignment, recovers the same signed member without an IoTox worker restart,
and completes only through an explicit fresh class-pinned pull (ADR 0226).

ADR 0227 now carries the already-frozen range-v1 request/result frames over an exact authenticated
auxiliary route without changing their encoding. Both the primary authority session and the selected
worker must negotiate `state-sync-ranges-v1`; the parent intersects those facts before admitting a
range. Accepted compact proof `pair.ej_4507n` builds a native 4 MiB generation-1 basis, pins its
generation-2 successor to the signed construction-I2P member, reuses 4,194,176 verified bytes, fetches
one 128-byte range over that exact member, and activates the reconstructed artifact with zero
reassignment or router/front restart. ADR 0228 adds the destructive companion. Compact proof
`pair.a9zwongf` stops the client router after 86,373 bytes of a concrete 1 MiB range, proves strict
staging cleanup, one blocked fail-closed job, and zero reassignment, then recovers the same signed
member without an IoTox worker restart. Only explicit cancellation plus a distinct fresh job may
fetch the complete 1 MiB range, reuse the verified remaining 3 MiB, reconstruct, accept, and activate
generation 2. This closes bounded live-range loss and explicit fresh recovery, not I2P carrier-loss
prefix reuse or implicit continuation. `iotox routes` now exposes content-free auxiliary transport,
application, reciprocal-binding, epoch, range-negotiation, frame-counter, and failure state so a
future rejected recovery identifies its exact layer without changing peer framing.

ADR 0229 removes the avoidable manifest refetch from that recovery path. A range pull now applies the
same exact digest/size/shape proof used by whole-object retry to its durable manifest prerequisite;
corruption fails locally and is never overwritten implicitly. Accepted compact proof
`pair.ip5q0at9` repeats the destructive actual-I2P gate from clean commit `704a3c7`: after a
71,292-byte failed range prefix is discarded, the distinct fresh job requests exactly one object,
commits two, reuses the 786,496-byte manifest locally, fetches only the complete 1 MiB range, and
activates the same exact 4 MiB target. This removes 42.86% of the qualified recovery-phase transport
bytes without changing framing, authority, HEAD ordering, or the failed-I2P-prefix nonclaim.

ADR 0230 closes a narrower failed-prefix case without weakening those I2P loss rules. Every
seek-capable range receive now owns its exact private attempt inode from byte zero. One bounded
same-process, same-job, same-carrier retry may finish and fence the old signed attempt, hand that
strict prefix to a fresh attempt, allocate a fresh message ID and FileId, seek to the exact byte
count, and receive only the suffix. Clean Sandwurm proofs `pair.cj5y5vgt` and `pair.qeb99i4o` retain
and resume 15,081 direct-UDP bytes and 24,678 forced-TCP bytes respectively, with zero discard and
zero fallback, before reconstructing and explicitly activating the same exact 4 MiB generation 2.
This is not same-handle, cross-carrier, carrier-loss, explicit-fresh-job, or restart continuation;
ADR 0228's failed I2P range prefix remains discarded.

ADR 0231 closes the next native available-policy edge. A live 1 MiB range may retire its dead
auxiliary receive, finish and fence the old signed attempt, hide the old FileId, hand only an exact
strict prefix to a fresh attempt on the other authenticated range-capable carrier, and seek before
suffix receive. Compact proofs `pair.urbhf0je` and `pair.n76biwao` retain/resume 283,797 direct-UDP
bytes and 293,394 forced-TCP bytes with zero discard/fallback, one loss/reassignment/stale terminal/
recovery, complete 4 MiB verification, HEAD-last acceptance, and explicit activation. Fail-closed
I2P still discards and blocks. Deterministic coverage now repeats the handoff through three losses:
one 50% prefix grows to 75%, then 87.5%, and moves onto a fourth fresh carrier with every stale
generation fenced and no retry-budget consumption. ADR 0232 closes the corresponding genuine
two-loss native row.
Compact proofs `pair.le38qcl5` and `pair.8u14ddcy` preserve/resume cumulative exact prefixes of
542,916 direct-UDP bytes and 564,852 forced-TCP bytes through two losses, reassignments, stale
terminals, recoveries, and worker restarts, with zero discard/fallback and full verification/
activation. ADR 0233 separately faults one native range after 15/16: `pair.tev4u3rs` preserves
984,378 direct-UDP bytes and `pair.1z7_d0jn` preserves 995,346 forced-TCP bytes, leaving only 64,198
or 53,230 bytes for the fresh carrier attempt. Both converge with zero discard/fallback. Repeated
late loss, four-plus loss, and multi-source striping remain unqualified. ADR 0242 freezes the
multi-source authority prerequisite: one verified content-v2 HEAD stays authoritative, and any
additional immutable source independently needs exact-head v3 proof, `sync.publish`, writer
membership, and that identical HEAD digest. ADR 0244 allocates feature bit 29 and canonical
object types 28/29, with a bounded flat/paged coordinator, exact CAS resolver, subscriber-gated
publisher, replay retention, deterministic two-source scheduling, source-loss fencing, and exact
reconstruction. ADR 0245 adds exact sparse
availability types 30/31; two authorized even/odd partial stores now deterministically reconstruct
the frozen artifact without claiming complete mirrors. ADR 0246 strictly inventories the canonical
SHA-256 CAS and counts flat plus CAS physical objects against one transaction-bound namespace quota;
ADR 0247 then makes root-manifest and coordinator page/chunk commits use canonical private staging,
verified-copy publication, and prospective combined quotas. ADR 0248 adds a distinct signed CTA1
journal that binds HEAD/object/FileId/source/carrier before effect, safely finalizes exact complete
staging after restart, and fences partial or absent work without reviving a carrier. ADR 0249 adds
the local product publisher: flat or paged construction occurs in an exact private workspace, the
complete deduplicated object set is admitted and committed to CAS, and the stable-device-signed HEAD
lands last. ADR 0250 completes root-manifest bootstrap and the one-source transport-neutral receiver:
early offers stay paused until their exact result, whole-artifact CAS precedes accepted HEAD, and
retry closes the post-CAS/pre-HEAD crash window. At that boundary Agent dispatch, activation,
accepted reachability, and repair/GC were still dark. ADR 0251 closes that deterministic product
boundary: content services
dispatch HEAD/object packets and exact FileId/terminal truth on the primary carrier; startup
authenticates the persisted live graph before dynamically advertising bit 29; ordinary pull/status/
cancel controls select the owning engine; accepted HEAD remains last; explicit exact-token
activation rechecks the whole artifact and manifest; and repair plus authenticated quarantine-only
GC are live. ADR 0252 carries that paged revision across genuine c-toxcore in two simultaneous
Sandwurm guests over direct UDP and forced TCP, with one pull, zero failure, HEAD-last acceptance,
and explicit activation. ADR 0254 adds the explicit owner-local multi-source entrance and exact
sparse-window consumption. Every source needs its own exact-v3 `sync.publish` proof and writer
membership; the original HEAD stays authoritative. ADR 0258 enables auxiliary content carriers with
primary authority/HEAD unchanged and exact pre-HEAD worker binding; its one-source actual-Tor product
gate is accepted. ADR 0259 accepts complementary routed multi-source convergence through two exact
actual-Tor worker identities and adds bounded per-source carrier evidence; I2P content-v2 remains
unqualified. ADR 0269 separately binds one principal/authority session to two exact actual-Tor
workers and proves positive whole-object contribution through both without claiming byte striping.
ADR 0260 qualifies selected
actual-Tor worker loss as whole-job failure, exact-route recovery, and explicit fresh-job convergence
without native downgrade or same-job continuation. ADR 0261 repeats that safety boundary through a
second public relay record without widening it into exit, time-window, or long-running evidence. ADR
0262 enables two exact same-source object lanes over direct UDP and forced TCP while keeping root/HEAD
serial and leaving byte striping plus performance unclaimed. ADR 0267 qualifies unclean
client-daemon restart at explicit caps two and four on both native carriers: verified complete CAS
objects survive exactly, transport-owned partials are removed, old attempts are fenced, and only a
distinct authorized pull may activate. ADR 0268 qualifies one already-attached Ratox session at
explicit cap two against a predeclared native-carrier construction SLA without raising default one
or changing framing. ADR 0255
accepts the direct-UDP genuine-provider gate and preserves the bounded forced-TCP rendezvous
falsification without generalizing it into a c-toxcore limit: more or reordered relay paths,
ordinary pending acceptance, mutual key pre-provision, and hybrid pre-accept/address rendezvous are
not sufficient; the strongest transient second session dies before authority. ADR 0256 adds atomic source admission
and qualifies explicit fail-closed recovery after selected-source loss. ADR 0257 gives that partial
source a distinct device-authenticated availability-only replica store: the foreign HEAD never enters
local publication, present graph bytes remain GC-rooted, and a true cold start serves them without
post-start reinjection. ADR 0258 freezes the complementary deterministic source lanes onto two exact
auxiliary identities and adds atomic named-route local control without changing peer framing. ADR
0259 carries that shape through genuine c-toxcore with two native authority sessions and distinct Tor
workers, and repairs strict preflight so it validates exact worker endpoint replacements. ADR
0235 closes a
separate three-loss native gate: compact proofs `pair.3iufekzy` and `pair.zleebk2k` preserve 862,359
direct-UDP or 871,956 forced-TCP bytes through three handoffs with zero discard/fallback. Its
instrumented calibration exposed a transport-online/application-offline reconnect race; ADR 0236
now retries the same frozen HELLO and CAPABILITIES records at a bounded cadence and surfaces their
content-free attempt counters without changing peer framing or authority. The next diagnostic
reached a distinct four-entry scheduler tombstone ceiling after retaining 542,916 bytes. ADR 0237
now binds that fence
history to host-local namespace policy and grants only the triple fixture its exact fifth record;
stale-event fences are never evicted. ADR 0238 renders the signed restart ceiling and derived
remaining capacity separately; both accepted cells leave the twice-restarted route healthy with no
restart capacity remaining.

ADR 0234 now implements a distinct whole-object restart boundary without reviving dead transport
state. Startup marks only a strict positive canonical prefix as restart-retained in the
stable-device-signed attempt journal. A fresh authorized pull must verify a signed HEAD naming the
identical digest and size, then uses fresh job/message/FileId/attempt identities to inherit the inode
and seek. Full digest verification, HEAD-last acceptance, and explicit activation remain unchanged;
unmatched retained work is pruned. Deterministic tests pass, and genuine `sync-file-restart-resume`
compact proofs `pair.f20ma62y` and `pair.lj0pdz6a` retain/resume two exact prefixes totaling 115,164
direct-UDP or 159,036 forced-TCP bytes. ADR 0239 now implements the range-bundle prerequisite:
plan-bound ATM1 records retain only a strict incomplete prefix, and only a fresh authorized pull
deriving the identical manifest/basis plan may resume it under fresh transport identities.
Its bounded hash chain removes the single-payload plan-size ceiling. Genuine direct-UDP
`pair.xg41pthc` and forced-TCP `pair.00992erw` qualification now resumes 281,055 or 276,942 exact
bytes under fresh identities, fetches only the suffix, and completes HEAD-last activation after a
two-sided authority barrier.

A persisted-disk publisher-guest-restart gate
now also retires the old receive, preserves the exact publisher identity, policy, objects, and signed
HEAD across two bounded VMM epochs, waits for a stable higher authenticated epoch, and converges only
through an explicit fresh whole-object pull on both carriers. The genuine successor-range gate now
passes on both carriers: each cell fetches one 128-byte range, reuses 4,194,176 verified bytes, and
activates the exact reconstructed 4 MiB generation 2. The original partial-range fault baseline
passes on both carriers: after positive progress the first 1 MiB attempt is locally cancelled, fully
discarded and fenced, then the identical plan is retried once under a fresh FileId. ADR 0230's later
cells retain an exact prefix across that fresh-attempt fence and receive only the suffix while
preserving full verification. Local `sync-repair NAMESPACE` now verifies one
strict object store and quarantines only digest-named private objects whose bytes no longer match
their identity. The genuine repair gate now passes on both carriers: it fsyncs a deliberate 4 MiB
target-object corruption, quarantines only that mismatch, preserves signed accepted/activation state,
re-pulls the same signed revision, retains the corrupt evidence, and finishes with a clean two-object
scan.
Signed engine `treepack-v1` now publishes an owner-controlled directory as one bounded deterministic
artifact and activates it as a derived read-only tree only after signed activation state is durable.
`sync-namespace-template-tree` emits the policy; directory publication rejects links, special files,
shared-write entries, excessive paths/entries, and complete-artifact overflow. Activation unpacks to
private staging, deterministically repacks to the signed digest, fsyncs and freezes the complete tree,
atomically switches `materialized-trees/current`, recovers exact abandoned staging on retry, and
retains only the current derived projection. The genuine three-directory/three-file 4 MiB tree gate
passes over direct UDP and forced TCP with the same artifact, manifest, signed HEAD, and binary.
The dual-carrier adversity gate now advances that tree through three signed generations and four
publisher restarts. It accepts and activates generation 2A, refuses a coherent stale generation 1
and a distinct valid generation-2 fork without changing accepted or active truth, then accepts
generation 3. A dedicated 64 MiB ext4 namespace is filled until only 2,096,128 bytes remain: signed
activation commits, derived projection fails while `current` remains generation 2A, and removing only
the filler lets an exact duplicate activation materialize generation 3 with one revision and no
temporary residue.
The worker-pressure gate now passes on both carriers with a configured queue bound of one. A real
publisher transaction holds one active job while a second is queued; a third namespace job is refused
without stalling the toxcore event pump, and exact retry converges both retained namespaces after
capacity returns. `sync-status` reports `publisher-busy=1` instead of waiting behind publisher
verification, while independent worker/subscriber counters remain visible.
The whole-store byte-quota gate also passes on both carriers. A subscriber with 4,981,169 retained
bytes under a 5,242,880-byte ceiling refuses a valid generation 2 whose artifact and manifest each
exceed the exact remaining budget, cleans staging, and preserves its accepted HEAD, activation,
two-object inventory, and visible generation-1 tree.
The separate object-count gate fills a six-object ceiling while retaining about 28 MiB of byte
headroom, refuses the same valid successor with zero candidate objects committed, and preserves the
six-object predecessor inventory and all signed/visible truth on both carriers. ADR 0142 records that
v1 `maximum-objects` also bounds treepack entries.
A real read-only-storage gate now passes on both carriers as well. A dedicated loop-backed ext4
namespace refuses successor pull before any object request and refuses activation before changing
signed or visible truth. Each exact operation succeeds only after an explicit read-write remount and
retry; pull acceptance still remains separate from activation. ADR 0143 freezes this fail-closed
transaction boundary.
The maximum-entry memory gate also passes on both carriers. After a small generation-1 baseline, a
128-entry, 7,616,908-byte signed successor publishes, transfers, and activates with process-lifetime
`VmHWM` peaks of 12,924 KiB over UDP and 13,132 KiB over forced TCP. Both remain below the explicit
65,536 KiB construction ceiling; ADR 0144 keeps this observation distinct from a hard product quota.
A publisher-source corruption gate now passes on both carriers. The provider re-verifies both
digest-named generation-2 objects before offer, refuses their deliberately corrupted bytes with zero
subscriber admission or commit, and leaves generation 1 authoritative. Explicit repair quarantines
exactly 2 objects and 4,981,169 bytes; duplicate publication reconstructs the same generation-2
identities, and only an explicit fresh pull plus exact-token activation advances the subscriber.
ADR 0145 freezes that fail-near-source recovery contract.
A subscriber-destination corruption gate now also passes on both carriers. After positive progress,
the guest pauses and fsync-corrupts the exact incoming artifact temporary. Tox completion cannot
commit it: full SHA-256 verification fails the job, clears corrupt staging, and leaves generation 1
authoritative. The independently committed manifest is reverified and reused, so explicit retry
requests only the missing artifact before HEAD-last acceptance and separate activation. ADR 0146
freezes the integrity boundary and selective-progress rule.
A duplicate/reordered synchronization-control gate now passes on both carriers. After both original
FileId offers are admitted, exact object-request replays return two retained results with no new file
offers; an exact HEAD replay after those results produces no request cascade. Reusing that HEAD
message identifier with different canonical bytes is refused exactly once while the original pull
still converges, accepts HEAD last, and activates separately. ADR 0147 freezes the bounded same-epoch
replay contract.
Exact cancellation observations are retained in
[`docs/evidence/2026-08-21-sandwurm-sync-cancel.md`](docs/evidence/2026-08-21-sandwurm-sync-cancel.md).
Exact disconnect observations and nonclaims are retained in
[`docs/evidence/2026-08-21-sandwurm-sync-disconnect.md`](docs/evidence/2026-08-21-sandwurm-sync-disconnect.md).
Exact pause/resume observations and nonclaims are retained in
[`docs/evidence/2026-08-21-sandwurm-sync-pause.md`](docs/evidence/2026-08-21-sandwurm-sync-pause.md).
Exact publisher-guest-restart observations and nonclaims are retained in
[`docs/evidence/2026-08-22-sandwurm-sync-guest-restart.md`](docs/evidence/2026-08-22-sandwurm-sync-guest-restart.md).
Deterministic range construction evidence and exact nonclaims are retained in
[`docs/evidence/2026-08-22-sync-range-reconstruction.md`](docs/evidence/2026-08-22-sync-range-reconstruction.md).
Genuine two-guest range evidence is retained in
[`docs/evidence/2026-08-22-sandwurm-sync-range.md`](docs/evidence/2026-08-22-sandwurm-sync-range.md).
Genuine dual-carrier corrupt-basis fallback evidence is retained in
[`docs/evidence/2026-08-22-sandwurm-sync-corrupt-basis.md`](docs/evidence/2026-08-22-sandwurm-sync-corrupt-basis.md).
Genuine dual-carrier partial-range retry evidence is retained in
[`docs/evidence/2026-08-22-sandwurm-sync-range-retry.md`](docs/evidence/2026-08-22-sandwurm-sync-range-retry.md).
Genuine native cross-carrier bounded-range prefix evidence is retained in
[`docs/evidence/2026-08-29-sandwurm-sync-range-route-loss.md`](docs/evidence/2026-08-29-sandwurm-sync-range-route-loss.md).
Genuine native repeated bounded-range carrier-loss evidence is retained in
[`docs/evidence/2026-08-29-sandwurm-sync-range-repeated-route-loss.md`](docs/evidence/2026-08-29-sandwurm-sync-range-repeated-route-loss.md).
Genuine native late bounded-range carrier-loss evidence is retained in
[`docs/evidence/2026-08-29-sandwurm-sync-range-late-route-loss.md`](docs/evidence/2026-08-29-sandwurm-sync-range-late-route-loss.md).
Genuine dual-carrier target-object repair evidence is retained in
[`docs/evidence/2026-08-23-sandwurm-sync-repair.md`](docs/evidence/2026-08-23-sandwurm-sync-repair.md).
Genuine dual-carrier deterministic-directory evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree.md`](docs/evidence/2026-08-24-sandwurm-sync-tree.md).
Genuine dual-carrier rollback, fork, and disk-full recovery evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-adversity.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-adversity.md).
Genuine dual-carrier worker-pressure and retry evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-pressure.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-pressure.md).
Genuine dual-carrier whole-store quota refusal evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-quota.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-quota.md).
Genuine dual-carrier object-count quota refusal evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-object-quota.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-object-quota.md).
Genuine dual-carrier read-only-storage refusal and retry evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-read-only.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-read-only.md).
Genuine dual-carrier maximum-entry process high-water evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-memory.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-memory.md).
Genuine dual-carrier publisher-source corruption and recovery evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-source-corrupt.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-source-corrupt.md).
Genuine dual-carrier subscriber-destination corruption and selective-retry evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-destination-corrupt.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-destination-corrupt.md).
Genuine dual-carrier duplicate/reordered-control and replay-conflict evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-tree-control-replay.md`](docs/evidence/2026-08-24-sandwurm-sync-tree-control-replay.md).
Genuine dual-carrier whole-object prefix-resume evidence is retained in
[`docs/evidence/2026-08-28-sandwurm-sync-byte-resume.md`](docs/evidence/2026-08-28-sandwurm-sync-byte-resume.md).
Genuine actual-Tor-process-loss prefix-resume evidence is retained in
[`docs/evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md`](docs/evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md).
The first M6 desired-state mutation and its genuine dual-carrier provider convergence are frozen in
[`ADR 0148`](docs/decisions/0148-reapply-only-bounded-desired-state.md) and retained in
[`docs/evidence/2026-08-24-sandwurm-mutable-profile-status.md`](docs/evidence/2026-08-24-sandwurm-mutable-profile-status.md).
A bounded stable-device-signed retained-revision snapshot now exists. A mark-only planner inventories
exact published, accepted, activated, retained, missing, mismatched, and unreferenced state. Explicit
`sync-gc NAMESPACE dry-run|quarantine` may now move exact descriptor-pinned unreachable objects into
namespace-local quarantine without unlinking. ADRs 0312 and 0314 optionally anchor each namespace's
effect-bearing semantic roots in a separately enrolled external record. Single-writer engines bind
the exact signed published, accepted, activated, and retained roots; tree-v2 binds the live branch
frontier plus its exact signed workspace and maintenance state. Coordinated replay of those roots
and their local guard refuses while that service record remains current. Permanent purge remains
disabled because quarantine/object inventory, content availability, health, worktree bytes, and
projection-marker/current-pointer state are not witnessed. All current local sync mutations
and the stable stored-state planner share one strict namespace transaction lock. Accepted HEAD and
activation state are stable-device-signed. A signed committed/pending namespace rollback-guard
now surrounds every implemented root mutation, detects isolated root rollback, and reconciles either
power-cut transition side. The optional per-namespace lanes detect only their named semantic
snapshots and do not certify custody, backup, or deletion safety, so purge stays absent.

The M7 signed-update construction remains default-off and does not confuse delivery with installation
authority. `signed-update-bundle-v1` binds a staged payload to its exact
namespace, target, release sequence, version, size, digest, and an owner-pinned Ed25519 release
signer. `update-stage` joins that bundle to one accepted sync HEAD, installs only a reverified
mode-`0400` inactive slot, and commits stable-device-signed lifecycle state. `update-apply` commits
before switching the exact pointer; only a later durable Agent incarnation may `update-confirm` with
the one-use token. Health expiry, a second restart, and both pointer/state interruption directions
return predictably to the last confirmed slot. The eight-slot hot store fails closed and never
deletes bytes.
ADR 0311 adds an optional separately enrolled `update-lifecycle` witness. It commits the exact
canonical release-signer policy and absent-or-complete signed state, retains the exact successor in
a device-signed intent across remote CAS, and treats `current` as a repairable effect. Every stage,
apply, health admission, confirmation, and rollback generation commits externally before pointer
movement or service exposure. The first protocol intentionally freezes policy rotation within its
witness epoch until an explicit replacement/re-anchor ceremony exists.
The same source-linked binary passes a 4 MiB sequence-1 lifecycle between genuine Sandwurm guests
over direct UDP and forced TCP. Remote `command ... update.stage HEAD` now requires bilateral
feature bit 20, a current `install.firmware` proof, the exact accepted HEAD, and the ordinary signed
command journal before it can stage. Apply, restart, and health confirmation remain local.
Owner-local update policy v2 adds a positive signer-policy epoch
and an explicit bounded revoked-release-signer list. Active and revoked signer sets must be
canonical and disjoint, so a rotated policy can reject future bundles from a retired release key
without changing the signed bundle format or claiming retroactive state reinterpretation.
No-clobber `update-signer-keygen`/`update-signer-show` and reviewable `update-policy-rotate` output
now define the owner-local authoring and two-epoch overlap/retirement ceremony. Explicit
`update-gc dry-run|quarantine` protects the signed confirmed and live candidate slots, moves only
historical slots into a bounded recovery directory, resumes safely after a partial move, and still
offers no purge path.

Policy v3 and signed payload kind 2 now freeze the first executable consumer as
`linux-service-v1`. A later Agent incarnation rehashes the selected mode-`0400` slot into a sealed
anonymous image, enters it through the no-new-privileges parent-death helper with fixed argv and
environment, and requires the exact sequence-bound readiness record before the local one-use token
can confirm. Candidate exec/readiness/exit failure immediately signs rollback and relaunches the
prior confirmed service. Historical opaque policy and state stay byte-compatible and can never be
reinterpreted as executable. Direct-UDP `pair.pwpgv4si` and forced-TCP `pair.rntpawny` now qualify
pre-readiness service death, Agent parent-death cleanup, health expiry, confirmation, and confirmed
recovery inside simultaneous Sandwurm VMs. Abrupt whole-VMM/host power loss and the physical
manager/recovery/hardware matrix remain M7 gates. See
[`protocol-signed-update-bundle-v1.md`](docs/protocol-signed-update-bundle-v1.md),
[`ADR 0186`](docs/decisions/0186-authorize-remote-update-staging-through-durable-commands.md),
[`ADR 0187`](docs/decisions/0187-freeze-release-signer-revocation-policy.md),
[`release and retention operations`](docs/update-operations.md),
[`ADR 0188`](docs/decisions/0188-operate-release-keys-and-quarantine-update-slots.md), and
[`the Linux service adapter`](docs/update-linux-service-v1.md),
[`ADR 0189`](docs/decisions/0189-freeze-linux-service-deployment-adapter.md), and
[`sealed-service dual-carrier evidence`](docs/evidence/2026-08-27-sandwurm-linux-service-update.md),
plus the earlier
[`remote dual-carrier evidence`](docs/evidence/2026-08-26-sandwurm-remote-update-stage.md).
See `docs/foundation.md` for the import boundary and
`docs/toxsync-integration-plan.md` for the fail-closed integration sequence.
The implemented quarantine-first collection boundary is frozen in
[`ADR 0149`](docs/decisions/0149-quarantine-unreferenced-objects-without-purge.md) and the
[`containment plan`](docs/sync-gc-containment-plan.md); its dual-guest evidence is retained in
[`docs/evidence/2026-08-24-sandwurm-sync-gc-quarantine.md`](docs/evidence/2026-08-24-sandwurm-sync-gc-quarantine.md).
No purge API exists.
Current work is ordered in [`docs/roadmap.md`](docs/roadmap.md), and the Ratox construction sequence is
maintained in [`docs/ratox-service-implementation-plan.md`](docs/ratox-service-implementation-plan.md).
The measured multi-route implications, protected-Ratox rule, and immutable-object scheduler order are
frozen in [`docs/multi-route-plan.md`](docs/multi-route-plan.md). The explicit auxiliary construction
surface is documented in [`docs/route-workers-v1.md`](docs/route-workers-v1.md); its ready bulk routes
are eligible for the transport-neutral scheduler. The first live sync file path uses the single-route
capacity adapter. A full receive ledger now leaves an exact sync offer paused and retries it through
bounded fair service without changing its immutable attempt (ADR 0166). Genuine direct-UDP and
forced-TCP one-slot/two-object cells qualify that excess-work boundary by composition with the
accepted 1,000-sample route-latency rows; measured multi-route reassignment now also passes genuine
direct-UDP and forced-TCP two-guest loss, stale-result, same-savedata recovery, and protected-Ratox
gates (ADR 0169).
Auxiliary workers now also have a default-off bounded carrier for canonical sync object request/result
frames. The parent binds a real primary authority/HEAD job to one exact authenticated bulk
incarnation without forging an auxiliary authority session. It routes FileId offers and terminal
truth through that carrier, fences route loss, and reissues whole immutable objects with fresh
attempt/message/FileId identities on another ready worker. HEAD exchange stays primary, accepted HEAD
still commits last, and activation stays explicit (ADRs 0167 and 0168). That initial Gate 3 boundary
kept range transfers primary-only; ADR 0227 now admits the unchanged range-v1 frames on an exact
authenticated auxiliary only when both primary and worker sessions negotiated the feature. ADR 0228
qualifies fail-closed loss of a concrete auxiliary range and explicit fresh same-carrier recovery,
while deliberately discarding the failed prefix. The
accepted dual-carrier Gate 3 proof is retained in
[`docs/evidence/2026-08-25-sandwurm-sync-route-loss.md`](docs/evidence/2026-08-25-sandwurm-sync-route-loss.md).
The same cell now also passes direct UDP and forced TCP with exact positive-prefix inheritance and
suffix continuation (ADR 0224 and
[`2026-08-28 evidence`](docs/evidence/2026-08-28-sandwurm-sync-byte-resume.md)). Adaptive scheduler
qualification remains open; this is safe per-object resume, not byte striping or transparent bonding.
The default-off private-v2 path now also passes its first genuine cross-context cell. Two Sandwurm
guests each used a native UDP primary, native UDP bulk route, and strict generic-SOCKS/TCP bulk route
under independent keys, reached two reciprocally ready bulk routes, and converged the same signed
4,194,389-byte tree. Exact-key worker context mapping and the early-proof context-adoption rule are
frozen by ADR 0201; compact proof `pair.z948jeii` and its generic-SOCKS nonclaims are documented in
[`docs/evidence/2026-08-27-sandwurm-private-route-mixed-context.md`](docs/evidence/2026-08-27-sandwurm-private-route-mixed-context.md).
The first Gate 4 prerequisite is implemented as explicit `--sync-route-policy fixed|adaptive`.
Replacement is independent: `--sync-route-failover available|fail-closed` keeps compatibility
reassignment by default or fences a lost job without selecting another ready carrier (ADR 0220).
The owner can override that default per pull with `iotox sync-pull FRIEND NAMESPACE
[available|fail-closed]`. The choice is frozen in the live job and shown as `failover=...`; a retry
cannot change it. This is a local per-job no-downgrade boundary (ADR 0221).
Adding a second optional value pins initial placement and every permitted replacement:
`iotox sync-pull FRIEND NAMESPACE fail-closed tox/i2p`. `any` preserves compatibility;
every named class requires a matching authenticated auxiliary worker and sends no object bytes over
primary when that class is absent. Route-set v2 now signs the authorized class for the exact member,
and construction plus coordinator admission must match it (ADRs 0222 and 0225).
Adaptive selection uses only bounded current work/budget and restart truth at admission or mandatory
reassignment; it never migrates healthy work. ADR 0170 freezes the deterministic policy. The first
genuine two-guest topology A/B now passes over direct UDP and forced TCP: fixed reuses one eligible
eight-slot route for two overlapping jobs, while adaptive places the later job on the idle route;
all four exact trees activate and protected Ratox remains live (ADR 0171 and
[`docs/evidence/2026-08-25-sandwurm-sync-route-balance.md`](docs/evidence/2026-08-25-sandwurm-sync-route-balance.md)).
Independent fixed-first and adaptive-first cells pass on both carriers, removing policy phase-order
bias. The first exact auxiliary cancellation row also passes both carriers: after positive worker
progress, signed work returns from two to zero without reassignment in 70 ms on direct UDP and 80 ms
on forced TCP, followed by protected Ratox (ADR 0172 and
[`docs/evidence/2026-08-25-sandwurm-sync-route-cancel.md`](docs/evidence/2026-08-25-sandwurm-sync-route-cancel.md)).
An eight-job population row now fills both signed route budgets on each carrier. Fixed produces
`00001111`, adaptive produces `01010101`, every job commits and activates, work drains to zero, and
bounded resource intervals plus protected Ratox survive the phase (ADR 0173 and
[`docs/evidence/2026-08-25-sandwurm-sync-route-population.md`](docs/evidence/2026-08-25-sandwurm-sync-route-population.md)).
A concurrent-cancellation row now admits eight adaptive 262,211-byte artifacts as `01010101`,
withdraws four jobs concurrently and evenly across both bulk routes, lets the other four commit and
activate, drains work 16-to-zero without reassignment, and retains protected Ratox over direct UDP
and forced TCP (ADR 0174 and
[`docs/evidence/2026-08-25-sandwurm-sync-route-concurrent-cancel.md`](docs/evidence/2026-08-25-sandwurm-sync-route-concurrent-cancel.md)).
A loss-before-cancellation row now faults an active 4,194,601-byte pull after real progress,
reassigns it, requires positive progress on the replacement, cancels it without a second
reassignment, restores the stopped identity under one restart-budget unit, and retains protected
Ratox on both carriers (ADR 0175 and
[`docs/evidence/2026-08-25-sandwurm-sync-route-loss-cancel.md`](docs/evidence/2026-08-25-sandwurm-sync-route-loss-cancel.md)).
Exact auxiliary readiness order is now qualified without rewriting the signed route inventory.
One default-off seam holds nonselected workers until the named worker is application-ready and
reciprocally bound, then starts a bounded observation delay. Both corresponding orders pass for both
roles over direct UDP and forced TCP, followed by the same signed tree and protected Ratox (ADR 0176
and
[`docs/evidence/2026-08-25-sandwurm-sync-route-startup-order.md`](docs/evidence/2026-08-25-sandwurm-sync-route-startup-order.md)).
The opposite deterministic fault order now passes too. After ordinary cancellation has drained work
and removed staging, the cancelled pull's exact retained carrier is stopped, produces zero
reassignment, spends one signed restart-budget unit, and returns ready without reviving the pull.
Direct UDP and forced TCP retain protected Ratox (ADR 0177 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md`](docs/evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md)).
The shared-arm race is now qualified separately. A byte-progress observation freezes one exact
worker for a stop 500 ms later while the ordinary cancellation client independently waits the same
500 ms. Direct UDP and forced TCP both linearize as cancel-first: one loss, zero reassignment, one
typed cleanup retry, one route recovery, and no pull revival or activation (ADR 0178 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-cancel-race.md`](docs/evidence/2026-08-26-sandwurm-sync-route-cancel-race.md)).
A fault-leading 250/1,000 ms companion then produces loss-first on both carriers without polling for
reassignment before cancellation: exactly one reassignment, a distinct terminal replacement
carrier, zero cleanup retries, and one recovery (ADR 0179 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md`](docs/evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md)).
An eight-job population-loss row now closes the first multi-job same-carrier fault. Fixed placement
fills two four-job routes as `00001111`; after positive progress one carrier disappears; all four
affected two-object jobs move as complete remaining work sets; stale terminals are fenced; all eight
revisions activate; work drains 16-to-zero; the identity recovers once; and protected Ratox passes on
direct UDP and forced TCP. The campaign also added bounded fresh-identity retry for transient
pre-offer publisher unavailability and separated auxiliary carrier service from required-event
draining (ADR 0180 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-population-loss.md`](docs/evidence/2026-08-26-sandwurm-sync-route-population-loss.md)).
The degraded scheduler now also accepts work created after loss rather than merely migrating work
that existed beforehand. `sync-tree-route-loss-admission` faults a carrier holding two jobs,
requires both reassignments, then starts two additional jobs while exactly one bulk route is ready;
both late jobs select the survivor, all four revisions activate, work drains four-to-zero, and the
route recovers once. Direct UDP and forced TCP pass raw and compact evidence with protected Ratox.
The same campaign fixed clean shutdown ordering so synchronous auxiliary carrier commands quiesce
while required-event draining remains alive (ADR 0181 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-loss-admission.md`](docs/evidence/2026-08-26-sandwurm-sync-route-loss-admission.md)).
Controlled degraded startup admission now passes too. After a clean same-state subscriber Agent
restart, `sync-tree-route-startup-admission` holds one exact authenticated bulk route for 20 seconds,
requires ten stable sole-ready observations, and starts two independent 16 MiB trees through it.
Both jobs remain live and retain that carrier when the delayed route joins; both activate with zero
reassignment and work four-to-zero on direct UDP and forced TCP. Protected Ratox passes afterward
(ADR 0182 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-startup-admission.md`](docs/evidence/2026-08-26-sandwurm-sync-route-startup-admission.md)).
The first larger-object ABBA comparison now passes as `sync-tree-route-throughput`. Four fresh-Agent
phases pull two 16 MiB trees each: fixed selects `00`, adaptive selects `01`, all eight revisions
activate, and work drains four-to-zero. Adaptive improves aggregate observed artifact throughput by
16.80% on direct UDP and 6.56% on forced TCP in these cells. The TCP prerequisite exposed a Tox
transport epoch that remained continuous across Agent replacement; feature bit 27 now permits only a
strictly greater durable application generation to retire all old authority/work and re-confirm
without weakening same-generation HELLO conflicts (ADR 0183 and
[`docs/evidence/2026-08-26-sandwurm-sync-route-throughput.md`](docs/evidence/2026-08-26-sandwurm-sync-route-throughput.md)).
Two larger 1 MiB/job direct-UDP cells completed the cancellation invariants but missed Ratox
`OPENED` through the common 4 Mbit FIFO-shaped TAP. A protected logical route is therefore not
physical QoS. The controlled companion `sync-tree-route-common-link-fairness` keeps that 1 MiB/job
load and 4 Mbit bottleneck but uses a live-proved HTB/`fq_codel` hierarchy. Direct UDP
`pair.am47s4qe` and forced TCP `pair.78uagrhw` now pass balanced four-job cancellation, four survivor
activations, zero residual work/reassignment, and 40 protected Ratox samples with 17.067/112.817 ms
render maxima (ADR 0241 and
[`docs/evidence/2026-08-29-sandwurm-common-link-fairness.md`](docs/evidence/2026-08-29-sandwurm-common-link-fairness.md)).
This qualifies one same-host flow-aware shared-edge mechanism, not transparent bonding, strict
priority, reserved bandwidth, proportional scaling, a randomized distribution, independent
bottlenecks, or relay diversity. Randomized startup/fault delays and cold application startup with a
route absent remain open. The startup row is an already-running guest plus a controlled
application-readiness hold, not machine cold boot.
The accepted future operator vocabulary is in [`docs/future-cli-contract.md`](docs/future-cli-contract.md),
and all two-node qualification is standardized on the
[`Sandwurm laboratory`](docs/sandwurm-two-node-lab.md).
The 2026-08-20 baseline keeps two stock Cloud Hypervisor guests live concurrently and verifies
source-linked friendship, confirmed IoTox sessions, private L2 reachability, and bidirectional text
under both direct UDP and forced TCP. The complete 1,000-sample Ratox load matrix and local route-fault
campaign are now classified. Direct-UDP multi-source synchronization and explicit fail-closed
selected-source recovery, including durable partial-replica cold start, are accepted; forced TCP
on the old single-subscriber topology remains falsified. Genuine mixed-route auxiliary content and
selected actual-Tor worker-loss qualification are now accepted. Same-source whole-object placement
over distinct authenticated Tor workers is also accepted; byte striping remains open.
Bounded same-source two-object concurrency is also accepted over direct UDP and forced TCP; lane-count
performance is now measured at caps 1/2/4/8 on both carriers. Forced TCP has an observed cap-4 knee,
and one persistent 720-sample Ratox attachment now survives competing caps 1/4/8 on both carriers.
Cap 8 regresses against cap 4 and worsens p95 terminal latency in both accepted cells. Fresh
post-bulk admission and counterbalanced `1/2/4/8` scaling now pass both carriers. The default stays
one; explicit cap 2 is the efficient mixed/relay-heavy bulk recommendation, cap 4 is the fixed-UDP
throughput option, and cap 8 remains stress-only. Multi-lane daemon restart now passes at caps two
and four on both native carriers. Persistent Ratox at cap 2 now passes the same predeclared
interactive construction SLA over both native carriers; caps 4 and 8 miss its p95 ceiling.
Same-source auxiliary whole-object distribution now passes over two exact logical Tor workers, while
byte striping, independent-bottleneck speedup, and automatic carrier selection remain open.
Permanent sync purge remains absent. Representative-hardware M6 qualification is explicitly
unsupported and retired from repository completion by ADR 0277.

rev0039 adds a proactive cgroup-v2 PSI tripwire to rev0038's host-local admission gate. An
administrator may pair any configured CPU `some avg10`, memory `full avg10`, or I/O `full avg10`
maximum with a cumulative stall threshold and one common portable 2-to-10-second tracking window in
exact 2-second quanta. IoTox registers each trigger on its own descriptor and polls all sources in one
bounded monitor thread, so pressure can close the gate between new-PTY admission attempts instead of
waiting for the next
synchronous sample.

A trigger atomically records its resource class, closes the gate, and holds it closed for at least one
complete tracking window. The hold never bypasses rev0038's exact hysteresis: reopening still requires
a later complete descriptor-pinned sample in which every configured metric is at or below
`maximum-hysteresis`. Poll failure, descriptor invalidation, monitor failure, malformed evidence, or
disabled accounting fails closed. Owner-private status now exposes bounded trigger configuration,
monitor health, remaining hold, typed local failure, and saturation-safe total/per-resource counters.
The policy remains default-off and host-local; it is proactive load shedding, not a real-time guarantee,
capacity forecast, atomic cross-resource snapshot, or existing-session preemption.

rev0038 added the underlying synchronous delegated-root PSI admission gate before aggregate capacity
reservation or mutable process/cgroup state. It pins `cgroup.pressure` and configured PSI files beneath
the exact daemon-owned delegation, requires enabled accounting before and after every complete canonical
sample, closes only above exact integer basis-point maxima, and reopens only at the exact lower
hysteresis boundaries.

rev0037 extends the descriptor-pinned completed-session outcome with memory work, swap failure,
freezer duration, and IRQ/SOFTIRQ pressure evidence. Before payload attachment, IoTox pins every
available protected `memory.stat`, `memory.swap.events`, `cgroup.stat.local`, and `irq.pressure`
interface and requires zero retained counters. Memory policy makes `memory.stat` mandatory; swap
policy makes `memory.swap.events` mandatory; newer local-stat and IRQ PSI capabilities remain
independently optional.

After recursive quiescence and before exact inode removal, bounded key-based parsers retain page and
major faults, complete optional scan/reclaim and swap-in/out tuples, swap high/max/fail events,
cumulative freeze microseconds, and the current kernel's IRQ `full` PSI microseconds. Whole-record and
tuple capability counts preserve absent-versus-zero truth. Any protected read or parse failure makes
the entire session outcome incomplete, so no partial PID, memory, CPU, I/O, pressure, peak, freeze, or
swap evidence is aggregated. All totals remain saturation-safe, owner-private, unlabeled, and outside
authorization, admission, enforcement, adaptive policy, and causal attribution.

rev0036 completes the bounded resource-accounting outcome for each proved-empty Ratox PTY cgroup.
Before payload attachment it independently opens protected `pids.peak`, `memory.peak`, and
`memory.swap.peak` descriptors, requires canonical zero in every available fresh-leaf record, and
retains the exact lifetime high-water mark after quiescence but before exact inode removal. Interface
absence stays explicit. Aggregate status publishes capability counts, saturation-safe sums, and maxima;
these are independent session peaks, not simultaneous host demand, working sets, or reservations.

`cpu.stat` observation is no longer coupled to a configured CPU quota. Every session attempts to retain
its exact usage, user, and system microseconds. Controller bandwidth and burst counters are accepted
only as complete nested tuples, so controller-disabled and older-kernel records remain compatible while
partial evidence fails closed. Owner-private status carries explicit work, bandwidth, and burst
capability counts. None of these outcomes becomes authorization, live policy, capacity inference, or
per-process attribution.

rev0035 retains exact per-session Linux Pressure Stall Information after a Ratox PTY cgroup is
proved recursively empty. Before payload attachment, IoTox opens each available protected
`cpu.pressure`, `memory.pressure`, and `io.pressure` interface, verifies canonical records, and
requires zero cumulative `some`/`full` totals. When `cgroup.pressure` exists it must report accounting
enabled. After quiescence and before exact inode removal, IoTox captures absolute stall totals in
microseconds. Interface absence and an older missing `full` class remain explicit instead of becoming
fabricated zero support.

Owner-private runtime status now accumulates CPU, memory, and I/O `some` and `full` microseconds with
saturating arithmetic and separate capability counts. Rolling `avg10`/`avg60`/`avg300` percentages are
validated but not retained. A statistics failure contributes one incomplete outcome and no partial
controller or PSI totals while proved-empty cleanup may still complete. These are completed-session
content-free outcomes, not live PSI monitoring, causal diagnosis, threshold alerts, adaptive
admission, latency/throughput guarantees, or per-session histories.

rev0034 extends the same fail-closed local cgroup envelope to block-device traffic. Canonical terminal
profile v5 and host CLI policy can name one exact numeric `MAJOR:MINOR` and independently cap read and
write bytes per second plus read and write operations per second. Host/profile policy may compose only
for the same device, then each direction selects the lower configured value. Startup probes and real
session creation activate the delegated `io` controller, write one complete `io.max` line, parse its
unordered nested-key readback, and require the exact retained policy before the blocked helper runs.
Remote Ratox bytes select neither the device nor its rates.

A protected `io.stat` descriptor now joins the existing PID, memory, and CPU outcome set. IoTox
requires a zero known-counter baseline before attachment, then after recursive quiescence and before
exact inode removal retains saturating read/write/discard bytes and operation totals. Private runtime
status exposes only cumulative content-free counters. It does not retain the device identity or any
profile, process, command, path, peer, or terminal label. I/O ceilings are rate controls, not aggregate
media reservations, deterministic latency guarantees, or automatic storage-topology discovery.

rev0033 adds a controlled memory-pressure boundary and retains kernel outcome truth for every proved-
removed Ratox PTY cgroup. Canonical local terminal profile v4 and host CLI policy now carry optional
`memory.high` beneath the existing hard `memory.max`. Host/profile values compose by monotone minimum;
the final high threshold is clamped beneath the effective hard ceiling; startup preflight and real
session creation write and exactly read back the kernel value before payload attachment. The soft
threshold remains a throttle/reclaim boundary, not an OOM guarantee or aggregate hard-memory charge.

For each configured controller, IoTox prefers protected read-only `pids.events.local` and
`memory.events.local`, falls back to the hierarchical event files only when the local interfaces are
unsupported, and opens `cpu.stat` for configured CPU bandwidth. It requires a zero baseline before attachment. After
recursive `populated=0` and before exact inode removal, keyed bounded parsers capture PID-limit hits,
memory high/max/OOM outcomes, CPU usage, and CPU throttling. Completed outcomes accumulate with
saturating arithmetic in owner-private runtime status even when aggregate reservation ceilings are
disabled. A statistics failure contributes an explicit incomplete-outcome count without preventing
proved-empty cleanup; uncertain teardown still claims no completed outcome and retains the existing
fail-closed reservation-stranding behavior. No profile, process, command, path, peer, or terminal
content is retained.

rev0032 extends rev0031's conservative host-wide cgroup reservation ledger to exact CPU bandwidth.
Administrators may cap the sum of reserved process slots, memory bytes, swap bytes, and CPU
`quota/period` ratios across all live production Ratox PTYs. CPU ratios are normalized to one explicit
host accounting period, defaulting to 100000 microseconds. Every configured aggregate dimension
requires a finite matching effective per-session maximum; a profile that cannot fit once on an idle
ledger, or whose CPU ratio would require fractional quota microseconds at the selected accounting
period, fails host activation before network exposure. These are conservative accounting reservations
over configured maxima, not physical allocation or advance kernel reservation.

The production factory derives one canonical process/memory/swap/CPU charge and atomically claims it
before helper validation, executable or directory opening, PTY/socket construction, cgroup-leaf
creation, or process spawn. CPU comparison uses exact continued-fraction arithmetic and GCD-reduced
normalization, with no floating point, overflowing cross-products, or hidden rounding. Concurrent
claims are serialized and overflow-safe. A move-only reservation automatically rolls back pre-spawn
and proved-cleanup failures; successful sessions retain the charge until descendants are gone, the
delegated cgroup is empty and removed, and the leader is reaped. If a post-spawn rollback or destructor
cannot prove both direct-child reap and exact cgroup removal, it strands the complete charge instead
of under-accounting possible live work. Capacity exhaustion is typed `resource_exhausted`; malformed,
missing, oversized, or nonrepresentable policy is `invalid_argument`.

Private runtime status exposes configured aggregate maxima, CPU accounting period, current and peak
reservations, rejection count, and stranded-reservation count without profile, identity, command,
path, or terminal-content data. Aggregate CPU admission accounts exact average bandwidth; it does not
align independent period boundaries, enforce a parent `cpu.max`, reserve processor time, or guarantee
latency or throughput.

rev0030 advanced that boundary from one host-global envelope to profile-scoped budgets beneath an
administrator-owned ceiling. Its canonical profile v3 added process, hard memory, swap, CPU-quota, and
CPU-period fields; rev0033 profile v4 inserted the soft memory-throttle field; rev0034 profile v5 adds
one exact device plus read/write BPS and IOPS fields. At activation and again at spawn, IoTox composes
host and profile policy monotonically: scalar maxima select the smaller configured value, cross-layer
memory high is clamped beneath hard memory max, CPU bandwidth selects the lower exact `quota/period`
ratio, and I/O policy requires one matching device before selecting per-direction minima. A profile
may tighten or add a limit but can never weaken or redirect host policy. Canonical v1 through v4
records remain readable and migrate without inventing `memory.high` or I/O policy; remote Ratox bytes
still select neither profile nor limits.

After acquiring the signed host-incarnation lease, Agent startup computes every enabled profile's
effective policy and creates one disposable cgroup probe for each distinct `(payload identity,
effective budget)` pair. Every probe exercises the real leaf topology, controller activation,
ownership boundary, exact read-back, and empty-leaf removal before rev0028 orphan recovery,
PTY-factory construction, or Ratox networking starts. Only after all probes succeed may a proved-stale
subtree be mutated. Any effective limit without a delegated root, invalid byte alignment,
missing/inactive controllers, threaded topology, unsafe ownership, or probe cleanup failure keeps the
host offline. Empty host and profile policy preserves the rev0028 lifecycle-only behavior.

rev0029 established the underlying kernel-enforced per-session process, memory, swap, and CPU
controls. The administrator-owned command-line ceiling maps to `pids.max`, `memory.max`,
`memory.swap.max`, `memory.oom.group=1`, and `cpu.max`; rev0030 retains its exact write/read-back and
blocked-helper ordering while varying the effective value by locally resolved profile.

rev0028 closes the configured cgroup-v2 crash/restart lifecycle gap. Every new hardened PTY leaf is
named for the creating daemon's canonical Linux boot ID, numeric PID, `/proc/<pid>/stat` field-22
start time, and collision-resistant local sequence. Startup opens the real procfs and cgroup-v2
interfaces without following links, pins a candidate owner with `pidfd_open(2)`, compares the exact
start time, and polls the pidfd before treating the owner as live. A boot mismatch, absent process,
different start time, or terminal task state proves that the named owner incarnation is stale.
Unreadable or malformed identity evidence never authorizes cleanup.

Recovery runs before the PTY factory or network service is activated. It enumerates at most a
configured bounded number of reserved leaves, pins every pathname to one cgroup-v2 inode, verifies
daemon-only ownership, domain type, empty subtree controls, and the absence of child cgroups, and
preflights the complete set before mutation. Live exact incarnations are preserved. Stale exact
incarnations receive recursive `cgroup.kill`, wait on kernel `cgroup.events` notifications until
`populated 0`, and have only their revalidated inode removed. Empty legacy leaves are removed; populated legacy leaves
fail startup because their old PID-only names cannot defeat PID reuse retrospectively. Content-free
recovery counters are published in `run/status`.

Independent lifecycle-recovery, memory/PID-resource, and CPU-resource process routes mount fresh
cgroup-v2 views inside isolated user, mount, and cgroup namespaces. On this cloudtainer the lifecycle
route positively passes live preservation, deliberate creator-crash reclamation, recursive payload
death, empty-legacy removal, populated-legacy refusal, malformed-name refusal, and bounded preflight.
The memory/PID and CPU routes return separate named skip code 77 results because neither controller
is preactivated for child cgroups here; their exact readback, PID exhaustion, memory-high pressure,
CPU throttling, teardown-outcome, and cleanup branches remain
executable on a qualifying delegated hierarchy. This is not target-fleet qualification, protection
from a privileged competing manager, or a claim that every future cgroup lifecycle or resource race
is closed.

The final analyzer pass also made both directory-stream boundaries explicitly fail closed: cgroup
child inspection and procfs session sweeping now validate `dirfd()` before using descriptor-relative
kernel interfaces.

rev0027 removes silent-peer head-of-line waits from both owner-private local IPC planes. The
administrative `control.sock` now polls a bounded set of accepted clients together, gives each an
independent complete-record lease, services ready requests before unrelated expiry, and enforces
explicit global, per-process, accept-refill, and per-cycle request budgets. One silent client can no
longer reserve the only administrative request lane until its timeout.

On Linux 6.5+ with suitable headers, every accepted control client is also pinned to the exact
connection process through `SO_PEERPIDFD`. Process exit releases a silent admission immediately even
when the socket file description was inherited or transferred elsewhere. The CLI applies the same
connection-process pin to the server while awaiting a response, so a dead server cannot outsource a
timeout-length hang to a retained accepted descriptor. When response data and process exit become
ready together, the complete queued response is consumed first.

The terminal server now keeps a bounded set of contenders inside the active controller poll loop
instead of synchronously waiting in a shared grace window. Active input, owner-pidfd exit, and
outbound drain remain ahead of contender work; contender acceptance and record decoding are
rate-limited and per-process bounded; every contender response is best-effort nonblocking. A successor
still queued in the kernel when the active process dies remains eligible for normal admission.
The accepted active connection is process-pinned before its first `OPEN`, preventing an inherited or
passed silent descriptor from retaining the sole controller slot after its exact connector exits.

rev0026 established the message-bound foundation retained here. Both private administrative and
terminal `SOCK_SEQPACKET` planes require per-record `SCM_CREDENTIALS`, exact agreement with
connection-time `SO_PEERCRED`, and matching `SCM_PIDFD` when the running Linux kernel supports
`SO_PASSPIDFD`. Malformed, duplicate, truncated, missing, or unexpected ancillary data fails closed;
received `SCM_RIGHTS` descriptors are closed before rejection; clients authenticate server responses;
and the terminal controller slot remains fenced to both the connection process before `OPEN` and the
first valid record sender process afterward.

These controls improve finite availability inside the owner-private socket boundary. They do not turn
same-UID local IPC into cryptographic authorization, preempt a blocking application callback,
guarantee starvation freedom against an unlimited coalition of same-UID processes, or create a
namespace/cgroup traffic-isolation boundary.

rev0025 adds an explicit, fail-closed cgroup-v2 lifecycle boundary for hardened PTYs. When an
administrator supplies `--ratox-cgroup-root`, the production supervisor creates one daemon-owned,
inode-pinned domain cgroup per session, attaches the still-waitable sealed helper before releasing its
manifest, uses `cgroup.kill` for explicit KILL and natural-leader cleanup, waits for recursive
`cgroup.events: populated 0`, removes the exact leaf, and only then reaps and reports the leader.
Malformed paths, ordinary filesystems, missing kernel controls, unsafe ownership, compatibility
profiles, inherited/root/same-UID payload identities, and injected factories fail explicitly; no
configured failure silently falls back.

The cgroup path is optional. Empty configuration preserves rev0024's descriptor-relative procfs,
pidfd, start-time, and three-empty-inventory supervision. The delegated path must belong exclusively
to the IoTox manager under the cgroup-v2 single-writer contract. At rev0025 this path did not claim
crash-restart garbage collection; rev0028 supplies the boot-bound recovery gate above. rev0029 adds
optional process, memory, swap, and CPU ceilings, and rev0030 permits a local profile to tighten those
ceilings or add its own effective budget. rev0031 prevents configured pids, memory, and swap maxima
from multiplying across simultaneously admitted sessions beyond explicit host-wide sums; rev0032 adds
exact rational CPU-bandwidth admission at an administrator-selected accounting period. rev0033 adds
monotone `memory.high` throttling and cumulative teardown-time controller outcomes. rev0034 adds exact
per-device `io.max` BPS/IOPS ceilings plus cumulative teardown-time `io.stat` totals. rev0035 adds
zero-baseline teardown-time CPU, memory, and I/O PSI totals with explicit capability counts. rev0036
adds zero-baseline PID/memory/swap lifetime peaks and quota-independent complete CPU work accounting.
rev0037 adds exact memory fault/reclaim/swap work, swap allocation events, freezer duration, and
full-class IRQ/SOFTIRQ pressure with explicit interface and tuple capability counts. rev0038 adds
delegated-root PSI admission before recovery mutation, aggregate reservation, and spawn mutation,
exact basis-point hysteresis, before/after accounting proof, fail-closed sampling, and private typed
last-sample/latch/counter projection. rev0039 adds dedicated PSI-trigger descriptors, one bounded poll
monitor, minimum-window holds, proactive fail-closed trip events, and private trigger health/counters.
The path still does not claim aggregate I/O reservation, latency or queue-depth guarantees, atomic
cross-resource PSI snapshots, automatic threshold tuning, synchronized CPU burst control, parent-cgroup CPU
enforcement, protection from root or a competing same-UID manager, a cgroup namespace, or target-fleet
qualification.

rev0024 pins the procfs side of PTY-session supervision. The parent opens and verifies the real
procfs inventory, opens each numeric process directory without following links, parses the reported
PID, session, live state, and field-22 start time through that pinned directory, then re-reads the same
identity after `pidfd_open(2)` before signaling through `pidfd_send_signal(2)`. Once KILL begins, the
waitable leader is retained until three consecutive complete inventories report no live executable
session member. A single empty scan can no longer release the session-ID pin. A bounded fork-churn
oracle exercises shutdown while descendants are still being created in separate process groups.

The final payload now receives `EPERM` for the reviewed process-handle interfaces—`pidfd_open`,
`pidfd_send_signal`, `process_madvise`, and `process_mrelease`—while the supervisor retains only its
pre-filter handles. Enabling the remote-terminal host also seals the long-lived Agent process before
device state is constructed: dumpability is disabled and both core-file limits are irreversibly set
to zero for that process. These rules are executable and fail closed, but they are not cgroup-v2
ownership, atomic `cgroup.kill`, complete syscall confinement, or target-fleet qualification.

rev0023 closes argument-level and lifecycle holes in the default terminal boundary. Baseline now
inspects `ioctl(2)` requests and rejects controlling-terminal detach/reassignment, terminal-input
injection, line-discipline, console, keyboard/font, and virtual-terminal mutation while preserving
ordinary termios and window operations. It inspects the architecture-correct legacy `clone(2)` flags
word, rejects reviewed namespace creation bits, and returns `ENOSYS` for `clone3(2)` so libc can retry
the inspected legacy path. After helper setup it also freezes the session and verified-parent
contract by denying `setsid(2)` and `prctl(PR_SET_PDEATHSIG, ...)`. One shared build-header-derived
policy table drives both filter generation and the exec'd payload oracle; real fork and `std::thread`
probes prove that ordinary process and thread creation remain available.

Baseline and strict now fail closed unless the supervisor can use pidfds, pidfd signaling, and readable
procfs identity/inventory. The parent retains the leader pidfd, inventories every live member of the
fixed PTY session, revalidates each member after pidfd acquisition, and sends HUP/TERM/KILL through
`pidfd_send_signal`. Repeated KILL sweeps include descendants in separate shell process groups and also
run after natural leader exit while preserving the leader's original status. Compatibility keeps its
historical process-group semantics. The final child additionally closes and proves every unreserved
descriptor through actual `/proc/self/fd` inventory, including inherited descriptors above a lowered
`RLIMIT_NOFILE` ceiling.

rev0022 turns the R7 gate into a reproducible attested evidence chain. A deterministic balanced
schedule reconstructs every route/load trial and run-bound token. The v2 sample schema retains raw
controller-local and host-local steady-clock timestamps, derives all qualification durations, and
never subtracts clocks across hosts. Ratox host events now expose exact content-free message, byte-span,
and event-ordinal coordinates so one input admission, whole-frame PTY commit, and output append can be
joined without storing terminal content.

Canonical SHA-256 digests bind the schedule, sample rows, and retained route/bulk observation files.
Two distinct ephemeral Ed25519 capture keys sign role-separated payloads containing the same complete
unsigned run; signing verifies the local Linux boot ID and that the secret key derives the advertised
public key. Sealing and analysis verify both signatures, and analysis requires the auxiliary evidence
files again. This supplies tamper evidence and explicit capture-role agreement, not hardware remote
attestation or proof that capture metadata is true. The complete-service experiment and independent review
remain unclaimed.

At its historical boundary, rev0022 substantially hardened the native terminal child. Every profile
mode discovered the running
kernel's capability ceiling, clears and verifies ambient plus effective/permitted/inheritable sets,
and refuses a privileged launch that cannot seal its capability boundary. When `CAP_SETPCAP` is
available, the helper locks root/set-ID/keep-caps/ambient securebits, empties the complete bounding
set, and verifies the result after identity transition. The helper handoff is nondumpable,
`no_new_privs` was mandatory, and the native oracle proved zero active privilege at final exec.
ADR 0286 preserves that default while adding one explicit profile-v6 compatibility exception for a
non-root owner login that must use host-authorized set-ID/file-capability helpers such as sudo.

Canonical terminal profile v7 retains profile v6's frozen account/elevation policy, the explicit
local `confinement` tier introduced by v2, the
profile-scoped cgroup budgets introduced by v3, optional `memory.high` from v4, and one exact numeric
block-device I/O policy from v5. It adds optional SHA-256 pins for the exact shell and rescue Toybox
ELFs. Existing byte-canonical v1 records decode as `compatibility`; canonical v2
records retain confinement and an empty cgroup budget; canonical v3 records decode with no high
threshold; canonical v4 records decode with no I/O policy; canonical v1--v5 records never invent
account groups, elevation, or pins; canonical v6 records never invent pins. New profiles default to `baseline`, which
installs an
architecture-checked seccomp filter denying a bounded set of hazardous process-inspection, kernel,
mount/namespace, module, keyring, privileged-I/O, host-mutation, and time-mutation interfaces. The
filter is a reviewed deny floor, not a complete syscall allowlist.

`strict` is opt-in and fail closed. It requires MDWE and Landlock ABI 10, grants ordinary mutation
only beneath the already-open non-root working directory, denies character/block-device creation,
grants no TCP or UDP port, and scopes external pathname/abstract Unix sockets and signals. Its host
oracle distinguishes allowed in-tree mutation from denied external create/truncate/unlink and
TCP/UDP bind/connect/send operations. Unsupported or externally filtered kernel primitives reject
startup at a named stage; they never silently downgrade the profile. Strict does not restrict read or execute access and does not become a
namespace, cgroup, mount, or virtual-machine sandbox.

rev0021 makes the R7 complete-service experiment observable and fail closed before any two-node
claim is attempted. The serialized transport owner now retains fixed-allocation cumulative queue-wait
histograms for interactive, control, and bulk work, with exact microsecond buckets through 4,096 us,
nearest-rank p50/p95/p99 bounds and exactness flags, and an exact count at or above the strict 2 ms
owner gate. Validated sensitive Ratox sends publish coherent typed provider outcomes, while the Agent
separately exposes controller and host retained-head rejection totals, live streaks, maxima, and
steady-clock ages. Ratox lifecycle records now carry nonzero nondecreasing service-relative steady
time. All projections remain content-free.

A new bounded ASCII TSV analyzer freezes the R7 two-route by six-load-cell evidence shape, rejects
unsafe or malformed input, applies one-commit/one-render semantics, uses deterministic integer
percentiles, enforces direct-UDP and strict owner-tail gates, and reports forced-TCP latency without
mislabeling it as direct. Ordinary builds keep the monolithic owned-registry contamination oracle;
sanitizer presets split that same deterministic registry into bounded shards. This revision constructs
instrumentation and evidence gates. It does not claim that the Sandwurm two-node R7 run has occurred.

rev0020 hardens the R5 private controller stream and completes the first deterministic-provider R6 restart/fault contract. A
connected same-user process now owns only a finite first-OPEN lease; a silent process cannot reserve
the sole controller slot indefinitely. While one controller is active, contenders are accepted in a
small bounded batch, their first canonical record is consumed without dispatch, and the loser receives
an exact typed `resource_exhausted` result on its own stream ID. This removes the previous race where
the real CLI could report `Broken pipe` or a changed stream ID instead of the actual contention reason.
If the active descriptor is already terminal, that death is processed before queued contenders, so a
replacement is not rejected on behalf of a controller that no longer exists.

A committed local `DETACH` is now a bounded two-phase close rather than a successful send followed by
an immediate descriptor teardown. Final `OUTPUT` and `DETACHED` records drain first; for a configurable
1 ms..5 s interval (250 ms default), only exact-stream cumulative `OUTPUT_ACK` records may cross back
into the Agent. The listener is removed from polling during that phase so successors remain in the
kernel backlog instead of provoking a busy loop or stale denial. Packet sends consume the same
absolute deadline, and any other post-detach operation is rejected before dispatch.

The actual installed `iotox` executable is now exercised across a separate-process controller fault
gate: one winner remains attached, one loser receives the explicit busy outcome, abrupt winner death
detaches the local attachment, a replacement `terminal-resume` renders retained and final detach
output before sending the exact cumulative ACK, that ACK reaches the server before release, and a
server replacement returns an explicit `not_found` outcome for state that did not survive restart.
These are deliberately local controller semantics; they do not claim that a remote PTY or Agent
replay state survives daemon restart.


An enabled Ratox host now reserves a signed, device-bound incarnation before service, listener, or
network startup. The exact 128-byte record advances only after a nonblocking lifetime lease is held,
uses descriptor-relative no-follow traversal, strict owner/type/mode/link checks, a retained temporary
inode across atomic rename, file and directory synchronization, and strict signed reread. Every newly
created private directory is synchronized together with its containing directory entry before the
host depends on the path. Enabled direct-service callers also start from an unreserved zero sentinel
and must inject a leased value explicitly. A rejected contender cannot consume an incarnation; a
clean successor commits exactly `+1`. Runtime status projects the nonsecret incarnation and lease-held
fact, and failed-start cleanup preserves `phase=failed` rather than rewriting the evidence to
`stopped`.

The retained full-path R6 oracle crosses reconnect, controller replacement, exact-byte SENDQ retry,
friend-number reuse cleanup, signed revocation, one explicit authority-free denial, daemon restart,
and stale-session refusal through the real Agent, private socket, mock Tox owner thread, and native PTY
helper. Authentication retained for that denial is never accepted as current effect authority.

The controller still retains immutable outbound Ratox packets until c-toxcore accepts them, preserves
unacknowledged input and retained output under independent limits, validates duplicate/overlapping
output byte-for-byte, coalesces cumulative output ACKs and latest resize, and fences OPEN/RESUME to
the exact confirmed online epoch and authenticated principal. Route loss keeps only safely resumable
state. Stale correlations, wrong identities, destructive gaps, nonadvancing generations, sequence or
message-ID exhaustion, and local delivery overflow fail closed.

The local stream remains deliberately separate from finite administrative `control.sock` RPC. Local
protocol v1 uses canonical bounded packets over Linux pathname `SOCK_SEQPACKET`; the parent and socket
must be owner-private, connection credentials are checked with `SO_PEERCRED`, and every request and
response is bound to exact kernel-supplied record credentials. Optional kernel pidfds strengthen that
proof and terminal-owner lifetime; all injected descriptors are closed and rejected. Active listeners
are never stolen, stale reclamation rechecks the exact inode, administrative silent requests expire,
and shutdown removes only the socket inode created by that server. The terminal client restores raw mode and signal handlers, propagates window size,
writes output before acknowledging it, commits final detach ACKs through the bounded ACK-only phase,
and provides explicit `~.`, `~d`, `~~`, and `~?` local escapes.

Both host and controller roles remain disabled by default. A client-only device creates no PTY or
profile resolver. The remote host still requires bilateral Ratox negotiation, transcript-bound
principal proof, an exact current `interactive.terminal` grant, fixed owner-controlled profile policy,
and the sealed PTY boundary. Terminal bytes, argv, environment, paths, profile identifiers, and error
strings are not placed in the persistent Ratox lifecycle journal.

This is security-sensitive construction, not a production remote shell or complete sandbox claim.
The current construction does not preserve PTYs or controller replay state across Agent restart, recover populated
PID-only legacy leaves without operator action, resist rollback by an equivalent owner or storage
snapshot, provide power-cut qualification, support multiple simultaneous local terminal
streams, restrict all read/execute
paths, provide aggregate I/O reservation, latency/queue-depth guarantees, persistent PSI histories, adaptive threshold selection, positive trigger-delivery qualification on this host, existing-session pressure preemption, or memory-high feedback control, synchronize CPU quota periods, enforce a parent CPU ceiling,
defend against a privileged/same-UID writer that
violates delegation, authorize one same-UID process over another, guarantee starvation freedom under an unbounded same-UID process coalition, or prove every future session-escape path. The attested R7 tooling
binds a reproducible evidence chain but does not manufacture a missing topology result or hardware
attestation; laboratory execution, retained-provenance review, and independent security review remain.

Original IoTox work is available under the permissive MIT License. Third-party components retain
their own terms; see `LICENSE.md`, `THIRD_PARTY.md`, and `third_party/README.md`. In particular, a
binary linked with c-toxcore is subject to c-toxcore's GPL distribution terms.

For a bounded, self-describing public seed suitable for GitHub, another ChatGPT
session, or a future office holder, build a seed repository datacube:

```sh
./tools/iotox-repo.sh datacube --seed
```

It captures an exact clean commit, a cloneable one-commit source-snapshot bundle,
available same-commit distribution and test evidence, and strict integrity
manifests. See `docs/conversation-datacubes.md` for the content, safety,
verification, and recovery contract. For a deliberate full-history provenance
handoff, use `./tools/iotox-repo.sh datacube --upload`. For the older public
profile with automatic history selection under the default 128 MB ceiling, use:

```sh
./tools/iotox-repo.sh datacube --public
```

For a richer internal conversation/recovery handoff with nested founding-cube provenance when it
fits, use `./tools/iotox-repo.sh datacube --conversation`.

The next human-facing distribution layer is intentionally split. `tools/iotox-repo.sh` is the first
public repository companion for ordinary Bash/Nix doctor, build, quick/full test,
sync-recovery-drill, same-host loopback custody drill, dishonest-storage drill,
dishonest-storage matrix, witness-custody receipt, stable-evidence-plan,
release-plan/release-check, datacube, and cleanup workflows around the one
`iotox` binary. A founder-preview release should start with
`tools/iotox-repo.sh release-plan founder-preview` and pass
`tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox`;
stable/no-concern release remains gated by `iotox ship-check all stable`.
Stable graduation additionally requires the explicit dossier printed by
`tools/iotox-repo.sh stable-evidence-plan`. The stable command
`iotox ship-check all stable --evidence-manifest stable-evidence.manifest`
stays blocked until every sync and Ratox gate is backed by a content-free
receipt or review-record file whose SHA-256 matches the manifest. Stable sync
evidence is also shape-checked by the binary, so storage-readiness,
long-soak, recovery-custody, restore-drill, and recovery-runbook
entries cannot be satisfied by arbitrary prose. Long soaks are explicit stable
evidence: sync contributes `sync.long-soak`, and `terminal.long-soak` must be
an accepted native terminal long-soak receipt, not just a label.
`tools/run-massive-soak.py plan|preflight|smoke|launch-long|status|watch|stop`
is the repo-level orchestration porch for the elapsed campaign that matters
before trusting daily-driver behavior: sync long soak, terminal long soak,
person background delivery, Toxic bridge loops, resident service status, and
route-specific claims. See `docs/massive-soak.md`.
`tools/iotox-repo.sh current-stable-evidence` prints the current accepted
local all-scope dossier and expected manifest SHA-256; the current pointer uses
the refreshed service-reality manifest under
`.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/`.
`tools/iotox-monsternix-adapter.sh` is currently a read-only doctor/plan porch for later exact IoTox
source/package/proof admission into MonsterNix. Future sync, terminal, sudo, and service-manager
helpers must stay inside that split. Neither layer may become a second device-authority root, a
hidden sudo switch, witness deployment, or an automatic backup claim. ADR 0363 freezes that
boundary; ADR 0365 adds the retained witness-custody drill wrapper; ADR 0366 adds local
requirement flags and the retained sync recovery drill helper; the 2026-09-17 loopback helper makes
the local different-device recovery prerequisite repeatable without calling it recovery custody;
ADR 0378 adds the first same-host dm-snapshot dishonest-storage drill; ADR 0379
adds the ext4+btrfs matrix including `dm-flakey drop_writes`.

Ignored VM proofs, interrupted benchmark fixtures, and reproducible build trees are audited with
`python3 tools/clean-workspace.py`. Cleanup is dry-run by default, protects documented evidence, and
requires explicit `--apply`. It also covers strictly named stale payloads in the nested
`.sandworm/home/.local/share/Trash/` tree so sandbox-side trash cannot silently become repository
bulk. It has a bounded `operator-tor` scope for failed route caches;
the Sandwurm scope recognizes exact `iotox-device-repair.*` offline postmortem workspaces without
allowlisting arbitrary `.sandwurm` children. Strict pair, three-writer, shadow,
ten exact sync-power-cut, signed-metadata-corruption, and dishonest-storage proof classes can be
pruned only when undocumented; tracked Markdown protects their
compact evidence. A dedicated `sync-power-cut` scope makes the multi-gigabyte raw VMM lifecycle
auditable after strict compact export; `sync-metadata-corruption` does the
same for its separate one-boot class; `sync-dishonest-storage` audits the
dm-snapshot liar-drill receipts and optional raw roots.
Accepted operator-Tor runs remove their private roots automatically. Accepted pair proofs can first
be reduced to the verifier's exact content-free surface with `tools/export-sandwurm-pair.py`; see
`docs/workspace-retention.md`.

## What rev0051 adds

Rev0051, “Freshness-Explicit Projection Recovery,” separates three storage
questions that look similar but require different guarantees. Successful
tree-v2 repair now says `rollback-witness=0|1`: authenticated signed metadata
is not called fresh unless the independently configured witness participated.
Direct tests restore cryptographically valid old branch, workspace, and
maintenance state together with matching old local guards and prove that a
current external witness refuses both live and cold replay without changing
either side.

The writable projection path now catches two concrete descriptor race points.
If a file changes through an already-open descriptor after the last
pre-exchange scan or immediately after the directory exchange but before
validation, IoTox validates the obsolete tree at its staged path, returns
`protocol_error`, and retains both projections plus the pending signed
workspace for operator recovery. Preserved excluded/sparse
paths are compared in both directions as exact path/type/mode/size/digest
closures. A canonical prior projection marker must bind the authenticated
active manifest before policy-transition absence is tolerated; a missing,
malformed, or unrelated marker fails closed. This is intentionally bounded:
writes after final old-tree validation begins, writable mappings, and hostile
same-UID writers remain open architectural work.

ADR 0340 qualifies that production path at the real syscall boundary on the
founding Sandwurm/KVM/ext4 stack. Source-linked run `1fq3WhIY`, bound to
commit `e034311`, fences selected entry and unselected exit
`renameat2(..., RENAME_EXCHANGE)` cases with external `strace`, proves held
descriptor inode continuity, live `sync-repair` refusal, controlled restart,
ext4 busy read-only-remount refusal while a writable descriptor remains open,
closed-descriptor RO/RW remount preservation, cold-start refusal before control
socket exposure, explicit salvage publication, `[3,3,3]` convergence, and
repair. Compact proof `.sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY`
independently replays through the same strict verifier. See
`docs/evidence/2026-09-08-sync-projection-descriptor-retention.md`.

Metadata-corruption receipt v2 also places all five byte-invalid signed roots
on disk together while every Agent task is stopped, then proves first-error
repair refusal, controlled shutdown, layered cold-start refusal, exact ordered
restoration, and final convergence. The mutations are sequential harness
writes made before Agent resume, not one atomic storage transaction. The
strict verifier retains backward replay of the accepted rev0050 receipt and
reports which receipt schema it actually verified. The rev0051 v2 Sandwurm
qualification now passes as compact proof `run.MG27auOK`, bound to source
commit `2be7a2a`; the retained rev0050/v1 proof remains historical
single-family evidence, not v2 evidence. See
`docs/evidence/2026-09-08-sync-tree-v2-co-resident-metadata-corruption.md`.

## What rev0050 adds

Rev0050, “Fail-Closed Metadata Restoration,” closes the first durable-record
corruption slice. Agent startup and `sync-repair` now authenticate all five
present namespace-local signed semantic roots: branch pointer, exact immutable
branch record, referenced manifest, workspace, and maintenance. Errors name
the family; the corrupt signed bytes remain untouched, and ordinary mutation
cannot overwrite them. Recovery is deliberately external and byte-exact.

The bounded Sandwurm construction runs three source-linked nodes and six
read/write shares inside one networkless KVM/ext4 guest. It applies one
same-size last-bit flip per family, demands protocol-error exit 4 from live
repair and startup exit 3 from a cold Agent, checks exact corrupt-byte
retention on both paths, restores the original bytes with file and parent
barriers, and requires unchanged identity/worktree plus final `[3,3,3]`
convergence. Compact export projects extensible Sandwurm records into closed
content-free summaries and authenticates its exact five-file surface.
Run `mixJ9VUp`, source-linked to commit `08e4179`, passes in 26.429 seconds;
its binary SHA-256 is
`449107ef7152547ededabd378c6298cda2963169527e2912f79676209fcef5bf`.
This is
not automatic repair, valid-old rollback detection, recovery-custody
provenance, simultaneous corruption, physical power, or dishonest-storage
evidence.

## What rev0049 adds

Rev0049, “Semantic Branch-Publication Recovery,” turns the three pre-rename tree-v2 metadata states
into strict whole-VMM targets. Proof v5 separately selects the fully written and file-fsynced
manifest `.install.tmp`, immutable branch-record `.install.tmp`, or mutable branch-pointer
`.update.tmp`; binds exact target and prior bytes; and requires the stable prior worktree plus the
correct durable metadata prefix. A redacted commitment object carries hashed names, exact sizes,
successor hashes, and the prior-pointer hash consistently across both boots. A qualification-only
external `strace` delay stops the actual sync
worker at syscall entry. The harness then proves that worker remains ptrace-stopped and every Agent
thread is stopped before the host kills the exact task-owned Cloud Hypervisor process. After the
second boot, the selected temporary may be absent or exact, every unrelated temporary must be
absent, and ordinary startup must authenticate the successor, advance its pointer, converge all
three nodes, and repair. The v5 harness, strict verifier/exporter, NixOS cells, and guarded cleaner
are implemented, and the three repaired-source-linked campaigns pass with independently verifiable
compact proofs. The pointer cell first exposed and then verified the repair for an orphan immutable
record beside a prior mutable pointer. This result does not cover post-rename/pre-directory-fsync
windows, dishonest storage, physical power, or backup trust.

## What rev0048 adds

Rev0048, “Durable Object-Pipeline Recovery,” makes tree-v2 receive and immutable-object cleanup
durable without restoring a directory barrier per file. Canonical `.receive-*.part` and exact
`.iotox-.receive-*.part.part-<six-base62>` transport-temporary cleanup use one
incoming-directory `fsync` per bounded lane batch, while recovered CAS `.install.tmp` removal is
persisted in its exact fanout directory. The versioned whole-VMM gate can now stop one real follower
at either a partial authenticated receive or the exact CAS install temporary, kill the task-owned
Cloud Hypervisor process, boot the crash image under a second kernel, inspect the offline tree and
temporary/object states before Agent startup, and demand exact three-writer convergence and repair.
V2/v3 workspace-cut evidence remains independently verifiable; v4 is reserved for the object
pipeline, and both source-linked v4 cells now pass. This strengthens ordinary crash recovery. It
does not make `fsync`-dishonest hardware
honest, certify precious-data backup, or qualify the remaining branch-publication and corruption
matrix.

## What rev0047 contains

One installed executable, `iotox`, now exposes the complete transport-friend lifecycle through
ordinary private FIFOs and typed local control. Friendship is ordinary but never authority:

```text
outgoing request  exact root `request` record carrying a complete Tox address and message
incoming accept   exact `accept` record in requests/<PUBLIC_KEY>/accept
incoming reject   exact `reject` record in requests/<PUBLIC_KEY>/reject
peer removal      exact `remove` record in peers/<PUBLIC_KEY>/remove
lifecycle read    bounded friend-events journal through files or the one binary
```

Established peers additionally expose:

```text
message/action   live normal/action Tox text; no durable queue or machine authority
command          signed durable machine intent; commit precedes transport or effect
file-send        one absolute finite local source path
file-receive     one provider file number plus one absolute local destination
file-control     one provider file number plus pause, resume, or cancel
```

Local Tox presentation is readable under `self/name`, `self/status-message`, and `self/status`.
Private `name-set`, `status-message-set`, and `status-set` FIFOs in that directory mutate the same
typed provider state as the `iotox profile-*` commands; these fields are never IoTox authority.

All paths converge on typed C++ product code and one serialized c-toxcore owner thread. FIFO bytes
are local framing only: they are never the durable command queue, file payload, remote receipt, or
completion truth.

The registered machine reads are `device.describe` and the privacy-bounded `system.summary`. The
first mutation is `profile.status.set available|away|busy`, a non-expiring desired-state operation
requiring `write.settings`. `update.stage HEAD` is a second non-expiring operation requiring
`install.firmware`; it can only populate the independently verified inert inactive slot. All four
cross the signed durable command path. Presence is presentation, not identity or actuation. No GPIO,
generic setting, remote update apply/restart/confirm, arbitrary shell operation, or remote-selected
local path is advertised.

The terminal boundary retains two separately enabled roles. The host resolves one
owner-controlled canonical profile for the authenticated principal, routes negotiated `0xA2` frames
through the exact session/authority epoch, and drives the PTY controller with bounded round-robin work.
Every native child crosses the common capability-hygiene, nondumpability, identity, resource, and
inventory-proved descriptor floor. Profile v7 defaults to verified `no_new_privs` and the
architecture-checked, argument-aware baseline seccomp tier, which also requires pidfd-backed
session-wide lifecycle containment; it may opt into fail-closed MDWE plus Landlock ABI 10 strict
confinement. A separately reviewed non-root account profile may instead set
`allow-privilege-escalation=1` with compatibility confinement, preserving the host capability bound
for ordinary sudo while clearing every active/ambient capability before shell exec. Root-starting,
baseline/strict, and delegated-cgroup combinations fail closed. The controller role creates the
private `terminal.sock`, joins canonical local packets to a replay-bounded Ratox client, and exposes
`iotox terminal`, `iotox terminal-resume`, `terminal-sessions`, authenticated `terminal-close`, and
pipeline-safe `--batch`; ADR 0289 adds interactive `terminal PEER --reconnect`, which retries only the
exact retained session after authoritative loss and accepts only a higher generation. ADR 0300
qualifies one genuine loss on direct UDP and forced TCP; ADR 0316 carries one unchanged production
client and retained shell through two sequential losses with exact generations and byte progress.
Client-only activation never loads profiles or creates a process. The same
binary now authors and strictly rereads canonical profile/binding stores and live-probes host
confinement and sudo prerequisites with `host-capabilities`, discovers canonical login shells with
`terminal-shell-discover`, and emits disabled ordinary or explicit-sudo account profiles with
`terminal-profile-shell-template`. The separate `iotox-rescue-toolbox` package adds about 1.22 MiB
of static oksh 7.9 plus Toybox 0.8.14 userland, while
`terminal-profile-toolbox-template` emits its explicit disabled baseline profile with the toolbox
first in PATH. Toybox's pending shell is excluded; oksh is the reviewed interactive shell. ADR 0301
adds same-source static AArch64 bytes, validated SPDX/provenance, qemu-user execution, and v7 payload
pins. ADR 0304 passes the unchanged pinned production PTY as UID 1000 on AArch64 Linux 6.6.94 under
QEMU system emulation; one named real target remains before that capsule is recommended. This is
prepared fallback when dynamic userland is damaged, not automatic failover or a second IoTox product
binary. These owner-local additions do not change frozen Ratox or local terminal framing (ADRs
0285--0289, 0300, 0301, 0316). The client sends one frozen-v1
attachment heartbeat per second and warns after three missed
deadlines without detaching or changing carrier/session truth; one exact PING identity per attachment
bounds the host replay cost. Signed authority-head mutation remains serialized with PTY/controller effects and retained
transport admission. `docs/terminal-profile-v7.md` freezes the current payload-integrity policy;
`docs/terminal-profile-v6.md` retains the identity/elevation policy;
`docs/terminal-profile-v5.md` retains the unchanged I/O budget and kernel-outcome contract,
`docs/terminal-client-v1.md` freezes the local stream, and ADRs 0064 through 0090 record the process,
network-dispatch, controller, admission, restart, evidence, confinement, argument-fence,
lifecycle-freeze, descriptor-proof, procfd-session, delegated-cgroup, message-bound local-IPC, and
boot-bound orphan-recovery boundaries. This remains
experimental capability-gated construction, not a complete sandbox or production remote shell.
For self-owned machines, `--mode self` is the preferred Ratox activation shape: host and controller
come up as part of the Agent, but no peer can attach until the owner has installed and bound a fixed
profile and granted `interactive.terminal`. For a concise outsider-facing explanation of what Ratox
is, how it differs from OpenSSH, and what an Eternal/Mosh-shaped future would still require, see
[`docs/ratox-ssh-status.md`](docs/ratox-ssh-status.md).
The optional static fallback, exact commands, retention requirements, and hard failure limits are in
[`docs/ratox-rescue-toolbox.md`](docs/ratox-rescue-toolbox.md).

The exact shared-library toxcore mock acts as another IoTox peer and drives the product fixture,
including callbacks, send-queue pressure, live text and receipts, transcript proof, authorization,
offline durable admission, cancellation, backoff/retry and restart, paused finite-file offer, path
admission, exact-byte publication, and two-sided file control.

## Ordinary friendship

The runtime root owns:

```text
<RUNTIME>/
├── friendship.help
├── request                 private outgoing-request FIFO
├── request.help            exact record and evidence contract
├── friend-events
├── requests/<PUBLIC_KEY>/
│   ├── message
│   ├── request.help
│   ├── accept              private FIFO
│   └── reject              private FIFO
└── peers/<PUBLIC_KEY>/
    ├── lifecycle.help
    └── remove              private FIFO
```

Outgoing example:

```sh
address=<76-HEX-TOX-ADDRESS>
printf '%s\t%s\n' "$address" 'hello from my device' > "$RUNTIME/request"
# Structured equivalent:
iotox --runtime "$RUNTIME" transport-peer-request \
  "$address" 'hello from my device'
```

The exact root record is `<76 hexadecimal address bytes><TAB><1..921 message bytes><LF>`. The
complete address includes the 32-byte public key, 4-byte nospam, and 2-byte checksum. Hex may be
upper- or lowercase. IoTox decodes exact syntax; c-toxcore decides checksum, own-key, duplicate, and
changed-nospam semantics. There is no whitespace search and no default message.

After TAB, every non-LF byte is message data, including TAB, NUL, CR, and high bytes. Shell
variables cannot carry NUL, so binary producers must construct the finite record and make one direct
`write(2)`. The maximum is 999 bytes including LF. IoTox queries the actual FIFO `PIPE_BUF` and
refuses the promised lane if that complete record cannot be atomic.

Incoming and established examples:

```sh
printf '%s\n' accept > "$RUNTIME/requests/$REQUEST_KEY/accept"
printf '%s\n' reject > "$RUNTIME/requests/$REQUEST_KEY/reject"
printf '%s\n' remove > "$RUNTIME/peers/$PEER/remove"
iotox --runtime "$RUNTIME" friend-events
```

`accept`, `reject`, and `remove` require the exact lowercase filename token plus LF. A successful
writer-side `write(2)` means only kernel admission. `friend-events` records parse or provider
disposition. `request-send disposition=requested` proves only that `tox_friend_add` accepted the
request into local Tox state; it does not prove remote receipt or acceptance.

Malformed request records with no trustworthy public-key prefix render `public-key=unknown` rather
than inventing an all-zero peer. A successful request creates the peer projection under the
uppercase public key. Removal is public-key-bound all the way into the serialized toxcore owner
thread, where lookup and delete occur in one queued operation so friend-number reuse cannot redirect
the mutation.

Accepting, requesting, rejecting, or removing Tox friendship leaves the signed IoTox authorization
ledger unchanged. Rejection withdraws only IoTox's live inbox record because c-toxcore has no
pending-request object or remote rejection operation. Deletion likewise does not notify the remote
peer.

See `docs/ratox-friend-lifecycle-v1.md`, ADR 0048, and ADR 0049.

## Ordinary human text

Every projected peer now owns:

```text
<RUNTIME>/peers/<PUBLIC_KEY>/
├── message             private FIFO: normal Tox text
├── action              private FIFO: Tox action text
├── message.help        exact writer/evidence contract
├── message-events      bounded local ingress evidence
└── messages            bounded transport lifecycle journal
```

Examples:

```sh
printf '%s\n' 'hello from the workshop' > "$RUNTIME/peers/$PEER/message"
printf '%s\n' 'waves'                   > "$RUNTIME/peers/$PEER/action"
```

Each body is 1..1372 bytes followed by LF. LF frames the FIFO record and is removed; the local
adapter preserves every other byte, including NUL, CR, and high bytes. Current c-toxcore 0.2.23
copies the supplied bounded span without validating UTF-8, but the Tox message protocol defines
normal/action bodies as UTF-8. Use valid UTF-8 for interoperable human text. Arbitrary machine bytes
belong in IoTox lossless packets or Tox file transfer, not in a text lane. A complete body plus LF
must be emitted in one `write(2)`. The daemon queries each FIFO's `_PC_PIPE_BUF` and refuses to
monitor the lane unless the 1373-byte maximum is atomic.

The same binary also exposes stdin and hex entrances for exact adapter testing, embedded LF, and a
synchronous typed response:

```sh
printf 'a\0b\nc' | iotox --runtime "$RUNTIME" message-stdin "$PEER"
iotox --runtime "$RUNTIME" action-hex "$PEER" 6100620A63
```

Evidence remains layered:

```text
FIFO write success            kernel accepted bytes
message-events accepted       IoTox framed the record and toxcore assigned an id
messages outgoing             transport journal observed local send acceptance
messages receipt              c-toxcore reports remote friend receipt
application effect            not defined; text is never a machine command
```

There is no hidden offline spool or retry. Exact failures distinguish absent peer, disconnected
peer, saturated toxcore send queue, and invalid body. Message id zero is valid and represented with
an explicit presence field. c-toxcore clears still-pending text receipts when a friend disconnects;
IoTox therefore abandons the corresponding local kind correlations and emits a diagnostic rather
than retaining stale receipt state or promising a future receipt.

See `docs/ratox-message-fifo-v1.md` and ADR 0043.

## Ordinary finite files

Every projected peer also owns:

```text
<RUNTIME>/peers/<PUBLIC_KEY>/
├── file-send              private FIFO: absolute finite source path
├── file-receive           private FIFO: file number, TAB, absolute destination
├── file-control           private FIFO: file number, TAB, pause|resume|cancel
├── file.help              exact grammar and evidence boundaries
├── file-events            bounded ingress and toxcore callback journal
└── files/
    ├── incoming/<NUMBER>/ atomic live transfer projections
    └── outgoing/<NUMBER>/ atomic live transfer projections
```

Examples:

```sh
printf '%s\n' /home/alice/export/snapshot.bin > "$RUNTIME/peers/$PEER/file-send"
printf '%s\t%s\n' 65536 /home/alice/import/snapshot.bin \
  > "$RUNTIME/peers/$PEER/file-receive"
printf '%s\t%s\n' 7 pause  > "$RUNTIME/peers/$PEER/file-control"
printf '%s\t%s\n' 7 resume > "$RUNTIME/peers/$PEER/file-control"
printf '%s\t%s\n' 65536 cancel > "$RUNTIME/peers/$PEER/file-control"
```

The FIFOs carry path and control records, not file bytes. Source and destination paths are local,
absolute, bounded, and never shell-evaluated. Incoming offers remain paused until `file-receive`
validates policy and acquires a private same-directory temporary file. The destination appears only
after exact completion, file synchronization, no-clobber publication, and directory
synchronization.

Pause ownership is two-sided. A local resume clears only local pause and cannot override a peer
pause. A pending incoming offer cannot use generic resume before a destination is acquired. The
complete c-toxcore file number is preserved as an opaque friend-specific handle and may be reused
after terminal completion.

Evidence remains layered:

```text
FIFO write success          kernel accepted one local record
file-events ingress         IoTox accepted or rejected its semantics
file-events transport       a toxcore file callback was observed
files/... projection        transfer is live now; not durable
incoming destination        safely published completion truth
```

See `docs/ratox-file-fifo-v1.md` and ADRs 0045–0047.

## Ordinary durable command

Each peer also owns:

```text
<RUNTIME>/peers/<PUBLIC_KEY>/
├── command              private FIFO
├── command.help         exact local command contract
├── command-events       bounded admission evidence
└── iotox/description/   current terminal `device.describe` projection
```

A conforming write is:

```sh
printf '%s\n' device.describe > "$RUNTIME/peers/$PEER/command"
printf '%s\n' 'profile.status.set busy' > "$RUNTIME/peers/$PEER/command"
iotox --runtime "$RUNTIME" command "$PEER" profile.status.set busy normal
# After the receiver has accepted the exact signed-update sync HEAD:
iotox --runtime "$RUNTIME" command "$PEER" update.stage "$HEAD" high
```

The printable operation record is bounded to 256 body bytes. The FIFO monitor hands one framed
record to the same durable command entrance used by `iotox command`. It owns no persistent queue,
authority policy, transport retry, or result state.

For each logical command, IoTox freezes and signs:

```text
direction and remote Tox public key
persistent sender epoch and message id
canonical request bytes
operation and authority evidence
lifecycle and delivery state
canonical application receipt
canonical terminal result
```

Outgoing requests commit before toxcore send. Incoming requests commit before application receipt.
Authority/start state commits before execution. Terminal bytes commit before send. Exact duplicates
replay exact committed evidence; different bytes under an existing durable key are conflicts.

The signed v3 store is plaintext and whole-snapshot. It independently persists request, receipt,
and result schedules; bounded priority/quota policy; cancellation-before-first-attempt; TTL clock
requirements; and `expired` versus `timed-out-unconfirmed` terminal evidence. It detects record
mutation but not replacement by a valid older snapshot. Rollback resistance, confidentiality,
compaction, flash wear, and physical-effect semantics remain open.

The FIFO is still ingress only. Structured offline admission and cancellation are explicit:

```sh
iotox --runtime "$work/run" command "$FRIEND" system.summary high
iotox --runtime "$work/run" \
  command-cancel "$PEER_KEY" "$SENDER_EPOCH" "$MESSAGE_ID"
```

An optional final TTL in milliseconds requires daemon startup with `--trust-wall-clock`; signed
history is checkpointed and checked at startup, then monotonic elapsed time guards the live process
against a backward wall-clock step before time-sensitive work proceeds:

```sh
iotox run --trust-wall-clock --clock-rollback-tolerance-ms 300000 ...
iotox --runtime "$work/run" command "$FRIEND" system.summary normal 60000
```

See `docs/ratox-command-fifo-v1.md`, `docs/command-store-v3.md`, and ADRs 0036–0042 plus 0055.

## Identity and authority

IoTox separates:

```text
Tox endpoint identity        route/session endpoint and friendship
stable IoTox device identity product identity above route replacement
RecallRoot owner principal   reproducible owner authority from permanent phrase
authorization ledger         roles, capabilities, revocation, and epochs
```

Tox friendship is transport only. Mutual transcript confirmation is compatibility only.
Stable-principal proof binds an authority candidate to the confirmed transcript, but the signed
local ledger alone decides active roles and capabilities. Required friend-connection callbacks alone
open and close protocol epochs; friend-list snapshots reconcile inventory and presentation only.

The permanent generated phrase and fixed Argon2id RecallRoot-v1 contract are intentional. Offline
password guessing is possible by design; generated phrase strength is structural. No vendor key,
account, or service may silently reassign customer devices.

Authority-ledger v2 is reached only by one owner-self-signed `migrate-v2` record that extends the
exact v1 tail. Migration preserves every principal at its exact old capability mask and changes the
signature/digest domain; it does not grant `interactive.terminal`. New binaries continue to read v1,
while v1 binaries reject the v2 header and record format. The separate private `IOTOXAG2` guard
detects replacement, deletion, or forking of the ledger alone and recovers the two exact interrupted
replace states. Coordinated replacement of both files still requires an external monotonic witness
to detect.

Authority-ledger v3 is reached only from an exact v2 head through one owner-self-signed
`migrate-v3` record. It preserves every grant and adds no power during migration. Feature bit 25,
independent `IAL3` record/digest/proof domains, and the existing rollback guard bind the new format.
Bits 8–11 name `sync.admin`, `sync.publish`, `sync.subscribe`, and `sync.activate`. The current owner
must receive desired v3 bits in a separate explicit self-grant before delegating them.

## Build the owned implementation

From the repository root:

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
./build/gcc-debug/iotox --version
```

Expected identity prefix:

```text
IoTox 0.51.0 rev0051
```

The 62-entry default CTest surface includes separate namespace-backed cgroup lifecycle,
memory/PID-controller, CPU-controller, I/O-controller, and PSI-admission process oracles. The direct
unit/integration runner registers 844 C++ checks, plus separate native PTY, controller-fault,
restart-fence, one-binary, and cgroup process tests. Warnings are errors. GCC and Clang presets, sanitizers, twelve parser/state
fuzzers, a system-linked Argon2 lane, and the preserved Mutorr incubator are driven by:

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-matrix.sh
```

Historical final results and exact caveats live in the revisioned research reports, especially
`docs/research/cloudtainer-build-report.md`. Bulky generated logs and old prebuilt binaries are no
longer retained in the tracked source tree; current public handoff goes through the clean-tree
repository datacube and same-commit standalone distribution checks. Do not infer green real-network
behavior from the exact ABI mock.

## Run the exact one-binary fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

This starts the actual `iotox run` process and operates it through the same executable plus literal
peer FIFOs. It exercises private runtime publication, profile continuity, friendship, human text and
action, outgoing message identifiers and receipts, HELLO, transcript confirmation, authority proof,
durable command denial and success, delayed admission, safe cancellation, offline admission,
injected `SENDQ`, byte-identical backoff/retry, exact result replay, finite-file
send/receive/control, exact-byte publication, orderly stop, restart, and frozen-record recovery.

The mock verifies the consumed C ABI and the IoTox control path. It is not a Tox network
implementation and cannot prove bootstrap, NAT traversal, UDP, relay, or genuine-peer behavior.

## Operator surface

Start a temporary node:

```sh
work=$(mktemp -d)
./build/gcc-debug/iotox run \
  --state "$work/tox.save" \
  --identity "$work/device.identity" \
  --authority-ledger "$work/authority.ledger" \
  --command-store "$work/commands.store" \
  --runtime "$work/run"
```

For a reviewed service deployment, put those same arguments in one canonical owner-private record,
then lint it and prepare the profile work needed before terminal preflight/start:

```sh
iotox init plan --root /var/lib/iotox --mode self --enable-sync
iotox init write-config --root /var/lib/iotox --mode self --enable-sync
chmod 600 /var/lib/iotox/agent.conf
iotox config-lint /var/lib/iotox/agent.conf
iotox terminal daily-plan --root /var/lib/iotox --peer alias:self
iotox terminal daily-status --root /var/lib/iotox --peer alias:self
iotox terminal service plan --root /var/lib/iotox --manager systemd-user
iotox terminal service render --root /var/lib/iotox --manager systemd-user \
  --binary /usr/bin/iotox --raw > ~/.config/systemd/user/iotox-self.service
iotox terminal service receipt --root /var/lib/iotox --manager systemd-user \
  --binary /usr/bin/iotox --accept-operator-responsibility \
  --out /var/lib/iotox/terminal-service.receipt
iotox service plan --target all --root /var/lib/iotox --manager systemd-user
iotox service render --target all --root /var/lib/iotox \
  --manager systemd-user --binary /usr/bin/iotox --raw
iotox service receipt --target all --root /var/lib/iotox \
  --manager systemd-user --binary /usr/bin/iotox \
  --accept-operator-responsibility \
  --out /var/lib/iotox/resident-service.receipt
iotox terminal activation-check --root /var/lib/iotox --peer alias:self
iotox terminal graduation-check --root /var/lib/iotox --peer alias:self
iotox ship-check terminal stable
iotox terminal profile plan shell owner-shell "$USER" --store /var/lib/iotox/ratox
```

`init plan` is read-only and prints the exact canonical record plus the replayable write/lint/check/run
commands. `init write-config` writes a no-clobber owner-private `0600` config using the same
AgentConfig encoder that `config-lint` reads. The record is shell-free, command-line option groups replace same-named file groups, and both
`run-check` and `run` cross the same static preflight. In self mode, the Ratox host/controller are
selected by default but still start locked: install and bind a reviewed terminal profile before
expecting terminal readiness. `terminal activation-check` is the fail-closed daily-driver porch:
without evidence labels it prints what still needs proving; with labels it records operator custody
but keeps `repo-certified=0`. `terminal service plan|render|receipt` is the
native service-manager porch: it generates systemd/NixOS service artifacts and
a content-free `service-supervision=terminal.service.*` receipt, while keeping
actual service-manager state, cgroup delegation, route loss, and sudo policy as
separate gates. `terminal daily-status` is the non-failing daily dashboard for
the same runbook: status, sessions, reconnect, service generation, stale-profile checks, and the strict activation command.
The top-level `service plan|render|receipt|status-plan|status-receipt` porch
is the resident-service version of that idea: it drafts the long-lived
Agent/sync/Ratox unit and the person messenger background worker together for
systemd-user, NixOS user, NixOS system, or MonsterNix adapter review. Its
render receipt records the reviewed shape; its status receipt records the
operator-observed active/enabled/log-reviewed/health-passed/upgrade-passed
state accepted by `terminal.service-supervision`, without claiming routes are
healthy, sync folders are healthy, cgroups/sudo are graduated, or a human has
read any message.
`terminal graduation-check` is stricter: it adds long soak, Tor/I2P route-loss, sudo policy,
security review, and explicit activation-decision labels before reporting
`daily-driver-graduation=operator-attested`; it remains a host/route/operator attestation, not a
fleet certification.
`ship-check` is the release brake: stable/no-concern Ratox shipping is blocked,
and founder-preview shipping is only the profile-bound self-machine daily-driver
candidate with explicit nonclaims. `tools/iotox-repo.sh release-plan
founder-preview` prints the repeatable release command trail, and
`tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox`
checks the clean-tree/script/gate boundary before packaging.
The stable channel is evidence-gated: run `tools/iotox-repo.sh
stable-evidence-plan`, collect the required receipt files and hashes, including
the sync and terminal long-soak receipts, then use:

```sh
iotox ship-check all stable --evidence-manifest stable-evidence.manifest
```

Then run:

```sh
iotox run-check --config /var/lib/iotox/agent.conf
iotox run --config /var/lib/iotox/agent.conf
```

A successful check says ready for start; it
does not mutate state or claim that locked durable recovery and final PTY-child kernel enforcement
have run. See [`docs/agent-configuration.md`](docs/agent-configuration.md),
[`docs/deploy-systemd.md`](docs/deploy-systemd.md),
[`docs/deploy-nixos.md`](docs/deploy-nixos.md), and ADR 0290.

For encrypted-at-rest Agent state, externally unlock one fscrypt policy-v2 root, place the config and
every configured durable root inside it, keep runtime on tmpfs, and require the boundary explicitly:

```sh
iotox run-check --config /absolute/encrypted/iotox-root/agent.conf \
  --require-state-protection fscrypt-v2 \
  --protected-state-root /absolute/encrypted/iotox-root \
  --protected-state-policy-id 0123456789abcdef0123456789abcdef
iotox run --config /absolute/encrypted/iotox-root/agent.conf \
  --require-state-protection fscrypt-v2 \
  --protected-state-root /absolute/encrypted/iotox-root \
  --protected-state-policy-id 0123456789abcdef0123456789abcdef
```

IoTox receives no key; it verifies the explicitly pinned policy identifier, live key status, mount, extant inodes, configured
and derived paths, and runtime before creating its runtime tree. The default remains unchanged and
unencrypted. The authority-lane rollback transaction coordinator now has a CLI-selectable,
authenticated remote-service backend with device-signed enrollment and a pinned dedicated service
identity. Separately enrolled opt-in application and Ratox incarnation lanes consume an exact signed
next namespace on every startup and reject older valid records before runtime. They are selected by
`--witness-application-incarnation` and `--witness-ratox-incarnation`; the latter requires the Ratox
host. `--witness-route-generation` separately anchors the reviewed signed route policy and admits
only one exact next generation through a crash-recoverable external transaction. All lanes fail
before runtime on stale local state, service outage, or wrong key. `--witness-terminal-policy`
adds one canonical commitment over the complete reviewed profile/binding tree. Profile edits remain
unusable until `iotox witness-terminal-policy-commit --config PATH`; restoring an older
sudo-capable tree plus its signed local checkpoint still refuses.
`--witness-command-effects` separately commits the exact durable frontier of authorized mutable
commands after signed `STARTED` persistence and before either provider/update effect. Restoring a
journal that erases a started effect refuses, while result delivery and read-only work do not move
the lane. This is a replay boundary, not a generic exactly-once claim; effect history intentionally
remains retained until witnessed compaction exists. `--witness-sync-policy` separately commits the
complete canonical namespace and signed automation tree. Startup freezes the exact authenticated
snapshot, and Agent-mediated policy changes advance the remote head before the new policy becomes
live. Quiescent offline changes require `iotox witness-sync-policy-commit --config PATH` and an
Agent restart; restoring an old complete policy tree plus its local checkpoint refuses. Namespace
runtime/guarded state and content are not part of that policy lane. `--witness-update-lifecycle`
separately binds the exact update policy and signed lifecycle state before selected-slot pointer
movement. `--witness-sync-guarded-state` then requires the sync-policy lane and one explicit
`iotox witness-sync-guarded-enrollment --config PATH NAMESPACE` enrollment for every namespace.
Single-writer namespaces use lane 9 for the exact four reachability roots; tree-v2 namespaces use
lane 10 for the live branch frontier plus exact signed workspace and maintenance state. Live
namespace add/remove remains refused, and every namespace reconciles before RuntimeTree. Actual
independence still requires deploying the service outside the Agent's disk/admin/snapshot/failure
domain. ADR 0313 adds an exact service-signed complete-store checkpoint: stop the service, export it
with `iotox witness-service-checkpoint`, verify it against the pinned key, retain it under separate
versioned/append-only or rollback-resistant administration, and pass it as the final
`witness-service-serve` argument. The service then refuses a missing enrollment, selective rollback,
or fork before it binds. A checkpoint kept beside the service store is not independent, and fscrypt
alone cannot detect replay of an older complete encrypted root. See
[`docs/protected-local-state.md`](docs/protected-local-state.md) and ADRs 0302--0314.

An enabled Ratox terminal host may add a delegated-root PSI policy. Values are basis points
(`250` is `2.50%`); these numbers are syntax examples, not qualified deployment defaults:

```sh
  --ratox-cgroup-root /sys/fs/cgroup/iotox \
  --ratox-cgroup-admission-cpu-some-avg10-bp 250 \
  --ratox-cgroup-admission-memory-full-avg10-bp 100 \
  --ratox-cgroup-admission-io-full-avg10-bp 100 \
  --ratox-cgroup-admission-hysteresis-bp 25 \
  --ratox-cgroup-admission-trigger-window-us 2000000 \
  --ratox-cgroup-admission-cpu-some-trigger-stall-us 250000 \
  --ratox-cgroup-admission-memory-full-trigger-stall-us 100000 \
  --ratox-cgroup-admission-io-full-trigger-stall-us 100000
```

Live Ratox attachments use demand-driven 5 ms service and toxcore-iteration caps, then restore the
ordinary idle cadence. `--ratox-active-service-ms` (1..20) and `--ratox-active-iterate-ms` (1..1000)
override those defaults for controlled qualification; runtime status reports the configured values
and whether active mode is selected. These knobs change scheduling only. They do not alter Ratox v1
framing, authority, route choice, or turn an observed latency result into a deadline guarantee.

Startup refuses this policy if the exact delegated root lacks enabled per-cgroup PSI accounting or a
configured interface. Trigger windows are deliberately limited to 2,000,000-microsecond multiples from
2 through 10 seconds, so a daemon without `CAP_SYS_RESOURCE` gets the same accepted policy grammar and
does not request the kernel realtime PSI worker. Runtime status exposes the latch, monitor health, active
hold, hold-specific rejections, and cumulative admission/trigger evidence; it does not make these example
thresholds safe for another workload or host.

From another terminal:

```sh
iotox --runtime "$work/run" status
iotox --runtime "$work/run" address
iotox --runtime "$work/run" identity
iotox --runtime "$work/run" authority
iotox --runtime "$work/run" peers
iotox --runtime "$work/run" requests
iotox --runtime "$work/run" friend-events
iotox --runtime "$work/run" sessions
iotox --runtime "$work/run" command-store
```

Fresh-controller owner re-entry uses the target device's RecallRoot phrase on the controller's
standard input, then delegates only that connected controller's stable device principal:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" \
  authority-delegate-self-recall-stdin "$TARGET_FRIEND" automation read.telemetry
iotox --runtime "$work/run" authority-delegation "$TARGET_FRIEND"
```

The phrase and derived owner secret remain in the short-lived client process. A queued transport
request is not completion; `authority-delegation` reports the correlated receiver outcome and exact
resulting ledger head.

A local v1 ledger migrates without widening the owner:

```sh
printf '%s\n' "$LOCAL_RECALL_PHRASE" | \
  iotox --runtime "$work/run" authority-migrate-v2-recall-stdin
```

For a connected target, first complete the recalled-owner proof, then prepare and sign the exact
remote migration. Confirm the result and run a fresh proof before any later grant:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" \
  authority-migrate-v2-remote-recall-stdin "$TARGET_FRIEND"
iotox --runtime "$work/run" authority-delegation "$TARGET_FRIEND"
```

After migration, grant terminal authority only with an explicit capability list containing
`interactive.terminal` or the explicit `all-v2` token. Plain `all` remains bits 0–6.

To migrate an exact v2 owner into v3, supply that owner's current capability set explicitly. This
prevents the client from guessing whether terminal authority was previously activated:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" \
  authority-migrate-v3-remote-recall-stdin \
  "$TARGET_FRIEND" all-v2
iotox --runtime "$work/run" authority-delegation "$TARGET_FRIEND"
```

Migration still grants no sync rights. Run a fresh proof, then use an explicit v3 grant such as
`all-v3` or a narrower named list.

To revoke an active non-owner principal remotely, first prove the same target owner in the current
authority round, then sign the exact revocation body locally:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$work/run" \
  authority-revoke-remote-recall-stdin "$TARGET_FRIEND" "$SUBJECT_PUBLIC_KEY"
```

For a planned ownership transfer or a phrase-compromise cut, derive the successor's public key
without contacting a daemon. The current owner nominates it; then the successor phrase proves key
possession and signs the next-epoch record:

```sh
SUCCESSOR_PUBLIC_KEY=$(
  printf '%s\n' "$SUCCESSOR_RECALL_PHRASE" | \
    iotox recall-owner-public-key-stdin | sed -n 's/^owner-public-key=//p'
)
printf '%s\n' "$CURRENT_RECALL_PHRASE" | \
  iotox --runtime "$work/run" authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$CURRENT_RECALL_PHRASE" | \
  iotox --runtime "$work/run" \
  authority-nominate-successor-remote-recall-stdin \
  "$TARGET_FRIEND" "$SUCCESSOR_PUBLIC_KEY"
printf '%s\n' "$SUCCESSOR_RECALL_PHRASE" | \
  iotox --runtime "$work/run" authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$SUCCESSOR_RECALL_PHRASE" | \
  iotox --runtime "$work/run" \
  authority-transition-remote-recall-stdin "$TARGET_FRIEND"
```

No authority mutation may intervene between nomination and transition. Confirm each correlated
`authority-delegation` result before proceeding; every applied mutation invalidates prior proofs.
After transition, only the successor is live and all controllers must be delegated again.

For an outgoing request, incoming request, or established peer:

```sh
address=<76-HEX-TOX-ADDRESS>
printf '%s\t%s\n' "$address" 'hello from this node' > "$work/run/request"
iotox --runtime "$work/run" friend-events

request=<64-UPPERCASE-HEX>
cat "$work/run/requests/$request/request.help"
printf '%s\n' accept > "$work/run/requests/$request/accept"
# or: printf '%s\n' reject > "$work/run/requests/$request/reject"
iotox --runtime "$work/run" friend-events

peer=<64-UPPERCASE-HEX>
cat "$work/run/peers/$peer/lifecycle.help"
cat "$work/run/peers/$peer/message.help"
printf '%s\n' hello > "$work/run/peers/$peer/message"
iotox --runtime "$work/run" peer-message-events "$peer"
iotox --runtime "$work/run" peer-messages "$peer"

cat "$work/run/peers/$peer/command.help"
printf '%s\n' device.describe > "$work/run/peers/$peer/command"
cat "$work/run/peers/$peer/command-events"
iotox --runtime "$work/run" peer-description "$peer"

cat "$work/run/peers/$peer/file.help"
printf '%s\n' /absolute/source > "$work/run/peers/$peer/file-send"
printf '%s\t%s\n' 65536 /absolute/destination > "$work/run/peers/$peer/file-receive"
printf '%s\t%s\n' 7 pause > "$work/run/peers/$peer/file-control"
iotox --runtime "$work/run" peer-file-events "$peer"

printf '%s\n' remove > "$work/run/peers/$peer/remove"
iotox --runtime "$work/run" friend-events
```

Use `iotox command-record outgoing PEER EPOCH MESSAGE` to inspect the signed durable record named by
an admitted command event.

## Source-linked standalone direction

The intended product build compiles pinned official dependencies and installs one executable:

```sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
./tools/compare-standalone-builds.sh
./dist/standalone/iotox --version
./tools/run-real-peer-smoke.sh --prepare-keys
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh --fresh-keys
./tools/run-four-route-lab.sh --prepare-keys
IOTOX_FOUR_ROUTE_BYTES=8388608 IOTOX_FOUR_ROUTE_TRIALS=3 \
  ./tools/run-four-route-lab.sh --reuse-keys
IOTOX_FOUR_ROUTE_BYTES=16777216 IOTOX_FOUR_ROUTE_TRIALS=3 \
IOTOX_FOUR_ROUTE_STREAM_TOTALS=8,16,32,64 \
  ./tools/run-four-route-lab.sh --reuse-keys
```

Pinned targets are c-toxcore 0.2.23, libsodium 1.0.22, and Argon2 20190702. The linked toxcore path
requires official upstream headers and links the provider into `iotox`; the runtime-loaded provider
remains available for the exact test double.

The standalone tool fetches and verifies the pinned source graph itself. The resulting linked binary
and the genuine two-peer smoke are maintained release-evidence gates; runtime-loaded providers remain
available for exact ABI doubles in the ordinary test suite. Genuine testing reuses private
test-only Tox/device key baselines by default while resetting all higher-level state; the explicit
fresh-key run preserves first-boot qualification. Neither cache nor retained work may be packaged.
The four-route command is a same-client performance laboratory, not a bonded-transport claim.
`build-standalone.sh` uses Ninja when it is available and falls back to Unix
Makefiles otherwise; set `IOTOX_CMAKE_GENERATOR` only when a release operator
needs to pin a generator explicitly. It still requires ordinary C and C++
compilers in `PATH`, or explicit `CC` and `CXX`; on Nix hosts, run it inside
the project dev shell when the bare shell is intentionally tiny. Set
`IOTOX_STATIC_CXX_RUNTIME=1` to link libstdc++/libgcc statically when the host
toolchain supports it; the choice is recorded in `build-info.txt`.

Each source-linked distribution carries a deterministic, binary-bound SPDX 2.3 source-component
SBOM at `iotox.spdx.json`; the Nix package installs the same contract under
`share/doc/iotox/`. `verify-standalone.sh` refuses a missing or drifted inventory.
`compare-standalone-builds.sh` builds in two disposable empty product roots and requires byte-identical
binary, SBOM, provenance, verification, notice, and license outputs. That is a same-host/toolchain
reproducibility gate, not yet an independent-builder or complete deployment-image claim (ADR 0150).

The flake's qualification-only `toxcoreProviderUpgrade` result separately builds exact c-toxcore
0.2.22 and 0.2.23 fixtures. It proves that two mutually friended old-provider identities survive
current-provider and real-IoTox load/rewrite and remain backward-readable, without linking 0.2.22
into the product or treating readability as downgrade authorization (ADR 0152).

The paired `provider-rolling` Sandwurm gate then boots two simultaneous KVM guests from
0.2.22-created savedata, leaves the client live on 0.2.22, runs the device live on 0.2.23, and
requires bilateral exchange plus exact friend-route truth over direct UDP and forced TCP. Both live
providers rewrite their saves and both versions must read the same post-exchange semantics. Compact
content-free evidence is retained without keys, messages, savedata, guest disks, or bootstrap secret
state (ADR 0153).

## Network model

Current route states are:

```text
IoTox protocol over Tox/native   enabled and network-qualified in the controlled Sandwurm lab
IoTox protocol over Tox/Tor      generic-SOCKS pair plus bounded single/two-peer actual-Tor samples
IoTox protocol over Tox/I2P      strict route, actual-I2P two-guest VM-qualified
```

ADRs 0211–0213 add a lab-only strict SOCKS-to-I2P SAM v3.1 adapter, a persistent silent
SAM-to-loopback service forward, the original `tox/i2p-construction` label, and a bounded
two-live-router actual-I2P STREAM seam.
It maps only explicit numeric Tox records to canonical 52-character b32 destinations, keeps SAM on
numeric loopback, uses one long-lived transient session, and closes admission across SAM loss.
Ten process-double streams pass, including eight simultaneous and generation-two recovery. One
4 KiB warm-up plus four simultaneous 64 KiB byte-verified streams also pass through two distinct
i2pd 2.60.0 processes on this host. Accepted compact proof `pair.k_vopzf5` adds two simultaneous
source-linked Sandwurm guests, three persistent address-preserving service fronts, TCP friendship,
canonical session confirmation, bidirectional text, and TAP evidence that each guest contacts only
the bridge adapter with zero UDP or direct-peer traffic. Accepted compact proof `pair.v_11i2me`
then keeps that listener reachable while client SAM disappears, replaces the exact router over its
preserved datadir, requires both guests to observe authoritative offline, advances both authenticated
epochs from 1 to 2, and exchanges fresh text bilaterally without native fallback.
Accepted compact proof `pair.6rrdsdc_` holds both routers and SAM sessions live while replacing
all three server fronts over their unchanged private Destination keys. Both guests again observe
offline, advance epochs 1 to 2, and exchange fresh text; exact router PIDs own their SAM listeners
and established public TCP sockets. Accepted compact proof `pair.5xjf2n4d` then keeps native control
and fallback members available while private route-binding v2 assigns one exact 131,369-byte signed
tree to the authenticated I2P auxiliary; it verifies and activates with zero reassignment. Rejected
512 KiB and 4 MiB diagnostic attempts selected I2P before carrier loss moved complete work to native.
Accepted compact proof `pair.q2pka1fm` adds route-set-v2 construction authorization on both guests
and converges the bounded tree under explicit fail-closed I2P selection with zero reassignment.
ADR 0253 then promotes that exact policy to canonical `tox/i2p` without changing numeric class 3,
local route-constraint byte 4, savedata, framing, or authority. Production-spelling compact proof
`pair.btm5vwr9` repeats the two-guest baseline through the actual-I2P topology with zero native UDP,
direct bootstrap, or direct-peer packets. `tox/i2p-construction` remains an input/reproduction alias;
it is no longer a separate route.
Accepted compact proof `pair.jbr89_gc` then replaces the client router after positive object bytes,
blocks the exact fail-closed job despite a ready native route, recovers the same signed member with
zero worker restart, and permits only an explicit fresh job to finish. Digest-bound range transport
is now positively qualified by compact proof `pair.ej_4507n`: one native basis plus one I2P-pinned
successor reuses 4,194,176 verified artifact bytes and fetches only its 128-byte changed range on the
exact signed member. Compact proof `pair.a9zwongf` then faults a live 1 MiB range, proves empty
staging and zero downgrade, recovers the same member without worker restart, and completes only
through a distinct explicit fresh job that refetches the range and reuses the other 3 MiB. Failed-
prefix byte resume and broader time/record qualification remain open hardening and availability
work. These results prove neither anonymity nor broad production suitability
(ADRs 0216–0219, 0225–0228, and 0253).

The source-linked provider is `iotox-file-rr1-tcp-connect120`: its established TCP ping cadence and
timeout remain 30/10 seconds, while initial proxy plus relay establishment has a 120-second budget.
Onion path, node, announce, and offline lifetimes remain upstream-exact.
The first I2P/Tox attempt proved why this distinction matters: exact SAM admission took 0.468
seconds while the complete relay response arrived around 34 seconds, beyond upstream's ten-second
combined setup timer. A later address-preserving three-service control and full E2E gate passed with
only this TCP patch; the apparent onion-timeout hypothesis was falsified. This construction patch is
not a latency or availability claim (ADRs 0214–0215).

Fresh I2P construction uses at least three explicit bootstrap and relay records. Each adapter map
must preserve the record's real numeric Tox address: Tox embeds those addresses inside onion paths,
so a local documentation alias can complete SOCKS and relay handshakes while making the remote path
unroutable. Three address-preserving persistent fronts carried the full two-peer application and
authority lifecycle on the founding host. A distinct two-guest Sandwurm baseline proves strict TAP
containment plus friendship/session/text and secret-free compact verification. Its router-restart
companion separates listener, SAM, transport, session, and application truth; both guests recover at
a higher epoch and exchange fresh text. Its service-front companion preserves both routers and
reloads all three stable Destinations in distinct processes before the same application recovery.
Its private-member companion assigns and activates one exact 131,369-byte signed tree on I2P with
zero reassignment while native fallback stays ready. Production `tox/i2p`, large privacy-pinned
payload behavior, and anonymity remain unclaimed (ADRs 0215–0219).

`tox/tor` requires one explicit numeric SOCKS5 endpoint and explicit nonempty numeric bootstrap and
TCP-relay records. It suppresses compiled node catalogs; disables UDP, discovery, announcements,
hole punching, and native DNS; rejects route/proxy confusion and UDP-required auxiliary members
before state mutation; and has no native fallback. The repeatable provider gate is:

Unless `--state` or `IOTOX_STATE_PATH` explicitly selects a path, native uses
`device.toxsave`, Tor uses `device.tox-tor.toxsave`, and I2P uses
`device.tox-i2p.toxsave` in the same state directory. The stable
device identity and authority ledger remain shared above these independent random Tox identities.
Complete cross-route inventory is private authority material: current route-binding v1 is retained
for same-context construction and is not a native/Tor unlinkability claim. The default-off
`--enable-private-route-bindings` path moves the roster to an authority-authenticated primary frame,
admits bounded replay/generation state, and exposes only one inventory-digest-bound member proof on
an auxiliary transcript. Primary authority loss clears auxiliary work and readiness. Repeatable
`--route-worker-network KEY=tox/native|KEY=tox/tor@NUMERIC_PROXY|KEY=tox/i2p@NUMERIC_PROXY`
selects an exact auxiliary local
context and the entire topology is rejected before any worker starts if it is incomplete or
incompatible. Optional repeatable `--route-worker-bootstrap KEY=HOST:PORT:KEY` and
`--route-worker-tcp-relay KEY=HOST:PORT:KEY` records replace that worker's inherited lists, up to 16
unique entries each. They let a Tor member use public numeric rendezvous records while native
members remain pinned to private fixture records. Those endpoint/catalog records remain unsigned
local deployment policy; route-set v2 separately signs the member's coarse network class.
Deterministic Agent/provider evidence and genuine native/generic-SOCKS mixed-context Sandwurm
qualification are complete (ADRs 0198–0202 and 0225). The separate first two-peer actual-Tor auxiliary-route
sample is also qualified (ADR 0203).

```sh
python3 tools/run-tox-tor-smoke.py
./tools/iotox-sandwurm-lab.sh up-pair tox-tor proxy-restart
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-private-mixed
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-payload \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-soak \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
python3 tools/run-tox-operator-tor-smoke.py \
  --node IP:TCP_PORT:64_HEX_PUBLIC_KEY \
  --output operator-tor-receipt.json
```

The first three gates use a numeric-only allowlisted SOCKS5 forwarder, not Tor. They prove
source-linked c-toxcore uses only the proxy, opens no IoTox UDP or direct relay socket, observes
proxy loss, and recovers through the same endpoint. The two-guest proofs additionally bind confirmed
IoTox traffic and exact TAP containment.

The fourth command is the qualified two-IoTox actual-Tor auxiliary-route gate. It leaves native
primary/control traffic on the pinned local fixture and sends one exact-key bulk worker per role
through separate Tor clients with independent process, policy, control, and circuit state. A strict
offline verifier joins each guest source and the operator-supplied public Tox endpoint through raw
authenticated Tor events, checks Tor-owned public-socket commitments and TAP containment, and
requires the same signed 4,194,389-byte tree convergence as the generic-SOCKS cell. Accepted compact
proof `pair.2mycvy9n` records two successful exact-target streams and a distinct three-hop
`CONFLUX_LINKED` circuit per role, 583/531 Tor proxy packets, and zero unexpected context packets.
It proves the Tor members became ready inside the application topology; it does not attribute the
tree's object payload bytes to Tor (ADR 0203).

The next command is the qualified payload-attribution gate. It binds the founding reusable key
ordering before workload start, makes the exact Tor member the fixed scheduler's selected carrier,
and requires the completed client sync job to name that member with zero reassignment. It adds no
production route-forcing control. Accepted compact proof `pair.lzsyitvy` completes the signed
4,194,389-byte tree on that exact member with zero reassignment and first-attempt pull admission.
Both roles bind two successful exact-target streams to distinct three-hop `CONFLUX_LINKED` circuits;
their TAP captures contain 2,469/4,341 Tor-proxy packets and zero unexpected traffic. This is bounded
payload-carrier attribution, not anonymity or physical-path independence (ADR 0204).

The following external-loss gate begins on that exact Tor carrier, captures positive partial-object
progress and authenticated Tor process/control evidence, then has the host `SIGKILL` only the client
Tor process. IoTox must fence the lost incarnation, reassign the immutable job to the other member,
complete it, and count the Tor carrier's return after the same binary bootstraps again. An internal
qualification fault or IoTox route-worker restart is a failure. Accepted compact proof
`pair.iompvehf` kills Tor after 74,034 exact-carrier bytes and records one loss, one native-member
reassignment, two stale terminals, one genuine carrier return, two ready bulk members, and zero
route-worker restarts. The signed 16,777,513-byte treepack converges; three authenticated Tor phases
and both TAP captures independently reverify with zero unexpected-context packets (ADR 0205).

The `ratox-route-actual-tor-loss` pair command is the process-loss terminal follow-on. Both primary agents run entirely through
separate real Tor processes. After an attached PTY crosses its first heartbeat and byte, the host
captures Tor evidence and kills only the client Tor process. The frozen Ratox lifecycle must warn
on heartbeat loss while carrier truth still says TCP, reach authoritative offline, retain one
detached live device PTY, and explicitly resume the same session/incarnation at generation 2 after
the identical Tor instance returns. Zero IoTox daemon restarts, three authenticated Tor phases, and
TCP-only guest TAP containment are mandatory. Accepted compact proof `pair.2waqdpgk` records a
2.204-second heartbeat warning while carrier truth remains TCP, authoritative offline after 27.379
seconds, one detached live PTY, exact-session generation-2 resume after Tor returns, zero IoTox
daemon restarts, and zero guest bypass packets. Its private and 1.65 MiB compact forms independently
pass the strict verifier (ADR 0206; `docs/evidence/2026-08-27-sandwurm-actual-tor-ratox-loss.md`).

The bounded terminal duration cell is accepted as compact proof `pair.k8o54n2v`
(`ratox-route-actual-tor-soak`, ADR 0207).
It holds one attachment for 120 one-second-paced heartbeat/PTTY exchanges, pauses after samples 20
and 100, and closes the exact client then device Tor application circuit through authenticated
control. Live science produced both carrier-loss and no-error attempts even though Tor stayed alive,
so a post-replacement PING now resolves the outcome: PONG requires unchanged epoch/generation;
`unavailable` requires explicit higher-epoch resume and one generation increment. Tor process/control
identity, the Ratox session/incarnation, the remote PTY, and contiguous byte sequences must survive,
while each attributed Tor stream either reattaches on a distinct circuit or reopens as a new stream,
proven by retained authenticated before/after Tor inventories and raw close/recovery ordering, with
TCP-only TAP containment. The accepted run exercised both branches: client same-stream reattachment
preserved epoch 2/generation 1 after 123.813 ms; device stream reopening produced authoritative loss
and explicit same-session resume at epoch 3/generation 2 after 30.220 seconds. All 120 samples, one
PTY/incarnation, exact byte positions, unchanged Tor/IoTox processes, and 5,823 TCP-only guest egress
packets independently reverify in the 3.13 MB secret-free compact proof. This is bounded duration
and controlled circuit-churn science on one host/relay/Tor/time sample; it does not imply anonymity,
relay diversity, automatic migration, public-network availability, or a latency SLA.

ADR 0208 repeats the unchanged cell through a second operator-supplied public record as accepted
compact proof `pair.9cx0jels`. Both exact Tor streams reopen on distinct qualifying circuits in
17.273 and 17.174 seconds, yet both Ratox checkpoints remain at epoch 2/generation 1 with zero
resume. Across the two proofs, `stream-reopened` accompanies both transparent attachment continuity
and authoritative-loss explicit resume. Tor transition type therefore cannot predict or authorize
the application lifecycle. These are two sequential relay-record samples on one host/date, not
exit/time diversity or an availability claim.

The adversarial boundary is now live-qualified through `tools/run-socks5-adversary.py` and
`ratox-route-actual-tor-adversary` (ADR 0209). The separate numeric SOCKS-over-SOCKS interposer keeps
its listener and established TCP streams open while a host-owned hold file withholds relay bytes.
Accepted compact proof `pair.vx6z0csh` keeps listener reachability and a fresh exact-target SOCKS
CONNECT positive while Ratox warns after 2.578 seconds, c-toxcore reaches authoritative offline
after 27.241 seconds, and the device retains the detached PTY. Removing only the hold file permits
exact higher-epoch generation-2 resume with unchanged Tor/interposer/IoTox processes. Every audited
chain is joined to authenticated Tor control and TCP-only TAP containment. Local reachability,
target admission, and Tor control are observations—not carrier or session authority.

The eight retained compact actual-Tor proofs are now jointly and deterministically accounted under
ADR 0210 after ADR 0243's later operator-window repetition. After strict proof verification, 30
exact-target/churn declarations resolve to 24 normalized three-hop paths, 20 first-hop identities,
and 23 last-hop identities; no two proofs
reuse a complete path or last hop. The report publishes only counts and domain-separated
commitments. This closes corpus accounting, not independent exit/operator review, separated time
windows, anonymity, or availability.

The separately qualified single-IoTox actual-Tor route sample binds the exact
Tor binary/configuration, a current operator-supplied public numeric relay, successful initial and
recovered configured-target streams
to new Agent sources and three-hop `CONFLUX_LINKED` circuits, Tor-owned public sockets, and
IoTox-only loopback TCP with no UDP/direct fallback during a held outage. The accepted rev0045
sample used Tor 0.4.8.11, reached TCP in 9.120 seconds, observed local listener refusal 35 ms after
Tor loss while the carrier still reported TCP, reached authoritative offline in 74.602 seconds,
held 30 no-bypass samples, and recovered in 3.913 seconds. It remains one host/relay/time sample—not
anonymity, a public SLA, or the separate two-IoTox auxiliary-route proof.

Owners can inspect the independent local observation without changing that provider truth:

```sh
iotox route-health
iotox route-health FRIEND
iotox --sample-ms 250 --failure-samples 3 --recovery-samples 2 \
  route-health-watch FRIEND
iotox --timeout-ms 2000 route-target-health
```

The first form reports the exact carrier plus a bounded local SOCKS-listener connection when routed;
the second adds a transcript-confirmed lossless peer echo. It exposes no endpoint/peer/nonce content,
never treats a listening proxy as upstream success, and cannot advance a session epoch. SOCKS target
and Tor-control monitoring remain later gates (ADR 0192).

The watch strictly parses each canonical report and keeps independent, process-local boundary and
application latches. Failure/recovery thresholds are bounded to 1..64; defaults are three and two.
Inconclusive observations fabricate no state, and the loop cannot relabel the carrier, detach/resume,
or advance an epoch. The terminal's separate exact Ratox heartbeat crosses the current attachment;
the installed client samples every second and warns after three misses while retaining the session.
It proves remote Ratox route/replay reachability, not PTY progress, output latency, or Tor upstream
health (ADR 0193). The accepted two-guest bounded-impairment matrix therefore measures heartbeat and
PTY echo separately across direct UDP, forced TCP, and strict generic SOCKS. All three keep one
authenticated session through 20 baseline, 80 seeded-delay/loss, and 20 recovered observations.
ADR 0196 freezes partial impairment as warning-only: it cannot detach, resume, or migrate a terminal.
ADR 0197's accepted 100%-loss matrix then separates that warning from authoritative offline on
direct UDP, forced TCP, and strict generic SOCKS. The heartbeat misses after about two seconds while
the route remains confirmed; c-toxcore offline arrives at about 30–31 seconds, returns typed
`unavailable` to the controller, and leaves the exact remote PTY detached and live. After a higher
authenticated epoch, explicit resume preserves session/incarnation/byte positions and advances only
the attachment generation. Automatic migration remains open. ADR 0206's distinct actual-Tor
explicit-resume gate is accepted as compact proof `pair.2waqdpgk`: it retains the same semantics
across a real client Tor process death, with three authenticated Tor phases and zero-bypass TAP
evidence. ADR 0207 separately accepts bounded compact proof `pair.k8o54n2v` for a no-process-loss
soak and records that active Tor circuit closure is not predictably transparent to c-toxcore TCP:
provider-authoritative loss must use explicit Ratox resume when it occurs, while a real PONG proves
same-epoch continuity; never may a circuit observer invent a session transition. Direct IoTox-over-I2P would be a
separate future transport.

The explicit target command is not part of the watch. On `Tox/Tor`, the Agent selects only the first
numeric relay already present in its validated configuration and performs one complete SOCKS5
CONNECT with no application bytes. The content-free result distinguishes proxy-connect, method,
target-connect, and complete stages without accepting or exposing an endpoint. Success proves one
TCP target admission at that instant—not a Tox handshake, Tor circuit identity, or anonymity. The
separate operator gate can bind this observation to authenticated control, an exact stream
lifecycle, and one qualifying circuit without changing the command's ordinary trust boundary
(ADRs 0194/0195).
IoTox should help owners contribute bootstrap and TCP relay infrastructure without granting
infrastructure operators ownership authority. The flake now exports an inert-by-default
`nixosModules.toxBootstrap` service with an explicit pinned package, closed-by-default firewall,
private persistent identity, systemd confinement/resource ceilings, and a KVM restart/firewall
check. It creates no account plane or IoTox-operated endpoint. See
`docs/bootstrap-relay-operations.md`, `docs/networks.md`,
`docs/evidence/2026-08-27-sandwurm-tox-tor-route.md`,
`docs/evidence/2026-08-27-operator-tor-public-route.md`,
`docs/evidence/2026-08-27-sandwurm-ratox-route-impairment.md`,
`docs/evidence/2026-08-27-sandwurm-ratox-route-loss.md`,
`docs/evidence/2026-09-02-sandwurm-ratox-cli-reconnect.md`,
`docs/evidence/2026-08-27-sandwurm-private-route-mixed-context.md`,
`docs/evidence/2026-08-27-sandwurm-actual-tor-ratox-loss.md`,
`docs/evidence/2026-08-28-sandwurm-actual-tor-ratox-churn.md`,
`docs/evidence/2026-08-28-sandwurm-actual-tor-adversarial-boundary.md`,
`docs/evidence/2026-08-28-actual-tor-path-population.md`,
`docs/evidence/2026-08-29-sandwurm-actual-tor-ratox-repetition.md`, and ADRs
0190/0191/0192/0193/0194/0195/0196/0197/0198/0199/0200/0201/0206/0207/0208/0209/0210/0240/0241/0243/0300.

## Ratox inheritance

Keep:

```text
one small supervised process
peer directories keyed by public identity
ordinary files, journals, and FIFOs
external script composition
human text that “just werx”
no mandatory vendor cloud
```

Replace:

```text
friendship as implied authority
FIFO bytes as implicit durable state
one ambiguous text lane for machine control
monolithic transport/business logic
fragile profile persistence
single conflated transfer state
```

rev0020 preserves the complete ordinary relationship loop and hardens the separate default-off Ratox
terminal lane. A signed, exact-head migration introduces the v2 authority vocabulary without changing
any v1 grant; terminal authority appears only in a later explicit v2 record. The Agent now joins that
proof to a locally fixed profile and bounded PTY service, but only after explicit startup activation
and bilateral feature negotiation. Human text still reaches native Tox text, machine intent reaches
signed durable admission, local path records reach finite Tox file transfer, and no friendship
operation becomes authority. A v1 owner without bit 7 receives an exact retained Ratox OPEN denial
and cannot cause a process spawn.

For an owner workstation, first inspect the account and exact shell path IoTox can freeze:

```sh
iotox terminal-shell-discover "$USER"
```

Generate either an ordinary non-elevating login or an explicitly sudo-capable login. Both outputs
are disabled until reviewed:

```sh
iotox terminal-profile-shell-template owner-shell "$USER" \
  > owner-shell.profile
iotox --allow-sudo terminal-profile-shell-template owner-admin "$USER" \
  > owner-admin.profile
```

The default profile uses baseline confinement and permanently blocks set-ID/file-capability gain.
`--allow-sudo` still starts as the frozen non-root account, including its exact supplementary groups,
but selects compatibility confinement and leaves privilege gain to the machine's existing
sudoers/PAM policy. IoTox does not create a sudo rule or test a password. Review the complete record,
change `enabled=0` to `enabled=1`, lint, run `iotox terminal profile check ./owner-shell.profile`
to catch stale executable bytes, install, and bind it with the owner-local profile commands.
See `docs/terminal-profile-v7.md` for the complete ceremony and why a full root-capable shell cannot
honestly retain baseline seccomp/Landlock/cgroup sandbox claims.

## Evidence boundary

Implemented and exercised here:

- C++20 one-binary product and local operator mode;
- runtime-loaded exact c-toxcore ABI boundary and one owner thread;
- pinned source-linked standalone construction and retained two-genuine-peer lifecycle evidence in
  normal native and TCP-relay-only modes on the founding bare-metal host;
- stable savedata and stable IoTox device identity;
- exact root outgoing-request FIFO plus typed equivalent, transactionally published live incoming
  request projection, exact accept/reject/remove FIFOs, public-key-bound owner-thread deletion,
  friend-number-gap reuse tests, explicit keyless parse evidence, and bounded lifecycle journal;
- RecallRoot derivation and signed authorization ledger;
- signed non-widening authority-ledger v2 migration, independent record/proof domains, exact-format
  session negotiation, explicit terminal-capability grant, restart replay, and downgrade rejection;
- signed non-widening authority-ledger v3 migration and a sync admission primitive requiring an exact
  v3 proof, one operation-specific capability, namespace membership, and host activation policy;
- canonical owner-only terminal profiles and principal bindings, atomic generation-bound resolution,
  exact safe environment construction, a fake-backed PTY lifecycle controller, and a native Linux
  descriptor-based PTY child with readiness/error handoff, binary I/O, resize, limits, identity,
  descriptor hygiene, pidfd-backed session-wide close escalation, and exact reap evidence;
- manual/default-off Agent Ratox activation plus self-mode default-on host/controller selection,
  bilateral HELLO negotiation, exact online-epoch and authority gating, bounded coordinator
  queues/replay/tombstones, round-robin PTY service, retained SENDQ output, disconnect detachment,
  authority-revocation shutdown, and content-free lifecycle evidence;
- independent same-user terminal controller stream and one-binary OPEN/RESUME client, default-off in
  manual mode and selected by self mode, with a finite pre-OPEN lease, bounded consume-and-deny
  contention, and exact typed loser outcomes;
- a real-CLI process gate for winner death, replacement resume, retained-output rendering and ACK,
  clean detach, and explicit empty-server restart `not_found` behavior;
- a signed device-bound host-incarnation lease reserved before network startup, plus deterministic
  R6 process proof of route re-entry, exact SENDQ retry, controller replacement, live revocation
  denial, restart `not found`, and durable incarnation advancement;
- HELLO, callback-owned online epochs, transcript confirmation, and directional authority proof;
- bounded canonical command/receipt/result codecs;
- signed v3 durable command store, verified v2 migration, bounded offline outbox, priority/quota,
  clock-gated TTL, cancellation boundary, exact backoff/retry, and restart recovery;
- registered `device.describe` and `system.summary` reads plus the bounded, provider-read-back
  `profile.status.set` desired-state operation and exact-HEAD `update.stage` inactive-slot operation;
- distinct signed `linux-service-v1` intent, sealed memfd execution, exact readiness, local
  confirmation gating, and immediate signed candidate rollback/relaunch without remote execution;
- private per-peer durable command FIFO and evidence journal;
- private per-peer normal/action FIFOs, binary-preserving framing, ingress journal, outgoing ids,
  incoming text, and read receipts;
- typed text failures for absent, disconnected, saturated, and invalid sends;
- finite native file-transfer manager plus private send/receive/control FIFOs, two-sided pause truth,
  callback journal, and live transfer projections;
- compiler, sanitizer, race, and bounded fuzzer facilities, plus the reproducible
  `tools/agent-session-stress.sh` gate with 100 consecutive Agent-session repetitions preserving one
  callback as one online epoch.

Not yet claimed:

- independent reproduction of the founding-host genuine-peer results;
- public-network, production-fleet, reverse-direction, or future-pin rolling-upgrade behavior beyond
  the retained 0.2.22-to-0.2.23 savedata/product-load and two-Sandwurm-guest live route gates; seeded
  5% packet-loss continuity is retained for direct UDP and forced TCP, but is not a public-network SLA;
- Tor/I2P anonymity, large privacy-pinned I2P payloads, or long-running/diverse actual-Tor
  qualification beyond the retained bounded single- and two-peer readiness, 128 KiB I2P payload,
  Tor payload, process-loss, and circuit-churn samples;
- durable offline human-message delivery;
- PTY or controller replay survival across daemon restart, storage-full or power-cut durability,
  Sandwurm two-node remote qualification, multiple simultaneous local terminal streams, cgroup resource
  ownership or proof against unknown future session escapes, production-default Ratox activation, or R7 complete-service evidence;
- automatic clock trust or execution of expiring commands when wall-clock trust is absent;
- rollback-resistant or encrypted persistent stores;
- representative-hardware mutable-state qualification, physical actuation, safety-critical control,
  remote update apply/restart/confirm, bootable OTA deployment, or physical service-adapter
  power-cut/recovery qualification;
- production security audit or target-hardware fitness.
