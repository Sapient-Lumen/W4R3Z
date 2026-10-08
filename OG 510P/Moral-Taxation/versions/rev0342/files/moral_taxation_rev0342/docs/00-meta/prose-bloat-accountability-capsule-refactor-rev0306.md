# rev0306 prose-bloat accountability capsule refactor

Rev0306 addresses the main post-compression risk left by Rev0305: route memos were repeating actor-accountability tables whose canonical assignments now live in `actor-accountability-profiles.json`.

## Change

- Rewrote 85 legacy `Rev#### accountability map` sections into compact `Accountability capsule` sections.
- Removed the repeated six-question table form from live route prose.
- Preserved route-specific duty owner, beneficiary/rent trace, bottleneck/evidence start, and fallback duty in each capsule.
- Kept citations where a removed accountability section had source footnote usage.

## Metrics

| Metric | Value |
|---|---:|
| Legacy accountability sections rewritten | 85 |
| Accountability section bytes before | 97543 |
| Accountability capsule bytes after | 77366 |
| Bytes saved in those sections | 20177 |
| Legacy table headers remaining | 0 |
| Legacy Rev#### accountability-map headings remaining | 0 |
| Accountability capsules after rewrite | 85 |

## Rule going forward

Route memos may keep a short capsule for local readability, but the six-field accountability assignment belongs in `docs/00-meta/actor-accountability-profiles.json`. If a route needs more than the capsule, it should explain an exception or contested judgment, not reproduce the profile table.
