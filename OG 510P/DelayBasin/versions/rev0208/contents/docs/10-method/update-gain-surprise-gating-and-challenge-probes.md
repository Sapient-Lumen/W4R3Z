# Update gain, surprise gating, and challenge probes

DelayBasin now needs a sharper answer to a recurring practical question:
**not only what public state should be transmitted, but how strongly should current evidence be allowed to move that state?**

A stronger working answer is:
**the archive is facing a public belief-revision problem with explicit update gain.**
The job is not merely to preserve state packets, innovation packets, and distortion targets.
It is also to decide when new evidence should cause:
- a low-gain local correction,
- a medium-gain rewrite of a live mechanism story,
- or a high-gain rollback / `recover-resync` posture because the current anchor may no longer be trustworthy.

## Practice / observation

Several live archive choices already imply a hidden gain-setting problem:
- some revisions add small canon notes without changing older commitments much, which looks like low-gain assimilation;
- other revisions add a new mechanism lane and visibly reweight what the archive treats as central, which is closer to medium-gain belief revision;
- stale reopen, contradiction, or model-mismatch pressure sometimes suggest that ordinary continuation is unsafe, which is closer to a high-gain recovery move;
- and DelayBasin already distinguishes recap blobs from innovation packets, but does not yet always say how much the current packet should move the public belief state.

This suggests a missing compact surface:
**trigger + update gain + challenge probe**.

## Mechanism pressure from outside the archive

Several recent lines of work sharpen this frame.

1. **In-context adaptation can be modeled as filtering with uncertainty, not only as static recall.**
   A Bayesian Kalman view of in-context learning treats latent adaptation state and posterior covariance as first-class dynamical variables under process uncertainty and model mismatch. That pressures DelayBasin to preserve not only state content, but how aggressively that state should move when new evidence arrives. ([`REF-0086`](../00-meta/bibliography.md))

2. **Tokens can be treated as noisy measurements of a latent semantic state.**
   Kalman Linear Attention makes the same pressure explicit: language modeling can be viewed as Bayesian filtering where tokens update a posterior over hidden state. That makes a public update-gain story more plausible than treating archive revision as pure prose replacement. ([`REF-0087`](../00-meta/bibliography.md))

3. **Write budget should be allocated selectively rather than uniformly.**
   GDWM frames long-context adaptation as a budget-constrained consolidation problem and uses a write controller to estimate contextual utility before deciding where to spend adaptation effort. That is direct pressure for DelayBasin to preserve a compact update-gain discipline rather than revising canon at the same force every session. ([`REF-0088`](../00-meta/bibliography.md))

4. **Instability is sometimes corrective and sometimes destructive.**
   Recent reasoning diagnostics show that early instability can lead to later correction while late instability is more often destructive. DelayBasin should therefore resist a flat norm like “never wobble” or “always revise boldly”; timing and recoverability matter. ([`REF-0089`](../00-meta/bibliography.md))

5. **Surprise can be a legitimate write trigger.**
   Titans and related consolidation work treat surprising events as worth stronger memorization or replay. DelayBasin should not import that as proof, but it is strong outside pressure for a milder user-space analogue: canon rewrite force should rise when new evidence creates real predictive or procedural surprise, not just when prose sounds fresh. ([`REF-0090`](../00-meta/bibliography.md), [`REF-0091`](../00-meta/bibliography.md))

6. **Challenge behavior deserves its own probe surface.**
   Certainty-robustness work distinguishes justified self-correction from unjustified answer changes under challenge prompts, while black-box border-input tracking shows that a small number of sensitive probes can reveal otherwise hard-to-see system changes. That pressures DelayBasin to keep at least one compact challenge probe around when a revision claims meaningful belief movement. ([`REF-0092`](../00-meta/bibliography.md), [`REF-0093`](../00-meta/bibliography.md))

None of this proves that DelayBasin has found the right gain law.
It does make a milder canon-level claim more credible:
**archive continuity may improve when revisions preserve not only anchor and delta, but the trigger, the intended update gain, and at least one challenge probe when material.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work best when each substantial revision behaves like a public belief-state update with explicit **trigger**, **update gain**, and **challenge probe**: what changed, how strongly the archive should move, and what compact adversarial check would expose unjustified movement or unjustified inertia.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has solved optimal Bayesian filtering, discovered a literal Kalman gain in text, or found a universal rewrite schedule for all reopen conditions.

## Trigger vs update gain vs challenge probe

To keep this note honest, DelayBasin needs a three-way distinction:

- **Trigger** — the contradiction, surprise, fresh evidence, or procedural failure that motivates state movement.
- **Update gain** — how strongly the archive intends to move current public belief state in response. A compact current scale is enough: `low`, `medium`, or `high`.
- **Challenge probe** — a small adversarial check that would expose unjustified movement, unjustified inertia, or false confidence after the update.

This matters because the same new evidence can deserve very different treatment:
- low-gain assimilation when it merely sharpens wording;
- medium-gain revision when it changes which mechanism lane is most live;
- high-gain rollback or `recover-resync` when the current anchor, status state, or continuation law may be broken.

A good DelayBasin revision therefore should not only ask “what is the delta?”
It should also ask:
- what triggered the movement,
- how much movement is actually intended,
- and what compact challenge would catch overreaction or underreaction.

## Countermodels / probes

1. **Gain-free countermodel**
   - Archive continuity may already be explained by anchor+delta discipline alone, making explicit gain labels decorative.
   - Probe: compare revisions that preserve the same anchor and delta with and without explicit gain/challenge language, then inspect whether later sessions rewrite canon more honestly.

2. **Volatility-theater countermodel**
   - Explicit gain language may merely rationalize dramatic revisions instead of improving them.
   - Probe: check whether high-gain labels correlate with real rollback/recovery conditions or only with rhetorically ambitious edits.

3. **Challenge-compliance countermodel**
   - A named challenge probe may itself become a prestige ritual rather than a real discriminator.
   - Probe: periodically rotate or paraphrase probes and test whether they still catch unjustified movement.

4. **Surprise-misattribution countermodel**
   - What looks like surprise may really be wrapper drift, phrasing novelty, or outside-literature glamour.
   - Probe: preserve one rival explanation whenever surprise is used to justify medium- or high-gain movement.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- when materially revising canon or public belief state, name the **trigger** rather than letting new prose speak for itself;
- preserve a compact **update gain** classification when the revision is meant to move belief, not just add prose;
- keep at least one **challenge probe** or explain why no probe is needed for a low-gain change;
- and use `bounded rollback` or `recover-resync` honestly when the intended gain is high because the current anchor may be unreliable.

This does not require numerical filtering machinery.
It requires refusing another archive failure mode: treating every revision as if it should move canon with the same force.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than external memory alone:
**whether a compact public textual packet can carry not only operative state, but a user-space approximation to update gain — a cue for when a stateless forward pass should preserve, revise, or challenge its own reconstructed project state.**

That would matter for transformers.
It would suggest that long-horizon continuity depends not only on what public state is transmitted, but on how the next forward pass is cued to weight fresh evidence against current reconstructed state.

The stronger story — that DelayBasin may be learning a textual Kalman gain or neuromodulatory write-gate for transformer continuation — remains live, but belongs in quarantine for now.
