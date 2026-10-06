# Object-capability RPC as the “crossing primitive” (Cap’n Proto / OCapN lessons)

DeriveBSD already treats *authority* as something that should be:
- explicitly granted
- diffable/reviewable
- mediated across compartments

To keep that story coherent, DeriveBSD should standardize one RPC substrate that can *carry capabilities*
without falling back to ambient naming and ad-hoc ACLs.

This doc proposes an **object-capability RPC** lane for host↔service-jails↔microVMs.

## Why this is worth baking in

Classic “RPC by name” encourages ambient power:
- clients discover services by global names
- servers re-check identity/ACLs everywhere
- capability routing becomes a bolted-on policy layer

Object-capability RPC flips this:
- you only get access to an object/service if someone hands you a reference
- references can be mediated, logged, and (via proxies) revoked

That aligns with DeriveBSD’s core contract: **authority flows should be explicit artifacts**.

## Candidate substrates

### Cap’n Proto RPC (capability-based by design)

Cap’n Proto’s RPC layer is explicitly capability-oriented and supports promise pipelining.
It is a strong fit for *local* transports (Unix sockets, vsock) where we want low overhead.

Primary references:
- Cap’n Proto RPC overview: https://capnproto.org/rpc.html
- Cap’n Proto FAQ (malicious peer framing): https://capnproto.org/faq.html

### OCapN / CapTP (interoperable networked object capabilities)

OCapN is a protocol suite for interoperable capability transport (CapTP at its core).
It is a stronger fit when we expect multi-language, internet-shaped distributed systems,
with explicit “handoff” and distributed GC semantics.

Primary references:
- OCapN overview: https://ocapn.org/
- CapTP draft specification (OCapN repo): https://github.com/ocapn/ocapn/blob/main/draft-specifications/CapTP%20Specification.md

See: `docs/353-captp-ocapn-remote-capabilities.md`.

github.com/ocapn/ocapn/blob/main/draft-specifications/CapTP%20Specification.md

### Doors / FD-first IPC (local-only inspiration)

Solaris/illumos **Doors** are an under-copied IPC primitive where the RPC endpoint is a **file descriptor**.
Even if DeriveBSD never implements kernel Doors, the pattern is valuable: “authority = handle”, and
handoff happens by passing the handle.

See: `docs/341-doors-lightweight-capability-rpc.md`.

### Contract discipline (Singularity lesson)

Object-capability RPC still needs a way to keep RPC surfaces reviewable.
Singularity’s “contract channels” framing is a good reminder: treat the interface as a digest-bound
contract input to policy.

See: `docs/339-singularity-manifests-and-contract-channels.md`.

A practical modern option for defining contract surfaces is **WIT** (WebAssembly Component Model): a small, diffable IDL that can be digested into contract hashes even when the implementation is not Wasm.

See: `docs/356-wasm-component-model-and-wit-contracts.md`.

## DeriveBSD mapping (minimal v0)

DeriveBSD doesn’t need to adopt *all* of a framework. It needs:

1) **A capability-carrying channel**
   - transport: Unix socket (service jails) and/or vsock (microVM)
   - mutual auth: bound to workload identity lane when available (`docs/181-workload-identity-and-secretless-deploys.md`)

2) **A small set of capability “kinds”** (wired into policy + explainability)
   - file streams (read/export)
   - control operations (start/stop/inspect)
   - secret-ops (decrypt/sign) via broker objects
   - dataset/state operations (snapshot/clone/promote)

3) **Evidence for crossings**
   - policy decision: allow/deny
   - transcript digest (no plaintext secrets)
   - capability grants as leases when the capability is meant to persist

The key point: *capability references* are the unit we route, not global service names.

## Integration points

### qrexec-style policy becomes the “front door”

`docs/135-qrexec-style-rpc-policy.md` stays the model:
- deny-by-default
- rule decides whether a connection/call is allowed

Object-capability RPC only changes the *payload*:
- if allowed, the callee returns a capability reference rather than “doing everything itself”
- follow-on actions happen through that reference

### Portals/powerbox returns RPC capabilities too

Portals (`docs/179-portals-and-powerbox.md`) can return:
- file stream capabilities (proxy)
- RPC capabilities (object references)

Those are naturally revocable using lease semantics (`docs/182-capability-leases-and-revocation.md`).

### Capability routing manifests can name “routes” as capability edges

A route graph (`docs/140-capability-routing-manifests.md`) can be realized as:
- initial capability handoffs during activation
- plus optional portal-mediated later grants

## Non-goals (v0)

- Choosing a public, internet-facing wire protocol for all time.
- Supporting arbitrary UI workflows.
- Making every kernel primitive revocable.

Candidate RFC: **Object-capability RPC lane for DeriveBSD crossings**.

Last updated: 2026-02-24
