# Publish-session revocation affordances stay same-surface durable
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must not leave the stop/revoke control implicit. `evidence.revocation_affordance_posture` is now required and must stay `same-surface-durable-until-ended`, so the active bounded share keeps an immediate revoke path on the same trusted-UI surface as the durable share cue for the life of the session.

## Why

DeriveBSD already says relay-backed temporary sharing is leased, revocable, reboot-cleared, and trusted-UI-visible. The neighboring datacubes made one remaining ambiguity look real rather than cosmetic: a durable cue is still too weak if the actual stop action hides in a transient toast button, a buried menu, or a different route the user has to rediscover while the share remains live. The receipt should say whether the revoke affordance stayed durably present on the same active-share surface, not merely whether some later control existed somewhere.

## Contract

- `net.publish.session.evidence.revocation_affordance_posture` is required.
- `evidence.revocation_affordance_posture = same-surface-durable-until-ended`.
- A transient toast/snackbar action, overflow-menu scavenger hunt, or off-surface revoke path is not sufficient to satisfy the active-share stop floor.
- Adjacent return/re-entry persistence is tracked separately by `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`; this document stays about the live stop affordance once the user is on the active-share surface.

## Checks

- `tools/check_publish_session_revocation_affordance_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0189-publish-session-revocation-affordances-stay-same-surface-durable.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r334


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
