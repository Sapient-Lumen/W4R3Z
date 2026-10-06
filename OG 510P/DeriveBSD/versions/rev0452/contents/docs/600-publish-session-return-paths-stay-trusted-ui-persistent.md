# Publish-session return paths stay trusted-ui persistent
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must not leave return to the live-share management surface implicit. `evidence.management_return_path_posture` is now required and must stay `trusted-ui-persistent-until-ended`, so a still-live bounded share keeps a stable trusted-UI re-entry path for the life of the session instead of relying on browser back/history luck, a one-shot toast, or route rediscovery.

## Why

DeriveBSD already says relay-backed temporary sharing is leased, trusted-UI-visible, same-surface revocable, and reboot-cleared. The neighboring datacubes made one remaining ambiguity look real rather than cosmetic: a durable cue plus revoke button is still too weak if leaving the page strands the operator and the only way back is navigation luck or memory. The receipt should say whether the active-share management surface stayed reacquirable through a stable trusted-UI entry, not merely whether some control once existed on-screen.

## Contract

- `net.publish.session.evidence.management_return_path_posture` is required.
- `evidence.management_return_path_posture = trusted-ui-persistent-until-ended`.
- Browser back/history luck, a transient toast/snackbar link, or manual route rediscovery is not sufficient to satisfy the active-share management-surface return floor while the share is still live. The adjacent exactness floor now also lives in `docs/601-publish-session-management-return-paths-stay-lease-exact.md`, where `evidence.management_return_binding = lease-exact` keeps that stable return path bound to the exact live `authority.lease_id`.

## Checks

- `tools/check_publish_session_return_path_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0190-publish-session-return-paths-stay-trusted-ui-persistent.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r334


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
