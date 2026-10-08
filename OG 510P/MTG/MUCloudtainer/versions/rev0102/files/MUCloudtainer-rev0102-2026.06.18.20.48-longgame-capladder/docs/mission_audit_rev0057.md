# Mission audit — rev0057

## Heart of the mission

MUC-5 is not trying to become generic Magic. Its real mission is to become a small, exact, hidden-information research instrument where construction, mulligan, and play policies can be tested without confusing legality with strategy. The engine should say what is legal; learners and generated policies should decide what is good.

The deepest current mission statement is:

```text
Build a closed-world, reproducible imperfect-information Magic microgame where exact legal-action traces, public-safe observations, replayability, and claim hygiene let us discover local strategic theory rather than merely produce bots.
```

The five-card restriction is a strength, not an embarrassment. Full Magic is too large and too rule-rich to be a good first substrate for scientific claims. The right benchmark is not card coverage; it is whether the project can make one local claim survive public-frame replay, hidden-information boundaries, seed-disjoint retesting, C++ parity checks, and explanatory decomposition.

## Outside research context checked for this audit

Relevant external anchors remain stable:

- OpenSpiel frames games as procedural environments for RL/search/planning, including imperfect-information settings.
- CFR and its descendants remain central in large imperfect-information games because they reason over information sets and counterfactual regret rather than only observed-state control.
- The Magic comprehensive rules distinguish constructed deck legality, limited deck legality, starting life, mulligans, life loss, and library-out loss. MUC-5 intentionally deviates by allowing only 40/60-card shells and unlimited copies of the five local cards.
- Published complexity work on Magic supports the decision not to implement generic Magic first.

## What is missing

1. **A one-page mission charter.** The README says what MUC-5 is, but not what counts as mission success, what is deliberately out of scope, or when a strategic claim may be trusted.
2. **Claim cards.** rev0056 has enough evidence for a compact human-readable claim card, but the evidence is scattered across CSV/JSON/docs.
3. **Mechanism labels.** The current claim is named by life cell, but the terminal reasons show it is mostly an endurance/library-out result.
4. **A causal decomposition lane.** The next work should distinguish deck size, pilot policy, mulligan policy, and Jace/Brainstorm self-decking pressure.
5. **A retention budget.** The cube keeps raw transition evidence, caches, build outputs, summaries, and docs all in the same shipped layer. That makes it trustworthy but not tidy.
6. **An experiment registry.** There is a revision log, but no simple active question ledger with owners, planned ablations, stop conditions, and multiple-testing warnings.
7. **Report surfaces.** The project needs a compact local dashboard/claim-card generator, not only raw audit gates.

## What should change

Near-term priority should shift from more claim mining to explanation of the first replicated claim:

```text
1. Make a claim card for cf34_counter_wall vs pub_threat_overlord.
2. Run same-deck pilot swaps.
3. Run same-pilot deck swaps.
4. Run deck-size equalization: 40-vs-40 and 60-vs-60 variants.
5. Run no-Jace / low-draw ablations to test whether the result is caused by library exhaustion dynamics.
6. Add terminal_mechanism and target_win_mechanism columns to every claim table.
```

This is a better scientific move than promoting another policy or opening another broad label screen.

## What may have gone wrong or wasteful

The severe waste is not a semantic bug; it is artifact hygiene. The current tree is about **916.742 MiB uncompressed**. Raw C++ transition CSV evidence accounts for about **684.949 MiB** across many revisions, while cache/build outputs account for about **2.068 MiB**. The compressed zip stays modest, but the working tree has become a warehouse.

Corrective direction:

```text
core zip: source, tests, docs, manifests, compact summaries, claim cards
archive tier: raw transitions, replay traces, bulky historical CSV evidence
ignored tier: __pycache__, .pytest_cache, build outputs, compiled binaries unless specifically requested
```

Do not delete scientific evidence blindly. First add an index and compression/retention policy, then migrate old raw traces behind reproducible summaries.

## Speculative read

The first replicated signal may be less “life total changes who wins” and more “a 60-card counter/Jace endurance shell punishes a 40-card Overlord threat shell that draws and churns.” Raising life from 20 to 40 likely gives the counter-wall more time to avoid dying before the opponent runs out of library. That is still a real local theory, but it should be named as endurance/decking until ablations prove otherwise.

## Files added in rev0057

- `docs/claim_mechanism_audit_rev0057.md`
- `docs/cloudtainer_maintenance_policy_rev0057.md`
- `docs/experiment_matrix_rev0057.md`
- `docs/cpp_core_plan_rev0057.md`
- `data/rev0057_claim_mechanism_summary.json`
- `data/rev0057_claim_mechanism_profile.csv`
- `data/rev0057_claim_action_profile.csv`
- `data/rev0057_cloudtainer_size_audit_summary.json`
- `data/rev0057_cloudtainer_size_audit.csv`

