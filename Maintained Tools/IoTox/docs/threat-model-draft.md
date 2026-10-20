# IoTox threat model draft — rev0051

This is a working security model, not an audit or proof. It describes the current one-binary ratox
successor, RecallRoot, stable identity, signed authority, durable commands, Tox transport, local
control, manual/default-off Ratox plus self-mode/default-on Ratox terminal selection,
construction-enabled strict routed privacy, and bounded immutable and multiwriter synchronization.
Significant architectural additions must update
this document through `docs/architectural-change-intake.md` whenever they add a trust boundary,
durable state family, remote input, terminal/process authority, support artifact, or route behavior.

## 1. Security objectives

Protect:

```text
owner authority derived from the permanent phrase
stable device signing identity
current Tox route identity and savedata
signed authorization history and active capabilities
durable command identity, admission, result, and replay state
synchronization namespace policy, accepted HEAD state, content store, and activation state
private local control socket and runtime files
Ratox session/authority/replay integrity and local terminal process boundary
self-machine membership, aliases, route inventory, and minimum accepted generations
public person delivery cards and contact freshness floors
person message envelopes, duplicate-suppression state, and future group transcripts
message/file contents and metadata
future settings, actuators, firmware, and owner data
route policy, especially no native leak from Tor/I2P selection
```

Preserve:

```text
no vendor reassignment authority
friendship is not authorization
from-memory owner re-entry
self-machine join by owner-held IoTox authority, not Tox multidevice
person identity by signed IoTox person envelopes, not by a Tox route or group peer alone
one logical command despite transport retry/reconnect
no externally visible receipt before durable local admission
no physical effect without explicit operation policy
```

## 2. Adversaries

Assume possible:

- unauthenticated Internet peers sending malformed Tox traffic;
- Tox friends that are not authorized IoTox principals;
- authorized principals exceeding or retaining intended capability;
- a peer replaying, duplicating, reordering, delaying, or conflicting application frames;
- a local unprivileged process probing paths and sockets;
- an equal-privilege local process reading or modifying owner-readable state;
- theft of a phone, controller, recovery print, device, or filesystem image;
- offline guessing of the permanent phrase;
- rollback to old valid signed state;
- a peer offering forked, rollback, oversized, corrupt, or wrong-namespace synchronization state;
- disk full, torn write, power loss, clock rollback, and process crash;
- a malicious or compromised bootstrap/relay operator;
- a malicious runtime-loaded provider library;
- defects in c-toxcore, libsodium, Argon2, the compiler, or IoTox;
- a vendor/operator attempting to turn infrastructure or update keys into ownership authority.

Physical invasive attacks and a fully compromised kernel can defeat current file/IPC controls.
Hardware-backed designs remain future target-specific work.

## 3. Trust boundaries

```text
human memory/printed phrase
    crosses only into short-lived local recall client code

local operator -> private SOCK_SEQPACKET
    same-user admission, bounded structured packets

runtime tree
    private projection, not constitutional state

agent business logic -> toxcore owner thread
    bounded internal commands and normalized callbacks

IoTox protocol -> Tox lossless custom packet
    encrypted/authenticated transport plus independent application checks

persistent files
    Unix ownership/mode, atomic replacement, signatures where defined

synchronization namespace store
    local policy only; remote names, HEADs, manifests, and objects grant no effect without
    authority-ledger capability, local quota, and activation checks

Ratox network frame -> Agent coordinator
    exact packet ID, current confirmed epoch, bilateral feature, authenticated principal, exact-head
    terminal authority, attachment fencing, bounded replay, and retained response admission

local terminal policy -> resolved immutable profile
    owner-only canonical tree; no peer-selected argv, executable, cwd, or environment

self-mode selection -> Ratox roles
    host/controller default-on only because the operator selected --mode self; profile binding,
    interactive.terminal authority, and host sudo policy remain separate gates

self-swarm roster -> self-machine membership
    owner-signed membership above Tox; alias, stable principal, route key, generation, and
    retirement are verified before plan/apply; no Tox friendship, savedata key, roster row, or alias
    alone grants shell authority

person delivery card -> public reachability for one person key
    owner-signed card publishes active Tox route keys without aliases or authority principals;
    route keys are delivery addresses, not person identity or authority

person message envelope -> speaker/recipient identity
    sender person signature verifies the human/person claim independent of which Tox route,
    file lane, group, or future relay carried the bytes

PTY parent -> hidden child -> fixed executable
    bounded manifest, already-open descriptors, readiness plus close-on-exec EOF; the child has no
    direct protocol parser or network callback

bootstrap/relay infrastructure
    reachability only; no application authority
```

## 4. Permanent RecallRoot

The permanent phrase is intentionally reusable. A fixed Argon2id contract allows the same owner
principal to be reconstructed from memory or print. This also allows offline guessing when an
attacker obtains sufficient verifier/context material.

Required controls:

```text
generated phrase with mandated entropy
pinned word list and normalization
fixed Argon2id version/parameters and domain separation
known-answer vectors
no human-chosen weak phrase described as equivalent
no phrase/root/owner secret sent to the daemon
no vendor escrow or override
```

Threats:

- photographed or copied recovery print;
- weak phrase chosen despite warnings;
- parameter downgrade or implementation drift;
- side-channel or swap/core-dump exposure in the local client;
- phishing the phrase into a vendor service;
- compromise of all devices while the phrase remains unchanged.

ADR 0054 now defines phrase-compromise epoch and planned ownership succession while a current owner
secret remains available. Open requirements include remote route discovery, rollback witnesses,
destructive physical reclaim, and how a device whose local ledger is gone recognizes any prior
owner without a vendor master key.

## 5. Identity separation

### Stable device identity

The stable Ed25519 seed is currently stored in a private local file. It signs authority/command
state and proves the device principal over a confirmed Tox transcript.

Threats:

- filesystem theft permits device impersonation;
- plaintext seed exposure to equal-privilege local processes;
- missing identity beside existing signed state;
- replacement identity paired with a wiped ledger;
- future route identities accidentally becoming the stable identity.

Current mitigations:

```text
private regular file
atomic creation
public key re-derived from seed
existing signed state plus missing/foreign identity fails closed
Tox endpoint key remains a separate class
```

Hardware keystore, secure element, measured boot, and migration are target-specific future work.

### Tox route identity

Tox savedata supplies the current transport address and friend state. Compromise permits Tox-level
impersonation and metadata exposure. It must not alone grant IoTox application capabilities.
When a signed multi-route inventory is configured, the primary savedata public key must equal its
signed coordinator key before any network activity; auxiliary workers inherit the same requirement
for their member key. Peer-visible route membership additionally requires a stable-device signature
over the exact member policy, route-set generation, and locally derived confirmed-session transcript
digest. This prevents path substitution and cross-session replay, but does not protect stolen route
private keys or make a route an authority principal.
The bounded v1 wire exchange carries the complete signed route set with the transcript binding, but
it does not trust the principal or generation named by those bytes. The receiver supplies an
expected remote stable principal and minimum generation from a separate authority-authenticated
primary session. Self-signed foreign inventories and older valid inventories fail closed; bounded
process-local state rejects rollback, forks, stale worker incarnations, and same-epoch conflicts.
The live Agent now wires this registry into reciprocal worker admission and coordinator lifecycle.

ADR 0198 also recognizes what those checks do not protect: the sender transmits the complete v1
roster on the auxiliary friendship before reciprocal primary authority is proved there. V1 remains
qualified for same-context construction only. Mixed native/privacy routing requires private
inventory exchange over the already authorized primary session followed by a member-scoped
auxiliary proof. The ADR 0199 construction codec binds that proof to the complete inventory digest,
primary authority friend/epoch/transcript, and exact auxiliary transcript. ADR 0200 supplies bounded
delivery, generation/fork high-water, worker handoff, member-only exchange, and immediate readiness
withdrawal behind an explicit default-off Agent gate. ADR 0201 adds exact local context selection,
ordering-safe early-proof adoption, and genuine native/generic-SOCKS two-guest qualification without
widening the actual-Tor claim. ADR 0202 binds optional replacement bootstrap and relay catalogs to
the exact auxiliary key and validates them before construction; they remain local reachability
policy and cannot alter signed membership or application authority.
Only reciprocal proof advances readiness; trust loss clears work and closes readiness. The first
process-local synchronization scheduler admits immutable kind/digest/size records only to an exact
ready bulk-worker incarnation, reserves coordinator capacity, and retains a bounded attempt fence so
late completion cannot target a replacement. It accepts prior atomic capacity withdrawal only for
the exact now-closed zero-work incarnation. Worker receive admission now rechecks the exact
reciprocally authenticated bulk incarnation at the network/filesystem effect boundary.
Ordinary single-route feature advertisement remains disabled.
Auxiliary workers are independent transport owners inside the same process, not independent agents:
they receive no authority ledger, synchronization root, or effect executor. Initial savedata with
zero or multiple friends fails closed to avoid attaching transcript evidence to an implicit peer.
In-process supervision improves transport-domain separation but provides no process-fault isolation.

### Multi-route synchronization attempts

Threats include treating a reused toxcore file number as stable identity, duplicate assignment,
completion after reassignment, digest/size substitution, protected-route starvation, accounting
leakage, and unbounded replay state. The scheduler instead keys objects above transport, permits one
current attempt, retains bounded tombstones, verifies exact caller observations before commit,
reserves only ready bulk capacity, and fails closed at configured bounds. Explicit close fences live
work and releases reservations.

An attempt now derives one path below the private namespace staging directory. The commit boundary
accepts only a singly linked owner mode-0600 regular file, verifies exact size and digest, and uses the
existing exclusive double-checking object commit under the namespace transaction. Fenced discard
refuses unexpected shapes rather than following or deleting them. The namespace-scoped scheduler
reserves the full object size across every route until fence or commit, preventing concurrent attempts
from independently consuming
the same staging allowance. This remains process-local accounting rather than a filesystem quota; a
hostile or mistaken integration could still bypass the proof or leave disk state across a crash.
Scheduler attempts remain process-local; the signed journal below reconstructs their storage outcome,
and the default-off Gate 3 qualification now proves exact mid-object loss, stale-result rejection,
fresh whole-object reassignment, and one-budget same-savedata recovery in two genuine guests on both
native carrier classes. This does not authorize byte-prefix reuse, adaptive carrier choice, or
production policy replacement by itself. ADR 0171 separately qualifies the first bounded adaptive
admission-topology comparison; byte-prefix reuse and production policy replacement remain later
gates.

The optional adaptive selector does not accept remote throughput claims. It consumes only the local
coordinator's exact admitted work, signed work ceiling, restart count, stable key, and currently
authenticated incarnation. Selection is permitted only before admission or after fencing, so score
changes cannot move live bytes or become authority. Fixed stable-key choice remains the default.
The first genuine two-guest comparison proves only that this local accounting changes bounded
placement as designed on direct UDP and forced TCP. ADR 0176 separately qualifies both exact
corresponding auxiliary readiness orders with a fail-closed post-authentication hold. Neither result
establishes throughput, proportional fairness, random startup/fault delay stability, startup under
fault, scheduler-phase resource cost, cancellation tails, or physical route/relay diversity. ADR
0171 counterbalances fixed-first and adaptive-first policy order.

Cancellation is terminal authority state, not a hint to the route scheduler. ADR 0177 stops the
retained exact carrier only after cancellation cleanup has settled and observes one subsequent loss,
zero reassignment, and one capacity recovery on UDP and TCP. A late route failure therefore cannot
resurrect immutable-object work in this deterministic order. ADR 0178 drives cancellation and exact
worker stop from one armed progress edge; both carrier classes preserve terminal cancellation with
zero reassignment, expose typed cleanup unavailability, settle it by one nonrepeating exact retry,
and recover route capacity. Multiple affected pulls on one carrier remained separate qualification
work at that boundary. ADR 0179 also forces loss-first from the same arm edge on UDP and TCP,
requiring exactly one fresh assignment and cancellation of that replacement without waiting for
reassignment in the test controller. ADR 0180 then qualifies four simultaneously affected jobs from
an eight-job fixed population: complete remaining-work admission, exact affected-job fencing,
bounded pre-offer unavailable retry, stale terminal rejection, and recovery only after every
remembered job is terminal. Random timing, startup under fault, larger populations, and unbounded
schedules remain open.
ADR 0181 then creates two additional jobs only after loss and both existing-job reassignments are
visible. Both must enter through the sole ready survivor before recovery, proving degraded admission
does not trust a stale route view or close merely because capacity changed. The same campaign makes
shutdown carrier-first: synchronous carrier service quiesces while the ordered required-event
consumer remains alive, preventing a clean-stop owner/event wait cycle. Daemon cold startup with a
route absent, randomized timing, larger populations, and unbounded schedules remain open. ADR 0182
uses a clean same-state Agent restart plus an explicit post-authentication hold to prove that one
ready route can admit two large jobs and that a newly ready route cannot move either live
assignment. The hold does not simulate physical path isolation, independent relay failure, or a
machine/guest cold boot; treating it as those stronger conditions would be an evidence-boundary
error.

Auxiliary file-transfer state is isolated per worker and bounded by signed route work capacity. The
parent can address it only by exact route key and worker incarnation, and receive/cancel fails unless
that bulk worker has a confirmed application session plus reciprocal binding. Protected and stale
routes cannot acquire a destination; their offers are explicitly cancelled, and primary-trust loss
cancels retained transfers before revocation. Each admitted receive reserves actual bounded terminal
storage before transport resume. The exact route/worker/file outcome is delivered once without
eviction; terminal-capacity exhaustion refuses a new receive before effect. The namespace bridge
still treats completion only as a prompt to verify the exact staged size and digest, commit the
immutable object, and then complete the retained attempt. Failure, cancellation, corrupt bytes,
metadata conflict, and replay discard or fence without retargeting a replacement. Scheduler and
binding records remain process-local, so Agent recovery invocation and multi-namespace dispatch are
still explicit integration boundaries.

The signed attempt journal now removes the first crash ambiguity. It burns an ID before assignment
and records the immutable object plus exact route incarnation before receive resume. Restart does not
trust or retain a file number: final bytes are reverified, complete staging may be committed, and
absent or safely removable corrupt staging is fenced. Unexpected shapes and uncertain I/O retain the
active record and fail startup. Terminal events remain in the process-local bridge across retryable
journal failure. The journal signature and previous digest do not prevent complete older-record
replay; it is not a synchronization root and cannot authorize HEAD, activation, retention, or GC.

The v1 wire mapping no longer trusts a filename or file number to join these layers. An object request
names the namespace, exact complete signed-HEAD digest, object kind, and a nonzero 32-byte transfer
token. The publisher supplies that token as the c-toxcore FileId and rejects provider readback
substitution; the subscriber matches the paused offer by FileId and derives size/digest locally from
the verified HEAD. Auxiliary outgoing attempts reserve terminal capacity before effect just like
receives. Token disclosure is harmless and an `offered` result is not completion. The codec grants no
authority; only an explicitly sync-enabled Agent advertises it after strict service construction.
Publisher replay is an epoch-scoped bounded recent window (ADR 0282), subscriber retries retain exact unanswered frames, and queued Agent
effects reconstruct current session/authority context. Multi-source reassignment, partial ranges,
remote cancellation, and broader genuine-provider fault qualification remain open. Explicit local
pull withdrawal now has direct-UDP and forced-TCP Sandwurm evidence after positive provider progress;
that evidence does not claim remote CANCEL acknowledgement.

### Reusable genuine-test identities

The founding-host genuine harness keeps a dedicated test-only Tox/device pair so ordinary runs can
observe stable peers. Those private files have the same impersonation risk as any other identity and
must never be copied from a live profile, committed, packaged, or shared. The harness confines them
to an ignored owner-only provider-version cache, permits only the four baseline key files, copies
them into disposable state, rejects pre-existing friendship/request state, serializes their use,
and verifies that a run did not mutate the cache. Fresh ledgers and command stores prevent the
harness's intentional revocations and ownership transitions from becoming persistent authority.
An explicit fresh-key gate continues to test first creation. See ADR 0056.

## 6. Authority ledger

Threats and current treatment:

### Forged or malformed records

Canonical fixed-size records, stable-device binding, Ed25519 signatures, strict reserved bytes,
known actions/roles/capabilities, and deterministic replay fail closed.

### Excess delegation

The issuer must be active, hold `manage.principals`, stay within role ceilings, and cannot grant
capabilities it does not hold.

### Owner removal

Only owners can create/revoke owners. An active owner cannot be overwritten into a weaker role,
and the last active owner cannot be revoked by ordinary ledger mutation.

### Replay, reorder, truncation

Records carry sequence/history commitments and deterministic replay checks. The signed ledger is
atomically replaced. A separate private `IOTOXAG2` guard retains committed and pending exact heads,
so replay can distinguish the two expected crash-interrupted replace states from an unexplained
third head.

### Coordinated snapshot rollback

Rolling back, deleting, or forking only the ledger is detected relative to the retained guard. A
same-privilege attacker who restores both ledger and guard as one mutually consistent older pair can
still revive an older principal or capability. Hardware monotonic state, external owner checkpoints,
replicated heads, or append-only anchors need a separate design.

### Time

Current authorization is sequence/epoch based, not trusted-clock based. Temporary grants and expiry
are not mature.

## 7. Transcript-bound authority

Tox friendship and an online connection are insufficient. IoTox freezes both HELLOs and both
confirmations, derives one transcript, and signs fresh directional challenges/proofs.

Threats:

```text
HELLO downgrade or disagreement
confirmation replay across online epochs
proof replay to another peer or transcript
claiming another device's principal
assuming our proof enqueue means peer verification
accepting application traffic before mutual confirmation
```

Current controls bind proof to peer keys, transcript digest, challenge, verifier device,
ownership epoch, and current online epoch. Authority remains directional. `proof-sent` is only local
queue acceptance; no remote proof acknowledgement is claimed.

### Ownership-epoch transition

A current owner cannot unilaterally install an unproved successor and complete a cut. The current
owner first signs a distinct successor-owner nomination; the immediately nominated successor must
then prove possession and sign the next-epoch record. The transition cross-links the old tail,
advances the epoch exactly once, resets sequence to one, and removes all old-epoch principals from
live authority. Exact replay is idempotent.

This limits future use after a completed phrase-compromise response; it does not undo prior effects
or stop another holder of the compromised current phrase from racing before the cut. Restoring an
older complete valid ledger remains possible without a monotonic hardware or external witness. If
no current owner secret survives, there is no nondestructive recovery and no vendor reassignment
key.

## 8. Durable command identity and replay

### Command key collision/reuse

The receiver keys by sender Tox public key, persistent sender epoch, and message id. Direction is
local. Exact canonical duplicate is replayed; changed bytes under the same key are conflict.

Random nonzero IDs and sender epochs reduce accidental collision but are not a formal uniqueness
proof. Generation exhaustion and RNG failure fail closed.

### Acknowledge-before-persist

Forbidden. Incoming request and exact `RECEIVED` receipt are committed before the receipt is sent.
Outgoing request bytes are committed before the first send.

### Execute-before-persist

Forbidden for the current engine. Authority admission and `STARTED` are committed before
`device.describe` execution; terminal bytes are committed before result send.

### Lost acknowledgement/result

The sender retains exact request identity. The receiver retains exact receipt/result. Reconnect,
restart, and exact duplicate delivery replay the same artifacts instead of inventing another
logical operation.

### Result substitution

Receipt/result correlation must match request message id and sender epoch. A second non-identical
artifact for the same correlation is conflict. Successful device description principal must match
the principal established by authority challenge.

### Local timeout

A timed-out local call does not prove the operation was cancelled. Once durable admission is
possible, operator APIs must return/retain the durable key and expose later status. Physical effects
cannot use timeout as cancellation.

### Expiry and clock rollback

Absolute expiry exists in the frame, but device wall clock may be wrong or move backward. The v3
store holds expiring work unless the operator explicitly trusts wall time and the current value is
within the rollback tolerance of signed history. Trusted startup checkpoints that value, while a
steady-clock anchor detects backward movement during the live process. This policy is sufficient
for the current harmless reads; physical commands still require stronger time/freshness evidence
and a target-specific restart model.

## 9. Command-store attacks

### Tamper and foreign identity

The v3 snapshot is signed by the stable device identity. Invalid signature, foreign public key,
malformed size/count, duplicate locator, invalid canonical frame, or illegal transition fails
closed. A v2 snapshot is verified and must be atomically rewritten as v3 before startup continues.

### Symlink and permissions

Reads use no-follow behavior and require a private regular file owned by the current user. Atomic
replacement creates a private temporary file. A hostile parent directory or compromised user can
still interfere.

### Rollback

An old valid signed store remains valid. This can erase evidence, resurrect an unfinished command,
or permit a sender id to appear unused. No physical effect may rely on the store until rollback
consequences and an external monotonic anchor are settled.

### Confidentiality

The store is plaintext. Peer public keys, operation type, timestamps, authority head, and canonical
payloads are visible to a local reader. Encryption-at-rest and key recovery policy are unresolved.

### Disk exhaustion and DoS

The store is bounded. Only oldest fully delivered terminal records are pruned; an incoming terminal
result awaiting local queue acceptance remains unfinished. Total unfinished records,
per-peer/direction records, and per-peer/direction canonical bytes have explicit refusal limits;
priority affects scheduling but never bypasses quota. Authentication-aware rate limits and operator
alerts remain needed for hostile but authorized clients.

### Write amplification and flash wear

Every transition rewrites/fsyncs the complete snapshot. Power-cut correctness is favored over
performance in rev0016. High-rate or flash-constrained targets need append/checkpoint design and
fault-injection measurements.

## 10. Local IPC and runtime tree

The private control socket checks peer credentials, bounds one complete packet, uses request IDs,
and returns structured status. It is not a privilege boundary against another process with the same
user identity.

The runtime tree is private and atomically/transactionally projected, but deliberately not
`fsync`-durable. Consumers must not treat observation of one file as an atomic transaction with a
control response unless the contract explicitly says so. The tree is replaceable and cannot grant
authority.

rev0016 retains the ordinary friendship lifecycle with one required root outgoing-request lane
beside incoming decisions and established-peer removal. Threats specific to that lifecycle include:

```text
friend number reused after deletion and a delayed numeric mutation deletes the wrong peer
malformed, case-changed, padded, partial, or wrong-lane destructive token inferred as intent
short, oversized, nonhex, wrong-separator, or empty outgoing request inferred as an invitation
multiple FIFO writers interleave one request or a later writer completes an abandoned fragment
root request FIFO removed or replaced while status continues to claim readiness
complete address confused with public key, or IoTox reimplements checksum/nospam incorrectly
malformed input represented by a fabricated all-zero peer and later mistaken for a real identity
local tox_friend_add admission described as remote receipt or acceptance
request projection replaced between operator observation and decision
accepting a Tox friend confused with granting IoTox authority
removing a Tox friend confused with revoking a stable principal
local rejection or deletion described as remote acknowledgement
live request inbox or bounded friend-events journal mistaken for durable audit
root/public-key FIFO replaced by symlink, regular file, foreign owner, or permissive mode
request-message bytes injected into terminal, log, shell, path, or parser
repeated requests used for projection churn or bounded-resource denial
```

Signed introduction adds a separate artifact threat set:

```text
self-signed unknown inviter mistaken for a trusted human/device
invitation address replaced independently of its stable identity signature
expired, far-future, padded, oversized, or unknown-capability artifact accepted
suggested alias treated as remote authority to replace an existing binding
requested capabilities installed as grants or synchronization membership
replayed acceptance creates a different friend, alias, or authority result
friendship succeeds, alias persistence fails, and the partial effect is hidden
wall-clock rollback extends transport-level invitation acceptance
accepted artifact mistaken for durable endpoint-migration authority
```

ADR 0293 uses a fixed canonical signed record, separate signature/artifact hash domains, a random
nonce, 60-second..30-day lifetime, closed capability mask, canonical alias grammar, and explicit
out-of-band inviter pin. Inspect labels trust unestablished; dry import mutates nothing. Acceptance
targets only the signed Tox key, reuses an exact existing friend, refuses alias collisions, reports
partial alias failure, and always grants zero authority. Bad clocks remain a stated transport-level
replay limitation because workstream 8, not friendship, owns rollback witnesses.

Controls:

- the root `request` record has one exact 76-hex + TAB + 1..921-byte grammar and no default message;
- the complete 38-byte address reaches c-toxcore, which remains authoritative for checksum, own-key,
  duplicate, and nospam behavior;
- root and public-key lanes share owner/mode/type/no-follow/opened-inode/`PIPE_BUF` checks, bounded
  buffering, partial-record expiry, and safe replacement;
- startup and live readiness require every promised root lane, so removing `request` cannot remain
  silently green;
- producers are required to make one complete write including LF, at most the opened FIFO's actual
  `PIPE_BUF`;
- malformed records use explicit keyless evidence when no key prefix is trustworthy and never invent
  an all-zero identity;
- request and peer directories are named by canonical uppercase 32-byte public-key hex;
- accept/reject/remove bodies are exact lowercase tokens plus one LF record delimiter;
- all outgoing/incoming/destructive friendship methods are serialized in the Agent;
- removal runs public-key lookup and delete in one toxcore owner-thread command;
- the required removal event carries the key captured before deletion;
- request and peer projections use private transactional/no-follow publication;
- friendship events explicitly state that the signed authorization ledger is unchanged;
- request-send success is described as local provider admission only;
- rejection removes only IoTox's live record, and deletion makes no remote-notification claim;
- untrusted request text is byte-counted and escaped before human journal rendering.

The established-peer data/control lanes retain these additional threats:

```text
regular-file or symlink substitution
foreign-owner or permissive-mode path
writer interleaving and ambiguous record boundaries
abandoned partial record joined to a later writer
oversized or policy-invalid input
FIFO saturation and monitor starvation
confusing write success with later evidence
confusing human text with authorized machine intent
leaking untrusted text bytes into unsafe terminal/log consumers
scan or startup races while peer projections change
remote filename confused with a local destination
relative path, NUL, delimiter, or shell interpretation confusion
source path replaced or mutated after admission
destination symlink/race or existing-file clobber
stale/reused friend file number controls another live transfer
local resume incorrectly erases a peer-owned pause
successful control enqueue confused with peer acknowledgement
live transfer projection confused with restart-durable state
transferred content treated as trusted or executable
```

The implementation uses type/owner/mode checks before and after no-follow open, compares opened
inodes, bounds records, queries `_PC_PIPE_BUF` for the full maximum record, expires inactive
fragments, and keeps map mutation on the FIFO worker. Per-lane statistics are allocated at
construction and remain bounds-checked because the event thread may observe service state before
`start()` completes. Directory-level and lane-level scan errors have distinct keys.

The root outgoing lane uses the complete Tox address because `tox_friend_add` consumes nospam and
checksum as well as the long-term public key. After local parsing, the ordinary FIFO and structured
control operation converge on one Agent method and one owner-thread provider call. The full address
is not persisted into the public-key directory, and provider admission is not described as remote
observation. A compromised same-user process can still submit a syntactically valid request; the
runtime tree is not a privilege boundary against that process.

Incoming and destructive lifecycle lanes use public-key directory names and exact word records.
Acceptance requires the same key to remain in IoTox's live request inbox. Established removal sends
the key through local control and performs `tox_friend_by_public_key` plus `tox_friend_delete` in one
owner-thread operation; the numeric handle is returned only as evidence. This prevents a queued key
decision from landing on a later friend that reused a provider slot. It does not protect against a
compromised same-user process deliberately choosing the wrong key.

c-toxcore has no persistent pending-request object and no remote rejection call. `reject` therefore
withdraws the IoTox callback projection only. `tox_friend_delete` is local and silent. Neither fact
changes the signed authorization ledger. A stale authorized principal may remain authorized after
its current Tox route is removed; that is deliberate separation, not implied revocation. Operators
must use an explicit ledger mutation when revocation is intended.

`friend-events` is private, bounded, rotating local evidence. It may be lost, altered by the same
user, or disappear with the runtime tree. It cannot prove remote observation, persistent provider
state, or authority change. High-rate request handling still needs quotas, suppression, and durable
policy before deployment on an exposed address.

The file lanes carry one bounded path/control record, never payload bytes. Path decoding rejects NUL
and relative paths; FIFO framing cannot represent LF, and the first TAB is reserved by receive/control
grammars. No shell, quoting, glob, variable expansion, or remote destination selection occurs.
Source descriptors are opened with no-follow policy and retained; identity, size, and modification
facts are checked while serving exact chunks. Receive staging occurs in the destination directory,
requires an owned real parent and absent target, and publishes without replacement only after exact
completion and synchronization. A remote filename is presentation data only.

Friend file numbers are opaque, friend-scoped, live handles and may be reused after terminal cleanup.
`local_paused` and `peer_paused` are independent; local RESUME cannot erase peer pause. Disconnect and
process restart discard current provider transfer state. `file-events` and `files/` are disposable
evidence, while safe destination appearance is receive-completion truth. Transferred content gains no
execution or import authority.

Sync restart-prefix retention is not provider-transfer restoration. ADR 0234 preserves only a strict
positive private inode bound to an exact object digest/size in stable-device-signed local truth. A
fresh authorized signed HEAD and fresh job/FileId/attempt must claim it, and the complete digest is
reverified before commit. Unmatched retained prefixes are pruned; old routes and handles have no
authority.

The `command` lane accepts only printable operation records and synchronously enters the signed
durable command path. The `message` and `action` lanes preserve every non-LF byte at the local
adapter boundary and enter the live c-toxcore text path. Interoperable human text is UTF-8; byte
preservation is not permission to treat native Tox text as a machine-binary channel. The lanes
perform no command parsing, capability decision, hidden retry, or durable spooling. Same-user
malware can submit either local path just as it can use the structured socket; remote machine
effects still require the independent application authority path.

A successful FIFO write proves only kernel acceptance. `message-events` can prove local framing and
typed toxcore acceptance/rejection; `messages` can later show a Tox read receipt. A friend
disconnect destroys upstream pending-receipt state, so IoTox clears its local correlation and emits
a diagnostic rather than promising a later receipt. Neither proves a machine effect.
`command-events` can name a signed durable key, but remains unsigned, rotating observation. Loss or
alteration of runtime journals does not change authoritative stores.

Human-text and friend-request bytes are escaped before journal rendering. Consumers must still
treat journal bodies as untrusted data and must not unescape into a terminal, shell, path, or parser
without their own bounds and policy. `friend-events` is mode 0600 and rotating but is not signed,
rollback-resistant, or synchronously durable. Its process-local sequence may repeat after restart.

## 11. Queues, callbacks, and shutdown

One thread serializes each `Tox*`. Required semantic events apply backpressure; observational event
loss is counted. Bounded local queues prevent unbounded memory growth.

Threats:

- callback reentrancy and lock ordering;
- queue starvation by one peer;
- shutdown while work is admitted;
- a caller timing out while owner-thread work later executes;
- event evidence dropped under pressure;
- full-disk failure after an operation is prepared.

Physical effects require a durable scheduler with explicit queued/running/cancelled/indeterminate
states rather than relying on the current generic control wait.

## 12. Tox and dependency risk

c-toxcore is network-facing native C. The current pin, 0.2.23, fixes a remotely triggerable stack
buffer overflow affecting relevant earlier versions. IoTox must retain rapid dependency update and
reproducible build capability.

Current controls:

```text
one narrow provider table
one serialized owner thread
official-header requirement for linked source provider
strict owned frame/record decoders
sanitizer, race, and fuzz lanes
application authority independent of Tox friendship
pinned sources and checksums
```

Not proven:

```text
cryptographic correctness of Tox
absence of other memory-safety defects
real-network compatibility in this container
sandbox containment of toxcore
formal protocol audit
```

A runtime-loaded provider path executes arbitrary native code and is a research/developer feature.
A product should ship a known source-linked dependency set.

The release surface carries a deterministic SPDX 2.3 source-component SBOM whose exact package set
and executable digest are verified during standalone and Nix construction (ADR 0150). This reduces
undeclared embedded-component and artifact-substitution risk. It does not inventory the deployment
image's libc, C++ runtime, kernel, or service packages, and therefore cannot replace an image-level
SBOM, vulnerability scan, VEX decision, or independent rebuild.

The frozen Ratox terminal protocol has a narrower focused service analysis in
`security-ratox-v1.md`. rev0018 permits only explicit default-off construction advertisement after
secure local activation; production/default advertisement remains closed. Authority migration,
attachment fencing, whole-frame input commitment, the PTY process boundary, content-free audit,
bounded availability, client behavior, restart policy, confinement, and two-host qualification must
remain independently evidenced.

## 13. Bootstrap and relay infrastructure

Bootstrap and relay operators can observe timing/network metadata and influence reachability. They
must not read application plaintext or grant IoTox authority. Malicious infrastructure can still
delay, partition, fingerprint, or deny service.

Contributing IoTox-operated or owner-operated Tox infrastructure improves commons capacity but
must not create an account dependency or reassignment channel.

## 14. Tor and I2P route privacy

Tox/native normally seeks direct connectivity and is not anonymous. Rev0045 construction-enables
one explicit `Tox/Tor` configuration. `Tox/I2P` now uses an equivalent strict explicit boundary
qualified on the two-guest VM substrate (ADR 0253).

Threats include:

```text
native UDP or DNS leak
silent native fallback
identity linkability across routes
proxy bypass by bootstrap/relay configuration
long-lived route fingerprints
multiple Tox instances diverging in state
false UI claim that proxy option equals route containment
```

`Tox/Tor` requires one numeric SOCKS5 endpoint plus nonempty explicit numeric bootstrap and relay
records. It suppresses compiled catalogs and forces UDP, discovery, announcements, hole punching,
and native DNS off. Source-linked Linux socket ownership proves no IoTox UDP or direct relay socket,
plus proxy-loss offline state and same-endpoint recovery, in the bounded local construction gate.
The two-guest Sandwurm gate additionally proves TAP containment, confirmed application traffic,
proxy-loss offline state, epoch-advancing recovery, and fresh restored text. The lab forwarder is
not Tor and cannot prove circuit use or anonymity.

Native, Tor, and future I2P contexts now select independent random savedata identities by default.
Their route-scoped filenames share the directory-scoped stable device identity and authority state,
not the observable Tox key. Explicit state-path reuse remains a linkability choice. There is no
public stable-principal route lookup, deterministic route-key derivation, or claim that separate
identifiers defeat timing, traffic-shape, peer, relay, or host correlation.

Private route-binding v2 now qualifies the identifier-disclosure boundary in two guests. The full
signed roster crosses only an authority-authenticated native primary; a native auxiliary and strict
generic-SOCKS auxiliary exchange member-only proofs. Exact-key local network overrides are validated
before any worker starts. A member proof received before the reciprocal primary inventory remains
inert and is accepted only if it later verifies against that exact context; stale proof bytes are
discarded without authority. TAP evidence permits native UDP and related ICMP destinations but
requires all TCP to terminate at configured host-local proxy/relay endpoints. This joins several
independent facts; it does not make packet capture process attribution or the lab forwarder Tor
(ADR 0201).

The separate operator-Tor gate binds Tor 0.4.8.11 and its normalized loopback configuration,
authenticates its control plane, correlates initial and recovered configured-target streams from new
Agent source ports to distinct three-hop `CONFLUX_LINKED` application circuits, and proves from
Linux socket ownership that only Tor owns public TCP
while IoTox owns neither UDP nor a direct-relay route. Tor death, authoritative offline, a 30-sample
held outage, and exact-endpoint recovery establish bounded no-fallback behavior. This closes the
single-host public-route construction threat, not traffic correlation, malicious exits/relays,
censorship, multi-relay reliability, or anonymity. Separate accepted two-IoTox compact proofs now
bind exact Tor auxiliary readiness, exact sync-carrier attribution, immutable-object reassignment
across Tor process loss, and detached-terminal explicit resume after primary Tor process loss.
Those are one-host bounded application behaviors, not diversity or a general reliability claim.
ADR 0207 accepts compact proof `pair.k8o54n2v` for a 120-sample continuous-process Ratox cell that
deliberately replaces exact client and device application circuits. Live attempts showed either Tox TCP offline or no terminal
error; post-replacement PONG must preserve epoch/generation, while only provider offline may detach
and only explicit higher-epoch resume may advance generation. Session/incarnation/PTY/bytes remain
exact, and Tor observations themselves still cannot mutate carrier or session truth.
The accepted run exercises both lawful branches while all processes remain continuous. Longer
relay/time diversity remains required regardless. Direct Tor/I2P transports are separate future
architectures.

ADR 0208 repeats the same gate through a second public record. Both Tor streams reopen while both
Ratox checkpoints stay same-epoch/generation continuous; ADR 0207's device reopening instead
required explicit resume. A compromised or merely misleading route observer therefore cannot use a
Tor stream-transition label to force either detach or continuity. Two sequential records still do
not establish exit/time independence.

ADR 0209 constructs a distinct local interposer that can truthfully keep its listener and TCP
streams open while withholding bytes. This models a misleading or failed local route boundary
without granting the injector any product authority. Accepted compact proof `pair.vx6z0csh` closes
the bounded live threat cell: listener reachability and a fresh exact-target SOCKS CONNECT coexist
with heartbeat loss and later authoritative offline; only c-toxcore detaches the retained PTY, and
only a higher authenticated epoch plus explicit exact-session resume advances generation. Tor,
interposer, and IoTox processes remain unchanged. The result does not generalize to arbitrary proxy
implementations, time/exit populations, anonymity, automatic migration, or fleet behavior.

ADR 0210 removes one ambiguity from that nonclaim by accounting the exact retained corpus. After
ADR 0243's later operator-window repetition, all eight compact actual-Tor proofs reverify before 30
exact-target/churn path declarations resolve to 24 normalized three-hop paths and 23 last-hop
identities. No cross-proof complete path or last hop
is reused. Relay identities remain committed rather than published. This establishes observed
path-population diversity only: it does not prove independent exit operators, jurisdiction or
network diversity, independently witnessed time separation, anonymity, availability, or
global-observer resistance.

ADR 0211 gives future `Tox/I2P` a narrower construction boundary than a generic outproxy. The
adapter accepts only complete numeric Tox records mapped to canonical b32 destinations and only a
numeric loopback SAM bridge. Domain/address-book names, clearnet outproxying, UDP, wildcards, and
native fallback are absent. SAM session loss withdraws new admission and recovery changes only a
local generation. The process double is not evidence that I2P carried traffic; a compromised local
router, malicious destination, timing observer, and Tox-key correlation remain outside that claim.

ADRs 0212–0219 extend that seam through two live routers, three stable service fronts, two contained
guests, router/front replacement, private route-binding v2, and one exact 131,369-byte signed sync
tree attributed to the authenticated I2P member with zero reassignment. Native fallback remains
ready in the payload cell, so the attribution does not come from removing alternatives. It still
does not prove anonymity, independent router administration, or packet-level content classification.

Rejected 512 KiB and 4 MiB diagnostic objects identify a separate downgrade threat: both selected
I2P, then authoritative carrier loss caused correct whole-object reassignment to native while router
and service-front processes stayed healthy. Route membership and fixed/adaptive placement therefore
cannot authorize privacy-class transitions. Before privacy-sensitive large sync or OTA uses this
construction, auxiliary chunks/ranges must remain digest-bound and signed policy must constrain
replacement to an allowed route class or fail closed. ADR 0227 preserves the existing range-v1
digest/HEAD/FileId contract while permitting those frames on an authenticated auxiliary; ADRs
0225–0226 supply the signed class and genuine fail-closed loss evidence. Availability-selected jobs
may explicitly retain current whole-object cross-class recovery.

ADR 0220 supplies the enforcement prerequisite: owner-local `fail-closed` mode fences the lost exact
incarnation, exposes a blocked-job count, and never invokes replacement selection. ADR 0221 freezes
that choice per job, and ADR 0222 freezes a constructed network class used by both initial selection
and replacement. Named classes never fall back to primary; the original actual-I2P gate explicitly
named `tox/i2p-construction` and production gates now name `tox/i2p`. ADR 0225 joins those local
facts to a stable-device-signed route-set-v2
member class and refuses primary, worker, or coordinator mismatch. ADR 0253 makes `tox/i2p` the
canonical text for the same signed class and keeps the construction spelling only as an alias.
Exact endpoint infrastructure and
per-job failover intent remain local. Genuine fail-closed actual-I2P loss/recovery is accepted under
ADR 0226, positive auxiliary range transport under ADR 0227, and live range loss plus explicit
fresh same-carrier recovery under ADR 0228. Same-attempt or failed-prefix byte resume remains open.

ADR 0224 reduces the availability-mode retransmission cost without trusting the old carrier's
prefix. Only a strict private incomplete whole-object file may survive loss, and it moves to the
fresh attempt path with atomic no-replace semantics before an exact seek. ADR 0231 extends the same
rule to a concrete bounded range under native `available` policy: the old receive, FileId, and
signed scheduler attempt are fenced before a distinct authenticated range-capable worker inherits
the exact private inode under fresh identities. A stale old-carrier terminal is fenced. The complete
staged file is still hashed against the signed immutable identity; malicious or corrupted prefix
bytes therefore cause rejection, not partial publication. Fail-closed jobs, including the qualified
I2P loss path, retain no cross-carrier bytes. Restart recovery currently discards these partials
using signed burned-attempt high-water truth rather than resuming them.

## 15. Finite files, OTA, and physical effects

Tox file transfer is a transport facility, not a storage constitution and not execution authority.
rev0017 exposes that facility through finite local path/control records:

```text
file-send      absolute source path
file-receive   friend-scoped file number + absolute destination
file-control   friend-scoped file number + pause|resume|cancel
```

### Local source threats

A malicious same-UID writer may name a sensitive file, substitute a path, mutate the source while it
is being sent, exhaust descriptors, or force repeated reads. Current controls require an absolute
path, no-follow regular-file open, ownership/type/mode policy, size and active-transfer limits, and
captured device/inode/size/mtime evidence. Exact chunk reads use the already-open descriptor.

These controls do not provide content immutability. Filesystem metadata can be insufficient on some
filesystems, and the current transfer has no application content digest. A future durable object
layer should hash content and bind the digest into a signed manifest. A hardened service deployment
should consider a dedicated export root, dirfd capability traversal, Linux `openat2()` resolve
constraints, mount policy, and privilege separation rather than accepting arbitrary host paths.

### Incoming destination threats

Remote names are untrusted presentation metadata and never choose a local path. The local operator
must admit an absolute destination. Incoming offers remain paused until IoTox has created a private
temporary regular file under a locally approved parent. Completion requires exact finite size,
synchronization, and atomic rename.

Pathname parent validation still has race surface between checks and later operations. The same UID
can interfere. Existing destination overwrite is rejected. Future work must define dedicated receive
roots, quotas, reserved disk, symlink/mount crossing policy, dirfd-relative publication, and behavior
for full disk, read-only media, fsync failure, and power loss.

### Control and identity threats

c-toxcore file numbers are friend-scoped live handles and may be reused. They are not durable object
identities. A stale local `file-control` record can target a different later transfer if handle reuse
and operator timing align. Current live projections include direction, file number, file ID, state,
position, size, and pause facts; terminal projections disappear. A future durable control API should
bind a stable application transfer/object ID and expected file ID rather than relying on the live
number alone.

Local pause and peer pause are independent. Both sides must resume before progress. Successful local
`tox_file_control()` is not a peer-originated callback. Collapsing these states can misreport peer
intent or resume an unadmitted incoming offer.

### Evidence and restart threats

A FIFO write proves kernel admission only. `file-events` is a bounded, rotating human journal. Live
`files/` directories are disposable projections. Neither survives as durable transfer truth. Active
file descriptors, chunk position, c-toxcore handle, and partial-transfer state are not restored after
process restart. The sync-only ADR 0234 exception retains bytes, not those live states, and requires
a fresh authorized pull before suffix transport.

`file-receive` success proves local destination admission and c-toxcore RESUME acceptance. It does
not prove completion. A tiny transfer may complete before the synchronous response is rendered;
IoTox therefore returns frozen admitted truth and relies on publication/journal evidence for later
completion.

### Untrusted content and OTA

Received bytes remain untrusted data. Receipt does not grant parsing, decompression, image decode,
plugin loading, configuration import, firmware installation, shell execution, or actuator authority.
Any consumer needs its own bounded parser and capability check.

OTA requires a signed manifest, immutable artifact/content digest, hardware and version constraints,
storage reservation, anti-rollback, staged install, reboot/health confirmation, and recovery image.
The authority to transfer a file is not the authority to install it.

GPIO, locks, valves, motors, heat, power, and safety systems require operation-specific policy:

```text
idempotency definition
maximum effect and duration
preconditions and interlocks
cancellation semantics
crash/power-loss behavior
local override
rate and abuse limits
auditable terminal evidence
```

rev0018 intentionally exposes none of these physical effects.

## 16. Default-off live Ratox host, PTY, and controller boundary

rev0020 retains packet `0xA2` across the R1 session engine, R2 authority model, and R3 process boundary,
but only after an explicit startup gate. Normal configurations omit feature bit 23. An enabled
process must securely load a complete owner-only profile store, find enabled policy, select a valid
helper/factory, and validate service bounds before toxcore starts. Both peers must then advertise bit
23 in the current confirmed epoch. Reachability is therefore deliberate, bilateral, and fail closed;
it is not production activation.

Network and session threats include:

```text
one-sided or stale feature advertisement treated as negotiation
packet 0xA2 dispatched outside the current transcript-confirmed online epoch
friend-number reuse or delayed packets crossing into a later route
friendship or v1 owner status mistaken for interactive.terminal authority
ledger-head change or revocation not closing an existing attachment
authority-head mutation racing between an exact-head check and the resulting PTY or send effect
OPEN duplicate replay spawning a second process
INPUT duplicate, overlap, gap, or partial PTY write causing repeated or uncertain bytes
stale incarnation, nonce, or generation controlling a replacement attachment
one busy PTY starving other sessions or toxcore progress
SENDQ rejection dropping, regenerating, or reordering a reserved response
retained successful response crossing a later authority mutation or being replayed as an unfenced denial
transport disconnect killing a resumable PTY or leaving a stale writer attached
shutdown abandoning a live process or blocking without a deadline
terminal content, argv, environment, paths, or error strings leaking through telemetry
```

Local policy and process threats include:

```text
malicious or non-canonical profile and binding records
symlink, hardlink, replacement, or permissions attacks in the policy tree
policy reload races that mix generations
ambient environment or dynamic-loader variable injection
ambient capability inheritance across helper and target exec
helper, target, or working-directory replacement
file-descriptor leaks, aliasing, or confused fixed-descriptor handoff
ambiguous child setup failure mistaken for successful exec
startup hangs, unbounded PTY pressure, or abusive resize requests
signal races, PID reuse, incomplete process-group shutdown, and unreaped children
escaped descendants or same-UID interference outside the supervised process group
```

Current controls are intentionally layered:

```text
default-off outer gate and complete activation validation before transport startup
immutable local HELLO mask per process and bilateral feature intersection per online epoch
packet-ID-specific dispatch only after transcript, epoch, principal, and exact-head capability checks
Agent-level serialization of signed authority mutation with Ratox receive, bounded PTY progress, and send
complete session/incarnation/principal/nonce/generation attachment identity
pre-effect exact result reservation and conflict rejection for admission duplicates
whole-frame staged PTY input; ACK only after complete sink commitment
partial-write failure terminalizes the incarnation instead of replaying uncertain bytes
bounded replay, output history, queues, sessions, events, and round-robin service budgets
byte-for-byte outbound retention across retryable toxcore admission rejection
per-packet authority dependency retained across replay and rechecked before transport admission
transport-offline attachment fencing, exact authority-revocation closure, finite shutdown drain
private rotating content-free lifecycle journal and aggregate bounded counters
exact owner-only profiles/ and bindings/ tree with no-follow component traversal
canonical bounded records, exact identifiers, and atomic whole-registry generation replacement
fixed argv, executable, cwd, TERM, allowlisted inherited names, and fixed environment values
already-open and revalidated helper/target/cwd descriptors
posix_spawn of this reviewed binary into one hidden child role; no post-fork C++ application code
fixed child descriptors for PTY, manifest, status, target, and cwd
bounded canonical manifest plus explicit child-ready record and close-on-exec EOF proof
stage/errno startup failure records and a finite startup deadline followed by kill and reap
new session, controlling terminal, foreground process group, exact initial dimensions
RLIMIT_CORE=0, configured soft limits, exact account or cleared-group identity,
verified default PR_SET_NO_NEW_PRIVS, verified ambient/active-capability clearing, umask 077, and
closure of unreserved descriptors
bounded nonblocking I/O and dimensions; no input or resize once close begins
observe-before-signal HUP -> TERM -> KILL escalation with fresh deadlines and waitid-based reap
separate test fixture executable so product operation does not gain a general command mode
```

Profile v7 retains v6's host-authorized elevation as an explicit exception rather than weakening that default.
Only a `compatibility` profile with one frozen non-root account may set
`allow-privilege-escalation=1`; root-starting and inherited-root profiles are rejected. The child
proves that inherited no-new-privileges, securebits, and bounding-set state still permits an ordinary
set-ID/file-capability helper, then clears every active, permitted, inheritable, and ambient
capability before executing the account's shell. The exception intentionally makes baseline
seccomp, strict Landlock, and cgroup containment unavailable because a successful root shell could
escape those mechanisms. The device's sudoers/PAM policy, not a Ratox packet, decides elevation.
Consequently compromise of a sudo-capable terminal principal has the same practical impact as
compromise of that owner's administrative login; it must never be confused with a constrained
maintenance profile.

The optional static rescue payload narrows one availability dependency; it is not a new trust
shortcut. Its shell and Toybox directory are exact owner-local profile inputs, must pass canonical
ELF/ownership/mode checks, and never arrive from Ratox bytes. The rescue record omits hazardous
startup variables such as `ENV`, starts baseline/non-root, and keeps sudo as the same explicit
compatibility exception. Static linking removes dependency on target shared libraries but introduces
an architecture/kernel-ABI and third-party-code dependency. A writable/replaced toolbox, collected
Nix closure, missing profile/binding, absent Agent, broken PTY/filesystem, or compromised oksh/Toybox
still defeats the path. The toolbox-first PATH is deterministic command resolution, not confinement;
an interactive owner may invoke absolute host paths. Operators must preserve and qualify the exact
closure before failure, and deployments must carry its separate notices and inventory (ADR 0287).

The rev0019 local controller, bounded and fault-hardened in rev0020, adds a distinct same-user threat
boundary:

```text
relative, aliased, or embedded-NUL socket paths
pathname replacement between validation and connect
connecting to a live attacker-controlled listener under an unsafe parent
stealing or unlinking an active listener
accepting a different UID or more than one admitted local controller
a silent accepted client reserving the sole pre-OPEN slot indefinitely
an immediate busy-close racing the contender's OPEN send and erasing the typed denial
reading a contender's OPEN for identity and accidentally dispatching it as an operation
malformed, oversized, wrong-direction, wrong-stream, or noncanonical local packets
duplicate OPENED or inconsistent GAP/OUTPUT state hidden as network replay
local output acknowledged before successful terminal write
server close before the final detach ACK reaches controller state
post-detach input, resize, close, or ping dispatched as a fresh effect
readable-listener spin or stale successor denial during detach drain
route or authenticated-principal drift across resume
unbounded retained input/output/outbound/event state
raw terminal mode or signal handlers left altered after failure
```

Controls are: absolute NUL-free paths; real private parent traversal; mode/owner/type checks before and
after connection; `SO_PEERCRED`; device/inode identity fencing; mode-0600 creation; one-client and
first-OPEN rules; a configurable finite first-OPEN lease; bounded four-contender batches with one
shared 20 ms consume-and-deny receive window; explicit non-dispatch of contender records; connection-scoped pre-OPEN
errors with exact stream IDs still required for success/progress; canonical 32-byte `ITTS` framing
with a 16 KiB payload bound; exact local sequence transitions; output-before-ACK; a bounded ACK-only
post-DETACH phase whose packet sends share one absolute deadline; listener suppression during that
phase so successors remain in the kernel backlog; independently bounded controller resources; exact
peer/epoch/principal resume identity; and RAII-style restoration of terminal state and signal actions.
Socket shutdown unlinks only the exact inode created by the server.

This is a live service boundary and process-hygiene layer, not a general sandbox. It does not create
user, PID, mount, network, or cgroup namespaces; apply seccomp, an LSM profile, a container, or a VM;
guarantee control of descendants that deliberately escape the supervised process group; survive
daemon restart; or protect against a fully compromised kernel or an equally privileged attacker that
can mutate the same account's files and processes. Exact UID/GID transition also requires suitable
privilege.

The Linux implementation depends on `/proc/self/fd`, PTY ioctls, `waitid()`, and `fexecve()`-style
semantics. Portability is not claimed. There is one same-user admitted local terminal stream. rev0020
adds separate-process local contention, death, replacement, replay-ACK, detach, and empty-restart
failure evidence, but there is no daemon-restart state survival, multiple local streams, complete
remote reconnect/revocation/storage qualification, two-guest Sandwurm complete-service evidence, or R8
production-support decision.

## 17. Future synchronization boundary

Synchronization is daemon-integrated only behind explicit `--enable-sync`; namespace policy remains
owner-local and the service is absent by default. The intended boundary is:

```text
local namespace policy -> sync planner/worker
    canonical owner-only records, stable writer/subscriber principals, mandatory quotas, explicit
    engine and activation mode

remote sync HEAD/manifest/object -> staging/content store
    accepted only after confirmed session, proven principal, authority-ledger capability, namespace
    match, signature, parent/fork/rollback, size, object identity, and quota checks

staging/content store -> active revision
    local activation decision only; transfer completion is never executable or filesystem authority
```

Threats retained through S2 protocol integration:

```text
friendship confused with writer/subscriber authority
remote namespace names selecting local paths
HEAD rollback, fork, replay, or cross-namespace substitution
manifest/object hash confusion or sparse availability lies
symlink, hard-link, path traversal, no-clobber, and permission bypass in stores
power loss between HEAD admission, content commit, activation, pinning, and GC
quota exhaustion deleting the last accepted revision or blocking unrelated namespaces
content-v2 multi-source scheduling amplifying metadata or CPU beyond configured bounds
content source possession or route availability being confused with signed-HEAD authority
content object requests being rebound across HEAD, namespace, kind, index, digest, size, or FileId
publisher replay causing duplicate file offers or changed authority reviving an old offer
sparse availability crossing windows, setting noncanonical tail bits, or claiming unverified CAS bytes
owner-local multi-source setup dispatching a cached HEAD before every intended source is authenticated
foreign-writer replica state being mistaken for a locally authored published HEAD after restart
process-local friend numbering being persisted or rebound as an unattended synchronization source
automation policy tamper, stale completion, retry amplification, or service-thread filesystem work
managed sync state recursively entering its own publication source
friend/principal rebinding between read-only-share preparation, RecallRoot signing, and commit
authority grant being confused with namespace membership after a partial share transaction
two mutually authorized linear writers being mistaken for a convergent bidirectional filesystem
received content being activated merely because a follower policy exists
operator mistaking sync convergence for unattended OTA or safety-critical actuation
```

Current controls are default-off and layered: `iotox-sync-namespace-v1` rejects noncanonical records,
requires sorted unique stable principals and explicit quotas, loads only an exact owner-only
`ROOT/namespaces/<id>.namespace` tree without symlink or hard-link acceptance, and replaces the
in-memory registry atomically. Owner-local creation now reuses that exact record: offline template and
lint are effect-free, while same-user local control writes and fsyncs an unnamed mode-0600 file,
atomically publishes the final name without clobber, fsyncs the directory, strictly reloads the
complete store, and replaces the live registry. Local control v1.29 serializes install, update, and
removal. Update is admitted only after publisher replay state and target subscriber work have drained;
it may change activation and canonical writer/subscriber membership but not ID, root, engine, or
quotas. It uses one strict owner-private canonical temporary plus atomic rename. Removal unlinks only
policy and leaves all content and signed state intact. Every possibly committed result reconciles disk
with the live registry, which is emptied if reload fails. Exact retries are generation-stable.
Namespace administration grants no remote capability and creates, migrates, activates, or deletes no
data root. `iotox-sync-accepted-head-v1` persists one accepted record per
namespace through IoTox atomic state replacement and rejects rollback, fork, parent mismatch, wrong
namespace, unauthorized writer, engine mismatch, quota, and generation-jump candidates before
mutation. Its at-rest envelope is signed under a separate domain by the stable device and rejects
unsigned legacy, foreign, or altered state. The local activation transaction requires manual policy
and the exact current accepted HEAD, rechecks both immutable objects and their engine-specific semantic
binding, rejects rollback/fork/corrupt prior state, and atomically stores a separately domain-signed
activation pointer. ADR 0091 reserves future sync capability bits without widening v2.

ADR 0270 adds one strict `IOTXSAU1` automation record per namespace under the stable device signer.
The record stores a proven remote stable principal, never a friend number, or one canonical absolute
local publication path. Generation replacement fences stale worker completion; a signed disabled
tombstone is the revocation fact; bounded retry prevents an offline source from creating an
unbounded queue. Active policy prevents namespace update/removal. The service loop may only claim
work; source scans, network/session resolution, accepted-state reads, and activation execute on the
bounded sync worker. Automatic pull re-enters current v3 publisher authorization, and verified
activation re-enters the exact accepted-HEAD transaction under the namespace's existing activation
permission. The host-local policy chain still has no independent rollback witness.

ADR 0271's `sync-create` puts generated roots only below a descriptor-validated owner-private
`data/` child and refuses either direction of containment with the publication source. Exact retry
requires the installed namespace and automation policies to match; a convenience command cannot
silently mutate roots, quotas, engines, membership, or cadence. `sync-share` resolves the peer's
stable device from a current application-ready exact-v3 session both before and after RecallRoot
signing. The commit requires the prepared principal to remain identical, preserves all existing
roles/capabilities and writers, and adds only `sync.subscribe` plus subscriber membership. A grant
committed before a quiescence-dependent membership update remains inert for that namespace and is
safe to retry. This ceremony intentionally cannot create read-write access: linear signed HEADs have
no causal merge, conflict, or deletion semantics, so the CLI refuses the label rather than exposing
silent last-writer-wins data loss.

ADR 0272 removes that data-model blocker. Tree-v2
retains immutable signed records for every claimed causal observation and refuses foreign-origin
values absent from authenticated proof manifests. The signed workspace checkpoint binds the exact
frontier actually projected, preventing a newly received but unseen remote branch from retroactively
becoming the causal parent of a local edit. Concurrent values and tombstones are projected with
origin provenance; a later edit is the explicit resolution event. Whole-directory exchange is
journaled before effect and keeps the old projection until the target marker and contents reverify.
An unsafe path, same-writer fork, missing observation record, invented carried value, unexpected
worktree mutation, or ambiguous restart orientation fails closed.

ADR 0273 advertises tree-v2 only with synchronization enabled and adds bounded peer-controlled
inventory and recursive proof fetch. Every request/result and file offer is tied to one negotiated
primary carrier, online epoch, exact authority head, stable principal, capability set, digest, size,
and FileId. The receiver commits immutable bytes before signed branches and signed branches before
workspace effect; failure cancels and removes its exact staging lane. Reciprocal owner ceremonies
grant both sync capabilities and membership but cannot choose the other device's path. The durable
automation record binds a sorted bounded set of remote stable principals and refuses implicit
rebinding. Every bilateral writer grant remains an owner act; there is no transitive group trust.

ADRs 0330--0331 narrow small-file resource amplification. File lanes commit in bounded windows and
one pull may reuse an opaque strictly verified in-memory CAS inventory instead of re-hashing the
complete store per window. That cache is never durable truth: before branch or projection effects,
the complete store is re-opened, re-sized, digest-verified, and quota-checked under the effect's
namespace transaction. Every cached object must remain exact. Independently added valid immutable
objects are safe and counted; missing, replaced, corrupt, malformed, or quota-excessive state is
refused. Consistently lying storage, unhonored durability barriers, and disk exhaustion between the
point-in-time checks remain outside the threat boundary.

ADR 0275 addresses unbounded quiet history and local writer retirement. A received remote frontier
does not itself cause a new signed branch; the authenticated workspace roots the derived merge until
a real local edit observes it. Negotiated format-2 checkpoints terminate graph traversal only after
a conflict-free exact frontier is signed. GC roots current branches, exact pins, and active/pending
workspace manifests/frontiers; it moves only authenticated unreachable objects into recoverable
quarantine and has no purge mode. A cutoff binds one writer to one exact terminal record and fails
later admission, but it is owner-local policy that must be repeated by every survivor and does not
revoke other capabilities. The maintenance signature detects alteration but has no hardware rollback
witness. Malicious fork/conflict storms, long-offline permutations, power cuts, large-tree resource
behavior, and permanent deletion were outside ADR 0275's historical claim. ADRs 0280--0281 now
qualify the named crash/fork matrix, 16-candidate conflict ceiling, 128 arrival orders, 4,096-file
tree, and the accepted long-offline lifecycle. Physical power cuts, dishonest storage, larger
populations, and permanent deletion remain outside the supported claim.

A checkpoint is one authorized writer's compact attestation, not multisignature agreement. A
receiver authenticates its writer, manifest, generation, and observation claims but deliberately
does not fetch the pruned graph below the floor; a receiver without older local state may bootstrap
from it. Consequently an authorized malicious writer can misrepresent pre-floor history even though
an unauthorized peer or modified checkpoint cannot. Writer authorization and controlled checkpoint
operation remain part of the trust boundary.

Authority-ledger v3 now implements those bits behind a signed non-widening v2 migration, independent
record/digest/proof domains, bilateral feature negotiation, exact-head proof, and explicit later
grant. `IOTXSHD1` now freezes a fixed 296-byte writer-signed publication record: the stable IoTox
device identity signs a domain-separated hash of namespace, engine, generation, parent, immutable
artifact/manifest identities, and sizes. Parent linkage hashes the complete signed predecessor under
a second domain. Local creation derives writer, namespace, engine, generation, and parent; conversion
to acceptance state first verifies signature and policy and computes record identity internally. The
private fixed-size publisher file rejects symlinks, hard links, wrong ownership/mode/size, corruption,
foreign predecessor writers, quota violations, and exact-retry generation consumption before atomic
replacement. This deliberately avoids importing toxsync's separate HEAD key as a second publication
root.

The signed HEAD alone does not prove its named immutable objects exist, does not itself grant
`sync.publish` or activation authority, and has no external monotonic witness. The local publication
job now closes the first availability gap: it independently bounds, hashes, privately stages,
no-clobber commits, and reverifies both artifact and manifest at their final digest-named paths before
advancing the HEAD. It refuses source symlinks, changing sources, and corrupt, public, or multiply
linked existing objects. Late cancellation preserves the HEAD; unreferenced committed objects are
safe for later reuse or collection. A private persistent advisory lock now serializes signed-HEAD
predecessor load and atomic replacement across local processes. A canonical object inventory rejects
unexpected/public/linked entries, checked-adds exact bytes, and applies sequential whole-store
byte/object admission. The lock is cooperative, not distributed. Reachability-safe collection and
coordinated rollback of an otherwise valid HEAD plus surrounding state remain unclaimed. The fixed
remote wire codec, explicit-FileId carrier, default-off Agent publisher/subscriber, owner-local
range-v1 publication, and exact-token manual activation now exist. Two source-linked Sandwurm guests
now pass the genuine one-source 4 MiB convergence and explicit-activation baseline over both observed
direct UDP and forced TCP. A separate 8 MiB cell kills the receiver after positive c-toxcore progress
and passes unclean daemon restart over both carriers. The experiment exposed that the transport's
private pre-rename temporary could survive while signed attempt recovery saw only an absent canonical
path. Recovery now derives the one exact temporary prefix from the signed attempt ID, validates all
candidates before mutation, removes only a private singly linked regular file, fsyncs the staging
directory, and clears the active journal record afterward. Malformed, duplicate, linked, or uncertain
candidates fail closed. This is attempt-scoped crash cleanup, not general orphan GC or byte-range
resume. Pull cancellation now names one collision-checked process-local job, marks it terminal before
cleanup, closes admitted receives at most once, removes staging and signed active-attempt records,
and fences remaining scheduler reservations. Late HEAD/object/offer/terminal events cannot revive
the job or accept its HEAD. Failure to enqueue a remote CANCEL is surfaced but cannot prevent local
cleanup; exact retry settles the tombstone without repeating transport cancellation. The job ID is
not durable and cancellation does not claim the peer stopped sending. Rate-shaped direct-UDP and
forced-TCP Sandwurm cells now pass after positive provider progress with no acceptance or activation.
A separate bilateral TAP-blackhole cell now passes over both carriers: offline observation retires
the old epoch, job, FileIds, signed attempt state, and partial staging; a fresh pull is admitted only
after both peers advance and retain one confirmed, authorized epoch for a bounded stability window.
That is whole-object retry, not partial-byte resume or implicit epoch rebinding. A live receive may
now reuse the existing finite-file control path to set and clear its local pause fact. The job,
signed attempt, staging reservation, file number, request-selected FileId, and authenticated epoch
remain unchanged, and a remote pause cannot be cleared locally. Rate-shaped genuine-provider cells
hold one positive partial position stable before resuming and completing on both carriers. Pause is
not cancellation, durable intent, handle reconstruction, acceptance, or activation. A controlled
publisher guest reboot now passes on both carriers across two bounded VMM epochs. The subscriber
retires the old job and staging on offline observation; the successor preserves and validates the
exact publisher identity, policy, source, immutable objects, and signed HEAD from its persisted disk.
Only an explicit whole-object pull after 50 stable samples of a higher confirmed authorized epoch may
accept and activate that revision. This is not abrupt power-cut recovery, partial-byte reuse, or
automatic retry. Quiescent namespace update and policy-only removal are now local effects; range
reuse is now implemented behind separately negotiated bit 26. The subscriber commits and verifies
the complete candidate manifest first, derives its plan only from the exact accepted local artifact,
and requests at most 64 sorted nonoverlapping nonadjacent target ranges bound to the current HEAD and
one FileId. The publisher rehashes the current artifact and offers a descriptor-pinned canonical
concatenation without a temporary bundle. The subscriber durably owns the target attempt before
receive, unlinks the range bundle before reconstruction, verifies the complete target SHA-256, and
accepts HEAD last. A peer never supplies basis matches or an executable path. If the exact accepted
basis is absent or corrupt at planning time, ADR 0137 treats only reuse as failed: the candidate
manifest is reverified and a new ordinary whole-artifact attempt must pass complete SHA-256 before
HEAD acceptance. The unusable object is not deleted, replaced, or granted authority. Storage I/O,
manifest corruption, and invariant failures remain terminal. Deterministic full-Agent evidence
fetches 4 KiB and reuses 12 KiB for one generation-2
successor. Genuine two-guest direct-UDP and forced-TCP evidence fetches one 128-byte range and reuses
4,194,176 verified bytes for an exact 4 MiB generation 2. The corrupt-basis fallback also passes on
both genuine carriers while retaining the invalid old path. A same-epoch partial range fault may now
retry exactly once only after exact staging removal, signed-attempt finish, and scheduler fencing.
The unchanged plan gets a fresh attempt, message ID, and FileId; discarded prefixes never become
reconstruction input. Genuine direct-UDP and forced-TCP cells prove this after public CLI cancellation
at positive progress. Explicit target-object repair also passes genuine direct-UDP and forced-TCP
cells: a fsynced digest mismatch is quarantined without changing signed acceptance or activation,
the same authorized revision restores the exact target path, the corrupt evidence remains private,
and a second scan verifies a clean final store. Signed engine 3 now binds deterministic treepack-v1
semantics without content sniffing. Publication accepts only bounded owner-controlled real
directories and single-link files; links, special entries, shared-write state, excessive population,
and complete-artifact overflow fail before HEAD mutation. Materialization happens only after signed
activation state is durable, unpacks privately, deterministically repacks to the signed digest,
fsyncs and freezes the result, and atomically switches a relative current pointer. Exact retry
reconciles projection interruption; canonical abandoned staging and pointer temporaries are recovered
only after complete classification, and noncurrent derived trees are pruned under the namespace
transaction. A separate-process `_exit` matrix now covers all eight explicit projection boundaries
and requires one complete old-or-new view followed by canonical exact-retry recovery. Automatic
scrub, quarantine purge, tree range reuse, multi-source merging, real power-cut behavior, and the
remaining resource/rollback/fork evidence remain open.

Explicit retained revisions now persist in a canonical capacity-bounded owner-private snapshot. Each
pin is copied only from a policy-valid accepted HEAD and preserves exact generation, record, artifact,
manifest, and sizes; process-serialized pin/unpin rejects forks and conflicting identities. The
v2 snapshot is signed by the stable device under a dedicated domain, and every mutation commits its
counter and the preceding signed-record digest. Foreign keys, tampering, truncation, and unsigned v1
state fail closed. A complete older valid record can still be replayed after restart because no
independent monotonic anchor exists. It is therefore a retention input, not deletion authority:
destructive purge remains disabled until an independent anti-rollback policy exists. Published,
accepted, activated, and pinned roots now share one ordered transaction and signed rollback guard;
quarantine-first construction and its workspace-contained test boundary are specified separately.

A mark-only reachability planner now merges those four persisted root classes against a strict
kind/digest/size object inventory. It fails malformed, foreign-signed, duplicate, quota-excessive, and
root-size-conflicting input, and distinguishes missing or mismatched live objects from unreferenced
candidates. This reduces ambiguity but grants no deletion authority: every root is authenticated, but
complete matching state remains replayable.

Explicit local `sync-gc ... quarantine` may consume only a freshly recomputed consistent plan. It
accepts no pathname, pins the transaction/root and complete inventory by descriptor identity,
refuses links and mount crossings through Linux `openat2`, reopens each exact candidate before a
no-replace same-filesystem rename, and fsyncs affected directories. Cancellation and late sync
failure retain exact moved-versus-durable evidence. This limits same-user path substitution and
ambient-path damage; it does not establish permanent disposability. Quarantine has no purge,
automatic expiry, remote entrance, or startup trigger and remains potentially live after a complete
coordinated rollback.

ADR 0244 freezes a dark content-v2 object boundary without enabling it. Each canonical request binds
namespace, exact frozen signed-HEAD record digest, manifest-page/artifact-chunk kind, digest, logical
index, byte size, and FileId. The publisher independently requires current `sync.subscribe` proof and
subscriber membership, rehashes its current signed HEAD, resolves the object only through the local
verified manifest, and verifies the derived digest-named CAS object before offering. Bounded recent
replay is retained before the offer; an exact retained replay never reoffers and changed bytes or
authority fail closed. A retired immutable-read identifier is re-authorized as fresh work and may
reoffer only the currently verified digest-bound object (ADR 0282).
The receiver independently freezes and rehashes the accepted HEAD/manifest, applies namespace bounds
to peers, lanes, objects, outstanding work, windows, memory, and I/O, and requires current exact-v3
`sync.publish` plus writer membership from every source. Source disappearance fences the exact
assignments before any live caller may retire their FileIds. At the ADR 0244 boundary the Agent did
not advertise bit 29: durable attempt/event joining, prospective combined-quota enforcement on every
CAS write, authenticated reachability/repair/GC, and restart recovery were prerequisites.

ADR 0245 narrows the sparse-inventory threat: a fixed request binds namespace, frozen HEAD, object
kind, first index, and a nonzero bounded count; the variable result is exactly the corresponding
little-endian bitmap with zero tail bits. The source rehashes the root and every claimed CAS object,
and the subscriber accepts the bitmap only for its current coordinator window after independently
reapplying source authority. Windows do not carry forward. Availability remains a scheduler hint and
never authenticates received bytes or revision truth. The Agent still does not dispatch these frames.

ADR 0246 closes the first physical quota ambiguity without enabling content-v2. Under the same
namespace transaction used by flat sync state, the CAS scanner accepts only the canonical `sha256`
fanout, private owner-owned single-link files on the namespace filesystem, bounded physical totals,
and optionally bytes whose stable SHA-256 equals their name. A combined view applies one object and
byte ceiling to flat plus CAS storage, preventing two independent full allowances. Preparation
refuses an existing alias or unsafe root and does not chmod through a symlink. This is still neither
prospective writer enforcement nor authenticated reachability/deletion authority.

ADR 0247 closes that prospective writer gap for the construction coordinator and standalone root
manifest entrance. Both use only derived private namespace roots and the exact assigned staging path;
require an owner-owned mode-0600 single-link file of the expected size on the namespace filesystem;
charge new bytes and identity against the combined inventory under the same transaction; and publish
only a fully hashed no-replace copy. Staging is consumed after success, while quota and structural
refusal leave it explicit for caller-directed retry or failure. The product path rejects
`source_preverified` and hard-link ingest. Durable attempt identity and FileId/event correlation are
still required before a network caller may reach this entrance.

ADR 0248 gives those staged bytes signed restart meaning without reviving dead transport state. A
bounded canonical CTA1 record commits the frozen HEAD, logical object, digest/size, FileId, source,
and complete carrier incarnation before effect; active request, FileId, and logical identities cannot
alias. Startup trusts neither filenames nor old friend numbers. It may reuse verified CAS truth or
commit one exact complete private staging file through the ADR 0247 entrance, but removes/fences a
partial file and leaves unsafe or corrupt-complete ambiguity plus the signed journal untouched. The
final active-set retirement is a new signed mutation, so a crash after CAS publication replays safely.
The hash link is not an independent anti-rollback witness, and fresh transport work still requires
current authority and frozen-HEAD admission in the Agent.

ADR 0249 closes the synthetic-local-publisher gap without enabling the network protocol. A content
writer must be the configured local device and own any predecessor before it builds. One private
transaction-bound workspace contains the toxsync scratch fabric; source metadata is fenced across
the build, complete object identities are deduplicated, scratch and combined physical quotas are
checked before CAS mutation, every immutable object is copied and rehashed through ADR 0247, and the
signed HEAD lands last. Cancellation after partial CAS publication therefore creates only
unreachable immutable bytes, never signed incomplete truth. Startup deletes only exact private
publication workspaces and treats an unexpected entry as ambiguity. A hostile same-user process can
still race pathname-based source reads; content confidentiality and hostile-kernel/filesystem safety
remain outside the claim.

ADR 0250 closes the transport-neutral receive order without enabling Agent dispatch. Root kind 3 is
valid only for the exact signed manifest at index zero. A stable-device-signed CTA1 binding exists
before every receive effect, and an early FileId offer stays paused until its exact offered result.
Root, pages, and chunks enter verified CAS before reconstruction; the whole verified artifact enters
CAS before accepted HEAD. Cancellation can leave unreachable immutable bytes but cannot accept or
activate them. Exact class-scoped workspaces prevent cleanup from crossing into publication,
reconstruction, or network-attempt state, and toxsync no longer creates network staging directories
outside CTA1 admission. The one-source service still lacks Agent authority/event dispatch, explicit
activation, signed reachability/repair/GC integration, genuine provider evidence, hostile same-user
isolation, and arbitrary power-loss qualification.

All implemented local synchronization mutations now acquire one strict per-namespace advisory lock.
Nested operations must present a move-only token bound to the acquiring process and thread, preventing
self-deadlock, fork-inherited reuse, and concurrent cross-thread reuse. A stored-state reachability pass
loads published, accepted, activated, and retained roots and scans exact inventory under the same
acquisition. Accepted and activation state are independently domain-separated and stable-device-signed.
This closes local mutation/scan races among cooperating IoTox processes, but not same-owner out-of-band
filesystem changes or complete valid-state replay. Exact idempotent mutation retries reconcile either
valid pending crash side before returning a duplicate result.

ADR 0251 closes the deterministic Agent product gate without broadening remote authority. Bit 29 is
added to HELLO only after content service construction, startup recovery, and a complete authenticated
walk of every persisted live graph. Primary-carrier dispatch joins canonical packets, exact FileIds,
and terminal events to one content job; content convergence still advances accepted HEAD last and
never activates implicitly. Explicit activation rehashes the whole artifact and manifest through
their CAS paths. Published roots retain the complete transfer fabric, while accepted/retained roots
also retain whole artifacts. Missing required root/page metadata makes traversal incomplete and
suppresses unreferenced classification. Repair may quarantine only a digest/name mismatch. GC
replans under the namespace transaction, freezes exact filesystem identities, and uses no-replace
same-filesystem rename plus fsync; purge, remote invocation, automatic collection, and expiry remain
absent. The deterministic mock-provider gate does not qualify hostile same-owner interference,
arbitrary power loss, genuine carrier behavior, sparse-source selection, striping, or source loss.

ADR 0252 narrows only the genuine-carrier nonclaim. Two independent source-linked microVMs now
converge and explicitly activate the same paged content revision through c-toxcore over direct UDP
and forced TCP. The strict compact proof retains the ordered content shape and binds its artifact,
manifest, and HEAD hashes to both role receipts. This establishes one complete primary source and
one object lane on native carriers; it grants no authority from transport success and does not
qualify complementary partial sources, multi-source scheduling, striping, selected-source loss,
performance superiority, hostile same-owner interference, or power loss. Daemon restart was still
unqualified at this gate and is narrowed separately by ADR 0267.

ADR 0254 closes the deterministic sparse-consumption gap without granting source discovery or HEAD
authority. One same-user local-control mutation may attach an application-ready primary peer to an
active content-v2 job only after exact-v3 `sync.publish` and writer-membership checks. Every current
window is requested from all registered sources, and a selected request/FileId/CTA1/terminal chain
stays bound to one exact authenticated context. The original peer alone supplies the frozen HEAD;
added sources cannot change or activate it. Complementary stores converge in the owned registry,
and ADR 0255 now qualifies genuine complementary sources over direct UDP. Forced TCP remains
unqualified after thirteen bounded relay/admission/rendezvous cells. The strongest hybrid briefly
confirmed the secondary TCP/application session but lost it before v3 authority or object work;
established relay sockets and transient confirmation confer no authority. Selected-source
loss is qualified only as whole-job failure followed by explicit higher-epoch recovery under ADR
0256. Local-control v1.41 authenticates and installs all intended sources before primary HEAD
dispatch, eliminating the cached-root/source-add ordering race. The construction secondary's foreign-
writer HEAD now enters only the ADR 0257 replica store: the original writer signature, current
policy, complete metadata graph, same-writer chain, and a local device custody signature are all
required. The local publication tree stays absent. A replica can answer exact availability/object
requests for the frozen record after cold start, but primary HEAD acceptance still binds the
authenticated writer and activation remains local and explicit. GC retains present replica graph
bytes, treats absent replica-only chunks as expected, and refuses classification when metadata
traversal is incomplete. ADR 0258 permits the already-authorized content availability/object/FileId/
CTA1 chain to use one exact reciprocally bound route-worker incarnation selected before HEAD. It
does not move the primary writer proof or HEAD to that friendship, and exact carrier loss fails the
whole job. ADR 0259 qualifies complementary sources through two distinct actual-Tor worker
identities while both publisher authority sessions remain native. Per-source owner-private status
binds each stable principal to its authority route and exact carrier incarnation, and independent
verification recomputes the carrier-set commitment. Both device-side workers share one Tor process;
therefore per-source circuit/physical-path diversity is not implied. ADR 0260 now qualifies one
destructive routed-source boundary: exact Tor-worker loss after positive progress makes the whole
content job terminal, cleans transient staging, cannot accept or activate HEAD, and cannot rebind or
downgrade that source. The route may restart only after all affected content work is terminal; a new
worker incarnation can serve only a distinct explicitly authorized pull. Verified immutable CAS
objects remain reusable and are not confused with partial staging or authority. ADR 0262 permits
bounded same-source page/chunk overlap only after root discovery. Every live lane has a distinct
request/FileId/CTA1 binding; one permanent lane failure cancels its siblings and the whole job, and
signed namespace quotas can only reduce the process cap. Direct-UDP and forced-TCP two-lane VM gates
pass, but they do not imply byte or route striping. ADR 0263 measures stable-session effective caps
`1/2/4/8`; ADR 0266 now counterbalances ascending and descending order on both native carriers.
Cap 2 is the efficient mixed/relay-heavy construction recommendation, cap 4 the controlled
direct-UDP option, and cap 8 stress-only. This does not justify raising the default, automatic
tuning, or—by ADR 0266 alone—an interactive-latency budget. ADR 0267 qualifies unclean subscriber-Agent restart at
explicit caps two and four over both native carriers. Recovery distinguishes complete verified CAS
objects, canonical journal-governed CTA1 staging, and c-toxcore's private pre-rename transport
temporaries. Complete CAS inventory survives exactly; exact safe transport temporaries are removed;
old attempts cannot accept HEAD or activate; and only a fresh pull after independently observed
two-sided authority recovery can converge. Malformed or unsafe transport residue fails startup
closed. This does not qualify partial-prefix resume, transparent same-job continuation, power loss,
or a general crash-consistency proof. ADR 0268 separately freezes and passes an already-attached
Ratox cap-two construction SLA over direct UDP and forced TCP under 4 Mbit/s subscriber shaping:
at least 40 exact-overlap rows, p50/p95/p99/max no greater than 250/500/1,000/1,500 ms, and
owner-queue p95 no greater than 10 ms. Cap four and cap eight miss its p95 ceiling in both cells.
This permits deliberate cap-two native interactive-bulk use, but does not raise default one, tune
automatically, change framing, or claim Internet, physical-host, faster-link, routed-privacy,
multiple-terminal, fresh-admission, or long-running latency. ADR 0269 qualifies bounded same-source
whole-object distribution over two exact authenticated Tor workers, including colliding route-local
friend numbers, while retaining one primary authority/HEAD session and fail-closed loss. It does not
qualify byte striping, balancing, speedup, independent circuits/physical paths, or automatic route
selection. I2P content-v2, anonymity, and physical-host diversity remain unqualified. ADR 0261 repeats the same exact-worker-loss contract
through a second compiled public Tox relay record. That weakens the hypothesis that ADR 0260 was a
single-relay accident, but same-day same-host samples do not establish independent exits, physical
paths, time windows, availability, or long-running fault policy.

A signed fixed-size namespace rollback guard now binds committed and optional pending head sets across
publication, acceptance, activation, and retention. Its transition store detects missing guards,
isolated rollback/deletion/fork, foreign signatures, tampering, weak paths, and both expected power-cut
states under the namespace transaction. Every implemented signed-root mutation now uses its
begin/replace/finish protocol. Coordinated replacement of both guard and matching roots remains
possible without a hardware counter or external owner/replica witness.

### Accepted protected-local-state expansion

Roadmap workstream 8 and ADRs 0302--0314 define two distinct mechanisms and forbid treating either as the
other. The implemented first tier is an externally unlocked fscrypt-v2 root whose descriptor-safe
preflight closes over every configured security-bearing state domain, derived companion, and
disk-backed runtime before network or effect startup. A required public master-key-identifier pin
also refuses an unintended encrypted root/policy. It accepts no unlock secret through argv,
environment, config, local control, or a peer. Encrypted-at-rest state protects copied or stolen
storage only to the extent of its unlock/key-custody model. Replacing a current valid
ciphertext with an older valid ciphertext is still possible when all monotonic truth lives on that
same storage.

Rollback resistance therefore requires a separately controlled monotonic witness. ADR 0303
implements the authority-lane transaction coordinator with a durable exact signed local intent and
an authenticated pending/committed compare-and-swap. ADR 0305 adds the first remote-service backend:
device-signed nonce-bound requests, responses under a pinned dedicated witness identity, explicit
device-signed no-replace enrollment, and a signed crash-atomic store under one exclusive writer. A
same-disk mock remains test-only and is rejected outside the explicit exception. Its exact ceremonies
cover lost hardware, board replacement, disaster recovery, witness unavailability, cloning, and
intentional restoration.
No deployment may silently weaken to “encryption only,” reset its counter, or accept an old state
because the witness is offline. The fscrypt VM establishes construction-host offline-media behavior.
The two-guest service VM separately establishes authority advancement, complete Agent-state rollback
refusal, outage/restart behavior, and server-key pinning, but both guests share one host and admin.
The service's per-record signature cannot detect restoration of its own complete disk. ADR 0313 adds
a service-signed complete-population checkpoint and an exact-or-later startup floor, but the operator
must retain that artifact in another failure domain and supply the trusted copy. Coordinated restore
of the service and its only checkpoint still succeeds. Production therefore requires separate
administration/storage/failure domains plus rollback-resistant persistence or genuinely independent
checkpoint retention. ADR 0306 separately enrolls the application-protocol and Ratox
host incarnation records. Every opted-in startup must commit its exact signed next record through a
durable intent and external pending/committed CAS before runtime creation. Restoring an older valid
incarnation therefore refuses even when authority is current; an earlier lane may safely burn a
position before a later lane refuses, but no network/effect surface is exposed.
ADR 0307 extends the same external transaction to the signed route artifact and local generation
checkpoint. Enrollment anchors one reviewed current digest; future policies must advance exactly
one generation. Coordinated replay of both local route files, a fork, deletion, or skipped history
therefore refuses before routes are constructed. ADR 0308 witnesses the complete validated Ratox
profile/binding tree through an explicit owner commit, caches the exact verified activation, and
refuses restoration of an old sudo-capable tree plus its matching signed checkpoint before runtime.
ADR 0309 witnesses the exact durable identity/frontier of every authorized mutable command after
signed `STARTED` persistence and before the provider/update call. Whole or selective command-store
rollback that erases a started effect therefore refuses while later result/delivery churn does not
consume witness positions. It is not a generic exactly-once physical-effect protocol.
ADR 0310 witnesses the complete canonical namespace and stable-device-signed automation policy tree.
Startup freezes that exact authenticated snapshot; Agent-mediated edits commit the complete durable
candidate externally before the live registry or scheduler changes. A full old policy tree plus old
local checkpoint therefore refuses. Source paths and membership are protected by this policy
freshness boundary but remain private witness-correlatable configuration, not content-free material.
ADR 0311 witnesses the canonical update policy and signed lifecycle state before selected-slot
pointer effects. ADR 0312 gives each opted-in single-writer namespace a domain-separated record for
its signed published, accepted, activated, and retained roots. ADR 0314 gives tree-v2 a separate
record for its live branch frontier plus exact signed workspace and maintenance state. Each refuses
a coordinated older semantic-state/guard snapshot while the service remains current. The lanes
require complete policy witnessing, but supply only startup/mutation freshness rather than a
continuously renewed clone lease. Replica and attempt journals, object/quarantine inventory,
content, projection-marker/current-pointer state, namespace health, and the complete recovery/
rollback campaign remain open.

### Diagnostic recorder and support-bundle threats

ADR 0291's local recorder is stable-device-signed and canonical. No-follow owner-only single-link
reads, strict bounds, contiguous tail accounting, and crash-atomic replacement reject weak paths,
foreign state, byte tampering, truncation, and malformed closed values. The Agent/incarnation lease,
not the file format, supplies single-writer exclusion. Replacing the recorder with an older complete
valid copy remains possible without the independent witness described above.

The record schema has no content, identity, address, path, endpoint, filename, command, terminal,
credential, signature, or time fields. Raw argv is not hashed: its small or predictable values could
otherwise be recovered by dictionary comparison. The structural configuration commitment still
correlates equal reviewed feature/quota shapes, and counters/order reveal activity. “Content-free” is
therefore not an anonymity claim.

Export crosses same-user local control and returns only a validated redaction. The created bundle is
private and no-clobber, but once shared it is ordinary data. Its payload digest detects accidental
corruption, not malicious rewriting; the deliberate absence of device key/signature prevents a
recipient from authenticating the emitter. Inspection is neither device attestation nor proof that
events were not omitted. Arbitrary logs, environment, `/proc`, `/sys`, configuration, and runtime
trees must not be swept into this channel.

### Peer alias confusion and takeover

ADR 0292 prevents lexical ambiguity: bare names begin with lowercase letters and stop at 63 bytes,
so they cannot be uint32 friend numbers or 64-hex keys; explicit `friend:`, `key:`, and `alias:` forms
never fall through. There is no case folding, Unicode normalization, abbreviation, prefix lookup,
hostname lookup, or “closest” match. The same parser is used by ordinary and terminal clients.

The device-signed store is one-to-one. A set cannot replace an existing name or give a second name
to one key, and the Agent rechecks new bindings against current friendship. Rename is atomic.
Transport peer deletion retains its name so attacker-controlled reconnect timing cannot free a
trusted label; rebind requires explicit remove then set. A rolled-back but valid store can restore an
old mapping because no independent witness exists yet.

Aliases are private metadata and may disclose machine roles. They are excluded from diagnostics.
An alias authenticates nothing: it binds a local label to a Tox route key, not the remote stable
device principal, authority capabilities, DNS, or physical machine. Operators must use explicit key
or future verified migration ceremonies when the transport identity changes.

### Retained-history and forward-restore threats

ADR 0294 treats every record name, manifest, and file object as hostile until its existing canonical
digest/signature/size checks pass. History inventory rejects unexpected names and reloads exact
records. Diff and conflict paths are hexadecimal so filesystem bytes cannot inject output fields;
bounded detail always reports omission. These are same-user owner-local metadata surfaces, not a new
remote read capability.

The restore plan closes the review-to-effect race across namespace policy, authenticated pins and
cutoffs, current branch frontier, current merged manifest, signed workspace generation, worktree
contents, target record, and required object inventory. Apply re-derives and constant-time compares
the ID. A concurrent edit or convergence step makes the token stale. A successful token cannot be
replayed because its own higher branch changes the frontier. Conflicted targets are refused, and a
missing or corrupt object prevents readiness.

A malicious authorized writer can still sign destructive content, and the local owner can
deliberately restore harmful bytes. The mechanism supplies causal and review integrity, not content
safety. All history, pins, current state, and signing keys share one machine and one rollback domain;
host loss or replay of a complete old image defeats freshness and availability. Therefore the time
machine is never recovery custody or a rollback witness. Workstream 8 remains responsible for
protected state and an external monotonic witness.

### Sparse-custody threats

ADR 0295 treats signed metadata knowledge, selected content custody, and complete backup recovery as
three different facts. A sparse receiver validates the complete record/manifest graph and all signed
digest/size declarations, but it does not request or repair unselected bytes. Status and maintenance
therefore expose `partial`; a successful pull cannot be cited as proof that omitted bytes exist.

Interest paths are canonical owner-local configuration. Remote frames carry neither rules nor a
destination, so a malicious writer cannot expand filesystem scope. The policy-bound projection
marker prevents widening from interpreting formerly unprojected absence as deletion. Missing newly
selected bytes fail projection closed. GC can quarantine locally present unselected objects, and a
pin roots only the selected content closure; operators must not narrow and collect the only copy.
ADR 0296 consumes the frozen wire's authenticated exact absence as availability evidence and advances
only that immutable digest through an owner-selected bounded source set. The primary alone chooses
the signed frontier; complementary sources cannot author, activate, or choose paths. Exhaustion still
fails closed, serial probes can amplify round trips, and recovery custody remains separate.

ADR 0297 prevents transient counters or expected sparse omission from being presented as durable
health. The local device signs one fixed content-free observation after verifying selected custody
and authenticated workspace state; a changed policy is explicit, source exhaustion is red, and
structural corruption refuses a color. The same-storage signature cannot detect replay of an older
valid record, and green expressly does not establish an independent copy or successful restore.

ADR 0298 prevents the shareable diagnostics join from becoming a namespace dictionary or durable
tracking surface. It exports only anonymous aggregate counts after local signature verification;
names, paths, principals, content digests, namespace/policy commitments, signatures, and stable slots
are absent. Aggregate counts still reveal activity and fleet shape, the recipient cannot authenticate
the emitter, omitted or replayed local records remain possible, and the permanent no-witness/no-backup
qualifiers must survive inspection.

ADR 0299 treats host probing itself as a process-safety and privacy boundary. The running Agent does
not fork to test seccomp, MDWE, or Landlock; it passively samples support and labels the weaker grade.
Only a closed reduction reaches diagnostics v3. Cgroup roots, sudo paths, controller names, kernel
text, environment, and arbitrary errors remain local. These observations can be stale immediately,
do not prove the final PTY child, and do not establish sudo authorization or kernel integrity.

### Signed tree-v2 metadata corruption

The current branch pointer, referenced immutable record and manifest, signed
workspace, and signed maintenance state are cryptographic authority-bearing
roots. ADR 0337 requires startup and `sync-repair` to authenticate all five
before effects or a verified repair result. A byte-invalid record is retained
unchanged and blocks the namespace until an operator restores reviewed exact
bytes externally. An attacker with write access can therefore still cause
denial of service, but cannot make the corrupt bytes authoritative through
these paths or rely on repair to erase the evidence.

ADR 0339 makes that distinction operator-visible: a successful repair reports
`rollback-witness=0|1`. Direct tests replay exact valid-old branch, workspace,
and maintenance records with matching old local guards while a separate
current witness refuses both live and cold access. Immutable record and
manifest names remain content-addressed; changing bytes at a current digest
path is not a coherent valid-old substitution. This protects only the
semantic roots committed to the configured witness, and only while that
witness is in a genuinely independent administration/storage/checkpoint
domain.

Receipt v2's stopped-task co-resident byte corruption is a stronger integrity
construction than ADR 0337's isolated cells, but it is not an atomic storage
transaction or an independent observation of guest logs. Exact restoration is
trusted operator input; the bounded gate does not prove recovery custody,
provenance, or availability under concurrent corruption.

### Writable projection descriptor races

ADR 0338 catches an edit through an already-open descriptor between the last
pre-exchange scan and `RENAME_EXCHANGE`, and in the immediate post-exchange,
pre-validation interval: IoTox checks the obsolete staged tree, including the
excluded projection closure, and preserves ambiguity rather than deleting it.
Canonical projection markers are bound to the authenticated active manifest so
a malformed marker cannot masquerade as a sparse-policy change. This remains a
bounded detection window. A same-UID writer, writable mapping, or descriptor
write after final old-tree validation begins can still race staging removal;
open-descriptor remount/restart behavior awaits ADR 0340.

## 18. Claims not made

IoTox rev0051 does not claim:

```text
production readiness
independent security audit
formal cryptographic verification
hardware-backed secrets
production-qualified hardware-anchored or independently deployed rollback resistance
encrypted local journals
device-authenticatable or rollback-witnessed diagnostic exports
automatic command expiry on untrusted clocks
safe cancellation after a possibly peer-visible attempt, or physical actuation
Tor/I2P anonymity, large privacy-pinned I2P payloads, or process-loss/long-running actual-Tor behavior beyond the retained bounded samples
mobile background suitability
production-supported or default-on terminal service
full sandbox containment or guaranteed control of escaped descendants
PTY session recovery across daemon restart
disaster recovery, unrestricted sole-system-of-record safety, permanent sync purge, or hostile/large-tree behavior beyond
the named 16-candidate and 4,096-entry qualification bounds
compliance or safety certification
```

The safe claim is narrower: owned C++ code process-tests one exact root outgoing request and seven
established-peer write meanings over an exact c-toxcore ABI peer. It proves complete-address request
framing, explicit keyless parse evidence, exact accept/reject/remove records, key-bound deletion
despite numeric-gap reuse, byte-preserving live human text with IDs/receipts, durable authorized
read-only commands with restart/duplicate semantics, and finite local-file send/receive/control with
exact chunks, two-sided pause truth, and no-clobber publication. rev0020 also tests canonical terminal
policy generations, sealed process launch, bounded PTY lifecycle, the default-off host activation
gate, bilateral bit-23 negotiation, live packet-`0xA2` authority denial, retained outbound behavior,
round-robin service bounds, revocation/offline/shutdown fencing, a pure bounded controller, an
owner-private same-user terminal socket, canonical local framing, and one-binary terminal failure
paths. It does not yet prove daemon-restart recovery, multiple local terminal streams, complete
separate-process reconnect lifecycle, two-guest Sandwurm terminal latency, broad network suitability,
target-hardware suitability, or complete confinement. Separate dated evidence still verifies only
the named pinned c-toxcore and founding-host normal-native/TCP-relay fixtures.
