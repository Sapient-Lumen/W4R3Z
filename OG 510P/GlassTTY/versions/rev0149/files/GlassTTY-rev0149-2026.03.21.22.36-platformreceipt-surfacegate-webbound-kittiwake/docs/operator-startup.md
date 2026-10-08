# Operator startup

This file is for a future operator or LLM waking up with little short-term memory.

## Objective

Protect GlassTTY’s current truth surface and make one careful move at a time. The goal is **not** to prove everything in one turn. The goal is to pick the next leverage point without confusing bootstrap truth, runtime truth, and support truth.

## Five-minute wake-up path

0. Start with `docs/operator-startup.md` so the wake path is explicit before following it.
1. Read `README.md`.
2. Read `STATUS.md`.
3. Read `REVISION-RECEIPT.json`.
4. Read `PROJECT_MAP.md`.
5. Run `python scripts/doctor.py --pretty`.
6. Run `python scripts/readiness-report.py --pretty`.
7. Run `python scripts/check-opening-contract.py --pretty`.
8. Run `python scripts/check-revision-receipt.py --pretty`.
9. If only the stale or non-citable truth heads matter, run `python scripts/truth-surface-warnings.py --pretty`.
10. If bootstrap confusion remains, run `python scripts/install-receipt.py --pretty`.
11. If support-claim confusion remains, run `python scripts/support-surface-snapshot.py --pretty`.
12. If the source basis for a support claim feels unclear, run `python scripts/support-source-baseline.py --pretty`.
13. If support publication state is unclear, run `python scripts/support-bundle-queue.py --pretty`.
14. If `validation/latest/*` feels too large to reason about, run `python scripts/validation-artifact-inventory.py --pretty`.
15. If the packaged `validation/latest/*` surfaces may be stale, run `python scripts/refresh-truth-surfaces.py --pretty`.
16. If a durable handoff bundle is needed, run `python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff`.

## Safe default after waking up

If the repo still feels confusing, do **not** invent a new theory of the project from old handoff notes.
Choose one of these narrower actions instead:

- repair bootstrap truth,
- resume the existing validation path,
- freeze the current support surface,
- inspect support-bundle publication pressure,
- or backfill one support record from named evidence.

## What to avoid

Do not:

- claim runtime support from transient UI cues alone,
- confuse native-host registration with live runtime reachability,
- widen support language without freezing the prior support surface,
- or start a brand-new validation run when the latest one is resumable.

## Cold-open discipline

Treat `OPENING-CONTRACT.json` as the declared minimum startup surface and `OPENING-SURFACE-CONFORMANCE.json` as the latest machine-checked answer to whether that startup surface still lines up with reality. Treat `REVISION-RECEIPT.json` as the current archive’s self-description and `REVISION-RECEIPT-CONFORMANCE.json` as the machine-checked answer to whether that description still matches the packaged archive identity and truth-surface counts.


Before widening support language, compare `python scripts/support-bundle-queue.py --pretty` with `python scripts/published-support-surface.py --pretty`; the first tells you what is under review, the second tells you what is citable now.

If you are considering stronger support language, inspect `SUPPORT-SOURCE-LOCK.json` plus `SUPPORT-SOURCE-BASELINE.json` before you inspect `SUPPORT-PUBLISH-GATE.json`; publication now needs both approved source authority and live workflow evidence.
