# Mission and integrity audit — rev0068

## Executive verdict

MUC-5's deepest value is not that it can produce a winning bot. Its value is that it can act as an **adversarial scientific instrument for local strategic claims**: exact legality, public-information boundaries, deterministic replay, seed-disjoint replication, mechanism decomposition, and a second C++ implementation can force an attractive story to survive contact with stronger controls.

The project has demonstrated that capability unusually well. The sequence from rev0054 through rev0064 replicated a flattering counter-wall result, explained it, discovered that a passive 60-card buffer could reproduce much of it, repaired the opponent's closure policy, and finally quarantined the original claim. That is the best evidence that the mission is alive.

The project also has a governance problem. By rev0067, the scientific code was passing all 232 tests and the inherited 176-check audit, while the package described itself as the wrong revision, the revision ledger stopped six revisions early, the formal spec stopped near rev0010, and a documented evidence-retention plan had not been executed. The audit system was proving internal consistency inside selected surfaces, not truth of the research object as a whole.

The high-level diagnosis is therefore:

```text
engine and replay discipline:        strong
self-correction of claims:           strong
package truth and provenance:        failed in rev0067
statistical claim discipline:        incomplete
strategic robustness measurement:    missing
artifact retention discipline:       documented, not enforced
```

rev0068 repairs the most dangerous mechanical gaps without changing game rules: it makes package identity executable, catches incomplete response matrices, restores the revision ledger, records the validation environment, creates a live claim registry, and establishes an evidence-budget roadmap.

## The heart of the mission

The original charter says MUC-5 should discover and verify local strategic theory in a tiny hidden-information Magic-like game. The sharper version is:

> Build a closed-world, reproducible imperfect-information laboratory that is better at destroying false strategic explanations than at producing impressive win rates.

That phrasing matters. A leaderboard rewards policy strength against a fixed opponent. A scientific instrument rewards calibrated claims that survive alternative opponents, legal-size controls, policy swaps, hidden-information checks, fresh seeds, replay, and mechanism ablations.

The five-card universe is not a toy to apologize for. It is the control that makes causal diagnosis possible. The project should resist becoming generic Magic until it can answer, for each promoted claim:

```text
What exactly is claimed?
Against which policy population?
Under which deck/life/seat/seed distribution?
What mechanism causes the effect?
What evidence would demote the claim?
How exploitable is the promoted strategy outside the training matchup?
Can an independent implementation reproduce the result?
```

The mission succeeds when the answer to those questions is machine-readable and rerunnable, not merely when another policy wins a panel.

## What is healthy

### 1. Exactness is treated as infrastructure, not decoration

The referee emits legal macro-actions; agents choose among them. Public observations are separated from hidden state. Replay traces, conservation checks, terminal-clean requirements, and C++ transition shadows are real safeguards. The uploaded rev0067 cube passed 232 tests, smoke validation, and 176 inherited audit checks.

### 2. The project has already corrected itself

The claim history is a model of useful skepticism:

```text
rev0054–56: replicate a counter-wall edge
rev0057–60: identify library-out/endurance as a major mechanism
rev0061: show that inert 60-Island can remain competitive
rev0062: expose a life-40 closure pathology and deck-size confound
rev0063: repair the threat pilot's overdraw/under-closure behavior
rev0064: show the historical counter-wall edge collapses under the repair
rev0065–67: search for and stress a named counter response without restoring the old claim
```

The old result was not erased. It was reclassified. That is exactly what a claim-testing laboratory should do.

### 3. Later revisions stopped adding full transition ballast

From rev0058 onward, the project generally retained compact transition samples instead of another full raw transition CSV. That arrested the fastest growth even though it did not migrate the historical warehouse.

## What has gone severely wrong

### 1. The linked research object could pass while lying about its identity

The uploaded archive and README identify rev0067. `manifest.json` identifies rev0066, including the rev0066 cube name and filename. `data/revision_log.json` ends at rev0061. Yet the rev0067 artifact audit and inherited audit both pass.

This is not cosmetic. A manifest is the package's claim about what it is. A stale manifest breaks citation, provenance, automation, lineage, and reproducibility. A checksum manifest can still be perfectly correct while hashing semantically wrong metadata; cryptographic consistency does not imply semantic integrity.

Root cause: revision-local audits only check expected new paths, forbidden rev-specific raw filenames, and CSV row caps. They do not check the package as a research object.

rev0068 correction:

```text
root directory name
archive filename recorded in manifest
manifest revision/timestamp/codename
README first heading
latest revision-log entry
complete checksum coverage and hashes
generated build/cache exclusions
```

are now one executable contract.

### 2. An incomplete response matrix could become a false refutation

`compare_response_matrix_by_life()` previously used an empty mapping for a missing closure, pressure, or surge row, then converted its absent score to `0.0`. A missing surge result could therefore be labeled `threat_surge_refutes_counter_guard`.

The corresponding gate only checked that each threat axis and each size axis appeared somewhere. It did not require the complete size × life × policy Cartesian product. This is a severe scientific bug because missing evidence was converted into maximally negative evidence.

rev0068 correction:

```text
missing policy row -> null scores
missing policy row -> provisional_read = incomplete_matrix
missing policy row -> no best policy classification
gate -> requires all 18 size/life/policy cells
```

Regression tests now pin this behavior.

### 3. “Gate passed” conflated operational integrity with inferential support

The rev0067 gate proves valuable things: enough total games, no truncations, complete forensic reruns, C++ parity, policy-axis presence, and no accidental own-spell counters. It does **not** prove that a strategy is robust, superior, or statistically distinguished from another strategy.

The cumulative matrix has many cells with only 8 or 20 games. Examples from the shipped uncertainty columns:

```text
n=8, score=0.5000: 95% Hoeffding interval 0.0198–0.9802
n=20, score=0.6500: 95% Hoeffding interval 0.3463–0.9537
n=24, pressure score=0.8333: 0.5561–1.0000
n=24, surge score=0.4167:    0.1394–0.6939
```

Even the conspicuous 60-vs-60 life-40 pressure/surge difference has overlapping conservative intervals. The point-estimate labels are useful triage labels, but they are not confirmation labels.

rev0068 makes the gate report its scope as `operational_integrity_only`. A later inference gate should be separate and should fail closed when a comparison is underpowered or adaptively selected.

### 4. Hand-authored response policies are becoming a best-response treadmill

`threat_closure`, `counter_guard`, `threat_pressure`, and `threat_surge` are valuable falsification probes. But the project is now iterating by writing a policy against the last policy and then writing another policy against that one. This is a local Red Queen process: each policy can appear strong because the opponent population is narrow and moving.

The PSRO literature was motivated in part by this exact failure mode: policies trained against individual opponents can overfit, while approximate best responses to mixtures and empirical-game meta-strategies provide a broader target. CFR and MCCFR provide a complementary information-set benchmark for two-player zero-sum imperfect-information games.

The next strategic unit should therefore be a **policy population**, not one more named duel. Keep the hand-authored policies, but place them in a payoff matrix and ask:

```text
What mixture is selected by a meta-solver?
What is each policy's worst-case payoff over the population?
Can an oracle find a profitable deviation?
How does the result change on frozen holdout seeds and generated mutations?
```

### 5. The formal specification and environment did not keep pace with the implementation

`docs/muc5_spec.md` is still framed as a rev0002 specification with addenda through approximately rev0010. The code has since accumulated dozens of policy, replay, C++ shadow, counterfactual, terminal-mechanism, and claim-gate surfaces. There is no single current executable specification or conformance matrix.

The uploaded package also has no `pyproject.toml`, requirements file, lockfile, container recipe, license, or citation metadata. Source imports NumPy, pandas, scikit-learn, and pytest, but the expected versions were unstated. rev0068 adds a direct dependency pin file and an environment capture; it does not pretend this is a complete transitive or operating-system lock.

License and citation metadata remain owner decisions because authorship and licensing cannot be invented safely.

## What is wasteful

The uploaded rev0067 archive contains 1,959 files and 939.300 MiB uncompressed. A conservative audit classifies:

```text
full transition/segment evidence: 37 files, 717.707 MiB
replay JSONL traces:              45 files,  62.362 MiB
combined:                                     83.05% of the cube
```

The archive also ships four compiled build artifacts totaling 0.256 MiB despite the rev0057 policy saying build outputs should not normally be shipped or checksummed. The upload itself did not contain Python caches; validation runs generate them locally, and rev0068's finalizer removes them before packaging.

Exact duplicate content is only 2.309 MiB, so deduplication is not the main opportunity. The largest duplicate is a repeated 1.26 MiB C++ trace table; many smoke logs are identical; several stdout files are byte-for-byte copies of summary JSON. Cleaning these is tidy but will not solve the warehouse problem.

The severe waste is **repeated inheritance**. Every linked revision carries the same historical raw evidence again. Even when ZIP compression makes the download modest, extraction, hashing, indexing, and cognitive navigation operate on nearly a gigabyte. The rev0057 maintenance policy correctly proposed three tiers, but ten revisions later the historical data remained in the linked working cube.

The correction should preserve evidence, not delete it:

```text
Tier 1: small linked working cube
  source, tests, current spec, docs, compact summaries, claim registry,
  small replay/transition samples, evidence index, checksums

Tier 2: immutable content-addressed evidence bundle
  full transition CSVs, full replay JSONL, bulky historical tables

Tier 3: generated and disposable
  build/, __pycache__/, .pytest_cache/, local binaries
```

Each Tier-2 object needs SHA-256, byte/row counts, producing script, source revision, command, schema, and the compact Tier-1 artifact that depends on it. RO-Crate is a plausible metadata model because it can describe a dataset, its files, software, workflows, and provenance in structured JSON-LD. FAIR is a useful target for the entire research object, not only the CSV files.

## What is missing

### A single source of package truth

The directory name, filename, manifest, README, revision ledger, and checksum set must be generated from one revision object. rev0068 adds validation; the next step is generation so drift is structurally impossible.

### A current claim ledger

Evidence is distributed across append-only README sections, docs, JSON, and CSV. `data/rev0068_claim_registry.json` is the first explicit ledger with statuses such as `quarantined`, `supported_local`, and `provisional`. Future revisions should update claims transactionally: every claim must name its scope, evidence, uncertainty, falsifier, and superseding claim.

### A current executable specification

Create one versioned spec for state, information states, legal action grammar, chance, terminal conditions, utility, deck legality, mulligan procedure, public observation, replay serialization, and deliberate deviations from Magic. Every clause should point to conformance tests in Python and C++.

### A statistical design contract

For every promoted experiment, register before running:

```text
complete matrix and primary estimand
minimum per-cell sample size or precision target
seed allocation and whether comparisons are paired
stopping rule
primary versus exploratory cells
multiple-comparison policy
confidence interval method
frozen holdout seed family
promotion/demotion criterion
```

Common-random-number pairing should be used where simulator semantics make it valid, because unpaired sequential seed blocks add avoidable variance and make policy deltas harder to interpret.

### A strategic validity metric

Win rate against the current opponent is not enough. Add at least one of:

```text
empirical-game meta-strategy and oracle gain
worst-case payoff against a fixed policy population
approximate exploitability / NashConv
CFR or MCCFR reference policy in a tractable abstraction
held-out mutation-bank performance
```

OpenSpiel is worth evaluating as an independent adapter or cross-check because it represents procedural extensive-form imperfect-information games and exposes exploitability and other evaluation tools. It should not replace MUC-5's exact engine; its value is independent representation and standard algorithms.

### Independent implementation evidence

C++ shadows selected transition kernels, which is useful. It is not yet an independent game implementation: much of the experiment orchestration and semantic framing still flows from Python. A small independent game tree or OpenSpiel adapter for a constrained subgame would provide stronger cross-validation than another Python analysis layer.

## Recommended sequence

### Phase 0 — completed in rev0068

```text
repair manifest and revision ledger
add package contract and finalizer
fix missing-cell false-zero bug
mark response gate operational-only
record direct dependencies and environment
add claim registry and archive inventory
prune generated build/cache artifacts from linked package
```

### Phase 1 — evidence budget

Create an immutable evidence index and migrate one old revision family at a time. Start with the largest transition tables whose compact summaries and reproducer commands already exist. Verify hashes before and after compression. Do not change historical content silently.

Target: linked core below 150 MiB uncompressed without losing the ability to locate or reproduce raw evidence.

### Phase 2 — claim and spec consolidation

Generate a short current README from the manifest/claim registry rather than appending another full history block. Move historical narrative to a changelog. Publish an executable current spec and Python/C++ conformance map.

### Phase 3 — inference discipline

Add a preregistered experiment schema, paired seed blocks, precision-based stopping, and a separate inference gate. Re-label old point-estimate classifications as exploratory unless they satisfy the new contract.

### Phase 4 — population game

Build the empirical payoff matrix over all named public policies, add a simple meta-solver, and implement a response oracle. PSRO is a natural conceptual template. In parallel, attempt CFR/MCCFR on a reduced exact subgame to obtain a strategic reference point.

### Phase 5 — independent validation

Implement an OpenSpiel adapter or another independently coded reduced game. Compare legal histories, information states, terminal utilities, and selected policy values.

## Speculation, clearly labeled

1. **The true research subject may be resource closure, not “control versus threats.”** With only five cards, large deck-size variation, Jace/Overlord draw effects, and library-out loss, the dominant strategic axis may be control of library burn and closure timing. That is a legitimate game, but the project should either embrace and name it or redesign experiments so it does not masquerade as generic counterspell strategy.

2. **The project may be overinvesting in execution parity relative to its present bottleneck.** C++ parity is excellent, but the limiting uncertainty is now opponent-population and inference design, not transition throughput. More C++ work should be justified by a measured experiment bottleneck or independent semantic validation.

3. **Revision count may be substituting for consolidation.** Sixty-eight rapid revisions demonstrate energy, but append-only docs, duplicated validation outputs, stale governance ledgers, and one-off runners suggest the unit of work has become too small. Fewer, preregistered, end-to-end revisions may produce more knowledge per artifact.

4. **The most valuable product may be the audit machinery itself.** The project has shown an ability to catch self-countering, decision-count errors, truncation artifacts, library-buffer confounds, and opponent closure failure. A generalized “claim autopsy” pipeline may be more novel and reusable than any individual MUC-5 policy.

These are hypotheses, not findings. The next revisions should design tests that could disconfirm them.

## Research anchors

1. Lanctot et al., *A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning* (NeurIPS 2017): policy overfitting, approximate best responses to mixtures, empirical-game meta-strategies.
2. Zinkevich et al., *Regret Minimization in Games with Incomplete Information* (NeurIPS 2007): counterfactual regret and approximate equilibrium in imperfect-information extensive games.
3. Lanctot et al., *Monte Carlo Sampling for Regret Minimization in Extensive Games* (NeurIPS 2009): sampled CFR with bounded regret.
4. Lanctot et al., *OpenSpiel: A Framework for Reinforcement Learning in Games* and current OpenSpiel documentation: procedural extensive-form games, imperfect information, exploitability metrics.
5. RO-Crate 1.2 specification: structured metadata and provenance for research-object files, software, and workflows.
6. Wilkinson et al., *The FAIR Guiding Principles for scientific data management and stewardship* (Scientific Data 2016): FAIR applies to data, algorithms, tools, and workflows.

Machine-readable source records are in `data/rev0068_research_anchors.json`.
