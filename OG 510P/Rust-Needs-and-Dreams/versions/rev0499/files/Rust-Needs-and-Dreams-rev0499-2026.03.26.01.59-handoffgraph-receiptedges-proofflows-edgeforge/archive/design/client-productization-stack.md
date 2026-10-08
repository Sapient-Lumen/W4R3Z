# Design note: Client Productization Stack (Client App Surface + A11yKit + Localization Surface + Distribution Contract + Update Continuity + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust client-app surfaces, accessibility semantics, localization support, distribution/install truth, and support claims so the ecosystem can make **real desktop/mobile/embedded apps** reviewable without anointing one GUI toolkit, one shell, one bridge generator, or one app-store pipeline as the default answer.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose, and it should now be read together with [`proposals/epic-client-productization-stack.md`](../proposals/epic-client-productization-stack.md):
- [`design/client-app-surface-kit.md`](./client-app-surface-kit.md)
- [`design/a11ykit-ui-testing.md`](./a11ykit-ui-testing.md)
- [`design/localization-surface-kit.md`](./localization-surface-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/rollout-surface-kit.md`](./rollout-surface-kit.md)

## Why this note is needed now
Rust’s current signals no longer say only “native apps are possible.” They say Rust now has **multiple credible client-app lanes**, but still lacks a portable productization layer above them:
- Tauri 2 is stable and explicitly targets **all major desktop and mobile platforms**, with capability files plus permissions/scopes attached to windows and webviews;
- Dioxus positions itself as a **crossplatform app framework** with an integrated CLI for hot reload, bundling, and dev servers, but its deploy/bundle docs also make package-type and native-platform build limits explicit;
- Slint positions itself as a native GUI toolkit for **embedded, desktop, and mobile**, which means “client app in Rust” is no longer one ecosystem niche;
- AccessKit now gives Rust toolkits a real cross-platform accessibility substrate and already names multiple Rust integrations;
- but cargo/mobile glue is still fragmented enough that `cargo-mobile2` explicitly says it is maintained primarily for the Tauri use case and cannot broadly support all uses outside it;
- and localization/runtime-support truth remain separate sharp edges: ICU4X explicitly targets client-side and resource-constrained environments, Fluent remains an expressive message system, and `i18n-embed` shows there is still real demand for application-level embedding and runtime loading choices.

Together these signals justify treating client productization as a **frontier-worthy ecosystem seam** rather than leaving Rust apps as a pile of framework docs, capability manifests, localization files, a11y fixes, store checklists, and install notes.

## Stack layers

### 1) Client App Surface: the app boundary
Client App Surface owns the **declared product surface** for an app:
- app identities and flavors
- bridge catalogs
- platform capabilities and permissions
- lifecycle assumptions
- package/store profiles
- checked per-platform behavior

Client App Surface answers questions like:
- “What kind of app is this and where is it officially supported?”
- “Which bridge/API surfaces are public versus internal?”
- “Which platform capabilities and lifecycle hooks are part of the promise?”
- “What package or store identities belong to this app?”

Design rule: **client-app support must not be inferred only from framework templates, generated projects, or scattered Android/iOS/macOS manifest files**.

### 2) A11yKit: semantic usability truth
A11yKit owns the **accessibility and UI-testing boundary**:
- semantic trees and snapshots
- role/label/focus expectations
- framework-agnostic UI-test queries
- accessibility diffs and conformance reports

A11yKit answers questions like:
- “Can assistive technology actually understand this UI?”
- “Did a release regress labels, focus, or text-input exposure?”
- “What accessibility semantics are stable enough for CI and archaeology?”

Design rule: **visual screenshots and happy-path clicks must not masquerade as accessibility evidence**.

### 3) Localization Surface: language and region truth
Localization Surface owns the **locale/message/fallback boundary**:
- supported locales and support posture
- message catalogs and placeholder schemas
- negotiation and fallback policy
- runtime data/provider assumptions
- checked localized surface evidence

Localization Surface answers questions like:
- “Which locales are actually supported, and how well?”
- “What fallback or partial-locale behavior is intended?”
- “What runtime data or embedded resources are required?”

Design rule: **a folder of translation files is not the localization contract**.

### 4) Distribution Contract: shipping and install truth
Distribution Contract owns the **consumer-side delivery boundary**:
- visible channels and candidates
- prebuilt-vs-source selection posture
- verification and signature outcomes
- mirror/fallback behavior
- install receipts and local mutation records

Distribution Contract answers questions like:
- “What did the user actually install?”
- “Did the app come from a direct bundle, a store package, or a source-build fallback?”
- “Which verification checks ran and which were skipped?”

Design rule: **published artifacts and installed artifacts are related but not identical truths**.

### 5) Update Continuity: post-install lifecycle change
Update Continuity owns the **post-install mutation boundary**:
- current installed app identity and imported install receipts
- update feed/channel and comparator posture
- chosen update plan, delegation, restart, or staged-apply behavior
- apply/rollback/downgrade results
- managed-content ownership and uninstall scope

Update Continuity answers questions like:
- “What app version or bundle state did the device start from?”
- “What update candidate was chosen and under what comparator or rollout policy?”
- “What actually changed on the device and what rollback or uninstall scope exists now?”

Design rule: **install truth and update continuity must stay separate even when the same framework supplies both pieces**.

### 6) Support Envelope + DocProof: support and docs truth
Support Envelope and DocProof together own the **supportability boundary**:
- platform/runtime floors
- target/cfg assumptions
- source-build versus released-binary posture
- docs surface truth
- checked examples and support references

This layer answers questions like:
- “Which OS/runtime/SDK assumptions are official?”
- “Do the docs match the actual platform support and feature/capability posture?”
- “What does docs.rs show, and what target/cfg caveats remain?”

Design rule: **support claims must not be inferred from one successful simulator run, one docs.rs build, or one local packaging success**.

### 7) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Release / distribution** consumers can attach app-surface, package, verification, and install receipts.
- **Support / incident** consumers can escalate from declared app boundaries instead of starting from screenshots and folklore.
- **Atlas / learning** consumers can recommend credible Rust app paths without pretending there is one universal winner.
- **Rollout / experimentation** consumers can later import app/package/channel truth without redefining the app surface itself.

Design rule: **consumers import selected evidence; they do not redefine the app truth models**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the one true Rust app framework.”
It is a portable, reviewable stack with clear boundaries:

1. **App/package/capability truth first**
   - prove `app-surface/v0`, bridge catalogs, capability profiles, lifecycle profiles, and package profiles on one real app;
2. **Support/docs second**
   - attach `doc_cfg` / docs.rs / target/runtime-floor truth so support claims stop living only in guides and issue trackers;
3. **Accessibility third**
   - add `a11y-snapshot/v0`, `a11y-report/v0`, and UI-test evidence grounded in semantics rather than screenshots alone;
4. **Localization fourth**
   - attach locale catalogs, placeholder/fallback truth, and runtime-data assumptions without pretending all i18n stacks are the same;
5. **Distribution/install and rollout consumers fifth**
   - prove direct-bundle, store, or prebuilt/source-fallback installs can import the stack honestly, and only then let rollout/channel consumers build on top.

An eventual aggregate artifact may exist, but it should be a **thin pack of referenced artifacts**, not a new truth engine that erases the lane boundaries.

## Ranked first execution lanes
1. **App surface + package profile lane**
   - best first exporter because real Rust apps already have capability files, bridge APIs, and package/store identities even when the rest of the productization story is still fuzzy.
2. **Support/docs lane**
   - proves target/cfg/runtime-floor truth instead of README optimism.
3. **Accessibility lane**
   - proves the ecosystem can capture semantic UI truth across toolkits rather than treating accessibility as a post-hoc bug list.
4. **Localization lane**
   - proves locale support and runtime data assumptions can be reviewed like any other product contract.
5. **Distribution/install + rollout consumer lane**
   - proves the stack matters after build time and before support/incident archaeology.

## Non-goals
- one universal Rust GUI toolkit;
- one universal mobile/desktop shell;
- one giant app template or generated platform-control plane;
- flattening capabilities, lifecycle, accessibility, localization, distribution, and support into one fake “app readiness” schema;
- pretending app-store success, docs.rs builds, or screenshot tests alone prove product support.

## Archive implications
- The archive should now treat **Client App Surface + A11yKit + Localization Surface + Distribution Contract + Support Envelope** as a coupled **Client Productization Stack** in frontier discussions.
- Future revisions should prefer **portable app/package contracts, validated a11y semantics, locale/fallback truth, distribution/install receipts, support/docs truth, and consumer proofs** over new shells, bridge generators, app templates, or store-specific wrappers.
- When Distribution, Release, Support, Atlas, or Rollout work cites app readiness, they should import **app surface**, **a11y truth**, **locale truth**, **distribution/install truth**, and **support truth** separately.

## References (signals)
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tauri 2 stable release:
  https://v2.tauri.app/blog/tauri-20/
- Tauri capabilities / permissions:
  https://v2.tauri.app/security/capabilities/
  https://v2.tauri.app/learn/security/using-plugin-permissions/
- Dioxus guide and deploy docs:
  https://dioxuslabs.com/learn/0.7/
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- Slint docs:
  https://docs.slint.dev/latest/docs/slint/
- AccessKit overview:
  https://accesskit.dev/
- cargo-mobile2 docs / maintenance status:
  https://docs.rs/crate/cargo-mobile2/latest
- Project Fluent:
  https://projectfluent.org/
  https://projectfluent.org/fluent/guide/
- ICU4X charter / docs:
  https://github.com/unicode-org/icu4x
  https://docs.rs/icu/latest/icu/
- i18n-embed:
  https://docs.rs/i18n-embed
- OpenFeature Rust SDK:
  https://openfeature.dev/docs/reference/sdks/server/rust/
- Stabilize rustdoc `doc_cfg` feature:
  https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- docs.rs changed default targets:
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
