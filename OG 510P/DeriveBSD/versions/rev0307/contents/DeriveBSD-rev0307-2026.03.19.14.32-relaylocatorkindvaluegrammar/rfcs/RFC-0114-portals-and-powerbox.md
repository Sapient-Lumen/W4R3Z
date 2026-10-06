# RFC-0114: Portals / powerbox broker (mediated capability acquisition)

Status: **draft**

## Problem

DeriveBSD wants capability mode (Capsicum) and compartmentation (jails/microVMs) to be the default.

However, many real workflows require **dynamic** access to resources:
- user-chosen files (file pickers)
- “export logs now” actions
- post-start access to newly created objects
- narrow, policy-approved exceptions during incident response

If DeriveBSD lacks a sanctioned mechanism, teams tend to reintroduce ambient authority.

## Goals

1) Provide a small, typed interface for **requesting capabilities** at runtime.
2) Keep default posture **deny-by-default** (fail closed).
3) Make every grant **evidence-bearing** and explainable.
4) Support both:
   - headless policy-only mode
   - optional interactive “ask” mode (developer/workstation)

## Non-goals

- Shipping a full desktop environment.
- Making interactive prompts a production requirement.
- Allowing arbitrary “open any path” behavior.

## Prior art

- Capsicum powerbox pattern (“trusted UI mediates file access”).
- XDG Desktop Portals (host broker APIs for sandboxed apps).
- FreeBSD Casper (brokered services usable inside capability mode).

References:
- Towards oblivious sandboxing with Capsicum: https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf
- XDG Desktop Portal overview: https://flatpak.github.io/xdg-desktop-portal/
- Flatpak portal model: https://docs.flatpak.org/en/latest/sandbox-permissions.html
- libcasper(3): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3

## Proposed interface

### 1) Portal request

Define a canonical, hashed request object:

```
portal.request = {
  kind: "portal.request",
  requester: {
    service: "derive-vmmd" | "derive-fetchd" | ...,
    instance_id?: "host" | "jail:..." | "vm:...",
    uid?: number,
  },
  capability: {
    type: "file" | "dataset" | "socket" | "rpc" | "secret-op" | ...,
    params: { ... }
  },
  context: {
    plan_digest?: string,
    policy_snapshot_digest?: string,
    reason?: string,
    ttl_seconds?: number
  }
}
```

Requests MUST be deterministic (canonical JSON) so their digest is stable.

### 2) Policy evaluation

Policy returns one of:
- deny
- allow (with constraints)
- ask (interactive backend decides allow/deny)

Production default should treat `ask` as disabled unless explicitly enabled.

### 3) Grant delivery

Grant delivery is OS-specific:
- file/dataset/sockets are returned as **file descriptors** (preferred)
- cross-compartment grants may be returned as **tokens** that the RPC layer resolves

### 4) Evidence object: `portal.grant`

Every allow MUST emit a content-addressed evidence object:
- request digest
- decision + constraints
- expiry
- reference to the policy decision record digest

Schema: `spec/portal.grant.schema.json`.

## Implementation sketch

### Option A: Casper-based portals (preferred)

Implement portal services as Casper services (e.g. `derive.portal.file`).
This makes portals usable from inside Capsicum capability mode without regaining ambient authority.

### Option B: Unix socket broker

For jails/microVMs, a host-side broker can expose a socket endpoint with strict request typing.
This begins to converge with `derive-rpc` (qrexec-shaped), so shared libraries and evidence formats should be reused.

## Integration points

- Capsicum hardening: `docs/49-capsicum-casper-hardening.md`
- Cross-compartment RPC: `docs/135-qrexec-style-rpc-policy.md`
- Policy decision records: `docs/93-policy-decision-records.md`
- Explainability contract: `docs/95-explainability-contract.md`

## Tradeoffs

- Adds complexity (a broker daemon, policy rules).
- Risk of “escape hatch” if the portal is too permissive.
- Requires tight, typed capability definitions to stay reviewable.

## Open questions

- What capability types are v1-worthy (file/dataset/socket are likely; others may be later)?
- How should interactive `ask` be represented in evidence (UI backend id, prompt hash, operator id)?
- Can we reuse DSSE envelopes for `portal.grant` statements without bloating v1?
