# Publish-session ended states stay terminal-cause exact
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must not let explicit ended-share state flatten away the exact bounded end cause. `lifecycle.terminal_end_condition` is now required whenever `ended_at` is present, absent while `ended_at` is absent, and must stay within the declared `lifecycle.end_conditions` vocabulary so ended bounded-share state preserves which terminal cause actually fired.

## Why

DeriveBSD already says relay-backed temporary sharing is leased, trusted-UI-visible, same-surface revocable, trusted-UI-reacquirable while live, lease-exact while live, fail-closed for stale public/share handles after end, and exact-ended if a surviving management return is followed after end. The remaining ambiguity was smaller but still real: even an explicit ended state was free to collapse lease expiry, manual revoke, local-service loss, session end, maintenance-window end, and host reboot into one vague terminal label. The archive already carries a typed end-condition vocabulary, so the ended state should preserve that exact terminal cause instead of discarding it at the boundary.

## Contract

- `net.publish.session.lifecycle.terminal_end_condition` is introduced.
- If `ended_at` is present, `lifecycle.terminal_end_condition` is required.
- If `ended_at` is absent, `lifecycle.terminal_end_condition` must be absent.
- `lifecycle.terminal_end_condition` must stay within the existing publish-session `lifecycle.end_conditions` vocabulary and name one of the declared end conditions for that bounded share.
- This contract composes with `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/598-publish-session-post-end-access-stays-fail-closed.md`, and `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`.

## Checks

- `tools/check_publish_session_terminal_end_condition_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0193-publish-session-ended-states-stay-terminal-cause-exact.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/598-publish-session-post-end-access-stays-fail-closed.md`
- `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r334


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
