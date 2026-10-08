# Roadmap

The roadmap is ordered by epistemic leverage, not spectacle. Rev0169 is a send-ready polish pass over the test and release surface: the close-time SQLite WAL cleanup no longer uses a blocking truncation checkpoint, generated scenario capsules are refused until their placeholders are edited, the release is MIT-licensed, and recipient acceptance is documented as a bounded per-module runner. Rev0168's public-surface polish, rev0167's post-rating method-identifiability custody, and rev0166's send-surface, complete public-history custody, artifact doctor, and full retained-tree canary scan remain intact.

## Delivered in rev0169: test-harness repair, template gate, and MIT license

- Replaced close-time `PRAGMA wal_checkpoint(TRUNCATE)` cleanup with bounded passive checkpoint cleanup so fixture/subprocess readers cannot leave teardown waiting behind a truncating checkpoint.
- Added `tools/run_acceptance.py`, a bounded per-module acceptance runner that reports the exact module that fails or times out.
- Made generated scenario capsule templates fail closed until placeholder player inputs and model policy values are replaced.
- Added a top-level MIT `LICENSE` and current rev0169 architecture, research, audit, decision, and acceptance records.
- Preserved database schema 8, event schema 1, all rev0168/rev0167/rev0166 custody surfaces, ordinary play behavior, and parent-only authority.

## Delivered in rev0167: post-rating masking, method-identifiability, and child unblind gates

- Added a separate post-primary-rating masking stage before unblinding for four-condition scenario runs.
- Retained method guesses, confidence, cue text, familiarity, and recognition flags as typed artifacts.
- Joined method-guess correctness only during scenario and bundle report unblinding.
- Required bundle block seals to bind masking artifacts before any block can unblind.
- Added bundle child unblind gates opened by the parent with block-seal digests.

## Delivered in rev0166: send-ready entrances, complete history, full-tree scanning, and artifact self-check

- Made `PLAY_NOW.md`, `FOR_GWERN.md`, and `OPERATE_LACUNA.md` distinct manifest-enforced entrances for player, researcher, and parent/operator.
- Added `artifact check` for read-only manifest/member/version/syntax/parse/link verification of an extracted release; strict mode refuses any unlisted regular file.
- Added `history complete`, a checkpoint-bound ledger census requiring one exact retained committed managed-run transcript per durable pre-checkpoint audience turn.
- Added public-history/view and continuation-dispatch v2 contracts that distinguish explicit partial lists from complete-before-checkpoint coverage.
- Refused missing, duplicate, stateless-without-transcript, wrong-boundary, wrong-cube, wrong-audience, and ledger-mismatched completeness claims.
- Retained two preregistered high-entropy canaries per opaque scenario cell: operator-only and filesystem-only.
- Kept exact source allowlists and expected-absent classes while scanning the complete retained regular-file tree, including cube databases, SQLite sidecars, cooperative locks, and relative pathnames; no basename, suffix, or cube-subtree exemption.
- Refused unreadable/skipped traversal, links, nonregular files, multiple links, oversized/changing members, unplanned cell directories, and post-scan tree drift before blind-rating publication.
- Refactored descriptor authentication into shared sidecar helpers and added one incremental SHA-256/exact-token scanner that catches matches spanning read boundaries without retaining whole large files in memory.
- Preserved detected cells, propagated scan custody through bundle seals and rater exports, and preserved database schema 8, event schema 1, ordinary play behavior, and parent-only authority.

## Delivered in rev0164: source-bound fresh continuation and public-history custody

- Added `lacuna.checkpoint-continuation-dispatch.v1`, joining one authenticated committed checkpoint to one exact fresh ordinary turn and one dedicated `lacuna-fresh-narrator` role.
- Added `checkpoint run next-turn`, which requires the accepted checkpoint head and opens only an audience-only `play-turn`, `solo`, no-anchor turn before emitting the handoff.
- Added `checkpoint run continuation` for an already-open qualifying turn while retaining `narrator-capsule` as the reusable checkpoint-only artifact.
- Added `lacuna.public-history.v1` and `history build` to carry exact player input and accepted narration across a context reset with separate parent-side source custody and immutable event order.
- Authenticated exact player/narrator bytes against durable request and narration sources, refusing a fully self-consistent rehashed forgery.
- Added `lacuna.public-history-view.v1` so the fresh narrator receives exact prose continuity without run/request/proposal IDs, receipt hashes, or event positions.
- Refused invalid public history before creating a continuation turn, preventing forged content, chronology, cube, audience, or digest errors from leaving an orphan run.
- Added portable, Codex, Claude Code, Gemini CLI, and ChatGPT fresh-narrator aliases and focused operator instructions.
- Centralized ledger head-to-event-sequence lookup and committed-turn public extraction, reducing duplicated raw database and sidecar logic.
- Preserved database schema 8, event schema 1, rev0163 scenario topology, and parent-only accept/commit authority.

## Delivered in rev0163: fresh narrator capsules and context-reset treatment

- Added `lacuna.checkpoint-narrator-capsule.v1` with exact request, proposal, receipt, compression, state-card, audience-context, and post-commit-head custody.
- Added `checkpoint run narrator-capsule` and made it available after committed checkpoint audit.
- Excluded candidates, rejected rollouts, scores, provenance, verifier findings, and parent history from the capsule builder's accepted inputs.
- Made `continuation_mode` explicit: three persistent-context controls versus one fresh-narrator-capsule treatment.
- Required fresh pairwise-distinct role contexts, one narrator context per story segment, and exact checkpoint/capsule linkage for the first post-checkpoint turn.
- Added a concise root operator entrance, focused fresh-narrator guide, and an explicit disposition of the rev0160 direct-upload feedback.
- Preserved database schema 8, event schema 1, provider-neutral operation, and parent-only commit authority.

## Next: live conformance and completed evidence

- Run the preregistered conditions against actual fresh API/subagent/chat contexts and retain exact host settings, card/capsule bytes, public-context mode, complete-history custody when available, and transport logs.
- Run the preregistered operator/filesystem canaries against live provider contexts and publish all detected, refused, failed, and clean cells.
- Analyze retained method-identifiability confidence and cue fields without letting them alter frozen primary ratings after publication.
- Publish one complete pilot including null, negative, refused, and failed cells; report mechanical custody separately from human ratings.
- Preserve provider-native attestations where available without making one vendor mandatory or treating absence as failure.

## Delivered in rev0162: preregistered scenario bundles

- Added a two-to-128-block plan with complete capsule embedding, fixed rating comparability, story/model/replicate strata, primary dimensions, all-block inclusion, and terminal-failure retention.
- Added one private randomized schedule fixing block order, child run identities, and independent assignment seeds before any result is accepted.
- Added atomic all-child publication, public commitment, optional external-witness threshold, one-active-block execution, and cross-block context/invocation declaration checks.
- Added immutable blind block seals and an all-blocks-sealed-before-any-unblind state machine, including typed detection of direct witness bypass, future-child advance, and premature child unblinding.
- Added crash-resumable all-child unblinding and deterministic rater-level JSON, Markdown, and spreadsheet-safe CSV exports.
- Consolidated clone, sidecar-containment, private-directory, immutable-artifact, and staged-child construction; removed two competing draft experiment modules.
- Added hyperlegible ChatGPT, Codex, Claude Code, Gemini-oriented, native-subagent, separate-chat, human-bridge, scientific, Gwern-gift, architecture, audit, and threat guidance.

## Later: attestations, masking checks, and analysis contracts

- Preserve provider-native request/response attestations or signed exports where available without making one provider mandatory.
- Add a preregistered semantic-leak/masking review that complements the delivered exact-token canaries before ratings are accepted.
- Add rater assignment, masking-confidence fields, disagreement summaries, and explicit rater independence declarations without overstating them.
- Define portable analysis-plan exchange contracts for ordinal/hierarchical models, multiplicity policy, missingness/failure treatment, and sensitivity analysis; keep inference outside the custody kernel.
- Add a public redaction package that can share commitments, selected transcripts, mechanical outcomes, and rater-level observations without private schedules, assignments, or rejected futures.
- Add scientific-task bundle profiles separating private hypotheses, blind comparison, compact state updates, method/data verification, and public reports.
- Explore external transparency-log adapters that verify inclusion proofs while retaining an offline/manual witness route.

## Delivered in rev0161: comparative scenario capsules

- Added fixed forward-only, prompt-only-retcon, Lacuna-serial, and Lacuna-role-separated treatments on four exact verified seed clones.
- Added hidden assignment custody, opaque serial dispatch, fixed model/sampling/budget/rater policies, script-bound invocation records, declared context isolation checks, and frozen cell receipts.
- Added transcript-only blind rating packets, complete fixed-count rating custody, and deterministic post-rating unblinding with separate mechanical, host-declared, and human evidence.
- Added ChatGPT/human-bridge/native-subagent operational guidance and explicit limits on randomization, semantic blindness, provider attestation, and single-block inference.
- Refactored initial run publication into one shared private staging/rename primitive and closed ordinary turn cube-path ambiguity.

## Delivered in rev0160: managed checkpoint runs and invocation custody

- Wrapped the stateless checkpoint protocol in `lacuna.checkpoint-run.v1` with one authoritative manifest, exact stage topology, deterministic next action, and explicit `awaiting-*`, `verifier-refused`, `ready-to-commit`, and `committed` states.
- Added `lacuna.checkpoint-run-agent-dispatch.v1`, embedding the exact current card, fixed provider route and alias, save/accept/failure commands, authority boundary, and nonclaims.
- Added ordered `lacuna.checkpoint-invocation-receipt.v1` custody for accepted and failed attempts, including exact card/dispatch/output digests and honest host-declared model metadata.
- Added per-role heterogeneous routing, source-path binding, full chain reconstruction on every transition, one accepted receipt per retained role output, pointer-only recovery, and terminal verifier refusal.
- Reused one shared hardened sidecar implementation across ordinary turns and checkpoints rather than allowing security-critical read/lock behavior to drift.
- Authenticated committed checkpoint receipts against the complete retained chain and durable ledger change, while avoiding redundant exact-preparation replay on already validated internal paths.

## Later: connected checkpoint adapters, retention, and live conformance

- Add narrow Action/App/MCP/HTTP adapters exposing only managed checkpoint begin/status/dispatch/accept/failure/recover/commit—not arbitrary mutation, sidecar editing, or seal custody.
- Run live conformance smokes against installed Codex, Claude Code, Gemini CLI, ChatGPT-connected hosts, and other frontier systems; downgrade honestly to serial or human-bridge execution when isolation or tools are unavailable.
- Add explicit archive, encrypt-at-rest, redact, retention, and deletion policy hooks because checkpoint runs may contain privileged rejected futures and planner context outside the event ledger.
- Decide whether a future run export should be version-neutral, migratable, or deliberately immutable; do not silently reinterpret old role cards under a new runtime.
- Keep automatic checkpoint triggering, provider selection policy, and aesthetic optimization outside the kernel until comparative evidence justifies stable contracts.

## Next: factor dependence, correction, and portability

- Give related assertions explicit evidence-family or dependence identities so shared observations cannot be multiplied as though independent.
- Distinguish conditional, alternative, duplicate, derivative, and jointly assessed factors.
- Design factor replacement as reviewed predecessor→successor lineage for correcting a mistaken likelihood vector without deleting the original assessment.
- Decide whether a superseding assertion always withdraws its factor or whether an explicit factor-disposition operation should override that default.
- Bind likelihood assessments to typed evidence packets, assessor identity, method, and intended conditioning assumptions.
- Design a factor-portability review for structural epoch changes; never carry old likelihoods across changed custody automatically.
- Add an explicit zero-likelihood policy: extinction review, reversible quarantine, declared floor, or deliberate irreversibility.
- Evaluate decimal, rational, or canonical fixed-point wire arithmetic for reproducibility beyond one supported Python/SQLite runtime.

## Next: particle proposal, ancestry, and diversity

- Branch worlds by explicit deltas without eager assignment copies.
- Record proposal parentage, proposer, rationale, and generation/search receipt.
- Trigger proposal from explanatory residuals—not merely low ESS—when all surviving worlds fit new evidence badly.
- Distinguish a new explanatory mode from a duplicate valuation with different custody.
- Design resampling as a separate reviewed act with ancestry records.
- Preserve minority explanations through a declared diversity floor or mode reserve.
- Compare ESS with valuation-group count, claim-disagreement coverage, explanatory residual, and semantic clustering.
- Never make maximum weight an automatic winning-world selector.

## Next: stronger fair-play witnessing and richer repair policy

- Design explicit one-to-many split and many-to-one merge repair without weakening one-to-one lineage.
- Decide whether consequence severity changes require replacement or a dedicated governed transition.
- Bind optional repair reviews to a proposed candidate fingerprint for high-assurance hosts.
- Add configurable human approval gates above the kernel’s fixed blocker policy.
- Add optional signed or co-signed receipt witnesses without coupling the kernel to one service.
- Design a Merkle seal scheme for independently revealable clue or solution leaves.
- Define campaign policy for minimum sequence gaps, required intervening disclosures, and repeated-void diagnostics.
- Test concurrent review/update/reconciliation/repair races across separate processes and adapters.

## Next: epistemic actions and agent-relative possibility

- Separate ontic state changes from observation policies.
- Represent which alternatives each agent considers possible without conflating that graph with the planner’s candidate-world bank.
- Support public, private, and partially observed announcement/action primitives.
- Add nested belief only where a concrete campaign use case pays for its complexity.
- Keep original assertions provenance-bearing; make closure an inspectable projection.

## Next: anti-overfitting and counterfactual integrity

- Penalize explanations that promote excessive atmospheric detail into clues.
- Track explanatory complexity, reincorporation count, coincidence cost, and identity drift.
- Represent actions, affordances, and causal dependencies outside the authored consequence graph.
- Probe nearby unchosen actions against the same candidate-world population and factor checkpoint.
- Measure causal divergence separately from retrospective significance.
- Track character core values, motive changes, and identity drift.
- Build seam-hunting, mystery-fairness, factor-dependence, stale-portability, and rubber-reality test suites.

## Then: disclosure compilation

- Generate narration from an already accepted semantic delta.
- Extract candidate claims from prose into a review-only proposal.
- Compare prose implications with permitted disclosure sets.
- Refuse or regenerate hidden-world leakage and unsupported physical facts.
- Add transcript custody as an outer campaign service with digest verification.

## Integration surfaces

- Portable model entrance: read-only verified brief as resource/prompt, with explicit chat/workspace/orchestrated capability profiles.
- Digest-bound orchestration: packet audit and role cards as read-only resources/prompts; parent-only commit remains the sole mutation tool.
- Thin MCP/Action/App adapter: context and task cards as resources, turn packet/commit and visible receipt inspection as narrow tools; seal custody remains administrative.
- Chat-host adapter retaining exact transcript bytes, proposals, reviews, and receipts.
- Human review queue for proposed anchors, hard commitments, binding consequences, factor correction, zero-likelihood assessments, and resampling.
- Game-engine bridge where the engine owns physical simulation and Lacuna owns custody/disclosure scope.
- Read-only observability endpoint for head, migrations, verification, factor reconciliation, particle debt, impact reviews, and consequence repair debt.

## Explicitly deferred

- A built-in LLM client.
- Autonomous self-modification or self-release.
- A general-purpose story authoring UI.
- Arbitrary natural-language theorem proving.
- Claims that normalized weights, ESS, reconciliation, consistency, burden, seals, or custody prove narrative quality, agency, causality, calibration, or fairness.
