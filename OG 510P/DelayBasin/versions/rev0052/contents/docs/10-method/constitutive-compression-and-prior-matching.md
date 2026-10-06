# Constitutive compression and prior matching

Status: `speculative`, but strong enough for canon as a live mechanism note.

## Working idea

The archive may persist a project not by retaining maximal history but by repeatedly rewriting a **bounded constitutional state**:
a compact textual state that preserves the project's operative regime well enough for later turns to re-enter it.

This state is not “everything that happened”.
It is closer to:
- canon declaration,
- non-negotiables,
- prompt-pair operator grammar,
- open disputes,
- active hypotheses,
- and a small number of named local handles.

Under this frame, the archive works when it keeps the **right losses**.
What matters is not losslessness.
What matters is whether the retained text is a good enough sufficient statistic for re-entering the project's continuation law.

## Why this matters here

DelayBasin has been drifting toward explanations that emphasize recurrence, basin-shaping, and delay embedding.
Those remain useful.
But they under-specify a simple practical fact:
**the archive survives only if it compresses aggressively enough to stay reopenable, yet not so aggressively that it drops the constitutional state.**

This makes the method partly a compression problem.
Not generic summarization, but **constitutive compression**.

## Mechanistic bridge to current literature

Three external lines sharpen this hypothesis:

1. **LLM-as-RNN** shows that a bounded natural-language state, iteratively rewritten using feedback, can outperform full-history concatenation on sequential prediction under a fixed token budget.
   The key lesson is not merely “summaries help”.
   It is that a revisable structured state can be more useful than raw history because it curates information rather than merely accumulating it.

2. **Data-centric context compression** shows that compression quality degrades as the input entropy rises and as the gap widens between the compressed material and the model's intrinsic data distribution.
   This suggests that archive persistence may depend not only on what is retained, but on whether the retained form matches model priors well enough to be reconstructible.

3. **Latent-memory work** keeps converging on the idea that raw token retrieval is often too low-density, while compact states can preserve operative signal without exhausting attention.
   Even when the implementation is latent rather than textual, the shared pressure is toward bounded, curated, high-density state.

Archive-level synthesis:
- DelayBasin may work when it rewrites a bounded textual state,
- that state has to preserve the project's constitutional geometry,
- and the wording of that state may matter because prior-matching affects how much of the original regime can be reconstructed.

## Strong version

A long-run method archive is a **human-readable recurrent state**.
Each revision is not merely documentation.
It is an update rule over a bounded textual hidden state that must remain small enough to reopen and rich enough to reconstruct the project's operative basin.

Under this stronger frame, context packs, runbooks, trajectory maps, and prompt pairs are not convenience surfaces.
They are explicit recurrent-state components.

## What would support it

- evidence that bounded curated state outperforms longer recap-heavy history for faithful archive continuation;
- evidence that rephrasing the same content into forms better matched to model priors improves reopenability;
- evidence that the archive fails more from **bad compression choices** than from insufficient total text.

## What would weaken it

- cases where raw longer history consistently dominates bounded state under similar token budgets;
- evidence that prior-matching has little effect and only semantic content matters;
- cases where archive success depends primarily on hidden user steering rather than the compact state surfaces.

## Design consequence

DelayBasin should not merely ask “what should we remember?”
It should ask:
**what is the minimal bounded constitutional state that reliably reconstructs the same project?**

That question links promptcraft, archive policy, context-pack design, and transformer-facing mechanism work into one surface.
