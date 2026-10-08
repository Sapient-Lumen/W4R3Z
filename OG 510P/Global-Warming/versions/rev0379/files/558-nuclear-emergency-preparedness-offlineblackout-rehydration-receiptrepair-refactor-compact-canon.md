# 558 — Nuclear emergency preparedness: offline blackout capture, rehydration, and receipt repair refactor

## Purpose

This revision closes a practical event-day gap left after the live-drop red-team work: the evidence operation must still work when the console, network, printer, identity provider, shared drive, web access, or normal timestamp source fails.

The package now treats offline capture as a first-class evidence mode. A paper form, offline note, phone photo, thumb-drive copy, local hash, delayed hash, or post-outage rehydration package can preserve custody and route a packet for adjudication. It cannot close emergency-readiness evidence by itself.

## Hard rule

A folder, README, placeholder, label, synthetic payload, red-team drill artifact, paper receipt, offline form, delayed hash, rehydrated packet, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, accepted-folder state, or complete-looking packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## Operational route

`console unavailable → offline capture mode → paper receipt / local custody note → deferred hash queue → rehydration scan → conflict repair board → candidate-for-adjudication only → CAP/retest/verifier if applicable → claim-kernel release gate`

## What changed in rev0351

* Added an offline blackout mode register for console, network, identity, printer, shared-drive, call-center, public-web, timestamp-source, and evaluator-capture failures.
* Materialized offline packet forms for all 60 event-day must-capture packets.
* Added deferred hash, clock-skew, receipt-repair, redaction-surrogate, and post-outage rehydration queues.
* Added negative controls so an offline form, paper receipt, delayed hash, or rehydrated packet remains an adjudication candidate only.
* Kept all live and synthetic packet loss caps active until a real/anonymized packet passes adjudication, CAP/retest/verifier, and claim-release gates.

## Claim boundary

No Beaver Valley, Pennsylvania, West Virginia, Ohio, county, ORO, controller, evaluator, alerting authority, EOC/EOF/JIC, hospital, CRC, utility, or facility readiness conclusion is made. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only.
