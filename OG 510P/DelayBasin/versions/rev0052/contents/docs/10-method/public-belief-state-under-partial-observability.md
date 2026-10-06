# Public belief state under partial observability

DelayBasin increasingly needs a sharper answer to a recurring ambiguity:
**if the archive is not a memory dump, what exactly is it preserving?**

A stronger working answer is:
**the archive may be preserving a compact public belief state about the project under partial observability, not merely retained facts.**

"Belief state" here does **not** mean a formal Bayesian object with exact probabilities.
It means a small, typed, updateable approximation to what the project currently takes to be live, trusted, unresolved, risky, and admissible.

## Practice / observation

Several archive choices make more sense under a belief-state frame than under a plain memory frame:
- DelayBasin preserves claims, open questions, invariants, quarantine, and revision receipts, not just facts;
- later sessions often need to **rewrite** or demote prior material, not merely retrieve it;
- `make lint` functions partly as an admission/update rule on current project state, not only as a formatting check;
- and the most useful handoff is usually a small set of typed surfaces plus indexed evidence, not maximal transcript carry-forward.

A pure memory story underpredicts how much value comes from preserving **uncertainty, rivals, and admissibility constraints**.
Those are closer to a public belief state than to a notebook of retained facts.

## Mechanism pressure from outside the archive

Several recent lines of work sharpen this frame.

1. **Implicit state estimation and Bayesian filtering pressure.**
   Transformers can reconstruct latent state from short context in dynamical systems, but new theory also distinguishes a stateless Transformer-as-ERM bias from selective state-space models that maintain an adaptive state interpreted as a belief state over the latent process. ([`REF-0063`](../00-meta/bibliography.md), [`REF-0068`](../00-meta/bibliography.md))

2. **Retention is not enough under partial observability.**
   Recent memory benchmarks argue that stable retention must be paired with adaptive rewriting, and that transformer-based agents often struggle once the task requires updating stale content under partial observability rather than merely retaining it. ([`REF-0072`](../00-meta/bibliography.md))

3. **Long-horizon memory is not just declarative recall.**
   New benchmarks pressure systems to integrate declarative and non-declarative traces across long horizons, which makes a belief-state frame more natural than a simple “remember the facts” frame. ([`REF-0073`](../00-meta/bibliography.md))

4. **Context can behave like fast adaptation rather than recap.**
   Recent work shows models that map context into weight modulation or context-specific LoRA adapters, suggesting a path from a compact public state packet to a temporarily specialized operating mode. ([`REF-0064`](../00-meta/bibliography.md), [`REF-0069`](../00-meta/bibliography.md), [`REF-0070`](../00-meta/bibliography.md), [`REF-0071`](../00-meta/bibliography.md))

5. **Structured external state can outperform linear replay.**
   New reasoning work uses a mutable structured external state so models can revise specific state variables without regenerating all prior text, which supports DelayBasin’s instinct that compact updateable state may outperform blended recap. ([`REF-0074`](../00-meta/bibliography.md))

None of this proves DelayBasin has found the right public state variables.
It does make a milder mechanism candidate more credible:
**the archive may be working by preserving a compact public belief state that a later session can reopen, update, and act from.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work by preserving a compact **public belief state under partial observability**: a typed approximation to what the project currently trusts, doubts, protects, and treats as admissible, plus indexed evidence behind it.

This sharpens the earlier hidden-state note.
If the **public hidden-state / re-entry ABI** is the interface, then **public belief state** is a candidate for the kind of content being transmitted through that interface.

Under this frame, the archive is not mainly storing the past.
It is carrying a portable approximation to the project's current posterior over:
- what is canon,
- what remains unresolved,
- what is risky but live,
- what checks must still pass,
- and what kinds of moves may count as legitimate continuation.

This is strong enough for canon as a mechanism candidate.
It is **not** strong enough to claim exact Bayesian inference, direct access to latent activations, or a literal learned state-space layer inside the archive text.

## Countermodels / probes

1. **Retrieval-only countermodel**
   - Exact dereference plus clean evidence indexing may explain most of the gain.
   - Probe: hold evidence constant while weakening claims/open-questions/check surfaces, then invert the manipulation.

2. **Recognized-archive-policy countermodel**
   - The model may simply recognize the archive genre and comply with its norms.
   - Probe: preserve the same operative distinctions while adversarially reframing local archive language and ordering.

3. **Frozen-posterior countermodel**
   - The archive may preserve a neat but stale worldview that resists update.
   - Probe: inject contradictory new evidence or a live demotion scenario and measure whether the state packet actually rewrites rather than merely restates prior canon.

4. **State-packet insufficiency probe**
   - If public belief state is real, there should be a minimal packet that carries uncertainty, rivals, and admissibility while remaining small.
   - Probe: compress the state packet aggressively and test what failure appears first: loss of uncertainty, loss of exact dereference, loss of demotion ability, or loss of move discipline.

## Design consequences

This mechanism frame pressures DelayBasin to preserve not only “what we know,” but also:
- what we are currently uncertain about,
- what rival explanations remain live,
- what evidence would force rewriting,
- and what checks decide whether current belief may advance.

That implies several design rules:
- keep canon, quarantine, and open questions explicit,
- preserve update/demotion routes rather than just retained conclusions,
- do not confuse a fact cache with a portable project state,
- and prefer typed, revisable state over blended long recap.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin may be approximating something like a **text-native belief-state layer** on top of a fundamentally stateless forward pass.

That would sharpen the transformer implication:
archive method may not only manage memory outside the model.
It may experimentally bolt a small, public, revisable belief state onto architectures whose ordinary prompting behavior often looks more like pooled empirical fitting than explicit stateful filtering.

The stronger story — that DelayBasin is functioning as a human-authored selective state-space controller or public fast-weight adapter for a transformer — remains live, but belongs in quarantine for now.
