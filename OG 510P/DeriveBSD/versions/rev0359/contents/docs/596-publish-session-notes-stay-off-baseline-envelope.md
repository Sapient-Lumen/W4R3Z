# Publish-session notes stay off baseline envelope
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

## Summary

The compact `net.publish.session` receipt must stay note-free. Free-text `evidence.notes` is removed so the bounded temporary-sharing envelope cannot become a prose side channel for share meaning, operator interpretation, or support context.

## Why

DeriveBSD already carries typed surfaces for audience, access model, locator shape, authority joins, support/session linkage, secret handoff posture, and baseline-safe share evidence. Letting `evidence.notes` remain on the same compact envelope would let callers smuggle commentary back onto the outward/public-facing receipt instead of tightening the typed contract.

## Contract

- `net.publish.session` keeps only typed baseline-safe share fields on the compact envelope.
- `evidence.notes` is not part of the schema.
- Commentary, backstage interpretation, operator diagnosis, and support narrative belong on stronger evidence joins or dedicated neighboring receipts.

## Checks

- `tools/check_publish_session_notes_contract.py`
- `tools/validate_spec_examples.py`
- `tools/hygiene.py`

## References

- `adrs/ADR-0186-publish-session-notes-stay-off-baseline-envelope.md`
- `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`

Last updated: 2026-03-20r326


For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.
