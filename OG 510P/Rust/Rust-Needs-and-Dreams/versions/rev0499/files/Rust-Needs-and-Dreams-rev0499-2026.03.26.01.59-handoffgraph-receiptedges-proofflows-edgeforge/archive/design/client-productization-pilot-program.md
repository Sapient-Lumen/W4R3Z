# Design: Client Productization Pilot Program

## Purpose
Turn the **Client Productization Stack** into an executable program instead of leaving it as an attractive synthesis.

The archive should evaluate Rust client-app work as a **ranked pilot program** spanning app surfaces, platform capabilities and package identity, accessibility semantics, localization/runtime data, distribution/install truth, and downstream support/release consumers.

## Why now
- Tauri, Dioxus, and Slint now make “Rust app” mean much more than one experimental desktop lane, but they expose different package, permission, and support realities.
- AccessKit means accessibility can finally be treated as shared substrate instead of a toolkit-specific afterthought.
- Localization is no longer optional for serious products, and Rust now has credible pieces across Fluent, ICU4X, and application-level embedding/loading paths.
- Mobile and store/distribution glue remain fragmented enough that `cargo-mobile2` openly scopes its maintenance around Tauri, which is a warning against pretending the ecosystem already has a clean productization layer.
- Dioxus’s bundle/deploy docs are useful precisely because they stay honest about package types and cross-build limits; that is the kind of truth the product layer must preserve rather than hide.
- docs/support truth is also moving: `doc_cfg` and docs.rs target changes mean app support claims need structured artifacts rather than README optimism.

## References (signals)
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tauri start/prerequisites/permissions/plugin docs: https://v2.tauri.app/start/ ; https://v2.tauri.app/start/prerequisites/ ; https://v2.tauri.app/security/permissions/ ; https://v2.tauri.app/plugin/
- Dioxus docs / getting started / deploy / bundle: https://dioxuslabs.com/learn/0.7/ ; https://dioxuslabs.com/learn/0.7/getting_started/ ; https://dioxuslabs.com/learn/0.7/tutorial/deploy/ ; https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- Slint site/docs/blog: https://slint.dev/ ; https://docs.slint.dev/latest/docs/slint/ ; https://slint.dev/blog/making-slint-desktop-ready
- AccessKit overview: https://accesskit.dev/
- cargo-mobile2 maintenance status: https://github.com/tauri-apps/cargo-mobile2
- Project Fluent: https://projectfluent.org/
- ICU4X: https://github.com/unicode-org/icu4x
- i18n-embed: https://docs.rs/i18n-embed
- OpenFeature Rust SDK: https://openfeature.dev/docs/reference/sdks/server/rust/
- rustdoc `doc_cfg` goal: https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- docs.rs target-default changes: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/

## Pilot ranking
### Pilot 1 — App-surface / capability / package lane
**Goal:** make app identities, bridge surfaces, platform capabilities, lifecycle assumptions, and package/store identities reviewable.

Deliver:
- `app-surface/v0`
- bridge catalogs
- capability profiles
- lifecycle profiles
- package profiles
- one checked desktop/mobile/embedded app lane

Success looks like:
- reviewers stop guessing what the app officially supports just because a template or manifest exists.

### Pilot 2 — Support/docs lane
**Goal:** make docs and support claims match the app/product reality.

Deliver:
- target/cfg/runtime-floor notes
- docs.rs / `doc_cfg` posture
- platform caveat attachments
- checked docs/examples tied to the app surface

Success looks like:
- support claims can be reviewed without spelunking through guides, simulator logs, and issue threads.

### Pilot 3 — Accessibility lane
**Goal:** prove semantic UI truth can be captured portably.

Deliver:
- `a11y-snapshot/v0`
- `a11y-report/v0`
- one query-driven UI test lane grounded in roles/labels/focus
- raw platform/accessibility attachments where needed

Success looks like:
- a regression like an unlabeled control or broken focus order becomes a reviewable diff instead of a vague bug report.

### Pilot 4 — Localization lane
**Goal:** make locale support and fallback behavior reviewable.

Deliver:
- `locale-surface/v0`
- message-catalog / placeholder truth
- fallback/negotiation plan
- runtime-data/provider notes
- one real localized surface check lane

Success looks like:
- teams can tell the difference between “we have translation files” and “this app officially supports locale X with fallback behavior Y.”

### Pilot 5 — Distribution / install / rollout consumer lane
**Goal:** prove the stack matters once the app ships.

Deliver:
- release/distribution imports for one direct-bundle or store-adjacent lane
- install receipt / verification / fallback notes
- optional rollout/channel import using existing experimentation tooling
- support/incident/archeology consumer examples

Success looks like:
- the stack can explain what the user actually got, not just what the app author intended to publish.

## Honest partial outcomes
A pilot may still succeed if it proves one of these narrower conclusions:
- app-surface/package truth is the main bottleneck and a11y/localization can follow later;
- accessibility wants one early toolkit-first substrate while other lanes stay app-first;
- localization/runtime-data truth is useful even before generalized UI/render snapshots settle;
- distribution/install receipts help more than another deployment wrapper right now.

## Failure modes to avoid
- inventing one universal GUI/runtime/store schema before proving consumers
- flattening app surface, a11y, locale, distribution, and support truth into one report
- pretending screenshot tests or one simulator run prove accessibility or platform support
- pretending app-store packaging and direct-bundle installs are the same lane
- turning the pilot into a stealth new framework, shell, or deployment SaaS

## Archive policy
Future revisions should prefer:
- app identity / capability / lifecycle / package truth,
- semantic accessibility reports,
- locale/fallback/runtime-data truth,
- distribution/install receipts with explicit fallback and verification posture,
- support/docs evidence,
- and ranked consumer pilots

over new shells, bridge generators, UI toolkit shootouts, or giant “cross-platform Rust app” marketing bundles.
