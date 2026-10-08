# Cooperation benchmark human lanes should publish participant-pool provenance and repeat-exposure policy

Human-lane cooperation results are not only about the evaluated policy.
They also depend on **who the humans are**, **where they were recruited**, and **whether they have already seen similar AI interactions or benchmark tasks**.
Two standing sources now support a compact archive rule:

- `RS-GR-059` shows that willingness to cooperate with artificial agents can differ across countries even when human-human cooperation is more stable, so one participant pool should not be laundered into “humans in general.”
- `RS-GR-060` shows that participant-pool effects and contextual framing can materially alter cooperation conclusions and replication fidelity.

## Minimum contract

Whenever a benchmark lane includes real humans, publish:

1. the **recruitment platform / participant pool**;
2. the **country or residence mix** actually used in analysis;
3. any important **eligibility filters** (for example language proficiency, prior AI use, or domain background);
4. whether participants were **benchmark-naive**, previously exposed to the task family, or repeat participants;
5. the rule for **multiple participations / re-contact / longitudinal reuse** if any;
6. and whether headline results are reported **within one pool** or **pooled across distinct pools / countries**.

## Implementor consequence

Do not compare or pool human-lane cooperation scores across studies if participant-pool provenance or repeat-exposure policy differs.
A policy can look more or less cooperative partly because the benchmark changed the humans who were sampled or because participants arrived with different prior exposure to AI and game tasks.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: recruiting pool, country/residence mix, key eligibility filters, and repeat-exposure policy.
That prevents future sessions from laundering one human sample into a universal human-compatibility claim.
