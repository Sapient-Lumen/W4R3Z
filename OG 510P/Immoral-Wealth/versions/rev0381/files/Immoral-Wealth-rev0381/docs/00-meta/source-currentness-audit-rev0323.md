---
status: audit
claim_kind: source_currentness
route_role: temporal_currentness_core
canonical_anchor: true
route_refs:
- temporal_currentness_core
- source_governance_core
- certification_core
supersedes: rev0322
depends_on:
- currentness-ledger.json
- SOURCES.json
source_refresh_due: 2027-03-31
revision_current: rev0370
---

# Source currentness audit — rev0357

rev0323 audits a different subsystem from evidence, routes, remedy operability, and fields: **temporal currentness**. The archive already stores `date`, `accessed`, and `refresh_due` in `SOURCES.json`, but operators still lacked a first-class ledger explaining which claims are volatile because law, guidance, release lags, or rulemaking changed.

## Findings

- Current-law claims need a `snapshot_date`; they cannot be treated as timeless facts.
- Tax, trust, beneficial-ownership, and charitable-vehicle sources have different refresh cadences.
- Litigation and rulemaking surfaces need shorter review loops than ordinary statistical releases.
- Old scoreboards can pass mechanical validation while carrying a stale legal premise.

## rev0323 repair

- Adds `docs/00-meta/currentness-ledger.json`.
- Adds temporal-currentness schema fields such as `temporal_currentness_gate`, `current_law_snapshot_date`, `source_staleness_risk`, `law_effective_date_stability`, and `litigation_or_rulemaking_volatility`.
- Adds validator checks for currentness-ledger revision sync and rev0323 case-family coverage.
- Adds stress cases where currentness is not cosmetic: transfer-tax law date, BOI reporting perimeter, trust duration, and charitable-vehicle public subsidy. [S427][S428][S429][S430][S431][S432][S433][S434][S435][S436][S437][S438][S439][S440]
<!-- current_revision: rev0324; audit overlay: semantic-currentness-invariants-and-cloudtainer-waste-map -->
<!-- current_revision: rev0325; overlay: substance-case-hardening-and-refresh-sync-refactor -->

<!-- current_revision: rev0326; codename: gate20-backstop-burndown-and-source-canonicalization -->

<!-- current_revision: rev0327; codename: compute-climate-health-minerals-backstop-burndown -->

<!-- current_revision: rev0328; codename: federal-claim-security-credit-guarantee-burndown -->

<!-- current_revision: rev0329; codename: sovereign-fiscal-contingent-liability-and-public-asset-burndown -->

<!-- current_revision: rev0330; codename: score-mediated-exclusion-rights-remedy-burndown -->

<!-- current_revision: rev0331; codename: fresh-start-family-transfer-backlog-closure-and-source-fit-refactor -->

<!-- current_revision: rev0332; codename: seed-backlog-closure-and-gate-inventory-source-refactor -->

<!-- current_revision: rev0333; codename: workplace-power-current-law-hardening-and-seedclass-refactor -->

<!-- current_revision: rev0334; codename: household-market-extraction-current-law-hardening-and-seedclass-burndown -->

<!-- current_revision: rev0335; codename: place-public-finance-service-floor-hardening-and-sourcefit-refactor -->

<!-- current_revision: rev0336; codename: jurisdictional-mobility-current-law-hardening-and-sourcefit-burndown -->

<!-- current_revision: rev0337; codename: democratic-power-and-portfolio-seedclass-closure; rollforward_marker: rev0337 -->

<!-- current_release: rev0339; rev0339 currentness/callchain repair validated -->

<!-- current_release: rev0340; memo-citation-lineage-and-source-alias-canonicalization validated -->
<!-- current_release: rev0342; case-memo-status-drift-and-stale-seed-language-repair validated -->

<!-- current_revision: rev0343; live-doc source alias canonicalization validated -->

> rev0344 release-surface note: source-use lineage and validator callchain were repaired in rev0344; this document remains an active live surface.


> rev0345 current-surface note: retained as a current release surface after the front-door reality audit and changelog repair.


## Rev0360 additions

- `S538`: West Feliciana IDB resolution route; refresh due 2026-07-31.
- `S539`: local reporting on Hut 8 $10M PILOT advance and cooperative endeavor agreement; refresh due 2026-07-31.


Current release marker: rev0370.
