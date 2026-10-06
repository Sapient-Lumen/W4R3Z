# DelayBasin OQ-0266 fail-fast response execution audit — rev0381 working overlay

Source working overlay: `DelayBasin-rev0380-2026.06.18.01.02-threefreeze-custodyrun-commandtruth.zip`  
Canonical state still named inside the cube: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`  
Status: **tested cloudtainer working overlay, not a canonical DelayBasin promotion**.

## Result

Rev0380 made the response → custody → scorer chronology truthful, but the first stage was still not executable as a controlled freeze. A responder had no bundled initializer/finalizer, and the custody helper treated timestamps, hashes, positive packet costs, and identity as sufficient evidence that a response was complete. That meant a distinct custodian could spend effort and freeze evidence around a response that the final scorer would reject later for empty required answers, missing clean attestations, undeclared fields, or provenance drift.

Rev0381 moves the complete response contract to the responder boundary. The standalone responder ZIP now initializes a hash-bound draft and refuses to finalize it until every required answer and cost is complete, the template shape is exact, helper-owned provenance fields remain unchanged, and the responder explicitly attests clean pre-answer separation. Custody reruns the same validator against the exact finalized response before writing any evidence. The score-sheet helper and final scorer rerun it again. Bad response runs now fail before a custodian or scorer is consumed.

No external response, custody record, or score sheet was fabricated in this repair.

## 1. Critical fail-late defect reproduced against rev0380

The rev0380 custody helper was executed against a synthetic response with:

- all seven required answer fields empty in all four packet rows;
- all three responder clean-separation attestations still `null`;
- no responder-side finalization state or artifact record; and
- only structurally valid identity, timestamp, bundle/packet hash, and positive-cost fields.

The old helper returned exit code `0` and wrote a custody record. Its validator inspected packet cost but did not inspect answer completeness, clean responder attestations, exact template shape, or a tool-owned response freeze. This was not merely a missing convenience command: it permitted invalid work to advance across an operator boundary and made rejection unnecessarily late and expensive.

The current regression suite preserves this reproduction as a fail-before-custody canary. Removing an answer from an otherwise complete draft must fail in the extracted responder kit, and no frozen-response output may appear.

## 2. Responder-side execution now exists

The responder bundle now includes:

- the responder packet;
- the response template;
- responder instructions;
- `tools/prepare_priority_zero_external_replay_response.py`;
- a scorer-key-free shared response-contract validator; and
- small strict-artifact primitives used by all three stage helpers.

The responder runs `init` before answering. The helper records the responder identity, the exact original responder-ZIP digest, the exact packet digest, and a local process-clock start time. The responder edits only packet answers and cost fields. The `finalize` command then:

1. rejects missing, placeholder, reordered, extra, or malformed answer rows;
2. reconciles positive per-packet effort with the run total;
3. verifies that the same bundle and packet are being finalized;
4. verifies that helper-owned start/provenance fields were not changed;
5. requires explicit clean-preanswer attestation and exposure notes;
6. records completion/finalization from the helper clock; and
7. publishes a new non-clobbering, read-only response candidate.

Manual `run_completed_at` and `response_frozen_at` arguments are gone. The response artifact itself now owns those values.

## 3. One shared response contract, four enforcement points

`tools/priority_zero_external_replay_response_lib.py` is safe to ship to the responder because it contains no scorer key, expected outcome, current expected bundle digest, or prior submission. It enforces the current `responder-finalize-v1` contract at four points:

- responder finalization;
- custody preparation;
- score-sheet initialization/finalization; and
- final scoring.

The validator requires exact top-level, responder-stage, response-artifact, and packet-row field sets. This closes a class of hidden-field and split-interpretation defects where one stage could ignore data that another stage later consumed. It also binds `draft_created_at` to `run_started_at` and `response_artifact.finalized_at` to `run_completed_at`.

Custody can no longer accept an answer-complete but unfinalized draft. Scoring can no longer rely on a weaker response interpretation than the responder and custodian used.

## 4. Artifact publication refactor

The three preparation tools previously duplicated strict JSON parsing, timestamp handling, digest logic, and check-then-write output behavior. Rev0381 consolidates those primitives in `tools/priority_zero_external_run_artifact_lib.py`.

Final artifacts are now published by writing and `fsync`-ing a same-directory temporary file, then atomically hard-linking it into a previously absent target name. An existing target causes an atomic failure rather than a race-prone existence check followed by overwrite. Drafts remain writable; finalized response, custody, and score-sheet artifacts are emitted without write bits to reduce accidental post-freeze edits.

This is operational hardening, not cryptographic immutability. A sufficiently privileged local actor can still alter permissions or replace files, and the local filesystem clock is not an independent timestamp authority. Exact byte hashes and downstream rebinding remain the evidentiary mechanism.

The shared numeric validator also now handles oversized integer conversion failures as contract errors instead of uncaught exceptions.

## 5. Standalone-kit and command audit

The responder, custody, and scorer ZIPs are rebuilt from exact member lists and checked after extraction. The positive contract path is no longer assembled by the checker. It executes:

1. responder-kit `init`;
2. responder-kit `finalize`;
3. custody-kit record creation;
4. scorer-kit score-sheet `init`;
5. scorer-kit score-sheet `finalize`; and
6. scorer-kit final scoring.

The checker also verifies that finalized response, custody, and score-sheet files are non-writable at creation. Negative canaries cover incomplete answers, provenance drift, hidden fields, unfinalized responses, implicit attestations, overwrite attempts, chronology inversion, self-scoring, score/rationale defects, cost defects, split-brain files, and ambiguous JSON.

The Makefile and current instructions no longer ask operators to invent stage timestamps. The only human-supplied run content is identity, answer/cost content, exposure notes, rubric judgments, and explicit attestations.

## 6. Research pressure and interpretation

SLSA and in-toto provenance models provide a useful general design pressure: bind exact artifact identities to the steps and actors that produced them, then verify those bindings at later gates. Rev0381 follows that pattern at a small local scale. It does not claim SLSA conformance, signed attestations, or a trusted timestamp service. Explicit timezone-offset timestamps improve parseability and ordering checks, but local helper clocks remain operator-environment observations rather than independent proof of wall-clock truth.

This is an architectural analogy, not external validation of DelayBasin's assay.

## Remaining highest risks

The principal missing object is unchanged: OQ-0266 still has no genuinely external finalized response, distinct-custodian record, and separate post-response score sheet.

The current assay also remains bounded:

- all four packet cues are co-visible to one responder and appear in fixed order;
- packet-delta is a public-trace excerpt, not a measured full-archive condition;
- file permissions are an accidental-edit guard, not tamper-proof storage; and
- helper timestamps are locally observed, not independently witnessed.

The next mission-bearing act is an actual clean handoff through the three standalone kits. Another internal gate is not a substitute for that run.

## Validation target

Before packaging, this overlay must pass the complete generated-surface and lint suite from both the working tree and a fresh extraction, with no file changed by lint, no bytecode residue, exact source/package parity, standalone-kit execution, ZIP integrity, and cloudtainer preflight with zero failures or warnings.

## Non-claim

This audit is not a clean external replay result, independent certification, cryptographic provenance, trusted timestamping, global compact-default confirmation, causal compact-versus-full burden evidence, deletion authority, benchmark authority, or a canonical DelayBasin promotion.
