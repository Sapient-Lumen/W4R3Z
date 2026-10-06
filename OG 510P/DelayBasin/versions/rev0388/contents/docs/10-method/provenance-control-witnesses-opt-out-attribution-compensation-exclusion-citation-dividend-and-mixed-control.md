# Provenance-control witnesses, opt-out, attribution, compensation, exclusion, citation dividend, and mixed control

This is the compact successor surface for `OQ-0163`.

## Practice / observation

After `citation_incentive_state` separated quality-preserving visibility work, evidence-market distortion, source-grooming distortion, and mixed citation incentives, one older pressure remained live: some AI-search source disputes are not mostly about citation quality or citation probability. They are about which content-use control is being asserted and whether that control should change the archive's reliance on the source.

Use this witness only when a sourced online-research claim depends on a publisher, platform, crawler, snippet, provenance, license, exclusion, compensation, or citation-dividend control. Ordinary citation hygiene, weak sources, evidence ecology, and source-grooming claims remain upstream.

## External pressure from robots.txt, AI crawler controls, snippet controls, user-triggered fetchers, content provenance, and content-use signals

`REF-1082` supplies the access-control baseline: robots.txt is a machine-readable request surface for crawlers, not an authorization layer, and caches can lag. That makes opt-out relevant, but not equivalent to payment, licensing, or security.

`REF-1083`, `REF-1086`, and `REF-1087` keep AI-search crawler roles split. Search crawlers, training crawlers, and user-triggered fetchers can have different purposes and different control behavior; DelayBasin should not collapse them into one source-use claim.

`REF-1084` and `REF-1085` add serving and model-use controls: snippet limits, nosnippet / max-snippet controls, AI Overviews / AI Mode eligibility, and Google-Extended-style model-improvement controls can affect how content is displayed or used without proving that every source citation creates a compensation case.

`REF-1088` adds the provenance representation pressure: provenance can represent entities, activities, agents, and their relationships. That supports explicit attribution and lineage, but does not itself create a source-rights court.

`REF-1089` adds the emerging content-use signal pressure: public preferences can distinguish search, AI input, and AI training. Treat those signals as evidence of declared control posture, not as self-executing legal or economic machinery inside DelayBasin.

## Working synthesis

Admit one compact witness family, `provenance_control_state`, with six exact tokens:

- `access-opt-out-control` — the load-bearing control is whether automated access, crawling, indexing, fetching, or use by a named agent is permitted, disallowed, rate-shaped, or otherwise requested.
- `attribution-control` — the load-bearing control is whether source identity, authorship, provenance, citation, link, or representation is preserved clearly enough for the claim being made.
- `compensation-control` — the load-bearing control is a payment, licensing, revenue-sharing, bargain-for-use, or traffic-allocation claim that must be named before the source is treated as ordinary evidence.
- `exclusion-control` — the load-bearing control is an asserted refusal, block, removal, de-indexing, no-snippet/no-display demand, or no-use condition stronger than ordinary attribution.
- `citation-dividend-control` — the load-bearing control is a proposed allocation of value because a source was cited, summarized, linked, or used to answer a query, but the archive has not admitted a source-market court.
- `mixed-provenance-control` — two or more control postures are materially present and no one token would be honest.

Excluded synonyms: `robots-equals-payment`, `attribution-means-consent`, `opt-out-means-compensation`, `citation-dividend-by-default`, and `provenance-control-ish`.

## Opt-out vs attribution vs compensation vs exclusion vs citation dividend vs mixed provenance control

Use `access-opt-out-control` when the key fact is a crawler, fetcher, user agent, robots directive, content signal, contractual access rule, or similar public access-control posture. This token does not by itself prove a compensation duty.

Use `attribution-control` when the source can be used only if lineage, authorship, credit, provenance, or a visible citation path is preserved. Attribution can coexist with ordinary citation, but it is not consent to every downstream use.

Use `compensation-control` when the claim depends on payment, licensing, ranking consideration, revenue allocation, traffic restitution, or similar economic control. Name the bargain or demanded bargain; do not infer one from mere citation.

Use `exclusion-control` when the core demand is that the content not be crawled, indexed, excerpted, displayed, used for AI input, used for training, or used in a particular answer surface. Exclusion can be softer than security but stronger than ordinary credit.

Use `citation-dividend-control` only when the live proposal is a dividend-like allocation from citation or answer contribution itself. Keep it quarantine-adjacent unless repeated archive-local cases show compact provenance-control tokens cannot stay honest.

Use `mixed-provenance-control` when a publisher both opts out of training and seeks attribution in search, or when an answer surface combines snippet restrictions, user-triggered fetching, licensing, and compensation claims.

## Countermodels / probes

1. **Robots is not rights settlement.** A robots or crawler directive can show access posture without deciding attribution, compensation, exclusion remedies, or security.
2. **Attribution is not consent.** Clear citation can satisfy lineage pressure without licensing training, excerpting, or synthetic reuse.
3. **Payment is not provenance.** A licensing or revenue claim can matter even when provenance is clear; do not hide it as mere citation hygiene.
4. **Exclusion is not deletion proof.** A no-use or no-snippet control does not automatically require a permanent source court or deletion-proof receipt.
5. **Signals are not governance.** Content-use signals can inform classification while still leaving legal, contractual, or platform remedies outside DelayBasin's canon.

## Design consequences

`OQ-0163` is resolved by adding this compact provenance-control witness. Keep it downstream of `citation_incentive_state`: first ask whether the problem is ordinary visibility, source-market distortion, or source grooming; then ask whether the live issue is specifically access opt-out, attribution, compensation, exclusion, citation-dividend, or mixed provenance control.

Do not promote a provenance-rights clearinghouse, citation-dividend market, source-access court, crawler treaty board, or evidence-market exchange from this document. Those remain quarantined unless repeated future revisions cannot stay honest with the compact witness.

Because `OQ-0163` was an older open branch, resolving it does not supersede the current GPU appeal chain. The next live successor surface returns to `OQ-0176`: post-portability drift and revocation governance for retired custody-exit appeal precedent.

## Overflow test

Promote stronger provenance governance only if at least two later archive-local passes meet all four conditions:

- the claim cannot be adjudicated by ordinary source hygiene, `evidence_ecology_state`, `citation_incentive_state`, or this compact `provenance_control_state` witness;
- the missing state is specifically about enforceable source-use control, not just weak attribution, stale indexing, or low-quality evidence;
- the needed remedy cannot be represented as access opt-out, attribution, compensation, exclusion, citation dividend, or honest mixed control;
- the proposed stronger surface has a shrink-back rule that prevents permanent source-market adjudication.

Otherwise, keep provenance-control accounting compact and local.

## Transformer-facing implication

When a future session is tempted to turn every AI-search citation into a payment, rights, opt-out, or source-market case, first classify the pressure as `access-opt-out-control`, `attribution-control`, `compensation-control`, `exclusion-control`, `citation-dividend-control`, or `mixed-provenance-control`. The token is a brake on both ignoring real source-control obligations and over-marketizing ordinary citations.
