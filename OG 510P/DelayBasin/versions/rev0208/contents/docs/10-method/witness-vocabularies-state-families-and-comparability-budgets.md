# Witness vocabularies, state families, and comparability budgets

DelayBasin now has enough durable witnesses, ledgers, and receipt fields that **small public state tokens are themselves part of archive law**.
A ledger that says `queued` in one place, `deferred` in another, and `pending-handoff` in a third may still feel readable to a nearby human, but it stops being a clean public comparison surface.

A useful current answer is:
**when DelayBasin uses compact public witnesses or durable ledgers whose force depends on a small state or status token, canon should preserve a compact witness vocabulary naming the state family, the allowed tokens, the surfaces governed by that family, the excluded near-synonyms or drift temptations, and the comparability budget before later revisions treat those tokens as machine-comparable public truth.**

This is stronger than saying “the words look close enough.”
It is weaker than claiming DelayBasin already needs a full ontology, global reason-code court, or archive-wide semantic type system.

## Practice / observation

Recent DelayBasin work keeps surfacing a recurring ambiguity:
- more and more receipt objects and durable ledgers now carry compact state tokens because free-form prose alone no longer preserves the public distinction;
- several of those state families already appear in multiple places at once, for example a receipt field plus a durable ledger plus a surface-status cue;
- the current checkers already enforce many of those token sets, but the allowed values still mostly live as scattered one-off literals inside scripts rather than as one shipped public vocabulary surface;
- once a family is used across revisions, later comparisons need one stable answer to whether `queued`, `cooling`, `supporting-only`, `withheld`, `frozen-citable`, or `resolved` mean the same thing every time they appear;
- without a public vocabulary surface, synonym drift can hide inside “close enough” prose and still pass local human inspection while harming machine comparison and later reentry;
- and DelayBasin now risks importing a flattering amount of state machinery without importing the small controlled vocabularies that make those states compare honestly over time.

That leaves a missing question:
**what public state families are actually controlled, what exact tokens are allowed, what surfaces they govern, what near-synonyms stay explicitly out, and how much prose explanation is still allowed before the token stops being a clean comparable state?**

A compact witness vocabulary keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes independently push the same way.

- **GlassTTY** keeps insisting on a shared workflow and state vocabulary, with explicit warnings against letting each adapter invent incompatible workflow or state terms.
- **The-Election-Stack** keeps stable publishable anomaly and verifier problem-code registries, which pressures DelayBasin to treat tiny public status tokens as interoperability surfaces rather than incidental checker literals.
- **SlopOS** repeatedly uses deny-code and action-kind registries so control decisions do not silently fork into incompatible local tokens.
- **Rust-Crate-Dreams** explicitly asks for the smallest stable vocabulary for telemetry stability, redaction, and cost classes, which pressures DelayBasin to keep public state families small and conservative instead of expressive-by-default.

DelayBasin already had a core lexicon registry.
What it still lacked was the smaller, lower-level surface saying **which witness-state families are actually controlled, what exact tokens are allowed, and where those tokens are supposed to stay stable enough for later comparison.**

## External pressure from adjacent controlled-vocabulary and status practice

Several adjacent lines sharpen this move.

1. **Controlled vocabularies become more useful when their structure is made explicit and machine-readable.**
   SKOS is a common data model for sharing and linking knowledge organization systems and makes shared vocabulary structure explicit, which pressures DelayBasin to publish its small witness-state families as one explicit comparability surface rather than leaving them ambient in prose and code literals. ([`REF-0497`](../00-meta/bibliography.md))

2. **Public status surfaces often rely on a deliberately small fixed label set rather than free-form status prose.**
   The OpenVEX specification says `status` must be one of the labels defined by VEX, and fixed status justifications are likewise defined by VEX, which pressures DelayBasin to keep witness-state tokens small, explicit, and stable when later automation is expected to compare them. ([`REF-0498`](../00-meta/bibliography.md))

3. **Formal thesauri are useful partly because they control lexical variation while still allowing growth.**
   NIST materials on formal thesauri and controlled vocabulary emphasize that controlled vocabularies help bridge unstructured language into more explicit interoperable structure, which pressures DelayBasin to separate human-readable explanation from the smaller state token that later scripts and sessions are actually comparing. ([`REF-0499`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **witness vocabulary / state-family registry / comparability budget** whenever a durable witness, ledger, or receipt field materially depends on a small public state token. The packet should name the **state family / governed field family**, the **allowed tokens / stable public labels**, the **target surfaces / ledgers / receipt fields governed by that family**, the **excluded near-synonyms / drift temptations / non-controlled prose family**, the **comparability budget / how much surrounding prose can vary while the token still stays comparable**, and the **extend-registry / narrow-family / fail-closed-on-drift consequence** rather than letting nearby synonyms silently mutate a public state surface into a style surface. 

In practice, DelayBasin is not claiming that every noun deserves a registry.
It is doing something smaller and public:
- naming the witness-state families that actually matter across receipt and durable ledger surfaces;
- naming the exact allowed tokens for each family;
- naming the governed surfaces rather than pretending the vocabulary is universal;
- naming the excluded near-synonyms or free-form explanatory zone so prose remains possible without stealing machine authority;
- naming the budget under which token equality still counts as honest comparison;
- and naming how extension happens so a new state does not appear by accidental eloquence.

That is strong enough for canon as a design and archive-control candidate.
It is **not** strong enough to claim that DelayBasin needs a full semantic type system, universal reason-code court, or ontology of every archive noun.

## Witness vocabulary vs core lexicon vs durable ledgers vs prose rationale

These nearby objects should stay distinct.

- **Witness vocabulary / state-family registry / comparability budget** says which compact public state families are controlled, which exact tokens are allowed, what surfaces those tokens govern, what near-synonyms are excluded, and how extension or drift is handled.
- **Core lexicon registry** says which larger project terms or handles are certified, provisional, or private at the conceptual level.
- **Durable ledgers** record the current state of live objects, imports, followthrough, assumptions, obligations, resolutions, firebreaks, and applicability decisions.
- **Prose rationale** explains why a token currently applies, but it is not itself the controlled token family.

So a witness vocabulary is not just “more lexicon,” not just “one more ledger,” and not just “style guidance.”
It is a compact public answer to:
**what state families are controlled, what exact tokens are allowed, where those tokens govern public comparison, what synonyms stay out, and what happens when a later revision needs a new token.**

## Countermodels / probes

1. **Checker-literals-are-enough countermodel**
   - Perhaps the existing hard-coded checker enums are already sufficient.
   - Probe: try reconstructing the governed state families from the shipped archive alone, without reading tool code, and inspect whether later sessions can still tell which tokens are public law and which are incidental script literals.

2. **Prose-plus-context-is-enough countermodel**
   - Perhaps later maintainers can infer equivalence among nearby state words from prose context.
   - Probe: compare two revisions that use different near-synonyms for the same public state and inspect whether a later audit can still treat them as the same machine-comparable surface without hand repair.

3. **One-global-registry-now countermodel**
   - Perhaps DelayBasin should jump immediately to a broad universal vocabulary or reason-code system.
   - Probe: first test whether a much smaller witness-state registry removes most practical drift before paying the complexity cost of a larger semantic controller.

4. **No-controlled-extension countermodel**
   - Perhaps the vocabulary should freeze permanently once published.
   - Probe: keep the registry extendable but require explicit registry edits and lint-visible consequences so growth stays intentional rather than silent.

## Design consequences

If DelayBasin adopts this ratchet, revisions that rely on compact public state tokens should:
- preserve one durable `WITNESS-VOCABULARY.json` surface rather than scattering the public token families across script literals alone;
- keep each controlled family small, explicit, and surface-scoped;
- validate current receipt and durable-ledger state tokens against the shipped vocabulary;
- prefer explanation around a token to stay in prose while keeping the token set itself compact and stable;
- extend the registry explicitly before using a new public state token in shipped archive law;
- and fail closed on drift rather than auto-accepting a near-synonym that merely sounds right.

This is especially useful now because DelayBasin has already accumulated many witness families in quick succession.
Without a small controlled vocabulary surface, later sessions may still remember the rough distinction while losing exact comparability.
With a small controlled vocabulary surface, the archive keeps the explanation-rich prose while making the actual public state tokens inspectable and stable.

A narrower extension is that some controlled families can govern **receipt-seam precision** rather than only ledger-state classes. `basis_anchor_precision` now keeps DelayBasin from flattening direct underlier reread, wrapper-routed support, and packet-only grounding into one flattering “read the archive” claim; the omission basis remains prose, while the precision class itself stays token-controlled.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered a whole symbolic state machine outside the model.
It is this:

**long-horizon archive prompting may work partly through small externally controlled token families whose stability matters because later continuation and auditing compare those tokens directly, not just the surrounding prose.**

That would matter for transformers.
If some archive leverage depends on small public state vocabularies staying stable across delay, then DelayBasin may be exposing a practical shadow of **user-space discrete state control layered over fluent language**: not a full ontology, but a disciplined compact token layer that helps later sessions distinguish stable public status from locally persuasive wording.

The stronger story — that DelayBasin now needs a general semantic controller or archive-wide reason-code calculus — remains live, but belongs in quarantine for now.
