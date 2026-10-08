# Cooperation benchmarks should publish interaction language and translation policy

Cooperation results are not language-neutral.
A benchmark can change behavior not only by swapping policies or partners, but also by changing the **interaction language**, the **wording frame**, or the **translation/localization pipeline**.
Two standing sources now make the compact archive rule clear:

- `RS-GR-053` shows that payoff magnitude and linguistic context can materially change repeated-dilemma strategies, with cross-linguistic divergence and language effects that can rival architecture differences.
- `RS-GR-054` shows that even outside multilingual comparisons, contextual framing changes LLM strategic behavior across canonical games.

## Minimum contract

Whenever a cooperation benchmark is run in natural language, publish:

1. the **interaction language(s)** used by each side;
2. whether all sides saw the **same wording** or a **translated/localized** variant;
3. who authored the translation / localization and whether it was **semantics-checked**;
4. whether results are reported **per language** or **pooled across languages**;
5. and any language-conditioned system prompt, role text, or framing template that differs across lanes.

## Implementor consequence

Do not pool English and non-English cooperation scores, or original and localized prompt lanes, unless the aggregation rule is published explicitly.
A policy can look more or less cooperative partly because the benchmark changed the linguistic contract rather than the strategic situation.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: interaction language, translation/localization regime, symmetry across sides, and the pooling rule.
That prevents future sessions from laundering a language effect into a policy-generalization claim.
