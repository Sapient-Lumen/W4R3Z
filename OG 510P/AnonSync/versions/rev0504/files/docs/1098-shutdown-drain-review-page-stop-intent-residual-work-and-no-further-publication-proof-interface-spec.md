# Shutdown drain review page: stop intent, residual work, and no-further-publication proof

This page exists so `stop requested` does not overclaim `nothing else will happen`.
Stopping a sync runtime can still leave draining work, late index commits, or uncertainty about whether further publication is already impossible.

## Operator question

> I asked this runtime to stop. What work is still draining, what evidence do we have that publication has ceased, and what stronger sentence is still blocked?

## When this page must appear

Render whenever:

- the operator requests runtime stop or service stop
- the product cannot yet prove drain completion
- a stop attempt was interrupted by service manager, OS policy, or projection loss
- later evidence suggests bytes or metadata may still have been published after stop intent

## Fixed review order

1. **Stop request and scope**
2. **Residual work ledger**
3. **Publication-proof ladder**
4. **Interruption / failure causes**
5. **Approval / escalation actions**

## 1) Stop request and scope

Show:

- receipt / request id
- request time
- requester identity or automation source
- requested scope: `projection`, `runtime`, `service`, `future-boot`, `unknown`
- whether the request was accepted, rejected, or only partially applied

The operator must be able to answer: **what exact stop was requested?**

## 2) Residual work ledger

List any still-relevant residuals, such as:

- hashing / indexing still draining
- transfer finalization still pending
- archive / history / metadata flush still pending
- service manager still reporting alive
- unknown because projection disappeared before proof

For each residual, show:

- class
- current status: `active`, `quiescing`, `cleared`, `unknown`
- freshness of the observation
- whether it can still result in externally visible change

The operator must be able to answer: **what work may still matter after stop intent?**

## 3) Publication-proof ladder

Show one explicit strongest-safe rung:

- `stop requested only`
- `runtime no longer accepts new work`
- `drain appears complete`
- `no further publication observed`
- `stable stop proven across observation window`
- `unknown`

Do not skip rungs.
If a stronger rung is blocked, show why.

The operator must be able to answer: **what is the strongest honest sentence available now?**

## 4) Interruption / failure causes

Show any blocking or weakening causes:

- projection vanished before proof
- service manager restarted runtime
- startup hook still enabled
- task killer / OS background policy interference
- missing permissions to observe actual stop state
- platform does not support background so scope was weaker/stronger than expected

The operator must be able to answer: **why is the proof weaker than I expected?**

## 5) Approval / escalation actions

Offer only actions that match the proof ladder:

- `Accept weaker proof and close review`
- `Wait for drain completion`
- `Stop service manager too`
- `Disable future startup`
- `Open restart provenance`
- `Escalate to hard stop repair`

## What this page must never imply

It must never imply that these are the same:

- stop request and drain completion
- drain completion and no-further-publication proof
- one clean observation and stable stop across time
- runtime stop and service-manager silence

## Receipt / audit consequence

The resulting receipt should preserve request scope, residual classes observed, strongest-safe proof rung reached, blocked stronger sentence, and any re-entry posture that still weakens the stop claim.
