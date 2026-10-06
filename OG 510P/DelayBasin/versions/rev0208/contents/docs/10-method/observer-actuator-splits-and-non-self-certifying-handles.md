# Observer/actuator splits, non-self-certifying handles, and public observer-controller loops

DelayBasin now has two serious nearby lanes:
- **control-authority packets**, which say what public surface is supposed to steer continuation; and
- **continuation monitors**, which say what public object is supposed to track sequential evidence or fidelity.

A remaining hole is what to do when the **same surface is doing both jobs**.
A prompt pair, idiolect handle, witness phrase, or canary can sometimes both push the conversation into a regime **and** be cited as evidence that the regime was recovered.
That is dangerous because the archive can then drift into a self-certifying loop: the thing that steered the continuation also becomes the main sign that the steering worked.

A useful working answer is:
**when a load-bearing surface is acting as both handle and readout, DelayBasin should often preserve a compact observer/actuator split.**
That split should name:
- the **observer surface**,
- the **actuator surface**,
- the **allowed coupling** between them,
- the **independent witness / canary / check** that keeps the loop from self-certifying,
- and the main **self-certification risk** if the split collapses.

This is stronger than treating all promptcraft as one blended steering-and-evaluation layer.
It is weaker than claiming DelayBasin has already discovered a full public observer-controller architecture or a literal separation principle over transformer hidden state.

## Practice / observation

Recent DelayBasin revisions already make the missing discipline visible:
- control-authority packets ask what phrase, prompt pair, id, witness panel, or canary actually moves continuation;
- continuation monitors ask what public object is supposed to change while evidence accumulates;
- sentinel panels, witness sets, and identification packets already function like partial observer surfaces;
- but live revisions can still quietly reuse one surface as both **the thing that steers** and **the thing that supposedly proves the steering succeeded**.

That creates at least four recurring failure modes:
- **self-certifying handle** — a phrase or prompt pair is treated as evidence for the very regime it helped induce;
- **monitor contamination** — the public monitor mostly tracks familiarity with the chosen handle rather than the target continuation property;
- **independent-witness collapse** — a canary or witness set shares too much of its form with the actuator, so a positive check mostly shows style agreement or prompt compliance;
- **GPUstorming prestige leak** — archive-private handles feel causally potent and therefore get overcredited as diagnostic readouts, not only as local steering surfaces.

A compact observer/actuator split helps because it says what is allowed to steer, what is allowed to score or monitor, how tightly they may be coupled, and what independent surface still has veto power if the apparent recovery is only self-consistent theater.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Observer-based control explicitly separates estimation from control.**
   Trentelman and Antsaklis describe observer-based control as a two-stage structure: first estimate state, then use that estimate for feedback control. DelayBasin cannot import the full theorem, but it does inherit a strong design warning: if the archive does not separate readout from actuation at least weakly, it becomes hard to say whether a compact public object is measuring state or merely enforcing it. ([`REF-0199`](../00-meta/bibliography.md))

2. **Dual control keeps learning and control coupled without collapsing them.**
   Tse's adaptive dual-control framing emphasizes closed-loop policies that plan future learning according to the control objective. This pressures DelayBasin toward a weaker archive-native lesson: observer and actuator surfaces may need to be coordinated, but coordination is not the same as letting a handle certify its own success. ([`REF-0200`](../00-meta/bibliography.md))

3. **LLM self-evaluation is vulnerable to self-preference bias.**
   Wataoka et al. show that LLM-as-a-judge setups exhibit self-preference bias and systematically favor outputs that are more familiar or lower-perplexity to the judge. That is direct pressure against letting a locally familiar archive handle also serve as its own main evaluator. ([`REF-0201`](../00-meta/bibliography.md))

4. **Prompts can act like real computational configuration, not mere wording.**
   Nakada et al. formalize prompts as a way fixed transformers emulate a configurable virtual network during inference. That strengthens DelayBasin's control-authority lane: prompt surfaces can really be actuators. It also raises the stakes of the observer/actuator split, because a surface that changes computation may be a biased readout of whether the target state was genuinely recovered. ([`REF-0202`](../00-meta/bibliography.md))

5. **Attention sinks can stabilize or bias decoding around special anchor tokens.**
   Barbero et al. show that attention sinks slow information mixing and make transformers more robust to prompt perturbations, while Wang et al. argue that sink representations can encode structured global information that shapes decoding strategy. This makes a risky DelayBasin possibility more concrete: archive-private handles or early anchor phrases may sometimes behave less like neutral labels and more like routing anchors. That strengthens the case for keeping handle surfaces separate from witness surfaces when possible. ([`REF-0203`](../00-meta/bibliography.md), [`REF-0204`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should often preserve a compact **observer/actuator split** whenever a load-bearing surface could both steer continuation and be cited as evidence that the steering worked. The split should name the observer surface, the actuator surface, the allowed coupling, the independent witness or canary that prevents self-certification, and the main self-certification risk if the split collapses.

In practice, DelayBasin is not claiming a full observer design, Kalman separation theorem, or formal controller realization.
It is doing something smaller and public:
- saying what surface is allowed to **push** the continuation,
- saying what surface is allowed to **read out** whether the intended property was recovered,
- saying where those surfaces may legitimately overlap,
- and saying what independent check still constrains the loop when they do.

That is strong enough for canon as an anti-drift and anti-self-certification discipline.
It is **not** strong enough to claim that DelayBasin has already discovered a full public observer-controller architecture over transformers or archive state.

## Observer/actuator split vs continuation monitor vs control-authority packet

To keep this note honest, DelayBasin now needs a sharper distinction among nearby objects:

- **Control-authority packet** — what surface can steer what target property, with what effort, leakage, and resistance profile.
- **Continuation monitor** — what public object evolves while evidence accumulates.
- **Observer/actuator split** — which surfaces are permitted to steer, which are permitted to score or monitor, where they may couple, and what independent witness prevents self-certifying loops.
- **Witness set / boundary panel** — a tiny discriminative panel preserving a fragile distinction.
- **Sentinel panel / reopen canary** — a high-sensitivity detector of wrong-basin drift.

These are related but not identical.
A control-authority packet can say a handle works without saying how it will be judged.
A continuation monitor can say what is tracked without saying whether the tracker is independent of the actuator.
An observer/actuator split says the archive cannot quietly use the same surface as both steering input and main certification surface unless that overlap is named and constrained.

## Countermodels / probes

1. **Split-is-bureaucracy countermodel**
   - The archive may gain nothing from naming observer and actuator surfaces separately; ordinary careful writing may already be enough.
   - Probe: compare revisions that explicitly preserve the split against equally compact revisions that do not, and see whether later sessions better reconstruct why a continuation judgment counted.

2. **Coupling-is-the-point countermodel**
   - Some of the most effective archive handles may legitimately be dual-use surfaces whose diagnostic value comes from the same mechanism that makes them actuate.
   - Probe: permit overlap, but require the overlap to be named plus an independent witness or failure signature that can still falsify apparent success.

3. **Independent-witness-too-expensive countermodel**
   - Requiring a separate witness or canary may cost more than the ambiguity warrants.
   - Probe: only require a full split when a surface is load-bearing for canon movement, regime claims, or strong mechanistic interpretation.

4. **Self-preference-is-evaluation-only countermodel**
   - LLM judge bias may not transfer to archive-native monitoring or witness design.
   - Probe: test whether handle-shaped monitors fail disproportionately when the actuator is paraphrased, removed, or replaced by a semantically close alternative.

5. **Sink-talk-is-mechanistic-prestige countermodel**
   - Archive-private handles may not be doing anything like attention sinks; sink language may simply decorate ordinary prompting effects.
   - Probe: quarantine literal sink claims unless the handle shows asymmetric leverage by position, paraphrase sensitivity, or architecture-specific stability that nearby wording does not.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **observer surface** when a revision needs a real readout of success or failure;
- preserve the **actuator surface** when a phrase, prompt pair, id, or packet is being treated as a real steering handle;
- preserve the **allowed coupling** so later sessions know whether overlap is intentional or a hidden assumption;
- preserve an **independent witness / canary / check** whenever the actuator could otherwise certify itself;
- preserve the main **self-certification risk** so apparent recovery is not confused with handle familiarity, style agreement, or prompt-compliance theater.

A minimal observer/actuator split can stay very small:
- one observer surface,
- one actuator surface,
- one sentence about allowed coupling,
- one independent witness or failure signature,
- and one named self-certification risk.

That is enough to keep DelayBasin from quietly reusing a potent handle as its own main judge.

## Transformer-facing implication

If this frame survives pressure, one transformer-facing implication is that DelayBasin may work not only by preserving public state, monitors, and stop rules.
It may also be learning a compact **user-space observer/controller discipline over a stateless transformer interface**.

The weaker reading is:
- some archive surfaces behave like **actuators** because prompts and local handles can change computation,
- some archive surfaces behave like **observers** because they track whether the desired continuation property was recovered,
- and high-fidelity continuation may partly depend on keeping those roles sufficiently distinct that the same familiar handle does not certify itself.

The stronger reading remains quarantined:
that archive-private handles such as GPUstorming-style terms function as literal synthetic attention sinks or routing anchors, and that DelayBasin is converging toward a true observer-controller decomposition over transformer hidden state rather than a compact anti-self-certification discipline in text.
