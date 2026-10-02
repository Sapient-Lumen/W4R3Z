# Content-free diagnostics

IoTox keeps a small authenticated flight recorder so an operator can answer “what class of state
change happened?” without copying what a peer said, what a terminal displayed, or where private
state lives. ADR 0291 implements the authenticated recorder/export core, ADR 0298 joins the signed
tree-v2 namespace-health grammar without per-namespace handles, and ADR 0299 adds normalized passive
host capabilities without host paths or raw kernel text.

## Operator commands

Plan a support artifact and review the exact commands before mutating:

```sh
iotox support-bundle plan ./iotox.support
```

Export from a running Agent to a new file:

```sh
iotox --runtime /run/user/$UID/iotox diagnostics-export /absolute/path/iotox.diagnostics
```

The friendlier equivalent is:

```sh
iotox support-bundle create /absolute/path/iotox.diagnostics
```

Inspect the file before sharing it:

```sh
iotox diagnostics-inspect /absolute/path/iotox.diagnostics
iotox support-bundle inspect /absolute/path/iotox.diagnostics
```

The destination parent must already exist. Export creates one owner-private mode-0600 regular file,
uses `O_NOFOLLOW|O_EXCL`, fsyncs the completed file and parent directory, and never replaces an
existing path. `diagnostics-inspect` needs no running Agent or private identity. Success contains:

```text
decision=valid-content-free-bundle
share-review=contains-closed-metadata-but-correlates-config-and-activity
```

That second line matters. “Content-free” is not “information-free.” Counts, state ordering, selected
network class, enabled-feature bits, aggregate namespace health, normalized host capabilities, and
the redacted configuration commitment can correlate device activity or two reports. Review every
bundle for its intended recipient.

`support-bundle` is a porch around the same bundle contract. It adds review
language and exact next commands; it does not add raw logs, configs, paths,
keys, endpoint lists, attestation, backup proof, or remote upload.

## What the Agent retains

The default recorder path is derived from Tox savedata as
`SAVEDATA_PARENT/.iotox-diagnostics/SAVEDATA_FILENAME.flight`. It can be replaced with
`--diagnostics-store ABSOLUTE_PATH`; `--max-diagnostics-records 16..256` selects the tail bound and
defaults to 128. Both options belong in the canonical Agent configuration when one is used.

Each fixed-size record contains only:

- a contiguous sequence number;
- one closed event class and one numeric `ErrorCode`;
- closed Agent phase and network class;
- eight closed feature/state bits;
- a path/key/endpoint-free structural configuration commitment;
- ten unsigned counters for peers, authorized peers, pending commands, active file transfers,
  Ratox sessions/admission rejection, dropped transport/Ratox events, and admitted/rejected sync
  work.

Implemented event producers cover secure recorder initialization, Agent running/stopping/failure,
self-transport changes, authority-ledger mutation, Ratox lifecycle changes, and runtime-projection
failure. `sync-state` and `resource-pressure` are frozen event names for later dedicated transitions;
current records still sample sync work and the pressure-admission-closed bit whenever any implemented
event is committed. `current-snapshot` labels the unrecorded live observation added during export.

The complete canonical store is hashed in the `diagnostics-flight-v1` domain and signed by the
stable device identity after every mutation. Writes use the ordinary crash-atomic state store. A
reopen requires the expected device public key, exact signature, canonical encoding, private regular
file shape, and contiguous tail invariants. Startup fails closed if an existing recorder is corrupt,
foreign, weakly permissioned, or cannot accept the initial record. Once the Agent is running,
recorder write failures are best-effort and counted in the next successful export so a diagnostic
disk failure does not itself take machine control offline.

The Agent/process incarnation lock supplies the single-writer boundary. The recorder format by
itself is not a multi-writer journal.

## What never enters the recorder or bundle

The implementation has no fields for:

```text
peer public keys, Tox addresses, friend numbers, or aliases
messages, actions, terminal input/output, command operation/arguments/results
filenames, namespace names, local paths, endpoints, bootstrap/relay keys
namespace/policy commitments or stable per-namespace diagnostic slots
RecallRoot phrases, private keys, signatures, authority-ledger records
wall-clock or monotonic timestamps
raw argv or a digest over raw argv
```

The configuration commitment is computed only from a closed structural projection. Revision 9 binds
network class, native-UDP and feature enablement, required protected-state, authority-witness, and
application/Ratox incarnation-witness plus route-generation-witness, terminal-policy-witness, and
command-effect-witness, sync-policy-witness, update-lifecycle-witness, and sync-guarded-state-witness
presence, selected file/sync
quotas, and the recorder bound.
It deliberately
omits paths, keys, endpoints, profiles, and arbitrary option text so an exported digest cannot serve
as a cheap dictionary oracle for those values.

## Export and trust boundary

Local-control v1.56 operation 108 accepts no payload. The same-user client asks the running Agent for
a canonical `iotox-diagnostics-redacted-v3` view. Before answering, the Agent verifies the
already-open device-signed recorder state, verifies each cached eligible tree-v2 health record, and
adds one current observation plus the accumulated write-failure count. The health records are
reduced to anonymous totals: verified/absent/invalid, green/yellow/red, complete/partial custody,
policy staleness, conflicts, missing objects/bytes, automation stalls, store pressure, source
exhaustion, source-result counts, and the maximum automation failure streak. Older engines are not
counted as missing. It also samples the reusable host-capability probe in passive/no-fork mode and
reduces pidfd, seccomp, MDWE, Landlock/ABI, privilege-escalation prerequisites, sudo mechanism,
cgroup-v2 delegation, known controllers, and twelve fixed resource interfaces to closed grades,
bitmasks, and counts. No executable/cgroup path or raw controller/kernel text survives. The CLI
validates that closed grammar, adds product version/revision, and hashes the exact payload in the
`diagnostics-bundle-v1` domain, validates the complete bundle again, and only then creates the output.

Offline inspection remains compatible with redacted v1 flight-only and v2 health-only payloads and
explicitly labels their missing appendices. New exports use v3. The outer bundle format remains v1
because its length, digest, and framing semantics did not change.

The shareable bundle intentionally contains neither device public key nor stable-device signature.
Its digest detects accidental corruption and `diagnostics-inspect` proves canonical closed-field
shape; neither proves which device emitted it. A recipient who can edit the bundle can recompute its
digest. This is an inspectable support artifact, not remote attestation, a signed audit log, authority
evidence, or proof of non-omission.

The device-signed ring also has no independent monotonic witness. It detects byte tampering and a
foreign signer, but replacement with an older valid copy is possible when an attacker controls the
same storage. Workstream 8 owns that separate rollback problem.

## Present limits and next joins

The bundle is capped at 64 KiB and the redacted payload at 48 KiB. It exports recorder state, the
current closed Agent observation, anonymous tree-v2 health aggregates, normalized passive host
capabilities, and product identity. If a
256-record local tail with full-width counters cannot fit the smaller control bound, export drops
only the oldest excess records and reports `export-omitted-records`; the signed local store is
unchanged. The health aggregate is never shortened. Every new export freezes
`namespace-health-rollback-witness=0` and `namespace-health-backup-certified=0`. Raw `/proc`, `/sys`,
environment, logs, config, or arbitrary diagnostic text may never be swept into this artifact.
`available` in the Agent appendix is weaker than `live-proved` from explicit
`iotox host-capabilities`; neither proves sudo policy or final child confinement.

Passing inspection does not mean the device is healthy, backed up, uncompromised, current, or safe
to operate. It means only that these bytes satisfy the bounded content-free bundle contract.
