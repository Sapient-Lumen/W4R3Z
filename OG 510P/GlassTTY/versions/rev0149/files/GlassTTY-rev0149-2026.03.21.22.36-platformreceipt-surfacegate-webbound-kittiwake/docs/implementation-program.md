# Implementation program

This is the recommended implementation order after the rev0122 docs overhaul.

## Program 1 — Adopt the canon
Deliverable:
- top-level docs and canonical design docs adopted in-tree

Why first:
- future work accelerates once the repo stops underspecifying the product

## Program 2 — Lock keys and templates
Deliverable:
- canonical keys, support-record template, release-gate template, support-bundle expectations

Why second:
- it reduces vocabulary drift and makes later records comparable

## Program 3 — Establish support records
Deliverable:
- one support record per official surface

Why third:
- it forces clarity about what “official surface” means operationally

## Program 4 — Lock the shared workflow and state contracts
Deliverable:
- workflow catalog and state contracts tied to current outputs

Why fourth:
- adapter work, evidence work, and agent work all depend on this shared vocabulary

## Program 5 — Backfill Claude support truth
Deliverable:
- one formal Claude support record with named evidence refs and lane scope

Why fifth:
- it turns the current reference adapter into a concrete model rather than a reputation

## Program 6 — Choose and implement the second adapter
Recommended target:
- ChatGPT, unless fresher implementation evidence says another surface is meaningfully easier

Why sixth:
- one additional real adapter is the best proof that the generic core is working

## Program 7 — Unify evidence into support truth
Deliverable:
- support bundles, ledgers, release gates, and support matrix tied together

## Program 8 — Start drift baselines for all official surfaces
Deliverable:
- per-surface baselines and comparison artifacts

## Program 9 — Layer in agent execution
Deliverable:
- policy-bound action plans and execution reports on top of the visible bridge

Use `docs/implementation-epics.md` for the more granular breakdown.
