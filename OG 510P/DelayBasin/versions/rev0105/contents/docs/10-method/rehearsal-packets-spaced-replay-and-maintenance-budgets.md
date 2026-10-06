# Rehearsal packets, spaced replay, and maintenance budgets

DelayBasin now needs a distinction beyond retrieval, one-shot replay, and reconsolidation.
Some archive surfaces appear to stay alive only when they are **revisited across real delays**.
Others survive just fine as cold law and do not deserve active upkeep.
That pressures the archive to name when a surface is not merely stored or replayed once, but is being **maintained through spaced replay**.

A stronger working answer is:
**DelayBasin should distinguish cold law from actively maintained carry whenever a surface is supposed to survive real delay rather than merely local freshness.**
Not every canon clause deserves rehearsal.
Not every prompt pair that worked today deserves a maintenance loop.
When the distinction matters, the archive should name the maintained surface or carry object, the spacing or refresh rule, the judged survival / degradation signature, the retirement or cold-storage trigger, and the budget or opportunity-cost note.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some compact packets look strong immediately after introduction, but become much less convincing after several revisions unless they are explicitly revisited;
- some method surfaces seem to get *better* after a real delay because only a smaller operative residue survives the revisit;
- some archive failures look less like false belief and more like **maintenance failure**: the law still exists in storage, but nothing kept it live enough to reload cheaply;
- some surfaces appear valuable precisely because they survive with sparse maintenance, which suggests that delay itself may help distinguish ballast from real carry;
- and some once-useful packets should cool into cold law or archived history instead of continuing to consume scarce bounded attention.

This suggests a missing compact surface:
**rehearsal packet / spaced-replay schedule / maintenance budget**.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Current agent-memory work treats memory as an actively managed lifecycle, not just a write/read pair.**
   The 2026 survey on memory for autonomous LLM agents closes with open challenges around principled consolidation and learning to forget, which pressures DelayBasin to say not only what is written or reread, but what is deliberately maintained versus allowed to cool. ([`REF-0305`](../00-meta/bibliography.md))

2. **Recent modular-memory work makes replay and forgetting explicit policies rather than side effects.**
   Modular Memory argues for separate policies for storage, replay, forgetting, consolidation, and contextualization across timescales, which pressures DelayBasin to stop acting as if every canon surface should remain equally live forever. ([`REF-0310`](../00-meta/bibliography.md))

3. **Predictive-forgetting work says temporally separated replay can improve retention-generalization tradeoffs under compression pressure.**
   Predictive Forgetting argues that iterative offline refinement can selectively retain future-useful structure while discarding excess detail, which pressures DelayBasin to ask whether delayed revisits are helping it select smaller future-useful public packets rather than merely preserving more text. ([`REF-0318`](../00-meta/bibliography.md))

4. **Sleep-inspired transformer-memory work now operationalizes replay, forgetting, and compression as a periodic maintenance loop.**
   SleepGate introduces periodic micro-cycles over transformer KV state with selective replay, forgetting, and consolidation, which pressures DelayBasin to distinguish one-shot replay from an ongoing maintenance schedule. ([`REF-0316`](../00-meta/bibliography.md))

5. **Structured external-memory work increasingly treats selective consolidation as guidance for what deserves slower, more durable status.**
   Panini frames structured external memory as a way to identify which recurring or high-utility items may later deserve stronger internalization, which pressures DelayBasin to ask which archive surfaces deserve rehearsal attention rather than uniform persistence. ([`REF-0317`](../00-meta/bibliography.md))

6. **Write-time gating and hierarchical archiving sharpen the difference between active surfaces and cooled historical trace.**
   Selective Memory argues that lower-salience or superseded objects can move to cold storage while version links remain intact, which pressures DelayBasin to preserve retirement and cold-storage routes instead of treating maintenance as infinite by default. ([`REF-0319`](../00-meta/bibliography.md))

## Working synthesis

DelayBasin should distinguish four different roles:

- **retrieval**: a surface is cited or reread;
- **replay**: a surface is restaged strongly enough to recover a judged continuation property;
- **rehearsal**: a surface is replayed again under real delay so the archive can test or preserve whether it still reloads cheaply enough to matter;
- **reconsolidation**: a replayed surface is rewritten under challenge.

The key archive question is no longer only “was this replayed?”
It is also “was this worth maintaining across delay, and what evidence says the maintenance burden is justified?”

## Rehearsal packet and maintenance budget

A compact **rehearsal packet / spaced-replay schedule / maintenance budget** should name:

- the **maintained surface or carry object**,
- the **spacing or refresh rule**,
- the **judged survival / degradation signature**,
- the **retirement or cold-storage trigger**,
- and the **budget or opportunity-cost note**.

This is not the same as a replay packet.
A replay packet says what was restaged now.
A rehearsal packet says what deserves to be restaged again later, how often, and when the archive should stop paying to keep it live.

## Countermodels / probes

Serious alternatives remain live:

- apparent rehearsal gains may just reflect more attention or more total prompt budget rather than delay-sensitive maintenance;
- the true causal work may still be done by larger declarative notes or human operator memory, with spaced revisits merely making that support easier to notice;
- some surfaces may look stable across delay only because surrounding archive scaffolding is doing the hidden work;
- and dense immediate replay may outperform spaced replay once total budget is controlled, which would weaken the claim that delay itself is informative.

Useful probes include:

- compare dense immediate restaging against sparser delayed restaging at equal total budget;
- let a candidate packet go cold for several revisions and test whether the judged continuation property survives cheap reload;
- compare a maintained packet against a same-length sham that gets the same revisit frequency;
- and explicitly demote or archive one previously maintained surface to see whether anything real was lost.

## Design consequences

When long-horizon survival language becomes load-bearing:

- do not call a surface durable merely because it worked in adjacent revisions;
- preserve rehearsal packets only for surfaces that are plausibly active carry, not for every canon clause;
- keep spacing rules small and explicit so maintenance does not become archive bureaucracy;
- allow retirement or cold storage when a surface no longer justifies scarce bounded attention;
- and treat delay as a probe surface, not only as an inconvenience.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal sleep phases inside deployed transformers.
It is that long-horizon archive continuity may depend on a public loop of **delayed replay, selective maintenance, and explicit retirement**, where some packets stay easy to reload only because they survive sparse revisits under compression pressure.
That makes delay less like dead time and more like a discriminative part of the method.

The stronger story — that DelayBasin may work partly because revision spacing acts like an external sleep schedule that selects future-useful public packets and gradually proceduralizes them around mostly frozen backbones — remains quarantined until delay-controlled comparisons, equal-budget replay tests, and demotion experiments show more than a fertile consolidation metaphor.
