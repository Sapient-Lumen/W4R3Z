# Glossary

**Active assignment slot** — one world, claim, timeline, and exact validity interval with a currently active world assignment. Lacuna refuses a second occupant; changing truth requires governed revision.

**Ambient exposure** — records near a revision target, such as assertion history, evidence, questions, constraints, inherited worlds, and cross-world agreement. Exposure raises review attention but does not assert causality.

**Agent dispatch** — a strict `lacuna.agent-dispatch.v1` sidecar envelope for one delegated stage. It names the provider route and role, binds the retained card metadata/digest, embeds the exact card as `input_document`, specifies one return contract, separates worker from parent authority, and invokes no provider by itself.

**Anchor** — an active assertion whose contradiction would violate an observed event or explicit irrevocable commitment over its stated narrative interval.

**Assertion** — an agent’s stance toward a neutral claim, including assertor, perspective holder, source, basis, standing, confidence, visibility, and valid time.

**Audience context** — a perspective-scoped projection containing only records visible to a named epistemic subject. Candidate worlds, constraints, consequence links, revision guards, privileged evidence interpretation, and cross-world consensus are omitted.

**Burden** — a transparent ordinal review policy over recorded revision custody. It is not probability, utility, causality, fairness, or story quality.

**Campaign** — human-facing metadata plus one Lacuna cube. Title and selection are convenience metadata, not story canon.

**Chat-only play** — an immediately playable conversation in a model surface that lacks a live Lacuna packet/commit bridge. It may preserve the game conversationally but must not claim durable cube mutation.

**Checkpoint** — a source-bound backstage comparison opened with request purpose `checkpoint`. It freezes protected state and policy, walks exact generator → provenance-blind judge → winner-only compressor → verifier artifacts, and leaves assembly, kernel review, and commit with the parent.

**Checkpoint dispatch** — a strict `lacuna.checkpoint-agent-dispatch.v1` envelope recomputed from one validated checkpoint task card and provider route. It embeds the complete card and exact return contract, invokes no provider, and grants no assembly or mutation authority.

**Checkpoint invocation receipt** — an ordered `lacuna.checkpoint-invocation-receipt.v1` sidecar record for one managed-run attempt. It binds run, checkpoint, role, fixed route, role card, exact dispatch, expected output schema, host-declared model/timing metadata, and either one retained accepted output or one failure class. It is not provider-signed attestation.

**Checkpoint narrator capsule** — a deterministic `lacuna.checkpoint-narrator-capsule.v1` private host artifact compiled only from an authenticated committed request, proposal, compression, receipt, and post-commit audience context. It binds the selected state card and accepted public context for a fresh continuing narrator while excluding raw candidates, rejected rollouts, judge rationale, worker provenance, verifier findings, and parent history. It is not canon, a write grant, or proof that a provider forgot prior context.

**Checkpoint continuation dispatch** — a strict `lacuna.checkpoint-continuation-dispatch.v2` envelope joining one authenticated committed checkpoint to one fresh audience-only ordinary turn. It binds the capsule, exact next player input, optional authenticated v2 parent-history digest plus coverage-labelled least-context prose view, ordinary turn packet/proposal identity, provider alias, save path, and parent accept command. Its public-context mode distinguishes typed-only, explicit partial history, and checkpoint-bound complete durable-turn history. The `lacuna-fresh-narrator` worker can return one proposal but cannot accept or commit it.

**Checkpoint next turn** — the `checkpoint run next-turn` parent operation that requires the live checkpoint head, opens one `play-turn`/`solo`/no-anchor ordinary run, and emits its fresh-narrator continuation dispatch. It is not a model invocation or head reservation.

**Checkpoint run** — a strict `lacuna.checkpoint-run.v1` private sidecar state machine that turns the source-bound generator → judge → compressor → verifier protocol into one resumable walk. It fixes per-role provider routes, retains exact artifacts and invocation receipts, emits one deterministic `NEXT.md`, makes verifier refusal terminal, and leaves assembly, review, commit, recovery, and presentation with the parent. It is not a ledger event or model client.

**Checkpoint-run dispatch** — a self-contained `lacuna.checkpoint-run-agent-dispatch.v1` envelope recomputed from one managed run’s current card and fixed provider route. It embeds the complete card plus exact accept/failure commands so a remote chat or subagent need not infer local paths or later stages.

**Checkpoint-run next action** — the deterministic owner, fixed provider route when delegated, complete input path, expected schema, parent command, and visibility rule for the current managed checkpoint status. `run.json` is authoritative; `NEXT.md` is an audited recoverable rendering.

**Checkpoint protected state** — the digest-bound audience assertions, anchors, cross-world consensus, fair-play metadata, constraints, consequences, revision guards, open questions, unsettled claims, and exact unknown identifiers that a checkpoint must preserve or explicitly respect.

**Provenance-blind judging** — a card construction that removes generator provider/model/invocation labels and notes before scoring. It reduces one bias channel; it does not prove semantic anonymity, worker independence, or absence of collusion.

**Rollout beat** — one explicit ordered speculative future step in a noncanon checkpoint candidate. Every candidate must contain exactly one beat per declared horizon turn. Beats are experiment artifacts, not accepted story events.

**Selection custody** — the digest-bound evidence that records candidate artifact, judgment artifact, deterministic rule, eligible scores, winner, protected state, and selected state-card continuity. It proves internal artifact agreement, not aesthetic merit.

**Candidate world** — one weighted, coherent partial hidden-world hypothesis. Weight guides planning attention; selection favors it for one planning purpose. Neither act makes it global truth.

**Cardinality constraint** — an inclusive lower and upper bound on how many members of a fixed claim set may be true. Missing and `unknown` members remain unresolved.

**Claim** — a content-addressed neutral proposition. Declaring a claim does not assert it.

**Claim relation** — an explicit compatibility constraint between two claims. `excludes`, `negates`, `entails`, and `equivalent` reject incompatible explicit assignments without materializing closure.

**Commitment** — mutation policy attached to one world assignment: `tentative`, `soft`, `firm`, or `hard`. It is distinct from confidence and truth.

**Commitment basis** — recorded policy reason for a commitment level: `legacy`, `planning`, `authored`, `evidence`, `disclosure`, or `precommitment`.

**Commitment transition** — an event-sourced adjacent raise from one commitment level to the next, with basis, optional source, and rationale.

**Consequence link** — an authored directed dependency from one world assignment to an assertion, world assignment, or question, with relation and severity.

**Consequence severity** — `notice`, `material`, or `binding`. Binding blocks incident revision; softer links contribute burden and may become repair debt.

**Consequence repair** — an identified, digest-reviewed, atomic predecessor-to-successor replacement relation. It ends the old link and creates the new one without deleting either from custody.

**Consequence repair review** — a base-head-bound planner receipt describing one active predecessor, lifecycle state, explicit lineage candidates, blockers, and authorization digest. It does not choose or certify the successor.

**Consequence replacement lineage** — the one-to-one chain formed when a consequence is replaced. A successor may later become a predecessor, producing a visible middle node rather than a collapsed latest value.

**Constraint** — a rule used to reject inconsistent explicit state. It is distinct from an inference that creates another stored fact.

**Constraint retirement** — the additive ending of an active relation or cardinality constraint. Its declaration remains in custody.

**Constraint witness** — a deterministic set of records and temporal intersection sufficient to demonstrate a bound violation. It supports refusal; it does not prove the rule is correct.

**Custody explanation** — a record-level trace of origin, termination, direct dependencies, direct dependents, and access class. It is not proof of truth, causality, fairness, or sufficient justification.

**Cube** — the event ledger, change receipts, schema custody, and deterministic semantic projections for one represented campaign/world space.

**Database schema** — the physical SQLite/projection layout. The current revision uses database schema 8 while retaining event schema 1.

**Disclosure** — an assertion declared visible through a narration turn. Lacuna validates identity, source linkage, grant, and audience visibility, not full natural-language entailment.

**Epistemic ledger** — the typed record separating observation, testimony, belief, hypothesis, perspective, visibility, constraint, commitment, consequence, and world assignment.

**Event schema** — the immutable event envelope/payload contract version. It evolves independently from database schema.

**Governed revision** — the current-head review plus successor-creation protocol used to change an active world assignment’s truth without overwriting history.

**Fair-play seal** — an event-backed salted digest binding one external opening to a cube and seal identity. It proves exact-opening continuity under its trust assumptions, not truth or fairness.

**Fair-play seal opening** — the secret external bundle containing payload and 256-bit nonce. It stays outside the cube until reveal.

**Fair-play seal receipt** — a visible lifecycle view plus an immutable origin core and stable digest suitable for retention or external anchoring.

**Hard commitment** — a local prohibition on in-place revision. It requires a world fork or explicit custody repair; it does not canonize the claim across all worlds.

**Input kind** — the validated classification attached to exact turn text: `session-control` for out-of-fiction play management or `play-turn` for the active in-play exchange. It constrains routing and source custody; it does not itself authorize mutation.

**Impact digest** — SHA-256 over a revision review core including the atomic change-set base head. Any separately committed intervening event makes it stale; one atomic change-set shares its base head.

**Lacuna** — an explicit unresolved question or unsettled claim. Unknown is data, not permission to fill a blank.

**Library** — a directory of campaigns with one selected campaign for human convenience.

**Model brief** — a read-only `lacuna.model-brief.v1` entrance resolved from one cube or selected campaign. It reports verification/readiness, execution-profile assumptions, exact turn-run behavior, provider role aliases, recovery paths, and nonclaims. It grants no write authority.

**Model profile** — one capability contract for a host surface: `chat`, `workspace`, or `orchestrated`. A profile describes what the host can do; it is not a model-quality ranking or vendor identity.

**Narration source** — a source record containing a digest and provenance metadata for returned prose. Lacuna does not retain the prose body.

**Narrator return** — an exact `lacuna.narrator-return.v1` sidecar object bound to one narrator task, packet digest, and planner-return digest. It contains audience prose and directly observable facts only. It is not accepted narration until incorporated into a proposal and committed by the parent.

**Open-world cardinality** — bound evaluation where absent or explicitly unknown members may take either value in a possible completion. Refusal occurs only when no completion can satisfy the bound.

**Orphaned consequence** — an active consequence whose premise or dependent has ended. It is a visible repair obligation, not projection corruption.

**Orchestrated turn** — a source-bound turn in which a parent/coordinator may delegate planner, audience-only narrator, packet-bound proposal-builder, and read-only verifier tasks through generated role cards. A request-scoped run retains and audits the handoff chain. Subagents do not gain run or commit authority.

**Orchestration plan** — a deterministic, read-only `lacuna.orchestration-plan.v1` sidecar derived from an audited turn packet. It selects `solo`, `pair`, or `full`, records why, lists exact stages and card commands, and grants no authority. Automatic selection is policy, not a model-quality theorem.

**Packet digest** — SHA-256 of canonical JSON for one strictly audited turn packet. It binds sidecar task cards and returns to exact packet content; it is continuity evidence, not host authentication or semantic proof.

**Parent/coordinator** — the host process or primary workspace agent that captures exact input, begins and advances the run, renders and routes worker dispatches, approves the final proposal, commits it, and presents only accepted narration. Workers never acquire this authority from a provider alias.

**Play start** — the `lacuna.play-start.v1` entrance that safely resolves or explicitly bootstraps a campaign, retains one exact message as `session-control`, opens a request-scoped run, and returns the first next action. It does not invoke a model or narrate.

**Pointer recovery** — explicit reconstruction of only deterministic `NEXT.md` after every authoritative turn-run or checkpoint-run member passes audit. It never creates or repairs a packet, task card, model return, proposal, preparation, review, manifest, invocation receipt, or commit receipt.

**Partial valuation** — explicit true, false, and unknown assignments recorded for some claims. Absence is not falsehood.

**Particle bank** — the complete normalized planner projection over all live or selected candidate worlds. It includes raw weights, projected probabilities, fingerprints, concentration diagnostics, and applied-factor/debt summaries. It is not canon or a calibrated posterior.

**Particle-bank digest** — SHA-256 over the eligible population’s world IDs, statuses, raw weights, valuation fingerprints, and custody fingerprints. It authorizes one reviewed update and stales when the represented population changes.

**Particle update** — one immutable complete-population multiplication of prior planning attention by authored per-world likelihoods, followed by normalization. It changes weights only.

**Evidence factor** — one assertion used once as the evidential basis for a particle update. Its original update remains immutable even if the assertion later ends. Single use prevents exact repeated multiplication; it does not prove independence or calibration.

**Factor epoch** — the structurally coherent interval after the latest world creation, assignment, revision, commitment raise, manual weight change, or eligibility-status change. Factors are replayed only inside their epoch.

**Factor reconciliation** — a head-bound, complete-population replay that starts from one immutable epoch baseline, includes every still-authorized factor, records ended factors as excluded custody, normalizes in log space, and appends `particle.reconciled`. It repairs current planning weights without rewriting update history.

**Factor-set digest** — SHA-256 over the reconciliation epoch, baseline, and ordered included/excluded factor dispositions. It binds which historical reasons were replayed or withheld.

**Included factor** — a current-epoch factor whose evidence assertion remains active at the reconciliation head and is therefore replayed exactly once.

**Excluded factor** — a current-epoch factor whose evidence assertion ended before reconciliation. Its original update remains in custody, while the repaired distribution omits its likelihood vector.

**Effective sample size (ESS)** — `1 / Σw²` over normalized particle weights, reported as a concentration diagnostic. It is not a literal count of good, independent, or narratively diverse worlds.

**Reweighting debt** — a current-epoch particle factor whose evidence assertion has ended and whose effect has not yet been explicitly excluded by reconciliation. The historical update remains in custody. Structural epoch retirement or a later reconciliation resolves current debt without deleting the factor.

**Valuation fingerprint** — a digest over a world’s explicit active ontic assignments, excluding record identity, confidence, commitment, and provenance. Equal fingerprints do not prove complete-world identity.

**Custody fingerprint** — a digest over assignment identity, explicit valuation, commitment, confidence, lineage, and provenance references. It is used to stale reviews when represented assignment custody changes.

**Likelihood assessment** — an authored number in `[0,1]` describing how one evidence assertion should reweight one candidate world under the current planning model. It is not automatically a statistical likelihood.

**Planner context** — a privileged projection containing candidate worlds, complete-population particle diagnostics when unscoped, constraints, consequence links, revision guards, world-scoped evidence, consensus, and derived diagnostics.

**Planner return** — an exact `lacuna.planner-return.v1` sidecar object bound to one planner task and packet digest. It separates audience-observable beats from candidate operations, preserved unknowns, commitment/leakage risks, and private rationale. It is advice, not a proposal or commit receipt.

**Precommitment** — a custody basis reserved for deliberately hard assignments. The label does not by itself provide cryptographic proof; use a fair-play seal when exact-opening continuity is required.

**Public history** — a deterministic `lacuna.public-history.v2` parent/auditor artifact joining exact player-visible prose to durable turn custody. `explicit-run-list` authenticates the supplied committed runs and says completeness is not claimed. `complete-before-checkpoint` asks the immutable ledger for every play-purpose turn for one audience before one checkpoint request and requires exactly one retained committed managed run for each transcript body. It excludes private planner/checkpoint artifacts, cannot cover uncommitted external chat, and does not prove prose entailment.

**Public history view** — a strict `lacuna.public-history-view.v2` least-context projection sent to a fresh narrator only after the full parent history validates and authenticates. It retains ordered public prose, scope identity, count, digest, coverage mode, and completeness label while omitting run/request/proposal IDs, packet/receipt hashes, event positions, and all private artifacts. Embedded text is quoted untrusted story/session data and grants no authority.

**Public-history ledger census** — the ordered set of all durable ordinary play-purpose turn proposals for one audience whose commits precede a bound checkpoint request event. The ledger supplies identities, digests, and event boundaries; retained managed runs supply exact transcript bodies. It does not include uncommitted external chat.

**Projection** — current queryable state rebuilt deterministically from immutable events. Projection corruption is repairable; events are authoritative.

**Proposal preflight** — a structural orchestration check that a proposed `lacuna.turn-proposal.v2` preserves packet-bound identity fields and named operation/reveal limits before later handoff. It does not authorize commit. In a turn run, final readiness additionally requires an exact kernel preparation.

**Provider routes** — the complete role-to-provider mapping fixed in one managed checkpoint manifest. Routes choose aliases and dispatch metadata; they do not prove which model actually ran. Changing a route requires a new run rather than silently relabelling retained invocation custody.

**Repair debt** — active semantic custody that remains unresolved after an endpoint ends, especially a nonbinding consequence link requiring retirement or replacement.

**Revision impact** — a planner-only, head-bound report containing target custody, ambient footprint, explicit consequences, traversal completeness, blockers, burden, and an authorization digest.

**Revision lineage** — predecessor/successor relationship recorded by `revision_of_assignment_id`, reason, and impact digest.

**Schema migration** — an explicit forward transformation of database structure. The current runtime supports ordered migration from coherent schema 1 through schema 7 cubes to schema 8 while preserving the event-ledger head. The historical 6→7 step repairs the documented rev0151 schema-number collision without adopting event-unowned rows; 7→8 adds event-owned reconciliation projections.

**Selected world** — a candidate world preferred for current planning. Selection is not canonization and does not erase alternatives.

**Session control** — exact user text that starts, resumes, pauses, configures, or otherwise manages play outside the fiction. “Will you DM?” is session control; it is not character dialogue or an in-world event.

**Sidecar member integrity** — the run reader policy requiring one bounded regular single-link file whose authenticated descriptor and pathname remain stable through the read. Links, non-regular files, oversize members, and detected substitution refuse. This is not a hostile same-user security boundary.

**Turn packet** — a source-backed, head-bound request containing exact input, input digest and kind, least-authority grant, audience context, optional separate planner context, and a safe narration-only proposal template. New packets use request v4 with explicit input kind and purpose; supported v2 packets default to `play-turn`/`play`, and v3 packets preserve input kind while defaulting purpose to `play`.

**Turn task card** — a strict `lacuna.turn-task-card.v1` sidecar generated from one audited packet and any required validated upstream artifacts. It provides one role only its allowed input, exact instructions, output schema/template, digest bindings, and no commit authority.

**Turn proposal** — narration plus typed operations and declared disclosures. Empty operations are valid. Any supplied operations are normalized, grant-checked, visibility-checked, and committed atomically.

**Turn preparation** — a strict `lacuna.turn-preparation.v1` replay envelope produced by applying one normalized proposal through the real kernel mutation path and rolling the transaction back. It freezes generated IDs, time, event IDs/hashes, receipt, head, and projected contexts. It proves local executable consistency at one request head, not commitment, truth, provider authorship, or a reserved head.

**Turn receipt** — a strict `lacuna.turn-receipt.v3` acceptance record bound to one exact preparation and durable ledger change. Its delivery metadata distinguishes direct replay from crash recovery without changing the underlying epistemic custody.

**Turn run** — a request-scoped `lacuna.turn-run.v2` sidecar state machine for one exact input. It retains topology-required artifacts, binds them in `run.json`, emits deterministic `NEXT.md`, renders delegated dispatches, requires exact rollback preparation before readiness, serializes cooperative local transitions with `.run.lock`, and advances through parent-owned `begin`, `accept`, `recover`, and `commit`. It is not a ledger event, provider attestation, distributed lock, or proof of isolation.

**Turn-run next action** — the deterministic owner, complete input artifact, expected schema, parent command, and player-visibility rule for the current run status. A delegated action also points to the provider-dispatch command. `run.json` is authoritative; `NEXT.md` is an audited, recoverable rendering.

**Unknown** — an explicit truth value or absence of assignment that remains unresolved. It is never automatically converted to false.

**Verifier return** — an exact `lacuna.verifier-return.v1` advisory sidecar bound to one packet and proposal digest. Its template fails closed as `refuse`; even `pass` never replaces `turn commit` validation or authorizes presentation.

**World assignment** — one explicit truth value for one claim inside one candidate world over one narrative interval, with commitment and provenance custody.

**World fork** — creation of a child candidate world that inherits current assignments and may later diverge. Forking preserves alternatives; revision corrects one hypothesis lineage.

## Rev0161 experiment terms

**Contamination canary** — A deterministic domain-separated high-entropy token preregistered for one opaque scenario cell. An `operator-only` canary is intentionally present in the complete private cell driver; a `filesystem-only` canary is present only in a separate private file whose path and digest, but not body, are disclosed to the cell coordinator. A match outside its exact source allowlist is retained evidence of contamination, not automatic exclusion or provider attribution.

**Contamination plan** — The private `lacuna.scenario-contamination-plan.v1` artifact created at scenario begin. It binds every per-cell canary, scope, exact source paths, expected-absent artifact classes, complete retained-cell-tree scan policy, file/member limits, and nonclaims before any result exists. No cube, SQLite-sidecar, lock, suffix, or basename subtree is exempted from content/path scanning.

**Contamination scan** — The private `lacuna.scenario-contamination-scan.v1` artifact manufactured exactly once after all cells are frozen and before blind-rating material. It descriptor-reads the declared retained experiment-artifact boundary, classifies same-cell and cross-cell unexpected exact-token matches, binds a file manifest digest, and reports `clean` or `leak-detected`. Clean does not prove isolation or forgetting.

**Scenario capsule** — A seed-bound fixed script, four-condition set, model/sampling policy, budget, rubric, and rater count used to manufacture one comparative run.

**Opaque cell** — One exact seed clone named by a label that does not disclose its private condition assignment.

**Scenario driver** — The private complete local contract for executing one opaque cell, including condition topology and exact return template.

**Declared context ID** — A host-supplied identifier used to detect internally inconsistent context reuse. It is not provider attestation of a fresh conversation.

**Continuation mode** — The scenario contract stating whether narration intentionally remains in one persistent context or must move to a fresh capsule-bound narrator after a managed checkpoint. It is a testable host declaration, not provider attestation.

**Continuation capsule linkage** — The tuple of managed checkpoint ID, continuation checkpoint ID, and checkpoint narrator capsule digest that binds the first ordinary narration attempt after a role-separated checkpoint to the exact compressed continuation artifact.

**Blind rating packet** — A transcript-only artifact under opaque cell labels, bound to a fixed rubric and intentionally excluding structured condition identity.

**Unblinded report** — The deterministic post-rating join of condition assignment, frozen cell evidence, mechanical outcomes, host declarations, and human rating summaries.

## Rev0162 replicated-experiment terms

**Scenario bundle** — A preregistered parent sidecar over two to 128 single-block scenario runs. It fixes the complete block roster, private order, child identities, assignment seeds, comparable rating contract, inclusion rule, witness threshold, seals, and aggregate report before or during controlled transitions. It is not a player-facing game mode or statistical conclusion.

**Bundle plan** — The complete pre-execution roster of normalized seed paths, embedded capsules, story/model strata, replicate labels, primary dimensions, inclusion policy, witness threshold, notes, and nonclaims.

**Private schedule** — The master-seed-derived fixed order of opaque blocks, child scenario run IDs, and per-child assignment seeds. It must not be given to blind raters before bundle unblinding.

**Public bundle commitment** — A condition-mapping-free canonical digest boundary over the exact plan, private schedule, child seed boundaries, capsules, and hidden assignments. External retention can make later mutation or disappearance detectable; it is not trusted time or proof that no earlier unwitnessed bundle existed.

**External witness record** — An operator-supplied local description of a receipt retained by another person or service and bound to the public commitment digest. Lacuna does not verify the external signature, timestamp, service, locator, or continued availability.

**Witness gate** — A preregistered minimum count of unique external receipt records required before the first child can advance. Direct child advance before the threshold contaminates the retained bundle and is detected on audit.

**Block seal** — An immutable join of one rated child's run, capsule, assignment, blind packet, and rating artifact digests. It freezes the block while leaving the child structurally blind.

**Seal-all-before-unblind** — The invariant that every scheduled block must have a valid seal and every child must remain `ready-to-unblind` before the parent can durably enter aggregate unblinding.

**Premature child unblinding** — Direct production of a child report before the parent enters its all-block unblinding phase. This crosses the information boundary and is contamination, not recoverable parent-cache drift.

**Bundle report** — The deterministic post-unblind join of every scheduled child, terminal cell status, rater-level integer score/rank/comment, mechanical outcome, and host-declared execution total. It computes descriptive counts and sums only.

**Rater-level observation** — One retained rater × condition × block record. It is the analysis-preserving unit exported by JSON and CSV rather than only a condition-level aggregate.

**Spreadsheet-safe CSV** — A convenience export that prefixes text beginning with common formula triggers before spreadsheet import. Canonical JSON preserves the exact authored text.
