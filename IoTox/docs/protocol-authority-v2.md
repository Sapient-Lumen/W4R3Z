# IoTox authority ledger, rollback guard, and directional proof v2

**Implemented:** rev0016  
**Prerequisite:** authority-ledger v1 plus a signed migration  
**Feature bit:** `authorization-ledger-v2` (bit 24)  
**New durable capability:** `interactive.terminal` (bit 7)  
**New action:** `migrate-v2` (5)

Authority-ledger v2 adds one capability without changing the meaning of any v1 record or source-level
`all` value. It is a signed, replayed transition and still creates no PTY or Ratox service.
Authority-ledger v3 extends only an exact v2 tail and is specified separately in
`protocol-authority-v3.md`; nothing in that successor changes this v2 contract.

## 1. Capability contract

| Bit | Name | v1 | v2 |
|---:|---|:---:|:---:|
| 0 | `read.telemetry` | yes | yes |
| 1 | `write.settings` | yes | yes |
| 2 | `actuate` | yes | yes |
| 3 | `manage.principals` | yes | yes |
| 4 | `install.firmware` | yes | yes |
| 5 | `export.diagnostics` | yes | yes |
| 6 | `factory.reset` | yes | yes |
| 7 | `interactive.terminal` | no | yes |

```text
v1 mask       0x000000000000007f
v2 mask       0x00000000000000ff
all           v1 mask, permanently
all-v1        v1 mask
all-v2        v2 mask, explicit opt-in
```

Role ceilings are format-sensitive:

| Role | v1 ceiling | v2 ceiling |
|---|---:|---:|
| owner | `0x7f` | `0xff` |
| administrator | `0x3f` | `0xbf` |
| operator | `0x07` | `0x87` |
| viewer | `0x01` | `0x01` |
| automation | `0x07` | `0x07` |
| service | `0x23` | `0x23` |

Unknown bits, empty grants, and capabilities above a role ceiling are rejected.

## 2. Ledger file header

The file remains a private atomic sequence of fixed 256-byte signed records.

| Offset | Size | v1 | v2 |
|---:|---:|---|---|
| 0 | 8 | `IOTOXAL1` | `IOTOXAL2` |
| 8 | 1 | ledger format `1` | ledger format `2` |
| 9 | 1 | record format `1` | `0`, mixed signed history marker |
| 10 | 2 | zero | zero |
| 12 | 4 | big-endian record count | big-endian record count |

For v2, byte 9 is zero because a valid migrated file contains v1 records before its single v2
transition. Replay must end in the same format claimed by the header. The header cannot convert or
reinterpret records.

## 3. Signed v2 record

The record remains 256 bytes: a 192-byte body followed by a 64-byte Ed25519 signature.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | `IAL2` |
| 4 | 1 | record format `2` |
| 5 | 1 | action |
| 6 | 1 | role |
| 7 | 1 | zero flags |
| 8 | 8 | sequence |
| 16 | 8 | ownership epoch |
| 24 | 8 | `not_before`, zero in current policy |
| 32 | 8 | `not_after`, zero in current policy |
| 40 | 8 | capability mask |
| 48 | 32 | stable device public key |
| 80 | 32 | issuer principal public key |
| 112 | 32 | subject principal public key |
| 144 | 32 | previous signed-record digest |
| 176 | 16 | zero reserved bytes |
| 192 | 64 | Ed25519 signature |

The signature envelope is:

```text
"IOTOXS1"
2-byte domain length
domain = "iotox-authority-record-signature-v2"
exact 192-byte body
```

The record digest is BLAKE2b-256 under:

```text
iotox-authority-record-digest-v2
```

V1 retains its independent `...-v1` signature and digest domains.

## 4. Migration record

A migration is valid only when all fields match this policy:

```text
record format       v2
action              migrate-v2
role                owner
sequence            current v1 sequence + 1
ownership epoch     current v1 epoch
capabilities        exactly 0x7f
issuer              current active owner
subject             same current active owner
device              same stable device
previous digest     exact current v1 tail
time fields          zero
```

The migration is signed under the v2 record domain. It changes only the active ledger format. It
preserves every principal's exact active state and capability mask. It clears any pending successor
nomination and can occur only once.

A later, separate v2 `grant` is required to add bit 7. A v2 owner may explicitly activate only that
new bit when it is missing from the owner's existing `0x7f`; the ordinary role ceiling and all other
delegation rules still apply.

## 5. Mixed-history replay

The only accepted format sequence is:

```text
one v1 bootstrap
zero or more v1 grant/revoke/transition records
one v2 migrate-v2 record
zero or more v2 grant/revoke/transition records
```

An ownership epoch transition may reset sequence to one but does not change the active ledger
format. A migration never resets the epoch. Sequence or epoch overflow is rejected before mutation.

## 6. Private rollback guard

The default guard path is `<ledger>.guard`. It is a separate private 192-byte file written with the
same no-follow, owner/mode, bounded-read, and atomic-replace storage discipline as other private
state. It is not a signed ledger record and it is not a hardware counter.

### Guard layout

| Offset | Size | Field |
|---:|---:|---|
| 0 | 8 | `IOTOXAG2` |
| 8 | 1 | guard format `2` |
| 9 | 1 | flags; bit 0 means pending head present |
| 10 | 6 | zero reserved bytes |
| 16 | 32 | stable device public key |
| 48 | 64 | committed head |
| 112 | 64 | pending head, or all zero when absent |
| 176 | 16 | zero reserved bytes |

Each 64-byte head is:

| Head offset | Size | Field |
|---:|---:|---|
| 0 | 1 | initialized flag, 0 or 1 |
| 1 | 1 | authority ledger format, 1 or 2 |
| 2 | 6 | zero reserved bytes |
| 8 | 8 | record count |
| 16 | 8 | ownership epoch |
| 24 | 8 | sequence |
| 32 | 32 | signed-record tail digest |

An uninitialized head must be exactly format v1 with zero counters and digest. An initialized head
must have nonzero record count, epoch, and sequence.

### Append transaction and recovery

For current head `C` and validated next head `N`:

```text
1. guard := committed C, pending N
2. atomically replace ledger with N
3. guard := committed N, no pending
```

Before step 1, a live append verifies that the guard still matches `C`. On startup or before a later
live append, a pending guard is recoverable only when the ledger equals one of its exact heads:

```text
ledger == committed   replace did not land; clear pending
ledger == pending     replace landed; promote pending
anything else         reject rollback, deletion, or fork
```

A valid unguarded v1 ledger is adopted once by writing its current head. A persisted v2 ledger whose
guard is absent is rejected. A guard bound to another device, malformed reserved bytes, invalid
counters, unexplained pending bytes, or disappearance during an established live session is also
rejected.

This mechanism detects rollback, deletion, or fork of the ledger alone relative to the retained
guard. A same-privilege attacker who restores both files to a mutually consistent older pair can
bypass this local witness. Hardware monotonic state, an external replicated witness, or an
owner-observed checkpoint is still required for that coordinated-snapshot threat.

## 7. Directional challenge and proof v2

The outer IoTox frame types, sequences, correlations, and sizes remain those of authority-session
v1. The payload explicitly names the v2 format.

### Challenge, 160 bytes

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | `IAC1` |
| 4 | 1 | challenge wire format `2` |
| 5 | 1 | authority ledger format `2` |
| 6 | 2 | zero |
| 8 | 32 | verifier stable device principal |
| 40 | 8 | ownership epoch |
| 48 | 8 | authority sequence |
| 56 | 32 | authority tail digest |
| 88 | 32 | confirmed-session transcript digest |
| 120 | 32 | fresh nonzero challenge nonce |
| 152 | 8 | zero |

### Proof, 256 bytes

The first 192 bytes are the signed body:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | `IAP1` |
| 4 | 1 | proof wire format `2` |
| 5 | 1 | authority ledger format `2` |
| 6 | 2 | zero |
| 8 | 32 | verifier stable device principal |
| 40 | 32 | claimant stable principal |
| 72 | 8 | ownership epoch |
| 80 | 8 | authority sequence |
| 88 | 32 | authority tail digest |
| 120 | 32 | confirmed-session transcript digest |
| 152 | 32 | challenge nonce |
| 184 | 8 | challenge outer message ID |
| 192 | 64 | Ed25519 signature |

The v2 proof domain is:

```text
iotox-authority-session-proof-v2
```

Changing only the v1/v2 wire marker invalidates the signature. Challenge/proof creation and receipt
require negotiated feature bit 24. The runtime peer projection records
`authority-v2-negotiated=1` only for that exact confirmed online epoch.

Negotiation is directional. Each verifier challenges against its own current ledger format. A v1
verifier can continue a v1 exchange with a peer that supports v1; a migrated v2 verifier remains
inactive toward a v1-only peer rather than issuing v1 evidence for a v2 head. A capable peer can
answer the independently negotiated format requested by the other side without conflating the two
local ledgers.

## 8. Remote migration and mutation

Remote owner mutations require a connected peer, negotiated authority v1, a current proven owner
with `manage.principals`, and equality with the exact challenged local format/epoch/sequence/tail.
Migration additionally requires negotiated authority v2.

An applied mutation invalidates the just-used proof. The sender must complete a fresh challenge and
proof round before preparing another mutation. A byte-identical signed tail duplicate is an
idempotent no-op for transport retry; it is never appended twice and is acknowledged only inside the
same negotiated format boundary.

## 9. RecallRoot operator ceremonies

Local migration, with the phrase read only by the client process:

```sh
printf '%s\n' "$RECALL_PHRASE" | \
  iotox --runtime "$RUNTIME" authority-migrate-v2-recall-stdin
```

Remote migration of a connected target after recalled-owner proof:

```sh
printf '%s\n' "$TARGET_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-prove-recall-stdin "$TARGET_FRIEND"
printf '%s\n' "$TARGET_RECALL_PHRASE" | \
  iotox --runtime "$CONTROLLER_RUNTIME" \
  authority-migrate-v2-remote-recall-stdin "$TARGET_FRIEND"
iotox --runtime "$CONTROLLER_RUNTIME" authority-delegation "$TARGET_FRIEND"
```

Before signing any daemon-prepared body, the client decodes it and verifies exact equality with the
requested action, role, capabilities, issuer, subject, zero time fields, and required ledger format.
A substituted body is refused before a signature or signed record leaves the client. Then run a
fresh proof before an explicit terminal grant. Use a role-specific capability list or explicit
`all-v2`; plain `all` remains v1-only.

## 10. Compatibility and nonclaims

New binaries read valid v1 files and deny bit 7 there. Old binaries reject the v2 header, v2 record,
and unknown migration action rather than masking the bit. V2 does not provide a PTY, shell profile,
Ratox dispatch, feature bit 23 advertisement, trusted time bounds, route binding, quorum ownership,
or hardware-backed rollback resistance.

The signed ledger detects header/history mismatches and in-history downgrade attempts. The local
guard additionally detects rollback, deletion, or fork of the ledger file alone and recovers the two
exact interrupted replace states. Restoring both the ledger and guard as one older consistent pair
remains possible without an external monotonic witness. A rollback to v1 removes terminal authority
but may resurrect older principal state.
