# Evidence-ecology witnesses, selector source bias, citation-loop pressure, and retrieval-contamination collapse

This is the compact successor surface for `OQ-0161`.

## Practice / observation

DelayBasin increasingly uses online research as part of GPUstorming. A normal citation-frame check can ask whether a particular source is relevant, credible, fresh, or misread. `OQ-0161` asks a different question: whether the evidence surface itself has shifted because AI search, answer engines, generative citation behavior, or AI-generated web content changed which sources are visible enough to be cited.

The canonical move is not to distrust every AI-search citation and not to build a standing evidence-market court. The move is to preserve one small witness when current online research is load-bearing: name whether the risk is selector bias, citation-loop pressure, retrieval contamination/collapse, or an honest mix.

## External pressure from LLM search source coverage, SourceBench source quality, GEO citation optimization, Google AI Mode self-citation, publisher AI opt-out pressure, and retrieval collapse

Recent source-coverage work says LLM-based search engines can cite a materially different domain set from traditional search engines and do not automatically dominate traditional search on credibility, neutrality, or safety. SourceBench pressures the same boundary from a different angle: grounded answers depend on source quality, so citation presence is not itself a proof of evidence quality. Retrieval-collapse work names a still-stronger failure mode in which synthetic or adversarial material enters the source pool and then becomes overrepresented in exposure. GEO and generative-citation-visibility work adds the incentive layer: visibility can become a citation optimization problem rather than only a rank position problem. Current reporting and regulatory pressure around AI search self-citation, publisher click-through, and AI-feature opt-outs show why DelayBasin should keep citation-loop pressure separate from local source quality.

## Working synthesis

Use `evidence_ecology_state` when the archive is relying on online research and the live uncertainty is not merely whether one cited source is good.

The compact witness has four tokens:

- `selector-source-bias` — the interface, answer engine, or search provider appears to be selecting a skewed or changed source set, but the substrate evidence pool itself need not be contaminated. This can often be handled by broader source-frame, query-frame, and rival-set checks.
- `citation-loop-pressure` — the system's citation, traffic, self-citation, or optimization incentives may be changing which sources gain visibility or how publishers adapt, but the case has not shown actual source-pool contamination.
- `retrieval-contamination-collapse` — generated, synthetic, low-quality, or adversarial material is plausibly entering the retrievable evidence pool and altering exposure, diversity, or provenance enough that ordinary citation/source checks are insufficient.
- `mixed-evidence-ecology` — the visible case honestly mixes selection, citation-loop, and contamination/collapse signals, or the evidence is not clean enough to separate them.

## Selector source bias vs citation-loop pressure vs retrieval-contamination collapse vs mixed evidence ecology

`selector-source-bias` is about which sources an interface surfaces. The repair is source-diversification, alternate query paths, and explicit comparison against non-answer-engine search or primary sources where possible.

`citation-loop-pressure` is about visibility incentives. The repair is to stop treating citations as neutral by default, name whether the cited surface benefits from the answer engine's loop, and keep SEO/GEO adaptation from becoming evidence quality by another name.

`retrieval-contamination-collapse` is about the substrate. The repair is to look for provenance, primary-source anchors, corpus contamination warnings, and independent corroboration outside the potentially contaminated loop.

`mixed-evidence-ecology` is the fail-closed state. It prevents a fluent answer from deciding too early whether the problem is only a selector, only an incentive loop, or an actual source-pool contamination story.

## Countermodels / probes

A normal bad citation is not enough for `retrieval-contamination-collapse`; it may be only a weak source, a stale page, or a poor query. A source that ranks differently in an AI answer is not enough for `citation-loop-pressure`; it may be legitimate retrieval diversity. Publisher concern about AI search traffic is not enough for canon-level evidence-market governance; it is pressure for a compact witness and a quarantine successor.

Useful probes:

- compare answer-engine citations with primary-source, scholar, government, standards, or official documentation anchors;
- run alternate query formulations and non-answer-engine search paths when possible;
- ask whether the suspected failure is visible-source selection, citation/traffic incentive, or source-pool contamination;
- when all three are plausible, record `mixed-evidence-ecology` and lower the claim ceiling.

## Design consequences

Resolve `OQ-0161` by admitting one compact evidence-ecology witness. Use it only when online research itself is load-bearing. It should not replace ordinary source-quality checks, citation-frame controls, contradiction packets, or rival-set discipline.

Do not canonize a standing evidence-market board, citation-incentive tariff, publisher-compensation court, or provenance-dividend ledger yet. Those are quarantined as `QWS-0244` unless repeated archive-local overflows show that `evidence_ecology_state` cannot keep the work honest.

The successor open question is `OQ-0162`: what citation-incentive witness would distinguish quality-preserving generative visibility optimization from evidence-market distortion or source-grooming effects?

## Overflow test

Promote beyond this witness only if a future revision repeatedly needs to price or adjudicate citation incentives, publisher opt-outs, source grooming, compensation, traffic hoarding, or provenance dividends as first-class archive state. Until then, keep the admitted row small and use `mixed-evidence-ecology` when the substrate cannot be cleanly separated.

## Transformer-facing implication

For transformer continuations, the danger is a false independence glow: a cited answer can feel externally grounded even when the cited set was shaped by the same class of generative systems, citation incentives, or contaminated source pools being evaluated. The witness forces the model to name whether it is seeing a selector effect, an incentive loop, a contamination/collapse effect, or a mixture before spending the source set as public evidence.
