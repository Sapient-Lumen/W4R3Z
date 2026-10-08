# Audit — rev0164

## Scope

The audit began from accepted rev0163 and examined the boundary between a committed checkpoint and the first ordinary turn narrated in a fresh context. It also examined the public-information asymmetry noted in the rev0163 direct-upload audit: a long-lived narrator may remember prose that a fresh narrator cannot reconstruct from typed custody alone.

## Finding A164-01 — the capsule was not bound to the eventual turn

**Risk.** A parent could give a fresh narrator the right capsule but the wrong player input, open a director/full turn, change proposal identities, or accept freeform prose through another path.

**Repair.** Added `lacuna.checkpoint-continuation-dispatch.v1` and `checkpoint run next-turn`. The dispatch binds checkpoint/capsule custody, exact input, ordinary packet/proposal template, provider role, save path, and accept command.

**Evidence.** End-to-end tests validate deterministic dispatch, exact role/template binding, recomputed return path/command, schema validation, and successful ordinary-turn accept/preparation/commit.

## Finding A164-02 — the normal path still required several expert-only commands

**Risk.** A human or weaker coordinator had to compile the capsule, create a correctly scoped turn, merge contexts, and hand-build a prompt.

**Repair.** `next-turn` derives cube, audience, actor, head, and least-authority settings from the authenticated checkpoint and opens the qualifying turn itself.

**Evidence.** The CLI help exposes the command; tests show the one-command dispatch equals the lower-level bridge result.

## Finding A164-03 — a stale checkpoint could be used as current continuation state

**Risk.** Another accepted turn after the checkpoint makes the capsule an obsolete description of the live cube.

**Repair.** One-command continuation requires the current cube head to equal the checkpoint post-commit head. The lower-level bridge verifies the turn request base head and live expected head.

**Evidence.** Stale and different-cube continuation tests refuse before dispatch.

## Finding A164-04 — an operator could widen the fresh narrator's authority

**Risk.** A director packet, pair/full topology, anchor grant, or session-control request could expose extra state or give the fresh narrator the wrong contract.

**Repair.** The bridge accepts only a fresh `awaiting-solo-proposal` ordinary `play-turn` with audience-only context and no anchor authority. The one-command path manufactures exactly that shape.

**Evidence.** Focused tests refuse director, non-solo, non-fresh, and session-control turns.

## Finding A164-05 — public prose continuity was advisory and unauthenticated

**Risk.** The fresh condition could lose scene facts that controls retained in context, or a host could paste an edited/selective transcript without a typed relation to accepted turns.

**Repair.** Added `lacuna.public-history.v1` and `history build`. Every source run is fully audited; exact player input and accepted narration are separated from parent-side source custody; both arrays receive canonical digests.

**Evidence.** Tests cover exact JSON/Markdown/CLI output, reverse order, uncommitted runs, mixed cubes, ordinary tampering, and unknown ledger heads.

## Finding A164-06 — artifact-local hashes still allowed a self-consistent forgery

**Risk.** A host could replace accepted prose, recompute the text digests, both array digests, and deterministic history ID, producing a fully self-consistent artifact that never matched the cube.

**Repair.** Added `authenticate_public_history`. It verifies the cube, reloads each immutable source-backed request, authenticates request/input/proposal identity, checks changeset and event boundaries, and authenticates each narration source and content digest.

**Evidence.** A dedicated test constructs a deliberately rehashed forged narration that passes `validate_public_history` but fails ledger authentication with `public-history-ledger-mismatch`.

## Finding A164-07 — the fresh narrator received audit custody it did not need

**Risk.** Sending run IDs, request/proposal IDs, packet/receipt hashes, and event positions to a weaker narrator increased cognitive load and leaked orchestration vocabulary without improving prose continuity.

**Repair.** Added `lacuna.public-history-view.v1`. The parent retains the full authenticated artifact; the continuation embeds only exact ordered public prose, scope identity, and the public-entry digest. All prose is explicitly quoted untrusted story/session data.

**Evidence.** Tests validate the standalone view schema, exact public-entry parity, canonical digest, and absence of `source_custody` from the worker-facing object.

## Finding A164-08 — filename order was not enough to prove chronology

**Risk.** A schema-valid history could reorder or overlap turns, or extend past the checkpoint whose state it was meant to contextualize.

**Repair.** Added immutable head-to-event-sequence validation and requires strict nonoverlap plus `history.last_commit_event_seq < checkpoint_request_event_seq`.

**Evidence.** Public-history and continuation tests exercise chronological refusal and same-cube/audience binding.

## Finding A164-09 — invalid optional history could create a stray turn

**Risk.** If turn creation happened before history validation, a bad history file would fail the command after leaving an authoritative request/run.

**Repair.** Factored `_checkpoint_continuation_event_custody` and invokes it before `begin_turn_run` in the one-command path.

**Evidence.** The one-command test confirms invalid history leaves the target turn root absent.

## Finding A164-10 — chronology logic was starting to duplicate database queries

**Risk.** Public history, continuation, future host artifacts, and tests could implement subtly different head lookup semantics.

**Repair.** Added `Cube.event_sequence(head)` with typed malformed/unknown-head refusal and genesis handling.

## Finding A164-11 — the Markdown continuation handoff omitted the exact return template

**Risk.** The recommended `--format markdown` route showed the least-context input and named `return_contract.template`, but did not print that template. A chat worker or weaker model had to reconstruct the full `lacuna.turn-proposal.v2` shape and prebound identities from surrounding metadata, defeating the self-contained handoff claim.

**Repair.** The Markdown renderer now embeds the exact proposal template as JSON immediately before the parent save/accept command. It explicitly tells the worker to preserve all bound identity fields and change only proposal content allowed by the embedded response contract.

**Evidence.** The managed-checkpoint continuation test asserts that the rendered handoff contains the exact pretty-printed template and its proposal ID; the focused test passes through the real deterministic dispatch builder.

## Finding A164-12 — the outer handoff could accept a self-consistent unsafe starting template

**Risk.** The continuation builder emitted an empty-operation proposal template, but the standalone dispatch validator checked its identity bindings without independently requiring the return format, narration placeholder, message, and empty operation/reveal arrays to remain exact. A rehashed or accidentally rewritten dispatch could therefore pass structural validation with a prepopulated starting proposal, even though ordinary turn acceptance would still enforce the grant.

**Repair.** Centralized the ordinary safe proposal message, made the continuation return format a fixed constant, and require the runtime validator plus Draft 2020-12 schema to preserve the exact narration-only starting shape.

**Evidence.** Focused subtests alter the return format, prepopulate an operation, and replace the narration placeholder; every mutation now fails with `bad-checkpoint-continuation-dispatch`.

## Finding A164-13 — manifest verification did not reject unlisted archive members

**Risk.** `sha256sum -c MANIFEST.sha256` proves that every listed member has the expected bytes, but it does not reject additional archive members. A release candidate demonstrated the failure mode by carrying generated cache files that were absent from the manifest while still passing checksum verification.

**Repair.** Final release acceptance treats the manifest as an allow-list: the ZIP's complete regular-file set must equal the 297 listed members plus `MANIFEST.sha256`, with no duplicate names, cache directories, bytecode, missing files, or extras. `.pytest_cache/` is also excluded from source custody.

**Evidence.** The final archive contains exactly 298 unique regular files, exactly matches that expected set, contains no `__pycache__`, `.pytest_cache`, `.pyc`, or `.pyo` members, and passes full ZIP integrity plus clean-extraction manifest verification.

## Finding A164-14 — one-command success can outlive its printed dispatch

**Risk.** `next-turn` durably opens the ordinary request/run before printing the handoff. If the command succeeds but stdout is lost, blindly rerunning it must not open a second turn or pretend the checkpoint is still current.

**Repair.** The live-head guard makes a blind retry refuse after the first request advanced the cube. The operator guide now makes this durability boundary explicit: use a dedicated `--root`, retain command output, and recover by locating the fresh turn run and invoking the lower-level `checkpoint run continuation` bridge. Do not delete the first run or rebase the capsule.

**Evidence.** The one-command and lower-level bridge tests produce the same deterministic dispatch for the same retained turn; stale-head tests prove that a second creation attempt cannot silently rebase. This is fail-closed recovery guidance, not an atomic filesystem/stdout transaction.

## Refactor assessment

The revision adds no second story state and no new commit engine. Public history is a private host artifact; its view is an even narrower worker artifact. Continuation writes only the ordinary request source/run needed for the next turn; accepted story mutation still passes through the existing turn proposal, exact rollback preparation, event ledger, and receipt path.

The two-run bridge holds locks in fixed checkpoint-then-turn order. Shared sidecar readers and canonical digest functions remain the file-integrity boundary. Provider definitions are thin discovery adapters.

## Residual risks

- A host can omit earlier public turns from a valid history.
- Run IDs and packet/receipt hashes remain sidecar custody and need retained runs for independent re-audit.
- A provider can retain memory or read files despite a fresh-context declaration.
- A parent can send extra material outside the dispatch.
- Exact visible text does not prove its semantic implications were typed or protected.
- Public-history artifacts contain sensitive player text and are not encrypted.
- The one-command path refuses after later cube advancement rather than rebasing.
- Scenario machinery records capsule/context declarations but does not remotely attest them.
- No comparative narrative result is produced by this revision.

## Acceptance disposition

Rev0164 is acceptable when all source and clean-extraction tests pass, all three new schemas validate, provider definitions parse, Markdown links resolve, version/help smoke succeeds, the clean manifest verifies, and focused continuation/public-history tests demonstrate fail-closed chronology, self-consistent forgery refusal, least-context projection, and successful ordinary-turn commit.
