# Signed peer invitations

ADR 0293 completes product-expansion workstream 5 with one bounded transport-introduction ceremony.
An invitation binds the inviter's stable IoTox device identity to its exact current 38-byte Tox
address, an expiry, a random nonce, an optional alias suggestion, and a closed set of requested
capabilities. It does not grant friendship by being inspected, and friendship does not grant IoTox
authority when it is accepted.

## Operator ceremony

For human setup, the native pair-card porch is the shortest safe entry:

```sh
iotox pair-card create ./workstation.iotox-invitation \
  --expires 86400 --alias workstation \
  --capabilities interactive.terminal,sync.subscribe
iotox pair-card inspect ./workstation.iotox-invitation \
  INVITER_STABLE_PRINCIPAL_HEX
iotox pair-card accept ./workstation.iotox-invitation \
  INVITER_STABLE_PRINCIPAL_HEX --alias workstation
```

These commands print the underlying `peer-invitation-*` operation and keep the
same boundary: `authority-granted=0`.

On the inviting Agent, create one no-clobber private artifact. The lifetime is 60 seconds through 30
days:

```sh
iotox peer-invitation-create ./workstation.iotox-invitation 86400 \
  workstation interactive.terminal,sync.subscribe
```

The command asks the live Agent to sign its exact current Tox address with its stable device identity.
It independently verifies the returned artifact before creating a mode-`0600` output. Existing output
is never replaced. `-` means no alias suggestion or no requested capabilities.

Move the artifact through any convenient out-of-band channel. Move the printed
`inviter-stable-principal` through an independently trusted channel: in person, a previously pinned
record, or another method appropriate to the deployment. A self-signature proves integrity and key
possession; it does not tell a recipient that an unknown key belongs to the intended human or device.

The recipient may inspect without asserting trust:

```sh
iotox peer-invitation-inspect ./workstation.iotox-invitation
```

Then perform the dry import preflight with the independently pinned stable principal:

```sh
iotox peer-invitation-import ./workstation.iotox-invitation \
  INVITER_STABLE_PRINCIPAL_HEX
```

`import` is intentionally nonmutating. It rechecks the complete canonical artifact, Ed25519
signature, exact pinned inviter, issue time, expiry, and five-minute future-clock tolerance, then
prints `import-ready=1` and `import-mutated-state=0`. It creates no inbox, friend, alias, authority
record, capability, profile binding, or sync policy.

Acceptance is the distinct effect:

```sh
iotox peer-invitation-accept ./workstation.iotox-invitation \
  INVITER_STABLE_PRINCIPAL_HEX
```

The optional final argument overrides the suggested alias; `-` suppresses alias creation. Acceptance
sends one ordinary Tox friend request to the exact signed address and then applies the alias through
the existing one-to-one signed alias store. The fixed request message carries a short artifact ID,
not arbitrary remote-selected content. Exact retry before expiry is idempotent: an existing exact
friend is reused and the same alias binding does not advance its generation.

If friendship succeeds but alias persistence fails, the command says so and returns failure. It does
not delete the friend as compensation; an exact retry can finish the alias while the invitation is
valid. A conflicting alias or key remains refused. After expiry, inspect still works for forensics,
but import and acceptance fail.

## Frozen artifact

`IOTXINV1` is exactly 320 bytes: a 256-byte canonical body and 64-byte Ed25519 signature. The body
contains format and zero padding, issue/expiry Unix milliseconds, a 32-byte random nonce, the
32-byte inviter stable principal, the complete 38-byte Tox address, the authority-v3 requested
capability bitset, and a zero-padded canonical alias slot. The signature covers a hash in the
`peer-invitation-v1` domain. The displayed artifact ID hashes the complete signed record in the
separate `peer-invitation-record-v1` domain.

Unknown capability bits, noncanonical aliases or padding, zero signing/transport identities,
oversized lifetimes, signature tampering, a wrong pinned inviter, a future issue time beyond five
minutes, and expiry all fail closed. The Tox provider remains responsible for validating the address
checksum, own-key, nospam, and duplicate transport conditions when acceptance requests friendship.

## Authority and time boundary

Requested capabilities are a reviewable statement of intent only. Acceptance always prints
`authority-granted=0`. The new peer must still negotiate an IoTox session, prove the stable principal,
receive an explicit signed ledger grant, and satisfy any Ratox profile or sync namespace membership
policy. In particular, this artifact does not install a synchronization policy or turn a read-only
request into access.

Expiry uses the two machines' ordinary wall clocks. Because friendship alone is not authority, IoTox
does not make a wall-clock rollback witness a prerequisite for this ceremony. A bad or rolled-back
clock can reject a legitimate invitation or extend transport-level replay; it cannot manufacture a
different signed address, alias replacement, or capability grant. Workstream 8 owns independent
rollback witnesses where stronger time/state claims are required.

The accepted artifact is not automatically retained as a trust database. The operator-supplied pin
is checked at import and acceptance, and the artifact remains the portable receipt. A later endpoint
migration still needs a separate verified rebind ceremony; aliases never silently follow a claimed
stable principal.
