# 526 — Nuclear Emergency Preparedness Ingestion, AFN, Producer, and Public-Context Firebreak Refactor — Compact Canon

Revision: `rev0319`  
Created: `2026-06-04T12:49:00-04:00`  
Base revision: `rev0318`

## Why this revision exists

Rev0318 hardened the ETE / route / worker firebreak, but a serious offsite-readiness failure can still hide in a different place: **the household, access-and-functional-needs, farm/animal, food, milk, water, and producer side of the emergency**.

A public evacuation route table or public ETE number does not tell us whether the people without cars were actually identified, whether wheelchair vans and ambulances can arrive, whether farmers and processors can hold food from commerce, whether milk/water/animal-feed sampling has a chain of custody, whether animal owners receive usable instructions, or whether a cross-border county packet exists and was exercised.

This revision therefore moves the cube from generic ingestion-pathway placeholders to a **site-specific Beaver Valley household/producer proof spine**. It keeps the firebreak: public cards, public brochures, public REP plans, and public agriculture guidance create evidence demands, but they do not close local readiness rows.

## Main correction

The cube now has a first-class distinction between:

1. **public household/producer context**, such as annual access-and-functional-needs cards, farmer information, public 10-mile/50-mile guidance, public agriculture procedures, and county/public plan tables; and
2. **local closure evidence**, such as current rosters, de-duplicated transportation assignments, vehicle/vendor agreements, accessible alert test logs, field sampling chain-of-custody, lab capacity, food/milk/water interdiction decisions, exercise observations, corrective-action closure, and independent verification.

The material rule is:

> Public AFN or farmer information can discover demand and route packets. It cannot prove readiness without local roster, assignment, drill, sampling, CAP/retest, verifier, and redaction evidence.

## New operational surfaces

- `cube/nuclear-emergency-bvps-afn-card-to-transport-packet-rev0319.csv`
- `cube/nuclear-emergency-bvps-farmer-food-animal-ingestion-packet-rev0319.csv`
- `cube/nuclear-emergency-bvps-ingestion-sampling-procedure-gap-rev0319.csv`
- `cube/nuclear-emergency-bvps-wv-plan-availability-blocker-rev0319.csv`
- `cube/nuclear-emergency-bvps-household-producer-critical-cutset-rev0319.csv`
- `cube/nuclear-emergency-bvps-household-producer-firebreak-test-result-rev0319.csv`
- `cube/nuclear-emergency-bvps-afn-farmer-privacy-redaction-rule-rev0319.csv`
- `cube/nuclear-emergency-bvps-open-action-workorders-rev0319.csv`
- `cube/datacube-rev0319-emergency.sqlite`

## What is now blocked

The real-public Beaver Valley overlay remains `REAL_BVPS_PUBLIC_ONLY`. These claims remain blocked unless the required local/anonymized packets are imported:

- access-and-functional-needs transport readiness;
- school, medical, wheelchair, ambulance, and carless-household movement readiness;
- farm/animal/food/milk/water ingestion-pathway readiness;
- current Hancock/WV offsite readiness;
- route-capacity readiness from public ETE/public route tables;
- EN58200 EOF closure;
- 2026 exercise pass/closure.

## Specific refactor

The old generic table `cube/nuclear-ingestion-pathway-food-water-controls.csv` remains as a broad template. This revision adds site-specific BVPS proof surfaces and query views, then routes public context through:

`public AFN/farmer/ingestion source -> evidence demand -> packet import -> exercise/sampling/CAP/retest -> independent verification -> public claim gate`

## No real-site readiness claim

This revision does not assert that Beaver Valley, Beaver County, Columbiana County, Hancock County, Pennsylvania, Ohio, or West Virginia are ready or unready. It asserts only that public sources expose open evidence demands and that the cube now rejects public-context-to-local-closure leakage.
