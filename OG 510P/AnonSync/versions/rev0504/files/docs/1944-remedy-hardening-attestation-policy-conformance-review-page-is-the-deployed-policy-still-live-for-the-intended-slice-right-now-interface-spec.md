# Remedy-hardening-attestation policy-conformance review page — is the deployed policy still live for the intended slice right now?

## Purpose

This page is the operator-facing review that answers the practical conformance question after rollout: does the product know enough to say the policy still governs the named slice now, or has drift, stale evidence, or world change collapsed that sentence?

## Primary review prompts

The review must answer these prompts in order:

1. **Which rollout receipt is the starting basis for this current conformance review?**
2. **Which named slice is being claimed as still governed right now?**
3. **What fresh witness proves present conformance rather than historical deployment only?**
4. **What changed since the last trusted witness: overrides, new arrivals, reconnects, service moves, or principal changes?**
5. **Is drift only suspected, or is breach now confirmed?**
6. **What is the strongest sentence the product may still say right now?**

## Review sections

### 1. Rollout basis board

Show:

- source rollout receipt and class
- last known conformance class
- why a present-time conformance review is allowed or required now

### 2. Fresh witness board

Show:

- newest conformance witnesses
- witness freshness class
- covered populations
- uncovered populations
- recertification deadline

### 3. Change-since-last-proof board

Show:

- newly added objects or members
- manual overrides since the prior receipt
- service-user, principal, or world changes
- reconnects or path forks
- whether each change is harmless, drift-suspect, or breach-relevant

### 4. Drift and containment board

Show:

- suspected drift items
- confirmed breach items
- containment state
- repair owner and due time
- whether stronger still-governing language is blocked now

### 5. Conformance sentence chooser

The review must output one and only one primary sentence class such as:

- deployed policy, current conformance unverified
- current conformance evidenced for named slice only
- inherited coverage incomplete
- recertification overdue, stronger sentence blocked
- suspected drift under investigation
- confirmed breach with containment active
- confirmed breach without adequate containment
- repair applied, recertification pending
- conformance restored after fresh recertification
- policy narrowed, paused, or retired

## Hard rules

The review must never let an operator hide:

- rollout history behind present conformance
- one narrow fresh example behind whole-slice proof
- `new folders follow it` behind `older covered population still conforms`
- a storage or service-world fork behind `same deployment still governs`
- containment effort behind `breach resolved`
