# Publish-session post-end access stays fail-closed
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

## Summary

The compact `net.publish.session` receipt must say what old copied or remembered share handles are allowed to do after the lease ends. `lifecycle.post_end_access_posture` is now required and must stay `explicit-ended-or-fresh-share`, so a stale temporary-share URL/handle cannot silently rebind to a successor session, a generic launcher, or a durable ingress lane. The adjacent trusted-UI return affordance must stay exact too, and the ended bounded-share state itself should keep the exact terminal cause and exact bounded end-condition class through `lifecycle.terminal_end_condition`; see `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md` and `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`.

## Why

DeriveBSD already says temporary sharing is reboot-cleared, lease-addressable, and `new-session-with-fresh-authority` after interruption, and it already freezes the outward published surface for the life of one lease. That still left a quiet post-end ambiguity: what should an old copied URL, bookmark, browser-history entry, or remembered relay handle do after the share ends?

The bounded answer is not “invent the whole stale-link UI now.” It is: stale temporary-share access must fail closed. A later revisit should either reach an explicit ended/expired/revoked bounded-share state or require a fresh share. It must not pretend the old share is still current by dropping the user onto a generic start-over shell or a successor session.

## Contract

- `net.publish.session.lifecycle.post_end_access_posture` is required.
- `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share`.
- Old copied/bookmarked/share handles must not silently bind to a later session or durable ingress surface after the bounded share ends.

## Checks

- `tools/check_publish_session_post_end_access_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0188-publish-session-post-end-access-stays-fail-closed.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r334


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
