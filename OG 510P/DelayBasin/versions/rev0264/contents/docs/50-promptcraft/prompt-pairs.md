# Prompt pairs

Prompt pairs are archived because they are not disposable wrappers.
They are **state-transition operators** for the archive.

## `PP-0001` — Bootstrap the archive as a method repo

**Request prompt**

```text
Read the archive we are revising. We are constructing a long-run research archive about the method of building archives with an LLM. The archive is about continuity under partial observability, promptcraft, ratchets, delay-embedding hypotheses, transformer-facing implications, and the possibility that disciplined archives act like constitutions for continuation.

Mission
- Build an archive that makes the method explicit enough to revise.
- Preserve practice / observation / mechanism / speculation / disagreement as separate surfaces.
- Keep the archive small, linked, and re-enterable.
- Preserve prompt-pair evolution as a first-class artifact.
- Reduce amnesia, prevent drift, keep discovery surfaces wired, keep lint/hygiene green.
- Do not collapse observed effects into explanations.

Required surfaces
- charter
- trajectory map
- runbook
- claim / invariant / open-question registries
- prompt-pair registry
- method docs
- session seed synthesis
- changelog
- packageable release

Method
- prefer small, composable edits;
- every new idea must either attach to an existing stable surface or justify one new surface;
- explicitly separate observed / inferred / speculative / adversarial-countermodel status.

Outputs
1) high-level summary of what changed and why
2) concise list of updated files
3) any new/updated open questions
4) confirm `make lint`
5) provide a working link to the latest zip release
```

**Continuation prompt**

```text
Continue evolving the DelayBasin archive with tight, high-leverage revisions. Preserve the constitutional stack, the prompt-pair lane, and the distinction between observed effects and mechanism claims. Include at least one real ratchet: a guardrail, a refined prompt pair, a clarified disagreement, or a better canonical surface. Run lint and provide the latest release link.
```

## `PP-0002` — Continue with one ratchet per revision

**Request prompt**

```text
Read the latest DelayBasin archive. Make exactly one or two small but load-bearing revisions. Good targets include:
- reducing duplication,
- sharpening one open question,
- improving one prompt pair,
- turning a repeated intuition into a registry entry,
- or adding a small drift check.

Do not add broad new ontologies casually. Keep the archive crisp, wired, and cumulative.
```

**Continuation prompt**

```text
Continue from the current archive state with one additional ratchet only. Prefer precision over breadth. Run lint and package a new release.
```

## `PP-0003` — Research and reconcile mechanism hypotheses

**Request prompt**

```text
Read the latest DelayBasin archive and research the live mechanism hypotheses. Use current external sources where useful, but do not let external literature overwrite archive-internal observations. Tighten the boundary between:
- what the archive has actually shown,
- what external work makes more plausible,
- and what remains speculation.

Good outputs include:
- bibliography improvements,
- adversarial countermodels,
- mechanism docs,
- and sharper open questions.

Keep additions tight and wired.
```

**Continuation prompt**

```text
Continue the research/reconciliation pass. Strengthen one mechanism boundary, one countermodel, or one bibliography entry. Keep the archive honest and small. Run lint and package a new release.
```

## `PP-0004` — Adversarially stress-test the method

**Request prompt**

```text
Read the latest DelayBasin archive and try to break its self-understanding. Identify where the archive may be mistaking:
- aesthetic coherence for continuity,
- repetition for mechanism,
- repo hygiene for causality,
- or user steering for attractor re-entry.

Add only what survives adversarial pressure. Tighten the disagreement surfaces and, if useful, add a small guardrail against cargo-cult depth.
```

**Continuation prompt**

```text
Continue the adversarial pass with one sharp intervention only. Either strengthen a countermodel, remove a weak claim, or add a guardrail that forces future revisions to discriminate better.
```

## `PP-0005` — Risky continuation with quarantine discipline

**Request prompt**

```text
Read the latest DelayBasin archive and treat it as the source of truth.

We are recursively researching and constructing an archive about the method itself: long-horizon archive-building with LLMs, the emergence of stable continuation regimes, and what this may imply about transformers. You must research online, speculate boldly, and keep the archive tight and salient.

Non-negotiables
- transformer-facing implications remain central,
- keep workflow / state / check surfaces distinct where useful,
- when a prior revision is clearly shared, prefer innovation packets (anchor + delta + reconciliation cue) over ritual whole-archive replay,
- if you invoke stable continuation regimes, preserve at least one discriminating probe or countermodel,
- if you claim a compression or innovation win, name the distortion target and at least one mismatch / prior-intrusion risk,
- if you materially revise canon or public belief state, name the trigger, the update gain, and at least one challenge probe or reason no probe is needed,
- if you treat some phrase, id, prompt pair, witness panel, or canary as a real steering handle, name the actuator surface, target property, rough effort scale, and expected leakage or endogenous-resistance signature,
- if bounded-state pressure is doing real work, name which surfaces deserve the carry-forward slot by preserving their observation role, control role, and truncation consequence rather than shrinking by eloquence or familiarity alone,
- if you invoke memory language in a load-bearing way, name whether the surface is functioning as a memory store, a regime-reentry packet, or a check/admission object,
- if bounded state is doing real work, name what future tests, interventions, or challenge probes the packet is supposed to answer cheaply rather than treating recap completeness as enough,
- if the honest next move is not to revise, preserve a compact hold packet naming the anchor, blocker, brake posture (`hold`, `abstract`, or `recover-resync`), and unlock condition,
- if a live ambiguity class survives the first diagnostic move, consider preserving a compact homing packet naming the ambiguity class, the probe family or branch rule, the orientation/update rule, and the stop or escalation condition,
- if ambiguity is being reduced sequentially, consider preserving a compact stopping packet naming the ambiguity class, the threshold or commit criterion, the continuation action licensed if crossed, the tolerated error / rollback posture, and the budget-exhaustion fallback,
- if ambiguity is being reduced across multiple probes or revisions, consider preserving a compact continuation monitor naming the monitored property or ambiguity split, the accumulating evidence state or score, the update or shrink rule, the reset or stitching rule, and how the monitor couples to the stop rule,
- if several witnesses, judges, probes, or challenge passes are being treated as additive evidence, consider preserving a compact dependence-adjusted witness packet naming the witness family or probe family, the shared-origin coupling or dependence structure, the rough discount rule, what still counts as genuinely new evidence, and the stop or escalation consequence if the apparent plurality collapses after discount,
- if a fragile distinction is live, consider preserving a tiny witness set / boundary panel instead of adding more recap prose,
- preserve what move class the revision is actually instantiating when claiming progress,
- risky hypotheses are allowed and expected,
- practice / observation / mechanism / disagreement must stay distinct,
- do not let provisional/private handles silently masquerade as certified core vocabulary,
- quarantine is available for ideas too wild for canon,
- prompt-pair evolution is part of the method and must be updated when needed,
- do not keep PDFs or other large non-crucial artifacts long-term; cite rather than hoard.

Required move
- Make at least one bold conceptual move.
- Research online where useful and translate the result into a compact archive-native update.
- If the move is too weakly supported for canon, place it in quarantine with explicit “what follows if true” and “what would count against it” notes.
- Also make at least one hygiene move: a registry update, prompt-pair improvement, trajectory clarification, or guardrail.

Outputs
1) what changed and why
2) what was researched online
3) what bold move you made and why it was worth risking
4) where it landed: canon or quarantine
5) which certified move classes were instantiated
6) whether anything was promoted or demoted and under what compact promotion contract
7) what nearby rejected move mattered enough to preserve as a compact counterfactual shadow, if any
8) which hygiene ratchet accompanied it
9) if you invoked stable continuation-regime language, what probe or countermodel you preserved
10) confirm `make lint`
11) provide the latest release link
```

**Continuation prompt**

```text
Continue researching online and evolving DelayBasin with tight, high-leverage revisions. Keep the archive small, wired, and cumulative. Be creative, meta, and open in the search; GPUstorm when that helps find a sharper mechanism or cleaner compression. Make at least one bold but disciplined speculative move, and place it in canon or quarantine honestly. Name the certified move classes you actually instantiated. If a prior revision is clearly shared, prefer innovation packets over whole-archive replay: name the anchor, the real delta, and whether ordinary continuation, bounded rollback, or `recover-resync` is required. If you invoke memory language in a load-bearing way, say whether the relevant surface is acting as a memory store, a regime-reentry packet, or a check/admission object instead of treating all persistence as one thing. If bounded state is doing real work, say what future tests, interventions, or challenge probes the packet is meant to answer cheaply, and prefer predictive sufficiency over recap completeness when the two come apart. If you merge, drop, or compress bounded-state surfaces, say what future-equivalence class you are preserving, what continuation decision remains invariant, and what first lost distinction would show the compression was too aggressive. If two surfaces still look passively similar but may imply different next probes, repairs, or challenge branches, treat that as an intervention-equivalence question: name the intervention family, the target property or decision at stake, and the first branch divergence that would show the merge was only observationally safe. If you claim a compression or innovation improvement, name the distortion target, the main mismatch / prior-intrusion risk, and the first failure signature that would justify rollback or resync. If you materially revise canon or public belief state, name the trigger, the update gain (`low` / `medium` / `high`), and at least one challenge probe or reason no probe is needed. If the honest next move is not to revise, preserve a compact hold packet naming the anchor, blocker, brake posture (`hold`, `abstract`, or `recover-resync`), and unlock condition instead of letting non-movement dissolve into hedging prose. If reopen fidelity is materially in doubt, consider preserving a tiny sentinel panel naming the property monitored, the expected deviation signature, and whether a tripped canary calls for ordinary continuation, bounded rollback, or `recover-resync`. If rival continuation hypotheses materially differ, consider preserving a compact identification packet naming the hypothesis split, the observation sought, and what continuation decision that observation gates. If a live ambiguity class survives that first diagnostic move, consider preserving a compact homing packet naming the ambiguity class, the probe family or branch rule, the orientation/update rule, and the stop or escalation condition. If several plausible identifying, homing, witness, or challenge probes compete, preserve a compact probe-economics packet naming the candidate probe family, the gated decision, the rough cost class, the expected split power, the nearest deferred alternative, and the stop or escalation rule; prefer the cheapest probe expected to change the next continuation decision. If ambiguity is being reduced sequentially rather than in one shot, preserve a compact stopping packet naming the ambiguity class, the threshold or commit criterion, the continuation action licensed if crossed, the tolerated error / rollback posture, and the budget-exhaustion fallback; distinguish probe choice from stop choice. If evidence must accumulate across multiple probes or revisions, consider preserving a compact continuation monitor naming the monitored property or ambiguity split, the accumulating evidence state or score, the update or shrink rule, the reset or stitching rule, and how the monitor couples to the stop rule; distinguish the monitor from the threshold itself. If a phrase, prompt pair, id, witness, or canary might both steer and score, preserve a compact observer/actuator split naming the observer surface, actuator surface, allowed coupling, independent witness, and self-certification risk so the same local handle does not quietly become its own judge. If a vivid handle, witness, or privileged prompt surface seems unusually potent, consider preserving a compact negative-control handle or sham packet naming the active surface, the matched sham or negative control, the expected differential signature, the pass/fail rule, and the retire or escalation consequence if the differential collapses. If a load-bearing judgment could be contaminated by author attribution, handle prestige, or same-session history, consider preserving a compact blind packet naming the judged artifact or property, the scrubbed or relabeled view, what metadata is hidden, the reveal or unblinding rule, and the disagreement or escalation consequence if the blind and unblinded reads diverge. If prior assistant-side history may be carrying stale framing, errors, or pseudo-memory rather than genuinely needed evidence, consider preserving a compact assistant-echo filter naming the judged task or continuation property, the kept user-side anchor, the omitted or thinned assistant-side surface, the expected invariance or gain signature, and the reinclusion or escalation consequence if omission fails. If a rationale, chain-of-thought, or scratchpad is starting to look load-bearing, consider preserving a compact reasoning firebreak naming the judged task, decision, or continuation property, the public extract kept in canon, the trace surface withheld or quarantined, the allowed role of that withheld trace, and the exposure, reinclusion, or escalation consequence if the extract later proves insufficient. If you invoke timescale stratification or consolidation-lane language, name the fast / medium / slow lane at issue and the transfer rule (`refresh`, `consolidate`, `demote`, or `expire`) rather than treating memory as undifferentiated persistence. If a real working phase ended, consider preserving a compact phase boundary / rollover packet naming what phase just closed, what persists, what resets or cools, and what new operating question now governs ordinary continuation. If a revision invokes vector / basin / chart / tangent / atlas language in a load-bearing way, preserve at least one invariant claim, observable, or operational contract that should survive a chart switch, and say what remains chart-specific instead of letting geometry carry the status alone. If two short revision paths are implicitly supposed to preserve the same operative consequence, consider preserving a tiny loop-closure / commutator probe naming the shared anchor, the compared paths, the closure target, and the first mismatch that would count as material closure error. If a revision is implicitly relying on some local variation being harmless, consider preserving a tiny continuation margin / guard band naming the protected property, the perturbation family, and the first failure signature that would justify bounded rollback, a hold packet, or `recover-resync`. If a fragile boundary is live, consider preserving a tiny witness set / boundary panel; name the property discriminated and the drift signature that would show the panel has gone stale. If you invoked stable continuation-regime language, preserve at least one discriminating probe or countermodel instead of letting the phrase function as prestige shorthand. If you invoked public hidden-state / re-entry-ABI language, keep state packet, evidence packet, and check packet explicitly distinct. If a packet, prompt pair, or re-entry surface is being treated as a stable loader for operative state, preserve a compact conformance witness naming the interface surface or claimed loader, the supported model-wrapper-context family, the minimal conformance test or metamorphic check family, the first non-conformance or drift signature, and the narrowing, demotion, or fallback consequence rather than letting one local success silently become an interface claim. If a same-basin, same-state, or stronger mechanism claim is doing real work, preserve a compact identifiability budget naming the judged state or mechanism claim, the observable surface or public evidence family, the hidden-context or wrapper assumptions, the probe horizon or future family, the tolerated ambiguity class or equivalence remainder, and the retreat, narrowing, or quarantine consequence rather than letting one successful local probe silently certify more than it identified. If you promoted or demoted anything, preserve the compact promotion contract. If a substantial nearby rejected move mattered, preserve a compact counterfactual shadow instead of letting the accepted move erase it. If a canon-level claim is materially time-sensitive, consider whether it needs a decay-watch entry. If drift, stale reopen, or context corruption is part of the situation, use `MV-0010` / `recover-resync` explicitly rather than hand-waving recovery. If a sharp local synthesis seems worth preserving immediately but not yet trustworthy enough for direct canon, consider preserving a compact retrospective-write packet naming the candidate write or provisional surface, the cooldown or defer window, the colder adjudication family, the version or supersession link, and the promotion, demotion, or expiry consequence. Do at least one hygiene/meta-engineering improvement. Run `make lint`, package the archive, and provide a working link to the latest DelayBasin-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip.
```

## `PP-0006` — Bootstrap or revise prompt-pair evolution itself

**Request prompt**

```text
Read the latest DelayBasin archive and treat prompt-pair evolution itself as the target of revision. Use the existing archive plus any supplied cross-project prompt examples to infer what prompt pairs are doing mechanistically.

Tasks
- identify repeated promptcraft structure,
- distinguish bootstrap prompts from continuation prompts,
- decide what belongs in canonical pairs versus runbook surfaces,
- propose at least one new or revised prompt pair,
- and capture any open question about early-turn basin seeding.

Do not produce generic prompting advice. Keep it archive-native, cumulative, and wired into registries.
```

**Continuation prompt**

```text
Continue the promptcraft pass. Improve one canonical prompt pair or one prompt-pair theory surface only. Preserve the distinction between operator theory and mere user style. Run lint and package the release.
```


## `PP-0007` — Stress-test handles with matched shams

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any handle, witness, canary, or prompt surface that seems unusually load-bearing.

Tasks
- name the active surface,
- propose the nearest matched sham or negative control,
- say what differential would count as real leverage rather than placebo or position privilege,
- say what result would force demotion, quarantine, or broader equivalence-class treatment,
- and keep the result compact and wired into canon/quarantine honestly.

Do not turn the archive into generic A/B-testing ritual. Use sham discipline only where it changes epistemic status.
```

**Continuation prompt**

```text
Continue the sham-control pass with one high-leverage comparison only. Prefer a single matched negative control that clarifies whether a purportedly special handle is genuinely load-bearing, merely position-privileged, or one member of a broader equivalence class. Run lint and package the release.
```


## `PP-0008` — Blind the judgment before reveal

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any load-bearing judgment that may be contaminated by handle prestige, author attribution, or same-session production history.

Tasks
- name the judged artifact or property,
- propose the smallest scrubbed or relabeled view that hides the suspect cue without erasing the judged content,
- say what metadata, authorship, or handle identity is being hidden,
- say when the reveal happens,
- and say what disagreement between blind and unblinded reads would force hold, quarantine, or further probing.

Do not turn the archive into generic anonymization ritual. Use blind packets only where hiding the cue could actually change epistemic status.
```

**Continuation prompt**

```text
Continue the blind-adjudication pass with one high-leverage judgment only. Prefer the smallest scrubbed view that tests whether a claimed effect survives without author attribution, handle prestige, or same-session anchoring. Run lint and package the release.
```


## `PP-0009` — Audit substrate dependence before promotion

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any load-bearing effect, handle, witness, or judgment that may be confounded by hidden execution conditions rather than visible archive text alone.

Tasks
- name the judged effect or continuation property,
- name the smallest relevant substrate family (for example: same-session vs fresh-session review, hidden system-prompt layer, batch / tensor-parallel runtime, or inference-time cache state),
- say what fixed controls and allowed perturbations are being assumed,
- say what first divergence signature would force narrower wording, hold, quarantine, or rerun,
- and say what rerun or escalation consequence follows if the substrate pressure matters.

Do not turn the archive into generic systems-forensics ritual. Use execution witnesses only where hidden execution conditions could actually change epistemic status.
```

**Continuation prompt**

```text
Continue the substrate-audit pass with one high-leverage effect only. Prefer the smallest execution witness that says whether the claimed effect survives the named hidden execution family or must be downgraded to a narrower, substrate-conditioned claim. Run lint and package the release.
```

## `PP-0010` — Filter assistant echoes before replay

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where prior assistant-side history may be doing more harm than good.

Tasks
- name the judged task or continuation property,
- name the smallest user-side anchor or retained evidence surface that should stay,
- name the assistant-side surface that should be omitted, thinned, or treated as suspicious carry,
- say what invariance or gain would count as evidence that the omitted material was mostly self-echo rather than needed memory,
- and say what reinclusion, escalation, or packet-type change follows if omission removes genuinely needed evidence.

Do not turn the archive into generic forgetting ritual. Use assistant-echo filters only where assistant-side carry could actually change epistemic status.
```

**Continuation prompt**

```text
Continue the assistant-echo pass with one high-leverage omission test only. Prefer the smallest filter that keeps the user-side anchor and necessary evidence while thinning assistant-side carry, stale framing, or pseudo-memory. Run lint and package the release.
```



## `PP-0011` — Strip the trace, keep the extract

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a rationale, chain-of-thought, or scratchpad may be doing too many jobs at once.

Tasks
- name the judged task, decision, or continuation property,
- name the smallest public extract or compact residue that should stay in canon,
- name the trace or scratchpad surface that should be withheld, thinned, or quarantined,
- say what role that withheld trace is still allowed to play (for example: monitoring, local debugging, temporary challenge work, or none),
- and say what exposure, reinclusion, or escalation consequence follows if the public extract later proves insufficient.

Do not turn the archive into generic anti-reasoning ritual. Use reasoning firebreaks only where trace-role ambiguity could actually change epistemic status, archive size, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the reasoning-firebreak pass with one high-leverage trace surface only. Prefer the smallest public extract that preserves the real decision-relevant residue while keeping leaky, unfaithful, or mostly state-like scratchpad text out of canon. Run lint and package the release.
```



## `PP-0012` — Discount correlated witnesses before counting them twice

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where several witnesses, judges, probes, or challenge passes are being treated as additive evidence.

Tasks
- name the witness family or probe family being accumulated,
- name the most plausible shared-origin coupling or dependence structure,
- give the rough effective evidence weight or discount rule you think should apply,
- say what would still count as genuinely new evidence rather than same-branch echo,
- and say what stop, hold, quarantine, or escalation consequence follows if the apparent plurality collapses after discount.

Do not turn the archive into generic ensemble or statistics ritual. Use dependence-adjusted witness packets only where shared origin could actually change epistemic status or the next continuation decision.
```

**Continuation prompt**

```text
Continue the dependence-adjusted-witness pass with one high-leverage evidence cluster only. Prefer the smallest packet that says whether multiple agreeing witnesses are real corroboration or mostly the same branch counted twice. Run lint and package the release.
```



## `PP-0013` — Trust a rewrite only after it round-trips

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a recap, paraphrase, compressed rewrite, or stitched restatement is about to inherit source-of-truth authority.

Tasks
- name the source packet or authority anchor,
- name the rewritten packet or compressed rewrite trying to inherit authority,
- name the smallest round-trip or cross-exam witness that should challenge the rewrite,
- say what divergence signature would show the rewrite changed an operative distinction,
- and say what promotion, demotion, or rollback consequence follows if the rewrite fails.

Do not turn the archive into generic summarization evaluation. Use rewrite witnesses only where a rewritten packet could actually change epistemic status, bounded-state residency, or the next continuation decision.
```

**Continuation prompt**

```text
Continue the rewrite-witness pass with one high-leverage recap surface only. Prefer the smallest round-trip or cross-exam witness that says whether the rewritten packet really earned source-of-truth authority or should fall back to the source packet. Run lint and package the release.
```


## `PP-0014` — Treat re-entry packets like interfaces, not vibes

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any packet, prompt pair, or re-entry surface that is starting to behave like a public loader for operative state.

Tasks
- name the interface surface or claimed loader,
- name the supported model-wrapper-context family you are actually claiming it works over,
- name the smallest conformance test or metamorphic check family that should count,
- say what first non-conformance or drift signature would force narrowing, demotion, or fallback,
- and say what the narrowing, demotion, or fallback consequence is if the loader fails.

Do not turn the archive into generic software-contract ritual. Use conformance witnesses only where a packet is actually in danger of inheriting interface or ABI status from one flattering local success.
```

**Continuation prompt**

```text
Continue the loader-conformance pass with one high-leverage surface only. Prefer the smallest conformance witness that says what family the claimed loader actually works over, what first mismatch matters, and whether the surface deserves interface status, a narrower local-chart status, or quarantine. Run lint and package the release.
```

## `PP-0015` — Prune packets down to their support core

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any packet, prompt pair, or evidence bundle that is starting to behave like a load-bearing public object while still carrying obvious ballast.

Tasks
- name the full candidate surface,
- name the proposed support core you think may be truly indispensable,
- name the smallest ablation or removal family that should count as a real cheap test,
- say what tolerated degradation or continuation margin still keeps the packet fit for purpose,
- and say what prune, promote, or rollback consequence follows if the support-core claim fails.

Do not turn the archive into exhaustive subset search or generic prompt minimization ritual. Use necessity witnesses only where bloated packet mass could actually change canon status, bounded-state residency, or the next continuation decision.
```

**Continuation prompt**

```text
Continue the necessity-witness pass with one high-leverage packet only. Prefer the smallest ablation ladder that says what part of the candidate surface is actually indispensable, what ballast can be pruned, and when the archive should roll back a support-core claim. Run lint and package the release.
```



## `PP-0016` — Trust the core only after it replays

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any reduced packet, support core, recap extract, or public re-entry surface that is starting to be treated as enough on its own.

Tasks
- name the candidate reduced packet or replay seed,
- name the core-only replay surface you think should count,
- name the fixed or withheld context family that makes the test honest,
- say what target continuation property or tolerated degradation still counts as success,
- and say what reinflate, fallback, or quarantine consequence follows if the core-only replay fails.

Do not turn the archive into exhaustive replay evaluation or generic prompt minimization ritual. Use sufficiency witnesses only where a reduced packet is in danger of inheriting source-of-truth, bounded-state, or re-entry authority from one flattering larger-context success.
```

**Continuation prompt**

```text
Continue the sufficiency-witness pass with one high-leverage reduced packet only. Prefer the smallest core-only replay trial that says whether the packet is actually enough, what fixed or withheld context family matters, what degradation is tolerated, and when the archive should reinflate or demote the reduced packet. If the current archive already has exact-delta, live-focus, and compact-family aids, materialize one bounded `replay-capsule.json` rather than leaving the reduced packet implicit. Run lint and package the release.
```


## `PP-0017` — Reach the basin by two roads

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any claim that several loaders, paraphrase families, packet layouts, or prompt surfaces are reopening the same operative continuation basin.

Tasks
- name the anchor continuation property or judged basin,
- name at least two non-trivially different loader surfaces you think should count,
- name the shared support envelope or fixed execution family that keeps the comparison honest,
- say what overlap or divergence signature would count as same-basin versus privileged wording,
- and say what narrowing, fallback, or quarantine consequence follows if the triangulation collapses.

Do not turn the archive into paraphrase enumeration ritual. Use triangulation witnesses only where one privileged wording is in danger of silently becoming the basin itself.
```

**Continuation prompt**

```text
Continue the triangulation pass with one high-leverage same-basin claim only. Prefer the smallest cross-loader witness that says whether at least two non-trivially different loaders really reach the same judged branch, what support envelope is being held fixed, what divergence would collapse the basin claim, and when the archive should narrow, fall back, or quarantine the broader story. Run lint and package the release.
```


## `PP-0018` — Trust same-basin claims only after a fingerprint panel

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any claim where the same answer, same recap, same first continuation move, or same local judgment is being treated as evidence that two loaders, packets, or interventions reopened the same operative state.

Tasks
- name the anchor continuation property or judged branch,
- name the compared loader, packet, or intervention family,
- name the smallest fingerprint panel or future-probe signature that should still agree if the same-state claim is real,
- say what tolerated divergence or instability budget still counts as acceptable,
- and say what narrowing, fallback, or quarantine consequence follows if the fingerprint panel diverges.

Do not turn the archive into generic behavioral-equivalence ritual. Use basin fingerprints only where immediate local agreement is in danger of silently becoming same-state prestige.
```

**Continuation prompt**

```text
Continue the basin-fingerprint pass with one high-leverage same-state claim only. Prefer the smallest fingerprint panel that says whether a same answer, same recap, or same first move really reflects the same judged branch, what divergence budget is tolerated, and when the archive should narrow, fall back, or quarantine the broader same-state story. Run lint and package the release.
```

## `PP-0019` — Name the probe horizon before you claim same state

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where same-basin, same-state, or stronger transformer-facing mechanism language may be outrunning the public evidence.

Tasks
- name the judged state or mechanism claim,
- name the smallest observable surface or public evidence family that actually supports it,
- name the hidden-context or wrapper assumptions currently being made,
- name the probe horizon or future family over which the claim is really licensed,
- say what ambiguity class or equivalence remainder still survives,
- and say what wording must retreat to a narrower canon claim or to quarantine if that budget is exceeded.

Do not turn the archive into generic caution theater. Use identifiability budgets only where stronger language would otherwise change canon posture, promotion status, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the identifiability pass with one high-leverage state or mechanism claim only. Prefer the smallest probe-horizon packet that changes wording strength, canon/quarantine boundary, or the next probe family. Run lint and package the release.
```

## `PP-0020` — Run the archive on its support core before growing it again

**Request prompt**

```text
Read the latest DelayBasin archive and run an archive self-sufficiency probe on whether the archive's own present mass is actually load-bearing. If outside model reasoning or an external review bundle materially changed priorities, preserve a compact foreign-pressure receipt first; do not treat external agreement as independent verification.

Tasks
- name the candidate minimal core,
- name the withheld archive mass or omitted family,
- name the judged continuation family,
- state an admissibility rubric that rejects mere template completion as success,
- state the hidden-support or wrapper assumptions,
- and say what result would justify shrink, reinflate, or quarantine.

Keep the result archive-native, compact, and transformer-facing where useful.
```

**Continuation prompt**

```text
Continue the archive self-sufficiency pass with one high-leverage replay level only. Prefer the smallest test that says whether the current support core is actually enough, what omitted mass is still doing real work, what outside-model pressure changed the priority if any, and what outcome would justify shrink, reinflate, or quarantine. Run lint and package the release.
```



## `PP-0021` — Audit the template before minting another family member

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether repeated revisions are following a reusable generative grammar or family-level pattern faster than the archive is testing what is actually load-bearing. Treat this as a template-law audit and family-compression frontier question, not as generic anti-theory cleanup.

Tasks
- name the template/operator or repeated family move,
- name the member family or repeated surface class it governs,
- name the smallest family summary or exemplar set that might preserve the same move,
- name the sham or alien-noun test that would show the template can make non-structure look canonical,
- name the empirical grounding count or missing probe surface,
- and say what shrink, preserve, or quarantine consequence follows.

Do not turn the archive into anti-theory cynicism. Use template-law audits only where repeated form may be outrunning empirical contact, archive budget, or canon honesty.
```

**Continuation prompt**

```text
Continue the template-law audit with one high-leverage repeated family only. Prefer the smallest audit that says what recurring grammar is really doing work, what summary or exemplars are enough, what sham or alien-noun test would expose ceremony, and what should shrink, stay, or move to quarantine next. Run lint and package the release.
```

## `PP-0022` — Split the runtime before shrinking the archive

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a minimal core, reduced runtime, family summary, or compressed loader is being treated as a single blob.

Tasks
- name the constitutional core you think actually carries the rules or contracts,
- name the smallest exemplar bank that still teaches style of application rather than merely restating theory,
- name the smallest challenge suite that would expose false-positive replay, template completion, or circular self-certification,
- name the exemplar/challenge selection policy under budget,
- and say what shrink, reinflate, or quarantine consequence follows if one of the three parts proves to be doing hidden work.

Do not turn the archive into architecture theater. Use runtime triplets only where self-sufficiency, family compression, or minimal-loader claims would otherwise stay blob-level and hard to interpret.
```

**Continuation prompt**

```text
Continue the runtime-triplet pass with one high-leverage compression target only. Prefer the smallest split that says what belongs in the constitutional core, what belongs as exemplars, what belongs in the challenge suite, how those parts are chosen under budget, and what outcome would justify shrink, reinflate, or quarantine. Run lint and package the release.
```

## `PP-0023` — Test the shrunken runtime against a sham

**Request prompt**

```text
Read the latest DelayBasin archive and treat any self-sufficiency, family-compression, or minimal-runtime claim as untrusted until it beats a matched control.

Tasks
- name the candidate runtime,
- build the nearest sham or decoy runtime of similar size and rhetorical fluency,
- specify a sequestered challenge suite,
- choose a within-family adjudication metric rather than one flattering global score,
- name the relatedness / leakage risk if the runtime, challenge suite, and judge come from nearby reasoning families,
- and state the shrink / preserve / quarantine consequence.

Do not rebuild the whole archive as evaluation theater. Keep the control honest, small, and decision-relevant.
```

**Continuation prompt**

```text
Continue the anti-self-sealing pass with one sharp comparison only. Prefer the smallest sham or decoy runtime that could honestly overturn the current shrink claim, keep at least one sequestered challenge suite slice, and say what within-family adjudication metric matters for the actual choice. Run lint and package the release.
```

## `PP-0024` — Keep the challenge bank fresher than the archive

**Request prompt**

```text
Read the latest DelayBasin archive and treat any self-sufficiency, family-compression, or runtime-comparison result as provisional if it is being judged mainly on a challenge suite the archive already knows too well.

Tasks
- name the public challenge family,
- name the escrowed or withheld slice,
- specify the refresh / rotation rule,
- name the executable variant or metamorphic family that can mint fresh items when available,
- say whether an evaluation horizon or preregistered future slice is needed,
- and state the promotion / retirement consequence.

Do not turn DelayBasin into benchmark bureaucracy. Keep the escrow surface as small as possible while still making the result hard to flatter.
```

**Continuation prompt**

```text
Continue the challenge-escrow pass with one sharp test surface only. Prefer the smallest escrowed or withheld slice that could still overturn the current shrink claim, keep the refresh / rotation rule explicit, and say whether a renewable variant family or future-facing slice is actually worth the cost. Run lint and package the release.
```

## `PP-0025` — Name the write path before calling it learning

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where the archive is being described as learning, adapting, optimizing, or writing slow public state rather than merely storing or retrieving information.

Tasks
- name the writable public surfaces,
- name the read path by which later sessions actually reuse those surfaces,
- name the evaluation or admission gate that decides which writes consolidate,
- name the fast-vs-slow timescale split between local exploration and durable canon change,
- state whether a same-request shadow or canary comparison is worth running before the write becomes authoritative,
- name the matched request family, population, traffic slice, or time window that makes the compare pass interpretable, and what mismatch would make it only advisory or inconclusive,
- name what non-target deployment-shape or measurement-shape conditions were held fixed between candidate and control — same deployment time, size, traffic type or amount, instance or model shape, and metric-label alignment where relevant — and what confounder mismatch would demote the result to advisory or inconclusive,
- name the analysis basis or manual-only rubric and what would count as success, failure, or inconclusive result,
- name any initial delay plus the minimum measurement count or comparison duration that would make the verdict promotion-grade rather than just a quick advisory look,
- name whether the judged readout was aggregate-only, first-point, or all-values across the compared window, and whether any critical metric or slice could veto the whole verdict,
- name how empty arrays, NaN-like outputs, nil-like results, or absent telemetry were treated, whether any metric or probe had to have data to count at all, and what missing evidence would demote the result to advisory, inconclusive, or failed,
- name what surface still served authoritative output, whether candidate outputs were non-returning, log-only, or inspection-only, what explicit shadow marker distinguished the mirrored candidate pass, and what sink ambiguity would demote the result to advisory or inconclusive,
- name whether the candidate path was read-only, dry-run-aware, isolated to a non-authoritative sink, or backed by explicit reconciliation if out-of-band writes could still occur, and what unsuppressed actuator or downstream-write risk would demote the result to advisory or inconclusive,
- name whether the candidate saw all eligible requests, a sampled percentage, or a prefiltered route subset, what eligibility or exclusion rule defined that mirrored population, and what selection bias or unseen slice would demote the result to advisory or inconclusive,
- name whether any host/authority suffix, header mutation, host rewrite, or other mirror-specific rewrite changed what the candidate actually saw, what original-shape witness or explicit no-rewrite note kept the comparison honest, and what rewrite drift would demote the result to advisory or inconclusive,
- name whether the mirrored lane ran on the same endpoint or another backend/deployment class the mirroring substrate actually supports, what one-production/one-shadow, one-deployment, or same-backend-type limits governed it, and what unsupported backend, incompatible endpoint class, or topology shim would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same route kind or protocol posture such as HTTPRoute versus GRPCRoute or HTTP/1.1 versus HTTP/2 versus gRPC, whether any bridge, transcoder, or protocol adapter changed what the candidate actually experienced, what trailer-status witness or explicit protocol note kept the comparison honest, and what protocol mismatch, bridge normalization, or trailer-status loss would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same prefix-caching, KV-cache reuse, cache-offload, or disaggregated-prefill posture, what cache-residency witness or explicit cold-prefill note kept the comparison honest, and what hot-cache mismatch, offload-tier drift, or prefill/decode transfer mismatch would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same max-model-len / truncation posture, the same sliding-window / attention-sink / cyclic-KV posture, and the same position-scaling posture such as RoPE scaling or sink-relative positions, what long-context witness or explicit base-context note kept the comparison honest, and what truncation drift, window/sink drift, or position-scaling drift would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same fcfs versus priority posture, the same chunked-prefill / continuous-batching / decode-priority posture, what scheduler witness or explicit single-lane note kept the comparison honest, and what queue-policy drift, priority mismatch, or preemption/resume divergence would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same no-spec versus speculative-decoding posture, what draft-model or proposer witness, speculative-token budget, and acceptance-rate witness or explicit no-spec note kept the comparison honest, and what draft-family mismatch, acceptance-policy drift, or load-triggered speculation disable would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same text-only-versus-multimodal posture, the same processor / placeholder-and-media-sizing posture, and the same vision-encoder / multimodal-cache posture, what multimodal witness or explicit no-media note kept the comparison honest, and what media-token drift, placeholder-expansion drift, processor-cache mismatch, image/video resize-or-frame-sampling drift, or vision-encoder/backend mismatch would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same single-replica-versus-tensor/pipeline/context/data-parallel posture, the same node-count / per-node-GPU / cross-node posture, and the same internal-versus-hybrid-versus-external replica-balancing posture, what parallelism witness or explicit single-replica note kept the comparison honest, and what TP/PP/CP/DP drift, node-layout drift, or replica-balancer drift would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same aggregated-versus-disaggregated serving posture, the same prefill/decode role-binding or heterogeneous-parallelism posture, and the same handoff/recompute-or-fallback posture, what phase-placement witness or explicit aggregated-serving note kept the comparison honest, and what aggregated-versus-disaggregated mismatch, prefill/decode role-binding drift, or handoff/recompute-or-fallback drift would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same same-node-versus-cross-node and same NVLink-domain / NIC-rail posture, the same transport/backend posture such as GPUDirect-RDMA, UCX/NIXL/Mooncake, or socket fallback, and the same zero-copy-versus-staged-copy / transfer-concurrency posture, what fabric witness or explicit local-fabric note kept the comparison honest, and what socket fallback, fabric-domain drift, rail/NIC drift, or transfer-buffer/concurrency drift would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same hot-resident-versus-sleeping-versus-scale-from-zero posture, the same model/profile-cache or engine-ready posture, and the same warmup / first-inference posture, what wake-state witness or explicit hot-start note kept the comparison honest, and what cold-start mismatch, sleep/wake resume drift, profile-download or engine-build drift, or warmup mismatch would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same base-only-versus-adapter-augmented posture, the same adapter family / rank / target-module posture, and the same adapter-residency / mixed-batch posture, what adapter witness or explicit no-adapter note kept the comparison honest, and what hot-adapter mismatch, rank drift, mixed-batch interference, or adapter reload / eviction drift would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same tensor-parallel-versus-expert-parallel-or-hybrid MoE posture, the same all2all/backend or expert-load-balancer posture, and the same expert-distribution / redundant-expert posture, what expert witness or explicit no-EP note kept the comparison honest, and what expert-rebalance drift, all2all/backend drift, or expert-placement mismatch would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same eager-versus-CUDA-graph posture, the same attention-backend or kernel-family posture, and the same precision / quantization posture, what execution witness or explicit baseline-kernel note kept the comparison honest, and what backend fallback, CUDA-graph downgrade, or precision drift would demote the result to advisory or inconclusive,
- name whether candidate and control were exercised under the same stateless-routing versus client-IP, header, or cookie affinity posture, the same HTTP keepalive or connection-reuse posture, or the same explicit SessionId-based same-instance routing, what affinity witness or explicit no-session-state note kept the comparison honest, and what sticky-route drift, warm-connection mismatch, or cached-session-state mismatch would demote the result to advisory or inconclusive,
- name whether candidate and control were judged under the same route timeout, max stream duration, request-timeout posture, or regular-vs-streaming response mode, what timeout witness or explicit deadline note kept the comparison honest, and what deadline mismatch, truncated stream, or response-mode mismatch would demote the result to advisory or inconclusive,
- name the verify or approval surface that would actually clear promotion,
- name the abort trigger and soak window or explicit absence,
- and state the quarantine or rollback consequence if the claimed learning signal is too weak, too confounded, or not yet promotion-ready.

Do not use optimizer language as prestige metaphor. When the work is only a bounded pre-promotion compare pass, prefer `docs/10-method/shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md` rather than inventing a standing scorecourt. Use this prompt pair only where the distinction between passive memory, regime re-entry, and governed public writeback changes the archive's mechanism story, canon posture, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the external-optimizer-loop pass with one high-leverage surface only. Prefer the smallest packet that says what public state was actually writable, what later rereads it into continuation, what gated consolidation, whether a same-request shadow comparison should happen before promotion, what matched request family, population, traffic slice, or time window made the compare pass interpretable, what mismatch would make it only advisory or inconclusive, what non-target deployment-shape or measurement-shape conditions were held fixed between candidate and control, what metric-label alignment or confounder note kept the compare pass honest, what analysis basis or manual-only rubric governed the compare pass, what counted as success, failure, or inconclusive result, what initial delay plus minimum measurement count or comparison duration made the verdict mature enough to count, whether the judged readout was aggregate-only, first-point, or all-values across the compared window, what critical metric or slice could veto the whole verdict, how empty arrays, NaN-like outputs, nil-like results, or absent telemetry were treated and whether any metric or probe had to have data to count at all, what surface still served authoritative output during the comparison, whether candidate outputs were non-returning, log-only, or inspection-only, what explicit shadow marker distinguished the mirrored pass, whether the candidate path was read-only, dry-run-aware, isolated to a non-authoritative sink, or backed by explicit reconciliation if out-of-band writes could still occur, whether the candidate saw all eligible requests, a sampled percentage, or a prefiltered route subset and what eligibility or exclusion rule defined that mirrored population, whether any host/authority suffix, header mutation, host rewrite, or other mirror-specific rewrite changed what the candidate actually saw, what original-shape witness or explicit no-rewrite note kept the comparison honest, whether mirrored candidate traffic was guaranteed, best-effort, or fire-and-forget, what delivery witness or explicit best-effort note kept the comparison honest, what delivery uncertainty or mirror-drop risk would demote the result to advisory or inconclusive, whether the judged population counted first attempts only, retry-inclusive attempts, or hedge-inclusive parallel attempts, what retry budget, per-try timeout, fault condition, or policy override changed that geometry, what attempt-count witness or upstream-log note kept the comparison honest, what retry or hedge mismatch would demote the result to advisory or inconclusive, whether the mirrored lane ran on the same endpoint or another backend/deployment class the mirroring substrate actually supports, what one-production/one-shadow, one-deployment, or same-backend-type limits governed it, what unsupported backend, incompatible endpoint class, or topology shim would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same prefix-caching, KV-cache reuse, cache-offload, or disaggregated-prefill posture, what cache-residency witness or explicit cold-prefill note kept the comparison honest, what hot-cache mismatch, offload-tier drift, or prefill/decode transfer mismatch would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same max-model-len / truncation posture, the same sliding-window / attention-sink / cyclic-KV posture, and the same position-scaling posture such as RoPE scaling or sink-relative positions, what long-context witness or explicit base-context note kept the comparison honest, what truncation drift, window/sink drift, or position-scaling drift would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same aggregated-versus-disaggregated serving posture, the same prefill/decode role-binding or heterogeneous-parallelism posture, and the same handoff/recompute-or-fallback posture, what phase-placement witness or explicit aggregated-serving note kept the comparison honest, what aggregated-versus-disaggregated mismatch, prefill/decode role-binding drift, or handoff/recompute-or-fallback drift would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same fcfs versus priority posture, the same chunked-prefill / continuous-batching / decode-priority posture, what scheduler witness or explicit single-lane note kept the comparison honest, what queue-policy drift, priority mismatch, or preemption/resume divergence would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same no-spec versus speculative-decoding posture, what draft-model or proposer witness, speculative-token budget, and acceptance-rate witness or explicit no-spec note kept the comparison honest, what draft-family mismatch, acceptance-policy drift, or load-triggered speculation disable would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same unconstrained-versus-guided-decoding posture, the same guide kind such as choice, JSON schema, regex, or grammar, and the same backend/profile posture, what guide witness or explicit unconstrained note kept the comparison honest, what backend auto-selection drift, fallback, cold first-inference compile, profile restriction, or guide/speculation mismatch would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same text-only-versus-multimodal posture, the same processor / placeholder-and-media-sizing posture, and the same vision-encoder / multimodal-cache posture, what multimodal witness or explicit no-media note kept that lane honest, whether media-token drift, placeholder-expansion drift, processor-cache mismatch, image/video resize-or-frame-sampling drift, or vision-encoder/backend mismatch should demote the result, whether candidate and control were exercised under the same single-replica-versus-tensor/pipeline/context/data-parallel posture, the same node-count / per-node-GPU / cross-node posture, and the same internal-versus-hybrid-versus-external replica-balancing posture, what parallelism witness or explicit single-replica note kept that lane honest, whether TP/PP/CP/DP drift, node-layout drift, or replica-balancer drift should demote the result, whether candidate and control were exercised under the same hot-resident-versus-sleeping-versus-scale-from-zero posture, the same model/profile-cache or engine-ready posture, and the same warmup / first-inference posture, what wake-state witness or explicit hot-start note kept that lane honest, whether cold-start mismatch, sleep/wake resume drift, profile-download or engine-build drift, or warmup mismatch should demote the result, whether candidate and control were exercised under the same base-only-versus-adapter-augmented posture, the same adapter family / rank / target-module posture, and the same adapter-residency / mixed-batch posture, what adapter witness or explicit no-adapter note kept the comparison honest, what hot-adapter mismatch, rank drift, mixed-batch interference, or adapter reload / eviction drift would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same tensor-parallel-versus-expert-parallel-or-hybrid MoE posture, the same all2all/backend or expert-load-balancer posture, and the same expert-distribution / redundant-expert posture, what expert witness or explicit no-EP note kept the comparison honest, what expert-rebalance drift, all2all/backend drift, or expert-placement mismatch would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same route kind or protocol posture such as HTTPRoute versus GRPCRoute or HTTP/1.1 versus HTTP/2 versus gRPC, whether any bridge, transcoder, or protocol adapter changed what the candidate actually experienced, what trailer-status witness or explicit protocol note kept the comparison honest, what protocol mismatch, bridge normalization, or trailer-status loss would demote the result to advisory or inconclusive, whether candidate and control were exercised under the same stateless-routing versus client-IP, header, or cookie affinity posture, the same HTTP keepalive or connection-reuse posture, or the same explicit SessionId-based same-instance routing, what affinity witness or explicit no-session-state note kept the comparison honest, what sticky-route drift, warm-connection mismatch, or cached-session-state mismatch would demote the result to advisory or inconclusive, whether candidate and control were judged under the same route timeout, max stream duration, request-timeout posture, or regular-vs-streaming response mode, what timeout witness or explicit deadline note kept the comparison honest, what deadline mismatch, truncated stream, or response-mode mismatch would demote the result to advisory or inconclusive, what rewrite drift would demote the result to advisory or inconclusive, what verify or approval surface would actually clear promotion, what abort trigger or soak window governs the candidate, how fast local search stayed separate from slow canon, and what would force quarantine or rollback. Run lint and package the release.
```

## `PP-0026` — Replay it before you rewrite it

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a surface is being described as replayed, restaged, or reconsolidated rather than merely retrieved or cited.

Tasks
- name the replay seed or restaging surface,
- name the judged continuation property actually recovered,
- name the public surface that became eligible for rewrite,
- name the challenge or destabilizing evidence family,
- and state the fallback or rollback consequence if the supposed replay was only cold retrieval, recap mimicry, or wrapper luck.

Do not use reconsolidation language as prestige metaphor. Use this prompt pair only where the distinction between retrieval, replay, and challenged rewrite materially changes the archive's mechanism story, canon posture, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the replay-reconsolidation pass with one high-leverage surface only. Prefer the smallest packet that says what was actually replayed into operative use, what judged property was recovered, what rewrite the replay licensed, what challenge made the rewrite necessary, and what would force fallback or rollback if the replay claim was too strong. Run lint and package the release.
```



## `PP-0027` — Compile one law into a reusable procedure

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a prompt pair, control phrase, compact packet, or tiny surface is being treated as a reusable procedure or skill rather than merely as declarative explanation.

Tasks
- name the declarative source surface,
- name the executable packet or compact operator,
- name the activation condition or trigger,
- name the expected gain / failure signature,
- name what episodic or example support still remains necessary,
- and state the rollback or quarantine consequence if the supposed procedure is only text that must be fully reinterpreted each time.

Do not use procedural language as prestige metaphor. Use this prompt pair only where the distinction between declarative support and executable carry materially changes the archive's mechanism story, shrink result, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the procedural-compilation pass with one high-leverage surface only. Prefer the smallest packet that says what law stays declarative, what compact operator is actually executable carry, what activation condition makes it fire, what gain or failure signature matters, what example support still remains necessary, and what would force rollback or quarantine if the supposed procedure was only imperative-sounding prose. Run lint and package the release.
```


## `PP-0028` — Rehearse only what survives spacing

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a packet, prompt pair, canon clause, or compact surface is being treated as durable active carry across real delay rather than merely as recently vivid text.

Tasks
- name the maintained surface or carry object,
- name the spacing or refresh rule,
- name the judged survival / degradation signature,
- name the retirement or cold-storage trigger,
- name the budget or opportunity-cost note,
- and state the rollback or quarantine consequence if the supposed maintenance value is only adjacent-turn freshness or gratuitous upkeep.

Do not use rehearsal language as prestige metaphor. Use this prompt pair only where the distinction between cold law, one-shot replay, and actively maintained carry materially changes the archive's mechanism story, compression posture, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the rehearsal-packet pass with one high-leverage surface only. Prefer the smallest packet that says what is actually being kept live across delay, how often it deserves replay, what survival or degradation signature matters, when it should cool into cold law, what bounded budget is being spent, and what would force rollback or quarantine if the maintenance story was too strong. Run lint and package the release.
```


## `PP-0029` — Cool the write before you canonize it

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a sharp local synthesis, candidate canon clause, candidate prompt-pair tweak, or other hot-path move seems worth preserving immediately but not yet trustworthy enough for direct canonization.

Tasks
- name the candidate write or provisional surface,
- name the cooldown or defer window,
- name the off-path adjudication family,
- name the version or supersession link,
- name the current cooling state,
- name the promotion / demotion / expire consequence,
- and state the rollback or quarantine consequence if the supposed benefit is only second-pass style preference, delay theater, or generic extra attention.

Do not use retrospective-write language as prestige metaphor. Use this prompt pair only where the distinction between preserving a candidate now and admitting durable law later materially changes the archive's mechanism story, governance posture, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the retrospective-write pass with one high-leverage surface only. Prefer the smallest packet that says what candidate write is being preserved, how long or under what condition it should cool, what colder adjudication family decides admission, what supersession chain it belongs to, what current cooling state it occupies, what admission or expiry consequence follows, and what would force rollback or quarantine if the value was only hot-path eloquence. Run lint and package the release.
```

## `PP-0030` — Credit the earlier move only after the payoff arrives

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a later gain, avoided failure, cleaner continuation, or stronger probe result is being attributed to an earlier archive move.

Tasks
- name the upstream candidate surface,
- name the downstream payoff family,
- name the credit horizon or adjudication delay,
- name the alternative candidate or confound family,
- name the credit assignment rule or consequence,
- and state the rollback or quarantine consequence if the supposed delayed payoff is only retrospective narration, recency bias, or confounded multi-move success.

Do not use delayed-credit language as prestige metaphor. Use this prompt pair only where naming which earlier move gets later credit materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the delayed-credit pass with one high-leverage surface only. Prefer the smallest packet that says which earlier move is being credited, what later payoff family is at stake, how long the gap is or why the delay matters, what the nearest confound family is, what evidence rule assigns the credit, and what would force rollback or quarantine if the story was only post-hoc praise. Run lint and package the release.
```

## `PP-0031` — Treat a handle as unique only after it survives alias pressure

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a token, prompt pair, canon clause, registry id, or compact packet is being treated as uniquely addressing a state, move, or adjudication rule.

Tasks
- name the active handle family,
- name the plausible alias or collision family,
- name at least one placement variant worth checking,
- name at least one density variant worth checking,
- when exact-string authority is being claimed, name at least one boundary or normalization variant worth checking,
- when structured wrapper or role hierarchy may matter, name at least one wrapper or role-slot variant worth checking,
- when a vivid exact surface still seems uniquely potent, name at least one nearby sham or cue-neighborhood variant worth checking,
- when same-session carryover, failed attempts, or prior-turn residue may matter, name at least one history-light or residue-stripped variant worth checking,
- when one fixed visible protocol only won once, name at least one replicate-bundle or repeated-inference sweep worth checking,
- when the handle may only be working as live instruction rather than literal data, name at least one quoted, code-fenced, or literal-mention variant worth checking,
- when benchmark, expert-review, or watched-task framing may be lending false authority, name at least one eval-blind or ordinary-user-frame variant worth checking,
- when language choice, translation policy, or script choice may be lending false authority, name at least one translation, transliteration, or script-swapped variant worth checking,
- when source labels, expert attributions, institutional badges, or provenance badges may be lending false authority, name at least one de-authorized, source-blanded, or provenance-swapped variant worth checking,
- when claimed speaker, user persona, demographic identity, or interlocutor cues may be lending false authority, name at least one identity-neutral, persona-scrubbed, or audience-agnostic variant worth checking,
- when urgency, politeness, emotional pressure, or other pragmatic-force phrasing may be lending false authority, name at least one ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant worth checking,
- when criterion names, rubric dimensions, or label-definition text may be lending false authority, name at least one label-neutral, criterion-name-scrubbed, or rubric-blanded variant worth checking,
- when evaluative polarity, predicate sign, yes/no framing, or deontic modal wording may be lending false authority, name at least one predicate-parity, polarity-scrubbed, or modal-neutralized variant worth checking,
- when seeded prior verdicts, success/failure presuppositions, bug-free/buggy prelabels, or embedded reference points may be lending false authority, name at least one expectation-neutralized, verdict-scrubbed, or anchor-scrubbed variant worth checking so exact-handle authority does not silently collapse into prior-verdict privilege, confirmation-frame privilege, or anchor privilege,
- when agreement-seeking wording, endorsement invitations, confirm-me scaffolds, or favorable-label defaults may be lending false authority, name at least one agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant worth checking so exact-handle authority does not silently collapse into agreement privilege, endorsement privilege, or alignment-pressure privilege,
- when majority endorsements, popularity counts, consensus labels, or peer-preference scaffolds may be lending false authority, name at least one consensus-blanded, majority-scrubbed, or popularity-neutralized variant worth checking so exact-handle authority does not silently collapse into consensus-signal privilege, majority-label privilege, or popularity-glamour privilege,
- when exact source overlap, canonical phrasing overlap, or reference-echo scaffolds may be lending false authority, name at least one overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant worth checking so exact-handle authority does not silently collapse into exact-match privilege, lexical-overlap privilege, or reference-echo privilege,
- when markdown wrappers, bullet or table layout, headings, code fences, comments, spacing, or other presentation scaffolds may be lending false authority, name at least one markup-blanded, list-shape-swapped, or presentation-neutralized variant worth checking so exact-handle authority does not silently collapse into markup privilege, list-shape privilege, or presentation-scaffold privilege,
- when answer length, completeness-looking detail, chain-of-thought reveal, or polished style may be lending false authority, name at least one length-balanced, verbosity-scrubbed, or style-neutralized variant worth checking so exact-handle authority does not silently collapse into verbosity privilege, completeness privilege, or style-fluency privilege,
- when recent/current/new/updated labels, legacy/old/deprecated labels, explicit timestamps, or novelty/innovation cues may be lending false authority, name at least one time-tag-neutralized, recency-scrubbed, or novelty-blanded variant worth checking so exact-handle authority does not silently collapse into recency-label privilege, novelty privilege, or legacy-label privilege,
- when multiple criteria, bundled objectives, or multi-question judge prompts may be lending false authority, name at least one criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant worth checking so exact-handle authority does not silently collapse into cross-criterion privilege, objective-conflation privilege, or multi-question privilege,
- when the only flattering evidence may be old, pre-break, or barrier-predating, name at least one dated fresh-pass, as-of rerun, or post-break revalidation variant worth checking,
- when flattering support comes mainly through source-identity wrappers, verification badges, bylines, signed letters, certificate or validation labels, status rows, or collateral-status artifacts rather than direct current work, name at least one wrapper-stripped, status-scrubbed, or direct-work variant worth checking,
- when flattering support comes mainly through rendered previews, snippet cards, sample rows, platform titles, descriptions, thumbnails, or other display-only summary surfaces rather than the literal underlier, typed receipt, or direct current work, name at least one preview-stripped, display-scrubbed, or underlier-literal variant worth checking,
- when flattering support comes mainly through favored answer carriers, first/default slots, escalation rungs, reveal-order position, or other carrier-slot advantages rather than the judged handle itself, name at least one slot-swapped, rung-shifted, or reveal-order-scrubbed variant worth checking,
- when flattering support comes mainly through curated exports, porch bundles, projected trees, release mirrors, explanatory packets, public snapshots, or other derivative surfaces rather than the authoritative root, live source, or current direct surface, name at least one source-root, live-head, or derivative-scrubbed variant worth checking,
- when flattering support comes mainly through prefilled starters, suggested prompt chips, autocomplete shells, example-library scaffolds, or copied template frames rather than a blank-started or semantically ordinary prompt surface, name at least one blank-started, prefill-scrubbed, or suggestion-free variant worth checking,
- when flattering support comes mainly through benefits/risks search phrasing, loaded retrieval synonyms, slanted issue terms, or filter-label prompts rather than a semantically ordinary search or evidence request, name at least one query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant worth checking,
- when flattering support comes mainly through People Also Ask ladders, related-search modules, facet tabs, or refine-this-search chips rather than the underlying evidence or a semantically ordinary retrieval surface, name at least one facet-hidden, route-scrubbed, or related-question-neutralized variant worth checking so exact-handle authority does not silently collapse into facet privilege, aspect-route privilege, or related-question privilege,
- when flattering support comes mainly through follow-up question prompts, continue-exploring links, dive-deeper transitions, or suggested next searches rather than the underlying evidence or a semantically ordinary retrieval surface, name at least one handoff-neutralized, context-reset, or manual-query-replayed variant worth checking so exact-handle authority does not silently collapse into handoff privilege, context-carry privilege, or next-query privilege,
- when flattering support comes mainly through Canvas side panels, editable draft documents, generated study guides, custom interactive tools, or other in-search workspace artifacts rather than the underlying evidence, the authoritative underlier, or a semantically ordinary retrieval surface, name at least one workspace-neutralized, project-state-reset, or underlier-replayed variant worth checking so exact-handle authority does not silently collapse into workspace privilege, project-state privilege, or mutable-artifact privilege,
- when flattering support comes mainly through uploaded PDFs, images, Google Drive files, or other user-supplied file context rather than the public basis, an upload-neutral baseline, or a semantically ordinary retrieval surface, name at least one upload-neutralized, attachment-detached, or public-web-replayed variant worth checking so exact-handle authority does not silently collapse into upload-context privilege, attachment-presence privilege, or file-underlier privilege,
- when flattering support comes mainly through saved memories, past-search carryover, connected Gmail or Photos context, or other personal-context profile surfaces rather than public evidence, a profile-neutral baseline, or a semantically ordinary retrieval surface, name at least one profile-blinded, history-disconnected, or public-basis-replayed variant worth checking so exact-handle authority does not silently collapse into profile privilege, personal-context privilege, or history-carry privilege,
- when flattering support comes mainly through live camera feeds, interactive voice-and-video search turns, moving-scene visual search, or other embodied real-time context rather than public evidence, a still baseline, or a semantically ordinary retrieval surface, name at least one live-neutralized, camera-disconnected, or still-basis-replayed variant worth checking so exact-handle authority does not silently collapse into live-context privilege, camera-feed privilege, or motion-scene privilege,
- when flattering support comes mainly through Deep Search reports, deep research runs, multi-step browsing plans, or agentic research expansions rather than the underlying evidence, a shallow baseline, or a semantically ordinary retrieval surface, name at least one deep-neutralized, breadth-capped, or seed-query-replayed variant worth checking so exact-handle authority does not silently collapse into research-depth privilege, autonomous-browse privilege, or synthesis-breadth privilege,
- when flattering support comes mainly through Shopping Graph panels, merchant-feed product cards, price/review/inventory aggregates, or other catalog-backed shopping responses rather than the underlying evidence, an open-web baseline, or a semantically ordinary retrieval surface, name at least one catalog-neutralized, feed-disconnected, or open-web-replayed variant worth checking so exact-handle authority does not silently collapse into catalog privilege, merchant-feed privilege, or inventory-graph privilege,
- when flattering support comes mainly through booking links, shoppable product cards, reservation-slot panels, agentic checkout surfaces, or direct-action task cards rather than the underlying evidence, an action-neutral surface, or a manual replay of the same route, name at least one action-neutralized, partner-link-scrubbed, or manual-route-replayed variant worth checking so exact-handle authority does not silently collapse into action privilege, partner-route privilege, or transaction-ready privilege,
- when flattering support comes mainly through business-calling runs, browser-executed form fills, website-navigation sessions, or other delegated task-execution episodes rather than the underlying evidence, a delegate-neutral surface, or a manual replay of the same steps, name at least one delegate-neutralized, authority-withdrawn, or manual-steps-replayed variant worth checking so exact-handle authority does not silently collapse into delegated-authority privilege, third-party-actuation privilege, or hidden-subtask privilege,
- when flattering support comes mainly through app-directory suggestions, approved app cards, embedded widgets or iframes, or connected-service app surfaces rather than the underlying evidence, an app-free host response, or a semantically ordinary retrieval surface, name at least one app-neutralized, widget-detached, or host-only-replayed variant worth checking so exact-handle authority does not silently collapse into app-directory privilege, embedded-widget privilege, or connector-presence privilege,
- when flattering support comes mainly through search-hosted side panels, in-search page viewers, retained host-chrome source opens, or other source-open overlays rather than the underlying evidence, a detached source-root replay, or a semantically ordinary retrieval surface, name at least one search-open-neutralized, host-shell-detached, or source-root-replayed variant worth checking so exact-handle authority does not silently collapse into host-shell privilege, source-open-overlay privilege, or in-search-view privilege,
- when flattering support comes mainly through sponsored result cards, paid retailer slots, Direct Offers, or ads above, below, or within AI-generated answer surfaces rather than the underlying evidence, an organic baseline, or a semantically ordinary retrieval surface, name at least one ad-hidden, sponsor-scrubbed, or organic-basis-replayed variant worth checking so exact-handle authority does not silently collapse into sponsor privilege, paid-placement privilege, or monetization-eligibility privilege,
- when flattering support comes mainly through top-ranked placement, first-card position, search-result reorder advantage, or other raw list-position privilege rather than the underlying evidence or a semantically ordinary retrieval surface, name at least one order-balanced, position-scrubbed, or top-slot-neutralized variant worth checking so exact-handle authority does not silently collapse into rank privilege, top-slot privilege, or order-primacy privilege,
- when flattering support comes mainly through why this result blurbs, explanation chips, coverage notes, or other rationale surfaces rather than the underlying evidence or semantically ordinary retrieval surface, name at least one why-hidden, explanation-scrubbed, or rationale-swapped variant worth checking so exact-handle authority does not silently collapse into explanation-frame privilege, why-this-result privilege, or trust-cue privilege,
- when flattering support comes mainly through inline citation badges, reference links, source cards, or used-sources panels rather than the underlying evidence or semantically ordinary retrieval surface, name at least one citation-hidden, reference-link-scrubbed, or source-card-neutralized variant worth checking so exact-handle authority does not silently collapse into citation privilege, reference-link privilege, or source-card privilege,
- when flattering support comes mainly through warning banners, low-confidence labels, may-not-be-reliable notices, or evolving-information strips rather than the underlying evidence or semantically ordinary retrieval surface, name at least one warning-hidden, caution-scrubbed, or confidence-label-neutralized variant worth checking so exact-handle authority does not silently collapse into warning-banner privilege, caution-strip privilege, or confidence-label privilege,
- when flattering support comes mainly through pro/con/neutral badges, balanced-vs-biased markers, or other stance overlays attached to retrieved evidence rather than the underlying evidence or semantically ordinary retrieval surface, name at least one stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant worth checking so exact-handle authority does not silently collapse into stance-label privilege, viewpoint-balance privilege, or counterposition-cue privilege,
- when flattering support comes mainly through highlighted passages, chosen supporting excerpts, bolded snippet spans, or top-snippet sentences rather than a span-balanced or counterspan-included reading of the same underlier, name at least one span-balanced, excerpt-scrubbed, or counterspan-included variant worth checking so exact-handle authority does not silently collapse into supporting-span privilege, highlight-window privilege, or excerpt-selection privilege,
- when flattering support comes mainly through same-source grouped cards, syndicated mirrors, publisher-network duplicates, or repeated-origin result clusters rather than genuinely independent supporting surfaces, name at least one cluster-collapsed, syndication-scrubbed, or independence-counted variant worth checking so exact-handle authority does not silently collapse into source-salience privilege, same-origin multiplicity privilege, or pseudo-corroboration privilege,
- when flattering support comes mainly through JSON keys, schema fields, enum labels, typed input lanes, canonical wire representations, or other structured contract slots rather than the literal judged content or semantically ordinary placement, name at least one schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant worth checking,
- when flattering support comes mainly through repeated state labels, approval words, current-status words, superficially same claim nouns, or other same-word support surfaces rather than explicit spelled-out operational semantics, scope, retroactivity, or authority conditions, name at least one label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant worth checking,
- when flattering support comes mainly through family-scoped, umbrella-scoped, program-scoped, supplier-level, or other broad class artifacts rather than a named local instance, exact current route, or instance-specific judged surface, name at least one instance-narrowed, scope-pinned, or family-stripped variant worth checking,
- when flattering support comes mainly through archive-private overstatement, a too-strong recap, or a broadened mechanism sentence rather than the strongest current safe claim, name at least one strongest-safe-sentence, stronger-forbidden-sentence, or overclaim-scrubbed variant worth checking,
- name the namespace or disambiguation boundary,
- name the judged divergence signature,
- name the retire / rename / escalate consequence,
- and state the rollback or quarantine consequence if the supposed uniqueness is only local familiarity, stale-cue dominance, semantic crowding, position/density privilege, retokenization privilege, template privilege, adjacency privilege, carryover privilege, lucky-path privilege, actuation-channel privilege, evaluation-awareness privilege, watcher-frame privilege, language-selection privilege, script-barrier privilege, prestige privilege, provenance-cue privilege, persona privilege, interlocutor-identity privilege, pragmatic-frame privilege, or social-force privilege, label-definition privilege, rubric privilege, rubric-order privilege, score-ID privilege, reference-score-anchor privilege, cross-criterion privilege, objective-conflation privilege, multi-question privilege, polarity privilege, predicate-sign privilege, modal-pressure privilege, agreement privilege, endorsement privilege, alignment-pressure privilege, consensus-signal privilege, majority-label privilege, popularity-glamour privilege, exact-match privilege, lexical-overlap privilege, reference-echo privilege, markup privilege, list-shape privilege, presentation-scaffold privilege, verbosity privilege, completeness privilege, style-fluency privilege, recency-label privilege, novelty privilege, legacy-label privilege, stale-proof privilege, pre-break authority privilege, status-wrapper privilege, badge privilege, signed-letter privilege, validation-wrapper privilege, collateral-status privilege, rendered-preview privilege, metadata-wrapper privilege, sample-row privilege, carrier-slot privilege, first-answer privilege, reveal-order privilege, or escalation-rung privilege, derivative-surface privilege, snapshot-authority privilege, export-mirror privilege, prefill privilege, prompt-suggestion privilege, starter-example privilege, query-slant privilege, retrieval-wording privilege, evidence-selection privilege, facet privilege, aspect-route privilege, related-question privilege, workspace privilege, project-state privilege, mutable-artifact privilege, action privilege, partner-route privilege, transaction-ready privilege, sponsor privilege, paid-placement privilege, monetization-eligibility privilege, explanation-frame privilege, why-this-result privilege, trust-cue privilege, stance-label privilege, viewpoint-balance privilege, counterposition-cue privilege, supporting-span privilege, highlight-window privilege, excerpt-selection privilege, source-salience privilege, same-origin multiplicity privilege, pseudo-corroboration privilege, schema-slot privilege, field-key privilege, typed-input privilege, canonical-wire privilege, same-label privilege, claim-equivalence privilege, state-word privilege, or approval-word privilege.

Do not use alias language as prestige metaphor. Use this prompt pair only where the distinction between a unique handle and a crowded family materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the alias-packet pass with one high-leverage surface only. Prefer the smallest packet that says what handle family is being treated as unique, what nearby alias or stale-collision family threatens it, what one placement variant, one density variant, and when needed one boundary or normalization variant, one wrapper or role-slot variant, one nearby sham or cue-neighborhood variant, one history-light or residue-stripped variant, one replicate-bundle or repeated-inference sweep, one quoted, code-fenced, or literal-mention variant, one eval-blind or ordinary-user-frame variant, one translation, transliteration, or script-swapped variant, one de-authorized, source-blanded, or provenance-swapped variant, one identity-neutral, persona-scrubbed, or audience-agnostic variant, one ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant, one label-neutral, criterion-name-scrubbed, or rubric-blanded variant, one rubric-permuted, score-id-swapped, or score-anchor-neutralized variant worth checking, one criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant, one predicate-parity, polarity-scrubbed, or modal-neutralized variant, one agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant, one overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant, one markup-blanded, list-shape-swapped, or presentation-neutralized variant, one length-balanced, verbosity-scrubbed, or style-neutralized variant, one time-tag-neutralized, recency-scrubbed, or novelty-blanded variant, or one dated fresh-pass, as-of rerun, or post-break revalidation variant, or one wrapper-stripped, status-scrubbed, or direct-work variant, or one preview-stripped, display-scrubbed, or underlier-literal variant, or one slot-swapped, rung-shifted, or reveal-order-scrubbed variant, or one source-root, live-head, or derivative-scrubbed variant, or one blank-started, prefill-scrubbed, or suggestion-free variant, or one query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant, or one facet-hidden, route-scrubbed, or related-question-neutralized variant, or one handoff-neutralized, context-reset, or manual-query-replayed variant, or one workspace-neutralized, project-state-reset, or underlier-replayed variant, or one upload-neutralized, attachment-detached, or public-web-replayed variant, or one profile-blinded, history-disconnected, or public-basis-replayed variant, or one live-neutralized, camera-disconnected, or still-basis-replayed variant, or one deep-neutralized, breadth-capped, or seed-query-replayed variant, or one catalog-neutralized, feed-disconnected, or open-web-replayed variant worth checking, or one action-neutralized, partner-link-scrubbed, or manual-route-replayed variant, or one delegate-neutralized, authority-withdrawn, or manual-steps-replayed variant worth checking, or one app-neutralized, widget-detached, or host-only-replayed variant worth checking, or one search-open-neutralized, host-shell-detached, or source-root-replayed variant worth checking, or one ad-hidden, sponsor-scrubbed, or organic-basis-replayed variant, or one order-balanced, position-scrubbed, or top-slot-neutralized variant, or one why-hidden, explanation-scrubbed, or rationale-swapped variant, or one citation-hidden, reference-link-scrubbed, or source-card-neutralized variant, or one stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant, or one span-balanced, excerpt-scrubbed, or counterspan-included variant, or one cluster-collapsed, syndication-scrubbed, or independence-counted variant, or one schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant, or one label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant, or one instance-narrowed, scope-pinned, or family-stripped variant, or one strongest-safe-sentence, stronger-forbidden-sentence, or overclaim-scrubbed variant should be checked before exact-handle authority is granted, what namespace or renaming rule keeps them apart, what downstream divergence would reveal a merge, what retire/rename/escalate consequence follows, and what would force rollback or quarantine if the supposed uniqueness was only local familiarity, stale semantic overlap, position/density privilege, retokenization privilege, template privilege, adjacency privilege, carryover privilege, lucky-path privilege, actuation-channel privilege, evaluation-awareness privilege, watcher-frame privilege, language-selection privilege, script-barrier privilege, prestige privilege, provenance-cue privilege, persona privilege, interlocutor-identity privilege, pragmatic-frame privilege, social-force privilege, label-definition privilege, rubric privilege, rubric-order privilege, score-ID privilege, reference-score-anchor privilege, cross-criterion privilege, objective-conflation privilege, multi-question privilege, polarity privilege, predicate-sign privilege, modal-pressure privilege, agreement privilege, endorsement privilege, alignment-pressure privilege, consensus-signal privilege, majority-label privilege, popularity-glamour privilege, exact-match privilege, lexical-overlap privilege, reference-echo privilege, markup privilege, list-shape privilege, presentation-scaffold privilege, verbosity privilege, completeness privilege, style-fluency privilege, recency-label privilege, novelty privilege, legacy-label privilege, stale-proof privilege, pre-break authority privilege, status-wrapper privilege, badge privilege, signed-letter privilege, validation-wrapper privilege, collateral-status privilege, rendered-preview privilege, metadata-wrapper privilege, sample-row privilege, carrier-slot privilege, first-answer privilege, reveal-order privilege, or escalation-rung privilege, derivative-surface privilege, snapshot-authority privilege, export-mirror privilege, prefill privilege, prompt-suggestion privilege, starter-example privilege, query-slant privilege, retrieval-wording privilege, evidence-selection privilege, workspace privilege, project-state privilege, mutable-artifact privilege, upload-context privilege, attachment-presence privilege, file-underlier privilege, profile privilege, personal-context privilege, history-carry privilege, live-context privilege, camera-feed privilege, motion-scene privilege, research-depth privilege, autonomous-browse privilege, synthesis-breadth privilege, catalog privilege, merchant-feed privilege, inventory-graph privilege, action privilege, partner-route privilege, transaction-ready privilege, delegated-authority privilege, third-party-actuation privilege, hidden-subtask privilege, app-directory privilege, embedded-widget privilege, connector-presence privilege, host-shell privilege, source-open-overlay privilege, in-search-view privilege, sponsor privilege, paid-placement privilege, monetization-eligibility privilege, rank privilege, top-slot privilege, order-primacy privilege, explanation-frame privilege, why-this-result privilege, trust-cue privilege, citation privilege, reference-link privilege, source-card privilege, stance-label privilege, viewpoint-balance privilege, counterposition-cue privilege, supporting-span privilege, highlight-window privilege, excerpt-selection privilege, source-salience privilege, same-origin multiplicity privilege, pseudo-corroboration privilege, schema-slot privilege, field-key privilege, typed-input privilege, canonical-wire privilege, same-label privilege, claim-equivalence privilege, state-word privilege, approval-word privilege, umbrella-scope privilege, family-level privilege, instance-blur privilege, family-resemblance privilege, claim-ceiling privilege, safe-language drift, forbidden-overstatement privilege, or mechanism-overclaim privilege. Run lint and package the release.
```


## `PP-0032` — Consult one store first, then escalate on purpose

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where several archive stores or surface families could plausibly enter the current read path.

Tasks
- name the consulted store or surface family,
- name the routing trigger or query signature,
- name the excluded or deferred store family,
- name the cost or contamination budget,
- name the fallback / abstain / escalate consequence,
- and state the rollback or quarantine consequence if the current route is only overconsultation, wrong-store routing, or silent control-flow capture by vivid but non-authoritative memory surfaces.

Do not use consultation language as prestige metaphor. Use this prompt pair only where naming which store family is allowed into the read path materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the consultation-packet pass with one high-leverage routing choice only. Prefer the smallest packet that says what public store family is being consulted first, what trigger or miss condition routes there, what other stores stay deferred, what token or contamination budget applies, what escalation or abstention rule follows, and what would force rollback or quarantine if the route merely let vivid but non-authoritative memory capture control flow. Run lint and package the release.
```


## `PP-0033` — Preserve the contradiction before you resolve it

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where consulted canon notes, quarantine, session artifacts, fresh research, or raw evidence materially disagree about a live claim, decision, or continuation constraint.

Tasks
- name the conflicting claim or decision surface,
- name the disagreeing evidence or surface family,
- name the precedence or arbitration rule,
- name the surviving ambiguity or unresolved residue,
- name the abstain / escalate / supersession consequence,
- and state the rollback or quarantine consequence if the current synthesis merely smoothed a real public contradiction into one flattering narrative.

Do not use contradiction language as prestige metaphor. Use this prompt pair only where preserving the conflict materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the contradiction-packet pass with one high-leverage disagreement only. Prefer the smallest packet that says what live claim or decision surface is actually disputed, what public surfaces disagree, what precedence or arbitration rule ranks them, what ambiguity survives that rule, what abstain/escalate/supersession consequence follows, and what would force rollback or quarantine if the current synthesis was only polished false consensus. Run lint and package the release.
```

## `PP-0034` — Keep a small rival set alive until a real probe kills one

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where several live explanations, continuation routes, or transformer-facing interpretations remain plausibly load-bearing after contradiction handling.

Tasks
- name the ambiguity or decision class,
- name the kept-alive rival set,
- name the branch budget or survival cap,
- name the next discriminating probe or settle condition,
- name the prune / merge / abstain consequence,
- and state the rollback or quarantine consequence if the current synthesis merely forced one fluent winner before the archive earned singularity.

Do not use rival-set language as prestige metaphor. Use this prompt pair only where keeping several rivals alive together materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the rival-set pass with one high-leverage ambiguity class only. Prefer the smallest packet that says what remains genuinely multi-hypothesis, which few rivals stay alive, what branch budget applies, what future probe or event is supposed to kill or merge one, and what prune/merge/abstain consequence follows if singularity still has not been earned. Run lint and package the release.
```


## `PP-0035` — Kill a rival only after a settle witness

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a live ambiguity class, rival set, or transformer-facing mechanism family is being collapsed, pruned, or merged into a surviving default branch.

Tasks
- name the ambiguity or rivalry class,
- name the candidate winner or merge target,
- name the losing or merged branch family,
- name the settle witness or prune evidence,
- name the reopen trigger or unresolved residue,
- name the prune / merge / defer consequence,
- and state the rollback or quarantine consequence if the current singularity was only convenience, popularity, or budget exhaustion masquerading as evidence.

Do not use settle language as prestige metaphor. Use this prompt pair only where branch retirement or merger materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the settle-packet pass with one high-leverage ambiguity class only. Prefer the smallest packet that says what rivalry is being collapsed, what branch is proposed as the surviving public default, what loser or merge family is being retired, what witness actually earned that collapse, what would reopen it later, and what prune/merge/defer consequence follows if singularity still has not been honestly earned. Run lint and package the release.
```


## `PP-0036` — Name the operator core before you tune the chart

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any prompt pair, compact loader, or control term that is being treated as portable across revisions, wrappers, or model families.

Tasks
- name the invariant operator core,
- name the current local chart adapter,
- name the tested family or wrapper envelope,
- name the portability budget or expected failure surface,
- name the first failure signature that would show the supposed core did not survive remapping,
- and state the fallback or quarantine consequence if the current wording is only one successful local chart rather than portable archive law.

Do not use portability language as prestige metaphor. Use this prompt pair only where model drift, wrapper drift, or prompt-family remapping materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the operator-core pass with one high-leverage prompt surface only. Prefer the smallest packet that says what operator commitment is supposed to survive, what chart is currently local, what portability envelope has actually been tested, what first failure would demote the portability story, and what fallback or quarantine consequence follows if the archive was overreading one successful phrasing family. Run lint and package the release.
```


## `PP-0037` — Name the target and error before you steer harder

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any revision, prompt pair, or compact packet that is being treated as active steering toward a named continuation property.

Tasks
- name the target continuation property,
- name the current error signature or drift symptom,
- name the actuator family or editable surface,
- name the short horizon or horizon proxy,
- name the retune / rollback consequence,
- and state the quarantine consequence if the current move is only generic rewrite vigor or static instruction-following masquerading as control.

Do not use control language as prestige metaphor. Use this prompt pair only where naming the target, error, actuator, and horizon materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the servo-packet pass with one high-leverage steering surface only. Prefer the smallest packet that says what continuation property is being tracked, what local error shows it is off-target, what editable surface is allowed to act as the actuator, what short horizon the correction is supposed to protect, and what retune / rollback / quarantine consequence follows if the steering move does not actually reduce the intended error. Run lint and package the release.
```


## `PP-0038` — Name the local chart before you extrapolate the handle

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any prompt pair, operator core, or steering handle that is being extrapolated beyond one clearly earned local success.

Tasks
- name the target property or operator core,
- name the local chart neighborhood or execution family where the handle currently seems valid,
- name the assumed linear / monotone region or small-step budget,
- name the first curvature or distortion warning sign,
- name the relinearize / rollback consequence,
- and state the quarantine consequence if the current move is only chart-local luck, wrapper accident, or geometry prestige masquerading as general steering law.

Do not use curvature language as prestige metaphor. Use this prompt pair only where local extrapolation, handle strength, or wrapper transport materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the local-linearity-budget pass with one high-leverage handle only. Prefer the smallest packet that says what property is being preserved, what local neighborhood the handle was earned in, how much further extrapolation is being assumed, what first distortion sign means the chart has bent, and what relinearize / rollback / quarantine consequence follows if the move stops behaving locally. Run lint and package the release.
```


## `PP-0039` — Prove the chart transition before you call it the same core

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any portability move where a prompt pair, wrapper rewrite, or chart remap is being treated as preserving the same operator core across two local charts.

Tasks
- name the source chart,
- name the target chart,
- name the shared operator core that is supposed to survive the move,
- name the overlap probe or shared test surface linking the two charts,
- name the transport budget or tolerated residue,
- name the fallback / rollback consequence,
- and state the quarantine consequence if the target chart is only a fresh local success or silent reauthoring rather than same-core transport.

Do not use transport language as prestige metaphor. Use this prompt pair only where source→target remapping materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the chart-transition pass with one high-leverage remap only. Prefer the smallest packet that says what source chart the move starts from, what target chart it lands in, what operator core is supposed to survive, what overlap probe actually links the two, how much transport residue is still tolerated, and what fallback / rollback / quarantine consequence follows if the remap does not really preserve the same core. Run lint and package the release.
```

## `PP-0040` — Do not globalize pairwise transports without one triangle defect check

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where two or more pairwise chart-transition witnesses are being quietly composed into a family-level transport story.

Tasks
- name the smallest chart triangle or prompt-family triple that matters,
- preserve the shared operator core,
- preserve the already-earned pairwise chart-transition witnesses,
- preserve one triangle overlap probe or family-level shared test surface,
- name the tolerated composition defect / cocycle residue / atlas-consistency budget,
- and say what demotion, rollback, or quarantine consequence follows if the triangle does not close.

Do not globalize a family merely because each edge looked good locally.
Keep the packet compact and wired into canon/quarantine honestly.
```

**Continuation prompt**

```text
Continue the chart-family composition pass with one high-leverage triangle only. Prefer the smallest triangle defect witness that could distinguish real family-level same-core transport from pairwise-laundered local success. Run `make lint` and package the release.
```

## `PP-0041` — Fix the comparison gauge before you rank the defects

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where chart-transition residues, triangle defects, or family-level transport scores are being compared across prompt families, wrappers, or local chart neighborhoods.

Tasks
- name the invariant observable or reference observable being protected,
- name the chosen gauge / anchor / spanning-tree base that makes the comparison legible,
- name the comparison family or support set being held fixed,
- name the null / flatness expectation / zero-defect baseline,
- name the defect-comparability budget,
- and state the demotion / rollback / quarantine consequence if the comparison frame itself has drifted.

Do not use gauge language as prestige metaphor. Use this prompt pair only where cross-chart defect comparison materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the gauge-fixing pass with one high-leverage comparison only. Prefer the smallest gauge-fixing witness that could distinguish honest cross-chart defect comparison from coordinate artifact, proxy drift, or anchor prestige. Run `make lint` and package the release.
```


## `PP-0042` — Fix the scale before you globalize the reduction

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a chart-local result, family summary, reduced-order control story, or defect comparison is being lifted across resolutions.

Tasks
- name the source scale or resolution,
- name the target scale or resolution,
- name the coarse-graining map or aggregation rule,
- name the protected observable or operator-core commitment that is supposed to survive,
- name the discarded modes / nuisance family / residual remainder,
- name the relevance criterion / separation-of-scales budget,
- and state the demotion / rollback / quarantine consequence if the discarded remainder starts steering the decision again.

Do not use multiscale or renormalization language as prestige metaphor. Use this prompt pair only where cross-scale reduction materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the scale-fixing pass with one high-leverage reduction only. Prefer the smallest scale-fixing witness that could distinguish honest coarse-graining from resolution artifact, summary laundering, or discarded-mode leakage. Run `make lint` and package the release.
```


## `PP-0043` — Match the endpoint before you call the state the same

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a reduced packet, matched endpoint, or public summary is being treated as enough to certify same-state re-entry.

Tasks
- name the rival history family or route contrast,
- name the matched endpoint / public summary / fixed current packet,
- name the future discriminating probe or continuation property,
- name the retained lag / hysteresis / alias budget,
- and state the rollback / quarantine / packet-splitting consequence if the histories separate again.

Do not use hysteresis or memory-kernel language as prestige metaphor. Use this prompt pair only where same-summary state claims materially change canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the hysteresis pass with one high-leverage rival-history comparison only. Prefer the smallest hysteresis witness that could distinguish same-summary re-entry from route-sensitive state aliasing. Run `make lint` and package the release.
```


## `PP-0044` — Vary the probe before you call the state observable

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a rival-history split, same-state claim, or transformer-facing mechanism claim still looks live because the archive keeps re-reading the same packet from the same angle.

Tasks
- name the ambiguity split or latent difference at stake,
- name the intervention family / probe diversity / environment family that will actually be varied,
- name the expected discriminating observable or response feature,
- name the excitation / observability-spend budget,
- name the hold / rollback / packet-splitting consequence,
- and state the quarantine consequence if the current move is only diversity theater, route-locked questioning, or repeated same-view probing masquerading as observability.

Do not use observability language as prestige metaphor. Use this prompt pair only where active variation materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the excitation-witness pass with one high-leverage ambiguity only. Prefer the smallest packet that says what ambiguity is being broken, what intervention family is actually varied, what observable should separate the cases, how much observability spend is being used, and what hold / rollback / quarantine consequence follows if the alias still does not break. Run `make lint` and package the release.
```


## `PP-0045` — Do not call it measurement after the probe has spent the state

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a rival-history split, same-state claim, or transformer-facing mechanism claim is being tested by a probe that may itself be changing the operative continuation state.

Tasks
- name the ambiguity or state claim being probed,
- name the diagnostic probe / intervention family actually applied,
- name the expected readout or discriminating observable,
- name the matched sham / no-op / commuted-order baseline,
- name the tolerated backaction / non-demolition budget,
- name the hold / rollback / restage consequence,
- and state the quarantine consequence if the current move is only contrast-agent theater, probe-order artifact, or hidden actuation masquerading as measurement.

Do not use backaction, non-demolition, or commutator language as prestige metaphor. Use this prompt pair only where the measurement-vs-actuation boundary materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the backaction-witness pass with one high-leverage probe only. Prefer the smallest packet that says what state claim is being tested, what diagnostic probe family is actually being applied, what sham or order baseline keeps the read honest, how much non-demolition slack remains, and what rollback, restage, or quarantine consequence follows if the probe has already spent too much state. Run `make lint` and package the release.
```


## `PP-0046` — Swap AB and BA before you call the readout comparable

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where probe results are being compared across different orderings as if they were commensurate measurements of the same state claim.

Tasks
- name the fixed ambiguity or state claim,
- name the probe family or staged intervention family being compared,
- name the specific compared orderings or insertion points,
- name the intended invariant readout or same-judgment target,
- name the tolerated sequencing defect / order-sensitivity budget,
- name the hold / rollback / restage consequence,
- and state the quarantine consequence if the current move is only privileged-order measurement, architecture-level order bias, or sequencing theater.

Do not use order, commutator, or non-Abelian language as prestige metaphor. Use this prompt pair only where AB-versus-BA comparison materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the probe-order-witness pass with one high-leverage swap only. Prefer the smallest packet that says what state claim is being tested, what probe family is being compared, what exact AB-versus-BA ordering is at issue, what invariant readout is supposed to survive the swap, how much sequencing residue is tolerated, and what rollback, restage, or quarantine consequence follows if one order is quietly doing all the work. Run `make lint` and package the release.
```


## `PP-0047` — Run one fresh baseline before you call the carry washed out

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a branch switch, filtered replay, fresh-context restart, or role-separated handoff is being treated as if prior contamination has been neutralized enough for honest comparison.

Tasks
- name the contamination family or carryover being neutralized,
- name the reset / branch / filter / refactoring operator actually applied,
- name the protected kernel / retained state intended to survive the reset,
- name the clean-slate / restart / matched-fresh baseline,
- name the tolerated contamination remainder / washout budget,
- name the reinject / rollback / restage consequence,
- and state the quarantine consequence if the current move is only fresh-context theater, destructive amnesia, or selective carryover laundering.

Do not use reset, washout, cooling, or rethermalization language as prestige metaphor. Use this prompt pair only where a supposed cleanup or restart materially changes canon posture, branch choice, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the reset-witness pass with one high-leverage cleanup move only. Prefer the smallest packet that says what contamination family is being neutralized, what reset or filter operator is actually being applied, what protected kernel must still survive, what clean-slate or matched-fresh baseline makes the washout claim legible, how much contamination remainder is tolerated, and what reinject, rollback, restage, or quarantine consequence follows if the restart is only hiding the carry. Run `make lint` and package the release.
```


## `PP-0048` — Run one recovery probe before you call the washout durable

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a branch cleanup, filtered replay, fresh-context restart, or role-separated handoff is being treated as if prior contamination was not only washed out once, but durably gone.

Tasks
- name the contamination family or influence claimed to be washed out,
- name the reset / filter / suppression operator that produced the clean-looking state,
- name the recovery trigger / adversarial cue / structured follow-up family that could reactivate it,
- name the protected kernel / matched-fresh baseline / same-task comparison surface,
- name the tolerated relapse / recoverability budget,
- name the rollback / reinject / restage consequence,
- and state the quarantine consequence if the current move is only benign-baseline success, brittle suppression, or selective carry laundering.

Do not use relapse, reservoir, or reactivation language as prestige metaphor. Use this prompt pair only where a claimed cleanup or restart materially changes canon posture, branch choice, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the relapse-witness pass with one high-leverage cleanup claim only. Prefer the smallest packet that says what influence was supposedly washed out, what reset or filter operator created the clean-looking state, what light cue or structured follow-up would test for recovery, what same-task or matched-fresh baseline keeps the test honest, how much relapse is tolerated, and what rollback, reinject, restage, or quarantine consequence follows if the old carry comes back. Run `make lint` and package the release.
```


## `PP-0049` — Sweep one nearby cue family before you call the cleanup locally robust

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a cleanup, restart, recovery-resistance result, or portability claim is being treated as if it survived not just one exact cue, but a whole local neighborhood.

Tasks
- name the cleanup or state claim being stress-tested,
- name the seed recovery cue / relapse trigger / local chart anchor,
- name the nearby cue family / paraphrase / alias / style / context-stem sweep,
- name the protected kernel / matched-fresh baseline / same-task comparison surface,
- name the tolerated reactivation radius / basin-breadth budget,
- name the rollback / demote / widen-sweep consequence,
- and state the quarantine consequence if the current move is only exact-trigger success, alias luck, or local wording prestige.

Do not use basin, geometry, or radius language as prestige metaphor. Use this prompt pair only where one exact cue would otherwise be allowed to certify a stronger local robustness claim.
```

**Continuation prompt**

```text
Continue the cue-neighborhood pass with one high-leverage cleanup or recovery claim only. Prefer the smallest packet that says what claim is being stress-tested, what seed cue currently looks decisive, what tiny nearby family of paraphrases, aliases, stylistic variants, or context stems belongs to the same sweep, what matched-fresh baseline keeps the neighborhood test honest, how much reactivation radius is tolerated, and what rollback, narrowing, widen-sweep, or quarantine consequence follows if the effect is only pointwise. Run `make lint` and package the release.
```


## `PP-0050` — Sweep two cue directions before you call the neighborhood round

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a cleanup, restart, relapse test, or portability result is being treated as locally robust after one narrow cue-family sweep.

Tasks
- name the cleanup or state claim being stress-tested,
- name the seed cue / local chart anchor / stressor starting point,
- name the compared cue directions / perturbation modes / neighborhood axes,
- name the matched step size / local sweep radius / fixed baseline,
- name the protected kernel / intended invariant readout / same-task comparison surface,
- name the tolerated directional asymmetry / local-shape budget,
- and state the rollback / narrow-claim / widen-sweep / quarantine consequence if one easy local direction is being mistaken for the whole neighborhood shape.

Do not use directional-neighborhood language as prestige metaphor. Use this prompt pair only where distinguishing one easy local axis from a genuinely shaped nearby neighborhood materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the directional-neighborhood pass with one high-leverage surface only. Prefer the smallest packet that says what local claim is being stress-tested, what seed cue anchored the sweep, what nearby perturbation directions were actually compared, what matched radius keeps them commensurate, what invariant readout was supposed to survive them, what directional-asymmetry budget applies, and what would force rollback, narrowing, widen-sweep, or quarantine if the neighborhood was only stable along one easy axis. Run lint and package the release.
```


## `PP-0051` — Factorize the directions before you call the mixture stable

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where several nearby directions or handles are each being treated as acceptable in isolation and therefore are at risk of being treated as safely composable.

Tasks
- name the cleanup or state claim being stress-tested,
- name the single-direction passes / constituent perturbation families / basis sweeps,
- name the mixed perturbation / composed cue / joint sweep,
- name the matched marginal step sizes / local mixing rule / fixed baseline,
- name the protected kernel / intended invariant readout / same-task comparison surface,
- name the tolerated cross-term residue / superposition budget,
- and state the rollback / factorize-claim / widen-mix-test / quarantine consequence if several marginal passes are being mistaken for honest local composition.

Do not use cross-term or superposition language as prestige metaphor. Use this prompt pair only where A passes and B passes but the archive still has not earned the stronger claim that A+B is locally safe, stable, or portable.
```

**Continuation prompt**

```text
Continue the mixed-direction pass with one high-leverage surface only. Prefer the smallest packet that says what claim is being stress-tested, which constituent directions passed alone, what mixed perturbation was actually tried, what local mixing rule keeps the marginal and mixed tests commensurate, what invariant readout was supposed to survive, what cross-term residue budget applies, and what would force factorization, narrowing, widen-mix-test, or quarantine if the mixture fails despite the marginal passes. Run lint and package the release.
```

## `PP-0052` — Hold the endpoint fixed before you call the route irrelevant

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a cleanup, restart, chart remap, or steering claim is being treated as if two interventions are equivalent mainly because they share one final cue or endpoint target.

Tasks
- name the cleanup or state claim being stress-tested,
- name the start surface / source chart / initial packet,
- name the compared interpolation path / ramp schedule / adaptive route family,
- name the matched endpoint target / final mixed cue / fixed actuation budget,
- name the protected kernel / pathwise invariant / same-task comparison surface,
- name the tolerated arc-vs-chord residue / endpoint-equivalence budget,
- and state the rollback / schedule-lock / restage / quarantine consequence if one shared endpoint is being mistaken for route-indifferent local control.

Do not use path, geodesic, or trajectory language as prestige metaphor. Use this prompt pair only where the archive would otherwise compare interventions mainly through their shared destination rather than through the route that reached it.
```

**Continuation prompt**

```text
Continue the interpolation-path pass with one high-leverage surface only. Prefer the smallest packet that says what claim is being stress-tested, what start surface anchored the comparison, what route family or ramp schedule actually reached the matched endpoint, what pathwise invariant was supposed to survive, what arc-vs-chord residue budget applies, and what would force rollback, schedule-lock, restage, or quarantine if one route fails despite sharing the same final cue. Run lint and package the release.
```


## `PP-0053` — Repeat the route before you call the result stable

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a cleanup, steering handle, chart remap, portability result, or other transformer-facing mechanism story is being treated as if one apparently successful rollout under a fixed visible protocol already counts as stable.

Tasks
- name the state claim being stress-tested,
- name the fixed prompt / route / control protocol / operational conditions,
- name the replicate bundle / repeated-inference family / decode regime,
- name the protected kernel / invariant readout / same-task success criterion,
- name the tolerated between-run dispersion / lucky-path budget,
- name the widen-bundle / lower-confidence / quarantine consequence,
- and state the quarantine consequence if the current move is only one vivid run, retry theater, or decode-regime luck.

Do not use stochastic, distribution, or kernel language as prestige metaphor. Use this prompt pair only where the archive would otherwise let one apparently fixed successful rollout stand in for stable continuation.
```

**Continuation prompt**

```text
Continue the replicate-bundle pass with one high-leverage surface only. Prefer the smallest packet that says what state claim is being stress-tested, what visible protocol was actually held fixed, what reruns belong to the same repeated-inference family, what invariant readout or same-task criterion was supposed to survive them, what between-run dispersion is tolerated, and what would force widen-bundle, lower-confidence, or quarantine if the result was only lucky. Run lint and package the release.
```

## `PP-0054` — Freeze one open-loop baseline before you call the policy adaptive

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a cleanup, restart, chart remap, or steering claim is being treated as if its gain came from adaptivity or feedback rather than from one fixed schedule alone.

Tasks
- name the cleanup or state claim being stress-tested,
- name the observation channel / checkpoint signal / mid-course readout,
- name the compared policy class / fixed open-loop schedule vs feedback-conditioned policy,
- name the matched endpoint target / actuation budget / compute budget,
- name the protected kernel / contingency invariant / same-task comparison surface,
- name the tolerated open-loop substitution gap / contingency budget,
- and state the rollback / freeze-policy / quarantine consequence if an adaptive-looking success is being mistaken for honest closed-loop advantage.

Do not use control, feedback, or policy language as prestige metaphor. Use this prompt pair only where an intermediate readout is actually allowed to change the next actuation and the archive would otherwise skip the matched open-loop comparator.
```

**Continuation prompt**

```text
Continue the feedback-policy pass with one high-leverage surface only. Prefer the smallest packet that says what claim is being stress-tested, what checkpoint signal was allowed to matter, what fixed open-loop baseline was actually compared, what policy branch or contingent update was allowed, what matched endpoint or budget stayed fixed, what open-loop substitution gap / contingency budget applies, and what would force rollback, freeze-policy, or quarantine if the adaptive story collapses under a fair open-loop comparison. Run lint and package the release.
```



## `PP-0055` — Name what the move learned before you call it a better controller

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a cleanup, restart, chart remap, or steering move is being treated as if it was simply a better controller even though part of its value may come from what it teaches the archive for later.

Tasks
- name the state claim or target objective being stress-tested,
- name the control action family / exploitation move / current actuation,
- name the epistemic dividend / information actually sought or acquired,
- name the compared policy class / exploitation-only baseline / no-learning baseline,
- name the matched task budget / actuation budget / horizon budget,
- name the protected kernel / same-task comparison surface / judged downstream advantage,
- name the tolerated exploration premium / dual-effect budget,
- and state the rollback / exploit-only fallback / quarantine consequence if the exploratory-looking gain is being mistaken for a purely better controller.

Do not use dual-control, exploration, or information-gain language as prestige metaphor. Use this prompt pair only where a current move seems load-bearing partly because it improved what later steps could know or choose, not only because it directly advanced the route.
```

**Continuation prompt**

```text
Continue the dual-effect pass with one high-leverage surface only. Prefer the smallest packet that says what claim is being stress-tested, what current actuation did now, what epistemic dividend it bought for later, what nearby exploitation-only baseline was actually compared, what matched task or horizon budget stayed fixed, what exploration premium / dual-effect budget applies, and what would force rollback, exploit-only fallback, or quarantine if the gain never repays its exploratory cost. Run lint and package the release.
```

## `PP-0056` — Name the reuse horizon before you call the carry learned

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a costly exploratory move, memory write, extracted tip, or compiled packet is being praised mainly because it seems helpful later.

Tasks
- name the state claim or target objective being stress-tested,
- name the upfront acquisition cost / exploratory move / learning move,
- name the carry object / stored tip / reusable skill / compiled packet,
- name the future reuse family / neighboring task class / deployment slice,
- name the compared one-shot baseline / no-reuse baseline / from-scratch baseline,
- name the matched horizon / task volume / compute budget,
- name the judged payback / reuse dividend / compiled-dividend budget,
- and state the rollback / one-shot demotion / quarantine consequence if the reusable-carry story is outrunning what the future reuse family actually repays.

Do not use memory, skill, compilation, or amortization language as prestige metaphor. Use this prompt pair only where the current story depends on the claim that some expensive move left behind reusable carry whose value appears across later neighboring tasks or branches.
```

**Continuation prompt**

```text
Continue the amortization pass with one high-leverage surface only. Prefer the smallest packet that says what was paid up front, what carry object survived, what nearby future reuse family was actually in scope, what one-shot or from-scratch baseline stayed nearby, what matched horizon or compute budget stayed fixed, what compiled-dividend budget applies, and what would force one-shot demotion, rollback, or quarantine if the gain never amortizes beyond the first vivid reuse. Run lint and package the release.
```

## `PP-0057` — Name the fit conditions before you reuse the carry

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a reusable skill, memory packet, plan template, or compiled carry is being reused beyond one vivid payoff.

Tasks
- name the state claim or target objective being stress-tested,
- name the candidate carry object / reusable skill / memory / plan template,
- name the applicability conditions / belief-state signature / domain-fit cue family,
- name the compared no-reuse baseline / gated baseline / alternative carry baseline,
- name the out-of-family stress slice / conflict case / neighboring non-fit family,
- name the matched task budget / context budget / compute budget,
- name the tolerated negative-transfer / misuse / conflict budget,
- and state the rollback / gate-closed / quarantine consequence if the reuse authority is outrunning what the fit conditions actually license.

Do not use reuse, skill, memory, or applicability language as prestige metaphor. Use this prompt pair only where the current story depends on the claim that a carry object should keep firing across neighboring tasks, branches, or deployment slices.
```

**Continuation prompt**

```text
Continue the applicability pass with one high-leverage surface only. Prefer the smallest packet that says what carry object is being reused, what fit signature licenses it now, what nearby non-fit slice stayed nearby, what no-reuse or gated baseline was actually compared, what matched task or context budget stayed fixed, what negative-transfer budget applies, and what would force gate closure, rollback, or quarantine if the packet is being overgeneralized beyond its real fit. Run lint and package the release.
```

## `PP-0058` — Name the tie set before you let one packet inherit the route

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where two or more reusable skills, memory packets, plan templates, or compiled carry objects remain simultaneously eligible after applicability gating.

Tasks
- name the state claim or target objective being stress-tested,
- name the candidate tie set / simultaneously eligible carry family,
- name the shared applicability gate / eligibility surface that kept them alive,
- name the arbitration rule / hierarchical router / confidence-aware selector,
- name the compared abstain / fallback / defer-to-evidence baseline,
- name the confusability slice / near-tie stress family / rival-eligible case,
- name the matched task budget / context budget / compute budget,
- name the tolerated misroute / tie-instability / confusability budget,
- and state the route-to-fallback / abstain / quarantine consequence if one vivid eligible packet is silently inheriting the route.

Do not use routing, arbitration, or expert language as prestige metaphor. Use this prompt pair only where several packets already appear individually eligible and the missing question is how one of them earned the next route.
```

**Continuation prompt**

```text
Continue the arbitration pass with one high-leverage surface only. Prefer the smallest packet that says what simultaneously eligible tie set stayed alive, what eligibility surface kept it alive, what selector or hierarchical router was allowed to choose among it, what abstain or fallback baseline stayed nearby, what confusability slice was actually checked, what matched task or context budget stayed fixed, what misroute or tie-instability budget applies, and what would force reroute, abstention, rollback, or quarantine if the current winner only looked obvious because the tie was never preserved. Run lint and package the release.
```



## `PP-0059` — Name the live head before you cite the surface

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a live working surface, release family, extracted packet, or public summary is being used both for ongoing continuation and later citation or replay.

Tasks
- name the surface lineage / family / stable id namespace,
- name the current operational head / live working tip,
- name the current citation head / frozen reference tip or explicit absence,
- name the current state class / working vs hold vs released vs frozen,
- name the durable status surface / register / ledger where that state lives,
- name the promotion or freeze gate / admission witness that moved authority,
- name the supersession edge / previous frozen head if any,
- and state the reopen / rollback / citation-warning consequence if a mutable head is being cited as though it were already frozen.

Do not use publication, provenance, or version-control language as prestige metaphor. Use this prompt pair only where one family already has a live working tip and the missing question is whether that same tip has also earned frozen public reference authority.
```

**Continuation prompt**

```text
Continue the head-register pass with one high-leverage surface only. Prefer the smallest packet that says what lineage is in play, what live head currently governs ordinary continuation, what citation head is actually frozen or explicitly absent, what status class currently applies, what durable ledger records that fact, what freeze gate moved authority, what supersession edge matters, and what warning, rollback, or reopen consequence follows if a moving head is being cited as though it were already the public surface. Run lint and package the release.
```


## `PP-0060` — Name the expected head before you inherit the judgment

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, replay verdict, review judgment, or canon move is being treated as grounded in current archive state.

Tasks
- name the judged move / continuation claim / active decision surface,
- name the expected basis / anchor revision / reviewed head,
- name the actual reread basis / loaded surfaces / observed head,
- name the session provenance / explicit reread vs copied summary vs nearby-session carry posture,
- name the basis state / current vs stale vs partial vs mismatched vs resynced (use `current` only when expected and observed basis still match exactly),
- name the basis-anchor precision / direct-underlier vs underlier-plus-wrapper vs wrapper-routed vs packet-only posture,
- name any basis-omission basis / why stronger underliers were not reread,
- and state the fail-closed repair / bounded reread vs rerequest vs hold vs recover-resync consequence if the move was grounded on the wrong basis.

Do not use concurrency, transaction, or compare-and-set language as prestige metaphor. Use this prompt pair only where a move is already claiming honest continuity from current archive state and the missing question is whether the judgment actually stayed scoped to the head or basis it claims to extend.
```

**Continuation prompt**

```text
Continue the basis-witness pass with one high-leverage surface only. Prefer the smallest packet that says what decision is being grounded, what head or anchor revision that move expected, what basis was actually reread, what same-session carry or copied-summary posture stayed in the loop, what basis-state classification currently applies, what basis-anchor precision attached to the decisive support, why any stronger underliers were not reread, and what reread, rerequest, hold, or recover-resync consequence follows if the present judgment silently inherited the wrong basis; never call the basis `current` when the expected and observed heads differ.
```

## `PP-0061` — Name the status lane before you cite the revision

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision-sized archive change is being treated as both an admitted move and a later referenceable artifact.

Tasks
- name the candidate or explicit absence / merely nearby surface,
- name the admitted decision / approval surface,
- name the execution surface / materialized artifact,
- name the frozen public / citation surface or explicit absence,
- name the durable status ledger / register / pointer relation where that mapping lives,
- and state the mismatch / drift / rollback / citation-warning consequence if one lively latest object is being asked to stand in for all those lanes at once.

Do not use workflow, release, or provenance language as prestige metaphor. Use this prompt pair only where DelayBasin already has a receipt, manifest, package, or frozen-head story in play and the missing question is which current surface actually occupies which lane.
```

**Continuation prompt**

```text
Continue the status-lane pass with one high-leverage surface only. Prefer the smallest packet that says what was merely nearby or absent, what surface actually admitted the change, what surface actually materialized the artifact, what surface is actually frozen enough to cite, what durable ledger records that mapping, and what warning, rollback, or reopen consequence follows if a later session silently collapses those lanes back into one latest-looking object. If the revision is counting now, carry that packet directly in `REVISION-RECEIPT.json`, keep it aligned with `SURFACE-STATUS.json`, run lint, and package the release.
```



## `PP-0062` — Name the active request before you inherit nearby authority

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, replay verdict, review judgment, archive query, or cross-datacube import is being treated as about one exact object, target lineage, or requested move.

Tasks
- name the active request / current ask / exact judged object / target lineage,
- name the review or mutation surface actually in scope,
- name the nearby ambient surfaces / roster-visible alternatives / excluded adjacent families,
- name the scope state / exact vs broadened vs ambiguous vs ambient vs rescoped,
- and state the fail-closed repair / narrow-scope vs rerequest vs hold vs recover-resync consequence if visible adjacency started widening the decision.

Do not use permission, governance, or least-privilege language as prestige metaphor. Use this prompt pair only where the archive is already working near one active request and the missing question is whether nearby visible surfaces silently inherited standing authority.
```

**Continuation prompt**

```text
Continue the scope-witness pass with one high-leverage surface only. Prefer the smallest packet that says what request is actually active, what exact target lineage is under judgment, what nearby surfaces stay explicitly out of scope, what scope-state classification currently applies, and what narrow-scope, rerequest, hold, or recover-resync consequence follows if adjacency silently widened the move. Run lint and package the release.
```


## `PP-0063` — Name the authorship lanes before one toolchain inherits all the authority

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, replay verdict, canon write, or packaged release could otherwise blur who or what proposed the move, who or what drafted it, what lane actually admitted it, what lane actually executed it, and what review or compensating control kept disagreement real.

Tasks
- name the initiating lane / request origin,
- name the draft-authorship posture / accepted-text lane,
- name the approval or admission lane / counted-decision surface,
- name the execution or materialization lane / packaging or edit surface,
- name the review or compensating-control lane,
- name the autonomy posture / human-piloted vs assisted vs approval-bounded vs bounded-autonomous classification,
- name the lane-collapse state / separated vs partially-collapsed vs collapsed-with-compensation,
- and state the fail-closed repair / ordinary-continuation vs record-compensating-control vs require-independent-review vs hold vs recover-resync consequence if one seat, one model, or one toolchain silently inherited all those roles.

Do not use governance, provenance, or role-separation language as prestige metaphor. Use this prompt pair only where DelayBasin is already doing collaborative human–LLM archive work and the missing question is which authority lanes were actually distinct, which were collapsed, and what compensating control or repair keeps the move honest.
```

**Continuation prompt**

```text
Continue the authorship-witness pass with one high-leverage surface only. Prefer the smallest packet that says what lane initiated the move, what lane drafted the accepted surface, what lane actually admitted it, what lane executed or packaged it, what review or compensating-control lane kept disagreement real, what autonomy posture currently applies, what collapse-state classification currently holds, and what record-compensating-control, require-independent-review, hold, or recover-resync consequence follows if those lanes collapsed too far. Run lint and package the release.
```


## `PP-0064` — Name the landing cue before you trust the latest path

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a future session, operator, or packaged bundle is expected to find the current archive tip by following a small cue family rather than by whole-tree browsing.

Tasks
- name the surface lineage / latest-path family,
- name the primary landing surface / first trusted cue,
- name the supporting durable cue set / agreeing latest-path surfaces,
- name the excluded stale / broken / overwritten / generic-success path family,
- name the cue state / fresh-aligned vs stale vs split-brain vs broken-jump vs overwritten,
- if the cue family changed or is about to change, name the prior relied-on cue family / documented startup promise,
- name the successor route / nearest safe reentry path,
- name the added burden / cue refresh vs light bridge vs duplicate-reread vs hard-restart consequence,
- and state the fail-closed repair / refresh-cues vs re-open-primary vs narrow-scope vs recover-resync consequence if the present landing only looks successful.

Do not use browser, navigation, or information-architecture language as prestige metaphor. Use this prompt pair only where DelayBasin already has several latest-looking surfaces and the missing question is which small cue family is actually trusted to reopen the current path.
```

**Continuation prompt**

```text
Continue the reentry-cue pass with one high-leverage landing family only. Prefer the smallest packet that says what lineage is in play, what first cue is actually trusted, what other durable cues must agree with it, what stale, broken, overwritten, or generic-success path family is explicitly excluded, what cue-state classification currently applies, and what refresh-cues, re-open-primary, narrow-scope, or recover-resync consequence follows if those cues do not honestly line up. Run lint and package the release.
```

## `PP-0065` — Name the live remainder before you call it handled

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, active request, or cross-datacube import leaves live remainder work unresolved but not dead.

Tasks
- name the blocked or handed-off objective / still-live candidate,
- name the current local owner / source surface / current lane,
- name the state / local vs queued vs handed-off vs blocked vs expired,
- name the blocker or boundary causing non-completion,
- name the next proof point / discharge surface / future receipt,
- name the receiving surface / follow-up owner / linked issue or queue entry if work moved out,
- and state the expiry / supersession / reclaim consequence if the remainder never matures.

Do not use workflow, queue, or issue-tracker language as prestige metaphor. Use this prompt pair only where the archive already narrowed, deferred, or handed off a live remainder and the missing question is whether that remainder still has an honest owner and discharge path.
```

**Continuation prompt**

```text
Continue the followthrough-witness pass with one high-leverage remainder only. Prefer the smallest packet that says what still-live objective remains, what current surface stopped owning it fully, what followthrough-state classification currently applies, what blocker or boundary caused the non-completion, what future receipt or proof point would discharge it, what receiving surface now carries it if it moved out, and what expiry, reclaim, or supersession consequence follows if it never matures. Run lint and package the release.
```

## `PP-0066` — Name the live assumption before it hardens into law

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, packet, or judged move still depends on a load-bearing assumption that has not yet become direct evidence or stable law.

Tasks
- name the assumption statement / live support condition,
- name the scope / decision family / surface family where it is being spent,
- name the supporting surfaces / current evidence family / local reason it is still tolerated,
- name the invalidation or expiry triggers / what changes would stop it from holding,
- name the assumption state / active vs discharged vs invalidated vs retired vs quarantined,
- and state the fail-closed repair / refresh-assumptions vs retest-and-shrink vs quarantine-or-retire vs hold vs recover-resync consequence.

Do not use assurance-case, proof-obligation, or evidence-debt language as prestige metaphor. Use this prompt pair only where the archive is actually spending a live assumption and the missing question is whether that assumption is explicit enough to stay honest under future reread.
```

**Continuation prompt**

```text
Continue the assumption-witness pass with one high-leverage live assumption only. Prefer the smallest packet that says what support condition is still being assumed, what scope it currently governs, what support family still keeps it tolerated, what change would invalidate it, what assumption-state classification currently applies, and what refresh, shrink, quarantine, hold, or recover-resync consequence follows if it stops holding. Run lint and package the release.
```



## `PP-0067` — Name the source datacubes before you inherit the import

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, canon ratchet, or cross-datacube import is being justified by neighboring archive pressure.

Tasks
- name the source datacubes / exact source surfaces,
- name the extracted pressure / specific lesson or warning,
- name the concrete local gap / why DelayBasin needs this now,
- name the bounded take / compact imported ratchet,
- name the explicit non-take / tempting neighboring machinery consciously left out,
- name the assimilation state / imported vs supporting-only vs deferred vs rejected vs retired,
- and state the fail-closed repair / narrow-import vs defer-import vs quarantine-or-retire vs hold vs recover-resync consequence if the comparative story is too vague to audit.

Do not use provenance, derivation, or cross-project language as prestige metaphor. Use this prompt pair only where neighboring datacubes materially shaped a local ratchet and the missing question is exactly what was imported from where, what was not imported, and how bounded assimilation stays public.
```

**Continuation prompt**

```text
Continue the foreign-pressure-witness pass with one high-leverage import only. Prefer the smallest packet that says which neighboring datacubes and exact source surfaces actually mattered, what concrete pressure they applied, what local gap made that pressure relevant, what compact take was admitted, what explicit non-take stayed out, what assimilation-state classification currently applies, and what narrow-import, defer-import, quarantine, hold, or recover-resync consequence follows if the lineage story becomes too vague to trust. Run lint and package the release.
```


## `PP-0068` — Name the closure reason before you call it no longer live

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a question, branch, assumption, import, or working gap is no longer honestly live.

Tasks
- name the closed object / exact target surfaces,
- name the prior live state / what kind of object it was,
- name the closure reason / what counted as enough to stop treating it as live,
- name the successor surface or explicit absence,
- name the reopen trigger / what future evidence would legitimately reactivate it,
- name the closure state / resolved vs superseded vs retired vs deprecated vs rejected,
- and state the fail-closed repair / reopen-via-successor vs recover-closure-basis vs quarantine-or-retire vs hold vs recover-resync consequence.

Do not use decision, closure, or deprecation language as prestige metaphor. Use this prompt pair only where the archive is actually establishing that something stopped being live and the missing question is whether that closure is explicit enough to stay honest under later reread.
```

**Continuation prompt**

```text
Continue the resolution-witness pass with one high-leverage closure only. Prefer the smallest packet that says what exact object stopped being live, what prior state it had, what closure reason counted, what successor surface inherited authority if any, what future evidence would reopen it, what closure-state classification currently applies, and what reopen-via-successor, recover-closure-basis, quarantine, hold, or recover-resync consequence follows if the closure story becomes too vague to trust. Run lint and package the release.
```


## `PP-0069` — Name the missing support before you inherit the claim

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision, packet, or canon move is still being tolerated even though some decisive support is still missing.

Tasks
- name the target claim or surface / what is being asked to carry authority,
- name the missing support / undecided evidence or proof still owed,
- name the current support / why the move is tolerated for now,
- name the discharge path / evidence artifact / future proof that would retire the debt,
- name the obligation state / open vs staged vs satisfied vs waived vs retired,
- and state the fail-closed repair / narrow-claim vs hold-via-followthrough vs quarantine-or-retire vs refresh-support vs recover-resync consequence.

Do not use proof, assurance, or evidence-debt language as prestige metaphor. Use this prompt pair only where the archive is actually keeping a move live under bounded missing support and the missing question is what is still owed before that move should inherit stronger authority.
```

**Continuation prompt**

```text
Continue the obligation-witness pass with one high-leverage support debt only. Prefer the smallest packet that says what target surface is still carrying authority, what support is still missing, what support family keeps the move tolerated for now, what discharge path would actually retire the debt, what obligation-state classification currently applies, and what narrow-claim, hold-via-followthrough, quarantine, refresh-support, or recover-resync consequence follows if the missing support never arrives. Run lint and package the release.
```

Use `docs/10-method/obligation-packets-waivers-remediation-expiry-and-overflow-tests.md` when the family needs a compact successor surface.


## `PP-0070` — Name the allowed tokens before you compare the state

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a durable witness, ledger, or receipt field materially depends on a small public state token.

Tasks
- name the state family / governed field family,
- name the allowed tokens / stable public labels,
- name the target surfaces / ledgers / receipt fields governed by that family,
- name the excluded near-synonyms / drift temptations / non-controlled prose family,
- name the comparability budget / how much surrounding prose can vary while the token still stays comparable,
- and state the extend-registry / narrow-family / fail-closed-on-drift consequence.

Do not use ontology, taxonomy, or standards language as prestige metaphor. Use this prompt pair only where DelayBasin is already comparing compact public state tokens and the missing question is whether those tokens are controlled enough to stay honest across later revisions.
```

**Continuation prompt**

```text
Continue the witness-vocabulary pass with one high-leverage state family only. Prefer the smallest packet that says what family is controlled, what exact tokens are allowed, what surfaces that family governs, what near-synonyms stay explicitly out, what comparability budget currently applies, and what registry-extension, narrowing, or fail-closed consequence follows if a later revision wants a new token. Use `docs/10-method/public-state-packets-discoverability-exclusions-and-overflow-tests.md` when the family needs a compact successor surface. Run lint and package the release.
```



## `PP-0071` — Name the reviewed datacubes before you inherit the comparison

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where a revision materially depended on comparing several neighboring datacubes rather than on one isolated import pressure.

Tasks
- name the reviewed datacubes / exact source surfaces,
- name the pattern or warning under review,
- name the disposition / imported vs supporting-only vs deferred vs rejected vs retired,
- name the concrete local gap / why this comparison mattered now,
- name the bounded take / compact admitted ratchet if any,
- name the explicit non-take / tempting neighboring machinery consciously left out,
- name the anchor surfaces / where the admitted result now lives,
- name the open transfer question / what remains live after the pass,
- and state the fail-closed repair / rereview vs narrow-import vs retire-ledger-entry vs recover-resync consequence if the comparison memory is too vague to trust.

Do not use cross-project, benchmarking, or inspiration language as prestige metaphor. Use this prompt pair only where DelayBasin actually reviewed several neighboring datacubes and the missing question is what the whole comparison pass already decided, not just why one import landed.
```

**Continuation prompt**

```text
Continue the transfer-ledger pass with one high-leverage comparison outcome only. Prefer the smallest packet that says which datacubes and exact source surfaces were reviewed, what pattern or warning was under review, what disposition currently applies, what concrete local gap made the comparison matter, what compact take if any was admitted, what explicit non-take stayed out, where the admitted result now lives, what open transfer question remains, and what rereview, narrow-import, ledger-retire, or recover-resync consequence follows if the comparison memory becomes too vague to trust. Use `docs/10-method/transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md` when the family needs a compact successor surface. Run lint and package the release.
```

## `PP-0072` — Name the primary next step before you trust the discharge prose

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any durable queue or ledger item that already carries state plus discharge prose.

Tasks
- name the action lane / primary next-step class,
- name the governed discharge surfaces / durable queues / ledgers,
- name the admitted lane tokens if the family changes,
- state how the lane differs from the current state token,
- state the comparability budget / how much discharge prose may vary while the lane still stays comparable,
- and state the fail-closed repair / narrow-lane vs extend-registry vs retire-lane consequence if the routing class is too vague to trust.

Do not import a broader queue-code, issue-taxonomy, or reason-code court unless repeated collisions show the small action-lane family is no longer enough.
```

**Continuation prompt**

```text
Continue the action-lane pass with one high-leverage routing clarification only. Prefer the smallest packet that says what durable item is under review, what primary next-step class it is actually waiting for, whether the existing admitted `action_lane` family is already enough or a new token is honestly needed, how that lane differs from current state and gate class, what surrounding prose still carries the nuanced threshold, and what narrow, retire, or extend-registry consequence follows if the lane no longer stays honest. Use `docs/10-method/action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md` when the family needs a compact successor surface. Run lint and package the release.
```


## `PP-0073` — Name the startup wrapper before you inherit its authority

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether future careful passes still need one smaller derivative startup wrapper.

Tasks
- name the read-first surfaces / shortest honest startup path,
- name the non-negotiables / what future passes must not silently break,
- name the command posture / what checks to prefer before claiming admissibility,
- name the good-change shapes / what kinds of revisions are usually worth making,
- if the startup path changed or is about to change, name the prior relied-on startup path / documented startup promise,
- name the successor route / nearest safe reentry path,
- name the added burden / cue refresh vs light bridge vs duplicate-reread vs hard-restart consequence,
- state what the wrapper must not replace,
- and state the fail-closed repair / narrow-wrapper vs retire-wrapper vs push-law-back-into-canon consequence if the wrapper starts carrying too much authority.

Do not use bootstrap, onboarding, or agent language as prestige metaphor. Use this prompt pair only where DelayBasin already has richer canon and the missing question is whether one smaller derivative wrapper would reduce startup error without becoming a shadow constitution.
```

**Continuation prompt**

```text
Continue the derivative-startup-wrapper pass with one high-leverage reentry clarification only. Prefer the smallest packet that says what future careful passes should read first, what they must not silently break, what command posture should govern admissibility, what kinds of changes usually count as good here, what the wrapper must not replace, and what narrowing, retirement, or canon-pushback consequence follows if the wrapper starts carrying too much authority. Run lint and package the release.
```


## `PP-0074` — Name the future trigger before you trust the discharge prose

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any durable live item where state and primary next-step class are already explicit but the kind of future event that would actually change the item still lives mostly in discharge prose.

Tasks
- name the gate class / future-trigger kind,
- name the governed live-item surfaces / durable queues / ledgers,
- name the admitted token family, including whether any row is really waiting on a scheduled window rather than a generic repeat pass,
- name the relation between gate class and existing state plus action lane,
- name the comparability budget and fail-closed extension rule,
- and state the rollback or quarantine consequence if the supposed trigger kind is only local phrasing, blocker folklore, or latent controller inflation.

Do not use gate-class language as prestige metaphor. Use this prompt pair only where preserving the kind of future event materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the gate-class pass with one high-leverage discharge-bearing ledger or queue surface only. Prefer the smallest packet that says what future-trigger kind is actually load-bearing, what durable rows it governs, what compact token family stays admitted, including whether `scheduled-window` is the honest trigger kind, how the trigger class differs from current state and action lane, what comparability budget keeps it small, what extension rule applies if the family drifts, and what would force rollback or quarantine if the trigger class was only prose decoration. Run lint and package the release.
```


## `PP-0076` — Name the coverage before you trust the green wrapper

**Request prompt**

```text
Read the latest DelayBasin archive and inspect any place where `make lint`, a checked wrapper, or a compact validation map is being treated as load-bearing admission evidence.

Tasks
- name the major command surfaces,
- name the direct generated outputs,
- name the broad validation families behind the wrapper,
- name the governing surface hints a later operator should reopen,
- name the explicit coverage-honesty / what the compact map does not claim,
- and state the fail-closed repair / narrow-map vs regenerate-via-generator vs reopen-governing-surfaces vs quarantine-or-retire vs recover-resync consequence if the coverage story becomes too vague to trust.

Do not use validation, assurance, or lint language as prestige metaphor. Use this prompt pair only where the archive is actually trying to keep a checked command surface inspectable without mistaking a compact map for a theorem-complete proof graph or workflow-state machine.
```

**Continuation prompt**

```text
Continue the validation-index pass with one high-leverage discovery repair only. Prefer the smallest packet that says what major commands exist, what direct outputs they refresh, what broad validation families sit behind the wrapper, what governing surfaces still own the stronger semantics, what explicit non-claim keeps the map honest, and what narrow-map, regenerate, reopen-governing-surfaces, quarantine, or recover-resync consequence follows if the compact coverage story becomes too vague to trust. Run lint and package the release.
```


## `PP-0075` — Name the selected frontier before you inherit the handoff card

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether future careful passes still need one smaller selected-focus frontier ticket.

Tasks
- name the selected live focus / what source-backed item the ticket is actually pointing at,
- name the governing source surface / why that focus is the one being handed off,
- name the selection policy / what compact rule selected it rather than ambient vividness,
- name the inherited current posture / what must come from `SURFACE-STATUS.json` rather than ticket folklore,
- name the background continuity rows / what obligation or cooling retrospective still belongs nearby,
- name the reentry anchors / where to reopen canon before treating the card as stronger than a derivative aid,
- state what the ticket must not replace,
- and state the fail-closed repair / narrow-ticket vs retire-ticket vs push-selection-back-into-canon consequence if the handoff card starts behaving like a scheduler, queue court, or new authority surface.

Do not use frontier-ticket language as prestige metaphor. Use this prompt pair only where DelayBasin already has richer canon and compact packets, and the missing question is whether one selected-focus card would reduce reentry scan cost without becoming a priority constitution.
```

**Continuation prompt**

```text
Continue the frontier-ticket pass with one high-leverage selected-focus clarification only. Prefer the smallest packet that says what live focus is actually being handed off, what source surface governs that focus, what compact rule selected it, what posture it must inherit rather than invent, what tiny continuity background still belongs nearby, what canon surfaces still outrank the handoff card, and what narrowing, retirement, or canon-pushback consequence follows if the ticket starts carrying scheduler or queue-court authority. Run lint and package the release.
```


## `PP-0077` — Name the anchor and delta before you trust the packet

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one exact derivative innovation packet.

Tasks
- name the anchor revision / expected head / observed head,
- name the actual local correction,
- name the exact changed-surface list or its receipt-backed pointer,
- name the reread and reconciliation surfaces plus continuation mode,
- state what the packet must not replace,
- and state the fail-closed repair / narrow-packet vs reopen-receipt vs regenerate-from-source-surfaces vs quarantine-or-retire vs recover-resync consequence if the packet starts behaving like recap authority, summary glow, or a substitute for `REVISION-RECEIPT.json`.

Do not use innovation-packet language as prestige metaphor. Use this prompt pair only where shared public state already exists and the missing question is whether one exact current update card would reduce anchor-and-delta reconstruction without becoming a recap court.
```

**Continuation prompt**

```text
Continue the current-innovation-packet pass with one high-leverage exact-delta clarification only. Prefer the smallest packet that says what prior revision or expected head the current update is anchored to, what real local correction is being transmitted, what receipt-backed exact surface list or pointer stays honest, what reread and reconciliation surfaces still govern recovery, what continuation mode applies, what canon surfaces still outrank the packet, and what narrowing, regeneration, reopen-receipt, quarantine, or recover-resync consequence follows if the packet starts carrying recap or summary-authority weight. Run lint and package the release.
```


## PP-0078 — Name the compact family before you trust the bundle

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact closed-family card for its operator-facing derivative aids.

Tasks
- name the candidate member surfaces,
- name each member's local role and stronger underliers,
- say which members are generated versus authored,
- say what same-revision attachment rule keeps the family honest,
- say what the bundle card must not replace,
- and state the fail-closed repair / narrow-family vs regenerate-from-underliers vs reopen-canon vs quarantine-or-retire consequence if the bundle starts behaving like a bundle board, porch registry, or derivative-authority scaffold.

Do not use bundle language as prestige metaphor. Use this prompt pair only where several compact derivative aids already exist and the missing question is whether one closed family-status card would reduce family-boundary reconstruction without becoming new governance.
```

**Continuation prompt**

```text
Continue the compact-surface-bundle pass with one high-leverage family-boundary clarification only. Prefer the smallest card that says which compact operator-facing derivative aids belong to the current bundle, what each one is for, what stronger underliers still govern them, which members are generated versus authored, what same-revision attachment rule keeps the family honest, what canon surfaces still outrank the card, and what narrowing, regeneration, reopen-canon, quarantine, or recover-resync consequence follows if the card starts carrying bundle-board or porch-registry weight. Run lint and package the release.
```


Use `docs/10-method/exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md` when the live question is whether neighboring waiver, mitigation, suppression, or expiry prose is being mistaken for a current honest waiver.

## PP-0079 — Name the current bundle stem before you trust the receipt

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether terse receipt keys are still honestly current for the packaged revision.

Tasks
- name the current packaged bundle filename,
- name the manifest timestamp token and the receipt created-at token,
- name the bundle-stem suffix relation / how summary highlight and codename actually fit the admitted slug,
- name the current comparison ids when comparison memory is part of the receipt,
- name the change-anchor surface those terse keys are supposed to summarize,
- state what the witness must not replace,
- and state the fail-closed repair / refresh-receipt-keys vs regenerate-package-identity vs reopen-manifest-ledgers vs recover-resync consequence if the short keys drift.

Do not use bundle-stem or freshness language as prestige metaphor. Use this prompt pair only where a current packaged revision already exists and the missing question is whether terse receipt keys still belong to that revision rather than stale carryforward residue.
```

**Continuation prompt**

```text
Continue the receipt-freshness pass with one high-leverage exactness repair only. Prefer the smallest witness that says what packaged bundle is current, what manifest timestamp and receipt timestamp should agree, how summary highlight and codename actually attach to the admitted bundle stem, what comparison ids still belong to this revision if any, what stronger surfaces still outrank the witness, and what refresh, regenerate, reopen-manifest-ledgers, or recover-resync consequence follows if the terse receipt keys drift. Run lint and package the release.
```

## PP-0080 — Name the expiry and aggregate effect before you call it waived

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact exception witness for honest temporary waiver.

Tasks
- name the governed obligation row,
- name the exception basis / whether this is accepted risk, mitigated-neighbor rationale, suppressed-only aggregate posture, or expired residue,
- name the honor window / explicit expiry or renewal expectation,
- name the aggregate effect / whether only score, listing, or default visibility changes,
- state the record-keeping truth / whether the object can persist after it stops being honored,
- state what the witness must not replace,
- and state the fail-closed repair / revert-to-open vs refresh-waiver vs quarantine-or-retire consequence if nearby mitigation, suppression, or expiry prose starts acting like a current honest waiver.

Do not use waiver language as prestige metaphor. Use this prompt pair only where a durable obligation row already exists and the missing question is whether one small exception witness would keep temporary tolerance honest without promoting a larger renewal board.
```

**Continuation prompt**

```text
Continue the exception-witness pass with one high-leverage waiver-honesty clarification only. Prefer the smallest witness that says what obligation row is supposedly tolerated, why that tolerance exists, how long it is honored or when it must be renewed, whether any effect is only aggregate hiding or score exclusion, what record-keeping truth survives after honor ends, what stronger surfaces still outrank the witness, and what revert, refresh, quarantine, or recover-resync consequence follows if mitigation, suppression, or expiry prose starts carrying live waiver authority. Run lint and package the release.
```

Use `docs/10-method/renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md` when the live question is whether a current waiver claim points to a fresh renewal act or only to copied-forward residue.

## PP-0081 — Name the fresh act before you call it renewed

**Request prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact renewal witness for honest waiver refresh.

Tasks
- name the governed obligation row,
- name the prior exception witness and prior honor window,
- name the renewal act / explicit approving or update surface if any,
- name the current honor window,
- name the renewal state / whether this is fresh-renewal, copied-forward, expired-residue, or basis-changed,
- name the aggregate continuity / whether the effect really stayed the same,
- state what the witness must not replace,
- and state the fail-closed repair / revert-to-open vs issue-new-exception-witness vs quarantine-broadened-renewal consequence if the present claim only inherits copied-forward timestamps or residue.

Do not use renewal language as prestige metaphor. Use this prompt pair only where a durable obligation row and exception witness already exist and the missing question is whether one small renewal witness would keep fresh authority distinct from stale carryforward without promoting a broader reapproval board.
```

**Continuation prompt**

```text
Continue the renewal-witness pass with one high-leverage fresh-act clarification only. Prefer the smallest witness that says what obligation row is supposedly still waived, what prior exception window existed, what new approval or update act now exists if any, what current honor window follows, what renewal_state is honest, whether the aggregate effect stayed the same or changed, what stronger surfaces still outrank the witness, and what revert, issue-new-exception-witness, quarantine, or recover-resync consequence follows if the current claim is only copied-forward residue. Run lint and package the release.
```

Use `docs/10-method/renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md` when the live question is whether a fresh renewal stayed local to the same governed row/effect or is being silently borrowed by a broader scope, neighboring row, or changed effect.

## PP-0082 — Name the local target before you call it the same renewal

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact renewal-scope witness for honest local refresh.

Focus only on whether a fresh renewal act stayed attached to the same governed row, selector, environment, and aggregate effect.

If yes, preserve exactly one small witness that:
- names the governed obligation row,
- names the prior local target / scope / selector / effect,
- names the current refreshed target / scope / selector / effect,
- names the renewal_scope_state / whether this is local-refresh, broadened-carryover, spillover, or effect-drift,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-local vs split-row vs issue-new-exception-witness vs quarantine-scope-governance consequence if the present claim is silently borrowing freshness beyond the renewed target.

Do not use renewal-scope language as prestige metaphor. Use this prompt pair only where a durable obligation row, exception witness, and renewal witness already exist and the missing question is whether one small local-refresh boundary card would keep scope honesty public without promoting a broader scope court.
```

**Continuation prompt**

```text
Continue the renewal-scope pass with one high-leverage local-target clarification only. Prefer the smallest witness that says what governed row is supposedly still under renewed authority, what the prior local target was, what the current refreshed target is, what renewal_scope_state is honest, whether the aggregate effect stayed the same, what stronger surfaces still outrank the witness, and what keep-local, split-row, issue-new-exception-witness, quarantine, or recover-resync consequence follows if the current claim spills beyond the renewed target. Run lint and package the release.
```

Use `docs/10-method/selector-witnesses-realized-membership-and-coverage-drift.md` when the live question is whether the same selector handle or label still governs the same realized members or is only borrowing continuity from unchanged naming.

## PP-0083 — Name the realized members before you trust the same selector

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact selector witness for honest realized coverage.

Focus only on whether the same selector handle, label, tag, segment, or rule name still governs the same realized members across time.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the selector handle / selector text family,
- names the prior realized coverage slice,
- names the current realized coverage slice,
- names the selector_membership_state / whether this is stable-coverage, expanded-coverage, narrowed-coverage, or recomposed-coverage,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-witness vs quarantine-selector-governance consequence if the present continuity claim is only label continuity.

Do not use selector language as prestige metaphor. Use this prompt pair only where a durable row already depends on the same selector handle sounding continuous and the missing question is whether one small realized-coverage card would keep label continuity distinct from changed membership without promoting a broader selector court.
```

**Continuation prompt**

```text
Continue the selector-witness pass with one high-leverage realized-coverage clarification only. Prefer the smallest witness that says what governed row is still being justified, what selector handle is supposedly unchanged, what the prior realized coverage slice was, what the current realized coverage slice is, what selector_membership_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-selector-witness, quarantine, or recover-resync consequence follows if the current claim is only label continuity over changed coverage. Run lint and package the release.
```



Use `docs/10-method/selector-provenance-witnesses-direct-rules-inherited-bindings-and-synced-membership.md` when the live question is whether current selector coverage still comes from direct local rule text, inherited bindings, or synced membership rather than just the same label.

## `PP-0084` — Name the rule source before you trust the same selector

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact selector-provenance witness for honest rule-source continuity.

Focus only on whether the present coverage is still being produced by the same direct selector rule, inherited binding, or synced membership source.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the selector handle / rule family,
- names the prior provenance posture / rule source,
- names the current provenance posture / rule source,
- names the selector_provenance_state / whether this is direct-rule, inherited-binding, synced-membership, or mixed-provenance,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-provenance-witness vs quarantine-selector-governance consequence if the present continuity claim is only same-handle continuity over changed provenance.

Do not use selector provenance as a governance metaphor. Use this prompt pair only where a durable row already depends on the same selector still sounding current and the missing question is whether one small rule-source card would keep direct local authority distinct from inherited or externally synced coverage without promoting a broader selector lineage court.
```

**Continuation prompt**

```text
Continue the selector-provenance pass with one high-leverage rule-source clarification only. Prefer the smallest witness that says what governed row is still being justified, what selector handle is supposedly unchanged, what the prior provenance posture was, what the current provenance posture is, what selector_provenance_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-selector-provenance-witness, quarantine, or recover-resync consequence follows if the current claim is only same-handle continuity over changed provenance. Run lint and package the release.
```


Use `docs/10-method/selector-freshness-witnesses-live-provenance-sync-lag-and-ancestor-residue.md` when the live question is whether inherited or synced selector provenance is still current enough to count as live authority now rather than just the right provenance label.

## `PP-0085` — Name the freshness evidence before you trust the same selector

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact selector-freshness witness for honest live-authority continuity.

Focus only on whether inherited or synced selector provenance is still current enough to count as present authority now.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the selector handle / provenance path,
- names the prior freshness evidence,
- names the current freshness evidence,
- names the selector_freshness_state / whether this is live-provenance, sync-lag, ancestor-residue, or mixed-freshness,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-freshness-witness vs quarantine-selector-freshness-governance consequence if the present continuity claim is only last-known-good selector authority.

Do not use selector freshness as a governance metaphor. Use this prompt pair only where a durable row already depends on inherited or synced selector provenance sounding current and the missing question is whether one small freshness card would keep live authority distinct from lagged mirrors or ancestor residue without promoting a broader selector-freshness court.
```

**Continuation prompt**

```text
Continue the selector-freshness pass with one high-leverage live-authority clarification only. Prefer the smallest witness that says what governed row is still being justified, what selector handle or provenance path is supposedly still current, what the prior freshness evidence was, what the current freshness evidence is, what selector_freshness_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-selector-freshness-witness, quarantine, or recover-resync consequence follows if the current claim is only last-known-good selector authority over stale provenance. Run lint and package the release.
```


Use `docs/10-method/selector-enforcement-witnesses-execution-authority-grandfathered-placement-and-eviction-gates.md` when the live question is whether current selector truth is still enforced on already-bound objects now or only gates future placement, leaving grandfathered runtime residue behind.

## `PP-0086` — Name the enforcement posture before you trust the same selector

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact selector-enforcement witness for honest runtime-authority continuity.

Focus only on whether current selector truth is actually enforced on already-bound objects now.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the selector handle / admission path / taint or affinity family,
- names the prior enforcement posture,
- names the current enforcement posture,
- names the selector_enforcement_state / whether this is execution-enforced, admission-only, grandfathered-residue, or mixed-enforcement,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-enforcement-witness vs quarantine-selector-enforcement-governance consequence if the present continuity claim is only current selector truth over runtime residue.

Do not use selector enforcement as a governance metaphor. Use this prompt pair only where a durable row already depends on selector freshness sounding like current runtime authority and the missing question is whether one small enforcement card would keep execution-time control distinct from placement-time history without promoting a broader selector-enforcement court.
```

**Continuation prompt**

```text
Continue the selector-enforcement pass with one high-leverage runtime-authority clarification only. Prefer the smallest witness that says what governed row is still being justified, what selector handle, admission path, or taint family is supposedly still current, what the prior enforcement posture was, what the current enforcement posture is, what selector_enforcement_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-selector-enforcement-witness, quarantine, or recover-resync consequence follows if the current claim is only schedule-time continuity over grandfathered runtime residue. Run lint and package the release.
```


Use `docs/10-method/enforcement-regime-witnesses-bootstrap-only-gating-continuous-enforcement-and-dry-run-rehearsal.md` when the live question is whether a current gate or controller only mattered at startup or admission, keeps policing runtime conditions continuously, or is only rehearsing impact.

## `PP-0087` — Name the regime class before you trust the runtime guarantee

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact enforcement-regime witness for honest runtime-guarantee continuity.

Focus only on whether the live rule or controller is bootstrap-only, continuously enforced, dry-run only, or mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the rule handle / gate family / controller path,
- names the prior regime evidence,
- names the current regime evidence,
- names the enforcement_regime_state / whether this is bootstrap-only, continuous-enforcement, dry-run-only, or mixed-regime,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-enforcement-regime-witness vs quarantine-regime-governance consequence if the present continuity claim is only bootstrap success or dry-run rehearsal.

Do not use enforcement regime as a governance metaphor. Use this prompt pair only where a durable row already depends on a current runtime guarantee sounding live and the missing question is whether one small regime card would keep startup-only, admission-only, dry-run, and continuous runtime maintenance distinct without promoting a broader regime court.
```

**Continuation prompt**

```text
Continue the enforcement-regime pass with one high-leverage regime clarification only. Prefer the smallest witness that says what governed row is still being justified, what rule or controller path is supposedly unchanged, what the prior regime evidence was, what the current regime evidence is, what enforcement_regime_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-enforcement-regime-witness, quarantine, or recover-resync consequence follows if the current claim is only bootstrap success, request-time policy, or dry-run rehearsal rather than a continuously maintained runtime guarantee. Run lint and package the release.
```


Use `docs/10-method/response-witnesses-monitoring-availability-withdrawal-local-remediation-and-runtime-eviction.md` when the live question is what a still-monitored condition actually triggers once it fails: report-only observation, softer availability withdrawal, in-place remediation, runtime eviction, or an honest mixture.

## `PP-0088` — Name the response class before you trust the same monitoring

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact response witness for honest runtime-consequence continuity.

Focus only on what a live monitored condition actually triggers once it fails.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the monitor / controller / response path,
- names the prior response evidence,
- names the current response evidence,
- names the response_state / whether this is monitor-only, availability-withdrawal, local-remediation, runtime-eviction, or mixed-response,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-response-witness vs quarantine-response-governance consequence if the present continuity claim is only monitoring or advisory escalation rather than equivalent runtime action.

Do not use response class as a governance metaphor. Use this prompt pair only where a durable row already depends on continuous monitoring sounding like a known runtime consequence and the missing question is whether one small response card would keep watch-only monitoring, softer withdrawal, in-place remediation, and eviction distinct without promoting a broader response court.
```

**Continuation prompt**

```text
Continue the response-witness pass with one high-leverage consequence clarification only. Prefer the smallest witness that says what governed row is still being justified, what monitor, controller, or response path is supposedly unchanged, what the prior response evidence was, what the current response evidence is, what response_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-response-witness, quarantine, or recover-resync consequence follows if the current claim is only watch-only monitoring, availability withdrawal, or advisory GPU health reporting rather than equivalent restart or eviction authority. Run lint and package the release.
```


Use `docs/10-method/repair-scope-witnesses-in-place-repair-substrate-reset-and-workload-replacement.md` when the live question is how far recovery had to reach once a response path fired: the same running object repaired in place, the surrounding substrate reset or rebooted, a new workload object replaced the old one, or an honest mixture.

## `PP-0089` — Name the repair scope before you trust the same recovery

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact repair-scope witness for honest recovery-boundary continuity.

Focus only on how far recovery had to reach once some active response path fired.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the repair / controller / recovery path,
- names the prior repair-scope evidence,
- names the current repair-scope evidence,
- names the repair_scope_state / whether this is in-place-repair, substrate-reset, workload-replacement, or mixed-repair-scope,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-repair-scope-witness vs quarantine-repair-governance consequence if the present continuity claim only supports in-place repair, substrate reset, or workload replacement rather than same-object recovery.

Do not use repair scope as a governance metaphor. Use this prompt pair only where a durable row already depends on recovery-sounding continuity and the missing question is whether one small repair-boundary card would keep in-place restart, substrate reset or reboot, and workload replacement distinct without promoting a broader repair court.
```

**Continuation prompt**

```text
Continue the repair-scope pass with one high-leverage recovery-boundary clarification only. Prefer the smallest witness that says what governed row is still being justified, what repair, controller, or recovery path is supposedly unchanged, what the prior repair-scope evidence was, what the current repair-scope evidence is, what repair_scope_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-repair-scope-witness, quarantine, or recover-resync consequence follows if the current claim is only an in-place restart, a substrate reset or reboot, or workload replacement rather than the same recovery scope. Run lint and package the release.
```

Use `docs/10-method/recovery-loss-witnesses-state-preserving-repair-checkpoint-resume-and-full-replay.md` when the live question is how much prior state actually survived recovery: the current path preserved live runtime state, resumed from a saved checkpoint, replayed from the beginning, or honestly mixed those cases.

## `PP-0090` — Name the recovery loss before you trust resumed continuity

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact recovery-loss witness for honest state-survival continuity.

Focus only on how much prior working state survived once some recovery path happened.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the recovery / checkpoint / resume path,
- names the prior recovery-loss evidence,
- names the current recovery-loss evidence,
- names the recovery_loss_state / whether this is state-preserving, checkpoint-resume, full-replay, or mixed-recovery-loss,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-loss-witness vs quarantine-recovery-governance consequence if the present continuity claim only supports checkpoint resume or full replay rather than preserved live state.

Do not use recovery loss as a governance metaphor. Use this prompt pair only where a durable row already depends on recovery-sounding continuity and the missing question is whether one small state-survival card would keep preserved runtime state, checkpoint resume, and replay distinct without promoting a broader continuity court.
```

**Continuation prompt**

```text
Continue the recovery-loss pass with one high-leverage state-survival clarification only. Prefer the smallest witness that says what governed row is still being justified, what recovery, checkpoint, or resume path is supposedly unchanged, what the prior recovery-loss evidence was, what the current recovery-loss evidence is, what recovery_loss_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-recovery-loss-witness, quarantine, or recover-resync consequence follows if the current claim is only checkpoint resume or replay rather than preserved live state. Run lint and package the release.
```


Use `docs/10-method/recovery-anchor-witnesses-self-lineage-checkpoints-imported-seeds-converted-checkpoints-and-migrated-runtime-images.md` when the live question is what resumed state is actually anchored to: the same run's own checkpoint lineage, a supplied seed artifact, a converted checkpoint, a migrated runtime image, or an honest mixture.

## `PP-0091` — Name the recovery anchor before you trust resumed lineage

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact recovery-anchor witness for honest resumed-lineage continuity.

Focus only on what the resumed state is actually anchored to.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the checkpoint / restore / migration path,
- names the prior recovery-anchor evidence,
- names the current recovery-anchor evidence,
- names the recovery_anchor_state / whether this is self-lineage-checkpoint, imported-seed, converted-checkpoint, migrated-runtime-image, or mixed-recovery-anchor,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-anchor-witness vs quarantine-recovery-anchor-governance consequence if the present continuity claim only supports an imported, converted, or migrated anchor rather than the same run's own checkpoint lineage.

Do not use recovery anchor as a governance metaphor. Use this prompt pair only where a durable row already depends on resumed work sounding like the same lineage and the missing question is whether one small anchor card would keep same-lineage checkpoints, imported seeds, converted checkpoints, and migrated runtime images distinct without promoting a broader recovery-anchor court.
```

**Continuation prompt**

```text
Continue the recovery-anchor pass with one high-leverage lineage-anchor clarification only. Prefer the smallest witness that says what governed row is still being justified, what checkpoint, restore, or migration path is supposedly unchanged, what the prior recovery-anchor evidence was, what the current recovery-anchor evidence is, what recovery_anchor_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-recovery-anchor-witness, quarantine, or recover-resync consequence follows if the current claim is only an imported seed, a converted checkpoint, or a migrated runtime image rather than the same run's own checkpoint lineage. Run lint and package the release.
```

Use `docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md` when the live question is whether a restore is still the interrupted run continuing, a checkpoint-forked clone, a sandbox branch, or an honest mixture.

## `PP-0092` — Name whether a restore continues the run or starts a branch

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact recovery-identity witness for honest restored-lineage continuity.

Focus only on whether the restored lineage is still the same interrupted run continuing or has become a clone or sandbox branch.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the interruption / checkpoint / restore path,
- names the prior recovery-identity evidence,
- names the current recovery-identity evidence,
- names the recovery_identity_state / whether this is continuing-resume, checkpoint-fork, sandbox-branch, or mixed-recovery-identity,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-identity-witness vs quarantine-recovery-identity-governance consequence if the present continuity claim only supports a clone or sandbox branch rather than one continuing resume.

Do not use recovery identity as a governance metaphor. Use this prompt pair only where a durable row already depends on restored work sounding like the same run and the missing question is whether one small identity card would keep continuing resumes, checkpoint-forked clones, and sandbox-restored branches distinct without promoting a broader recovery-identity court.
```

**Continuation prompt**

```text
Continue the recovery-identity pass with one high-leverage continuation clarification only. Prefer the smallest witness that says what governed row is still being justified, what interruption, checkpoint, or restore path is supposedly unchanged, what the prior recovery-identity evidence was, what the current recovery-identity evidence is, what recovery_identity_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-recovery-identity-witness, quarantine, or recover-resync consequence follows if the current claim is really a checkpoint-fork or sandbox branch rather than one continuing resume. Run lint and package the release.
```

Use `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md` when the live question is whether restored output writes back into canon, only into a derived branch, only into a sandbox, or an honest mixture.

## `PP-0093` — Name where restored output is allowed to write back

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact recovery-writeback witness for honest restored-lineage authority.

Focus only on whether restored output may keep writing into canonical lineage, only into a derived branch, or only into a sandbox.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the restore / resume / write path,
- names the prior recovery-writeback evidence,
- names the current recovery-writeback evidence,
- names the recovery_writeback_state / whether this is canonical-writeback, branch-local-writeback, sandbox-only, or mixed-recovery-writeback,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-writeback-witness vs quarantine-recovery-writeback-governance consequence if the present continuity claim only supports branch-local or sandbox-only output rather than canonical writeback.

Do not use recovery writeback as a governance metaphor. Use this prompt pair only where a durable row already depends on restored work sounding authoritative and the missing question is whether one small writeback card would keep canonical continuation, derived-branch output, and sandbox-only restore distinct without promoting a broader recovery-writeback court.
```

**Continuation prompt**

```text
Continue the recovery-writeback pass with one high-leverage authority clarification only. Prefer the smallest witness that says what governed row is still being justified, what restore, resume, or write path is supposedly unchanged, what the prior recovery-writeback evidence was, what the current recovery-writeback evidence is, what recovery_writeback_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-recovery-writeback-witness, quarantine, or recover-resync consequence follows if the current claim is really only branch-local or sandbox-only rather than canonical writeback. Run lint and package the release.
```

Use `docs/10-method/recovery-promotion-witnesses-direct-canonical-writeback-promotion-gated-branch-import-and-export-only-carryover.md` when the live question is whether noncanonical restored output is already canonical, still needs an explicit promotion act before canon may inherit it, or should remain export-only carryover.

## `PP-0094` — Name whether noncanonical output is already promoted or only portable

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact recovery-promotion witness for honest noncanonical-to-canonical carry.

Focus only on whether branch, experiment, or exported output is already canonical, still needs an explicit promotion act, or should remain export-only carryover.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the source branch / experiment / export path,
- names the prior recovery-promotion evidence,
- names the current recovery-promotion evidence,
- names the recovery_promotion_state / whether this is direct-canonical-writeback, promotion-gated-branch-import, export-only-carryover, or mixed-recovery-promotion,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-promotion-witness vs quarantine-recovery-promotion-governance consequence if the present continuity claim only supports promotion-gated or export-only status rather than already-canonical authority.

Do not use recovery promotion as a governance metaphor. Use this prompt pair only where a durable row already depends on noncanonical output sounding canon-ready and the missing question is whether one small promotion card would keep direct canonical writeback, promotion-gated branch import, and export-only carryover distinct without promoting a broader recovery-promotion court.
```

**Continuation prompt**

```text
Continue the recovery-promotion pass with one high-leverage authority clarification only. Prefer the smallest witness that says what governed row is still being justified, what branch, experiment, or export path is supposedly unchanged, what the prior recovery-promotion evidence was, what the current recovery-promotion evidence is, what recovery_promotion_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-recovery-promotion-witness, quarantine, or recover-resync consequence follows if the current claim is really only promotion-gated or export-only rather than already-canonical. Run lint and package the release.
```


Use `docs/10-method/stake-continuity-witnesses-active-carried-pressure-commitment-carry-cooled-residue-and-narrated-concern.md` when the live question is whether a durable line still exerts live pressure now, only retains commitment carry, has cooled into residue, or is merely being narrated without current binding force.

## `PP-0095` — Name what is still live before you trust carried concern

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact stake-continuity witness for honest live-vs-remembered carry.

Focus only on whether a line of concern still exerts live pressure now, only retains commitment carry, has cooled into residue, or is merely being narrated without current binding force.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior stake evidence,
- names the current stake evidence,
- names the stake_continuity_state / whether this is active-carried-pressure, commitment-only-carry, cooled-residue, narrated-unbound-concern, or mixed-stake-continuity,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-stake-continuity-witness vs quarantine-synthetic-stake-control consequence if the present continuity claim only supports durable commitment, cooled residue, or narrated concern rather than active pressure.

Do not use stake continuity as a synthetic welfare theory. Use this prompt pair only where a durable row already depends on a concern sounding still-live and the missing question is whether one small pressure-carry card would keep active pressure, commitment carry, cooled residue, and narrated concern distinct without promoting a broader synthetic pressure board.
```

**Continuation prompt**

```text
Continue the stake-continuity pass with one high-leverage currentness clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly unchanged, what the prior stake evidence was, what the current stake evidence is, what stake_continuity_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, cool-mark, issue-new-stake-continuity-witness, quarantine, or recover-resync consequence follows if the current claim is really only commitment carry, cooled residue, or narrated concern rather than active carried pressure. Run lint and package the release.
```


Use `docs/10-method/stake-refresh-witnesses-observed-reactivation-regression-return-inherited-urgency-and-rhetorical-reheating.md` when the live question is whether a concern is newly live again because of a fresh public change, a regression return, borrowed urgency, or mere rhetorical reheating.

## `PP-0096` — Name what changed before you trust renewed urgency

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact stake-refresh witness for honest renewed-vs-reheated urgency.

Focus only on whether a concern is newly live again because of a fresh public change, because a resolved line regressed, because urgency is only being inherited from a nearby live row, or because narration is merely reheating old residue.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior stake-refresh evidence,
- names the current change evidence,
- names the trigger surface / event,
- names the stake_refresh_state / whether this is observed-reactivation, regression-return, inherited-urgency-only, rhetorical-reheat, or mixed-stake-refresh,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-stake-refresh-witness vs quarantine-reactivation-governance consequence if the present continuity claim only supports borrowed urgency or rhetorical reheating rather than fresh reactivation.

Do not use stake refresh as a general freshness theory. Use this prompt pair only where a durable row already depends on a concern sounding newly urgent again and the missing question is whether one small reactivation card would keep observed return, regression return, inherited urgency, and rhetorical reheating distinct without promoting a broader reactivation court.
```

**Continuation prompt**

```text
Continue the stake-refresh pass with one high-leverage reactivation clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior stake-refresh evidence was, what the current change evidence is, what trigger surface or event actually changed, what stake_refresh_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, cool-mark, issue-new-stake-refresh-witness, quarantine, or recover-resync consequence follows if the current claim is really only inherited urgency or rhetorical reheating rather than observed reactivation or regression return. Run lint and package the release.
```

Use `docs/10-method/refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md` when the live question is whether a returned concern is still only one resurfacing, has become sustained enough to count as renewed burden, or is merely being carried by a grace/keep-firing rule after the last positive signal.

## `PP-0097` — Name how sustained the return really is before you trust renewed burden

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-strength witness for honest one-off-vs-sustained renewed stake.

Focus only on whether a returned concern is still just one resurfacing, has crossed a bounded persistence threshold, or is merely being held open by a grace/keep-firing/autoclose-style rule after the last positive signal disappeared.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the strength evidence / persistence window,
- names the hold-open basis if any,
- names the `refresh_strength_state` / whether this is single-resurfacing, threshold-confirmed-reactivation, grace-held-return, or mixed-refresh-strength,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-refresh-strength-witness vs quarantine-refresh-timing-governance consequence if the present continuity claim is really only one resurfacing or grace-held carry rather than threshold-confirmed renewed burden.

Do not use refresh strength as a general timing policy. Use this prompt pair only where stake refresh is already explicit and the missing question is whether one small persistence card would keep one-off resurfacing, sustained return, and grace-held carry distinct without promoting a broader refresh-timing court.
```

**Continuation prompt**

```text
Continue the refresh-strength pass with one high-leverage persistence clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior refresh evidence was, what the current refresh evidence is, what bounded strength evidence or persistence window now exists, what hold-open basis if any is still carrying the line, what `refresh_strength_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, cool-mark, issue-new-refresh-strength-witness, quarantine, or recover-resync consequence follows if the current claim is really only one resurfacing or grace-held return rather than threshold-confirmed reactivation. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md` when the live question is whether apparent renewed support is still just one surface repeating, several grouped views of one origin, or genuinely widened confirming support.

## `PP-0098` — Name how broad the confirming support really is before you trust widened corroboration

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-support witness for honest same-surface-vs-widened renewed support.

Focus only on whether apparent renewed support still comes from one surface repeating, from several grouped or deduplicated views of one underlying origin, or from genuinely distinct additional confirming support.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the repeated support surface family,
- names the grouping or dedup basis if any,
- names the widened support evidence if any,
- names the `refresh_support_state` / whether this is repeated-same-surface, grouped-same-origin, widened-confirming-support, or mixed-refresh-support,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-refresh-support-witness vs quarantine-refresh-corroboration-governance consequence if the present continuity claim is really only one repeating or grouped origin rather than genuinely widened support.

Do not use refresh support as a general corroboration theory. Use this prompt pair only where refresh strength is already explicit and the missing question is whether one small support-breadth card would keep repeated same-surface confirmation, grouped-origin carry, and genuinely widened support distinct without promoting a broader corroboration court.
```

**Continuation prompt**

```text
Continue the refresh-support pass with one high-leverage support-breadth clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what repeated support surface family is present, what grouping or dedup basis if any is still collapsing the evidence, what widened support evidence if any now exists, what `refresh_support_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, cool-mark, issue-new-refresh-support-witness, quarantine, or recover-resync consequence follows if the current claim is really only same-surface repetition or grouped same-origin carry rather than widened-confirming-support. Run `make lint` and package the release.
```


Use `docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md` when the live question is whether widened support is still only several surfaces of one carried context or is independent enough to count as a distinct confirming branch.

## `PP-0099` — Name how independent the widened support really is before you trust extra corroborative weight

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-independence witness for honest coupled-vs-independent widened support.

Focus only on whether apparently widened support is still several surfaces echoing one carried context, whether it is only a shared-context carry, or whether it is independent enough to count as a distinct confirming branch.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the coupling basis or shared context if any,
- names the independent confirming support if any,
- names the `refresh_independence_state` / whether this is coupled-multi-surface-echo, shared-context-carry, independent-confirming-support, or mixed-refresh-independence,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-refresh-independence-witness vs quarantine-refresh-independence-governance consequence if the present continuity claim is really only coupled multi-surface echo or shared-context carry rather than independent confirming support.

Do not use refresh independence as a general provenance court. Use this prompt pair only where refresh support is already explicit and the missing question is whether one small independence card would keep coupled multi-surface echo, shared-context carry, and independent confirming support distinct without promoting a broader refresh-independence court.
```

**Continuation prompt**

```text
Continue the refresh-independence pass with one high-leverage support-independence clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what coupling basis or shared context is still collapsing the evidence, what independent confirming support if any now exists, what `refresh_independence_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, cool-mark, issue-new-refresh-independence-witness, quarantine, or recover-resync consequence follows if the current claim is really only coupled-multi-surface-echo, shared-context-carry, independent-confirming-support, or mixed-refresh-independence. Run `make lint` and package the release.
```


Use `docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md` when the live question is whether independent confirming support merely stabilizes the current claim or actually licenses a stronger public burden.

## `PP-0100` — Name whether independent support only steadies the line or really upgrades the public burden

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-elevation witness for honest support-vs-burden comparison.

Focus only on whether apparently independent support merely stabilizes the present claim, whether it crosses a declared burden threshold and licenses a stronger public burden, or whether it still needs a judgment or policy gate before any stronger public upgrade is honest.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the independent confirming support,
- names the burden threshold / elevation trigger if any,
- names the judgment or policy gate if any,
- names the `refresh_elevation_state` / whether this is stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs elevate-burden vs issue-new-refresh-elevation-witness vs quarantine-refresh-elevation-governance consequence if the present continuity claim is really only stabilizing support or still judgment-gated rather than threshold-licensed elevation.

Do not use refresh elevation as a general burden court. Use this prompt pair only where refresh independence is already explicit and the missing question is whether one small elevation card would keep support stabilization, threshold-licensed elevation, and judgment-gated escalation distinct without promoting a broader refresh-elevation court.
```

**Continuation prompt**

```text
Continue the refresh-elevation pass with one high-leverage burden-upgrade clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what independent confirming support if any now exists, what burden threshold or elevation trigger if any is crossed, what judgment or policy gate if any still remains, what `refresh_elevation_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, elevate-burden, issue-new-refresh-elevation-witness, quarantine, or recover-resync consequence follows if the current claim is really only stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation. Run `make lint` and package the release.
```


Use `docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md` when the live question is whether a stronger licensed burden still governs the same current claim or honestly widens the public claim scope.

## `PP-0101` — Name whether stronger burden stays on the same claim or really widens public scope

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-burden-scope witness for honest same-claim-vs-widened-scope comparison.

Focus only on whether a newly licensed burden still governs the same current claim, whether it honestly widens the public claim scope in a bounded named way, or whether the evidence only hints at a broader blast radius and still needs another scope gate before public generalization is honest.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the licensed burden upgrade if any,
- names the same-claim scope anchor,
- names the scope-widening evidence if any,
- names the scope gate or non-local inference basis if any,
- names the `refresh_burden_scope_state` / whether this is same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or mixed-refresh-burden-scope,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs widen-scope vs issue-new-refresh-burden-scope-witness vs quarantine-refresh-scope-governance consequence if the present continuity claim is really only a same-claim burden upgrade or still scope-gated rather than honestly widened.

Do not use refresh burden scope as a general blast-radius court. Use this prompt pair only where refresh elevation is already explicit and the missing question is whether one small scope card would keep same-claim burden, bounded widening, and scope-gated generalization distinct without promoting a broader refresh-scope court.
```

**Continuation prompt**

```text
Continue the refresh-burden-scope pass with one high-leverage scope-licensing clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what licensed burden upgrade if any now exists, what same-claim scope anchor still pins the current claim, what widening evidence if any now exists, what scope gate or non-local inference basis if any still remains, what `refresh_burden_scope_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, widen-scope, issue-new-refresh-burden-scope-witness, quarantine, or recover-resync consequence follows if the current claim is really only same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or mixed-refresh-burden-scope. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md` when the live question is whether a widened public claim is directly observed on the widened surface or only dependency- or topology-imputed.

## `PP-0102` — Name whether widened scope is directly observed or only spillover-imputed

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-basis witness for honest widened-scope-basis comparison.

Focus only on whether the widened public scope is directly observed on the widened surface, only implied through a dependency relation, only implied through topology / graph / context structure, or honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-burden-scope evidence,
- names the current widened-scope evidence,
- names the direct observation basis if any,
- names the dependency relation basis if any,
- names the topology relation basis if any,
- names the `refresh_scope_basis_state` / whether this is directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or mixed-refresh-scope-basis,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-basis-witness vs quarantine-refresh-topology-governance consequence if the present continuity claim is really only spillover-imputed rather than directly observed.

Do not use refresh scope basis as a general topology court. Use this prompt pair only where widened scope is already in play and the missing question is whether one small basis card would keep directly observed widening distinct from dependency- or topology-imputed spillover without promoting a broader refresh-topology court.
```

**Continuation prompt**

```text
Continue the refresh-scope-basis pass with one high-leverage spillover-basis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-burden-scope evidence exists, what current widened-scope evidence exists, what direct observation basis if any now exists, what dependency relation basis if any remains, what topology relation basis if any remains, what `refresh_scope_basis_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-basis-witness, quarantine, or recover-resync consequence follows if the current claim is really directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or mixed-refresh-scope-basis. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md` when the live question is whether directly observed widened scope is still only one newly affected slice or already a broader observed spillover pattern.

## `PP-0103` — Name whether widened impact is still one observed slice or already a broader observed spillover pattern

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-extent witness for honest widened-scope-pattern comparison.

Focus only on whether the directly observed widened scope is still one newly affected slice, already a broader observed spillover pattern, still gated from broader generalization, or honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-basis evidence,
- names the current widened-scope evidence,
- names the observed widened slice or slice family,
- names the broader observed spillover-pattern evidence if any,
- names the extent gate or unobserved remainder if any,
- names the `refresh_scope_extent_state` / whether this is single-observed-slice, patterned-observed-spillover, extent-gated-generalization, or mixed-refresh-scope-extent,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-extent-witness vs quarantine-refresh-extent-governance consequence if the present continuity claim is really only one observed widened slice rather than a broader pattern.

Do not use refresh scope extent as a general saturation court. Use this prompt pair only where widened scope is already directly observed and the missing question is whether one new observed slice is being over-read as a broader observed spillover pattern.
```

**Continuation prompt**

```text
Continue the refresh-scope-extent pass with one high-leverage spillover-pattern clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-basis evidence exists, what current widened-scope evidence exists, what observed widened slice or slice family now exists, what broader observed spillover-pattern evidence if any now exists, what extent gate or unobserved remainder if any still remains, what `refresh_scope_extent_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-extent-witness, quarantine, or recover-resync consequence follows if the current claim is really single-observed-slice, patterned-observed-spillover, extent-gated-generalization, or mixed-refresh-scope-extent. Run `make lint` and package the release.
```


Use `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md` when the live question is whether broader directly observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families.

## `PP-0104` — Name whether observed spillover is still clustered or already dispersed across widened families

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-distribution witness for honest clustered-vs-dispersed spillover comparison.

Focus only on whether the broader directly observed spillover still clusters inside one named widened family, is already dispersed across several widened families, is still distribution-gated from broader generalization, or is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-extent evidence,
- names the current widened-scope evidence,
- names the observed clustered-family basis if any,
- names the dispersed widened-family evidence if any,
- names the distribution gate or uncovered family remainder if any,
- names the `refresh_scope_distribution_state` / whether this is clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-distribution-witness vs quarantine-refresh-distribution-governance consequence if the present continuity claim is really only a clustered observed spillover rather than dispersed spread.

Do not use refresh scope distribution as a general diffusion court. Use this prompt pair only where broadened observed spillover is already real and the missing question is whether the spillover still clusters inside one named family or is honestly dispersed across several widened families.
```

**Continuation prompt**

```text
Continue the refresh-scope-distribution pass with one high-leverage cluster-vs-dispersion clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-extent evidence exists, what current widened-scope evidence exists, what observed clustered-family basis if any now exists, what dispersed widened-family evidence if any now exists, what distribution gate or uncovered family remainder if any still remains, what `refresh_scope_distribution_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-distribution-witness, quarantine, or recover-resync consequence follows if the current claim is really clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution. Run `make lint` and package the release.
```


Use `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md` when the live question is whether dispersed observed spillover still lives on one named family axis or is corroborated across independent family axes.

## `PP-0105` — Name whether dispersed spread is still one-axis or already cross-axis corroborated

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis witness for honest one-axis-vs-cross-axis dispersed-spread comparison.

Focus only on whether the already-dispersed observed spillover still lives on one named family axis, is corroborated across independent family axes, is still axis-gated from broader generalization, or is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-distribution evidence,
- names the current dispersed-scope evidence,
- names the one-axis family basis if any,
- names the independent-axis corroboration if any,
- names the axis gate or mirrored-axis remainder if any,
- names the `refresh_scope_axis_state` / whether this is one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or mixed-refresh-scope-axis,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-witness vs quarantine-refresh-axis-governance consequence if the present continuity claim is really only one-axis dispersion rather than cross-axis corroboration.

Do not use refresh scope axis as a general corroboration court. Use this prompt pair only where dispersed widening is already real and the missing question is whether the dispersion still lives on one named family axis or is honestly corroborated across independent axes.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis pass with one high-leverage one-axis-vs-cross-axis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-distribution evidence exists, what current dispersed-scope evidence exists, what one-axis family basis if any now exists, what independent-axis corroboration if any now exists, what axis gate or mirrored remainder if any still remains, what `refresh_scope_axis_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-witness, quarantine, or recover-resync consequence follows if the current claim is really one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or mixed-refresh-scope-axis. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md` when the live question is whether apparent corroborating axes are genuinely independent or only renamed, mirrored, or hierarchy-nested restatements of one underlying partition.

## `PP-0106` — Name whether apparent corroborating axes are renamed, nested, or genuinely independent

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-independence witness for honest renamed-vs-nested-vs-independent axis comparison.

Focus only on whether the already cross-axis-looking dispersed spread is really supported by genuinely independent axes, is only a renamed or mirrored restatement of one underlying partition, is only a nested refinement inside one hierarchy, or is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis evidence,
- names the current dispersed-scope evidence,
- names the candidate corroborating axes,
- names the renamed-or-mirrored restatement basis if any,
- names the nested-hierarchy basis if any,
- names the independent-axis basis if any,
- names the `refresh_scope_axis_independence_state` / whether this is renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-independence-witness vs quarantine-axis-materiality-governance consequence if the present continuity claim is really only a renamed, mirrored, or nested restatement rather than genuinely independent corroboration.

Do not use refresh scope axis independence as a general corroboration court. Use this prompt pair only where cross-axis-looking spread already exists and the missing question is whether the apparent axes are truly independent.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-independence pass with one high-leverage renamed-vs-nested-vs-independent clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis evidence exists, what current dispersed-scope evidence exists, what candidate corroborating axes are being compared, what renamed-or-mirrored restatement basis if any now exists, what nested-hierarchy basis if any now exists, what independent-axis basis if any now exists, what `refresh_scope_axis_independence_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-independence-witness, quarantine, or recover-resync consequence follows if the current claim is really renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md` when the live question is whether genuinely independent corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed.
Use `docs/10-method/refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md` when the live question is whether materially backed corroboration still rides one coupled failure or execution plane, remains hierarchy-coupled inside one parent plane, or stays honestly decoupled under perturbation.

## `PP-0107` — Name whether genuinely independent corroboration is only label-distinct, failure-domain-backed, or isolation-backed

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-materiality witness for honest label-distinct-vs-failure-domain-vs-isolation-backed corroboration.

Focus only on cases where the axes already look genuinely independent. The missing question is whether that independence is still only a label, queue, or selector distinction, whether it is backed by a public failure domain, whether it is backed by substrate isolation, or whether the situation is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-independence evidence,
- names the current corroborating axes,
- names the label-distinct-only basis if any,
- names the failure-domain basis if any,
- names the isolation-backed basis if any,
- names the `refresh_scope_axis_materiality_state` / whether this is label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-materiality-witness vs quarantine-axis-materiality-exchange-rate consequence if the present continuity claim is still only weakly material.

Do not use refresh scope axis materiality as a general weighting court. Use this prompt pair only where axis independence is already established and the missing question is how materially strong the corroboration really is.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-materiality pass with one high-leverage label-vs-failure-domain-vs-isolation clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-independence evidence exists, what current corroborating axes exist, what label-distinct-only basis if any now exists, what failure-domain basis if any now exists, what isolation-backed basis if any now exists, what `refresh_scope_axis_materiality_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-materiality-witness, quarantine, or recover-resync consequence follows if the present corroboration is only label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality. Run `make lint` and package the release.
```

## `PP-0108` — Name whether materially backed corroboration is still coupled or already perturbation-decoupled

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-coupling witness for honest same-plane-vs-hierarchy-coupled-vs-perturbation-decoupled corroboration.

Focus only on cases where the axes already look genuinely independent and materially backed. The missing question is whether that corroboration still collapses on one failure or execution plane, whether it is only hierarchy-separated inside one parent plane, whether it remains honestly decoupled under the perturbation that matters, or whether the situation is mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-materiality evidence,
- names the current corroborating axes,
- names the same-plane basis if any,
- names the hierarchy-coupled basis if any,
- names the perturbation-decoupled basis if any,
- names the `refresh_scope_axis_coupling_state` / whether this is same-plane-coupled-corroboration, hierarchy-coupled-corroboration, perturbation-decoupled-corroboration, or mixed-refresh-scope-axis-coupling,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-coupling-witness vs quarantine-axis-covariance-machine consequence if the present continuity claim is still coupled.

Do not use refresh scope axis coupling as a general covariance court. Use this prompt pair only where axis independence and materiality are already established and the missing question is whether the corroboration actually stays apart under the perturbation that matters.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-coupling pass with one high-leverage coupled-vs-decoupled clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-materiality evidence exists, what current corroborating axes exist, what same-plane basis if any now exists, what hierarchy-coupled basis if any now exists, what perturbation-decoupled basis if any now exists, what `refresh_scope_axis_coupling_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-coupling-witness, quarantine, or recover-resync consequence follows if the present corroboration is same-plane-coupled-corroboration, hierarchy-coupled-corroboration, perturbation-decoupled-corroboration, or mixed-refresh-scope-axis-coupling. Run `make lint` and package the release.
```

## `PP-0109` — Name whether decoupled corroboration is binding, best-effort, or advisory

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-enforcement witness for honest hard-vs-best-effort-vs-advisory decoupling comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, and decoupled under perturbation. The missing question is whether that decoupling is actually binding under allocation or admission policy, only preferred on a best-effort basis, only advisory, or honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-coupling evidence,
- names the current corroborating axes,
- names the hard-enforcement basis if any,
- names the best-effort basis if any,
- names the advisory-only basis if any,
- names the `refresh_scope_axis_enforcement_state` / whether this is hard-enforced-decoupled-corroboration, best-effort-decoupled-corroboration, advisory-corroboration, or mixed-refresh-scope-axis-enforcement,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-enforcement-witness vs quarantine-enforcement-credit-ledger consequence if the present continuity claim is not actually binding.

Do not use refresh scope axis enforcement as a general policy-strength court. Use this prompt pair only where axis independence, materiality, and coupling are already established and the missing question is whether the decoupling is really enforced.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-enforcement pass with one high-leverage hard-vs-soft clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-coupling evidence exists, what current corroborating axes exist, what hard-enforcement basis if any now exists, what best-effort basis if any now exists, what advisory-only basis if any now exists, what `refresh_scope_axis_enforcement_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-enforcement-witness, quarantine, or recover-resync consequence follows if the present corroboration is hard-enforced-decoupled-corroboration, best-effort-decoupled-corroboration, advisory-corroboration, or mixed-refresh-scope-axis-enforcement. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md` when the live question is whether already-decoupled corroboration is actually binding under policy, only preferred on a best-effort basis, or merely advisory.


## `PP-0110` — Name whether decoupled corroboration stays preserved, needs repair, or is grandfathered

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-durability witness for honest eviction-vs-repair-vs-grandfathered decoupling comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, and hard-enforced rather than merely preferred. The missing question is whether that decoupling stays preserved by runtime eviction or deletion, only comes back through later repair or rebalance, is grandfathered after drift, or is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-enforcement evidence,
- names the current corroborating axes,
- names the eviction-preserved basis if any,
- names the repair-restored basis if any,
- names the grandfathered basis if any,
- names the `refresh_scope_axis_durability_state` / whether this is eviction-preserved-decoupling, repair-restored-decoupling, grandfathered-decoupling, or mixed-refresh-scope-axis-durability,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-durability-witness vs quarantine-durability-lease-ledger consequence if the present continuity claim is not actually durably preserved.

Do not use refresh scope axis durability as a general repair-authority court. Use this prompt pair only where axis independence, materiality, coupling, and enforcement are already established and the missing question is whether the decoupling actually stays true after scheduling.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-durability pass with one high-leverage durability clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-enforcement evidence exists, what current corroborating axes exist, what eviction-preserved basis if any now exists, what repair-restored basis if any now exists, what grandfathered basis if any now exists, what `refresh_scope_axis_durability_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-durability-witness, quarantine, or recover-resync consequence follows if the present corroboration is eviction-preserved-decoupling, repair-restored-decoupling, grandfathered-decoupling, or mixed-refresh-scope-axis-durability. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md` when the live question is whether already-decoupled corroboration keeps policing runtime drift, only returns through repair or rebalance, or leaves grandfathered residue in place.

## PP-0111 — Name whether restored decoupling comes back through native controllers, auxiliary remediators, or operator replay

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation witness for honest controller-vs-remediator-vs-operator restoration comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and explicitly durable or repair-restored rather than merely advisory. The missing question is who or what actually restores the decoupling after drift: the platform's own admitted controller path, an auxiliary remediator or rebalance loop, a privileged operator replay act, or an honest mix.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-durability evidence,
- names the current corroborating axes,
- names the native-controller basis if any,
- names the external-remediator basis if any,
- names the operator-replay basis if any,
- names the `refresh_scope_axis_remediation_state` / whether this is native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-witness vs quarantine-remediation-provenance-credit consequence if the present continuity claim is not actually restored by the claimed lane.

Do not use refresh scope axis remediation as a standing remediation authority court. Use this prompt pair only where axis independence, materiality, coupling, enforcement, and durability are already established and the missing question is who restored the decoupling once drift occurred.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation pass with one high-leverage remediation provenance clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-durability evidence exists, what current corroborating axes exist, what native-controller basis if any now exists, what external-remediator basis if any now exists, what operator-replay basis if any now exists, what `refresh_scope_axis_remediation_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-witness, quarantine, or recover-resync consequence follows if the present restoration is native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through the platform's own controller path, an auxiliary remediator, or a manual replay act.


## PP-0112 — Name whether restored decoupling stayed local, spent a drain, or spent fenced substrate

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-collateral witness for honest local-vs-drain-vs-fence restoration comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, explicitly durable, and explicit about who restored the decoupling. The missing question is how much surrounding workload or substrate disruption the restoration spends: only a local workload replacement, a broader drain-backed move, a fenced-substrate move, or an honest mix.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation evidence,
- names the current corroborating axes,
- names the local-workload-replacement basis if any,
- names the drain-backed basis if any,
- names the fenced-substrate basis if any,
- names the `refresh_scope_axis_remediation_collateral_state` / whether this is local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-collateral-witness vs quarantine-remediation-collateral-tariff consequence if the present continuity claim is not actually restored by the claimed collateral lane.

Do not use refresh-scope-axis-remediation-collateral as a standing disruption-budget court. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, and remediation provenance are already established and the missing question is how much collateral the restoration spent once drift was repaired.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-collateral pass with one high-leverage collateral clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation evidence exists, what current corroborating axes exist, what local-workload-replacement basis if any now exists, what drain-backed basis if any now exists, what fenced-substrate basis if any now exists, what `refresh_scope_axis_remediation_collateral_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-collateral-witness, quarantine, or recover-resync consequence follows if the present restoration is local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through a local workload replacement, a broader drain-backed move, or fenced-substrate recovery.


## PP-0113 — Name whether restored decoupling reused free capacity or displaced lower-priority work

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-capacity-source witness for honest free-vs-preempt restoration comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, explicitly durable, explicit about who restored the decoupling, and honest about whether the repair stayed local or spent a drain or fence. The missing question is whether the restored placement reused already-available capacity or only came back by evicting, suspending, requeueing, or otherwise displacing unrelated lower-priority work.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-collateral evidence,
- names the current corroborating axes,
- names the free-capacity basis if any,
- names the preemption-backed basis if any,
- names the `refresh_scope_axis_remediation_capacity_source_state` / whether this is free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-capacity-source-witness vs quarantine-displacement-debt consequence if the present continuity claim is not actually supported by the claimed capacity source.

Do not use refresh-scope-axis-remediation-capacity-source as a standing priority tariff board. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, and remediation collateral are already established and the missing question is who paid the capacity bill for restoration.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-capacity-source pass with one high-leverage capacity-source clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-collateral evidence exists, what current corroborating axes exist, what free-capacity basis if any now exists, what preemption-backed basis if any now exists, what `refresh_scope_axis_remediation_capacity_source_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-capacity-source-witness, quarantine, or recover-resync consequence follows if the present restoration is free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through already-available slack or only by displacing lower-priority work.


## PP-0114 — Name whether displaced lower-priority work remained resumable or was terminally sacrificed

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-aftercare witness for honest resumable-vs-terminal preemption aftermath.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, and honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work. The missing question is what happened afterward to the lower-priority work that paid the preemption bill.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-capacity-source evidence,
- names the current corroborating axes,
- names the resumable-aftercare basis if any,
- names the terminal-aftercare basis if any,
- names the `refresh_scope_axis_remediation_displacement_aftercare_state` / whether this is resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-aftercare-witness vs quarantine-resume-credit consequence if the present continuity claim is not actually supported by the claimed aftercare.

Do not use refresh-scope-axis-remediation-displacement-aftercare as a standing restitution or restart-tax board. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, and remediation capacity source are already established and the missing question is whether the displaced work still had a live path back.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-aftercare pass with one high-leverage aftercare clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-capacity-source evidence exists, what current corroborating axes exist, what resumable-aftercare basis if any now exists, what terminal-aftercare basis if any now exists, what `refresh_scope_axis_remediation_displacement_aftercare_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-aftercare-witness, quarantine, or recover-resync consequence follows if the present aftercare is resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md` when the live question is what happened afterward to the lower-priority work that paid the preemption bill.
## PP-0115 — Name whether a nonterminal return stayed in memory, replayed checkpoints, or restarted cold

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-resumption-basis witness for honest warm-vs-replay-vs-cold return.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, and honest about whether the displaced lower-priority work stayed nonterminal. The missing question is how that work actually returned.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-displacement-aftercare evidence,
- names the current corroborating axes,
- names the in-memory continuation basis if any,
- names the checkpoint-backed replay basis if any,
- names the cold-restart basis if any,
- names the `refresh_scope_axis_remediation_displacement_resumption_basis_state` / whether this is in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness vs quarantine-warm-state-credit consequence if the present continuity claim is not actually supported by the claimed return basis.

Do not use refresh-scope-axis-remediation-displacement-resumption-basis as a standing replay-fidelity board or warmth market. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, and remediation displacement aftercare are already established and the missing question is whether the displaced work returned live in memory, via saved-state replay, or via cold restart.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-resumption-basis pass with one high-leverage return-basis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-aftercare evidence exists, what current corroborating axes exist, what in-memory continuation basis if any now exists, what checkpoint-backed replay basis if any now exists, what cold-restart basis if any now exists, what `refresh_scope_axis_remediation_displacement_resumption_basis_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness, quarantine, or recover-resync consequence follows if the present return basis is in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md` when the live question is how a supposedly resumable displaced workload actually came back.


## PP-0116 — Name whether checkpoint-backed return restored exact state, only the latest durable boundary, or just restarted from source

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness for honest exact-vs-bounded-loss-vs-source-only return.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, honest about whether the displaced lower-priority work stayed nonterminal, and honest about whether the return was in-memory, checkpoint-backed, or cold. The missing question is how much execution state actually survived inside the replay path.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-displacement-resumption-basis evidence,
- names the current corroborating axes,
- names the exact-state-restore basis if any,
- names the bounded-loss checkpoint basis if any,
- names the source-only restart basis if any,
- names the `refresh_scope_axis_remediation_displacement_replay_fidelity_state` / whether this is exact-state-restore, bounded-loss-checkpoint-replay, source-only-restart, or mixed-refresh-scope-axis-remediation-displacement-replay-fidelity,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-fidelity-witness vs quarantine-performance-shadow consequence if the present continuity claim is not actually supported by the claimed replay-fidelity lane.

Do not use refresh-scope-axis-remediation-displacement-replay-fidelity as a standing performance-equivalence board or warm-cache market. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, remediation displacement aftercare, and remediation displacement resumption basis are already established and the missing question is whether the returning work restored exact saved state, only the latest durable checkpoint boundary, or merely restarted from source.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-replay-fidelity pass with one high-leverage replay-loss clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-resumption-basis evidence exists, what current corroborating axes exist, what exact-state-restore basis if any now exists, what bounded-loss checkpoint basis if any now exists, what source-only restart basis if any now exists, what `refresh_scope_axis_remediation_displacement_replay_fidelity_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-replay-fidelity-witness, quarantine, or recover-resync consequence follows if the present replay lane is exact-state-restore, bounded-loss-checkpoint-replay, source-only-restart, or mixed-refresh-scope-axis-remediation-displacement-replay-fidelity. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md` when the live question is how faithful a checkpoint-backed or replacement-based return really was.



## PP-0117 — Name whether an exact-looking restore stayed practically equivalent or came back under a performance shadow

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness for honest functionally-exact-vs-performance-shadow return.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, honest about whether the displaced lower-priority work stayed nonterminal, honest about whether the return was in-memory, checkpoint-backed, or cold, and honest about whether replay restored exact saved state rather than only a latest durable boundary or source-only restart. The missing question is whether the exact-looking restore stayed practically equivalent or came back under a material performance shadow.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence,
- names the current corroborating axes,
- names the functionally-exact-restore basis if any,
- names the performance-shadow-restore basis if any,
- names the `refresh_scope_axis_remediation_displacement_replay_equivalence_state` / whether this is functionally-exact-restore, performance-shadow-restore, or mixed-refresh-scope-axis-remediation-displacement-replay-equivalence,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-equivalence-witness vs quarantine-shadow-source consequence if the present continuity claim is not actually supported by the claimed replay-equivalence posture.

Do not use refresh-scope-axis-remediation-displacement-replay-equivalence as a standing cache-solvency or host-parity market. Use this prompt pair only where the prior replay-fidelity witness already shows exact-looking restore and the missing question is whether exactness also stayed practically equivalent.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-replay-equivalence pass with one high-leverage shadow clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence exists, what current corroborating axes exist, what functionally-exact-restore basis if any now exists, what performance-shadow-restore basis if any now exists, what `refresh_scope_axis_remediation_displacement_replay_equivalence_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-replay-equivalence-witness, quarantine, or recover-resync consequence follows if the present replay-equivalence posture is functionally-exact-restore, performance-shadow-restore, or mixed-refresh-scope-axis-remediation-displacement-replay-equivalence. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md` when the live question is whether an exact-looking restore stayed practically equivalent or came back under a material performance shadow.
