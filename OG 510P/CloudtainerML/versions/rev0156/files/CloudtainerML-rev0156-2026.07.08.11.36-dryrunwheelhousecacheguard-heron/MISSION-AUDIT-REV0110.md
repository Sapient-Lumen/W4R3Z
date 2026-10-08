# Mission audit — REV0110

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

Rev0110 closes a concrete handoff defect discovered in rev0109: the relocation audit exercised forged/negative selector-entry cases without always passing an explicit selector receipt path, so the current default selector-entry receipt in `artifacts/probe-results/` could be overwritten by a fixture failure. That made the package look green while the default handoff artifact pointed at a forged v1 receipt.

This revision fixes that overwrite path and adds a replay gate for selector-entry receipts. The replay gate verifies the selector-entry receipt, input evaluation receipt, trace NPZ, provenance JSON, verifier tool, evaluator tool, and selector gate by SHA-256 subject digests. Moved or renamed bundles can still pass, but only when the actual file/tool digests replay exactly.

## Why this is the riskiest useful work

The project is now close enough to a real public trace that handoff integrity matters more than another policy document. A future real trace could otherwise be captured, accepted, moved into a selector/cost lane, and then evaluated under a stale or overwritten receipt. Rev0110 makes that failure mode executable and testable.

## What remains blocked

- Real public TinyLlama trace NPZ/provenance pair is still absent here.
- Selector-entry replay is handoff evidence only; it is not promotion evidence.
- Named-hardware sparse-vs-dense timing is still required before any performance claim.
