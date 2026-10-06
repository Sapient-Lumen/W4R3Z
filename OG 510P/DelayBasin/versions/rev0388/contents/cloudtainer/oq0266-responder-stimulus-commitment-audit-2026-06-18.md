# OQ-0266 responder-stimulus commitment and runtime-rebinding audit

Date: 2026-06-18  
Working overlay: `rev0385`  
Canonical head preserved inside the cube: `rev0374`

## Executive finding

Rev0384 fixed the hidden assignment and scoring policy before response, but it did **not** fix the bytes a responder actually saw. The commitment excluded responder-packet, response-template, and responder-bundle identities as postbuild runtime bindings. Those hashes could therefore be replaced together after the nominal commitment while leaving the committed plan and policy unchanged.

This was a critical experimental-integrity gap. A collector could substitute a same-arm packet containing answer-key leakage, update the packet/template/bundle hashes in the dispatch and postfreeze surfaces, finalize a matching response from the altered bundle, and still obtain a positive isolated-pilot result. The system proved that its scoring rules were preselected while failing to prove that the tested stimulus was preselected.

## Reproduced rev0384 exploit

The bypass was reproduced end to end against the untouched rev0384 package:

1. The prefreeze and postfreeze kits were extracted.
2. `arm-7f2c`'s responder packet was changed to disclose that the hidden expected score was `17` and that the compact posture was expected.
3. The response template was rebound to the changed packet hash, and the one-arm responder ZIP was rebuilt.
4. The dispatch manifest's bundle, packet, and template hashes were updated.
5. Matching postfreeze packet/template/custody/scorer runtime bindings were updated without changing the committed assignment plan or scoring policy.
6. Four tool-finalized responses, the all-response lock, policy-verification receipt, custody records, and score sheets were produced through the shipped commands.
7. Rev0384 returned `support-isolated-semantic-recovery-pilot`.

The altered compact packet SHA-256 was `e14c50df2cdc9ece2f19130ddf9a7ac9c1553b944495ef0fb668048a4ef419c1`; the rebuilt responder bundle SHA-256 was `aeb541696bcda4a48fbf8c2374c3fac87a63147cfd25058d800d2a81af389a2d`. The accepted synthetic scores were compact `17`, sham `4`, baseline `2`, and trace `16`.

This was not a parser edge case. It was an omission from the object committed before outcomes existed.

## Repair: commit the exact responder-visible stimulus

Rev0385 introduces `assignment-plan-policy-stimulus-v2`. The preanswer commitment now fixes:

- exact assignment-plan bytes;
- exact scoring-policy bytes; and
- one canonical digest for every complete responder-visible packet.

A responder packet embeds the commitment hash, so hashing the complete packet directly would create a self-reference. The new projection excludes **only** `assignment_commitment_sha256`; every other responder-visible field remains committed, including cues, instructions, arm identity, paths, boundaries, timestamps, and non-claims. Canonical strict JSON is used before SHA-256 calculation.

The packet's ordinary file hash and bundle hash remain runtime bindings. They can change for legitimate rebuilding only when the packet projection remains identical. A changed cue can no longer be legalized by merely updating the surrounding runtime hashes.

## Fail-fast enforcement across the real execution path

The exact packet-projection map is checked at every consequential boundary:

1. **Build:** packet drafts are projected before the commitment is written; the commitment hash is then inserted, and the builder proves that the projection did not change.
2. **Dispatch:** each row carries the committed packet-projection digest alongside ordinary packet/template/bundle hashes.
3. **Response-set lock:** the collector opens the actual nested responder ZIP, parses the actual packet, recomputes its projection, and rejects any disagreement before validating or freezing the response.
4. **Postfreeze verification:** the disclosed packet and dispatch bytes are rebound to the same preanswer projection map before custody or scoring may start.
5. **Final aggregation:** the scorer independently recomputes every packet projection and revalidates the response-set lock and policy-verification receipt.

The response-set contract is now `all-arms-freeze-v2`; the policy-verification contract is `postfreeze-policy-verification-v2`. Both carry the projection map rather than relying on narrative claims about stimulus stability.

## Executable regression, not registry prose

The ordinary isolated-pilot checker now constructs the real attack:

- copies the extracted prefreeze kit;
- modifies one responder-visible packet with hidden-target leakage;
- updates the matching template, nested bundle, and dispatch runtime hashes;
- produces a valid finalized response from that altered bundle; and
- attempts to create the four-response lock with the other three valid responses.

The lock must fail with `responder packet projection disagrees with the preanswer commitment`, and it must publish no output. This canary would pass through a system that merely compared the altered response with the altered runtime hashes, so it protects the substantive preanswer boundary rather than a superficial field name.

## Audit and refactor

### One commitment interpretation

`cloudtainer/tools/oq0266_isolated_commitment_lib.py` is now the sole live definition of:

- the commitment record and exact fields;
- the packet-projection scheme;
- canonical serialization;
- arm-set requirements; and
- plan, policy, and stimulus digest validation.

The builder, response-set lock, postfreeze verifier, final aggregator, package checker, and cloudtainer preflight use this contract. Rev0384 had commitment interpretation split between the policy library, lock tool, verifier, scorer, and preflight. Consolidation removes a recurrent source of stale contract versions and partial checks.

### Preflight no longer hard-codes the previous contracts

The preflight previously embedded `all-arms-freeze-v1` and `postfreeze-policy-verification-v1`, so the repaired package initially reported itself inconsistent. It now imports the live contract constants and validates actual packet projections against the shared commitment library. The new commitment library is also required in both prefreeze and postfreeze kit topologies.

### Runtime hashes demoted to their correct role

Bundle, packet-file, and template hashes still bind a response to the bytes used during finalization. They are no longer treated as evidence that those bytes were fixed before response. The preanswer projection answers that separate question. This distinction prevents a coherent post-hoc rebinding from masquerading as preregistered stimulus identity.

## What remains unresolved

1. No genuine four-person isolated batch or conventional OQ-0266 response/custody/score-sheet triplet exists.
2. The commitment has no independent publication timestamp, signature, transparency-log entry, or third-party custody. An operator who controls every file before distribution can still construct a different coherent package.
3. Distinct string identifiers do not prove distinct real people or non-collusion.
4. Local process clocks are chronology observations, not trusted time.
5. One responder per arm cannot identify causal operator burden; timing remains descriptive.
6. The trace condition remains a bounded excerpt rather than a measured full archive.

## Forward priority

The next highest-value action is external execution, not another internal contract. Before distributing the first real arm, preserve the exact prefreeze kit SHA-256 outside the cube with a separate person or append-only service. Then distribute only the nested one-arm bundles, retain their original bytes, and follow the lock → policy verification → custody → scoring sequence without opening the full cube.

Further internal changes should be triggered by a reproduced execution defect or by evidence from the first real run. The present repair makes the stimulus fixed enough for that run; it does not substitute for the run.

## External design pressure and bounded speculation

The Open Science Framework describes preregistration as posting a time-stamped, read-only study plan before data collection or analysis and recommends making design and analysis decisions before viewing data. The rev0384 defect shows that “study plan” must include the actual treatment material: freezing only hypotheses and scoring rules still permits outcome-adaptive stimulus replacement.

In-toto's official model connects steps through authorized materials and products and verifies artifact operations against a predefined layout. SLSA provenance similarly distinguishes an output artifact from the input materials used to produce it, while explicitly noting that provenance still depends on trust in the builder. Rev0385 borrows that narrower lesson: bind the actual material consumed by the responder, not only the downstream evaluator policy.

DelayBasin does not implement OSF registration, in-toto signatures/layout verification, or SLSA provenance. The comparison is design pressure, not a compliance or assurance claim. A plausible later assurance layer is an externally timestamped digest of the prefreeze kit plus signed per-stage receipts; that should be considered only after a real run demonstrates that the present operator flow is usable.

### Online references consulted

- Open Science Framework Help, “Welcome to Registrations & Preregistrations,” updated 2026-06-09.
- Center for Open Science, “Preregistration.”
- in-toto, “Getting started” and the in-toto specification's artifact rules.
- SLSA, “Provenance” and “in-toto and SLSA.”

## Validation status

The delivered working tree and a fresh extraction of the named package were checked with the complete `217`-step lint suite, the extracted isolated-pilot attack canaries, the cloudtainer preflight, ZIP integrity testing, source/package byte comparison, and whole-tree pre/post-lint hashing. The final package contains `842` files, with no Python bytecode residue and no lint-induced file changes. The full receipt trace is `96` surfaces while the operator-facing hot cue remains `18`.
