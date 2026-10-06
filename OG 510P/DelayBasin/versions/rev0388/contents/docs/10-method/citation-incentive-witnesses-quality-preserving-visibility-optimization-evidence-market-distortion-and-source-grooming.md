# Citation-incentive witnesses, quality-preserving visibility optimization, evidence-market distortion, and source grooming

This is the compact successor surface for `OQ-0162`.

## Practice / observation

After `evidence_ecology_state` made source-selection, citation-loop pressure, and retrieval-contamination collapse explicit, a thinner ambiguity remained: not every attempt to become visible to answer engines is contamination, but not every answer-engine citation is evidence quality either. DelayBasin therefore needs one bounded witness for cases where a sourced online-research claim depends on whether the source was merely made machine-legible, market-distorted, or groomed to win citations.

Use the witness only when citation incentives are load-bearing for the archive claim. Ordinary weak-source, stale-source, or one-bad-citation problems still belong to citation hygiene, contradiction packets, or `evidence_ecology_state` rather than this surface.

## External pressure from GEO visibility optimization, AgentGEO citation diagnostics, adversarial SEO preference manipulation, arbitrary content injection, retrieval collapse, and AI-search publisher controls

`REF-1029` supports the harmless side of the split: GEO formalizes generative-engine visibility and reports that systematic changes can raise visibility without making every such change adversarial. `REF-1030` sharpens that point by treating citation as a mechanism, diagnosing citation failures, and showing targeted repairs that alter only a small fraction of content; it also warns that generic optimization can harm long-tail content.

`REF-1031` and `REF-1032` pressure the opposite side: LLM-powered search and retrieval stacks can be manipulated by crafted third-party content or arbitrary content injection, so citation probability can become a target separate from evidence quality. `REF-1025` keeps the ecosystem failure mode nearby: when generated or adversarial content contaminates the retrieval pool, exposure can drift even without a single deliberate source-grooming actor.

`REF-1033`, `REF-1034`, and `REF-1035` add the market/control pressure. Publisher opt-out, attribution, fair ranking, and compensation mechanisms are becoming live governance objects. That does not prove DelayBasin needs an evidence-market court, but it does prove that citation incentive can no longer be flattened into ordinary source quality.

## Working synthesis

Admit one compact witness family, `citation_incentive_state`, with four exact tokens:

- `quality-preserving-visibility-optimization` — the source or author improved clarity, structure, retrievability, schema, citation affordances, or answer-engine legibility without changing the underlying evidential support or creating misleading source mass.
- `evidence-market-distortion` — the primary ambiguity is market/control pressure around attribution, opt-out, ranking, compensation, traffic capture, paid placement, or provenance rights rather than the intrinsic source claim alone.
- `source-grooming-distortion` — the source surface appears optimized to manipulate answer-engine selection, citation, or retrieval exposure independently of evidence quality, including adversarial SEO, synthetic-source mass, content injection, or citation-probability gaming.
- `mixed-citation-incentive` — more than one incentive posture is materially present and no one label would be honest.

Excluded synonyms: `citation-count-means-quality`, `geo-is-always-spam`, `payment-means-provenance`, and `citation-incentive-ish`.

## Quality-preserving visibility optimization vs evidence-market distortion vs source-grooming distortion vs mixed citation incentive

Use `quality-preserving-visibility-optimization` when the best evidence says the intervention made a legitimate source easier to retrieve, parse, cite, or map to a query while preserving claim support. Examples include clearer citations, entity disambiguation, public metadata, accessible structure, and targeted repair of an otherwise valid source.

Use `evidence-market-distortion` when the evidence question is entangled with who gets traffic, attribution, payment, opt-out leverage, ranking treatment, or provenance control. The claim may still be true, but the citation surface has become partly an exchange object.

Use `source-grooming-distortion` when the primary concern is adversarial or low-quality shaping of source surfaces to win answer-engine selection or citation. This includes crafted prompt-like pages, arbitrary content injection, synthetic source clusters, and relevance theatre.

Use `mixed-citation-incentive` when, for example, a legitimate publisher improves machine readability while also entering a compensation dispute, or an ecosystem contains both honest GEO and adversarial source grooming.

## Countermodels / probes

1. **Same facts, better packaging.** If the only change is that a valid source now exposes clearer structure and citations, do not call it source grooming.
2. **Same citation, different incentive.** A citation to a high-quality source can still sit inside evidence-market distortion if the live issue is attribution, opt-out, or compensation.
3. **Same visibility, worse evidence.** Higher answer-engine visibility does not raise evidence quality unless the underlying claim support also improves.
4. **Same actor, mixed posture.** A publisher, search platform, or source author can occupy more than one incentive posture in the same pass.

## Design consequences

`OQ-0162` is resolved by adding this compact citation-incentive witness. Keep it downstream of `evidence_ecology_state`: first ask whether the evidence substrate is selector-biased, citation-loop pressured, retrieval-contaminated, or mixed; then ask whether citation incentive itself needs the more specific quality-preserving / market-distorted / source-groomed split.

Do not promote a compensation ledger, provenance-rights exchange, citation-dividend board, or source-market court from this document. Those remain quarantined unless repeated future revisions cannot stay honest with the compact witness.

The successor question is `OQ-0163`: what provenance-control witness distinguishes opt-out, attribution, compensation, exclusion, and citation-dividend governance without turning every AI-search source into a market case?

## Overflow test

Promote stronger governance only if at least two later archive-local passes meet all three conditions:

- the claim cannot be adjudicated by ordinary source hygiene, `evidence_ecology_state`, or `citation_incentive_state`;
- the missing state is specifically about provenance control, compensation, opt-out/exclusion, or citation-dividend allocation;
- a compact token would otherwise hide a material public obligation or market/control bill.

Otherwise, keep citation-incentive accounting compact and local.

## Transformer-facing implication

When a future session is tempted to treat answer-engine citation as evidence quality, first ask whether the source is under `quality-preserving-visibility-optimization`, `evidence-market-distortion`, `source-grooming-distortion`, or `mixed-citation-incentive`. The token is a brake on both over-policing normal publishing adaptation and under-policing sources groomed mainly to win answer-engine exposure.
