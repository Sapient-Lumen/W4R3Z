# Consent UX contract (GUI/TTY/OOB approvals with uniform receipts)

DeriveBSD leans hard on “no ambient authority”: risky actions should be mediated (portals) and timeboxed (leases).
But a portal is only as good as its **approval UX**.

Older ecosystems have many disjoint patterns:
- GUI auth prompts (PolicyKit/polkit agents)
- TTY password prompts at boot/runtime (systemd ask-password agents)
- ad-hoc Slack/pager approvals (“type YES in chat”)

This doc defines a small, uniform contract:
- `consent.request`: what action is being proposed (inputs, policy, expiry)
- `consent.receipt`: what approvals happened (who/when/how), as evidence

The goal is interchangeability: GUI vs TTY vs OOB can vary by deployment, but the evidence object is the same.

## Prior art to steal

- polkit agent model (mechanism checks authorization; agent handles interactive auth): https://www.freedesktop.org/software/polkit/docs/latest/polkit-agents.html
- polkit overview (client/mechanism framing): https://manpages.ubuntu.com/manpages/focal/man8/polkit.8.html
- systemd password agent spec + tooling:
  - password agent spec: https://systemd.io/PASSWORD_AGENTS/
  - agent man page: https://man7.org/linux/man-pages/man1/systemd-tty-ask-password-agent.1.html
- XDG portal request/session + permission store:
  - Request: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
  - PermissionStore: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.PermissionStore.html

## New artifacts

### `consent.request`

A request describes:
- action kind (export, breakglass, trace session start, …)
- the policy digest governing the action (export.policy, breakglass policy, etc.)
- the input digests (bundle.plan, export.policy, artifact digest, …)
- expiry and required approver quorum (including two-person flows)
- “secure attention” requirements (if any)

See: `spec/consent.request.schema.json`.

### `consent.receipt`

A receipt records:
- request digest
- decision (approved/denied/timeout)
- approver identities and method (gui/tty/oob)
- authentication strength metadata (e.g., “local session + PAM”, “FIDO2”, “OOB signed approval”)

See: `spec/consent.receipt.schema.json`.

## How it composes

- `export.policy.consent` expresses whether interactive consent is required.
- export portal (or CLI) emits `consent.request` and waits for a `consent.receipt`.
- `export.receipt` may include `consent_receipt_digest`.
- stronger `packet.capture.normalized` export now stays on this same substrate but pins a narrower profile: the request must bind policy/artifact/lease state **plus** `action.destination`, require secure attention, and keep the later transport / recipient-acceptance / export evidence on that same approved destination tuple; the approval evidence may be GUI/TTY/OOB but not `method = auto` (`docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `spec/packet.capture.export.consent.request.profile.schema.json`, `spec/packet.capture.export.consent.receipt.profile.schema.json`).

The same pattern can gate:
- breakglass mode entry
- tracing sessions
- “confirmable change-sets” confirmation
- enabling lockdown levels

## Operational guidance

- Ensure the UI path is *non-observing* when possible (no leaking screen content to the requester).
- Bind consent prompts to a stable display of “what will happen” (digests + human summary).
- Prefer “confirmable” actions (auto-revert without confirmation) for high-risk operations.

See also: `docs/288-multiparty-approvals-and-separation-of-duties.md`.

See: `rfcs/RFC-0188-consent-ux-contract.md`.

Last updated: 2026-03-09r248
