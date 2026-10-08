# Mission audit — REV0111 handoff archive gate

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

Rev0111 turns the selector/evaluator handoff into a portable archive contract instead of another path-sensitive receipt. The new gate checks a handoff manifest, enforces relative paths, recomputes SHA-256 over trace/provenance/receipt/tool subjects, rejects path escapes, and then runs the selector-entry receipt replay gate against the extracted files.

## Why this is the riskiest useful change

The cube now has a chain from public trace capture to evaluation receipt to selector-entry receipt to replay. The next failure mode is mundane but dangerous: someone zips or moves the bundle and the receiver cannot prove that the receipt still names the exact same NPZ/provenance/toolchain subjects. Rev0111 makes that handoff portable and testable.

## Audit/refactor action

The current entry docs now route through one endgame lane:

1. capture real public trace;
2. emit accepted evaluation receipt;
3. emit selector-entry receipt;
4. replay selector-entry receipt;
5. validate the portable handoff archive;
6. only then continue to selector/cost evaluation and named-hardware timing.

No promotion evidence was added. The blockers remain the real public trace, accepted real receipts, selector/cost evaluation, and named-hardware timing.
