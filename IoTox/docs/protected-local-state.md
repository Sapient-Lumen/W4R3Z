# Protected local state and independent rollback witness

Status: fscrypt-v2 enforcement, authenticated authority/application/Ratox/route-generation/terminal-policy/command-effect/sync-policy/update-lifecycle/per-namespace semantic-state witness lanes, complete-store checkpoint floors, custody reporting, retained custody-drill receipts, and local custody requirements implemented by ADRs 0303, 0305--0314, 0360, 0365, and 0366; independent deployment and broader freshness campaign remain open
Updated: 2026-09-10

## The split

IoTox needs two separate mechanisms:

1. encrypted storage protects copied or stolen media while its key is unavailable;
2. an independently controlled monotonic witness detects replay of an older, valid complete state.

Encryption does not imply freshness. A witness does not imply confidentiality. Neither is a backup.
The Agent must never silently fall back from a requested protected mode.

## State closure

A protected-state claim covers a declared closure, not a few convenient files. The first Linux
implementation must inventory and contain all security-bearing durable paths selected by the Agent:

| Domain | Required closure |
|---|---|
| Core | Tox savedata, device identity, authority ledger and guard, command store, diagnostic recorder, aliases, protocol and Ratox incarnation records and locks |
| Routes | signed route-set artifact and generation record/lock, every auxiliary worker savedata |
| Ratox policy | profile and binding trees; an old profile may restore sudo or weaker confinement |
| Sync policy | namespace and automation records, managed data roots, and every externally named namespace root |
| Sync state | transactions, heads, activation, retention/pins, rollback guards, attempt journals, CAS/objects/manifests, partial/quarantine trees, tree-v2 branches/workspaces/maintenance, projections and current pointers |
| Updates | update policy, lifecycle state, slots, quarantine and current pointer |
| Deployment | the file-backed Agent configuration that selects all of the above |
| Runtime | tmpfs, or a separately protected filesystem; disk-backed message/file/command projections are otherwise outside the claim |

Derived companions count: `.guard`, `.generation`, lock, pending, intent, temporary, quarantine, and
transaction files must not escape merely because the operator did not name each one on the command
line. User source/worktree data, arbitrary send/receive paths, exports, backups, release-signer keys,
and provider binaries need their own declared storage/code policy and are never covered implicitly.

## Implemented first tier: enforced fscrypt closure

The accepted Linux mode requires one externally unlocked fscrypt policy-v2 root. The Agent
will receive no passphrase or raw key through argv, environment, config, local control, or a peer.
A random 256-bit data key belongs to an explicit custodian such as operator-held material, FIDO2,
TPM2 policy, or a systemd credential provisioned before Agent start. It is not derived directly from
RecallRoot.

Before any runtime listener, network session, command, PTY, update, or sync effect, the Agent now:

- descriptor-pin one normalized absolute owner-private root;
- bind its mount identity with `statx`, require fscrypt policy v2 and one expected master-key ID,
  and require the kernel to report that key present;
- resolve every configured and derived durable path beneath that descriptor without prefix,
  `..`, symlink, bind-mount, or mount-crossing escapes;
- verify every extant inode has the expected policy; and
- require runtime tmpfs or separately verified protected storage.

Unsupported filesystems, absent or wrong keys, partial migration, a mismatched policy, or any state
escape fail start. LUKS/dm-crypt remains an excellent deployment choice, but a path alone does not
prove its key custody; accepting it needs a separately authenticated mount-attestation adapter.

The exact service flags are:

```text
iotox run-check --config /absolute/encrypted/iotox-root/agent.conf \
  --require-state-protection fscrypt-v2 \
  --protected-state-root /absolute/encrypted/iotox-root \
  --protected-state-policy-id 0123456789abcdef0123456789abcdef
iotox run --config /absolute/encrypted/iotox-root/agent.conf \
  --require-state-protection fscrypt-v2 \
  --protected-state-root /absolute/encrypted/iotox-root \
  --protected-state-policy-id 0123456789abcdef0123456789abcdef
```

All three protection fields are required together. The policy ID is the canonical 16-byte
hexadecimal identifier printed by `fscryptctl add_key`; it is a public pin, never the key. `--config`
itself must be inside the protected closure. The
external service manager or local unlock ceremony installs the key before these commands; IoTox
only queries the policy and key status. `run-check` reports the exact policy identifier, configured
path count, verified inode count, and whether runtime is tmpfs. Live `run` repeats the inspection to
close the check/start gap.

Offline migration is: stop Agent; create an empty encrypted root; install policy and key; copy with
descriptor-safe metadata rules; fsync; compare the canonical inventory; switch mount/config; run
preflight; start; retain the old image sealed until recovery is verified. Removing an fscrypt key
requires the Agent stopped and file descriptors closed; it is not instantaneous lockout of a running
kernel.

## Implemented coordinator: authority witness transaction

The independent witness is a second gate. IoTox now pilots the low-frequency authority lane. A witness
record contains a create-once random domain ID, stable device key, witness epoch, closed lane ID,
committed sequence/digest, and optional pending sequence/digest/transaction nonce. Its API is an
authenticated compare-and-swap. A local file implementation is a test double and can never report
`independent=1`.

For one mutation from `old` to `new`:

1. under the existing lane lock, durably write a local intent containing domain/device/lane,
   old/new sequence and digest, exact owner-signed mutation, and random transaction nonce;
2. witness-CAS `committed(old)` to `pending(old,new,nonce)`;
3. run the existing local guard/store transition;
4. witness-CAS the exact pending value to `committed(new)`; and
5. fsync-unlink the intent.

An ambiguous network reply is resolved by querying and retrying the idempotent CAS, never guessing.
Recovery is closed: witness-old/local-old may retry or discard an unapplied intent; witness-pending
requires the exact intent and deterministically completes forward; witness-new/local-new removes a
stale intent. Missing pending intent, unrelated local head, fork, deletion, or an older whole-root
snapshot fails closed.

ADR 0305 supplies the first production-capable backend as a separately runnable role of the same
binary. It uses a dedicated witness-role Ed25519 identity. Every fixed request is signed by the stable
device identity and every nonce-bound response is signed by the pinned witness identity. Enrollment
is an explicit device-signed, no-replace artifact for one exact committed head; network requests can
neither enroll nor reset a lane. The service persists signed exact-CAS records under an exclusive
process lock. A port probe, truncated connection, reset, timeout, or lost response kills only that
client connection, while durable or cryptographic uncertainty stops the service.

The initial ceremony, with the Agent quiescent, is:

```sh
# Witness administration domain
install -d -m 0700 /var/lib/iotox-witness
iotox witness-service-keygen /var/lib/iotox-witness/service.identity

# Device administration domain
DOMAIN=$(iotox witness-domain-generate)
iotox witness-authority-enrollment \
  /var/lib/iotox/device.identity /var/lib/iotox/authority.ledger \
  "$DOMAIN" 1
iotox witness-incarnation-enrollment \
  /var/lib/iotox/device.identity \
  /var/lib/iotox/.iotox-incarnations/device.toxsave.protocol-incarnation \
  application "$DOMAIN" 1
iotox witness-incarnation-enrollment \
  /var/lib/iotox/device.identity /var/lib/iotox/ratox/incarnation.state \
  ratox "$DOMAIN" 1
iotox witness-route-enrollment \
  /var/lib/iotox/device.identity /var/lib/iotox/routes.signed \
  /var/lib/iotox/routes.generation "$DOMAIN" 1

# Transfer each printed signed enrollment hex (authentic, not secret), then
# enroll each artifact exactly once:
iotox witness-service-enroll /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity ENROLLMENT_HEX
iotox witness-service-serve /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity 0.0.0.0 37177
```

ADR 0313 makes independently checkpointed service persistence executable. After enrollment or an
important set of lane advances, stop the service to acquire one quiescent exclusive-store view,
export its complete signed selector population, verify it against the separately pinned service
key, and retain version history outside the service's disk/admin/snapshot domain:

```sh
iotox witness-service-checkpoint \
  /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity \
  /independent/checkpoints/iotox-witness.checkpoint
iotox witness-service-checkpoint-verify \
  /independent/checkpoints/iotox-witness.checkpoint \
  WITNESS_ED25519_PUBLIC_KEY_HEX
iotox witness-service-checkpoint-custody \
  /var/lib/iotox-witness \
  /independent/checkpoints/iotox-witness.checkpoint \
  WITNESS_ED25519_PUBLIC_KEY_HEX \
  custody-system=restic \
  custody-generation=witness-checkpoint-2026-09-10 \
  custody-failure-domain=external-usb-disk
tools/iotox-repo.sh witness-custody \
  --iotox build/iotox \
  --evidence evidence/witness-custody-2026-09-10.json \
  --custody-system restic \
  --custody-generation witness-checkpoint-2026-09-10 \
  --custody-failure-domain external-usb-disk \
  --require-custody-labels \
  --require-different-device \
  /var/lib/iotox-witness \
  /independent/checkpoints/iotox-witness.checkpoint \
  WITNESS_ED25519_PUBLIC_KEY_HEX
iotox witness-service-serve \
  /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity 0.0.0.0 37177 \
  /independent/checkpoints/iotox-witness.checkpoint
```

The optional final argument is a startup floor, not a configuration hint. Before binding, the
service validates every stored record and requires every checkpoint selector at its exact or a later
head. Missing enrollment, predecessor, same-position fork, wrong key, and malformed or modified
artifact refuse. An exact pending record or its exact/later committed successor is valid, so taking
a checkpoint during a recoverable transition does not strand the service. Later no-replace
enrollments may extend an older floor. ADR 0360 adds `witness-service-checkpoint-custody` to verify a
signed checkpoint from outside the service root, report same/different filesystem observation, and
embed optional operator custody labels in hex while still saying
`operational-independence=not-assessed`. ADR 0365 adds the repository wrapper above so an operator
can retain a content-free JSON receipt containing hashes, bounded counts, root-device observation,
and custody-label hashes. ADR 0366 adds `--require-custody-labels` and
`--require-different-device` so independence-oriented drills can reject same-device or unlabeled
receipts instead of merely recording them. The operator must update and preserve the trusted
artifact; a copy beside the witness store adds integrity evidence but no independent freshness.

The device pins the public key printed by `witness-service-keygen` and selects the complete service:

```text
--authority-witness-host witness.example
--authority-witness-port 37177
--authority-witness-server-key WITNESS_ED25519_PUBLIC_KEY_HEX
--authority-witness-domain DOMAIN_HEX
--authority-witness-epoch 1
--authority-witness-timeout-ms 3000
--authority-witness-intent /var/lib/iotox/authority.witness-intent
--witness-application-incarnation
--application-incarnation-witness-intent /var/lib/iotox/.iotox-incarnations/application.witness-intent
--witness-ratox-incarnation
--ratox-incarnation-witness-intent /var/lib/iotox/ratox/ratox.witness-intent
--witness-route-generation
--route-witness-intent /var/lib/iotox/route.witness-intent
--witness-terminal-policy
--terminal-policy-witness-checkpoint /var/lib/iotox/terminal-policy.checkpoint
--terminal-policy-witness-intent /var/lib/iotox/terminal-policy.intent
--witness-command-effects
--command-effect-witness-checkpoint /var/lib/iotox/command-effect.checkpoint
--command-effect-witness-intent /var/lib/iotox/command-effect.intent
--witness-sync-policy
--sync-policy-witness-checkpoint /var/lib/iotox/sync-policy.checkpoint
--sync-policy-witness-intent /var/lib/iotox/sync-policy.intent
--witness-update-lifecycle
--update-lifecycle-witness-intent /var/lib/iotox/update-lifecycle.intent
--witness-sync-guarded-state
```

Host, port, key, domain, and epoch are inseparable. The intent path derives beside the ledger when
omitted. `run-check` validates this closed selection without making a network request; live `run`
authenticates and reconciles it before runtime creation. The C++ injection boundary remains for TPM
or other deployment adapters, but a false-valued same-domain backend is rejected outside tests.

ADR 0306 makes the two incarnation flags independent opt-ins and gives each a separate service
lane. Their intent paths derive beside the corresponding state record when omitted. Application
witnessing is valid for every Agent. Ratox witnessing also requires `--enable-ratox-terminal` and a
valid non-root-start profile store. Enrollment is a quiescent read of the exact current signed local
record; absent state is position zero. Every later start consumes exactly one forward incarnation
before runtime. Restoration, deletion, or forking of either local record therefore refuses even
when authority remains current. Recovery may complete one prior pending startup and then consumes a
second incarnation for the new process; safe namespace burn is preferred to reuse.

Cryptographic service separation is not an operational-independence claim. The service must be
administered and persisted outside the Agent's disk/snapshot/failure domain, with rollback-resistant
storage or an ADR 0313 checkpoint actually retained in another failure domain. A same-host service,
coordinated restore of both machines, rollback of the service plus its only trusted checkpoint, or a
service launched against an intentionally stale floor is not defeated by self-signature.

Application/Ratox incarnations and signed route generations are implemented. Route enrollment
anchors the newest reviewed artifact even if its local high-water checkpoint has not yet been
materialized. Thereafter the artifact generation must be exactly committed-plus-one; arbitrary
generation skips are deliberately refused. The signed intent binds the next artifact digest and
exact local generation record before external pending CAS. A full rollback of both route files can
therefore no longer restore old network policy while the service remains current.

ADR 0308 adds the `terminal-policy` lane. Enrollment hashes the complete strictly validated profile
and binding tree without mutating it. Later profile installs, removals, binds, and unbinds remain
uncommitted until `iotox witness-terminal-policy-commit --config PATH` writes the exact signed next
checkpoint through the external transaction. Startup verifies and caches the externally committed
tree before advancing either startup incarnation. Restoring an old sudo/permissive profile tree and
its old signed checkpoint therefore refuses before RuntimeTree.

ADR 0309 adds the `command-effect` lane. Enrollment binds the existing signed command store's exact
frontier. Each incoming non-read-only command enters that frontier only after its proven principal,
authority head, exact request, and `STARTED` lifecycle are durable; the external transition must
then commit before `profile.status.set` or `update.stage` is called. Read-only work and later result
or delivery churn do not consume positions. Effect identities are not ordinarily pruned while the
lane is enabled, so restoration that erases a start changes the digest and refuses. The record cap
therefore becomes a deliberate lifetime-effect ceiling until a separately witnessed compaction
protocol exists. A crash after witness commit may still reapply only an operation already classified
as idempotent desired state: this is rollback/re-execution protection, not generic exactly-once
actuation.

ADR 0310 adds the `sync-policy` lane. Enrollment binds the complete strict namespace-policy and
stable-device-signed automation-policy tree. Startup verifies, rereads, and freezes the exact
externally committed snapshot before RuntimeTree. Agent-mediated namespace/automation mutations
write their candidate records, commit that complete candidate tree through the external transaction,
and only then replace the frozen snapshot and live registries. A failed transition leaves the disk
candidate uncommitted and unused. Quiescent offline edits require
`iotox witness-sync-policy-commit --config PATH` followed by Agent restart; a live process never
adopts a second process's policy commit. Restoring an old complete namespace/automation tree plus its
matching local checkpoint refuses. This policy lane intentionally excludes per-namespace heads,
guards, branches, workspaces, maintenance/cutoff state, object inventories, content, projections,
and current pointers.

ADR 0311 adds the `update-lifecycle` lane. Its exact head binds the canonical release-signer policy
and absent-or-complete signed lifecycle state. A device-signed intent retains the exact successor
across external pending CAS; every state transition commits before the derived `current` pointer is
changed or repaired. State absence is position one and generation `g` is position `g+1`, so the
enrolled policy is frozen within the witness epoch and later signer-policy rotation requires the
explicit replacement/re-anchor ceremony. Enrollment is:

```sh
iotox witness-update-enrollment --config /etc/iotox/agent.conf
```

ADR 0312 adds one `sync-guarded-state` lane per non-tree-v2 namespace. It requires the complete
`sync-policy` lane so an older policy tree cannot omit a namespace. The exact digest binds the
namespace ID, normalized root, engine, every quota, and the signed published, accepted, activated,
and retained `(counter, record)` roots. Each namespace receives a stable collision-separated domain
derived from the configured base domain, stable device key, and namespace ID, while retaining the
configured epoch and common lane 9.

With the Agent stopped and the complete policy tree already enrolled and externally current, enroll
each namespace exactly once:

```sh
iotox witness-sync-guarded-enrollment --config /etc/iotox/agent.conf NAMESPACE
# Transfer the printed signed record to the witness administration domain:
iotox witness-service-enroll /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity ENROLLMENT_HEX
```

Enrollment starts at position 1 even for an existing reconciled head, refuses missing or pending
local guard state, verifies the external policy lane first, and rereads that exact tree before
returning. Every namespace must be enrolled before selected startup. Live namespace add/remove is
refused; stop, commit the policy tree, enroll any new namespace, and restart instead. Removed IDs
leave service records, and reuse with another storage identity requires the later explicit
replacement/re-anchor ceremony.

The existing namespace transaction and signed two-head rollback guard serialize the entire
transition. IoTox writes the local pending successor, replaces one root, advances the external
witness to pending, commits the local guard, then finishes the external witness. Startup joins only
the exact predecessor/successor combinations before RuntimeTree; third heads, forks, wrong selectors,
missing enrollments, and outage refuse. Root-derived effects and exposure also verify the cached
authenticated semantic head while retaining the namespace transaction, preventing an in-process
reader from observing a locally landed but externally uncommitted successor.

ADR 0314 extends the same operator flag and enrollment command with a separate `tree-v2-state` lane
10 for every tree-v2 namespace. Its exact digest binds immutable storage identity, the writer-sorted
live branch frontier, and the complete signed workspace and maintenance records. A dedicated signed
two-head guard and the namespace transaction drive every branch, workspace, pin/unpin, and writer-
cutoff root change through local pending, durable root change, external pending, local commit, and
external commit. Startup reconciles these records before RuntimeTree; every root-derived effect or
exposure rechecks the cached authenticated head while retaining the transaction.

Replica heads, attempts/partials, quarantine/object inventory, health, worktree bytes,
projection-marker/current-pointer state, immutable content availability, and backup are outside the
per-namespace commitments. They do not authorize permanent purge. The cached head supplies
startup/mutation freshness, not a continuously renewed single-active lease against a concurrently
running clone.

## Boot and ceremonies

Boot order is external unlock, closure verification, exact local store/guard load and bounded
interrupted-write reconciliation, witness query/reconciliation, witnessed incarnation advance, then
runtime/network/effects. Local guard repair may finish one already durable old-or-new file transition
before the external query; it grants no effect and the external head still rejects rollback or fork.
Witness unavailability
means fail start or an explicitly designed local recovery/read-only mode with no network, effects,
or state mutation.

- Initialization is explicit and allowed only when participating state and witness domain are both
  absent.
- Backups are taken quiescently with the exact witness receipt. Older content is restored by a new
  forward mutation, not a counter reset.
- Witness-service backups include a newly exported `IOTXWCP1` checkpoint. Preserve it outside the
  service failure domain and require that exact or a later trusted version at restart; never replace
  the retained floor with an artifact emitted from an already suspect restored store.
- Witness/board replacement requires old-witness plus owner-authorized handoff to a higher witness
  epoch. Emergency re-anchor after loss visibly abandons the previous freshness proof, compares an
  independent checkpoint, and rotates reachable credentials.
- Clones receive a new device identity and witness domain. Shared-identity high availability needs a
  different protocol.
- Data-key loss is unrecoverable without separately protected owner escrow.

## Qualification status

The retained ext4-fscrypt NixOS VM provisions a policy externally, starts the real source-linked
Agent, refuses an absent/wrong key before runtime creation, re-adds the exact key, and scans the raw
unmounted block device for a plaintext canary. It asserts tmpfs runtime/no swap and rejects sibling-
prefix, configured symlink, hard-link, special-inode, and nested bind-mount escapes. Unit tests cover
default-off/ambiguous selection and plaintext refusal before runtime mutation. This establishes the
first tier on the construction kernel; it is not every filesystem/kernel or crash point.

The coordinator tests cover strict one-step records, a real concurrent two-clone exact-CAS race, normal
authority commit, whole-ledger/guard deletion, both lost-reply CAS boundaries, unapplied-intent
cleanup, recovery with either the old or new local side of an exact pending transition, missing-intent
refusal, production refusal of a same-domain backend, and replay of a matching pre-revocation
ledger/guard snapshot while the witness remains advanced. Incarnation tests add two separately
domain-hashed lanes, exact startup advancement, pending-local-new recovery, and complete signed local
rollback refusal. Route tests add enrollment, exact sequential adoption, complete pair rollback,
skipped-generation refusal, interrupted final-CAS recovery, and the actual authenticated service.
Remote-service tests add authenticated
enrollment, persistent begin/commit, wrong-key and store-tamper refusal, exclusive store ownership,
two-client election, real ledger restart, one real remote incarnation advance, and truncated-client
survival. ADR 0313 adds complete-population checkpoint signing, pinned-key/tamper refusal,
forward-progress acceptance, exact pending-floor recovery, missing-selector refusal, and selective
old-record rollback detection before bind. ADR 0360 adds CLI custody evidence for a real signed
checkpoint, including rejection of an in-service-root retained copy. ADR 0365 adds a retained
content-free receipt wrapper for that report. ADR 0366 lets the wrapper fail closed when requested
custody labels or different-device observations are absent. This proves reporting, receipt
retention, and outside-root enforcement, not independent administration or rollback-resistant
retention.

The per-namespace four-root tests bind immutable storage identity and all four roots, keep 64
derived namespace domains distinct, and exercise every root mutator. The crash matrix covers root
replacement before/after landing, both remote lost-reply boundaries, every valid local-guard/remote
join, impossible predecessor/pending states, forks, wrong selectors, early-return rollback refusal,
and a transaction-held reader blocked across external commit. The tree-v2 tests separately bind its
live branch frontier, signed workspace, and signed maintenance state; cover every supported crash
join and both lost-reply boundaries; reject old complete state, forks, wrong selectors, malformed
guards, and stale early-return decisions; and hold concurrent readers behind the transaction. ADR
0314 brings the direct registry to 817 checks.

The retained two-guest NixOS gate assigns separate disks/processes to the Agent and witness. It
enrolls authority, application, Ratox, route, terminal-policy, command-effect, sync-policy,
update-lifecycle, two per-namespace four-root records, and one tree-v2 semantic-state record,
commits bootstrap, and advances both startup namespaces. It separately restores older valid
authority, application, and Ratox state while the corresponding service lane remains current and
requires refusal before runtime. Ratox uses a real UID-1000 login profile. It advances route
generation one to two before refusing restoration of the complete old artifact and checkpoint,
replaces and commits a terminal profile before refusing the complete old sudo-capable tree, advances
the automation policy before refusing the preceding complete policy tree and checkpoint, and
publishes one single-writer namespace before refusing its complete old four-root/guard state, and
advances tree-v2 before refusing its complete older branch/workspace/maintenance/guard snapshot.
Exact-current recovery, service outage/restart, wrong-key rejection, and final recovery pass. This
proves state-separation logic on one hypervisor, not an independent physical or administrative
deployment.

The remaining campaign must
exhaustively interrupt after every local fsync and witness request/response,
including commit with a lost reply; replay, fork, delete, and restore each artifact and the entire VM
snapshot while the witness remains advanced; race two clones; exhaust counters; and lose the witness
at boot and mid-mutation. End-to-end gates revoke authority then restore pre-revoke disk, witness a
command before effect then restore, replay an old sudo binding, and replay sync cutoff/GC state. Each
must refuse. A second same-host Sandwurm VM proves protocol logic but not independent failure domain.

## Nonclaims

Filesystem encryption does not hide all metadata or protect a powered-on unlocked kernel, root,
swap/hibernation, key-using process, or malicious hardware. It does not prove authorization,
freshness, secure deletion, or backup. A witness does not prove confidentiality, content
correctness, availability, or independence when it shares disk/admin/failure domains with the
Agent. These limitations remain visible in diagnostics and deployment documentation.
The per-namespace lanes do not make content complete or correct, certify a backup, cover the broader
sync state closure, make deletion safe, or prove operational independence.
