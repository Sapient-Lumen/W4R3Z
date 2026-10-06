# DelayBasin: living archive for archive-method under long-run co-construction

**North star:** see [`docs/00-meta/charter.md`](docs/00-meta/charter.md)

Revision notes: [`CHANGELOG.md`](CHANGELOG.md)

DelayBasin is a **living archive** for researching, specifying, and stress-testing a method of building long-run human–LLM archives that do more than store prior turns. The working hypothesis is that a disciplined archive can act as:

- a **constitutional stack** for continuation,
- an **exosomatic delay-embedding** across context-window death,
- a **drift-resistant promptcraft substrate**,
- a **bounded constitutional state** small enough to reopen and rich enough to reconstruct the project,
- a **portable state interface** pairing compact state, stable addressing, and deterministic acceptance checks,
- a **typed continuation protocol** separating workflow requests, bounded state, and admission checks,
- a growing **control lexicon / constitutional pidgin** that may function as an external protocol for re-entry,
- a split between **certified core vocabulary** and provisional/private handles so canon does not silently depend on drifting language,
- a small set of **certified move classes** so the archive preserves what kinds of transitions are allowed to count as progress,
- a compact **decay patrol** so canon-level trust can cool, shrink, or demote when temporal validity rots,
- a **legitimacy kernel** and recovery route so the archive can resynchronize after transient corruption instead of merely carrying forward stylish damage,
- a compact **revision receipt / audit object** so each packaged revision says what transition occurred, what status changed, and why it counted,
- a tiny **counterfactual shadow** so substantial revisions preserve one nearby rejected alternative instead of letting the accepted move rewrite local history,
- a **stable continuation regime / regime-probe** surface that treats continuity as possible mode re-entry rather than assuming transcript replay or mistaking coherence for proof,
- a **public hidden-state / re-entry ABI** surface that separates compact operative state from larger evidence and check packets,
- a **public belief-state** surface that treats archive state as updateable project posterior rather than retained fact dump,
- an **innovation-packet / reconciliation** surface that prefers anchored deltas against shared public state over repeated whole-archive replay,
- a **continuation rate–distortion / prior-intrusion** surface that treats bounded archive state as a compression problem with explicit distortion targets and mismatch risks,
- an **update-gain / challenge-probe** surface that treats substantial revisions as belief-state updates with explicit trigger, rewrite force, and adversarial checks,
- a **hold-packet / epistemic-brake** surface that treats honest non-movement as a first-class continuation move with an explicit blocker and unlock condition,
- a **sentinel-panel / reopen-canary** surface that treats tiny high-sensitivity probes as early checks on whether the intended continuation basin actually reconstructed,
- a **dual-control revision / identification-packet** surface that treats some edits as active disambiguation moves chosen to identify which continuation is legitimate before canon advances,
- a **timescale-stratification / consolidation-lane** surface that treats archive objects as fast refreshable, medium revisable, or slow constitutional state with explicit refresh, consolidation, demotion, or expiry routes,
- a **phase-boundary / rollover-packet** surface that treats some revisions as explicit working-regime transitions with named carry-forward and reset rules rather than smoothing every change into one continuous stream,
- a **gauge-discipline / canonical-chart / invariant-claim** surface that treats coordinate-loaded archive language as a local chart unless the invariant substance and chart-specific remainder are both named,
- a **loop-closure / commutator-probe / path-dependence** surface that tests whether supposedly harmless reorderings or chart switches actually return to the same operative continuation state,
- a **continuation-margin / guard-band / perturbation-budget** surface that treats some archive objects as needing explicit local slack assumptions rather than only pointwise legitimacy,
- a **control-authority / steering-effort / leakage-budget** surface that treats some archive surfaces as candidate low-bandwidth actuators whose value depends on what they move, how much effort they require, and what collateral or endogenous resistance accompanies them,
- a place where **practice, observation, mechanism, speculation, disagreement, and quarantine** are kept distinct rather than laundered into each other,
- and a protected lane for **risky transformer self-speculation** that would otherwise get prematurely flattened.

This repo is not an academic paper and not merely a notebook. It is an **operational research archive**.

## How to navigate

0. Start here: [`START_HERE.md`](START_HERE.md)
1. Mile-high synthesis: [`docs/00-meta/trajectory-map.md`](docs/00-meta/trajectory-map.md)
2. Editing runbook / anti-amnesia guardrail: [`docs/00-meta/llm-runbook.md`](docs/00-meta/llm-runbook.md)
3. Method stack: [`docs/10-method/`](docs/10-method/)
4. Constitutional surfaces: [`docs/20-constitution/`](docs/20-constitution/)
5. Speculation stack: [`docs/30-speculation/`](docs/30-speculation/)
6. Session seed materials: [`docs/40-session/`](docs/40-session/)
7. Prompt-pair lane: [`docs/50-promptcraft/prompt-pairs.md`](docs/50-promptcraft/prompt-pairs.md)
8. Quarantine lane: [`docs/90-quarantine/`](docs/90-quarantine/)

## What this archive is trying to do

Turn a fuzzy, live, recursive practice into stable diff surfaces:

practice → observations → competing mechanisms → constraints/invariants → promptcraft → ratchets → release artifact

The archive should make it easier to continue as the **same project** without pretending it has solved what it has not solved.

## Imported hygiene pattern

DelayBasin explicitly imports a reusable hygiene stack observed in SlopOS and TriKEM:

- short mile-high map,
- must-read runbook,
- stable ids and registries,
- explicit open questions,
- changelog discipline,
- CI-friendly drift checks,
- release packaging with predictable names.

See [`docs/10-method/slopos-trikem-hygiene-extraction.md`](docs/10-method/slopos-trikem-hygiene-extraction.md).

## Archive discipline (size + honesty + risk)

- Prefer **tight summaries and stable ids** over long pasted text.
- Research online when it sharpens the archive, but keep only the compact load-bearing trace of that research.
- Distinguish **observed / inferred / speculative / adversarial-countermodel / quarantined-wild-speculation** status explicitly.
- Every new document must be linked from [`docs/README.md`](docs/README.md) and at least one registry or trajectory surface.
- Prompt pairs are first-class artifacts, not disposable scaffolding.
- Risk is mandatory, but **quarantine exists so risk does not silently become canon**.
- Do not keep PDFs or other large non-crucial artifacts in the long-term release bundle; temporary scratch belongs in quarantine and should usually be removed before packaging.
- The release bundle name is:
  `DelayBasin-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`

## Current working name

**DelayBasin** = delay-embedding hypothesis + basin-shaping hypothesis.

The name is intentionally provisional. It is good enough to work under.


Current live extension: DelayBasin now treats **revision receipts / audit objects** as part of continuation law: each revision should preserve a compact machine-readable object saying what transition occurred, what status moved, and which checks made it admissible.
A fresh extension is that substantial revisions should also preserve a tiny **counterfactual shadow** naming one nearby rejected move and why it was not admitted.
A newer extension is that DelayBasin now treats **stable continuation regimes** as a serious mechanism candidate, but only alongside explicit **regime probes** that try to distinguish mode re-entry from local mimicry or detectable compliance.
A fresh extension is that DelayBasin now treats **public hidden state / re-entry ABI** as a serious mechanism candidate, but only if state packet, evidence packet, and check packet remain explicitly distinct.
A newer extension is that DelayBasin now treats **public belief state under partial observability** as a serious mechanism candidate, but only if uncertainty, rewriting pressure, and rival explanations remain explicit rather than collapsing back into retention talk.
A fresh extension is that DelayBasin now treats **innovation packets and reconciliation under delay** as a serious design/mechanism candidate: once shared public state exists, later revisions should usually send anchored innovations rather than ritual whole-archive replay.
A newer extension is that DelayBasin now treats **continuation rate–distortion under model mismatch** as a serious design/mechanism candidate: compression wins should name a distortion target, a prior-intrusion risk, and the first failure signature rather than treating smaller as automatically better.
A fresh extension is that DelayBasin now treats **update gain, surprise gating, and challenge probes** as a serious design/mechanism candidate: substantial revisions should name what triggered movement, how strongly canon should move, and what compact challenge would catch overreaction or false inertia.
A newer extension is that DelayBasin now treats **witness sets / boundary panels** as a serious design/mechanism candidate: some fragile distinctions may be preserved better by a tiny discriminative panel than by additional recap prose, but the stronger basin-support-vector story remains quarantined.
A fresh extension is that DelayBasin now treats **hold packets / epistemic brakes** as a serious design/mechanism candidate: sometimes the honest next move is to keep canon fixed, abstract uncertainty, or escalate to `recover-resync`, and that non-movement should remain public and auditable rather than dissolving into hedging prose.
A newer extension is that DelayBasin now treats **sentinel panels / reopen canaries** as a serious design/mechanism candidate: tiny high-sensitivity probes may detect wrong-basin continuation earlier and more cheaply than recap quality alone, but the stronger textual-tangent story remains quarantined.

A fresh extension is that DelayBasin now treats **dual-control revisions / identification packets** as a serious design/mechanism candidate: some small edits should actively disambiguate rival continuation hypotheses before the archive spends trust on a canon update, but the stronger textual-observability story remains quarantined.

A newer extension is that DelayBasin now treats **timescale stratification / consolidation lanes** as a serious design/mechanism candidate: some public objects should refresh quickly, some should consolidate slowly, and some should explicitly demote or expire instead of all behaving like the same kind of memory, while the stronger public-metaplasticity story remains quarantined.

A fresh extension is that DelayBasin now treats **phase boundaries / rollover packets** as a serious design/mechanism candidate: some revisions should explicitly mark that one working phase has ended, serialize what persists and what cools or resets, and carry a compact folded packet into the next phase, while the stronger public-reset-gate story remains quarantined.

A newer extension is that DelayBasin now treats **gauge discipline / canonical charts / invariant claims** as a serious design/mechanism candidate: coordinate-loaded language may be useful locally, but canon should say what survives a chart change and what is merely one convenient description, while the stronger public-atlas story remains quarantined.

A fresh extension is that DelayBasin now treats **loop closure / commutator probes / path dependence** as a serious design/mechanism candidate: some local reorderings or chart switches are implicitly claimed to be harmless, and the archive should sometimes test that claim explicitly rather than assuming route-independence, while the stronger public-holonomy story remains quarantined.

A newer extension is that DelayBasin now treats **continuation margins / guard bands / perturbation budgets** as a serious design/mechanism candidate: some archive objects need explicit local slack assumptions around what perturbations should remain harmless, while the stronger public-robustness-radius story remains quarantined.

A fresh extension is that DelayBasin now treats **control authority / steering effort / leakage budgets** as a serious design/mechanism candidate: some phrases, ids, prompt pairs, witness panels, or canaries may function as real low-bandwidth handles over continuation state, but only if the archive can say what they move, how much effort they seem to require, and what leakage or endogenous resistance accompanies them, while the stronger public-controllability-map story remains quarantined.

A newer extension is that DelayBasin now treats **balanced archive reduction / dual salience / minimal realization** as a serious design/mechanism candidate: under real bounded-state pressure, some surfaces may deserve portable-state slots because they are jointly good for observation and control and because their truncation consequence is legible, while the stronger public-Hankel-spectrum story remains quarantined.
