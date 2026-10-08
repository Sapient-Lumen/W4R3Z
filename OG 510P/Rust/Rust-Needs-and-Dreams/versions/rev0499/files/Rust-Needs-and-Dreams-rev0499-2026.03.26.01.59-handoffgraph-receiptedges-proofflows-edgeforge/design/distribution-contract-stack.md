## Execution addendum (rev0444)
Read `design/distribution-contract-execution-blueprint-2026Q1.md` immediately after this note when the question is no longer only “what layers compose the delivery seam?” but “what should the actual contribution ship first?”

Interpretation rule:
- this stack still explains composition;
- the new blueprint now treats the worthy project shape as **reference layer + report/pack command + adapter/acceptance corpus**;
- and future work should prove source-build, prebuilt/fallback, mirror, ownership, and bounded consumer-handoff lanes before widening into larger installer or updater stories.

## Frontier note (rev0407)
This stack should now be read as an explicit **Distribution Contract** frontier rather than as a useful-but-background stack note.
The current evidence is strong enough that Rust delivery should no longer be narrated as “release truth plus whatever installer happened”.

Interpretation rule:
- keep **Publisher & Source Identity Contract** as the upstream publication / authority / route-identification seam;
- keep **Package Intake Gateway** as the local ingress / extraction / staging seam;
- keep **Consumer Install Kit** as the leaf first-acquisition event;
- keep **Update Continuity Kit** as the later lifecycle seam; but
- read this stack as the clearest next **delivery / acquisition / ownership-shaping** move because the ecosystem now has serious release automation, prebuilt acquisition, mirror fallback, and ownership/uninstall pressure without one reviewable delivery boundary.

Read together with `design/distribution-contract-2026Q1.md`.

# Design: Distribution Contract Stack (Consumer Install + Signed Binaries + Airgap + release/support imports)

## Goal
This stack now sits inside the archive's explicit [`design/consumer-lifecycle-continuity-bundle.md`](./consumer-lifecycle-continuity-bundle.md) composition point, which keeps first install, later lifecycle events, and route/home changes separate instead of letting the stack silently become a universal updater story.

Treat **Consumer Install Kit**, **Signed Binaries Kit**, **Airgap Kit**, and selected **Release Truth / Support Envelope / Policy** imports as one shared **Distribution Contract Stack** for the **consumer side** of Rust software delivery.

The missing contribution is **not** another installer script, another package-manager shim, another host-page parser, or another “one command to install anything” wrapper.
It is a portable, reviewable stack that keeps these truths distinct while letting them compose at the moment software is actually selected, fetched, verified, and installed:
- **release truth** — what the producer published and attached;
- **catalog truth** — which install candidates and channels were visible to the consumer;
- **selection truth** — which candidate was chosen and why;
- **verification truth** — what checks actually passed, failed, warned, or were skipped;
- **fallback truth** — what happened when the preferred path was unavailable or insufficient;
- **installed-state truth** — what landed on disk or in the tool root;
- **support/incident truth** — what later consumers can legitimately conclude from the receipt.

That separation matters because the Rust ecosystem now has credible producer-side release tooling, but still lacks a stable consumer-side boundary for how a tool actually reaches a machine.

## Why this seam matters now
Current Rust signals are unusually aligned here:
- Cargo install, cargo-binstall, cargo-dist, CI fallback wrappers, and tool-local receipt/updater crates now make the leaf install event more explicit rather than less; the archive should respond by giving that event its own reusable boundary.
- The ecosystem already has evidence that **install truth**, **signature/provenance truth**, **mirror/offline topology truth**, and **post-install lifecycle continuity** are distinct layers.
- crates.io and Rust’s 2026 supply-chain work keep strengthening producer-side truth, which makes it more valuable — not less — to preserve the package → release → install handoff honestly downstream.

Taken together, these signals say ideal Rust now needs a **stack-level consumer distribution layer** above leaf install truth and below support, incident, or policy consumers.

## What each layer owns
### Release Pipeline Kit
[`design/release-pipeline-kit.md`](./release-pipeline-kit.md) owns:
- release subject, intent, and manifest,
- source publish records,
- artifact attachments,
- producer-side release policy,
- and `release-pack/v0`.

Its question is:
> what did the producer publish and claim to ship?

### Consumer Install Kit
[`design/consumer-install-kit.md`](./consumer-install-kit.md) owns:
- install subject identity,
- visible candidate catalogs,
- caller/org install policy,
- ranked install plans with refusal reasons,
- install receipts and managed-content claims,
- and `install-pack/v0`.

Its question is:
> what install candidates did the consumer see, what was chosen, and what actually happened on disk?

### Signed Binaries Kit
[`design/signed-binaries-kit.md`](./signed-binaries-kit.md) owns:
- downloadable binary metadata,
- signature material and issuer references,
- verification reports for prebuilt artifacts,
- and attachment semantics for release packs.

Its question is:
> what signature/provenance facts hold for this prebuilt artifact?

### Airgap Kit
[`design/airgap-kit.md`](./airgap-kit.md) owns:
- restricted-network topology,
- mirror exact-copy posture,
- rustup / Cargo / tool-install lane separation,
- warm-cache-vs-validated-offline truth,
- and offline bootstrap verification.

Its question is:
> under restricted network assumptions, what sources and validations were actually available?

### Distribution Contract Stack
This stack owns:
- stack-level import and comparison of install packs, signed-binary evidence, release truth, and airgap posture,
- cross-host / cross-channel / cross-mirror diffs,
- install-truth handoffs into support, incident, inventory, and policy consumers,
- bounded stack-level summaries that do not replace leaf receipts,
- and the rule that one acquisition event and later lifecycle continuity stay separate.

Its question is:
> how should leaf install truth, producer-side evidence, mirror/offline posture, and downstream consumer handoffs compose?

Design note: this stack stops at composition and handoff. The leaf install event belongs to [`design/consumer-install-kit.md`](./consumer-install-kit.md). Ongoing change over an existing installation — update checks, chosen update plans, apply results, rollback, uninstall scope, and ownership drift — belongs to [`design/update-continuity-kit.md`](./update-continuity-kit.md).

## What the stack should make possible
A reviewer should be able to answer all of these from one linked distribution bundle, without reconstructing the story from shell history, host pages, or CI logs:
1. Which install packs or receipts are being composed?
2. Which channel, host, or mirror differences matter across those receipts?
3. What producer-side release/signature evidence is attached versus missing?
4. What install-truth differences are leaf facts versus stack-level handoff summaries?
5. What later support, policy, or incident conclusions are justified — and which are still out of scope?
6. Which current managed-state or lifecycle questions must be handed off instead of silently answered by the install stack?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Stack boundary relative to Release Truth
This stack must stay clearly distinct from the broader **Release Truth Stack**.

Release truth is about:
- what the producer published,
- which artifacts and evidence belong to a release,
- and what was intended for distribution.

Distribution contract is about:
- what the consumer actually saw and selected,
- which host/mirror/channel/fallback path was taken,
- how verification behaved in that path,
- and what ended up installed.

Release truth should feed distribution truth later, but it must **not** silently pretend that a published artifact was necessarily the artifact or channel a consumer ended up using.

## Recommended execution posture
The stack now needs a shared execution layer, captured in:
- [`design/distribution-contract-pilot-program.md`](./distribution-contract-pilot-program.md)

That pilot program should prove the stack in the following order:
1. **leaf consumer-install lane first**
2. **mirror / host fallback composition lane**
3. **package-manager / install-script import lane**
4. **restricted-network consumer lane**
5. **support / incident / archaeology consumer lane**

That ordering is intentional.
The archive should not jump straight to another universal installer, release website, or binary trust dashboard.
It should first prove that ordinary Rust installs can carry enough structured truth to make consumer-side acquisition reviewable and reusable.

## Design principles
1. **Leaf install truth before stack composition.** Import `install-pack/v0` instead of silently re-inventing it.
2. **Producer truth before downstream handoff.** Import release and signature artifacts instead of flattening them.
3. **Selection is not verification.** Choosing a candidate and verifying it are related but distinct.
4. **Fallback must stay visible.** Source-build substitution, mirror substitution, or package-manager substitution should never be silent.
5. **Restricted-network reality is first-class.** Online, mirrored, and airgapped consumers should fit one contract without pretending they are the same environment.
6. **Installed-state ownership must stay explicit.** Co-located binaries are not automatically managed by the same tool, and leaf receipts must leave enough truth for later update/uninstall flows to say what they do and do not own.
7. **First install is not lifecycle continuity.** Update, rollback, downgrade, and uninstall events should import install receipts instead of being flattened into them.
8. **Honest incompleteness is allowed.** `INCONCLUSIVE` or partially verified installs must remain representable.
9. **Thin consumers later.** Support UIs, dashboards, and assistant summaries should consume the stack, not replace it.

## What an epic contribution would look like in practice
A serious contribution here would:
- reuse `install-pack/v0`, `release-pack/v0`, `binpack/v0`, and Cargo-native install/build semantics instead of forking them;
- let leaf install adapters stay honest about source builds, prebuilt downloads, package-manager imports, and local-path lanes;
- make mirror/channel/fallback behavior explainable and auditable at stack level;
- and preserve honest handoffs into support, incident response, and policy rather than letting “installed successfully” stand in for everything.

## Anti-goals
Do not turn this stack into:
- one monopoly installer,
- one release-host scraping engine,
- one fake universal “safe to install” badge,
- one replacement for OS package managers,
- one binary-only worldview that erases source builds,
- or one airgap umbrella that swallows normal online distribution.

The stack is a **consumer-side review boundary**, not a replacement distribution empire.
