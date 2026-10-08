# Cooperation benchmark cards should publish failure handling, retry / repair, and exclusion policy

A compact cooperation benchmark card is still too weak if the published result quietly depends on **which attempts counted**.
When malformed outputs, refusals, timeouts, judge failures, comprehension failures, parser repairs, or post-hoc filters are possible, a top-line score is partly a statement about the benchmark's failure-handling policy, not only about cooperation quality.

Recent evaluation work makes the archive rule clear:

- `RS-GR-083` frames automated benchmark practice around explicit measurement targets, implementation details, and qualified reporting, reinforcing that evaluation reports need enough protocol detail for valid interpretation.
- `RS-GR-084` shows that invalid outputs and task-execution failures are a routine part of LLM evaluation, not an exotic corner case, and that they can directly depress measured scores.
- `RS-GR-085` gives one compact concrete policy: generations are JSON-validated, invalid outputs get one retry with identical settings, then count as failures and are reported alongside runtime.
- `RS-GR-086` shows the opposite reporting choice can matter too: invalid judge outputs were filtered out during response-accuracy calculation, which changes the effective denominator unless the report says so explicitly.

## Minimum contract

Whenever a retained cooperation result could be affected by failures, retries, repairs, or filters, publish five short fields on the card or neighboring compact receipt:

1. **raw attempt denominator** — how many benchmark attempts, episodes, turns, or judgments were originally launched;
2. **scored denominator** — how many attempts actually enter the reported primary score;
3. **failure / invalid-output taxonomy** — malformed output, refusal, abstention, timeout, parser failure, tool failure, judge failure, comprehension failure, or other declared bucket;
4. **retry / repair rule and budget** — whether failed attempts are retried, re-asked, parser-repaired, manually recovered, or left as failures, and how many chances each unit receives;
5. **exclusion / scoring rule** — whether failures remain in the denominator as zeros / failures, are filtered before scoring, are separately summarized, or are promoted to a different metric such as abstention quality.

If a benchmark uses multiple denominator views, identify which one is the **primary reported object** and label the others as auxiliary summaries.
If repairs change the effective object, say that directly.

## Implementor consequence

Do not compare a raw-attempt score to a valid-attempt, repaired-attempt, or filtered-judge score as if they were the same cooperation result.
If manual repair, judge filtering, or post-hoc exclusion changed the effective sample, narrow the comparison license accordingly.
The compact card should make clear whether the retained object is a raw benchmark score, a valid-output score, a repaired-output score, or a filtered-judgment score.

## Archive consequence

Keep the retained object tiny.
One short denominator / failure-taxonomy / retry-rule / exclusion-rule block is enough.
That prevents future sessions from laundering hidden failure handling into an inheritor-facing cooperation gain while still keeping the archive compact.
