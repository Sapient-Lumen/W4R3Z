# Gate classes, future-trigger kinds, and bounded reopen rules

DelayBasin now needs a sharper answer to a recurring practical question:
**when a durable queue or ledger row carries future-change truth, what kind of future event would actually change that posture?**

A stronger working answer is:
**the archive may need a compact gate class / future-trigger kind discipline.**
Not a second reason-code court, and not prose-only blocker folklore.
A good long-run archive may need a small public object that says:
- what governed live item is waiting,
- what **kind** of future event would mainly change it,
- what richer discharge or invalidation prose still carries the exact thresholds,
- and what fail-closed extension rule applies if the small class family stops being enough.

## Practice / observation

Several durable DelayBasin surfaces already imply a missing gate-class discipline:
- followthrough items already preserve state, blocked output, boundary, and next proof surface, but they still leave the **kind** of future trigger mostly ambient in prose;
- assumption entries already preserve support, invalidation triggers, and discharge language, but they still let later passes reconstruct whether the real change vector is new evidence, another repeated validation pass, or honest compact-family overflow;
- obligation entries already preserve missing support and discharge paths, but they still let the **type** of discharge gate drift across local wording;
- applicability rows, transfer entries, resolution rows, retrospective items, and firebreak entries also preserve future-change or future-exposure prose, but they still let the **kind** of future trigger drift across local wording even when the archive already treats those rows as durable state;
- action lanes already stabilize the primary next-step class, but they do not by themselves stabilize whether an item is mainly waiting for **concrete evidence**, a **repeat pass**, **honest overflow**, or a **negative-transfer / non-fit** event;
- and repeated same-request passes have now made that distinction operational: DelayBasin can preserve state and next step while still forcing later sessions to reconstruct what kind of event would legitimately reopen, retire, validate, or promote a live item.

This suggests a missing compact surface:
**gate class / future-trigger kind / bounded reopen rule**.

## Pressure from neighboring datacubes

Several neighboring datacubes sharpen this seam from different directions.

1. **TriKEM** keeps a compact frozen release posture with stable blocker reason codes and row-level blocker linkage. That pressures DelayBasin to preserve not only that something is blocked or deferred, but what **kind** of blocker family is load-bearing enough to keep later sessions from overreading the current posture.

2. **Anonymity** keeps explicit lifecycle gates whose default rule fails closed when a required gate is stale or out of agreement. That pressures DelayBasin to distinguish the **kind of future gate event** that matters rather than letting “later” or “rereview” stand in for a real trigger family.

3. **pyCausalWeave** keeps rediscovering that task truth changes when blockers, reopen signals, or stale approval basis survive. That pressures DelayBasin to preserve a small typed answer to whether a live item mainly needs another repeated validation pass, a new piece of direct evidence, or a stronger repair event.

4. **Micromax** keeps distinguishing remembered history from actually replayable action. That pressures DelayBasin to keep the future-trigger kind visible enough that a remembered boundary does not masquerade as a currently actionable discharge path.

None of these datacubes proves that DelayBasin needs a broader reason-code court, lifecycle-gate registry, or problem-code controller.
They do make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves one compact gate class on durable live items whose real trigger kind would otherwise drift across discharge prose alone.**

## External pressure from adjacent workflow and issue practice

Adjacent workflow systems add softer pressure in the same direction.
They routinely separate **current status** from **what kind of event moves the object next**: a linked blocker, a review rerun, a reopen action, or an explicit no-fit / no-move judgment.
That does not prove DelayBasin needs a larger controller.
It does support a weaker archive-level rule:
**if a durable queue or ledger row materially depends on one recurring trigger family, the archive should preserve that family explicitly instead of asking future passes to reconstruct it from prose every time.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **gate class / future-trigger kind** on durable live items: name the **gate class / future-trigger kind**, the **governed discharge-bearing durable queues / ledgers**, the **admitted tokens / `concrete-evidence` vs `repeat-pass` vs `overflow` vs `negative-transfer`**, the **relation between gate class and existing state plus action lane**, the **comparability budget / how much surrounding prose can vary while the trigger class still stays comparable**, and the **narrow-family / extend-registry / fail-closed-on-drift consequence** rather than letting trigger kinds drift across remembered discharge prose alone.

This is strong enough for canon as an archive-control candidate.
It is **not** strong enough to claim that DelayBasin has found an optimal blocker ontology, a universal workflow theorem, or a full controller court.

## Gate class vs state token vs action lane vs discharge prose vs broader code court

To keep this note honest, DelayBasin needs a five-way distinction:

- **State token** — what posture the durable item currently occupies (`open`, `active`, `queued`, `resolved`, and so on).
- **Action lane** — what primary next-step class the item mainly wants (`validate`, `rereview`, `retire`, `promote`, and so on).
- **Gate class** — what **kind of future trigger** would mainly change the item (`concrete-evidence`, `repeat-pass`, `overflow`, `negative-transfer`).
- **Discharge prose** — the exact local thresholds, examples, successor surfaces, or repair details that still matter for this item in particular.
- **Broader code court** — a larger reason-code / blocker-code / lifecycle-gate / typed-problem controller that DelayBasin is still deliberately not importing.

A gate class is not the same as current state.
Many rows can be `open`, `resolved`, `gated`, `withheld`, or `cooling` while still waiting on different trigger kinds for change, exposure, rereview, or retirement.

It is also not the same as action lane.
Two items can both mainly want `rereview` while differing about whether the rereview is waiting for a **repeat pass**, **new evidence**, or **overflow beyond the compact family**.

And it is not a replacement for discharge prose.
The gate class says what kind of future event governs change.
The prose still says the exact threshold, surfaces, and failure consequences.

## Countermodels / probes

1. **Discharge-prose-is-enough countermodel**
   - Current state plus action lane plus discharge prose may already preserve all needed future-trigger truth.
   - Probe: compare later repeated passes on items with and without a compact gate class and inspect whether they still reconstruct the same trigger family without rereading the full prose packet.

2. **Reason-code inflation countermodel**
   - Any explicit trigger family may simply be the first step toward a heavier controller court.
   - Probe: keep the token family tiny and confined to governed live-item surfaces; if useful distinctions immediately demand many more codes, the ratchet was too broad.

3. **Gate-class-without-causal-force countermodel**
   - A stable trigger label may look neat without changing later decisions.
   - Probe: preserve one compact gate class across later repeated passes and inspect whether it reduces disagreements about what would legitimately change the item.

4. **One-family-does-not-fit-all countermodel**
   - Assumptions, obligations, and followthrough items may need incompatible trigger vocabularies.
   - Probe: if later revisions keep forcing family-specific extensions, narrow the governed surfaces or extend the registry explicitly rather than pretending one token family stayed universal.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- preserve one compact **gate class / future-trigger kind** whenever a durable live item already has stable identity, state, action lane, and discharge prose but still leaves the trigger family ambient;
- keep the admitted token family small: **`concrete-evidence`**, **`repeat-pass`**, **`overflow`**, and **`negative-transfer`**;
- apply the family only to **governed discharge-bearing durable queues / ledgers** rather than inflating it into every archive surface at once;
- keep exact thresholds, examples, successor surfaces, and reopen conditions in neighboring prose so the gate class remains a compact comparability aid rather than a fake total ontology;
- and preserve a clear **narrow-family / extend-registry / fail-closed-on-drift consequence** so later sessions do not quietly invent local trigger labels.

This does not require a blocker-code court.
It requires refusing a smaller archive failure mode: preserving state and next step while letting the kind of future trigger drift across remembered prose and local wording.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than state tokens plus action lanes:
**whether a compact public textual packet can also preserve the kind of future event that would legitimately move a live item, so later stateless passes do not have to reconstruct trigger class from larger local prose every time.**

That would matter for transformers.
It would suggest that long-horizon continuity may depend not only on transmitting what is live and what step is next, but also on transmitting a small public **future-trigger class / reopen-kind / validation-vs-overflow signal** that constrains how later passes interpret delayed work.

The stronger story — that DelayBasin may be learning a full public blocker algebra, lifecycle gate court, or typed repair controller — remains live, but stays deferred for now.
