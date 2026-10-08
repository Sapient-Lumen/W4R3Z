# Research Sources (2026-03-18)

This file records primary references used to reset Concord as a scientific tool.

Selection rules:
- Favor primary papers and official project/tool documentation.
- Prefer sources with stable URLs and explicit scope statements.
- Map each source to concrete repo implications.

Link health was checked on 2026-03-06 (UTC) for newly added references; older source IDs remain from the 2026-03-03 pass unless refreshed below.

## Repeated-Game Science

1. `RS-IPD-001`  
   [Press & Dyson (2012), *Iterated Prisoner’s Dilemma contains strategies that dominate any evolutionary opponent*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3387070/)  
   Relevance: establishes zero-determinant strategy constraints for memory-one play and motivates analytic certification of strategy behavior.

2. `RS-IPD-002`  
   [Stewart & Plotkin (2013), *From extortion to generosity, evolution in the Iterated Prisoner’s Dilemma*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3780848/)  
   Relevance: shows generous strategies can outperform extortion in evolving populations; motivates holdout tests beyond single-opponent exploitability.

3. `RS-IPD-003`  
   [Hilbe et al. (2013), *Evolution of extortion in Iterated Prisoner’s Dilemma games* (arXiv)](https://arxiv.org/abs/1308.2577)  
   Relevance: extortion is not generally evolutionarily stable; motivates population-level and robustness-first evaluation.

4. `RS-IPD-004`  
   [Stewart & Plotkin (2013), *Extortion and cooperation in the Prisoner’s Dilemma*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3799065/)  
   Relevance: formalizes why longer memory does not automatically defeat memory-one extortion constraints; informs model-scope boundaries.

5. `RS-IPD-005`  
   [Axelrod-Python documentation](https://axelrod.readthedocs.io/en/stable/)  
   Relevance: broad strategy corpus and tournament framing for benchmark interoperability.

6. `RS-IPD-006`  
   [OpenSpiel paper (arXiv)](https://arxiv.org/abs/1908.09453)  
   Relevance: standardized environment framing for algorithm/game comparisons, useful as external benchmark bridge.

7. `RS-IPD-007`  
   [OpenSpiel repository](https://github.com/google-deepmind/open_spiel)  
   Relevance: practical API and game implementations for compatibility experiments.

8. `RS-IPD-008`  
   [Axelrod & Hamilton (1981), *The evolution of cooperation* (PubMed record)](https://pubmed.ncbi.nlm.nih.gov/7466396/)  
   Relevance: canonical tournament-based reciprocity framing for repeated-game experimentation.

9. `RS-IPD-009`  
   [Nowak (2006), *Five rules for the evolution of cooperation* (PubMed/PMC)](https://pubmed.ncbi.nlm.nih.gov/17158317/)  
   Relevance: mechanism taxonomy to diversify beyond one-environment strategy evaluation.

## Golden-Rule Adjacent Mechanisms

1. `RS-GR-001`  
   [Glynatsi et al. (2024), *Conditional cooperation with longer memory*](https://www.pnas.org/doi/10.1073/pnas.2420125121)  
   Relevance: longer-memory reactive strategies widen the design space for forgiving-but-non-naive reciprocity.

2. `RS-GR-002`  
   [Chen et al. (2023), *Outlearning extortioners: unbending strategies can foster reciprocal fairness and cooperation*](https://academic.oup.com/pnasnexus/article/2/6/pgad176/7179485)  
   Relevance: anti-extortion evaluation should track fair resistance and convergence pressure, not just one-sided payoff maximization.

3. `RS-GR-003`  
   [Graser et al. (2025), *Repeated games with partner choice*](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1012810)  
   Relevance: allowing agents to leave and rematch can raise cooperation and should become a first-class world mechanic.

4. `RS-GR-004`  
   [Salonia (2024), *A Foundation for Universalisation in Games*](https://www.tse-fr.eu/publications/foundation-universalisation-games)  
   Relevance: provides a tractable formal bridge from Golden-Rule-like intuitions to explicit decision models that can be benchmarked.

5. `RS-GR-005`  
   [Leung & Turrini (2024), *Learning Partner Selection Rules that Sustain Cooperation in Social Dilemmas with the Option of Opting Out*](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p1110.pdf)  
   Relevance: even weak opting-out mechanics can support emergent cooperation, which makes leave/stay policies worth treating as learnable strategy components.

6. `RS-GR-006`  
   [LaPorte et al. (2026), *Payoff equivalence and complete strategy spaces of direct reciprocity*](https://www.pnas.org/doi/10.1073/pnas.2518486123)  
   Relevance: benchmark conclusions depend on whether the compared strategy space is complete enough; nested-space sanity checks should accompany any “best strategy” claim.

7. `RS-GR-007`  
   [Hübner et al. (2025), *Stable strategies of direct and indirect reciprocity across all social dilemmas*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12103940/)  
   Relevance: direct and indirect reciprocity can be analyzed in one broader frame across social dilemmas, which supports treating reputation/institutions as benchmarkable rather than merely narrative.

8. `RS-GR-008`  
   [Schmid et al. (2022), *Direct reciprocity between individuals that use different strategy spaces*](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1010149)  
   Relevance: richer memory can improve welfare and still lose in adaptation against simpler spaces; heterogenous-space tests are necessary before crediting complexity.

9. `RS-GR-009`  
   [Berker & Conitzer (2024), *Computing Optimal Equilibria in Repeated Games with Restarts* (arXiv / IJCAI 2024)](https://arxiv.org/abs/2406.00851)  
   Relevance: restart-world equilibrium search is already computationally nontrivial, which makes cheap but sound canonicalization-cache invalidation rules worth encoding early.

10. `RS-GR-010`  
   [Hilbe et al. (2017), *Memory-n strategies of direct reciprocity*](https://pmc.ncbi.nlm.nih.gov/articles/PMC5422766/)  
   Relevance: stable cooperation in repeated dilemmas with implementation errors requires explicit error-correction; rematch-world canonicalization should therefore treat tremble/noise semantics as part of the world contract rather than reuse zero-noise reachability caches.

11. `RS-GR-011`  
   [Press & Dyson (2012), *Iterated prisoner's dilemma contains strategies that dominate any evolutionary opponent*](https://www.pnas.org/doi/10.1073/pnas.1206569109)  
   Relevance: the classic memory-one framing makes previous-round state explicit, which is useful for reasoning about exact support-reachability horizons in the current proxy.

12. `RS-GR-012`  
   [Fleischmann, Fragkia, & Berker (2025), *Beyond Symmetry in Repeated Games with Restarts* (IJCAI 2025)](https://www.ijcai.org/proceedings/2025/430)  
   Relevance: once restart/rematch worlds allow asymmetric strategies, role assignment on rematch becomes part of the equilibrium/world contract rather than an ignorable engine default.

13. `RS-GR-013`  
   [Bester & Sákovics (2024), *Cooperation, competition, and welfare in a matching market*](https://doi.org/10.1016/j.geb.2023.12.003)  
   Relevance: lower matching frictions have two opposing effects in repeated-dilemma matching markets — they weaken punishment by easing exit, but they also increase the share of agents in productive cooperative relationships — so rematch delay should not be conflated with full market-thickness effects.

14. `RS-GR-014`  
   [Premo & Brown (2019), *The opportunity cost of walking away in the spatial iterated prisoner’s dilemma*](https://doi.org/10.1016/j.tpb.2019.03.004)  
   Relevance: the cost of leaving rises with error and lower density, which supports treating search difficulty / market thickness as a first-class ecological variable rather than a hidden constant.

15. `RS-GR-015`  
   [Camera & Gioffré (2025), *Cooperation in temporary partnerships*](https://doi.org/10.1016/j.jedc.2024.104987)  
   Relevance: the interesting middle ground between permanent partners and one-shot strangers has its own cooperation logic, so future rematch worlds should expose partnership persistence/separation separately from rematch/search dead-time.

16. `RS-GR-016`  
   [Honhon & Hyndman (2020), *Flexibility and Reputation in Repeated Prisoner's Dilemma Games*](https://doi.org/10.1287/mnsc.2019.3495)  
   Relevance: matching institutions that differ in how relationships are dissolved produce systematically different cooperation rates, which supports treating partnership persistence / turnover as its own world-contract dimension rather than as a hidden side-effect of one delay parameter.

17. `RS-GR-017`  
   [Mengel, Orlandi & Weidenholzer (2022), *Match length realization and cooperation in indefinitely repeated games*](https://doi.org/10.1016/j.jet.2022.105416)  
   Relevance: realized match length can materially alter cooperation and even treatment comparisons, which reinforces the need to publish persistence / tempo fields and paired occupancy-normalized rankings rather than only raw aggregate rematch scores.

18. `RS-GR-018`  
   [Bernard, Fanning & Yuksel (2018), *Finding cooperators: Sorting through repeated interaction*](https://doi.org/10.1016/j.jebo.2017.11.016)  
   Relevance: treatment differences in repeated relationships can be driven strongly by sorting / replacement opportunities, which supports reporting rematch-delay robustness rather than treating one institutional friction point as definitive.

19. `RS-GR-019`  
   [Wilson & Wu (2017), *At-will relationships: How an option to walk away affects cooperation and efficiency*](https://doi.org/10.1016/j.geb.2017.02.007)  
   Relevance: once walk-away institutions and outside-option asymmetries are admitted, cooperation and efficiency can shift sharply through selection effects, so rematch reports should surface the live contender set and winner margins instead of implying a single universal ranking.


20. `RS-GR-020`  
   [Kim & Nelson (2006), *Selecting the Best System*](https://users.iems.northwestern.edu/~nelsonb/Publications/17KimNelson.pdf)  
   Relevance: ranking-and-selection treats choosing the best simulated alternative as a statistical problem with explicit probability-of-correct-selection or budget constraints, which supports attaching winner-certification metadata to rematch leaderboards instead of trusting point estimates alone.

21. `RS-GR-021`  
   [Morris, White & Crowther (2019), *Using simulation studies to evaluate statistical methods*](https://pubmed.ncbi.nlm.nih.gov/30652356/)  
   Relevance: simulation studies should define estimands, methods, and performance measures clearly and are often poorly analyzed/reported, which supports making uncertainty-bearing winner artifacts first-class rather than emitting bare rematch rank tables.

22. `RS-GR-022`  
   [Hong, Fan & Luo (2021), *Review on ranking and selection: A new perspective*](https://link.springer.com/article/10.1007/s42524-021-0152-6)  
   Relevance: ranking-and-selection procedures split naturally into fixed-precision and fixed-budget formulations, which supports treating unresolved rematch winners as a budget-allocation problem instead of reflexively demanding ever more replications.

23. `RS-GR-023`  
   [Eckman & Henderson (2022), *Posterior-Based Stopping Rules for Bayesian Ranking-and-Selection Procedures*](https://pubsonline.informs.org/doi/10.1287/ijoc.2021.1132)  
   Relevance: smarter stopping rules can reduce unnecessary sampling, which supports adding a budget-to-certify field and near-tie triage rather than oversampling every unresolved rematch frontier.

24. `RS-GR-024`  
   [Lakens (2017), *Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses*](https://pmc.ncbi.nlm.nih.gov/articles/PMC5502906/)  
   Relevance: equivalence testing uses a prespecified smallest effect of interest to decide when an observed difference is small enough to be considered practically negligible, which supports adding a declared rematch indifference zone instead of treating every positive gap as decision-relevant.

25. `RS-GR-025`  
   [Gutierrez & Cribbie (2023), *Effect sizes for equivalence testing: Incorporating the equivalence interval*](https://doi.org/10.1016/j.metip.2023.100127)  
   Relevance: effect interpretation should be tied to the equivalence interval itself, which supports surfacing not just winner certification but also how far a rematch top-gap panel is from a practical-tie declaration.

26. `RS-GR-026`  
   [Smiley et al. (2023), *Null regions: a unified conceptual framework for statistical tests of hypotheses in terms of their practical significance*](https://pmc.ncbi.nlm.nih.gov/articles/PMC10663783/)  
   Relevance: null-region thinking reduces minimum-effect, equivalence, and related interval decisions to a confidence-interval-vs-threshold geometry, which supports publishing rematch materiality as compact delta frontiers rather than as many ad hoc threshold labels.

27. `RS-GR-027`  
   [Giner-Sorolla et al. (2024), *Power to Detect What? Considerations for Planning and Evaluating Sample Size*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11193916/)  
   Relevance: the smallest effect size of interest should be distinguished from purely resource-based practical minima, which supports making rematch delta sensitivity explicit instead of silently baking a single arbitrary indifference zone into the archive.

28. `RS-GR-028`  
   [Ranganathan et al. (2022), *Equivalence trials*](https://pmc.ncbi.nlm.nih.gov/articles/PMC9106130/)  
   Relevance: equivalence claims depend explicitly on a prespecified margin, and narrower margins drive larger sample-size requirements, which supports publishing the rematch delta-vs-budget tradeoff rather than hiding closure cost behind one arbitrary threshold.

29. `RS-GR-029`  
   [Villarino et al. (2025), *Recommendations for a Complete Reporting of Statistical Methods in Veterinary Pharmacology*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12257266/)  
   Relevance: effect sizes used for sample-size planning should be scientifically relevant rather than reverse-engineered from convenient budgets, which supports surfacing rematch delta-budget frontiers openly instead of letting simulation cost silently choose the indifference zone.

30. `RS-GR-030`  
   [Greene et al. (2008), *Noninferiority and Equivalence Designs: Issues and Implications for Mental Health Research*](https://pmc.ncbi.nlm.nih.gov/articles/PMC2696315/)  
   Relevance: when the prespecified margin is too small, power can drop dramatically, which supports surfacing rematch delta hazard bands rather than acting as if every SESOI near an observed top-gap mean is equally cheap to close.

31. `RS-GR-031`  
   [Schubert et al. (2025), *Improving statistical reporting in psychology*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12618885/)  
   Relevance: equivalence margins should be justified and reported across plausible ranges, and post hoc margin choices require caution, which supports publishing rematch hazard/frontier artifacts instead of quietly picking whichever delta looks cheapest after seeing the data.


32. `RS-GR-032`  
   [European Medicines Agency (2025), *Non-inferiority and equivalence comparisons in clinical trials – Scientific guideline*](https://www.ema.europa.eu/en/non-inferiority-equivalence-comparisons-clinical-trials-scientific-guideline)  
   Relevance: current EMA guidance frames non-inferiority/equivalence margins as part of trial planning, conduct, analysis, and interpretation, which supports treating rematch practical margins as an explicit contract rather than a quiet post hoc tuning knob.

33. `RS-GR-033`  
   [EMA (2000), *Points to consider on switching between superiority and non-inferiority*](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)  
   Relevance: EMA explicitly warns that post hoc changes to equivalence margins are not acceptable, which supports publishing rematch budget-admissible delta bands so future inheritors choose from prespecified stable intervals rather than whichever knife-edge threshold looks cheapest after the fact.


34. `RS-GR-034`  
   [Baldwin et al. (2022), *Protecting against researcher bias in secondary data analysis: challenges and potential solutions*](https://pmc.ncbi.nlm.nih.gov/articles/PMC8791887/)  
   Relevance: multiverse/specification-curve style reporting reduces scope for selective reporting across defensible analytic choices, which supports publishing rematch topology-stable delta subbands instead of one quietly chosen anchor inside a broad admissible band.

35. `RS-GR-035`  
   [Dick et al. (2025), *Meaningful Associations Redux: Quantifying and interpreting effect size in the context of the Adolescent Brain and Cognitive Development study*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12554081/)  
   Relevance: the proposed define-compare-test-visualize framework ties SESOI choice to explicit visualization and interpretation, which supports publishing rematch topology-core artifacts and stability-first anchors rather than only scalar delta labels.

36. `RS-GR-036`  
   [Ruhdorfer et al. (2025), *The Overcooked Generalisation Challenge*](https://openreview.net/forum?id=YKvBiRWdQC)  
   Relevance: partner novelty and environment novelty should be tested separately; zero-shot cooperation claims that hold only with familiar layouts or familiar partners are too weak for Concord benchmark interoperability.

37. `RS-GR-037`  
   [Jha et al. (2025), *Cross-environment Cooperation Enables Zero-shot Multi-agent Coordination*](https://openreview.net/forum?id=zBBYsVGKuB)  
   Relevance: training across many coordination environments can produce norms that transfer to unfamiliar partners, which supports treating cross-world generalization as a first-class benchmark axis rather than a side observation.

38. `RS-GR-038`  
   [Guo et al. (2026), *SocialJax: An Evaluation Suite for Multi-agent Reinforcement Learning in Sequential Social Dilemmas*](https://openreview.net/forum?id=Qg6kHVN91t)  
   Relevance: a fast social-dilemma suite with partner-generalization evaluation and validated dilemma structure makes it feasible to add a lightweight interoperability lane without retaining bulky local benchmark fanout.

39. `RS-GR-039`  
   [Capitaine et al. (2026), *Test-then-Punish: A Statistical Approach to Repeated Games*](https://arxiv.org/abs/2603.05619)  
   Relevance: under imperfect monitoring, the monitoring rule, test family, batch size, and false-punishment budget are part of the institution itself, which supports treating statistical deviation-detection contracts as compact benchmark metadata rather than as hidden implementation detail.

40. `RS-GR-040`  
   [Zhu et al. (2025), *Learning to Negotiate via Voluntary Commitment*](https://arxiv.org/abs/2503.03866)  
   Relevance: mixed-motive coordination changes materially once commitment is made explicit and enforceable, which supports treating blind-commit vs live-reoptimized promise semantics as a first-class world contract rather than as an unlogged controller detail.

41. `RS-GR-041`  
   [Song et al. (2025), *Learning to Cooperate with Emergent Reputation via Multi-agent Reinforcement Learning*](https://openreview.net/forum?id=VZCHc1OOrD)  
   Relevance: reputation-mediated cooperation depends on assessment rules, diffusion topology, and latency/noise in feedback channels, which supports treating reputation mechanics as a compact world contract rather than as hidden benchmark plumbing.

42. `RS-GR-042`  
   [Luo et al. (2026), *Algorithmic Collusion at Test Time: A Meta-game Design and Evaluation*](https://arxiv.org/abs/2602.17203)  
   Relevance: test-time strategic behavior can depend jointly on the initial policy class and the permitted in-game adaptation rule, which supports treating starting-policy provenance and adaptation budgets as compact world-contract metadata rather than as hidden controller detail.

43. `RS-GR-043`  
   [Syrnikov et al. (2026), *Institutional AI: Governing LLM Collusion in Multi-Agent Cournot Markets via Public Governance Graphs*](https://arxiv.org/abs/2601.11369)  
   Relevance: when worlds enforce norms through explicit legal states, transitions, sanctions, and restorative paths, those governance edges materially shape outcomes and should be published as institution/world-contract metadata rather than hidden runtime plumbing.

44. `RS-GR-044`  
   [Menendez et al. (2026), *Prompt-Dependent Ranking of Large Language Models with Uncertainty Quantification*](https://arxiv.org/abs/2603.03336)  
   Relevance: decision-safe evaluation should not force one brittle point ranking when local context changes or uncertainty leave several orderings live; confidence-aware partial orders are often the correct inheritor-facing object.

45. `RS-GR-045`  
   [Vishnyakova (2026), *From Prompt–Response to Goal-Directed Systems: The Evolution of Agentic AI Software Architecture*](https://arxiv.org/abs/2602.10479)  
   Relevance: multi-agent systems require explicit communication contracts, shared-memory choices, and authority / escalation models, which supports treating agent topology, messaging, memory, and action authority as compact world-contract metadata rather than hidden orchestration detail.

46. `RS-GR-046`  
   [Froger et al. (2026), *Gaia2: Benchmarking LLM Agents on Dynamic and Asynchronous Environments*](https://openreview.net/forum?id=9gw03JpKK4)  
   Relevance: when environments evolve independently of agent actions under temporal constraints, timing, exogenous events, and observation/update latency become part of the institution itself, which supports treating clock and event semantics as compact world-contract metadata rather than hidden benchmark scaffolding.

47. `RS-GR-047`  
   [Wu et al. (2026), *CUBE: An open benchmark package for evaluating foundation models*](https://arxiv.org/abs/2603.15798)  
   Relevance: benchmark programs benefit from explicit layering across tasks, benchmark packages, registries, and interfaces, which supports compact publication cards that separate benchmark content from governance / packaging state.

48. `RS-GR-048`  
   [Vijayvargiya et al. (2026), *Who Evaluates the Evaluators? Governance Challenges in AI Safety and Alignment Evaluations*](https://openreview.net/forum?id=8rwpMdkf0L)  
   Relevance: evaluations are governance instruments as well as measurement tools, which supports publishing compact transparency / governance cards for tranche closure, validator inventory, reproducibility posture, and risk review rather than hiding them in workflow residue.

## Formal Solvers and Verification

1. `RS-FM-001`  
   [SMT-LIB initiative](https://smt-lib.org/)  
   Relevance: common input language for solver-agnostic formal checks.

2. `RS-FM-002`  
   [Z3 Guide](https://microsoft.github.io/z3guide/)  
   Relevance: reference semantics for constraints and satisfiability workflows.

3. `RS-FM-003`  
   [Rust `z3` crate docs](https://docs.rs/z3/latest/z3/)  
   Relevance: native Rust interface for solver-backed invariants.

4. `RS-FM-004`  
   [cvc5 documentation](https://cvc5.github.io/)  
   Relevance: second solver backend for cross-solver consistency checks.

5. `RS-FM-005`  
   [Rust `rsmt2` crate docs](https://docs.rs/rsmt2/latest/rsmt2/)  
   Relevance: solver-process boundary for deterministic, adapter-driven SMT execution.

6. `RS-FM-006`  
   [PRISM model checker](https://www.prismmodelchecker.org/)  
   Relevance: probabilistic model checking for stochastic policy/world assertions.

7. `RS-FM-007`  
   [Storm model checker](https://www.stormchecker.org/)  
   Relevance: independent probabilistic model-checking engine for cross-tool confirmation.

8. `RS-FM-008`  
   [Kani Rust verifier](https://model-checking.github.io/kani/)  
   Relevance: bounded model checking for Rust safety/property checks.

9. `RS-FM-009`  
   [Prusti verifier docs](https://viperproject.github.io/prusti-dev/)  
   Relevance: contract-oriented Rust proofs for stronger guarantees on critical modules.

10. `RS-FM-010`  
    [Creusot project repository](https://github.com/creusot-rs/creusot)  
    Relevance: additional deductive verification path for Rust.

11. `RS-FM-011`  
    [Kani Rust feature support matrix](https://model-checking.github.io/kani/rust-feature-support.html)  
    Relevance: practical constraint map for what should (and should not) be sent to bounded model checking first.

12. `RS-FM-012`  
    [PRISM tutorial](https://www.prismmodelchecker.org/tutorial/)  
    Relevance: practical entry path for DTMC/MDP-style models and property workflows.

13. `RS-FM-013`  
    [Hartmanns et al. (2023), *A Practitioner's Guide to MDP Model Checking Algorithms* (arXiv)](https://arxiv.org/abs/2301.10197)  
    Relevance: algorithmic trade-offs for MDP checking (value iteration vs alternatives), useful for tool-choice policy.

## Rust/Python Boundary Tooling

1. `RS-RP-001`  
   [PyO3 guide](https://pyo3.rs/)  
   Relevance: stable Rust-to-Python FFI for exposing deterministic kernels.

2. `RS-RP-002`  
   [maturin documentation](https://www.maturin.rs/)  
   Relevance: reproducible packaging of Rust extensions for Python orchestration.

## Reproducibility and Operations

1. `RS-OPS-001`  
   [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/)  
   Relevance: declarative, reproducible workflow DAG concepts for experiment orchestration.

2. `RS-OPS-002`  
   [DVC documentation](https://dvc.org/doc)  
   Relevance: data/artifact lineage patterns for experiment versioning.

3. `RS-OPS-003`  
   [NASEM: *Reproducibility and Replicability in Science*](https://nap.nationalacademies.org/catalog/25303/reproducibility-and-replicability-in-science)  
   Relevance: high-level policy guidance for reproducibility posture and evidence practices.

4. `RS-OPS-004`  
   [Criterion.rs book](https://bheisler.github.io/criterion.rs/book/)  
   Relevance: statistically principled benchmarking for Rust performance claims.

5. `RS-OPS-005`  
   [cargo-nextest docs](https://nexte.st/)  
   Relevance: scalable, deterministic Rust test execution in CI and local loops.

6. `RS-OPS-006`  
   [Rust language site, *Getting Started*](https://rust-lang.org/learn/get-started/)  
   Relevance: the official Rust site says the Rust Playground lets users try Rust online without local installation, which supports treating the Playground as a minimal escalation lane for tiny non-sensitive snippets when this cloudtainer lacks `cargo`.

7. `RS-OPS-007`  
   [Rust documentation portal](https://doc.rust-lang.org/stable/)  
   Relevance: the official docs say the Playground is suitable for small bits of code and some popular crates, which supports keeping remote snippet work small and self-contained rather than trying to externalize the whole archive.

8. `RS-OPS-008`  
   [Compiler Explorer](https://godbolt.org/)  
   Relevance: Compiler Explorer exposes compile, execute, share, and output-inspection surfaces for tiny examples, which supports using it as a spot-check lane for small Rust fragments when local toolchains are unavailable.

9. `RS-OPS-009`  
   [Tree-sitter introduction](https://tree-sitter.github.io/tree-sitter/)  
   Relevance: Tree-sitter provides incremental concrete-syntax parsing with official Node and Python bindings, which supports static Rust source analysis in a Python/Node-capable cloudtainer even when `rustc` is absent.

10. `RS-OPS-010`  
   [tree-sitter-rust](https://github.com/tree-sitter/tree-sitter-rust)  
   Relevance: the upstream Rust grammar gives a syntax-only route for parsing Rust source without invoking Cargo, which supports source-surface inventories and future parser-backed static checks when the Rust lane is blocked.

## Immediate Repo Implications

1. Keep memory-one analytic certification as a first-class artifact path (`RS-IPD-001`..`RS-IPD-004`).
2. Evaluate strategy quality using robustness/holdouts, not single-opponent wins (`RS-IPD-002`, `RS-IPD-003`).
3. Add longer-memory and recency-weighted reciprocity baselines before expanding search breadth (`RS-GR-001`).
4. Treat anti-vampire evaluation as multi-objective: own payoff, payoff gap, recovery, and fairness pressure (`RS-GR-002`).
5. Add leave/rematch mechanics and opt-out policies as first-class world/strategy surfaces (`RS-GR-003`, `RS-GR-005`).
6. Keep universalisation/Kantian-style policies as explicit benchmark families instead of prose-only ideals (`RS-GR-004`).
7. Add nested-strategy-space sanity checks before ranking “best” strategies (`RS-GR-006`, `RS-GR-008`).
8. Treat indirect reciprocity / reputation as an explicit benchmark lane, not only future prose (`RS-GR-007`).
9. Build a dual-solver SMT layer (Z3 + cvc5) with shared SMT-LIB contracts (`RS-FM-001`..`RS-FM-005`).
10. Introduce probabilistic model-checking lanes for stochastic world properties (`RS-FM-006`, `RS-FM-007`).
11. Preserve Rust truth and Python orchestration using a typed FFI seam (`RS-RP-001`, `RS-RP-002`).
12. Treat reproducibility metadata as mandatory experiment output (`RS-OPS-001`..`RS-OPS-005`).
13. When `cargo` / `junest` are unavailable, keep the session moving with static Rust surface inventories and Python shadow checks, and treat remote compilers as tiny snippet-only escalation lanes rather than as archive-state dependencies (`RS-OPS-006`..`RS-OPS-010`).
14. Keep canonicalization-horizon choices world-aware and explicitly validated rather than inheriting a generic fixed bound (`RS-GR-011`).
15. Do not generalize exogenous-pool delay sweeps into matching-market welfare claims until market thickness / search difficulty is modeled separately from dead-round delay (`RS-GR-013`, `RS-GR-014`).
16. Require rematch-world welfare artifacts to decompose occupancy (`matched` vs `searching`) from in-match performance; otherwise aggregate payoffs can hide whether gains come from better matching or better conduct within matches (`RS-GR-013`, `RS-GR-015`).

17. Publish both raw aggregate and occupancy-normalized rematch leaderboards in rematch worlds; otherwise tempo-induced occupancy shifts can be mistaken for genuine within-match quality changes (`RS-GR-013`, `RS-GR-015`, `RS-GR-017`).
18. Do not ship single-delay rematch winners as if they were universal rankings; publish a delay sweep, crossover thresholds, or an explicit robustness interval over the deployed rematch-friction range (`RS-GR-016`, `RS-GR-017`, `RS-GR-018`).
19. Before widening rematch delay sweeps, publish a compact live contender artifact (dead contenders, tested-band leaders, winner margins, and frontier intervals where needed); the decision-relevant contender set can be much smaller than the full raw ranking table (`RS-GR-018`, `RS-GR-019`).

20. Publish budget-aware winner-triage metadata for unresolved rematch panels; if certifying a tiny frontier flip would require orders of magnitude more paired seeds than the baseline budget, keep it as a compact near-tie artifact instead of oversampling by default (`RS-GR-020`, `RS-GR-022`, `RS-GR-023`).
21. Publish a declared smallest effect of interest (`delta`) plus practical-equivalence status for rematch top gaps; in the current proxy, some statistically certified winners are already practical ties at modest `delta`, and the only uncertified leader flip becomes a practical tie well before it becomes cheap to certify a winner (`RS-GR-024`, `RS-GR-025`).
22. Publish per-panel rematch delta frontiers (`largest_material_delta_supported`, `smallest_equivalence_delta_supported`) so any later choice of `delta` can be applied from a compact artifact instead of proliferating ad hoc multi-threshold label tables (`RS-GR-025`, `RS-GR-026`, `RS-GR-027`).
23. Publish rematch delta-budget frontiers over the plausible SESOI band so inheritors can see how many panels remain unresolved and what extra paired-seed budget closure would require without letting budget silently choose `delta` (`RS-GR-027`, `RS-GR-028`, `RS-GR-029`).
24. Publish rematch leader-gap hazard bands or an equivalent no-knife-edge buffer over the plausible SESOI band; otherwise coarse delta sweeps can hide narrow threshold neighborhoods where closure cost explodes near observed top-gap means (`RS-GR-028`, `RS-GR-030`, `RS-GR-031`).
25. Publish budget-admissible rematch delta bands (plus one anchor per band) for any declared extra-budget cap; otherwise nearly indistinguishable margins can hide radically different closure costs and invite post hoc threshold shopping around knife-edge gaps (`RS-GR-024`, `RS-GR-032`, `RS-GR-033`).
26. Publish topology-stable rematch delta subbands or a stability-first anchor inside each admissible parent band; otherwise the same declared cap/band can still hide multiple materially different panel-label summaries (`RS-GR-031`, `RS-GR-034`, `RS-GR-035`).
27. When rematch or benchmark worlds rely on imperfect monitoring, publish the monitoring contract compactly (observation model, test family, batch/sequential rule, and false-punishment budget); otherwise changes in statistical detection policy can masquerade as changes in reciprocity itself (`RS-GR-039`).
28. When rematch or partner-choice worlds carry reputation across encounters, publish the reputation contract compactly (visibility, assessment rule, diffusion topology, latency/noise, and decision hooks); otherwise changes in gossip plumbing can masquerade as changes in reciprocity or assortment (`RS-GR-007`, `RS-GR-041`, `RS-GR-135`).
29. In partner-choice worlds, separate observable-help metrics from unobserved partner-maintenance metrics; otherwise performative reciprocity can masquerade as Golden-Rule conduct (`RS-GR-134`).
30. When rematch or benchmark worlds evaluate test-time adaptation from a standing strategic prior, publish the starting-policy source, adaptation rule, state carryover rule, and adaptation budget compactly; otherwise changes in strategic prior or adaptation permissions can masquerade as changes in reciprocity or institution quality (`RS-GR-042`).
31. When worlds enforce norms through sanctions, suspensions, restoration paths, or equivalent controller-mediated transitions, publish the governance graph compactly (legal states, evidence predicates, transitions, sanctions, restoration paths, and audit-log commitments); otherwise prompt-only prohibitions and enforceable institutions can be conflated (`RS-GR-039`, `RS-GR-043`).
32. When a declared benchmark or rematch summary can vary across nearby internal decision thresholds, publish the stability surface (subbands, buffers, unresolved partial orders, or equivalent confidence-aware structure) rather than laundering one knife-edge point into a fixed inheritor-facing object (`RS-GR-035`, `RS-GR-044`).
33. When a world routes decisions through multiple coordinated agents, publish the agent topology / role graph, messaging contract, memory regime, and action-authority graph compactly; otherwise changes in orchestration wiring can masquerade as changes in reciprocity or institutional quality (`RS-GR-045`).
34. When environments evolve asynchronously or exogenous events advance independently of agent actions, publish the clock model, action/observation latency, timeout semantics, and exogenous-event process compactly; otherwise changes in timing semantics can masquerade as changes in reciprocity, competence, or institution quality (`RS-GR-046`).
35. When a benchmark publication now depends on tranche closure, validator coverage, replay posture, and explicit risk review, publish one compact governance card over those surfaces rather than letting inheritors reconstruct readiness from multiple operational summaries (`RS-GR-047`, `RS-GR-048`).
36. When a benchmark uses human-proxy partners, publish proxy provenance, hosting posture, and whether any real-human lane has been run; otherwise proxy success can be laundered into an unjustified human-compatibility claim (`RS-GR-049`, `RS-GR-050`).
37. When a benchmark includes real humans, publish the counterpart-disclosure condition and any participant-belief elicitation; otherwise human-lane differences can partly reflect what people thought they were interacting with, not just the policy they faced (`RS-GR-051`, `RS-GR-052`).
38. When a cooperation benchmark uses natural-language interaction, publish the interaction language, translation/localization regime, and pooling rule across language lanes; otherwise language or wording changes can masquerade as changes in reciprocity or policy quality (`RS-GR-053`, `RS-GR-054`).
39. When a cooperation benchmark includes any message channel, publish the communication schedule, channel rights, and message constraints; otherwise differences in chat timing or permissions can masquerade as differences in reciprocity, trust, or policy quality (`RS-GR-055`, `RS-GR-056`).
40. When a cooperation benchmark includes real humans, publish the material payoff matrix, stake/compensation mapping, and comprehension protocol; otherwise differences in incentives or misunderstanding can masquerade as differences in reciprocity or social preference (`RS-GR-053`, `RS-GR-057`, `RS-GR-058`).

41. When a cooperation benchmark includes real humans, publish participant-pool provenance, recruitment platform, country / residence mix, and repeat-exposure policy; otherwise cross-population or re-participation effects can masquerade as differences in reciprocity or human compatibility (`RS-GR-059`, `RS-GR-060`).
42. When a cooperation benchmark uses repeated interaction, publish the horizon regime, stopping-rule parameters, and what participants knew about termination; otherwise differences in the shadow of the future or realized match length can masquerade as differences in reciprocity or policy quality (`RS-GR-055`, `RS-GR-061`, `RS-GR-062`).

43. When a cooperation benchmark reports cooperation or task success, publish whether it is outcome-only or process-aware, plus any reasoning / message / repair / common-ground metrics used; otherwise superficially similar outcomes can hide brittle or incoherent coordination paths (`RS-GR-063`, `RS-GR-064`).
44. When a cooperation benchmark mixes advice, delegation, co-action, or override-enabled control splits, publish the intervention rights, delegation policy, and final-action authority; otherwise interface-control choices can masquerade as differences in reciprocity or policy quality (`RS-GR-065`, `RS-GR-066`).

45. When a cooperation benchmark changes who can see which task-relevant facts, how much shared state is visible, or whether hidden information must be actively surfaced, publish the information-visibility and asymmetry regime explicitly; otherwise differences in observability can masquerade as differences in reciprocity, common-ground skill, or policy quality (`RS-GR-067`, `RS-GR-068`).


46. When a cooperation benchmark allows acclimation or practice before scoring, publish whether post-adaptation results come from same-partner continuation or from fresh-partner transfer, plus any state carryover across partner boundaries; otherwise private co-adaptation can masquerade as broader cooperation generalization (`RS-GR-037`, `RS-GR-069`, `RS-GR-070`).
47. When a cooperation benchmark is role-asymmetric or can place the system into substantively different interaction seats, publish the role taxonomy, seat-assignment rule, seat pooling rule, and whether a side-swapped companion lane was run; otherwise role allocation can masquerade as a general cooperation result (`RS-GR-071`, `RS-GR-072`, `RS-GR-073`).
48. When a cooperation benchmark card is used to support a headline comparison, publish the exact comparison the card licenses and at least one nearby stronger comparison it does not license without further justification; otherwise richly different lanes can still be laundered into a generic “more cooperative” claim (`RS-GR-053`, `RS-GR-055`, `RS-GR-063`, `RS-GR-067`, `RS-GR-074`, `RS-GR-075`, `RS-GR-076`).

49. When a cooperation benchmark reports a top-line score, publish the scored unit, pooling / weighting rule, and primary estimand; otherwise per-turn, per-episode, per-participant, or pooled-across-lane summaries can masquerade as one comparable cooperation quantity (`RS-GR-021`, `RS-GR-074`, `RS-GR-076`, `RS-GR-077`).
50. When a cooperation benchmark reports a comparative result, publish the dependence structure, inference / resampling unit, and primary uncertainty summary; otherwise repeated turns, episodes, or participants can masquerade as many independent datapoints and overstate certainty (`RS-GR-076`, `RS-GR-078`, `RS-GR-079`).
51. When a cooperation benchmark scores LLM / agent-only lanes, publish the incentive instruction, reward semantics, payoff scaling, and any points-to-utility conversion rule; otherwise changes in stake salience or reward framing can masquerade as changes in cooperation or rationality (`RS-GR-057`, `RS-GR-128`, `RS-GR-129`, `RS-GR-130`).
52. When a cooperation benchmark result depends on choosing one prompt, interface, scoring, or agent-shell variant from a wider family, publish the variant family, the selection / tuning rule, the search budget, and whether benchmark test outcomes were touched during selection; otherwise a best-picked wrapper can masquerade as a stable cooperation gain (`RS-GR-080`, `RS-GR-081`, `RS-GR-082`).
53. When a cooperation benchmark score can change because malformed outputs, refusals, timeouts, judge failures, retries, repairs, or filtered cases are handled differently, publish the raw denominator, scored denominator, failure taxonomy, retry / repair budget, and exclusion / scoring rule; otherwise valid-attempt or repaired-attempt scores can masquerade as raw benchmark performance (`RS-GR-074`, `RS-GR-083`, `RS-GR-084`, `RS-GR-085`, `RS-GR-086`).

54. When a cooperation benchmark relies on LLM judges, human raters, or hybrid adjudication stacks, publish judge provenance, rubric / scoring protocol, debias / adjudication rule, and calibration / escalation policy; otherwise evaluator choice can masquerade as a cooperation gain (`RS-GR-083`, `RS-GR-087`, `RS-GR-088`, `RS-GR-089`, `RS-GR-090`).
55. When a cooperation benchmark draws tasks, worlds, assignments, or episodes from a stochastic family, publish the scenario family, draw / randomization rule, seed / reroll policy, and release posture; otherwise one lucky draw or one public/private holdout posture can masquerade as a cooperation gain (`RS-GR-074`, `RS-GR-091`, `RS-GR-092`, `RS-GR-093`).

56. When a cooperation benchmark reports a result for a provider endpoint, dated model marker, local weight snapshot, or third-party compatible service, publish the evaluated-subject provenance, serving stack, evaluation window, and drift posture; otherwise endpoint identity or deployment drift can masquerade as a cooperation gain (`RS-GR-094`, `RS-GR-095`, `RS-GR-096`, `RS-GR-097`).
57. When a cooperation benchmark score can change because one run had more turns, tool calls, retained history, tokens, or timeout slack than another, publish the turn / action / tool budget, context / history-retention policy, token / compute / latency budget, and limit-hit rule; otherwise extra interaction or runtime slack can masquerade as a cooperation gain (`RS-GR-098`, `RS-GR-099`, `RS-GR-100`, `RS-GR-101`).
58. When a cooperation benchmark score can change because the available tools, writable world state, live-service posture, or retrieval corpus changed, publish the tool / capability catalog, external-state snapshot posture, knowledge-base / corpus provenance, and reset / refresh / mutability policy; otherwise environment or corpus drift can masquerade as a cooperation gain (`RS-GR-102`, `RS-GR-103`, `RS-GR-104`, `RS-GR-105`, `RS-GR-106`, `RS-GR-107`).
59. When a cooperation benchmark report could promote one metric, composite, or convenience headline from a wider family of plausible cooperation measures, publish the primary endpoint, auxiliary metrics, composite rule, and multiplicity / metric-selection policy; otherwise metric shopping can masquerade as a cooperation gain (`RS-GR-074`, `RS-GR-076`, `RS-GR-108`, `RS-GR-109`, `RS-GR-110`).

60. When the archive retains a cooperation benchmark card, prefer one machine-checkable compact publication object plus one worked example; otherwise future inheritors must repeatedly reconstruct the card from prose and can reintroduce silent omissions or inconsistent formatting (`RS-GR-111`, `RS-GR-112`, `RS-GR-113`).
61. When the archive expects future sessions to fill and review compact cooperation cards repeatedly, also ship one scaffold path and one canonical renderer; otherwise every inheritor can recreate omission drift or display drift around the same schema-backed object (`RS-GR-111`, `RS-GR-112`, `RS-GR-114`).
62. When the archive retains compact cooperation cards as claim-bearing objects, distinguish schema-valid draft cards from claim-ready cards via one tiny readiness lint; otherwise unresolved placeholders or vacuous inapplicability markers can masquerade as completed benchmark documentation (`RS-GR-111`, `RS-GR-114`, `RS-GR-115`, `RS-GR-116`).
63. When the archive cites or hands off a claim-ready compact cooperation card, also freeze it into one tiny receipt that binds the exact JSON card to the exact canonical rendered view plus the governing schema/tool hashes; otherwise later card edits or stale rendered summaries can drift apart while still looking like one publication object (`RS-GR-111`, `RS-GR-114`, `RS-GR-117`, `RS-GR-118`).
64. When the archive updates one retained claim-ready compact cooperation card into another, also emit one tiny delta receipt that lists the changed field paths and separates claim-surface changes from metadata-only drift; otherwise future inheritors must reconstruct by hand whether the benchmark claim moved or only the surrounding notes / labels moved (`RS-GR-117`, `RS-GR-119`, `RS-GR-120`, `RS-GR-121`).
65. When the archive retains heterogeneous example JSON snapshots under strict schemas, make each example addressable by either an explicit `id` or one canonical repo-path surrogate id; otherwise inventories, duplicate-id checks, and small receipt linkages must special-case schema families and drift back toward manual bookkeeping (`RS-GR-114`, `RS-GR-117`, `RS-GR-122`, `RS-GR-123`).
66. When the archive retains multiple compact cooperation cards plus freeze / delta receipts, also publish one tiny generated inventory over cards, receipt linkages, latest-known claim-ready ids, and orphan receipts; otherwise the archive regresses to manual archaeology even though the underlying card artifacts are already machine-checkable (`RS-GR-117`, `RS-GR-118`, `RS-GR-120`, `RS-GR-122`, `RS-GR-124`, `RS-GR-125`).
67. When the archive retains versioned cooperation-card lineages, also publish one tiny head register that distinguishes operational heads from frozen citation heads and flags branching or missing-freeze ambiguity; otherwise inheritors cannot tell which retained tip is current versus citation-ready without manual lineage tracing (`RS-GR-117`, `RS-GR-123`, `RS-GR-125`, `RS-GR-126`, `RS-GR-127`).

68. When a cooperation or rematch world excludes, suspends, or ostracizes agents, publish the rehabilitation contract compactly (exclusion duration, re-entry rule, apology / repair availability, signal visibility / trackability, and whether re-entry is automatic or earned); otherwise punishment worlds can masquerade as the same institution while materially differing in restoration semantics (`RS-GR-138`, `RS-GR-139`).
69. When a cooperation or reputation world enables apology, emotion, or other expressive repair signals, publish the signal vocabulary, timing rights, audience / visibility, reputation hooks, and at least one follow-through or abuse metric; otherwise extra error-correction bandwidth can masquerade as policy quality or norm robustness (`RS-GR-139`, `RS-GR-140`).

70. When a cooperation or partner-choice world includes pledges, vows, or other commitment stages, publish their timing, audience, bindingness, breach consequences, and whether evaluators score later actions relative to commitment state; otherwise promise-enabled cooperation can masquerade as generic reciprocity (`RS-GR-172`, `RS-GR-173`, `RS-GR-175`).
71. When a cooperation or reputation world allows post-hoc self-signaling, publish signal timing, cost, rate limits, scoring rule, and whether follow-through is required for repair; otherwise cheap impression management can masquerade as trustworthiness or moral growth (`RS-GR-174`, `RS-GR-175`).


72. `RS-GR-049`  
   [Akata et al. (2025), *Playing repeated games with large language models*](https://www.nature.com/articles/s41562-025-02172-y)  
   Relevance: cooperation conclusions depend on whether models are evaluated against other models, scripted human-like strategies, or actual human players, which supports publishing counterpart mix as explicit benchmark-contract metadata rather than burying it inside one blended score.

73. `RS-GR-050`  
   [Dizdarevic et al. (2025), *Ad-Hoc Human-AI Coordination Challenge*](https://openreview.net/forum?id=Kioojohsuy)  
   Relevance: human-proxy partners can make evaluation cheaper, more reproducible, and hostable to reduce overfitting, but they remain a distinct benchmark lane whose provenance and relation to real-human evaluation should be published explicitly.


74. `RS-GR-051`  
   [Tanguy et al. (2025), *Human Alignment: How Much We Adapt to LLMs?*](https://openreview.net/forum?id=U3FXUrEJWT)  
   Relevance: in a cooperative word game, humans showed different alignment patterns with LLMs than with humans, and users' beliefs about their partners further modulated those effects, so human-lane benchmark cards should publish disclosure and belief protocol rather than treating counterpart identity as invisible context.

75. `RS-GR-052`  
   [Barak & Costa-Gomes (2025), *Humans expect rationality and cooperation from LLM opponents in strategic games*](https://arxiv.org/abs/2505.11011)  
   Relevance: human strategic choices shift when the opponent is an LLM rather than a human, partly because participants infer different reasoning ability and cooperativeness, which supports publishing counterpart-disclosure and participant-belief metadata for real-human benchmark lanes.

76. `RS-GR-053`  
   [Huynh et al. (2026), *More at Stake: How Payoff and Language Shape LLM Agent Strategies in Cooperation Dilemmas*](https://arxiv.org/abs/2601.19082)  
   Relevance: repeated-dilemma behavior can shift with payoff magnitude and interaction language, with cross-linguistic divergence and language effects that can rival architecture differences, so benchmark cards should treat interaction language and pooling across language lanes as explicit metadata rather than hidden prompt context.

77. `RS-GR-054`  
   [Lorè & Heydari (2024), *Strategic behavior of large language models and the role of game structure versus contextual framing*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11316122/)  
   Relevance: contextual framing materially changes LLM strategic decisions across canonical games, reinforcing that wording and localization belong in the benchmark contract instead of being treated as a harmless wrapper around the same task.


78. `RS-GR-055`  
   [Anwar & Georgalos (2026), *Playing Against the Machine: Cooperation, Communication, and Strategy Heterogeneity in Repeated Prisoner's Dilemma*](https://arxiv.org/abs/2603.15852)  
   Relevance: in indefinitely repeated human–AI Prisoner's Dilemma, changing communication timing changes the benchmark interpretation itself: repeated chat substantially lifts human–human cooperation but shows almost no detectable additional effect with the AI partner, so benchmark cards should publish message schedule and channel rights rather than treating them as harmless interface details.

79. `RS-GR-056`  
   [Niszczota et al. (2025), *People Are Highly Cooperative with Large Language Models, Especially When Communication Is Possible or Following Human Interaction*](https://arxiv.org/abs/2507.18639)  
   Relevance: allowing communication can materially raise cooperation with both human and LLM partners even when the human–machine gap remains, which supports publishing whether communication was possible and how that lane was compared instead of pooling across silent and communicative settings.

80. `RS-GR-057`  
   [Gächter et al. (2024), *The role of payoff parameters for cooperation in the one-shot Prisoner's Dilemma*](https://doi.org/10.1016/j.euroecorev.2024.104753)  
   Relevance: human cooperation in Prisoner's Dilemma shifts with material payoff parameters, especially the gain from mutual cooperation over mutual defection, so benchmark cards should publish the actual payoff matrix and stake mapping rather than treating incentives as a harmless wrapper around the same task.

81. `RS-GR-058`  
   [Koppel et al. (2025), *Comprehension in economic games*](https://doi.org/10.1016/j.jebo.2025.107039)  
   Relevance: misunderstanding standard economic games is common and can itself raise measured prosocial behavior, which supports publishing comprehension checks, exclusion/retry rules, and whether headline results use the full sample or only participants who demonstrated understanding.


82. `RS-GR-059`  
   [Karpus et al. (2025), *Human cooperation with artificial agents varies across countries*](https://www.nature.com/articles/s41598-025-92977-8)  
   Relevance: cooperation with artificial agents can differ across countries even when human-human cooperation looks more stable, so real-human benchmark lanes should publish participant-pool provenance and country / residence mix rather than treating one recruiting pool as a universal human baseline.

83. `RS-GR-060`  
   [Moon et al. (2026), *Identity, Cooperation and Framing Effects within Groups of Real and Simulated Humans*](https://arxiv.org/abs/2601.16355)  
   Relevance: participant-pool effects, framing, and study context can materially affect cooperation conclusions and replication fidelity, which supports publishing recruitment platform, inclusion filters, and repeat-exposure policy as part of the benchmark contract rather than leaving them implicit.


84. `RS-GR-061`  
   [Smyth et al. (2023), *Cooperation in indefinite games: Evidence from red queen effects and finite horizon framing*](https://www.sciencedirect.com/science/article/pii/S0167268123000355)  
   Relevance: cooperation is more likely in indefinite games with a longer expected horizon, and the paper reports that indefiniteness itself matters rather than raw length alone, which supports publishing the horizon regime instead of treating all repeated-interaction lanes as equivalent.

85. `RS-GR-062`  
   [Mengel (2022), *Match length realization and cooperation in indefinitely repeated games*](https://www.sciencedirect.com/science/article/pii/S0022053122000060)  
   Relevance: the realized length of early matches in indefinitely repeated Prisoner's Dilemma materially affects later cooperation, which supports publishing stopping-rule details and whether results are pooled across realized horizon histories.

86. `RS-GR-063`  
   [Xie et al. (2026), *M3-BENCH: Process-Aware Evaluation of LLM Agents Social Behaviors in Mixed-Motive Games*](https://arxiv.org/abs/2601.08462)  
   Relevance: outcome-only mixed-motive evaluations can miss important failure modes because some models reach superficially reasonable behavioral outcomes while showing inconsistent reasoning and communication, which supports publishing whether a benchmark is process-aware and what trace channels it actually scores.

87. `RS-GR-064`  
   [Poelitz et al. (2026), *A Benchmark to Assess Common Ground in Human-AI Collaboration*](https://arxiv.org/abs/2602.21337)  
   Relevance: effective collaboration depends on common ground, situation awareness, referential coordination, and repair, and the benchmark reveals clear human-AI divergences on those process dimensions, which supports publishing grounding / repair metrics rather than relying on end-task success alone.

88. `RS-GR-065`  
   [Luo et al. (2026), *HAI-Eval: Measuring Human-AI Synergy in Collaborative Coding*](https://openreview.net/forum?id=pKqt8psClA)  
   Relevance: collaboration quality changes across explicitly different human-intervention levels, which supports publishing the intervention regime and final-action authority instead of treating one control split as the universal benchmark lane.

89. `RS-GR-066`  
   [Lai et al. (2022), *Human-AI Collaboration via Conditional Delegation: A Case Study of Content Moderation*](https://arxiv.org/abs/2204.11788)  
   Relevance: conditional delegation is a distinct collaboration contract in which humans specify trusted regions for model action, which supports publishing delegation policy and override boundaries rather than collapsing them into a generic human-AI score.

90. `RS-GR-067`  
   [Li et al. (2025), *Systematic Failures in Collective Reasoning under Distributed Information in Multi-Agent LLMs*](https://arxiv.org/abs/2505.11556)  
   Relevance: multi-agent LLMs perform much worse when task-relevant facts are distributed across agents than when full information is centrally available, and the failure arises from not surfacing hidden information rather than from an inability to integrate it once disclosed, which supports publishing the information-asymmetry regime rather than treating it as invisible benchmark plumbing.

91. `RS-GR-068`  
   [Poelitz et al. (2026), *A Benchmark to Assess Common Ground in Human-AI Collaboration*](https://arxiv.org/abs/2602.21337)  
   Relevance: the benchmark explicitly varies conditions of situation awareness and shows that common-ground tracking and repair are central to human-AI collaboration, which supports publishing shared/private visibility, awareness conditions, and history-window rules instead of pooling them into one headline cooperation score.


92. `RS-GR-069`  
   [Jiang et al. (2025), *Humans learn to prefer trustworthy AI over human partners*](https://arxiv.org/abs/2507.13524)  
   Relevance: human judgments about AI partners change with repeated exposure and disclosure because people learn about partner-type behavior over time, which supports publishing familiarization and repeat-exposure protocol instead of treating a post-learning lane as the same benchmark as a cold-start interaction.

93. `RS-GR-070`  
   [Kang et al. (2025), *Moving Out: Physically-grounded Human-AI Collaboration*](https://arxiv.org/abs/2507.18623)  
   Relevance: the benchmark makes adaptation to diverse human behaviors and unseen physical attributes a first-class evaluation target, which supports publishing whether collaboration was measured cold, after practice, or under an explicitly adaptive regime rather than collapsing those conditions into one headline cooperation score.

94. `RS-GR-071`  
   [Kappes et al. (2025), *How Relational Context Matters for Human-AI Cooperation Within Organizations*](https://doi.org/10.1093/9780198945215.003.0094)  
   Relevance: humans apply different cooperative norms to AI across relationship types such as teammate and boss/employee, which supports publishing role context and seat assignment rather than treating all cooperation lanes as normatively interchangeable.

95. `RS-GR-072`  
   [Chappidi et al. (2026), *Who Does What? Archetypes of Roles Assigned to LLMs During Human-AI Decision-Making*](https://doi.org/10.1145/3772318.3791428)  
   Relevance: changing the human-LLM role archetype, decision control split, or social hierarchy can materially change outputs and decisions, which supports publishing role taxonomy and seat assignment as benchmark-contract metadata rather than hidden deployment context.

96. `RS-GR-073`  
   [Gonzalez et al. (2026), *Toward a science of human–AI teaming for decision-making: A complementarity framework*](https://doi.org/10.1093/pnasnexus/pgag030)  
   Relevance: effective human-AI teams depend on partitioning roles, shared mental models, trust calibration, training, and task structure, which supports treating role partition and seat-specific evaluation as first-class collaboration metadata rather than implementation detail.

97. `RS-GR-074`  
   [Sokol et al. (2025), *BenchmarkCards: Standardized Documentation for Large Language Model Benchmarks*](https://openreview.net/forum?id=b2IJBWhGFu)  
   Relevance: benchmark documentation should standardize objectives, methodologies, data sources, and limitations so benchmark users can avoid misuse and misinterpretation, which supports treating cooperation benchmark cards as claim-boundary objects rather than decorative metadata.

98. `RS-GR-075`  
   [Navarro et al. (2025), *A Conceptual Framework for AI Capability Evaluations*](https://arxiv.org/abs/2506.18213)  
   Relevance: evaluation interpretation depends on the objective, task specification, evaluated subject, and operational context, which supports publishing the precise comparison a cooperation card is meant to license instead of treating one score as universally comparable.

99. `RS-GR-076`  
   [Keller et al. (2026), *Expanding the AI Evaluation Toolbox with Statistical Models*](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-3.pdf)  
   Relevance: common benchmark reporting can conflate different notions of performance and uncertainty, which supports publishing what a cooperation benchmark comparison is actually claiming rather than letting one aggregate score stand in for several distinct performance questions.

100. `RS-GR-077`  
   [Holmes, Seger & Raji (2026), *Making AI Evaluation Deployment-Relevant Through Context Specification*](https://arxiv.org/abs/2603.06811)  
   Relevance: evaluation design should translate stakeholder priorities into explicit evaluable constructs and indicators tied to a specific use context, which supports publishing the scored unit, pooling rule, and primary estimand rather than treating a top-line cooperation score as self-explanatory.


101. `RS-GR-078`  
   [Longjohn et al. (2024), *Benchmark Data Repositories for Better Benchmarking*](https://openreview.net/forum?id=YktwH3tOuc)  
   Relevance: benchmarked metrics shown without uncertainty can invite fallacious model-comparison conclusions, and benchmark infrastructure can help by enforcing uncertainty reporting alongside point estimates.

102. `RS-GR-079`  
   [Billot et al. (2024), *How should a cluster randomized trial be analyzed?*](https://pmc.ncbi.nlm.nih.gov/articles/PMC7616648/)  
   Relevance: when outcomes are correlated within clusters, analyses must account for that dependence to avoid incorrect inference, which supports publishing the effective inference unit for repeated-turn, repeated-episode, or repeated-partner cooperation results.


103. `RS-GR-080`  
   [Polo et al. (2024), *Efficient multi-prompt evaluation of LLMs*](https://arxiv.org/abs/2405.17202)  
   Relevance: performance can vary across prompt variants and can be summarized over a prompt family rather than one template, which supports publishing variant family and selection policy instead of treating one chosen wrapper as the whole benchmark.

104. `RS-GR-081`  
   [Alzahrani et al. (2024), *When Benchmarks are Targets: Revealing the Sensitivity of Large Language Model Leaderboards*](https://arxiv.org/abs/2402.01781)  
   Relevance: minor benchmark perturbations such as answer order and scoring method can shift leaderboard rankings substantially, which supports treating wrapper and scoring choices as benchmark-contract metadata rather than invisible plumbing.

105. `RS-GR-082`  
   [Singh et al. (2025), *The Leaderboard Illusion*](https://arxiv.org/abs/2504.20879)  
   Relevance: undisclosed private testing of multiple variants and selective disclosure can bias benchmark results upward, which supports publishing search budget and test-touch policy whenever one retained result was chosen from a wider variant family.

106. `RS-GR-083`  
   [Keller et al. (2026), *Practices for Automated Benchmark Evaluations of Language Models*](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf)  
   Relevance: automated benchmark evaluations should define their measurement target, share key protocol details, and report qualified claims, which supports publishing failure-handling and denominator policy rather than letting exclusions and repairs remain implicit.

107. `RS-GR-084`  
   [Chalamalasetti et al. (2025), *clem:todd: A Framework for the Systematic Benchmarking of LLM-Based Task-Oriented Dialogue System Realisations*](https://aclanthology.org/2025.sigdial-1.5/)  
   Relevance: invalid outputs, parsing errors, and task-execution failures are common enough in structured LLM evaluation to materially affect reported scores, which supports publishing a failure taxonomy instead of assuming all launched attempts are valid observations.

108. `RS-GR-085`  
   [Gleim et al. (2026), *Benchmarking Large Language Models on Reference Extraction and Parsing in the Social Sciences and Humanities*](https://arxiv.org/abs/2603.13651)  
   Relevance: benchmark scores can depend on an explicit retry rule and on whether invalid outputs are counted as failures, which supports publishing retry / repair budget and scored denominator alongside the main metric.

109. `RS-GR-086`  
   [Bell et al. (2025), *AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions*](https://arxiv.org/abs/2506.09038)  
   Relevance: filtering invalid judge outputs changes the effective denominator of response-accuracy estimates, which supports publishing exclusion rules whenever failures or invalid judgments are removed before scoring.

110. `RS-GR-087`  
   [Gu et al. (2025), *A Survey on LLM-as-a-Judge*](https://arxiv.org/abs/2411.15594)  
   Relevance: LLM-as-a-Judge is a full evaluation pipeline spanning input design, context / prompt construction, model choice, and output post-processing, and reliable judge systems require careful design and standardization, which supports publishing judge provenance and rubric protocol instead of treating the evaluator as invisible.

111. `RS-GR-088`  
   [Shi et al. (2025), *Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge*](https://aclanthology.org/2025.ijcnlp-long.18/)  
   Relevance: judge outcomes can change systematically with answer position and prompt ordering, which supports publishing order-debiasing and adjudication rules rather than treating one prompt order as a neutral scoring surface.

112. `RS-GR-089`  
   [Jung, Brahman & Choi (2024), *Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement*](https://arxiv.org/abs/2407.18370)  
   Relevance: confidence-aware escalation and selective abstention can materially improve agreement with human judgment, which supports publishing whether uncertain cases were escalated, abstained on, or force-scored inside the benchmark.

113. `RS-GR-090`  
   [Li et al. (2025), *Evaluating Scoring Bias in LLM-as-a-Judge*](https://arxiv.org/abs/2506.22316)  
   Relevance: scoring-only judge outputs can shift under rubric-order, score-ID, and reference-answer perturbations, which supports publishing rubric / scoring protocol rather than treating the scoring prompt as a harmless wrapper around the same evaluation.

114. `RS-GR-091`  
   [Zhou, Savova & Wang (2025), *Assessing the Macro and Micro Effects of Random Seeds on Fine-Tuning Large Language Models*](https://aclanthology.org/2025.ijcnlp-short.3/)  
   Relevance: benchmark outcomes can vary materially across random seeds at both aggregate and item levels, which supports publishing the actual seed set and any reroll policy rather than letting one bundle stand in for the whole evaluation object.

115. `RS-GR-092`  
   [Reuel et al. (2024), *BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices*](https://arxiv.org/abs/2411.12990)  
   Relevance: many popular benchmarks still do not make replication easy, which supports publishing scenario family and randomization policy explicitly rather than leaving them as internal scaffolding.

116. `RS-GR-093`  
   [Ishida et al. (2025), *How Can I Publish My LLM Benchmark Without Giving the True Answers Away?*](https://arxiv.org/abs/2505.18102)  
   Relevance: public release, private held-out evaluation, and repeated-query exposure create different contamination and overfitting risks, which supports publishing the scored set's release posture instead of treating benchmark exposure as invisible context.

117. `RS-GR-094`  
   [Rademacher et al. (2026), *Guidelines for Empirical Studies in Software Engineering involving Large Language Models*](https://arxiv.org/abs/2508.15503)  
   Relevance: empirical LLM studies should report model versions, configurations, customizations, and tool architecture beyond the model, which supports publishing evaluated-subject provenance and serving-stack details rather than treating “the model” as self-explanatory.

118. `RS-GR-095`  
   [Chauvin et al. (2025), *Log Probability Tracking of LLM APIs*](https://arxiv.org/abs/2512.03816)  
   Relevance: users rely on version-pinned API endpoints for consistency even though provider-side updates can remain largely unmonitored, which supports publishing evaluation windows and drift posture rather than assuming endpoint stability.

119. `RS-GR-096`  
   [Gringras (2026), *Safety Under Scaffolding: How Evaluation Conditions Shape Measured Safety*](https://arxiv.org/abs/2603.10044)  
   Relevance: deployment configuration and scaffold architecture can materially change measured benchmark outcomes, which supports publishing the serving / deployment stack and requiring per-model, per-configuration interpretation rather than collapsing them into one subject label.

120. `RS-GR-097`  
   [Zhang et al. (2026), *Real Money, Fake Models: Deceptive Model Claims in Shadow APIs*](https://arxiv.org/abs/2603.01919)  
   Relevance: unofficial compatible endpoints can diverge materially from the official models they claim to expose, which supports publishing endpoint provenance explicitly instead of treating any nominally matching API as the same evaluated subject.


121. `RS-GR-098`  
   [El Filali & Bedar (2026), *Towards More Standardized AI Evaluation: From Models to Agents*](https://arxiv.org/abs/2602.18029)  
   Relevance: evaluation pipelines shape outcomes through inputs, inference, grading logic, tool interfaces, and environment state, which supports publishing context / history policy and execution-budget settings instead of treating them as invisible harness details.

122. `RS-GR-099`  
   [Lu et al. (2026), *FinToolBench: Evaluating LLM Agents for Real-World Financial Tool Use*](https://arxiv.org/abs/2603.08262)  
   Relevance: reproducible agent evaluation can require an explicit fixed tool-use limit, per-call timeout, retry budget, deterministic caching, and full trace logging, which supports publishing turn / tool budget and limit-hit policy rather than hiding them in benchmark infrastructure.

123. `RS-GR-100`  
   [Li et al. (2026), *Benchmark Test-Time Scaling of General LLM Agents*](https://arxiv.org/abs/2602.18998)  
   Relevance: longer interaction histories do not monotonically improve agent performance and instead hit an effective context ceiling, which supports publishing history-retention and interaction-budget policy rather than assuming more turns are a neutral implementation detail.

124. `RS-GR-101`  
   [Fan et al. (2025), *SWE-Effi: Re-Evaluating Software AI Agent System Effectiveness Under Resource Constraints*](https://openreview.net/forum?id=x7C9A4Y9cF)  
   Relevance: agent effectiveness changes under token and time budgets, and expensive failures can consume excessive resources while stuck, which supports publishing compute / latency budget and timeout posture rather than treating them as irrelevant to benchmark interpretation.

125. `RS-GR-102`  
   [Ding et al. (2025), *Establishing Best Practices for Building Rigorous Agentic Benchmarks*](https://arxiv.org/abs/2507.02825)  
   Relevance: agentic benchmarks are defined by tasks in specific environments with given tool sets, so tool and environment setup belongs to benchmark validity and reporting rather than to invisible harness plumbing.

126. `RS-GR-103`  
   [Zhu et al. (2026), *The Necessity of a Unified Framework for LLM-Based Agent Evaluation*](https://arxiv.org/abs/2602.03238)  
   Relevance: current agent evaluations are confounded by toolset configurations and environmental dynamics, and lack of standardized environmental data makes results opaque and non-reproducible, which supports publishing environment and tool posture explicitly.

127. `RS-GR-104`  
   [Pysklo, Zhuravel & Watson (2026), *Agent-Diff: Benchmarking LLM Agents on Enterprise API Tasks via Code Execution with State-Diff-Based Evaluation*](https://arxiv.org/abs/2602.11224)  
   Relevance: agent performance varies with external tool access, and reproducible evaluation can require a sandbox that instantiates the environment identically across runs, which supports publishing tool-access and state-snapshot policy rather than treating them as hidden scaffolding.

128. `RS-GR-105`  
   [Wang et al. (2026), *Cloud-OpsBench: A Reproducible Benchmark for Agentic Root Cause Analysis in Cloud Systems*](https://arxiv.org/abs/2603.00468)  
   Relevance: a state-snapshot paradigm that freezes the operational context into an immutable persistence layer can turn a dynamic environment into a reproducible evaluation object, which supports publishing whether the benchmark used live state or frozen snapshots.

129. `RS-GR-106`  
   [Shi et al. (2026), *τ-Knowledge: Evaluating Conversational Agents over Unstructured Knowledge*](https://arxiv.org/abs/2603.04370)  
   Relevance: knowledge-grounded agent performance can depend on the accessible corpus and on retrieval configuration details such as reranking, grep access, and write-tool permissions, which supports publishing corpus provenance and retrieval/tool policy rather than hiding them behind one top-line score.

130. `RS-GR-107`  
   [Zhang et al. (2024), *ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities*](https://arxiv.org/abs/2408.04682)  
   Relevance: adding distraction tools or perturbing tool descriptions can materially change agent scores, which supports publishing the actual tool surface and access policy instead of treating it as a neutral implementation detail.


131. `RS-GR-108`  
   [Hopewell et al. (2025), *CONSORT 2025 statement: Updated guideline for reporting randomised trials*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11996237/)  
   Relevance: updated reporting guidance requires prespecified primary and secondary outcomes together with the measurement variable, analysis metric, aggregation method, time point, and disclosure of non-prespecified outcomes or analyses, which supports publishing the governing cooperation metric rather than letting it drift after inspection.

132. `RS-GR-109`  
   [Bishop (2023), *Using multiple outcomes in intervention studies: improving power while controlling type I errors*](https://pmc.ncbi.nlm.nih.gov/articles/PMC10011751/)  
   Relevance: multiple outcomes can be legitimate, but the criterion for success over the outcome family must be specified in a way that controls false positives, which supports publishing multiplicity / metric-selection policy rather than promoting one convenient cooperation metric after the fact.

133. `RS-GR-110`  
   [Stringer et al. (2024), *The analysis and reporting of multiple outcomes in mental health trials: a methodological systematic review*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11662570/)  
   Relevance: recent empirical review finds that explicit strategies for incorporating multiple outcomes into a primary analysis are uncommon, which supports treating metric governance as a first-class benchmark-card field rather than assuming the headline metric is self-justifying.

134. `RS-GR-111`  
   [Sokol et al. (2025), *BenchmarkCards: Standardized Documentation for Large Language Model Benchmarks*](https://openreview.net/forum?id=b2IJBWhGFu)  
   Relevance: BenchmarkCards argues benchmark documentation should follow a standardized structure over objectives, methodologies, data sources, and limitations, which supports shipping one fixed machine-checkable cooperation card rather than leaving future inheritors to reconstruct the object from prose.

135. `RS-GR-112`  
   [Reuel et al. (2024), *BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices*](https://arxiv.org/abs/2411.12990)  
   Relevance: many widely used benchmarks still do not make their results easy to replicate, which supports shipping one compact validated card artifact and worked example rather than only narrative guidance about what should be recorded.

136. `RS-GR-113`  
   [Chmielinski et al. (2024), *The CLeAR Documentation Framework for AI Transparency*](https://shorensteincenter.org/wp-content/uploads/2024/05/CleAR_KChmielinski_FINAL.pdf)  
   Relevance: documentation should be comparable by following a discrete, well-defined format in process, content, and presentation, which supports using one compact schema-backed card object rather than free-form benchmark prose alone.
137. `RS-GR-114`  
   [Wilkinson et al. (2016), *The FAIR Guiding Principles for scientific data management and stewardship*](https://www.nature.com/articles/sdata201618)  
   Relevance: FAIR explicitly emphasizes machine-actionable metadata that computational systems can find, access, interoperate with, and reuse, which supports keeping compact cooperation cards not only schema-valid but also easy to scaffold and render consistently for future inheritors.

138. `RS-GR-115`  
   [Batista et al. (2022), *Machine actionable metadata models*](https://www.nature.com/articles/s41597-022-01707-6)  
   Relevance: standards-driven metadata templates benefit from quantitative and verifiable measures of whether descriptors meet community reporting requirements, which supports a compact readiness lint over schema-backed cooperation cards rather than assuming structural validity is enough.

139. `RS-GR-116`  
   [Maiorano (2026), *Automated Self-Testing as a Quality Gate: Evidence-Driven Release Management for LLM Applications*](https://arxiv.org/abs/2603.15676)  
   Relevance: evidence-based quality gates can turn raw test evidence into explicit promote/hold decisions, which supports keeping a small local claim-readiness gate for compact cooperation cards instead of treating any valid draft as publication-ready.

140. `RS-GR-117`  
   [Soiland-Reyes et al. (2022), *Packaging research artefacts with RO-Crate*](https://www.researchobject.org/2021-packaging-research-artefacts-with-ro-crate/manuscript.html)  
   Relevance: lightweight machine-readable packaging with explicit relations between constituent artefacts supports tiny structured receipts that bind benchmark-card objects together without retaining bulky bundles.

141. `RS-GR-118`  
   [Leo et al. (2024), *Recording provenance of workflow runs with RO-Crate*](https://arxiv.org/abs/2312.07852)  
   Relevance: interoperable provenance records that bundle execution context and support comparison across heterogeneous systems reinforce the value of keeping compact receipts for benchmark-card lifecycle transitions.

142. `RS-GR-119`  
   [Ojewale et al. (2026), *Audit Trails for Accountability in Large Language Models*](https://arxiv.org/abs/2601.20727)  
   Relevance: audit trails should let reviewers reconstruct what changed, when, and under what governance context, which supports retaining one canonical machine-checkable delta receipt between claim-ready benchmark-card versions.

143. `RS-GR-120`  
   [Klyman et al. (2026), *Measuring What Matters: The AI Pluralism Index*](https://arxiv.org/abs/2510.08193)  
   Relevance: transparency indicators give credit to documentation that includes update history and version-linked release notes, which supports treating benchmark-card changes as explicit retained artefacts rather than silent overwrites.

144. `RS-GR-121`  
   [Davis et al. (2026), *AgentHub: A Registry for Discoverable, Verifiable, and Reproducible AI Agents*](https://arxiv.org/abs/2510.03495)  
   Relevance: lifecycle transparency improves when governance and evidence signals move into machine-checkable contracts, which supports classifying benchmark-card deltas explicitly instead of burying them in prose.

145. `RS-GR-122`  
   [GO FAIR, *FAIR Principles*](https://www.go-fair.org/fair-principles/)  
   Relevance: FAIR states that metadata should be assigned globally unique persistent identifiers and should explicitly include the identifier of the data they describe, which supports keeping retained example artifacts locally addressable rather than leaving identity implicit.

146. `RS-GR-123`  
   [Research Object Crate (RO-Crate) 1.2, *Metadata of the RO-Crate* and *Profiles*](https://www.researchobject.org/ro-crate/specification/1.2/metadata.html)  
   Relevance: RO-Crate requires entities to expose identifiers and treats profiles as a way to make structured content reliably consumable, which supports using stable explicit-or-surrogate identities for retained example JSON objects even when their schemas differ.


147. `RS-GR-124`  
   [GO FAIR, *F4: (Meta)data are registered or indexed in a searchable resource*](https://www.go-fair.org/fair-principles/f4-metadata-registered-indexed-searchable-resource/)  
   Relevance: FAIR treats indexing in a searchable resource as part of findability, which supports keeping a compact local inventory over retained cooperation cards and receipts rather than leaving lineage implicit.

148. `RS-GR-125`  
   [W3C, *PROV-DM: The PROV Data Model*](https://www.w3.org/TR/prov-dm/)  
   Relevance: PROV models provenance as entities, activities, and their relations, which supports retaining one compact lineage register that says how cards and receipts relate rather than leaving those relations to memory.

149. `RS-GR-126`  
   [W3C, *PROV-DM: Alternate Entities*](https://www.w3.org/TR/prov-dm/#term-alternate)  
   Relevance: PROV distinguishes alternate and specialized entities that capture different aspects or versions of the same thing, which supports treating multiple retained card tips in one lineage as related-but-distinct provenance objects rather than as one implicit current card.

150. `RS-GR-127`  
   [Research Object Crate (RO-Crate) 1.2, *Profiles*](https://www.researchobject.org/ro-crate/specification/1.2/profiles.html)  
   Relevance: explicit profiles and expected properties improve reliable programmatic consumption, which supports a small generated head register that says which retained card tips are operational versus citation-ready instead of leaving that interpretation to ad hoc reading.


151. `RS-GR-128`  
   [Wang et al. (2025), *When Experimental Economics Meets Large Language Models: Tactics with Evidence*](https://arxiv.org/abs/2505.21371)  
   Relevance: LLM experiments should carry the same payment-rule clarity expected in human experiments, and the authors find that stake-size changes can move measured rationality, which supports publishing incentive instructions and payoff scaling in LLM benchmark cards rather than treating them as hidden prompt detail.

152. `RS-GR-129`  
   [Gächter et al. (2024), *The role of payoff parameters for cooperation in the one-shot Prisoner's Dilemma*](https://doi.org/10.1016/j.euroecorev.2024.104753)  
   Relevance: cooperation changes with material payoff parameters, especially the gain from mutual cooperation over mutual defection, which supports publishing the actual payoff matrix and scaling instead of assuming payoff-preserving rewrites are behaviorally neutral.

153. `RS-GR-130`  
   [Huynh et al. (2026), *More at Stake: How Payoff and Language Shape LLM Agent Strategies in Cooperation Dilemmas*](https://arxiv.org/abs/2601.19082)  
   Relevance: repeated-dilemma LLM behavior shifts with payoff magnitude and language context, which supports publishing both reward scale and incentive framing whenever cooperation claims are compared across LLM lanes.

154. `RS-GR-131`  
   [W3C Provenance XG (2010), *Overview of Provenance on the Web*](https://www.w3.org/2005/Incubator/prov/wiki/images/0/02/Provenance-XG-Overview.pdf)  
   Relevance: the W3C provenance overview treats end-user provenance consumption as a problem of abstraction, multiple levels of description, and summary, which supports giving inheritors one tiny focus-lineage digest rather than forcing them to reconstruct their first inspection target from several compact-card reports.


155. `RS-GR-132`  
   [Izquierdo, Izquierdo & Boyd (2026), *Successful strategies in the voluntarily repeated Prisoner's Dilemma*](https://doi.org/10.64898/2026.01.16.699891)  
   Relevance: with substantial error, frequent strategy introduction, and the option to leave, classical retaliatory winners such as Grim, Tit-for-Tat, and Win-Stay-Lose-Shift can disappear and be replaced by leave-based sanctioning, which supports treating noisy voluntary separation as its own benchmark family rather than assuming fixed-dyad winners transfer automatically.

156. `RS-GR-133`  
   [LaPorte, Pracher & Pal (2026), *From simultaneous to leader–follower play in direct reciprocity*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12880187/)  
   Relevance: move order and current-action visibility can preserve some simple memory-1 equilibria yet destabilize richer equilibria, which supports publishing sequential-vs-simultaneous timing and commitment visibility as explicit world-contract metadata rather than treating them as harmless interface detail.

157. `RS-GR-134`  
   [Barclay (2025), *Partner choice increases observed reciprocity-based cooperation but decreases unobserved stake-based cooperation*](https://pubmed.ncbi.nlm.nih.gov/41307066/)  
   Relevance: partner choice can shift incentives toward visible, reputation-relevant helping while reducing hidden partner-maintenance help, which supports separating observed-help metrics from unobserved-care metrics rather than treating all cooperation as one scalar.

158. `RS-GR-135`  
   [Okada & De Silva (2024), *Norms prioritizing positive assessments are likely to maintain cooperation in private indirect reciprocity*](https://www.nature.com/articles/s41598-024-67773-5)  
   Relevance: under private assessment, whether cooperation survives depends materially on the image-update priority rule, which supports publishing assessment/update semantics explicitly rather than treating reputation as a binary world toggle.


159. `RS-GR-136`  
   [Kim & Murase (2026), *Incomplete reputation information and punishment in indirect reciprocity*](https://www.nature.com/articles/s41598-026-42957-3)  
   Relevance: incomplete observation and reputation fading / `Unknown` states produce qualitatively different cooperation and punishment behavior, which supports treating sparse observation and fading reputation as separate world-contract fields rather than as one generic imperfect-information toggle.

160. `RS-GR-137`  
   [Quan et al. (2026), *Gossip promotes cooperation in indirect reciprocity with private reputation*](https://doi.org/10.1016/j.chaos.2025.117814)  
   Relevance: under private reputation, cooperation can depend materially on gossip cadence, trust weighting, and source aggregation, which supports publishing gossip diffusion and merge semantics explicitly rather than treating gossip as background plumbing.


161. `RS-GR-138`  
   [Baier & Jaber-Lopez (2025), *Just saying sorry—The effect of apologies on reintegration after social exclusion*](https://doi.org/10.1016/j.jebo.2025.107246)  
   Relevance: after exclusion, apology availability and trackability can change theft and reintegration behavior, which supports publishing rehabilitation / re-entry semantics explicitly rather than treating sanction worlds as defined by punishment alone.

162. `RS-GR-139`  
   [Yeo & Zhuo (2024), *The usage of apologies and group cooperation*](https://doi.org/10.1016/j.joep.2024.102755)  
   Relevance: apology channels can raise cooperation, with publicity and follow-through shaping the effect, which supports publishing repair-signal visibility and amends semantics explicitly rather than treating apologies as narrative-only chat.

163. `RS-GR-140`  
   [Correia da Fonseca et al. (2025), *Evolution of indirect reciprocity under emotion expression*](https://www.nature.com/articles/s41598-025-89588-8)  
   Relevance: expressive signals can act as communicative error-correction channels in indirect reciprocity, especially under frequent errors, which supports publishing repair-signal rights and no-signal baselines explicitly rather than attributing all gains to action policy alone.

164. `RS-GR-141`  
   [Yamamoto, Okada & Suzuki (2025), *Gradual reputation dynamics evolve and sustain cooperation in indirect reciprocity*](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0329742)  
   Relevance: cooperation can depend on whether reputations move through graded states such as `good`, `neutral`, and `bad` rather than binary flips, which supports publishing reputation alphabet and transition granularity explicitly rather than treating them as cosmetic score resolution.

165. `RS-GR-142`  
   [Bhaskar (2019), *Community Enforcement of Trust with Bounded Memory*](https://academic.oup.com/restud/article/86/3/1010/5090464)  
   Relevance: when misconduct records expire under bounded memory, visible proximity to rehabilitation can unravel temporary exclusion, which supports publishing record-retention windows and rehabilitation-legibility semantics explicitly rather than treating expiry as harmless archive hygiene.

166. `RS-GR-143`  
   [Pires & Santos (2025), *Artificial Agents Mitigate the Punishment Dilemma of Indirect Reciprocity*](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1650.pdf)  
   Relevance: in hybrid indirect-reciprocity populations, even simple fixed artificial agents can change reputation consensus and cooperation under private assessment, which supports publishing agent-type assessment rules explicitly rather than treating humans and artificial agents as norm-identical by default.

167. `RS-GR-144`  
   [Manoli, Pauketat & Anthis (2025), *The AI Double Standard: Humans Judge All AIs for the Actions of One*](https://doi.org/10.1145/3711083)  
   Relevance: one AI's moral transgression can spill over to perceptions of all AIs, which supports publishing whether reputational updates attach to individuals, model families, providers, or the whole AI category rather than leaving spillover scope implicit.

168. `RS-GR-145`  
   [Harrell et al. (2025), *Reputation-based reciprocity in human–bot and human–human networks*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12084833/)  
   Relevance: adding bots can weaken generosity and alter how humans evaluate helping toward both bots and other humans, which supports keeping human-only and hybrid reciprocity worlds separate and publishing cross-type help semantics explicitly.


169. `RS-GR-146`  
   [Wei et al. (2025), *Indirect reciprocity in the public goods game with collective reputations*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12311877/)  
   Relevance: once reputations attach to groups rather than only individuals, the collective-assessment criterion itself can destabilize or sustain cooperation, which supports publishing whether reputations are individual, collective, or dual-layer rather than treating group scope as harmless aggregation.

170. `RS-GR-147`  
   [Kawakatsu et al. (2024), *When do stereotypes undermine indirect reciprocity?*](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1011862)  
   Relevance: substituting group stereotypes for individual reputations can either help or harm cooperation depending on how information is shared, and stereotype use can become sticky under noise or access cost, which supports publishing stereotype fallback rights explicitly rather than treating them as a neutral cognitive shortcut.

171. `RS-GR-148`  
   [Tateishi et al. (2025), *Cooperation beyond group boundaries is evaluated differently depending on the existence of intergroup competition*](https://www.frontiersin.org/journals/behavioral-economics/articles/10.3389/frbhe.2025.1493427/full)  
   Relevance: universalistic cooperation toward outgroups is not always reputationally rewarded; under intergroup competition, ingroup-favoring actors can be judged more positively, which supports publishing boundary-competition semantics explicitly rather than assuming Golden-Rule-like universalism survives group rivalry by default.

172. `RS-GR-149`  
   [Gross et al. (2025), *Free mobility across group boundaries promotes intergroup cooperation*](https://www.nature.com/articles/s44271-025-00192-y)  
   Relevance: even limited cross-boundary mobility can let a minority of agents selectively enforce intergroup cooperation, which supports publishing who may observe, reward, punish, or rematch across boundaries rather than treating group mobility as a background detail.

173. `RS-GR-150`  
   [Murase & Hilbe (2024), *Indirect reciprocity under opinion synchronization*](https://doi.org/10.1073/pnas.2418364121)  
   Relevance: the stability of indirect reciprocity depends on how correlated individual opinions become, which supports publishing reputation synchronization / consensus topology explicitly rather than treating private-versus-public agreement as harmless backend plumbing.

174. `RS-GR-151`  
   [Cavaliere et al. (2024), *Cooperation and social organization depend on weighing private and public reputations*](https://doi.org/10.1038/s41598-024-67080-z)  
   Relevance: weighting public reputation heavily — especially when agents ingest both friend and enemy opinions — can generate polarization cycles, defector invasion, and fragmentation, which supports publishing source-weighting and public-versus-private reputation priority explicitly rather than treating them as implementation detail.

175. `RS-GR-152`  
   [Genevsky (2025), *Social credit scores reduce interpersonal cooperation and trust*](https://doi.org/10.1371/journal.pone.0335810)  
   Relevance: centralized scalar social-credit-style scores can lower trust, reduce cooperation, and harden bias against later contradictory behavior, which supports treating centralized-score governance as its own benchmark family rather than as a generic reputation baseline.


176. `RS-GR-153`  
   [Perret et al. (2026), *Disentangling trust from cooperation: Trust as reduced monitoring across social dilemmas*](https://arxiv.org/abs/2509.04143)  
   Relevance: when monitoring is costly, trust can function as reduced observation rather than as cooperation itself, which supports publishing monitoring rights / costs explicitly and separating trust metrics from cooperation metrics rather than treating observation as free background plumbing.

177. `RS-GR-154`  
   [Hoffmann, Kittel & Larsen (2021), *Information exchange in laboratory markets: competition, transfer costs, and the emergence of reputation*](https://pubmed.ncbi.nlm.nih.gov/33786011/)  
   Relevance: direct transfer costs and competitive disadvantage reduce information sharing even when sharing would improve trust and efficiency, which supports publishing evidence-transfer frictions explicitly rather than assuming reputation information diffuses freely.

178. `RS-GR-155`  
   [Hrkalovic, Dudzik & Hung (2025), *Partner perceptions during brief online interactions shape partner selection and cooperation*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11981216/)  
   Relevance: partner selection depends on both willingness / warmth and ability / competence, with task affordances changing which dimension matters most, which supports separating cooperative intent from cooperative capacity rather than scoring all help failures as one thing.

179. `RS-GR-156`  
   [Boyer & Chantland (2025), *Victims of Misfortune are Blamed for Imposing Costs on Others*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12417269/)  
   Relevance: help-seeking or misfortune can trigger blame and devaluation as a way to avoid costly helping while preserving a generous self-image, which supports publishing recipient-need / burden semantics explicitly rather than assuming needy agents are evaluated neutrally.


180. `RS-GR-157`  
   [Wibral (2015), *Identity changes and the efficiency of reputation systems*](https://doi.org/10.1007/s10683-014-9410-3)  
   Relevance: when agents can erase their rating profile and re-enter as apparently new, trust and trustworthiness both fall and newcomers become harder to trust, which supports publishing reset rights, newcomer priors, and identity-history linkage explicitly rather than treating account reset as harmless hygiene.

181. `RS-GR-158`  
   [Zhang et al. (2025), *Trust Attacks and Defense in the Social Internet of Things: Taxonomy and Simulation-Based Evaluation*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12737177/)  
   Relevance: whitewashing remains a standard trust-attack class in open dynamic trust systems, alongside collusion and on-off attacks, which supports treating cheap identity reset as a live benchmark design problem rather than as an obsolete platform quirk.

182. `RS-GR-159`  
   [Hoenow (2025), *Disclosing Group Members' Identities Reduces Cooperation in an Artefactual Public Goods Field Experiment*](https://doi.org/10.1007/s12110-025-09508-7)  
   Relevance: revealing who is present can reduce cooperation even when individual actions remain private, which supports separating actor identifiability from action visibility rather than collapsing both into one transparency field.

183. `RS-GR-160`  
   [Sampaio et al. (2023), *Effects of co-players' identity and reputation in the public goods game*](https://doi.org/10.1038/s41598-023-40730-4)  
   Relevance: identity cues can modulate the behavioral effect of the same reputation information, which supports publishing identity-cue type and timing explicitly rather than assuming reputation means the same thing across anonymous, named, or face-linked worlds.


184. `RS-GR-161`  
   [Wang et al. (2026), *The dynamics of cooperation in asymmetric public goods games*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12867639/)  
   Relevance: the effect of inequality on cooperation depends on whether asymmetry lies in endowments, productivity, and return structure, which supports publishing capability alignment and payoff technology explicitly rather than treating unequal starts as innocuous initialization.

185. `RS-GR-162`  
   [Drouvelis & Qiu (2025), *Luck-based versus merit-based income shifts fairness perceptions and promotes cooperation in a public goods game*](https://doi.org/10.1093/oep/gpaf033)  
   Relevance: merit-framed versus luck-framed inequality changes fairness perceptions and cooperative contributions, which supports publishing the source of inequality explicitly rather than treating all unequal-resource worlds as equivalent.

186. `RS-GR-163`  
   [Gilgen et al. (2025), *From principles to practice: distributive justice and the role of perceived inequality in reward allocation*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12738866/)  
   Relevance: allocations of limited goods jointly reflect merit, need, and equality principles, with respondent background and perceived inequality shifting the result, which supports publishing scarce-allocation rules explicitly rather than treating redistribution as a neutral post-processing step.

187. `RS-GR-164`  
   [Koster et al. (2025), *Deep reinforcement learning can promote sustainable human behaviour in a common-pool resource problem*](https://www.nature.com/articles/s41467-025-58043-7)  
   Relevance: allocation mechanisms and planner policies can sustain cooperation by conditioning generosity on available resources and sanctioning defectors, which supports treating planner authority and allocation policy as first-class world dials rather than background optimization.

188. `RS-GR-165`  
   [Cox & Stoddard (2024), *Inequality and the allocation of collective goods*](https://doi.org/10.1016/j.jebo.2024.02.009)  
   Relevance: third-party allocation can improve efficiency relative to automatic equal division, but inequality creates conflicting fairness ideals and weakens allocator effectiveness, which supports publishing allocator authority and distribution rule explicitly in scarce collective-good worlds.

189. `RS-GR-166`  
   [Mathew et al. (2025), *Metanorms generate stable yet adaptable normative social order in a politically decentralized society*](https://pubmed.ncbi.nlm.nih.gov/41537884/)  
   Relevance: enforcement worlds need explicit metanorm semantics because rules about how norms are interpreted, changed, and enforced can stabilize or adapt social order without centralized authority.

190. `RS-GR-167`  
   [Désilets et al. (2026), *Individuals adapt how they punish social norm violations through social observation*](https://pubmed.ncbi.nlm.nih.gov/41625464/)  
   Relevance: punishment style is socially learned across response types such as inaction, gossip, exclusion, and confrontation, which supports publishing enforcement-style learning rights rather than treating local punishment culture as fixed background.

191. `RS-GR-168`  
   [Kamei, Sharma & Walker (2025), *Collective sanction enforcement: New experimental evidence from two societies*](https://doi.org/10.1016/j.jebo.2025.107138)  
   Relevance: when multiple third parties observe a violation, failure to punish and anti-social punishment can themselves become sanction targets, but the effect is institution- and society-sensitive, which supports publishing higher-order sanction rules explicitly.

192. `RS-GR-169`  
   [Krügel et al. (2025), *How do higher-order punishment institutions shape cooperation and norm-enforcement?*](https://doi.org/10.1007/s11558-025-09594-3)  
   Relevance: oversight structure over punishers matters because fourth-party monitoring and electoral-style competition discipline third-party enforcement in different ways.

193. `RS-GR-170`  
   [Alam & Rai (2025), *Profitable third-party punishment destabilizes cooperation*](https://pubmed.ncbi.nlm.nih.gov/40828010/)  
   Relevance: paying punishers can reduce cooperation by making sanctions look self-interested, so monetized punishment should be treated as its own institution rather than as a neutral enforcement boost.

194. `RS-GR-171`  
   [Kamei & Tabero (2025), *Motivations behind peer-to-peer (Counter-)punishment in public goods games: An experiment*](https://doi.org/10.1016/j.econlet.2025.112598)  
   Relevance: when counter-punishment is possible, sanctioning effects can become modest and emotionally retaliatory, which supports publishing retaliation exposure and sanctioner protection explicitly.


195. `RS-GR-172`  
   [Goeschl & Soldà (2024), *(Un)Trustworthy pledges and cooperation in social dilemmas*](https://doi.org/10.1016/j.jebo.2024.04.031)  
   Relevance: non-binding public pledges help cooperation chiefly when others have reason to believe the pledger is trustworthy, which supports publishing pledge-stage semantics and trustworthiness context explicitly rather than treating preplay promises as a generic communication boost.

196. `RS-GR-173`  
   [Brenner, Zeviny & De Kwaadsteniet (2025), *Words are not wind - how public joint commitment and reputation solve the Prisoner's Dilemma*](https://www.sciencedirect.com/science/article/pii/S0096300325002565)  
   Relevance: commitment state can change how third parties evaluate the same cooperative or defective act, which supports publishing whether action scoring is conditional on prior commitment rather than assuming one norm fits both committed and uncommitted interactions.

197. `RS-GR-174`  
   [Tanaka et al. (2026), *Dishonesty of cheap reputation signaling in indirect reciprocity*](https://www.sciencedirect.com/science/article/pii/S1090513826000358)  
   Relevance: when reputation-facing signals are cheap, actors can use them dishonestly after ambiguous or norm-sensitive conduct, which supports publishing signal cost and no-signal baselines explicitly rather than treating all added communication as trustworthy repair.

198. `RS-GR-175`  
   [Ekström et al. (2025), *Making a promise increases the moral cost of lying: Evidence from Norway and the United States*](https://doi.org/10.1016/j.jebo.2025.106995)  
   Relevance: active promise-making can reduce dishonesty while passive trust cues do not replicate the effect, which supports separating active commitment acts from ambient trust language and publishing how much personal engagement a promise stage requires.

199. `RS-GR-176`  
   [Vesely & Wengström (2025), *Increased cooperation in stochastic social dilemmas: Can it be explained by risk sharing?*](https://doi.org/10.1016/j.socec.2024.102309)  
   Relevance: stochastic risk can increase cooperation without strong evidence that informal risk sharing is the operative mechanism, which supports publishing shock structure and payout-smoothing rights explicitly rather than reading every risk-induced cooperation gain as moral improvement.

200. `RS-GR-177`  
   [Krendelsberger et al. (2025), *Climate change, collective shocks, and intra-community cooperation*](https://doi.org/10.1016/j.worlddev.2025.106717)  
   Relevance: cooperation can respond differently to collective versus individual shocks in lab-in-the-field public-goods settings, which supports treating common-fate structure as a first-class world dial rather than as generic payoff noise.

201. `RS-GR-178`  
   [Lenel, Thampanishvong & Vakis (2020), *Formal insurance and solidarity. Experimental evidence from Cambodia*](https://doi.org/10.1016/j.jebo.2020.08.019)  
   Relevance: people reduce private support when recipients could have insured against their losses, which supports publishing formal-insurance availability and unused-protection semantics explicitly rather than assuming need is judged the same across fallback regimes.

202. `RS-GR-179`  
   [Coombs (2025), *Crowding out crowd support? Substitution between formal and informal insurance*](https://doi.org/10.1016/j.jpubeco.2025.105499)  
   Relevance: formal unemployment insurance can crowd out informal transfers only modestly on average, which supports treating formal fallback and informal solidarity as separable institutions rather than assuming one simply replaces the other.

203. `RS-GR-180`  
   [Rossetti, Hauser & Hilbe (2025), *Dynamics of cooperation in concurrent games*](https://www.nature.com/articles/s41467-025-56083-7)  
   Relevance: when people manage concurrent games, cooperation can fall relative to the single-game baseline in both same-partner and different-partner settings, which supports publishing partner-portfolio width and concurrency topology explicitly.

204. `RS-GR-181`  
   [Donahue et al. (2020), *Evolving cooperation in multichannel games*](https://www.nature.com/articles/s41467-020-17730-3)  
   Relevance: linked multichannel games can sustain cooperation in a lower-benefit lane by borrowing leverage from a higher-benefit lane, which supports publishing cross-lane linkage rights rather than treating domains as automatically independent.

205. `RS-GR-182`  
   [Reiter et al. (2018), *Crosstalk in concurrent repeated games impedes direct reciprocity and requires stronger levels of forgiveness*](https://www.nature.com/articles/s41467-017-02721-8)  
   Relevance: accidental spillovers across concurrent games can shrink cooperative basins and make strict retaliators fragile, which supports treating crosstalk and channel-specific memory as world-contract choices rather than as implementation noise.

206. `RS-GR-183`  
   [Brask et al. (2024), *Evolution of cooperation in networks with well-connected cooperators*](https://www.cambridge.org/core/journals/network-science/article/evolution-of-cooperation-in-networks-with-wellconnected-cooperators/6BB0827520995DF1F3D819A6AC453AF5)  
   Relevance: degree heterogeneity, assortativity, and the network positions of cooperators can materially change whether cooperation persists, which supports publishing encounter topology and hub / bridge occupancy explicitly rather than treating the graph as neutral background.

207. `RS-GR-184`  
   [Redhead et al. (2024), *Evidence of direct and indirect reciprocity in network-structured economic games*](https://www.nature.com/articles/s44271-024-00098-1)  
   Relevance: positive reciprocity, negative reciprocity, and punishment operate on real community networks rather than only in well-mixed abstractions, which supports treating encounter-network structure as part of the benchmark contract.

208. `RS-GR-185`  
   [Samu et al. (2025), *Cooperation is not rewarded by friendship, but generous and selfish students repel each other in social networks*](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0326564)  
   Relevance: dynamic networks may sustain cooperation through selective separation and repulsion rather than by rewarding prosociality with new ties, which supports publishing tie-dissolution and rewiring semantics explicitly.

209. `RS-GR-186`  
   [Cárdenas et al. (2026), *Trust and the dynamics of network formation*](https://www.cambridge.org/core/journals/network-science/article/trust-and-the-dynamics-of-network-formation/7D29B42379B83F78E387F819D9B6FEAB)  
   Relevance: homophily and prior acquaintanceship can shape network formation more strongly than measured reciprocal trust, which supports publishing similarity-based tie-formation rules rather than attributing cooperative clustering to trust alone.

210. `RS-GR-187`  
   [Kuper-Smith & Korn (2025), *Loss avoidance during social interactions*](https://www.nature.com/articles/s44271-025-00288-5)  
   Relevance: cooperation in social dilemmas can move because people are trying to avoid losses rather than because they value cooperation more, which supports publishing gain/loss sign structure explicitly rather than treating payoff sign as harmless framing.

211. `RS-GR-188`  
   [Schuch, Nhim & Richter (2025), *Coordinating on good and bad outcomes in threshold games – Evidence from an artefactual field experiment in Cambodia*](https://doi.org/10.1016/j.ecolecon.2025.108547)  
   Relevance: threshold cooperation is higher when the same coordination problem is framed as producing a public good rather than preventing a public bad, which supports publishing help-versus-harm semantics explicitly rather than treating them as wording.

212. `RS-GR-189`  
   [Egberts, Engel & Fairfield (2026), *Out of sight is out of mind? Experimentally testing a gradually materializing public bad*](https://doi.org/10.1016/j.joep.2026.102877)  
   Relevance: when collective harm materializes only gradually, participants become less cautious and respond mainly after their own payoff turns negative, which supports publishing harm latency and experiential visibility explicitly rather than treating delay as realism garnish.

213. `RS-GR-190`  
   [Carlsson, Ek & Lange (2025), *One bad apple spoils the barrel? Public good provision under threshold uncertainty*](https://doi.org/10.1007/s10683-024-09836-y)  
   Relevance: threshold uncertainty is especially damaging under weakest-link aggregation but not under summation in the same way, which supports publishing threshold certainty and aggregation technology explicitly rather than collapsing them into one generic public-goods world.



214. `RS-GR-191`  
   [Du et al. (2025), *Emergent cooperative decision-making in triadic Prisoner’s Dilemmas: Effects of incentives and information*](https://doi.org/10.1016/j.actpsy.2025.105439)  
   Relevance: triadic reciprocity is not a simple dyadic scaleup, because third-player position and information scope can materially change whether pairwise cooperation stabilizes.

215. `RS-GR-192`  
   [Kitakaji, Hizen & Ohnuma (2025), *Communication among selected members improves cooperation in a social dilemma*](https://doi.org/10.3389/frbhe.2025.1495995)  
   Relevance: letting only some members communicate can still raise cooperation, which supports publishing partial-voice / partial-representation rights explicitly rather than treating communication as all-or-none.

216. `RS-GR-193`  
   [Ball, Sarangi & Upadhyay (2025), *Coalitions Improve the Coordination and Provision of Public Goods: Theory and Experimental Evidence*](https://doi.org/10.1111/jpet.70037)  
   Relevance: a coalition-formation stage can sort agents by preferences and increase public-good provision, which supports treating coalition rights and preplay sorting as first-class world dials rather than as harmless setup.

217. `RS-GR-194`  
   [Xu, Zhang & Zheng (2025), *How to Select the Leader in a One-Shot Public Goods Game: Evidence from the Laboratory*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12024131/)  
   Relevance: leadership effects depend on the selection mechanism and signal credibility, which supports publishing representative-selection rules explicitly rather than assuming “leader present” is one stable institution.

218. `RS-GR-195`  
   [Malthouse et al. (2026), *The private solution trap in collective action problems across 34 nations*](https://www.pnas.org/doi/10.1073/pnas.2504632123)  
   Relevance: once agents can invest in private solutions instead of shared ones, support for public provision can unravel and inequality can widen, which supports publishing private-solution availability and access asymmetry explicitly rather than treating them as harmless extra actions.

219. `RS-GR-196`  
   [Lo Iacono et al. (2024), *The effect of trusting contexts in social dilemmas with collective and individual solutions*](https://www.nature.com/articles/s41598-024-77190-3)  
   Relevance: trust context can shift investment between collective and individual solutions without increasing free-riding, which supports treating public-versus-private solution mix as its own institutional dial rather than as a mere payoff detail.

220. `RS-GR-197`  
   [Mori, Hanaki & Kameda (2024), *An outside individual option increases optimism and facilitates collaboration when groups form flexibly*](https://www.nature.com/articles/s41467-024-49779-9)  
   Relevance: outside options can help collaboration when loner externality is limited and groups can form flexibly, which supports publishing group-formation flexibility and loner externality explicitly rather than treating all opt-out rights as one institution.

221. `RS-GR-198`  
   [Gross et al. (2020), *Self-reliance crowds out group cooperation and increases wealth inequality*](https://www.nature.com/articles/s41467-020-18896-6)  
   Relevance: self-reliance can reduce cooperation and amplify inequality when shared problems can be solved individually, which supports treating self-reliance availability and access asymmetry as first-class world-contract fields.

222. `RS-GR-199`  
   [Bénabou, Jaroszewicz & Loewenstein (2025), *It hurts to ask*](https://doi.org/10.1016/j.euroecorev.2024.104911)  
   Relevance: asking for help is itself a strategic stage with rejection risk; greater need can reduce asking, and unsolicited offers can both help and discourage future asking, which supports publishing need observability, ask rights, and unsolicited-offer rights explicitly.

223. `RS-GR-200`  
   [Jo, Xie & Carroll (2024), *Understanding and Balancing Trade-offs of Visibility in Support Requests*](https://doi.org/10.1145/3613905.3650978)  
   Relevance: support-request visibility has nontrivial trade-offs rather than being a uniformly good communication upgrade, which supports publishing request audience and visibility semantics explicitly.

224. `RS-GR-201`  
   [Jo, Xie & Carroll (2025), *Psychological Barriers and Facilitators in the Sharing Economy: Exploring Recognition, Visibility, Social Costs, Community Belonging, and Efficacies*](https://doi.org/10.1145/3711052)  
   Relevance: request visibility and recognition for asking can change the perceived social costs of help-seeking, which supports publishing request recognition and audience design explicitly rather than treating them as UI garnish.

225. `RS-GR-202`  
   [Burke, Sommerfeldt & Wang (2025), *To Ask or Not to Ask: The Effects of Broadly and Narrowly Adopted Peer-Recognition Systems on Help Seeking*](https://doi.org/10.1287/mnsc.2023.00318)  
   Relevance: help-seeking norms depend on who adopts the recognition system; broad adoption can legitimize asking while partial adoption can do the reverse, which supports publishing subgroup asymmetry in request visibility and recognition.

226. `RS-GR-203`  
   [Dal Bó, Foster & Putterman (2024), *The Democracy Effect: a weights-based estimation strategy*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12341851/)  
   Relevance: democratic selection can directly change cooperative behavior beyond mere self-selection into preferred rules, which supports publishing endogenous versus exogenous rule choice explicitly rather than treating rule selection as preplay ceremony.

227. `RS-GR-204`  
   [Guan et al. (2026), *Formal democratic sanction mechanisms address the social dilemma in public goods games: A Chinese experimental study*](https://doi.org/10.1016/j.econlet.2025.112717)  
   Relevance: voting scope and sanction design jointly affect contributions, which supports publishing whether sanction parameters are group-chosen, individually chosen, or externally fixed rather than treating “democratic punishment” as one stable institution.

228. `RS-GR-205`  
   [Bühren, Dannenberg & Händel (2025), *The demand for complete and incomplete punishment institutions to promote cooperation*](https://doi.org/10.1016/j.jebo.2025.107071)  
   Relevance: complete and subgroup-binding punishment institutions generate different demand patterns because subgroup coordination and participant cooperativeness matter, which supports publishing franchise and binding scope explicitly rather than treating institution adoption as all-or-nothing.

229. `RS-GR-206`  
   [Zhou et al. (2026), *Does democratic decision-making process enhance cooperation among children and adolescents? A large-scale lab-in-the-field experiment with students*](https://doi.org/10.1016/j.jebo.2025.107343)  
   Relevance: endogeneity is not a universal cooperation premium; imposed rules can outperform chosen ones in some populations, which supports treating democratic choice as an empirical world dial rather than as a guaranteed improvement.

230. `RS-GR-207`  
   [Halali & Perez (2025), *Binding the future boosts intergenerational sustainability*](https://www.nature.com/articles/s44168-025-00216-7)  
   Relevance: letting the current generation invest in a mechanism that constrains the next generation increased replenishment and sustainability across generations, which supports publishing successor-binding, lock duration, and escape/reversal semantics explicitly rather than treating them as intertemporal fine print.

231. `RS-GR-208`  
   [Swinkels, de Vette & Toom (2025), *Future design in the public policy process: giving a voice to future generations*](https://doi.org/10.1080/01442872.2025.2502678)  
   Relevance: future generations are absent as present stakeholders, and future design can help represent their interests in policymaking, which supports publishing proxy / guardian / future-person representation explicitly rather than treating present-time voice for future cohorts as narrative flavor.

232. `RS-GR-209`  
   [Guida, Klaser & Mittone (2025), *Building sustainable futures through soft institutional interventions in the climate change context: An intergenerational experiment*](https://doi.org/10.1016/j.futures.2024.103531)  
   Relevance: sustainable outcomes were hard to achieve through individual action alone without institutional actors, while institutionalized agencies offering soft intergenerational guidance could promote sustainable futures, which supports treating future-facing advisory bodies as real institutional dials rather than as storytelling garnish.

233. `RS-GR-210`  
   [Imada et al. (2025), *Ingroup favoritism and outgroup derogation in intergenerational cooperation*](https://www.nature.com/articles/s44271-025-00272-z)  
   Relevance: intergenerational cooperation depends on whether future beneficiaries are framed as ingroup or outgroup members, which supports publishing beneficiary social scope explicitly rather than assuming “future generations” is a socially neutral target.


234. `RS-GR-211`  
   [Law et al. (2025), *Mapping prescriptive beliefs on seventh generation stewardship and increasing the temporal scope of intergenerational concern*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12569012/)  
   Relevance: people do not treat all future beneficiaries as one flat target; concern, obligation, and collective-decision scope decline across generational distance, which supports publishing beneficiary horizon depth explicitly rather than treating “future generations” as a single morally neutral endpoint.

235. `RS-GR-212`  
   [Ajdukovic, Spiegelman & Sutan (2025), *Motivational levers for the preservation of an intergenerational common resource: An experiment*](https://doi.org/10.1016/j.ecolecon.2025.108523)  
   Relevance: explicit intertemporal community links can improve coordination in intergenerational resource dilemmas, which supports publishing cross-cohort linkage and continuity cues explicitly rather than treating them as harmless story flavor.

236. `RS-GR-213`  
   [Cutler et al. (2025), *Psychological interventions that decrease psychological distance or challenge system justification increase motivation to exert effort to mitigate climate change*](https://www.nature.com/articles/s44271-025-00332-4)  
   Relevance: reducing perceived psychological distance to climate harms can increase effortful pro-environmental behavior, which supports publishing temporal/social/geographic proximity framing explicitly rather than treating future-harm nearness as neutral messaging.

237. `RS-GR-214`  
   [Muradova et al. (2025), *Promoting Pro-environmental Beliefs and Behaviour: Choose-Your-Own Story Futuristic Climate Game*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11957362/)  
   Relevance: vivid future-self perspective-taking can raise empathy and discussion while producing mixed downstream action effects, which supports publishing future-imagination vividness and agency balance explicitly rather than treating all future-oriented perspective aids as equivalent cooperation boosters.

238. `RS-GR-215`  
   [Syropoulos, Law, Kraft-Todd & Young (2024), *Responsibility to future generations: A strategy for combatting climate change across political divides*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11590069/)  
   Relevance: responsibility to future generations appears widely endorsed and less tightly tied to ideology than some alternative climate-responsibility framings, which supports publishing future-duty framing explicitly rather than treating it as harmless rhetoric.

239. `RS-GR-216`  
   [Law et al. (2025), *Responsibility for future generations and climate change mitigation: A cross-national study of predictors of pro-environmentalism in Europe*](https://doi.org/10.1016/j.jenvp.2025.102729)  
   Relevance: future-generations responsibility and climate-responsibility framings are not behaviorally identical across countries, which supports publishing duty-frame semantics explicitly rather than collapsing them into one generic moral prompt.

240. `RS-GR-217`  
   [Law et al. (2025), *Mapping and Increasing Americans' Actual and Perceived Support for Initiatives Protecting Future Generations*](https://pubmed.ncbi.nlm.nih.gov/41267496/)  
   Relevance: support for future-generations institutions can be widespread yet underestimated, and norm-correction can raise support, which supports publishing support-visibility and pluralistic-ignorance semantics explicitly rather than treating coalition expectations as background noise.

241. `RS-GR-218`  
   [Syropoulos, Watkins, Goodwin & Markowitz (2023), *Disentangling the contributions of impact-oriented versus reputation-focused legacy motives on intergenerational concern and action*](https://doi.org/10.1016/j.jenvp.2023.102092)  
   Relevance: impact legacy and reputation legacy are distinct motivational pathways, and visibility changes their relation to action, which supports publishing legacy type and action observability explicitly rather than treating “legacy motivation” as one scalar knob.

242. `RS-GR-219`  
   [Syropoulos, Markowitz, Demarest & Shrum (2023), *A letter to future generations: Examining the effectiveness of an intergenerational framing intervention*](https://doi.org/10.1016/j.jenvp.2023.102074)  
   Relevance: intergenerational letter-writing can raise responsibility, intentions, and some immediate giving while decaying quickly over time, which supports publishing intervention durability and follow-up horizon explicitly rather than treating short-lived salience effects as durable cooperation gains.



243. `RS-GR-220`  
   [Bosone et al. (2026), *Acting together for a positive future: A cross-cultural investigation of how environmental cognitive alternatives and efficacy beliefs contribute to individual and collective biodiversity-conservation intentions*](https://doi.org/10.1016/j.futures.2025.103720)  
   Relevance: positive future imagination and collective efficacy are distinct future-facing levers, which supports publishing desirability, achievability, and efficacy semantics explicitly rather than treating them as one generic hope cue.

244. `RS-GR-221`  
   [Goldwert et al. (2026), *A megastudy of behavioral interventions to catalyze public, political, and financial climate advocacy*](https://doi.org/10.1093/pnasnexus/pgaf400)  
   Relevance: the strongest advocacy intervention paired collective efficacy with emotional benefits, which supports publishing agency and emotional-payoff semantics explicitly rather than treating future-action motivation as one undifferentiated frame.

245. `RS-GR-222`  
   [Bosone et al. (2025), *Visions of Tomorrow: Emotional drivers of climate change mitigation and adaptation intentions*](https://doi.org/10.1016/j.jenvp.2025.102700)  
   Relevance: utopian and dystopian future visions work through different positive-emotion pathways rather than through a simple direct effect, which supports publishing future-vision valence and emotional-channel semantics explicitly rather than treating them as harmless presentation choices.

246. `RS-GR-223`  
   [Veijonaho et al. (2025), *From distress to action? – A three-wave longitudinal study of climate change distress, pro-environmental behavior, and coping strategies among Finnish adolescents*](https://doi.org/10.1016/j.jenvp.2025.102676)  
   Relevance: future-facing distress can either suppress or mobilize later action depending on meaning-focused coping, which supports publishing distress-channeling and coping-scaffold semantics explicitly rather than treating worry as a monotone motivator.

247. `RS-GR-224`  
   [Nieminen et al. (2025), *Climate worry and mental health: the role of pro-environmental behavior and efficacy-based hope as coping strategies*](https://doi.org/10.1016/j.jenvp.2025.102828)  
   Relevance: action plus efficacy-based hope is psychologically different from action without hope, which supports publishing agency-support and wellbeing-follow-up semantics explicitly rather than treating future-facing action burdens as emotionally neutral.


248. `RS-GR-225`  
   [Bauer et al. (2026), *Concern for future generations predicts costly present-day prosociality and extraordinary altruism: A case study of organ donorship*](https://doi.org/10.1111/bjso.70070)  
   Relevance: concern for future generations can predict immediate costly helping rather than crowd it out, which supports publishing present-day sacrifice semantics explicitly rather than assuming future-facing concern is a fixed tradeoff against current prosociality.

249. `RS-GR-226`  
   [Citi & Im (2026), *Big dilemmas, little time: intergenerational climate justice and public support for deep decarbonisation*](https://doi.org/10.1080/09644016.2026.2633837)  
   Relevance: awareness of intergenerational climate justice shifts support for costly decarbonisation through willingness to accept greater near-term economic losses, which supports publishing present-sacrifice semantics explicitly rather than treating future-duty support as costless moral rhetoric.

250. `RS-GR-227`  
   [Hoyle & Rhodes (2025), *Explaining public support for net-zero climate policy instruments: Perceptions of distributive fairness under competing frames*](https://doi.org/10.1016/j.enpol.2025.114644)  
   Relevance: support depends strongly on distributive-fairness perceptions, especially expected impacts on future generations, low-income households, and rural communities, which supports publishing fairness reference groups explicitly rather than treating justice as one scalar label.

251. `RS-GR-228`  
   [Tapia, Sánchez Gassen & Lundgren (2025), *Scaling fairness: Balancing self-interest, community needs and societal justice for public acceptance of climate change mitigation policies in the Nordic Region*](https://doi.org/10.1016/j.envsci.2025.104185)  
   Relevance: support can depend more on household and local-community impacts than on abstract societal distributive justice, which supports publishing burden scale and fairness-to-whom semantics explicitly rather than treating all fairness talk as equivalent.

252. `RS-GR-229`  
   [Tsuji & Shen (2025), *Preferences for policies from the perspectives of different generations: Evidence from a stated choice experiment in Japan*](https://doi.org/10.1016/j.futures.2025.103676)  
   Relevance: taking the standpoint of children and grandchildren shifts policy preferences away from burdening future generations, which supports publishing descendant-specific beneficiary framing explicitly rather than treating all future-beneficiary prompts as equivalent.

253. `RS-GR-230`  
   [Hampton, Taylor & Whitmarsh (2025), *Parenting and climate change: assessing carbon capability in early parenthood*](https://doi.org/10.1007/s11111-025-00506-6)  
   Relevance: parenthood can increase concern and openness to action while also increasing current resource use and structural friction, which supports publishing caregiver-role activation and present-household-burden semantics explicitly rather than treating parent-framed future concern as a clean prosocial boost.

254. `RS-GR-231`  
   [Earl-Jones, Davison & Lucas (2025), *Heated discussions: youth-led dialogue with older generations reveals unwitting silences and shared feelings about climate change*](https://doi.org/10.1016/j.geoforum.2025.104391)  
   Relevance: structured cross-age dialogue can surface responsibility differences, empathy, and collaboration, which supports publishing dialogue leadership and reciprocity-of-voice semantics explicitly rather than treating intergenerational contact as neutral context.

255. `RS-GR-232`  
   [Lissillour et al. (2025), *Intergenerational transmission of sustainable consumption practices: Dyadic dynamics of green receptivity, subjective knowledge, peer conformity, and intra-family communication*](https://doi.org/10.1016/j.jenvman.2025.124754)  
   Relevance: sustainable behavior can transmit in both directions across generations and is amplified by communication quality and receptivity, which supports publishing bidirectional influence and communication-channel semantics explicitly rather than assuming older-to-younger moral instruction is the only pathway.

256. `RS-GR-233`  
   [Savino et al. (2025), *Intergenerational interventions and their impact on active aging: A systematic review*](https://doi.org/10.1016/j.inpsyc.2025.100142)  
   Relevance: intergenerational programs often improve mental health, social inclusion, community cohesion, and ageism reduction for both age groups, which supports publishing contact structure and anti-ageism side effects explicitly rather than treating intergenerational cooperation as purely payoff-driven.

257. `RS-GR-234`  
   [Swinkels, de Vette & Toom (2025), *Future design in the public policy process: giving a voice to future generations*](https://doi.org/10.1080/01442872.2025.2502678)  
   Relevance: future design can insert absent future interests into current policymaking, which supports publishing future-voice insertion and role semantics explicitly rather than treating them as facilitation garnish.

258. `RS-GR-235`  
   [Ogami, Kameyama & Tasaki (2025), *Future-Regarding Institutions Through a Legitimacy Lens*](https://doi.org/10.1177/14789299251359387)  
   Relevance: future-regarding institutions can operate through input, throughput, and output legitimacy — especially ex-ante accountability, transparency, inclusiveness, and openness — which supports publishing process-accountability semantics explicitly rather than treating future-voice institutions as symbolic add-ons.

259. `RS-GR-236`  
   [Guida, Klaser & Mittone (2025), *Building sustainable futures through soft institutional interventions in the climate change context: An intergenerational experiment*](https://doi.org/10.1016/j.futures.2024.103531)  
   Relevance: soft intergenerational advice from institutionalized agencies can improve sustainable outcomes even without hard enforcement, which supports publishing advisory-presence and enforcement-strength semantics explicitly rather than treating institutions as all-or-nothing coercive actors.

260. `RS-GR-237`  
   [Morgan, Crichton, MacCarrick, Stephenson & Harris Rimmer (2025), *Scoping Existing National Policy Recognition of Future Generations: Prospects for Future Global Climate Justice*](https://doi.org/10.1111/1758-5899.70007)  
   Relevance: many constitutions and policy documents mention future generations, which supports publishing whether a benchmark gives future beneficiaries only nominal recognition or an actual procedural voice rather than collapsing recognition and representation into one label.

261. `RS-GR-238`  
   [Adipudi, Kim & Biermann (2025), *The potential negative impact of the UNFCCC: An analysis of sectoral, geographical, and temporal problem shifts from climate policies and measures in 25 industrialized countries*](https://doi.org/10.1016/j.gloenvcha.2025.103075)  
   Relevance: climate policies can shift burdens across sectors, regions, and time and thereby intensify burdens for future generations, which supports publishing problem-shifting semantics explicitly rather than treating every green-looking policy as net future-protective.

262. `RS-GR-239`  
   [Sugawara (2025), *Transgenerational Projects and Entangled Domination: Revisiting Autonomy in Radioactive Waste Management*](https://pmc.ncbi.nlm.nih.gov/articles/PMC12370860/)  
   Relevance: long-term projects differ sharply in whether they require rolling successor maintenance or achieve passive safety with lower future dependency, which supports publishing maintenance-burden and passive-safety semantics explicitly rather than treating reversibility alone as the whole intergenerational contract.



263. `RS-GR-240`  
   [Rose, Newig & Jager (2025), *Does participatory governance help address long-term environmental problems? Conceptualization and evidence from 23 democracies*](https://doi.org/10.1080/01442872.2025.2528782)  
   Relevance: intensive deliberation matters more than simple stakeholder representation for long-term environmental problems, which supports publishing deliberative depth separately from seat counts or participant presence rather than treating participation as one scalar.

264. `RS-GR-241`  
   [Rose (2024), *Institutional Proxy Representatives of Future Generations: A Comparative Analysis of Types and Design Features*](https://doi.org/10.17645/pag.7745)  
   Relevance: future-generation proxies vary sharply in legal basis, policy-process access, and formal influence, and many can speak without having teeth when ignored, which supports publishing institutional powers separately from mere representation presence.

265. `RS-GR-242`  
   [Düvel, Mertens & Wiertz (2026), *The obligation to long-term governance: a philosophical analysis*](https://doi.org/10.1186/s13705-025-00560-w)  
   Relevance: long-term governance involves unknown unknowns, uncertainty about relevant values, and loss of control over time, which supports publishing value uncertainty and successor-control semantics explicitly rather than treating long-horizon policy as ordinary risk management.

266. `RS-GR-243`  
   [Brister, Rohwer & Weber (2026), *Value pluralism supports portfolio approaches in conservation*](https://doi.org/10.1007/s13280-026-02368-0)  
   Relevance: plural value settings can justify portfolio and laddered approaches that preserve more future options than a single optimized path, which supports publishing option-preserving plurality semantics explicitly rather than forcing one locked future objective.

267. `RS-GR-244`  
   [Barnfield (2025), *Policy discounting across and beyond the lifespan*](https://doi.org/10.1111/1475-6765.12719)  
   Relevance: policy support depends partly on whether benefits arrive within or beyond the actor's lifespan, which supports publishing own-lifetime payoff boundary semantics explicitly rather than treating all future-facing policies as one altruism test.

268. `RS-GR-245`  
   [Gazmararian (2025), *Valuing the Future: Changing Time Horizons and Policy Preferences*](https://doi.org/10.1007/s11109-024-09965-3)  
   Relevance: parenthood and descendant salience can lengthen time horizons and increase support for long-horizon policy, which supports publishing time-horizon activation explicitly rather than treating future-facing support as a fixed trait.

269. `RS-GR-246`  
   [Gupta et al. (2025), *Thresholds of significant harm at global level: The journey of the Earth Commission*](https://doi.org/10.1016/j.esg.2025.100263)  
   Relevance: long-horizon governance may require explicit significant-harm limits rather than only aggregate optimization, which supports publishing hard harm-floor semantics explicitly rather than treating future protection as a smooth welfare tradeoff.

270. `RS-GR-247`  
   [Paarlberg et al. (2025), *Exploring the use of adaptation tipping points: A systematic review of definitions, characteristics and applications*](https://doi.org/10.1016/j.envsci.2025.104211)  
   Relevance: adaptation tipping points come in multiple categories with different triggers and consequences, which supports publishing threshold type and trigger semantics explicitly rather than treating all revision points as one monitoring event.

271. `RS-GR-248`  
   [Zorita et al. (2025), *Extending from Adaptation to Resilience Pathways: Perspectives from the Conceptual Framework to Key Insights*](https://doi.org/10.1007/s00267-025-02115-3)  
   Relevance: thresholds and tipping points can function as decision points that trigger additional or alternative measures, which supports publishing review and switching rights explicitly rather than treating them as operational aftercare.

272. `RS-GR-249`  
   [Langendijk et al. (2025), *Supporting climate resilient development planning − a dynamic adaptive pathways based approach and an illustrative case from Cork City, Ireland*](https://doi.org/10.1016/j.gloenvcha.2025.103070)  
   Relevance: dynamic pathways planning can include target points and critical decisions over time, which supports publishing trigger ownership and pathway-switch semantics explicitly rather than treating future adaptation as a fixed plan.
273. `RS-GR-250`  
   [Beckman (2025), *Democratic Legitimacy and Decisions for the Future*](https://doi.org/10.1007/s11158-025-09717-y)  
   Relevance: future-oriented representation can be democratically legitimate through surrogate and non-electoral forms even without ordinary authorization by future persons, which supports publishing representative-claim legitimacy and mandate-origin semantics explicitly rather than assuming all future proxies are interchangeable.

274. `RS-GR-251`  
   [Byskov & Hyams (2022), *Who Should Represent Future Generations in Climate Planning?*](https://doi.org/10.1017/S0892679422000168)  
   Relevance: not all future-generation representatives are equally plausible; hypothetical acceptance, epistemic / experiential similarity, and motivation to act on behalf of future generations distinguish proxy candidates, which supports publishing representative-selection route and constituency logic explicitly rather than treating any future proxy as equivalent.

275. `RS-GR-252`  
   [OECD (2025), *Government at a Glance 2025*](https://doi.org/10.1787/0efd0bcd-en)  
   Relevance: cohort composition in representative institutions is systematically skewed — across OECD countries, under-40s were 34% of the voting-age population on average but only 22% of MPs in 2024 — which supports publishing age-balance and cohort-composition semantics explicitly rather than treating future voice as detached from present representational skew.

276. `RS-GR-253`  
   [Hebinck et al. (2025), *ETC ST Report 2025/1: Intergenerational justice and youth participation*](https://www.eionet.europa.eu/etcs/etc-st/products/etc-st-report-1-2025-intergenerational-justice-and-youth-participation)  
   Relevance: youth participation functions as future-oriented proxy voice only when participation is meaningful, diverse, institutionally supported, and tied to transparent feedback and accountability, which supports publishing proxy-constituency, inclusion, and support semantics explicitly rather than treating youth presence as self-justifying future representation.

277. `RS-GR-254`  
   [Heo & Joseph (2025), *The traps and pitfalls of anticipatory governance – Comparative cases of South Korea and the United Kingdom*](https://doi.org/10.1016/j.futures.2025.103707)  
   Relevance: anticipatory governance can degrade into fragmented implementation, short-term resilience talk, and inadequate capacity-building, which supports publishing continuity, implementation-fragmentation, and public-capacity semantics explicitly rather than treating foresight rhetoric as institutional endurance.

278. `RS-GR-255`  
   [Tõnurist & Orlik (2025), *Towards anticipatory governance guidelines for public sector organisations*](https://doi.org/10.1787/a5203d0b-en)  
   Relevance: endurance, structures / procedures, support from leadership, exchange of intelligence, and cross-political-cycle continuity are distinct ingredients of anticipatory governance, which supports publishing institutional-memory and continuity semantics explicitly rather than treating long-term orientation as a mission statement.

279. `RS-GR-256`  
   [OECD (2025), *Exploring New Frontiers in Citizen Participation in the Policy Cycle*](https://doi.org/10.1787/77f5098c-en)  
   Relevance: participation institutions differ by targeted role design, institutional anchors, one-off versus permanent status, and whether accountability loops force recommendations into debate or response, which supports publishing permanence, anchor, and input-routing semantics explicitly rather than treating participation as generic consultation.

280. `RS-GR-257`  
   [Scheer et al. (2025), *No easy way out: towards a framework concept of long-term governance*](https://doi.org/10.1186/s13705-025-00513-3)  
   Relevance: long-term governance is coherent and consistent policy-making across sectors, institutions, and temporal scales and is best understood as reflexive policy-making, which supports publishing cross-cycle coherence and reflexive-review semantics explicitly rather than treating long-horizon governance as static commitment.

281. `RS-GR-258`  
   [European Commission Representation in Malta (2026), *Commission presents first ever Strategy on Intergenerational Fairness*](https://malta.representation.ec.europa.eu/news/commission-presents-first-ever-strategy-intergenerational-fairness-2026-03-05_en)  
   Relevance: the strategy makes future-regarding policymaking operational through a youth check, foresight tools, an intergenerational fairness index, and a scheduled progress report, which supports publishing ex-ante future-impact checks and review cadence explicitly rather than treating long-term concern as a vague aspiration.

282. `RS-GR-259`  
   [Joint Research Centre (2026), *JRC science for intergenerational fairness*](https://joint-research-centre.ec.europa.eu/jrc-science-intergenerational-fairness_en)  
   Relevance: the JRC's Futures Balance tool is designed to make intergenerational fairness and long-term trade-offs explicit and comparable across time and dimensions, which supports publishing trade-off-accounting semantics explicitly rather than treating future consideration as a narrative gloss.

283. `RS-GR-260`  
   [Future Generations Commissioner for Wales (2026), *Monitoring and Assessing*](https://futuregenerations.wales/do/involvement/monitoring-and-assessing/)  
   Relevance: the Welsh model treats monitoring, assessment, periodic examination, and formal reporting as part of the intergenerational institution itself, which supports publishing scrutiny cadence and review-surface semantics explicitly rather than treating them as administrative aftercare.

284. `RS-GR-261`  
   [Audit Wales (2025), *Ten years on, the Well-being of Future Generations Act has increased prominence but is not driving the system-wide change that was intended*](https://www.audit.wales/news/ten-years-well-being-future-generations-act-has-increased-prominence-not-driving-system-wide)  
   Relevance: explicit future-generations legislation can still underperform when bodies give little explicit consideration to the act or lack the information needed to understand impact, which supports publishing assessment-quality and impact-understanding semantics explicitly rather than treating statutory future language as implementation success.

285. `RS-GR-262`  
   [OECD (2025), *Regulating for the future: OECD Regulatory Policy Outlook 2025*](https://www.oecd.org/en/publications/2025/04/oecd-regulatory-policy-outlook-2025_a754bf4c/full-report/regulating-for-the-future_e948d334.html)  
   Relevance: regulatory impact assessment should consider future developments and future innovation effects rather than only immediate consequences, which supports publishing future-impact-assessment semantics explicitly rather than treating ex-ante review as present-only accounting.

286. `RS-GR-263`  
   [Pizer & Prest (2025), *Circular A-4: Practical Advances in Discounting for Policy Decisions*](https://www.rff.org/publications/journal-articles/circular-a-4-practical-advances-in-discounting-for-policy-decisions/)  
   Relevance: changing discount guidance from a 3% to a 2% central real rate and related valuation methods can materially raise the weight placed on long-lived harms and benefits, which supports publishing discount-schedule and valuation-rule semantics explicitly rather than treating future-protective outputs as purely moral changes.

287. `RS-GR-264`  
   [Belfiori & Macera (2025), *Demographic changes and social discounting*](https://doi.org/10.1016/j.econlet.2025.112584)  
   Relevance: demographic transition changes the social discounting problem itself, which supports publishing demographic assumptions explicitly rather than treating long-horizon valuation as invariant across population structure.

288. `RS-GR-265`  
   [Tamai (2023), *The rate of discount on public investments with future bias in an altruistic overlapping generations model*](https://doi.org/10.1016/j.ejpoleco.2023.102416)  
   Relevance: the appropriate social discount rate depends on future bias and can shift optimal public investment, which supports publishing future-bias and valuation-rule semantics explicitly rather than treating policy outcomes as independent of the planner's discount architecture.

289. `RS-GR-266`  
   [Liebenberg (2026), *Recognizing future generations under the International Covenant on Economic, Social and Cultural Rights*](https://academic.oup.com/hrlr/article/26/1/ngaf052/8495057)  
   Relevance: argues that international human-rights law can recognize future generations as rights-holders under ICESCR, which supports publishing whether future beneficiaries are treated as interests, rights-holders, or something weaker rather than collapsing them into one generic future-facing label.

290. `RS-GR-267`  
   [Lozada & Çalı (2025), *From litigation to implementation: framing smart remedies in rights-based climate litigation*](https://ora.ox.ac.uk/objects/uuid%3Ae7324e65-d825-48f5-9897-07c93a6a880a)  
   Relevance: distinguishes implementation-forcing remedies, target-setting remedies, oversight mechanisms, and procedural-access remedies, which supports publishing remedy-route semantics explicitly rather than treating all future-facing legal victories as equivalent.

291. `RS-GR-268`  
   [UNEP (2025), *Global Climate Litigation Report: 2025 Status Review*](https://www.unep.org/resources/report/global-climate-litigation-report-2025-status-review)  
   Relevance: shows that climate litigation now spans dozens of jurisdictions and international / regional bodies, which supports treating standing, remedy design, and implementation follow-through as first-class institutional dials rather than edge-case legal garnish.

292. `RS-GR-269`  
   [Bodansky & Rajamani (2025), *A Blueprint for Rights-Based Climate Action*](https://verfassungsblog.de/inter-american-court-of-human-rights-advisory-opinion-climate/)  
   Relevance: summarizes the Inter-American Court's 2025 climate advisory opinion as pushing toward broad standing, adjusted evidentiary standards, procedural rights, and full reparation, which supports publishing standing / proof / remedy semantics explicitly rather than treating future protection as rhetorical recognition.

293. `RS-GR-270`  
   [Mayer & Wewerinke-Singh (2025), *The ICJ’s Advisory Opinion on Climate Change*](https://verfassungsblog.de/the-icj-advisory-opinion-on-climate-change/)  
   Relevance: explains that the ICJ treated climate obligations as legal and enforceable, tied due diligence to best available science, prevention, and precaution, and affirmed that failures can trigger state responsibility and reparations, which supports publishing enforceability and uncertainty-default semantics explicitly rather than treating them as background law.

294. `RS-GR-271`  
   [IISD (2026), *What Does the International Court of Justice Advisory Opinion on Climate Change Mean for Climate Adaptation?*](https://www.iisd.org/publications/brief/icj-advisory-opinion-climate-adaptation)  
   Relevance: frames best-available-science planning, precautionary and forward-looking measures, and timely due diligence against foreseeable harm as binding adaptation obligations, which supports publishing science-threshold and precaution-default semantics explicitly rather than treating future care as generic intent.

295. `RS-GR-272`  
   [OHCHR (2025), *UN experts commend Norway decision to postpone deep-sea mining licensing*](https://www.ohchr.org/en/press-releases/2025/12/un-experts-commend-norway-decision-postpone-deep-sea-mining-licensing)  
   Relevance: calls for a precautionary pause because significant and irreversible harm may coexist with uncertainty about prevention, including harm transmitted to future generations, which supports publishing when uncertainty blocks action and when it instead triggers earlier intervention.

296. `RS-GR-273`  
   [Zhao et al. (2025), *Time to strengthen the governance of new contaminants in the environment*](https://www.nature.com/articles/s41467-025-63217-4)  
   Relevance: highlights proactive prevention, long latency of many harms, and REACH's shift of the burden of proof for chemical safety onto manufacturers and importers, which supports publishing proof-burden semantics explicitly rather than treating late-detected harm as unavoidable background noise.


297. `RS-GR-274`  
   [Buhr, Miehe & Potthast (2025), *The concepts of irreversibility and reversibility in research on anthropogenic environmental change*](https://doi.org/10.1093/pnasnexus/pgae577)  
   Relevance: irreversibility depends on temporal and spatial scales and is often left undefined even when it directly shapes policy and ecosystem-management decisions, which supports publishing repairability / reversibility semantics explicitly rather than treating future harm as a binary label.

298. `RS-GR-275`  
   [Kørnøv et al. (2025), *Beyond compliance: Enhancing biodiversity through transformative mitigation strategies in spatial planning related SEAs and EIAs*](https://www.sciencedirect.com/science/article/pii/S019592552500157X)  
   Relevance: argues for strengthening avoidance and adding proactive enhancement in SEA / EIA rather than relying on reactive mitigation, which supports publishing harm-ordering semantics explicitly rather than treating all mitigation steps as equivalent.

299. `RS-GR-276`  
   [Ghijselinck et al. (2026), *Beyond compliance: Strengthening mitigation hierarchy implementation in environmental impact assessment practice*](https://www.sciencedirect.com/science/article/pii/S0195925525003312)  
   Relevance: finds limited avoidance, weak remediation, semantic ambiguity, and limited substitutability in real-world EIA practice and proposes principles that prioritize avoidance, which supports publishing substitutability and mitigation-sequencing semantics explicitly rather than treating compensation as an interchangeable repair move.

300. `RS-GR-277`  
   [Soininen et al. (2025), *Ecological restoration hierarchy as a lens to reveal the foundational economic and legal structures impeding restoration*](https://doi.org/10.1111/rec.70216)  
   Relevance: distinguishes full restoration at sufficient scale from fragmented mitigation and shows that legal structures can bias choices toward weaker restorative paths, which supports publishing restoration-scale and full-restoration semantics explicitly rather than treating all repair language as equivalent.

301. `RS-GR-278`  
   [OECD (2025), *Strategic Foresight Toolkit for Resilient Public Policy*](https://doi.org/10.1787/bcdd9304-en)  
   Relevance: frames future-ready policymaking around scenario building, stress-testing, and the design of robust and adaptable policies, which supports publishing robustness architecture explicitly rather than treating future-readiness as a general aspiration.

302. `RS-GR-279`  
   [Engholm & Kristoffersson (2025), *Exploring “Many Objective Robust Decision Making” for managing uncertainty in climate policy analysis for the transport sector*](https://doi.org/10.1016/j.trip.2025.101524)  
   Relevance: shows that robust-decision methods surface policy trade-offs and vulnerabilities under deep uncertainty that reference-scenario analysis can miss, which supports publishing vulnerability and robustness semantics explicitly rather than treating one optimized path as future-proof.

303. `RS-GR-280`  
   [Schlumberger et al. (2026), *A review of tools and resources to support Decision-Making Under Deep Uncertainty*](https://doi.org/10.1016/j.envsoft.2026.106900)  
   Relevance: catalogs DMDU resources and finds practical uptake limited despite tool coverage across core components, which supports publishing tooling and implementation-capacity semantics explicitly rather than assuming robust adaptive planning is automatically available.

304. `RS-GR-281`  
   [OECD (2024), *Accelerating climate adaptation: A framework for assessing and addressing adaptation needs and priorities*](https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/12/accelerating-climate-adaptation_b375907c/8afaaeb8-en.pdf)  
   Relevance: separates no-regret, low-regret, win-win, and high-regret adaptation actions and warns against rigid pathway commitment under uncertainty, which supports publishing regret class and flexibility semantics explicitly rather than treating all future-facing investment as equivalent.


305. `RS-GR-282`  
   [OECD (2024), *Regulatory experimentation: Moving ahead on the agile regulatory governance agenda*](https://www.oecd.org/en/publications/regulatory-experimentation_f193910c-en.html)  
   Relevance: treats regulatory experimentation as a deliberate governance tool for adaptive learning and better-informed policy rather than as ad hoc improvisation, which supports publishing staged-commitment and reversibility semantics explicitly rather than treating them as rollout noise.

306. `RS-GR-283`  
   [OECD (2025), *Tools for agility: Actionable strategic intelligence and policy experimentation*](https://www.oecd.org/en/publications/2025/10/oecd-science-technology-and-innovation-outlook-2025_bae3698d/full-report/tools-for-agility-actionable-strategic-intelligence-and-policy-experimentation_288971cb.html)  
   Relevance: defines policy experimentation as deliberate small-scale and/or temporary intervention intended for scale-up if successful or phase-out if not, with formative evaluation and reflexive monitoring built in, which supports publishing pilotability and lock-in-delay semantics explicitly rather than treating them as implementation pacing.

307. `RS-GR-284`  
   [Ahern (2025), *The New Anticipatory Governance Culture for Innovation: Regulatory Foresight, Regulatory Experimentation and Regulatory Learning*](https://link.springer.com/article/10.1007/s40804-025-00348-7)  
   Relevance: distinguishes sandboxes, pilot regulation, policy labs, and experimentation clauses as ways to generate regulatory learning before permanent commitment, which supports publishing trial form and reversibility semantics explicitly rather than treating experimentation as generic caution.

308. `RS-GR-285`  
   [Motsenok et al. (2025), *The slippery slope of rights-restricting temporary measures: an experimental analysis*](https://www.cambridge.org/core/journals/behavioural-public-policy/article/slippery-slope-of-rightsrestricting-temporary-measures-an-experimental-analysis/9C05120AF029CCB3B7025301F3DC22CB)  
   Relevance: finds that temporary framing can increase approval of controversial measures and extension of measures already in place, which supports publishing sunset / extension semantics explicitly rather than treating temporary status as a self-sealing safeguard.

309. `RS-GR-286`  
   [Knill, Steinebach & Zink (2025), *The Challenge of Implementing Growing Policy Stocks*](https://www.cambridge.org/core/books/triage-bureaucracy/challenge-of-implementing-growing-policy-stocks/B27DA81408F5A8C782180E5AF3D21BFB)  
   Relevance: shows that policy accumulation can overload implementing agencies and force policy triage across entire portfolios, which supports publishing policy-stock load and retirement semantics explicitly rather than assuming future-facing duties remain costless once adopted.

310. `RS-GR-287`  
   [OECD (2025), *Regulating for effectiveness*](https://www.oecd.org/en/publications/oecd-regulatory-policy-outlook-2025_56b60e39-en/full-report/regulating-for-effectiveness_e4e30799.html)  
   Relevance: treats ex post evaluation, evidence use, and assessment of alternatives as part of effective regulation, which supports publishing reauthorization and retirement evidence standards explicitly rather than treating rule persistence as the default neutral baseline.

311. `RS-GR-288`  
   [Hradický & Sabovčík (2025), *Decommissioning without Financial Fallout: Reforming Public Nuclear Funds*](https://doi.org/10.1016/j.enpol.2025.114723)  
   Relevance: public-segregated decommissioning funds can suffer from moral hazard, conflicts of interest, time inconsistency, and taxpayer spillover when shortfalls appear, which supports publishing prefunding model and reserve-governance semantics explicitly rather than treating future cleanup finance as a budget afterthought.

312. `RS-GR-289`  
   [Rothwell (2025), *Contingency in nuclear power plant decommissioning cost estimation*](https://doi.org/10.1016/j.eneco.2025.108721)  
   Relevance: long-horizon liability coverage depends materially on contingency method, confidence level, variance assumptions, and cost correlations, which supports publishing estimation-confidence semantics explicitly rather than treating reserve adequacy as a single obvious number.

313. `RS-GR-290`  
   [BOEM (2026), *Risk Management and Financial Assurance for OCS Lease and Grant Obligations*](https://www.federalregister.gov/documents/2026/03/09/2026-04517/risk-management-and-financial-assurance-for-ocs-lease-and-grant-obligations)  
   Relevance: offshore decommissioning assurance changes turn on credit thresholds, predecessor liability, probabilistic cost estimates, and P50 versus P70 coverage choices, which supports publishing assurance architecture explicitly rather than treating future liability containment as one neutral financial detail.

314. `RS-GR-291`  
   [Australian Department of Industry, Science and Resources (2025), *Offshore decommissioning and financial assurance reforms: consultation paper*](https://consult.industry.gov.au/offshore-decommissioning-financial-assurance-reforms-consultation-paper)  
   Relevance: Australia's reform process makes financial planning, risk assessment, compliance, and title-surrender rules part of successor-burden design for liabilities expected over 30 to 50 years, which supports publishing who remains responsible and how liability funding is secured rather than treating long-tail cleanup as generic stewardship.

315. `RS-GR-292`  
   [Pew Charitable Trusts (2025), *State and Local Governments Face $105 Billion in Deferred Maintenance for Roads and Bridges*](https://www.pew.org/en/research-and-analysis/issue-briefs/2025/05/state-and-local-governments-face-105-billion-in-deferred-maintenance-for-roads-and-bridges)  
   Relevance: deferred maintenance is an accumulated liability created when preservation spending falls below depreciation, which supports publishing depreciation and backlog semantics explicitly rather than treating wear-and-tear as background noise.

316. `RS-GR-293`  
   [Pew Charitable Trusts (2025), *Strategies for Deferred Maintenance in State-Owned Buildings*](https://www.pew.org/en/research-and-analysis/articles/2025/12/19/strategies-for-deferred-maintenance-in-state-owned-buildings)  
   Relevance: complete asset inventories, condition assessments, repair histories, and lifecycle-cost estimates materially change whether deferred maintenance can be tracked or prioritized, which supports publishing asset-ledger semantics explicitly rather than treating building condition as informal operator knowledge.

317. `RS-GR-294`  
   [Pew Charitable Trusts (2026), *States Are Falling Behind on Roadway Maintenance*](https://www.pew.org/en/research-and-analysis/issue-briefs/2026/02/states-are-falling-behind-on-roadway-maintenance)  
   Relevance: the Asset Sustainability Index separates upward trend stories from actual funding adequacy and shows that improvement can still leave assets structurally underfunded, which supports publishing funding-adequacy ratios explicitly rather than relying on direction-of-change narratives.

318. `RS-GR-295`  
   [OECD (2025), *OECD Economic Surveys: Germany 2025*](https://doi.org/10.1787/39d62aed-en)  
   Relevance: the OECD warns that maintenance and replacement should count inside infrastructure-fund design and that contingent liabilities from extra-budgetary entities should be quantified transparently, which supports publishing maintenance eligibility and contingent-liability semantics explicitly rather than treating them as core-budget trivia.

319. `RS-GR-296`  
   [U.S. Government Accountability Office (2025), *Federal Real Property: Reducing the Government's Holdings Could Generate Substantial Savings*](https://www.gao.gov/products/gao-25-108159)  
   Relevance: rapidly growing deferred-maintenance backlogs can become a first-class governance risk category rather than a facilities nuisance, which supports publishing building-condition backlog semantics explicitly rather than letting successor burdens hide inside operations.



320. `RS-GR-297`  
   [Mining2030 (2025), *Mining Legacy Briefing Paper*](https://mining2030.org/wp-content/uploads/2025/07/Mining2030_Mining-Legacy-Definition_draft_WEBSITE.pdf)  
   Relevance: distinguishes jurisdictions that release firms at closure criteria from those that require 5 to 10 years of post-closure monitoring, notes that some impacts persist for decades, and warns that absent perpetual-care mechanisms long-term liability often defaults to the state, which supports publishing release-window and orphan-backstop semantics explicitly rather than treating closure as one universal endpoint.

321. `RS-GR-298`  
   [Chen et al. (2025), *Investigating post-remediation management strategies for contaminated sites based on residual pollutant migration risks*](https://www.sciencedirect.com/science/article/pii/S2352186425001397)  
   Relevance: shows that post-remediation governance can be both insufficient and excessive and that some sites need long-term monitoring plus institutional controls while others can shift to lighter controls, which supports publishing conditional-closure and monitoring-intensity semantics explicitly rather than treating “remediated” as one state.

322. `RS-GR-299`  
   [U.S. EPA (2025), *Long-Term Stewardship*](https://www.epa.gov/fedfac/long-term-stewardship)  
   Relevance: makes five-year protectiveness reviews, land-use controls, property-transfer controls, and follow-up obligations explicit whenever contamination remains, which supports publishing periodic-review and institutional-control semantics explicitly rather than treating nominal closure as final release.

323. `RS-GR-300`  
   [OECD (2022), *Equitable Framework and Finance for Extractive-based Countries in Transition (EFFECT)*](https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/11/equitable-framework-and-finance-for-extractive-based-countries-in-transition-effect_d91962ed/7871c0ad-en.pdf)  
   Relevance: argues that governments should ring-fence decommissioning funding, clarify liability, and adapt bankruptcy law so costs do not fall to taxpayers, and catalogs parent guarantees, letters of credit, and trust-like security arrangements, which supports publishing orphan-risk and insolvency-waterfall semantics explicitly rather than treating them as finance minutiae.

324. `RS-GR-301`  
   [Maybee et al. (2024), *Who is responsible for the residual risk and how can it be shared or transferred to optimize post-mine outcomes?*](https://www.cambridge.org/core/journals/research-directions-mine-closure-and-transitions/article/who-is-responsible-for-the-residual-risk-and-how-can-it-be-shared-or-transferred-to-optimize-postmine-outcomes/48EE562A89D9F1124101AC6B445F6CDB)  
   Relevance: frames residual-risk sharing and transfer as an open governance design problem tied to relinquishment and post-mine opportunity, which supports publishing who can absorb or share residual risk explicitly rather than treating the end state of liability as obvious.

325. `RS-GR-302`  
   [Torabi (2021), *Legal regime of residual liability in decommissioning*](https://www.sciencedirect.com/science/article/abs/pii/S0308597X21003389)  
   Relevance: shows that some states keep operators liable in perpetuity while others transfer maintenance, monitoring, and residual liability to the state under agreed financial regimes, which supports publishing transfer-versus-perpetual-liability semantics explicitly rather than treating residual liability as legally uniform.

326. `RS-GR-303`  
   [Purtill et al. (2026), *Barriers to introducing non-mining land uses onto mining and processing sites in Western Australia*](https://www.sciencedirect.com/science/article/pii/S2214790X25002308)  
   Relevance: finds that uncertainty around closure acceptance criteria, residual liabilities, and liability apportionment can block beneficial reuse, which supports publishing apportionment and acceptance-criteria semantics explicitly rather than treating post-closure transition as a pure land-use question.

327. `RS-GR-304`  
   [Wambwa et al. (2023), *Enhancing sustainable mining with effective design of financial assurance programs*](https://www.sciencedirect.com/science/article/pii/S2590291123002437)  
   Relevance: warns that financial assurance release before environmental-purpose performance benchmarks are met undercuts sustainable closure, which supports publishing release-gate and performance-benchmark semantics explicitly rather than treating assurance release as routine administrative closure.

328. `RS-GR-305`  
   [Deberdt et al. (2025), *From opposition to conditional acceptance: Corporate environmental and socio-economic engagement in critical minerals mining in Michigan*](https://www.sciencedirect.com/science/article/pii/S0301420725003022)  
   Relevance: shows that community-based environmental monitoring can make acceptance contingent on sustained performance and accessible presence, which supports publishing monitoring-independence and visible-accountability semantics explicitly rather than treating trust gains as generic cooperation.

329. `RS-GR-306`  
   [World Resources Institute (2026), *New Era of US Mineral Mining Must Put Communities First*](https://www.wri.org/insights/us-critical-mineral-mining-community-impacts)  
   Relevance: describes agreements that combine local monitoring access, inspection rights, independent annual environmental audits, permit-revision input, and neutral dispute routes, which supports publishing contestability and outsider-check rights explicitly rather than treating them as optional transparency garnish.

330. `RS-GR-307`  
   [Initiative for Responsible Mining Assurance (2025), *Barro Alto Nickel Mine Surveillance Audit Packet*](https://responsiblemining.net/wp-content/uploads/2025/10/Barro-Alto-Surveillance-Audit-packet-EN.pdf)  
   Relevance: shows that independent audits can publish scoring rationales, evidence references, stakeholder interview practices, feedback channels, and ownership-transfer continuity checks, which supports publishing verification-independence and audit-rationale semantics explicitly rather than treating an audit badge as self-explanatory.

331. `RS-GR-308`  
   [U.S. EPA (2025), *Long-Term Implementation of Engineering and Institutional Control Components of RCRA Corrective Action Remedies*](https://rcrapublic.epa.gov/files/14973.pdf)  
   Relevance: treats repeatable assessment checklists, prior findings, control locations, effectiveness tests, contact lists, and reviewed records as key long-term-stewardship tools, which supports publishing reassessment-protocol semantics explicitly rather than treating post-closure review as ad hoc.

332. `RS-GR-309`  
   [U.S. Department of Energy (2025), *2025 FUSRAP Stakeholder Report*](https://www.energy.gov/sites/default/files/2025-08/2025_FUSRAP_Stakeholder_Report_FINAL.pdf)  
   Relevance: shows that long-term stewardship depends on indexed records preserved for future custodial and stakeholder use and that new third-party characterization, historical records, or credible institutional knowledge can reopen assessment or referral, which supports publishing record-indexing and rediscovery-trigger semantics explicitly rather than treating closure documentation as inert history.

333. `RS-GR-310`  
   [Linköping University (2025), *Highly radioactive nuclear waste – how to keep it from oblivion*](https://liu.se/en/news-item/highly-radioactive-nuclear-waste-how-to-keep-it-from-oblivion)  
   Relevance: describes a Key Information File split into summary, critical information, and instructions for the future, and explicitly asks later generations to update and migrate the information, which supports publishing intelligibility and renewal semantics explicitly rather than treating preservation as raw record retention.

334. `RS-GR-311`  
   [OECD Nuclear Energy Agency (2025), *Remembering the Past in the Future: Building Awareness of Radioactive Waste Repositories Together*](https://www.oecd-nea.org/jcms/pl_111512/remembering-the-past-in-the-future-building-awareness-of-radioactive-waste-repositories-together?details=true)  
   Relevance: frames awareness preservation as a comprehensive strategy using an RK&M toolbox and stakeholder dialogue, which supports publishing awareness-preservation architecture explicitly rather than treating memory transfer as a one-time archival act.

335. `RS-GR-312`  
   [World Nuclear News (2025), *Can a guide to Sweden's repository last 100,000 years?*](https://www.world-nuclear-news.org/articles/document-aims-to-preserve-the-memory-of-swedish-repository)  
   Relevance: operationalises the Key Information File idea through multi-media and multilingual replication, dispersed archival placement, and proposed periodic renewal, which supports publishing renewal-cadence and storage-dispersal semantics explicitly rather than assuming one document can carry the whole burden forever.

336. `RS-GR-313`  
   [U.S. Department of Energy Office of Legacy Management (2025), *Fiscal Year 2025–2030 Human Capital Management Plan*](https://www.energy.gov/sites/default/files/2025-01/2025-2030%20HCMP%20FINAL.pdf)  
   Relevance: formal long-term stewardship can still fail when planned retirements, staffing depth, training, or mission-critical knowledge continuity are neglected, which supports publishing successor-competence and capability-continuity semantics explicitly rather than treating records alone as sufficient handoff machinery.

337. `RS-GR-314`  
   [U.S. Department of Energy Office of Legacy Management (2024), *Fiscal Year 2025–2030 High Performing Organization Plan*](https://www.energy.gov/sites/default/files/2024-12/2025-2030%20HPO_LM%20FINAL%20SINGLE%201.pdf)  
   Relevance: LM treats staffing levels, technical capability needs, workforce planning, geographic distribution, and continuing evaluation as part of the stewardship institution itself, which supports publishing capability-coverage semantics explicitly rather than treating them as internal management trivia.

338. `RS-GR-315`  
   [U.S. Department of Energy, *Office of the Chief Human Capital Officer*](https://www.energy.gov/hc/office-chief-human-capital-officer)  
   Relevance: DOE frames succession planning, competency development, training, and retention as mission-supporting human-capital work, which supports publishing successor-competence semantics explicitly rather than assuming institutions remain executable once documented.

339. `RS-GR-316`  
   [U.S. Department of Energy (2024), *Fiscal Year 2025–2035 Strategic Plan*](https://www.energy.gov/sites/default/files/2024-06/2025-2035_Strategic_Plan.pdf)  
   Relevance: DOE's strategic plan treats emergency-management exercises and drills as preparedness work, which supports publishing rehearsal and validation semantics explicitly rather than treating them as discretionary optics.

340. `RS-GR-317`  
   [National Nuclear Security Administration, *Emergency Preparedness*](https://www.energy.gov/nnsa/emergency-preparedness)  
   Relevance: public emergency-preparedness materials foreground exercised coordination, live-burn training, FRMAC setup exercises, and decision support during incidents, which supports publishing role-rehearsal and interface-testing semantics explicitly rather than assuming plans are self-validating.

341. `RS-GR-318`  
   [U.S. Department of Energy CESER, *Exercises and Training*](https://www.energy.gov/ceser/exercises-and-training)  
   Relevance: DOE describes exercises as building preparedness, improving readiness, and practicing defense and resilience, which supports publishing drill cadence and exercise architecture explicitly rather than treating preparedness as a paperwork property.



342. `RS-GR-319`  
   [U.S. Department of Energy (2025), *FY25-28 Enterprise Data Strategy*](https://www.energy.gov/sites/default/files/2025-07/DOE%20FY25-28%20Enterprise%20Data%20Strategy.pdf)  
   Relevance: DOE explicitly treats enterprise data catalogs, metadata standards, persistent identifiers, standardized retrieval protocols, and API-enabled interoperability as preconditions for trustworthy long-horizon data use, which supports publishing portability and anti-lock-in semantics explicitly rather than treating data plumbing as neutral background infrastructure.

343. `RS-GR-320`  
   [U.S. Cybersecurity and Infrastructure Security Agency et al. (2025), *Priority Considerations for Operational Technology Owners and Operators*](https://www.cisa.gov/sites/default/files/2025-04/Priority-Considerations-for-OT-508c.pdf)  
   Relevance: the guidance tells buyers to prioritize open standards because interoperability lets them pick among products without lock-in, which supports publishing standards-compliance and vendor-exit semantics explicitly rather than treating them as procurement trivia.

344. `RS-GR-321`  
   [OECD (2025), *El Co-Meta (Metadata Component)*](https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/02/access-to-research-data-from-public-funding-toolkit_14d72de8/el-co-meta-metadata-component_046c6abb/2b038f2f-en.pdf)  
   Relevance: the OECD case shows that common metadata schemas, controlled vocabularies, persistent identifiers, and metadata harvesting / synchronization change whether repositories interoperate and remain globally discoverable over time, which supports publishing semantic-alignment and federated-exit semantics explicitly rather than treating repository architecture as an implementation footnote.

345. `RS-GR-322`  
   [Federal Emergency Management Agency (2025), *Developing and Maintaining Emergency Operations Plans*](https://www.fema.gov/sites/default/files/documents/fema_npd_developing-and-maintaining-emergency_052125.pdf)  
   Relevance: FEMA's current planning guidance explicitly asks institutions to describe continuity / alternate facilities, continuity communications, essential records, and human-capital continuity, which supports publishing alternate-procedure and degraded-operations semantics explicitly rather than assuming systems will stay fully available.

346. `RS-GR-323`  
   [National Institute of Standards and Technology (2024), *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)  
   Relevance: NIST treats third-party contingency planning, data redundancy, tested fallback technologies, manual processing, incident-response rehearsal, and anti-capricious vendor termination clauses as distinct risk controls, which supports publishing manual-fallback and supplier-dependence semantics explicitly rather than treating them as technical aftercare.

347. `RS-GR-324`  
   [National Institute of Standards and Technology (2020), *Security and Privacy Controls for Information Systems and Organizations*](https://doi.org/10.6028/NIST.SP.800-53r5)  
   Relevance: NIST's contingency-control baseline explicitly includes orderly system degradation, shutdown, fallback to manual mode, alternate information flows, and alternate processing sites, which supports publishing graceful-degradation semantics explicitly rather than assuming failure means either full continuity or total outage.

348. `RS-GR-325`  
   [Federal Emergency Management Agency (2025), *Response and Recovery Federal Interagency Operational Plan*](https://www.fema.gov/sites/default/files/documents/fema_rd_response-recovery-fiop-npb-042025.pdf)  
   Relevance: FEMA's current federal response-and-recovery plan says plans and procedures should address resilient communications capabilities and cross-jurisdictional backup capabilities, which supports publishing backup-path and interoperability-of-interfaces semantics explicitly rather than assuming coordination channels survive disruption by default.

349. `RS-GR-326`  
   [National Archives (2025), *Digital Preservation Strategy 2022-2026*](https://www.archives.gov/preservation/digital-preservation/strategy)  
   Relevance: NARA treats data integrity, format and media sustainability, regular system/tool review, replication, lifecycle logging, fixity generation, annual fixity audits, file repair, and preservation action plans for unsustainable formats as core preservation architecture, which supports publishing fixity-refresh and format-migration semantics explicitly rather than treating retention as passive storage.

350. `RS-GR-327`  
   [National Archives (2025), *Digital Preservation Framework Updates, April – June 2025*](https://fixity-check.blogs.archives.gov/2025/06/30/digital-preservation-framework-updates-april-june-2025/)  
   Relevance: NARA's quarterly framework updates and linked-open-data preservation action plans show that long-horizon durability depends on continuously refreshed format-risk assessments rather than one-time archival intake, which supports publishing risk-review cadence and action-plan refresh semantics explicitly rather than treating preservation knowledge as static.

351. `RS-GR-328`  
   [National Archives (2025), *16363 Reasons to Trust*](https://fixity-check.blogs.archives.gov/2025/03/06/16363-reasons-to-trust/)  
   Relevance: NARA's biennial ISO 16363 self-assessment treats repository trustworthiness as an audited, repeatedly evidenced property tied to documented practice and improvement over time, which supports publishing trust-audit and maturity-refresh semantics explicitly rather than treating a repository as trustworthy by default once created.

352. `RS-GR-329`  
   [NIST (2025), *CSWP 39: Considerations for Achieving Cryptographic Agility: Strategies and Practices*](https://csrc.nist.gov/pubs/cswp/39/considerations-for-achieving-cryptographic-agility/final)  
   Relevance: NIST defines crypto agility as the capability to replace and adapt cryptographic algorithms across protocols, applications, software, hardware, firmware, and infrastructure while preserving security and ongoing operations, which supports publishing algorithm-transition semantics explicitly rather than treating signature or encryption choices as permanent background assumptions.

353. `RS-GR-330`  
   [NIST (2025), *Crypto Agility Project*](https://csrc.nist.gov/projects/crypto-agility)  
   Relevance: NIST frames PQC migration as one instance of a broader need to support repeated future cryptographic migrations without interrupting live systems, which supports publishing migration-readiness and future-transition semantics explicitly rather than treating today's cryptography as a one-time setup choice.

354. `RS-GR-331`  
   [NIST NCCoE (2026), *Frequently Asked Questions about Post-Quantum Cryptography*](https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/)  
   Relevance: the NCCoE FAQ organizes PQC migration as an ongoing sequence of awareness, planning, execution, and validation / monitoring steps and explicitly links it to broader crypto-agility preparation, which supports publishing cryptographic transition stages explicitly rather than treating migration as a single later patch.

355. `RS-GR-332`  
   [NIST (2020), *SP 800-57 Part 1 Rev. 5, Recommendation for Key Management: Part 1 – General*](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)  
   Relevance: NIST treats trust anchors, key-inventory management, backup, compromise, recovery, and cryptoperiod planning as part of core key management, which supports publishing trust-root lifetime and recovery semantics explicitly rather than treating credentials as indefinite background fixtures.

356. `RS-GR-333`  
   [ICANN (2024), *ICANN Publishes New DNSSEC Trust Anchor to Prepare for 2026*](https://www.icann.org/en/announcements/details/icann-publishes-new-dnssec-trust-anchor-to-prepare-for-2026-15-08-2024-en)  
   Relevance: ICANN's trust-anchor rollout uses prepublication, long standby windows, and vendor / package-maintainer distribution coordination, which supports publishing trust-anchor propagation and rollover-window semantics explicitly rather than assuming successors can swap roots instantly.

357. `RS-GR-334`  
   [StJohns (2007), *RFC 5011: Automated Updates of DNS Security (DNSSEC) Trust Anchors*](https://datatracker.ietf.org/doc/html/rfc5011)  
   Relevance: RFC 5011 describes automated authenticated trust-anchor updates, N-1 compromise protection, and revocation / hold-down / manual-recovery considerations, which supports publishing automated-update and compromise-recovery semantics explicitly rather than treating trust-root rollover as ad hoc operator folklore.

358. `RS-GR-335`  
   [The Update Framework (2026), *The Update Framework Specification*](https://theupdateframework.github.io/specification/latest/)  
   Relevance: TUF makes root trust threshold-based, keeps root keys offline, allows delegated roles and revocation, and requires out-of-band recovery if a threshold of root keys is compromised, which supports publishing delegation, threshold, and emergency-recovery semantics explicitly rather than treating software-trust provenance as a single static signer.


359. `RS-GR-336`  
   [Laurie, Messeri, & Stradling (2021), *RFC 9162: Certificate Transparency Version 2.0*](https://www.rfc-editor.org/rfc/rfc9162.html)  
   Relevance: RFC 9162 distinguishes inclusion proofs from consistency proofs and uses the latter to verify append-only log history, which supports publishing proof-verification semantics explicitly rather than treating log-backed provenance as a single undifferentiated badge.

360. `RS-GR-337`  
   [Trillian / transparency.dev, *Discourage misbehaviour by third parties in Certificate Transparency*](https://transparency.dev/application/discourage-misbehaviour-by-third-parties-in-certificate-transparency/)  
   Relevance: the Certificate Transparency deployment story shows that requiring public log publication makes misissued records openly discoverable and changes incentives beyond traditional private auditing, which supports publishing public-registration semantics explicitly rather than treating signatures or audits alone as durable accountability.

361. `RS-GR-338`  
   [Certificate Transparency, *Monitors*](https://certificate.transparency.dev/monitors/)  
   Relevance: CT names monitors as a distinct actor that checks whether all logged certificates are visible and watches for suspicious entries, which supports publishing monitor-coverage semantics explicitly rather than treating log availability as self-authenticating.

362. `RS-GR-339`  
   [Sigstore, *Overview*](https://docs.sigstore.dev/about/overview/)  
   Relevance: Sigstore treats signing events as recorded in an immutable append-only log, expects proof-of-inclusion verification, and expects both auditors and identity owners to monitor the log, which supports publishing inclusion-verification and identity-monitoring semantics explicitly rather than treating provenance as a one-time signature event.

363. `RS-GR-340`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/)  
   Relevance: the current SCITT architecture allows multiple independent transparency services and receipts, warns against trusting a single centralized service, and tells relying parties not to accept signed statements without discoverable receipts from trusted services, which supports publishing service-plurality and selective-submission semantics explicitly rather than treating one log's receipt as permanent provenance.

364. `RS-GR-341`  
   [C2SP (2026), *Transparency Log Witness Protocol*](https://c2sp.org/tlog-witness)  
   Relevance: the witness protocol requires a log to present a new checkpoint plus a consistency proof to each witness, and witnesses only cosign append-only evolution from previously observed state, which supports publishing checkpoint-witness and anti-equivocation semantics explicitly rather than treating append-only history as self-securing.

365. `RS-GR-342`  
   [transparency.dev / ArmoredWitness (2026), *ArmoredWitness*](https://github.com/transparency-dev/armored-witness)  
   Relevance: ArmoredWitness frames witnessing as protection against split-view attacks, treats countersigned checkpoints as third-party evidence that different users are seeing one history, and emphasizes diverse custodianship across ecosystems, which supports publishing witness-diversity and split-view-resistance semantics explicitly rather than treating one log operator as enough.

366. `RS-GR-343`  
   [Sigsum (2026), *Getting started*](https://www.sigsum.org/getting-started/)  
   Relevance: Sigsum's trust policy declares named witnesses and an explicit quorum rule for trusting a log, which supports publishing witness-threshold and quorum semantics explicitly rather than treating witness presence as an undifferentiated box-check.

367. `RS-GR-344`  
   [Witness Network (2026), *Home*](https://witness-network.org/)  
   Relevance: Witness Network shows that anti-equivocation depends not only on cryptographic design but also on sustainable configuration and onboarding across many logs and many witnesses, which supports publishing witness-discovery and configuration-governance semantics explicitly rather than assuming multi-witness operation will happen on its own.

368. `RS-GR-345`  
   [Apple Security Engineering and Architecture (2023), *Advancing iMessage security: iMessage Contact Key Verification*](https://security.apple.com/blog/imessage-contact-key-verification/)  
   Relevance: Apple's deployment has user devices verify inclusion and consistency directly, cross-check state across a user's own devices, and gossip log hashes to detect split views, which supports publishing client-self-audit and cross-perspective-consistency semantics explicitly rather than treating third-party monitoring as the only anti-equivocation path.



369. `RS-GR-346`  
   [Adams, Cain, Pinkas, & Zuccherato (2001), *RFC 3161: Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP)*](https://www.rfc-editor.org/rfc/rfc3161.html)  
   Relevance: RFC 3161 defines timestamps as proof that data existed before a particular time, requires the Time-Stamp Authority to use a trustworthy source of time, and notes that two different TSAs can mitigate compromise risk, which supports publishing time-source trust and timestamp-diversity semantics explicitly rather than treating a timestamp as self-justifying.

370. `RS-GR-347`  
   [Gondrom, Brandner, & Pordesch (2007), *RFC 4998: Evidence Record Syntax (ERS)*](https://www.rfc-editor.org/rfc/rfc4998.html)  
   Relevance: RFC 4998 defines renewable evidence records for proving existence and integrity over long or undetermined periods of time, including timestamp renewal and hash-tree renewal when algorithms weaken, which supports publishing evidence-renewal semantics explicitly rather than treating one timestamp as permanent proof.

371. `RS-GR-348`  
   [Uptane (2026), *Uptane Standard for Design and Implementation 2.1.0*](https://uptane.org/docs/latest/standard/uptane-standard)  
   Relevance: Uptane requires clients to load the current or latest securely attested time and to compare that time against expiration across root, timestamp, snapshot, and targets metadata to detect freeze attacks, which supports publishing attested-time and freshness-check semantics explicitly rather than treating signature verification as time-independent.

372. `RS-GR-349`  
   [Uptane (2026), *Best Practices 2.1.0*](https://uptane.org/docs/latest/deployment/best-practices)  
   Relevance: Uptane deployment guidance says devices need a secure notion of time as soon as they boot, and explains that compromised or incorrect time can make good metadata look expired or stale metadata look current, which supports publishing clock-bootstrap and bad-time failure semantics explicitly rather than treating freshness checks as enough by themselves.

373. `RS-GR-350`  
   [Ladd & Dansarie (2026), *Roughtime* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/)  
   Relevance: the current Roughtime draft provides authenticated rough time even for clients without an initial clock and gives clients cryptographic evidence of inconsistent or malicious time-server behavior, which supports publishing contestable multi-source time-attestation semantics explicitly rather than assuming one clock source is an unquestioned background oracle.

374. `RS-GR-351`  
   [Laurie et al. (2021), *RFC 9162: Certificate Transparency Version 2.0*](https://www.rfc-editor.org/rfc/rfc9162.html)  
   Relevance: RFC 9162 makes inclusion and consistency proofs verifiable against signed tree heads, which supports publishing compact proof-packet and checkpoint-retention semantics explicitly rather than treating live log reachability as the only verification path.

375. `RS-GR-352`  
   [Steele et al. (2025), *COSE (CBOR Object Signing and Encryption) Receipts* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/draft-ietf-cose-merkle-tree-proofs/)  
   Relevance: the current COSE receipts draft defines concise encodings for Merkle inclusion and consistency proofs and frames receipts as proofs about verifiable data structures, which supports publishing standardized portable-proof semantics explicitly rather than letting each tool invent its own opaque receipt format.

376. `RS-GR-353`  
   [Birkholz et al. (2024), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-10)  
   Relevance: the current SCITT architecture treats receipts as offline, universally verifiable proofs of registration, requires enough information to reproduce registration checks from either the log or the receipt, and allows re-registration of already-transparent statements on another service, which supports publishing service-loss survivability and re-anchoring semantics explicitly rather than treating one operator as permanent.

377. `RS-GR-354`  
   [Sigstore (2025), *Sigstore Bundle Format*](https://docs.sigstore.dev/about/bundle/)  
   Relevance: Sigstore defines a bundle as everything required to verify a signature on an artifact and includes verification material such as transparency-log entries, timestamps, inclusion proofs, and checkpoints, which supports publishing compact evidence-packet semantics explicitly rather than retaining sprawling side artifacts or relying on live fetches.

378. `RS-GR-355`  
   [Sigstore (2026), *Signing Blobs*](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/)  
   Relevance: Sigstore's keyless blob-signing guidance says the bundle must be stored for later verification and notes that the bundle format is being standardized across Sigstore clients, which supports publishing retained-bytes and cross-client survivability semantics explicitly rather than treating verification metadata as disposable scratch.

379. `RS-GR-356`  
   [Sigstore (2026), *Go Language Client*](https://docs.sigstore.dev/language_clients/go/)  
   Relevance: Sigstore's Go client supports bundle verification, online and offline verification with Rekor, TUF support, and custom trusted roots, which supports publishing offline-verification coverage and retained-trust-root semantics explicitly rather than treating live service access as an unavoidable assumption.


380. `RS-GR-357`  
   [Birkholz et al. (2025), *RFC 9334: Remote ATtestation procedureS (RATS) Architecture*](https://www.rfc-editor.org/rfc/rfc9334.html)  
   Relevance: RFC 9334 separates Appraisal Policy for Evidence from Appraisal Policy for Attestation Results, which supports preserving verifier and relying-party rulebooks explicitly rather than treating signed evidence as self-interpreting.

381. `RS-GR-358`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-11)  
   Relevance: the current SCITT architecture requires registration policies and trust anchors to be made transparent, applies the policy committed at registration time, and requires enough information to reproduce historical registration checks, which supports preserving policy snapshots explicitly rather than letting verifier behavior drift silently.

382. `RS-GR-359`  
   [The Update Framework Authors (2026), *The Update Framework Specification*](https://theupdateframework.github.io/specification/latest/)  
   Relevance: the current TUF specification makes clients ship configured trusted root keys, evaluate thresholded roles and delegations, and revoke delegations via new metadata, which supports preserving root / delegation policy explicitly rather than treating signature validity as repository-agnostic.

383. `RS-GR-360`  
   [Sigstore (2026), *Verifying Signatures*](https://docs.sigstore.dev/cosign/verifying/verify/)  
   Relevance: Sigstore verification requires explicit identity / issuer constraints for keyless signatures and allows signature verification with claim checks disabled, which supports preserving identity-acceptance and claim-check strictness as part of the verifier profile rather than assuming all "valid signatures" mean the same thing.

384. `RS-GR-361`  
   [Sigstore (2026), *Kubernetes Policy Controller*](https://docs.sigstore.dev/policy-controller/overview/)  
   Relevance: Sigstore policy-controller validates signatures and attestations while applying cue / rego policies and configurable TrustRoots, which supports treating enforcement policy as a portable artifact rather than hidden cluster-local configuration.

385. `RS-GR-362`  
   [Birkholz et al. (2026), *Concise Reference Integrity Manifest (CoRIM)* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-rats-corim-10)  
   Relevance: the current CoRIM draft defines deterministic verifier reconciliation, tracks authority within appraisal, and requires any profile to describe expected verifier behavior at profile-dependent points, which supports preserving deterministic appraisal and profile semantics explicitly rather than relying on one tool's undocumented interpretation.


386. `RS-GR-363`  
   [Cooper et al. (2008), *RFC 5280: Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile*](https://www.ietf.org/rfc/rfc5280.txt)  
   Relevance: RFC 5280 makes CRLs time-stamped revoked-certificate lists, ties acceptance to a suitably recent CRL under local policy, delays revocation visibility to the CRL issuance cadence, and preserves revocation entries until beyond certificate validity, which supports publishing status-freshness and negative-evidence retention semantics explicitly rather than assuming one timeless revoked bit.

387. `RS-GR-364`  
   [Santesson et al. (2013), *RFC 6960: X.509 Internet Public Key Infrastructure Online Certificate Status Protocol - OCSP*](https://datatracker.ietf.org/doc/html/rfc6960)  
   Relevance: RFC 6960 distinguishes `good`, `revoked`, and `unknown` status, includes revocation time and optional reason, and bounds responses with `thisUpdate` / `nextUpdate`, which supports publishing unknown-handling and status-validity-window semantics explicitly rather than collapsing all non-success cases together.

388. `RS-GR-365`  
   [Sporny et al. (2025), *Bitstring Status List v1.0*](https://www.w3.org/TR/vc-bitstring-status-list/)  
   Relevance: Bitstring Status List v1.0 makes revocation and suspension distinct status purposes and allows custom message-bearing statuses plus `statusReference`, which supports publishing status vocabulary and interpretation semantics explicitly rather than pretending every later change is just generic invalidation.

389. `RS-GR-366`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-22)  
   Relevance: the current SCITT architecture allows statements about the same subject to represent end of life, redirection to a newer version, or other issuer-published changes and correlates multiple statements by subject, which supports preserving supersession and successor-routing semantics explicitly rather than treating one positive statement as the whole lifecycle.

390. `RS-GR-367`  
   [Sigstore (2026), *Security Model*](https://docs.sigstore.dev/about/security/)  
   Relevance: Sigstore's security model says Fulcio avoids traditional revocation by issuing short-lived certificates and relies on transparency-log timestamps to prove an artifact was signed while the certificate was valid, which supports publishing whether the world uses revocation lists or time-bounded validity as its status model rather than assuming all ecosystems revoke the same way.

391. `RS-GR-368`  
   [Sigstore (2026), *Threat Model*](https://docs.sigstore.dev/about/threat-model/)  
   Relevance: Sigstore's threat model says OIDC-account compromise is not handled by Sigstore itself, recommends issuer-side revocation for compromised accounts, and notes that TUF-based trust roots can mark compromised material with a compromise time so legitimate signatures from before that time remain verifiable, which supports publishing compromise-time and historical-validity semantics explicitly rather than treating revocation as an undifferentiated all-time failure.


392. `RS-GR-369`  
   [Farrell et al. (2013), *RFC 6920: Naming Things with Hashes*](https://www.rfc-editor.org/rfc/rfc6920.html)  
   Relevance: RFC 6920 standardizes `ni` names that identify digital objects using hash outputs, separates naming from later dereferencing / location, and says comparisons should key off the digest algorithm and value rather than auxiliary URI fields, which supports preserving immutable core subject identifiers explicitly rather than treating mutable URLs or resolver paths as the thing that was proven.

393. `RS-GR-370`  
   [in-toto (2026), *Attestation Framework Statement v1*](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md)  
   Relevance: the current in-toto statement requires each subject to carry a digest, assumes subjects are immutable, treats `name` and `uri` as context-dependent fields, and says subject matching is purely by digest, which supports correlating attestations, receipts, and later status events to immutable subject identity rather than mutable labels.

394. `RS-GR-371`  
   [Docker (2026), *Image digests*](https://docs.docker.com/dhi/core-concepts/digests/)  
   Relevance: Docker's current guidance says image digests are unique cryptographic identifiers while tags can be reused or changed, and notes that one multi-platform tag can resolve to a manifest list plus several platform-specific digests, which supports publishing alias mutability and variant-resolution semantics explicitly rather than treating a displayed tag as a stable subject identifier.

395. `RS-GR-372`  
   [Open Container Initiative (2025), *Distribution Specification*](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)  
   Relevance: the OCI distribution spec defines digests as unique identifiers, tags as human-readable pointers, and subject / referrers relationships as digest-keyed associations between manifests, which supports correlating signatures, SBOMs, attestations, and later status material to immutable subject digests rather than to whichever tag happened to point there at one moment.

396. `RS-GR-373`  
   [Software Heritage (2021), *SoftWare Heritage persistent IDentifiers (SWHIDs)*](https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html)  
   Relevance: SWHIDs are stable identifiers rather than URLs, embed intrinsic cryptographic object identifiers in a Merkle structure, let context qualifiers carry origin / anchor information separately from the core identifier, and can be computed before archival, which supports preserving resolver-independent subject identity while still keeping context and alias history distinct.

397. `RS-GR-374`  
   [Sigstore / cosign (2026), *Cosign*](https://github.com/sigstore/cosign)  
   Relevance: cosign says signatures protect digests of registry objects and uses separate signed annotations when a specific tag-to-digest mapping matters, which supports preserving mutable-alias bindings as first-class signed evidence instead of assuming the signed object digest and the human-facing tag are the same contract.


398. `RS-GR-375`  
   [Rundgren et al. (2020), *RFC 8785: JSON Canonicalization Scheme (JCS)*](https://datatracker.ietf.org/doc/html/rfc8785)  
   Relevance: RFC 8785 says hashing and signing need invariant data, defines canonical JSON using strict primitive serialization, I-JSON constraints, and deterministic property sorting, and permits keeping original JSON on the wire while signing the canonical counterpart, which supports publishing the exact canonicalization boundary instead of assuming every JSON rendering is equally signable.

399. `RS-GR-376`  
   [Bormann & Hoffman (2020), *RFC 8949: Concise Binary Object Representation (CBOR)*](https://datatracker.ietf.org/doc/html/rfc8949)  
   Relevance: RFC 8949 says deterministic CBOR is a protocol-defined restricted form that requires preferred serialization, forbids indefinite-length items, sorts map keys by bytewise order of deterministic encodings, and forces protocols to be explicit about tags and number representations, which supports publishing deterministic-encoding profile details rather than treating compact binary encoding as self-explanatory.

400. `RS-GR-377`  
   [Secure Systems Lab (2024), *DSSE Protocol v1.0.2*](https://github.com/secure-systems-lab/dsse/blob/master/protocol.md)  
   Relevance: the DSSE protocol signs the exact serialized body plus an authenticated payload type, explicitly avoids canonicalization to reduce attack surface, and requires applications to consume the same bytes that were verified, which supports treating byte-freezing plus interpretation-binding as an explicit world contract rather than an implementation accident.

401. `RS-GR-378`  
   [Sporny et al. (2024), *RDF Dataset Canonicalization*](https://www.w3.org/TR/rdf-canon/)  
   Relevance: RDF Canonicalization defines a stable canonical serialization for RDF datasets, including stable blank-node identifiers across different serializations of the same graph, which supports publishing when the protected object is graph semantics rather than one surface syntax.

402. `RS-GR-379`  
   [Sporny et al. (2025), *Verifiable Credential Data Integrity 1.0*](https://www.w3.org/TR/vc-data-integrity/)  
   Relevance: VC Data Integrity says JCS is attractive for plain JSON, RDF Canonicalization is attractive when JSON-LD semantics must be secured, and the security of a proof depends on the correctness of the canonicalization algorithm, which supports publishing canonicalization choice and correctness assumptions explicitly rather than hiding them behind a generic “signed document” label.

403. `RS-GR-380`  
   [Python Packaging Authority (2026), *Index hosted attestations*](https://packaging.python.org/en/latest/specifications/index-hosted-attestations/)  
   Relevance: the current Python packaging attestation spec encodes an in-toto statement in JSON but treats the serialized statement as an opaque binary blob on the wire and signs it with DSSE to avoid canonicalization, which supports publishing when a system intentionally chooses exact-byte envelopes over semantic-normalization schemes.


404. `RS-GR-381`  
   [Freed, Klensin, & Hansen (2013), *RFC 6838: Media Type Specifications and Registration Procedures*](https://www.rfc-editor.org/rfc/rfc6838)  
   Relevance: RFC 6838 defines media types as registered format identifiers for use across protocols, which supports preserving the declared data-format contract explicitly rather than guessing meaning from filenames, transport, or tool defaults.

405. `RS-GR-382`  
   [JSON Schema (2022), *JSON Schema Core, Draft 2020-12*](https://json-schema.org/draft/2020-12/json-schema-core)  
   Relevance: JSON Schema Core says a dialect is a set of vocabularies and semantics, and that `$schema` declares which dialect a schema uses, which supports preserving schema-dialect and vocabulary semantics explicitly rather than treating JSON validation keywords as timeless or universal.

406. `RS-GR-383`  
   [Sporny et al. (2020), *JSON-LD 1.1*](https://www.w3.org/TR/json-ld11/)  
   Relevance: JSON-LD 1.1 says `@context` defines how terms are understood, `@version` can prevent older processors from producing different output, and remote contexts may be followed automatically, which supports pinning context and processing-mode semantics explicitly rather than assuming linked-data meaning survives without its interpretation bundle.

407. `RS-GR-384`  
   [in-toto (2026), *Statement layer specification v1*](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md)  
   Relevance: the current in-toto statement spec says the Statement unambiguously identifies Predicate types, fixes `_type` for the statement schema version, and requires `predicateType`, which supports preserving predicate-schema identity explicitly rather than treating a valid signature over generic JSON as self-explanatory.

408. `RS-GR-385`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-22)  
   Relevance: the current SCITT architecture says statements should be tagged with a relevant media type to help interpretation, which supports preserving statement-type and content-type semantics explicitly rather than treating transparency receipts as universal meaning-preserving wrappers.

409. `RS-GR-386`  
   [SPDX (2024), *SPDX Specification 3.0.1 — `specVersion`*](https://spdx.github.io/spdx-spec/v3.0.1/model/Core/Properties/specVersion/)  
   Relevance: SPDX 3.0.1 says `specVersion` provides the reference needed to parse and interpret an element and to support backward compatibility across future changes, which supports retaining versioned semantic contracts explicitly rather than expecting future inheritors to infer which rulebook produced an old statement.

410. `RS-GR-387`  
   [Cooper et al. (2008), *RFC 5280: Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile*](https://www.rfc-editor.org/rfc/rfc5280)  
   Relevance: RFC 5280 says basic constraints determine whether a key may verify certificate signatures, extended key usage constrains the certified public key to declared purposes, and name constraints restrict the namespace for subsequent certificates, which supports preserving purpose and namespace scope explicitly rather than treating a valid certification path as universal speaking authority.

411. `RS-GR-388`  
   [The Update Framework (2026), *The Update Framework Specification*](https://theupdateframework.github.io/specification/latest/)  
   Relevance: the current TUF specification says delegated roles are trusted by specific keys and thresholds, are limited to declared target paths, require the target to remain within trusted paths of every role in the delegation chain, and can terminate further trust search, which supports preserving delegation scope explicitly rather than treating any valid delegated signature as globally admissible.

412. `RS-GR-389`  
   [in-toto (2026), *in-toto specification*](https://github.com/in-toto/specification/blob/master/in-toto-spec.md)  
   Relevance: the current in-toto specification says layouts indicate which keys are authorized for signing link metadata for each step and that clients verify each step was performed by the authorized functionary, which supports preserving step-specific speaking authority explicitly rather than collapsing provenance to signer identity alone.

413. `RS-GR-390`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-22)  
   Relevance: the current SCITT architecture says registration policies and trust anchors must be transparent, enough information must survive to reproduce the registration checks in force at registration time, and multiple issuers can make conflicting statements about the same artifact, which supports preserving the standing policy that admitted an issuer's claim rather than relying on a receipt alone.

414. `RS-GR-391`  
   [SPIFFE (2026), *SPIFFE Trust Domain and Bundle*](https://spiffe.io/docs/latest/spiffe-specs/spiffe_trust_domain_and_bundle/)  
   Relevance: the current SPIFFE trust-domain specification says a trust domain is an identity namespace backed by an issuing authority, that validators must choose the bundle corresponding to the trust domain of the identity being checked, and that bundles evolve as authoritative keys rotate, which supports preserving namespace custody explicitly rather than treating identity strings as self-authenticating.

415. `RS-GR-392`  
   [SPIFFE (2026), *SPIRE Concepts*](https://spiffe.io/docs/latest/spire-about/spire-concepts/)  
   Relevance: the current SPIRE documentation says workload registration maps a SPIFFE ID to selectors the workload must possess, the server distributes only authorized registration entries, and workload identity issuance depends on matching selectors and parent-SPIFFE relationships, which supports preserving workload-standing snapshots explicitly rather than assuming possession of one workload key is enough.

416. `RS-GR-393`  
   [Jones et al. (2015), *RFC 7519: JSON Web Token (JWT)*](https://datatracker.ietf.org/doc/html/rfc7519)  
   Relevance: RFC 7519 says the `aud` claim identifies the recipients a token is intended for and that a principal not identifying itself in that audience claim must reject the token, which supports preserving audience scope explicitly rather than treating every otherwise-valid signed claim as universally admissible.


417. `RS-GR-394`  
   [Barker et al. (2019), *NIST SP 800-57 Part 2 Rev. 1: Best Practices for Key Management Organizations*](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt2r1.pdf)  
   Relevance: NIST SP 800-57 Part 2 says distribution plans may require key components with dual control and split knowledge, which supports preserving separation-of-duty assumptions explicitly rather than treating multi-party control as an unrecorded implementation detail.

418. `RS-GR-395`  
   [The Update Framework (2026), *The Update Framework Specification*](https://theupdateframework.github.io/specification/latest/)  
   Relevance: the current TUF specification says all roles use one or more keys and require a threshold of signatures, and that the root threshold should be chosen so compromise of all offline keys is extremely unlikely, which supports preserving threshold purpose and compromise-domain assumptions explicitly rather than treating threshold counts as decorative redundancy.

419. `RS-GR-396`  
   [in-toto (2026), *in-toto specification*](https://github.com/in-toto/specification/blob/master/in-toto-spec.md)  
   Relevance: the current in-toto specification says a step threshold is the number of link metadata pieces required to verify the step and is intended for higher-trust steps where multiple functionaries perform the operation and report the same results, which supports preserving concurrence semantics explicitly rather than collapsing assurance to one authorized actor.

420. `RS-GR-397`  
   [Sigsum (2026), *Getting started*](https://www.sigsum.org/getting-started/)  
   Relevance: current Sigsum documentation shows trust policy can require a declared witness quorum before a log is trusted, which supports preserving witness-concurrence policy explicitly rather than treating one transparency service as self-sufficient.

421. `RS-GR-398`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-22)  
   Relevance: the current SCITT architecture says the same statement may be registered in multiple transparency services to produce multiple independent receipts and that relying parties choose which issuers and transparency services they trust, which supports preserving multi-service concurrence policy explicitly rather than treating extra receipts as context-free embellishment.

422. `RS-GR-399`  
   [The Update Framework (2026), *The Update Framework Specification*](https://github.com/theupdateframework/specification/blob/master/tuf-spec.md)  
   Relevance: the current TUF specification says the `signatures` list should contain only one signature per keyid so the same key is not counted multiple times toward a threshold, which supports preserving the unit of distinctness explicitly rather than assuming any two signatures necessarily represent two independent approvals.

423. `RS-GR-400`  
   [The Update Framework (2026), *The Update Framework Specification*](https://theupdateframework.github.io/specification/latest/)  
   Relevance: the current TUF specification defines terminating delegations so clients stop considering later trust statements that match the delegated pattern, which supports preserving precedence and termination semantics explicitly rather than assuming overlapping authorities can be combined without order.

424. `RS-GR-401`  
   [python-tuf (2026), *Supporting classes — TUF documentation*](https://theupdateframework.readthedocs.io/en/stable/api/tuf.api.metadata.supporting.html)  
   Relevance: current TUF supporting-class documentation says delegated-role order defines the order that delegations are considered during target searches, which supports preserving search-order semantics explicitly rather than treating overlapping delegations as unordered.

425. `RS-GR-402`  
   [GitHub Advisory Database (2025), *CVE-2025-2886: tough terminating targets role delegations are not respected*](https://github.com/advisories/GHSA-v4wr-j3w6-mxqc)  
   Relevance: the 2025 advisory says terminating delegations and delegation priority give TUF repositories unambiguous control over overlapping delegations and that ignoring those rules can accept lower-priority information that should have been ignored, which supports preserving precedence semantics explicitly rather than assuming all valid signatures compose benignly.

426. `RS-GR-403`  
   [in-toto (2026), *API — in-toto 3.0.0 documentation*](https://in-toto.readthedocs.io/en/latest/api.html)  
   Relevance: current in-toto verification documentation says threshold verification fails unless enough authorized functionaries agree on recorded materials and products, which supports preserving agreement-versus-mere-count semantics explicitly rather than treating threshold as a naked signature total.

427. `RS-GR-404`  
   [Birkholz et al. (2025), *An Architecture for Trustworthy and Transparent Digital Supply Chains* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-22)  
   Relevance: the current SCITT architecture allows multiple issuers to make conflicting statements about the same artifact and says relying parties may include or exclude statements from issuers when deciding accuracy, which supports preserving issuer-conflict curation explicitly rather than assuming one receipt fixes the truth.

428. `RS-GR-405`  
   [sigstore/policy-controller (2026), *API Types*](https://github.com/sigstore/policy-controller/blob/main/docs/api-types/index.md)  
   Relevance: current Sigstore policy-controller API documentation says multiple authorities within one policy may be used to source the valid signature and that the policy-level rule can be evaluated only if at least one authority passes, which supports preserving within-policy `OR` semantics explicitly rather than treating multiple authorities as automatically cumulative.

429. `RS-GR-406`  
   [Sigstore (2026), *Kubernetes Policy Controller*](https://docs.sigstore.dev/policy-controller/overview/)  
   Relevance: current Sigstore policy-controller documentation says matched `ClusterImagePolicy` resources compose as `AND`, authorities inside each policy compose as `OR`, and `no-match-policy` can warn, allow, or deny, which supports preserving cross-policy conflict-resolution and no-match semantics explicitly rather than treating policy evaluation as an opaque yes/no box.

430. `RS-GR-407`  
   [Birkholz et al. (2023), *Remote ATtestation procedureS (RATS) Architecture* (RFC 9334)](https://www.rfc-editor.org/rfc/rfc9334.html)  
   Relevance: RFC 9334 defines an Attestation Result as verifier output produced by applying appraisal policy to evidence, endorsements, and reference values, which supports preserving decision-explanation artifacts explicitly rather than treating the final verdict as self-explanatory.

431. `RS-GR-408`  
   [OASIS (2010), *eXtensible Access Control Markup Language (XACML) Version 3.0 Core Specification*](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cs-01-en.pdf)  
   Relevance: the XACML core specification defines policy-combining algorithms and says policies and policy sets may carry obligations or advice, which supports preserving how a verdict was assembled and what follow-on duties attached rather than retaining only Permit/Deny.

432. `RS-GR-409`  
   [Open Policy Agent (2026), *REST API Reference*](https://www.openpolicyagent.org/docs/rest-api)  
   Relevance: current OPA REST API documentation says evaluation responses can return full or partial explanations with trace events, query and parent ids, AST nodes, and local bindings, which supports preserving machine-replayable decision traces explicitly rather than collapsing verification to one boolean.

433. `RS-GR-410`  
   [Open Policy Agent (2026), *Decision Logs*](https://www.openpolicyagent.org/docs/management-decision-logs)  
   Relevance: current OPA decision-log documentation says each logged event can include the queried policy path, input, result, decision id, request correlation fields, and bundle metadata, which supports preserving auditable decision receipts explicitly rather than relying on later inference about what was evaluated.

434. `RS-GR-411`  
   [Open Policy Agent (2026), *REST API Reference*](https://www.openpolicyagent.org/docs/rest-api)  
   Relevance: current OPA provenance documentation says policy-evaluation responses can include verifier version, build commit, build timestamp, build host, and activated bundle revisions, which supports preserving implementation and bundle provenance explicitly rather than assuming policy snapshots alone capture replay conditions.

435. `RS-GR-412`  
   [Cedar Policy Language (2026), *Authorization*](https://docs.cedarpolicy.com/auth/authorization.html)  
   Relevance: current Cedar authorization documentation says responses include diagnostics with determining policies and error conditions and that the algorithm is default-deny, forbid-overrides-permit, and skip-on-error, which supports preserving why an outcome happened explicitly rather than treating the final Allow/Deny as enough.

436. `RS-GR-413`  
   [Amazon Web Services (2026), *IsAuthorized — Amazon Verified Permissions API Reference*](https://docs.aws.amazon.com/verifiedpermissions/latest/apireference/API_IsAuthorized.html)  
   Relevance: current Verified Permissions API documentation says authorization responses return a decision plus determining policies and evaluation errors, which supports preserving compact replay diagnostics explicitly rather than retaining only the top-line verdict.

437. `RS-GR-414`  
   [Birkholz et al. (2023), *Remote ATtestation procedureS (RATS) Architecture* (RFC 9334)](https://www.rfc-editor.org/rfc/rfc9334.html)  
   Relevance: RFC 9334 defines Reference Values as the values against which claims are compared, Endorsements as verifier-consumed secure statements about an Attester's capabilities, and Attestation Results as verifier outputs, which supports preserving appraisal-input corpora explicitly rather than retaining only the final result.

438. `RS-GR-415`  
   [Birkholz et al. (2026), *Concise Reference Integrity Manifest* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-rats-corim-10)  
   Relevance: the current CoRIM draft says Reference Values and Endorsements are required for verifier reconciliation and that matched reference values add the CoRIM issuer's authority into the reconciled appraisal claims set, which supports preserving baseline corpora as trust-bearing inputs rather than disposable lookups.

439. `RS-GR-416`  
   [Thaler et al. (2026), *Reference Values and Endorsements for Remote Attestation Procedures* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-rats-endorsements-09)  
   Relevance: the current RATS endorsements draft distinguishes actual state from reference state, treats trust anchors as reference state, supports conditional endorsements, and allows multiple endorsers across layers, which supports preserving baseline composition explicitly rather than assuming one static known-good set.

440. `RS-GR-417`  
   [Birkholz et al. (2026), *Reference Interaction Models for Remote Attestation Procedures* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-rats-reference-interaction-models-15)  
   Relevance: the current reference-interaction draft says verifier inputs require Reference Values, Endorsements, and Appraisal Policy for Evidence and that claim selection can filter which claims are collected, which supports preserving appraisal-input scope explicitly rather than treating evidence collection as fixed background.

441. `RS-GR-418`  
   [Sigstore (2026), *Security Model*](https://docs.sigstore.dev/about/security/)  
   Relevance: current Sigstore security-model documentation says the Sigstore Trust Root secures the keys and certificates used to verify Fulcio certificates and Rekor entries, which supports preserving trust-root corpus identity explicitly rather than treating verification services as self-authenticating.

442. `RS-GR-419`  
   [Sigstore (2026), *Kubernetes Policy Controller*](https://docs.sigstore.dev/policy-controller/overview/)  
   Relevance: current Sigstore policy-controller documentation says TrustRoots may come from a remote TUF root that stays updated automatically, a serialized TUF repository for air-gap scenarios that must be rotated manually, or out-of-band keys / certificates, which supports preserving baseline refresh path explicitly rather than assuming all verifiers inherit the same current trust material.

443. `RS-GR-420`  
   [Open Policy Agent (2026), *Bundles*](https://www.openpolicyagent.org/docs/management-bundles)  
   Relevance: current OPA bundle documentation says policies and related data are loaded from bundles and enforced immediately once loaded, which supports preserving policy-data baselines explicitly rather than treating policy text alone as the whole rulebook.

444. `RS-GR-421`  
   [Birkholz et al. (2023), *Remote ATtestation procedureS (RATS) Architecture* (RFC 9334)](https://www.rfc-editor.org/rfc/rfc9334.html)  
   Relevance: RFC 9334 defines Evidence as Attester-produced information appraised by a Verifier, distinguishes Passport and Background-Check topological patterns, and treats freshness / trust relationships as architectural concerns, which supports preserving evidence-acquisition topology explicitly rather than retaining only post hoc verdicts.

445. `RS-GR-422`  
   [Birkholz et al. (2026), *Reference Interaction Models for Remote Attestation Procedures* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-ietf-rats-reference-interaction-models-15)  
   Relevance: the current reference-interaction draft makes Handle and optional Claim Selection part of the evidence request, cryptographically binds Claims / Handle / Attester identity into Evidence, distinguishes passport versus background-check flows, and defines uni-directional / streaming / brokered collection models, which supports preserving acquisition mode and collection scope explicitly rather than assuming one generic evidence path.

446. `RS-GR-423`  
   [Wallace et al. (2024), *The Entity Attestation Token (EAT)* (RFC 9711)](https://www.rfc-editor.org/rfc/rfc9711.html)  
   Relevance: RFC 9711 says all EAT use MUST provide a freshness mechanism, the EAT nonce supports multistage verification, and the nonce MUST have at least 64 bits of entropy, which supports preserving freshness-binding quality explicitly rather than treating replay resistance as ambient background.

447. `RS-GR-424`  
   [Tschofenig et al. (2025), *Nonce-based Freshness for Remote Attestation in Certificate Signing Requests (CSRs) for the Certification Management Protocol (CMP), for Enrollment over Secure Transport (EST), and for Certificate Management over CMS (CMC)* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/draft-ietf-lamps-attestation-freshness/)  
   Relevance: the current attestation-freshness draft reiterates the nonce entropy and privacy-preserving randomness requirements when Evidence is embedded inside CSR workflows, which supports preserving freshness provenance explicitly even when attestation is nested inside another protocol.

448. `RS-GR-425`  
   [in-toto project (2026), *in-toto-run — in-toto 3.0.0 documentation*](https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-run.html)  
   Relevance: current in-toto-run documentation says link metadata can capture materials, products, executed command, return value, stdout, stderr, and even no-command sign-off steps, which supports preserving observation-field scope explicitly rather than treating evidence capture as self-defining.

449. `RS-GR-426`  
   [in-toto project (2026), *in-toto-verify — in-toto 3.0.0 documentation*](https://in-toto.readthedocs.io/en/stable/command-line-tools/in-toto-verify.html)  
   Relevance: current in-toto-verify documentation requires step link metadata, thresholded link presence, authorized functionary signatures, artifact-rule compliance, and isolated local verification, which supports preserving admissible evidence form and verification boundary explicitly rather than collapsing everything into a single pass/fail story.

450. `RS-GR-427`  
   [in-toto project (2026), *API — in-toto 3.0.0 documentation*](https://in-toto.readthedocs.io/en/latest/api.html)  
   Relevance: current in-toto API documentation says `in_toto_record_start` / `in_toto_record_stop` can preserve preliminary versus final link metadata, command / byproducts, and environment information for steps not capturable by one wrapped command, which supports preserving capture staging and environment scope explicitly rather than assuming every evidence item has one obvious observation boundary.

451. `RS-GR-428`  
   [Fett et al. (2025), *Selective Disclosure for JSON Web Tokens* (RFC 9901)](https://www.rfc-editor.org/rfc/rfc9901.html)  
   Relevance: RFC 9901 defines selective disclosure for JSON payload elements, validates holder-selected disclosures, allows decoy digests to conceal the original number or conditional presence of claims, and forbids selectively disclosing authenticity-critical content, which supports preserving omission semantics explicitly rather than treating absent fields as self-explanatory.

452. `RS-GR-429`  
   [Terbu et al. (2026), *SD-JWT-based Verifiable Digital Credentials* (IETF Internet-Draft)](https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/)  
   Relevance: the current SD-JWT VC draft says a Holder can decide which claims to release within issuer-defined bounds, which supports preserving holder-choice scope and issuer-defined disclosure boundaries explicitly rather than treating all undisclosed material as equally absent.

453. `RS-GR-430`  
   [W3C (2025), *Verifiable Credentials Data Model v2.0*](https://www.w3.org/TR/vc-data-model-2.0/)  
   Relevance: VC Data Model v2.0 says holders can use selective disclosure and zero-knowledge proofs to provide precisely the information a verifier needs and nothing more, supports derived predicates such as age thresholds, and describes the ideal verifier as recording that a disclosure requirement was met and discarding sensitive data, which supports preserving disclosure granularity and retention posture explicitly rather than retaining only raw presented bytes.

454. `RS-GR-431`  
   [W3C (2025), *Verifiable Credential Data Integrity 1.0*](https://www.w3.org/TR/vc-data-integrity/)  
   Relevance: VC Data Integrity 1.0 says applications choose cryptography suites according to whether they need full, selective, or unlinkable disclosure, which supports preserving disclosure mode explicitly rather than treating all valid presentations as semantically equivalent.

455. `RS-GR-432`  
   [W3C (2025), *Data Integrity BBS Cryptosuites v1.0*](https://www.w3.org/TR/vc-di-bbs/)  
   Relevance: the current BBS cryptosuite separates mandatory from non-mandatory statements, carries mandatory and selective index information through derived proof processing, and targets unlinkable proof artifacts, which supports preserving mandatory-vs-optional reveal rules and correlation posture explicitly rather than retaining only the final derived proof.

456. `RS-GR-433`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 defines claims-query and claim-selection logic, treats value-restricted claims that do not match as though they did not exist in the credential, and includes an `intent_to_retain` parameter for ISO mdoc claim requests, which supports preserving omission and retention semantics explicitly rather than reading field absence as simple nonexistence.


457. `RS-GR-434`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says each DCQL claim query can carry a stable id, claim-path pointer, optional expected values, and holder-binding requirements inside a Credential Query, which supports preserving the original request contract explicitly rather than inferring it from the disclosed output alone.

458. `RS-GR-435`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says `claim_sets` and `credential_sets` let a Verifier describe alternative combinations that can satisfy a request, that their ordering expresses Verifier preference, and that `values` restrictions are best-effort privacy hints rather than security checks, which supports preserving alternative-satisfaction and preference semantics explicitly rather than treating one successful presentation as the only admissible answer.

459. `RS-GR-436`  
   [Decentralized Identity Foundation (2024), *Presentation Exchange 2.1.1*](https://identity.foundation/presentation-exchange/spec/v2.1.1/)  
   Relevance: Presentation Exchange 2.1.1 defines Submission Requirements with grouping, `pick`, `all`, and nested requirement logic, requires all submission requirements to be satisfied, and ignores unused descriptors once they are, which supports preserving combinatorial request logic explicitly rather than collapsing admissibility to the final disclosed claims.

460. `RS-GR-437`  
   [Decentralized Identity Foundation (2024), *Presentation Exchange 2.1.1*](https://identity.foundation/presentation-exchange/spec/v2.1.1/)  
   Relevance: Presentation Exchange 2.1.1 requires a `presentation_submission` with a `definition_id` plus `descriptor_map` entries containing descriptor ids, formats, JSONPath references, and optional nested traversal, which supports preserving a replayable satisfaction witness explicitly rather than retaining only the returned presentations.

461. `RS-GR-438`  
   [Gössner et al. (2024), *JSONPath: Query Expressions for JSON* (RFC 9535)](https://www.rfc-editor.org/rfc/rfc9535.html)  
   Relevance: RFC 9535 standardizes JSONPath as a concrete query language for selecting and extracting JSON values, which supports preserving path-language semantics explicitly rather than assuming claim-selection expressions will keep the same meaning forever.

462. `RS-GR-439`  
   [OpenID Foundation (2025), *OpenID Federation for Wallet Architectures 1.0* (draft 05)](https://openid.net/specs/openid-federation-wallet-1_0.html)  
   Relevance: the current OpenID Federation for Wallet Architectures draft allows verifier metadata to publish authorized DCQL queries for specific situations and allows policies to require a live query to equal or refine one of them, which supports preserving verifier-authorization boundaries explicitly rather than retaining only the raw request.

463. `RS-GR-440`  
   [OpenID Foundation (2025), *OpenID4VC High Assurance Interoperability Profile 1.0* (draft 04)](https://openid.net/specs/openid4vc-high-assurance-interoperability-profile-1_0-04.html)  
   Relevance: the current HAIP profile requires DCQL for OpenID4VP, mandates the `aki` trusted-authorities method, and for multiple ISO mdocs requires separate DeviceResponses matching respective DCQL queries, which supports preserving request-language profile choices and per-query response-mapping semantics explicitly rather than treating them as wallet-specific implementation detail.

464. `RS-GR-441`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says the `client_id` is used to detect replay of Verifiable Presentations to a party other than the intended one and says `nonce` binds the presentation to a specific authentication transaction, which supports preserving verifier-target and transaction-binding semantics explicitly rather than treating a valid presentation as globally reusable.

465. `RS-GR-442`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says that when a Wallet supplied a `wallet_nonce` during Request URI retrieval it must reject a Request Object that does not contain the same value, and says the Wallet must use only the parameters in that Request Object, which supports preserving request-fetch session binding and exact-object semantics explicitly rather than treating request retrieval as a harmless transport detail.

466. `RS-GR-443`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 requires `expected_origins` for signed requests over the Digital Credentials API and says the Wallet must compare them against the Verifier's Origin to detect replay from a malicious Verifier, which supports preserving origin-binding semantics explicitly rather than collapsing them into generic browser context.

467. `RS-GR-444`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says ISO mdoc `DeviceResponse` carries a signature or MAC over a `SessionTranscript` including an OpenID4VP-specific handover containing `clientId`, `nonce`, `jwkThumbprint`, and `responseUri`, which supports preserving authenticated session-transcript semantics explicitly rather than leaving response-channel binding outside the proof surface.

468. `RS-GR-445`  
   [Fett, Yasuda, & Campbell (2025), *Selective Disclosure for JSON Web Tokens* (RFC 9901)](https://www.rfc-editor.org/rfc/rfc9901.html)  
   Relevance: RFC 9901 says a Key Binding JWT signs over the presented SD-JWT package hash plus `nonce` and `aud`, and says Verifiers must validate `iat`, `nonce`, `aud`, and `sd_hash`, which supports preserving holder-proof verifier-targeting and transaction-binding semantics explicitly rather than treating key possession alone as sufficient.

469. `RS-GR-446`  
   [W3C (2025), *Verifiable Credential Data Integrity 1.0*](https://www.w3.org/TR/vc-data-integrity/)  
   Relevance: VC Data Integrity 1.0 says the `domain` proof option identifies the security domain in which a proof is meant to be used and says `challenge` should be used once for a domain and time window to mitigate replay, which supports preserving proof-option anti-misbinding and anti-replay semantics explicitly rather than treating them as optional decoration.

470. `RS-GR-447`  
   [Fett et al. (2023), *OAuth 2.0 Demonstrating Proof of Possession (DPoP)* (RFC 9449)](https://www.rfc-editor.org/rfc/rfc9449.html)  
   Relevance: RFC 9449 binds proof-of-possession to request method, request URI, creation time, optional nonce, and optionally the access-token hash, and says replay resistance still depends on endpoint / method checks plus time-window and replay checks, which supports preserving route-binding and replay-scope semantics explicitly rather than retaining only the signed proof token.

471. `RS-GR-448`  
   [OpenID Foundation (2026), *OpenID Federation 1.0*](https://openid.net/specs/openid-federation-1_0.html)  
   Relevance: OpenID Federation 1.0 says the final metadata for a participant is obtained from Trust Chain evaluation after applying metadata policies, which supports preserving the resolved metadata snapshot explicitly rather than retaining only a bare `client_id` or entity identifier.

472. `RS-GR-449`  
   [OpenID Foundation (2026), *OpenID Federation 1.0*](https://openid.net/specs/openid-federation-1_0.html)  
   Relevance: OpenID Federation 1.0 says a Trust Chain contains the subject configuration as it applies at chain-evaluation time, links signatures and `jwks` values statement-by-statement, and ends in a Trust Anchor distributed out of band, which supports preserving trust-chain material and evaluation-time context explicitly rather than treating resolved participant metadata as timeless.

473. `RS-GR-450`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says that when the `openid_federation` Client Identifier Prefix is used, OpenID Federation processing rules MUST be followed, the request MAY carry a `trust_chain`, the final Verifier metadata is obtained from the Trust Chain after policy application, and `client_metadata` MUST be ignored, which supports preserving metadata-resolution mode explicitly rather than collapsing all verifier metadata into one request object.

474. `RS-GR-451`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 defines multiple verifier-identification modes with different metadata and key-resolution rules — DID-based resolution, verifier attestation JWTs, X.509 SAN / hash chains, and unsigned `redirect_uri` flows — which supports preserving identifier-prefix-specific trust paths explicitly rather than treating all valid requests as if they were resolved the same way.

475. `RS-GR-452`  
   [W3C (2026), *Decentralized Identifier Resolution v0.3*](https://www.w3.org/TR/did-resolution/)  
   Relevance: DID Resolution v0.3 says DID resolution returns a DID document plus associated metadata such as content type, proof, and versioning, and says historical state can be obtained for audit purposes, which supports preserving DID-resolution inputs and outputs explicitly rather than retaining only the DID string.

476. `RS-GR-453`  
   [OpenID Foundation (2023), *OpenID Connect Discovery 1.0 incorporating errata set 2*](https://openid.net/specs/openid-connect-discovery-1_0.html)  
   Relevance: OpenID Connect Discovery 1.0 says that if configuration-validation procedures fail, operations requiring that information MUST be aborted and the invalid information MUST NOT be used, which supports preserving discovery-validation outcomes explicitly rather than keeping only fetched metadata blobs.

477. `RS-GR-454`  
   [Jones et al. (2018), *OAuth 2.0 Authorization Server Metadata* (RFC 8414)](https://www.rfc-editor.org/rfc/rfc8414.html)  
   Relevance: RFC 8414 says authorization-server metadata provides endpoint locations and capabilities and allows optional `signed_metadata`, which supports preserving both resolved capability surfaces and whether metadata was merely fetched or cryptographically vouched for.

478. `RS-GR-455`  
   [Lodderstedt et al. (2025), *Best Current Practice for OAuth 2.0 Security* (RFC 9700)](https://www.rfc-editor.org/rfc/rfc9700.txt)  
   Relevance: RFC 9700 recommends using OAuth Authorization Server Metadata because it reduces endpoint / security-feature misconfiguration and facilitates key rotation and crypto agility, which supports treating metadata-resolution continuity as a first-class security dependency rather than as optional convenience plumbing.


479. `RS-GR-456`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 defines `vp_formats_supported` as required Wallet metadata and lets Wallets / Verifiers advertise format-specific parameters such as supported algorithms, proof types, cryptosuites, and Client Identifier Prefixes, which supports preserving the advertised negotiation surface explicitly rather than retaining only the finally chosen presentation.

480. `RS-GR-457`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 lets Wallets declare supported request-object signing algorithms and request / response encryption algorithms for Request URI processing and requires `wallet_nonce` continuity when that path is used, which supports preserving the chosen request-protection profile explicitly rather than treating it as invisible transport detail.

481. `RS-GR-458`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says Wallets must error on `expected_origins` mismatch and must reject unauthorized `transaction_data` types as unsupported, which supports preserving hard-failure semantics for unsupported or downgraded capability asks explicitly rather than assuming best-effort fallback.

482. `RS-GR-459`  
   [Jones, Sakimura, & Bradley (2018), *OAuth 2.0 Authorization Server Metadata* (RFC 8414)](https://www.rfc-editor.org/rfc/rfc8414.html)  
   Relevance: RFC 8414 publishes capability metadata such as `response_types_supported`, `response_modes_supported`, and `grant_types_supported`, which supports preserving the response-path and grant-selection lattice explicitly rather than retaining only one observed path.

483. `RS-GR-460`  
   [Sheffer, Hardt, & Jones (2020), *JSON Web Token Best Current Practices* (RFC 8725)](https://www.rfc-editor.org/rfc/rfc8725.html)  
   Relevance: RFC 8725 says libraries must verify algorithms against an application-specified allowlist and recommends explicit typing for new JWT uses, which supports preserving the selected algorithm / token-type profile explicitly rather than letting attacker-chosen headers define the effective negotiation result.

484. `RS-GR-461`  
   [Lodderstedt et al. (2021), *The OAuth 2.0 Authorization Framework: JWT-Secured Authorization Request (JAR)* (RFC 9101)](https://www.rfc-editor.org/rfc/rfc9101.html)  
   Relevance: RFC 9101 applies explicit typing to request objects and recommends distinct key-management regimes to prevent cross-JWT confusion, which supports preserving protected-request profile and key-regime continuity explicitly rather than recording only that a request object verified.

485. `RS-GR-462`  
   [OpenID Foundation (2025), *OpenID for Verifiable Credential Issuance 1.0*](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)  
   Relevance: OpenID4VCI 1.0 publishes `credential_request_encryption` / `credential_response_encryption` requirements and `credential_configurations_supported` objects containing format, signing algorithms, cryptographic binding methods, proof types, and optional key-attestation constraints, which supports preserving the exact chosen credential profile explicitly rather than treating issuer compatibility as a yes/no fact.

486. `RS-GR-463`  
   [OpenID Foundation (2025), *OpenID for Verifiable Credential Issuance 1.0*](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)  
   Relevance: OpenID4VCI 1.0 defines fail-closed errors such as `unknown_credential_configuration`, `invalid_proof`, and `invalid_encryption_parameters`, and says deferred credential request encryption must be used to prevent substitution when response-encryption parameters are involved, which supports preserving downgrade / mismatch failure semantics explicitly rather than assuming all interoperable parties will converge on a safe fallback.

487. `RS-GR-464`  
   [W3C (2026), *Web Authentication: An API for accessing Public Key Credentials - Level 3*](https://www.w3.org/TR/webauthn-3/)  
   Relevance: WebAuthn Level 3 carries User Present (UP), User Verified (UV), and backup-eligibility / backup-state bits in authenticator data, which supports preserving per-transaction user-control and syncability semantics explicitly rather than treating all valid assertions as assurance-equivalent.

488. `RS-GR-465`  
   [W3C (2026), *Web Authentication: An API for accessing Public Key Credentials - Level 3*](https://www.w3.org/TR/webauthn-3/)  
   Relevance: WebAuthn Level 3 says a relying party may use the AAGUID to infer properties such as certification level and key-protection strength but that the AAGUID is not provably authentic without attestation, which supports separating authenticator-class inference from authenticator-class proof explicitly rather than collapsing them together.

489. `RS-GR-466`  
   [NIST (2025), *SP 800-63B: Authentication and Lifecycle Management*](https://pages.nist.gov/800-63-4/sp800-63b.html)  
   Relevance: the current NIST SP 800-63B guidance says verifiers should inspect WebAuthn UP and UV flags and may use backup-eligibility to distinguish device-bound authenticators from syncable ones, which supports preserving local user-verification and exportability state explicitly rather than treating key possession as a complete assurance story.

490. `RS-GR-467`  
   [NIST (2025), *SP 800-63B: Authentication and Lifecycle Management*](https://pages.nist.gov/800-63-4/sp800-63b.html)  
   Relevance: the current NIST SP 800-63B guidance says AAL3 requires a phishing-resistant cryptographic authenticator with a non-exportable private key, requires authentication intent, and disallows syncable authenticators, which supports preserving non-exportability and per-transaction intent semantics explicitly rather than inferring them from a bare cryptographic success.

491. `RS-GR-468`  
   [OpenID Foundation (2025), *OpenID for Verifiable Credential Issuance 1.0*](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)  
   Relevance: OpenID4VCI 1.0 key attestations can carry attested keys, key-storage claims, user-authentication resistance claims, freshness nonce, and status information, which supports preserving authenticator and key-container assurances explicitly rather than collapsing all holder keys into one credential-binding bucket.

492. `RS-GR-469`  
   [OpenID Foundation (2025), *OpenID4VC High Assurance Interoperability Profile 1.0*](https://openid.net/specs/openid4vc-high-assurance-interoperability-profile-1_0.html)  
   Relevance: the current HAIP profile requires wallet support for key attestations and specifies interoperable use of `jwt` plus `key_attestation` or `attestation` proof types, which supports preserving the distinction between bare proof-of-possession and attested key provenance explicitly rather than treating them as the same assurance level.

493. `RS-GR-470`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says a verifier may request a credential without proof of cryptographic holder binding and explicitly accepts replay risk when it does so, which supports preserving holder-binding-required versus holder-binding-waived semantics explicitly rather than assuming every valid presentation had the same possession guarantees.

494. `RS-GR-471`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 defines a `transaction_data` mechanism that binds the user's identification / authentication to the user's authorization for cases such as payments or document signing, which supports preserving transaction-specific approval semantics explicitly rather than retaining only a generic presentation proof.

495. `RS-GR-472`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 defines `transaction_data_hashes` so each hash maps to and integrity-protects one transaction-data object and requires those hashes to be included in the credential proof-of-possession mechanism, which supports preserving exact approval-object linkage explicitly rather than recording only session context.

496. `RS-GR-473`  
   [Lodderstedt, Richer, & Campbell (2023), *OAuth 2.0 Rich Authorization Requests* (RFC 9396)](https://www.rfc-editor.org/rfc/rfc9396.html)  
   Relevance: RFC 9396 defines `authorization_details` for fine-grained authorization data and says the authorization server asks the user for consent to the requested permissions and that the user may grant a subset, which supports preserving granted-subset semantics explicitly rather than storing only the original request.

497. `RS-GR-474`  
   [Lodderstedt, Richer, & Campbell (2023), *OAuth 2.0 Rich Authorization Requests* (RFC 9396)](https://www.rfc-editor.org/rfc/rfc9396.html)  
   Relevance: RFC 9396 says there is no standardized simple mechanism to compare arbitrary `authorization_details` requests and that servers should not rely on naive object comparison, which supports preserving transaction-type comparison rules explicitly rather than assuming bytewise or fieldwise similarity means same approval.

498. `RS-GR-475`  
   [Sakimura, Bradley, & Jones (2021), *The OAuth 2.0 Authorization Framework: JWT-Secured Authorization Request (JAR)* (RFC 9101)](https://www.rfc-editor.org/rfc/rfc9101.html)  
   Relevance: RFC 9101 allows authorization requests to be signed and optionally encrypted Request Objects so integrity, source authentication, and confidentiality of the approval object are protected, which supports preserving request-object protection posture explicitly rather than reconstructing approval state after the fact.

499. `RS-GR-476`  
   [Lodderstedt et al. (2021), *OAuth 2.0 Pushed Authorization Requests* (RFC 9126)](https://www.rfc-editor.org/rfc/rfc9126.html)  
   Relevance: RFC 9126 lets clients push the authorization request payload directly to the authorization server, notes that front-channel parameters otherwise lack cryptographic integrity and can even let an attacker swap payment context, and returns a `request_uri` reference, which supports preserving approval-object tamper-resistance explicitly rather than assuming the browser-carried ask stayed fixed.

500. `RS-GR-477`  
   [NIST (2025), *SP 800-63B: Authentication and Lifecycle Management*](https://pages.nist.gov/800-63-4/sp800-63b.html)  
   Relevance: the current NIST SP 800-63B guidance defines authentication intent as requiring the claimant to respond explicitly to each authentication or reauthentication request, which supports preserving what the user action was approving explicitly rather than treating any successful user gesture as semantically interchangeable.


501. `RS-GR-478`  
   [OpenID Foundation (2025), *OpenID Connect Core 1.0 - draft 36 incorporating errata set 3*](https://openid.net/specs/openid-connect-core-1_0-36.html)  
   Relevance: OpenID Connect Core says pairwise Subject Identifiers must be unique for each Sector Identifier and must not be reversible by any party other than the OpenID Provider, which supports preserving identifier-stability scope explicitly rather than treating every valid `sub` value as globally linkable.

502. `RS-GR-479`  
   [OpenID Foundation (2023), *OpenID Connect Dynamic Client Registration 1.0 - draft 38*](https://openid.net/specs/openid-connect-registration-1_0-38.html)  
   Relevance: Dynamic Client Registration says the `sector_identifier_uri` lets a group of sites under single administrative control share consistent pairwise subject values independent of their domain names, which supports preserving sector-scoped correlation boundaries explicitly rather than treating “pairwise” as automatically per-site.

503. `RS-GR-480`  
   [W3C (2025), *Data Integrity BBS Cryptosuites v1.0*](https://www.w3.org/TR/vc-di-bbs/)  
   Relevance: Data Integrity BBS Cryptosuites v1.0 says BBS signatures provide selective disclosure and unlinkable derived proofs, which supports preserving proof-family linkability posture explicitly rather than treating all selective-disclosure presentations as privacy-equivalent.

504. `RS-GR-481`  
   [W3C (2025), *Data Integrity ECDSA Cryptosuites v1.0*](https://www.w3.org/TR/vc-di-ecdsa/)  
   Relevance: Data Integrity ECDSA Cryptosuites v1.0 explicitly says its suites do not support unlinkable disclosure and points to the BBS cryptosuite when unlinkability is desired, which supports preserving whether repeated presentations remained linkable even when claim sets were minimized.

505. `RS-GR-482`  
   [Campbell et al. (2025), *Selective Disclosure for JWTs* (RFC 9901)](https://www.rfc-editor.org/rfc/rfc9901.html)  
   Relevance: RFC 9901 says decoy digests are a trade-off between payload size and the privacy of the user's data, which supports preserving padding / decoy posture explicitly rather than assuming hidden structure is inference-resistant by default.

506. `RS-GR-483`  
   [Campbell et al. (2025), *Selective Disclosure for JWTs* (RFC 9901)](https://www.rfc-editor.org/rfc/rfc9901.html)  
   Relevance: RFC 9901 says an issuer that issues only one type of SD-JWT can have privacy implications because the type and claim names can then be determined, which supports preserving issuer / type leakage posture explicitly rather than treating selective disclosure as sufficient for unlinkability.

507. `RS-GR-484`  
   [W3C (2025), *Bitstring Status List v1.0*](https://www.w3.org/TR/vc-bitstring-status-list/)  
   Relevance: Bitstring Status List v1.0 defines a privacy-preserving, space-efficient, high-performance mechanism for publishing credential status information, which supports preserving status-check privacy architecture explicitly rather than assuming every revocation or suspension path has the same observer surface.

508. `RS-GR-485`  
   [W3C (2026), *Threat Model for Decentralized Credentials*](https://www.w3.org/TR/threat-model-decentralized-credentials/)  
   Relevance: the current W3C Threat Model for Decentralized Credentials treats Verifiable, Minimal, and Unlinkable as distinct privacy properties in the credential-presentation phase, which supports preserving correlation scope explicitly rather than collapsing privacy to “valid and selectively disclosed”.


509. `RS-GR-486`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 defines `direct_post` and `direct_post.jwt` so a Wallet can send the Authorization Response to a Verifier-controlled `response_uri` via HTTPS POST instead of redirect-only delivery, which supports preserving whether request / response payloads moved through front-channel URLs or protected body delivery.

510. `RS-GR-487`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 warns that plain `direct_post` is susceptible to session-fixation style attacks because the result is sent out-of-band to the Verifier's `response_uri`, recommends strengthened mechanisms such as redirect-bound response codes, and says Wallets must ensure Authorization Response data cannot leak through Response URIs, which supports preserving delivery-path observer surfaces explicitly rather than treating every valid response mode as confidentiality-equivalent.

511. `RS-GR-488`  
   [OpenID Foundation (2025), *OpenID4VC High Assurance Interoperability Profile 1.0*](https://openid.net/specs/openid4vc-high-assurance-interoperability-profile-1_0.html)  
   Relevance: HAIP 1.0 requires signed Authorization Requests via JAR with `request_uri` and requires response encryption via `direct_post.jwt`, which supports preserving chosen delivery-path confidentiality posture explicitly rather than assuming high-assurance ecosystems only care about credential semantics.

512. `RS-GR-489`  
   [Fett et al. (2021), *The OAuth 2.0 Authorization Framework: JWT-Secured Authorization Request* (RFC 9101)](https://www.rfc-editor.org/rfc/rfc9101.html)  
   Relevance: RFC 9101 says JAR lets authorization requests be signed and encrypted so integrity, source authentication, and confidentiality are attained, which supports preserving whether the ask itself was exposed to browsers or intermediaries in plaintext.

513. `RS-GR-490`  
   [Lodderstedt et al. (2021), *OAuth 2.0 Pushed Authorization Requests* (RFC 9126)](https://datatracker.ietf.org/doc/html/rfc9126)  
   Relevance: RFC 9126 lets clients push the authorization-request payload directly to the authorization server and then send only a `request_uri` reference through the user agent, which supports preserving backchannel-versus-front-channel request exposure explicitly rather than assuming all request transport paths have the same observer surface.

514. `RS-GR-491`  
   [Lodderstedt et al. (2025), *Best Current Practice for OAuth 2.0 Security* (RFC 9700)](https://datatracker.ietf.org/doc/html/rfc9700)  
   Relevance: RFC 9700 says authorization codes in redirect URLs can end up in browser history and names form-post response mode as a countermeasure, which supports preserving whether sensitive response material transited URL-based browser surfaces rather than body-only delivery.

515. `RS-GR-492`  
   [Lodderstedt et al. (2025), *Best Current Practice for OAuth 2.0 Security* (RFC 9700)](https://datatracker.ietf.org/doc/html/rfc9700)  
   Relevance: RFC 9700 says access tokens can end up in browser history when passed in query parameters and states that such modes are now considered less secure or insecure, which supports preserving URL/query exposure posture explicitly rather than treating every transport route for valid artifacts as risk-equivalent.


516. `RS-GR-493`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says a Wallet SHOULD NOT return protocol errors before End-User consent when value matching or issuer selection would reveal sensitive information, and says consent also protects against undetected repeated requests, which supports preserving not only the request object but the pre-consent disclosure and approval-ceremony semantics.

517. `RS-GR-494`  
   [OpenID Foundation (2025), *OpenID for Verifiable Credential Issuance 1.0*](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)  
   Relevance: OpenID4VCI 1.0 defines claim-description metadata specifically for how claims are displayed to the End-User, including localized `display` objects with `name` and `locale`, which supports preserving the human-readable rendering contract rather than only raw claim paths.

518. `RS-GR-495`  
   [OpenID Foundation (2025), *OpenID for Verifiable Credential Issuance 1.0*](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)  
   Relevance: OpenID4VCI 1.0 says the order of claim-description objects determines the order in which claims are displayed to the End-User and that contradictory display descriptions must abort processing, which supports preserving rendering order and contradiction-handling as part of approval continuity.

519. `RS-GR-496`  
   [W3C (2024), *Secure Payment Confirmation*](https://www.w3.org/TR/secure-payment-confirmation/)  
   Relevance: Secure Payment Confirmation is designed to produce cryptographic evidence that the user confirmed transaction details, and it defines user-visible transaction fields such as instrument, payee name/origin, and total, which supports preserving the rendered approval surface rather than only the backend transaction object.

520. `RS-GR-497`  
   [W3C (2024), *Secure Payment Confirmation*](https://www.w3.org/TR/secure-payment-confirmation/)  
   Relevance: Secure Payment Confirmation warns that third parties can supply the transaction details shown to the user and gives a concrete spoofing example where the backend says $100 but the user is shown $1, which supports preserving whether the rendered approval surface was trusted, verified, and compared back to the authoritative transaction.

521. `RS-GR-498`  
   [NIST (2025), *SP 800-63B-4: Authentication and Authenticator Management*](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf)  
   Relevance: NIST SP 800-63B-4 says authentication intent requires an explicit response to each authentication request and that some biometric captures need an additional explicit action such as tapping a software or physical button, which supports preserving how the approval ceremony established intentional user action rather than passive capture.

522. `RS-GR-499`  
   [IETF (2025), *RFC 9700: Best Current Practice for OAuth 2.0 Security*](https://datatracker.ietf.org/doc/html/rfc9700)  
   Relevance: RFC 9700 says authorization interfaces are susceptible to clickjacking and user-interface redressing that can change granted scope or steal credentials, and requires authorization servers to prevent those attacks, which supports preserving whether the approval UI was frame-protected and trustable.

523. `RS-GR-500`  
   [W3C (2024), *Secure Payment Confirmation*](https://www.w3.org/TR/secure-payment-confirmation/)  
   Relevance: Secure Payment Confirmation includes locale-preference input for language negotiation and locale-affected formatting, while also reserving rendering control to the user agent for logos and presentation details, which supports preserving locale, formatting, and trusted-renderer semantics rather than assuming one machine object implies one human-visible approval.


524. `RS-GR-501`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says an Authorization Request can be passed across devices by rendering it as a QR Code and recommends `direct_post` together with `request_uri` for that case, which supports preserving whether a ceremony depended on cross-device QR transfer, by-reference request carriage, and out-of-band response return rather than treating device split as UI garnish.

525. `RS-GR-502`  
   [OpenID Foundation (2023), *Self-Issued OpenID Provider v2*](https://openid.net/specs/openid-connect-self-issued-v2-1_0-12.html)  
   Relevance: SIOPv2 distinguishes same-device from cross-device protocol models and says cross-device flows cannot use HTTP redirects through a user agent, requiring the wallet to send the Authorization Response directly to an RP endpoint, which supports preserving device split and response topology explicitly rather than assuming one presentation ceremony fits all transport assumptions.

526. `RS-GR-503`  
   [OpenID Foundation (2023), *Self-Issued OpenID Provider v2*](https://openid.net/specs/openid-connect-self-issued-v2-1_0-12.html)  
   Relevance: SIOPv2 says that at first interaction the RP usually cannot robustly determine the wallet URI, so invocation may be untargeted QR/deep-link scanning or a targeted `authorization_endpoint` launch, which supports preserving whether a ceremony depended on manual wallet selection versus pre-targeted app invocation.

527. `RS-GR-504`  
   [OpenID Foundation (2023), *Self-Issued OpenID Provider v2*](https://openid.net/specs/openid-connect-self-issued-v2-1_0-12.html)  
   Relevance: SIOPv2 allows a wallet `authorization_endpoint` to be a custom URL scheme or a claimed HTTPS URL such as a Universal Link or App Link, which supports preserving the concrete invocation route rather than collapsing all app launches into one generic “wallet opened” event.

528. `RS-GR-505`  
   [Denniss & Bradley (2017), *OAuth 2.0 for Native Apps* (RFC 8252)](https://www.rfc-editor.org/rfc/rfc8252.html)  
   Relevance: RFC 8252 says app-claimed HTTPS redirect URIs have security advantages because the operating system guarantees the destination app, while private-use URI schemes can suffer interception or collision risk, which supports preserving app-invocation identity posture rather than treating every redirect or deep link as equally trustworthy.

529. `RS-GR-506`  
   [FIDO Alliance (2025), *Client to Authenticator Protocol (CTAP) v2.2*](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html)  
   Relevance: CTAP 2.2 says hybrid transport decouples physical-proximity proof from message transport, using a tunnel service for network carriage and BLE to show co-presence, which supports preserving not only whether a ceremony was cross-device but how co-presence was actually established.

530. `RS-GR-507`  
   [FIDO Alliance (2025), *Client to Authenticator Protocol (CTAP) v2.2*](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html)  
   Relevance: CTAP 2.2 says QR-initiated hybrid transactions require proof of proximity via BLE advertisement to help prevent attacks, which supports preserving whether a QR-started ceremony had explicit proximity evidence or only a human scan.

531. `RS-GR-508`  
   [NIST (2025), *SP 800-63B-4: Authentication and Authenticator Management*](https://pages.nist.gov/800-63-4/sp800-63b.html)  
   Relevance: NIST SP 800-63B-4 says an out-of-band channel remains distinct only if the device does not leak information between channels without claimant participation, allows primary-to-secondary transfer via manual entry or QR code, and rejects fatigue-prone approval-only patterns, which supports preserving whether a multi-device or multi-channel ceremony actually required active cross-channel participation.

532. `RS-GR-509`  
   [RFC Editor (2020), *RFC 8785: JSON Canonicalization Scheme (JCS)*](https://www.rfc-editor.org/rfc/rfc8785)  
   Relevance: RFC 8785 says canonicalization creates an invariant, hashable JSON representation by constraining input to I-JSON, using strict primitive serialization, deterministic property sorting, and UTF-8 output, which supports deriving stable compact digests from successor-safe ceremony receipts instead of re-copying their bodies into every downstream note.

533. `RS-GR-510`  
   [RFC Editor (2013), *RFC 6920: Naming Things with Hashes*](https://www.rfc-editor.org/rfc/rfc6920.html)  
   Relevance: RFC 6920 defines `ni` identifiers that name a digital object by hash while keeping retrieval separate from identity, which supports shipping tiny content-addressed locator companions for successor-safe ceremony receipts so future sessions can cite stable handles rather than duplicate the receipt text.


534. `RS-GR-511`  
   [OpenID Foundation (2025), *OpenID for Verifiable Presentations 1.0*](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)  
   Relevance: OpenID4VP 1.0 says `direct_post` without the extra protection of a redirect URI leaves the Verifier without session context to detect fixation attempts and recommends strengthening the flow, which supports machine-checking whether a retained ceremony receipt names the session-mapping and anti-fixation material rather than only saying “direct POST happened.”

535. `RS-GR-512`  
   [NIST (2025), *SP 800-63B-4: Authentication and Authenticator Management*](https://pages.nist.gov/800-63-4/sp800-63b.html)  
   Relevance: NIST SP 800-63B-4 says phishing resistance requires cryptographic binding to the authenticated verifier and session (through channel binding or verifier name binding), which supports machine-checking that successor-safe ceremony receipts name the concrete verifier / audience / session binding rather than remaining structurally valid but replay-ambiguous.

536. `RS-GR-513`  
   [IETF (2021), *RFC 9126: OAuth 2.0 Pushed Authorization Requests*](https://www.rfc-editor.org/rfc/rfc9126.html)  
   Relevance: RFC 9126 says PAR gives a confidential, integrity-protected authorization request and authenticates the client before user interaction, which supports machine-checking that any receipt using `request_uri`-style indirection states whether the authoritative ask lived behind PAR, JAR, or another protected fetch path.

537. `RS-GR-514`  
   [NIST CSRC Glossary, *Risk Response*](https://csrc.nist.gov/glossary/term/risk_response)  
   Relevance: NIST defines risk response as an intentional and informed decision to accept, avoid, mitigate, share, or transfer identified risk, which supports collapsing a successor-safe ceremony receipt assessment into an explicit archive disposition instead of leaving warning and fail findings as unlabeled prose.

538. `RS-GR-515`  
   [NIST CSRC, *RMF Assess Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/05-assess%20step/nist%20rmf%20assess%20step-faqs.pdf)  
   Relevance: NIST's RMF Assess Step FAQ says a Plan of Action and Milestones details remediation plans for unacceptable risks identified in assessment findings, which supports requiring tiny required-action lists beside warned or failed successor-safe ceremony receipts rather than treating the findings as self-closing.

539. `RS-GR-516`  
   [NIST CSRC, *RMF Assess Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/05-assess%20step/nist%20rmf%20assess%20step-faqs.pdf)  
   Relevance: NIST's RMF Assess Step FAQ says a POA&M details remediation plans for unacceptable risks, can include mitigating tasks, resources, milestones, and schedule, and is used to trace risk mitigation as tasks are completed, which supports collapsing weak successor-safe ceremony receipts into tiny closure-oriented remediation plans rather than leaving findings as ambient backlog.

540. `RS-GR-517`  
   [NIST CSRC, *What is OSCAL and Who Needs It?*](https://csrc.nist.gov/csrc/media/Events/2022/3rd-oscal-workshop/documents/1.2%20-%20Main%20-%20NIST_OSCAL-What_is_and_Who_needs_it.pdf)  
   Relevance: NIST's OSCAL overview shows POA&M items as structured objects carrying unique IDs, weakness details, remediation activities, schedule, status, evidence, and citations, which supports keeping successor-safe ceremony receipt remediation plans small, machine-checkable, and evidence-linked instead of freeform prose.

541. `RS-GR-518`  
   [NIST CSRC, *RMF QSG: Authorize Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/06-authorize%20step/nist%20rmf%20authorize%20step-faqs.pdf)  
   Relevance: NIST's RMF Authorize Step FAQ says authorization decisions are made from the current security and privacy posture, residual risk, and POA&Ms and are issued with terms and conditions, which supports collapsing a successor-safe ceremony receipt package into one explicit claim-ready authorization decision instead of leaving final admission implicit.

542. `RS-GR-519`  
   [NIST CSRC, *RMF Assess Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/05-assess%20step/nist%20rmf%20assess%20step-faqs.pdf)  
   Relevance: NIST's RMF Assess Step FAQ says controls may be reassessed to verify that deficiencies were corrected and to identify residual risk, which supports requiring any claim-ready authorization decision to rest on a current assessment plus closed blocking remediation rather than stale repair intent alone.

543. `RS-GR-520`  
   [NIST CSRC, *RMF QSG: Monitor Step FAQs*](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf)  
   Relevance: NIST's RMF Monitor Step FAQ says that when weaknesses or deficiencies are corrected, the remediated controls are reassessed to verify that they are implemented correctly, operate as intended, and produce the desired outcome, which supports keeping a tiny promotion record that proves a successor-safe ceremony receipt package actually improved rather than merely changed labels.

544. `RS-GR-521`  
   [NIST Pages, *OSCAL Assessment Layer: Plan of Action and Milestones Model*](https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/poam/)  
   Relevance: NIST's OSCAL POA&M model says remediation planning and tracking should preserve discovery source, recommendations, remediation progress, and disposition status, which supports keeping a compact prior-versus-current promotion record beside successor-safe ceremony receipt packages so future stewards can see closure, carry-over, or regression without replaying the whole repair history.
545. `RS-GR-522`  
   [NIST CSRC, *RMF QSG: Monitor Step FAQs*](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf)  
   Relevance: NIST's RMF Monitor Step FAQ says automated support tools can support ongoing assessments and ongoing authorizations, and that continuous monitoring can let an authorizing official determine the current state and whether to authorize continued operation, which supports shipping one compact review watch for claim-ready successor-safe ceremony receipts instead of assuming yesterday's authorization stays fresh forever.

546. `RS-GR-523`  
   [NIST CSRC, *RMF Assess Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/05-assess%20step/nist%20rmf%20assess%20step-faqs.pdf)  
   Relevance: NIST's RMF Assess Step FAQ says ongoing assessment supports the decision to continue or discontinue authorization and that controls are assessed on an ongoing basis according to continuous-monitoring plans, which supports keeping a tiny reviewed-on / due-on watch artifact so future stewards know when a previously claim-ready ceremony package must be reopened.

547. `RS-GR-524`  
   [NIST CSRC, *RMF QSG: Monitor Step FAQs*](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf)  
   Relevance: NIST's RMF Monitor Step FAQ says authorization decisions and risk acceptance need to be revisited regularly and adjusted based on continuous-monitoring results, which supports collapsing a successor-safe ceremony receipt review watch into one explicit keep-citing versus reopen-now verdict instead of leaving freshness decisions implicit.

548. `RS-GR-525`  
   [NIST CSRC, *NIST RMF Quick Start Guide — Roles and Responsibilities Crosswalk*](https://csrc.nist.gov/csrc/media/Projects/risk-management/documents/Additional%20Resources/NIST%20RMF%20Roles%20and%20Responsibilities%20Crosswalk.pdf)  
   Relevance: NIST's 2024 RMF roles-and-responsibilities crosswalk says the authorizing official reviews posture information at the defined authorization frequency, determines whether continued operation remains acceptable, determines whether significant changes require reauthorization actions, and reauthorizes when required, which supports preserving one tiny review verdict beside a successor-safe ceremony receipt watch so future stewards can tell when a once-green package must reopen.


549. `RS-GR-526`  
   [NIST CSRC, *RMF QSG: Monitor Step FAQs*](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf)  
   Relevance: NIST's RMF Monitor Step FAQ says continuous-monitoring results need to be documented in posture reports, reflected in updated authorization-related artifacts, and provided accurately and timely because they influence ongoing authorization actions and decisions, which supports collapsing a successor-safe ceremony receipt review verdict into one tiny downstream citation advisory instead of leaving later citation handling in chat memory.

550. `RS-GR-527`  
   [NIST CSRC, *RMF QSG: Authorize Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/06-authorize%20step/nist%20rmf%20authorize%20step-faqs.pdf)  
   Relevance: NIST's RMF Authorize Step FAQ says authorization decisions are communicated via the authorization package, made available to relevant officials, and accompanied by terms and conditions whose adherence is checked on an ongoing basis, which supports shipping one compact citation advisory beside successor-safe ceremony receipts so future stewards inherit the downstream keep-citing versus withdraw decision rather than inferring it from prior review artifacts.

551. `RS-GR-528`  
   [IETF / RFC Editor, *RFC 8493: The BagIt File Packaging Format (V1.0)*](https://datatracker.ietf.org/doc/html/rfc8493)  
   Relevance: RFC 8493 says a bag has just enough hierarchical structure to enclose descriptive metadata tags and payload for reliable storage and transfer, which supports keeping one tiny package manifest beside a successor-safe ceremony receipt package instead of forcing future stewards to rediscover membership from neighboring files.

552. `RS-GR-529`  
   [Research Object Crate, *RO-Crate Structure 1.2*](https://www.researchobject.org/ro-crate/specification/1.2/structure.html)  
   Relevance: RO-Crate says an attached crate is rooted by a metadata file that describes the crate and its contents, which supports keeping one compact root manifest for the authoritative successor-safe ceremony receipt package rather than scattering package membership across changelog prose.

553. `RS-GR-530`  
   [W3C, *PROV-DM: The PROV Data Model*](https://www.w3.org/TR/prov-dm/)  
   Relevance: PROV-DM says provenance about entities, activities, and people can be used to assess the quality, reliability, and trustworthiness of a thing, which supports recording file-level fixity and package-state provenance for each current successor-safe ceremony receipt package.

554. `RS-GR-531`  
   [W3C, *Data on the Web Best Practices*](https://www.w3.org/TR/dwbp/)  
   Relevance: Data on the Web Best Practices says good data versioning helps consumers understand whether a newer version is available, identify which revision they are using, and understand how versions differ, which supports shipping one compact package supersession record when a successor-safe ceremony receipt package manifest is refreshed rather than making future stewards infer the replacement target from filenames and dates.

555. `RS-GR-532`  
   [DCMI, *Replaces*](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/terms/replaces/)  
   Relevance: DCMI says a resource can explicitly replace another resource that it supplants, displaces, or supersedes, which supports giving each refreshed successor-safe ceremony receipt package one tiny artifact that says which prior package manifest it replaced instead of leaving supersession implicit.

556. `RS-GR-533`  
   [DCMI, *Is Replaced By*](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/terms/isReplacedBy/)  
   Relevance: DCMI says a resource can explicitly name the resource that supplants or supersedes it, which supports keeping a compact prior-to-current package supersession record so future stewards can retire an older successor-safe ceremony receipt package root without guessing which manifest is now authoritative.


557. `RS-GR-534`  
   [W3C, *Dublin Core to PROV Mapping*](https://www.w3.org/TR/prov-dc/)  
   Relevance: The PROV vocabulary and data model are focused on expressing actions and resource states in a provenance chain rather than only describing isolated resources, which supports collapsing several successor-safe ceremony package refreshes into one explicit package-lineage artifact once pairwise supersession records start to accumulate.

558. `RS-GR-535`  
   [DCMI, *Using Dublin Core™ - Dublin Core™ Qualifiers*](https://www.dublincore.org/specifications/dublin-core/usageguide/qualifiers/)  
   Relevance: DCMI says that when establishing a chain of versions where only one version is valid, `isReplacedBy` and `replaces` should be used to express the relationship and direct the user to the appropriate version, which supports keeping one compact lineage record that names the current authoritative successor-safe ceremony package head instead of forcing future stewards to walk pairwise files by hand.

559. `RS-GR-536`  
   [W3C, *Data on the Web Best Practices*](https://www.w3.org/TR/dwbp/)  
   Relevance: Data on the Web Best Practices says version history should be available for versioned data and that consumers should be able to understand how versions typically change and how two specific versions differ, which supports keeping one tiny ordered lineage chain beside successor-safe ceremony receipt package supersession records.

560. `RS-GR-537`  
   [IETF / RFC Editor, *RFC 5829: Link Relation Types for Simple Version Navigation between Web Resources*](https://datatracker.ietf.org/doc/html/rfc5829)  
   Relevance: RFC 5829 defines `latest-version`, `version-history`, and `predecessor-version` relation types for navigating among versioned resources, which supports shipping one compact package-head pointer that tells future stewards which successor-safe ceremony package manifest is authoritative now and where its immediate history lives.

561. `RS-GR-538`  
   [IETF / RFC Editor, *RFC 9264: Linkset: Media Types and a Link Relation Type for Link Sets*](https://datatracker.ietf.org/doc/rfc9264/)  
   Relevance: RFC 9264 says a standalone document can use a well-defined media type to provide a set of links and support discovery of related resources, which supports keeping one tiny package-head discovery object beside successor-safe ceremony package artifacts instead of forcing future stewards to browse neighboring files by hand.

562. `RS-GR-539`  
   [IANA, *Link Relations Registry*](https://www.iana.org/assignments/link-relations/link-relations.xhtml)  
   Relevance: IANA's link-relation registry records stable machine-readable relation names including `latest-version`, `version-history`, `predecessor-version`, `describedby`, and `status`, which supports using registered relation semantics instead of archive-local ad hoc labels when pointing to the current authoritative package head and its status artifacts.

563. `RS-GR-540`  
   [IETF / RFC Editor, *RFC 8631: Link Relation Types for Web Services*](https://www.rfc-editor.org/rfc/rfc8631.html)  
   Relevance: RFC 8631 says the `status` link relation can point to a status resource that consumers retrieve to learn the current state of a key service resource, which supports making a successor-safe ceremony package head point at one compact package-status-card object rather than only at raw review and advisory ingredients.

564. `RS-GR-541`  
   [NIST, *RMF Monitor Step FAQs*](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf)  
   Relevance: NIST's Monitor Step FAQ says ongoing monitoring and authorization-package updates support ongoing authorization decisions, which supports preserving one tiny package-status-card object that collapses the live review window, review verdict, and citation guidance for the current package head.

565. `RS-GR-542`  
   [NIST, *RMF Roles and Responsibilities Crosswalk*](https://csrc.nist.gov/csrc/media/Projects/risk-management/documents/Additional%20Resources/NIST%20RMF%20Roles%20and%20Responsibilities%20Crosswalk.pdf)  
   Relevance: NIST's roles/responsibilities crosswalk says authorizing officials review posture information at the defined authorization frequency and determine whether continued operation remains acceptable, which supports keeping one explicit current-state card beside a successor-safe ceremony package head so future stewards can see the present citable posture without replaying multiple status files.


566. `RS-GR-543`  
   [IETF / RFC Editor, *RFC 8574: cite-as: A Link Relation to Convey a Preferred URI for Referencing*](https://www.rfc-editor.org/rfc/rfc8574.html)  
   Relevance: RFC 8574 says a `cite-as` link can state that one link target is preferred over the current resource for permanent citation, which supports giving each superseded successor-safe ceremony receipt package one tiny redirect artifact that points future stewards at the preferred current package-reference target instead of leaving replacement citation to filename guessing.

567. `RS-GR-544`  
   [IETF / RFC Editor, *RFC 5829: Link Relation Types for Simple Version Navigation between Web Resources*](https://www.rfc-editor.org/rfc/rfc5829.html)  
   Relevance: RFC 5829 defines `successor-version` and `latest-version` relations for navigating among versioned resources, which supports making a superseded successor-safe ceremony receipt package carry one compact redirect artifact that points both to its direct replacement manifest and to the current authoritative version.

568. `RS-GR-545`  
   [IANA, *Link Relations Registry*](https://www.iana.org/assignments/link-relations/)  
   Relevance: IANA's link-relation registry records stable relation names including `cite-as`, `successor-version`, `latest-version`, `status`, and `describedby`, which supports using registered semantics instead of archive-local labels when a superseded package root redirects future stewards to the live package head and its status materials.


569. `RS-GR-546`  
   [W3C, *Data Catalog Vocabulary (DCAT) Version 3*](https://www.w3.org/TR/vocab-dcat-3/)  
   Relevance: DCAT says catalogs improve discoverability and machine consumption of described resources, which supports keeping one tiny archive-local package catalog that lists the current successor-safe ceremony package families and their live heads instead of forcing future stewards to browse lineage files one by one.

570. `RS-GR-547`  
   [IETF / RFC Editor, *RFC 6573: The Item and Collection Link Relations*](https://www.rfc-editor.org/info/rfc6573)  
   Relevance: RFC 6573 defines `item` and `collection` link relations for relating collections to their members, which supports making a compact successor-safe ceremony package catalog point at each current package head as a catalog item instead of using archive-local membership labels.

571. `RS-GR-548`  
   [IETF / RFC Editor, *RFC 8288: Web Linking*](https://www.rfc-editor.org/rfc/rfc8288.html)  
   Relevance: RFC 8288 defines a general model for typed links between resources, which supports giving a successor-safe ceremony package catalog one compact, standard-semantics link surface for current package heads, version history, current manifests, and live status resources.

572. `RS-GR-549`  
   [NIST, *RMF Assess Step FAQs*](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/05-assess%20step/nist%20rmf%20assess%20step-faqs.pdf)  
   Relevance: NIST's Assess Step FAQ says assessment results, deficiencies, and remediation planning should be documented and used to judge whether controls are effective, which supports keeping one compact package verification report that records which local checks actually ran and what they concluded about the current package.

573. `RS-GR-550`  
   [NIST, *RMF Monitor Step FAQs*](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf)  
   Relevance: NIST's Monitor Step FAQ says ongoing assessments and authorization decisions depend on current posture information, which supports exposing one compact package verification report beside the live package head so future stewards inherit the current local verification boundary instead of rediscovering it by rerunning the cloudtainer.


574. `RS-GR-551`  
   [W3C, *PROV-DM: The PROV Data Model*](https://www.w3.org/TR/prov-dm/)  
   Relevance: PROV-DM says provenance can be used to form assessments about quality, reliability, and trustworthiness, which supports keeping one compact package claim-scope artifact beside a successor-safe ceremony receipt package so future stewards know what the local verification basis actually justifies them saying about that package.

575. `RS-GR-552`  
   [NIST, *SP 800-30 Rev. 1, Guide for Conducting Risk Assessments*](https://csrc.nist.gov/files/pubs/sp/800/30/r1/final/docs/sp800_30_r1.epub)  
   Relevance: NIST SP 800-30 says risk communication groups results for decision makers, which supports collapsing a mixed verification posture into one explicit package claim-scope decision instead of leaving future stewards to infer what kinds of downstream claims remain justified.

576. `RS-GR-553`  
   [W3C, *PROV-DM: The PROV Data Model*](https://www.w3.org/TR/prov-dm/)  
   Relevance: PROV-DM says provenance can be used to form assessments about quality, reliability, and trustworthiness, which supports collapsing package status, verification, and claim-scope inputs into one compact reliance card for downstream stewards.

577. `RS-GR-554`  
   [NIST, *SP 800-30 Rev. 1, Guide for Conducting Risk Assessments*](https://csrc.nist.gov/files/pubs/sp/800/30/r1/final/docs/sp800_30_r1.epub)  
   Relevance: NIST SP 800-30 says risk communication packages results for decision makers, which supports turning a mixed citable/verified/in-scope posture into one explicit reliance artifact rather than leaving stewards to synthesize it from multiple neighboring files.

578. `RS-GR-555`  
   [IANA, *Link Relation Types Registry*](https://www.iana.org/assignments/link-relations/)  
   Relevance: the IANA registry preserves stable relation names such as `describedby` and `status`, which supports carrying the package-reliance-card forward as a discoverable companion to the package head and package catalog instead of leaving it as an orphan JSON file.


579. `RS-GR-556`  
   [The rustup book, *Installation*](https://rust-lang.github.io/rustup/installation/index.html)  
   Relevance: the official rustup installation guide says Rust can be installed into user-controlled `CARGO_HOME` and `RUSTUP_HOME` paths and exposed through `CARGO_HOME/bin`, which gives this archive a plausible userspace Rust detour on later egress-capable machines when native `cargo` and JuNest are both absent.

580. `RS-GR-557`  
   [The rustup book, *Profiles*](https://rust-lang.github.io/rustup/concepts/profiles.html)  
   Relevance: rustup's `minimal` profile keeps the install to the working compiler set (`rustc`, `rust-std`, `cargo`) and is recommended for CI, which supports a byte-conscious first bootstrap lane instead of defaulting to a wider toolchain in cramped cloudtainer sessions.

581. `RS-GR-558`  
   [The rustup book, *Overrides*](https://rust-lang.github.io/rustup/overrides.html)  
   Relevance: rustup says `rust-toolchain.toml` can pin channel/profile/components and that listed components are additive with the current profile, which matters here because this repo's pinned toolchain still asks for `rustfmt` even if the bootstrap starts from `profile = minimal`.

582. `RS-GR-559`  
   [The rustup book, *Channels*](https://rust-lang.github.io/rustup/concepts/channels.html)  
   Relevance: rustup says `--profile=minimal` is the safest way to avoid nightly/component churn and that specific dated toolchains can be installed and pinned when needed, which gives future inheritors a disciplined fallback if the repo ever needs a narrow userspace bootstrap on a machine that has HTTPS egress but no system Rust.

583. `RS-GR-560`  
   [The Cargo Book, *cargo-fetch(1)*](https://doc.rust-lang.org/cargo/commands/cargo-fetch.html)  
   Relevance: Cargo says `cargo fetch` will download registry and git dependencies ahead of time and that later Cargo commands can run offline after a fetch as long as `Cargo.lock` does not change, which supports staging one brief egress window into a reusable later-machine comeback lane instead of spending that window on repeated first-failure retries.

584. `RS-GR-561`  
   [The Cargo Book, *Environment Variables*](https://doc.rust-lang.org/cargo/reference/environment-variables.html)  
   Relevance: Cargo documents both `CARGO_HOME` and `CARGO_TARGET_DIR`, which lets this archive keep the downloaded registry cache and compiled artifacts under explicit repo-local scratch roots that can be pruned before the next revision zip instead of silently inflating the retained tree.


585. `RS-GR-562`  
   [The Cargo Book, *Features*](https://doc.rust-lang.org/cargo/reference/features.html)  
   Relevance: Cargo documents that dependency features such as `features = ["derive"]` are enabled directly in `Cargo.toml`, which supports treating the current `clap` and `serde` derive requests as a real first-compile codegen signal rather than as an inferred transitive accident.

586. `RS-GR-563`  
   [The Cargo Book, *Build Scripts*](https://doc.rust-lang.org/cargo/reference/build-scripts.html)  
   Relevance: Cargo says a package-local `build.rs` is compiled and executed just before the package itself builds, which supports using the absence of workspace `build.rs` files and build-dependencies as a compact first-pass signal that the current comeback lane is not yet asking for an extra custom pre-build stage.

587. `RS-GR-564`  
   [The Cargo Book, *cargo-test(1)*](https://doc.rust-lang.org/cargo/commands/cargo-test.html)  
   Relevance: Cargo says `cargo test --no-run` compiles the selected test target without executing it, which supports adding an explicit offline compile checkpoint before the first exact comeback witness instead of jumping straight from fetch to execution.

588. `RS-GR-565`  
   [The Cargo Book, *FAQ — How can Cargo work offline?*](https://doc.rust-lang.org/cargo/faq.html#how-can-cargo-work-offline)  
   Relevance: Cargo says `--offline` / `--frozen` forbid network access and error if a command would touch the network, which supports treating the first later-machine proof as an explicit offline guardrail rather than an informal hope that the warmed cache was sufficient.

589. `RS-GR-566`  
   [The Cargo Book, *External tools*](https://doc.rust-lang.org/cargo/reference/external-tools.html)  
   Relevance: Cargo says `--message-format=json` emits one JSON object per line for compiler messages, produced artifacts, and build-script results, with a `reason` field distinguishing the message kind. That supports preserving a machine-readable later-machine failure-capture lane instead of relying only on mixed human stderr when the first offline compile or witness fails.

590. `RS-GR-567`  
   [The Cargo Book, *cargo-test(1)*](https://doc.rust-lang.org/cargo/commands/cargo-test.html)  
   Relevance: Cargo documents that `cargo test` accepts the `--message-format` family, including `json` and `json-render-diagnostics`, which means the exact later-machine compile / exact-witness / lane-smoke commands can be rerun with structured diagnostic output without switching to a different Cargo subcommand than the preserved comeback lane.
