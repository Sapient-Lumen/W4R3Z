# Research Sources (2026-03-06)

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
8. Introduce probabilistic model-checking lanes for stochastic world properties (`RS-FM-006`, `RS-FM-007`).
9. Preserve Rust truth and Python orchestration using a typed FFI seam (`RS-RP-001`, `RS-RP-002`).
10. Treat reproducibility metadata as mandatory experiment output (`RS-OPS-001`..`RS-OPS-005`).
11. Keep canonicalization-horizon choices world-aware and explicitly validated rather than inheriting a generic fixed bound (`RS-GR-011`).
