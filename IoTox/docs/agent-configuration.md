# Agent configuration and preflight

ADR 0290 adds one reviewed file-backed form of the existing Agent command line. It is local policy,
not peer framing, a network message, an authority record, or a place to store a RecallRoot phrase.

## Canonical record

The file is a shell-free ordered argument record. A minimal native deployment can be written as:

```text
iotox-agent-config-v1
argument-0000=--state
argument-0001=/var/lib/iotox/device.toxsave
argument-0002=--runtime
argument-0003=/run/user/1000/iotox
argument-0004=--no-default-bootstrap
argument-0005=--no-default-relays
```

Indices are four decimal digits, start at zero, and are contiguous. The record has exactly one
trailing LF. Each value is one literal argument: there is no quoting, escaping, environment
expansion, variable interpolation, include directive, or shell evaluation. Spaces inside a value are
literal; control bytes are rejected. The record is limited to 256 arguments, 4,096 bytes per
argument, and 256 KiB total.

The final file must have a normalized non-root absolute path and is opened with `O_NOFOLLOW`. It must
be one single-link regular file owned by the effective user, owner-readable, and have no group or
other permissions. Mode `0600` is the normal choice:

```sh
chmod 600 /etc/iotox/agent.conf
iotox config-lint /etc/iotox/agent.conf
iotox run-check --config /etc/iotox/agent.conf
iotox run --config /etc/iotox/agent.conf
```

`--config` must be the first Agent option. It cannot appear inside the record. `run`, `run-check`,
and `config-lint` are commands, not record arguments.

## Self mode

`--mode self` is an Agent option that deliberately selects the self-machine product mode. It enables
the Ratox terminal host and same-user terminal controller by default for machines the owner treats as
their own. In a generated config, the init porch writes the explicit profile-store and helper paths
so the record remains reviewable:

```sh
iotox init plan --root /var/lib/iotox --mode self --enable-sync
iotox init write-config --root /var/lib/iotox --mode self --enable-sync
```

Self mode does not create RecallRoot authority, pair peers, install terminal profiles, bind stable
principals, grant `interactive.terminal`, enable sudo, or choose a route fallback. It changes the
Ratox role default only; the profile/binding/authority/sudo boundaries remain the same as manual
terminal activation.

## Overrides

Arguments after the config path are explicit overrides:

```sh
iotox run-check --config /etc/iotox/agent.conf --runtime /tmp/iotox-check
iotox run --config /etc/iotox/agent.conf --network tox/native
```

For a non-repeatable option, the command-line group replaces the same file option. For repeatable
`--bootstrap`, `--tcp-relay`, `--route-worker-network`, `--route-worker-bootstrap`, and
`--route-worker-tcp-relay`, supplying that option on the command line replaces all file instances
and retains all command-line instances in order. Duplicate non-repeatable fields fail. An enabling
flag has no invented disabling twin: an override can enable a file-omitted feature but cannot silently
negate a file flag. Edit and review the record when a feature must be disabled.

The merged sequence enters the same Agent argument parser, normalization, and dependency checks as
ordinary `run`. There is no parallel typed configuration model to drift from the CLI.

## `config-lint`

`config-lint` checks file ownership, privacy, no-follow shape, stable read, canonical bytes, option
grouping, ordinary Agent parsing, route topology, resource bounds, and cross-option dependencies. It
does not inspect deployment paths or load providers. Successful output is deliberately small:

```text
iotox-agent-config-lint-v1
decision=valid
arguments=6
network=Tox/native
```

It prints neither raw arguments nor paths. There is intentionally no automatic `config-export`:
argv and local paths may be sensitive, and a mechanical dump could be mistaken for reviewed policy.

## `run-check`

`run-check` executes the same parse, merge, normalization, and static preflight that now precedes
`run`. It:

- loads the configured c-toxcore and libsodium providers without constructing a Tox instance;
- proves existing sensitive paths are private or that an absent path has a writable directory
  ancestor;
- cryptographically loads an existing device identity;
- verifies an existing signed route inventory and generation high-water record through a read-only
  route-store path which neither locks nor checkpoints;
- strictly loads existing synchronization namespaces and signed-update policy, including the update
  namespace/engine binding;
- strictly loads Ratox profiles and bindings, checks enabled executable and working-directory paths,
  composes cgroup budgets, and checks required cgroup-v2 interfaces without creating a probe leaf;
- reports every inspected category without printing configured paths; and
- creates no runtime tree, listener, Tox identity, identity file, journal, incarnation, lock,
  temporary, PTY, child, cgroup, or network traffic.

Success means `decision=ready-for-start`, not “the Agent started.” Existing authority, command, and
incarnation records are checked for private file shape, but their recovery-capable open paths remain
deferred to `run`: those paths may adopt a legacy rollback guard, reconcile an interrupted
transaction, advance an incarnation, migrate a journal, or take a lock, all of which would violate a
non-mutating check. The report says `runtime-recovery-pending` rather than pretending otherwise.
Likewise, final seccomp/MDWE/Landlock enforcement is proved in the production PTY child, not by
`run-check`; `host-capabilities` is the separate live host probe.

### Required fscrypt-v2 state

ADR 0303 adds an optional fail-closed deployment boundary:

```text
argument-0006=--require-state-protection
argument-0007=fscrypt-v2
argument-0008=--protected-state-root
argument-0009=/var/lib/iotox-protected
argument-0010=--protected-state-policy-id
argument-0011=0123456789abcdef0123456789abcdef
```

All three protection fields must appear together. The 32 hexadecimal characters pin the public
fscrypt-v2 master-key identifier and are not an unlock secret. When `--config` is used, that exact
configuration file is itself a
security-bearing path and must be inside the selected root; `/etc/iotox/agent.conf` therefore cannot
be used with the example root above. The external unlock service installs the fscrypt key first;
neither this record nor argv contains the key.

`run-check` then descriptor-pins the root and reports its exact v2 policy identifier, live kernel key
status, mount identity, configured-path count, extant-inode count, and runtime placement. It closes
over savedata, identity, authority and guard/witness intent, commands, diagnostics, aliases,
incarnation/route locks, every route-worker savedata root, Ratox profiles/bindings, sync policy and
each loaded namespace root, update policy/state/slots/quarantine, and derived companions. Prefix,
`..`, symlink, hard-link, nested mount, foreign policy, special-inode, weak ownership/mode, and absent-
key cases refuse. Runtime must resolve on tmpfs or inside the same protected root.

Live `run` repeats this protection inspection immediately before durable security initialization;
authority-witness reconciliation and all security-bearing store opens complete before the runtime
tree is created. This mode establishes encrypted-at-rest closure, not rollback freshness.

ADR 0305's authenticated authority-witness service is selected as one inseparable group:

```text
argument-0012=--authority-witness-host
argument-0013=witness.example
argument-0014=--authority-witness-port
argument-0015=37177
argument-0016=--authority-witness-server-key
argument-0017=0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF
argument-0018=--authority-witness-domain
argument-0019=0123456789ABCDEF0123456789ABCDEF
argument-0020=--authority-witness-epoch
argument-0021=1
argument-0022=--authority-witness-timeout-ms
argument-0023=3000
argument-0024=--authority-witness-intent
argument-0025=/var/lib/iotox-protected/authority.witness-intent
```

Host, port, pinned dedicated witness key, create-once domain, and nonzero epoch must all be present.
Timeout is 1..30000 ms and defaults to 3000; the intent path defaults beside the authority ledger.
`run-check` verifies the closed configuration without contacting the service. Live `run` signs with
the stable device identity, authenticates the pinned service, and reconciles the exact authority head
before creating the runtime tree. Endpoint/key/path values remain absent from shareable diagnostics.
See `protected-local-state.md` for enrollment, restart, replacement, independence, and rollback
nonclaims.

ADRs 0306--0314 optionally add startup-namespace, route-policy, complete Ratox-policy, mutable-
command effect, complete sync-policy, update-lifecycle, and per-namespace semantic-state lanes to that
same authenticated service:

```text
argument-0026=--witness-application-incarnation
argument-0027=--application-incarnation-witness-intent
argument-0028=/var/lib/iotox-protected/.iotox-incarnations/application.witness-intent
argument-0029=--witness-ratox-incarnation
argument-0030=--ratox-incarnation-witness-intent
argument-0031=/var/lib/iotox-protected/ratox/ratox.witness-intent
argument-0032=--witness-route-generation
argument-0033=--route-witness-intent
argument-0034=/var/lib/iotox-protected/route.witness-intent
argument-0035=--witness-terminal-policy
argument-0036=--terminal-policy-witness-checkpoint
argument-0037=/var/lib/iotox-protected/terminal-policy.checkpoint
argument-0038=--terminal-policy-witness-intent
argument-0039=/var/lib/iotox-protected/terminal-policy.intent
argument-0040=--witness-command-effects
argument-0041=--command-effect-witness-checkpoint
argument-0042=/var/lib/iotox-protected/command-effect.checkpoint
argument-0043=--command-effect-witness-intent
argument-0044=/var/lib/iotox-protected/command-effect.intent
argument-0045=--witness-sync-policy
argument-0046=--sync-policy-witness-checkpoint
argument-0047=/var/lib/iotox-protected/sync-policy.checkpoint
argument-0048=--sync-policy-witness-intent
argument-0049=/var/lib/iotox-protected/sync-policy.intent
argument-0050=--witness-update-lifecycle
argument-0051=--update-lifecycle-witness-intent
argument-0052=/var/lib/iotox-protected/update-lifecycle.intent
argument-0053=--witness-sync-guarded-state
```

The paths are optional and otherwise derive beside their respective incarnation records. Each flag
requires its own device-signed service enrollment under the configured domain and epoch. Ratox
witnessing additionally requires the ordinary enabled Ratox host/profile/helper configuration.
Route witnessing additionally requires the signed `--route-set` and uses the selected or derived
route-generation checkpoint. Its enrollment anchors the reviewed current artifact; later policy
updates must increment generation exactly once.
Update-lifecycle witnessing additionally requires enabled signed updates and an explicit private
intent path. Its enrollment freezes the exact update policy and current signed lifecycle state:

```sh
iotox witness-update-enrollment --config /etc/iotox/agent.conf
```

Within witness protocol v1, later update-policy rotation requires an explicit witness replacement or
re-anchor ceremony; editing the policy alone is intentionally refused.
Per-namespace state witnessing requires `--witness-sync-policy` and one no-replace enrollment
per namespace:

```sh
iotox witness-sync-guarded-enrollment --config /etc/iotox/agent.conf NAMESPACE
```

The command first verifies the externally committed policy tree. For single-writer engines it binds
the exact published, accepted, activated, and retained roots under lane 9; for tree-v2 it binds the
live branch frontier plus exact signed workspace and maintenance state under lane 10. All namespaces
must be enrolled before startup. Live namespace addition or removal is refused; the lanes do not
witness content, quarantine, projections/current pointers, health, or backup.

The separately administered witness daemon may enforce a portable complete-store restart floor.
With it stopped, use `witness-service-checkpoint ROOT SERVICE_IDENTITY OUTPUT`, verify the artifact
against the pinned service public key with `witness-service-checkpoint-verify`, retain it outside the
service failure domain, and pass it as the optional final argument to `witness-service-serve`. This
is witness-service administration and is intentionally not an Agent configuration field.
Terminal-policy witnessing requires the enabled Ratox host. Its enrollment commits the complete
validated profile/binding tree. Ordinary terminal profile administration intentionally makes the
tree unusable until the owner runs:

```sh
iotox witness-terminal-policy-enrollment --config /etc/iotox/agent.conf
# enroll the printed hex on the witness exactly once, then for later edits:
iotox witness-terminal-policy-commit --config /etc/iotox/agent.conf
```

The enrollment command is read-only. The commit command authenticates the configured remote service,
advances one exact position, and strictly rereads the store before reporting success. The default
checkpoint is `PROFILE_ROOT.witness-checkpoint`; the intent is beside it.
Command-effect enrollment similarly binds an existing signed command store:

```sh
iotox witness-command-effects-enrollment --config /etc/iotox/agent.conf
```

After no-replace witness enrollment, no manual commit command exists: each authorized mutable
command automatically advances the exact durable `STARTED` frontier before its provider/update
effect. If the service is unavailable or disagrees, the effect is not attempted. Effect identities
remain retained until a future witnessed compaction protocol; this prevents erased-start replay but
does not turn arbitrary physical actuation into exactly-once work.

Sync-policy enrollment and offline commit use the same reviewed service configuration:

```sh
iotox witness-sync-policy-enrollment --config /etc/iotox/agent.conf
# enroll the printed hex on the witness exactly once, then for a quiescent offline edit:
iotox witness-sync-policy-commit --config /etc/iotox/agent.conf
# once the exact policy tree is current, enroll every namespace separately:
iotox witness-sync-guarded-enrollment --config /etc/iotox/agent.conf NAMESPACE
```

The policy store must already exist and may be empty. Agent-mediated namespace and automation
changes automatically commit the exact complete candidate tree before it enters the live registry
or scheduler. Offline edits must be made while the Agent is stopped; the explicit commit is followed
by restart because a running Agent keeps its startup-frozen witnessed snapshot. Checkpoint and intent
paths default beside, not inside, the strict sync policy root.
`run-check` validates paths and dependencies without querying or advancing the service; live
security initialization reconciles and advances every selected lane before creating runtime.

The Agent configuration also owns the persistent content-free recorder:

```text
--diagnostics-store /var/lib/iotox/diagnostics.flight
--max-diagnostics-records 128
```

The path is derived beside savedata when omitted; the bound is 16..256. `run-check` performs private
path readiness checks and, when both recorder and identity already exist, verifies the exact device
signature and reports retained/evicted counts without writing either file. Existing diagnostic state
without its identity fails preflight. Live startup alone creates or appends the store. Export is a
separate running-Agent operation described in `diagnostics.md` and never exports this configuration
record.

The stable-device-signed peer-name registry similarly accepts an explicit path:

```text
--peer-alias-store /var/lib/iotox/peer-aliases.store
```

When omitted it is derived beside savedata. `run-check` verifies an existing store's private shape,
signature, canonical one-to-one mapping, generation, and 256-entry bound without writing it. Alias
names are private operator metadata and are not part of the Agent config or diagnostic export; see
`peer-aliases.md`.

Filesystem and provider state can change immediately after preflight. Live startup therefore reruns
the same static preflight and then performs its authoritative locked recovery and construction. A
green check is a deployment diagnostic, not a lease on future host state, a security audit, or a
backup certificate.
