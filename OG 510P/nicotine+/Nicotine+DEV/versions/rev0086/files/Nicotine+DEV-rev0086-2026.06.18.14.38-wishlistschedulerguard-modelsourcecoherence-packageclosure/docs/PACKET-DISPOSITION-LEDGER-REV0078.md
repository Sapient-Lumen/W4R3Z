# Packet disposition ledger — rev0078

Machine-readable authority is `data/current_packet_dispositions.json`. This document is navigation, not an independent status source.

| Packet | Current status | Selected research artifact |
|---|---|---|
| U-123 | closed research disposition | retained prototype; not contribution material |
| PB-01A / U-168 | open protocol-hardening research | none |
| PB-01B / U-176 | retired as a defect on current evidence | none |
| SEARCH-RESP-01A / U-163A | open defense-in-depth research | none |
| SEARCH-RESP-01B / U-163B | open request-epoch design research | none |
| SEARCH-AGAIN-SELF-01 | closed low-severity correctness disposition | one-line research patch |
| SEARCH-AGAIN-EPOCH-01 | open public design research | none |

## rev0078 addition

`SEARCH-AGAIN-EPOCH-01` records that current Search Again is same-token Retry/Merge behavior. A replacement refresh requires a logical/wire identity split and a network lifecycle contract. Public issue history already discusses removal and a new token, so rev0078 makes no novelty claim for that broad requirement.

The packet remains unselected for two separate reasons:

```text
ordinary queue calls can be silently rejected while disabled
accepted queued work can be cleared before processing on disconnect
```

The executable artifacts are contracts and counterexamples, not contribution-ready code.

## Validation

```text
schema/contract checks: 187/187 pass
snapshot equality:      pass
packet set exact:       pass
selected paths present: pass
```

Historical filenames such as `PRODUCTION-READY` do not override this ledger.
