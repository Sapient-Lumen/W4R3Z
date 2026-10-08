# Cooperation benchmark cards should publish primary endpoint, auxiliary metrics, and multiplicity policy

A compact cooperation benchmark card is still too weak if the published result quietly depends on **which metric became the headline**.
Even when the lane contract, evaluated subject, wrapper, judge, and scored unit are fixed, a cooperation result can move because one report promotes joint reward, another promotes cooperation rate, another promotes a judge composite, and another chooses the best-looking metric after seeing several plausible ones.

Recent evaluation work makes the archive rule clear:

- `RS-GR-074` argues that benchmark documentation should standardize objectives, methodologies, data sources, and limitations, which means the governing metric cannot remain implicit.
- `RS-GR-076` argues that benchmark reporting can conflate distinct notions of performance, which means different cooperation metrics should not be treated as interchangeable copies of one score.
- `RS-GR-108` updates CONSORT reporting guidance to require prespecified primary and secondary outcomes together with the measurement variable, analysis metric, aggregation method, and time point, plus disclosure of non-prespecified outcomes or analyses.
- `RS-GR-109` explains that multiple outcomes can be scientifically appropriate, but only if the criterion for success or rejection is specified in a way that controls false positives across the outcome family.
- `RS-GR-110` reviews recent trials and finds that explicit strategies for incorporating multiple outcomes into the primary analysis were uncommon, which makes metric-selection drift a live reporting failure rather than a theoretical worry.

## Minimum contract

Whenever a retained cooperation result could change because more than one plausible metric, composite, or outcome family exists, publish four short fields on the card or neighboring compact receipt:

1. **primary endpoint / governing metric** — which metric or endpoint governs the headline claim, including the measurement variable, time point when relevant, and whether it is descriptive or inferential;
2. **auxiliary / guardrail metrics** — which additional metrics are reported for interpretation, safety, robustness, or process diagnosis, and whether any of them can override the primary metric in deployment decisions;
3. **composite / normalization rule** — whether the headline uses one raw metric, a weighted composite, a judge-made rubric aggregate, thresholding, normalization, or Pareto / guardrail selection over several metrics;
4. **multiplicity / metric-selection policy** — whether the primary metric was fixed ex ante, whether several candidate metrics were inspected, what correction / decision rule governed that family, and how post-hoc metric promotion is labeled.

If the result intentionally studies a multidimensional cooperation profile, say that directly.
If one metric is merely a convenience headline over several non-equivalent dimensions, say that directly too.

## Implementor consequence

Do not compare joint reward, cooperation frequency, reciprocity score, common-ground score, judge score, harm rate, and convenience composites as though they were the same cooperation object.
A retained result may still be useful under any of those metrics, but the comparison license should say which metric actually governs the claim.
If a paper or benchmark promoted one metric after seeing several plausible alternatives, label the retained object as metric-selected or otherwise narrow the comparison license accordingly.

## Archive consequence

Keep the retained object tiny.
One short primary-endpoint / auxiliary-metrics / composite-rule / multiplicity-policy quartet is enough.
That prevents future sessions from laundering metric shopping or post-hoc composite promotion into an inheritor-facing cooperation gain while still keeping the archive compact.
