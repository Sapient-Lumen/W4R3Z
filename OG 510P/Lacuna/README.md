# Lacuna

## Keep the mystery open without moving what already happened

Lacuna gives an evolving fictional world a memory of **what was observed, what someone said, what a character believes, what might explain it, and what the story has committed to**. It is useful when a campaign, mystery or interactive simulation must adapt to unexpected choices without quietly rewriting the evidence that made those choices meaningful.

The supplied Python/SQLite kernel does not generate the prose or decide the best plot. It provides the persistent state and acceptance rules around a human or model storyteller. Several hidden explanations can remain available; choosing one for planning does not automatically make it established history. The creative aim is not to freeze invention, but to make invention answerable to what the participants have already been shown.

The [player entrance][play] keeps that machinery backstage. A player's words can be dialogue, requests or attempts; saying an action succeeds is not itself evidence that the world accepted it. The [operator entrance][operate] explains the host needed for durable play. Reading these files does not start a session. For a source-first tour, begin with the Lantern Room example below, then follow revision and accepted-turn custody before the research apparatus.

## One trembling voice, three possible worlds

The [Lantern Room fixture][lantern] is a small worked model of the distinction:

- The bell rang, and the innkeeper's voice trembled. These are public, anchored observations in the fixture.
- The innkeeper says a storm will arrive before dawn. That is recorded testimony, not automatically the weather's future truth.
- The player suspects the broken cup was a deliberate signal. That is a private belief, not a public discovery.
- Three live worlds give different hidden explanations: ordinary accident, a hidden heir, or a watcher who recognized the player. The fixture assigns them planning weights of 0.55, 0.25 and 0.20.

The same observed tremor can support a different interpretation inside different worlds. The fixture links it to fear of recognition in the heir hypothesis and recognition of the player in the watcher hypothesis. Those are authored evidence relations, not causal facts inferred by SQLite. A perspective-scoped context omits the hidden assignments and privileged evidence links; an omniscient planning context includes them.

This matters to play because uncertainty is structured rather than merely forgotten. The open question “Why did the cup break?” has an identity of its own. A later explanation can answer it while preserving the bell and trembling voice, and the difference between a suspicion and a reveal. The example's numerical weights are authored planning quantities, not measured probabilities of narrative truth.

## The durable distinction is in the records

A **claim** holds proposition content. An **assertion** adds who takes a stance toward it, on what basis, from which perspective, with what visibility and narrative interval. A **world assignment** belongs to one partial hidden-world hypothesis. An **anchor** is an assertion whose contradiction is no longer acceptable. Commitment is separate from confidence: how strongly a planner favors a premise is not the same as what changing it would break.

The [store implementation][store] appends typed events and derives current projections from them. A change-set names its expected ledger head. Inside a SQLite transaction, the kernel checks that head, prepares and validates each operation, appends events and updates projections; an error rolls the transaction back. Each event hash includes its predecessor hash. A separate change receipt binds the operation sequence to its before/after heads. Rebuild and verification paths make the stored projections answerable to the event history rather than independent competing versions of it.

This is a local integrity and replay mechanism, not an external witness of truth. The story event chain also is not the entire retained project: campaign metadata, exact transcript bodies and unrevealed seal openings have distinct storage and custody. A host must preserve the artifacts its particular continuation or audit depends on.

The [constraint code][logic] is deliberately open-world. An exactly-one-culprit rule rejects two explicit culprits, or enough explicit falsehoods to make the rule impossible. It does not create the missing truth values. Naming Ada does not silently write Basil=false into the record; leaving an assignment absent does not mean false. The kernel checks the supplied formal representation, not every implication of natural-language prose.

## Revise a premise without losing its consequences

A storyteller may initially use a secret passage to explain a draft, then prefer a ventilation shaft. In Lacuna's [revision protocol][revision], changing that assignment is not an overwrite. The host first requests an impact review tied to the current ledger head, then submits its digest with an explicit successor assignment and reason. A separately committed intervening event makes the review stale. The implementation recomputes the review and refuses a changed or blocked proposal.

The review distinguishes **ambient exposure** from **explicit dependence**. An assertion about the same claim may deserve attention without having been caused by the hidden premise. Only an authored consequence link says that the premise explains, motivates, promises, constrains or otherwise supports the particular dependent. This prevents every nearby detail from being retroactively recruited as foreshadowing.

Commitment rises through tentative, soft, firm and hard. Hard commitment or a binding consequence can block in-place revision. The [burden policy][commitment] separately counts recorded surfaces worth reviewing, including assertion history, evidence, descendants and consequences. Its ordinal score is an inspectable policy, not a measure of surprise, artistic quality or fairness.

Nonbinding consequences can outlive the premise they depended on. They become visible repair debt rather than disappearing. The [repair protocol][repair] records predecessor, successor and the reason connecting them in one atomic replacement. It does not automatically transfer an old promise to a new explanation: doing so would assert a dependency the author has not justified. Nor can a repaired record undo narration a player already read. The distinction makes retconning inspectable without declaring every retcon either forbidden or harmless.

## Acceptance is more than a plausible next paragraph

The [turn implementation][turns] separates a proposed continuation from an accepted one. Preparation rehearses the exact mutation path, captures its event chain and projected contexts, then rolls back. Commitment validates that preparation, checks the request head again, applies the frozen envelope and compares the resulting receipt, event chain and contexts. Readiness is therefore not a reservation of the head, and proposed narration is not already an event in the campaign.

The managed run adds exact input/output custody around that boundary. Its next-action document names the next role and return format. Different host configurations can use one storyteller or separated planning, narration and checking roles; Lacuna itself does not call those models. The accepted turn receipt supplies the narration to present. A narration-only proposal can be valid without adding new fictional facts.

This gives a concrete division of labor: imagination proposes; the kernel checks typed operations and permitted projections; the host commits and presents. It does not solve semantic completeness. A beautifully phrased paragraph can still imply something the typed operations failed to capture, and a valid record can still support a dull story. Those remain distinct problems rather than consequences supposedly proved by a passing receipt. Durable operation may retain exact player text, narration and private planning artifacts in local run directories; that storage is part of the host arrangement, not something this reading page initiates.

## Two additional ways to preserve an unresolved world

**Reweight explanations without erasing their evidence history.** A particle-bank update multiplies authored prior weights by authored likelihoods over the complete eligible population and normalizes the result. One evidence assertion can supply a factor only once. If that assertion is later withdrawn, its earlier update remains historical while reconciliation replays the active factors from the stored baseline. The [arithmetic][particles] uses log-space normalization for small factors. Membership or valuation changes require a new structural epoch rather than silently reusing old assessments. These calculations maintain planning state; they do not calibrate its input judgments.

**Precommit a particular secret without making every secret fixed.** A [fair-play seal][seals] binds an external payload and random nonce to a salted digest. Keeping a culprit opening outside the cube allows a later reveal to be compared with the earlier commitment. Creation and reveal occur in separate committed changes. The seal establishes continuity of the opening's bytes, not that the clues were sufficient, the answer was authored fairly, or no alternative fork existed. An externally retained receipt matters when the comparison must survive an operator's ability to replace local history.

## A research instrument, not a result in favor of itself

The [research entrance][research] makes a specific proposal testable: compare governed retrospective planning with simpler ways of continuing a story. The [scenario protocol][scenario] defines four conditions from matching seed clones: forward-only continuation, prompt-only retconning, Lacuna's roles in one serial context, and separated role contexts with a fresh narrator after a checkpoint.

The last condition uses an information bottleneck: a new narration context receives the accepted compressed state and permitted public history rather than rejected candidate explanations, scores and rollouts. The distinction between a complete retained pre-checkpoint history and a selected partial list matters; both can be authentic, but they support different coverage claims. A host's claim of a fresh context is not proof of provider memory erasure.

The experimental machinery freezes primary ratings before method-recognition judgments and unblinding. Replicated bundles retain all scheduled blocks before revealing their assignments; exact canary scans add a way to discover some contamination. This is useful even when the method fails: operational failures and subjective narrative ratings need not be collapsed into one persuasive transcript. A clean exact-token scan does not prove semantic isolation, and a completed block does not establish a general causal advantage. The artifact supplies the comparative machinery, not a demonstrated improvement in fiction.

## A descendant that deliberately became smaller in purpose

The [development history][history] records a substantial rev0145 cutover: Lacuna replaced the Datacube's self-compiling continuation/release machinery with a Python/SQLite semantic kernel. It removed native toolchain custody, container orchestration and the historical revision corpus from the shipped runtime. This is not evidence that the discarded foundation was pointless. It shows a project choosing a narrower useful form once its own problem became clearer.

Later revisions made that form more explicit: rev0146 separated perspective from privileged planning context; rev0149 made truth-changing assignment revision a reviewed operation; subsequent work added consequence repair, managed turns, checkpoints and comparative experiments. Rev0169 addresses a practical teardown stall with passive SQLite WAL cleanup, rejects unedited experiment templates and adds bounded acceptance runs and an MIT license. Its [architecture note][architecture] distinguishes those release repairs from changes to story semantics.

Read beside [DelayBasin](../DelayBasin/README.md) for what a continuation needs to carry, and [Metaphysics](../Metaphysics/README.md) for distinctions between possibility, fact and explanation. Lacuna gives those questions a particular operational home in evolving fiction; it is not a general proof system for either neighboring work.

## Snapshots and preservation

### Selected snapshots

#### [rev0169](versions/rev0169/README.md)

The README identifies this as a test-harness and release-license polish pass: nonblocking SQLite cleanup, fail-closed unedited scenario templates, an MIT license and a bounded acceptance runner. Read PLAY_NOW for the player-facing path, FOR_GWERN for the proposed research evaluation, and OPERATE_LACUNA for operation. These are archived paths, not requests to launch them.

### How to read this preservation

These are selected historical snapshots. Original filenames, ZIP bytes and extracted contents are unchanged; new guides, inventories and integrity notes are separate. “Latest” in a supplied filename is a historical label. Nested archives remain nested. Research source claims and reported validation runs were not independently reproduced for this archival delivery. Read the retained limitations, open gates and rights notices before reuse. See the [current owner declaration](../../LEGAL-NOTICE.txt); third-party terms remain distinct.

[Original identities and hashes](PROVENANCE.json) · [Back to OG 510P](../README.md)

[play]: versions/rev0169/files/Lacuna-rev0169/PLAY_NOW.md
[operate]: versions/rev0169/files/Lacuna-rev0169/OPERATE_LACUNA.md
[lantern]: versions/rev0169/files/Lacuna-rev0169/examples/lantern/change-set.template.json
[store]: versions/rev0169/files/Lacuna-rev0169/src/lacuna/store.py
[logic]: versions/rev0169/files/Lacuna-rev0169/src/lacuna/logic.py
[revision]: versions/rev0169/files/Lacuna-rev0169/docs/protocols/REVISION_IMPACT.md
[commitment]: versions/rev0169/files/Lacuna-rev0169/src/lacuna/commitment.py
[repair]: versions/rev0169/files/Lacuna-rev0169/docs/protocols/CONSEQUENCE_REPAIR.md
[turns]: versions/rev0169/files/Lacuna-rev0169/src/lacuna/turns.py
[particles]: versions/rev0169/files/Lacuna-rev0169/src/lacuna/particles.py
[seals]: versions/rev0169/files/Lacuna-rev0169/docs/protocols/FAIR_PLAY_SEALS.md
[research]: versions/rev0169/files/Lacuna-rev0169/FOR_GWERN.md
[scenario]: versions/rev0169/files/Lacuna-rev0169/docs/operators/SCENARIO_CAPSULES.md
[history]: versions/rev0169/files/Lacuna-rev0169/CHANGELOG.md
[architecture]: versions/rev0169/files/Lacuna-rev0169/docs/architecture/ARCHITECTURE_rev0169.md
