# Publish-session visible indicators stay durable until ended
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must not treat active-share visibility as a weak boolean. `evidence.visible_indicator_posture` is now required and must stay `durable-until-ended`, so a transient toast or one-shot flash cannot stand in for the active share cue.

## Why

DeriveBSD already says relay-backed temporary sharing is leased, revocable, reboot-cleared, and trusted-UI-visible. A boolean `visible_indicator = true` left too much room for drift: the share could still be active even after the only cue had vanished. The receipt should say whether the indicator posture stayed durably present for the life of the share, not merely whether some visibility event happened once.

## Contract

- `net.publish.session.evidence.visible_indicator_posture` is required.
- `evidence.visible_indicator_posture = durable-until-ended`.
- Transient or auto-dismissing message posture is not enough to satisfy the active-share visibility floor. The adjacent revocation affordance now also has its own exact floor in `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md`, where `evidence.revocation_affordance_posture = same-surface-durable-until-ended` keeps the live stop/revoke control on the same durable active-share surface.

## Checks

- `tools/check_publish_session_visible_indicator_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0187-publish-session-visible-indicators-stay-durable-until-ended.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r329


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
