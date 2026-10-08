# Research — rev0161

## The gift test

The useful gift is not “an implementation of retconning.” It is a way to make the retcon argument lose.

Gwern's proposal suggests a loop in which a system preserves canon, samples latent explanations and bounded futures, selects under a rubric, compresses a winner into hidden state, and forgets discarded branches. The serious objections are also procedural: later events can make earlier accidents suspiciously important; hidden explanations can move after clues; commitment can be too cheap; selection can overfit the desired payoff; and extra search can cost more without producing better play.

Rev0161 turns those objections into four treatments and three evidence classes. It can reveal whether Lacuna's additional machinery improves blind transcript judgments, changes failure/cost profiles, and preserves mechanically verified state. It can also reveal that a monolithic prompt is just as good, that forward-only is better, or that role separation costs more without visible benefit.

That falsifiability is the gift.

## Why these four conditions

`forward-only` estimates the behavior of continuing without retrospective latent-state revision.

`prompt-only-retcon` isolates the general idea of retrospective explanation from Lacuna's governance. It allows one context to generate, select, and compress.

`lacuna-serial` tests schemas, fixed cardinality, provenance-stripped judging, least-authority compression, and fail-closed verification while denying a claim of context independence.

`lacuna-role-separated` adds manufactured information boundaries. Its contrast with serial asks whether separate contexts/subagents matter beyond the protocol itself.

The design is not fully factorial: forward planning quality and prior hidden state may differ, and provider implementations can confound treatment. A larger study should add explicit forward-planning controls and block by model/story.

## Player entrance versus research operation

A player should be able to say “Will you DM?” and immediately enter fiction. That is a usability requirement, not a claim that an ordinary chat has durable custody.

The experiment owner has a different job: fix the capsule, preserve private assignment, create fresh contexts, operate exact handoffs, retain failures, and withhold unblinding. Combining these roles in one conversational prompt would make the player carry research machinery and would invite condition leakage.

## Datacube as context curriculum

The cube is more than storage. At each transition it compiles an exact context slice:

```text
seed boundary
  -> opaque condition driver
  -> exact ordinary turn packet
  -> exact checkpoint role card(s)
  -> exact accepted output digest
  -> exact next role/card
  -> frozen transcript
  -> blind rating packet
  -> unblinded descriptive join
```

This makes a long experiment legible to models that cannot infer the whole protocol from prose. The parent need only follow the current audited pointer. Workers need only satisfy one local contract. Repeated CLI invocations reconstruct the relevant boundary instead of trusting conversational memory.

## Subagents as an experimental variable

Two agents are useful when they create different information sets, not merely two samples from the same prompt. Generator blindness to later judgment, judge blindness to provenance, compressor blindness to rejected alternatives, and verifier nonparticipation in composition are the intended separations.

Native subagents can implement those slices conveniently. Separate chats or API calls can approximate them. A serial single context remains a valid control. None proves independence when models, provider memory, tools, or system prompts are shared.

For scientific use, the same topology maps naturally to hypothesis generation, blinded evaluation, concise state update, and independent verification. The same warning applies: a role label is not an independence certificate.

## Minimum credible study

A credible exploratory study should include:

- multiple seed campaigns and prewritten off-script actions;
- independent hidden assignments per block;
- at least two model families;
- fixed within-block model/sampling/tool budgets;
- several raters blind to structured condition identity;
- all terminal failures and exclusions retained;
- condition-order and story/model blocking;
- rater-level data rather than only sums;
- preregistered primary dimensions; and
- external retention of capsule/assignment commitments.

Analysis should model story, model, block, and rater variation. Preference ranks and ordinal scores should not be treated casually as interval utility. Report effect distributions and failure/cost tradeoffs, not only a winner.

## Open research work

1. Replicate bundles with one preregistration digest and deterministic block schedule.
2. Optional external witness/timestamp receipts for capsule and assignment commitments.
3. Provider-adapter capture of request/response IDs and signed or exportable metadata where available.
4. Contamination probes that deliberately plant canary strings outside worker context.
5. Transcript semantic-leak checks before rating.
6. Rater assignment, masking checks, and disagreement reporting.
7. Cost-normalized and latency-normalized comparisons.
8. Forward-planner and oracle-ablation conditions.
9. Scientific-task capsules with public-report/private-hypothesis separation.
10. A public redaction/export format that excludes private candidate futures while preserving verification evidence.

## Sources consulted

- Gwern Branwen, “LLM retcon,” 2026: <https://gwern.net/blog/2026/llm-retcon>
- OpenAI Codex subagents: <https://developers.openai.com/codex/subagents>
- Anthropic Claude Code custom subagents: <https://docs.anthropic.com/en/docs/claude-code/sub-agents>
