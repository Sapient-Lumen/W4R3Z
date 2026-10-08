# 544 — Nuclear emergency preparedness: lifeline infrastructure, fuel, water, telecom, and restoration-priority firebreak

Revision: **rev0337**  
Scope: **REAL_BVPS_PUBLIC_ONLY remains public-context-only. No real readiness or unreadiness claim is made.**

## Why this exists

The cube has built a strong branch-by-branch emergency-readiness spine: alerting, field receipt, action uptake, CRC/decon, first receivers, dose/PAR, ingestion controls, recovery, sustainment, and cyber/data continuity. The remaining shared risk is that all those branches may quietly assume the same fragile community lifelines: electric power, emergency fuel, telecommunications, water/wastewater, transportation access, hazardous-material interfaces, public works, and restoration priority.

This revision adds a cross-sector lifeline-infrastructure proof spine. The doctrine boundary is strict: **public lifeline, water, energy, telecom, CISA, DOE, EPA, FEMA, NRC, or utility guidance can create evidence demand, cap a claim, route an issue, or reopen a finding. It cannot close local emergency-readiness evidence.**

## Operational rule

A downstream emergency branch cannot be green if its lifeline dependency is red or unknown. A CRC throughput packet cannot close if potable water, wastewater, decon-water handling, generator fuel, traffic access, staff communications, or sewage service are unproven. A hospital surge packet cannot close if utility power, water, oxygen, telecom, fuel, and road access are unproven. A public-alert packet cannot close if telecom/cellular/EAS/LMR dependencies are unknown. A dose-field packet cannot close if met feeds, model workstations, field-team radios, GPS/PNT, road access, and fuel are unproven.

## New proof route

`branch claim → lifeline dependency DAG → lifeline status packet → restoration priority conflict check → emergency fuel / power / telecom / water / transportation / hazmat packets → CAP/retest/verifier → public claim gate`

## Anti-theater defaults

* A generator inventory is not fuel endurance.
* A utility ERP is not restored potable water.
* A telecom plan is not channel availability.
* A road map is not route access under debris, flood, snow, heat, smoke, or security control.
* A public lifeline dashboard is not local packet proof.
* A public source ID is not independent corroboration when it aliases the same canonical URL.
* A restoration priority list is not restoration execution.

## New rev0337 surfaces

The main files are:

* `cube/nuclear-emergency-bvps-lifeline-infrastructure-proof-ladder-rev0337.csv`
* `cube/nuclear-emergency-bvps-energy-fuel-blackstart-minimum-packet-rev0337.csv`
* `cube/nuclear-emergency-bvps-telecom-lmr-satellite-failover-packet-rev0337.csv`
* `cube/nuclear-emergency-bvps-water-wastewater-erp-warn-packet-rev0337.csv`
* `cube/nuclear-emergency-bvps-transportation-access-debris-bridge-flood-packet-rev0337.csv`
* `cube/nuclear-emergency-bvps-hazmat-industrial-compound-interface-packet-rev0337.csv`
* `cube/nuclear-emergency-bvps-lifeline-dependency-dag-rev0337.csv`
* `cube/nuclear-emergency-bvps-crosssector-restoration-priority-conflict-rev0337.csv`
* `cube/nuclear-emergency-bvps-compound-lifeline-outage-scenario-matrix-rev0337.csv`
* `tools/validate_nuclear_emergency_bvps_lifeline_infra_rev0337.py`
* `field-kits/bvps-rev0337/00-lifeline-infrastructure-runbook.md`

## Public claim gate

Allowed: “A public-context lifeline proof spine was added, and local/anonymized packets are required.”  
Blocked: “BVPS offsite readiness is green,” “energy/water/telecom/transportation lifelines are ready,” “public lifeline guidance closes local readiness,” or “generator/fuel/water/telecom plans prove exercised restoration.”
