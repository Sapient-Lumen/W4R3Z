# 534 — Nuclear Emergency Preparedness Alert Originator Authority, Delivery Receipt, and Public-Meeting Lockbox Refactor — Compact Canon

## Purpose

Rev0327 hardens the most fragile near-term part of the Beaver Valley public-only emergency-preparedness branch: alert evidence can look authoritative when it is only partial. A CAP message in a public archive, an IPAWS acknowledgement, a WEA headline, a press-release excerpt, a public meeting statement, or a screenshot of an alert does not by itself prove local emergency-preparedness readiness.

This revision introduces a delivery-evidence ladder and a public-meeting lockbox. It distinguishes:

1. an authorized originator was allowed to send the alert;
2. the right approval path authorized the specific protective-action message;
3. the message payload, target geometry, event code, status, msgType, references, and expiration were correct;
4. IPAWS accepted, updated, corrected, cancelled, rejected, or errored the message;
5. downstream channels carried or failed the message;
6. public archives later surfaced, omitted, duplicated, or lagged the message;
7. evaluators and after-action records converted the evidence into a finding, CAP, retest, verifier decision, or reopened blocker.

## Governing rule

Public alert feeds, public archives, CAP payloads, public meeting remarks, public event notices, public reactor-status records, public AAR excerpts, and synthetic evidence-bag manifests can discover, timestamp, route, cap, corroborate, contradict, reopen, or demand evidence. They cannot auto-close local emergency-readiness evidence.

## Why this matters

The June 2026 Beaver Valley exercise creates a short-lived evidence-capture window. Missing raw logs, missing acknowledgements, missing error records, missing originator authority, or missing public-meeting transcripts must default to a cap rather than to silence. The cube therefore treats the absence of a public archive hit as a possible false negative, not as proof that nothing happened; and it treats the presence of an archive hit as public context, not as proof that the local alerting function worked.

## New proof surfaces

- alert-originator authority controls;
- delivery-evidence ladder;
- ACK/error normal form;
- WEA geotargeting and undershoot/overshoot proof;
- public archive limitation and false-negative triage;
- public meeting lockbox schema and validator;
- source-clock and alert-authority audit;
- SQLite views for open P0 authority, delivery, public-meeting, archive, and leakage checks.

## Readiness claim posture

REAL_BVPS_PUBLIC_ONLY remains public-context-only. This revision makes the alert and public-meeting evidence path harder to misuse; it does not claim Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, any alerting authority, or any facility is ready, unready, green, failed, passed, certified, safe, sufficient, or closed.
