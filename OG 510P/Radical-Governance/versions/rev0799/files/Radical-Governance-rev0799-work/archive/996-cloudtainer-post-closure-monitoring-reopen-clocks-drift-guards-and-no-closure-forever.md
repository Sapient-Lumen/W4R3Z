# 996 — Cloudtainer post-closure monitoring, reopen clocks, drift guards, and no closure forever

## One-line thesis

Rev0797 made closure dossiers reviewable but still non-ready. Rev0798 adds post-closure monitoring controls so any future closure remains conditional: recurrence, source decay, denominator drift, policy change, private-data leakage, or later claimant/household evidence can qualify or reopen a gap. The governing rule is **no closure forever**.

## Why this matters

The archive now has a substantial fieldwork chain: source receipt → outcome-tail plan → sampling gate → intake control → authorization gate → execution control → release control → correction control → redress verification → closure dossier. That chain is useful because it keeps administrative surfaces from pretending to be material outcomes. But once a closure dossier exists, the next failure mode is finality theater.

A future maintainer could treat a public-safe dossier, owner attestation, independent review, or gap-ledger status as if it permanently settled a claimant or household outcome. That would be wrong. Payment can later be interrupted. Debt collection can restart. Identity or fraud holds can recur. Appeals can stall. A tenant can keep possession and still re-enter shelter or doubled-up instability. A source locator can decay. A policy, vendor, court practice, model, or administrative process can change the pathway that was originally verified.

Rev0798 adds `metadata/fieldwork_postclosure_monitoring_controls.json`. It does not activate monitoring, collect private evidence, approve surveillance, or reopen anything today. It defines the public-safe control surface that any future closure must carry if the archive is going to avoid pretending that closure is timeless.

The governing rule is **no closure forever**.

## Pattern pack

1. **Closure is a reviewable state, not a permanent fact.** A gap can be closed only within a stated scope, evidence level, source-preservation posture, and monitoring/reopen rule.
2. **Monitoring is not surveillance authority.** A post-closure control may specify cadence classes and drift triggers; it does not authorize contacting people, linking records, or holding private data.
3. **Recurrence defeats closure theater.** If payment holds, debt collection, appeal friction, lockouts, shelter returns, screening harms, or retaliation risks recur, the closure finding must be qualified or reopened.
4. **Sources can decay after closure.** A closure dossier relying on locators, hashes, archival receipts, or passage mappings must recheck whether those sources remain reconstructable.
5. **Denominators can drift.** Nonresponse, rare cohorts, informal exits, unrepresented cases, default cases, withdrawn cases, and suppressed cells must remain visible as limitation classes.
6. **Policy and system changes matter.** Law, rule, vendor, model, case-management, court, benefits, or provider changes can invalidate the pathway that a closure dossier once tested.
7. **A reopen trigger is not a failure.** It is the archive admitting that public power must remain answerable to later evidence.
8. **The cube stays public-safe.** It may hold monitoring class, cadence class, source-receipt ids, limitation classes, and reopen-decision classes. It must not hold names, claim numbers, addresses, court files, payment records, monitoring extracts, linkage keys, raw logs, transcripts, recordings, or partner case files.

## What changed

### Fieldwork post-closure monitoring controls

Rev0798 adds two non-active post-closure monitoring controls.

`PCM-UI-001` covers unemployment-insurance claimant post-closure monitoring. It inherits `FCD-UI-001` and requires recurrence checks for payment/backpay, identity or fraud holds, overpayment/waiver/refund, appeal correction, representative or assisted access, burden, and source-receipt integrity. It also requires a public-safe rule for qualifying or reopening closure if later claimant evidence, source decay, or unresolved exception trends undermine the closure finding.

`PCM-HC-001` covers housing household post-closure monitoring. It inherits `FCD-HC-001` and requires durable-stability checks for possession or safe move, lockout/exclusion repair, rehousing or shelter stability, arrears/subsidy cure, screening or record harm, retaliation/coercion risk, informal exits, default/unrepresented cases, and source-receipt integrity.

Both controls remain non-active. Neither proves an outcome, authorizes monitoring, stores private evidence, preserves source snapshots, or keeps a gap closed forever.

### Post-closure source receipts

Rev0798 adds source-claim receipts for OMB A-123 (2026), the GAO 2025 Green Book, GAO evidence-building practices, and OMB A-11 Section 290 as monitoring, corrective-action, continuous-improvement, and learning-cycle floors. These sources support the control discipline. They do not supply UI or housing outcome evidence.

### Audit/refactor

The bounded refactor adds `validate_fieldwork_post_closure_links` to `tools/fieldwork_lint_helpers.py`. Post-closure monitoring controls must inherit the same closure dossier, redress verification, correction, release, execution, authorization, intake, sampling, and outcome-tail lineage. They cannot create a parallel monitoring route.

The new surface is now part of `tools/build_steps.py`, `Makefile`, schema validation, generated-surface output, and `tools/lint_archive.py` checks.

## What this still does not do

It does not activate monitoring.

It does not approve contacting people, linking records, extracting administrative data, holding private evidence, or publishing a monitoring output.

It does not prove payment, debt cure, waiver/refund, appeal correction, hold removal, representative access, burden reduction, possession retention, safe move, rehousing, screening repair, durable stability, source preservation, or material power shift.

It does not close any live gap, keep any gap closed, or reopen any gap today.

## Anti-theater tests

1. Pick `PCM-UI-001`. Does it say what post-closure recurrence would look like for payment, holds, debt, appeal, representative access, burden, and source receipt integrity?
2. Pick `PCM-HC-001`. Does it say what post-closure recurrence would look like for possession, lockout, rehousing, subsidy, screening, retaliation, and durable stability?
3. Pick either row. Does it inherit the matching closure dossier and full fieldwork chain rather than inventing a parallel path?
4. Pick either row. Does it preserve outside-cube evidence boundaries and prohibit private monitoring artifacts?
5. Pick either row. Does it include gap reopen rules rather than promising permanent closure?
6. Pick `generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.md`. Does it show monitoring as `not_active`, not as complete or validated?
7. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the monitoring surface?
8. Pick the new source receipts. Do they support monitoring discipline without pretending to be source snapshots or claimant/household evidence?

## Source posture

Use OMB A-123 and the GAO Green Book as internal-control and corrective-action monitoring floors. Use GAO evidence-building practices and OMB A-11 Section 290 to ground evidence use, learning cycles, and continuous improvement after an apparent closure decision.

These sources support post-closure monitoring discipline. They do not prove any material outcome, authorize private monitoring, preserve source snapshots, or keep a gap closed.

The practical rule is: **a closed status is not a constitutional force field. Later evidence can reopen the cube.**
