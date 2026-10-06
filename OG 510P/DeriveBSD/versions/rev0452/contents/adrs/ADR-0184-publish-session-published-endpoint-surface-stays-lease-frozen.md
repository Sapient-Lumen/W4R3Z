# ADR-0184: Publish-session published endpoint surface stays lease-frozen

- Status: Accepted
- Date: 2026-03-20

## Context

ADR-0154 already made temporary publish sessions reboot-cleared and
`new-session-with-fresh-authority`.
ADR-0155 then kept public/org/support locators `session-scoped` so remembered relay names do not
become durable ingress by accident.
ADR-0169 and later endpoint-tuple decisions then made the outward `relay-url` surface more typed:
`hostname`, `port`, `url_hint`, `path_prefix`, audience, and access-model posture now already tell
one coherent story inside a single receipt.

One smaller but still expensive ambiguity remained across receipts:

**what keeps the same publish-session lease from quietly changing the outward published endpoint
surface while still pretending to be the same bounded share?**

Without one more narrow decision, a bookmark, copied URL, support reference, or export trail can say
“this lease is still the same share” while the share's outward hostname, path, audience, or access
shape has already drifted underneath it.

DeriveBSD does not need to define redirects, aliases, or multi-surface continuity for temporary
sharing yet.
But it does need one lease-shaped share to stop silently becoming a different outward share surface.

## Decision

1. Every `net.publish.session` now records
   `published_endpoint.continuity_posture = lease-frozen`.
2. For one bounded publish session, the canonical outward published-endpoint surface is frozen for the
   lifetime of that share.
3. A material outward published-endpoint change therefore requires a **new** `net.publish.session`
   with a fresh `session_id` and fresh `authority.lease_id`.
4. This decision is intentionally narrow.
   It does **not** define redirect semantics, cross-session aliases, or durable public-name reuse for
   temporary sharing.

## Consequences

- Copied URLs, support trails, and revoke/query flows can treat one publish-session lease as one
  stable outward share surface.
- Temporary sharing no longer has room to silently repoint hostname/path/audience posture under the
  same bounded authority instance.
- If operators want a changed outward surface, they must mint a new session instead of mutating the
  old one in place.

## Alternatives considered

- **Leave outward surface continuity implicit.** Rejected because it lets the same bounded lease mean
  different copy surfaces over time.
- **Model redirects, aliases, and continuity graphs now.** Rejected as too wide for this round; the
  archive only needs to stop same-lease surface drift.
- **Treat only URL strings as continuity-relevant.** Rejected because audience/access/exposure posture
  are part of the outward published-endpoint meaning too, not just one pasted URL field.
