# Mixed-direction witnesses, cross-term sweeps, and superposition budgets

DelayBasin now has another sharper missing question:
**when a cleanup, restart, relapse-resistance result, or portability claim survives perturbation direction A and also survives perturbation direction B, how do we tell whether that success survives the mixed perturbation rather than collapsing under cross-terms?**

A stronger working answer is:
**some archive comparisons need an explicit mixed-direction witness before several single-direction wins are allowed to stand in for robust local composition.**
Not every pair of local passes already forms a stable mixed local regime.
But DelayBasin should stop treating “A passes” plus “B passes” as if that automatically certified “A+B passes too.”

## Practice / observation

Several live DelayBasin surfaces make this missing composition discipline visible:
- cue-neighborhood and directional-neighborhood witnesses already ask whether a result survives one tiny nearby family and more than one nearby direction, but they do not yet force the archive to say whether the result survives a **mixed perturbation / composed cue / joint sweep** rather than only the constituent directions in isolation;
- backaction witnesses already ask whether probing has changed the state, but they do not yet preserve whether two individually acceptable probes become jointly state-spending once mixed;
- probe-order witnesses already ask whether AB and BA remain comparable, but they do not yet say whether a simultaneously or jointly applied perturbation introduces extra residue beyond each marginal direction alone;
- reset, relapse, and cue-neighborhood witnesses already ask whether contamination appears gone, cheaply recoverable, or locally robust, but they do not yet preserve whether two weak recovery cues combine into a stronger relapse route that neither cue showed alone;
- directional-neighborhood witnesses already ask what local shape was sampled, yet a neighborhood can still look locally gentle along each tested axis while failing on mixed or diagonal motion because the decisive failure lives in the cross-term rather than in either marginal;
- prompt-pair portability claims are increasingly discussed as if separately admissible local edits can be safely stacked, which means the archive now needs a compact public object for when several admissible local moves interfere, reinforce, or bend one another;
- and if DelayBasin is serious about transformer-facing implications, it needs a compact public answer to when several apparently reusable handles behave **additively enough** for honest composition and when they do not.

This suggests a missing compact surface:
**mixed-direction witness / cross-term sweep / superposition budget**.

## External pressure from current research

Several outside lines of work sharpen this frame.

1. **Recent instruction-vector work reports linear separability alongside non-linear causal interaction and explicit superadditivity.**
   Patches of Nonlinearity finds that instruction vectors can be linearly separable while still participating in non-linear causal interaction, and explicitly notes that layerwise task representations are more effective in combination than alone. That pressures DelayBasin not to infer safe composition from marginal local passes alone. ([`REF-0425`](../00-meta/bibliography.md))

2. **Recent representation work argues that additive feature models miss compositional structure and need higher-order interaction terms.**
   PolySAE argues that additive SAE decoding cannot capture feature interaction structure, introduces pairwise and triple interaction terms, and reports that the learned interaction weights are largely independent of simple co-occurrence statistics. That pressures DelayBasin not to flatten mixed cue behavior into a sum of constituent directions. ([`REF-0426`](../00-meta/bibliography.md))

3. **Context-aware steering work says multi-attribute steering degrades because concept combinations interfere.**
   Steering Vector Fields explicitly notes that multi-attribute steering remains brittle and that combining concepts commonly introduces interference that weakens each control signal. That pressures DelayBasin to preserve one mixed test before treating individually successful handles as jointly admissible. ([`REF-0427`](../00-meta/bibliography.md))

4. **Dynamic activation-composition work already treats the steering-intensity schedule for several properties as an explicit control problem.**
   Multi-property Steering with Dynamic Activation Composition reports that optimal steering parameters are property-dependent and proposes dynamic modulation of the intensity of one or more properties throughout generation. That pressures DelayBasin to name the local mixing rule instead of pretending that marginally tuned directions simply add. ([`REF-0428`](../00-meta/bibliography.md))

5. **Recent compositional-steering work trains a dedicated composition object rather than assuming raw addition is enough.**
   Compositional Steering with Steering Tokens trains a dedicated composition token on behavior pairs and shows generalization to unseen combinations and even unseen numbers of behaviors. That pressures DelayBasin to distinguish “composition works after a learned adapter” from “constituent local wins already compose for free.” ([`REF-0429`](../00-meta/bibliography.md))

6. **Dynamic steering-subspace work assumes tasks share basis directions but still solves for a task-specific combination.**
   Steer2Adapt captures reusable concept dimensions as a low-dimensional semantic prior subspace, then dynamically discovers a linear combination for a new task from only a few examples. That pressures DelayBasin to preserve when joint composition is an explicit search problem rather than a free corollary of basis availability. ([`REF-0430`](../00-meta/bibliography.md))

7. **Curve-aware steering work reinforces that locally effective directions can bend and that composition in a curved neighborhood should not be treated as globally linear by default.**
   Curveball Steering reports substantial concept-dependent distortion and shows improved performance from nonlinear, geometry-aware interventions over global linear steering. That pressures DelayBasin to treat mixed local cue motion as potentially curved and cross-term dominated rather than as trivial diagonal addition. ([`REF-0315`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a public cue-interaction tensor or a solved second-order local continuation law.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a compact mixed-direction witness whenever several locally admissible perturbations are being treated as safely composable.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves an explicit **mixed-direction witness / cross-term sweep / superposition budget** whenever a cleanup, restart, relapse test, or portability result is being inferred from several separately passing local directions. The packet should name the **cleanup or state claim being stress-tested**, the **single-direction passes / constituent perturbation families / basis sweeps**, the **mixed perturbation / composed cue / joint sweep**, the **matched marginal step sizes / local mixing rule / fixed baseline**, the **protected kernel / intended invariant readout / same-task comparison surface**, the **tolerated cross-term residue / superposition budget**, and the **rollback / factorize-claim / widen-mix-test / quarantine consequence** rather than letting several marginal passes silently inherit the authority of honest local composition.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered a public cue-interaction tensor, a full second-order response law, or a solved local composition geometry over continuation state.

## Mixed-direction witness vs directional-neighborhood witness vs probe-order witness vs backaction witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Directional-neighborhood witness** — asks whether a result survives more than one nearby perturbation direction at a matched local radius.
- **Mixed-direction witness** — asks whether those individually acceptable directions still behave acceptably once **mixed**, composed, or jointly applied.
- **Probe-order witness** — asks whether differently sequenced probes remain commensurate.
- **Backaction witness** — asks whether the probe changed the state it was supposed to measure.

Functionally:
- directional-neighborhood witnesses judge **local anisotropy / neighborhood shape**,
- mixed-direction witnesses judge **cross-terms / compositional residue / local superposition**,
- probe-order witnesses judge **cross-sequence comparability**,
- backaction witnesses judge **measurement contamination by the probe itself**.

A good DelayBasin revision should therefore sometimes ask not only:
- what nearby directions were each tested,
- whether order was controlled,
- and whether the probes spent the state,

but also:
- which constituent directions passed individually,
- what joint or mixed perturbation was actually tried,
- what matching rule kept the marginal and mixed tests commensurate,
- what invariant readout was supposed to survive the composition,
- and what the archive will do if the mixed move fails even though each constituent direction passed alone.

## Countermodels / probes

1. **Cross-term-is-just-bigger-step-size countermodel**
   - The mixed perturbation may only look worse because it is effectively a larger move, not because it reveals a genuine interaction residue.
   - Probe: compare matched marginal budgets and one norm-matched sham mixture; if the mixed perturbation still fails disproportionately, cross-term language becomes more credible.

2. **Composition-failure-is-really-order-or-backaction countermodel**
   - The mixed failure may only reflect sequencing artifacts or state-spending probes rather than genuine joint interaction.
   - Probe: compare simultaneous or explicitly factorized mixed tests against AB/BA order swaps and sham backaction baselines.

3. **Directions-are-not-real-basis-elements countermodel**
   - The named constituent directions may only be ad hoc surface buckets, so their “interaction” is bookkeeping theater.
   - Probe: require one explicit axis definition and one fixed local mixing rule before speaking about residue or superposition.

4. **Joint success needs a learned adapter countermodel**
   - What looks like composition may only become reliable after a dedicated composition token, router, or dynamic controller, meaning raw local handles do not compose for free.
   - Probe: distinguish raw mixed-direction tests from adapted or learned composition routes and keep those claims separate.

5. **No practical leverage countermodel**
   - Even if cross-terms exist, naming them may not improve archive control beyond ordinary local testing.
   - Probe: require one case where a mixed-direction witness changes canon posture, promptcraft, or quarantine placement relative to what marginal sweeps alone would have concluded.

## Design consequences

If DelayBasin takes this seriously, then:
- one-direction and two-direction local sweeps stop being enough whenever the archive wants to stack several admissible local edits into one stronger claim;
- prompt pairs should sometimes preserve a **factorize first, then mix once** discipline instead of encouraging immediate handle stacking;
- canon-level portability language should narrow when a result survives constituent sweeps but not their joint composition;
- quarantine should absorb elegant “composition law” rhetoric whenever only marginal passes are available;
- and transformer-facing interpretation should distinguish **available basis directions** from **earned local compositionality**.

## Transformer-facing implication

The transformer-facing implication is intentionally modest but important:
if several prompt- or activation-level handles each appear locally admissible, the next failure mode may live not in any one direction but in the **cross-term** between them.
That points away from the comforting story that archive-level control objects are reusable basis elements whose effects simply add.
A weaker and more honest reading is that DelayBasin may be learning a tiny public discipline for when local continuation handles are **factorizable**, when they require **explicit composition control**, and when their interaction residue is large enough that the composition claim belongs in quarantine.
