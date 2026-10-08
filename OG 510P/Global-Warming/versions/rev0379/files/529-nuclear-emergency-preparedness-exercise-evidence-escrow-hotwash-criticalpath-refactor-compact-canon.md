# 529 — Nuclear Emergency Preparedness Exercise Evidence Escrow, Hotwash Clock, and Critical-Path Refactor — Compact Canon

Revision: **rev0322**  
Scope: **REAL_BVPS_PUBLIC_ONLY remains public-context-only. No real Beaver Valley readiness or unreadiness claim is made.**

## Why this revision exists

The next high-risk failure is not another missing doctrine register. It is evidence loss. A biennial evaluated exercise produces many fragile artifacts: raw alert logs, controller/evaluator observations, timestamped public-message variants, hotwash notes, CAP owner assignments, instrument checks, field-monitoring logs, AFN dispatch records, JIC approval trails, rumor/correction handling, and preliminary findings. If those artifacts are not escrowed during or immediately after the exercise, the cube can only reason from polished post-hoc summaries.

Rev0322 therefore adds an **exercise evidence escrow spine**. The purpose is to make the June 2026 Beaver Valley evidence path operational before the exercise artifacts exist. Public context can trigger a capture slot, blocker, cap, or reopen path. It still cannot close local readiness evidence.

## Non-negotiable rule

**Schedule, public notice, public meeting, public AAR paragraph, public fact sheet, current reactor status, source URL, brochure, or message template alone cannot close readiness.**

Closure requires a local or anonymized packet with hash, owner, timestamp, scope, sensitive-annex split, evaluator/verifier, retest/CAP state, counterevidence path, and public-claim gate.

## New proof route

`prior AAR issue → exercise-day capture slot → evidence escrow ledger → preliminary finding intake → hotwash/CAP clock → retest/verifier → public claim gate`

## High-risk artifacts now captured

Rev0322 adds capture slots for:

- EAS, WEA/IPAWS, siren/SNB, county-alert, press-release, and JIC message logs;
- PAD/PAR decision records and release-sequence timestamps;
- message URL checks, KI/farmer/school/language-access diffs, and rumor/correction logs;
- AFN, school, LTC, hospital, route-control, reception/CRC/decon, field-monitoring, ingestion-pathway, and sampling chain-of-custody evidence;
- EN58200 EOF closure non-regression evidence;
- evaluator observations, hotwash notes, preliminary findings, CAP owner assignments, retest packets, closure board minutes, and public-claim board decisions.

## What changed from rev0321

Rev0321 had message lint and exercise-day capture slots. Rev0322 makes the capture path harder to evade by adding:

1. a 44-row evidence escrow ledger with irreversible-loss risk and capture deadlines;
2. a 24-row hotwash-to-CAP clock;
3. a 32-row evaluator-observation normal form;
4. an 18-row alert-channel minimum packet;
5. a 20-row missing-evidence default-cap table;
6. a 30-test evidence escrow validator with rejection/hold/candidate/reopen states;
7. a scoped SQLite mirror with zero public-context-to-local-closure leaks.

## Claim scope

The package does not assert Beaver Valley is ready, unready, green, safe, passed, failed, certified, or closed. It says only that a public exercise and public-source context exist, and that local/anonymized evidence is required before any readiness claim can be made.
