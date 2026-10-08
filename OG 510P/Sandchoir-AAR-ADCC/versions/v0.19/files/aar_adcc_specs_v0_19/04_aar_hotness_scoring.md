# 04 — AAR Hotness Scoring (v0.19)

Hotness is a bounded integer score used for promotion/eviction and view ordering.

## Inputs (additive)
- +100: H0 (always pinned)
- +80: mandatory events (mode/strictness change, lease affecting your scope)
- +70: selected patch changed
- +70: certified CE added/updated
- +60: top blocking failure evidence (latest fail in canonical checks)
- +40: item referenced by selected patch or certified CE
- +30: received >=2 attention upvotes, or 1 upvote from a high-weight agent
- +20: created/updated recently (decays)
- +10: belongs to your subscription scope

## Decay
- Each cursor tick: decay recentness contribution slowly.
- If untouched for N cursors and not referenced: mark `stale`.

## Promotion rule (default)
Item enters `HOT` if:
- score >= 60, OR
- explicitly promoted by vote and score >= 40, OR
- mandatory by type.

## Demotion/eviction eligibility
- score < 20 and stale → candidate for eviction/compaction.
- Demotion never removes mandatory anchors.
