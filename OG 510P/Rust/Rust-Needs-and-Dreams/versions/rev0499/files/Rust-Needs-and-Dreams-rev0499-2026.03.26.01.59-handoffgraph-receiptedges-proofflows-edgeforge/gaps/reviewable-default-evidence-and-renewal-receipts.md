# Gap: Reviewable default evidence and renewal receipts

## Missing thing
Rust is missing a portable way to say:
> here is the evidence bundle behind this currently recommended lane, here is when it was checked, here is what changed, and here is why the default still stands (or no longer does).

## Why this matters
The ecosystem now has enough public signals to support better defaults:
- official docs and books;
- crates.io security and publishing signals;
- `pubtime` and time-aware resolution inputs;
- emerging SBOM and public/private dependency support;
- semver-checking work;
- maintainer-support and maintenance-reality discussions.

But these signals are still too easy to leave scattered.
That means default guidance risks becoming:
- one blog-post synthesis,
- one assistant answer,
- one org-internal stack page,
- or one stale starter template.

## Consequences of the gap
Without renewal receipts:
- reasonable default cards become hard to maintain;
- serious alternatives disappear into prose;
- harder lanes like safety-tilted defaults remain too risky to publish;
- assistants and internal platform teams re-invent the same judgment over and over;
- and recommendation authority drifts back into tacit knowledge.

## What would close the gap
A thin `lane-evidence-pack/v0` family that keeps separate:
- canonical references;
- registry/supply-chain evidence;
- public API / compatibility evidence;
- maintenance/support-envelope posture;
- freshness and diff over time;
- and the final renewal judgment.

## Closest files
- `design/reviewable-lane-defaults.md`
- `design/lane-default-evaluation-framework.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/package-admission-stack.md`
- `design/maintenance-reality-stack.md`
- `design/compatibility-claims-stack.md`

## Promising next move
Promote **Lane Default Evidence Bundle** as the next practical seam beneath the corpus, and prove it with one renewal lane and one new bounded card instead of widening the corpus by volume.
