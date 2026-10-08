# Approved source hierarchy

GlassTTY now treats source authority as a first-class support input.

## Why

A support bundle can be honest about repo evidence and still overclaim if it never says which first-party or vendor-runtime sources justify the product/runtime framing around that evidence.

## Hierarchy

1. **first-party-product-surface** — official product pages or first-party product/help surfaces that establish that a browser surface exists and belongs to the vendor.
2. **vendor-runtime-doc** — browser/extension/runtime docs that define MV3 lifecycle, native-host registration, permissions, and similar substrate semantics.
3. **standards-reference** — web-platform references for route/history semantics when vendor docs are not precise enough.
4. **repo-current-evidence** — live captures, support bundles, and repo truth surfaces that show what this archive can currently prove.

## Rule

Repo evidence can strengthen or weaken a claim, but it does not replace source authority for product identity or runtime semantics.

That is why `SUPPORT-SOURCE-LOCK.json` exists beside the support queue and publish gate rather than inside them.

## Freshness rule

Approved authority is not timeless. The source lock now carries a review-age policy, and stale or missing review dates should be treated as a visible warning at baseline time and a publication blocker when required source refs are involved.
