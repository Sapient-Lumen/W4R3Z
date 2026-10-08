# Rev0976 changelog — reconcile regex memory and checked i64

## Lineage

- Preserved the linked regex-memory rev0975 as historical truth.
- Merged the divergent checked-i64 branch only under rev0976.
- Added one rev0976 revision-index entry and current mission/handoff documents.

## VM and language

- Added one non-boolean signed-64-bit value predicate and bounded decimal parser.
- Enforced it for literals, `to-int`, typed integer consumers, bytecode JSON/import/export/dispatch, compiled code, and plugin callbacks.
- Made arithmetic/comparisons/conversion inspect-before-commit and added stable overflow handling.
- Rejected JSON booleans, host bignums, mutable invalid bytecode operands/spans, and negative/past-end constant indexes.
- Pinned floor division and paired remainder with new portability cases and updated primitive help.

## Regex containment/refactor

- Retained Linux post-request `RLIMIT_AS`, stable `memory-limit`, exact UTF-8 replacement preflight, and fresh-worker recovery.
- Centralized positive parent worker-budget parsing.
- Rejected boolean result/memory limits before spawn and in the child protocol.
- Prebuilt both the low-memory failure mapping and encoded protocol response.

## Evidence and documentation

- Added integer-domain and plugin-amplification regressions; extended regex protocol/low-memory regressions.
- Updated data model, bytecode, portability, security, research, roadmap, worklist, README, TODO, and generated/current handoff artifacts.
- Added rev0976 audit, changelog, test record, and exact archive verification.
