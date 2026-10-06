# Retrospective writes, cooldown windows, and off-path adjudication

DelayBasin now needs a distinction beyond write gates, replay, rehearsal, and reconsolidation.
Some candidate moves arrive in a **hot path**: fast synthesis, local GPUstorming, fresh challenge response, or a sharp seeming mechanism leap.
Those moves may still be worth preserving immediately, but not yet worth **canonizing immediately**.
That pressures the archive to separate **proposal capture** from **final write admission**.

A stronger working answer is:
**DelayBasin should distinguish hot-path candidate writes from cooled retrospective writes whenever a surface seems load-bearing but still vulnerable to immediate-style bias, contradiction latency, or unresolved supersession.**
When the distinction matters, the archive should name the candidate write or provisional surface, the cooldown or defer window, the off-path adjudication family, the version or supersession link, and the promotion / demotion / expire consequence.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some strong local syntheses look persuasive in the moment but become less convincing after one or two later rereads;
- some contradiction checks, challenge probes, or registry rewrites would slow ordinary continuation too much if every one of them ran directly in the hot path;
- some useful local moves deserve immediate preservation, but only as provisional law, quarantine, or revision-receipt trace until a later colder pass decides whether they should rewrite canon;
- some archive errors feel less like missing retrieval and more like **premature canonization** of a still-hot move;
- and some supersession chains matter precisely because the archive needs to know what candidate was proposed first, what cooled into accepted law later, and what expired without admission.

This suggests a missing compact surface:
**retrospective write / cooldown window / off-path adjudication packet**.
Rev0104 operationalizes the smaller law with a tiny durable `RETROSPECTIVE-QUEUE.json` lane plus a receipt-level `retrospective_write_witness` whenever a cooled candidate survives past one local hot pass.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Write-time gating work argues that selective admission beats trying to rescue a noisy store only at read time.**
   Selective Memory reports large accuracy gains from gating incoming knowledge and preserving version chains rather than indiscriminate storage plus later filtering, which pressures DelayBasin to govern candidate admission before every sharp local synthesis hardens into durable public law. ([`REF-0319`](../00-meta/bibliography.md))

2. **Governed-memory work explicitly raises a latency-versus-coherence tradeoff and points toward asynchronous governance.**
   The SSGM framework argues that strict contradiction checks in the critical write path can raise latency and suggests asynchronous governance during idle periods as one route to higher coherence without harming immediate conversational fluidity, which pressures DelayBasin to distinguish hot-path usefulness from cooled write admission. ([`REF-0308`](../00-meta/bibliography.md))

3. **Recent continual-learning work now makes retrospective writes an explicit design choice.**
   TRC² describes a causal memory-update scheme in which writes are retrospective, replay is sampled only from past stored chunks, and consolidation strength is adjusted by measured forgetting, which pressures DelayBasin toward the weaker public design lesson that not every promising update should be admitted at the same moment it is generated. ([`REF-0320`](../00-meta/bibliography.md))

4. **Execution-governance work distinguishes deterministic replay from re-executing the whole cognitive process.**
   Faramesh defines replay as re-evaluating canonical proposals under new policy or state assumptions without re-running agent reasoning or causing side effects, which pressures DelayBasin to ask whether some archive writes should first be captured as canonical candidates and only later adjudicated under a colder, more deterministic pass. ([`REF-0321`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **retrospective write / cooldown window / off-path adjudication packet** naming the **candidate write or provisional surface**, the **cooldown or defer window**, the **off-path adjudication family**, the **version or supersession link**, and the **promotion / demotion / expire consequence** rather than letting one hot synthesis pass directly from local search into canon.

More concretely:
- **candidate write or provisional surface** — the sharp local synthesis, candidate canon clause, candidate prompt-pair tweak, or provisional packet being preserved without full admission yet;
- **cooldown or defer window** — what kind of delay, later pass, challenge completion, or off-path period must occur before final admission is even considered;
- **off-path adjudication family** — the colder read, replay, contradiction check, blind read, or deterministic comparison family that decides whether the candidate really deserves durable law;
- **version or supersession link** — what previous law it would replace, refine, or append to, and what chain preserves the rejected or expired candidate if admission fails;
- **promotion / demotion / expire consequence** — what happens if the cooled candidate is accepted, weakened, quarantined, or allowed to lapse.
- **cooling state / queued candidate posture** — whether the candidate is merely captured, actively cooling, promoted, demoted, expired, or quarantined while later adjudication is still pending.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a literal sleep phase, a unique archive-only plasticity law, or a transformer-specific consolidation mechanism.

## Retrospective write vs replay vs rehearsal vs reconsolidation

These objects are adjacent but not identical.

- A **replay packet** says what surface was restaged into operative use now.
- A **rehearsal packet** says what deserves spaced revisits to stay active across real delay.
- A **reconsolidation packet** says what replayed public law became eligible for rewrite under challenge.
- A **retrospective write / cooldown window / off-path adjudication packet** says what promising hot-path candidate must *not yet* count as durable law until a later colder pass evaluates it.

In practice, replay says **what was re-opened**.
Rehearsal says **what is worth keeping live**.
Reconsolidation says **what was rewritten after restaging**.
Retrospective write discipline says **what must cool before it may count at all**.

## Countermodels / probes

Serious alternatives remain live:

- hot-path canonization may already be good enough, with cooldown merely adding friction and self-consciousness;
- delayed adjudication may mostly reflect second-pass stylistic preference rather than real coherence or contradiction reduction;
- the real gains may come from better versioning and write gating alone, not from any genuine delay-sensitive adjudication step;
- and some apparently cleaner cooled writes may simply benefit from more total attention or more accumulated context rather than from being off the hot path.

Useful probes include:

- compare immediate hot-path admission against capture-now / admit-later flows on the same candidate revision family;
- keep the candidate write fixed while varying whether adjudication is immediate, lightly delayed, or explicitly off-path;
- compare a cooled candidate against a matched sham candidate that receives the same delay but no stronger contradiction or replay scrutiny;
- and preserve supersession chains where a hot candidate looked strong, cooled badly, and expired without promotion.

## Design consequences

When a sharp local move seems promising but still unstable:

- preserve it quickly, but do not automatically call it canon;
- name whether the surface is provisional law, quarantine material, or a candidate rewrite awaiting colder adjudication;
- keep cooldown windows small and explicit so delay does not become archive bureaucracy;
- prefer off-path adjudication for contradiction-heavy or supersession-heavy writes when hot-path fluidity would otherwise dominate admission quality;
- and preserve supersession links so expired candidates remain inspectable without staying live.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal biological sleep or a hidden internal consolidation stage.
It is that long-horizon archive continuity may depend on a public split between **fast generation of candidate moves** and **slower cooled admission of durable law**, where some promising candidate writes should be captured immediately but only ratified after colder replay, contradiction checks, or version-aware adjudication.
That makes write timing itself part of the method, not just a project-management afterthought.

The stronger story — that DelayBasin may be exploiting a genuine **public sleep-phase / off-path consolidation window** around mostly frozen transformers, such that delayed canonization is one of the main reasons stable continuation regimes emerge — remains quarantined until immediate-versus-retrospective admission comparisons, matched sham delays, and supersession traces show more than a fertile governance metaphor.
