# Reviewed-draft basis guard, stale attempt, and reissue interface spec

The archive already has reviewed drafts, mutation gates, approval reapproval, shareable-head registers, carryforward verdicts, and follow-through coverage.
What it still lacked was one durable public answer to a narrower practical question:

> once an operator has already reviewed a draft, packet, notice, queue entry, or apply-worthy action against one explicit basis, what keeps a later click from silently rebinding that reviewed intent onto a newer basis, or from silently disappearing when the basis has already drifted?

This document answers that question.
It exists so AnonSync does not recreate a common failure mode from other products and workflows, where a reviewed action remains visible as if it were still current even after the governing head, approval basis, evidence slice, policy version, or current shareable artifact has changed.

## Why this needs its own spec

The draft-object model says whether a draft exists.
The approval-memory model says whether trust may still be reused.
The shareable-head and carryforward models say which artifact is current for disclosure and how one older artifact compares to a newer one.
Those are all necessary, but they still leave one dangerous operational seam:

- a reviewed draft can stay on screen while the subject it was reviewed against already moved
- a queued or deferred issue/apply attempt can target one head while the family now has another
- a later basis change can make the old click either too strong or simply not comparable anymore
- products often fail here in two opposite ways: they silently rebind the old intent onto the new world, or they silently drop the stale attempt without one durable repair surface

AnonSync should do neither.
A reviewed action must either still match its reviewed basis, or it must surface `stale-attempt / reissue-needed` truth explicitly.

## Comparative motivation

The comparison archives made this seam unusually clear:

- **pyCausalWeave** repeatedly sharpens the law that approval, merge request, and queue-entry truths are scoped to the head they were reviewed against, with explicit reissue instead of sticky inheritance
- **Goldenrule** keeps head registers and compact publication contracts explicit enough that later public-facing actions can point to a stable current head instead of ambient latestness
- **EvidenceVault** reinforces that candidate working material, queued/publication intent, and the frozen public surface are different objects whose relations should be explicit rather than folkloric

These are not implementation dependencies.
They are pressure toward one reusable product law: a reviewed action should preserve its expected basis until it is either executed on that basis, explicitly reissued on a newer one, or cancelled.

## Core rule

Every non-trivial reviewed action that can outlive one immediate click should carry one explicit **basis guard**.

That guard must name the exact basis rows the action expects to remain current at execution time.
Examples include:

- current lineage or plan head
- current approval basis / reapproval state
- current frozen shareable head
- current evidence slice or incident snapshot
- current policy version or effective-policy digest
- current runtime/seat/owner snapshot when the action's meaning depends on it

If those rows still match, the action may execute on the reviewed basis.
If one or more rows no longer match, the product must surface `stale-attempt`, `reissue-needed`, `broader-reopen-required`, or `cancelled` truth explicitly.
It may not silently apply the action to the newer basis, and it may not silently erase the now-stale attempt.

## Fixed review order

Every guarded reviewed-action surface should preserve this order:

1. **Reviewed action and intended effect**
2. **Expected basis rows**
3. **Current basis comparison**
4. **Execution posture now**
5. **Reissue or reopen path**
6. **Receipt promise**

### 1) Reviewed action and intended effect

This section should show:

- draft / review / queue-entry / packet / notice / apply object ID
- action family
- intended effect if it executed successfully
- what current family or subject it belongs to
- whether the action is issue, apply, queue, disclose, refresh, rotate, or another bounded effect

The operator must be able to answer: **what reviewed act am I trying to carry through right now?**

### 2) Expected basis rows

This section should show one row per basis dependency:

- basis kind
- expected basis reference
- what the operator reviewed at review time
- why that basis matters to the meaning of this action
- whether the dependency is strict or admits reviewed equivalence

The operator must be able to answer: **what did this action expect to still be true when I reviewed it?**

### 3) Current basis comparison

This section should show, for each expected row:

- current basis reference
- comparison verdict (`matches`, `reviewed-equivalent`, `stale`, `missing`, `ambiguous`, `non-comparable`)
- changed-since-review summary
- whether the difference blocks execution or only forces a narrower label

The operator must be able to answer: **does the world this action was reviewed against still exist, and if not, how did it drift?**

### 4) Execution posture now

This section should show:

- `ready-on-reviewed-basis`, `ready-on-reviewed-equivalence`, `stale-attempt`, `reissue-needed`, `broader-reopen-required`, `blocked`, or `cancelled`
- whether an attempted click was already refused against a stale basis
- what claim ceiling applies if execution is allowed
- whether current approval or mutation authority is still enough even if the basis matches

The operator must be able to answer: **can this exact reviewed act still happen honestly right now?**

### 5) Reissue or reopen path

This section should show:

- minimal repair path (`refresh-guard`, `compare-and-reissue`, `open-broader-review`, `cancel`)
- whether earlier prose/comments/packet fields can be carried forward or only copied as suggestions
- whether the stale attempt is safe to keep visible for audit after reissue
- whether the next action is same-family reissue or truly a new review family

The operator must be able to answer: **what is the honest next step now that the original basis no longer cleanly binds?**
For recipient-specific actions, this basis guard is necessary but not sufficient; current target drift is handled separately by the reviewed recipient-target guard.

### 6) Receipt promise

This section should show:

- whether execution will emit an `applied-on-reviewed-basis` receipt or `applied-after-reissue` receipt
- whether a stale click already emitted a `stale-attempt` receipt
- which rows later prove exact basis match, mismatch, or explicit reissue

The operator must be able to answer: **what later evidence will prove that the product did not silently inherit or silently drop my reviewed intent?**

## Public objects

### Reviewed-action basis guard

A first-class object describing the expected-versus-current basis for one reviewed action.

Fields:

- `reviewed_action_basis_guard_id`
- `action_ref`
- `action_family`
- `expected_basis_rows[]`
- `current_basis_rows[]`
- `guard_verdict` (`ready-on-reviewed-basis`, `ready-on-reviewed-equivalence`, `stale-attempt`, `reissue-needed`, `broader-reopen-required`, `blocked`, `cancelled`)
- `current_authority_posture`
- `last_computed_at`
- `next_honest_actions[]`
- `receipt_promise`

### Basis guard row

A compact row for one specific dependency the action expected to remain current.

Fields:

- `basis_guard_row_id`
- `basis_kind` (`lineage-head`, `approval-basis`, `shareable-head`, `policy-version`, `evidence-slice`, `runtime-snapshot`, `startup-owner-snapshot`, `other`)
- `expected_ref`
- `current_ref` nullable
- `comparison_verdict` (`matches`, `reviewed-equivalent`, `stale`, `missing`, `ambiguous`, `non-comparable`)
- `change_summary`
- `blocks_execution`
- `reissue_hint`

### Stale-attempt receipt

A durable receipt proving that one attempted execute/issue/apply action was refused or downgraded because its reviewed basis no longer matched.

Fields:

- `stale_attempt_receipt_id`
- `action_ref`
- `attempted_transition` (`issue`, `apply`, `enqueue`, `disclose`, `refresh-notice`, `other`)
- `expected_basis_rows[]`
- `observed_current_basis_rows[]`
- `stale_reason_refs[]`
- `repair_path` (`refresh-guard`, `reissue`, `broader-reopen`, `cancel`)
- `recorded_at`

### Reissue receipt

A durable receipt proving that a later reviewed action explicitly replaced an older stale one on a newer basis.

Fields:

- `reissue_receipt_id`
- `superseded_action_ref`
- `new_action_ref`
- `carried_forward_fields[]`
- `new_basis_rows[]`
- `why_reissue_was_required`
- `recorded_at`

## Rules

1. **Reviewed intent is basis-scoped, not ambient.**  
   A reviewed draft or queue-worthy action is never approval for whatever later became current.

2. **Match or explicit equivalence only.**  
   Execution may proceed only when the expected basis still matches, or when a separately reviewed equivalence receipt explicitly says that later drift does not change the action's meaning.

3. **Stale attempts must stay visible.**  
   A refused click against stale basis should emit one durable stale-attempt receipt rather than disappearing into a toast or silent no-op.

4. **Reissue is explicit.**  
   Carrying forward prose, recipients, or suggested fields into a newer action may be convenient, but the product must still create a new action object or explicit reissue receipt on the newer basis.

5. **Authority and basis are different guards.**  
   An action may fail because current authority is insufficient, because basis drifted, or both. One failure must not hide the other.

6. **Queued or deferred actions need the same protection as immediate ones.**  
   Scheduling, batching, or later follow-through does not loosen basis truth.

7. **Current head is not enough when more than one basis row matters.**  
   Some actions depend simultaneously on current artifact head, approval basis, and evidence slice. Clients must preserve the row set rather than compressing everything into one `latest` badge.

8. **Cancellation should not counterfeit execution.**  
   If a stale action is abandoned rather than reissued, the archive should say so explicitly instead of letting the old draft linger as apparently current.

## CLI contract

Minimal commands:

```text
anonsync reviewed-action guard show dra_01J...
anonsync reviewed-action guard refresh dra_01J...
anonsync reviewed-action reissue dra_01J... --carry-forward recipients,summary --plan
anonsync reviewed-action stale-attempt show sar_01J...
anonsync reviewed-action reissue-receipt show rir_01J...
```

A stale click should read like this:

```text
$ anonsync reviewed-action guard show pktrev_01K...
Reviewed action basis guard
--------------------------
1. Reviewed action and intended effect
   Action: escalation-packet issue
   Family: packet-family fam_01J...
   Intended effect: issue current reviewed packet to named recipient class

2. Expected basis rows
   shareable-head    pkt_01K4...
   approval-basis    apb_01K7...

3. Current basis comparison
   shareable-head    current pkt_01K5...   stale
   approval-basis    current apb_01K8...   stale (rereview needed)

4. Execution posture now
   Verdict: reissue-needed
   Attempting issue now would create stale-attempt receipt, not disclosure

5. Reissue or reopen path
   Next honest action: compare current head and reissue on current basis

6. Receipt promise
   stale-attempt -> sar_01K...
   reissue receipt after fresh review -> rir_01K...
```

## Good enough test

This surface is good enough when a cautious operator can answer all of the following without reverse-engineering lineage manually:

- what this draft/review/queue-worthy action was reviewed to do
- which exact basis rows it expected to remain current
- which rows still match and which ones drifted
- whether the product refused a stale click explicitly instead of silently rebinding it
- what the minimal honest repair path is
- what later receipt proves explicit reissue rather than sticky inheritance
