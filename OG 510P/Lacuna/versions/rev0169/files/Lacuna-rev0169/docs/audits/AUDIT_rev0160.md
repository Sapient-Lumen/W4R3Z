# Audit — rev0160

## Scope

This audit began from the accepted rev0159 artifact and asked a narrower operational question: can a recipient actually walk the source-bound generator → provenance-blind judge → winner-only compressor → verifier protocol across several model calls, providers, processes, or chats without privately inventing resume state, route custody, retry rules, or commit recovery?

The audit covered managed checkpoint state, fixed provider routing, invocation custody, sidecar integrity, exact chain reconstruction, source-cube binding, terminal refusal, direct and historical commit recovery, provider/ChatGPT entrance legibility, and repeated-audit cost. It did not treat model identity, context isolation, creativity, scoring validity, or comparative narrative improvement as kernel properties.

## Parent baseline

Rev0159 supplied the complete lower-level checkpoint exchange: request purpose, protected-state freeze, exact-card cardinality, bounded rollout beats, provenance-blind scoring, deterministic winner selection, winner-only compression, parent assembly, advisory verification, kernel rollback review, and exact current/historical commit recovery. It passed 216 tests, but the operator still had to retain all filenames, routes, stage order, failed calls, and resume position outside the cube.

## Finding A160-01 — the checkpoint walk had no authoritative resume state

**Risk.** The exchange objects were individually strict, but a multi-call operator could still lose track of which role was current, which files were authoritative, which output had been accepted, or what command came next. A fluent model or human could invent a plausible but wrong continuation.

**Repair.** Added `lacuna.checkpoint-run.v1` and the nested `checkpoint run begin/status/recover/dispatch/accept/record-failure/commit` CLI. One strict `run.json` binds source/cube/run identity, exact artifact topology, status, fixed routes, invocation references, next action, and nonclaims. Derived `NEXT.md` exposes one owner, one complete input, one schema, and one command.

**Evidence.** Managed-run tests walk every state, reject wrong-stage and cross-run returns, verify exact topology, exercise pointer-only recovery, and reach both terminal refusal and committed states.

## Finding A160-02 — provider routes could drift between stages or retries

**Risk.** The lower-level dispatch accepts a route at each invocation. A host could accidentally or strategically relabel later stages, making provider comparisons and invocation histories ambiguous.

**Repair.** Managed begin fixes a complete role-to-provider map for generator, judge, compressor, and verifier. The current dispatch is recomputed from the retained card and fixed route. Empty maps and empty per-role overrides are refused rather than silently defaulted.

**Evidence.** Tests exercise heterogeneous ChatGPT/Codex/Claude Code/Gemini CLI routing, exact alias selection, self-contained dispatch, empty-route refusal, and fixed-route relabelling refusal.

## Finding A160-03 — accepted and failed model calls had no durable custody

**Risk.** A host could retry, cherry-pick, or replace calls without any structured record connecting a role card to the accepted output. A timeout and a malformed return were operationally indistinguishable from “no call happened.”

**Repair.** Added ordered `lacuna.checkpoint-invocation-receipt.v1` sidecars. Each receipt binds run, checkpoint, sequence, attempt, role, fixed provider route, agent alias, exact card digest, exact deterministic dispatch digest, expected output schema, host-declared model/version/ID/timing, and either one retained accepted output or one failure class/message. Failed attempts do not advance. Every retained role output requires exactly one accepted receipt.

**Evidence.** Tests cover failed-then-accepted generator attempts, sequence/attempt numbering, missing accepted receipt, semantically rehashed provider relabelling, role ordering, schema validation, and no post-accept attempt for the same role.

## Finding A160-04 — sidecar security primitives were duplicated

**Risk.** Turn runs already had descriptor-stable reads, link checks, size bounds, path resolution, owner-only locks, and shell quoting. Copying that code into checkpoint runs would create two security-sensitive implementations that could drift.

**Repair.** Extracted shared primitives into `src/lacuna/sidecars.py`: canonical JSON digesting, bounded descriptor reads, strict JSON/text reads, sidecar-directory resolution, lock creation/authentication, nonblocking advisory locking, and shell-command rendering. Turn runs and checkpoint runs now use the same implementation.

**Evidence.** Existing turn-run integrity/locking tests and new checkpoint symlink/integrity tests pass against the shared module. The turn-run mock target was updated to the shared `os.lstat` boundary.

## Finding A160-05 — a managed committed run needed independent receipt authentication

**Risk.** Retaining a schema-shaped checkpoint receipt and updating its manifest digest would not by itself prove that narration, embedded turn receipt, selection evidence, review, and durable change still agreed.

**Repair.** Added public `validate_checkpoint_commit_receipt` plus an internal validated-chain helper. Managed audit reauthenticates the exact commit receipt against the source request, proposal, review, embedded turn receipt, narration, cube verification, and current or reconstructed durable event chain.

**Evidence.** A test edits committed narration, recomputes both JSON and manifest digests, and still receives `bad-checkpoint-commit-receipt`. Direct, same-input retry, crash recovery, and later-head recovery remain exact and duplicate-free.

## Finding A160-06 — the caller could name a cube path different from the open cube object

**Risk.** A host API could freeze a request from one `Cube` while writing a different `resolved_cube_path` into the managed manifest. Later audit/commit would then follow a path the source object never authorized.

**Repair.** `begin_checkpoint_run` resolves both the supplied path and `cube.root` with `strict=True` and requires exact equality before creating the run root. The manifest stores the bound canonical path.

**Evidence.** A dedicated test opens one cube, supplies another valid cube path, receives `checkpoint-run-cube-path-mismatch`, and observes no run root.

## Finding A160-07 — ordinary input validation could leave a run-shaped orphan

**Risk.** Creating the directory before validating checkpoint policy or manufacturing the first source/card objects could leave an apparently meaningful run after a normal validation failure.

**Repair.** Begin now verifies and manufactures the complete source request plus generator card before sidecar publication. Only an actual interruption during filesystem publication can leave an incomplete directory.

**Evidence.** An invalid candidate count receives `bad-checkpoint-policy` and creates no run root.

## Finding A160-08 — malformed invocation topology could leak an untyped Python error

**Risk.** A non-list `invocations` field reached `require_list` outside a Lacuna error boundary, potentially producing an inconsistent CLI failure mode during forensic audit.

**Repair.** The managed invocation audit now converts the validation failure to `bad-checkpoint-run`.

**Evidence.** A manifest with an object in place of the invocation list fails as a typed `LacunaError`.

## Finding A160-08b — the invocation ceiling could have failed after publication

**Risk.** The manifest schema permits at most 1,000 invocation references. If capacity were checked only by the audit performed after a transition, a 1,001st failure or accepted attempt could write a receipt and invalid manifest before reporting the limit.

**Repair.** Centralized the limit as `MAX_INVOCATIONS` and enforce it while manufacturing the next receipt, before any receipt or manifest write.

**Evidence.** The malformed-invocation test now also presents an audited run at capacity through the public failure-record path and verifies `checkpoint-run-invocation-limit` plus byte-identical authoritative files.

## Finding A160-09 — repeated committed-run audit duplicated expensive exact preparation replay

**Risk.** Commit, committed audit, and idempotent retry each revalidated the full chain and then repeated the most expensive exact preparation path inside receipt validation, making an otherwise small managed run needlessly slow.

**Repair.** Split receipt checking into a public full-chain validator and a package-internal validator that is callable only after the caller has already validated the complete request/proposal/review chain. This removes duplicate preparation replay without trusting an unvalidated receipt or weakening the durable-change comparison.

**Evidence.** Representative local timings improved from roughly 5.5 seconds to 3.8 seconds for commit, 2.5 to 1.4 seconds for committed audit, and 2.2 to 1.4 seconds for idempotent commit retry on the same fixture. These are development measurements, not cross-machine performance guarantees.

## Finding A160-10 — refusal, pointer repair, and version boundaries needed to be explicit

**Risk.** An operator could edit a verifier refusal into a pass, treat `NEXT.md` as authority, or expect a new executable to reinterpret an old managed run.

**Repair.** `verifier-refused` is terminal. Recovery rewrites only deterministic `NEXT.md` after every authoritative artifact passes. The managed manifest binds the creating project version and has no migration or relocation path.

**Evidence.** Tests show terminal refusal cannot commit or dispatch, pointer deletion is recoverable without changing authoritative members, and fixed nonclaims/topology are audit-enforced.

## Finding A160-11 — the normal operator path still pointed at the stateless protocol

**Risk.** ChatGPT, a human bridge, or a less capable coordinator could read a correct protocol description and still be forced to invent the state machine the revision was meant to supply.

**Repair.** Added `docs/operators/CHECKPOINT_RUNS.md` as the normal path and updated root, model entrance, ChatGPT, multi-agent, provider, project-instruction, protocol, threat, glossary, design, roadmap, architecture, research, decision, and acceptance documentation. `CHECKPOINTS.md` is now explicitly the lower-level custom-host surface.

**Evidence.** Documentation link checks and provider-content tests are part of release acceptance.

## Refactor assessment

The principal refactor is a managed host layer around rev0159’s existing exchange and kernel paths, not a second truth or commit engine. Checkpoint runs retain advisory sidecars; parent assembly still emits the existing turn proposal; review still uses the real rollback preparation path; durable commit and historical recovery still use the established event-chain boundary. The database remains schema 8 and the immutable event envelope remains schema 1.

The sidecar extraction reduces security drift across ordinary turns and checkpoints. The receipt-validator split reduces repeated work while preserving a public full-chain API. Validation-before-publication reduces ordinary begin orphans. No worker receives assembly, review, commit, recovery, or presentation authority.

## Residual risks

- Lacuna does not invoke, authenticate, isolate, meter, or attest any provider, model, or subagent.
- Invocation receipts and failure classes are host declarations; unrecorded calls or dishonest metadata remain possible.
- Provenance-blind judging does not prove semantic anonymity, independence, or absence of shared memory.
- Exact rollout beats and deterministic scores do not prove search coverage, faithful simulation, calibrated judgment, or better fiction.
- Managed directories retain privileged rejected futures and receive no bundled encryption, archival, redaction, expiry, or secure deletion.
- Absolute run/cube paths make relocation fail closed; no managed-run migration is supplied.
- The lock is cooperative and per run, not distributed or per cube; SQLite and sidecar publication remain separate durability domains.
- A hostile same-user host can replace database, verifier, parent directories, and declarations together.
- Automatic checkpoint timing, connected provider adapters, live conformance, scenario capsules, and the comparative Gwern evaluation remain external.

## Acceptance disposition

The release is acceptable when all discovered tests pass in the worktree and clean extraction, every JSON/TOML/schema parses, relative Markdown links resolve, the manifest verifies, the launcher reports version 0.160.0, managed dispatch and failure custody smoke successfully, and a clean managed checkpoint reaches accepted commit plus exact later-head recovery without duplicate events. Final measured values are recorded in `../acceptance/ACCEPTANCE_rev0160.json`.
