# OQ-0266 preanswer scoring-policy binding and self-score bypass audit

Date: 2026-06-18  
Working overlay: `rev0384`  
Canonical head preserved inside the cube: `rev0374`

## Executive finding

Rev0383 froze the assignment mapping and all four response bytes before postfreeze work, but it did **not** freeze the rules that decided whether a score was admissible. The one-arm scorer intake remained a mutable postresponse file. The final aggregator trusted whichever boolean separation policy appeared in that file at scoring time.

That was a mission-critical outcome-adaptive evaluation path. After seeing every response, an operator could weaken `requires_distinct_scorer_from_responder`, change each score sheet to name its own responder as scorer, update the scorer-intake hashes, and still receive the positive batch decision `support-isolated-semantic-recovery-pilot`.

The bypass was reproduced against an untouched rev0383 package. Every arm in the accepted synthetic result had `responder_id == scorer_id`. The assignment commitment, all-response lock, custody chronology, and byte-bound score sheets all remained internally consistent. The failure was not missing hash machinery; it was that the wrong object had been committed.

## Heart of the repair

Rev0384 makes the scoring and admissibility rules part of the **preanswer commitment**. Responders still do not see the answer key or assignment mapping. They see only a commitment file whose exact hash is embedded in every one-arm responder packet. That commitment now binds two hidden postfreeze files:

1. the exact assignment plan; and
2. the exact scoring policy, including scorer-separation rules, custody requirements, score-sheet requirements, metric/rationale requirements, decision thresholds, answer-key projections, and the hashes of every executable validation surface used after disclosure.

The policy content remains hidden until all four responses freeze. Its bytes cannot be selected or relaxed after the responses are known without breaking the responder-bound commitment.

## New execution barrier

The live sequence is now:

1. distribute only the prefreeze dispatch kit;
2. collect four tool-finalized responses from four distinct responders;
3. create the immutable all-response lock;
4. open the postfreeze kit;
5. run `verify_oq0266_isolated_postfreeze_policy.py` from the prefreeze kit;
6. verify assignment bytes, policy bytes, every scorer-policy projection, and every committed validator/tool hash;
7. publish an immutable postfreeze policy-verification receipt;
8. only then open custody and scoring stages; and
9. run the final aggregator, which repeats the policy checks against current bytes and requires the exact verification-receipt hash in the run manifest.

Custody or scoring that begins before the policy-verification receipt is now a hard failure. Later scorer or tool substitution is also a hard failure.

## Defense in depth

The final batch scorer no longer relies only on a mutable per-arm boolean to prevent self-scoring. It directly rejects:

- `scorer_id == responder_id`;
- `custodian_id == responder_id`;
- any scorer field added, removed, or changed outside the explicitly enumerated runtime-binding fields;
- any scorer policy projection that differs from the preanswer scoring policy;
- any current scorer hash that differs from the postfreeze verification receipt;
- any committed tool whose current bytes differ from the preanswer policy; and
- any scorer intake that changes during the final validation process.

This duplicates the most mission-bearing separation invariant deliberately. A policy-file bug, helper bug, or future compatibility branch should not silently reopen the original bypass.

## Executable regression set

The ordinary isolated-pilot checker now performs the complete extracted-kit sequence and attacks it. In addition to the rev0383 canaries, rev0384 includes:

- custody before postfreeze policy verification;
- postresponse scorer-policy substitution plus responder self-scoring; and
- strict-JSON exponent overflow (`1e999`) becoming runtime infinity.

The self-score canary recreates the accepted rev0383 exploit: it copies the postfreeze kit, turns off distinct-scorer enforcement in every scorer intake, rebinds every score sheet to the changed scorer bytes, and changes every scorer identity to the corresponding responder. Rev0384 rejects the batch before semantic scoring because the scorer policy no longer matches the preanswer commitment.

## Refactor audit

### One policy projection

`oq0266_isolated_scoring_policy_lib.py` defines one exact split between:

- policy fields that must be selected before response; and
- runtime bindings that can exist only after responder bundles and templates are built.

The builder, postfreeze verifier, final scorer, static package checker, and cloudtainer preflight all use or inspect this same contract. This removes the previous duplicated interpretation of which scorer fields were “just metadata” and which fields could change the result.

### One finite strict-JSON parser

The external scoring tool previously carried a second duplicate-key/nonstandard-number parser. It now delegates to `priority_zero_external_run_artifact_lib.strict_json_bytes`.

That shared parser also closes a less obvious numeric hole: standards-valid JSON such as `1e999` was accepted by Python and converted to positive infinity even though explicit `Infinity` and `NaN` tokens were rejected. `parse_float` now rejects any token that overflows the finite runtime range. Embedded ZIP JSON, ordinary artifact JSON, and final score inputs therefore share the same finite-number boundary.

### Read-once policy binding

The batch scorer loads each scorer intake once for policy comparison and records its exact hash. The triplet validator still consumes a file path, so the aggregator re-hashes the file immediately afterward and rejects any split-time change. This is not an operating-system transaction, but it removes the easy double-read ambiguity and turns an in-process replacement into an explicit failure.

## What this does not solve

1. No genuine external four-person batch or conventional OQ-0266 response/custody/score-sheet triplet exists yet.
2. The verifier receipt is locally attested metadata, not a signature or trusted timestamp. A hostile operator controlling every file and clock can forge a coherent story.
3. Distinct strings do not prove distinct real people, and a scorer may still collude with a responder even when identifiers differ.
4. One different responder per arm still confounds condition with responder identity. Timing remains descriptive and cannot establish causal burden.
5. The trace arm remains a bounded excerpt, not a measured full-archive condition.
6. The full cube remains unsafe for preanswer distribution. A collector who opens it early has contaminated the run even if no artifact records that exposure.

## Forward priority

The next substantive step is a real external run using the prefreeze dispatch kit. The package now fixes assignment and evaluation policy before response and gives operators a fail-fast sequence. Further internal doctrine should be deferred unless the first real run exposes another executable defect.

At execution time, stronger assurance should come from real-world controls rather than more JSON: separate people or accounts, independently preserved original ZIPs, immutable storage or signed hashes, and a witnessable chronology. Those measures would strengthen claims that this cube intentionally continues to leave narrow.

## External design pressure and bounded speculation

This repair is not a formal preregistration system, but the underlying control is the same one emphasized by preregistration research: fix the decision-relevant plan before observing outcomes so later exploratory changes cannot masquerade as confirmatory ones. Nosek et al., “The preregistration revolution,” *PNAS* 115(11), 2018, DOI `10.1073/pnas.1708274114`, describes preregistration as a way to distinguish prediction from postdiction. The Center for Open Science likewise defines preregistration as specifying the study plan in advance and preserving the distinction between planned and unplanned work.

The artifact-chain design is also directionally similar to in-toto layouts. In-toto fixes expected steps, authorized functionaries, and material/product rules in a signed layout, then verifies step evidence against that layout. DelayBasin currently borrows only the weaker structural idea—precommitted steps and byte identities. It does **not** supply in-toto signatures, functionary keys, revocation, or an independent verifier, so the comparison is design pressure rather than an assurance claim.

The direct self-score prohibition is additionally supported by empirical LLM-evaluator work. Wataoka, Takahashi, and Ri report measurable self-preference bias in LLM-as-a-judge settings (`arXiv:2410.21819`). That literature does not prove that this specific pilot would be biased, and the current scorer could be human rather than an LLM. It does make “the responder may also judge itself” an avoidable validity risk rather than a harmless convenience.

The strongest plausible next assurance layer is therefore not another registry: it is a signed or transparency-logged preanswer commitment held by someone who cannot alter the postfreeze policy, followed by original artifact preservation and genuinely separate responder/custodian/scorer accounts. That would convert the present internally coherent chronology from a self-reported story into externally checkable provenance. This is a forward hypothesis, not a property of rev0384.

### Online references consulted

- in-toto, “Getting started”: `https://in-toto.io/docs/getting-started/`
- Nosek, Ebersole, DeHaven, and Mellor, “The preregistration revolution”: `https://www.pnas.org/doi/10.1073/pnas.1708274114`
- Center for Open Science, “Preregistration”: `https://www.cos.io/initiatives/prereg`
- Wataoka, Takahashi, and Ri, “Self-Preference Bias in LLM-as-a-Judge”: `https://arxiv.org/abs/2410.21819`
