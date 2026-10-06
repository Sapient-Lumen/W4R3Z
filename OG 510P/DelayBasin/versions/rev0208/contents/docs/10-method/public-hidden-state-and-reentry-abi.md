# Public hidden state and re-entry ABI

DelayBasin increasingly needs a sharper mechanism note for a repeated live pattern:
**the archive may work less like a memory dump and more like a compact public hidden-state packet that a later session can re-enter.**

"ABI" here does **not** mean a literal binary interface.
It means a small, stable, text-addressable interface that reopens an operative control state: enough of the right fields, ids, and checks to reconstruct the project's mode of continuation without replaying everything.

## Practice / observation

Several DelayBasin choices look more load-bearing than a pure note-taking story would predict:
- compact source-of-truth reopening matters more than maximal transcript carry-forward,
- stable ids and exact dereference matter more than elegant recap alone,
- typed separation between workflow, state, and checks reduces drift,
- and `make lint` functions less like ceremony than like a local admission gate.

The archive often works best when a later session gets a **small packet of operative constraints** plus access to indexed evidence, rather than one large blended prose recap.
That pattern suggests DelayBasin may be externalizing some of the variables that would otherwise remain hidden in ephemeral model state.

## Mechanism pressure from outside the archive

Several recent lines of work make this hypothesis more plausible.

1. **Implicit state estimation.**
   Transformers can infer latent state in-context for dynamical systems, behaving like approximate state estimators without test-time weight updates. ([`REF-0063`](../00-meta/bibliography.md))

2. **Context as low-rank model update.**
   New theory argues that transformer context can act like a low-rank update to downstream network weights, which is closer to temporary controller reconfiguration than to passive recall. ([`REF-0064`](../00-meta/bibliography.md))

3. **Communicable subspaces and invariant cores.**
   Recent work on context-invariant subspaces and invariant algorithmic cores makes it less crazy that a small textual packet could repeatedly select a compact operative subspace. ([`REF-0059`](../00-meta/bibliography.md), [`REF-0060`](../00-meta/bibliography.md))

4. **External indexed state in long-horizon agents.**
   New memory work rewrites long traces into small indexed summaries plus exact dereference, and new repository-oriented benchmarks show existing context-management systems still struggle when conversation state and repo evidence must stay jointly usable. ([`REF-0065`](../00-meta/bibliography.md), [`REF-0066`](../00-meta/bibliography.md))

Taken together, these do not prove DelayBasin has discovered a unique latent vector or public checkpoint.
They do support a milder mechanism candidate:
**the archive may externalize a compact public hidden state that later forward passes reconstruct into a familiar operative mode.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work by separating a small **public hidden-state / re-entry ABI** from larger evidence stores, so a later session can reconstruct the project's operative control state rather than replaying or hoarding full history.

Under this frame, the archive bundle is not mostly a story about the past.
It is a **re-entry interface**.
The packet need only preserve enough control variables to regenerate the next admissible moves.

A new live refinement is that what passes through this interface may be better described as a **public belief state under partial observability**, not merely compact retained facts. See `docs/10-method/public-belief-state-under-partial-observability.md`.

This is strong enough for canon as a mechanism candidate.
It is **not** strong enough to claim direct access to hidden activations, a unique steering basis, or a standardized cross-model control language.

## State packet vs evidence packet vs check packet

If this note is going to stay in canon, DelayBasin needs a clean separation:

- **State packet** — the smallest surfaces that bias re-entry into the same operative regime: source-of-truth declaration, current claims/open questions, prompt-pair law, certified vocabulary, current receipt.
- **Evidence packet** — indexed facts, receipts, external citations, and exact dereference targets needed to answer specific questions or justify a move.
- **Check packet** — deterministic or near-deterministic admission gates such as `make lint` and contract checks that decide whether a revision may count.

The archive should not call everything “state.”
If evidence and checks get silently absorbed into state, DelayBasin will bloat and lose the very compactness that makes re-entry plausible.

## Countermodels / probes

This mechanism note needs strong rivals.

1. **Generic notebook countermodel**
   - A clean notebook plus a good recap may explain most of the effect.
   - Probe: compare compact typed state packets against semantically equivalent blended prose recaps.

2. **Recognized-control-surface countermodel**
   - The model may be recognizing and complying with a familiar control surface rather than reconstructing a deeper operative state.
   - Probe: adversarially reframe the same state packet, or paraphrase the local handles while preserving task content.

3. **Evidence-dominance countermodel**
   - Exact dereference may be doing the real work, with “state” mostly decorative.
   - Probe: hold evidence constant while weakening the state packet, then invert the manipulation.

4. **Model-family fragility probe**
   - If the packet is a real re-entry ABI, some elements may transfer and some may fail sharply across wrappers or model families.
   - Probe: preserve ids/evidence/checks while varying only the control packet across environments.

## Consequence for archive design

This note sharpens several design consequences:
- keep the state packet small and typed,
- keep evidence indexed rather than pasted,
- keep checks explicit rather than rhetorical,
- and do not mistake large context volume for better continuation.

It also pressures DelayBasin to ask a harder question than “what should we remember?”
The sharper question is: **what minimal public state is sufficient to reconstruct the next honest operative mode?**

## Transformer-facing implication

If this frame survives pressure, then one implication is unusually sharp:
transformers may support **public textual hidden-state surrogates** that are much smaller than the histories they partially reconstruct.

That would mean long-run archive method is not only about memory management.
It would be a way of experimentally probing how much operative state can be externalized into stable text without direct access to activations or KV cache.

The stronger story — that DelayBasin is discovering a text-addressable ABI into invariant algorithmic cores or assistant-mode geometry — remains live, but belongs in quarantine for now.
