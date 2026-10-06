# Intent routing (“plumbing”) as a capability-mediated service

Modern systems want a simple primitive for:
- “open this file” / “view this URL” / “share this blob”
- “pick the best handler for this MIME type”
- “let the user choose a default app”

If apps do this by spawning arbitrary handlers or probing global registries, sandboxing collapses.

This doc proposes a DeriveBSD primitive: an **intent router** (Plan 9 “plumber” / Android intents shaped) that is:
- capability-mediated
- policy-gated
- evidence-bearing

## Lessons to steal

- **Plan 9 plumber**: a message routing service whose behavior is defined by a rules file; unusually, it is a *file server*, so sending is just writing to a file.
- **Android intents**: components declare intent filters; the system resolves implicit intents to handlers, optionally presenting a chooser and letting users set defaults.

References:
- Plan 9 plumbing design notes: https://9p.io/sys/doc/plumb.html
- plumb(7) rules and ports: https://9fans.github.io/plan9port/man/man7/plumb.html
- Android intents and intent filters: https://developer.android.com/guide/components/intents-filters

## What “intent routing” means in DeriveBSD

An **intent request** is a typed message:

- action: `open` / `view` / `edit` / `share` / `print` / …
- subject: a file capability, URL, or blob capability
- context: caller identity + plan/generation digests + reason
- constraints: UI requirements, redaction profile, time budget, etc.

The **intent router**:
1) evaluates rules + policy
2) selects a handler component
3) brokers the handoff using DeriveBSD’s capability substrate (portals + ocap RPC)
4) emits a signed **route receipt**

## Why bake this in early

- It avoids “xdg-open as ambient authority.”
- It provides a single place to enforce UX + safety constraints (e.g. "open untrusted PDF" defaults to a hardened viewer compartment).
- It makes inter-app integration compatible with capability mode.

## Proposed contract (v0)

### `intent.request`

Schema: `spec/intent.request.schema.json`.

Key fields:
- `action`
- `subject` (by-value digest metadata, plus an optional handle reference)
- `mime_type` / `uri_scheme`
- `caller` identity
- `context` digests

### Resolution outputs

The router produces one of:
- deny (default)
- allow (explicit handler)
- ask (interactive chooser)

On allow, it returns:
- a handler endpoint (ocap RPC capability)
- and/or a portal-derived file/socket capability for the handler

### Evidence: `intent.route.receipt`

Schema: `spec/intent.route.receipt.schema.json`.

Binds:
- request digest
- chosen handler identity (service digest)
- policy decision digest
- any portal grants minted as part of the routing
- optional consent receipt digest if interactive

## Rules model (non-normative)

DeriveBSD can support a Plan 9-ish rules file:
- match on action + MIME type + scheme + tags
- rewrite/annotate intent
- dispatch to a handler class

But unlike Plan 9, dispatch must go through portals/leases so the handler receives only the minimum capability set.

## Threat model notes

- Prevent “confused deputy” by making the router the only component allowed to:
  - resolve implicit handlers
  - invoke interactive chooser UI
- Bind route receipts to a policy snapshot digest (avoid silent rule changes).
- For "open" actions on host files, prefer `fs.bookmark` claims or portal file picks rather than raw path strings.

## Integration points

- Portals: `docs/179-portals-and-powerbox.md`
- Object-capability RPC substrate: `docs/183-object-capability-rpc.md`
- Consent receipts: `docs/185-portal-consent-and-audit-receipts.md`
- Deterministic redaction transforms (safe sharing): `docs/195-deterministic-redaction-transforms.md`

Last updated: 2026-02-24
