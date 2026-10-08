# Autonomy ladder

This file explains how GlassTTY should widen agent behavior without jumping from manual control to opaque autonomy.

## Level 0 — Manual operator
- human reads state directly
- human writes and submits directly
- no agent planning loop

Expected artifacts:
- optional state snapshots
- optional operator-attempt record

## Level 1 — Assisted operator
- an LLM may summarize state, suggest actions, or draft writes
- operator performs the final write/submit action
- no unattended looping

Expected artifacts:
- action suggestion
- action outcome when executed

## Level 2 — Approval-required single action
- an LLM may prepare one action plan
- operator approves before execution
- action executes once, then stops

Expected artifacts:
- action plan
- approval record
- action outcome
- relevant evidence refs

## Level 3 — Approval-required short sequence
- an LLM may prepare a bounded multi-step sequence such as read → write → submit → readback
- operator approves the sequence or each risky step
- execution must stop after the defined sequence or on uncertainty

Expected artifacts:
- bounded execution plan
- approval record
- per-step outcomes
- execution report

## Level 4 — Bounded autonomous lane
- the agent may perform a narrow loop without per-step approval inside an explicitly allowed workflow and lane
- examples might include support-capture, repeated state reads, or drift-comparison preparation
- risky writes/submits remain restricted by policy

Expected artifacts:
- policy record or resolved policy mode
- execution report
- evidence refs
- stop-condition reason on exit

## Level 5 — Broad autonomous operation
This level should be treated as aspirational and not implied by current docs. It would require much stronger policy, isolation, and artifact discipline than the repo currently has.

## Hard rules across all levels

1. Every action-capable level above 1 should leave a machine-readable outcome.
2. Every multi-step level should have explicit stop conditions.
3. Unknown state, receiver ambiguity, or missing support truth should bias toward stopping or downgrading.
4. The operator should be able to force a downgrade to a lower level at any time.
5. Support truth should never be inferred from autonomous optimism; it must still be backed by evidence.
