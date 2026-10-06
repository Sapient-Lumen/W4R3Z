# Publish-session diagnostic artifacts stay off baseline envelope

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

`net.publish.session` already says temporary sharing is a compact typed envelope: local-first
source, relay/transport join, explicit audience/authn posture, exact authority join, bounded
lifecycle, and a lease-frozen outward published-endpoint surface.

One smaller ambiguity still remained inside the evidence object itself:

> should the compact publish-session envelope also point directly at backstage relay/admin
> diagnostic artifacts?

If the archive leaves that open, the same receipt stops being clearly share-shaped.
It becomes half bounded share envelope and half privileged investigation surface.

See `adrs/ADR-0185-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`.

## Boundary

`net.publish.session.evidence` now stays baseline-envelope shaped.

### No `diagnostic_artifact_digests` on the compact publish-session envelope

`evidence.diagnostic_artifact_digests` is now removed from `net.publish.session`.

The compact envelope may still carry share-shaped summary evidence such as:

- `visible_indicator_posture = durable-until-ended`
- `network_receipt_digests`

But it no longer directly names backstage relay/admin/debug artifacts. A follow-on narrowing removes free-text `evidence.notes` too, so the same bounded receipt stays note-free instead of regrowing a prose side channel; another follow-on tightening replaces the old boolean visibility bit with required `visible_indicator_posture = durable-until-ended`, so the same bounded receipt also stops confusing transient flashes with lifetime-visible active-share state; see `docs/596-publish-session-notes-stay-off-baseline-envelope.md` and `docs/597-publish-session-visible-indicators-stay-durable-until-ended.md`.

### Richer diagnostics travel on the stronger evidence lanes instead

If support or investigation needs richer diagnostics, those artifacts now belong on the already
existing stronger evidence families instead of the baseline share envelope:

- `support.session`
- `operator.session`
- `incident.bundle`

This keeps the temporary-sharing receipt compact while preserving a place for deeper investigation
joins.

## What this prevents

### No baseline/privileged evidence blur inside one share receipt

Support/UI/export no longer have to guess whether `net.publish.session` is still the compact share
envelope or already a privileged log surface.

### No backstage log pointers hiding on an otherwise ship-safe surface

The envelope can still be bundled and reviewed as the bounded sharing act without quietly dragging
along a second investigation-only artifact index.

### No accidental pressure to treat every temporary share as an incident bundle

Temporary sharing stays small by default.
Only sessions that actually need deeper support/investigation joins escalate onto the stronger
evidence lanes.

## Why this is the right floor now

This is intentionally narrow.
It does **not** define a full privileged-log taxonomy, role matrix, or new admin-session object.
It only prevents the current compact publish-session envelope from becoming a mixed baseline-plus-
backstage surface.

That is enough to keep temporary-sharing exports, support bundles, and future implementation more
coherent without widening the archive.

For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_diagnostic_artifact_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`
- `docs/229-evidence-spine-overview.md`
- `docs/251-export-policies-and-support-bundle-portal.md`

Last updated: 2026-03-20r327
