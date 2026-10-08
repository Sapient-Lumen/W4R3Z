# Recovery rung page: safest next step, proof, and escalation boundary interface spec

## Purpose

Current sync products too often jump from warning text straight to folklore.
This document defines the interface contract for one first-class **Recovery rung** page.

## Core rule

Any non-trivial warning family must expose one least-destructive ladder that keeps these distinct:

1. wait and observe
2. inspect affected scope
3. local same-lineage repair
4. broader recreate-or-readd repair
5. off-product or escalated intervention

The page must say what proof is required before climbing to a broader rung.

## Public object

### Recovery rung page

Suggested fields:

- `recovery_rung_page_id`
- `warning_ref`
- `current_rung` (`observe`, `inspect`, `local-repair`, `same-lineage-rebind`, `recreate-successor`, `off-product-escalation`)
- `recommended_rung`
- `rung_rows[]`
- `proof_requirements[]`
- `skip_risk_rows[]`
- `stop_conditions[]`
- `receipt_promise`
- `generated_at`

### Rung row

Suggested fields:

- `rung_row_id`
- `rung`
- `action_summary`
- `destructiveness` (`none`, `low`, `moderate`, `high`, `epoch-breaking`)
- `preserves_continuity` (`yes`, `maybe`, `no`, `unknown`)
- `requires_stop_or_quiesce` bool
- `required_proof_refs[]`
- `disqualifier_refs[]`
- `success_readback_ref`

## Fixed page order

1. **Recommended rung now**
   - safest next step
   - why broader steps are not yet justified or are already required

2. **Proof before escalation**
   - what evidence is still missing
   - what would justify moving from inspect to repair, or from repair to recreate

3. **Rung ladder**
   - each candidate rung in order
   - continuity posture
   - stop / restart / quiesce requirements
   - strongest cost

4. **What acknowledgement is *not***
   - hiding the warning
   - accepting risk
   - disabling future warning delivery
   - none of these may impersonate repair

5. **Receipt and follow-on verification**
   - what receipt will exist after this rung
   - what verification page reopens automatically

## Compact row contract

A dense recovery row should preserve these labels in this order:

- `Rung`
- `Action`
- `Continuity`
- `Cost`
- `Needs proof`

Example:

```text
same-lineage-rebind   point to recovered path   maybe preserved   low   recovered path must still match known subject lineage
```

## Anti-goals

- no restart-first superstition when inspect-first is enough
- no re-add-first ritual when same-lineage repair is still plausible
- no warning dismissal presented as resolution
- no destructive rung offered without explicit continuity language

## Acceptance test

This page is good enough when a cautious operator can answer:

- what safest rung is recommended right now
- what proof justifies escalating to the next rung
- whether the current rung preserves continuity or recreates successor state
- what had to stop first
- what receipt and verification will follow
