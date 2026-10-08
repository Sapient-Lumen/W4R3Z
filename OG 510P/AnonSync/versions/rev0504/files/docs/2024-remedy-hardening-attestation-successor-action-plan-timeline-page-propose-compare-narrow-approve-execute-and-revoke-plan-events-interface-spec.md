# Remedy-hardening-attestation successor action-plan timeline page — propose, compare, narrow, approve, execute, and revoke plan events

## Purpose

This page is the time-ordered event view for how a named successor-world action plan moved from authorized action to a proportionate chosen actuator, execution, narrowing, or downgrade.
It exists so the product can separate `action may happen`, `candidate lane proposed`, `narrower alternative found`, `broader lane tolerated`, `execution completed`, and `plan later judged too broad`.

## Required event types

The timeline must preserve at least these event types:

- action authorization imported
- required outcome recorded
- beneficiary slice fixed
- candidate actuator proposed
- narrower actuator discovered
- narrower actuator rejected with reason
- broader actuator challenged as excessive
- emergency broader lane invoked
- expiry or use-budget attached
- chosen actuator approved
- plan executed
- post-execution spillover discovered
- plan narrowed after execution
- broader standing plan refused
- plan verdict downgraded after contradiction

## Mandatory timeline questions

The page must answer in order:

1. **When was the action first eligible to execute?**
2. **When was the minimum required outcome fixed?**
3. **When were candidate actuators compared?**
4. **When, if ever, was a narrower alternative rejected and why?**
5. **Was the chosen actuator accepted as necessary, acceptable, emergency-only, or unresolved?**
6. **When did execution occur relative to that proportionality verdict?**
7. **When, if ever, was the plan later narrowed, contradicted, or judged broader than justified?**

## Event rendering rules

- Every event must show whether it narrows, broadens, or preserves plan legitimacy.
- Every event must show whether it affects the named action only or implies a broader reusable planning precedent.
- Every event must show whether it increases or decreases blast radius, persistence, or forwardability.
- Downgrade events must remain visible even after successful execution.

## Hard rules

The timeline must never let:

- an action-authorization event impersonate a least-harm-plan verdict
- a chosen actuator event erase earlier narrower alternatives
- emergency tolerance erase the need for later narrowing
- execution success erase evidence that a broader lane was chosen for convenience
- one proportionate plan silently authorize future broad actuators by analogy
