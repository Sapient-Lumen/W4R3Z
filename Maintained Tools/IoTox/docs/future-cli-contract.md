# Future IoTox command-line contract

Status: accepted command vocabulary for planned work; commands in this document are not implemented
unless they also appear in `iotox --help`. `routes`, `routes-watch`, `sync-namespaces`, `sync-publish`,
`sync-pull`, `sync-cancel`, `sync-activate`, the unfiltered `sync-status`, and the generic-command
form `command FRIEND profile.status.set available|away|busy [PRIORITY]` are now implemented.
The exact-HEAD form `command FRIEND update.stage HEAD_RECORD_HEX [PRIORITY]` is also implemented;
it stages only and inherits the durable command journal.

## Naming rules

IoTox keeps one flat kebab-case verb namespace. Read/show commands use stdout, mutation commands fail
unless their complete input is explicit, and streaming views end in `-watch`. `-hex` and `-stdin`
variants exist only where they preserve the same bounded typed operation; they are not added merely
for symmetry. Compatibility aliases are exceptional and never create a second semantic path.

New commands must join the same typed Agent/control path as the filesystem surface. A command name is
not permission: every effect still requires the applicable local ownership and remote authority.

## Implemented route startup

```text
iotox run ... --network tox/native [--native-tcp-only]
iotox run ... --network tox/tor --socks5-proxy IP:PORT \
  --bootstrap IP:PORT:KEY --tcp-relay IP:PORT:KEY
```

`tox/native` remains the default and may use the compiled node catalogs unless explicitly replaced
or disabled. `tox/tor` is a complete route choice, not an additive proxy hint: it suppresses those
catalogs, forces TCP-only/no-discovery/no-native-DNS policy, and requires numeric proxy, bootstrap,
and relay endpoints. Hostnames, incomplete topology, proxy use under native, and silent fallback are
errors. This construction surface does not claim that the SOCKS endpoint is actually Tor; see ADR
0190 and `networks.md`.

When `--state` and `IOTOX_STATE_PATH` are absent, startup now selects route-scoped savedata under one
state directory: `device.toxsave` for native and `device.tox-tor.toxsave` for Tor. This preserves one
directory-scoped stable device identity and authority ledger while preventing the observable Tox key
from crossing route contexts by default. An explicit state path is a compatibility and linkability
choice, not a privacy-preserving alias (ADR 0198).

The implemented multi-route startup keeps v1 as its compatibility default. Adding
`--enable-private-route-bindings` beside the required `--enable-route-workers`, `--route-set`, and
`--route-worker-root` options instead sends full inventory only over an authority-authenticated
primary and member-only proofs over auxiliaries. Repeatable
`--route-worker-network KEY=tox/native|KEY=tox/tor@NUMERIC_PROXY` selects one exact auxiliary's local
context. Implemented repeatable `--route-worker-bootstrap KEY=HOST:PORT:KEY` and
`--route-worker-tcp-relay KEY=HOST:PORT:KEY` options replace that worker's inherited lists when a
route context needs independently reachable rendezvous infrastructure. All mappings, list bounds,
and TCP/Tor constraints fail closed before any worker starts. Route-set v2 signs the coarse network
class while those exact endpoint/catalog mappings remain local private deployment policy
(ADRs 0200–0202 and 0225).

## Near-term operator gaps

### Host and configuration preflight

Status: implemented by ADRs 0285, 0286, and 0290.

```text
iotox host-capabilities
iotox run-check [AGENT_OPTIONS]
iotox config-lint PATH
iotox run --config PATH [AGENT_OPTION_OVERRIDES]
```

`host-capabilities` is read-only and reports the exact kernel/runtime primitives IoTox can prove:
pidfds, seccomp, MDWE, Landlock ABI, cgroup-v2 controllers/delegation, PSI files/triggers, relevant
resource interfaces, privilege-escalation prerequisites, and a privileged sudo helper. Sudo
discovery deliberately reports its authorization policy as `not-probed`; this read-only command does
not run sudo or inspect the complete sudoers/PAM decision. It distinguishes unavailable, available,
delegated, and live-proved states where those categories apply.

`run-check` applies the same parsing, normalization, provider/path/policy/profile/route/cgroup
preflight as `run`, but creates no listener, network identity, cgroup, PTY, lock, or durable mutation.
`--config` uses one owner-only canonical shell-free indexed-argument record. Command-line option
groups replace explicit same-named file groups; duplicate non-repeatable fields, unknown fields,
unsafe ownership, symlinks, and incomplete policy groups are errors. Existing recovery-capable
authority/command/incarnation opens and final PTY-child kernel enforcement are reported as deferred
to `run`, so success means ready for start rather than started. There is no automatic
`config-export`: runtime argv and local paths may be sensitive, and a mechanical dump could be
mistaken for a reviewed deployment policy. See `agent-configuration.md`.

### Protected state and authority witness

Status: fscrypt-v2 closure and authority coordinator implemented by ADR 0303; authenticated remote
service implemented by ADR 0305; application/Ratox startup lanes implemented by ADR 0306; signed
route-generation lane implemented by ADR 0307; complete Ratox-policy lane implemented by ADR 0308.
The exact mutable-command effect frontier is implemented by ADR 0309; the complete namespace and
automation policy tree by ADR 0310; update policy/lifecycle by ADR 0311; per-namespace single-writer
four-root freshness by ADR 0312; witness-service checkpoint floors by ADR 0313; and tree-v2
frontier/workspace/maintenance freshness by ADR 0314. ADR 0360 adds the checkpoint custody report.

```text
iotox witness-domain-generate
iotox witness-service-keygen OUTPUT
iotox witness-authority-enrollment IDENTITY LEDGER DOMAIN_HEX EPOCH
iotox witness-incarnation-enrollment IDENTITY STATE application|ratox DOMAIN_HEX EPOCH
iotox witness-route-enrollment IDENTITY ROUTE_SET GENERATION_STATE DOMAIN_HEX EPOCH
iotox witness-terminal-policy-enrollment --config PATH
iotox witness-terminal-policy-commit --config PATH
iotox witness-command-effects-enrollment --config PATH
iotox witness-sync-policy-enrollment --config PATH
iotox witness-sync-policy-commit --config PATH
iotox witness-update-enrollment --config PATH
iotox witness-sync-guarded-enrollment --config PATH NAMESPACE
iotox witness-service-enroll ROOT SERVICE_IDENTITY ENROLLMENT_HEX
iotox witness-service-checkpoint ROOT SERVICE_IDENTITY OUTPUT
iotox witness-service-checkpoint-custody SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX \
  [custody-system=TEXT custody-generation=TEXT custody-failure-domain=TEXT]
iotox witness-service-checkpoint-verify CHECKPOINT SERVICE_PUBLIC_KEY_HEX
iotox witness-service-serve ROOT SERVICE_IDENTITY HOST PORT [CHECKPOINT_FLOOR]
iotox run ... --authority-witness-host HOST --authority-witness-port PORT \
  --authority-witness-server-key HEX --authority-witness-domain HEX \
  --authority-witness-epoch N [--authority-witness-timeout-ms N] \
  [--authority-witness-intent PATH] \
  [--witness-application-incarnation \
   --application-incarnation-witness-intent PATH] \
  [--witness-ratox-incarnation --ratox-incarnation-witness-intent PATH] \
  [--witness-route-generation --route-witness-intent PATH] \
  [--witness-terminal-policy \
   --terminal-policy-witness-checkpoint PATH \
   --terminal-policy-witness-intent PATH] \
  [--witness-command-effects \
   --command-effect-witness-checkpoint PATH \
   --command-effect-witness-intent PATH] \
  [--witness-sync-policy \
   --sync-policy-witness-checkpoint PATH \
   --sync-policy-witness-intent PATH] \
  [--witness-update-lifecycle \
   --update-lifecycle-witness-intent PATH] \
  [--witness-sync-guarded-state]
```

Each device-signed enrollment is an explicit, no-replace binding of one exact committed lane head.
Application and Ratox records are enrolled separately and then advance once per selected startup.
The route record is separately enrolled at the reviewed artifact's generation/digest. After that
ceremony, only the exact next signed generation may be adopted; gaps and whole-pair rollback refuse.
Normal network traffic cannot enroll or reset state. Requests are signed by the stable device;
responses are nonce-bound and signed by the pinned dedicated witness identity. `run` authenticates
and reconciles the service before runtime creation. The backend is production-capable, but the
operator must actually place it outside the Agent's disk/admin/snapshot/failure domain and protect
its own persistence from rollback. Same-host VMs are protocol evidence, not independence. See
`protected-local-state.md`.

The terminal enrollment hashes the complete strictly loaded profile/binding tree and mutates
nothing. Later offline profile administration is not auto-authorized: `witness-terminal-policy-commit`
is the explicit review boundary and advances exactly one external position. Startup may finish an
already prepared exact intent but never creates a transition for an unrecognized tree.

Command-effect enrollment binds the existing signed journal frontier. Thereafter each exact
authorized mutable command commits its principal/authority/request-bound `STARTED` identity through
the service before the effect. Read-only/result/delivery writes do not move this lane. No manual
commit verb exists, and unavailable or contradictory witness state prevents the effect. Retained
effect history makes this replay protection rather than a generic exactly-once claim.

Sync-policy enrollment binds the complete strict namespace and signed automation tree. Ordinary
Agent-mediated policy mutations automatically commit the exact candidate before live activation.
An offline edit requires a stopped Agent, explicit `witness-sync-policy-commit`, and restart; the
running Agent never swaps its frozen policy because another process moved the witness. This policy
lane does not include per-namespace runtime state or content; separate ADRs 0312 and 0314 cover the
named semantic roots below.

Per-namespace guarded-state enrollment requires that complete policy lane. It binds the signed
published, accepted, activated, and retained roots for a single-writer namespace under lane 9, or
the live branch frontier plus signed workspace and maintenance state for tree-v2 under lane 10.
Every configured namespace must be enrolled before selected startup. Live add/remove is refused;
content, quarantine, projection/current pointers, health, and backup remain outside the commitment.

### Terminal profile administration

Status: implemented by ADRs 0285--0287. Store-reading and mutation commands require the same explicit
`--ratox-profile-store PATH` used by host activation; the expected owner defaults to the effective
UID and may be pinned with `--ratox-profile-owner-uid N`.

```text
iotox terminal-profile-list
iotox terminal-profile-show PROFILE_ID
iotox terminal-profile-template PROFILE_ID
iotox terminal-profile-lint PATH
iotox terminal-profile-install PATH
iotox terminal-profile-remove PROFILE_ID
iotox terminal-profile-bind PRINCIPAL_PUBLIC_KEY_HEX PROFILE_ID
iotox terminal-profile-unbind PRINCIPAL_PUBLIC_KEY_HEX
iotox [--shell PATH] terminal-shell-discover [USER]
iotox [--shell PATH] [--allow-sudo] terminal-profile-shell-template PROFILE_ID [USER]
iotox --shell PATH --toolbox-dir PATH [--allow-sudo] \
  terminal-profile-toolbox-template PROFILE_ID [USER]
```

These commands author the existing canonical profile/binding store; they do not invent a parallel
configuration format. Install is descriptor-relative, atomic, synchronized, strictly reread, and
validated against the complete store under an owner-local mutation lock. Removal fails while a
binding still names the profile. An already-running session retains its immutable resolved profile
and generation until exit; a later store mutation cannot retarget it. Binding remains owner-selected:
the remote peer never supplies a profile or arbitrary argv.

Shell discovery resolves a named or numeric non-root account, its canonical regular ELF login shell,
and its complete bounded NSS group vector. The shell template freezes those values and a deterministic
PATH into profile v7 with exact shell/toolbox byte pins. Its ordinary output is baseline and cannot
gain privilege. `--allow-sudo`
requires a discovered set-ID-root or file-capability sudo helper and emits a separate compatibility
profile with explicit privilege escalation enabled; it still starts as the non-root account and does
not grant, edit, or probe sudoers/PAM authorization. All generated profiles remain disabled until
reviewed.

The toolbox template is the explicit optional rescue variant. It requires a qualified directory
containing Toybox plus an independently qualified static shell, starts the shell with `-i`, prefixes
that directory to the deterministic PATH, and remains baseline/no-elevation unless `--allow-sudo` is
separately selected. It is not automatic shell fallback and changes no peer framing.

### Terminal lifecycle visibility

Status: implemented by ADR 0285 for the Agent's single retained controller session. This is not a
host-wide inventory of inbound PTYs.

```text
iotox terminal-sessions [PEER]
iotox terminal-close SESSION_ID_HEX [PEER]
iotox terminal PEER --batch
```

`terminal-sessions` lists only content-free resumable identity and lifecycle facts. `terminal-close`
uses the existing authenticated CLOSE/process-reap path; it is not named `terminal-kill` because a
Unix signal is an implementation detail, not the protocol effect. Batch mode keeps the same fixed
owner-selected profile and byte-stream framing while avoiding local raw-TTY setup. It does not accept
a remote command line. The already implemented
`terminal-resume SESSION_ID_HEX [PEER]` remains the only qualified post-route-loss
mutation: ADR 0197 requires a higher authenticated epoch and exact prior session/incarnation/byte
positions. A heartbeat warning never invokes it automatically.

The implemented ADR 0289 Mosh-like owner-local extension is:

```text
iotox terminal PEER --reconnect
```

It keeps one local invocation alive after authoritative offline, waits for a strictly higher
authenticated epoch, and resumes only the exact
session/incarnation/profile it originally opened or attached. It never turns a heartbeat warning
into resume authority, retries an input whose commit is ambiguous, silently opens a replacement
shell, or survives Agent/host death. A process gate forces two unavailable resume attempts before an
exact higher-generation success. ADR 0316 now carries the same production process through two
sequential genuine losses on direct UDP and forced TCP with exact progress between generations
1, 2, and 3. Longer and overlay-route soaks remain; the command changes no Ratox v1 frame.

### Diagnostics

Status: authenticated recorder/export core implemented by ADR 0291; ADR 0297 defines signed
namespace health, ADR 0298 joins only anonymous aggregates to the shareable bundle, and ADR 0299
adds normalized passive host capabilities. ADR 0317 implements command-name completion from the
complete typed CLI registry.

```text
iotox diagnostics-export PATH
iotox diagnostics-inspect PATH
iotox completion bash|zsh|fish
```

The implemented v3 payload contains version/revision, a bounded closed event/counter tail, one
current closed observation, recorder failure truth, anonymous aggregate tree-v2 health, normalized
host capability grades/masks, and a
path/key/endpoint-free structural configuration commitment. It excludes identities, addresses,
terminal bytes, messages, commands, filenames, namespace names/commitments, paths, endpoints, time,
phrases, keys, signatures, raw config, and ledger contents.
Its digest proves byte integrity, not device authorship; inspect every bundle before sharing. See
`diagnostics.md`. ADR 0317 established shell completion from one complete registry; ADR 0319 added
the recovery verifier, ADR 0360 adds witness checkpoint custody, and the second native ergonomics
gate brings its current population to 210 spellings. The registry remains shared with the help index and parser
classification tests, so completion is not an independent command description. It
does not complete dynamic peers, paths, namespaces, or typed operands.

### Route-set visibility

```text
iotox --identity PATH route-set-create OUTPUT GENERATION COORDINATOR_KEY MEMBER...
iotox --identity PATH route-set-create-v2 OUTPUT GENERATION COORDINATOR_KEY MEMBER...
iotox run ... --sync-route-policy fixed|adaptive
iotox run ... --sync-route-failover available|fail-closed
iotox routes
iotox routes-watch
```

`route-set-create` is implemented offline creation-only authoring. Each `MEMBER` is
`KEY:protected|bulk:tcp|udp|either:WORK:RESTARTS:EXPIRES_MS`; two through sixteen exact members are
required. The command signs with an existing stable device identity, canonical-verifies the result,
and refuses replacement. It neither mutates a live coordinator nor provisions route savedata.
`route-set-create-v2` requires
`KEY:protected|bulk:tcp|udp|either:tox/native|tox/tor|tox/i2p:WORK:RESTARTS:EXPIRES_MS`,
signs that class, and requires the coordinator to be the sole protected member. V1 remains an exact
compatibility author and cannot encode this field (ADR 0225).
`--sync-route-policy` is implemented only for explicit sync plus route-worker construction. `fixed`
is the default stable-key reference; `adaptive` makes bounded load-aware choices only at admission or
mandatory reassignment and never migrates healthy work.

`--sync-route-failover` is also implemented only with sync and route workers. `available` preserves
qualified whole-object replacement; `fail-closed` fences loss and leaves the exact job awaiting
explicit cancellation/new pull without selecting another member. This is local process policy, not
yet signed per-job privacy intent (ADR 0220).

The two implemented read-only commands expose the coordinator's content-free route-set generation,
member role, connection class, signed network class (or `unspecified` for v1), lifecycle state,
admitted/active work, restart count, and last typed failure.
They do not reveal private keys or peer content. `routes-watch` is the streaming twin of the same
coherent snapshot schema, not an independent event truth.

There is deliberately no opportunistic `route-add`, `route-replace`, or `bond` command. Route
membership binds a Tox public key to the stable device principal and coordinator generation through
reviewed owner policy. An unauthenticated connection cannot become replacement capacity, and a
missing required route cannot silently push work or Ratox onto another member. The complete planned
contract is in `multi-route-plan.md` and ADR 0108.

## Verified synchronization commands

### Namespace administration

```text
iotox sync-namespaces
iotox sync-namespace NAMESPACE
iotox sync-namespace-template NAMESPACE ROOT WRITER_PUBLIC_KEY_HEX [SUBSCRIBER_PUBLIC_KEY_HEX...]
iotox sync-namespace-template-tree NAMESPACE ROOT WRITER_PUBLIC_KEY_HEX [SUBSCRIBER_PUBLIC_KEY_HEX...]
iotox sync-namespace-lint PATH
iotox sync-namespace-install PATH
iotox sync-namespace-update PATH
iotox sync-namespace-remove NAMESPACE
```

A canonical namespace record selects its local root, accepted stable writer device keys, subscriber
principals, storage and staging quotas, retained-revision policy, activation policy, and permitted
sync engine. Names are local policy identifiers, not remote paths.

`sync-namespace-template`, `sync-namespace-template-tree`, `sync-namespace-lint`, creation-only `sync-namespace-install`, quiescent
`sync-namespace-update`, and policy-only `sync-namespace-remove` are implemented. The template emits
the canonical range-v1/manual record with bounded defaults; its output may be reviewed or privately
edited and must lint canonically before the live same-user Agent consumes it. The tree form selects
`treepack-v1` with the same explicit manual-activation defaults. Update may replace only
activation and canonical writer/subscriber membership; ID, root, engine, and quotas are immutable.
Removal leaves content and all signed namespace state untouched. Exact retries are generation-stable.
The single-namespace detail view remains contract, and persistent automatic subscriptions remain a
separate future scheduler concern.

The standalone toxsync `head-keygen` command remains a component/research tool. Integrated IoTox HEADs
should be signed by the publishing IoTox device identity, while fresh authority-ledger capabilities
authorize principals to request namespace administration, publication, subscription, or activation.
The subscriber pins accepted writer device keys in its local namespace record. This avoids creating a
second ambient ownership root beside IoTox identity and RecallRoot. ADR 0091 and
`protocol-authority-v3.md` freeze the names and implemented v3 bits; the v2 mask remains unchanged and
grants no sync authority:

```text
sync.admin
sync.publish
sync.subscribe
sync.activate
```

### Publication, convergence, and activation

```text
iotox sync-publish NAMESPACE PATH
iotox sync-subscribe FRIEND NAMESPACE
iotox sync-unsubscribe FRIEND NAMESPACE
iotox sync-plan FRIEND NAMESPACE
iotox sync-pull FRIEND NAMESPACE \
  [available|fail-closed [any|tox/native|tox/tor|tox/i2p]]
iotox sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]
iotox sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]
iotox sync-source-add JOB_ID FRIEND
iotox sync-replica-import NAMESPACE SIGNED_HEAD_PATH
iotox sync-status
iotox sync-watch NAMESPACE [--samples N] [--interval SECONDS]
iotox sync-freeze NAMESPACE
iotox sync-unfreeze NAMESPACE
iotox sync-freeze-status NAMESPACE
iotox sync-cancel JOB_ID
iotox sync-verify NAMESPACE [REVISION]
iotox sync-repair NAMESPACE
iotox sync-gc NAMESPACE dry-run|quarantine
iotox sync-activate NAMESPACE REVISION
```

The implemented tree-v2 lifecycle surface is:

```text
iotox sync-checkpoint NAMESPACE
iotox sync-pin NAMESPACE BRANCH_RECORD_HEX
iotox sync-unpin NAMESPACE BRANCH_RECORD_HEX
iotox sync-retention NAMESPACE
iotox sync-gc NAMESPACE dry-run|quarantine
iotox sync-restore NAMESPACE
iotox sync-writer-cutoff NAMESPACE WRITER_PUBLIC_KEY_HEX
```

Checkpointing refuses unresolved conflicts. Quarantine is recoverable and has no purge companion.
A writer cutoff is exact owner-local policy and must be repeated on every survivor; it is neither a
group-membership transaction nor general authority revocation (ADR 0275).

The implemented ordinary M5C entrances are:

```text
iotox sync-create NAMESPACE PATH [INTERVAL_SECONDS]
iotox sync-create NAMESPACE PATH read-write [INTERVAL_SECONDS]
iotox sync-create NAMESPACE PATH read-write INTERVAL_SECONDS \
  executable-v1|owner-mode-v2 [include=PATH|exclude=PATH...]
iotox sync-share NAMESPACE FRIEND read-only|read-write
```

The trust-graduation plan's first read-only local preflight entrance is implemented by ADR 0288:

```text
iotox sync-doctor PATH [one-writer|read-write] [INTERVAL_SECONDS] \
  [executable-v1|owner-mode-v2] [include=PATH|exclude=PATH...]
iotox sync-doctor-configured --config PATH NAMESPACE
iotox sync-recovery-verify BACKUP_ROOT RESTORED_ROOT [MAXIMUM_BYTES [MAXIMUM_ENTRIES]] \
  [backup-system=TEXT backup-generation=TEXT backup-failure-domain=TEXT restore-provenance=TEXT]
```

`sync-doctor` performs the production source inventory and policy interpretation without creating a
namespace or writing managed state. It hashes selected files and reports transformations,
entry/object/byte estimates, conservative first-revision store/staging minima, default bounds, and
source-filesystem availability. It explicitly reports managed-store headroom as `not-probed` until a
deployed Agent configuration supplies the exact store and nondefault quotas. ADR 0315 implements the
configured form: it joins that exact signed automation source to live immutable-store/staging
occupancy, remaining quotas, and current filesystem headroom without starting the Agent or creating
missing namespace state. See `sync-doctor.md` and `sync-trust-graduation.md`; either clean report is a
point-in-time admission check, not a reservation, backup, or promise that storage honors `fsync`.
ADR 0319 adds the separate exact external-restore comparison. ADR 0360 lets the operator attach
all-or-none backup-system, backup-generation, backup-failure-domain, and restore-provenance labels
to that report. It reads neither Agent configuration
nor live namespace state and refuses to infer recovery custody or restore provenance from two
paths; see `sync-recovery-rehearsal.md`.

`sync-create` infers `content-v2` for a regular file and `treepack-v1` for a directory, installs a
managed sole-writer namespace, and starts publication. `sync-share` reads RecallRoot from standard
input, binds the live selector to its exact-v3 stable principal, and adds only `sync.subscribe` plus
subscriber membership. It does not configure the recipient's local root, writer authorization, or
follow/activation policy.

ADR 0273 adds the pairwise read-write form. Each side independently creates the same namespace at a
locally chosen absolute directory and reciprocally runs `sync-share ... read-write`. The share grants
the exact proven peer `sync.publish|sync.subscribe`, adds writer/subscriber membership, and binds
local bidirectional automation to that stable principal. It never selects or creates the remote
path. The format can represent more writers, but the first ordinary automation surface binds one
remote writer exactly. Signed automation-v2 subsequently generalizes that binding to a bounded
sorted set. ADR 0278 adds recipient-local component-prefix selection and exact private owner `r/w/x`
metadata. Exclude wins; the peer cannot select a path or learn rule names from status.

The implemented expert automation surface is:

```text
iotox sync-auto-publish NAMESPACE PATH [INTERVAL_SECONDS]
iotox sync-follow FRIEND NAMESPACE pull|verified [INTERVAL_SECONDS]
iotox sync-automation
iotox sync-automation-remove NAMESPACE
```

These commands configure an owner-local scheduler; they are not new peer operations. Publication,
pull, and activation still use the implemented commands and protocol below. `sync-follow` resolves
the supplied live friend to its currently proven stable principal before committing policy. The
record never persists a friend number. `verified` authorizes only exact accepted-HEAD activation
under the namespace's existing activation mode. See `everyday-sync-plan.md` for the signed record,
retry, restart, and non-goal contract.

The current default-off vertical slice implements `sync-pull FRIEND NAMESPACE
[available|fail-closed [ROUTE_CLASS]]` as an exact durable
HEAD-plus-whole-object request/resume, `sync-status` as a content-free bounded worker/job snapshot,
and `sync-cancel JOB_ID` as terminal process-local cancellation. The pull response and status expose
the same nonzero job ID. Cancellation is not durable resumption state: restart recovery already fences
every lost transport handle from signed attempt truth.
For an active content-v2 or tree-v2 pull, `sync-source-add JOB_ID FRIEND` adds one explicitly selected
primary Tox peer. The peer must negotiate that engine and independently prove exact-v3
`sync.publish` plus namespace writer membership. For content-v2, the original pull peer remains the
sole HEAD authority and every source proves exact availability windows. For tree-v2, the original
peer remains the sole frontier authority and each source answers the existing exact object probe;
authenticated `absent`/`unavailable` advances that digest to the next source. No source can replace
the candidate/frontier or activate it. Status reports per-job and per-source request/result facts.
`sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]` is the atomic initial entrance when the source
set is already known: it authenticates the primary and up to 15 auxiliaries, registers all
auxiliaries before dispatching the primary HEAD/frontier, and cancels the new job if setup or dispatch
fails. Tree-v2 currently uses primary lanes only. This avoids racing a cached root/inventory result
against later local `sync-source-add` requests.
`sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]` is the implemented atomic
mixed-route entrance. The named class must be `tox/native`, `tox/tor`, or `tox/i2p`; Agent requires
one independently authenticated primary session and one ready content-capable auxiliary worker in
that exact class for every source. All auxiliary carrier bindings freeze before the sole primary
HEAD request leaves. Availability, object, FileId, CTA1, and terminal effects use those exact worker
incarnations, while writer proof, HEAD admission, HEAD-last acceptance, and activation remain on the
primary authority model. Loss is fail-closed for the whole job. This does not claim the primary
authority sessions themselves traversed the named route. The one-source
`sync-pull FRIEND NAMESPACE fail-closed tox/tor` form is now Sandwurm-qualified with native primary
authority/HEAD and an exact actual-Tor content carrier. The multi-source spelling is also qualified
with two independently authorized native publishers, distinct exact Tor worker identities,
complementary source contribution, and explicit activation. `sync-status` emits one bounded
owner-private `content-source-job=` record per source so the principal-to-carrier decision is
inspectable; it is not a new command or peer frame.
Repeating a `SOURCE` selector in this routed form is intentional: each occurrence requests another
distinct exact ready carrier for the same stable principal and primary authority session. Agent
refuses the whole entrance if the named class cannot supply all requested distinct carriers.
`sync-pull-multi` continues to reject duplicate selectors. Each source-path status row includes
`requested`, `committed`, and `fetched-bytes`; route-local friend numbers may be equal because they
belong to different worker transports. Whole objects are assigned to one path, exact path loss fails
the job, and no byte striping, balancing, fallback, or automatic route count is implied (ADR 0269).
The Agent run surface also implements `--max-sync-content-lanes N` (`1..64`, default `1`). This is a
process ceiling, not a peer request: signed namespace `maximum-lanes` and
`maximum-outstanding-requests` quotas may only reduce it. `sync-status` exposes the effective process
cap as `content-lane-cap`, each pull's `active-lanes`, and one owner-private `content-lane-job=` row
per exact request/FileId/carrier binding. Root and HEAD phases remain serial. ADR 0262 qualifies a
two-lane one-source pull over direct UDP and forced TCP without claiming byte or route striping.
ADR 0263 measures signed effective caps `1/2/4/8` on a stable process/session: cap 4 is the smallest
promising forced-TCP bulk setting, while the public default remains one and no automatic route-based
tuning is accepted.
The tree-v2 subscriber now has its own process cap:

```text
iotox run ... --max-sync-tree-lanes N
```

`N` is `1..64` and defaults to `4`. It is still only a local ceiling: signed namespace
`maximum-lanes` and `maximum-outstanding-requests` can only reduce the active exact-object window.
`sync-status` exposes `tree-lane-cap`, each tree pull's `active-lanes`, and one owner-private
`tree-lane-job=` row per request/FileId/source binding. Retained tree pull rows also expose the final
local apply shape with `reconcile-` prefixes after completion. The compatibility `active-file` and
`active-file-number` fields remain populated only for zero/one-lane tree jobs.
`sync-replica-import NAMESPACE SIGNED_HEAD_PATH` is a separate owner-local custody operation for a
content-v2 partial source. It verifies the original foreign writer and complete manifest graph,
enforces a same-writer linked chain, and stores a device-signed availability-only record. It is not
publication, HEAD acceptance, activation, or automatic network replication.
For whole immutable objects, an availability-permitted same-process route replacement may reuse an
exact private prefix while retaining fresh attempt, message, FileId, and carrier identities.
`sync-status` exposes only the aggregate `retained-partials` gauge and saturating
`retained-attempts`, `retained-bytes`, `retention-fallbacks`, `resumed-attempts`, `resumed-bytes`,
`restart-resumed-attempts`, and `restart-resumed-bytes` counters;
full content digest verification remains mandatory before commit. Fail-closed pulls, range bundles,
and terminal/cancel paths do not reuse that live-loss prefix (ADR 0224). ADR 0234 separately permits
a fresh authorized post-restart pull to inherit a strict device-signed prefix for the identical
whole object; it never resurrects the prior job or transport handle.
An omitted failover value captures the Agent's configured default. An explicit value is frozen on
that job; retries with a conflicting value fail, and carrier-loss handling consults the job rather
than later process configuration. This is per-job owner-local intent; the authorized member class is
independently signed in route-set v2 (ADRs 0221 and 0225).
An explicit route class is also frozen on the job and filters initial auxiliary placement plus every
permitted replacement. `any` retains primary fallback; a named class requires an exact authenticated
auxiliary worker and otherwise leaves the HEAD request retryable without sending object bytes. The
class is enforced from the worker's constructed local network context and may be joined to the exact
stable-device-signed v2 member class (ADRs 0222 and 0225).
`sync-namespaces` lists policy summaries without paths or principals. `sync-publish` accepts one
absolute regular file for range-v1/content-v2 or one owner-controlled directory for treepack-v1 and
constructs the engine's bounded canonical metadata. `sync-repair NAMESPACE` verifies the local strict object store and
quarantines only digest-named private final objects with content/identity mismatches. It is an
explicit local maintenance action, not part of pull convergence. `sync-gc NAMESPACE dry-run` reports
guarded rooted/candidate counts without mutation; `quarantine` moves only exact descriptor-pinned
unreferenced objects into namespace-local `gc-quarantine`. There is intentionally no `apply` or purge
mode. `sync-activate` consumes the exact
32-byte accepted HEAD record printed by status, not a generation number or implicit newest revision.
The remaining verbs in these blocks outside the implemented namespace creation subset are still contract, not implementation; a
namespace-filtered status view may be added without
changing the existing no-argument command.

`sync-publish` constructs an immutable range file, deterministic treepack, or local flat/paged
content-v2 revision, commits its complete object fabric, and publishes the next signed HEAD last. The
local install primitive follows the inverse subscriber
ordering: evaluate the candidate HEAD first, verify and publish immutable bytes, then commit accepted
HEAD state last. `sync-plan` is read-only and reports bounded counts and bytes already
available/needed without leaking paths. `sync-pull` creates or resumes a durable convergence job.
`sync-activate` is always a distinct locally authorized operation; completed transfer does not imply
activation.

The first vertical slice used one source, whole-object treepack-v1, and range-v1 file reuse. Paged
content-v2 and explicit job-scoped primary-peer sources now use the same command family; tree range
reuse remains later. Engine selection remains local namespace policy rather than a separate user
verb.

### Retention

```text
iotox sync-pin NAMESPACE BRANCH_RECORD_HEX
iotox sync-unpin NAMESPACE BRANCH_RECORD_HEX
iotox sync-retention NAMESPACE
iotox sync-checkpoint NAMESPACE
iotox sync-gc NAMESPACE dry-run
iotox sync-gc NAMESPACE quarantine
iotox sync-restore NAMESPACE
iotox sync-writer-cutoff NAMESPACE WRITER_PUBLIC_KEY_HEX
```

For content-v2 and treepack-v1, garbage collection remains descriptor-guarded against publication,
acceptance, activation, replica, and retention roots. Tree-v2 additionally authenticates current
branches, explicit exact-record pins, signed workspace manifests/frontiers, and checkpoint floors.
`quarantine` recomputes the guarded plan and moves only exact verified candidates; it never unlinks,
purges, or accepts a caller path. `sync-restore` is tree-v2-only and reauthenticates quarantined bytes
before a no-replace move. A future purge is not reserved under the misleading name `apply`; it
requires a separate witness-dependent design decision.

There is deliberately no `sync-rollback` command. To restore older content, an authorized publisher
materializes that content and publishes it as a new higher, parent-linked revision. Revision numbers
and accepted HEAD chains never move backward.

The accepted time-machine expansion preserves that rule:

```text
iotox sync-history NAMESPACE [LIMIT]
iotox sync-diff NAMESPACE FROM_RECORD_HEX TO_RECORD_HEX
iotox sync-conflicts NAMESPACE [RECORD_HEX]
iotox sync-restore-plan NAMESPACE RECORD_HEX
iotox sync-restore-forward NAMESPACE RECORD_HEX PLAN_ID_HEX
```

ADR 0294 implements this expansion. History/diff/conflict/plan are read-only and paths are rendered
as unambiguous hexadecimal owner-local output. A restore plan names required retained objects,
missing bytes, conflicts, membership/cutoff facts, the current frontier, workspace generation, and
the new local generation. Its opaque ID binds those facts and a clean worktree. The apply command
must present that exact still-current ID, then re-authors the chosen retained projection as a
distinct higher authorized revision; it never rewinds accepted HEAD state. These commands never
describe retained history as a backup.

Sparse custody is live recipient-local policy:

```text
iotox sync-interest NAMESPACE [include=PATH|exclude=PATH...]
iotox sync-interest-clear NAMESPACE
```

ADR 0295 implements these commands. With no rules, `sync-interest` inspects; with rules, it replaces
both canonical rule sets; `sync-interest-clear` restores complete intent. The peer never supplies
these paths. Pull status, repair, and GC report partial custody, while all branch/manifests remain
available for conflict inspection. An interest mutation plus ordinary `sync-pull` performs on-demand
backfill without confusing formerly unprojected absence with deletion. ADR 0296 makes the existing
`sync-pull-multi` and `sync-source-add` entrances engine-polymorphic: one tree-v2 primary freezes the
frontier, and bounded complementary primary-lane sources satisfy exact objects after authenticated
absence. ADR 0329 adds bounded same-source tree-v2 object pipelining over those unchanged frames.
Routed tree transfer and intra-object striping remain planned.

Durable tree-v2 health is also live:

```text
iotox sync-health NAMESPACE [cached|refresh]
```

Refresh is the default and commits a content-free stable-device-signed green/yellow/red observation;
cached verifies it without walking content. The output makes sparse custody, policy staleness,
rollback-witness absence, and lack of backup certification explicit.

## Signed update controls

```text
iotox update-policy-template NAMESPACE TARGET ROOT \
  [--signer-policy-epoch N] SIGNER_PUBLIC_KEY_HEX... \
  [--revoked-signer PUBLIC_KEY_HEX...]
iotox update-policy-lint PATH
iotox update-signer-keygen OUTPUT
iotox update-signer-show PATH
iotox update-policy-rotate PATH \
  [--add-signer PUBLIC_KEY_HEX...] \
  [--retire-signer PUBLIC_KEY_HEX...]
iotox --identity PATH update-bundle-create POLICY PAYLOAD OUTPUT SEQUENCE VERSION
iotox update-stage NAMESPACE HEAD_RECORD_HEX
iotox update-apply MANIFEST_RECORD_HEX
iotox update-confirm HEALTH_TOKEN_HEX
iotox update-gc dry-run|quarantine
iotox witness-update-enrollment --config PATH
iotox command FRIEND update.stage HEAD_RECORD_HEX [PRIORITY]
```

These commands are implemented and remain default-off behind explicit local policy/state paths.
The optional update-lifecycle witness binds the exact canonical policy and complete signed state;
its enrollment command emits the no-replace service artifact and never mutates local or remote
state. Lifecycle changes then advance automatically inside the Agent. Policy rotation remains
frozen within the enrolled epoch until the replacement/re-anchor ceremony is implemented.
`update-policy-template` emits v1 policy unless a positive signer-policy epoch or revoked signer list
is supplied; then it emits v2 policy. The v2 policy does not change `signed-update-bundle-v1`: it
records active release signers plus a bounded canonical revoked-signer set so a rotated local policy
rejects future staging of bundles signed by retired keys. `update-policy-lint` reports counts and
epoch without dumping keys. `update-signer-keygen` is no-clobber, `update-signer-show` prints only
public identity, and `update-policy-rotate` emits a separately reviewable incremented policy. The
routine ceremony adds a replacement for one overlap epoch before retiring the old key.

Local `update-stage` binds the current accepted sync HEAD to the exact release-signed bundle and
copies only verified bytes into an inert inactive slot. A separately enabled policy-v3
`linux-service-v1` adapter may later consume only signed kind-2 state through its sealed native-image
contract. Remote `command FRIEND update.stage ...`
uses the signed command journal plus `install.firmware` authority to request the same staging effect.
`update-gc` is same-user local-only. Dry-run reports signed-state-protected and eligible slots;
quarantine moves eligible historical payloads into bounded recoverable custody without unlinking.
Neither update path grants remote apply, restart, health confirmation, retention, arbitrary file
write, purge, helper selection, or executable deployment authority.

## Human peer aliases

Status: product-expansion workstream 5 implemented by ADRs 0292 and 0293.

```text
iotox peer-aliases
iotox peer-alias-set NAME PEER
iotox peer-alias-rename OLD_NAME NEW_NAME
iotox peer-alias-remove NAME
iotox peer-invitation-create OUTPUT LIFETIME_SECONDS [ALIAS|-] [CAPABILITIES|-]
iotox peer-invitation-inspect PATH [EXPECTED_INVITER_PUBLIC_KEY]
iotox peer-invitation-import PATH EXPECTED_INVITER_PUBLIC_KEY
iotox peer-invitation-accept PATH EXPECTED_INVITER_PUBLIC_KEY [ALIAS|-]
```

The device-signed owner-local store is bounded, one-to-one, collision-refusing, and explicit about
rename/removal. All established-peer and terminal selectors share exact `friend:`, `key:`, and
`alias:` escapes plus unambiguous bare compatibility forms. Peer deletion retains a name; only
explicit removal releases it. An alias binds one Tox key and grants no authority. The fixed signed
invitation binds stable inviter, exact Tox address, expiry/nonce, alias suggestion, and closed
requested capabilities. Inspect establishes no trust; import requires an out-of-band inviter pin and
mutates nothing; accept creates only transport friendship and an optional exact alias. RecallRoot—not
aliases—is what satisfies “from memory, you can reach your devices.” See `peer-aliases.md` and
`peer-invitations.md`.

## Deliberately planned, deferred, or rejected vocabulary
- `file-send-stdin`: Tox chunk service requires a finite size and seekable/retryable source. A safe
  implementation would first spool stdin into a bounded synchronized immutable file and is therefore
  a new durable operation, not a trivial companion alias.
- `authority-export` / `authority-import`: importing a ledger alone can create rollback, fork, identity,
  and guard inconsistency. Backup and recovery must cover one identity-bound state set with an exact
  manifest and recovery ceremony; raw ledger replacement is not accepted.
- `command-store-compact`: the signed durable store's deduplication and result history cannot be
  discarded merely to reduce bytes. Any pruning scheme needs a frozen retention/checkpoint protocol.
- `route-set` runtime mutation: no live add/replace/remove verb is accepted. Offline creation-only
  `route-set-create` and `route-set-create-v2` author reviewed signed artifacts; `routes` and
  `routes-watch` remain read-only.
  Runtime Tor/I2P selection separately waits for M8's identity and no-silent-fallback contract.
- Remote update apply/restart/confirm: rev0044 implements peer-facing `update.stage` only through
  `command FRIEND update.stage HEAD_RECORD_HEX [PRIORITY]`, with `install.firmware`, exact current
  accepted HEAD, durable replay/restart, quotas, pre-first-send cancellation, and audit. The remote
  peer cannot invoke local `update-apply`, restart the Agent, obtain a health token, or call
  `update-confirm`; those effect-bearing verbs remain deliberately absent.
- A remote-selected `terminal ... COMMAND`, general port forwarding, and agent forwarding are outside
  the Ratox security model. An owner-bound profile may now be a real interactive login shell and that
  shell naturally interprets typed commands; this does not create a protocol-level argv request. M6
  device effects continue to use `command FRIEND OPERATION`; new safe effects are operation strings
  and capabilities, not top-level CLI proliferation.

## Implementation order

1. Extend the implemented and twice-interrupted native-carrier `terminal --reconnect` gate to a
   longer soak and overlay routes; do not block deployable configuration on downstream evidence.
2. Continue protected-state qualification without conflating encryption and freshness. Authority,
   startup namespaces, route and Ratox policy, command effects, sync policy, update lifecycle, and
   per-namespace single-writer and tree-v2 semantic sync state are implemented. Operationally
   independent persistence, replacement/re-anchor, broader namespace state, and the exhaustive
   rollback campaign remain.
3. ADR 0317 completes the command-level typed registry, help index, parser classification, and
   Bash/Zsh/Fish generation; ADRs 0319, 0360, and the second native ergonomics gate bring the
   current population to 210 stable spellings. A later
   descriptor revision may add closed positional-enum completion; dynamic remote or path guessing
   remains out of scope.
4. Widen the optional rescue capsule to supported architectures and cross it through the production
   PTY; never make fallback userland an automatic remote payload.
