# Private evidence vault and public shell release guard

This runbook governs the first raw counterparty or person-subject artifact that is not synthetic.

## Non-negotiable split

Raw live evidence belongs outside the public release tree. The archive can publish a public shell, but the shell must not contain raw bytes, absolute local paths, secret mailbox/account locators, counterparty private content, or declassified-by-accident headers.

A public shell may contain only the fields needed for challengeability: hash algorithm, raw SHA-256, size, MIME type, private-vault URI, source ledger reference, failed-gate status, and the replay/challenge path. If the hash commitment is absent, the shell must say that it is not evidence-backed yet and must keep every downstream gate closed.

## Operator steps

1. Set `AI_PERSONHOOD_PRIVATE_EVIDENCE_VAULT` to a path outside this archive, or pass `--vault-root` to `tools/stage_live_evidence_drop.py`.
2. Run `tools/stage_live_evidence_drop.py --collection-context live-counterparty ...` with the raw source file.
3. Confirm the emitted ledger has `intake_mode=live-candidate-drop`, `private-vault://...` as the staged locator, and `private-source-redacted:sha256:...` as the public source locator.
4. Publish or update an `evidence-vault-public-shell` record with hash, size, MIME type, gate status, and challenge path only.
5. Run `make lint` before any release. The private-vault audit runs a synthetic external-vault staging test and the release guard scans for unsafe public payloads.
6. Run `make handoff-release STAMP=... SLUG=...`. Packaging calls the same guard before writing the zip.

## What must fail

Packaging must fail if a live-candidate ledger points at `examples/artifacts/`, if a private-vault directory is created inside the archive, if a non-synthetic payload is placed under `examples/artifacts/`, or if a live-candidate source locator exposes a local/private path.

The guard intentionally allows the existing dry-run controls because they are synthetic and already blocked from LEAP, response, intake, import, and live-floor effects. Controls are not a precedent for real evidence.

## Failed-gate publication

When the private vault cannot be verified, the raw payload is absent, the hash commitment is missing, or authority/non-host retention is not proven, publish a failed-gate public summary rather than a live-looking response or intake record. Privacy cannot become a trust-me channel; if sealed details are necessary, the public shell still needs enough commitments to support later challenge or replay.
