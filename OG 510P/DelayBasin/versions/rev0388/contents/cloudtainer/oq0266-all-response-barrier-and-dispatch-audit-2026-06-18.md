# OQ-0266 all-response barrier and dispatch-boundary audit

Date: 2026-06-18  
Working overlay: `rev0383`  
Canonical head preserved inside the cube: `rev0374`

## Executive finding

The isolated-arm pilot in rev0382 enforced response-before-custody chronology **inside each arm**, but did not enforce the batch-level rule stated by its own runbook: all four responses must be frozen before any assignment mapping, custody material, or scorer material opens.

That gap was mission-critical. A collector could finalize one response, open the postfreeze kit, prepare custody and scoring for that arm, then collect the remaining three responses. The rev0382 final aggregator still accepted the completed batch and returned `support-isolated-semantic-recovery-pilot` because every arm was locally chronological even though the batch had already been contaminated.

A temporary exploit harness reproduced the defect against an untouched rev0382 extraction. The first custody stage opened at `2026-06-18T11:03:59.493174+00:00`; three later responses did not finalize until approximately `2026-06-18T11:04:01+00:00`. The batch nevertheless passed. This is now a permanent negative canary rather than an informal warning.

## Repair

Rev0383 splits the live execution boundary into two artifacts.

### Prefreeze dispatch kit

`cloudtainer/oq0266-isolated-semantic-pilot/prefreeze-dispatch-kit.zip`

This is the only pilot-wide artifact allowed before all responses freeze. It contains:

- one exact opaque dispatch manifest;
- the assignment commitment but not the assignment mapping;
- four nested one-arm responder ZIPs;
- a response-set locking command and its shared contract library; and
- only the response-validation dependencies required to verify returned response bytes.

It excludes the assignment plan, custody templates, scorer intakes, score sheets, decision thresholds, and batch scorer. The full cube and the pilot builder are explicitly classified as not prefreeze-safe.

### All-response lock

`cloudtainer/tools/lock_oq0266_isolated_response_set.py` requires exactly four finalized responses, four distinct responder identifiers, and a fifth collector identifier. It reopens each exact nested responder bundle, validates its member order and hashes, strictly parses the embedded packet/template bytes, revalidates each finalized response, and emits one atomic read-only lock binding:

- response file hashes;
- responder identifiers;
- response finalization times;
- responder-bundle hashes;
- responder-packet hashes;
- dispatch-manifest hash; and
- assignment-commitment hash.

The lock records a local process-clock observation and explicit collector attestations. It is not represented as a trusted timestamp, signature, or independent identity proof.

### Postfreeze verification

The postfreeze batch scorer now requires the exact response-set lock and dispatch manifest. After independently validating all four response/custody/score triplets, it binds those current response bytes and identities back to the lock and rejects any custody or scorer opening earlier than the lock timestamp.

A run manifest must bind the exact response-set lock hash. Replacing a response, commitment, mapping, or lock after collection therefore causes a hard failure.

## Executable canaries

`cloudtainer/tools/check_oq0266_isolated_semantic_pilot.py` now performs the actual package sequence:

1. extract only the prefreeze kit;
2. execute all four nested responder kits;
3. prove that a three-response lock fails without publishing output;
4. create the four-response lock;
5. extract the postfreeze kit only after the lock exists;
6. execute custody and scoring for every arm;
7. aggregate the exact four triplets; and
8. attack the resulting chain.

The negative set covers:

- responder-bundle mapping leakage;
- postfreeze material inside the prefreeze kit;
- incomplete response-set publication;
- custody/scoring before the all-response lock;
- response-set lock substitution;
- post-response plan/commitment substitution; and
- duplicate responders.

`tools/check_oq0266_isolated_batch_barrier_contract.py` promotes that full execution canary into the ordinary validation toolchain. This is intentionally not another declarative registry row: lint now runs the actual staged kits and fails if the chronology exploit returns.

## Refactor audit

### One strict JSON byte boundary

ZIP-member parsing previously risked diverging from file parsing. `tools/priority_zero_external_run_artifact_lib.py` now exposes `strict_json_bytes`, and path-based `strict_json` delegates to it. The prefreeze lock therefore applies the same UTF-8, duplicate-key, and non-finite-number rejection to embedded ZIP members that the rest of the external evidence lane applies to ordinary files.

### One response-set contract

`cloudtainer/tools/oq0266_isolated_response_set_lib.py` is shared by the prefreeze lock command and the postfreeze scorer. Exact fields, safe dispatch content, chronology, responder separation, hashes, and current-response matching no longer have independent interpretations on the two sides of the visibility boundary.

### Exact topology rather than prose intent

The checker and preflight verify exact prefreeze ZIP member order, nested responder ZIP byte equality, postfreeze exclusions, dispatch hashes, and concrete mapping-label absence. The boundary no longer rests on a README instruction alone.

## External methodological pressure

The repair follows two well-established principles without claiming their stronger guarantees.

CONSORT-SPIRIT distinguishes sequence generation, allocation concealment, and assignment implementation, and recommends separating the people who know the allocation sequence from those implementing assignments because failure to do so can introduce bias. Here, the analogous correction is to keep mapping and scoring material unavailable until collection is complete.

The in-toto specification treats step order, actors, and bit-for-bit material/product linkage as separate verification concerns. Rev0383 borrows that shape by linking response, lock, custody, and score artifacts across ordered stages. It does **not** implement in-toto signatures, trusted functionary identity, or authenticated metadata.

NIST experimental-design guidance also reinforces the existing inference clamp: nuisance factors should be blocked where possible and remaining variation randomized. With one different responder per arm, responder identity is confounded with condition, so timing remains descriptive and cannot establish a causal burden advantage.

## Remaining high risks

1. No genuine external response-set lock, four-arm batch, conventional OQ-0266 triplet, or separate human score sheet exists yet.
2. Local clocks can be wrong or manipulated; the checks establish internal chronology consistency, not trusted time.
3. String identifiers and attestations do not prove that responders, collector, custodian, or scorer are genuinely independent people.
4. One observation per arm cannot identify causal operator burden, and the trace arm remains a bounded excerpt rather than the full archive.
5. A collector who opens the full cube before the response-set lock has already violated the boundary; tooling can reject recorded contradictions but cannot erase unrecorded exposure.

## Forward priority

The next high-value action is external execution through the prefreeze dispatch kit, not another layer of admission doctrine. The first real run should preserve the unopened postfreeze ZIP, exact four response files, response-set lock, custody records, score sheets, run manifest, and final summary as one evidence package. Any identity or clock assurance stronger than local attestations should be added at execution time rather than simulated inside the cube.
