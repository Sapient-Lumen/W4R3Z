# Design: Publish Set Pilot Program

## Goal
Turn Publish Set Kit from a good conceptual anchor into a **ranked execution plan**.

Rust already has enough source-publication machinery to prove the gap is real.
The next step is not more CI glue or another cargo-release wrapper.
It is a pilot sequence that shows Rust projects can publish **reviewable source-publication truth** across single-package publishes, workspace publish sets, alternative registries, trusted-publishing flows, checks/waivers, and index receipts without pretending all publish events are one lane.

Read this together with:
- [`design/publish-set-kit.md`](./publish-set-kit.md)
- [`design/publish-set-lane-map.md`](./publish-set-lane-map.md)
- [`design/manifest-truth-stack.md`](./manifest-truth-stack.md)
- [`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)
- [`proposals/epic-publish-set-kit.md`](../proposals/epic-publish-set-kit.md)

## Why this needs its own design layer
The Publish Set Kit already defines the artifact family: brief / subject / payload / check / receipt / pack / diff / handoff artifacts.

What it did **not** yet answer clearly enough is:
- which publication lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep workspace publish-set truth separate from single-package truth,
- how to keep authority path separate from trust verdict,
- how to keep checks/waivers separate from registry acceptance,
- and what counts as pilot success versus another publish-workflow blog post.

Without that layer, publish-set work risks two bad outcomes:
1. **publication flattening** — the archive starts implying package selection, tarball contents, check posture, authority path, and receipts are all one story;
2. **CI theater** — one successful GitHub/GitLab workflow or release page import impersonates evidence for a broader publication contract.

## Design principles
1. **Start from exact lane identity.** Every pilot should say which publication lane it is proving.
2. **Keep subject separate from payload.** Selected packages are not the same thing as packaged files.
3. **Keep checks separate from receipts.** Verification/semver/policy results are not registry acceptance or index visibility.
4. **Treat authority path as public contract.** Tokens, credential providers, and Trusted Publishing are not one posture.
5. **Treat workspace publication as first-class.** Multi-package publishing should not be treated as a weird extension of single-package publishing.
6. **Prefer vectors that reveal lossiness.** Timeouts, waivers, generated files, package-order drift, and imported-forensic gaps matter more than glossy screenshots.
7. **Treat later registry observation as its own lane.** `pubtime`, index visibility, and later archaeology should refine the picture without rewriting the original event.
8. **Consumer handoffs must stay bounded.** Release, package-admission, and support layers should only claim the publish-set facts actually exported.

## Artifact family
### 1. `publish-pilot-brief/v0`
Why this publication lane is being piloted.

Should record:
- pilot id and summary
- lane family (`single-package`, `workspace-set`, `alt-registry`, `trusted-publishing`, `checks`, `receipt`, `forensics`, `handoff`)
- why the lane matters now
- intended consumer(s)
- why the lane is tractable now

### 2. `publish-lane-profile/v0`
The declared contract for the lane.

Should record:
- selected registry/index posture
- authority-path family
- package-selection posture
- payload/report expectations
- check families in scope
- receipt expectations
- explicit unsupported areas

### 3. `publish-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `publish-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`release-review`, `package-admission`, `support-archaeology`, `publisher-identity`, `library-productization`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `publish-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it keep subject/payload/check/receipt separate?
- did it make authority-path posture explicit?
- did it attach concrete vectors and reports?
- did at least one real consumer import it?
- did it avoid claiming universal publish truth?

### 6. `publish-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- publish-set artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Single-package crates.io direct-publish lane
**Why first**
- This is the clearest baseline publication event.
- It proves selected subject, packaged payload, basic checks, and initial receipt capture without workspace or alt-registry complexity.

**Primary artifacts**
- `publish-subject/v0`
- `package-file-report/v0`
- `publish-check-report/v0`
- `publish-receipt/v0`

**Primary consumers**
- library maintainers
- release reviewers
- support consumers

### 2) Workspace publish-set lane
**Why second**
- Rust 1.90 made multi-package publishing stable, so this is no longer future work.
- It forces the archive to keep subject grouping and per-package receipts honest.

**Primary artifacts**
- `publish-subject/v0`
- multiple `package-file-report/v0`
- `publish-diff/v0`
- `publish-check-report/v0`

**Primary consumers**
- workspace maintainers
- release-truth consumers
- package-admission reviewers

### 3) Alternative-registry / auth-required lane
**Why third**
- This lane proves registry/index/credential-provider facts can be captured without collapsing them into token folklore.
- The registry-auth docs make this lane concrete enough now.

**Primary artifacts**
- `publish-lane-profile/v0`
- `publish-subject/v0`
- `publish-receipt/v0`
- `publish-check-report/v0`

**Primary consumers**
- private-registry operators
- publisher-identity reviewers
- support/ops consumers

### 4) Trusted-publishing / TP-only lane
**Why fourth**
- crates.io now makes this a first-class authority lane instead of a custom GitHub-only hack.
- This pilot proves OIDC/issuer posture can be attached without becoming the whole trust verdict.

**Primary artifacts**
- `publish-lane-profile/v0`
- `publish-check-report/v0`
- `publish-receipt/v0`
- `publish-consumer-handoff/v0`

**Primary consumers**
- publisher-identity reviewers
- trust/policy consumers
- release reviewers

### 5) Check / waiver lane
**Why fifth**
- This lane should arrive only after subject/payload/authority lanes are legible.
- It proves that package verification, semver checks, policy imports, warnings, and waivers can attach separately from receipt success.

**Primary artifacts**
- `publish-check-report/v0`
- `publish-query-budget/v0`
- `publish-diff/v0`
- `publish-pilot-scorecard/v0`

**Primary consumers**
- package-admission reviewers
- policy consumers
- support consumers

### 6) Receipt / index / `pubtime` lane
**Why sixth**
- This lane turns later registry/index observation into a first-class report instead of a shell-transcript footnote.
- It is especially valuable for sparse-index lag, timeout, and archaeology cases.

**Primary artifacts**
- `publish-receipt/v0`
- `publish-diff/v0`
- `publish-consumer-handoff/v0`

**Primary consumers**
- release-truth reviewers
- support/incident consumers
- archaeology consumers

### 7) Release / package-admission handoff lane
**Why seventh**
- This lane becomes credible only after the earlier lanes are individually legible.
- It proves downstream layers can import publish-set truth without re-synthesizing publication from CI and registry pages.

**Primary artifacts**
- `publish-handoff/v0`
- `publish-consumer-handoff/v0`
- `publish-pilot-pack/v0`

**Primary consumers**
- Release Truth Stack
- Package Admission Stack
- Library Productization / support consumers

## Graduation criteria
A publish-set pilot should graduate only when it has:
1. an explicit pilot brief;
2. a lane profile naming the publication lane under review;
3. a bounded query budget with named vectors;
4. at least one consumer-handoff artifact;
5. concrete payload/check/receipt reports or attached evidence;
6. a scorecard showing the pilot remained lane-specific and did not claim universal publish truth.

## Failure modes to avoid
- Treating one CI workflow as the whole publish-set story.
- Treating package payload truth as a manifest diff only.
- Treating semver or policy checks as registry acceptance.
- Treating later registry pages as a complete substitute for direct receipts.
- Treating trusted publishing as a full trust verdict instead of an authority-path lane.
