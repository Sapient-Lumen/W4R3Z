# Proof obligation — rev0096

Executable obligations added:

- Python-route call archive accepts only when the upstream call ledger is accepted and no native result was selected.
- Promotion denial accepts repeated matching shadow evidence only as denied evidence, not as permission.
- Shadow-GC can compact soft vectors only while preserving fallback, denial, tombstone, quarantine, and crash memory.
- `nativearchivefold.py` must pass current-path fold/audit checks.

Verification is recorded in `artifacts/process/rev0096_verification_summary.json`.
