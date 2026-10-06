# Publish-session post-end management return stays lease-exact-ended
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must not let post-end management return dissolve into a generic surface. `lifecycle.post_end_management_return_posture` is now required and must stay `exact-ended-state-if-followed`, so any surviving trusted-UI return path or management deep link that is followed after the bounded share ends lands on the explicit ended state for that same lease instead of a generic share home, a successor lease, or a blank miss, with the ended bounded-share state itself still preserving the exact terminal cause through `lifecycle.terminal_end_condition`.

## Why

DeriveBSD already says relay-backed temporary sharing is leased, trusted-UI-visible, same-surface revocable, trusted-UI-reacquirable while live, lease-exact while live, and fail-closed for stale public/share handles after end. The neighboring datacubes made one remaining ambiguity look real rather than cosmetic: exact live return is still too weak if the same trusted-UI path loses bounded-share identity the moment the lease ends. Post-end recovery should preserve the identity of the ended bounded act too, not just the fact that sharing exists somewhere.

## Contract

- `net.publish.session.lifecycle.post_end_management_return_posture` is required.
- `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed`.
- If a surviving trusted-UI return path, browser-history entry, or management deep link for that publish session is followed after the share ended, it must resolve to the explicit ended / revoked / expired state for that same `authority.lease_id`. A generic share home, successor lease, or blank miss is not sufficient.
- That explicit ended state should preserve the exact terminal cause instead of flattening it away.
- This is adjacent to, not a replacement for, `docs/601-publish-session-management-return-paths-stay-lease-exact.md` (live exactness), `docs/598-publish-session-post-end-access-stays-fail-closed.md` (stale external share-handle behavior), and `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md` (terminal-cause exactness).

## Checks

- `tools/check_publish_session_post_end_management_return_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0192-publish-session-post-end-management-return-stays-lease-exact-ended.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/598-publish-session-post-end-access-stays-fail-closed.md`
- `docs/601-publish-session-management-return-paths-stay-lease-exact.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r334


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
