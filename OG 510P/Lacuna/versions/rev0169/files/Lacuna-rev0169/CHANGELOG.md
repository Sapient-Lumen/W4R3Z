# Changelog

## 0.169.0 — rev0169

- Replaced close-time SQLite `wal_checkpoint(TRUNCATE)` cleanup with bounded passive WAL checkpoint cleanup to avoid teardown stalls behind readers during checkpoint-heavy tests.
- Added `tools/run_acceptance.py`, a bounded per-module recipient acceptance runner, and updated current documentation to point at it.
- Made generated scenario capsules fail closed until template player inputs and model-policy placeholders are edited.
- Added a top-level MIT `LICENSE`.
- Added current rev0169 architecture, research, audit, decision, and acceptance records while retaining prior revision records as history.


## 0.168.0 — rev0168

### Polished

- Updated the root README opening so the public-facing release summary names the current revision instead of stale rev0166/rev0165 wording.
- Reworked the root “What this release contains” section into a send-ready summary of the player, Gwern, operator, fresh-narrator, contamination, masking, bundle, and artifact-audit surfaces.
- Added current rev0168 architecture, research, audit, decision, and acceptance records while retaining prior revision records as history.
- Added a release-surface regression that fails if the README opening drifts away from the current revision summary again.

### Preserved

- Database schema 8, event schema 1, zero third-party runtime dependencies, rev0167 method-identifiability custody, rev0166 artifact/entrance/complete-history/canary surfaces, and parent-only mutation/presentation authority.

## 0.167.0 — rev0167

### Added

- Added `lacuna.scenario-masking-assessment.v1` for post-primary-rating, pre-unblinding method-identifiability assessments.
- Added `awaiting-masking` to scenario-run v3 so primary ratings freeze before method guesses and cues are collected.
- Added scenario-report v3 and bundle-report v3 method-identifiability summaries and rater-level export fields.
- Added scenario-bundle v2 and block-seal v3 custody that binds masking artifacts before any block is unblinded.
- Added parent-opened bundle child unblind gates, bound to block-seal digests, to close the direct child unblind bypass.
- Added `scenario masking-template`, `scenario mask`, `scenario bundle masking-template`, and `scenario bundle mask` CLI surfaces.

### Fixed

- Prevented primary blind ratings from being treated as method-recognition feedback or vice versa.
- Prevented method-guess correctness from being joined before unblinding.
- Prevented direct child unblind of a bundle-staged scenario run before the bundle parent enters all-block unblinding.

### Preserved

- Database schema 8, event schema 1, zero third-party runtime dependencies, rev0166 release entrances, complete public-history custody, full retained-tree contamination scan, replicated bundle witness gates, and parent-only mutation/presentation authority.

## 0.166.0 — rev0166

### Added

- Three manifest-enforced top-level entrances: `PLAY_NOW.md`, `FOR_GWERN.md`, and `OPERATE_LACUNA.md`.
- `lacuna artifact check` and `lacuna.artifact-audit.v1` for read-only manifest/member/version/syntax/parse/link verification of an extracted release.
- `history complete` plus `lacuna.public-history.v2` / `lacuna.public-history-view.v2`, with checkpoint-bound complete-before-checkpoint census custody and explicit-run-list non-completeness labeling.
- `lacuna.checkpoint-continuation-dispatch.v2` with `typed-only`, `bound-public-history`, and `complete-bound-public-history` modes.
- Portable/Codex/Claude Code/Gemini CLI fresh-narrator v2 role contracts.
- Shared incremental authenticated sidecar scanning that computes SHA-256 and exact-token occurrences, including chunk-boundary matches, without whole-file buffering.
- Release-surface, artifact-audit, public-history completeness, continuation-v2, full-tree canary, and streaming scanner tests.

### Fixed

- Restored complete contamination coverage after an unshipped branch excluded cloned cube state and pathnames: every retained regular-file body and relative pathname under frozen cells is scanned, including cube databases, SQLite sidecars, and locks.
- Refused traversal errors/skipped subtrees, unplanned cell directories, links, multi-linked/nonregular/oversized/changing members, tree drift, and path substitution before blind-rating publication.
- Prevented an authentic but selective transcript list from being described as complete.
- Made the promised player-only and researcher entrances actual manifest members rather than revision-record claims.
- Added one executable package audit so source acceptance cannot be mistaken for final archive acceptance.

### Preserved

- Database schema 8, event schema 1, zero third-party runtime dependencies, source-bound turns/checkpoints, exact rollback preparation, historical recovery, fixed comparative conditions, replicated all-blocks-before-any-unblind custody, and parent-only mutation/presentation authority.

## 0.165.0 — rev0165

### Added

- Added `lacuna.scenario-contamination-plan.v1`, deterministically preregistering one operator-only and one filesystem-only opaque canary for every experimental cell before any model result exists.
- Added `lacuna.scenario-contamination-scan.v1`, compiled after all four cells are frozen and before the blind-rating packet, with exact source allowlists, content/relative-path surfaces, same-cell/cross-cell classification, per-cell summaries, and an exact retained-file-manifest digest.
- Added `scenario contamination RUN_PATH` for private authenticated inspection of the retained scan without exposing condition mappings or canary findings to blind raters.
- Added scenario run, cell-driver, and report v2 contracts carrying private control custody, scan identity, and unblinded condition-mapped findings.
- Added scenario-bundle block-seal and report v2 contracts so every replicated block seal and JSON/CSV aggregate binds its exact pre-rating contamination scan.
- Added positive controls for operator-context leakage, filesystem-read leakage, cross-cell leakage, valid cube-state leakage, SQLite-sidecar leakage, lock-file leakage, relative-path leakage, fail-closed traversal errors, unsafe linked members, nonadvancing scan refusal, exact retry, and aggregate propagation.

### Fixed

- Made the claimed fresh-context boundary falsifiable: exact private bytes that unexpectedly enter a model return, transcript, managed run sidecar, or another cell are now retained as evidence instead of relying only on declared context IDs.
- Prevented contamination findings from becoming a cherry-picking mechanism: leak-detected cells remain rateable, included, sealed, and reported; no automatic discard, repair, or rerun path exists.
- Kept canary plans and findings out of blind-rating packets while preserving their exact hashes for later unblinding and replicated block custody.
- Refused symlinked, hard-linked, nonregular, oversized, changing, or incompletely enumerable scan trees and left the authoritative scenario manifest unchanged when final scan compilation failed.
- Closed pre-release false-negative boundaries: the scan now includes committed cube files, SQLite sidecars, cooperative lock files, and relative file pathnames; it refuses unplanned cell directories and fails closed on traversal errors instead of silently skipping a subtree.
- Made the filesystem-only token absent from the private driver body: the parent sees only its path and digest, while the exact token exists only in the unrelated private file.

### Refactored

- Moved canary derivation, plan validation, per-cell controls, bounded secure tree enumeration, exact scanning, authentication, and Markdown rendering into `src/lacuna/contamination.py` rather than further enlarging the scenario state machine.
- Reused the existing scenario freeze, blind-rating, report, bundle-seal, and all-blocks-before-unblind boundaries; no second experiment runner or story mutation path was introduced.
- Made the scan boundary explicit as the content and relative pathname of every retained regular file under the preregistered cell tree—drivers, role sidecars, returns, receipts, locks, transcripts, cube state, and database sidecars—while keeping semantic cube verification as a separate kernel check.

### Nonclaims

- A clean exact-token scan proves only absence from retained regular-file contents and relative pathnames; it does not prove provider memory erasure, fresh context, tool denial, filesystem confinement, semantic independence, absence from empty-directory names, or absence of paraphrased leakage.
- A detected token proves only that those exact retained bytes crossed one local boundary; it does not identify the provider-side mechanism or establish causality by itself.
- A hostile parent can omit unretained calls, leak information without copying the token, or discard an unwitnessed experiment before publication.

## 0.164.0 — rev0164

### Added

- Added `lacuna.checkpoint-continuation-dispatch.v1`, a self-contained least-context handoff joining one authenticated committed checkpoint to one exact fresh ordinary turn.
- Added `checkpoint run next-turn`, the normal one-command continuation entrance: exact `play-turn` input, audience-only packet, `solo` topology, no anchor authority, dedicated fresh-narrator provider alias, and ordinary proposal/accept contract.
- Added `checkpoint run continuation` for binding an already-open qualifying turn, while retaining `checkpoint run narrator-capsule` as the reusable checkpoint-only artifact.
- Added `lacuna.public-history.v1` and `history build` for exact player-visible input/narration custody from explicitly supplied committed turns, plus durable request/narration-source authentication.
- Added portable, Codex, Claude Code, Gemini CLI, and ChatGPT definitions for the dedicated `lacuna-fresh-narrator` role.
- Added `lacuna.public-history-view.v1`, a prose-only fresh-narrator projection that omits source-custody IDs, hashes, and event positions.
- Added three Draft 2020-12 exchange schemas and focused public-history, continuation, provider, CLI, tamper, self-consistent-forgery, stale-head, and end-to-end commit tests.
- Tightened the continuation handoff validator and schema so the return format and prebound proposal template remain the exact fail-safe narration-only starting shape.

### Fixed

- Closed the operator seam where a correct capsule could still be paired with the wrong next input, a widened director turn, a non-solo topology, or an unbound prose response.
- Refused stale, different-cube, nonfresh, session-control, director, and otherwise ineligible continuation turns.
- Refused invalid public-history chronology, cube/audience scope, text/artifact digests, unknown ledger heads, and fully rehashed prose substitutions that do not match durable request/narration sources.
- Validated optional public history before creating a one-command continuation turn, preventing a failed context artifact from leaving an orphan run.
- Made public-context parity operational without pretending that supplied history is complete or that prose entailment is mechanically proven.
- Made the recommended Markdown fresh-narrator handoff genuinely self-contained by embedding the exact prebound turn-proposal return template instead of requiring a chat worker to reconstruct it.
- Made release custody exact-set rather than checksum-only: the final ZIP must contain precisely the manifest-listed files plus `MANIFEST.sha256`, with generated caches and bytecode refused.

### Refactored

- Centralized immutable ledger head-to-event-sequence lookup in `Cube.event_sequence`.
- Added one fully audited, private-free committed-turn public record extractor rather than re-reading turn sidecars ad hoc.
- Split full parent/auditor history custody from the minimal public-prose view supplied to weaker fresh narrators.
- Reused the ordinary turn proposal, exact rollback preparation, receipt, and crash-recovery path; no second commit engine or story state was introduced.
- Updated operator, provider, ChatGPT, scenario, architecture, threat, research, and gift documentation around the source-bound continuation boundary.

## 0.163.0 — rev0163

- Added strict `lacuna.checkpoint-narrator-capsule.v1` continuation custody and the read-only `checkpoint run narrator-capsule` command after committed-run audit.
- Made committed checkpoint `NEXT.md` teach the fresh-narrator handoff rather than ending at receipt presentation.
- Structurally excluded candidates, rejected rollouts, judge scores/rationale, worker provenance, verifier findings, and parent history from capsule construction.
- Added exact request/proposal/receipt/compression/state-card/audience-context digests plus state-card and audience-context tamper refusal.
- Added scenario `continuation_mode`, managed-checkpoint identity, continuation-checkpoint identity, and capsule-digest custody.
- Sharpened the four-condition topology: three persistent-context controls versus fresh checkpoint roles and a fresh capsule-bound narrator segment in `lacuna-role-separated`.
- Refused role-context reuse, post-checkpoint narrator reuse, missing/mismatched capsule linkage, serial-control context drift, and post-accept retries.
- Refused checkpoints after the final scenario script step and changed the default capsule to include an observable post-checkpoint continuation.
- Added concise `OPERATE_LACUNA.md`, focused fresh-narrator guidance, and a disposition audit of the rev0160 direct-upload kit/manual.
- Made public-context parity explicit: capsule-only studies require typed material canon, while transcript-based studies must bind the same player-visible history across conditions.
- Added current architecture, research, decisions, audit, threat, glossary, schema-lineage, provider, ChatGPT, scenario, and Gwern-gift documentation.
- Preserved database schema 8, event schema 1, zero runtime dependencies, parent-only commit authority, and all rev0162 bundle behavior.

## 0.162.0 — rev0162

### Added

- Preregistered `scenario bundle template/begin/status/recover/commitment/witness-template/witness/dispatch/record/rating-template/rate/seal/unblind/export` lifecycle above the existing four-condition child scenario runner.
- Complete two-to-128-block plan with embedded validated capsules, normalized seed paths, story/model/replicate strata, fixed comparable ratings, primary dimensions, all-scheduled inclusion, terminal-failure retention, and optional external-receipt threshold.
- Private master schedule fixing randomized block order, child run identities, and assignment seeds before execution; one public commitment binds the complete plan/schedule and every child seed/capsule/assignment boundary without revealing condition mappings.
- Atomic all-child staging and publication, one-active-block execution, immutable blind block seals, and all-blocks-sealed-before-any-child-unblind discipline.
- Cross-block declared context and non-null invocation-ID separation, future-child contamination detection, direct witness-gate bypass detection, and typed premature-child-unblind refusal.
- Crash-resumable all-child unblinding plus deterministic rater-level JSON, Markdown, and spreadsheet-safe CSV reports retaining completed, refused, and failed outcomes.
- Seven strict exchange/sidecar schemas for bundle plan, private schedule, public commitment, manifest, witness record, block seal, and aggregate report.
- Hyperlegible operator, architecture, research, decision, audit, threat, glossary, provider/subagent, ChatGPT-player, Gwern-gift, and scientific-use documentation.

### Fixed

- Required every child capsule in one bundle to use the exact same rating scale, prompts, dimensions, and required rater count before publication.
- Derived aggregate commitment and witness digests from fully validated retained objects instead of trusting cached manifest references.
- Counted `refused` cells separately from `failed` and `completed` cells in aggregate condition summaries.
- Refused child-directory symlink substitution and required every child authority path to remain contained under its exact parent bundle.
- Refused cross-block context or invocation reuse before mutating the active child and repeated the global invariant during full audit.
- Neutralized formula-leading rater comments and strata in derived CSV exports while preserving exact text in canonical JSON.
- Unified the 64-receipt witness bound across runtime and schemas and refused an overflow receipt before publishing a file or changing the manifest.

### Refactored

- Consolidated exact cube cloning, private sidecar directory creation, member containment, immutable JSON publication, and staged scenario construction into shared primitives.
- Centralized the sealed-child-still-blind topology check so completed-prefix and all-sealed states produce one typed premature-unblinding boundary.
- Removed unfinished competing `experiments` and `scenario_studies` implementations; `scenario_bundles` is the sole replicated-experiment contract.
- Preserved database schema 8, event schema 1, single-block scenarios, ordinary play, managed turns/checkpoints, historical compatibility, and the literal “Will you DM?” entrance.

### Nonclaims

- A bundle is an auditable experiment dataset, not statistical significance, a causal estimate, an ethics review, or proof that Lacuna improves fiction or science.
- Witness records are operator-supplied descriptions; Lacuna does not verify external signatures, timestamps, transparency-log inclusion, service identity, or availability.
- Same-host owners can inspect private assignments or discard a bundle before external retention; direct child contamination can be detected but not undone.
- Provider/model/context/invocation/timing/token/cost/failure fields remain host declarations, and distinct IDs do not prove independent subagents or fresh memory.
- Structured blind packets do not guarantee semantic anonymity, rater independence, or absence of method leakage.
- Whole-tree publication and cooperative locks are same-filesystem process coordination, not distributed transactions or hostile-user confinement.

## 0.161.0 — rev0161

### Added

- Comparative `scenario template/begin/status/recover/dispatch/record/rating-template/rate/unblind` lifecycle for one fixed four-condition test of forward-only continuation, monolithic prompt retcon, Lacuna serial roles, and Lacuna role-separated contexts.
- Nine strict scenario exchange schemas covering capsule, run, private assignment, cell driver/return/receipt, blind rating packet, rating, and unblinded report.
- Four exact verified seed clones, hidden pre-result condition assignment, one-active-cell serial dispatch, fixed model/budget/rater policies, transcript-only blind packets, and post-rating deterministic unblinding.
- Script-step-bound invocation custody, cross-cell declared-context separation, global non-null invocation-ID uniqueness, condition-specific role/context topology, and exact transcript-to-accepted-turn correspondence.
- A hyperlegible scenario operator guide for ChatGPT, Codex, Claude Code, Gemini-oriented agents, human bridges, native subagents, replication, recovery, and honest nonclaims.
- Eleven scenario protocol tests and one CLI lifecycle test, plus emitted-artifact validation against every new public schema.

### Fixed

- Required ordinary turn runs to bind the caller-supplied resolved path to the exact open `Cube` before publication.
- Prevented completed, failed, or refused scenario returns from omitting player-visible transcript steps for accepted ordinary model calls.
- Refused cross-condition reuse of declared model contexts before any cell artifact write and rechecked the invariant on every full audit.
- Detected pending-cell mutation, post-acceptance clone mutation, role-topology collapse, assignment relabeling, script-step drift, duplicate invocation identity, and early or incomplete unblinding.

### Refactored

- Added one shared owner-private whole-directory publication primitive and adopted it for ordinary turn runs, managed checkpoint runs, and scenario runs.
- Built initial lock, members, manifest, and deterministic pointer under a hidden sibling staging path and published them with one same-filesystem rename; construction failure leaves no final or staged run directory.
- Preserved database schema 8, event schema 1, ordinary play, managed turn/checkpoint contracts, parent-only commit authority, exact recovery, and historical compatibility.

### Nonclaims

- A scenario run is a single-block experiment instrument, not evidence that Lacuna improves fiction, science, or retcon planning in general.
- Hidden assignment is locally committed but not externally witnessed; a same-host owner can still discard unpublished runs.
- Provider, model, context, invocation, timing, token, and cost records remain host declarations unless independently attested.
- Structured blind packets do not guarantee semantic anonymity, human blindness, or independent model memory.
- Atomic directory publication is one-filesystem cooperative-host behavior, not a distributed transaction or atomic commit with story-ledger mutation.

## 0.160.0 — rev0160

### Added

- Managed `checkpoint run begin/status/dispatch/accept/record-failure/recover/commit` commands that turn the source-bound generator → provenance-blind judge → winner-only compressor → advisory verifier exchange into one strict resumable sidecar with one deterministic next action.
- `lacuna.checkpoint-run.v1`, `lacuna.checkpoint-run-agent-dispatch.v1`, and `lacuna.checkpoint-invocation-receipt.v1` exchange schemas for exact topology, self-contained least-context handoffs, and ordered host-declared accepted/failed invocation custody.
- Fixed heterogeneous provider routes for portable, Codex, Claude Code, Gemini CLI, and ChatGPT roles, including provider-native aliases and a serial human-paste bridge when subagents are unavailable.
- Terminal verifier-refusal state, pointer-only `NEXT.md` recovery, exact committed-run audit, and checkpoint-run recovery after a durable database commit or later legitimate head advancement.
- Managed-run operator, ChatGPT, provider, multi-agent, architecture, research, decision, threat, glossary, Gwern-gift, audit, and acceptance documentation.
- Fifteen managed checkpoint-run tests plus expanded CLI/provider/schema coverage, bringing the accepted suite to 232 tests.

### Fixed

- Bound `resolved_cube_path` to the exact open `Cube` used to freeze the request, preventing a caller from opening one cube while naming another in run custody.
- Refused empty or malformed provider-route maps and empty per-role overrides instead of silently substituting the default route.
- Manufactured and validated the source request and generator card before sidecar creation so ordinary invalid checkpoint policy cannot leave a run-shaped orphan.
- Converted malformed invocation collections into typed Lacuna refusals, enforced the 1,000-receipt schema cap before any 1,001st write, and required every retained role output to have exactly one ordered accepted invocation receipt.
- Revalidated committed checkpoint receipts against the retained request/proposal/review chain, receipt narration, cube verification, and exact durable change, including semantically rehashed tampering.
- Preserved wrong-stage and cross-run fail-before-mutation behavior, fixed trust-boundary nonclaims, exact dispatch relabel refusal, and authoritative-member symlink refusal.

### Refactored

- Extracted descriptor-stable bounded reads, canonical JSON digests, strict sidecar directory resolution, owner-only lock handling, cooperative nonblocking locks, and shell rendering into one shared `sidecars` module used by ordinary turn runs and checkpoint runs.
- Reused rev0159 request/card/selection/compression/proposal/review/commit contracts and the existing rollback-preparation and historical-recovery kernel rather than introducing a second truth or commit engine.
- Added a validated-chain checkpoint-receipt helper so internal commit and audit paths do not repeat the most expensive exact-preparation replay while the public validator still authenticates the complete chain.
- Preserved database schema 8, immutable event schema 1, request-scoped ordinary turn behavior, one-sentence play, and all historical checkpoint exchange commands.

### Nonclaims

- A managed run does not invoke, authenticate, isolate, or attest a provider, model, subagent, route, tool boundary, timing value, or invocation identifier; those fields are exact host declarations.
- Different provider routes and provenance-stripped judging do not prove independent contexts, semantic anonymity, absence of collusion, calibrated scoring, useful diversity, or better fiction.
- `ready-to-commit` proves exact rollback preparation, not commitment or head reservation; only the accepted receipt proves durable mutation or authenticated recovery.
- Checkpoint sidecars may retain privileged rejected futures and receive no bundled encryption, remote archive, expiry, redaction, secure deletion, hostile-user boundary, distributed lock, or cross-store atomic transaction.
- Revision 0160 still does not supply vendor invocation, automatic checkpoint triggering, a connected-host product, live provider conformance results, or the completed comparative Gwern experiment.

## 0.159.0 — rev0159

### Added

- Source-bound `checkpoint begin/card/dispatch/assemble/review/commit` workflow for exact generator → provenance-blind judge → winner-only compressor → advisory verifier orchestration without provider invocation or worker commit authority.
- Typed `lacuna.turn-request.v4`, `lacuna.turn-grant.v2`, and request-source protocol v3 with explicit `request_purpose = play | checkpoint`, while preserving request v2/v3 and grant v1 compatibility.
- Eleven checkpoint exchange contracts covering request, task card, exact candidates, judgment, compression, proposal, verifier return, review, commit receipt, provider dispatch, and turn-request v4 issuance.
- Exact cardinality-explicit model templates: every generator card preallocates the declared candidate count and one ordered rollout beat per horizon turn; every judge card preallocates one complete score slot per candidate.
- Fixed seven-dimension integer-weight scoring, declared disqualifiers, deterministic highest-eligible/lexical-tie selection, selected-candidate custody, compression budget, and exact unknown preservation.
- Four read-only checkpoint roles for Codex, Claude Code, and Gemini CLI plus role-dedicated ChatGPT instructions and a complete operator guide.
- Checkpoint-specific exact retry recovery after later valid ledger writes and expanded end-to-end, schema, provider, dispatch, cardinality, tamper, and compatibility coverage, bringing the accepted suite to 216 tests.

### Fixed

- Closed a rollout-evidence loophole that allowed a claimed summary or optional hash without the exact forward beats a judge must inspect.
- Prevented weaker models from having to infer array counts, candidate IDs, horizon structure, or judge coverage from prose alone.
- Rejected schema-shaped but altered checkpoint dispatches by validating the embedded card and exactly recomputing the complete provider envelope.
- Corrected verifier scope: the least-context verifier checks proposal-visible custody consistency, while parent assembly alone revalidates raw candidates, score arithmetic, eligibility, tie-breaking, winner, and selected compression.
- Verified checkpoint retry recovery against the historical request-head prefix and exact durable event chain even when unrelated later changes advance the live head, without appending duplicate events.
- Preserved historical request v2/v3 packet semantics instead of silently rewriting them into the new purpose-aware contract.
- Added an explicit selected-candidate canonical digest to selection evidence and the durable custody-source metadata, rather than relying only on the aggregate candidate artifact digest plus ID.

### Refactored

- Centralized portable, Codex, Claude Code, Gemini CLI, and ChatGPT role aliases for ordinary turns and checkpoints in one provider registry.
- Reused the existing turn proposal, rollback preparation, exact replay, receipt, and historical recovery paths rather than creating a parallel checkpoint commit engine.
- Kept detailed candidates, rejected rollouts, scores, and model provenance outside the story event ledger while binding accepted selection/compression evidence through a narrow source operation.
- Reworked Gwern gift analysis, three-question design, player/ChatGPT/provider entrances, multi-agent guidance, protocols, threat model, glossary, roadmap, architecture, research, decisions, audit, and acceptance records around the datacube as an executable context compiler.
- Preserved rev0158 one-sentence play and hardened run custody, rev0157 exact kernel preparation/recovery, database schema 8, and event schema 1.

### Nonclaims

- Lacuna does not invoke, sample, authenticate, isolate, or attest a provider/model/subagent; dispatch and provenance fields are exact host-supplied custody, not vendor proof.
- Provenance-blind judging removes declared generator identity and notes but does not prove semantic anonymity, independent contexts, or absence of collusion.
- Exact rollout beats prove supplied cardinality, not faithful simulation, useful diversity, predictive validity, or narrative quality.
- Fixed scoring and deterministic selection make one declared decision reproducible; they do not make aesthetic judgments objective, calibrated, or valid particle likelihoods.
- A verifier pass is advisory, exact checkpoint artifacts remain sensitive host-side files, automatic trigger policy remains external, and the comparative Gwern experiment has not yet been run.

## 0.158.0 — rev0158

### Added

- Typed `lacuna.turn-request.v3` packets and source-protocol-v2 custody for explicit `session-control` versus `play-turn`, with strict v2 compatibility defaulting historical requests to `play-turn`.
- One-command `play start` and `lacuna.play-start.v1` receipts that safely resolve or bootstrap only absent/empty campaign paths, select unambiguous campaigns, derive roles, and open exact session control without invoking a model or fictionalizing the request.
- Provider-neutral `lacuna.agent-dispatch.v1` handoffs and `turn run dispatch` for portable, Codex, Claude Code, Gemini CLI, and ChatGPT routes; each envelope embeds the exact current least-context card, role alias, input kind, return schema, parent accept command, authority split, and nonclaims.
- Explicit `turn run recover` for deterministic pointer-only repair after complete authoritative audit.
- Direct-play, dispatch, recovery, and adversarial sidecar-integrity coverage, bringing the accepted suite to 199 tests.

### Fixed

- Refused symlinked, hard-linked, nonregular, oversized, mutated-during-read, and detected path-substituted authoritative sidecar members through one descriptor-stable bounded reader.
- Corrected a pathname-substitution failure branch that could raise an unrelated exception shape instead of structured `turn-run-member-unsafe`.
- Removed the remaining path-only assumption from ChatGPT/subagent handoffs by embedding the complete task card in every delegated dispatch.
- Prevented session-management text such as “Will you DM?” from being silently interpreted as in-fiction dialogue or physical action by hosts that follow the typed contract.
- Made missing or linked `NEXT.md` repairable without permitting reconstruction or editing of authoritative artifacts.

### Refactored

- Composed campaign resolution, model-reference readiness, and request-scoped run creation behind one hyperlegible play entrance rather than adding a parallel story-state path.
- Centralized sidecar file opening, identity checks, bounded reads, decoding, and parsing under one integrity primitive used by manifest and artifact audit.
- Kept provider-native files as discovery adapters while making the generated dispatch/card the exact per-invocation context contract.
- Reworked player, ChatGPT, provider, multi-agent, threat, protocol, roadmap, architecture, research, decision, audit, and acceptance documentation around typed intent and context compilation.
- Preserved rev0157 exact rollback preparation, frozen direct replay, later-head historical receipt recovery, cooperative same-run locking, database schema 8, and event schema 1.

### Nonclaims

- A dispatch does not invoke, authenticate, isolate, or attest a provider/model/subagent and does not prove that a worker followed its card.
- A one-sentence chat can begin play, but durable ChatGPT persistence still requires a human bridge or connected host with access to the cube.
- Descriptor-stable sidecar reads reduce local substitution mistakes; they are not encryption or a hostile same-user filesystem boundary.
- Pointer recovery repairs only `NEXT.md`; it cannot reconstruct authoritative cards, returns, proposals, preparations, or receipts.
- Lacuna still does not implement candidate generation, rollout, resampling, aesthetic scoring, checkpoint optimization, a provider SDK, or the completed comparative Gwern experiment.

## 0.157.0 — rev0157

- Replaced sidecar-only readiness with `lacuna.turn-preparation.v1`: the final proposal is normalized, executed through the real kernel mutation engine, projected into audience/planner contexts, and unconditionally rolled back before `ready-to-commit` is published.
- Refactored changeset preview and commit onto one `_execute_changeset` path; exact replay freezes the timestamp and every event ID, then compares the complete change receipt, payload digest, event hash chain, after-head, and returned contexts inside the commit transaction.
- Made model-omitted operation identifiers deterministic from proposal identity and operation position so independent preparation validation cannot drift across invocations.
- Added `lacuna.turn-receipt.v3` with preparation binding and explicit direct-versus-recovered delivery provenance.
- Added verified post-commit crash recovery: reconstruct the request-head cube from an in-memory SQLite backup, replay and roll back the preparation there, compare the durable change and full event chain, and never duplicate committed events.
- Added `lacuna.turn-run.v2`, stable `43-turn-preparation.json`, exact preparation audit at status/accept/commit, and durable-change equality checks for committed runs.
- Added an owner-only, no-symlink, single-link `.run.lock` with nonblocking advisory locking over complete status, accept, and commit transitions.
- Added adversarial coverage for rollback non-mutation, kernel-invalid proposal refusal before readiness, recovery after later head advance, rehashed forged-context refusal, lock contention, and lock symlink substitution; accepted suite now contains 180 tests.
- Updated model/provider instructions, operator documentation, threat model, glossary, architecture, research, decisions, audit, and acceptance records around exact executable readiness and its remaining cross-store/distributed nonclaims.

## 0.156.0 — rev0156

### Added

- Request-scoped `turn run begin`, `status`, `accept`, and `commit` commands that retain exact player input, packet, deterministic topology, task cards, role returns, proposal, verifier result, receipt, and one audited `NEXT.md` pointer.
- Strict `lacuna.turn-run.v1` sidecar schema, canonical artifact digests, expected role/schema metadata, deterministic stage topology, and provider-specific role aliases for Codex, Claude Code, Gemini CLI, and role-dedicated ChatGPT contexts.
- Exact UTF-8 `--player-input-file` support, including standard input, so shells, newlines, CRLF, and metacharacters need not be reinterpreted as command text.
- One-sentence player entrance and honest ChatGPT paths for chat-only play, a human paste bridge, bounded role contexts, and a future narrow connected host.
- A deep three-question design record mapping Lacuna to Gwern’s commitment-budget problem, defining the gift precisely, and specifying a four-condition comparative experiment.
- Five turn-run adversarial tests plus expanded CLI and provider assertions, bringing the accepted suite to 175 tests.

### Fixed

- Implemented the exact `--player-input-file` route that the prior ChatGPT bridge documented but the CLI did not actually accept.
- Refused valid JSON artifacts submitted at the wrong stage, cross-turn or edited returns, relabelled schema/role metadata, tampered canonical digests, and a modified `NEXT.md` pointer.
- Refused unchanged narration placeholders in both direct and run-mediated proposals.
- Removed default planner-context inclusion from generated run entrances; privileged context is returned only by explicit operator choice.
- Removed a solo-mode instruction ambiguity that named two possible inputs while pointing to only one complete artifact.
- Replaced active entrance documentation that expected a weaker model to remember the packet/plan/card chain with one resumable run state machine.

### Refactored

- Wrapped the lower-level packet/plan/card protocol in an auditable sidecar workflow without changing schema-8 database storage, event schema 1, or parent-only kernel mutation authority.
- Made `run.json` the strict machine state, `NEXT.md` a deterministic audited rendering, and each stage a single-owner transition with one complete input artifact and one expected output schema.
- Converged `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, ChatGPT project instructions, operator guides, README, and start guide on the same four-command entrance.
- Kept provider files as stable discovery preambles while moving per-turn data, digest bindings, least-context slices, and exact return templates into generated task cards.
- Expanded threat and recovery documentation around same-run concurrency, absolute paths, crash windows, cleanup, privacy, and provider-isolation limits.

### Nonclaims

- A turn run is a local sequential sidecar, not a lock service, distributed transaction, model invoker, provider attestation, or cryptographic confidentiality boundary.
- Run paths are absolute in v1 and are not relocatable; one run must not be advanced concurrently by multiple parents.
- A crash after request creation or after kernel commit can require explicit inspection/recovery; the sidecar does not make SQLite and filesystem writes one atomic transaction.
- Canonical JSON digests preserve parsed JSON meaning, while exact byte custody is guaranteed only for the retained player-input text.
- Lacuna still does not implement candidate-world generation, rollout, resampling, aesthetic scoring, checkpoint optimization, or a completed comparative Gwern experiment.

## 0.155.0 — rev0155

### Added

- Read-only `turn plan` and `turn card` CLI entrances with deterministic `solo`, `pair`, and `full` routing from strict packet-visible risk signals.
- Strict `lacuna.orchestration-plan.v1` and `lacuna.turn-task-card.v1` exchange contracts plus exact planner, narrator, and verifier return schemas.
- Digest-bound task identities tying every worker artifact to one canonical packet and its exact ordered upstream returns; edited and cross-turn mixtures refuse.
- Manufactured least-context narrator cards containing only exact player data, audience context, and an approved observable plan—not the privileged packet, planner rationale, or candidate operations.
- Exact `card_command` fields for every selected worker stage so a fresh or literal coordinator need not infer roles, flags, dependencies, or filenames.
- Packet-bound proposal-builder and fail-closed verifier cards, with local proposal identity/grant preflight that remains explicitly non-authoritative.
- Task-card-native Codex, Claude Code, Gemini CLI, and ChatGPT role instructions with one portable exact-JSON output contract.
- Eleven orchestration tests and expanded model-entrance, provider, and exchange-schema coverage, bringing the accepted suite to 169 tests.

### Fixed

- Refused internally inconsistent turn packets before any model/subagent fan-out, including player-input digest, context/head, access/grant, response-contract, and safe-template drift.
- Refused narrator returns that copy the generated narration instruction unchanged.
- Prevented a verifier from changing only `status` or severity while retaining the fail-closed `unperformed-review` finding.
- Prevented narrator handoffs from carrying planner private notes or candidate operations by construction rather than coordinator convention.
- Prevented downstream cards/returns from silently accepting an upstream artifact edited after task issuance.
- Removed the requirement that weaker models reverse-engineer downstream `turn card` command-line arguments from prose.

### Refactored

- Exposed public read-only `validate_turn_grant()` and `Cube.has_active_agent()` helpers instead of depending on private turn/storage implementation details.
- Generalized CLI JSON-object loading for packets and sidecar artifacts instead of reusing a change-set-specific reader.
- Separated stable provider role preambles from generated role-specific data; the complete task card is now the worker prompt and output authority.
- Documented orchestration plans/cards as advisory sidecars around an unchanged schema-8/event-schema-1 kernel, with parent-only packet and commit authority.
- Expanded the Gwern gift test and executable-context-curriculum design with handoff-contamination, topology, and card-native ablations.

### Nonclaims

- Packet and handoff digests prove continuity of supplied canonical JSON, not host authentication, provider isolation, semantic correctness, or truth.
- `turn plan`, `turn card`, proposal preflight, and verifier returns do not invoke models, store a workflow, accept a proposal, or grant commit authority.
- Provider prompt/tool configuration is behavioral policy rather than a provider-independent confidentiality boundary.
- Example `/tmp` files assume one sequential turn; request-scoped concurrent sidecar workspaces remain host/future work.
- Lacuna still does not generate/resample worlds, roll them forward, score aesthetics, optimize checkpoints, or publish comparative retcon-planning results.

## 0.154.0 — rev0154

### Added

- A read-only `model brief` CLI entrance with strict `lacuna.model-brief.v1` JSON and directly operational Markdown renderings.
- Capability-honest `chat`, `workspace`, and `orchestrated` profiles that separate cube readiness from the host surface’s actual ability to persist a turn.
- Deterministic readiness checks for ledger verification and active audience/narrator registration, plus explicit blockers and intent routing for play, repository work, and inspection.
- Exact source-bound verify/packet/commit commands with named packet, proposal, and receipt paths and a required `PLAYER_INPUT` guard.
- Least-context planner, narrator, proposal-builder, and verifier role cards with parent-only packet issuance and commit authority.
- Native project instructions and bounded agent definitions for Codex, Claude Code, and Gemini CLI, plus capability-honest ChatGPT Project/custom-GPT instructions and a human paste bridge.
- A Gwern gift test, cross-provider operator guides, and a falsifiable retcon-planning evaluation design with scenario-capsule and monolithic-versus-orchestrated ablations.
- Twelve model-entrance tests, six provider-configuration tests, and one executable CLI entrance test, bringing the accepted suite to 158 tests.

### Fixed

- Replaced the turn packet’s fake `replace.me` claim/assertion example with a fully valid narration-only proposal so literal models cannot accidentally commit demonstration artifacts.
- Corrected host guidance that incorrectly described accepted narration as `receipt.narration`; the actual turn receipt exposes top-level `narration`.
- Prevented a generated packet command from silently opening a request for missing input; the shell now aborts before mutation when `PLAYER_INPUT` is unset or empty.
- Blocked governed-start claims when deterministic cube verification fails, while withholding detailed forensic findings from the general model brief.
- Made role-readiness checks ignore retired agents.
- Distinguished ChatGPT subscription/product labels from actual execution capabilities and distinguished Codex prompt separation from hard filesystem confidentiality.

### Refactored

- Centralized the model-facing turn response contract in `entrance.py` and reused it from runtime packet construction, reducing drift between documentation and executable behavior.
- Separated portable role contracts from provider-specific discovery syntax and model names; native agents inherit the parent model and degrade to the single-workspace profile when provider configuration drifts.
- Made the datacube’s multi-turn role explicit: a deterministic context curriculum that can reproduce the same head, projection, grant, refusal, and commit path across models and repeated CLI invocations.
- Kept provider invocation, dramatic policy, transcript bodies, rollout bodies, and evaluation judgments outside the zero-runtime-dependency custody kernel.

### Nonclaims

- A model brief does not call an LLM, prove provider compliance, or grant mutation authority.
- Uploaded files, a ChatGPT Project, or a Pro subscription do not by themselves provide durable access to a local Lacuna cube.
- Provider prompt files and subagent definitions are behavioral policy, not a security boundary; Codex read-only agents may still inspect readable workspace files.
- Least-context orchestration does not prove noninterference, better prose, lower leakage across every model version, or scientific truth.
- Lacuna still does not implement the full candidate-generation, rollout, scoring, checkpoint-compression, or comparative-evaluation loop proposed in retcon planning.

## 0.153.0 — rev0153

### Added

- Digest-bound factor-ledger reconciliation over the latest structurally coherent particle epoch.
- Immutable baseline recovery from the first update’s prior-bank receipt, explicit included/excluded factor custody, and a separately event-sourced `particle.reconciled` repair.
- Max-shifted log-space replay with complete per-world arithmetic, extinguishing-factor diagnostics, total-variation reporting, and no nonfinite event JSON.
- Planner-only CLI, direct Python, context, Markdown, explanation, and unscoped-director turn entrances for reconciliation review and commit.
- Database schema 8 with additive reconciliation projections and ordered migration from coherent schema 1 through 7 cubes.
- Factor-ledger reconciliation protocol, rev0153 architecture/research/decisions/audit/acceptance records, and a reconciliation operation example.
- Nine reconciliation tests plus one executable CLI lifecycle test, bringing the accepted suite to 139 tests.

### Fixed

- Repaired current particle weights after evidence supersession without deleting or mutating the historical update that originally used the evidence.
- Recovered mathematically positive low-mass worlds that sequential floating-point multiplication had reduced to zero solely through underflow.
- Prevented old likelihood vectors from being replayed across changed world membership, assignment custody, commitment, status, or authored prior by introducing explicit factor epochs.
- Refused stale, malformed, incomplete-population, all-zero, duplicate-ID, and repeated no-op reconciliations atomically.
- Detected reconciliation projection tampering and rebuilt all derived rows and current weights from canonical events.
- Prevented schema-7 cubes with legitimate event-owned particle history from inheriting the schema-6 dormant-row collision refusal during 7→8 migration.
- Kept reconciliation reviews, factor dispositions, IDs, counts, and arithmetic outside audience and world-scoped director contexts.

### Refactored

- Centralized live and historical particle-bank construction in one pure helper.
- Centralized valuation-equivalent likelihood-divergence grouping across presentation and verification.
- Kept update, reconciliation, factor correction, structural mutation, proposal, resampling, selection, and canonization as separate powers.
- Defined authority, epoch, baseline, factor-set, replay, nonclaim, migration, and verification rules as a stable protocol rather than storage-local behavior.

### Nonclaims

- Reconciliation repairs derived planner attention; it does not prove that factors are independent, likelihoods are calibrated, or the resulting vector is true.
- Active/ended assertion status supplies a deterministic default factor disposition; it does not semantically prove that evidence remains valid or has been withdrawn correctly.
- Rev0153 cannot yet replace a mistaken likelihood vector with explicit predecessor/successor factor lineage or port factors across structural epochs.
- Log-space replay reduces underflow but does not define arbitrary-precision or cross-runtime canonical numeric arithmetic.
- Reconciliation does not propose missing worlds, resample, preserve minority modes, test causal agency, or choose canon.

## 0.152.0 — rev0152

### Added

- Complete planner-only particle bank over every live or selected candidate world, with normalized attention, valuation/custody fingerprints, duplicate-valuation groups, ESS, entropy, maximum mass, and explicit nonclaims.
- Digest-reviewed `update_particle_bank` operation and `particle.updated` event with one authored likelihood and optional rationale per eligible world.
- Human CLI, direct Python/change-set, strict exchange-schema, unscoped director-turn, rendering, context, explanation, status, snapshot, verification, and rebuild entrances for particle updates.
- Immutable per-world prior, likelihood, unnormalized, posterior, status, and fingerprint custody plus prior/posterior bank digests.
- Single-use evidence factors, applied-factor history, and superseded-factor `reweighting_debt`.
- Database schema 7 and an explicit 6→7 migration that reconciles the canonical fair-play schema-6 branch with the particle sibling design.
- Schema-lineage protocol, particle-bank protocol, rev0152 architecture/research/decisions/audit/acceptance records, and particle examples.
- Three schema-collision migration tests and sixteen particle tests, bringing the accepted suite to 129 tests.

### Fixed

- Prevented normalization over incomplete or world-scoped populations.
- Prevented the same evidence assertion from being multiplied twice; both review and mutation refuse reuse, a unique index enforces projection custody, and duplicate factors inside one atomic change-set roll back together.
- Surfaced stale normalized weights when an applied evidence assertion is superseded instead of silently calling them a current posterior.
- Detected valuation-equivalent worlds receiving divergent likelihoods without assuming the difference is invalid.
- Made malformed/nonfinite particle projection numbers verification-visible without crashing audit.
- Refused nonempty event-unowned particle rows during schema-6 migration rather than deleting or adopting them silently.
- Accepted both official rev0151 schema-6 physical shapes—fresh cubes with empty dormant particle tables and migrated cubes without them—and produced one canonical schema-7 shape.
- Removed the schema-number collision between sibling rev0151 branches while preserving the delivered fair-play artifact as canonical parent and retaining its 5→6 migration digest.

### Refactored

- Extracted deterministic particle fingerprints, bank construction, distribution statistics, digesting, and likelihood arithmetic into `src/lacuna/particles.py`.
- Centralized active-unused evidence-factor validation across review and mutation entrances.
- Kept reweighting separate from proposal, resampling, pruning, selection, assignment revision, disclosure, and canonization.
- Extended the context firewall so the complete bank and update history exist only in unscoped planner context.
- Made schema lineage an explicit documented protocol rather than an implicit version integer.

### Nonclaims

- Weights and likelihoods are authored planning quantities, not calibrated probabilities or truth scores.
- ESS, entropy, information gain, and maximum mass are concentration diagnostics, not narrative-diversity, quality, agency, or fairness measures.
- Rev0152 does not propose, resample, rejuvenate, merge, prune, select, or canonize candidate worlds.
- Superseded factors create visible debt; rev0152 does not yet retract factors or recompute from a base-weight ledger.
- Zero likelihood can create a live zero-mass world and remains an explicit future policy problem.
- The candidate bank can omit the best explanation, and equal valuation fingerprints do not prove complete-world identity.

## 0.151.0 — rev0151

### Added

- Fair-play precommitment seals with domain-separated salted SHA-256 openings bound to cube and seal identity.
- Host-only CLI lifecycle: `seal prepare`, `create`, `list`, `receipt`, `verify`, `reveal`, and `void`.
- A strict portable JSON opening profile with 256-bit nonces, no floats, safe integers, Unicode-scalar validation, payload bounds, and exact opening self-verification.
- Stable externally retainable receipt cores whose digest remains unchanged across reveal or void.
- Public/restricted visibility, perspective-safe context, status, rendering, explanations, snapshots, verification, and deterministic rebuild for seal custody.
- Database schema 6 with explicit digest-identified migration from schema 5 and ordered migration from schema 1, 2, 3, or 4.
- Strict Draft 2020-12 schemas for seal openings and receipts.
- Current fair-play protocol, interaction-surface guide, architecture, research, decisions, audit, threat, glossary, roadmap, and acceptance records.

### Fixed

- Prevented nonce or payload leakage into the cube, event ledger, pre-reveal projection, context, receipt, and CLI creation output.
- Refused same-change-set seal creation and reveal/void, preserving a meaningful ledger phase boundary.
- Excluded seal create/reveal/void from all ordinary model-turn grants, including privileged director turns.
- Removed privileged seal-source linkage from perspective records and explanations.
- Bound every seal projection and terminal opening to exact immutable event payloads and sequences.
- Corrected the receipt core so live lifecycle state no longer changes an externally anchored digest.
- Aligned runtime opening parsing with the strict opening schema and custody envelope.
- Removed the advertised but unimplemented particle-update operation/event and quarantined dormant projection tables.
- Refused lone UTF-16 surrogate code points before canonicalization so malformed strings fail with a structured protocol error rather than an encoder exception.

### Refactored

- Separated immutable receipt-core fields from current seal lifecycle views.
- Made legacy particle tables verification-visible and rebuild-clearable while retaining schema compatibility.
- Added an explicit host-custody operation set instead of equating director authority with administrative authority.
- Kept fair-play reveal semantically inert: opening a seal does not automatically create truth, canon, or world assignments.
- Replaced the Python bootstrap launcher with a POSIX wrapper that invokes the zero-dependency runtime under `python3 -S`, excluding ambient site packages and reducing executable-test startup cost.
- Accepted 109 kernel, migration, confidentiality, exchange-schema, and executable tests.

### Nonclaims

- A valid seal proves exact-opening continuity only, not payload truth, authorship, completeness, uniqueness, trusted time, clue sufficiency, causal agency, or narrative fairness.
- The local event chain is not a signature, external timestamp, transparency service, or hostile-host non-equivocation guarantee.
- A verifier must independently retain or externally anchor the pre-reveal receipt digest for evidence against later forking.
- Rev0151 does not provide Merkle selective disclosure, signed witnesses, threshold opening custody, or a built-in LLM client.

## 0.150.0 — rev0150

### Added

- Digest-bound `consequence-repair-review` and atomic `replace_consequence` across direct change-sets, CLI, strict exchange schemas, planner context, explanations, snapshots, rebuild, and director turns.
- Identified one-to-one predecessor/successor repair lineage with a dedicated `consequence_repairs` projection and `original` / `replaced` / `replacement` / `middle` lifecycle diagnostics.
- Planner-only, world-scoped `consequence_repair_frontier` receipts and CLI entrance for active repair debt.
- Database schema 5 with ordered migration from schema 1, 2, 3, or 4 while preserving the event-ledger head.
- Fourteen dedicated repair tests, four schema-contract tests, expanded governance and turn coverage, and an idempotent-shutdown regression test, bringing the accepted suite to 95.
- A consequence-repair protocol plus current architecture, research, decisions, audit, threat, glossary, roadmap, and acceptance records.

### Fixed

- Prevented new consequences from targeting ended assertions/assignments or closed questions.
- Validated replacement cycles against the post-repair graph rather than falsely retaining the predecessor edge.
- Allowed a reviewed mutation to follow benign provenance creation inside the same atomic source-bound turn while still refusing any separately committed intervening change.
- Bound repair projection rows to their exact immutable origin events and detected replacement events missing projection lineage.
- Prevented repair IDs, predecessor/successor IDs, and review receipts from crossing the audience-context firewall.

### Refactored

- Shared one change-set base-head path across assignment revision and consequence replacement review validation.
- Centralized repair-digest construction across storage and turn-packet rebinding, and exposed receipt-derived review-head custody.
- Made `Cube.close()` idempotent so teardown cannot mask the primary refusal.
- Centralized active consequence endpoint validation and predecessor-excluding assignment-edge enumeration.
- Extended turn normalization with separate primary and secondary creator identities.
- Treated repair as forward correction with durable custody instead of retire-plus-link convention or automatic transfer.
- Made the acceptance suite discoverable through the standard `python -m unittest discover` entrance while keeping JSON Schema validation an optional test extra.

### Nonclaims

- Consequence replacement is not rollback and does not prove predecessor/successor equivalence.
- A review lists explicit lineage candidates but does not select or certify a successor.
- Repair does not compensate external narration, game-engine effects, or player decisions automatically.
- Rev0150 supports one-to-one chains, not split or merge repair.
- Lacuna still does not call an LLM, infer dependencies from prose, or choose a winning world.

## 0.149.0 — rev0149

### Added

- Digest-bound governed revision: `revision-impact` reviews one active assignment at the current ledger head, and `world-revise` creates a custodied successor with lineage, reason, and review digest.
- Adjacent monotone commitment transitions with explicit bases, optional sources, durable hard-commitment policy, replay, verification, CLI, schemas, turn aliases, context, and explanations.
- First-class consequence links from world assignments to assertions, assignments, or questions, with typed relations, notice/material/binding severity, retirement, cycle refusal, bounded traversal, and endpoint lifecycle diagnostics.
- Transparent revision burden with named components and explicit probability/utility/causality/fairness nonclaims.
- Orphaned-consequence repair debt in conflicts, status, snapshots, planner context, and rebuild.
- Database schema 4 with ordered migration from schema 1, 2, or 3 while preserving the event-ledger head.
- Dedicated commitment, revision-impact, and consequence-link protocols plus current research, architecture, decisions, audit, and acceptance records.

### Fixed

- Refused silent exact-slot world-assignment replacement; all truth changes now use governed revision.
- Prevented hard commitments and active binding consequences from being revised in place.
- Prevented active assignment consequence cycles and bounded transitive impact analysis.
- Closed a high-severity perspective `explain` side channel in which visible records could disclose hidden world, constraint, or consequence IDs through dependency links.
- Removed raw event payloads/change IDs, source locators/metadata, agent metadata, and invisible ancestry from perspective explanations.
- Preserved historical visibility so an ended but once-visible assertion/source remains explainable without widening access.

### Refactored

- Extracted commitment ordering, burden policy, and deterministic cycle-witness logic from the storage class into a pure module.
- Separated ambient revision exposure from explicit authored consequence claims.
- Reused one consequence lifecycle query across status, conflicts, snapshots, planner context, and verification.
- Extended turn/world-scope reference validation and strict JSON Schemas for every governance operation.

### Nonclaims

- Burden is not probability, utility, causal effect, player surprise, agency, or narrative quality.
- Consequence links are authored policy, not discovered causality.
- Hard commitment is local mutation governance, not global canon.
- Lacuna still does not call an LLM, select a winning world, parse prose entailment, or automatically repair downstream consequences.

## 0.148.0 — rev0148

### Added

- First-class, event-sourced cardinality constraints with explicit members, inclusive `min_true` / `max_true` bounds, source, rationale, retirement, replay, snapshots, explanations, CLI commands, and Markdown projection.
- Open-world exactly-one, at-least-one, at-most-K, exactly-K, and ranged compatibility checks that never materialize unresolved member truth.
- Deterministic multi-record temporal witnesses spanning anchors and one candidate world at a time.
- Database schema 3 with ordered schema 1→2→3 and 2→3 migrations that preserve the event-ledger head.
- A registered list-reference normalizer for turn aliases, first used by cardinality member lists.
- Eleven cardinality, migration, firewall, alias, replay, and executable lifecycle tests, bringing the suite to 55.

### Fixed

- Prevented hidden constraint ontology from leaking through relation- or cardinality-derived diagnostics in perspective context.
- Refused new cardinality declarations that would retroactively invalidate anchors or live/selected worlds.
- Preserved honest unknowns under mathematically forced exactly-one completions.
- Added an end-to-end CLI path proving declaration, refusal, retirement, and post-retirement verification.

### Refactored

- Kept set-level bound evaluation as deterministic pure logic while the store owns event lifecycle, querying, and refusal policy.
- Unified scalar and list-valued alias handling through explicit registries.
- Extended migration custody as an ordered transactional chain rather than a release-by-release special case.

### Nonclaims

- Cardinality constraints are not a theorem prover, fairness metric, culprit selector, or automatic closure engine.
- A witness proves incompatibility with an authored bound, not that the bound is objectively true.
- Lacuna still does not call an LLM, resample worlds, generate prose, or score narrative quality.

## 0.147.0 — rev0147

### Added

- First-class, event-sourced claim relations: `excludes`, `negates`, `entails`, and `equivalent`.
- Relation declaration/retirement operations, CLI commands, projection queries, snapshots, replay, conflict reporting, and planner-context rendering.
- One-hop custody explanations across ledger record namespaces with origin, termination, dependencies, dependents, access class, and explicit nonproof semantics.
- Database schema 2, migration-custody records, and an explicit schema-1-to-2 migration that preserves the event-ledger head.
- Strict source-bound `lacuna.turn-request.v2` and `lacuna.turn-proposal.v2` schemas and examples.
- Nine relation, explanation, interval, replay, and migration tests, bringing the suite to 44.

### Fixed

- Refused partially overlapping opposite assignments to the same claim inside one candidate world while preserving exact-interval replacement.
- Prevented a newly declared relation from retroactively corrupting active anchors or live/selected worlds.
- Prevented claim-relation ontology from leaking through perspective context or perspective-scoped explanation queries.
- Removed stale turn-v1 documentation and schemas that omitted request-source and input-digest binding.

### Refactored

- Centralized same-claim and cross-claim compatibility in one relation-aware consistency engine shared by mutation, reactivation, conflict reporting, and verification.
- Separated physical database schema version from immutable event schema version.
- Kept logical closure outside stored custody: constraints reject incompatible explicit states but never materialize missing endpoint truth.

### Nonclaims

- Pairwise relations do not express exactly-one, at-least-one, arbitrary formulas, or natural-language semantics.
- `explain` is a custody trace, not a theorem prover or causal proof.
- Lacuna still does not call an LLM, choose a candidate world, resample particles, or score narrative quality.

## 0.146.0 — rev0146

### Added

- Campaign libraries with strict manifests, named campaigns, exact selection, default participants, and selected-library resolution for ordinary cube commands.
- A two-phase turn protocol: head-bound packet, external generation/reasoning, typed proposal, atomic commit, and narration/receipt output.
- Sequential `as` / `@alias` bindings so models do not need to calculate claim hashes or coordinate generated IDs.
- Narration source digests, declared audience disclosures, and visibility/source preflight.
- One structured context projection with JSON and Markdown renderers.
- Separately labelled audience and privileged planner contexts for director turns.
- JSON Schemas for libraries, campaigns, turn requests, and turn proposals.
- A dedicated documentation tree for architecture, protocols, design, research, decisions, audits, acceptance, and history.
- Seventeen campaign, turn, context-firewall, and executable end-to-end tests, bringing the suite to 35.

### Fixed

- Refused the rev0145 mixed-scope context path that could expose a named hidden world inside a perspective packet.
- Prevented hidden anchors or cross-world consensus from silently removing a visible claim from a perspective’s unsettled set.

### Refactored

- Centralized assertion and question visibility predicates.
- Separated context construction from Markdown rendering.
- Added atomic JSON replacement for library and campaign metadata.
- Kept all new behavior above database schema version 1; no event migration was introduced.

### Nonclaims

- Lacuna does not call an LLM or prove narration semantics.
- Narration bodies and campaign metadata are not stored in the story event chain.
- The runtime does not perform retcon search, particle resampling, or dramatic scoring.

## 0.145.0 — rev0145

### Renamed

- The project became **Lacuna**: an epistemic ledger for worlds that have not finished becoming true.

### Cut over

- Replaced the Datacube self-bearing continuation/release surface with a compact Python/SQLite semantic kernel.
- Established an immutable event ledger and deterministic projections.
- Added typed claims, assertions, provenance sources, agents, perspectives, visibility, narrative validity intervals, candidate worlds, world assignments, world-scoped evidence links, and open questions.
- Added anchor/world contradiction refusal and stale-head atomicity.
- Added perspective, canon, unknown, conflict, snapshot, and LLM-context projections.
- Added projection rebuild and integrity verification, including event/change-receipt agreement checks and ledger-only repair preflight.
- Added a three-world Lantern Room demonstration and eighteen invariant tests.

### Removed from the runtime

- Native self-compilation and toolchain custody.
- Capsule/release assembly and sidecar machinery.
- Operation profiling and continuation benchmarking.
- Cloud/container orchestration.
- Historical revision corpus from the shipped runtime.

The rev0145 cutover record is retained under `docs/history/rev0145/`.
