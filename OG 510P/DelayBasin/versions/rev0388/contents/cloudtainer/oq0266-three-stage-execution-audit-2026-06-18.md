# DelayBasin OQ-0266 three-stage execution audit — rev0380 working overlay

Source working overlay: `DelayBasin-rev0379-2026.06.17.23.05-tripletbind-costscope-strictjson.zip`  
Canonical state still named inside the cube: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`  
Status: **tested cloudtainer working overlay, not a canonical DelayBasin promotion**.

## Result

This pass found and repaired a blocking contradiction in the only remaining Priority-0 execution path. The published procedure required the custody record to be frozen before the scorer kit opened, while the custody record itself required `scorer_opened_at` and scorer-intake identity. A truthful operator therefore had to either open scorer material too early or forecast a future scorer event inside an already-frozen record. The clean OQ-0266 run was procedurally impossible as written.

The current path now has three artifact freezes with one-way ownership:

1. the responder freezes the response;
2. a distinct custodian opens the custody kit and freezes a response-bound custody record; and
3. only then does a scorer open the scorer kit, initialize a byte-bound draft, complete the rubric, freeze the score sheet, and run the scorer.

The repair is executable from the standalone ZIPs and is exercised by the live contract checker. It does not manufacture the missing external triplet.

## 1. Critical contradiction reproduced

The prior current contract simultaneously asserted:

- scorer material must remain unopened until after custody-record freeze; and
- custody evidence must contain `scorer_opened_at`, scorer-intake surface, and scorer-intake hash.

Those conditions cannot both be satisfied by an honest chronology. The contradiction was distributed across templates, instructions, scorer validation, and the stale custody-preparation helper, so a prose-only correction would have left split behavior.

Current behavior removes all scorer-stage fields from the current custody contract. Historical records retain their legacy chronology under an explicit compatibility path; they are not silently reinterpreted as current evidence.

## 2. Three-stage contract and artifact ownership

The current `three-stage-v2` contract now assigns fields to the stage that can truthfully know them.

The custody record owns:

- responder and custodian identity;
- response hash and responder-material hashes;
- response-freeze, custody-kit-open, and custody-record-freeze times;
- exact pre-response exposure; and
- clean-preanswer and separation attestations.

The separate score sheet owns:

- scorer identity;
- exact response, custody-record, and scorer-intake hashes;
- scorer-kit-open and scored times;
- every metric score, matching rationale, and packet note; and
- scoring-stage separation attestations.

The scorer now rejects legacy scorer-stage fields when a record claims the current custody contract. This prevents a mixed-schema record from carrying an ignored or contradictory scorer timestamp while still being admitted as current.

## 3. Standalone custody execution repaired

`tools/prepare_priority_zero_clean_response_custody_record.py` was rewritten around the current responder bundle and evidence template. It now:

- runs from the extracted post-freeze custody kit;
- parses strict UTF-8 JSON and rejects duplicate keys/non-standard constants;
- derives responder identity from the frozen response;
- verifies the responder-observed bundle and packet hashes against the post-freeze template;
- reconciles per-packet and total operator cost;
- rejects self-custody and impossible response/custody chronology;
- requires an explicit `--attest-clean-preanswer` switch rather than manufacturing clean booleans silently; and
- refuses to overwrite a possibly frozen output unless explicitly forced.

The custody kit now contains this helper, its exact template, and its README only.

## 4. Separate score-sheet execution added

The scorer kit now contains `tools/prepare_priority_zero_external_replay_score_sheet.py` with two commands:

- `init` binds the exact response, custody-record, and scorer-intake bytes after custody freeze; and
- `finalize` verifies that all binding fields remained unchanged, validates every score/rationale/note, records scorer chronology, and writes a new final artifact.

The helper rejects responder self-scoring, binding drift, duplicate keys, booleans, non-finite or out-of-range scores, incomplete metric maps, missing rationales, missing notes, and impossible scorer chronology. Final clean-scoring attestations require an explicit switch.

The live checker now extracts both standalone kits and performs the actual custody → score-draft → score-finalization → scoring command sequence. The positive fixture is no longer assembled by hand inside the checker.

## 5. Operator-command and topology audit

A stale hot command in `context-pack.json` omitted the required `SCORE_SHEET` argument even though the Makefile rejected such an invocation. `tools/gen_context_pack.py` now emits the complete triplet command, and a new validation tool compares the generated command, Makefile guards, and scorer README tokens.

The handoff manifest now records the exact post-freeze sequence, current custody/scoring contract versions, and two-operator minimum. Both preparation helpers are explicitly excluded from responder-visible material. The cloudtainer preflight now checks exact custody- and scorer-kit membership rather than only noticing missing scorer members.

## 6. Refactor boundary

`tools/priority_zero_custody_timeline_lib.py` now has one explicit current path and one historical compatibility path:

- current: responder start ≤ responder completion ≤ response freeze ≤ custody-kit open ≤ custody-record freeze;
- historical: responder start ≤ responder completion ≤ response freeze ≤ scorer open in custody record.

The scorer adds the remaining current order from the separate score sheet:

- custody-record freeze ≤ scorer-kit open ≤ scored.

This avoids duplicating one seven-event chronology across two artifacts while preserving archived canaries. Current evidence is not allowed to smuggle legacy scorer fields back into custody.

## 7. Research pressure and residual validity risk

Research on LLM-as-a-judge position bias supports continued caution about the fixed, co-visible packet order; the current assay remains bounded semantic evidence rather than a causal compact-versus-full comparison. NIST guidance on identifying and managing bias in AI also supports treating evaluation procedure and human/operator effects as part of the evidence claim rather than incidental paperwork.

Neither source validates DelayBasin’s protocol. They reinforce the decision not to upgrade this repaired execution path into a global burden claim.

## Remaining highest risks

The principal unfinished object remains unchanged: no genuinely external response, distinct-custodian record, and separate post-response score sheet have yet been collected and imported.

Three residual limitations remain explicit:

- all four packet cues are still co-visible to one responder and presented in fixed order;
- packet-delta remains a trace excerpt, not a measured full-archive condition; and
- timestamps are operator attestations, not trusted third-party timestamping.

The next substantive move is therefore operational, not another gate: give only the responder bundle to a fresh responder, freeze the output, run the custody kit with a distinct custodian, then open the scorer kit and complete the score sheet with a scorer distinct from the responder. The custodian may also score, preserving a two-person minimum.

## Validation target

Before packaging, this overlay is required to pass:

- the extracted standalone custody helper;
- the extracted standalone score-sheet `init` and `finalize` helpers;
- the extracted standalone scorer command;
- negative canaries for implicit custody attestation, early scorer-kit opening, scoring before scorer-kit opening, legacy scorer fields in current custody, response self-scoring, split-brain files, score-shape defects, cost defects, and ambiguous JSON;
- the complete generated-surface and lint suite without mutating the target tree; and
- a fresh-extraction repeat of the same checks.

## Non-claim

This audit is not a clean external replay result, independent certification, global compact-default confirmation, causal compact-versus-full burden evidence, trusted timestamping, deletion authority, benchmark authority, or a canonical DelayBasin promotion.
