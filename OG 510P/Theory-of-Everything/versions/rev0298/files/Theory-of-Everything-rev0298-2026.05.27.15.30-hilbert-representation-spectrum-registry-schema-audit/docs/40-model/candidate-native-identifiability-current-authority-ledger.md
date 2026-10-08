# Candidate-native identifiability current-authority ledger

This document is the current-authority consolidation surface for candidate-native identifiability custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the eight-field route, replace evidence intake, replace supersession / decay, replace challenge handling, replace release sealing, replace head adoption, replace succession, replace branch arbitration, replace retirement / vacancy, replace reinstatement / thaw, certify a lane as closed, promote any lane, demote any lane, or turn a current release into scientific evidence.
It answers the next operational question after head-reinstatement / thaw:

> once adoption, succession, branch arbitration, retirement, vacancy, and reinstatement rows can all produce locally valid custody states, how does the archive state exactly which bounded `OQ-0057` authority object is current for a given target scope without letting multiple rows, generated mirrors, older heads, repaired carriers, or summaries all claim authority at once?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`
- `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`
- `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`
- `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md`
- `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md`
- `docs/40-model/candidate-native-identifiability-decision-trace-docket.md`
- `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-response-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md`
- `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`
- `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`
- `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md`
- `docs/40-model/candidate-native-identifiability-export-claim-docket.md`
- `docs/40-model/candidate-native-identifiability-reimport-firewall.md`
- `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md`
- `docs/40-model/candidate-native-identifiability-release-seal-docket.md`
- `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`
- `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`
- `docs/40-model/candidate-native-identifiability-head-succession-docket.md`
- `docs/40-model/candidate-native-identifiability-head-branch-arbitration-docket.md`
- `docs/40-model/candidate-native-identifiability-head-retirement-vacancy-docket.md`
- `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The post-release custody stack can now admit, verify, adopt, succeed, arbitrate, retire, vacate, and reinstate bounded `OQ-0057` authority.
That stack is safer than a single current-head sentence, but it also creates a new failure mode: local custody rows can be quoted selectively.
A later summary might point to an adopted head, a successor head, a branch-loser, a retirement survivor, a thawed slice, and a generated mirror at the same time, then let whichever one is rhetorically convenient carry current authority.

The correct posture is:

**current authority is a scoped ledger state, not a vibe inherited from the newest bundle. For every target quotient or scope in which `OQ-0057` posture is reused, the archive must name one current authority object, its source custody row, its surviving owner rows, its residual cap, its excluded carriers, its rollback / quarantine handle, and the next admissible transition. If two authority objects overlap without a disjoint scope split or a branch-arbitration result, the affected scope freezes. If the ledger row cannot be replayed from canonical owners rather than generated mirrors or exported summaries, it freezes.**

Use this ledger when:
- a summary, release note, START_HERE mirror, README sentence, or handoff wants to say which `OQ-0057` posture is current;
- a verified carrier, adopted head, successor, branch-arbitrated head, retirement survivor, or reinstated head is being reused across documents;
- two or more custody rows appear to survive for the same target quotient or record denominator;
- a scope split claims that different heads are current for different target slices;
- a rollback, quarantine, vacancy, retirement, or historical pointer must be kept visible in the same handoff as a bounded current head;
- a future merge or reimport tries to treat generated mirrors, release packages, receipts, abstracts, or external paraphrases as if they named current authority by themselves;
- a future handoff says “current head,” “current authority,” “active posture,” “safe to carry forward,” “restored head,” “bounded successor,” or “standing result” for `OQ-0057`.

Do not use this ledger to score a new physics result, compare families, introduce a new route field, or create a followthrough item by wish.
New artifacts still start at evidence intake.
Old credit still passes supersession / decay.
Conflicts still pass adjudication.
Release carriers still pass seal verification, adoption, succession, branch arbitration, retirement / vacancy, and reinstatement / thaw as needed.
This ledger records which custody result is allowed to be called current for a declared scope after those controls have run.

## Current-authority states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, head-adoption states, head-succession states, head-branch arbitration states, head-retirement states, or head-reinstatement states.
They say which authority object is allowed to carry current `OQ-0057` posture for a declared scope after the relevant upstream custody states have been resolved.

| Code | Current-authority state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `CA0` | no current-authority claim | No surface is trying to reuse or declare current `OQ-0057` authority. | Leave this ledger unused. | Auditing every ordinary edit as a head decision. |
| `CA1` | historical / pointer-only authority | A prior head, bundle, branch, or generated mirror is being used for navigation or history only. | Keep it pointer-only and route any live claim through lineage merge, reimport, or evidence intake. | Treating historical usefulness as current authority. |
| `CA2` | verified carrier, non-authority | A package or mirror verifies as a sealed carrier but has not passed adoption, succession, arbitration, retirement, or thaw for the relevant scope. | Permit citation as a carrier while preserving non-head status and no-evidence wording. | Treating local verification as current posture. |
| `CA3` | adopted bounded authority | A verified carrier has been adopted as the bounded current authority for a scope without successor or branch complication. | Name the adoption row, owner rows, residual cap, and rollback handle. | Treating adoption as route promotion or witness closure. |
| `CA4` | successor / arbitrated bounded authority | A later continuation or branch result has become current for a declared scope after succession or arbitration. | Name predecessor, successor / branch state, displaced carriers, cap, and rollback. | Letting revision recency, polish, or plurality decide authority. |
| `CA5` | scoped split authority | More than one authority object is current only because the target quotient, record denominator, or owner-row scope has been explicitly split and the slices do not overlap. | State the split boundaries, row owners, caps, exclusions, and recombination prohibition. | Hiding branch conflict inside vague “both are useful” language. |
| `CA6` | retired / vacant / quarantined authority | The affected scope has no current authority object except historical pointers or frozen owner rows after retirement, vacancy, or quarantine. | Preserve vacancy / quarantine wording, rollback, re-entry condition, and barred reuse. | Forcing a weak successor or reviving a predecessor because current status is uncomfortable. |
| `CA7` | reinstated bounded authority | A retired, vacant, quarantined, or historical-only object has re-entered current use after reinstatement / thaw review. | Name the reopened retirement row, trigger, restored scope, surviving cap, and re-quarantine handle. | Treating repair, nostalgia, or answered objections as automatic full restoration. |
| `CA8` | ledger inconsistency / freeze | The archive cannot identify one current authority state for an overlapping scope, or the ledger row cannot replay from canonical owner surfaces. | Freeze the affected scope until branch, retirement, thaw, lineage, or owner-row repair resolves it. | Letting multiple incompatible heads survive through summary ambiguity. |

## Mandatory current-authority row

Fill this row whenever a surface wants to reuse current `OQ-0057` posture rather than merely point to history.
For `CA0`, no row is needed.
For `CA1`, a compact historical-pointer note is enough unless the object is later cited as current.

| Field | Required content | Failure mode if absent |
|---|---|---|
| Target scope | The target quotient, route row, record denominator, family / lane slice, or release-custody scope for which authority is being declared. | One head silently governs more scope than it earned. |
| Authority object | The exact owner row, release root, custody row, or scoped slice being treated as current. | Generated mirrors or summaries become head objects. |
| Source custody state | The upstream `HA`, `HS`, `HB`, `HR`, or `HI` row that makes the authority claim possible. | Current authority appears without admission history. |
| Current-authority code | One of `CA0`–`CA8`. | Mixed states get retold as a stable head. |
| Surviving owner rows | The canonical rows that still carry route, cap, challenge, and public-bridge support. | Old or derivative credit carries posture without owner replay. |
| Excluded / non-current carriers | Bundles, branches, mirrors, summaries, retired heads, or historical pointers that are explicitly not current for this scope. | Branch losers or stale mirrors quietly re-enter. |
| Residual cap and no-closure wording | The minimum cap that must travel with the authority object. | Bounded `S3`, borrowed-public, package-grain, or non-comparable status evaporates. |
| Scope split / overlap rule | Whether the authority is global for the target scope, split, or barred from overlapping another row. | Two heads govern the same question through prose ambiguity. |
| Export sentence | The exact safe wording allowed in README / START_HERE / release notes / handoffs. | Later summaries improvise stronger language. |
| Next admissible transition | The only allowed next custody move: adoption, succession, arbitration, retirement, reinstatement, lineage rebase, reimport split, or freeze. | Future edits jump dockets or choose a convenient path. |
| Rollback / quarantine handle | The row, state, or trigger that withdraws authority if replay fails. | Broken authority persists because no one knows where to roll back. |

## No co-current authority rule

For any declared target scope, `OQ-0057` may have many historical carriers, many useful summaries, many bounded field rows, and many generated mirrors.
It may not have two overlapping current authority objects unless a scope split is explicit and non-overlapping.

A valid split must say:
- what target quotient or record denominator separates the slices;
- which owner rows remain valid in each slice;
- which residual cap travels with each slice;
- which summaries must not recombine the slices;
- which branch, challenge, or retirement row reopens if the split boundary becomes disputed.

If those declarations are missing, the correct state is `CA8`, not “multiple current views.”
This protects the archive from a common custody laundering move: keeping one head for route optimism, another for conservative no-closure wording, another for package cleanliness, and another for historical continuity.

## Source precedence

When current authority is disputed, source precedence is:

1. canonical owner rows and route-field ledgers;
2. lifecycle dockets that explicitly update or preserve those owner rows;
3. custody dockets that admit, succeed, arbitrate, retire, or reinstate bounded authority;
4. release manifests, receipts, status files, and context packs as carriers;
5. generated mirrors and indexes as navigation aids;
6. README / START_HERE prose as export mirrors;
7. user-facing answers, abstracts, handoff summaries, and external paraphrases as pointer-only derivatives.

No lower tier may override a higher tier.
A lower tier may only trigger reimport, lineage merge, branch arbitration, retirement, reinstatement, or ledger repair.
If a generated mirror says one thing and the owner rows say another, the mirror is repaired; the route is not promoted.
If a release package verifies but the owner rows do not replay, the package remains a verified non-authority carrier.
If an exported summary is clearer than the underlying rows, clarity is not evidence; the summary must reanchor or be demoted to pointer-only use.

## Mapping from head lifecycle dockets

| Upstream result | Ledger consequence | Notes |
|---|---|---|
| `HA7` adopted bounded current head | Usually `CA3`. | Only for the declared adoption scope and cap. |
| `HS7` adopted bounded successor | Usually `CA4`. | Requires predecessor and displaced-carrier treatment. |
| `HB7` arbitrated bounded head | Usually `CA4`, or `CA5` if arbitration produces a commuting split. | Branch losers become excluded carriers. |
| `HR1` historical pointer only | `CA1`. | Usable for navigation, not current posture. |
| `HR2` carrier retirement with owner survival | Usually `CA2` for the carrier and prior owner rows remain owner-row evidence only. | Do not convert carrier repair into route credit. |
| `HR3` / `HR4` scoped or challenge retirement | `CA6` for the retired scope unless a safe split remains. | Surviving slices need explicit caps. |
| `HR6` successorless vacancy | `CA6`. | Absence of replacement is not predecessor revival. |
| `HR7` retirement-complete bounded standby | `CA6` with clear re-entry condition. | Standby is not current authority. |
| `HI3` owner-row thaw after carrier repair | Usually `CA2` unless adoption / succession also runs. | Carrier repaired; authority not automatically restored. |
| `HI4` scoped owner reinstatement | `CA5` or `CA7` depending on overlap. | Split boundaries must be explicit. |
| `HI5` challenge-repaired reinstatement | `CA7` only after challenge closure, cap, and owner replay survive. | Answered challenge is not full restoration by default. |
| `HI6` custody-restored candidate | `CA2` or `CA8` until current-authority row is complete. | Candidate status is not head status. |
| `HI7` bounded reinstated head | `CA7`. | Must keep rollback / re-quarantine handle. |
| Any unresolved overlap | `CA8`. | Freeze until arbitration, retirement, thaw, or lineage repair resolves the overlap. |

## Current-authority handoff template

When a future handoff needs to say what `OQ-0057` posture is current, use this shape:

> For `[target scope]`, current authority is `[authority object]` under `[CA-code]`, sourced from `[HA/HS/HB/HR/HI row]`. The surviving owner rows are `[owner rows]`; excluded carriers are `[non-current branches / mirrors / summaries]`; the residual cap is `[cap]`; the safe export sentence is `[wording]`; the next admissible transition is `[transition]`; rollback / quarantine is `[handle]`. This is current custody posture only, not route promotion, witness closure, or candidate-native identifiability closure.

If that sentence cannot be filled, the handoff should say the scope is `CA8` frozen rather than infer current authority from recency, package cleanliness, or summary polish.

## Export-safe sentence forms

Safe forms:
- “For this declared scope, the current authority carrier is bounded and cap-preserving.”
- “The sealed / verified package is a carrier, not evidence; current authority depends on the named ledger row.”
- “This historical head remains pointer-only unless reinstatement / thaw and current-authority ledger rows are filled.”
- “The scope is frozen because overlapping candidates have not been arbitrated or split.”

Unsafe forms:
- “The latest bundle is the current answer.”
- “The restored head is back.”
- “Both branches remain current.”
- “The verified package settles the posture.”
- “A clean successor supersedes the old head.”
- “The summary captures the current authority.”

## Interaction with release and restart surfaces

Release, restart, and handoff surfaces should not repeat the entire custody stack.
They should name this ledger when they need current `OQ-0057` authority and route details to canonical owner rows.
The compact export obligation is:

1. state whether the claim is authority-bearing or pointer-only;
2. if authority-bearing, name the `CA` state and source custody row;
3. preserve the minimum residual cap and no-closure wording;
4. state excluded carriers or branch losers if relevant;
5. name the rollback / quarantine handle.

This keeps README / START_HERE / context prose from becoming a second, unofficial head registry.
Those surfaces may mirror a ledger row, but they cannot create one.

## Authority-transition handoff

This ledger declares which bounded authority object is current for a scope; it does not, by itself, authorize later movement between ledger states.
If a future update changes, narrows, replaces, splits, vacates, quarantines, or restores a `CA` row, open `docs/40-model/candidate-native-identifiability-authority-transition-docket.md` and declare the prior authority row, proposed authority row, trigger, owner-row delta, displaced carriers, cap carry-forward, mirror / export consequences, and rollback / quarantine handle.

Without that transition row, the safe posture is that the old ledger row remains unchanged or the affected scope freezes; summaries, generated mirrors, release receipts, and user-facing handoffs cannot move current authority by themselves. If a transition row later fails or its rollback / quarantine handle fires, route through `docs/40-model/candidate-native-identifiability-authority-rollback-docket.md` before restoring a predecessor, preserving a successor, splitting a scope, vacating authority, or repairing mirrors as changed current posture.
