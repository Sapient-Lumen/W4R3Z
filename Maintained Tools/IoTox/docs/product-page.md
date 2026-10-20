# IoTox

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗ ██████╗ ████████╗ ██████╗ ██╗  ██╗                                    ║
║   ██║██╔═══██╗╚══██╔══╝██╔═══██╗╚██╗██╔╝                                    ║
║   ██║██║   ██║   ██║   ██║   ██║ ╚███╔╝                                     ║
║   ██║██║   ██║   ██║   ██║   ██║ ██╔██╗                                     ║
║   ██║╚██████╔╝   ██║   ╚██████╔╝██╔╝ ██╗                                    ║
║   ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝                                    ║
║                                                                              ║
║        self-owned device nerves over Tox                                      ║
║        a modern ratox successor for ordinary shells and sovereign machines    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   From memory, you can reach your devices.                                    ║
║   From an ordinary shell, you can understand and operate them.                ║
║   No vendor key can reassign them.                                            ║
║                                                                              ║
║   The outside should be ordinary; the inside must tell the truth.             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

IoTox is a one-binary C++20 device agent. It uses Tox as the connection fabric,
then adds the missing product constitution above it: stable device identity,
owner-reconstructible authority, explicit capabilities, durable commands, careful
sync, and a Ratox-style Unix surface that normal tools can understand.

The project is built around one hard distinction:

```text
transport says:  I can reach this Tox peer
IoTox says:      this stable principal is allowed to do this exact thing
the filesystem says: here is the ordinary surface humans and scripts can use
the evidence says:   here is what actually happened, and what did not
```

Friendship is not authority. A file arriving is not permission to execute it. A
sync completing is not a backup. A route working once is not a route guarantee.
A shell opening is not permission to become root. IoTox tries to be useful
without erasing those boundaries.

## What it is for

IoTox is for machines you own and want to operate without a vendor control
plane. The intended operator story is small:

```text
install one executable
create or recover owner identity
pair devices over Tox
grant exact capabilities
choose self mode for your own machines
sync ordinary directories when the directory is not your only copy
open an owner-approved terminal profile when remote control is needed
inspect health and evidence without leaking content
```

This is not a cloud fleet manager. It is not a remote vendor account. It is not a
replacement for backups or disaster recovery. It is not an SSH clone with agent
forwarding, arbitrary remote-selected exec, or general port tunneling. It is a
device-control tool that treats ownership as the root primitive.

## Why Tox

Tox already gives IoTox a serious peer fabric: long-lived peer keys, encrypted
sessions, bootstrap discovery, NAT traversal, TCP relay fallback, custom packets,
and finite file transfer. IoTox does not replace that with an account service.
It builds the missing device semantics on top.

Routes are explicit. Native Tox is the default working path. Tox over Tor and
Tox over I2P are treated as named route classes with fail-closed construction and
separate evidence. They are not silent fallbacks and they are not anonymity
certificates.

## The ordinary surface

Ratox proved that a Tox peer can feel like a directory instead of an SDK. IoTox
keeps that instinct:

```text
read status
write a bounded request
watch events
send text
send files
run typed commands
attach to a terminal
```

The surface is ordinary because ordinary tools compose. The implementation is
strict because ordinary surfaces are easy to misuse if the hidden state is vague.
Every local write becomes one typed operation with bounded parsing, bounded
queues, transaction state, and content-free evidence.

## Sync

IoTox synchronization is now useful for noncritical working directories on the
founding Linux/KVM evidence path. It has one-writer and bounded read-write
tree-v2 modes, signed branches, conflict preservation, tombstones, sparse
custody, health, recovery rehearsal, and measured capacity gates.

The important product rule remains:

```text
IoTox sync can be a working copy.
IoTox sync is not the backup.
```

Important data still needs an independent, versioned, immutable or otherwise
rollback-resistant backup outside the same Agent disk, VM, snapshot, and
administration domain. IoTox now has tools that can compare a restored tree and
record provenance labels; it does not yet prove that an operator's backup system
is independent or trustworthy.

## Ratox and SSH-shaped control

IoTox's Ratox work is the SSH-shaped part of the product. The intended daily
control path is an owner-approved login shell over Tox. For machines you own,
`--mode self` is the default-on Ratox shape:

```text
the Agent is started in self mode
the owner creates a terminal profile
the profile chooses the account, executable, argv, cwd, environment, limits, and policy
the peer proves current authority
the terminal attaches
the human types commands inside the shell
sudo is denied by default
sudo can be enabled only by an explicit host-authorized compatibility profile
```

That matters. The remote peer does not choose an arbitrary executable. It does
not choose a profile by surprise. It does not receive SSH agent forwarding. It
does not get general port forwarding. Root access is a deliberate host policy
crossing, not an ambient property of connection.

Self mode is also the multidevice frontier. IoTox does not depend on Tox
multidevice semantics: `iotox self-swarm` keeps an owner-signed roster of self
machines above Tox, then renders and applies narrow grants through the existing
authority ledger. A roster row names an alias, stable principal, Tox route key,
role, capabilities, generation, and active/retired state; it never grants shell
authority merely because a friendship or savedata key exists.

Above that private roster, `iotox person` now creates the first public person
delivery layer. A signed delivery card says “this person key currently has
these active Tox route keys” without publishing private machine aliases or
authority principals. A signed person message envelope can then be planned,
sent to every current route, and verified independent of which device route
carried it. The next native slices are also in place: a rostered stable device
can hold a person-signed sender delegation for daily messages, contacts can pin
delivery-card freshness, receivers can suppress duplicate fanout payloads,
signed group descriptors/messages can be delivered through member person
cards, and local messenger stores can hold contact, transcript, delegated
receipt, aggregate receipt, and reviewed outbox state. This is the beginning
of “send to the human, reach all their devices,” not a complete automatic
messenger yet. Native card-refresh, outbox-retry, outbox-expire,
background-plan, and background-run commands now cover supervised bounded
retry, attempt accounting, receipt rollup, and dead-letter expiration. The
top-level resident-service porch can render Agent/sync/Ratox and person-worker
service artifacts for systemd, NixOS, and MonsterNix-adapter review. Local
read marks, read-status, transcript convergence checks, and group-status
summaries make the lived messenger easier to operate without pretending to
prove remote human attention or global ordering. Delivery to devices that
never return online, independent freshness custody, and automatic Tox
group/conference carriers remain future work.

There is also a small rescue-userland track: static oksh plus Toybox as a
fallback payload when the normal userland shell is broken. It is optional,
profile-pinned, disabled by default, and not a second product binary.

## Evidence level today

The founding roadmap is complete for this machine's accepted scope. The current
work is product expansion and trust graduation:

```text
sync:      useful, bounded, still not backup-grade for precious data
terminal:  serious construction, not production-activated remote administration
routes:    native strong; Tor/I2P bounded and explicit; long overlay soaks remain
storage:   loopback/KVM storage science passed inside scope; ext4+btrfs liar
           matrix and production prefix replay passed; versioned recovery
           custody remains operator-scoped; media certification is out of scope
packaging: full-history upload datacube, slim public datacube, richer conversation cube,
           and cleanup tooling exist
```

IoTox states claims in evidence-shaped language because that is the only way to
keep a tool like this honest. A passing Sandwurm/KVM gate is useful. It is not a
fleet guarantee. A same-machine retained proof is useful. It is not disaster
recovery. A cgroup/PSI service-manager cell is useful. It is not a
complete sandbox.

The binary now includes the first human porches for that honesty:

```text
iotox help
iotox help quickstart
iotox help all
iotox doctor binary
iotox help self
iotox help person
iotox help routes
iotox help evidence
iotox help shipping
iotox help support
iotox person quickstart
iotox overview
iotox readiness
iotox explain storage-precious-data-blocked
iotox pair-card create|inspect|accept
iotox sync-conflicts-summary
iotox support-bundle plan
```

They shorten ordinary work without turning friendship into authority, sync into
backup, diagnostics into attestation, or sudo into a default.

## The script direction

The end product should remain one executable, but first contact should be a
single understandable script. The first repository helper is
`tools/iotox-repo.sh`; it currently covers safe doctor/build/test/datacube/clean
entry points plus retained recovery, dishonest-storage, and witness-custody
drills. The broader public script should be Bash-owned and Nix-aware:

```text
iotox doctor       explain what this host can do without mutating state
iotox build        build the exact package
iotox test         run named proof tiers
iotox run          start from an explicit state/runtime/config root
iotox sync         guide create/share/follow/doctor/recovery commands
iotox terminal     guide profile, sudo, and rescue choices
iotox datacube     package a clean committed repository for conversation
iotox clean        audit bulky local proof/build residue, dry-run first
```

MonsterNix should receive a separate adapter, not a hidden fork of IoTox. The
first IoTox-side adapter is `tools/iotox-monsternix-adapter.sh`, a read-only
doctor/plan script. The later writer's job is to admit exact IoTox source or
package objects, run Monsternix proof loops, and project machine-specific
service configuration only after explicit operator acceptance. The adapter must
be inert by presence, content-free in receipts, and honest about which authority
belongs to IoTox versus which authority belongs to the host machine.

The practical split is:

```text
script for everyone:     teach, build, test, run, package, and clean IoTox
script for Monsternix:   admit exact objects, produce receipts, wire host policy
product binary:          own device identity, authority, sync, routes, and Ratox
```

That split keeps IoTox portable while allowing Monsternix to become an excellent
home for exact local deployment.

## How to read the repository

Start with `BOOTSTRAPROSE.md` for the wake-from-amnesia truth, `README.md` for
the current revision narrative, `docs/README.md` for the docs map,
`docs/quickstart.md` for the first safe hour,
`docs/edge-of-hope.md` for the ideal, `docs/pragmatic-guardrails.md` for the
counterweight, `docs/roadmap.md` for priority and nonclaims,
`docs/everyday-sync-plan.md` for sync use, `docs/replace-resilio-sync.md` for
the incumbent-sync migration question, `docs/ratox-ssh-status.md` for terminal
control, `docs/human-stories.md` for likely operator journeys and frictions,
`docs/script-distribution-plan.md` for the public script/Monsternix adapter
plan, and `docs/architectural-change-intake.md` before treating a significant
new subsystem as coherent product architecture.
