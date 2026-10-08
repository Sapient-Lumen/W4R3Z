# Revision 0412 — proof-bound runtime acceptance writer

Date: 2026-03-22
Revision: 0412

## What changed

- added the explicit `vhk macro-runtime-accept <project> <macro> --accepted-by <name> --note <why>` command
- added the generated warm-stack wrapper `bin/record_runtime_acceptance.sh <macro> --accepted-by <name> --note <why>`
- durable runtime acceptance updates now write the current posture plus the current proof contract into the acceptance ledger in one bounded step
- the selected-macro acceptance ticket now recommends the proof-bound write helper instead of dead-ending at an out-of-band ledger edit
- added focused tests for command behavior and generated wrapper output

## Why it matters

The previous control plane could compute when signoff was stale, but it still forced the LLM/operator loop to hand-edit YAML to refresh it. This revision keeps acceptance explicit and operator-driven while making the write path first-class and machine-readable.
