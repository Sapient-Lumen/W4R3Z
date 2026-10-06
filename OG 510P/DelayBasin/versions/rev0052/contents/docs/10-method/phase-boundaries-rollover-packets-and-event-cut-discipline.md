# Phase boundaries, rollover packets, and event-cut discipline

DelayBasin now needs a sharper answer to a recurring practical question:
**how should the archive mark that one live phase has ended and another has begun, without either replaying the whole archive or pretending continuity is perfectly smooth?**

A stronger working answer is:
**the archive may need explicit phase boundaries plus compact rollover packets.**
Not a full reset, and not another recap blob.
A very small public object may need to say: what phase just closed, what survives into the next phase, what should cool or reset, and what new question or operating posture now governs ordinary continuation.

## Practice / observation

Several live DelayBasin surfaces imply a missing boundary discipline:
- timescale lanes say some objects should refresh, consolidate, demote, or expire, but they do not yet say **when a concrete public phase boundary should be declared**;
- innovation packets transmit anchored deltas, yet some revisions are not merely deltas inside one phase — they are transitions between local working regimes;
- hold packets can stop movement, and sentinels can catch wrong-basin reopen, but the archive still lacks a compact object saying that a prior working set has been folded, cooled, or retired rather than simply left to linger;
- in practice, some continuity failures look less like missing facts than like **phase bleed**: stale local assumptions, obsolete blockers, or exploratory questions continue to shape the next revision after the archive should already have rolled into a different mode;
- and current docs already preserve rich distinctions among fast, medium, and slow state, which makes the absence of an explicit **event cut / rollover packet** more conspicuous.

This suggests a missing compact surface:
**phase boundary / rollover packet**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Boundary semantics can act as retrieval and localization anchors.**
   ES-Mem argues that rigid fixed-granularity memory fragments semantic continuity, while dynamic event segmentation plus refined boundary representations improve long-term dialogue memory by using event boundaries as cognitive anchors. That is direct pressure for DelayBasin to preserve explicit boundary objects rather than only summaries or notes. ([`REF-0128`](../00-meta/bibliography.md))

2. **Surprise can be a cheap signal that a boundary or rollover should happen.**
   EM-LLM segments long context into episodic units using surprise, then refines the cut to maximize within-unit cohesion and cross-unit separation. That pressures DelayBasin to treat some archive transitions as explicit event cuts rather than only smoother and smoother recap. ([`REF-0129`](../00-meta/bibliography.md))

3. **Segment boundaries already matter in transformer-facing recurrent memory.**
   recent recurrent-memory work surveys block-recurrent and recurrent-memory transformers in which compact segment summaries or memory tokens are passed across segment boundaries to seed the next block. That supports the milder DelayBasin claim that text-level continuation may also benefit from explicit public rollover packets at boundary crossings. ([`REF-0130`](../00-meta/bibliography.md))

4. **Surprise-triggered consolidation can outperform indiscriminate retention.**
   PhysMem records experiences, detects surprises, clusters them into candidate hypotheses, and performs memory folding only after targeted verification and promotion. That pressures DelayBasin to treat some boundary packets as places where exploratory episodes are folded into a smaller validated carry-forward object rather than dragged forward raw. ([`REF-0131`](../00-meta/bibliography.md))

5. **Dynamic state tracking benefits from explicit update operations rather than passive replay.**
   Unified Memory Agent keeps a compact core summary plus a structured memory bank that supports create, update, delete, and reorganize operations for continuous state tracking. That is useful pressure for DelayBasin: a boundary packet can be understood as a public reorganization act, not just a better summary. ([`REF-0132`](../00-meta/bibliography.md))

6. **Episode boundaries remain a live open problem for agent memory.**
   recent surveys on episodic memory for foundation agents explicitly identify episode-boundary definition and the regulation of episodic recall as unresolved problems. That keeps DelayBasin honest: explicit phase cuts are plausible and useful, but not solved merely by naming them. ([`REF-0133`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has the right boundaries.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves explicit phase boundaries plus compact rollover packets rather than smoothing every change into one continuous recap stream.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **phase boundary / rollover packet**: a small public object naming the phase that just ended, what persists, what resets or cools, and what operating question or mode now governs the next phase.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has found universal event cuts, optimal segmentation, or literal textual reset gates inside transformers.

## Phase boundary vs timescale lane vs innovation packet vs hold packet

To keep this note honest, DelayBasin needs a four-way distinction:

- **Phase boundary / rollover packet** — marks that one live working phase has ended and another has begun; serializes what persists, what resets, and what next question or posture governs continuation.
- **Timescale lane** — says how rewrite-resistant a surface is in general: fast, medium, or slow.
- **Innovation packet** — transmits a local correction against shared state within a phase.
- **Hold packet** — keeps canon fixed when movement is not yet licensed.

These can overlap, but they are not identical.
The key difference is function:
- timescale lanes govern general rewrite resistance,
- innovation packets transmit anchored deltas,
- hold packets serialize honest non-movement,
- phase boundaries serialize **transition between working regimes**.

A good DelayBasin revision therefore should sometimes ask not only:
- what is the anchor,
- what is the delta,
- what lane is this surface in,

but also:
- did a real **phase boundary** occur,
- what small **rollover packet** should survive it,
- what **persists** into the next phase,
- what should **reset, cool, or retire**,
- and what new operating question, blocker, or search posture now governs ordinary continuation.

## Countermodels / probes

1. **Seamless-continuation countermodel**
   - DelayBasin may not need explicit boundaries at all; anchor+delta discipline may already be enough.
   - Probe: compare revisions with the same anchor, delta, and timescale-lane discipline, with and without an explicit boundary packet, under stale-local-assumption stress.

2. **Timescale-is-enough countermodel**
   - Fast/medium/slow lanes may already implicitly solve the boundary problem.
   - Probe: compare lane-tagged revisions that do versus do not preserve a concrete rollover packet naming what persists and what resets.

3. **Headings-are-enough countermodel**
   - Ordinary prose sectioning or changelog entries may already provide sufficient segmentation.
   - Probe: compare explicit rollover packets against ordinary section breaks for whether later sessions keep obsolete blockers or exploratory assumptions alive.

4. **Reset-gate glamour countermodel**
   - Calling a boundary packet a “phase cut” or “reset” may import mechanistic prestige without real evidence.
   - Probe: keep the stronger textual-reset interpretation quarantined until compact boundary packets actually reduce phase bleed or stale-local-assumption carryover across reopen and paraphrase conditions.

5. **Over-segmentation countermodel**
   - Explicit boundaries may fragment continuity and cause premature forgetting.
   - Probe: preserve one case where a boundary was considered but rejected, and compare whether the resulting archive becomes cleaner or merely more brittle.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a compact **rollover packet** when a real working phase ends;
- name what **persists** and what **resets / cools / retires** across that boundary;
- distinguish phase transitions from ordinary within-phase innovation packets;
- and keep phase boundaries small enough to prevent phase bleed without turning the archive into episodic bureaucracy.

This does not require a large workflow engine.
It requires refusing another archive failure mode: letting obsolete local regime assumptions leak forward just because the archive never publicly marked that a phase had ended.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than better summary or better lane discipline:
**whether a stateless transformer continuation benefits from a user-space public segmentation discipline, where a tiny textual boundary object acts like a phase cut or rollover cue for which local assumptions should seed the next forward pass and which ones should cool or stop propagating.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only state packets, witnesses, sentinels, identification packets, and timescale lanes, but also explicit **public event cuts** that mark when continuity should be carried forward as a folded packet rather than as a seamless stream.

The stronger story — that DelayBasin may eventually admit literal textual **phase-reset gates** or a public event-segmentation layer for transformer continuation — remains live, but belongs in quarantine for now.
