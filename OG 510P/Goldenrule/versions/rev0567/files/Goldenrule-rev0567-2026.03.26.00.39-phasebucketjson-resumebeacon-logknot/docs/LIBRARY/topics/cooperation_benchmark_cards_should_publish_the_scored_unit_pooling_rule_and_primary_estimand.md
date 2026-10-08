# Cooperation benchmark cards should publish the scored unit, pooling rule, and primary estimand

A compact cooperation benchmark card is still underspecified if its top-line score does not say **what object was averaged**.
The same retained result can look different when it is summarized per turn, per episode, per dyad, per participant, or per lane.
A pooled score can also change meaning when it is micro-averaged, macro-averaged, partner-weighted, participant-weighted, or reported after dropping truncated / missing cases.
That is not harmless presentation detail; it changes the quantitative object the archive is comparing.

Recent methodology work makes the archive rule clear:

- `RS-GR-021` says simulation studies should define **estimands**, methods, and performance measures clearly instead of leaving the target quantity implicit.
- `RS-GR-074` argues benchmark documentation should standardize objectives, methodologies, data sources, and limitations so users can avoid benchmark misuse and misinterpretation.
- `RS-GR-076` distinguishes measurements on a fixed benchmark from broader generalized accuracy and highlights the need to state benchmark assumptions and measurement targets explicitly.
- `RS-GR-077` frames evaluation design as a translation from stakeholder priorities into **evaluable constructs** and indicators, which means the reported score should say which construct-level quantity it is actually estimating.

## Minimum contract

Whenever a retained cooperation result carries a top-line score, publish three short score-construction fields:

1. **scored unit / unit of analysis** — e.g. round, episode, dyad, participant, task, or lane;
2. **pooling / weighting / censoring rule** — e.g. micro vs macro aggregation, equal-lane weighting, participant weighting, and any truncation / exclusion handling;
3. **primary estimand** — the quantity the score is meant to estimate, such as mean per-episode joint payoff within one declared lane or participant-weighted task-success rate across fresh-partner episodes.

If a retained object also includes convenience roll-ups, label them as **descriptive composites** rather than as interchangeable copies of the primary cooperation score.

## Implementor consequence

Do not compare two benchmark numbers as though they were the same quantity unless they share the scored unit and pooling rule.
A per-turn cooperation rate, a per-episode payoff, and a participant-weighted lane average can all be legitimate summaries, but they license different comparisons.
If truncation, early stopping, missingness, or lane pooling changes the score construction, say so directly on the compact card or neighboring compact receipt.

## Archive consequence

Keep the retained object tiny.
One short unit / pooling / estimand trio is enough.
That prevents future sessions from laundering unlike averages into a single inheritor-facing “cooperation score” when the archive is actually comparing different quantitative objects.
