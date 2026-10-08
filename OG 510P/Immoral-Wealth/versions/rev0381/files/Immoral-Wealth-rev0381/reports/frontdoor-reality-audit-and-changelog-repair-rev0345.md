---
revision_current: rev0355
status: active_report
claim_kind: audit_refactor
route_role: archive_governance_core
route_refs:
- archive_governance_core
- source_governance_core
canonical_anchor: false
supersedes: rev0344
depends_on:
- CHANGELOG.md
- cases/CASE_LEDGER.json
- cases/EVIDENCE_LEDGER.json
- docs/00-meta/field-registry.json
- SOURCES.json
---

# Front-door reality audit and changelog repair — rev0355

## What was missing

The cube had spent rev0344 repairing unused source lineage, but several front-door documents still told older release stories. The most important examples were:

- `cases/case-portfolio-summary.md` described the portfolio as 91 case memos and 91 scoreboards.
- `docs/20-program/case-portfolio-coverage-map.md` still carried an 88-case carry-forward statement.
- `docs/20-program/scoreboard-spec.md` mixed old schema-count language with current frontmatter.
- `docs/90-open/open-questions.md` still asked about 56 unused schema fields.
- `CHANGELOG.md` said `revision_current: rev0355`, opened with rev0343, duplicated a rev0342 heading, omitted a visible rev0341 heading, had no visible rev0324 heading, left rev0344 at the tail after rev0200-era history, and also left rev0327-rev0332 stranded after rev0200.

## What had gone severely wrong

The validator was checking whether the current revision string appeared anywhere in a current-release surface. A trailing release note was enough to pass even when the main body still carried old counts. That is not a storage problem; it is a truth-surface problem. It makes the archive look current while the human entry points are stale.

## What changed in rev0345

- Current portfolio surfaces now say **95 case memos and 95 scoreboards**.
- The scoreboard spec now says **367 registered field keys** and **50 registered_unused fields**.
- Open questions now name the current field-retirement queue: **50 registered_unused fields**.
- The changelog opens with rev0345, then rev0344; the duplicate top frontmatter block and nested `# Changelog` marker were removed; rev0327-rev0332 were moved back above rev0326 in near-current order.
- A new validator check fails if these front-door facts drift again.

No new sources, cases, or schema fields were added.

## Current metrics

| Metric | Value |
|---|---:|
| Case memos | 95 |
| Scoreboards | 95 |
| Sources | 489 |
| Evidence edges | 5407 |
| Registered field keys | 367 |
| Active fields | 317 |
| Registered-unused fields | 50 |
| Case memos under 2500 bytes | 13 |
| Sources without case use | 19 |
| Retained aliases without case use | 19 |

## Waste map

The largest apparent waste is generated ledger bulk, not ZIP size. `cases/EVIDENCE_LEDGER.json` is 2408570 bytes uncompressed but compresses to 55305 bytes. That means it is cheap inside a ZIP but expensive to read and diff. The better long-term correction is to keep compact human summaries and regenerate full ledgers from scoreboards when needed.

The second waste class is metadata overloading. `source_type` currently carries many meanings: provenance, source fit, evidence role, retained-alias state, context, tracker, official status, and sometimes document form. This should become separate fields before the next large source-expansion revision.

The third waste class is historical active-status ambiguity. Old report and release-note language remains searchable beside live doctrine, which makes stale counts easy to reanimate. The archive needs an explicit status taxonomy for current-law cases, historical comparators, retained release history, generated ledgers, and scaffolding notes.

The validation pass also exposed a wasteful report-churn pattern: three older checks were still using `CURRENT_REVISION` to locate legacy audit reports, which would force regenerated copies of rev0337, rev0338, and rev0341 audit artifacts on every later release. Rev0345 pins those checks to their actual historical report files instead.

## Online scan: currentness risks not yet ingested as sources

The web scan suggests the next recertification work should focus on volatile surfaces rather than more schema growth:

- U.S. wealth distribution and macro balance-sheet surfaces should track the Federal Reserve Distributional Financial Accounts and Z.1 release timing.
- Beneficial-ownership transparency needs current-law recertification because domestic U.S. entities were exempted from BOI reporting under the 2025 FinCEN interim final rule.
- Medical-debt credit-reporting cases need recertification because the CFPB Regulation V medical-debt rule was vacated in July 2025.
- AI/data-center public-balance-sheet cases should keep a short refresh cadence because large-load interconnection and co-location policy is moving through federal energy governance.
- UK wealth-statistics cases should track ONS quality/accreditation warnings and top-tail uncertainty rather than treat a survey release as a stable measurement anchor.
- Canada and WID/WIR wealth-distribution surfaces should carry explicit comparability/provisional-data warnings.
- AI electricity demand should stay on the Gate 20 watchlist because data-center growth can shift grid, water, interconnection, and ratepayer costs.

These findings are deliberately not converted into new source rows in rev0345; they are a recertification queue for later substance-first hardening.

## Next repair queue

1. Normalize source metadata into provenance, evidence role, source fit, and retained-alias state.
2. Add a generated-artifact policy for evidence/source/route/currentness ledgers.
3. Reclassify historical release reports so stale front-door statements cannot masquerade as current doctrine.
4. Burn down the **50 registered_unused fields** through retire/quarantine/activate decisions.
5. Add currentness-specific validator checks for Fed DFA/Z.1, FinCEN BOI, CFPB medical debt, FERC large loads, ONS wealth quality, Statistics Canada DHEA, WID/WIR, and IEA AI-energy evidence before any new case family is added.
