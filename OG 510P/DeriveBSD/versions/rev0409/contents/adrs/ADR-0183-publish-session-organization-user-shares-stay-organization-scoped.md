# ADR-0183: Publish-session organization-user shares stay organization-scoped

- Status: Accepted
- Date: 2026-03-20

## Context

ADR-0153 already made publish-session audience posture explicit, and later decisions made
`organization-users` more concrete in two more ways:

- ADR-0162 keeps ordinary audience-bound human sharing `relay-url` shaped.
- ADR-0163 and ADR-0182 keep the same lane IdP-bound and evidence-shaped through
  `published_endpoint.audience.identity_provider_hint`.

One smaller but still expensive ambiguity remained:

**what keeps a receipt from saying `audience.class = organization-users` while still claiming
`published_endpoint.exposure_scope = internet`?**

Without one more narrow decision, a share can still read like “coworkers only” in the audience
lane while the published endpoint posture still reads like generic internet publication.
That forces UI, policy, support, and later implementation to guess which part of the receipt was
supposed to be the real boundary.

DeriveBSD does not need to settle the entire human-share exposure matrix yet.
In particular, it does not need to decide whether `named-recipients` always compiles to one
exposure scope.
But it does need the already-typed `organization-users` lane to stop contradicting itself.

## Decision

1. If `published_endpoint.audience.class = organization-users`, then
   `published_endpoint.exposure_scope` must be `organization`.
2. This is intentionally one-way for now.
   It does **not** decide that every `organization`-scoped share must be `organization-users`.
3. This ADR also does **not** decide whether `named-recipients` always compiles to
   `organization` or `internet`.
   That remains open until the archive has a better internal/external recipient posture.

## Consequences

- `organization-users` can no longer masquerade as generic internet publication.
- Receipts, trusted UI, and support/export surfaces can treat the organization-user lane as one
  coherent “coworkers via org-scoped relay-url share” posture.
- The archive narrows one ambiguity without prematurely freezing the full named-recipient exposure
  matrix.

## Alternatives considered

- **Leave `organization-users` exposure loose.** Rejected because it keeps the same receipt able to
  say both “organization audience” and “internet exposure” at once.
- **Force both `organization-users` and `named-recipients` onto one exposure scope now.** Rejected
  as too wide for this round; the archive still has a real internal-versus-external named-recipient
  question.
- **Make `exposure_scope = organization` imply `organization-users` immediately.** Rejected because
  that would close off future org-scoped named-recipient or other narrower audience lanes before
  the archive is ready.
