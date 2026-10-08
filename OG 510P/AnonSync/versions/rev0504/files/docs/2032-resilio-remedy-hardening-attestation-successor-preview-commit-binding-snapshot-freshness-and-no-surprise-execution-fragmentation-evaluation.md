# Resilio remedy-hardening attestation successor preview/commit binding, snapshot freshness, and no-surprise execution fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a risky action is legitimate
- the chosen actuator looked least-broad
- an execution envelope was reviewed
- guardrails can be armed and runtime overspill can be discussed honestly

That is still weaker than answering a sharper question:

**is the run that is about to execute still the same run that was reviewed?**

That question deserves its own family because `same action name`, `same operator intention`, `same successor world`, `same folder label`, and `same link still visible` are not enough to justify `no surprise execution`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many moving parts, but it still leaves preview-to-commit sameness spread across unrelated articles:

- linked devices can automatically make all folders available across the linked set
- approvals are remembered by default unless operators deliberately require approval every time
- pending folders can auto-connect later if the sharer had approved that person before
- folder rescans happen on start and every 600 seconds by default
- settings saves happen every 600 seconds by default
- pause still allows delete propagation, rescanning, and indexing

That is useful candor, but it means the operator still reconstructs `was the reviewed picture still current at commit time?` from several convenience and background-behavior pages rather than from one typed preview/commit object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- preview generated once
- preview still fresh now
- preview bound to this exact run
- topology unchanged since preview
- approval facts unchanged since preview
- auto-arrival set unchanged since preview
- background scan or save clocks did not materially move the world
- execute-if-unchanged gate satisfied
- no-surprise execution honestly earned

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **reviewed execution envelope is weaker than bound preview/commit legitimacy**
- **same plan identifier is weaker than same reviewed snapshot**
- **same reviewed snapshot is weaker than same snapshot still fresh inside its validity window**
- **fresh snapshot is weaker than execute-if-unchanged proof at commit time**
- **`no obvious change noticed` may never impersonate `no material drift occurred`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- reviewed snapshot identifier
- snapshot scope
- freshness window
- invalidation triggers
- pre-commit drift check result
- execute-if-unchanged gate
- commit token binding
- same-run versus re-review requirement
- strongest honest sentence and blocked stronger no-surprise sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor preview/commit binding contract sheet**
- **successor preview/commit binding review**
- **successor preview/commit binding proof**
- **successor preview/commit binding timeline**
- **successor preview/commit binding lineage receipt**
