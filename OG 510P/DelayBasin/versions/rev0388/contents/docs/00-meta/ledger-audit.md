# Ledger audit

Generated continuity-ledger inventory. This surface summarizes counts and latest-id alignment; it is not a ledger review court.

| Surface | Items | Latest | Receipt witness | States |
| --- | ---: | --- | --- | --- |
| `FOLLOWTHROUGH-QUEUE.json` | 273 | `FT-0273` | `FT-0273` | deferred:8, expired:99, handed-off:2, queued:164 |
| `ASSUMPTION-LEDGER.json` | 269 | `AS-0270` | `AS-0270` | active:164, discharged:12, retired:93 |
| `OBLIGATION-LEDGER.json` | 266 | `OB-0266` | `OB-0266` | open:163, retired:89, satisfied:14 |
| `APPLICABILITY-LEDGER.json` | 265 | `AP-0265` | `AP-0265` | eligible:109, gated:156 |
| `FOREIGN-PRESSURE-LEDGER.json` | 269 | `FP-0270` | `FP-0270` | imported:269 |
| `DATACUBE-TRANSFER-LEDGER.json` | 276 | `TL-0276` | `TL-0276` | deferred:1, imported:109, rejected:5, supporting-only:161 |
| `RESOLUTION-LEDGER.json` | 273 | `RS-0273` | `RS-0273` | resolved:273 |
| `RETROSPECTIVE-QUEUE.json` | 260 | `RT-0260` | `RT-0260` | captured:15, cooling:152, expired:93 |
| `FIREBREAK-LEDGER.json` | 267 | `FB-0267` | `FB-0267` | quarantined:86, withheld:181 |
| `SELF-SUFFICIENCY-LEDGER.json` | 61 | `SA-0061` | `SA-0061` | guarded-not-scored:12, introduced-not-scored:1, scored-canary:48 |

## Debt pressure

This section is a non-review gate for stale-debt burn-downs: it records state counts and bulk transition groups without adjudicating historical merit.

- `FOLLOWTHROUGH-QUEUE.json` live `queued` count `164` of `273` items.
- `ASSUMPTION-LEDGER.json` live `active` count `164` of `269` items.
- `OBLIGATION-LEDGER.json` live `open` count `163` of `266` items.
- `RETROSPECTIVE-QUEUE.json` live `cooling` count `152` of `260` items.

## Bulk state-transition groups
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0338` count `25`; states retired:25; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0341` count `6`; states retired:6; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0355` count `27`; states retired:27; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0356` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0357` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0358` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0359` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0360` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0361` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0362` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0363` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0364` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0365` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0366` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0367` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0368` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0369` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0370` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0371` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0372` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0373` count `1`; states retired:1; latest-in-group `False`.
- `ASSUMPTION-LEDGER.json` `retirement_revision` `rev0374` count `17`; states retired:17; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0336` count `20`; states expired:20; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0342` count `3`; states expired:3; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0355` count `29`; states expired:29; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0356` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0357` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0358` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0359` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0360` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0363` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0364` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0365` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0366` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0367` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0368` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0369` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0370` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0371` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0372` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0373` count `1`; states expired:1; latest-in-group `False`.
- `FOLLOWTHROUGH-QUEUE.json` `expiry_revision` `rev0374` count `17`; states expired:17; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0338` count `25`; states retired:25; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0355` count `30`; states retired:30; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0356` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0357` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0358` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0359` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0360` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0363` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0364` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0365` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0366` count `2`; states retired:2; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0367` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0368` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0369` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0371` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0372` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0373` count `1`; states retired:1; latest-in-group `False`.
- `OBLIGATION-LEDGER.json` `retirement_revision` `rev0374` count `18`; states retired:18; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0338` count `25`; states expired:25; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0355` count `20`; states expired:20; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0366` count `1`; states expired:1; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0369` count `1`; states expired:1; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0371` count `1`; states expired:1; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0372` count `1`; states expired:1; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0373` count `1`; states expired:1; latest-in-group `False`.
- `RETROSPECTIVE-QUEUE.json` `retirement_revision` `rev0374` count `29`; states expired:29; latest-in-group `False`.
