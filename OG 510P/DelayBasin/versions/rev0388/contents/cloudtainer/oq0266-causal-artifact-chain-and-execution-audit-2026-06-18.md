# OQ-0266 causal artifact chain and execution audit — 2026-06-18

## Executive finding

Rev0385 had reached the point where another policy layer was less valuable than walking the shipped workflow as an external operator. That execution audit found a concrete blocker: the isolated four-arm collector rejected an otherwise valid response whenever a responder machine's wall clock was ahead of the collector. The failure was reproduced against an untouched rev0385 extraction by advancing one responder-local timestamp set by fifteen minutes. The all-response lock aborted with:

```text
response-set lock chronology impossible: arm-7f2c finalized after response_set_locked_at
```

This was not an exotic adversarial case. The workflow expected genuinely separate responders, collectors, custodians, and scorers, but compared their independent local clocks as if they shared trusted synchronization. The same documentation correctly said those clocks were not trusted timestamp evidence. The implementation therefore produced both a false-negative execution risk and a false sense of causal proof.

Rev0386 replaces cross-operator wall-clock ordering with an exact artifact-receipt chain. Timestamps remain useful local observations and are still checked for monotonicity inside the process that emits each artifact. Across processes and machines, causality is carried by the exact bytes that one stage observes and the SHA-256 bindings that the next stage must consume.

## Why this was the priority risk

The live mission risk is not lack of another registry. It is failure to obtain the first genuine OQ-0266 evidence because the handoff is too brittle or laborious to complete correctly.

The rev0385 isolated lane had four properties that made the clock defect severe:

1. It deliberately distributes work across several machines and people.
2. It requires all four responses before postfreeze disclosure.
3. Its clocks are ordinary local process clocks, not a shared trusted time service.
4. The collector already possesses the exact finalized response bytes and can record when those bytes were observed.

Rejecting an exact response because its producer clock is ahead of the collector throws away stronger evidence—the actual received artifact—in favor of a weaker observation. It also tempts operators to edit or backfill timestamps merely to satisfy the checker, which would make the record less truthful.

## The repaired causal chain

### Conventional OQ-0266 lane

The conventional lane now uses `causal-three-stage-v3`:

1. The responder helper finalizes a response and records responder-local start/completion.
2. The custodian helper strictly validates and hashes those exact response bytes, records a custodian-local observation, and freezes a custody record.
3. The scorer helper validates the exact response and custody bytes, records scorer-local opening and custody observation, and freezes a score sheet.
4. The final scorer revalidates the response → custody → score-sheet hash chain.

The conventional custody template intentionally requires no additional prerequisite receipt. The response hash is the cross-operator link.

### Isolated four-arm lane

The isolated lane now uses:

- `all-arms-causal-freeze-v3` for the collector's exact four-response lock;
- `postfreeze-policy-causal-verification-v3` for the verifier's receipt; and
- `causal-three-stage-v3` for every arm's custody and scoring.

Each arm's custody record must bind two exact prerequisites:

- `response-set-lock`; and
- `postfreeze-policy-verification`.

The final aggregator rejects any arm whose custody record omits, substitutes, or mis-hashes either receipt. This turns the intended batch barrier into an artifact dependency rather than a story inferred from unrelated clocks.

## Positive and negative execution tests

The ordinary regression path now performs a positive skew test: one responder-local clock is moved fifteen minutes ahead of the collector, making its reported finalization later than the collector's lock time. The exact response is still accepted because the collector observes and hashes the bytes before publishing the lock.

The same path continues to fail closed when causality is actually missing:

- incomplete response collection is rejected;
- custody without both prerequisite receipts is rejected before publication;
- a substituted policy-verification receipt is rejected;
- a substituted response-set lock is rejected;
- a response not matching the all-response lock is rejected;
- a score sheet not binding the exact response and custody bytes is rejected; and
- responder self-scoring, duplicate responder IDs, policy substitution, and responder-stimulus substitution remain rejected.

The conventional checker separately proves that clock skew is accepted while reversed scorer-local order remains invalid. Removing cross-machine comparisons did not disable chronology checks; it moved them to the boundary where a single clock can truthfully order events.

## Operator burden reduction

A real run previously required an operator to copy many hashes into a batch manifest by hand. That was both clerical waste and a likely source of fail-late mismatch.

`cloudtainer/tools/prepare_oq0266_isolated_run_manifest.py` now accepts the lock, policy receipt, four responses, four custody records, and four score sheets; validates every exact binding; and atomically publishes the completed run manifest. Missing arms, substituted receipts, and mismatched triplets fail before final aggregation.

The generated prefreeze and postfreeze READMEs were also audited as shell instructions. Several commands had been flattened into one dense line by Python string escaping. The builder now constructs every multi-line command from explicit argument lines, so the extracted kits contain copyable commands rather than prose that an operator must reconstruct.

## Refactor audit

The previous implementation repeated timestamp parsing and cross-clock comparisons across the custody timeline, response-set lock, policy verifier, score-sheet helper, final scorer, batch aggregator, checker, and preflight.

Rev0386 introduces `tools/priority_zero_causal_artifact_lib.py` as the live shared contract for:

- current contract identifiers;
- strict SHA-256 receipt validation;
- same-process local ordering;
- same-process observation windows; and
- ordered prerequisite receipt sets.

Historical `three-stage-v2` behavior remains behind an explicit compatibility adapter. The current implementation no longer needs each caller to invent its own interpretation of cross-operator chronology.

This design is consistent with the underlying distributed-systems distinction between causal order and physical clock readings, and with artifact-provenance systems that verify materials and products across steps. It does **not** claim Lamport clocks, in-toto link signatures, SLSA provenance, trusted timestamping, or third-party attestation. It borrows only the narrower idea that exact communicated artifacts are a stronger causal bridge than unsynchronised wall-clock comparisons.

## What remains uncompleted

The workbench is now more runnable, but the mission-bearing evidence is still absent:

- no genuine conventional response/custody/score-sheet triplet exists;
- no genuine four-person isolated batch exists;
- string identifiers do not prove real-world identity separation or non-collusion;
- local SHA-256 records are not signed attestations or independently held commitments;
- local timestamps are not trusted time;
- one responder per arm cannot identify causal operator burden; and
- the trace arm remains an excerpt rather than a measured full-archive load.

The next high-value action is therefore an actual external execution using the prefreeze dispatch kit, not another internal control layer unless that execution exposes a new runnable defect.

## Research pressure

Two external bodies of work sharpened this repair:

- Leslie Lamport's *Time, Clocks, and the Ordering of Events in a Distributed System* formalizes “happened before” as a partial ordering grounded in process order and communication rather than assuming one reliable global physical clock.
- The in-toto design records and verifies exact materials and products at each step so a later verifier can reconstruct and check the artifact chain.

DelayBasin's implementation is intentionally much weaker than either a signed provenance framework or a trusted logical-clock protocol. The comparison supports the direction of the repair, not a certification claim.
