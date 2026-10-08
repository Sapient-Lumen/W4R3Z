# Representation coverage and gate immutability — rev0865

## Substantive recovery

`sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md` is now physically present at **356,744 bytes** with exact canonical SHA-256 `0f7174a89094f7695b899fad71c2e6d0fb12cd6041734d779aacd8a8bfe400c2`. This moves exact canonical coverage from **18 to 19 files** and exact canonical source coverage from **0 to 1 file**.

The three adjacent generated analysis files remain absent. They are listed with exact identities in the JSON audit; no carried patch contains their file bodies.

## Honest representation boundary

The canonical index describes **4,586 files / 106,421,990 bytes**. This overlay physically matches **19** of those files exactly, carries **17** same-path but revision-divergent files, and is missing **4550**. Under `sources/`, exact coverage is **1 of 3,476 files**.

Therefore an overlay gate PASS means the carried overlay is internally intact. It does **not** mean the canonical datacube is complete.

## Gate defect corrected

The rev0864 `--report` option required output inside the bundle. A report written under `VALIDATION/` immediately became an unmanifested file and caused the next integrity check to fail. rev0865 reverses that unsafe contract:

- reports are allowed only outside the immutable bundle;
- selected checks always include integrity;
- integrity runs before and after other checks;
- partial invocations are labeled `NOT A FULL GATE`;
- gate output always exposes canonical representation as partial.

## Priority

Do not spend the next revision adding another search registry. The only high-value next inputs are real missing bytes, a full canonical tree, or owner/upstream rights decisions.
