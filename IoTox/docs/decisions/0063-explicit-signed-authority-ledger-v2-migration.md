# ADR 0063: Migrate authority-ledger v1 to v2 with an explicit non-widening signed transition

Status: accepted  
Date: 2026-08-16

## Context

Ratox v1 reserves durable capability bit 7 for `interactive.terminal`. The deployed authority-ledger
v1 contract defines only bits 0 through 6, and its source-level `all` value means exactly those seven
bits. Simply adding bit 7 to the old mask would reinterpret existing source, records, owner grants,
role ceilings, session proofs, and recovery ceremonies as terminal authority. Changing only the
ledger header would also leave old and new signatures in the same domain and make the active format
ambiguous during replay.

R2 must add the capability without creating a PTY, advertising Ratox feature bit 23, or allowing an
upgrade to manufacture shell access. New code must continue to read valid v1 ledgers. Old code must
reject v2 rather than truncate or ignore the new bit. Local and remote migration must extend the
exact signed head, survive restart, and force a fresh authority proof before any later mutation.

The signed append history authenticates content and ordering but does not by itself distinguish a
current file from an older valid copy. The migration therefore also needs a local crash-recoverable
head witness that fails closed when only the ledger is rolled back, deleted, or forked, while stating
honestly that an attacker capable of coordinated replacement of both local files is still outside
that witness.

## Decision

Introduce `AuthorityLedgerFormat::v2`, capability bit 7 `interactive.terminal`, one signed
`migrate-v2` action, negotiated authority feature bit 24, and a separate two-head rollback guard. The
transition is a permanent signed format boundary, not a metadata rewrite.

### Stable capability meanings

- `kAuthorityV1Capabilities` remains `0x7f`.
- `kAuthorityV2Capabilities` is `0xff`.
- `kAllCapabilities` deliberately remains the v1 mask so recompiling an existing caller cannot add
  terminal authority.
- CLI tokens `all`, `all-v1`, and `legacy-all` remain `0x7f`; `all-v2` and
  `all-with-terminal` are the explicit `0xff` opt-in.
- The format-less `role_capability_ceiling(role)` remains a v1 compatibility API. Code operating on
  a v2 ledger must pass the format explicitly.
- Unknown capability bits are rejected in every format.

### Signed record and file domains

A v2 record uses `IAL2`, record-format byte 2, and independent permanent domains:

```text
iotox-authority-record-signature-v2
iotox-authority-record-digest-v2
```

A v2 ledger file uses `IOTOXAL2`, ledger-format byte 2, and record-format header byte 0. Zero means
that the file may contain the one allowed mixed history: signed v1 records followed by one signed v2
migration record and then only signed v2 records. The replayed signed history, not the header alone,
determines the active format. A header whose claimed format disagrees with replay is rejected.

### Exact migration policy

The only valid migration record:

- extends an initialized v1 ledger's exact epoch, sequence, and tail digest;
- is encoded and signed as v2 action `migrate-v2`;
- is self-signed by the active owner named as both issuer and subject;
- retains role `owner` and capabilities exactly `0x7f`;
- keeps the same device and ownership epoch;
- increments the current sequence once; and
- may occur exactly once.

Migration changes the active record domain and capability vocabulary. It does not edit any existing
principal, grant bit 7, nominate a successor, or reset an epoch. Every v1 principal therefore keeps
its exact old capability mask. A second migration, a v1 record after migration, a widened migration,
or a header-only conversion is invalid.

### Explicit terminal activation

After migration, terminal authority exists only after a separate signed v2 `grant`. Because the
migrating owner still has `0x7f`, v2 permits an active owner to add only the otherwise-missing bit 7
in an explicit grant. No other missing capability may be manufactured. The ordinary role ceiling
still applies: owner and administrator can carry bit 7, operator can carry it with its existing
operator capabilities, while viewer, automation, and service cannot.

An owner must always retain every constitutional v1 owner bit. Successor nomination records carry an
exact capability set, and the successor-signed epoch transition must preserve that exact set. An
ownership transition therefore cannot silently add terminal authority either.

### Session and remote-mutation binding

Capability-session feature bit 24 names `authorization-ledger-v2`. A v2 authority challenge and
proof carry wire format 2 and an explicit ledger-format byte 2. The v2 proof signature domain is:

```text
iotox-authority-session-proof-v2
```

The negotiated feature mask is part of the confirmed session transcript. A v2 challenge, proof,
remote migration preparation, remote migration application, or v2 duplicate acknowledgement is
refused unless bit 24 was negotiated for that exact online epoch. A peer that negotiated only v1 may
continue v1 authority interaction with a v1 verifier; a migrated v2 verifier does not silently
reinterpret or downgrade its local head to accommodate that peer.

Every remote mutation remains bound to the exact local format, ownership epoch, sequence, and tail
that the peer proved. Applying a mutation invalidates that proof. An exact signed tail duplicate is
a content-addressed no-op for transport retry, but it is acknowledged only for the same connected,
negotiated device/session capability boundary and is never appended again.

### RecallRoot prepared-body verification

The daemon prepares canonical unsigned record bytes, but it is not trusted to choose what the human
asked to sign. Before deriving a signature, the RecallRoot client decodes the returned body and
compares its action, role, capability set, issuer, subject, zero time fields, and required migration
format against the requested ceremony. Any substitution is rejected before a signature or signed
record is transmitted. The phrase and owner secret remain in the client process only.

### Local rollback guard

The default guard path is `<ledger>.guard`. It is a private, atomically replaced 192-byte
`IOTOXAG2` file bound to the stable device public key. It contains one committed authority head and,
while an append is in flight, one pending head. Each head includes initialized state, ledger format,
record count, ownership epoch, sequence, and tail digest.

The append transaction is:

1. verify the guard's committed head equals the live ledger head, reconciling only an exact prior
   interrupted state;
2. atomically publish `committed=current, pending=next`;
3. atomically replace the signed ledger with `next`;
4. atomically promote `next` to the committed guard head and clear pending.

Startup and the next live append accept only two interrupted transition states:

- the ledger still equals `committed`, meaning the ledger replace did not land; or
- the ledger equals `pending`, meaning the ledger landed but final guard promotion did not.

Every third head is rejected as rollback, deletion, or fork evidence. An existing valid unguarded v1
ledger is adopted by writing its current head into a new guard. A persisted v2 ledger without its
guard is rejected rather than silently re-adopted.

The guard is not signed, not hardware monotonic, and not an independent trust domain from the local
same-UID storage boundary. Reverting or replacing the ledger alone is detected; coordinated
replacement of both ledger and guard with a mutually consistent older pair is not. Hardware
counters, replicated witnesses, or owner-observed checkpoints remain separate milestones.

## Consequences

R2 now permits a transcript-confirmed principal to prove an explicitly granted terminal bit under a
v2 ledger while every untouched v1 ledger and every non-terminal principal remains denied. Local
RecallRoot and remote recalled-owner ceremonies can prepare and sign the exact migration without
sending the phrase or owner secret to the daemon or peer. Restart replay accepts the one mixed
history and rejects malformed format boundaries.

The local guard detects single-file ledger rollback, deletion, and fork, and recovers the two exact
interrupted append states without requiring a restart. It does not justify a general claim of
rollback-resistant authority storage against coordinated same-privilege replacement.

The authority fuzzer and deterministic tests cover v1/v2 canonical round trips, independent
signature domains, exact non-widening migration, role ceilings, stale/downgraded records, header
mismatch, remote feature negotiation, duplicate retry, proof invalidation, ownership transition,
restart, guard adoption/recovery/tamper cases, and prepared-body substitution refusal.

R2 still creates no process, PTY, terminal stream, Ratox Agent dispatch, or advertised Ratox feature.
R3 is the next independent prerequisite; R4 may join R1-R3 only after R3's fake-backed PTY/profile
exit gate passes.

## Rejected alternatives

- **Expand v1 `all` to include bit 7.** This grants terminal authority by recompilation and changes
  the meaning of old policy text.
- **Rewrite the file header without a signed record.** This makes the transition unauditable and
  permits unsigned format selection.
- **Give all v1 owners bit 7 during replay.** Ownership is not equivalent to terminal use, and an
  upgrade must not create a remote shell grant.
- **Reuse v1 signature and digest domains.** Cross-version reinterpretation would weaken the format
  boundary and downgrade analysis.
- **Drop v1 read support.** Existing devices need a controlled in-place ceremony rather than an
  offline ledger replacement.
- **Store only one guard head.** A crash between two atomic replaces would make either the old or new
  exact state indistinguishable from rollback. The bounded pending head makes both sides explicit.
- **Treat the guard as complete rollback protection.** It catches ledger-only replacement but is
  locally writable beside the ledger and supplies no external monotonic witness for coordinated
  pair replacement.
