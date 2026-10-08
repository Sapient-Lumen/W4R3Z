# Candidate-native identifiability head-branch arbitration docket

This document is the post-succession arbitration surface for candidate-native identifiability custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace head adoption, replace head succession, certify a lane as closed, promote any lane, demote any lane, or let a branch race decide authority.
It answers the next operational question after the head-succession docket:

> if more than one later continuation claims to succeed the same adopted bounded `OQ-0057` head, or if one continuation wins one subset of owners while another wins a different subset, how does the archive choose, split, freeze, or roll back head authority without treating recency, package cleanliness, generated mirrors, or branch popularity as scientific evidence?

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
- `docs/40-model/candidate-native-identifiability-head-retirement-vacancy-docket.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

Head succession says when one candidate continuation may replace one adopted bounded head.
That is still underpowered when the archive has two or more candidate successors, a returned fork, a cherry-picked owner repair, a parallel packaging cleanup, a challenged continuation, or a scope-split branch where different successors are stronger for different owner rows.
Without a branch-arbitration surface, the archive can still leak authority through a quiet rule such as newest package wins, cleanest lint wins, highest revision id wins, most polished mirror wins, or broadest summary wins.

The correct posture is:

**branch arbitration is a custody decision over candidate successors, not a scientific vote and not a timestamp race. When multiple post-adoption continuations exist, the archive must name the predecessor head, enumerate all candidate successors and excluded non-successors, replay lineage and owner deltas for each candidate, compare them on the same residual-cap and no-closure denominator, decide whether their deltas commute, conflict, scope-split, or freeze, choose one bounded authority carrier only where owner precedence is replayable, and preserve rollback handles for every displaced or quarantined branch. If that arbitration cannot be replayed, no branch may become the unique current `OQ-0057` head by recency, zip cleanliness, generated mirrors, or editorial convenience.**

Use this docket when:
- two or more newer releases, forks, extracted trees, local edits, returned bundles, or cherry-picked surfaces claim successor authority over the same adopted `OQ-0057` head;
- one branch repairs mirrors while another changes owner rows;
- one branch closes a challenge while another preserves a stronger cap, narrower public bridge, or safer lineage;
- two branches both satisfy parts of the head-succession docket but touch overlapping route fields, readiness rows, caps, or public-bridge claims;
- a branch is stronger scientifically but weaker as a release carrier, or cleaner as a release carrier but weaker scientifically;
- a future handoff says “use the latest” while more than one candidate continuation remains visible;
- a rollback or quarantine must identify which predecessor, branch, or owner row remains authoritative.

Do not use this docket to score a new physics result, compare families, or pick the most promising theory.
That remains the job of the route ledger, evidence intake, lifecycle dockets, hostile controls, calibration, residual caps, and promotion gate.
This docket decides how competing successor candidates share, lose, freeze, or receive bounded head authority after ordinary head succession is insufficient.

## Head-branch arbitration states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, head-adoption states, or head-succession states.
They say how competing successor candidates are handled.

| Code | Head-branch state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `HB0` | no branch contest | Only one successor candidate is in play, or no current-head replacement is being considered. | Leave this docket unused and use head succession if needed. | Auditing ordinary single-branch work as a branch fight. |
| `HB1` | duplicate candidate | Multiple objects are byte-identical, mirror-equivalent, or same-head navigation copies. | Collapse to one carrier pointer; keep duplicates navigation-only. | Treating copies as independent confirmation or rival support. |
| `HB2` | metadata / mirror branch | One candidate only changes receipt, generated index, README, START_HERE, status, context, changelog, or package shell. | Keep it as carrier cleanup unless owner rows changed. | Letting mirror polish beat owner-row deltas. |
| `HB3` | incomplete branch set | Visible candidates are not all enumerated, lineage is unknown, or one branch lacks owner / validation / cap replay. | Freeze unique-head selection until the candidate set and predecessor relation are complete enough to compare. | Choosing among partially described branches by convenience. |
| `HB4` | commuting scope split | Branch deltas touch disjoint owner rows or compatible mirrors and can be merged without changing caps, challenge state, or rollback. | Merge narrowly, record both deltas, and rerun seal / verification / adoption / succession on the combined carrier. | Calling a mechanical merge scientific convergence. |
| `HB5` | owner-conflicting branches | Candidates change overlapping route fields, caps, challenge states, public bridge conditions, or readiness rows incompatibly. | Run conflict adjudication and branch-specific replay; no unique head until conflict closes or scope-splits. | Letting the newest branch overwrite unresolved owner disagreement. |
| `HB6` | asymmetric custody branch | One branch is scientifically stronger but carrier-unsafe, or carrier-clean but scientifically weaker, cap-erasing, challenge-frozen, or lineage-unsafe. | Split scientific input from carrier authority; preserve the safer bounded head and route the unsafe branch to intake, challenge, rebase, or quarantine. | Treating package hygiene and scientific merit as interchangeable. |
| `HB7` | arbitrated bounded head | The branch set is enumerated; lineage, owner deltas, caps, challenges, validation, mirrors, and rollback agree on a bounded winner or scoped merge. | Allow bounded current-head continuation with explicit displaced-branch pointers and residual caps. | Treating arbitration as `S4` / `S5` promotion or witness closure. |
| `HB8` | arbitration failure / freeze | Branch authority cannot be replayed, conflict remains unresolved, or a hidden candidate invalidates the branch set. | Freeze succession, roll back to the last adopted bounded head, or quarantine the branch family. | Letting unresolved branch competition set current posture. |

## Branch arbitration route sheet

Any future branch-arbitration claim should fill these fields before broad mirrors, release identity, or current-head posture change.

| Field | Required declaration |
|---|---|
| Predecessor adopted head | The last adopted bounded `OQ-0057` head from which the branch set descends or to which it is rebased. |
| Candidate branch set | Every visible release, fork, local edit, cherry-pick, generated artifact, returned bundle, and excluded duplicate relevant to the transition. |
| Branch lineage relation | Direct descendant, rebased descendant, fork, orphan edit, cherry-pick, metadata refresh, generated mirror, duplicate, or unknown for each candidate. |
| Owner-delta comparison | Which owner rows, route fields, readiness rows, caps, public bridges, or challenge closures each branch changes, preserves, narrows, or contradicts. |
| Custody comparison | Release seal, verification, adoption, succession, package boundary, mirror parity, root identity, and rollback status for each branch. |
| Cap / no-closure comparison | Minimum residual cap, target grain, record denominator, publicness condition, witness-owner boundary, earliest blocker, and no-closure wording per branch. |
| Conflict / commutation test | Whether deltas commute, require ordered merge, scope-split, conflict adjudication, challenge closure, or freeze. |
| Displaced-branch treatment | Navigation-only duplicate, superseded branch, scientific input only, fork candidate, challenge input, quarantine, or rollback handle. |
| Arbitrated head state | Which `HB` state applies, and whether any bounded current head, scoped merge, or freeze is authorized. |
| Future reentry rule | Which branch future editors should open first, which branch is historical only, and what triggers rollback or re-arbitration. |

## Branch arbitration rules

### 1. Enumerate before choosing

A branch choice is unsafe when it names only the branch being packaged.
The archive must first enumerate known alternatives: direct descendants, returned forks, local continuations, copied roots, generated archives, metadata repairs, and duplicate carriers.
Hidden or unclassified candidates default to `HB3` until they are ruled out, collapsed, or quarantined.

### 2. Compare owner rows separately from carrier hygiene

A candidate can have the best package boundary and the weakest owner-row basis.
Another can have a useful scientific delta but stale manifest identity, failed cap preservation, or broken mirror parity.
Carrier hygiene may let a branch travel; it cannot by itself elect the branch as the scientific or posture authority.
Scientific deltas may enter the evidence lifecycle; they cannot by themselves elect a broken carrier as head.

### 3. Deltas that commute may merge, but merged authority must be rebuilt

If two branches touch disjoint owner rows or one branch performs mirror cleanup while the other performs a compatible owner-row delta, the result can be an `HB4` scope split or narrow merge.
The merged carrier still needs release seal, verification, adoption, succession, and branch-arbitration replay.
A clean merge does not become independent confirmation, route promotion, or witness closure.

### 4. Overlapping owner conflicts freeze unique-head authority

If two branches disagree on a field score, cap, challenge state, public-bridge condition, readiness row, successor relation, or rollback handle, the archive should not let one branch overwrite the other by recency.
Use conflict adjudication and challenge closure.
If the conflict remains open, use `HB5` or `HB8` and roll broad mirrors back to the last adopted bounded head.

### 5. The most restrictive cap wins across branches unless a branch earns a narrower owner-level replacement

A branch cannot erase bounded package-grain `S3`, mixed-record denominator, borrowed-public bridge, named-discriminator pocket, witness-separated support, non-comparable row, or no-closure wording merely because another branch omitted it.
When branches disagree about caps, keep the stricter cap until owner-level evidence and residual-cap replay justify a narrower replacement.

### 6. A branch can be useful without becoming head

A fork can supply a challenge, a proof idea, a mirror repair, a validation hint, or a scientific delta that deserves intake.
That does not imply head authority.
The safe treatment is often: use branch content as evidence input, keep current head unchanged, and record a displaced-branch pointer.

### 7. Arbitration can produce a scoped winner rather than a single global winner

If one branch is authoritative for package identity and another is authoritative for a field-local correction, the correct result may be a scoped merge or branch-specific owner handoff rather than one global victor.
The resulting head must still state which parts were adopted, which parts were rejected, and which branch remains available only for rollback, challenge, or history.

### 8. Failed arbitration rolls back to the last adopted bounded head

If branch authority cannot be replayed, do not choose a README sentence, revision number, generated index, or zip name as the fallback.
The rollback target is the last adopted bounded head, then the last verified owner row, then quarantine if neither can be replayed.

## Current branch posture

Current safe branch use for `OQ-0057` is bounded:

| Object | Branch posture | Allowed use | Unsafe use |
|---|---|---|---|
| Single direct successor | `HB0` unless a rival candidate is visible. | Use head succession. | Pretending branch arbitration has produced extra evidence. |
| Duplicate zipped or extracted copy | `HB1`. | Navigation, checksum / carrier pointer, cold replay handle. | Independent confirmation. |
| Mirror-only release branch | `HB2`. | Carrier cleanup if owner rows agree. | Scientific progress or head election. |
| Partially described fork set | `HB3`. | Freeze unique-head selection and enumerate candidates. | Latest or cleanest branch wins. |
| Compatible owner repair plus package cleanup | `HB4` after replay. | Scoped merge followed by seal / verification / adoption / succession. | Convergence or promotion language. |
| Conflicting cap or challenge branches | `HB5` or `HB8`. | Conflict adjudication, challenge closure, rollback, or quarantine. | Silent overwrite by timestamp. |
| Strong content in unsafe carrier | `HB6`. | Evidence input, rebase candidate, challenge input. | Current-head authority. |
| Fully replayed bounded winner | `HB7`. | Bounded current-head continuation and future release reuse. | `S4` / `S5` closure language. |

## Branch-safe handoff template

When a future handoff presents more than one candidate continuation, use this shape:

> Treat competing continuations as a branch set, not a freshness race. Name the predecessor adopted head, enumerate each candidate branch, classify lineage, separate owner deltas from carrier hygiene, compare caps and no-closure wording, test whether deltas commute or conflict, record displaced-branch treatment, choose an `HB` state, and preserve rollback / re-arbitration triggers. If branch authority cannot be replayed, freeze unique-head selection and fall back to the last adopted bounded head rather than letting revision order, package cleanliness, generated mirrors, or summary wording decide.

## Interaction with succession, adoption, verification, and lineage controls

This docket sits after head succession and only opens when the successor problem becomes multi-branch:

1. The lineage-merge docket decides whether branch-local posture can be rebased through current owners.
2. The release-seal docket says what an outgoing branch carrier is allowed to carry.
3. The seal-verification docket checks whether the actual branch artifact preserves the seal.
4. The head-adoption docket decides whether a verified carrier can become an adopted bounded head.
5. The head-succession docket decides whether a later continuation can replace the adopted head.
6. This head-branch arbitration docket decides what happens when more than one candidate successor, fork, local continuation, or scope-split branch claims the same current-head slot.
7. The head-retirement / vacancy docket decides what happens when no branch, successor, predecessor, or carrier should keep the current-head slot for the affected scope.

A branch can pass verification but fail adoption.
A branch can pass adoption but fail succession.
A branch can pass succession in isolation but fail arbitration against a competing successor.
A branch can lose current-head authority while still providing evidence input, challenge input, mirror repair, or rollback history.
A branch contest can fail and trigger scoped vacancy rather than weak successor selection.
A successful arbitrated head remains bounded by `OQ-0057` caps and no-closure wording.

## Net result

This docket prevents a post-succession custody inflation channel: confusing branch recency, cleanliness, or plurality with authority.
It keeps multi-branch continuation useful while preventing competing zips, forks, local edits, generated mirrors, and cherry-picked surfaces from donating head authority by accident.
A future package may become the arbitrated bounded `OQ-0057` head only when the predecessor, candidate branch set, lineage, owner deltas, custody state, caps, conflict / commutation result, displaced-branch treatment, and rollback handles are replayable.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete branch set earns a real `HB` row beyond the default single-successor posture.


A later attempt to restore any retired, vacant, or quarantined successor authority should use `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md`; re-entry conditions trigger review rather than automatic authority revival.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
