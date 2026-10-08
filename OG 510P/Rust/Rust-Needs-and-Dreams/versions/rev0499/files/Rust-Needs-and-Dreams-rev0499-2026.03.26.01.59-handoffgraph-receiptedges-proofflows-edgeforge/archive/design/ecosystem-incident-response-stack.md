# Design: Ecosystem Incident Response Stack (Incident Kit + Trust Decision + Package Admission + Release Truth)

## Goal
Treat **ecosystem incident response** as a first-class Rust control-plane seam.

Rust now has materially better supply-chain signals than it did even a year ago:
- crates.io surfaces RustSec-backed security data directly on crate pages,
- trusted publishing is becoming a stronger release-identity boundary,
- provenance and threat-model work are getting more concrete,
- real-time scanning and capability-analysis work are being prototyped,
- and the registry has clarified that routine malicious-crate removals will primarily flow through RustSec advisories rather than individual blog posts.

But the downstream response story is still often a blur of screenshots, Slack messages, `cargo deny` failures, lockfile greps, emergency yanks, patch overrides, token rotation, clean-rebuild folklore, and improvised customer notes.
The missing contribution is therefore **not** another scanner, another score, another security dashboard, or another generic “secure your supply chain” essay.
It is a thin **reviewable incident-response layer** that keeps these truths separate:
- **incident-subject truth** — what happened: malicious crate, compromised publish path, suspicious typosquat, vulnerable dependency with credible exploitation, provenance/signing anomaly, or registry/security notice;
- **exposure truth** — whether the workspace, branch, release line, binary artifact, CI path, or mirror actually consumed the affected subject, and in what scope (build-dep / proc-macro / test / runtime / publish path);
- **containment truth** — what was done immediately: block, patch, pin, mirror quarantine, owner/token changes, trusted-publishing policy changes, feature disablement, or package-admission freeze;
- **rebuild-and-reissue truth** — what was rebuilt, reverified, republished, or redistributed, with what evidence and what residual uncertainty;
- **communication truth** — what maintainers, downstream integrators, release consumers, or internal responders were told, and what they may honestly conclude;
- **post-incident truth** — what changed afterward in admission policy, trust posture, release process, mirrors, canary lanes, or drills.

The point is to stop treating “we handled the incident” as one blob.

## Why this seam matters now
Official Rust/Foundation/Cargo signals are unusually aligned here:
- The January 2026 crates.io development update says crate pages now expose a **Security** tab backed by RustSec advisories, expand **Trusted Publishing** to GitLab CI/CD, allow **Trusted Publishing Only Mode**, and block risky GitHub triggers like `pull_request_target` and `workflow_run`. That means incident-relevant registry signals and release-identity controls are becoming first-class ecosystem inputs rather than external lore.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The February 2026 malicious-crate notification-policy update says the crates.io team will stop publishing a blog post for every malicious crate, will **always publish a RustSec advisory** when a crate is removed for containing malware, and will reserve extra public broadcast for cases with evidence of real usage or exploitation. That sharply increases the value of local, attachable response artifacts because public blog posts are no longer the default downstream coordination surface.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- The Rust Foundation’s 2026–2028 strategy puts **stable, secure infrastructure** at the center, explicitly naming OpenSSF-aligned best practices, signed crates, official mirrors, and sustaining crates.io and release-download infrastructure. That is strong evidence that incident response is not a side quest; it sits on the critical path of ecosystem trust.
  https://rustfoundation.org/strategic-plan/
- The Rust Foundation’s May 2025 Alpha-Omega security update says crate provenance tracking is live, Typomania and Painter have matured, real-time crate-scanning pilots are underway, a Rust-focused Capslock-style Cargo subcommand is being built, and TUF-based signed-metadata work is part of the roadmap. Those are exactly the kinds of inputs a real incident-response layer would need to consume without reinventing them.
  https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- Rust’s 2026 flagships include **Secure your supply chain**, with milestones like public/private dependency control and SBOM support. That means ecosystem incident handling should expect richer package and artifact evidence rather than pretending advisories alone are the whole story.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s publishing docs say **yanking does not delete code**, is not a remedy for leaked secrets, and does not break existing `Cargo.lock` files. In other words: registry action alone does not equal containment.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo’s overriding-dependencies docs say `[patch]` exists specifically so downstream users can test or carry an unpublished upstream fix immediately. That makes local override/remediation posture a real first-class response lane, not just a maintainer trick.
  https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html

Taken together, ideal Rust now needs an **incident-response stack** above raw advisories/scanners and below release/support/install conclusions.

## What counts as incident-subject truth
Not every incident needs every field, but the stack should be able to name these subjects explicitly:
- malicious crate or typosquat removal;
- compromised publish credential or suspicious publisher/source identity change;
- known-vulnerable dependency with plausible real-world impact or active exploitation concern;
- provenance/signature/mirror anomaly;
- trusted-publishing policy violation or release-path drift;
- unexpected dependency-graph inclusion of a forbidden or quarantined subject;
- internal rediscovery that a previously handled incident still survives in a release line, binary, or airgapped mirror.

A project does not become more honest by flattening all of these into “dependency security issue”.

## What each neighboring stack owns
### Incident Kit
[`design/incident-kit.md`](./incident-kit.md) owns:
- the reference CLI shape,
- concrete portable report fields,
- drill scenarios,
- and automation hooks.

Its question is:
> what concrete operational commands and artifacts should responders use?

The Ecosystem Incident Response Stack owns the **higher-level control plane** above that kit.

### Trust Decision Stack
[`design/trust-decision-stack.md`](./trust-decision-stack.md) owns:
- normal intake and trust-policy evidence,
- waivers and policy overlays,
- local trust/admission judgments.

Its question is:
> should we admit, trust, or continue trusting this package/source under normal conditions?

The incident stack begins when ordinary trust signals are no longer enough and a time-sensitive response program is needed.

### Package Admission Stack
[`design/package-admission-stack.md`](./package-admission-stack.md) owns:
- package review and publish-review evidence,
- dependency/public-API/SBOM/trust inputs,
- bounded admission decisions.

Its question is:
> should this package enter or remain in the allowed set?

The incident stack may freeze or revise admission, but it should not erase the difference between pre-incident review and emergency containment.

### Canary Validation Stack
[`design/canary-validation-stack.md`](./canary-validation-stack.md) owns:
- advance-warning watch lanes,
- cadence and gating,
- observed canary outcomes,
- escalation into deeper stacks.

Its question is:
> what future-risk watch program noticed something might be wrong?

The incident stack begins when the answer shifts from **watch** to **contain and communicate**.

### Release Truth / Distribution Contract
[`design/release-truth-stack.md`](./release-truth-stack.md) and [`design/distribution-contract-stack.md`](./distribution-contract-stack.md) own:
- what source and artifacts were released,
- how consumers receive them,
- install/update/distribution receipts.

Their questions are:
> what artifacts actually went out?
>
> what channels and installers may consumers have used?

The incident stack imports those truths to answer exposure and reissue questions, but does not replace them.

### Publisher & Source Identity Stack
[`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md) owns:
- source/publisher authority claims,
- release-path identity,
- registry/repo provenance posture.

Its question is:
> who or what was actually authorized to publish this thing?

The incident stack consumes that when suspected compromise or impersonation is part of the subject.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. What exactly is the incident subject?
2. Did we actually ingest or publish it anywhere relevant?
3. What immediate containment actions were taken, and what risks remain uncontained?
4. What had to be rebuilt, republished, rotated, re-mirrored, or re-verified?
5. What did we tell maintainers, users, downstream integrators, or internal teams?
6. What policy/process changes should survive after the incident is over?

If the stack cannot answer those six questions, it is still just security folklore.

## Recommended execution posture
The archive should prefer a ranked rollout like this:

### 1. Advisory/removal intake + exposure slice
Prove the stack on RustSec advisory or crates.io removal intake first:
- affected crate + versions,
- workspace/lockfile/release-line presence,
- build-dep vs runtime scope,
- confidence and blind spots.

### 2. Containment pack
Prove explicit containment artifacts:
- block/deny policy,
- `[patch]` or source override posture,
- mirror quarantine / install-channel pause,
- owner/token/trusted-publishing changes,
- “yank seen, but existing lockfiles remain exposed” truth.

### 3. Rebuild/reissue lane
Prove that local artifacts can be cleanly re-derived or explicitly marked uncertain:
- rebuild plan,
- affected binary/package list,
- release or distribution replacement plan,
- support/update notes.

### 4. Communication and consumer handoff
Prove that the response can emit honest outputs for different audiences:
- maintainers,
- internal platform/security teams,
- downstream integrators,
- end-user release/update channels.

### 5. Retrospective and drill lane
Only after the above should the stack claim maturity through:
- tabletop scenarios,
- replayable drills,
- permanent admission/publishing/mirror/canary changes,
- and measured time-to-containment / time-to-reissue.

That order matters.
The archive should not jump straight from “there was a malicious crate” to “we now have a complete ecosystem-security platform”.

## Design principles
1. **Incident subject first.** Do not start with the remediation command before naming the event.
2. **Exposure stays explicit.** A RustSec advisory, a registry removal, a yanked release, a published artifact, and a consumed lockfile are related but not identical truths.
3. **Containment is not repair.** Blocking future resolution, rotating credentials, applying `[patch]`, or quarantining mirrors does not by itself prove downstream artifacts are clean.
4. **Communication is part of the stack.** Once routine incident blog posts are no longer the default, local attachable communication artifacts matter more.
5. **Registry action is not enough.** Yanks and removals do not rewrite already-issued lockfiles, binaries, mirrors, or airgapped bundles.
6. **Retrospective changes stay reviewable.** Admission rules, publisher-identity requirements, canary lanes, and mirror policies changed because of an incident should remain visible after the page of alerts scrolls away.
7. **Downstream consumers inherit bounded authority.** Release notes, support pages, install/update tools, and local platform overlays should import explicit incident facts rather than improvising them.

## What an epic contribution would look like in practice
A serious contribution here would likely publish a compact artifact family such as:
- `incident-subject/v0` — advisory/removal/compromise identity, scope hints, source links, severity/posture
- `incident-exposure/v0` — lockfile/release-line/artifact/install-path presence and blind spots
- `incident-containment/v0` — blocks, patches, owner/token changes, mirror/distribution pauses, admission freezes
- `incident-rebuild/v0` — rebuild/reissue/reverification plan, completed receipts, residual unknowns
- `incident-handoff/v0` — maintainer/internal/downstream/end-user communications and post-incident policy changes

A thin `cargo incident` / `incident-pack/v0` layer would then:
- ingest registry/RustSec/Foundation/security inputs rather than mirror them into another scanner silo,
- preserve exposure versus containment versus reissue as separate artifacts,
- attach local overrides and rebuild evidence without pretending they solve upstream governance,
- and let Trust Decision / Package Admission / Release Truth / Distribution Contract / Support consumers import only what is justified.

## Anti-goals
Do not turn this stack into:
- one universal security score,
- one hosted SOC dashboard,
- one malware scanner wrapper,
- one “cargo secure all the things” brand package,
- or one vague supply-chain manifesto that never says who was exposed or what changed.

The stack is a **review boundary for incident response**, not a replacement for RustSec, crates.io, Cargo, or the Foundation’s broader security work.
