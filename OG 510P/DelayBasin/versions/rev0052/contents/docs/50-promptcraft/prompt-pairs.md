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
Continue researching online and evolving DelayBasin with tight, high-leverage revisions. Keep the archive small, wired, and cumulative. Be creative, meta, and open in the search; GPUstorm when that helps find a sharper mechanism or cleaner compression. Make at least one bold but disciplined speculative move, and place it in canon or quarantine honestly. Name the certified move classes you actually instantiated. If a prior revision is clearly shared, prefer innovation packets over whole-archive replay: name the anchor, the real delta, and whether ordinary continuation, bounded rollback, or `recover-resync` is required. If you invoke memory language in a load-bearing way, say whether the relevant surface is acting as a memory store, a regime-reentry packet, or a check/admission object instead of treating all persistence as one thing. If bounded state is doing real work, say what future tests, interventions, or challenge probes the packet is meant to answer cheaply, and prefer predictive sufficiency over recap completeness when the two come apart. If you merge, drop, or compress bounded-state surfaces, say what future-equivalence class you are preserving, what continuation decision remains invariant, and what first lost distinction would show the compression was too aggressive. If two surfaces still look passively similar but may imply different next probes, repairs, or challenge branches, treat that as an intervention-equivalence question: name the intervention family, the target property or decision at stake, and the first branch divergence that would show the merge was only observationally safe. If you claim a compression or innovation improvement, name the distortion target, the main mismatch / prior-intrusion risk, and the first failure signature that would justify rollback or resync. If you materially revise canon or public belief state, name the trigger, the update gain (`low` / `medium` / `high`), and at least one challenge probe or reason no probe is needed. If the honest next move is not to revise, preserve a compact hold packet naming the anchor, blocker, brake posture (`hold`, `abstract`, or `recover-resync`), and unlock condition instead of letting non-movement dissolve into hedging prose. If reopen fidelity is materially in doubt, consider preserving a tiny sentinel panel naming the property monitored, the expected deviation signature, and whether a tripped canary calls for ordinary continuation, bounded rollback, or `recover-resync`. If rival continuation hypotheses materially differ, consider preserving a compact identification packet naming the hypothesis split, the observation sought, and what continuation decision that observation gates. If a live ambiguity class survives that first diagnostic move, consider preserving a compact homing packet naming the ambiguity class, the probe family or branch rule, the orientation/update rule, and the stop or escalation condition. If several plausible identifying, homing, witness, or challenge probes compete, preserve a compact probe-economics packet naming the candidate probe family, the gated decision, the rough cost class, the expected split power, the nearest deferred alternative, and the stop or escalation rule; prefer the cheapest probe expected to change the next continuation decision. If ambiguity is being reduced sequentially rather than in one shot, preserve a compact stopping packet naming the ambiguity class, the threshold or commit criterion, the continuation action licensed if crossed, the tolerated error / rollback posture, and the budget-exhaustion fallback; distinguish probe choice from stop choice. If evidence must accumulate across multiple probes or revisions, consider preserving a compact continuation monitor naming the monitored property or ambiguity split, the accumulating evidence state or score, the update or shrink rule, the reset or stitching rule, and how the monitor couples to the stop rule; distinguish the monitor from the threshold itself. If a phrase, prompt pair, id, witness, or canary might both steer and score, preserve a compact observer/actuator split naming the observer surface, actuator surface, allowed coupling, independent witness, and self-certification risk so the same local handle does not quietly become its own judge. If a vivid handle, witness, or privileged prompt surface seems unusually potent, consider preserving a compact negative-control handle or sham packet naming the active surface, the matched sham or negative control, the expected differential signature, the pass/fail rule, and the retire or escalation consequence if the differential collapses. If a load-bearing judgment could be contaminated by author attribution, handle prestige, or same-session history, consider preserving a compact blind packet naming the judged artifact or property, the scrubbed or relabeled view, what metadata is hidden, the reveal or unblinding rule, and the disagreement or escalation consequence if the blind and unblinded reads diverge. If prior assistant-side history may be carrying stale framing, errors, or pseudo-memory rather than genuinely needed evidence, consider preserving a compact assistant-echo filter naming the judged task or continuation property, the kept user-side anchor, the omitted or thinned assistant-side surface, the expected invariance or gain signature, and the reinclusion or escalation consequence if omission fails. If a rationale, chain-of-thought, or scratchpad is starting to look load-bearing, consider preserving a compact reasoning firebreak naming the judged task, decision, or continuation property, the public extract kept in canon, the trace surface withheld or quarantined, the allowed role of that withheld trace, and the exposure, reinclusion, or escalation consequence if the extract later proves insufficient. If you invoke timescale stratification or consolidation-lane language, name the fast / medium / slow lane at issue and the transfer rule (`refresh`, `consolidate`, `demote`, or `expire`) rather than treating memory as undifferentiated persistence. If a real working phase ended, consider preserving a compact phase boundary / rollover packet naming what phase just closed, what persists, what resets or cools, and what new operating question now governs ordinary continuation. If a revision invokes vector / basin / chart / tangent / atlas language in a load-bearing way, preserve at least one invariant claim, observable, or operational contract that should survive a chart switch, and say what remains chart-specific instead of letting geometry carry the status alone. If two short revision paths are implicitly supposed to preserve the same operative consequence, consider preserving a tiny loop-closure / commutator probe naming the shared anchor, the compared paths, the closure target, and the first mismatch that would count as material closure error. If a revision is implicitly relying on some local variation being harmless, consider preserving a tiny continuation margin / guard band naming the protected property, the perturbation family, and the first failure signature that would justify bounded rollback, a hold packet, or `recover-resync`. If a fragile boundary is live, consider preserving a tiny witness set / boundary panel; name the property discriminated and the drift signature that would show the panel has gone stale. If you invoked stable continuation-regime language, preserve at least one discriminating probe or countermodel instead of letting the phrase function as prestige shorthand. If you invoked public hidden-state / re-entry-ABI language, keep state packet, evidence packet, and check packet explicitly distinct. If a packet, prompt pair, or re-entry surface is being treated as a stable loader for operative state, preserve a compact conformance witness naming the interface surface or claimed loader, the supported model-wrapper-context family, the minimal conformance test or metamorphic check family, the first non-conformance or drift signature, and the narrowing, demotion, or fallback consequence rather than letting one local success silently become an interface claim. If you promoted or demoted anything, preserve the compact promotion contract. If a substantial nearby rejected move mattered, preserve a compact counterfactual shadow instead of letting the accepted move erase it. If a canon-level claim is materially time-sensitive, consider whether it needs a decay-watch entry. If drift, stale reopen, or context corruption is part of the situation, use `MV-0010` / `recover-resync` explicitly rather than hand-waving recovery. Do at least one hygiene/meta-engineering improvement. Run `make lint`, package the archive, and provide a working link to the latest DelayBasin-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip.
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
Continue the sufficiency-witness pass with one high-leverage reduced packet only. Prefer the smallest core-only replay trial that says whether the packet is actually enough, what fixed or withheld context family matters, what degradation is tolerated, and when the archive should reinflate or demote the reduced packet. Run lint and package the release.
```
