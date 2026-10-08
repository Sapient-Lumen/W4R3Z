# Execution-lineage receipt page — mandate scope, actor kind, freshness, and blocked stronger sentences

## Purpose

This page is the compact carry-forward receipt for what execution sentence was actually earned for a specific act version.
It exists so later operators can answer `who was truly allowed to carry this out, how, and what stronger autonomous sentence is still blocked?` without reopening the whole case.

## Mandatory receipt fields

- source act identifier
- source version identifier
- effect lane covered by this receipt
- highest execution-mandate rung earned
- actor kind that made the rung count
- supervision posture
- freshness posture
- highest honest execution sentence earned
- strongest blocked stronger execution sentence
- next event that could strengthen or weaken the receipt

## Required compact verdicts

At minimum the receipt must be able to state verdicts like:

- `assented; execution mandate absent`
- `delegate may prepare; irreversible commit still human-only`
- `linked-device route available; device-only execution blocked`
- `supervised agent may execute within narrow lane; autopilot still blocked`
- `standing mandate present; fresh execute-now confirmation still required`
- `execution completed; stronger autonomous sentence blocked`

## Required comparisons

The receipt must keep these comparisons explicit:

- `assented` vs `execution-mandated`
- `principal` vs `delegate`
- `delegate` vs `agent`
- `agent` vs `autopilot`
- `standing mandate` vs `fresh execute-now confirmation`

## Failure modes the receipt must prevent

- later operators assuming that assent itself meant the act could now be executed
- later operators assuming that owner status or linked-device presence meant execution authority
- losing the exact actor kind in which execution counted
- losing the reason a stronger autonomous or irreversible-execution sentence stayed blocked
- losing whether freshness and supervision requirements were actually satisfied

## Stronger-sentence guard

This receipt may say `delegate-authorized for preparatory routing; supervised agent used for transport; final irreversible commit remained human-only because fresh execute-now confirmation and principal execution were both required`.
It may not say `the system was cleared to execute automatically` unless that stronger sentence was actually earned.
