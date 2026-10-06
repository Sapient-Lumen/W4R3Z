# DelayBasin OQ-0266 custody-entry and isolated-arm audit — rev0382 working overlay

Source working overlay: `DelayBasin-rev0381-2026.06.18.03.16-failfast-responsefinalize-atomicpublish-schemaclamp.zip`  
Canonical state still named inside the cube: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`  
Status: **tested cloudtainer working overlay, not a canonical DelayBasin promotion**.

## Result

This revision makes two mission-bearing changes rather than adding another readiness registry.

First, it closes a reproduced fail-late hole at the scorer boundary. Rev0381's score-sheet initializer verified response binding and some chronology, but it did not execute the complete current custody contract before creating a score draft. A tampered custody record could therefore reach scoring preparation even when it declared self-custody, denied separation attestations, named forbidden pre-response material, and carried an undeclared field. Rev0382 moves the complete `three-stage-v2` custody interpretation into one shared library and requires it before score-sheet draft publication as well as at final scoring.

Second, it creates a runnable alternative to the old four-packet, one-responder assay. Four opaque responder ZIPs now expose one cue arm each, with a committed hidden mapping and a post-freeze batch kit. This removes within-responder packet carryover and fixed sequence from the semantic comparison. It does **not** turn four different people with one observation each into a causal burden experiment; timing remains descriptive and the global compact gate remains unconfirmed.

During full integration, the runbook cue check also exposed an operational-burden regression: it still demanded every full-trace receipt item on a hot reentry surface. That checker and cue are now clamped to the exact ordered 18-item `hot_current_supports` set, while the complete trace remains in `REVISION-RECEIPT.json`.

No external response, custody record, score sheet, or pilot result was fabricated in this repair.

## 1. Severe score-entry defect reproduced against rev0381

The rev0381 score-sheet `init` path was exercised with a custody record that was otherwise byte-bound to the response but had all of the following defects:

- `custodian_id` equal to `responder_id`;
- `custodian_is_distinct_from_responder: false`;
- `custody_kit_opened_only_after_response_frozen: false`;
- `responder_was_given_only_responder_bundle_before_response: false`;
- pre-response materials naming responder and scorer/post-freeze material together; and
- an undeclared top-level field.

The initializer returned success and emitted a score-sheet draft. The final scorer would reject that record later, but by then scorer effort and a new artifact had already been spent. This was a split contract: custody preparation and final scoring knew more than score entry.

Rev0382's negative canary mutates an otherwise valid record in this manner and requires score-sheet initialization to fail with no output created.

## 2. Shared custody contract and scorer refactor

`tools/priority_zero_external_replay_custody_lib.py` now owns the live `three-stage-v2` contract. It validates:

- exact current custody and attestation field sets;
- exact response-file, responder-bundle, responder-packet, and response-template bindings;
- response finalization identity and time;
- responder/custodian separation;
- the exact sole pre-response material;
- every clean-custody attestation;
- helper-owned timestamp-source fields and stage order; and
- rejection of legacy scorer-stage fields in a current custody record.

The same function is called by custody preparation, score-sheet initialization/finalization, and final scoring. The final scorer was refactored so the live branch delegates once to this library and the remaining compatibility logic is explicitly historical. This removes duplicated current-contract branches that could drift again.

The important behavior change is the failure boundary: invalid custody now fails **before a score draft exists**, not only at the final score command.

## 3. Why the old assay could not answer the burden question

The existing OQ-0266 lane presents sham, compact, baseline, and trace cues to one responder in one fixed packet sequence. Its scorer correctly narrowed the scope in rev0379, but the design still allows earlier packets to teach, prime, or contaminate later answers. Packet order and cue carryover are inseparable from the observed scores and times.

This is a methodological, not documentary, defect. General experimental-design guidance treats randomization and counterbalancing as tools for controlling order effects. Separate LLM-evaluator studies also report non-random position bias and substantial sensitivity to prompt templates. These sources do not validate DelayBasin's assay; they are pressure against interpreting a fixed, co-visible sequence as clean comparative evidence.

Research anchors:

- NIST IR 8040, *Measuring the Usability and Security of Permuted Passwords on Mobile Platforms*, section on experimental design and order effects.
- Shi et al., *Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge*, arXiv:2406.07791.
- *Systematic Evaluation of LLM-as-a-Judge in LLM Alignment Tasks: Explainable Metrics and Diverse Prompt Templates*, arXiv:2408.13006.

## 4. Runnable isolated semantic pilot

`cloudtainer/oq0266-isolated-semantic-pilot/` now contains:

- four responder ZIPs, each containing exactly one opaque arm and no other arm, mapping, answer key, custody template, or scorer intake;
- an exact-byte SHA-256 assignment-plan commitment;
- one post-freeze kit containing all custody, scoring, mapping, and aggregation material;
- per-arm response, custody, and score-sheet templates;
- a completed-run manifest template; and
- a batch aggregator that revalidates all four exact response/custody/score-sheet triplets.

The opaque mapping deliberately does not preserve the canonical packet order. The batch requires four distinct responder IDs and validates one arm per triplet. A synthetic package canary extracts every actual ZIP and runs responder initialization/finalization, custody freeze, score-sheet initialization/finalization, strict per-arm scoring, and batch aggregation. Synthetic answers and scores remain temporary and are explicitly non-evidence.

The pilot's semantic decision boundary is narrow:

- compact must meet its minimum;
- sham and baseline controls must remain below their maxima;
- trace-versus-compact score difference determines support versus continued narrowing; and
- no result can set `global_compact_gate_confirmed` to true.

Operator times are retained only as arm descriptions. With one different responder per arm and `n=1`, responder identity is confounded with condition. The pilot can test isolated semantic recoverability; it cannot identify causal compact-versus-trace burden.

## 5. Commitment substitution defect found during the pilot audit

The first pilot aggregator verified that a supplied assignment plan matched a supplied commitment. That was not enough. After responses froze, a replacement plan and replacement commitment could agree with each other while differing from the mapping commitment that responders actually received.

The sealed design now binds the exact commitment-file SHA-256 into every responder packet. Each response and scorer contract independently bind that packet's bytes. Batch scoring therefore verifies this chain:

`committed assignment plan -> commitment file -> frozen responder packet -> finalized response triplet`

It also checks that the committed arm mapping agrees with that arm's one-row scorer key. A negative canary swaps arm assignments, recomputes a matching plan/commitment pair, and confirms that the batch is rejected because the replacement commitment is not the one frozen into the responder packets.

This is still a digest commitment, not proof of trusted publication time. The delivered revision ZIP and its external SHA-256 sidecar provide the practical pre-run package anchor; they are not a signature or trusted timestamp.

## 6. Receipt coldstore integration repair

The expanded touched-surface trace initially broke the receipt coldstore round-trip at full lint. The hot receipt had changed, but the coldstore still carried hashes and byte accounting for the previous reconstructed receipt. The repair preserved all 125 historical cold keys, recomputed restored-receipt canonical and pretty hashes, and refreshed byte arithmetic through the existing coldstore contract. No historical witness was deleted or silently reclassified.

This matters because a green generated-surface check alone would not have caught the reconstructed receipt mismatch; the full contract did. The coldstore remains a storage optimization rather than a substitute receipt or witness court.

## 7. Runbook hot-cue contract repair

The first full lint after the receipt trace was extended failed because `tools/check_llm_runbook_current_cue_alignment.py` still required every `canon_additions` entry to appear somewhere in the runbook current cue. That policy contradicted the rev0377 hot-cue split: the operator surface was being forced toward a 73-item implementation trace even though the receipt already carries that trace. Its substring checks also admitted accidental partial matches rather than validating the field as a list.

Rev0382 now parses exactly one `Current additions:` field, rejects empty or duplicate entries, and requires exact ordered equality with the bounded `hot_current_supports` list. The runbook cue was reduced from 51 stale entries to the current 18 hot supports. The lossless pre-compaction runbook source remains preserved in `HOT-SURFACE-COMPACTION-ORIGINALS.json`, and `HOT-SURFACE-COMPACTION.json` was refreshed to the new compacted bytes and hashes.

This is a burden reduction, not evidence deletion: the full 75-surface working trace remains in the receipt mirrors and the runbook still carries the current method, question posture, witness slot, derivative warnings, and excluded non-takes.

## 8. Concrete next execution

The old single-responder lane remains available for the missing conventional OQ-0266 triplet. It can produce bounded semantic evidence but cannot answer burden causally.

The stronger pilot begins by distributing these four files to four genuinely separate responders, one ZIP per responder and nothing else:

- `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-7f2c/responder-bundle.zip`
- `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-b91e/responder-bundle.zip`
- `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-d4a7/responder-bundle.zip`
- `cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-e263/responder-bundle.zip`

Only after all four responses freeze should a custodian/scorer open:

`cloudtainer/oq0266-isolated-semantic-pilot/postfreeze-batch-kit.zip`

The remaining work is external execution, not another internal gate.

## Remaining highest risks

- No genuinely external OQ-0266 triplet or four-arm pilot batch exists yet.
- Distinct string IDs are enforced, but real-world identity separation still depends on honest operators and custody records.
- One responder per arm removes within-person carryover but leaves between-person variance and provides no burden identification.
- The trace arm is a bounded trace excerpt, not the full archive.
- Digest commitments and package hashes do not prove trusted publication time, signatures, or independent wall-clock chronology.

## Validation result

The working tree and a freshly extracted candidate package each passed all `216/216` lint checks with zero changed files. Generated-surface drift was clean; source/package comparison found `823` files with no missing, extra, or byte-mismatched entries; cloudtainer preflight reported `0` failures and `0` warnings; the custody fail-before-score and extracted four-arm canaries passed; the post-response commitment-substitution and duplicate-responder batches were rejected; ZIP integrity passed; and no Python bytecode residue remained. The final archive was resealed after recording these results and subjected to the same fresh-extraction checks.

## Non-claim

This audit is not a canonical promotion, clean external replay result, executed four-arm pilot, causal burden result, global compact-default confirmation, independent certification, signed provenance, trusted timestamping, deletion authority, or benchmark authority.
