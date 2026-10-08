# Cooperation benchmark cards should publish judge provenance, rubric, and adjudication policy

A compact cooperation benchmark card is still too weak if the published result quietly depends on **who or what did the judging**.
When cooperation is scored by an LLM judge, a rubric-following committee, a human rater pool, or a hybrid escalation pipeline, the benchmark result is partly a statement about that adjudication stack, not only about the policy being evaluated.

Recent evaluation work makes the archive rule clear:

- `RS-GR-083` frames automated benchmark practice around explicit protocol details and qualified reporting, which means model-based judging cannot remain implicit implementation detail.
- `RS-GR-087` surveys LLM-as-a-Judge as a full pipeline spanning input design, context / prompt design, model selection, and output post-processing, and argues that reliable judge systems require careful design and standardization.
- `RS-GR-088` shows that judge outcomes can change because of prompt-side position bias, so answer order and order-debiasing policy are part of the benchmark contract rather than harmless plumbing.
- `RS-GR-089` shows that confidence-aware escalation and selective human-alignment guarantees are feasible, which means a benchmark should say whether uncertain cases were abstained on, escalated, or force-scored.
- `RS-GR-090` shows that even scoring-only judges are sensitive to rubric order, score IDs, and reference-answer protocol, so the scoring rubric itself belongs on the card.

## Minimum contract

Whenever a retained cooperation result depends on any model-based or human adjudication stack, publish four short fields on the card or neighboring compact receipt:

1. **judge / rater provenance** — judge model family or human-rater pool, version if known, single-judge vs panel / committee, and any hosted third-party evaluation service;
2. **rubric / scoring protocol** — prompt or rubric family, pointwise vs pairwise vs rubric-based mode, answer-order policy, and any reference-answer or calibration examples;
3. **adjudication / debias rule** — order swapping, repeated judging, multi-judge aggregation, tie-break rule, abstain option, and final decision rule;
4. **calibration / escalation policy** — whether judges were calibrated against humans or gold labels, whether low-confidence or disputed cases were escalated, and whether human spot-checks or audit slices were run.

If the benchmark uses a fixed deterministic scorer with no adjudication choices, say that directly.
If the benchmark uses a human-only rating protocol, the same compact fields still matter: who rated, by what rubric, how disagreements were resolved, and what escalation path existed.

## Implementor consequence

Do not let one hidden judge stack masquerade as a policy property.
A retained cooperation result scored by one judge model, one rubric order, one pairwise protocol, or one force-scoring rule is not automatically interchangeable with a result scored by a different adjudication stack.
If the benchmark relied on confidence-based abstention, cascaded judging, or human escalation, label that directly and keep the comparison license narrow enough to match the actual judging pipeline.

## Archive consequence

Keep the retained object tiny.
One short judge-provenance / rubric / adjudication / escalation block is enough.
That prevents future sessions from laundering evaluator choice into an inheritor-facing cooperation gain while still keeping the archive compact.
