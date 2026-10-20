# Goldenrule / Concord

## What makes a cooperative world possible?

Concord studies a problem that a strategy leaderboard can easily miss: how to sustain reciprocity without rewarding exploitation, becoming exploitative oneself, or destroying cooperation through endless retaliation. Its materials join a normative covenant, a deterministic repeated-game laboratory, analytical scorecards and a long-running effort to make research resumable and its claims inspectable.

The covenant begins with two brothers secretly carrying grain to one another. Their care converges without either calculating a profitable bargain. It then asks what happens when goodwill meets someone who deliberately takes advantage of it. The formal inquiry concerns the conditions under which cooperative lives can persist. It does not claim to manufacture the disposition that makes those lives worth seeking.

That makes the collection both a philosophical work and an experimental design project. The prose is not decoration for the software, and the software is not a proof that the prose is morally right.

[Read the covenant](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/COVENANT.md) · [The parables](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/PARABLES.md) · [Project charter](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/PROJECT_CHARTER.md)

## More than one meaning of reciprocity

The [original concept map](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/Original-Starting-Place/12_GoldenRule_DeepDive.md) treats the Golden Rule as a family of potentially conflicting norms: initiating care, restraining harm, reversing roles, respecting different preferences, justifying burdens and repairing relationships. Imagining what *I* would want can misrepresent what another person values. Forgiveness can enable restoration or become an exploitable reset. Self-play can test one consequence of a universal policy without settling every question of justifiability.

These distinctions motivate different worlds and scorecards rather than one all-purpose cooperation number. They are conceptual proposals, not a list of institutions already implemented in the engine. A genuine tension remains: the early map rejects systematic exploitability, while the [later virtue discussion](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/LIBRARY/topics/virtue_vs_strategy.md) permits absorbing some exploitation rather than retaliating beyond repair. The collection does not resolve that tension by supplying a single numerical price for mercy. Its boundary tests can discriminate behavior under pressure; they do not by themselves authenticate the inward source of that behavior.

## A better score can still reward the exploiter

Two retained search artifacts give the problem a concrete shape. In a 1,000-round result against `extortion_chi3_v1`, the leading random-search candidate receives an average payoff of **1.841**, while its opponent receives **3.086**. The leading row in a hill-climb artifact reaches **2.211**, with mutual cooperation in **70%** of rounds, while the opponent rises to **3.411**.

These are particular retained results, not universal performance estimates. Their explanatory value is immediate: improving the focal player's payoff and increasing cooperation do not establish that the relationship has become fair. A search can succeed at its stated objective while leaving the project's actual concern unresolved.

The archive calls a policy that exploits cooperative trust a *vampire*. Its contrast is not merely between cooperating and defecting. A policy can benefit from another's willingness to cooperate while returning less than the cooperative baseline. The charged term belongs to that defined inquiry; it is not a diagnosis of an actual person.

The anti-vampire scorecard therefore asks several questions together: what does the focal player receive, who gets the surplus, can cooperation recover after a shock, can repair offers be abused, and does the behavior remain acceptable in a noisy ecology? A high score in one column cannot silently answer the others.

[Random-search result](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/search_vs_extortion_long.json) · [Hill-climb result](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/hill_climb_vs_extortion_sigma02.json) · [Scorecard specification](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/LIBRARY/topics/anti_vampire_scorecard_spec.md)

## The world and the strategy are explicit objects

The Rust core models repeated social dilemmas through declared game, noise, termination and strategy specifications. The visible game model is an iterated Prisoner's Dilemma with configurable payoffs and an exit action. The model distinguishes implementation noise, where an intended action changes, from observation noise, where the other player's action is perceived differently. It supports fixed and geometrically terminated encounters, with separate seeded random streams for decisions, noise and termination.

A memory-one strategy is a compact conditional policy: an opening cooperation probability and probabilities after CC, CD, DC and DD. In the Rust simulator, those conditions use the player's previous intended action and its observation of the opponent. That detail matters when noise is present. The vocabulary is not interchangeable with an unspecified real person's memory, motive or moral character.

The surrounding research machinery makes definitions into versioned artifacts. A probe expands deterministically into tasks; suites collect probes; snapshots bind their definition hashes; result diffs expose behavioral drift. A shrinking tool seeks a smaller failing horizon, matchup or replication set. Metamorphic checks ask questions such as whether swapping players swaps their statistics or extending a fixed-seed horizon preserves its earlier trace.

These mechanisms let a later reader ask more than “Which policy won?” They help identify what changed, which definition was used, and what smallest case demonstrates a failure.

[World and strategy types](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/crates/gr_engine/src/spec.rs) · [Simulation semantics](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/crates/gr_engine/src/sim.rs) · [Definitions, probes and shrinking](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/DEFINITIONS.md)

## The analytical work asks where a trajectory goes, not just its average

For two memory-one policies, the analytical lane constructs a four-state transition model in the declared CC/CD/DC/DD order. From that model it can examine occupancy, payoffs and the structure of recurrent behavior. The later Python `grlab/certify.py` substantially expands the earlier stationary-payoff analysis with explicit contracts, uncertainty summaries and path-dependent diagnostics.

The distinction between a stationary distribution and the outcome reached from a particular opening is important. A reducible chain can have more than one closed class. The opening distribution and transitions determine which basin is reached and with what probability. A generic stationary vector or a finite averaging fallback can conceal that dependence.

The later result surface exposes the transition matrix, communicating and closed classes, initial reachability, entry probabilities and timing, and a basin-weighted asymptotic distribution. It also records pre-closure payoff burdens and state/transition visits. Two policies can reach the same eventual mixture while imposing different costs on the way there. That difference is especially relevant to a project concerned with exploitation and repair.

Not every field has the same evidentiary status. Noisy ecology and repair fields use declared sampling and interval conventions. The command retains `screening_proxy` status because a fuller recovery and repair-channel judgment still needs an explicit world contract. The name `certify` is not permission to promote every emitted field into a final certificate.

The charter assigns simulation semantics to Rust and orchestration to Python. Read that architectural intention beside the implementation: the later memory-one analysis and noisy proxy rollouts are in Python, and their action-history convention is not simply the Rust simulator's convention copied verbatim. Comparisons must retain the particular analytical or simulation contract they use.

[Analytical implementation](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/grlab/certify.py) · [Declared scorecard contracts](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/LIBRARY/topics/anti_vampire_scorecard_spec.md)

## Negative results can tell the project to change the world

A retained research note reports that none of 200,000 sampled memory-one candidates jointly achieved nonnegative fairness against extortion, self-play payoff of at least 2.5, and no more than 0.1 gain from exploiting Always-Cooperate. The note explicitly calls this a warning rather than an impossibility proof. Its random sample does not exhaust the space, especially exact boundary policies.

The interesting response is not to award the least unsatisfactory candidate a moral crown. It is to ask whether the model omits resources that matter: longer memory, partner choice, repair channels or institutional structure.

One neighboring investigation makes this concrete. A unilateral exit action in a fixed pair is not yet partner choice. If leaving supplies no new partner, matching pool, reputation spillover or outside-option structure, it does not model the conditions under which choosing partners changes incentives. A policy can even exploit the exit mechanism as a first-defection trap.

A separate [Python rematch proxy](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/scripts/report/build_partner_choice_proxy_snapshot.py) does implement a more concrete experiment: one focal policy repeatedly draws a new opponent from a fixed pool of extortion and generous Tit-for-Tat, resets pair memory, and plays for at most 50 rounds. It varies the extortion share between 20%, 50% and 80% and inserts zero, one or two dead-time rounds between encounters. That gives leaving a subsequent encounter and a cost, without pretending to model an evolving population or a mutual matching market.

A richer comparison must also distinguish conduct from opportunity. Overall payoff depends partly on how much time is spent matched rather than searching; payoff conditional on being matched answers another question. A leaderboard that erases that decomposition can confuse a cost of the matching institution with the quality of behavior inside an encounter.

The later rematch materials make this distinction a research contract, but their claim frontier still identifies the endogenous world/strategy engine gap, `SG-003`, as unresolved. A receipt declaring a synthetic or copied bridge ready does not establish an implemented native rematching world. The material is valuable as a precise design and handoff, without being redescribed as a completed native rematching experiment.

[Scoped memory-one finding](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/LIBRARY/topics/memory_one_tradeoff_against_extortion.md) · [Why exit is not partner choice](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/LIBRARY/topics/unilateral_exit_is_not_partner_choice.md) · [Rematch claim frontier](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/REMATCH_WORLD_BENCHMARK_CLAIM_FRONTIER.md)

A small reading correction matters here: the courteous-firm witness's `p_dd` is a probability of **cooperation** after DD. Its value near 0.0047 therefore makes the focal player very unlikely to resume cooperation after DD, contrary to the topic note's phrase “do not linger.” The supplied parameter file and strategy semantics should govern that interpretation; the original note remains preserved.

[Courteous-firm parameters](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/examples/strategies/mem1_courteous_firm.json)

## Continuity is part of the research object

The two supplied snapshots expose a useful developmental contrast. The charter and the examined Rust specification/simulation files retain the same identities across rev0012 and rev0567. The larger later package is therefore not, by size alone, evidence of a new simulator. Much of the visible growth concerns analysis, interpretability, declared claim boundaries, evidence handling and recovery of ongoing work.

The later archive includes failure/resume cards, queue and checkpoint surfaces, frozen interpretation handoffs and explicit unresolved questions. Their purpose is to let a successor distinguish completed evidence from a planned run, a valid retained result from a placeholder, and an actionable implementation gap from another round of reporting about it. An archive can preserve a failed avenue or a narrowly scoped unapplied repair as useful work rather than needing every handoff to announce a new success.

This is a research foundation another operator can inspect and continue differently. It preserves the questions and constraints that make continuation meaningful, not merely a command to repeat the previous action. The original mission and workflow instructions remain historical project material; this reading entrance does not restart them.

[Early charter](versions/rev0012/files/docs/PROJECT_CHARTER.md) · [Later recovery card](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md) · [Research priorities and scope](versions/rev0567/files/Goldenrule-rev0567-2026.03.26.00.39-phasebucketjson-resumebeacon-logknot/docs/SCIENCE_PLAN.md)

## Choose an entrance

- **For the moral question:** read the covenant and parables, then the payoff trap and multi-part scorecard. Keep the claim about care distinct from the operational definition of a strategy.
- **For the experimental model:** start with `spec.rs`, `sim.rs` and the definitions guide; inspect a concrete result with its world and policy identifiers.
- **For the analytical development:** compare memory-one certification across the two snapshots, especially opening conditions, reducible chains, transient burdens and proxy uncertainty.
- **For continuation:** use the rematch claim frontier and recovery card to locate what exists, what remains conditional and what actually needs implementation.

Read beside [Parables](../Parables/README.md), [The Good](../The-Good/README.md) and [Righteousness](../Righteousness/README.md). These are neighboring arguments, not interchangeable components of one theory. Concord's distinctive contribution is to make the conditions of reciprocity investigable while refusing to equate a successful optimization with the moral disposition it hopes to serve.

## Versions and preservation

### Selected snapshots

#### [rev0012](versions/rev0012/README.md)

An early Concord snapshot organized around deterministic experiments, schema/contract checks and reproducible artifacts. Its README retains absolute /workspace links from its original environment; the links in this added guide point to the corresponding preserved files where available.

#### [rev0567](versions/rev0567/README.md)

A later snapshot with a much larger evidence, workflow and recovery vocabulary, including userspace failure/resume records and a machine-readable research/review surface. Read the normative covenant and project charter alongside the technical state, rather than equating a receipt or benchmark model with a moral conclusion.

### How to read this preservation

These are selected historical snapshots. Original filenames, ZIP bytes and extracted contents are unchanged; new guides, inventories and integrity notes are separate. “Latest” in a supplied filename is a historical label. Nested archives remain nested. Research source claims and reported validation runs were not independently reproduced for this archival delivery. Read the retained limitations, open gates and rights notices before reuse. No new blanket license is granted.

[Original identities and hashes](PROVENANCE.json) · [Back to OG 510P](../README.md)
