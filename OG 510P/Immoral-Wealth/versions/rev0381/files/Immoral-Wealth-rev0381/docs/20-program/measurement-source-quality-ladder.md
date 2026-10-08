---
status: active_protocol
claim_kind: source_quality_protocol
route_role: source_governance_core
canonical_anchor: false
route_refs:
- measurement_uncertainty_core
- source_governance_core
supersedes: null
depends_on:
- source-order-and-conflict-resolution.md
- top-tail-audit-and-uncertainty-bounds.md
source_refresh_due: 2026-12-31
---

# Measurement source quality ladder

Use this ladder when wealth estimates conflict. It does not rank institutions morally; it ranks **fitness for this archive's certification task**.

## Ladder

1. **Verified administrative or registry microdata linked to national accounts** — strongest when privacy-safe, auditable, and able to capture top-tail, debt, pension, housing, and entity ownership.
2. **Distributional national accounts or national-accounts-consistent experimental accounts** — strong for macro consistency, weaker when underlying microdata cannot see top controllers.[S142][S143]
3. **Survey plus tax/rich-list/top-tail correction** — strong when correction method is explicit and repeatable.[S144][S146][S150]
4. **High-quality household wealth survey with high-net-worth oversample** — usable but requires nonresponse, item-response, and top-tail checks.
5. **Ordinary survey-only estimate** — usable for broad middle/lower distribution, weak for very top shares.
6. **Commercial rich list** — useful for top-tail floor and private-valuation clues, not sufficient alone for distributional certification.[S159]
7. **Advocacy or media estimate** — can trigger evidence debt; cannot certify unless traceable to stronger underlying data.

## Demotion rules

A source is demoted when:

- its official status or accreditation is suspended;
- response rates or mode shifts materially change comparability;
- it excludes top wealth holders or institutionalized/offshore owners;
- it lacks household/person/control distinction;
- it cannot separate pensions, housing, business equity, and liquid wealth;
- it reports stale data after a major asset-price, tax, war, inflation, or currency shock.

UK wealth statistics now provide a live example: accreditation concerns mean a survey-based estimate can still be informative, but it cannot carry a soft certification by itself.[S147][S148][S149]

## Conflict handling

When source families conflict, the archive should not average them. It should write the conflict into the scoreboard:

- `survey_reading`;
- `top_tail_adjusted_reading`;
- `macro_consistent_reading`;
- `ownership_visibility_reading`;
- verdict consequence.

A case should name which estimate it is using for moral judgment and which estimates remain live rivals.
