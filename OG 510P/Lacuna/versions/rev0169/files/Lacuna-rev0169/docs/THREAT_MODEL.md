# Threat model

## Protected by current design

### Ledger, mutation, and schema custody

- Partial, stale, malformed, or unauthorized change-sets are refused atomically.
- Event mutation is detected by ledger verification when the verifier and database are not both replaced by an attacker.
- Projection corruption can be rebuilt from valid events.
- Unknown operation, proposal, manifest, and cube-config fields are refused.
- Coherent schema-1 through schema-7 cubes require explicit integrity-checked migration to schema 8; every step preserves the event-ledger head.
- The schema-6 collision repair accepts the two official empty/absent particle shapes but refuses nonempty event-unowned particle rows before destructive DDL; that refusal is not misapplied to legitimate schema-7 particle projections.
- The bundled executable suppresses ambient Python site initialization, so unrelated site packages and `sitecustomize` hooks are outside that launcher’s runtime boundary.

### Epistemic and revision custody

- An occupied active assignment slot cannot be silently replaced.
- Truth-changing revision requires a current-base-head impact digest and records predecessor, successor, reason, and digest.
- Hard commitment blocks in-place revision and requires a durable basis.
- Commitment transitions are adjacent, monotone, timed within assignment custody, and replay-verifiable.
- Binding incident consequences block revision; softer links remain visible repair obligations when endpoints end.
- Consequence replacement requires a digest-bound review and atomically preserves predecessor, successor, reason, and repair lineage.
- New consequence custody refuses ended assignments/assertions and closed questions.
- Assignment-cycle checks model the post-replacement graph.
- Explicit pairwise and cardinality constraints apply across anchors and every live/selected world.
- Missing and `unknown` constraint members remain unresolved; rules never silently materialize forced values.

### Particle-bank and factor-ledger custody

- A reviewed particle update covers every live or selected world exactly once; hidden subset normalization is refused.
- The review digest covers population membership, status, raw weight, explicit valuation fingerprint, and assignment custody fingerprint.
- A changed population, assignment, commitment, provenance reference, status, or weight makes the bank receipt stale.
- An evidence assertion must be active and may act as a multiplicative factor only once.
- Single use is enforced during review, operation preparation, projection insertion, and physical schema validation.
- Two uses of the same factor inside one atomic change-set refuse and roll back the first update.
- All-zero posterior mass, zero prior mass, duplicate/missing assessments, nonfinite values, and malformed likelihoods are refused before commit.
- A particle update changes weights only. It cannot create, delete, select, prune, archive, fork, merge, revise, assign, anchor, disclose, or canonize a world as a side effect.
- Historical member status, prior/posterior arithmetic, normalization, ESS, entropy, information gain, fingerprints, and bank digests are replay-verified.
- Projection tampering and orphan particle rows are verification-visible and rebuildable from canonical events.
- Superseding an already-applied evidence assertion leaves the original factor in immutable custody and surfaces reconciliation debt.
- A reconciliation review reconstructs the latest coherent factor epoch from the first update’s immutable prior, classifies every factor as included or excluded, and binds the complete projected result to the current head.
- Reconciliation uses max-shifted log-space replay, so positive mass lost only through sequential multiplication underflow can be recovered.
- Structural mutations start a new factor epoch; stale likelihoods are not replayed across changed world membership, valuation, custody, status, or authored prior.
- A reconciliation appends a separate `particle.reconciled` event, retains withdrawn factors as excluded history, and changes weights only.
- Baseline/current/posterior digests, factor-set selection, included/excluded authority, per-world arithmetic, statistics, origin events, and projection rows are independently replay-verified.
- A repeated reconciliation of the same factor set and posterior is refused; a stale review or changed denominator is refused atomically.
- The complete particle bank, factor history, reconciliation review/history, rationales, and diagnostics are planner-only; a world-scoped director cannot update or reconcile the global denominator.

### Access and turn custody

- Perspective context omits candidate worlds, particle bank/history, reconciliation state, constraints, consequence links, revision guards, privileged evidence interpretation, consensus, and hidden-ontology diagnostics.
- Perspective-scoped explanation checks every returned dependency/dependent, strips raw event payloads/change IDs, removes source locators/metadata, and sanitizes invisible ancestry.
- A perspective context cannot be combined with a named hidden world.
- Turn-request v3 packets commit exact input digest, explicit `session-control`/`play-turn` kind, and least-authority grant before a proposal exists; supported v2 packets default to `play-turn` rather than inferring a new meaning.
- Narration disclosures must reference active assertions visible to the audience; newly revealed assertions must cite the narration source.
- Reviewed particle updates and reconciliations inside an unscoped director turn remain complete-population operations; world-scoped packets do not receive either authority.

### Model entrance and orchestration custody

- `model brief` resolves the selected cube, performs deterministic verification, checks active audience/actor roles, and emits a strict read-only `lacuna.model-brief.v1` object without changing the ledger head.
- Chat, workspace, and orchestrated profiles state their capability assumptions and non-assumptions instead of treating uploaded files, shell access, persistent storage, or subagents as interchangeable.
- `play start` safely resolves or bootstraps only an absent/empty campaign path, retains exact default or supplied text as `session-control`, and opens one collision-resistant owner-only run without invoking a model.
- `run.json` is a strict `lacuna.turn-run.v2` manifest binding run/cube/request/proposal identity, expected head, packet digest, topology, artifact metadata/digests, status, and deterministic next action.
- `NEXT.md` is regenerated from `run.json` and audited byte-for-byte. A missing, altered, or linked pointer refuses during ordinary audit; explicit `turn run recover` can replace only that deterministic pointer after every authoritative member passes.
- The turn response contract defaults to a valid narration-only proposal. It contains no fake claim, assertion, alias, or `replace.me` operation that a literal model could accidentally commit.
- Generated instructions name the actual accepted receipt shape: player-facing prose comes from the receipt's top-level `narration` field, never from an unaccepted proposal.
- Every plan, card, and run transition is generated only after strict packet and chain audit: exact input, head/cube/context bindings, grant/profile agreement, response-contract agreement, safe template, stage topology, artifact role/schema metadata, and required upstream objects must match.
- Deterministic task IDs and canonical-JSON SHA-256 bindings tie narrator, proposal-builder, and verifier work to one exact packet and ordered upstream artifacts; edited, cross-turn, relabelled, or valid-but-wrong-stage handoffs are refused.
- The narrator card is manufactured from audience context plus the coordinator-approved observable plan. It never contains the full packet, planner context, private notes, or candidate operations.
- Planner, narrator, proposal-builder, and verifier contracts require exact JSON objects. An unchanged narration placeholder is refused, and the verifier template remains a refusal until an independent review replaces the `unperformed-review` finding.
- Every next action names one owner, complete input path, expected schema, exact parent command, and visibility rule. Delegated stages print the provider-dispatch command, reducing flag, filename, role, and topology inference by less capable coordinators.
- Proposal preflight checks packet identity, grant names, and cardinality before verifier handoff without claiming kernel acceptance. Run begin/accept/commit remain parent/coordinator-only.
- `ready-to-commit` additionally requires a strict `lacuna.turn-preparation.v1` envelope generated by the same mutation engine used for commit and authenticated by an unconditional rollback replay.
- Prepared generated IDs, timestamp, event IDs, event hash chain, change receipt, head, and post-state contexts are compared exactly; mismatches refuse before durable commit.
- Direct commit holds the same-run lock, revalidates the entire chain, requires the live request head, and rolls back if the durable transaction differs from the preparation.
- Crash recovery verifies the live cube, reconstructs the exact request-head ledger prefix in isolated memory, replays the preparation there, and compares the durable payload, receipt, and event chain before materializing a recovered receipt.
- `.run.lock` must be an owner-only, single-linked regular file and is held nonblockingly over complete status/accept/commit transitions; symlink substitution, permissive mode, and cooperative contention refuse.
- `lacuna.agent-dispatch.v1` binds the current run/stage to a provider route, role alias, typed input kind, retained card metadata/digest, complete embedded `input_document`, exact return schema, save path, parent accept command, authority split, and nonclaims.
- Dispatch refuses parent-owned stages and unknown providers, and rechecks the task-card digest while building the envelope. Embedding the card prevents a missing-local-path handoff but does not prove worker compliance.
- `lacuna.checkpoint-run.v1` gives the backstage retcon walk one strict manifest binding the run and cube paths, source request identity, protected-state head, fixed per-role provider routes, exact artifact topology, ordered invocation custody, status, deterministic next action, and fixed nonclaims.
- `checkpoint run begin` resolves the supplied cube path against the exact open `Cube` object, verifies the source cube, and manufactures the request and first card before publishing a run directory. A mismatched path or ordinary source-policy validation failure therefore refuses before a run is created.
- Managed checkpoint provider routes are fixed at begin. `lacuna.checkpoint-run-agent-dispatch.v1` is recomputed from the current retained card and fixed route, embeds the complete least-context card, and names the exact parent accept/failure commands without granting worker authority.
- Every retained worker output requires exactly one ordered accepted `lacuna.checkpoint-invocation-receipt.v1`. Failed attempts retain card/dispatch identity and host-declared metadata but do not advance the stage; later attempts remain ordered under the same role card. The 1,000-receipt ceiling is enforced before publication so a limit refusal cannot corrupt the manifest.
- Managed checkpoint audit reconstructs the full request → generator card/output → judge card/output → compressor card/output → parent proposal → verifier card/output → kernel review → receipt chain. Wrong-stage, cross-run, relabelled, rehashed, missing-custody, or topology-inconsistent artifacts refuse.
- A verifier refusal is terminal for that managed run. A passing verifier still has no commit authority; the parent manufactures the kernel review and only `checkpoint run commit` may apply or exactly recover the transition.
- A committed checkpoint receipt is reauthenticated against its source-bound proposal, review, embedded turn receipt, narration, durable event chain, and current or reconstructed historical cube state. Repeated commit is idempotent and does not duplicate events.
- `checkpoint run narrator-capsule` is available only after full committed-run audit. It binds exact request, proposal, receipt, compression, state-card, audience-context, and post-commit-head digests and changes neither the cube nor the sidecar.
- The narrator-capsule builder accepts no candidate, judgment, or verifier artifact, preventing accidental direct copy-through of rejected futures, scores, provenance, or verifier findings.
- `checkpoint run next-turn` authenticates the committed capsule and opens only an audience-only `play-turn`, `solo`, no-anchor ordinary run at the exact checkpoint head; stale heads, director packets, session control, non-solo topology, or another cube/audience refuse.
- `lacuna.checkpoint-continuation-dispatch.v2` binds checkpoint/capsule custody, exact next player input, ordinary turn packet/proposal identity, optional authenticated public-history digest and explicit completeness label, provider alias, save path, and parent accept command in one object while granting no accept or commit authority.
- `history build` audits an explicitly supplied ordered list and labels completeness `not-claimed`; it never promotes a selective list into a complete transcript claim.
- `history complete` takes a committed checkpoint boundary, derives the expected pre-checkpoint audience-turn census from immutable ledger custody, scans supplied managed-run roots for exact transcript bodies, and refuses missing, duplicate, wrong-version, wrong-path, wrong-audience, stateless-only, or ledger-disagreeing turns.
- `authenticate_public_history` verifies the cube, reloads each immutable turn request, authenticates exact player-input and narration digests, checks proposal changeset/event boundaries, and for complete mode recomputes the checkpoint-bound census and its digest.
- `lacuna.public-history-view.v2` removes run/request/proposal IDs, packet/receipt hashes, and event positions before the fresh narrator sees the prose while retaining only the explicit coverage mode/completeness label; embedded player/narrator strings remain quoted untrusted story/session data.
- A public-history artifact supplied to `next-turn` is authenticated before the ordinary turn is opened; forged content, missing ledger head, wrong chronology, wrong cube/audience/checkpoint boundary, or history reaching the checkpoint request refuses without leaving a new continuation run.
- Scenario-cell validation makes continuation mode explicit: the three controls must use one persistent declared context, while role-separated cells require fresh checkpoint-role contexts and a fresh capsule-bound narrator after every completed checkpoint.
- Scenario-capsule validation refuses a checkpoint after the final script step, ensuring every checkpoint treatment has at least one retained post-checkpoint ordinary turn.
- Scenario begin deterministically preregisters one operator-only and one filesystem-only random-looking canary per opaque cell, binds their source allowlists, and creates the filesystem source before any cell advances.
- Once every cell is frozen, the parent performs one exact descriptor-bound scan of retained experiment artifacts before manufacturing the blind rating packet. Same-cell and cross-cell unexpected matches are retained rather than discarded or retried.
- Scenario-bundle block seals bind each child contamination-scan digest, and the aggregate report carries clean/leak block counts plus exact unexpected-match totals.
- Managed checkpoint `NEXT.md` is derived from `run.json`, audited byte-for-byte, and recoverable only as a pointer after all authoritative artifacts pass. It never reconstructs a missing model return, review, or receipt.
- All authoritative run members and `NEXT.md` are read through verified descriptors. Symlinks, hard links, non-regular files, oversize members, descriptor/path identity mismatch, metadata drift, and detected pathname substitution refuse.
- Turn runs and checkpoint runs share the same hardened member-read, canonical-digest, path-resolution, shell-rendering, and owner-only cooperative-lock primitives, reducing the chance that one sidecar path silently weakens while the other is repaired.
- Provider-native agent definitions are checked for parseable structure, bounded recursion/turns, empty or read-only tool grants, exact task-card input/output behavior, explicit role naming, and no-commit instructions.

### Fair-play seal custody

- Seal creation stores only a domain-separated salted digest and public metadata; nonce and payload remain outside the cube until reveal.
- Seal reveal and void require an already committed origin change-set, so same-transaction commit/reveal is refused atomically.
- A reveal must recompute to the recorded digest and is bound to exact origin and terminal events during verification/rebuild.
- Restricted seal visibility is audience-checked, and perspective views omit privileged provenance source linkage.
- Seal lifecycle operations are host-only and excluded from audience and director model-turn grants.
- The anchorable receipt core and `receipt_sha256` remain stable across reveal or void while current lifecycle fields remain outside that core.

### Campaign boundary

- Campaign slugs cannot traverse outside the campaign directory, and campaign creation refuses nonempty overlays.

## Not protected

### Host and cryptographic limits

- A hostile machine can replace both database and verifier.
- The hash chain is not a digital signature, trusted timestamp, or remote transparency log.
- A hostile host can fork the cube or show different receipts unless a verifier independently retains or externally anchors a stable receipt digest.
- Campaign/library metadata, transcript bodies, opening files, shell history, backups, host logs, and model-provider logs are outside Lacuna’s protected story-ledger boundary.
- SQLite commit and sidecar publication remain separate durability domains. Exact historical recovery authenticates a matching post-commit change and writes the missing receipt without duplicate events, but cannot make both stores one atomic transaction or repair every begin-time orphan automatically.
- `.run.lock` is a cooperative same-host advisory lock. It is not a distributed lease, cannot defeat a hostile account with filesystem/database control, and does not serialize different runs against the same cube; stale-head enforcement remains the cross-run guard.
- Historical recovery uses a verified in-memory SQLite reconstruction at an exact changeset boundary. It does not make arbitrary historical heads writable or portable across a substituted cube.

### Particle, factor, and inference limits

- Authored weights and likelihoods are not calibrated probabilities and may be biased, dependent, strategically chosen, or simply wrong.
- The bank contains only candidate worlds already proposed. It cannot detect a missing explanatory mode.
- Equal valuation fingerprints cover only explicit assignments; worlds may still differ in unrepresented latent detail.
- Different likelihoods for valuation-equivalent worlds are diagnosed but not automatically rejected.
- ESS, entropy, maximum mass, information gain, total variation, and duplicate counts do not prove truth, adequacy, independence, diversity, causal agency, or narrative quality.
- An explicit zero baseline or zero included likelihood is mathematically absorbing under reconciliation; no extinction review, epsilon floor, or minority-mode guarantee is bundled.
- Single-use assertion IDs do not prevent correlated, derivative, or paraphrased evidence from being multiplied repeatedly. The current release has no factor-family or conditional-dependence model.
- Reconciliation mechanically treats active assertion factors as included and ended assertion factors as excluded. It does not judge whether supersession semantically withdraws the evidence, whether another assertion replaces it, or whether an active factor remains epistemically sound.
- A mistaken likelihood vector can be included or excluded but cannot yet be corrected through explicit factor predecessor/successor lineage.
- Factor epochs are deliberately conservative and coarse. A structural change retires earlier factors even when a human might consider some portable; no portability review is implemented.
- Log-space replay avoids ordinary product underflow but still uses IEEE-754 doubles. Exact cross-runtime decimal/rational reproducibility is not promised.
- Reweighting and reconciliation do not resample, rejuvenate, preserve minority modes, test nearby counterfactuals, or measure whether a player action causally changed the outcome.
- An unscoped director or hostile host can provide manipulative likelihoods or authorize a misleading reconciliation within the accepted structural rules.

### Narrative and semantic limits

- The runtime does not prove that prose entails exactly its declared assertions.
- A content digest does not prove authorship or correct interpretation.
- A custody explanation is not a logical derivation and may trace a false or poorly justified record.
- A burden score is not a probability, utility, causal effect, surprise estimate, or fairness metric.
- A consequence link is authored policy; a mistaken or malicious link can distort revision review until retired.
- A binding severity may be abused to freeze a premise.
- Nonbinding repair debt is detected and may be explicitly replaced, but is never automatically resolved or transferred.
- A repair review is not a certificate that the authored successor is semantically equivalent or narratively wise.
- One-to-many and many-to-one consequence repair are not implemented.

### Model-host and orchestration limits

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Project instructions, and subagent prompts are behavioral context, not an enforcement boundary. A model or hostile host can ignore them.
- Provider tool allowlists and sandbox fields are enforced, interpreted, or ignored by the provider runtime, not by Lacuna. Configuration syntax and discovery behavior may drift after this release.
- Uploaded files or Project/custom-GPT instructions do not by themselves grant ChatGPT access to a local cube, shell, persistent process, or commit tool. Governed persistence requires a human bridge or connected host.
- A parent can bypass generated cards, leak planner context to the narrator through the supposedly observable plan or alongside a valid capsule, widen task payloads, trust a bad subagent return, or present rejected prose. The kernel can validate only the artifacts and proposal actually submitted; it cannot observe the provider's full prompt.
- Packet and handoff SHA-256 checks establish exact-byte/canonical-JSON continuity inside the supplied artifacts; they do not authenticate the host, certify semantic correctness, or prove that a provider showed a worker only that card.
- The least-context split, fresh-narrator capsule, continuation dispatch, and contamination scan reduce accidental leakage surfaces and add falsification pressure; they do not prove noninterference between model calls, provider logs, Project memory, Custom Instructions, inherited conversation, linked API state, unreadable/unscanned storage, or external tools.
- A clean canary scan proves only that the exact preregistered tokens were absent from the exact frozen files in the declared scan scope. A worker may leak other information, transform a token, retain semantic knowledge without reproducing bytes, or communicate through a channel outside the retained artifact set.
- A detected canary match is evidence of contamination under the declared source/scan contract, not proof of which provider mechanism caused it. The runner preserves the affected cell; it does not automatically exclude, replace, or rerun it.
- A valid public-history artifact proves exact custody only for the committed runs explicitly supplied. Lacuna cannot prove that the operator included every earlier player-visible turn, that the text semantically entails the typed state, or that a provider saw no other transcript source.
- Lacuna retains local turn-run and checkpoint-run state machines and renders provider-specific dispatch, but still does not invoke a model, create or authenticate a provider subagent, enforce provider isolation, or make a verifier verdict authoritative. Invocation receipts and failure classes are parent/host declarations, not vendor-signed telemetry.
- Distinct runs receive collision-resistant directories, and cooperative same-host callers are serialized per run by `.run.lock`. There is still no distributed lock, per-cube scheduler, hostile-user boundary, or transaction spanning filesystem and SQLite.
- Run directories contain exact player text and potentially privileged model artifacts, including rejected checkpoint futures, scores, and the only full retained body of a selected state card. Mode `0700`, single-link member checks, and descriptor-stable reads are not encryption and do not protect against another process with the same operating-system identity, malicious parent-directory replacement between operations, backups/logs, or a remote provider receiving a card.
- Turn-run v2 and checkpoint-run v1 identity use absolute run and cube paths. Moving a run directory or rebinding it to another path makes audit fail; no relocation, export, or managed-run migration protocol is bundled.
- A crash after SQLite commit but before sidecar publication is recoverable only when the durable change matches the exact preparation. A begin-time interruption can still leave a committed request source plus an incomplete run directory; begin-orphan indexing and automatic cleanup are not bundled.
- Unreferenced leftover files after an interrupted sidecar write are ignored because `run.json` is authoritative, but explicit archive/redact/cleanup policy remains a host responsibility.
- Canonical JSON digests bind semantic object content rather than raw whitespace or key order. Exact-byte claims apply to retained text, not JSON serialization formatting.
- The auto topology is deterministic policy over packet-visible signals, not empirical proof that `solo`, `pair`, or `full` is optimal for a particular model or scene. Manual mode selection remains possible and visible.
- A passing commit receipt proves accepted typed mutation at one expected head. It does not prove that the displayed prose came from the receipt, that the prose is good, or that the host retained exact transcript bytes.
- The model brief verifies the cube at emission time. A later write can stale the packet or invalidate assumptions; every mutating turn still requires a fresh source-bound run/packet.
- No bundled evaluation proves that one-message routing, subagent use, mystery restraint, or player enjoyment generalizes across model versions.

### Checkpoint and retcon-planning limits

- Checkpoint cards, lower-level dispatches, managed-run dispatches, invocation receipts, and return digests prove continuity of supplied canonical JSON and host declarations, not that a named provider/model ran, that contexts were isolated, or that workers were independent.
- Provenance-blind judging removes declared generator identity and notes; candidate wording, structure, or shared provider memory may still reveal origin or coordinate behavior.
- Exact rollout beats are speculative noncanon artifacts. Their required cardinality prevents a claimed-but-missing rollout, but does not prove faithful simulation, diversity, plausibility, or good search coverage.
- Fixed dimensions, integer weights, arithmetic checks, disqualifiers, and deterministic tie-breaking make selection reproducible. They do not make aesthetic scores calibrated, objective, manipulation-resistant, or suitable as particle likelihoods.
- The compressor receives only the selected candidate and narrow grant, but can still omit artistically important information or encode misleading state within schema-valid text.
- A valid narrator capsule proves exact local object identity and deliberate exclusions, not that the state card is sufficient, that the host supplied no extra bytes, or that a provider forgot rejected material.
- Requiring a post-checkpoint script step proves that a continuation opportunity exists; it does not prove that the checkpoint causally improved or even influenced that continuation.
- The story ledger may retain only a state-card digest and accepted typed operations. Losing the checkpoint sidecar can therefore leave a valid cube without the prose-level hidden guidance needed for intended continuation.
- The proposal verifier is advisory and checks only proposal-visible custody consistency. It cannot independently recompute winner selection because raw candidates and scores are intentionally withheld; parent assembly revalidates the complete chain.
- Lower-level `checkpoint dispatch` is exactly recomputed from its embedded card and chosen provider route but remains stateless transport description. Managed `checkpoint run dispatch` additionally binds one retained run stage and fixed route; its separate invocation receipts still remain host declarations rather than provider attestations.
- Exact candidates, judgments, and future beats live outside the story event ledger. Their confidentiality, retention, deletion, and access control are host responsibilities.
- A complete public-history claim covers only durable Lacuna play-purpose turns for the named audience before the bound checkpoint. It cannot recover uncommitted chat, externally narrated text, deleted run sidecars, or semantic implications never represented as typed custody.
- Complete mode refuses when a durable turn has no matching managed-run transcript rather than silently filling or summarizing it; this improves honesty but can make old or partially retained campaigns ineligible for that claim.
- Fresh-narrator capsules include typed audience custody and the accepted checkpoint narration, but Lacuna does not retain full transcript bodies. Optional public history authenticates only the explicitly supplied committed runs; a host can omit earlier turns or apply unequal coverage across conditions. Run IDs and packet/receipt hashes remain sidecar custody requiring retained runs for independent re-audit.
- `record-failure` preserves an attempt without advancing the checkpoint, but Lacuna cannot independently prove that the provider failed, that the host classified the failure honestly, or that unrecorded cherry-picked calls did not occur.
- Managed runs are strict to the creating Lacuna project version and have no compatibility or migration layer. This prevents ambiguous reinterpretation but means an old run may need the old executable to audit or complete it.
- Source-path binding proves that begin used the exact open cube path under a cooperative host. It does not protect against a hostile same-user process replacing parent directories, the database, and verifier together.
- Automatic checkpoint timing, model sampling, retry policy, and comparative efficacy remain outside the kernel. A host can over-trigger checkpoints, cherry-pick model calls before submission, or use a biased rubric while still producing mechanically valid artifacts.
- Historical commit recovery authenticates an exact already-durable checkpoint event chain, including after later valid writes. It does not permit a stale uncommitted proposal to write against a later head.

### Fair-play limits

- An assignment commitment basis named `precommitment` remains a policy label; only a fair-play seal binds an exact external opening under the v1 scheme.
- A fair-play seal does not prove payload truth, authorship, completeness, uniqueness, clue sufficiency, narrative fairness, or that no alternative seals were prepared.
- The local event time is not proof that a player possessed the receipt then.
- A host can create and reveal in immediately adjacent transactions; Lacuna enforces phase order, not a genre-specific minimum delay.
- Opening a seal is semantically inert; it does not automatically create claims, assertions, assignments, anchors, or canon.

## Security posture

Lacuna is designed to make internal state transitions, provenance, omissions, and repairs inspectable under a cooperative or independently audited host. It narrows accidental authority and detects many classes of local corruption. It does not turn an untrusted machine into a trusted institution, and it does not turn authored narrative judgments or factor arithmetic into statistical facts.

## Rev0165 comparative-scenario, bundle, and contamination threats

- **Discarded whole-bundle bias:** the host can create and discard a bundle before anyone else sees it. Mitigation: one public commitment plus optional preregistered external-receipt threshold. Residual: Lacuna cannot expose an earlier unwitnessed discarded bundle.
- **False witness evidence:** an operator can invent a service, timestamp, signature claim, locator, or receipt digest. Mitigation: witness artifacts explicitly declare themselves operator-supplied and unverified; independent holders must verify their own evidence.
- **Late child or assignment creation:** lazy construction could adapt later replicates to earlier results. Mitigation: every child, assignment seed, assignment artifact, and exact clone tree is staged and published before execution.
- **Outcome-informed later execution:** unblinding one block could alter later prompts, retries, or handling. Mitigation: every block must be rated and sealed while blind; no child report is permitted until all blocks are sealed.
- **Direct child bypass:** a same-host operator can call child commands outside the bundle. Mitigation: parent audit detects witness-gate bypass, future-child advance, premature unblinding, stale cache, and frozen-artifact drift. Residual: detection does not undo information already revealed.
- **Cross-block memory contamination:** one real provider conversation can be relabeled with distinct context IDs. Mitigation: candidate preflight and full audit reject repeated declared context and invocation IDs. Residual: provider attestation and true memory isolation remain absent.
- **Checkpoint-only separation theater:** four fresh checkpoint roles can still feed an old narrator that remembers rejected futures. Mitigation: role-separated cells require a fresh narrator context and exact checkpoint/capsule declaration on the first subsequent turn; `checkpoint run next-turn` binds the new narrator's complete supplied input to one ordinary turn. Residual: the host can lie about context identity or provide extra hidden material.
- **Control-topology drift:** fresh contexts in controls or persistent contexts in treatment can erase the intended contrast. Mitigation: forward-only, prompt-only-retcon, and Lacuna-serial require one declared persistent context; role-separated requires story-segment resets. Residual: IDs describe host behavior but do not attest it.
- **Condition leakage:** prose, failures, or method vocabulary can reveal a condition to raters. Mitigation: transcript-only structured packets and artifact-minimal handoffs. Residual: semantic masking checks are not yet encoded.
- **Private-tree overexposure:** plan, schedule, assignments, drivers, blind packets, and reports coexist under one owner-private tree. Mitigation: mode `0700`, contained non-symlink member resolution, and role-minimal exports. Residual: no encryption or cryptographic compartmentalization from the same OS identity.
- **Block substitution or omission:** an owner could otherwise replace a weak replicate or report only successful blocks. Mitigation: fixed schedule, child/run/seed/assignment bindings, immutable block seals, all-scheduled inclusion, and no exclusion field.
- **Terminal failure laundering:** failed or refused cells could be treated as absent. Mitigation: both statuses are retained separately in observations and descriptive counts.
- **Incomparable rating aggregation:** differing scales or prompts could produce meaningless combined summaries. Mitigation: exact rating-contract equality is required across every block.
- **False metering and provider identity:** model, version, context, managed-checkpoint, continuation-capsule, invocation, latency, token, cost, and failure fields can be invented. Mitigation: classify them as host declarations and keep them separate from Lacuna-derived mechanics and human ratings.
- **Child-path substitution:** a child directory could be replaced by a symlink to another run. Mitigation: every child must be a contained non-symlink directory under the exact bundle authority path.
- **Partial unblinding crash:** some child reports may exist before the aggregate. Mitigation: one durable parent `unblinding` phase, fixed timestamp, idempotent child reports, and deterministic resume. Residual: this is resumable construction, not an atomic cryptographic reveal.
- **Spreadsheet command injection:** rater comments or strata can begin with spreadsheet formula syntax. Mitigation: derived CSV prefixes formula-leading text; canonical JSON remains exact. Residual: downstream tools must still treat untrusted text safely.
- **Overinterpreted descriptive sums:** ordinal scores and ranks can be treated as interval utility or significance. Mitigation: retain rater-level integers, emit only sums/counts, and make explicit nonclaims. Statistical modeling, power, multiplicity, rater dependence, and causal inference remain external.
- **Cooperative-lock race:** `.bundle.lock` and child `.run.lock` coordinate normal callers, not hostile same-user processes or distributed hosts. Direct concurrent mutation can contaminate the retained tree and cause refusal.
