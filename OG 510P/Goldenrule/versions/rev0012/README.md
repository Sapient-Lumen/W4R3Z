# Goldenrule — rev0012

## Make a reciprocity claim inspectable

Concord asks how cooperative strategies behave when the world, opponent and conditions change. This early snapshot gives that inquiry an explicit experimental vocabulary: specify a world and two policies, record what was actually run, and compare results without silently changing the meaning of success.

The useful object is not simply a winning strategy. It is a claim another reader can inspect: which payoff system, which noise, which horizon, which opponent, which seed and which asserted threshold? The [project charter](files/docs/PROJECT_CHARTER.md) makes that scope central and explicitly rejects grand moral-authority claims. A reproducible result can support an experimental conclusion without proving that the behavior is morally right.

**Start with the [small example experiment](files/examples/experiments/ipd_smoke.json), its [world](files/examples/worlds/ipd_core.json), and the [definitions guide](files/docs/DEFINITIONS.md).** For the broader moral inquiry, covenant, parables and later research developments, use the [collection introduction](../../README.md).

## A small world you can understand before running anything

The retained smoke experiment lists Always-Cooperate, Always-Defect, Tit-for-Tat, Win-Stay-Lose-Shift and a generous memory-one policy, with two replications and eight trace rounds requested. Its world specifies fifty rounds, no noise and seed 12345. In the declared Prisoner's Dilemma payoffs, mutual cooperation gives each player 3, mutual defection gives each 1, and unilateral defection gives the defector 5 while the cooperator receives 0.

These numbers expose the dilemma rather than solve it: unilateral advantage and the jointly cooperative outcome pull in different directions. The [Rust specification](files/crates/gr_engine/src/spec.rs) makes the mapping explicit and separates world definitions from strategy definitions. Changing the payoffs or adding noise changes the question being asked, not merely the difficulty of an otherwise identical test.

The same specification includes distinct models for implementation noise and observation noise: an action going wrong and a player receiving a misleading observation are different disturbances. It also distinguishes fixed and geometrically terminated encounters. Those declarations help prevent a result about one setting from drifting into a claim about cooperation everywhere. The example above remains a small configured experiment, not evidence that all these conditions were tested.

## From an experiment to a checkable claim

A *probe* is a declared test with a world, matchups, replication settings and assertions. The [actual probe implementation](files/crates/gr_engine/src/probe.rs) shows how it works:

1. The probe's typed representation is serialized and hashed. This identifies the definition used, rather than relying on its display name.
2. Each matchup becomes repeated tasks with seeds derived from the world's seed, a matchup offset and the replication index.
3. Each run contributes per-player payoff and cooperation statistics, mutual cooperation and mutual defection rates, with requested traces retained.
4. The probe takes an arithmetic mean of those statistics across replications and evaluates its declared assertions. Each replication has equal weight, even when encounter lengths differ; this is not a pooled-round average or a confidence bound. An assertion can require a player's mean payoff to reach a minimum, or the mean mutual-defection rate not to exceed a maximum.
5. The result retains both the observed value and the assertion that produced pass or fail, together with replication detail and definition identifiers.

The consequence is important: passing means meeting those assertions in that configured test. It does not mean that a policy is fair, robust in every environment or worthy of moral imitation. A payoff threshold can be satisfied while some other important feature remains unmeasured. The later collection guide develops precisely this problem through exploitation, repair and multi-part scorecards.

This also distinguishes a reusable probe from a bare score. If a policy changes, a successor can ask whether its behavior changed under the same definition or whether the definition itself moved. Both can be legitimate research steps; they should not be reported as the same event.

## Keeping meaning stable while research changes

The [definitions guide](files/docs/DEFINITIONS.md) connects probes to suites, definition snapshots, result diffs and smaller counterexamples. It calls this an early-stage target workflow, describes some registry and suite structures as minimal shells, and treats a frozen probe suite and a holdout that search never consults as longer-run intentions. Those intentions are distinct from the concrete probe path inspected above.

It also describes *metamorphic checks*: relations expected between runs even when no single correct score is known in advance. In eligible deterministic, noiseless settings, swapping player roles should swap the per-player statistics. Extending a fixed-seed horizon should preserve the earlier trace prefix. Such checks examine consistency of the experimental machinery; they do not turn a cooperative outcome into a moral proof.

Shrinking serves a different purpose. The documented tools seek a smaller failing horizon, a failing matchup within a larger probe, or fewer replications that preserve a failure. A smaller counterexample can make the relevant condition easier to see. It is not a claim to have found the smallest possible explanation across every dimension.

The charter assigns simulation semantics and artifact-level primitives to Rust, with Python responsible for orchestration, search and reporting. That is the project's architectural commitment, not a substitute for checking any particular command's implementation. This entrance follows the inspected Rust probe path and the supplied example definitions rather than treating the original README's long command index as a list of independently established results.

## How this edition fits the later work

Rev0012 is useful for seeing the experiment's basic objects before the later evidence and recovery vocabulary grows much larger. Read its bounded model and claims discipline on their own terms, then compare the [later snapshot](../rev0567/README.md) through the collection guide's analysis of scorecards, transient burdens, exploitation and rematching.

The [changelog](files/CHANGELOG.md) describes a scientific-repository transformation, expanded reproducibility and release tooling, and a Golden-Rule research pass. Neither a growing archive nor a successful packaging check establishes a stronger simulator or a settled ethic. This is a foundation for asking more precise questions and retaining results that another researcher can continue, reject or reinterpret.

The original [README](files/README.md) preserves absolute paths from its former workspace. The relative links here provide usable entrances to the preserved files without rewriting that historical document. Its operational instructions remain source material, not instructions to restart the experiments.

<details>
<summary>Original files and preservation</summary>

- [Original README](files/README.md)
- [Revision notes](files/CHANGELOG.md)
- [Project charter](files/docs/PROJECT_CHARTER.md)

ZIP members passed CRC checks and the extracted copies were byte-hashed. The review note states which supplied inventories were checked. The new archival inventory records every received file even where no complete current inventory was established. Byte identity does not establish correctness, rights clearance, source currentness, deployment readiness or the truth of research conclusions.

- [Original ZIP](../../originals/Goldenrule-rev0012-2026.03.06.09.39-ruleschema-contractgate-embedding-martin.zip)
- ZIP SHA-256: `0786250a72f579fae4f8219356b68c19744260e6f7af4caedd1fccde621a4952`
- Extracted files: 529
- [Exact byte inventory](INVENTORY.json)
- [Integrity-review scope](INTEGRITY.json)

Lumen added this guide beside the unchanged files. Original member paths, wrapper layout and executable-bit distinctions are retained. No supplied program, experiment, fieldwork, outreach or writing protocol was executed. Original rights and notices remain applicable; no new blanket license is granted.

</details>

