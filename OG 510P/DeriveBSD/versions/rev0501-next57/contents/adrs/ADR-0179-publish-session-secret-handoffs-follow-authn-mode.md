# ADR-0179: Publish-session secret handoffs follow authn_mode

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0156, ADR-0157, and ADR-0158 already made secret-gated temporary sharing much tighter:
when a publish session uses `single-use-secret` or `shared-secret`, the usable secret must travel on
`published_endpoint.secret_handoff`, that handoff stays session-authority-bounded, and the
consumption posture becomes explicit.

One smaller but still expensive ambiguity remained:

**what keeps a receipt from carrying `published_endpoint.secret_handoff` even when the typed
`audience.authn_mode` says the share is `none`, `provider-identity`, `support-session`, or
`tailnet-identity`?**

Without one more narrow decision, a public link, provider-identity share, or support-session peer
handoff can still carry an extra secret handoff object and tell two competing stories about what the
receiver was actually expected to present.

DeriveBSD does not need a broader multi-factor publish-session vocabulary here, but it does need the
existing `authn_mode` field to stay singular and implementation-worthy.

## Decision

1. `published_endpoint.secret_handoff` now follows `published_endpoint.audience.authn_mode`
   exactly.

2. If `authn_mode` is `single-use-secret` or `shared-secret`, `secret_handoff` remains required.

3. If `authn_mode` is `none`, `provider-identity`, `support-session`, or `tailnet-identity`,
   `secret_handoff` must be absent.

4. If `secret_handoff` is present, the publish session must therefore also use either
   `single-use-secret` or `shared-secret`.

5. This ADR does **not** invent an MFA or stacked-authn publish-session language.
   If future product work really needs provider-identity-plus-secret or other composed authn, that
   should arrive as a new typed posture instead of smuggling a second authority story into the
   existing receipt.

## Consequences

- `public-link` publication can no longer carry a secret handoff blob beside `authn_mode = none`.
- Provider-identity and support-session shares can no longer imply a second hidden secret lane.
- Receipts, policy, and support surfaces can trust `authn_mode` as the one summary of what the
  receiver was expected to present.

## Alternatives considered

- **Leave `secret_handoff` optional outside secret authn modes.** Rejected because it lets the
  receipt tell two competing auth stories at once.
- **Interpret `secret_handoff` as an optional extra factor.** Rejected because the schema has no
  typed way to describe composed authn semantics, so that would be folklore rather than product.
- **Invent a broader composed-authn object now.** Rejected as too wide for this round.
