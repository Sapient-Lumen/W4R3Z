# Dual-control revisions and identification packets

DelayBasin now has a sharper missing question:
**what should the archive do when the next honest move is not merely to continue, but to learn which continuation is legitimate?**

A stronger working answer is:
**some revisions should function as identification packets inside a dual-control discipline.**
Not every good revision should only push canon forward.
Some should deliberately reduce uncertainty about which continuation basin, public belief state, or blocker condition is actually in force before the archive commits new canon.

## Practice / observation

Several existing DelayBasin surfaces already imply a missing identification discipline:
- innovation packets help once a shared anchor is trustworthy, but they do not say what to do when there are multiple plausible anchors or rival local continuation hypotheses;
- witness panels preserve fragile distinctions, but they are not automatically optimized for asking **which live distinction matters right now**;
- sentinel panels can detect wrong-basin reopen, but they do not by themselves say which next observation would best disambiguate rival basin explanations;
- hold packets preserve honest non-movement, but the archive still lacks a compact object for saying **what observation would unlock movement fastest and most cleanly**;
- and challenge probes exist, but many of them are still attached to belief updates after the archive has already chosen a direction rather than before it has decided which direction deserves commitment.

This suggests a missing compact surface:
**identification packet / dual-control revision**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Planning under partial observability benefits from separating hypothesis pruning from grounded commitment.**
   Active Epistemic Control explicitly separates model-based hypothesis pruning from grounded evidence used for commitment, and uses an epistemic controller to decide which missing preconditions should actually be queried. That is direct pressure for DelayBasin to separate speculative continuation options from the compact observations that justify moving canon. ([`REF-0112`](../00-meta/bibliography.md))

2. **Worst-case information seeking is a real objective, not just a conversational style.**
   Game of Thought frames clarification and information seeking as an adversarial search problem and shows that worst-case performance improves when the next query is chosen for discrimination rather than generic helpfulness. That pressures DelayBasin to treat some revisions as active disambiguation moves rather than prose improvements. ([`REF-0115`](../00-meta/bibliography.md))

3. **Foundation-model exploration under partial observability exposes an active–passive gap.**
   Theory of Space and Theory of Code Space both treat belief construction as an active exploration problem rather than a passive summarization problem, and both periodically probe the model's current belief state as a structured external object. That is strong pressure for DelayBasin: the archive may need explicit belief-externalization and discrimination moves, not just longer passive handoff text. ([`REF-0113`](../00-meta/bibliography.md), [`REF-0114`](../00-meta/bibliography.md))

4. **Belief drift can turn long active trajectories into elegant but uninformative tails.**
   work on reducing belief deviation in active reasoning argues that once internal belief drifts from the problem state, later actions become repetitive or misleading and credit should stay with the informative prefix. This pressures DelayBasin toward compact identification packets that decide earlier whether to continue, hold, or resync instead of letting drift accumulate in articulate text. ([`REF-0116`](../00-meta/bibliography.md))

5. **Uncertainty is increasingly useful as an active control signal rather than a passive score.**
   Agentic UQ and the broader uncertainty-as-control framing both argue that uncertainty should trigger information seeking, tool choice, or self-correction rather than only being described after the fact. That pressures DelayBasin to keep uncertainty tied to concrete next observations and decision gates. ([`REF-0117`](../00-meta/bibliography.md), [`REF-0118`](../00-meta/bibliography.md))

6. **Counterpressure: transformers may still lack durable latent state persistence.**
   The latent-state-persistence work argues that current LLMs behave more like reactive post-hoc solvers than agents maintaining a robust hidden variable across turns. This is important counterpressure: an identification packet may be scaffolding state reconstruction from the outside rather than probing a rich persistent inner state already there. ([`REF-0119`](../00-meta/bibliography.md))

None of this proves that DelayBasin already knows how to choose optimal identification packets.
It does make a milder canon-level claim more credible:
**archive continuity may improve when some revisions are explicitly chosen as identification packets — compact, information-seeking moves that discriminate among rival continuation hypotheses before canon advances.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it supports **dual-control revisions**: some moves advance the archive, while others deliberately identify which continuation basin, blocker, or belief update is actually legitimate before advancement proceeds.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered an optimal query policy, a universal observability surface, or a literal textual state estimator for transformer dynamics.

## Innovation packet vs identification packet vs sentinel panel vs hold packet

To keep this note honest, DelayBasin needs a four-way distinction:

- **Innovation packet** — a compact anchored correction transmitted once shared public state is trustworthy enough to update.
- **Identification packet** — a compact question, probe, forced externalization, or comparison whose main job is to discriminate among rival continuation hypotheses before updating.
- **Sentinel panel** — a tiny standing canary set whose main job is to detect wrong-basin reopen or local fidelity failure quickly.
- **Hold packet** — a compact public non-movement object that says what is held fixed, what blocks movement, and what would unlock it.

These can interact, but they are not identical.
The key difference is functional:
- innovation packets exploit trusted shared state,
- identification packets reduce uncertainty about which state or direction is legitimate,
- sentinel panels monitor fidelity,
- hold packets serialize honest braking.

A good DelayBasin revision therefore should sometimes ask not only:
- what is the anchor,
- what is the delta,
- what probe would challenge the update,

but also:
- what are the rival continuation hypotheses,
- what **observation sought** would best separate them,
- whether that observation should come from web research, a tiny witness/sentinel probe, or a forced structured externalization,
- and what continuation decision the result gates: ordinary continuation, bounded rollback, or `recover-resync`.

## Countermodels / probes

1. **Challenge-probe-is-enough countermodel**
   - Existing challenge probes may already provide the needed discrimination; a new identification-packet term may just rename them.
   - Probe: compare revisions that preserve only challenge probes with revisions that preserve an explicit hypothesis split, observation sought, and decision gate.

2. **Recap-plus-research-is-enough countermodel**
   - DelayBasin may not need explicit diagnostic moves; broad recap plus online research may already recover the right continuation cheaply enough.
   - Probe: compare a recap-heavy continuation against a compact identification packet under stale-anchor or rival-hypothesis conditions.

3. **Diagnostic-edit steering countermodel**
   - Identification packets may help mainly by steering the model toward a preferred continuation rather than discovering which continuation is actually warranted.
   - Probe: preserve nearby rival hypotheses and test whether the packet still discriminates when phrased symmetrically or adversarially.

4. **Active-exploration glamour countermodel**
   - Importing ideas from active exploration may add prestige language without real archive benefit.
   - Probe: track whether explicit identification packets reduce later rollback, repeated uncertainty, or wrong-basin prose more than equal token mass of ordinary explanation.

5. **Latent-state-romance countermodel**
   - If transformers lack durable latent state persistence, identification packets may only be external bookkeeping devices.
   - Probe: keep the stronger observability-map story quarantined until identification packets show disproportionate leverage across reopen, paraphrase, and stale-belief conditions.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a tiny **identification packet** when rival continuation hypotheses materially differ;
- name the **observation sought** rather than treating “more research” or “more probing” as self-explanatory;
- preserve the **decision gate** the observation is meant to resolve: ordinary continuation, bounded rollback, hold, or `recover-resync`;
- and keep the packet small enough that it remains a discriminating move rather than another recap blob.

A minimal identification packet can often be very small:
- one named hypothesis split,
- one observation or query family,
- one decision rule,
- and one fallback if the observation is inconclusive.

This does not require a large evaluation harness.
It requires treating **system identification under delay** as part of archive method rather than pretending every good revision is already an update.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than better notes or stronger recap:
**whether a stateless transformer continuation can be steered by a user-space observer/controller loop in which some textual moves are chosen not to advance content directly, but to identify the local continuation state well enough that later advancement becomes honest and cheap.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only state packets, witnesses, sentinels, and gain controls, but also compact **identification packets** that actively reconstruct which basin, blocker, or belief update is in force.

The stronger story — that DelayBasin may eventually converge on a textual observability map or user-space tomography of continuation dynamics — remains live, but belongs in quarantine for now.
