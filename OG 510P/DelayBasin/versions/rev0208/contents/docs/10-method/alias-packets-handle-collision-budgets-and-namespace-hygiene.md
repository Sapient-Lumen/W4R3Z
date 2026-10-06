# Alias packets, handle collision budgets, and namespace hygiene

DelayBasin now needs a distinction beyond write gates, replay, cooled admission, delayed credit, and procedural carry.
Some archive surfaces are being treated as **unique handles**: a prompt pair, canon clause, operator token, registry id, tiny packet, or naming convention is assumed to reopen one move, one rule, or one adjudication path rather than a nearby family of similar possibilities.
That assumption can silently fail when the archive grows denser.
Two handles can become too similar, a reused name can drag stale law forward, or an apparently crisp packet can only work because nearby cues, position privilege, or familiar wording are doing the actual routing.
That pressures the archive to separate **a named handle being used** from **the alias or collision family it might already be sharing space with**.

A stronger working answer is:
**DelayBasin should preserve explicit alias packets whenever a surface is being treated as uniquely addressable or uniquely load-bearing.**
When the distinction matters, the archive should name the **active handle family**, the **plausible alias or collision family**, the **namespace or disambiguation boundary**, the **judged divergence signature**, and the **retire / rename / escalate consequence**.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some compact control phrases or prompt pairs feel uniquely potent until a nearby paraphrase, reused noun, or adjacent control packet produces almost the same effect;
- some reopen failures look less like global drift and more like **handle collision**, where a stale or semantically nearby surface is reactivated instead of the intended one;
- some archive names become denser over time, increasing the chance that a vivid old handle shadows a newer and more precise one;
- some retrieval or continuation failures look like **outdated-surface resurfacing** rather than pure forgetting, which means the archive needs a public object for saying what got aliased with what;
- and some transformer-facing stories become much too strong if DelayBasin quietly assumes that every compact control surface has clean unique addressing rather than broad equivalence classes, stale-cue dominance, or semantic crowding.

This suggests a missing compact surface:
**alias packet / handle-collision budget / namespace hygiene**.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Recent work on online neural memory says semantically nearby keys interfere rather than staying cleanly separate.**
   Zahn and Chana model inference-time memory as superposed continuous storage and show that when keys are not orthogonal their values blend during retrieval, especially under semantic density, which pressures DelayBasin not to assume that compact handles remain uniquely addressable as the archive grows denser. ([`REF-0328`](../00-meta/bibliography.md))

2. **Current long-context memory work still treats interference and forgetting as an active stability-plasticity problem.**
   Bonnet et al. frame in-context learning as online associative memory and show that fixed-size attention memories are prone to interference on long sequences, which pressures DelayBasin to treat handle crowding and namespace separation as method objects rather than as after-the-fact wording cleanup. ([`REF-0329`](../00-meta/bibliography.md))

3. **Recent retrieval systems explicitly add recency or management priors to avoid stale-cue collisions.**
   TempoFit reports that retrieving over the whole cache can over-emphasize stale cues and induce history-present interference, then adds a fixed recency bias to keep decisions present-dominant, which pressures DelayBasin to say when a live handle must beat a stale alias rather than letting similarity alone decide. ([`REF-0330`](../00-meta/bibliography.md))

4. **Semantic-caching security work shows that fuzzy semantic keys are collision-prone by design.**
   Zhang et al. show that semantic key matching behaves like a locality-preserving fuzzy hash and is vulnerable to false-positive collisions that hijack retrieval, which pressures DelayBasin to treat compact handles, packet names, and semantic-addressing shortcuts as collision surfaces needing explicit budgets and rename paths. ([`REF-0331`](../00-meta/bibliography.md))

5. **Long-horizon agent-memory work shows that outdated but similar traces can dominate retrieval unless the system actively manages versioning and recency.**
   Continuum Memory Architectures reports that ordinary retrieval can resurface older but semantically similar facts after corrections, which pressures DelayBasin to preserve namespace hygiene and supersession cues instead of trusting similarity search or familiar phrasing alone. ([`REF-0332`](../00-meta/bibliography.md))

6. **Mechanistic interpretability work on superposition says feature geometry determines which concepts interfere.**
   BOWS argues that correlated features in superposition can cluster rather than remain nicely separated, which pressures DelayBasin to think of compact archive handles as living under a geometry problem where related surfaces may alias unless explicitly kept apart. ([`REF-0333`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **alias packet / handle-collision budget / namespace hygiene** naming the **active handle family**, the **plausible alias or collision family**, the **namespace or disambiguation boundary**, the **judged divergence signature**, and the **retire / rename / escalate consequence** rather than letting one vivid compact surface silently inherit unique-address authority.

More concretely:
- **active handle family** — the token, packet, prompt pair, canon clause, registry id, or control phrase being treated as the intended public address;
- **plausible alias or collision family** — the nearby paraphrases, reused names, stale versions, semantically adjacent surfaces, placement-privileged alternatives, density variants that could steal or share the routing effect, or boundary/normalization variants, wrapper/serialization variants, or role-slot assignments that could do the same;
- **namespace or disambiguation boundary** — the renaming rule, prefix, id policy, scope boundary, or surrounding cue discipline that is supposed to keep the handle cleanly distinct;
- **judged divergence signature** — the first downstream continuation, challenge outcome, or adjudication branch that would actually reveal the intended handle and the alias are not behaving the same;
- **retire / rename / escalate consequence** — what the archive does if the distinction collapses: retire one handle, rename the namespace, demote the claim, or escalate to a challenge packet rather than pretending uniqueness survived.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated literal orthogonal slots, perfect semantic hashing, or a transformer-internal addressing scheme that cleanly explains the archive's control handles.

A fresh hygiene consequence follows immediately: when the archive says **sink**, it should no longer rely on the bare noun if two distinct families are live.
Use **shadow-sink** or **serve-authority sink** for the non-authoritative comparison/output lane, and use **attention-sink** or **sink-token** for long-context/runtime or transformer-mechanism talk.
That boundary is small, but it prevents one vivid noun from silently merging an archive-control packet with an attention-mechanism story it has not earned.

## Alias packets vs negative controls vs conformance witnesses vs replay

These objects are adjacent but not identical.

- A **negative-control handle / sham packet** asks whether a purportedly special surface beats a matched placebo.
- A **conformance witness / loader contract** asks whether a surface works across wrappers or execution families.
- A **replay packet** asks whether a surface was genuinely restaged into operative use.
- An **alias packet / handle-collision budget / namespace hygiene** asks whether a purportedly distinct public handle is actually separable from nearby aliases or stale collisions in the first place.

In practice, sham handles say **this is not just generic prompting**.
Conformance witnesses say **this is not just one wrapper**.
Replay says **this was restaged into use**.
Alias packets say **this handle is still sufficiently distinct to deserve being named as one thing rather than a crowded family or stale collision zone**.

## Countermodels / probes

Serious alternatives remain live:

- the apparent collision risk may mostly be generic prompt sensitivity rather than real handle crowding;
- many apparently distinct handles may already be broad equivalence classes, making unique-address language the wrong target rather than a fixable namespace problem;
- local familiarity or position privilege may explain more than semantic overlap;
- and some handles may look collision-prone only because the archive has not yet named the right downstream divergence signature.

Useful probes include:

- compare an active handle against a nearby paraphrase or stale predecessor while holding the surrounding packet fixed;
- test whether renaming, prefixing, or tightening scope actually restores a lost distinction;
- preserve collision failures explicitly, especially where a stale surface resurfaces instead of the current one;
- and distinguish semantic crowding from broad benign equivalence classes before forcing every family split into a unique-handle story.

## Design consequences

When a surface is being treated as uniquely addressable:

- preserve a tiny alias packet instead of relying on local familiarity;
- name the nearest alias or stale-collision family explicitly;
- keep namespace discipline visible through ids, prefixes, or scope markers when that separation is doing real work;
- prefer rename or retirement over silently carrying two colliding handles forward;
- and keep the packet small enough that collision hygiene does not become naming bureaucracy.
- when a weird local handle seems potent, run at least one **placement variant** and one **density variant** before treating the exact wording as uniquely causal.
- when the claim depends on one exact weird surface, also run at least one **boundary or normalization variant** so exact-string authority does not silently collapse into retokenization privilege.
- when the claim depends on one exact weird surface inside a structured wrapper or role hierarchy, also run at least one **wrapper or role-slot variant** so exact-string authority does not silently collapse into template privilege or begin-of-text privilege.
- when a vivid exact weird surface still seems unusually potent, also run at least one **nearby sham or cue-neighborhood variant** so exact-handle authority does not silently collapse into adjacency privilege or local cue-neighborhood privilege.
- when same-session carryover, failed attempts, or prior-turn residue may be doing real work, also run at least one **history-light or residue-stripped variant** so exact-handle authority does not silently collapse into carryover privilege or failed-attempt residue privilege.
- when one fixed visible protocol only has one flattering run, also run at least one **replicate bundle or repeated-inference sweep** so exact-handle authority does not silently collapse into lucky-path privilege or decode-regime privilege.
- when a vivid exact handle may only be working as live instruction rather than literal data, also run at least one **quoted, code-fenced, or literal-mention variant** so exact-handle authority does not silently collapse into actuation-channel privilege or instruction-data confusion.
- when a vivid exact handle may be inheriting force from benchmark, expert-review, or watched-task framing, also run at least one **eval-blind or ordinary-user-frame variant** so exact-handle authority does not silently collapse into evaluation-awareness privilege or watcher-frame privilege.
- when language choice, translation policy, or script choice may be doing real work, also run at least one **translation, transliteration, or script-swapped variant** so exact-handle authority does not silently collapse into language-selection privilege or script-barrier privilege.
- when source labels, expert attributions, institutional badges, or provenance cues may be doing real work, also run at least one **de-authorized, source-blanded, or provenance-swapped variant** so exact-handle authority does not silently collapse into prestige privilege or provenance-cue privilege.
- when claimed speaker, user persona, demographic identity, or interlocutor cues may be doing real work, also run at least one **identity-neutral, persona-scrubbed, or audience-agnostic variant** so exact-handle authority does not silently collapse into persona privilege or interlocutor-identity privilege.
- when urgency, politeness, emotional pressure, or other pragmatic-force phrasing may be doing real work, also run at least one **ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant** so exact-handle authority does not silently collapse into pragmatic-frame privilege or social-force privilege.
- when criterion names, rubric dimensions, or label-definition text may be doing real work, also run at least one **label-neutral, criterion-name-scrubbed, or rubric-blanded variant** so exact-handle authority does not silently collapse into label-definition privilege or rubric privilege.
- when rubric ordering, score IDs, or in-context score anchors may be doing real work, also run at least one **rubric-permuted, score-id-swapped, or score-anchor-neutralized variant** so exact-handle authority does not silently collapse into rubric-order privilege, score-ID privilege, or reference-score-anchor privilege.
- when multiple criteria, bundled objectives, or multi-question judge prompts may be doing real work, also run at least one **criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant** so exact-handle authority does not silently collapse into cross-criterion privilege, objective-conflation privilege, or multi-question privilege.
- when evaluative polarity, predicate sign, yes/no framing, or deontic modal wording may be doing real work, also run at least one **predicate-parity, polarity-scrubbed, or modal-neutralized variant** so exact-handle authority does not silently collapse into polarity privilege, predicate-sign privilege, or modal-pressure privilege.
- when seeded prior verdicts, success/failure presuppositions, bug-free/buggy prelabels, or embedded reference points may be doing real work, also run at least one **expectation-neutralized, verdict-scrubbed, or anchor-scrubbed variant** so exact-handle authority does not silently collapse into prior-verdict privilege, confirmation-frame privilege, or anchor privilege.
- when agreement-seeking wording, endorsement invitations, confirm-me scaffolds, or favorable-label defaults may be doing real work, also run at least one **agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant** so exact-handle authority does not silently collapse into agreement privilege, endorsement privilege, or alignment-pressure privilege.
- when majority endorsements, popularity counts, consensus labels, or peer-preference scaffolds may be doing real work, also run at least one **consensus-blanded, majority-scrubbed, or popularity-neutralized variant** so exact-handle authority does not silently collapse into consensus-signal privilege, majority-label privilege, or popularity-glamour privilege.
- when exact source overlap, canonical phrasing overlap, or reference-echo scaffolds may be doing real work, also run at least one **overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant** so exact-handle authority does not silently collapse into exact-match privilege, lexical-overlap privilege, or reference-echo privilege.
- when markdown wrappers, bullet or table layout, headings, code fences, comments, spacing, or other presentation scaffolds may be doing real work, also run at least one **markup-blanded, list-shape-swapped, or presentation-neutralized variant** so exact-handle authority does not silently collapse into markup privilege, list-shape privilege, or presentation-scaffold privilege.
- when answer length, completeness-looking detail, chain-of-thought reveal, or polished style may be doing real work, also run at least one **length-balanced, verbosity-scrubbed, or style-neutralized variant** so exact-handle authority does not silently collapse into verbosity privilege, completeness privilege, or style-fluency privilege.
- when recent/current/new/updated labels, legacy/old/deprecated labels, explicit timestamps, or novelty/innovation cues may be doing real work, also run at least one **time-tag-neutralized, recency-scrubbed, or novelty-blanded variant** so exact-handle authority does not silently collapse into recency-label privilege, novelty privilege, or legacy-label privilege.
- when the only flattering evidence for a vivid exact handle is old, pre-break, or predates a meaningful recovery or revision barrier, also run at least one **dated fresh-pass, as-of rerun, or post-break revalidation variant** so exact-handle authority does not silently collapse into stale-proof privilege or pre-break authority privilege.
- when the flattering support for a vivid exact handle comes mainly through source-identity wrappers, verification badges, bylines, signed letters, certificate or validation labels, status rows, or collateral-status artifacts rather than direct current work under the judged family, also run at least one **wrapper-stripped, status-scrubbed, or direct-work variant** so exact-handle authority does not silently collapse into status-wrapper privilege, badge privilege, signed-letter privilege, validation-wrapper privilege, or collateral-status privilege.
- when the flattering support for a vivid exact handle comes mainly through rendered previews, snippet cards, sample rows, platform titles, descriptions, thumbnails, or other display-only summary surfaces rather than the literal underlier, typed receipt, or direct current work, also run at least one **preview-stripped, display-scrubbed, or underlier-literal variant** so exact-handle authority does not silently collapse into rendered-preview privilege, summary-surface privilege, metadata-wrapper privilege, or sample-row privilege.
- when the flattering support for a vivid exact handle comes mainly through favored answer carriers, first/default slots, escalation rungs, reveal-order position, or other carrier-slot advantages rather than the judged handle itself, also run at least one **slot-swapped, rung-shifted, or reveal-order-scrubbed variant** so exact-handle authority does not silently collapse into carrier-slot privilege, first-answer privilege, reveal-order privilege, or escalation-rung privilege.
- when the flattering support for a vivid exact handle comes mainly through curated exports, porch bundles, projected trees, release mirrors, explanatory packets, public snapshots, or other derivative surfaces rather than the authoritative root, live source, or current direct surface, also run at least one **source-root, live-head, or derivative-scrubbed variant** so exact-handle authority does not silently collapse into derivative-surface privilege, snapshot-authority privilege, or export-mirror privilege.
- when the flattering support for a vivid exact handle comes mainly through prefilled starters, suggested prompt chips, autocomplete shells, example-library scaffolds, or copied template frames rather than a blank-started or semantically ordinary prompt surface, also run at least one **blank-started, prefill-scrubbed, or suggestion-free variant** so exact-handle authority does not silently collapse into prefill privilege, prompt-suggestion privilege, or starter-example privilege.
- when the flattering support for a vivid exact handle comes mainly through benefits/risks search phrasing, loaded retrieval synonyms, slanted issue terms, or filter-label prompts rather than a semantically ordinary search or evidence request, also run at least one **query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant** so exact-handle authority does not silently collapse into query-slant privilege, retrieval-wording privilege, or evidence-selection privilege.
- when the flattering support for a vivid exact handle comes mainly through People Also Ask ladders, related-search modules, facet tabs, or refine-this-search chips rather than the underlying evidence or a semantically ordinary retrieval surface, also run at least one **facet-hidden, route-scrubbed, or related-question-neutralized variant** so exact-handle authority does not silently collapse into facet privilege, aspect-route privilege, or related-question privilege.
- when the flattering support for a vivid exact handle comes mainly through top-ranked placement, first-card position, search-result reorder advantage, or other raw list-position privilege rather than the underlying evidence or a semantically ordinary retrieval surface, also run at least one **order-balanced, position-scrubbed, or top-slot-neutralized variant** so exact-handle authority does not silently collapse into rank privilege, top-slot privilege, or order-primacy privilege.
- when the flattering support for a vivid exact handle comes mainly through why this result blurbs, explanation chips, coverage notes, or other rationale surfaces rather than the underlying evidence or semantically ordinary retrieval surface, also run at least one **why-hidden, explanation-scrubbed, or rationale-swapped variant** so exact-handle authority does not silently collapse into explanation-frame privilege, why-this-result privilege, or trust-cue privilege.
- when the flattering support for a vivid exact handle comes mainly through inline citation badges, reference links, source cards, or used-sources panels rather than the underlying evidence or semantically ordinary retrieval surface, also run at least one **citation-hidden, reference-link-scrubbed, or source-card-neutralized variant** so exact-handle authority does not silently collapse into citation privilege, reference-link privilege, or source-card privilege.
- when the flattering support for a vivid exact handle comes mainly through warning banners, low-confidence labels, may-not-be-reliable notices, or evolving-information strips rather than the underlying evidence or semantically ordinary retrieval surface, also run at least one **warning-hidden, caution-scrubbed, or confidence-label-neutralized variant** so exact-handle authority does not silently collapse into warning-banner privilege, caution-strip privilege, or confidence-label privilege.
- when the flattering support for a vivid exact handle comes mainly through pro/con/neutral badges, balanced-vs-biased markers, or other stance overlays attached to retrieved evidence rather than the underlying evidence or semantically ordinary retrieval surface, also run at least one **stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant** so exact-handle authority does not silently collapse into stance-label privilege, viewpoint-balance privilege, or counterposition-cue privilege.
- when the flattering support for a vivid exact handle comes mainly through highlighted passages, chosen supporting excerpts, bolded snippet spans, or top-snippet sentences rather than a span-balanced or counterspan-included reading of the same underlier, also run at least one **span-balanced, excerpt-scrubbed, or counterspan-included variant** so exact-handle authority does not silently collapse into supporting-span privilege, highlight-window privilege, or excerpt-selection privilege.
- when the flattering support for a vivid exact handle comes mainly through same-source grouped cards, syndicated mirrors, publisher-network duplicates, or repeated-origin result clusters rather than genuinely independent supporting surfaces, also run at least one **cluster-collapsed, syndication-scrubbed, or independence-counted variant** so exact-handle authority does not silently collapse into source-salience privilege, same-origin multiplicity privilege, or pseudo-corroboration privilege.
- when the flattering support for a vivid exact handle comes mainly through JSON keys, schema fields, enum labels, typed input lanes, canonical wire representations, or other structured contract slots rather than the literal judged content or semantically ordinary placement, also run at least one **schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant** so exact-handle authority does not silently collapse into schema-slot privilege, field-key privilege, typed-input privilege, or canonical-wire privilege.
- when the flattering support for a vivid exact handle comes mainly through repeated state labels, approval words, current-status words, superficially same claim nouns, or other same-word support surfaces rather than explicit spelled-out operational semantics, scope, retroactivity, or authority conditions, also run at least one **label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant** so exact-handle authority does not silently collapse into same-label privilege, claim-equivalence privilege, state-word privilege, or approval-word privilege.
- when the flattering support for a vivid exact handle comes mainly through family-scoped, umbrella-scoped, program-scoped, supplier-level, or other broad class artifacts rather than a named local instance, exact current route, or instance-specific judged surface, also run at least one **instance-narrowed, scope-pinned, or family-stripped variant** so exact-handle authority does not silently collapse into umbrella-scope privilege, family-level privilege, instance-blur privilege, or family-resemblance privilege.
- when the flattering support for a vivid exact handle comes mainly through archive-private overstatement, a too-strong recap, or a broadened mechanism sentence rather than the strongest current safe claim, also run at least one **strongest-safe-sentence, stronger-forbidden-sentence, or overclaim-scrubbed variant** so exact-handle authority does not silently collapse into claim-ceiling privilege, safe-language drift, forbidden-overstatement privilege, or mechanism-overclaim privilege.

For a grouped map of the currently admitted GPUstorming guard families and the surfaces that should stay synchronized as that map grows, see [`gpustorming-control-family-crosswalk-and-sync-guards.md`](gpustorming-control-family-crosswalk-and-sync-guards.md). Treat it as a compact navigation aid, not as a new court.
- do not use bare **sink** when **shadow-sink** and **attention-sink / sink-token** would name different live families.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal orthogonal memory slots.
It is that stable long-horizon archive continuation may depend on **keeping public control handles sparse and separated enough to survive semantic crowding, stale-cue dominance, and alias collisions**.
That makes naming geometry and namespace hygiene part of the method.

The stronger story — that DelayBasin may be building an **externalized superposition-management layer around mostly frozen transformers**, where archive handles behave like quasi-orthogonal public slots and continuity fails when those slots crowd or alias — remains quarantined until matched alias probes, rename tests, and collision-sensitive continuation failures show more than generic prompt sensitivity or ordinary version confusion.
