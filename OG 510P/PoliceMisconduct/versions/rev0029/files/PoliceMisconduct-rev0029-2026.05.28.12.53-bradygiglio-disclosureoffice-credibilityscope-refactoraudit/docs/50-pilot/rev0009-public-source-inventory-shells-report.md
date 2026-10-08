# rev0009 public source-inventory shells report

Rev0009 converts the DOJ SLS law-enforcement source graph into **27 internal page shells**. These are not public release pages yet. They are preflight objects that test whether the cube can render useful department/matter source inventories without admitting current-status claims, person records, incident records, lawsuit-merits records, or settlement amounts.

The move is deliberately conservative: the seed imagines a national, longitudinal police-accountability corpus, but this revision only proves a display surface for source inventory and missingness.

## Counts

- Matter/page shells: 27
- Document-role rows: 148
- Missingness banners: 27
- Module permission rows: 378
- Copy-block candidates: 27
- Review queue tickets: 27
- Public current-status claims admitted: 0
- Person or incident records admitted: 0
- Full document summaries admitted: 0

## New rule

**A page shell is not a public department accusation page.**

The shell can hold: source owner, source page URL, observed source-page status label with timestamp, document-label counts, document-role counts, and a missingness banner.

The shell cannot hold: current legal-status banner, officer lookup, civilian/witness names, incident lists, lawsuit merits, settlement amounts, or document-content summaries.

## Why this matters

This is the first revision that treats display itself as a safety-critical data structure. The cube is now able to say not only what sources it has, but which public page modules are blocked and why.
