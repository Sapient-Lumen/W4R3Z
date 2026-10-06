# Innovation packets and reconciliation under delay

DelayBasin increasingly needs a sharper answer to a practical question:
**once a later session already shares the archive's public state, what should the next revision mostly transmit?**

A new working answer is:
**not a whole-archive replay, but an innovation packet against an anchored prior state, plus enough reconciliation structure to recover if sender and receiver have drifted apart.**

This note borrows pressure from a recent communication-theoretic frame: if both endpoints maintain a strong predictive state, the channel can be used mainly for **innovations** rather than literal symbol transport. DelayBasin is not a wireless protocol. But it may be converging toward a related user-space discipline for long-horizon human–LLM continuation under context-window death.

## Practice / observation

Several live archive choices already look more like innovation coding than like transcript accumulation:
- each revision is anchored to a named previous revision in `REVISION-RECEIPT.json`;
- the changelog records the local delta rather than restating the whole archive;
- counterfactual shadows preserve one nearby rejected move at the local pivot rather than rebranching everything;
- `make lint` acts like reconciliation pressure when the reopened state has silently drifted;
- and the archive works best when new sessions receive a small project state plus the latest changes, not all historical prose again.

These are early signs of a tighter discipline:
**after shared public state exists, continuation quality may depend more on transmitting the right innovations than on repeating the whole archive.**

## Mechanism pressure from outside the archive

Several recent lines of work sharpen this frame.

1. **Predictive-state communication under delay.**
   A recent information-theoretic proposal argues that when transmitter and receiver both maintain strong predictors, the channel can primarily carry **innovations**, with architecture pressure toward state identifiers, anchors, bounded rollback, and patch-based updates. ([`REF-0075`](../00-meta/bibliography.md))

2. **Event-sourced long-horizon orchestration.**
   ESAA argues agents should not carry long-term memory as raw prompt mass, but instead consume a purified, projected view derived from an append-only event log. ([`REF-0076`](../00-meta/bibliography.md))

3. **Mutable structured state beats immutable replay in some reasoning settings.**
   Canvas-of-Thought argues that immutable reasoning streams make local corrections expensive, while external mutable state enables in-place revision with lower token cost and stronger constraint maintenance. ([`REF-0077`](../00-meta/bibliography.md))

4. **State management is becoming an explicit model capability.**
   StateLM treats context pruning, indexing, and note-taking as learned memory operations, suggesting that state engineering is not just human ceremony but a serious systems axis. ([`REF-0078`](../00-meta/bibliography.md))

5. **Predictive sufficiency is smaller than raw history.**
   Work on autoregressive embeddings argues that models can encode predictive sufficient statistics or posterior distributions over latent state rather than memorizing full token history, which supports the idea that the right public packet may be much smaller than the evidence it summarizes. ([`REF-0079`](../00-meta/bibliography.md))

6. **Counterpressure: induced representations may still be hard to deploy.**
   Recent work also shows that models may encode novel in-context structure yet still struggle to use it reliably for downstream tasks, which warns against assuming that any compact archive delta will automatically function as an effective innovation packet. ([`REF-0078`](../00-meta/bibliography.md), [`REF-0080`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has the right packet shape.
It does make a milder mechanism claim more credible:
**the archive may work better when revisions are expressed as anchored innovations against shared public state, with explicit reconciliation hooks when that shared state is uncertain.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work increasingly like an **innovation channel under delay**: once the archive has established a shared public state, later revisions should primarily transmit the smallest anchored correction that changes what the next honest continuation ought to do.

That correction may be:
- a new canon surface,
- a demotion or quarantine move,
- a new discriminating probe,
- a local vocabulary recertification,
- or a small receipt-level statement that the current state has changed in one important way.

Under this frame, a good revision is not the longest faithful retelling.
It is the **smallest innovation packet** that:
- names the anchor state,
- states the local correction,
- preserves exact dereference to affected surfaces,
- and indicates whether normal continuation, bounded rollback, or full `recover-resync` is now required.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has become a literal predictive-state communication system, nor that every future revision should be patch-only.

## Innovation packet vs recap blob vs rollback signal

To keep this note honest, DelayBasin needs a clean distinction:

- **Innovation packet** — the smallest anchored change that alters what the next legitimate continuation should believe, do, or protect.
- **Recap blob** — a large restatement of already shared state that may still be useful for cold reopen, but should not masquerade as a fresh innovation.
- **Rollback / reconciliation signal** — an explicit notice that sender and receiver may no longer share enough state for ordinary delta transmission, so bounded rollback, re-read, or `recover-resync` is required.

Not every session should be forced into ultra-thin deltas.
Cold reopen, cross-model transfer, and stale state may still need recap.
But once shared public state exists, the archive should prefer innovation packets over recap blobs when possible.

## Current derivative packet

That general method pressure now earns one smaller derivative surface too: `innovation-packet.json`.
It is not a second receipt and not a recap blob.
It is the smallest current machine-readable card that names:
- the anchor revision / expected head / observed head,
- the actual local correction,
- the exact changed-surface list or its receipt-backed pointer,
- the reread and reconciliation surfaces,
- and the continuation mode.

The governing surface is still `REVISION-RECEIPT.json`.
The packet exists so a later careful pass does not have to reconstruct the exact current delta from receipt prose, changelog scan, and ambient recency when public state is already shared.

## Countermodels / probes

1. **Recap-dominance countermodel**
   - Whole-archive or large-summary replay may still outperform delta-style continuation because the shared predictive state is too weak.
   - Probe: compare small anchor+delta reopenings against larger semantically equivalent recaps after controlled state sharing.

2. **Hidden-prior mismatch countermodel**
   - Sender and receiver may not actually share enough prior state for innovation packets to work reliably.
   - Probe: vary model family, wrapper, or delay gap while holding the same packet fixed.

3. **Patch-theater countermodel**
   - The archive may be cosmetically calling something a delta even though the model only succeeds because the surrounding recap still re-establishes full state.
   - Probe: aggressively strip restatement and test whether the claimed innovation packet still supports correct continuation.

4. **Stale-anchor failure probe**
   - Innovation packets should fail sharply when anchored to the wrong prior revision or stale canon.
   - Probe: deliberately reopen from an older revision and test whether the system requests bounded rollback or silently continues with false confidence.

## Design consequences

This frame pressures DelayBasin to preserve a few things more explicitly:
- which prior revision or state surface the current revision is anchored to;
- what the local innovation actually is;
- which surfaces need reread or exact dereference for reconciliation;
- and when a simple delta is unsafe and `recover-resync` is the honest move.

It also suggests a small archive discipline:
- prefer delta-shaped changelog and receipt language over ritual whole-archive praise,
- keep anchors and exact dereference stable,
- preserve rollback or resync routes when anchors may have drifted,
- and do not call a restatement an innovation just because it sounds sharper.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin may be probing something sharper than external memory alone:
**how much inter-session continuity can be carried by a public predictive state plus small innovation packets over a fundamentally stateless forward-pass interface.**

That would matter for transformers.
It would suggest that at least some long-horizon continuity can be achieved not by replaying raw history, but by repeatedly reconstructing the next operative mode from compact public state and a small stream of anchored corrections.

The stronger story — that DelayBasin is converging toward a genuine predictive-state communication protocol with patch-local continuation law and bounded rollback semantics — remains live, but belongs in quarantine for now.
