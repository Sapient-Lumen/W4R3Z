---
status: active_bridge
claim_kind: program_rule
route_role: implementation_core
canonical_anchor: false
route_refs:
- implementation_core
- case_calibration_core
supersedes: null
depends_on: []
source_refresh_due: 2026-11-30
case_pressure: rev0304_portfolio_calibration
---

# Local housing ownership concentration screen

## What this note is for

This note sharpens the housing lane. It tells the archive not to confuse national ownership shares with local market power. A landlord or investor category can be small nationally and still meaningful in a specific rental submarket, neighborhood, or metropolitan entry channel.

Use this note with [`housing-land-and-anti-monopoly.md`](housing-land-and-anti-monopoly.md), [`dominant-breach-and-fastest-washout-selection.md`](dominant-breach-and-fastest-washout-selection.md), and [`../10-framework/spatial-concentration-and-place-based-closure.md`](../10-framework/spatial-concentration-and-place-based-closure.md).

## Minimum operating rule

Do not certify or dismiss a housing-concentration claim from national shares alone. GAO's 2026 study of six metro areas found institutional investors owned from less than 1% to 3% of all single-family homes, but from 4% in Seattle to 22% in Jacksonville of single-family rental homes in 2024.[S418]

That is the archive's model distinction: the same fact pattern can mean **small national footprint** and **material local submarket power**.

## Case questions

1. What is the relevant market: all homes, all rentals, single-family rentals, entry-level homes, a school catchment, a neighborhood, or a metropolitan commute zone?
2. Is the concern purchase competition, rent-setting, fees, maintenance, eviction, tenant bargaining, financing, land banking, or political influence?
3. Are institutional owners the main bottleneck, or are zoning, supply, credit, tax, insurance, and household-income constraints doing more work?
4. Does concentration interact with race, migration status, age, disability, or family structure?
5. Would the proposed cure improve entry and security, or merely change the landlord mix without adding supply, tenant power, or affordability?

## False passes

- **National-small pass:** dismissing local power because the national share is small.
- **Local-outrage pass:** treating any investor presence as the dominant breach without checking supply, credit, rent burden, and ownership alternatives.
- **Ownership-only pass:** focusing on purchase shares while ignoring fees, maintenance, lease terms, repair delays, and eviction practice.
- **Supply-blind pass:** banning one buyer class while leaving scarcity and land-price dynamics untouched.
- **Tenant-invisible pass:** measuring only buyer competition while renters' bargaining and security deteriorate.

## Scoreboard fields

| Field | Question |
|---|---|
| `local_ownership_concentration` | What share of the relevant local submarket is held by large or coordinated owners? |
| `entry_home_purchase_share` | Are investors buying homes ordinary first-time buyers could realistically buy? |
| `tenant_bargaining_surface` | Do lease terms, fees, repairs, and evictions show concentrated power? |
| `supply_elasticity_and_land_rules` | Is scarcity doing more work than ownership concentration? |
| `group_specific_exposure` | Are excluded groups more exposed to the concentrated submarket? |

## Program implications

Use local concentration evidence to choose targeted remedies: registry and disclosure, tenant protections, anti-fee rules, repair enforcement, fair-housing enforcement, anti-collusion tools, public/social housing, land-value capture, supply reforms, and limits on concentrated acquisition where justified. The package should target the mechanism actually causing closure.
