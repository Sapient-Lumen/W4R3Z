# Human peer aliases

ADR 0292 adds durable owner-local names for exact Tox peer public keys. An alias is typing and memory
ergonomics. It is not IoTox authority, discovery, a stable-device identity, or an invitation.

## Commands

```sh
iotox peer-alias-set workstation PEER
iotox peer-aliases
iotox peer-alias-rename workstation desktop
iotox peer-alias-remove desktop
```

`peer-alias-set` may bind only a current Tox friend. The Agent rechecks that exact 32-byte key at the
mutation boundary. One name maps to one key and one key has at most one name. Repeating the same
binding is an idempotent no-op. A name collision, key collision, or implicit replacement is refused;
rename is one explicit atomic mutation. To bind an existing name to a different peer, remove it and
then set it again as two visible operations.

Names are 1..63 ASCII bytes, begin with lowercase `a`--`z`, and then contain only lowercase letters,
digits, dot, underscore, or hyphen. There is no case folding, Unicode normalization, abbreviation,
prefix matching, or implicit DNS/hostname interpretation.

## Selector grammar

Every ordinary established-peer command in the main CLI and all four terminal commands use one
shared grammar:

```text
friend:17                 explicit process-local friend number
key:64_HEXADECIMAL_BYTES  explicit Tox public key
alias:workstation         explicit owner-local alias
17                        compatibility bare friend number
64_HEXADECIMAL_BYTES      compatibility bare Tox public key
workstation               compatibility bare canonical alias
```

Precedence is fixed in that order. Bare aliases begin with a letter and are at most 63 bytes, so
they cannot collide with decimal friend numbers or 64-hex keys. The three prefixes are escape hatches
and never fall through to another interpretation. Friend-request accept/reject and initial add still
take literal public keys because a not-yet-friend cannot already receive a new alias.

Commands that require a live friend resolve the alias to its exact key and then require that key in
the current toxcore friend inventory. Historical key-oriented reads such as a durable command record
can resolve a retained alias even when the friend is absent. Ratox terminal open/resume/list/close
resolve through the same control plane before touching the terminal socket.

## Persistence and deletion

The default store is
`SAVEDATA_PARENT/.iotox-aliases/SAVEDATA_FILENAME.peer-aliases`; a deployment may select an absolute
path with `--peer-alias-store`. The bounded canonical store holds at most 256 lexically sorted,
one-to-one entries. Every changed generation is hashed in the `peer-alias-store-v1` domain, signed by
the stable device identity, and crash-atomically replaced. Startup and `run-check` reject a foreign,
tampered, noncanonical, oversized, symlinked, multiply linked, or weakly permissioned existing store.

Removing a Tox friend deliberately does not remove its alias. This prevents a network event or peer
cleanup from silently freeing a trusted human name for a different key. While that peer is absent,
live operations through the alias fail as “not a current Tox friend.” Only `peer-alias-remove`
releases the name, and repeating removal is idempotent.

The signed store detects tampering and foreign-device substitution, but has no independent monotonic
witness and can be rolled back with the rest of local storage. Names can reveal operator intent or
machine role, are not placed in the content-free diagnostics bundle, and should be protected like
other private local metadata.

## Authority boundary and invitations

An alias binds a Tox route key only. It neither proves the peer's stable IoTox device principal nor
grants a capability; friendship and authority remain separate. A future transport-identity migration
must use an explicit verified rebind ceremony rather than silently following a claimed device name.

ADR 0293 now completes the separate signed invitation half. Its fixed artifact binds inviter stable
identity, exact transport address, expiry/nonce, an optional alias suggestion, and only the closed
authority-v3 capability vocabulary. Dry import verifies without mutation; acceptance is a distinct
local act that creates friendship and may choose a different alias, while authority still requires
its existing signed grant/proof ceremony. See `peer-invitations.md`. No invitation makes friendship
equal authority.
