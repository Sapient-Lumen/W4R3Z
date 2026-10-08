# Dispatch join: misbind + egress

`misbindguard.py` already catches cross-surface mistakes like using a valid frame, payload, actor, request id, or scope from one context to authorize a different handler.  `dispatchjoin.py` adds the missing joined-boundary check: the egress attached to a handler must be bound to the same handler intent.

rev0029 tests:

- accepted mutable-head handler intent with witness-publish egress;
- rejected upstream misbind guard;
- quarantined scope leak;
- quarantined object/body-digest leak;
- forbidden raw-key egress for witness/useful-refusal/repair-intent handlers;
- egress-budget rejection before dispatch.

This surface exists because final dispatch is where local safety reports most often get accidentally blurred.
