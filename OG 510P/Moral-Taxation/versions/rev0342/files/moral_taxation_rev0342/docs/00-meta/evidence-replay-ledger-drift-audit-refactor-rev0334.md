> **Superseded evidence-status notice (rev0337):** This historical report treated archive-generated deterministic fixtures as implementation-grade evidence. Its implementation, promotion, or finalization counts demonstrate schema conformance only, not externally observed facts or authority. Use [the rev0337 truth-boundary report](evidence-truth-boundary-release-lineage-refactor-rev0337.md) for current status.

# Evidence replay ledger drift audit refactor — rev0334

## Purpose

rev0333 made strict authority/current-law and jurisdiction evidence depend on raw intake plus source-manifest proof. The next risk was replayability: a validated evidence bundle could clear strict execution once, but the cube had no compact way to prove later that the same adapter packet, evidence record, producer contract, and execution result were the same.

rev0334 adds a post-execution replay ledger. It records hashes and decision traces only. It does not store raw authority text, model outputs, or jurisdiction conclusions as doctrine.

## Added runtime boundary

`tools/build_evidence_replay_ledger.py` builds an `adapter_execution_replay_ledger` with one record per adapter execution. Each record carries:

- adapter packet hash,
- evidence lookup keys,
- evidence hash,
- producer ID and producer-contract hash,
- execution status and finalization status,
- decision-trace hash,
- full execution-result hash,
- evidence locator and checked-at date when available,
- explicit non-doctrine warning.

`tools/audit_evidence_replay_ledger.py` independently rebuilds implementation-grade model/source and authority/source/intake/evidence bundles, builds a replay ledger, replays the same bundle, mutates evidence hashes, corrupts authority-source proof, and verifies the ledger detects the changes.

## Audit results

- Answer packets checked: **122**
- Adapter execution records: **1724**
- Authority adapter records: **865**
- Model-style adapter records: **859**
- Same-bundle replay mismatches: **0**
- Hash-tamper mismatches detected: **5172**
- Authority-source corruption execution-status mismatches: **865**
- Implementation replay status counts:
  - `executed_evidence_satisfies_adapter`: **1672**
  - `executed_evidence_blocks_finalization`: **52**
- Implementation evidence-present records: **1724/1724**
- Producer-contract-hash records: **1724/1724**

## Substantive correction

The cube now distinguishes four things that previously sat too close together:

1. an adapter requires evidence,
2. an evidence bundle is supplied,
3. strict execution accepts or blocks that evidence,
4. the execution decision can be replayed and hash-compared later.

That prevents evidence from becoming invisible doctrine. A later change to source text, model assumptions, producer contract, or execution logic must show up as replay drift rather than silently passing as the same clearance.

## Refactor discipline

This revision adds no routes, axes, or source IDs. It adds a narrow replay surface and an audit. The ledger stores hashes and traces, not live-law conclusions or model results.

## Remaining risk

The next frontier is external producer replacement: live authority retrieval and calibrated model/no-go producers should emit externally retained evidence bundles whose hashes can be replayed through this ledger.
