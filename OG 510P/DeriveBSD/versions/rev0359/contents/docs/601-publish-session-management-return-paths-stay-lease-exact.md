# Publish-session management return paths stay lease-exact
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must not let a stable trusted-UI return affordance quietly retarget. `evidence.management_return_binding` is now required and must stay `lease-exact`, so the still-live return path lands on the management surface for that exact bounded share instead of reopening a generic sharing hub, the nearest active share, or a successor lease.

## Why

DeriveBSD already says relay-backed temporary sharing is leased, trusted-UI-visible, same-surface revocable, reboot-cleared, fail-closed after end, and trusted-UI-reacquirable while live. The neighboring datacubes made one remaining ambiguity look real rather than cosmetic: a persistent return path is still too weak if it can silently rebind to the wrong current share after navigation, tab reuse, or UI re-entry. The receipt should say whether management return preserves bounded-share identity, not merely whether some path back into sharing exists.

## Contract

- `net.publish.session.evidence.management_return_binding` is required.
- `evidence.management_return_binding = lease-exact`.
- A stable trusted-UI return affordance for a still-live publish session must re-enter the management surface for that exact `authority.lease_id`. A generic share home, nearest-current-share view, or successor lease is not sufficient. The adjacent post-end exactness floor lives in `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`, where `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed` keeps any surviving post-end return path bound to the explicit ended state for that same lease instead of losing bounded-share identity after end.

## Checks

- `tools/check_publish_session_management_return_binding_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0191-publish-session-management-return-paths-stay-lease-exact.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r334


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
