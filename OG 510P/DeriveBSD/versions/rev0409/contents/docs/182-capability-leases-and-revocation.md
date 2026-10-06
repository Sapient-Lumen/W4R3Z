# Capability leases + revocation (keep least-authority usable)

Classic capability systems (including Capsicum) intentionally make capabilities **hard to revoke** once handed out.
That property is great for reasoning, but it becomes an adoption trap:
operators and UI flows often *need* temporary / conditional authority.

DeriveBSD should bake in a single, opinionated pattern for **revocable, time-bounded grants** so people don’t
reintroduce ambient authority “just to make it practical”.

This doc defines the *mechanics*; policy lives elsewhere.

## The problem (why this matters)

We want:
- **deny-by-default compartments** (jails / cap-mode / microVMs)
- **dynamic access** when humans or operators choose it (portals/powerbox)
- **auditable crossings** (evidence objects)

But without revocation:
- long-lived daemons accumulate access “forever”
- one-time “debug” or “export logs” approvals become permanent leaks
- compromised compartments keep any granted capability until process death

## The DeriveBSD stance

Dynamic authority is *always* represented as a **lease**:

- every dynamic grant has a `lease_id`
- leases are time-bounded (`expires_at`)
- leases are **revocable** (fail-safe): revocation makes future use fail
- revocation emits a `portal.revoke` evidence object

This is enforced by construction: anything revocable is delivered through a *mediated handle*.

## Revocation mechanics (three options)

Different resources support revocation differently. DeriveBSD should standardize three patterns,
ordered from “strongest revocation” to “best performance”.

### A) Proxy capability (strong revocation, default for long-lived grants)

Instead of returning the raw resource (e.g., a raw FD), the portal returns a handle that routes
operations through a broker/proxy that can deny future requests.

Examples:
- **file read lease**: portal returns a `portal://file/<lease_id>` stream endpoint; reads are served by the broker
- **RPC lease**: portal returns an object reference in an object-capability RPC channel (see `docs/183-object-capability-rpc.md`)

Revocation is implemented by invalidating `lease_id` inside the proxy.

Properties:
- fail-safe (proxy down => access fails)
- supports rate limits / content filters / size caps
- supports explicit revocation with evidence

### B) “Fresh-open” capability (revocation via re-authorization)

For some operations, don’t hand out a reusable handle at all. Hand out *permission to ask again*.

Example:
- “open this path relative to directory X” is re-authorized per open

Properties:
- great for operations naturally expressed as discrete actions
- avoids a long-lived bearer handle

### C) Raw capability + short TTL (weak revocation, only for one-shot flows)

Sometimes the underlying primitive is not revocable (e.g., a raw FD).
In those cases:
- require **one-shot** semantics
- enforce small TTL and/or byte limits
- treat this as *debug/workstation lane only*

Rule of thumb:
> If the grant might outlive the immediate operation, don’t use raw capabilities.

## Note on CHERI temporal revocation

CHERI-style systems also use the word *revocation* for temporal memory safety (revoking dangling pointers/capabilities).
That is a different problem than revoking **authority leases**.
DeriveBSD should keep these concepts separate and prefer indirection at security boundaries; see `docs/250-cheri-temporal-revocation-and-indirection.md`.

## Evidence objects

- `portal.grant` includes `lease_id` whenever revocation is supported.
- `portal.revoke` records who revoked what, when, and why.

This makes revocation explainable:
- “why can’t I read this anymore?” → revoked/expired lease evidence
- “who granted/extended this?” → portal grants bound to policy decisions

## Where it plugs in

- Portals/powerbox: `docs/179-portals-and-powerbox.md`
- Cross-compartment RPC policy: `docs/135-qrexec-style-rpc-policy.md`
- Capability routing manifests: `docs/140-capability-routing-manifests.md`

## Non-goals (v0)

- Revoking all capabilities in a compartment (that’s a restart / shutdown boundary).
- Perfect revocation for raw kernel FDs (not generally possible).

Last updated: 2026-02-25
