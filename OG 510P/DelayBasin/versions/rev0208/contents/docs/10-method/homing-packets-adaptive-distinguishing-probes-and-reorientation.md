# Homing packets, adaptive distinguishing probes, and reorientation under ambiguity

DelayBasin now has a sharper missing question:
**what should the archive preserve when a later session is not merely missing facts, but is genuinely uncertain which local continuation state it is in?**

A stronger working answer is:
**some bounded-state surfaces should function as homing packets: compact, possibly branching probe families that re-orient the next session among a named ambiguity class before canon advances.**

This is stronger than “ask one good question,” but weaker than claiming a full public state estimator.
It says the archive may sometimes need a tiny **orientation policy**, not just more recap.

## Practice / observation

Several existing DelayBasin surfaces point at a missing reorientation layer:
- identification packets can name one hypothesis split and one observation sought, but some reopen situations stay ambiguous after one probe and need a short branching sequence rather than a single query;
- sentinel panels detect that something is wrong, but they do not by themselves say how to re-orient once a canary trips;
- witness panels preserve fragile distinctions, but they are not automatically chosen to orient a fresh session among rival local states;
- intervention-equivalence and causal-control packets say which distinctions must survive compression, but not which **next adaptive probe family** recovers the right state most cheaply when that distinction is live;
- and recap-heavy reopen text often expands while still failing to answer the practical question: **which short observation path would tell the next session where it actually is?**

This suggests a missing compact surface:
**homing packet / adaptive distinguishing probe family**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Homing sequences are explicitly about orientation under state uncertainty.**
   Rivest and Schapire define a homing sequence as an input sequence that “orient[s]” the learner by using observed outputs to determine the resulting state. That is unusually close to DelayBasin's reopen problem: not generic memory recovery, but compact reorientation after uncertainty about current state. ([`REF-0181`](../00-meta/bibliography.md))

2. **Adaptive distinguishing sequences are often more available and more compact than fixed ones.**
   Hierons, Jourdan, and Ural show that adaptive distinguishing sequences are usually sufficient where preset distinguishing sequences were previously assumed, and that they are strictly more common and can be exponentially shorter. This is direct pressure against recap theater: DelayBasin may need small branching probe trees rather than longer fixed probe lists or larger summaries. ([`REF-0182`](../00-meta/bibliography.md))

3. **Active sensing treats information gathering as a decision problem, not a passive add-on.**
   Recent survey work on active sensing explicitly categorizes information-gathering problems as decision-theoretic and distinguishes reactive sensing from active sensing. That supports a DelayBasin move from passive recap toward explicit reorientation policies when ambiguity classes are live. ([`REF-0183`](../00-meta/bibliography.md))

4. **Bayesian experimental design treats adaptive measurement choice as an optimization target.**
   Modern Bayesian experimental design frames experiment choice as maximizing expected information and emphasizes adaptive, sequential design. That does not mean DelayBasin should become a formal optimizer, but it does pressure the archive to preserve which next probes are expected to collapse the relevant uncertainty fastest. ([`REF-0184`](../00-meta/bibliography.md))

5. **Informative input design in system identification reinforces the same point.**
   Recent system-identification work treats the choice of inputs as a way to reduce uncertainty in model parameters and highlights the open problem of selecting input sequences that lead to highly informative measurements. This sharpens DelayBasin's need to preserve not only a current packet but, when necessary, a compact next-probe family that is informative about the local continuation state. ([`REF-0185`](../00-meta/bibliography.md))

6. **Counterpressure: a good recap plus one identification packet may already be enough.**
   DelayBasin should not assume that every ambiguity class needs a multi-step orientation policy. Many cases may collapse under one identification packet or one hold packet plus one web query. Homing-packet language is only justified when the branch structure itself is doing real work.

None of this proves that DelayBasin already knows how to choose optimal orientation policies.
It does support a milder canon-level claim:
**archive continuity may improve when some fragile ambiguity classes are paired with compact homing packets — short, possibly adaptive probe families that orient the next session before canon advances.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves **homing packets** for live ambiguity classes: small, branching probe families whose outcomes orient the next session into the right local continuation state, or else escalate honestly to hold, bounded rollback, or `recover-resync`.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered an optimal experiment policy, a full observability map, or a literal public automaton for continuation dynamics.

## Identification packet vs homing packet vs sentinel panel vs witness panel

To keep this note honest, DelayBasin needs a four-way distinction:

- **Identification packet** — one compact observation-seeking move whose main job is to discriminate among rival continuation hypotheses before updating.
- **Homing packet** — a small, possibly branching probe family whose main job is to orient the next session among a named ambiguity class when one observation may not be enough.
- **Sentinel panel** — a tiny standing canary set whose main job is to detect wrong-basin reopen or drift quickly.
- **Witness panel** — a tiny discriminative example or boundary set whose main job is to keep a fragile distinction explicit.

These interact, but they are not identical.
The key difference is functional:
- identification packets ask **which of these rivals is live right now**;
- homing packets ask **what short adaptive path gets us oriented enough to continue honestly**;
- sentinel panels ask **did the reopen drift**;
- witness panels ask **what distinction must not be flattened**.

A good DelayBasin revision should sometimes ask not only:
- what is the hypothesis split,
- what observation is sought,
- what intervention branch matters,

but also:
- what **ambiguity class** remains after the first probe,
- what **probe family or branch rule** should be tried next,
- what **orientation/update rule** the outcomes induce,
- and what **stop condition** ends orientation and allows ordinary continuation or forces escalation.

## Countermodels / probes

1. **Identification-packet-is-enough countermodel**
   - A single identification packet may already solve nearly all practical ambiguity classes; homing-packet language may just rename repeated identification.
   - Probe: compare one-shot identification against compact multi-step homing packets under stale-reopen and rival-local-state conditions.

2. **Recap-plus-web-is-enough countermodel**
   - Ordinary recap plus one fresh web search may already re-orient later sessions cheaply enough.
   - Probe: compare recap-heavy reopen against a compact homing packet on the same ambiguity class and track whether the extra branch structure changes continuation choice.

3. **Orientation-theater countermodel**
   - The archive may begin preserving elaborate probe trees that look scientific but do not actually change continuation outcomes.
   - Probe: require each homing packet to name the first branch outcome that would alter continuation, rollback, or hold posture.

4. **Adaptive-glamour countermodel**
   - Importing automata or experimental-design language may add prestige without improving archive method.
   - Probe: compare token cost and actual uncertainty reduction against equally small identification packets or witness panels.

5. **Hidden-state-romance countermodel**
   - If transformers are not maintaining a rich latent continuation state worth orienting to, homing packets may only be external bookkeeping devices.
   - Probe: keep the stronger public-homing-automaton story quarantined until compact homing packets show disproportionate leverage across paraphrase, stale reopen, and model-family variation.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve a tiny **homing packet** when a named ambiguity class survives the first identification move;
- name the **ambiguity class** rather than hiding it inside “uncertainty” language;
- preserve the **probe family or branch rule** rather than gesturing at generic more-probing;
- preserve the **orientation/update rule** and the **stop condition** that returns the archive to ordinary continuation, hold, bounded rollback, or `recover-resync`;
- and keep the packet small enough that it remains an orientation policy rather than becoming recap in experimental-design costume.

A minimal homing packet can often stay tiny:
- one named ambiguity class,
- one short probe family or branch rule,
- one orientation/update rule,
- and one stop or escalation condition.

That is enough to test whether the branch structure buys real leverage.
It is not a license to preserve miniature decision trees everywhere.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than memory engineering, recap compression, or one-shot diagnostic querying:
**whether a long-horizon archive can preserve not only compact public state, but a compact user-space reorientation policy that helps a fresh forward pass locate the right local continuation state after context loss.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only state packets, witness panels, sentinels, and identification packets, but also compact **homing packets** when ambiguity classes persist across reopen.

The stronger story — that DelayBasin may eventually converge on a public active-experiment policy or adaptive distinguishing automaton over continuation space — remains live, but belongs in quarantine for now.
