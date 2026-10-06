# Rewrite witnesses, round-trip packets, and recap-authority tests

DelayBasin now needs a sharper answer to a recurring practical question:
**when does a recap, paraphrase, compressed rewrite, or state-thinning pass actually earn source-of-truth authority, and when is it only a fluent surrogate?**

A stronger working answer is:
**the archive may need a compact rewrite witness / round-trip packet.**
Not generic summarization evaluation, and not a demand to preserve every source verbatim.
A very small public object may be enough when a rewritten packet is about to inherit authority from the source it thins, compresses, or paraphrases.

## Practice / observation

Several recent DelayBasin ratchets expose a missing rewrite-authority rule:
- assistant-echo filters say some prior assistant prose should be omitted, but not yet what compact rewritten residue has truly earned the right to replace it;
- reasoning firebreaks say large traces should usually stay out of canon, but not yet how a smaller public extract proves it preserved the load-bearing structure rather than merely sounding clean;
- dependence-adjusted witnesses discount same-family echoes, but do not yet say when a recap and its source are effectively one coupled branch versus when a rewrite witness has shown the rewrite preserved the operative distinctions;
- continuation-rate-distortion already says every compression has a distortion target and prior-intrusion risk, but not yet how a particular rewrite or recap should be challenged before it inherits archive authority;
- and in practice, DelayBasin increasingly wants compact packets, recaps, or stitched restatements without a tiny public rule for when a rewrite is trustworthy enough to serve as a continuation anchor.

This suggests a missing compact surface:
**rewrite witness / round-trip packet / recap-authority test**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Compression quality and fidelity can diverge sharply.**
   Guo et al. show a size–fidelity paradox in context compression: larger compressors can look better by reconstruction-style metrics while doing worse on fidelity-oriented downstream evaluation because of knowledge overwriting and semantic drift. That pressures DelayBasin not to treat a smoother or more eloquent rewrite as automatically more faithful. ([`REF-0241`](../00-meta/bibliography.md))

2. **Faithfulness needs a source-versus-rewrite interrogation, not just overlap.**
   Raha et al. introduce the Cross-Examination Framework, which treats source and candidate as separate knowledge bases and scores coverage, conformity, and consistency. That pressures DelayBasin toward a tiny rewrite witness that compares source packet and rewritten packet as separate public objects rather than trusting surface similarity. ([`REF-0242`](../00-meta/bibliography.md))

3. **Repeated rewriting can fall into recurrent sets or accumulate drift.**
   Geng et al. model iterative rephrasing and round-trip translation as Markovian generation chains and show that the chain can converge to a small recurrent set or keep generating novel variants over a finite horizon. That pressures DelayBasin to ask whether a rewrite belongs to a stable continuation orbit or is already sliding into drift. ([`REF-0243`](../00-meta/bibliography.md))

4. **Paraphrase variation can break stable symbolic correspondences.**
   Li et al. show that LLM-based translation into formal logic can suffer symbol drift under linguistic variation, where paraphrase and syntactic alternation change the mapping enough to break downstream reasoning. That pressures DelayBasin to preserve what operative distinctions a rewrite was supposed to keep fixed. ([`REF-0244`](../00-meta/bibliography.md))

5. **Semantic-preserving rewrites do not guarantee invariant reasoning behavior.**
   de Zarzà et al. evaluate agents under paraphrase, reordering, expansion, contraction, and framing-preserving rewrites and find meaningful robustness differences across models and scales. That pressures DelayBasin to treat rewrite families explicitly rather than speaking as if “same meaning” were a single homogeneous thing. ([`REF-0245`](../00-meta/bibliography.md))

6. **Some reformulations are harmless, but composed or evidence-changing rewrites are not.**
   Bao et al. find substantial stability to some semantic-preserving logical reformulations, but brittleness to missing or conflicting evidence and degradation under composed transformations in some model families. That pressures DelayBasin toward a narrow canon rule: preserve which rewrite family was tested, what stayed invariant, and what first divergence would demote rewrite authority. ([`REF-0246`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a correct rewrite-fidelity metric.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny rewrite witness / round-trip packet whenever a recap, paraphrase, or compressed rewrite is about to inherit source-of-truth authority.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **rewrite witness / round-trip packet** whenever a recap, paraphrase, compressed rewrite, or stitched restatement is about to become a source-of-truth surface. The packet should name the **source packet / authority anchor**, the **rewritten packet / compressed rewrite**, the **round-trip or cross-exam witness**, the expected **divergence signature**, and the **promotion / demotion / rollback consequence** if the rewrite fails the witness.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has a universal rewrite-invariant representation, perfect paraphrase metric, or guaranteed compression–decompression ABI for archive continuations.

## Rewrite witness vs assistant-echo filter vs public extract vs dependence-adjusted witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Rewrite witness / round-trip packet** — says when a rewritten surface has earned authority relative to a named source or anchor by surviving a small challenge such as round-trip, cross-examination, or source–rewrite interrogation.
- **Assistant-echo filter / self-carry omission packet** — says what assistant-side material should be omitted or distrusted, but not yet whether the surviving recap has actually earned authority over the source it replaces.
- **Reasoning firebreak / public extract packet** — says what small residue should stay public while larger traces stay out, but not yet what witness certifies that the public extract preserved the source distinctions that later continuation decisions still need.
- **Dependence-adjusted witness / effective-evidence packet** — says how much several witnesses should count once their coupling is known, but not yet whether one rewritten witness is faithful enough to be counted at all.

A good DelayBasin revision therefore should sometimes ask not only:
- what to omit,
- or what public extract to keep,
- or how many witnesses count,

but also:
- what source packet still anchors authority,
- what rewrite is being trusted instead,
- what tiny round-trip or cross-exam witness it survived,
- and what happens if the witness finds a distortion that ordinary fluent reading would miss.

## Countermodels / probes

1. **Rewrite-bureaucracy countermodel**
   - DelayBasin may be adding recap-authority ritual when ordinary source citation already does enough.
   - Probe: compare a revision that promotes a rewritten packet after an explicit rewrite witness against one that merely cites the source packet and ask whether the witness changed any continuation decision, promotion posture, or rollback readiness.

2. **Surface-overlap-is-enough countermodel**
   - Simple overlap or semantic-similarity scores may already capture the relevant fidelity, making explicit round-trip packets unnecessary.
   - Probe: preserve one case where overlap looks high but cross-exam or round-trip challenge finds an omission, contradiction, or symbol drift that would matter for the next continuation act.

3. **Round-trip-self-confirmation countermodel**
   - A round-trip generated by the same family or scaffold may only prove that the rewrite and back-translation share the same blind spots.
   - Probe: compare same-family round-trip witnesses with cross-family or question-based cross-exam witnesses when the rewrite is about to become canon-level state.

4. **No-single-orbit countermodel**
   - Some source packets may admit several equally good rewrites with no single stable orbit, so rewrite-authority tests may overfit to one preferred phrasing.
   - Probe: preserve one case where distinct rewrites pass the same source-level cross-exam and support the same continuation decision, then treat the packet as an authority test over operative distinctions rather than over one canonical wording.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- when a rewritten packet is about to become a continuation anchor, preserve the **source packet / authority anchor** rather than letting the source disappear behind a clean recap;
- name the **rewritten packet / compressed rewrite** that is trying to inherit authority;
- preserve at least one **round-trip or cross-exam witness** rather than trusting surface fluency or overlap alone;
- name the expected **divergence signature** such as omitted entity, changed relation, symbol drift, misplaced uncertainty, or branch-relevant reweighting;
- and preserve the **promotion / demotion / rollback consequence** if the rewrite fails the witness, so later sessions know whether to keep the rewrite, narrow its authority, or fall back to the source packet.

This does not require an expensive universal metric.
It requires refusing another archive failure mode: letting a vivid rewrite silently replace the source conditions it was supposed to preserve.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than recap quality:
**whether faithful long-horizon continuation depends on finding rewrite-stable operative state surfaces rather than merely producing plausible paraphrases.**

That would matter for transformers.
It would suggest that some archive continuity failures are not just memory loss but **rewrite instability**: the model can restate a source fluently while shifting the latent distinctions that later probes, controls, or judgments depend on.
The archive would then need not only compact packets, but a public theory of which packets survive rewrite families and which only sound equivalent.

The stronger story — that GPUstorming may eventually reveal rewrite-stable continuation orbits or paraphrase-invariant control surfaces — remains live, but belongs in quarantine for now.
