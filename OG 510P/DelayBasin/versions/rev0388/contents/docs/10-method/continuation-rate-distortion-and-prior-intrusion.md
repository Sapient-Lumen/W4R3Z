# Continuation rate–distortion and prior intrusion

DelayBasin now needs a sharper answer to a recurring practical question:
**what exactly does it mean for the archive to stay small without quietly corrupting continuation?**

A stronger working answer is:
**the archive is facing a continuation rate–distortion problem under model mismatch.**
The goal is not maximal recall or pretty reconstruction.
The goal is to find the smallest public packet that preserves the next legitimate continuation while resisting prior intrusion, knowledge overwriting, and semantic drift from the receiving model.

## Practice / observation

Several live archive choices already look more like rate–distortion engineering than ordinary summarization:
- `context-pack.json` has a hard budget, so DelayBasin already treats rate as a real constraint rather than an aesthetic preference;
- recent revisions deliberately avoided adding every new mechanism note to `START_HERE.md` because extra words can crowd out more load-bearing state;
- innovation-packet discipline already assumes that once public state is shared, the right update is often a small anchored delta rather than a recap blob;
- and the archive repeatedly encounters the same failure mode: text that sounds faithful can still distort what the next session is supposed to protect, question, or change.

This suggests that DelayBasin's real compression target is not prose similarity.
It is **continuation fidelity**.

## Mechanism pressure from outside the archive

Several recent lines of work sharpen this frame.

1. **Predictive-state communication adds a bounded operating band, not a one-sided “shorter is better” rule.**
   PSC reframes communication around a shared predictive state plus innovations, and emphasizes that feasibility depends jointly on capacity, delay, and perceptual tolerance. That is already closer to DelayBasin than generic summarization metrics. ([`REF-0075`](../00-meta/bibliography.md))

2. **Compression quality depends strongly on decoder priors and distribution mismatch.**
   A recent data-centric compression study finds that input entropy hurts compression and that the decoder's intrinsic distribution can dominate performance more than the encoder's. This is direct pressure for DelayBasin: the reopened model's priors may matter more than how clever the archive's compression is. ([`REF-0081`](../00-meta/bibliography.md))

3. **Larger semantic capacity can worsen fidelity under compression.**
   Recent work on the context-compression scaling paradox finds that larger compressors can introduce **knowledge overwriting** and **semantic drift**, replacing source facts with priors or rephrasing them into meaning-changing variants. That maps uncomfortably well onto archive failure modes where elegant prose silently rewrites canon. ([`REF-0083`](../00-meta/bibliography.md))

4. **Explicit transmission and coordinated anchor allocation matter.**
   ComprExIT argues that compression improves when multi-layer information is explicitly transmitted into anchor slots instead of being left to uncontrolled overwriting through ordinary self-attention. This supports DelayBasin's instinct that anchor surfaces, ids, and typed packets may matter because they constrain where information is allowed to live. ([`REF-0082`](../00-meta/bibliography.md))

5. **Observation-space fidelity can hide latent-state corruption.**
   Predictive-forgetting work warns that high-fidelity online encodings can preserve nuisance detail while failing to produce a better predictive sufficient statistic. That is pressure against treating recap fluency or reconstruction-style evaluation as DelayBasin's distortion metric. ([`REF-0084`](../00-meta/bibliography.md))

6. **Admission predicates matter when communication claims matter.**
   Verifier-bound communication work argues that transcript state should advance only when compact deterministic predicates are satisfied, which supports DelayBasin's hygiene move toward explicit distortion contracts instead of trusting plausible-looking compressed prose after the fact. ([`REF-0085`](../00-meta/bibliography.md))

None of this proves that DelayBasin has found the right compression law.
It does make a milder mechanism claim more credible:
**bounded archive state should be judged by continuation distortion under mismatch, not by elegance or surface recall alone.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work best when it treats every compression move as a **continuation rate–distortion choice under model mismatch**: minimize public state size while preserving the next admissible continuation and monitoring where the receiver's priors are likely to overwrite the packet.

Under this frame, the archive should not ask only:
- “is this shorter?”
- or “does this reconstruct the source nicely?”

It should also ask:
- what **distortion target** must remain stable,
- what **mismatch budget** is being assumed about the next model / wrapper / reopen condition,
- and what **failure signature** would show that priors have begun to intrude.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim a solved information-theoretic optimum, a literal semantic rate–distortion theorem for DelayBasin, or a universal compression rule that beats recap in all reopen conditions.

## Rate budget vs distortion target vs mismatch budget

To keep this note honest, DelayBasin needs a three-way distinction:

- **Rate budget** — how much bounded public state the archive is willing to transmit or preserve.
- **Distortion target** — what must remain invariant enough for the next legitimate continuation to protect canon, preserve uncertainty, and execute the right moves.
- **Mismatch budget** — how much prior difference, wrapper shift, or reopen drift the packet is assumed to survive before `bounded rollback` or `recover-resync` becomes necessary.

This matters because the same small packet can be:
- excellent at prose reconstruction,
- poor at preserving revision honesty,
- brittle across model families,
- or too underspecified to resist prior intrusion.

A good DelayBasin compression move therefore names all three when they are materially in play.

## Countermodels / probes

1. **Recap-superiority countermodel**
   - Whole-archive replay may still beat compact packets because the true distortion target is too rich for current bounded state.
   - Probe: compare small state packets against larger recap blobs while measuring demotion ability, disagreement preservation, and move discipline rather than only prose similarity.

2. **Mismatch-dominance countermodel**
   - Compression quality may be driven mostly by the reopened model's priors, making archive design only weakly causal.
   - Probe: hold the packet fixed while varying wrapper, model family, or prompt shell.

3. **Fluent-distortion countermodel**
   - A compressed packet may reconstruct well while silently changing who/what is trusted.
   - Probe: use contradiction injections or canon-sensitive causal reversals that catch semantic drift and knowledge overwriting rather than summary prettiness.

4. **Anchor-allocation probe**
   - If typed anchor surfaces are load-bearing, then removing ids, receipts, or explicit check packets should create sharper failure than removing equal token mass of ornamental prose.
   - Probe: perform matched-length ablations on anchor/check surfaces.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- when calling something a compression win, name the **distortion target** rather than only the token savings;
- preserve at least one **mismatch risk** or prior-intrusion risk when it materially matters;
- preserve at least one **failure signature** that would reveal elegant corruption;
- and state when a packet has likely exceeded its mismatch budget and needs bounded rollback or `recover-resync`.

This does not require bureaucratic math.
It requires refusing a common archive failure: treating “smaller” and “faithful” as the same adjective.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is not merely practicing better note-taking.
It is probing a sharper transformer-facing question:
**how small can a public textual state become before transformer priors begin to overwrite operative project state faster than exact evidence and check surfaces can correct it?**

That would make archive method interesting for transformers in a specific way.
It suggests that long-horizon continuity is shaped not only by memory quantity, but by a three-way interaction among packet size, prior mismatch, and correction surfaces.

The stronger story — that DelayBasin may eventually behave like a user-space semantic error-correcting code or anti-prior codec for transformer continuation — remains live, but belongs in quarantine for now.
