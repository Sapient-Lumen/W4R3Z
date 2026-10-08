# CloudtainerML rev0078 — deep mission / waste / integrity read

Generated: 2026-07-06T02:06:00-04:00  
Source revision: rev0077  
Codename: missionwasteintegrity-sablekite

## Status

This is a non-promotional session overlay. It does not add a new sparse-attention claim, a real public model trace, a named-GPU timing, or a deployment result. It preserves the rev0077 scientific boundary and adds a deep mission reading plus a checksum-smoke guard.

The clean uploaded rev0077 archive checksum ledger validated before edits: 1436 entries OK, 0 failed, 0 missing, 0 malformed. A working-copy mismatch observed during the session was traced to local audit/tool execution mutating artifacts after unpack, not to a bad uploaded archive. That mutation hazard is now treated as a first-class workflow risk.

## Heart of the mission

CloudtainerML is best understood as a claim compiler and falsification wind tunnel for ML architecture ideas. The product is not a registry, a benchmark table, or a green check. The product is a trustworthy decision: compress a mechanism claim into the cheapest hostile experiment that could kill it, then allow promotion only when semantic exactness, cost, provenance, and deployment constraints survive.

The strongest form of the mission is:

1. translate a proposed mechanism into executable semantics;
2. produce a negative control that should fail if the mechanism is wrong;
3. require exact model-path replay before public/pretrained claims;
4. require named-hardware cost/latency/throughput/memory evidence before performance claims;
5. stop or pivot lanes that only generate governance artifacts around missing evidence.

## What is missing

- A real immutable public-model post-transform trace. Rev0077 proves a deterministic Llama-like post-transform contract, but it still does not load a public pretrained model or capture the actual post-RoPE/scored Q/K/V path.
- A model/runtime dense reference captured or recomputed against the same attention path, including scale, mask/bias, RoPE/position transforms, head dimensions, tokenizer/model revision, and trusted-code revision when applicable.
- Named hardware and full-system measurements. No GPU/fused kernel timing, no end-to-end replay, no memory/throughput/latency quality comparison, and no index/mask construction cost.
- A small set of canonical statuses. The current cube has dozens of ledger status labels, which weakens triage.
- A hard cap on registry growth. The cube tracks hundreds of questions and sources, while most questions remain open.
- Immutable audit ergonomics. Some historical/audit tools can mint or rewrite artifacts when run from a later revision; smoke validation previously did not verify the checksum ledger itself.

## What should change next

1. Make the next scientific revision either a real-model trace capture or a lane stop. No more gate-only trace governance unless it directly enables the real trace.
2. Add a public-model adapter acceptance fixture around one small Llama-family/HF model: capture post-transform Q/K/V, attention scale, mask/bias, position transform, tokenizer revision, model revision, code revision, prompt tokens, layer/head IDs, and dense reference.
3. Add one named-hardware baseline harness before optimization claims: dense backend, candidate sparse backend, input distribution, quality metric, latency, throughput, peak/allocated memory, and index/mask construction time.
4. Collapse ledger statuses into a tiny taxonomy: `candidate`, `falsified`, `blocked_missing_evidence`, `measured_survivor`, `retired`, `archived_reference`.
5. Convert historical mutable runners into read-only replayers, or quarantine them under `legacy_mutating_tools/` with explicit warnings.
6. Keep checksum validation in smoke so any post-unpack mutation becomes obvious immediately.

## Places where something has gone wrong or become wasteful

### 1. Governance loop around absent data

The cube has become very good at detecting that public/GPU evidence is absent. That is useful, but it risks becoming a replacement for the missing experiment. The next useful revision must reduce uncertainty about a model/runtime path or explicitly stop the lane.

### 2. The semantic bug was severe, and rev0077 is the right kind of correction

A core previous failure mode was treating raw projection Q/K as if it were the scored attention Q/K path. Rev0077 correctly moves toward post-transform replay and rejects raw projection as a public claim. This was not a clerical bug; it attacked the center of the mission because the whole compiler depends on checking the same semantics the model actually uses.

### 3. The cube is accumulating registry entropy

The rev0077 waste audit reports 660 questions with about 97.4% still open, 343 sources, 354 ideas, and very fragmented cell/idea statuses. That suggests the cube is becoming a warehouse as much as a wind tunnel. The cure is not deleting knowledge indiscriminately; it is forcing each active lane to name its falsifier, current blocker, stop condition, and next measurable artifact.

### 4. Historical revision machinery still leaks cost

The lineage audit reports 63 historical dynamic artifact-minting hazards and 12 hard-coded timestamp hazards. The current policy of fixing when touched is reasonable, but only if future revisions stop invoking stale historical runners during normal workflows.

### 5. Binary/input carry cost exists but is not the main disease

The tree contains compiled/native artifacts and duplicate recoverable bytes. These are worth pruning over time, but the more serious waste is cognitive: too many surfaces and statuses make it hard to see which experiment should run next.

## Speculative diagnosis

CloudtainerML looks like it began as a tiny-scale architecture/surprise lab, then discovered that trust boundaries were the real bottleneck. That is a healthy evolution, but some older tools and surfaces still pull the project back toward benchmark/registry behavior. The mission should now be stated less as "explore many ideas" and more as "kill or certify exact claims under hostile evidence rules."

The cloudtainer should behave like a court, not a museum: every active claim needs admissible evidence, cross-examination, and a verdict path. Unadjudicated material can remain, but it should not dominate the working set.

## Session changes in rev0078

- Added this deep mission/waste/integrity audit.
- Added a structured session audit artifact at `artifacts/audit/REV0078_SESSION_DEEP_READ_AUDIT.json`.
- Added a readable mirror at `artifacts/audit/REV0078_SESSION_DEEP_READ_AUDIT.md`.
- Updated entry surfaces to mark rev0078 as a non-promotional mission overlay inheriting rev0077 scientific evidence.
- Updated `tools/smoke_validate.py` so smoke validation also verifies every entry in `CHECKSUMS.sha256`.
- Regenerated `FILE-MANIFEST.json` and `CHECKSUMS.sha256` after all edits.

## Recommended next-turn contract

Deliver exactly one of:

1. real public-model post-transform trace capture with immutable model/tokenizer/code provenance and dense parity;
2. named-hardware end-to-end sparse-vs-dense measurement with quality and memory; or
3. an explicit lane-stop memo retiring this sparse-attention path until external evidence appears.

Anything else should be treated as support work, not mission progress.
