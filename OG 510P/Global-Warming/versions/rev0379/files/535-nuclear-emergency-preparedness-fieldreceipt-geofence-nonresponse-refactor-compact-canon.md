# 535 — Nuclear Emergency Preparedness Field Receipt, Geofence Edge, and Nonresponse Triage Refactor — Compact Canon

## Purpose

rev0328 attacks a narrower but dangerous failure mode in the June 2026 Beaver Valley emergency-preparedness path: an alert can be authorized, logged, archived, and discussed publicly while still not being demonstrated as received by the right people, in the right geography, in the right language, with the right protective action, at the right time.

The new rule is:

**Originator proof plus CAP proof plus archive proof is not field-receipt proof.**

Field receipt, geofence edge behavior, nonreceipt triage, accessibility/language receipt, and privacy-safe recipient evidence now become separate evidence gates. Public archives, IPAWS ACKs, WEA screenshots, EAS monitor logs, public meeting statements, public AAR paragraphs, and receiver anecdotes can corroborate, contradict, reopen, cap, or route evidence. They cannot auto-close local emergency-readiness evidence.

## Substantive change

rev0328 adds a field-receipt probe grid, geofence/target-polygon minimum packet, nonreceipt triage state machine, accessibility/language receipt proof, recipient privacy redaction rules, delivery-chain reconciliation, critical cutsets, workorders, validator fixtures, and a scoped SQLite query surface.

The focus is practical:

- prove that target polygons, CAP area blocks, WEA/EAS/SNB/county alert pathways, and recipient evidence are reconciled;
- sample inside-target, edge-target, just-outside-target, low-signal, rural, dense, school, LTC, hospital, AFN, producer, multilingual, and public-facility strata;
- treat no-hit/no-receipt/late-receipt as triage inputs rather than proof of failure or proof of success;
- protect recipient privacy by replacing precise locations, phone identifiers, and medical/AFN details with redacted surrogates;
- keep the June 2026 public meeting and final AAR/IP clock from becoming a shortcut around field evidence.

## Active query route

`alert authority -> CAP/PAD/PAR lineage -> delivery ladder -> field receipt probe grid -> nonreceipt triage -> geofence/accessibility proof -> adjudication -> CAP/retest/verifier -> public claim gate`

The old universal nuclear crossproduct tables remain compatibility artifacts only. Real-site emergency-readiness queries should not route through them.

## Claim scope

No real Beaver Valley readiness or unreadiness claim is made. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only. rev0328 improves last-mile receipt proof and overclaim prevention; it does not say Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, any alerting authority, or any facility is ready, unready, green, failed, passed, certified, safe, sufficient, or closed.
