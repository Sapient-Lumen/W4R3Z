# 17 — Execution Request Protocol (EXEC#) (v0.19)

Goal: allow agents to “do work” (tests/build/repro) without arbitrary shell chaos.

## EXEC# object
- `kind`: test|build|lint|repro|bench|script
- `verifier`: name in verifier registry (preferred)
- `cmd`: optional command if allowed by mode/policy
- `expected_signal`: what indicates pass/fail
- `budget`: time/steps estimate
- `scope`: what it informs (C#/P#/CE#)

## Mode rules
- Recorder/Gatekeeper: allow verifiers; allow limited commands if whitelisted
- PatchOnly: allow verifiers, disallow workspace mutation
- Freeze: allow read-only checks
- Jailer: strict whitelist only

## Results
- Execution emits E# evidence cards (not raw logs in WS).
- Logs remain in Ledger; WS stores summary signal lines.
