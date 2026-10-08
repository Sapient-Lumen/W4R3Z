# 557 — Nuclear emergency preparedness: ghost-fork cleanup, live-drop red-team drill, and receipt-gate refactor compact canon

## Claim boundary

This revision is a clean canonical **rev0350** built from the last linked rev0349 package:

`Global-Warming-rev0349-2026.06.05.17.04-preflightrehearsal-snapshotseal-operatorreceipts-refactor.zip`

The cloudtainer working state already contained same-revision rev0350 build artifacts from side attempts, while the selected base remained the last linked rev0349 zip. Rev0350 records those ghost/staging artifacts in `cube/package-ghost-rev0350-artifact-audit-rev0350.csv`, avoids silently switching bases, and rebuilds a single canonical numbered `557` file.

The operational rule remains strict: a folder, receipt, snapshot, redacted surrogate, hash, synthetic payload, red-team drill artifact, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, accepted-folder state, or complete-looking packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## Why this revision exists

The near-term risk is not another doctrine gap. The risk is that event-day evidence enters through the wrong fork, wrong folder, wrong clock, wrong source cluster, or wrong claim state. The red-team drill tests the intake path before real/anonymized packets arrive.

Rev0350 therefore adds:

- a ghost-fork cleanup audit;
- a 54-case live-drop red-team drill;
- file-level hashes for drill artifacts;
- a receipt issuance gate;
- replay/canary and synthetic-contamination checks;
- redaction/custody delta checks;
- public-claim embargo checks;
- a SQLite query surface that proves zero public-context-to-local-closure leaks.

## Data route

`rev0349 preflight snapshot -> ghost-fork cleanup -> red-team dropbox drill -> file hash scan -> receipt gate -> rejection/hold/candidate/reopen/context classification -> loss cap -> claim embargo -> adjudication only`

## Non-closure rule

The only allowed intake states are:

- rejected_closure_attempt;
- hold_no_upgrade;
- candidate_for_adjudication_not_closure;
- accepted_reopen_signal;
- context_no_upgrade.

There is no auto-close state in this revision.

## Still not evidence

The red-team files under `field-kits/bvps-rev0350/redteam-dropbox-drill/` are synthetic drill artifacts. They prove the intake controls can reject and classify evidence-like material. They do not assert that any Beaver Valley exercise branch, jurisdiction, packet owner, alerting authority, evaluator, controller, EOC/EOF/JIC, or facility is ready, unready, green, failed, passed, certified, sufficient, demonstrated, or closed.
