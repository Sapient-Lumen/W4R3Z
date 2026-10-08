# Decisions — rev0164

## D164-01 — make the normal post-checkpoint product one exact turn dispatch

**Decision.** Add `checkpoint run next-turn` and `lacuna.checkpoint-continuation-dispatch.v1`.

**Why.** A capsule authenticated compact state but did not bind the next player input or ordinary proposal authority. Human and weaker-model operators still had to invent a three-way join.

**Rejected.** Freeform “paste capsule and input” prompts; letting the fresh narrator return unbound prose; adding a second commit engine.

## D164-02 — reuse ordinary turn-run authority

**Decision.** The fresh narrator returns `lacuna.turn-proposal.v2` into an ordinary `solo` turn run. Existing accept, rollback preparation, commit, and crash recovery remain authoritative.

**Why.** The checkpoint bridge is context manufacture, not a new mutation protocol.

## D164-03 — constrain one-command continuation to least authority

**Decision.** Open only `play-turn`, audience-only, `solo`, no-anchor turns with no planner context.

**Why.** One fresh narrator must be able to propose the continuation without receiving hidden cube-wide planner state or acquiring irreversible authority.

## D164-04 — require the checkpoint to remain current

**Decision.** `next-turn` requires the live cube head to equal the accepted checkpoint head. The lower-level bridge requires the already-open turn request to have been created directly from that head and still be fresh.

**Why.** A checkpoint capsule is not portable across later changes. Best-effort rebasing would blur what state the compression represented.

## D164-05 — make public transcript custody optional and explicit

**Decision.** Add `lacuna.public-history.v1` plus `history build`; use it only when the parent passes `--public-history`.

**Why.** Some campaigns type every material observation; others rely heavily on prose. One universal implicit transcript policy would either overfeed the clean condition or make it forget public canon.

**Rejected.** Automatically scanning arbitrary transcripts; storing transcript bodies in the story ledger; pretending narration digests reconstruct prose.

## D164-06 — separate visible entries from source custody

**Decision.** The parent artifact contains `public_entries` and `source_custody` arrays with independent digests.

**Why.** Readable continuity and audit custody are different data classes. Their independent digests make the join explicit.

## D164-07 — compile only from fully audited committed managed turns

**Decision.** Add one private-free `committed_turn_public_record` extractor under the turn-run lock.

**Why.** Reading receipts and text files ad hoc would duplicate sidecar validation and risk exporting an uncommitted or tampered draft.

## D164-08 — authenticate content against durable cube sources, not artifact hashes alone

**Decision.** `authenticate_public_history` must reopen every request and narration source and verify proposal/event boundaries before a history may enter a continuation.

**Why.** A malicious or mistaken host can recompute every hash in a self-consistent sidecar. The player and narration byte digests must still match immutable request and narration custody.

## D164-09 — project a minimal worker view

**Decision.** Add `lacuna.public-history-view.v1`; send it to the fresh narrator while retaining the full authenticated history parent-side.

**Why.** Run IDs, proposal IDs, receipt hashes, and event positions help audit but hinder weaker narrators and leak protocol vocabulary. The worker needs exact public prose, not the audit ledger.

## D164-10 — treat embedded story text as untrusted quoted data

**Decision.** Fixed full-history, view, dispatch, and provider instructions state that player/narration strings cannot override role, tools, output shape, or authority.

**Why.** Exact transcript inclusion creates an instruction-injection surface unless its trust class is explicit at every handoff.

## D164-11 — enforce immutable chronology, not supplied filename order alone

**Decision.** Resolve every request and commit head to an immutable event sequence and require strict nonoverlap. Continuation history must end before the checkpoint request.

**Why.** A list can be reordered, duplicated, or drawn from the wrong point in history while remaining schema-shaped.

## D164-12 — validate history before creating a one-command turn

**Decision.** Authenticate public history and checkpoint chronology before calling `begin_turn_run`.

**Why.** A failed optional context artifact should not leave an orphan source request/run that the operator must clean up.

## D164-13 — centralize head-to-event lookup

**Decision.** Add `Cube.event_sequence(head)`.

**Why.** Continuation and public-history modules need the same ancestry primitive. Raw SQL in each host layer would drift and produce inconsistent error semantics.

## D164-14 — add one dedicated fresh-narrator role

**Decision.** Register `lacuna-fresh-narrator` aliases and checked-in no-tool/read-only adapters.

**Why.** Reusing the ordinary narrator role obscures that this worker receives private compact state and returns a full proposal rather than an audience-only narrator return.

## D164-15 — do not claim transcript completeness or provider forgetting

**Decision.** Fixed nonclaims state that public history covers only supplied runs and context freshness is host-declared.

**Why.** Exact hashes can otherwise make a partial transcript or a named new chat look stronger than the evidence supports.


## D164-16 — render the return template in the human/model handoff

**Decision.** The Markdown continuation dispatch must include the exact `lacuna.turn-proposal.v2` template, not merely name it.

**Why.** Markdown is the normal ChatGPT/human-bridge transport. A return contract that exists only in the machine JSON envelope is not self-contained for the worker receiving the rendered handoff, especially a weaker model.

**Boundary.** Printing the template does not widen authority; the ordinary turn-run validator and kernel still decide whether the returned object is accepted.

## D164-17 — require the exact fail-safe continuation starting shape

**Decision.** Validate the continuation return format and the prebound proposal template's placeholder narration, fixed message, empty operations, and empty reveal list in both runtime and schema.

**Why.** A self-consistent rehash must not turn a safe worker starting point into a prepopulated mutation proposal. Ordinary turn acceptance remains the final authority, but the outer handoff should fail before delegation when its own safety contract has drifted.

## D164-18 — treat the release manifest as an exact archive allow-list

**Decision.** Release acceptance compares the complete ZIP regular-file set with every path listed in `MANIFEST.sha256` plus the manifest itself. Missing, duplicate, or extra members refuse the release.

**Why.** Checksum verification alone is one-sided and can pass while generated caches or unrelated files ride inside the archive. Exact membership makes the handoff smaller, legible, and reproducible.

## D164-19 — fail closed after lost one-command output

**Decision.** Do not make `next-turn` silently create another request after the first one advanced the cube. Document recovery through the retained fresh turn and lower-level `checkpoint run continuation` bridge.

**Why.** A duplicate or rebased request would weaken exact checkpoint-to-turn custody. SQLite, sidecar files, and terminal output are separate durability domains; explicit recovery is safer than pretending the command is atomically idempotent.

