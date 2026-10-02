# IoTox authority ledger and directional proof v3

**Implemented:** current main  
**Prerequisite:** authority-ledger v2 plus a signed migration  
**Feature bit:** `authorization-ledger-v3` (bit 25)  
**New durable capabilities:** bits 8 through 11  
**New action:** `migrate-v3` (6)

Authority-ledger v3 admits synchronization authority without changing any v1 or v2 byte, mask,
parser, role-ceiling, aggregate-token, feature, or signature contract. Migration changes the active
format and cryptographic domains only. It grants no synchronization power.

## 1. Capability contract

| Bit | Name | v1 | v2 | v3 |
|---:|---|:---:|:---:|:---:|
| 0 | `read.telemetry` | yes | yes | yes |
| 1 | `write.settings` | yes | yes | yes |
| 2 | `actuate` | yes | yes | yes |
| 3 | `manage.principals` | yes | yes | yes |
| 4 | `install.firmware` | yes | yes | yes |
| 5 | `export.diagnostics` | yes | yes | yes |
| 6 | `factory.reset` | yes | yes | yes |
| 7 | `interactive.terminal` | no | yes | yes |
| 8 | `sync.admin` | no | no | yes |
| 9 | `sync.publish` | no | no | yes |
| 10 | `sync.subscribe` | no | no | yes |
| 11 | `sync.activate` | no | no | yes |

```text
v1 mask       0x000000000000007f
v2 mask       0x00000000000000ff
v3 mask       0x0000000000000fff
all           v1 mask, permanently
all-v1        v1 mask, permanently
all-v2        v2 mask, permanently
all-v3        v3 mask, explicit opt-in
```

`all-with-sync` is a compatibility spelling for `all-v3`; `all-with-terminal` remains exactly v2.
Unknown bits, empty grants, and capabilities above a role ceiling are rejected.

## 2. Role ceilings

| Role | v3 ceiling | Synchronization rights permitted by the ceiling |
|---|---:|---|
| owner | `0xfff` | admin, publish, subscribe, activate |
| administrator | `0xfbf` | admin, publish, subscribe, activate |
| operator | `0xc87` | subscribe, activate |
| viewer | `0x401` | subscribe |
| automation | `0xe07` | publish, subscribe, activate |
| service | `0x623` | publish, subscribe |

A ceiling is not a grant. The signed principal record must contain the bit, and namespace policy is
still an independent mandatory constraint. `sync.subscribe` grants neither activation nor firmware
installation. `sync.activate` authorizes a request but cannot bypass activation mode, exact accepted
HEAD, object verification, or local transaction policy.

## 3. Ledger and signed-record formats

The file remains a private atomic sequence of fixed 256-byte records. A v3 ledger header is:

| Offset | Size | Value |
|---:|---:|---|
| 0 | 8 | `IOTOXAL3` |
| 8 | 1 | `3` |
| 9 | 1 | `0`, mixed signed-history marker |
| 10 | 2 | zero |
| 12 | 4 | big-endian record count |

A v3 signed record keeps the established 192-byte body plus 64-byte Ed25519 signature layout. It
uses magic `IAL3`, record-format byte `3`, and the existing field offsets. Reserved bytes remain zero.

The independent signature and digest domains are:

```text
iotox-authority-record-signature-v3
iotox-authority-record-digest-v3
```

Changing an `IAL2` marker to `IAL3`, or the inverse, invalidates the signature. A ledger header must
equal the format reached by replay of the complete signed history.

## 4. Non-widening migration

The only v3 transition is one signed `migrate-v3` record with:

```text
record format       v3
action              migrate-v3
role                owner
sequence            current v2 sequence + 1
ownership epoch     unchanged
capabilities        exact current issuer capability mask, within v2
issuer              current active owner
subject             same current active owner
device              same stable device
previous digest     exact current v2 tail
time fields         zero
```

Migration is valid only from v2. It preserves every active principal, role, capability mask, and
ownership epoch exactly and clears any pending successor nomination. Direct v1-to-v3 migration,
repeated migration, a widened migration mask, a non-owner issuer, or a changed subject fails before
mutation.

After migration, an owner may explicitly self-grant missing format-extension bits. That activation
record must retain all capabilities the owner already holds; it cannot combine a new sync grant with
a capability removal. The owner must receive a bit before delegating it to another principal. This is
stricter than the historical v2 terminal-activation rule, whose behavior remains unchanged.

## 5. Replay and rollback guard

The only accepted format order is:

```text
one v1 bootstrap
zero or more v1 records
one v2 migrate-v2 record
zero or more v2 records
one v3 migrate-v3 record
zero or more v3 records
```

The existing fixed `IOTOXAG2` committed/pending rollback guard stores the ledger-format byte in each
head and therefore covers v3 without changing its binary layout. A persisted v2 or v3 ledger without
its guard fails closed. Exact interrupted ledger/guard replacement states remain recoverable; an
unrelated head, deletion, fork, or local downgrade is rejected. Coordinated restoration of both files
still requires an external monotonic witness to detect.

## 6. Directional online proof

V3 challenge and proof bodies retain their fixed sizes and field offsets. Their wire-format byte and
embedded ledger-format byte are both `3`. Proof signatures use the independent domain:

```text
iotox-authority-session-proof-v3
```

The confirmed HELLO epoch must share both `authorization-ledger-v2` bit 24 and
`authorization-ledger-v3` bit 25. Requiring the lineage bit prevents an isolated v3 feature marker
from skipping the defined migration ancestry. A challenge/proof remains bound to the exact device,
ownership epoch, sequence, tail digest, canonical session transcript, nonce, and challenge message ID.

Any ledger mutation invalidates the old proof. A sync effect must use the exact-head authorization
check; a merely connected friend or a proof against an earlier head is insufficient.

## 7. Local and remote ceremonies

The migration record must carry the current owner's exact v2 capabilities. The CLI requires that mask
as an explicit argument so it never guesses whether bit 7 was previously activated.

Local migration:

```sh
printf '%s\n' "$RECALL_PHRASE" | \
  iotox --runtime "$RUNTIME" \
  authority-migrate-v3-recall-stdin CURRENT_CAPABILITIES
```

Remote migration after a fresh recalled-owner proof:

```sh
printf '%s\n' "$RECALL_PHRASE" | \
  iotox --runtime "$RUNTIME" \
  authority-migrate-v3-remote-recall-stdin FRIEND CURRENT_CAPABILITIES
```

`CURRENT_CAPABILITIES` is normally `all` or `all-v2`, or an exact named list. `all-v3` is rejected for
migration because migration cannot widen. After the correlated result and a fresh proof, a separate
owner self-grant such as `all-v3` activates the desired v3 rights.

## 8. Retained nonclaims

- V3 does not enable synchronization transport, namespace service, content projection, or OTA.
- Capability possession does not satisfy namespace membership, writer signature, HEAD linkage,
  quotas, object verification, activation mode, or filesystem policy.
- The rollback guard is not a hardware, network, or replicated monotonic witness.
- V3 does not add trusted clocks, temporary grants, confidential content, or distributed consensus.
