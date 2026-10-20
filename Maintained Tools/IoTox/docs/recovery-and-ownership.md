# Recovery and ownership direction

## Permanent recall decision

IoTox retains RecallRoot-v1: a fixed Argon2id contract that lets the same exact strong phrase
reproduce the same 32-byte root without stored derivation metadata.

```text
phrase            8 independently generated words
word list         pinned EFF large list, 7776 entries
canonical form    lowercase ASCII, one space between words
algorithm         Argon2id version 19
memory            65536 KiB
iterations        3
parallelism       4 lanes / 4 threads
salt              ASCII IoToxRecallRoot1
output            32 bytes
entropy           ~103.4 bits under uniform generation
```

The fixed public contract enables offline guessing. That is accepted. Generated phrase strength
is a hard requirement. A user-created sentence or ordinary password does not meet the design.

A printed permanent phrase is not an accidental legacy master password; it is an intentional
owner-controlled recovery object. IoTox must minimize where it is exposed and use delegated keys
for routine work.

## Separation of identities

The intended hierarchy distinguishes:

```text
RecallRoot                  reconstructible owner root material
owner signing identity      durable authority derived from RecallRoot
delegated controller keys   daily phones, computers, hubs
stable device identity      application identity independent of route
Tox endpoint identities     replaceable native/Tor/I2P transport endpoints
local data keys             protect retained device state
rollback witnesses          detect old valid identity/ledger/command snapshots
```

RecallRoot-v1 freezes the stable owner Ed25519 derivation used by the local signing ceremony.
Controller, discovery, route-binding, and local-data derivations remain open. The rollback witness
uses an explicit create-once random domain rather than a phrase derivation; its authenticated
service, enrollment, and authority/application/Ratox/route/terminal/command/sync-policy/update lanes
are implemented. ADRs 0312 and 0314 also give each namespace an optional derived-domain record: the
four signed single-writer roots or tree-v2's live branch frontier plus signed workspace and
maintenance state. Operationally independent
persistence and replacement/re-anchor ceremonies remain deployment work.

## No vendor recovery authority

No IoTox-controlled key can replace an owner, generate a recovery grant, or reassign a device.
Manufacturer attestation and software-update signing must remain separate from ownership
transition.

## Authorization ledger

The current canonical signed ledger implements both the original v1 history and the signed v2
format boundary:

- owner root and ownership epoch;
- delegated controller;
- role and capability grant;
- temporary grant fields and bounds;
- revocation;
- explicit owner succession within the current ownership epoch;
- adjacent successor nomination and successor-signed ownership-epoch transition;
- one exact owner-self-signed v1-to-v2 migration; and
- durable capability bit 7, `interactive.terminal`, only in v2 and only through a later explicit
  signed grant;
- one exact owner-self-signed v2-to-v3 migration; and
- durable capability bits 8–11 for synchronization, only in v3 and only through a later explicit
  owner activation and delegation.

Migration preserves every existing principal's exact v1 mask. It changes the record/header/signature
domain but grants no terminal authority. The historical `all` spelling remains bits 0 through 6;
`all-v2` is the explicit bits-0-through-7 opt-in; `all-v3` explicitly includes bits 8–11. Route binding, fully enforced time bounds, and
namespace membership remain future formats.

A device evaluates relevant authority locally without asking an IoTox account service.

## Durable commands are downstream of authority

rev0010 persists a command before transport or effect and freezes the authority-ledger head used
for admission. This improves auditability but does not turn an old grant into permanent power.
The generic engine still needs exact rules for revocation between receipt, admission, start, and
an interruptible effect.

The command store is signed by the stable device identity. It is not an ownership ledger and
cannot grant capability. The authority ledger rejects a header/history mismatch, a v1 record after
migration, and cross-domain record reinterpretation. Its private `IOTOXAG2` guard also detects
rollback, deletion, or fork of the ledger alone and recovers the two exact interrupted replace
states. A same-privilege attacker can still restore both ledger and guard as an older consistent
pair. The optional authenticated external authority and command-effect lanes now detect those
specific coordinated snapshots relative to their separately retained service records. The
per-namespace lanes similarly detect older complete four-root or tree-v2 frontier/workspace/
maintenance plus guard snapshots, but only for each explicitly enrolled namespace and only after
the complete namespace-policy tree is witnessed. They are not whole-store, content, or backup
freshness, nor a continuously renewed lease against a live clone.
ADR 0313 lets the service sign its complete selector population and enforce an operator-supplied
checkpoint as a restart floor. A separately retained current artifact detects selective service-file
rollback or omission before the listener binds. These are implemented protocols, not proof that any
deployment actually placed the service or checkpoint under independent, rollback-resistant
administration; unwitnessed, stale-floor, or same-failure-domain deployments retain the original
limitation.

## Re-entry path and remaining discovery gap

1. A local `iotox` client reconstructs the stable owner principal from RecallRoot input.
2. The daemon prepares canonical authority bytes without receiving the phrase or owner secret.
3. The client signs locally and submits only the signed record or session proof.
4. A confirmed peer challenge binds proof to verifier device, ledger head, session digest,
   nonce, and challenge ID.
5. Ordinary operation moves to narrower delegated controller credentials.

Before using a v1 ledger for terminal-capable policy, migrate it through one signed,
non-widening ceremony. For the local device:

```sh
printf '%s\n' "$LOCAL_RECALL_PHRASE" | \
  iotox --runtime "$LOCAL_RUNTIME" authority-migrate-v2-recall-stdin
```

For a connected target, complete the current recalled-owner proof, sign the exact remote migration,
confirm the correlated result, and then run a fresh proof before any later grant or mutation:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-migrate-v2-remote-recall-stdin "$TARGET_FRIEND"
iotox --runtime "$CONTROLLER_RUNTIME" authority-delegation "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
```

The migration record retains owner capabilities exactly `0x7f`. A terminal-capable owner,
administrator, or operator requires a separate v2 grant containing `interactive.terminal`; migration
alone is never sufficient. Feature bit 24 must have been negotiated for the exact online epoch.

For v3, pass the current owner's exact v2 mask rather than guessing it:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-migrate-v3-remote-recall-stdin "$TARGET_FRIEND" all-v2
```

The target must negotiate both authority feature bits 24 and 25. Migration preserves the supplied
exact mask; a fresh proof and separate `all-v3` or named sync grant are required afterward.

For a fresh controller already connected to the target device, the concrete ceremony is:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-delegate-self-recall-stdin "$TARGET_FRIEND" automation read.telemetry
iotox --runtime "$CONTROLLER_RUNTIME" authority-delegation "$TARGET_FRIEND"
```

`TARGET_DEVICE_RECALL_PHRASE` reconstructs the target device's owner, not the controller's owner.
The ordinary fresh-device proof is expected to be denied first. Exactly one explicit recalled-owner
proof may replace that denied candidate; an authorized proof remains frozen. The target then appends
an owner-signed grant whose subject is the connected controller's stable device key. The phrase and
owner secret exist only in the client process and are never sent to the daemon or peer.

An enrolled controller can enter a later explicit owner administration proof and revoke an active
non-owner principal. Owner principals are categorically excluded from this remote ceremony:

```sh
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_DEVICE_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-revoke-remote-recall-stdin "$TARGET_FRIEND" "$SUBJECT_PUBLIC_KEY"
iotox --runtime "$CONTROLLER_RUNTIME" authority-delegation "$TARGET_FRIEND"
```

For planned transfer or suspected phrase compromise, first derive the new phrase's public owner key
without contacting a daemon. The current owner signs an exact nomination, and the immediately
nominated successor signs the epoch transition:

```sh
SUCCESSOR_PUBLIC_KEY=$(
  printf '%s\n' "$SUCCESSOR_RECALL_PHRASE" | \
    iotox recall-owner-public-key-stdin | sed -n 's/^owner-public-key=//p'
)
printf '%s\n' "$CURRENT_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$CURRENT_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-nominate-successor-remote-recall-stdin \
  "$TARGET_FRIEND" "$SUCCESSOR_PUBLIC_KEY"
printf '%s\n' "$SUCCESSOR_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$SUCCESSOR_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-transition-remote-recall-stdin "$TARGET_FRIEND"
```

Confirm each correlated result before the next step. No mutation may intervene between nomination
and transition. The completed transition makes the successor the only live principal, so every
controller must be delegated again. It limits future use of the retired phrase but cannot undo
prior effects, defeat a race by another holder of the current phrase, or detect restoration of an
older complete ledger.

Still unresolved: discovery of current route bindings from memory alone, destructive physical
reclaim after all owner secrets are lost, multi-owner/quorum policy, and rollback detection.

## Printed phrase operational questions

- How is the phrase generated with verifiable uniformity?
- How is a printout made without leaving spool or application history?
- How does a user verify transcription?
- Can a hardware token hold one copy without becoming mandatory?
- What warnings are needed for photography, cloud notes, or password-manager entry?
- How can the phrase be entered without argv, shell history, logs, crash dumps, or swap?
- What happens when the phrase is believed exposed?

The answer cannot be “add a vendor reset.”
