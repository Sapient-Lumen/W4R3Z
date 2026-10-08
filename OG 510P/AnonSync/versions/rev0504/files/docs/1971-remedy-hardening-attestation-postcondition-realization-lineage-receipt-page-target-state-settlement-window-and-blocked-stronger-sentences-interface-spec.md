# Remedy-hardening-attestation postcondition-realization lineage receipt page — target state, settlement window, and blocked stronger sentences

## Purpose

This page is the durable one-receipt summary for postcondition realization after executable mandate review.
It lets a later operator read one artifact and know exactly whether the mandate merely routed, produced an observable outcome for a named slice, entered a provisional settlement window, hit contradiction or rollback, or truly realized the target state for the governed slice while broader stronger language stayed blocked.

## Receipt fields

- receipt identifier
- postcondition-realization identifier
- source executable-mandate receipt identifier
- governing mandate sentence
- target postcondition summary
- beneficiary-slice summary
- governed object-set summary
- observation quorum summary
- current contrary-observation summary
- settlement-window summary
- rollback or survivor-hazard summary
- current postcondition-realization class
- highest honest realization sentence
- blocked stronger sentence
- evidence references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest postcondition-realization sentence**
- **Blocked stronger sentence**

## Required sections

1. **What state the mandate was supposed to make true**
2. **Which witnesses show that state now, and for whom**
3. **Which witnesses are still route-only, placeholder-only, or missing**
4. **Whether contradiction, rollback, or settlement-window limits still matter**
5. **Why the next stronger realization sentence is blocked**

## Hard rules

The receipt must never let:

- `the mandate executed` impersonate `the target state became true`
- `the folder is visible` impersonate `the beneficiary has usable bytes or rights`
- `one observed slice` impersonate `all governed slices realized`
- `one favorable observation` impersonate `settled outcome`
- `temporary realization` impersonate `broader stronger realization complete`
