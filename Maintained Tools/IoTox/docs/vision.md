# IoTox vision

IoTox is a self-owned nervous system for physical things, built first as a stronger modern
ratox successor.

A device should boot into an identity it holds locally, connect through Tox without a
mandatory vendor account, remain operable through ordinary Unix tools, and recognize only
owner-defined authority above transport friendship. An owner should be able to return from a
strong generated phrase without granting the IoTox project a universal recovery key.

## Product sentence

> From memory, you can reach your devices; from an ordinary shell, you can understand and
> operate them.

The publishable public entrance is `docs/product-page.md`. It should stay shorter than the revision
history but honest about the same boundaries: friendship is not authority, synchronization is not a
backup, a route is not an anonymity proof, and sudo is not the default terminal posture.
The aspirational north-star is `docs/edge-of-hope.md`; its practical counterweight is
`docs/pragmatic-guardrails.md`.

## Outside simplicity

```text
run the agent
show its address
pair or accept a transport peer
inspect peers by public key
message and watch
send and receive files
send structured device frames
stop and restart without losing identity
```

The outside should feel as direct as ratox. The inside must tell the truth about
connectivity, authorization, delivery, execution, persistence, and failure.

## Inside discipline

```text
one toxcore owner thread
exact external-C boundary
private structured local control
bounded queues and decoders
atomic state and transactional projections
independent authorization ledger
durable idempotent command lifecycle
owner-reconstructible RecallRoot
explicit native/Tor/I2P route policy
signed updates and target-device hardening
```

## Tox and the commons

Tox remains primary because it is a strong, beautiful working peer network. IoTox should
contribute fixes, bootstrap nodes, TCP relays, reproducible deployment tooling, and transparent
infrastructure governance where possible. Infrastructure operators help packets travel; they
do not become owners.

## Long direction

Tox/native comes first. Tox routed over Tor and I2P may add reachability and privacy when they
can be made explicit and leak-free. Direct Tor/I2P transports are separate future designs.
An optional owner-operated hub may hold durable queues and automation while remaining
replaceable and non-sovereign.

Mutorr's small-circle replication remains preserved as an optional future organ. The body
being built now is the ratox successor: identity, peers, text, files, frames, local control,
authority, recovery, and reliable device semantics.

## Shell and Nix direction

The product remains one executable. The surrounding operator surface should be a small Bash/Nix
script layer that teaches and orchestrates without owning device authority. A general public script
can provide doctor, build, test, run, sync, terminal, datacube, and cleanup paths. A separate
MonsterNix adapter can admit exact source/package objects and project host-specific services through
MonsterNix's own proof and switch ceremonies. Neither script is allowed to create a second signer,
choose a remote path, enable sudo, or silently claim recovery custody.
