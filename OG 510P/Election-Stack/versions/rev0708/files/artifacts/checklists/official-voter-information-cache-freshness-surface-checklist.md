# Official voter-information cache-freshness checklist

Use this quickcheck when an election office needs a bounded way to keep current voter-information pages from replaying stale answers through browser, CDN, or service-worker layers.

## Critical page scope

- Identify a small set of mutable current-answer page classes rather than treating every response like a static asset.
- Keep the office/help recovery lane in the critical set.
- Re-check the set when a new emergency page, deadline page, lookup flow, or cure/status page is introduced.

## HTTP / edge-cache posture

- Confirm that mutable HTML answer documents have an explicit validation posture rather than blind long-lived reuse.
- Prefer keeping validators available on mutable answer documents.
- Do not assume `no-store` alone fixes stale-answer reuse.
- Review CDN/edge behavior separately from origin intent when a critical answer changed at the same URL.

## Service-worker posture

- Declare whether service workers intercept critical navigations.
- Avoid cache-first handling for mutable current-answer documents unless the freshness risk is explicitly reviewed.
- Distinguish static-asset caching from navigation/document caching.
- Re-check critical pages after service-worker, routing, or offline-mode changes.

## Update and rollback readiness

- Confirm there is a bounded way to move users onto a waiting service-worker update after a material answer change.
- Keep a same-URL no-op or equivalent neutralization path for buggy service-worker incidents.
- Treat emergency cache/storage eviction as an exceptional measure, not the ordinary publication model.
- Check that the office/help lane remains visible when stale-answer recovery is underway.

## Evidence posture

- Preserve only critical page-class labels, mutable-document classification state, validator/revalidation posture, service-worker navigation-scope state, waiting-update visibility state, rollback readiness, emergency-eviction readiness, and last review time.
- Do not preserve full HAR files, giant CDN debug dumps, per-user cache keys, browser storage inventories, or session replays when bounded policy reconstruction is sufficient.
