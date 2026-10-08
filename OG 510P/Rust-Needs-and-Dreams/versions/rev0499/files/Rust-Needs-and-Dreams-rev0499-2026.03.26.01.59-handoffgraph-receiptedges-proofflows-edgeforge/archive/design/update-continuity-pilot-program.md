# Design: Update Continuity Pilot Program

## Goal
Turn Update Continuity Kit from a good conceptual anchor into a **ranked execution plan**.

Rust already has enough update ingredients to prove the gap is real.
The next step is not more release-feed glue or another self-update library.
It is a pilot sequence that shows Rust projects can preserve **reviewable continuity truth** across source-installed tools, prebuilt reinstall flows, receipt-driven updaters, bundle/app updaters, delegated managers, and ownership/uninstall boundaries without pretending all update events are one lane.

Read this together with:
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/update-continuity-lane-map.md`](./update-continuity-lane-map.md)
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`proposals/epic-update-continuity-kit.md`](../proposals/epic-update-continuity-kit.md)

## Why this needs its own design layer
The Update Continuity Kit already defines the artifact family: installed subject, candidate set, plan, apply report, rollback report, ownership report, diff, pack, handoff.

What it did **not** yet answer clearly enough is:
- which continuity lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep source-build installed-tool updates separate from prebuilt reinstall flows,
- how to keep receipt-driven and app-bundle updater lanes separate from delegated-manager lanes,
- how to keep check/plan separate from apply,
- and what counts as pilot success versus another updater demo.

Without that layer, update-continuity work risks two bad outcomes:
1. **lifecycle flattening** — the archive starts implying installed subject, visible candidates, chosen plan, apply result, rollback state, and ownership scope are all one story;
2. **updater theater** — one successful self-update or app-updater demo impersonates evidence for a broader continuity contract.

## Design principles
1. **Start from exact lane identity.** Every pilot should say which update lane it is proving.
2. **Keep current subject separate from candidate visibility.** “Installed now” and “could update to” are different truths.
3. **Keep check/plan separate from apply.** A chosen plan is not an applied result.
4. **Treat delegation as a first-class outcome.** Refuse/delegate is often the honest result.
5. **Treat ownership and uninstall as public contract.** Cleanup scope is not postscript trivia.
6. **Prefer vectors that reveal lossiness.** Missing receipts, architecture mismatch, interrupted apply, downgrade rules, and stale logs matter more than screenshots.
7. **Consumer handoffs must stay bounded.** Support, productization, and policy layers should only claim the continuity facts actually exported.

## Artifact family
### 1. `update-pilot-brief/v0`
Why this update lane is being piloted.

Should record:
- pilot id and summary
- lane family (`source-install`, `prebuilt-reinstall`, `receipt-updater`, `bundle-updater`, `delegated`, `ownership`, `forensics`, `handoff`)
- why the lane matters now
- intended consumers
- why the lane is tractable now

### 2. `update-lane-profile/v0`
The declared contract for the lane.

Should record:
- installed-subject family
- candidate-source family
- comparator/check posture
- apply/delegate posture
- rollback/uninstall expectations
- explicit unsupported areas

### 3. `update-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `update-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`support`, `incident`, `cli-productization`, `client-productization`, `extension-productization`, `policy`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `update-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it keep subject, candidate, plan, apply, rollback, and ownership separate?
- did it surface direct vs delegated behavior?
- did it attach concrete vectors and reports?
- did at least one real consumer import it?
- did it avoid claiming universal update truth?

### 6. `update-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- update-continuity artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Source-installed tool lane (`cargo install` + `cargo-update`)
**Why first**
- This is the clearest baseline continuity event for Rust tools.
- It proves installed subject, candidate discovery, plan/apply separation, and install-root ownership without app-bundle or receipt-specific complexity.

**Primary artifacts**
- `installed-subject/v0`
- `update-candidate-set/v0`
- `update-plan/v0`
- `update-apply-report/v0`

**Primary consumers**
- CLI maintainers
- support consumers
- install/update archaeology

### 2) Prebuilt reinstall lane (`cargo-binstall` + fallback ladder)
**Why second**
- This is where target matching and fallback order become impossible to ignore.
- It proves the archive can keep prebuilt selection truth separate from the final applied path.

**Primary artifacts**
- `installed-subject/v0`
- `update-candidate-set/v0`
- `update-plan/v0`
- `update-diff/v0`

**Primary consumers**
- CLI maintainers
- CI/install wrapper authors
- support consumers

### 3) Receipt-driven updater lane (cargo-dist + `axoupdater`)
**Why third**
- This lane proves continuity can import install receipts without flattening them into release truth.
- It also forces explicit treatment of interrupted/partial apply and backend-host assumptions.

**Primary artifacts**
- `installed-subject/v0`
- `update-candidate-set/v0`
- `update-plan/v0`
- `update-apply-report/v0`
- `ownership-report/v0`

**Primary consumers**
- client-app maintainers
- support/incident consumers
- release/install reviewers

### 4) Bundle/app updater lane (Tauri updater)
**Why fourth**
- This lane proves app-bundle semantics, target matching, downgrade rules, and before-exit behavior can be attached without becoming the whole continuity story.

**Primary artifacts**
- `update-lane-profile/v0`
- `update-candidate-set/v0`
- `update-plan/v0`
- `update-apply-report/v0`

**Primary consumers**
- client-app maintainers
- support consumers
- policy consumers

### 5) Delegated-manager / ownership lane
**Why fifth**
- This lane should come after the direct-apply lanes are legible.
- It proves that refusal/delegate plans and uninstall ownership boundaries are first-class outcomes, not failures of the schema.

**Primary artifacts**
- `update-plan/v0`
- `ownership-report/v0`
- `rollback-report/v0`
- `update-consumer-handoff/v0`

**Primary consumers**
- support/incident consumers
- policy consumers
- productization layers

### 6) Forensic/support handoff lane
**Why sixth**
- This lane becomes credible only once the earlier lanes are individually legible.
- It proves downstream consumers can import bounded continuity truth rather than inventing a hidden lifecycle model.

**Primary artifacts**
- `update-handoff/v0`
- `update-diff/v0`
- `update-consumer-handoff/v0`
- `update-pilot-pack/v0`

**Primary consumers**
- Support Envelope Kit
- Policy Kit
- CLI / Client / Extension / Operator productization stacks

## Graduation criteria
An update-continuity pilot should graduate only when it has:
- explicit lane identity,
- at least one direct vector and one lossy/imported vector,
- separate installed-subject, candidate, plan, apply, rollback, and ownership artifacts where applicable,
- at least one real downstream consumer import,
- and an honest statement of what remains unsupported.

## Failure modes this program should catch early
- confusing “update available” with “update applied”;
- treating prebuilt fallback ladders as one artifact choice;
- letting install receipts impersonate universal installed-state truth;
- hiding delegated-manager refusal under “not supported” rather than recording ownership;
- and collapsing rollback/uninstall into generic apply success.

## What success looks like
A good pilot sequence should leave the archive able to say:
- what installed subject the machine started from,
- which update candidates and comparator rules were actually visible,
- what plan was selected or delegated,
- what changed or failed to change,
- what rollback/uninstall ownership facts remain,
- and what downstream consumers may safely conclude,

without rebuilding the story from release pages, shell history, updater logs, and memory.
