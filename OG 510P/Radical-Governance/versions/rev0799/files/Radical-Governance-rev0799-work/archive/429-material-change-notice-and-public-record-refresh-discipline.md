# 429 — Material-change notice and public-record refresh discipline

## One-line thesis

When a consequential public AI system changes in scope, data, model, provider, phase, or operating context, every public record about it should be refreshed before or at the moment the change takes effect.

## Why this matters

Public AI systems often drift faster than their public documentation.

A notice page may describe a pilot while the system is now in production. A transparency record may name one dataset while a retrained model now depends on another. An impact assessment may describe one workflow while support staff are using a much broader intervention script. The result is not merely stale paperwork; it is a public record that no longer describes the governed system.

Official guidance already rejects silent drift. UK ATRS guidance says substantive changes should trigger an updated record, renewed internal clearance, and record refresh, with examples including a pilot moving to production, new datasets used to train or refine the tool, or a change to the broader operational process. Canada’s Algorithmic Impact Assessment guidance says the AIA should be completed again before production, published as final results, and reviewed and updated on a scheduled basis and when the functionality or scope of the system changes. NIST’s AI RMF Playbook also calls for change management inside post-deployment monitoring and for mechanisms to communicate and acknowledge substantial changes.

The archive should therefore treat **public-record refresh discipline** as a release gate, not a clerical afterthought.

## Pattern pack

### 1. Define material change broadly enough to catch real governance shifts

A material change is not limited to a full rebuild. It should include changes such as:

- pilot to production promotion,
- retraining on new data,
- a changed decision threshold,
- a new model or model family,
- a new external provider,
- expanded user population,
- a broader policy purpose,
- different operator discretion,
- different appeal or fallback routes.

If the public would care about the change, governance should care too.

### 2. Refresh all outward-facing records together

A consequential change should trigger coordinated updates to the artifacts that tell the public and operators what the system is:

- transparency record or registry entry,
- public notice and explanation materials,
- impact assessment or rights analysis,
- appeal packet templates,
- operator scripts,
- support and assisted-digital guidance,
- source indexes and release notes where used.

One fresh record surrounded by stale companions is still governance drift.

### 3. Re-clear ownership before the changed system goes live

Updated public records should pass through renewed internal clearance by the responsible owner and relevant legal, policy, operational, communications, and accessibility functions where needed. This matters because a changed system may require:

- different oversight arrangements,
- new operator training,
- new fallback planning,
- new stakeholder communication,
- revised incident thresholds.

A refreshed record without renewed ownership is only a version bump.

### 4. Publish dated deltas, not just overwritten descriptions

Users, watchdogs, and future operators should be able to tell what changed and when. Prefer:

- visible effective dates,
- version numbers or release windows,
- short change logs,
- archived prior versions where practical,
- links between current notices and previous states.

This supports accountability when the public needs to compare pre-change and post-change behavior.

### 5. Re-notify affected operators and user-facing teams

A material change is not complete when engineering ships it. The institution should confirm that:

- frontline staff understand the new behavior,
- appeal and complaint handlers know what changed,
- assisted-digital and human-channel teams can explain the updated process,
- monitoring and incident teams know any new thresholds,
- relevant communities are told when the practical experience has changed.

Silence inside the institution often becomes confusion outside it.

### 6. Block silent scope creep with release gates

A changed system should not reach live use until the corresponding governance artifacts are refreshed. For higher-risk contexts, the release gate should require:

- updated public record,
- updated impact or rights analysis,
- updated support scripts,
- updated rollback plan,
- confirmation that notices and recourse routes still match the new system.

If documentation can lag indefinitely behind a production change, the institution has no disciplined public release process.

### 7. Tie change refresh to fallback, retraining, and review windows

Every material change should ask three practical questions:

- what new failure modes does this introduce,
- what operator or reviewer retraining is required,
- what review window will verify the change behaved as claimed.

This keeps record refresh connected to operational reality rather than publication alone.

## Guardrails

- Do not define “material change” so narrowly that major scope expansion becomes invisible.
- Update public artifacts before or at launch, not weeks later.
- Keep archived versions or dated change notes where practicable.
- Re-clear records when datasets, model families, providers, or workflows materially change.
- Make sure notice, appeal, and support materials move in sync.

## Failure modes

- **stale transparency**: the public record still describes last quarter’s system.
- **silent promotion**: a pilot quietly becomes production without a refreshed record.
- **partial refresh**: one artifact updates while notices, support scripts, or impact documents stay old.
- **scope creep by release note**: the operational change is major but described as minor maintenance.
- **operator surprise**: frontline teams learn about a material change only from user complaints.

## Practical tests

A refresh discipline passes when it can answer yes to all of the following:

1. Is there a broad and workable definition of material change?
2. Do transparency, notice, impact, appeal, and support artifacts refresh together?
3. Does a material change trigger renewed internal clearance and ownership?
4. Can the public tell what changed and when it changed?
5. Is live release blocked until the changed system’s public record matches reality?

## Compression rule for the archive

If the public record still describes yesterday’s system, today’s system is being governed with **expired notice**.
