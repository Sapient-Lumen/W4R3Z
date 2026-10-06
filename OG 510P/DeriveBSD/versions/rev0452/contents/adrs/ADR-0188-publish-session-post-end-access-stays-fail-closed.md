# ADR-0188: Publish-session post-end access stays fail-closed

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` already says relay-backed temporary sharing is leased, revocable, reboot-cleared, and `new-session-with-fresh-authority` after interruption. It also now says the outward published surface is `lease-frozen`, so one lease cannot silently drift into a different hostname/path/audience/access meaning.

But one gap remained: what is a previously copied URL, relay handle, bookmark, browser-history entry, or remembered share target allowed to do **after** the lease ends? Without a small explicit law, stale temporary-share handles can still degrade into exactly the folklore DeriveBSD is trying to avoid: generic launcher redirects, silent rebinding to a successor session, or “looks current enough” pages that no longer name the bounded share that was actually granted.

The neighboring datacubes made the narrow cut clear enough to trust here. The useful import is not “do rich stale-link UX now”; it is: when a bounded public/share surface is temporary, stale re-entry must fail closed and either name the ended state explicitly or require a fresh bounded act.

## Decision

1. `net.publish.session.lifecycle.post_end_access_posture` is required.
2. The publish-session envelope requires `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share`.
3. After a publish session ends, reuse of the old outward share handle must not silently bind to a successor session, a generic launcher/start-over shell, or a durable ingress lane. It must instead resolve as an explicit ended/expired/revoked share state or force creation of a fresh share with new authority.

## Consequences

- The archive now states what stale copied/share handles are allowed to do after the bounded act ends.
- `resume_policy = new-session-with-fresh-authority` no longer has to carry that whole burden indirectly.
- Lease-frozen outward surfaces and session-scoped locators now compose with an explicit post-end failure posture instead of leaving stale reuse semantics to provider or frontend folklore.

## Alternatives considered

- **Rely on `resume_policy` alone.** Rejected because it governs recreation after interruption, not the behavior of old copied/bookmarked/share handles after the lease is already over.
- **Model full stale-link recovery UX now.** Rejected as too wide; the narrow fix is to state the bounded failure posture first.
