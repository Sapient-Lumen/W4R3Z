# 702 — Trust recovery and failure handoff path

**Track:** Shared / Track A pilot readiness

v827 adds a narrow trust-recovery layer for the synthetic Example County pilot. The goal is not to make a failed or missing artifact sound harmless. The goal is to force every ambiguous evidence state into a bounded handoff: preserve the bytes, name the failure mode, use public-safe language, identify the owner, and avoid claims the packet cannot support.

## What changed

- Added `artifacts/registries/trust-recovery-playbook.csv` as the canonical failure-handoff registry.
- Added `tools/trust_recovery_output_pack.py` to derive the synthetic trust-recovery matrix, failure-handoff index, and public failure bulletin.
- Added `artifacts/examples/example_county_2026_municipal_pilot/trust-recovery-matrix.json`.
- Added `artifacts/examples/example_county_2026_municipal_pilot/failure-handoff-index.csv`.
- Added `artifacts/examples/example_county_2026_municipal_pilot/public-failure-bulletin.md`.
- Added `scripts/check_trust_recovery_playbook.py` and `scripts/check_trust_recovery_output_pack.py` to keep the handoff path machine-checkable.

## Failure modes covered

The playbook covers verifier failure, publication missingness, public-surface parity divergence, signing-key compromise or confusing rotation, official AI-assisted output error, forged screenshots or unverified derivatives, non-voting election technology outage, witness-set divergence, public-safety or intimidation reports, and stale or unpinned external source review.

## Non-claim boundary

The handoff layer is evidence-preservation and public-language discipline. It is not outcome certification, not a finding of intent or fraud, and not legal advice. Live use still needs local roles, local law, safe-reporting channels, and counsel-reviewed preservation rules.

## Operator path

```bash
python3 scripts/check_trust_recovery_playbook.py
python3 tools/trust_recovery_output_pack.py --write
python3 scripts/check_trust_recovery_output_pack.py
```

The public-facing starting point is `artifacts/examples/example_county_2026_municipal_pilot/public-failure-bulletin.md`.

## Why this belongs in Track A

The stack already verifies happy-path packet integrity. Real legitimacy disputes start when something fails: a packet does not verify, a deadline is missed, a public surface diverges, an official channel changes, an AI-assisted artifact is corrected, or a screenshot circulates outside the digest chain. Track A needs a prewritten, release-gated failure handoff so operators do not improvise under pressure.
