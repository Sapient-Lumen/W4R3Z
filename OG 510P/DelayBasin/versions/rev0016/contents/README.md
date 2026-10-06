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
