---
status: active_doctrine
claim_kind: evidence_protocol
route_role: certification_core
canonical_anchor: true
route_refs:
- certification_core
- source_governance_core
supersedes: null
depends_on:
- scoreboard-schema.json
- minimum-evidence-pack-for-case-work.md
source_refresh_due: 2026-12-31
---

# Evidence debt register and data plan

rev0305 made evidence debt explicit. rev0306 extended the rule to liability stacks, life interruptions, and secure-renter substitution. rev0307 extends it again to conversion rails, claim finality, payment rails, title proof, and starter-asset maturity. The archive should no longer say “data are missing” and then proceed as if missingness were harmless.

## Debt classes

### Low

The missing field would refine confidence but is unlikely to change the verdict.

Example: exact top 0.1% wealth share is unavailable, but top 1%, bottom half, group gaps, ownership registries, and political capture signals all point the same way.

### Medium

The missing field may change package order or mode.

Example: the housing washout channel is visible, but deposit, guarantee, rent burden, mortgage-access, and regional split data are incomplete.

### High

The missing field can block soft certification.

Example: a country looks acceptable on household wealth shares, but pension valuation, household control, migrant access, and top-tail correction are unresolved.

### Blocking

The missing field is itself a rule or closure problem.

Example: beneficial ownership is secret, land records are non-public, court debt is not centrally measured, top-tail wealth is likely hidden offshore, or household assets are counted without knowing whether women, migrants, disabled people, caste groups, renters, or young adults can actually control them.

## Minimum data plan for each case

Each active case should record:

1. official wealth distribution;
2. corrected top-tail estimate or undercoverage warning;
3. bottom-half liquid/security buffer;
4. housing-entry and rent-burden evidence;
5. inheritance/parental-transfer evidence;
6. subgroup wealth/control split;
7. public/social counterweight claim rules;
8. ownership-legibility and enforcement rails;
9. fastest washout channel;
10. one reopening trigger;
11. liability-stack composition and consequence evidence;
12. renter/non-owner substitution evidence when homeownership is not the relevant foothold;
13. claim-conversion evidence for any benefit, tax credit, transfer, social-housing claim, public dividend, starter account, disaster aid, pension, or title claim used in the verdict;
14. fee leakage, offset, garnishment, and payment-rail evidence for small claims;
15. title/probate/disaster-proof evidence for inherited or occupied property.

## Upgrade rule

A case memo can remain useful while provisional. But a case cannot be called `acceptable` or `near_ideal` while high or blocking evidence debt remains on any gate that could reverse the moral verdict.

## JSON location

Use the root `evidence_debt_register` field added in rev0305 scoreboards. Each item should include:

- `question`;
- `severity`;
- `next_evidence`;
- optional `source_ids`.

This register is meant to make future work obvious. It is also a guardrail against laundering speculation into certification.


## rev0306 required debt/interruption questions

Each active case should now ask:

1. Are medical, student, criminal-legal, collections, care, disability, or high-cost-credit liabilities material to lower-half wealth?
2. Which debts carry consequences beyond payment, such as license loss, credit damage, record blocks, housing denial, benefit offset, or employment exclusion?
3. Which debts are state-created or state-amplified?
4. Are debt burdens and consequences reported by race/caste/gender/disability/citizenship/age/region/household form?
5. Can secure renting or social housing substitute for ownership, or does non-ownership simply hide a missing foothold?

Missing answers to these questions are not necessarily fatal in every case. They are fatal when the case is seeking `acceptable` or `near_ideal` certification on floor, threshold, or renter-security grounds.[S104][S108][S110][S196]


## rev0307 required conversion questions

Each active case should now ask:

1. Which nominal claims does the case rely on for floor, early-foothold, public/common, or emergency-repair certification?
2. What share of eligible people actually receive each claim?
3. Which identity, address, household, disability, income, immigration, title, or account documents are required?
4. What payment rail is used, and is it low-cost, person-controlled, and accessible offline or with assistance?
5. How long does the claim take from eligibility to usable receipt?
6. What share of value is lost to fees, paid intermediaries, offsets, garnishment, clawbacks, or account penalties?
7. Which groups are more likely to be denied, delayed, churned off, underpaid, or unable to appeal?
8. Can the claimant correct errors without lawyers, expert help, or long delays?
9. Are starter accounts found and claimed at maturity?
10. Can inherited or occupied property be converted into repair, insurance, disaster aid, credit, sale, or transfer value?

Missing answers are fatal when the case uses the nominal claim as evidence of a real floor, first foothold, public/common counterweight, or asset-security pass.[S120][S263][S122][S124][S126][S262][S130][S133][S139][S140]


## rev0308 measurement evidence debt

A case now carries high-severity evidence debt when its verdict depends on top-tail coverage, source accreditation, macro/micro reconciliation, beneficial-owner verification, trust/legal-arrangement coverage, or private-asset valuation. Evidence debt is not closed by citing one point estimate; it is closed by showing why the verdict survives plausible low/central/high readings.[S141][S142][S146][S147][S431][S155]
