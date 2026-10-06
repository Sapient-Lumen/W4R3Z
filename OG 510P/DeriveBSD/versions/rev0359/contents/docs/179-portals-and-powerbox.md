# Portals / “powerbox” (mediated capability acquisition)

Capsicum (and compartments generally) are easiest when programs can be fully described up-front:
pre-open everything, then `cap_enter(2)`.

But real systems often need **dynamic access**:
- an interactive program needs the user to choose a file
- an operator wants to approve an emergency export of logs
- a capability-mode daemon needs to open a newly created file *after* it has dropped ambient authority

This doc proposes a *small* DeriveBSD primitive for these cases: a **portal** (aka “powerbox”) broker.

## Lesson to steal

Several ecosystems converged on a similar pattern:

- **Powerbox**: capability-sandboxed apps request file access through a trusted UI/broker.
- **XDG Desktop Portals**: sandboxed desktop apps request resources through a host-side broker API.
- **Casper**: capability-mode programs can obtain narrowly scoped services via a broker.

The shared idea: **dynamic authority acquisition must be mediated**, deny-by-default, and auditable.

References:
- “Towards oblivious sandboxing with Capsicum” (powerbox concept in a Capsicum context): https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf
- XDG Desktop Portal overview: https://flatpak.github.io/xdg-desktop-portal/
- Flatpak portal model (sandbox permissions and portals): https://docs.flatpak.org/en/latest/sandbox-permissions.html
- Casper broker API: https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3

## What “portal” means in DeriveBSD

A **portal** is a small host-side broker that:

1) Receives a **portal request** (typed, reviewable).
2) Evaluates policy (and optionally asks a human).
3) Returns a narrowly scoped capability (FD/handle/token) *and* emits evidence objects.

Portals are *not* only for desktop UX. DeriveBSD can run portals in two modes:

- **headless / server mode**: policy-only (no UI), like a strict qrexec policy.
- **interactive mode**: “ask” decisions route to a UI backend (development / workstation use).

## Why bake this in early

Without a portal primitive, capability-mode adoption tends to stall at “it’s too hard”:
people reintroduce ambient authority to handle the messy parts.

Portals let DeriveBSD keep the rule:

> *capability mode is the default; dynamic access is an explicit, evidence-bearing exception.*

## Proposed contract (v0)

### Portal request

Shape (conceptual):

```
portal.request = {
  kind: "portal.request",
  requester: { pid, uid, service_name, instance_id? },
  capability: {
    type: "file" | "socket" | "dataset" | "rpc" | "secret-op" | ...,
    params: { ... typed per capability ... }
  },
  context: {
    plan_digest?,
    policy_snapshot_digest?,
    reason?,
    ttl_seconds?
  }
}
```

### Policy decision

Policy returns one of:
- **deny** (default)
- **allow** (with constraints)
- **ask** (interactive backend decides allow/deny)

### Evidence objects

#### Portal grant evidence

Every *allow* yields a content-addressed evidence object:

`portal.grant` records:
- request digest
- decision (allow + constraints)
- capability description (rights, scope)
- expiry
- policy decision record digest

Schema: `spec/portal.grant.schema.json`.

#### Consent receipts (optional, interactive-only)

If the decision was made via interactive **ask**, also emit:

- `portal.consent` (who approved what; prompt template id/version; constraints)

Schema: `spec/portal.consent.schema.json`.

See: `docs/185-portal-consent-and-audit-receipts.md`.

#### Sessions + remembered permissions

Some portal families create long-lived streams/handles (screen share, remote desktop, global shortcuts).
Standardize this via **portal sessions** and an optional **permission store**:

- `portal.session` receipts for long-lived sessions
- `portal.permission.{grant,revoke}` for “remember my choice” decisions

See: `docs/210-portal-sessions-and-permission-store.md`.

### Leases + revocation

If a grant is intended to outlive a single operation, the portal should return a **mediated** capability and assign a `lease_id`.
Revocation is then a first-class act: emit `portal.revoke` evidence (schema: `spec/portal.revoke.schema.json`) and make future use of the lease fail (fail-safe).

See: `docs/182-capability-leases-and-revocation.md`.

### Token capabilities (optional)

Sometimes a portal returns a *token* rather than an FD/handle (e.g. for cross-host delegation).
If so, prefer **attenuating** token formats and record only token digests/metadata as evidence.

See: `docs/184-attenuating-delegation-tokens.md`.

## Mapping to existing DeriveBSD lanes

- **Capsicum/Casper**: implement portals as Casper services (e.g. `derive.portal.file`) so capability-mode daemons can call them without regaining ambient authority.
- **Activation broker**: long-lived services should get a *portal client handle* via activation (not ambient power). Interactive access becomes a mediated request, not a startup privilege. See `docs/196-capability-activation-and-escrow.md`.

- **qrexec-style RPC**: `derive-rpc` becomes “a portal across compartments”; same deny-by-default posture, same evidence shape.
- **Debugging/observability**: portals can issue leased `trace.stream.grant` and `debug.record.grant` objects for interactive sessions, producing `trace.capsule` and `debug.replay.capsule` outputs.
- **URI opening / handler routing**: portals can stay responsible for chooser/consent/default-app UX while `docs/539-workstation-intent-routed-uri-opening-floor.md` keeps risky `http` / `https` rendering in a designated browsing compartment instead of falling back to an ambient host opener, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` keeps that chooser/default-app layer on trusted host-managed role slots rather than arbitrary "open with…" discovery, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` keeps the remembered defaults in a typed `intent.role.binding` object rather than in ambient desktop registries, `docs/605-workstation-file-open-import-and-bounded-document-roles.md` keeps cross-compartment document open/view/edit import-shaped first and role-bound second, `docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixes the mutation boundary so foreign imported documents remain view-first and require an explicit working-copy act before the editing lane applies, `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then makes that act typed through `content.working-copy.plan` / `content.working-copy.receipt` and keeps allowed edit routes joinable through `working_copy_receipt_digest`, `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` then fixes ordinary save onto the working-copy output instead of quiet source write-back, `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then keeps any path back toward source lineage explicit and successor-candidate-shaped instead of replace-in-place folklore, `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then keeps that successor-candidate evidence frozen to one digest instead of a mutable working-path alias, `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then keeps multi-candidate ordering explicit by digest instead of newest-wins folklore, `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then keeps that explicit supersession same-authoritative-origin-only and self-describing by carrying the exact superseded candidate/origin digests, and `docs/542-role-binding-diff-as-review-surface.md` keeps trusted settings changes reviewable without turning the portal layer into a general writable settings bus.
- **Policy decision records**: grants are “runtime policy decisions”; they should be explainable like any other decision.

Pointers:
- Capsicum/Casper posture: `docs/49-capsicum-casper-hardening.md`
- Cross-compartment RPC: `docs/135-qrexec-style-rpc-policy.md`
- Policy decision records: `docs/93-policy-decision-records.md`
- Observability as capability: `docs/192-observability-as-capability.md`
- Debugging by lease: `docs/194-debugging-by-lease-and-replay-capsules.md`

## Persistent file access (bookmarks)

Many “dynamic access” requests are not one-shot: apps want to reopen recently approved files after restart.

DeriveBSD should support a persistable, revocable pattern via `fs.bookmark` objects that can be claimed through the portal to obtain a fresh rights-minimized FD.

See: `docs/198-persistent-file-capabilities-bookmarks.md`, RFC-0133.

## Non-goals (v0)

- Designing a full desktop UX.
- Making interactive “ask” a production dependency.
- Allowing arbitrary file path opens: grants should be constrained (directory capability + relative open, specific files, or explicit export actions).

Candidate RFC: **Portals/powerbox broker + evidence objects**.

Last updated: 2026-03-20r342
