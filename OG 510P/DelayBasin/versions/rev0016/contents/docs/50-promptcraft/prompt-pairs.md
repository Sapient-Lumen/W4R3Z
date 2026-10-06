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
9) confirm `make lint`
10) provide the latest release link
```

**Continuation prompt**

```text
Continue researching online and evolving DelayBasin with tight, high-leverage revisions. Keep the archive small, wired, and cumulative. Make at least one bold but disciplined speculative move, and place it in canon or quarantine honestly. Name the certified move classes you actually instantiated. If you promoted or demoted anything, preserve the compact promotion contract. If a substantial nearby rejected move mattered, preserve a compact counterfactual shadow instead of letting the accepted move erase it. If a canon-level claim is materially time-sensitive, consider whether it needs a decay-watch entry. If drift, stale reopen, or context corruption is part of the situation, use `MV-0010` / `recover-resync` explicitly rather than hand-waving recovery. Do at least one hygiene/meta-engineering improvement. Run `make lint`, package the archive, and provide a working link to the latest DelayBasin-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip.
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
