# Specimen flow 01 — browser detour with callback proof

This is a **specimen**, not a frozen architecture. It exists to stress the emerging Harbor vocabulary against a real class of crossings.

## Purpose

Test whether Harbor can represent a browser-based detour and return without confusing these layers:
- launch admission;
- route choice;
- callback arrival;
- callback-to-request binding proof;
- durable account or trust consequence.

## Candidate objects

1. **request envelope**
   - who asked;
   - requested route class;
   - requested return capability, if any;
   - cancellation / timeout posture.

2. **route set**
   - browser detour;
   - verified-app-link hint;
   - local app / chooser path;
   - denied / blocked.

3. **admission choice**
   - which route class was admitted;
   - what Harbor is willing to say about user mediation;
   - what Harbor declines to claim.

4. **detour lease**
   - issued_at;
   - expires_at or expiry posture;
   - expected callback proof class;
   - whether provider-local browser state was involved.

5. **callback proof note**
   - no callback;
   - callback arrived but unbound;
   - callback bindable to detour lease;
   - callback bindable plus provider response payload present.

6. **aftermath receipt**
   - denied;
   - admitted-no-return;
   - returned-weakly;
   - returned-with-bindable-proof;
   - materialized;
   - grant-issued.

## What this specimen refuses to decide yet

- whether detour lease becomes a general Harbor family or remains a narrower auth/callback object;
- whether callback proof note lives inside the aftermath receipt or remains a sibling object;
- whether verified associations are hints on the route set, separate evidence objects, or something else entirely.

## Why this specimen matters

If Harbor cannot survive this flow without collapsing into one giant “exchange result,” the cube is not ready for a broader family map.
