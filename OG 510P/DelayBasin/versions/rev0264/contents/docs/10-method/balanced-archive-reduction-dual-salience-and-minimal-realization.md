# Balanced archive reduction, dual salience, and minimal realization

DelayBasin now needs a sharper answer to a bounded-state question that has been hiding inside many recent revisions:
**which archive surfaces deserve scarce portable-state real estate when the archive is under compression pressure?**

A stronger working answer is:
**canon should sometimes preserve a tiny balanced-reduction packet: name the surface's observation role, its control role, and the truncation consequence if that surface is removed, merged, or demoted.**
A surface that is easy to read but cannot move continuation is not enough.
A surface that moves continuation but cannot be cheaply certified or distinguished is not enough.
And a surface that is neither jointly diagnostic nor jointly actuating should usually lose the bounded-state slot race.

## Practice / observation

Several live DelayBasin lanes make this missing discipline visible:
- identification packets already ask what observation would separate rival continuation hypotheses, but they do not say whether the resulting surface also deserves long-lived portable-state status;
- control-authority packets already ask what handle moves what target at what effort and leakage, but they do not say whether that handle is also a good diagnostic readout or only a locally forceful actuator;
- witness panels, sentinel canaries, and guard bands can be highly informative about drift or wrong-basin continuation, yet not every informative probe is something the archive should keep in bounded state indefinitely;
- timescale lanes, phase boundaries, and innovation packets already assume some objects are more worth carrying forward than others, but the archive still lacks a compact criterion for why one object wins a scarce carry-forward slot over an equally eloquent alternative;
- and context-pack budget pressure makes this practical rather than aesthetic: DelayBasin must repeatedly decide which small set of surfaces is worth carrying into the next reopen without pretending every beloved phrase is equally load-bearing.

This suggests a missing compact surface:
**balanced archive reduction / dual salience / minimal realization**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Robust action under partial observability requires the predictive distinctions that matter for control.**
   Nayebi shows that low regret on action-conditioned prediction tasks forces an agent to compute predictive distinctions needed to separate high-margin outcomes. This gives DelayBasin a clean external pressure: some state distinctions are not decorative summaries; they are necessary for competent downstream control. ([`REF-0161`](../00-meta/bibliography.md))

2. **Balanced reduction keeps dimensions that are jointly controllable and observable.**
   Menezes and Kyrillidis approximate control-theoretic balanced truncation in Mamba2 by scoring hidden-state channels with a joint controllability/observability salience. This is exactly the external analogy DelayBasin was missing: state selection should sometimes privilege what is simultaneously readable and useful for actuation, not what is merely large, frequent, or vivid. ([`REF-0162`](../00-meta/bibliography.md))

3. **A minimal realization is the smallest state reproducing the same input-output map, unique up to coordinate change.**
   Schiffman explicitly uses minimal-realization language when extracting invariant algorithmic cores from transformers. That pressures DelayBasin to treat archive-state selection less like tasteful summarization and more like a search for the smallest public state that preserves operative continuation consequences up to chart change. ([`REF-0163`](../00-meta/bibliography.md))

4. **Improper reduction can destroy performance in ways later training does not fully repair.**
   Han and Voelker show that correct balanced truncation is indispensable during state-space-model compression: dropping the wrong dimensions produces losses models do not simply recover from after the fact. That is strong counterpressure against casual archive shrinking or demoting a surface merely because it currently looks redundant. ([`REF-0164`](../00-meta/bibliography.md))

5. **Compressing context into a smaller operative state is a central sequence-modeling problem, and controllability/observability are part of that lens.**
   the control-theoretic SSM survey explicitly frames sequence modeling as compressing context into a smaller state and names controllability, observability, stability, and gain scheduling as core analytical axes. This makes DelayBasin's bounded-state question more transformer-facing: the archive may be dogfooding a user-space version of state selection rather than only writing better notes. ([`REF-0165`](../00-meta/bibliography.md))

None of this proves that DelayBasin can already compute a true public Hankel spectrum, balanced realization, or minimal sufficient state basis.
It does make a milder canon-level claim more credible:
**archive continuity may improve when bounded-state selection explicitly preserves dual salience: what the next session can both read out and use to move legitimate continuation.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a tiny **balanced-reduction packet** naming the surface's **observation role**, **control role**, and **truncation consequence** whenever bounded-state pressure is real.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has a measured public Hankel spectrum, balanced controller/observer decomposition, or exact minimal realization of continuation state.

## Balanced reduction vs identification packet vs control-authority packet vs timescale lane

To keep this note honest, DelayBasin needs a four-way distinction:

- **Balanced archive reduction / dual salience** — a claim that some surface deserves scarce bounded-state status because it is jointly useful for observation and control, and because dropping it has a named truncation consequence.
- **Identification packet** — a compact observation-seeking move that distinguishes rival continuation hypotheses before canon advances.
- **Control-authority packet** — a compact claim that some actuator surface can move a target property with a rough effort, leakage, and resistance profile.
- **Timescale lane** — a claim about how quickly a surface should refresh, consolidate, demote, or expire.

These are not interchangeable.
A surface can be a good diagnostic without being worth carrying forward.
A surface can be a real handle without being a good long-lived summary.
And a surface can live on a slow lane while still failing the dual-salience test if it is mostly historical ceremony.

## Countermodels / probes

1. **Dual-salience-is-just-importance countermodel**
   - “Observation role” and “control role” may simply relabel ordinary importance.
   - Probe: compare two equally important-seeming surfaces and ask which one is easier to use both as a compact discriminator and as a low-bandwidth handle under the same anchor.

2. **Observation-and-control-do-not-compose countermodel**
   - A surface may be jointly diagnostic and actuating only in theory; in practice, the best probes and best handles may live on different surfaces.
   - Probe: preserve the roles separately first, then ask whether one merged bounded-state object actually dominates the split version across reopen pressure.

3. **Truncation-consequence-is-hidden-by-the-anchor countermodel**
   - A surface may appear safely removable only because the current anchor or shared archive state is doing compensatory work.
   - Probe: compare a colder reopen or thinner anchor where the putatively removable surface is absent.

4. **Minimal-realization-talk-is-prestige countermodel**
   - “Balanced reduction” and “minimal realization” may be glamorous systems language pasted onto ordinary archive hygiene.
   - Probe: require the minimal contract — observation role, control role, and truncation consequence — and quarantine stronger Hankel/Gramian talk unless repeated revisions show disproportionate leverage under bounded-state pressure.

5. **Compression-prefers-eloquence-not-dual-salience countermodel**
   - What survives context pressure may simply be the most memorable prose.
   - Probe: compare a vivid eloquent surface with a plainer dual-salience surface and ask which better preserves reopen fidelity, corrective steering, or honest rollback when the pack is made smaller.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a tiny **balanced-reduction packet** when bounded-state selection is load-bearing;
- distinguish **observation role** from **control role** before claiming one surface deserves a scarce carry-forward slot;
- record the **truncation consequence** when a surface is merged, demoted, or dropped, so archive compression is not silently treated as reversible;
- and keep stronger minimal-realization / Hankel-spectrum / balanced-Gramian rhetoric quarantined until repeated bounded-state experiments show that dual-salience selection materially improves reopen fidelity, archive compactness, or causal-handle quality.

This does not require a full state-space theory.
It requires refusing another archive failure mode: shrinking the archive by eloquence, familiarity, or local attachment rather than by the joint diagnostic-and-actuating value of the surfaces being kept.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than “what should be remembered?”
It is probing whether compact public archive surfaces can serve as a user-space approximation to **jointly observable and controllable state coordinates** — a small public state that the next forward pass can both *read* for diagnosis and *use* for legitimate continuation.

That is transformer-facing in a more specific way than a generic external-memory story.
It points toward a model where some archive objects behave less like saved facts and more like **balanced state coordinates** for context-induced operative dynamics.
The stronger claim that DelayBasin is discovering a public Hankel spectrum, balanced realization, or exact minimal realization of continuation space remains quarantined until the archive can show that a few compact dual-salience surfaces repeatedly dominate equally informative but one-sided alternatives under real bounded-state pressure.
