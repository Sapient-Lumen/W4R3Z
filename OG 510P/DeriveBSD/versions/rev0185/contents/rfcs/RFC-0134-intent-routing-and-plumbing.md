# RFC-0134: Intent routing (“plumbing”) as a capability-mediated system service

Status: draft

## Motivation

Users and applications expect a simple capability:
- open/view/edit/share a file or URL
- pick an appropriate handler
- optionally choose defaults

If sandboxed programs implement this by invoking arbitrary handlers, probing global registries, or following ambient PATH rules, capability mode breaks.

We want a first-class, policy-audited mechanism for inter-app integration.

## Proposal

Introduce a small **intent router** service that:

1. accepts typed `intent.request` messages
2. resolves them using declarative rules + policy
3. brokers the handoff using portals + object-capability RPC
4. emits `intent.route.receipt` evidence

The router is the only component allowed to resolve *implicit* handler selection.

## Evidence objects

### `intent.request` (signed optional)

Schema: `spec/intent.request.schema.json`.

- In workstation/desktop mode, requests may be unsigned but are still digested and recorded.
- In headless/server mode, signatures may be required for cross-compartment requests.

### `intent.route.receipt` (signed)

Schema: `spec/intent.route.receipt.schema.json`.

Binds:
- request digest
- selected handler identity (service digest)
- policy decision digest
- portal grants minted during routing
- optional consent receipt digest if interactive

## Resolution model (v0)

- deny by default
- allow if:
  - explicit rule matches
  - policy permits
- ask if:
  - multiple handlers match
  - user interaction is configured

## Integration points

- Portals for file picks / bookmark claims: RFC-0114 / RFC-0133
- OCap RPC substrate for handler invocation: RFC-0118
- Consent receipts for chooser decisions: RFC-0120

## Open questions

- How to represent “share” (copy vs reference) in a capability-safe way by default?
- Should intent rules be part of a user profile artifact (derived + signed), or runtime mutable state with transparency?
- How to prevent handler fingerprinting (information leaks via resolution timing/errors)?

