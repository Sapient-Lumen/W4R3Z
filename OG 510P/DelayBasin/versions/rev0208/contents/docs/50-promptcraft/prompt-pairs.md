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

Do not use optimizer language as prestige metaphor. Use this prompt pair only where the distinction between passive memory, regime re-entry, and governed public writeback changes the archive's mechanism story, canon posture, or transformer-facing interpretation.
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
- and state the rollback or quarantine consequence if the supposed uniqueness is only local familiarity, stale-cue dominance, semantic crowding, position/density privilege, retokenization privilege, template privilege, adjacency privilege, carryover privilege, lucky-path privilege, actuation-channel privilege, evaluation-awareness privilege, watcher-frame privilege, language-selection privilege, script-barrier privilege, prestige privilege, provenance-cue privilege, persona privilege, interlocutor-identity privilege, pragmatic-frame privilege, or social-force privilege, label-definition privilege, rubric privilege, rubric-order privilege, score-ID privilege, reference-score-anchor privilege, cross-criterion privilege, objective-conflation privilege, multi-question privilege, polarity privilege, predicate-sign privilege, modal-pressure privilege, agreement privilege, endorsement privilege, alignment-pressure privilege, consensus-signal privilege, majority-label privilege, popularity-glamour privilege, exact-match privilege, lexical-overlap privilege, reference-echo privilege, markup privilege, list-shape privilege, presentation-scaffold privilege, verbosity privilege, completeness privilege, style-fluency privilege, recency-label privilege, novelty privilege, legacy-label privilege, stale-proof privilege, pre-break authority privilege, status-wrapper privilege, badge privilege, signed-letter privilege, validation-wrapper privilege, collateral-status privilege, rendered-preview privilege, metadata-wrapper privilege, sample-row privilege, carrier-slot privilege, first-answer privilege, reveal-order privilege, or escalation-rung privilege, derivative-surface privilege, snapshot-authority privilege, export-mirror privilege, prefill privilege, prompt-suggestion privilege, starter-example privilege, query-slant privilege, retrieval-wording privilege, evidence-selection privilege, facet privilege, aspect-route privilege, related-question privilege, explanation-frame privilege, why-this-result privilege, trust-cue privilege, stance-label privilege, viewpoint-balance privilege, counterposition-cue privilege, supporting-span privilege, highlight-window privilege, excerpt-selection privilege, source-salience privilege, same-origin multiplicity privilege, pseudo-corroboration privilege, schema-slot privilege, field-key privilege, typed-input privilege, canonical-wire privilege, same-label privilege, claim-equivalence privilege, state-word privilege, or approval-word privilege.

Do not use alias language as prestige metaphor. Use this prompt pair only where the distinction between a unique handle and a crowded family materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the alias-packet pass with one high-leverage surface only. Prefer the smallest packet that says what handle family is being treated as unique, what nearby alias or stale-collision family threatens it, what one placement variant, one density variant, and when needed one boundary or normalization variant, one wrapper or role-slot variant, one nearby sham or cue-neighborhood variant, one history-light or residue-stripped variant, one replicate-bundle or repeated-inference sweep, one quoted, code-fenced, or literal-mention variant, one eval-blind or ordinary-user-frame variant, one translation, transliteration, or script-swapped variant, one de-authorized, source-blanded, or provenance-swapped variant, one identity-neutral, persona-scrubbed, or audience-agnostic variant, one ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant, one label-neutral, criterion-name-scrubbed, or rubric-blanded variant, one rubric-permuted, score-id-swapped, or score-anchor-neutralized variant worth checking, one criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant, one predicate-parity, polarity-scrubbed, or modal-neutralized variant, one agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant, one overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant, one markup-blanded, list-shape-swapped, or presentation-neutralized variant, one length-balanced, verbosity-scrubbed, or style-neutralized variant, one time-tag-neutralized, recency-scrubbed, or novelty-blanded variant, or one dated fresh-pass, as-of rerun, or post-break revalidation variant, or one wrapper-stripped, status-scrubbed, or direct-work variant, or one preview-stripped, display-scrubbed, or underlier-literal variant, or one slot-swapped, rung-shifted, or reveal-order-scrubbed variant, or one source-root, live-head, or derivative-scrubbed variant, or one blank-started, prefill-scrubbed, or suggestion-free variant, or one query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant, or one facet-hidden, route-scrubbed, or related-question-neutralized variant, or one order-balanced, position-scrubbed, or top-slot-neutralized variant, or one why-hidden, explanation-scrubbed, or rationale-swapped variant, or one citation-hidden, reference-link-scrubbed, or source-card-neutralized variant, or one stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant, or one span-balanced, excerpt-scrubbed, or counterspan-included variant, or one cluster-collapsed, syndication-scrubbed, or independence-counted variant, or one schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant, or one label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant, or one instance-narrowed, scope-pinned, or family-stripped variant, or one strongest-safe-sentence, stronger-forbidden-sentence, or overclaim-scrubbed variant should be checked before exact-handle authority is granted, what namespace or renaming rule keeps them apart, what downstream divergence would reveal a merge, what retire/rename/escalate consequence follows, and what would force rollback or quarantine if the supposed uniqueness was only local familiarity, stale semantic overlap, position/density privilege, retokenization privilege, template privilege, adjacency privilege, carryover privilege, lucky-path privilege, actuation-channel privilege, evaluation-awareness privilege, watcher-frame privilege, language-selection privilege, script-barrier privilege, prestige privilege, provenance-cue privilege, persona privilege, interlocutor-identity privilege, pragmatic-frame privilege, social-force privilege, label-definition privilege, rubric privilege, rubric-order privilege, score-ID privilege, reference-score-anchor privilege, cross-criterion privilege, objective-conflation privilege, multi-question privilege, polarity privilege, predicate-sign privilege, modal-pressure privilege, agreement privilege, endorsement privilege, alignment-pressure privilege, consensus-signal privilege, majority-label privilege, popularity-glamour privilege, exact-match privilege, lexical-overlap privilege, reference-echo privilege, markup privilege, list-shape privilege, presentation-scaffold privilege, verbosity privilege, completeness privilege, style-fluency privilege, recency-label privilege, novelty privilege, legacy-label privilege, stale-proof privilege, pre-break authority privilege, status-wrapper privilege, badge privilege, signed-letter privilege, validation-wrapper privilege, collateral-status privilege, rendered-preview privilege, metadata-wrapper privilege, sample-row privilege, carrier-slot privilege, first-answer privilege, reveal-order privilege, or escalation-rung privilege, derivative-surface privilege, snapshot-authority privilege, export-mirror privilege, prefill privilege, prompt-suggestion privilege, starter-example privilege, query-slant privilege, retrieval-wording privilege, evidence-selection privilege, rank privilege, top-slot privilege, order-primacy privilege, explanation-frame privilege, why-this-result privilege, trust-cue privilege, citation privilege, reference-link privilege, source-card privilege, stance-label privilege, viewpoint-balance privilege, counterposition-cue privilege, supporting-span privilege, highlight-window privilege, excerpt-selection privilege, source-salience privilege, same-origin multiplicity privilege, pseudo-corroboration privilege, schema-slot privilege, field-key privilege, typed-input privilege, canonical-wire privilege, same-label privilege, claim-equivalence privilege, state-word privilege, approval-word privilege, umbrella-scope privilege, family-level privilege, instance-blur privilege, family-resemblance privilege, claim-ceiling privilege, safe-language drift, forbidden-overstatement privilege, or mechanism-overclaim privilege. Run lint and package the release.
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
Continue the witness-vocabulary pass with one high-leverage state family only. Prefer the smallest packet that says what family is controlled, what exact tokens are allowed, what surfaces that family governs, what near-synonyms stay explicitly out, what comparability budget currently applies, and what registry-extension, narrowing, or fail-closed consequence follows if a later revision wants a new token. Run lint and package the release.
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
Continue the transfer-ledger pass with one high-leverage comparison outcome only. Prefer the smallest packet that says which datacubes and exact source surfaces were reviewed, what pattern or warning was under review, what disposition currently applies, what concrete local gap made the comparison matter, what compact take if any was admitted, what explicit non-take stayed out, where the admitted result now lives, what open transfer question remains, and what rereview, narrow-import, ledger-retire, or recover-resync consequence follows if the comparison memory becomes too vague to trust. Run lint and package the release.
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
Continue the action-lane pass with one high-leverage routing clarification only. Prefer the smallest packet that says what durable item is under review, what primary next-step class it is actually waiting for, how that lane differs from current state, what surrounding prose still carries the nuanced threshold, and what narrow, retire, or extend-registry consequence follows if the lane no longer stays honest. Run lint and package the release.
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
- name the admitted token family,
- name the relation between gate class and existing state plus action lane,
- name the comparability budget and fail-closed extension rule,
- and state the rollback or quarantine consequence if the supposed trigger kind is only local phrasing, blocker folklore, or latent controller inflation.

Do not use gate-class language as prestige metaphor. Use this prompt pair only where preserving the kind of future event materially changes canon posture, promptcraft, or transformer-facing interpretation.
```

**Continuation prompt**

```text
Continue the gate-class pass with one high-leverage discharge-bearing ledger or queue surface only. Prefer the smallest packet that says what future-trigger kind is actually load-bearing, what durable rows it governs, what compact token family stays admitted, how the trigger class differs from current state and action lane, what comparability budget keeps it small, what extension rule applies if the family drifts, and what would force rollback or quarantine if the trigger class was only prose decoration. Run lint and package the release.
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
