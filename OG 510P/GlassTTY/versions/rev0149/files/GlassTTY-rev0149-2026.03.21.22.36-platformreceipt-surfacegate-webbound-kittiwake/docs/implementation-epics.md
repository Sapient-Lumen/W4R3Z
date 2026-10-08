# Implementation epics

This file breaks the program into implementer-friendly epics with outputs and acceptance ideas.

## Epic 1 — Canon adoption
Outputs:
- top-level docs replaced
- canonical design docs adopted
- repo map updated

Acceptance idea:
- a new reader can identify product, support model, and next work in under one read-through

## Epic 2 — Vocabulary and contracts
Outputs:
- canon keys stabilized
- workflow catalog complete
- state contracts complete
- action/outcome semantics stable enough to implement against

Acceptance idea:
- no new adapter doc invents its own incompatible names for shared workflows or state families

## Epic 3 — Support truth seeding
Outputs:
- support record template
- six seeded support records
- support matrix summary rules

Acceptance idea:
- every official surface has a current record, even if its status is only investigated

## Epic 4 — Claude backfill
Outputs:
- one dated Claude support record
- named evidence refs
- first release-gate example

Acceptance idea:
- the repo can show how support truth is supposed to work using a real existing adapter

## Epic 5 — Second adapter implementation
Outputs:
- chosen target recorded in decisions
- first non-Claude adapter effort started
- first support bundle for the second surface

Acceptance idea:
- one non-Claude surface reaches experimental support for at least part of the core workflow set on one lane

## Epic 6 — Drift and evidence program
Outputs:
- baseline plans per surface
- drift comparison expectations
- support-record update loop after drift

Acceptance idea:
- a changed surface can produce a meaningful comparison bundle and next action

## Epic 7 — Agent policy surfaces
Outputs:
- policy schema
- approval model
- execution report shape
- stop-condition list

Acceptance idea:
- the repo can describe safe bounded local-LLM control before runtime autonomy is widened

## Epic 8 — Release discipline
Outputs:
- gate checklist
- promotion/demotion rules
- support-truth update discipline

Acceptance idea:
- stronger support claims are accompanied by current evidence, not narrative optimism
