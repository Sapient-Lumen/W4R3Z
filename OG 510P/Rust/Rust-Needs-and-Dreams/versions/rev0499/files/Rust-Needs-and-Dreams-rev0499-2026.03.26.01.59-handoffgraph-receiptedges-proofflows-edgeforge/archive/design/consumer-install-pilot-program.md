# Design: Consumer Install Pilot Program

## Goal
Turn Consumer Install Kit from a good conceptual anchor into a **ranked execution plan**.

Rust already has enough installation machinery to prove the gap is real.
The next step is not another installer script or another “fast install” benchmark.
It is a pilot sequence that shows Rust projects can emit **reviewable first-install truth** across source builds, prebuilt artifacts, mirror fallback, CI wrapper installs, delegated-manager imports, and receipt handoffs without pretending every install event is one lane.

Read this together with:
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/consumer-install-lane-map.md`](./consumer-install-lane-map.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/airgap-kit.md`](./airgap-kit.md)
- [`proposals/epic-consumer-install-kit.md`](../proposals/epic-consumer-install-kit.md)

## Why this needs its own design layer
The Consumer Install Kit already defines the artifact family: subject / candidate / catalog / policy / plan / receipt / pack / handoff artifacts.

What it did **not** yet answer clearly enough is:
- which install lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep source-build truth separate from prebuilt truth,
- how to keep host ordering separate from selected-source receipts,
- how to keep wrapper/CI installs separate from direct user installs,
- and what counts as pilot success versus another shell transcript with nicer prose.

Without that layer, consumer-install work risks two bad outcomes:
1. **install flattening** — the archive starts implying requested subject, visible candidates, chosen plan, selected host, verification posture, and installed-state receipt are all one story;
2. **wrapper theater** — one successful bootstrap action or release installer gets mistaken for a general Rust install contract.

## Design principles
1. **Start from exact lane identity.** Every pilot should declare which install lane it is proving.
2. **Keep subject separate from candidates.** What was requested is not the same truth as what was visible.
3. **Keep plan separate from receipt.** Ranked/refused choices are not the same as actual mutation.
4. **Keep verification posture explicit.** Checksums, signatures, TLS-only fetches, and unsigned fallback are not interchangeable.
5. **Treat delegated ownership as first-class.** Imported or package-manager installs should emit explicit lossiness rather than fake direct receipts.
6. **Prefer vectors that reveal fallback.** Host outage, target mismatch, missing signatures, and `--no-track` are more valuable than a smooth happy path alone.
7. **Consumer handoffs must stay bounded.** Update/support/policy consumers should only claim the install facts actually exported.

## Artifact family
### 1. `install-pilot-brief/v0`
Why this install lane is being piloted.

Should record:
- pilot id and summary
- lane family (`source-build`, `prebuilt`, `mirror`, `ci-wrapper`, `delegated-import`, `receipt-handoff`)
- why the lane matters now
- intended consumer(s)
- why the lane is tractable now

### 2. `install-lane-profile/v0`
The declared contract for the lane.

Should record:
- subject class and source class
- candidate/host expectations
- verification expectations
- install-root/ownership posture
- receipt expectations
- explicit unsupported areas

### 3. `install-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `install-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`update-continuity`, `support`, `inventory`, `policy`, `distribution-review`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `install-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it keep subject/catalog/plan/receipt separate?
- did it preserve selected-source and verification posture explicitly?
- did it attach concrete vectors and receipts?
- did at least one downstream consumer import it?
- did it avoid claiming universal install truth?

### 6. `install-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- install artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) `cargo install` source-build lane
**Why first**
- This is the clearest baseline install event.
- It proves requested subject, packaged-lock posture, install-root tracking, and managed-content claims without mirror or wrapper complexity.

**Primary artifacts**
- `install-subject/v0`
- `install-catalog/v0`
- `install-plan/v0`
- `install-receipt/v0`

**Primary consumers**
- CLI maintainers
- support reviewers
- update-continuity consumers

### 2) Prebuilt binary lane (`cargo-binstall`)
**Why second**
- This lane forces the archive to keep candidate host/target/verification truth separate from source-build assumptions.
- `cargo-binstall` already exposes the fallback ladder explicitly enough to make the distinction concrete.

**Primary artifacts**
- `install-candidate/v0`
- `install-catalog/v0`
- `install-plan/v0`
- `install-receipt/v0`

**Primary consumers**
- CLI/client productization reviewers
- signed-binaries consumers
- support/inventory reviewers

### 3) Mirror / host-order lane (cargo-dist-style)
**Why third**
- This lane proves candidate ordering and selected-source receipts can stay explicit under fallback.
- It is the first lane where airgap/mirror topology becomes public install semantics rather than deployment trivia.

**Primary artifacts**
- `install-catalog/v0`
- `install-policy/v0`
- `install-plan/v0`
- `install-receipt/v0`

**Primary consumers**
- airgap/mirror reviewers
- distribution-contract consumers
- support/incident reviewers

### 4) CI wrapper lane (`install-action`)
**Why fourth**
- This lane proves wrapper manifests, fallback policy, checksum/signature posture, and prerequisite setup can be captured without pretending the wrapper is the installed tool.
- CI is where many real organizations first encounter Rust tool installation as durable infrastructure.

**Primary artifacts**
- `install-lane-profile/v0`
- `install-plan/v0`
- `install-receipt/v0`
- `install-consumer-handoff/v0`

**Primary consumers**
- CI/platform maintainers
- support and archaeology consumers
- policy/inventory consumers

### 5) Delegated-manager / imported lane
**Why fifth**
- This lane should arrive only after direct lanes are legible.
- It proves the archive can preserve useful first-install facts without faking direct authority over package-manager or app-store installs.

**Primary artifacts**
- `install-subject/v0`
- `install-receipt/v0` with explicit lossiness
- `install-consumer-handoff/v0`
- `install-pilot-scorecard/v0`

**Primary consumers**
- support/incident reviewers
- update-continuity consumers
- inventory/policy consumers

### 6) Update/support handoff lane
**Why sixth**
- This lane becomes credible only after the earlier lanes are individually legible.
- It proves Update Continuity and support consumers can import install truth without rescraping terminals or redefining first install.

**Primary artifacts**
- `install-handoff/v0`
- `install-consumer-handoff/v0`
- `install-pilot-pack/v0`

**Primary consumers**
- Update Continuity Kit
- Support Envelope Kit
- Distribution Contract Stack

## Graduation criteria
A consumer-install pilot should graduate only when it has:
- preserved install subject, visible candidates, chosen plan, receipt, and managed-content claims as separate truths;
- captured at least one meaningful fallback/refusal/uncertainty case;
- shown what changes when the install lane changes;
- produced a receipt or explicit lossiness artifact durable enough for downstream import;
- and been consumed by at least one downstream layer without that layer inventing stronger install claims.

## Failure modes to avoid
- Treating “installed latest version” as enough.
- Treating source builds and prebuilt downloads as the same lane with different performance.
- Letting mirror/host selection disappear into installer internals.
- Letting CI wrappers quietly become the install authority.
- Pretending imported/package-manager installs have the same completeness as direct receipts.
- Letting update/uninstall logic overwrite the first-install record.

## Expected effect on the archive
If this pilot plan works, the archive will gain a boring but powerful new invariant:
**first install remains reviewable even when the ecosystem uses multiple acquisition paths.**

That is the missing substrate under Distribution Contract and above later lifecycle continuity.
