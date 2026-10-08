# Renewal receipt: conservative desktop app product (2026-03-22)

## Subject
- default card: `defaults/conservative-desktop-app-product-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0383
- scope: desktop-first Rust GUI products where a boring cross-platform starting lane matters more than framework maximalism
- non-goal: blessing one framework for all GUI, mobile, embedded, or internal-tool cases

## Renewal verdict
**add as new card**

The defaults corpus still lacked a public GUI/product card.
The correct lane-level answer for this narrow scope is now:
- **Tauri 2** as the conservative default shell,
- explicit capability and plugin-permission posture,
- explicit frontend/static-host assumptions,
- separate accessibility posture rather than screenshot theater,
- and visible escalation to **Slint** or **Dioxus** when the product wants a different runtime/UI contract.

## Canon import checked this round
Primary surfaces re-read:
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tauri 2 stable release:
  https://v2.tauri.app/blog/tauri-20/
- Tauri overview / start:
  https://v2.tauri.app/start/
- Tauri frontend configuration:
  https://v2.tauri.app/start/frontend/
- Tauri capabilities:
  https://v2.tauri.app/security/capabilities/
- Tauri plugin permissions:
  https://v2.tauri.app/learn/security/using-plugin-permissions/
- Tauri prerequisites:
  https://v2.tauri.app/start/prerequisites/
- Dioxus overview:
  https://dioxuslabs.com/learn/0.7/
- Dioxus getting started:
  https://dioxuslabs.com/learn/0.7/getting_started/
- Dioxus desktop:
  https://dioxuslabs.com/learn/0.7/guides/platforms/desktop/
- Dioxus bundle:
  https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- Dioxus deploy:
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- Slint homepage:
  https://slint.dev/
- Slint backends/renderers:
  https://docs.slint.dev/latest/docs/slint/guide/backends-and-renderers/backends_and_renderers/
- Slint accessibility note:
  https://slint.dev/blog/slint-1.1-released
- AccessKit overview:
  https://accesskit.dev/
- iced docs:
  https://docs.rs/iced/latest/iced/
- egui docs:
  https://docs.rs/crate/egui/latest
- cargo-mobile2 maintenance status:
  https://github.com/tauri-apps/cargo-mobile2

Canon judgment:
- Tauri currently provides the clearest conservative desktop product lane because it is stable, template-backed, explicit about frontend/static-host constraints, and explicit about capabilities and plugin permissions.
- Dioxus is a serious Rust-first alternative, but its own docs still keep system-webview desktop rendering and native-platform bundling limits visible, so it remains a serious alternative rather than the conservative default here.
- Slint is a serious native/declarative alternative with unusually strong embedded/desktop/mobile continuity and now-credible accessibility signals.
- iced and egui remain important watch lanes, but their current documentation posture keeps them outside this conservative product default.

## Toolkit / runtime import
Imported judgments:
- **Tauri** wins the default slot for boring cross-platform desktop products because it makes the shell/frontend/permission model inspectable instead of magical.
- **Dioxus** wins when Rust-first UI and integrated tooling matter more than the lane’s conservative shell choice.
- **Slint** wins when native rendering, declarative UI, or embedded/Desktop continuity matter enough that webview-hosted is the wrong default.
- **iced** and **egui** stay visible because a useful corpus card must not flatten renderer style and interaction model into one story.

## Accessibility / support import
Imported judgments:
- AccessKit materially changes the review story because it gives Rust toolkits a real shared accessibility substrate.
- Slint’s desktop accessibility support via AccessKit is strong evidence that a11y can no longer be treated as outside the lane.
- For Tauri/Dioxus-style webview UIs, semantic HTML and explicit a11y checks remain the honest starting posture.
- The card should stay conservative and avoid claiming a generalized cross-framework accessibility proof standard that current primary docs do not yet support.

## Packaging / lifecycle import
Imported judgments:
- Desktop product lanes are not only about UI code: Tauri prerequisites and Dioxus bundling/deploy docs make packaging/system-dependency truth part of the real lane.
- Dioxus’s own docs are particularly useful here because they stay explicit about native-platform bundling limits.
- cargo-mobile2’s explicit Tauri-only maintenance scope is a warning that this default card must stay **desktop-first**, not pretend the whole client-app lifecycle is already unified.

## Maintenance / support-envelope import
Support-envelope facts that still hold:
- this lane is strongest for teams that want a boring desktop product starting point, not a universal client-app doctrine;
- client-app support burden rises quickly once platform packaging, updater, store, or localization requirements become dominant;
- therefore the default should stay `default-with-caveats` and escalate early when the project’s real constraints differ.

Maintenance judgment:
- the lane deserves a maintained default card because it fills a real public-product gap in the corpus;
- but it should stay narrow enough that later revisions can split off **mobile-first client product**, **native/embedded HMI**, or **operator-console/immediate-mode** lanes without pretending they were always the same thing.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://v2.tauri.app/blog/tauri-20/
- https://v2.tauri.app/start/
- https://v2.tauri.app/start/frontend/
- https://v2.tauri.app/security/capabilities/
- https://v2.tauri.app/learn/security/using-plugin-permissions/
- https://v2.tauri.app/start/prerequisites/
- https://dioxuslabs.com/learn/0.7/
- https://dioxuslabs.com/learn/0.7/getting_started/
- https://dioxuslabs.com/learn/0.7/guides/platforms/desktop/
- https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- https://slint.dev/
- https://docs.slint.dev/latest/docs/slint/guide/backends-and-renderers/backends_and_renderers/
- https://slint.dev/blog/slint-1.1-released
- https://accesskit.dev/
- https://docs.rs/iced/latest/iced/
- https://docs.rs/crate/egui/latest
- https://github.com/tauri-apps/cargo-mobile2

Replay notes:
- renew when Tauri’s shell/frontend/capability story changes materially;
- renew when Dioxus’s desktop renderer or bundle story changes enough to move the default;
- renew when Slint’s native/declarative path becomes the clearer boring default for a narrower central scope;
- split the card when the archive is ready for separate **mobile-first** or **native/embedded HMI** client-product cards.

## Lane judgment
Add the card as a maintained public default.

Why:
- it fills the biggest remaining GUI/product gap in the maintained defaults corpus;
- it turns older client-productization notes into a bounded current answer;
- and it does so without pretending one Rust GUI framework has already won the whole ecosystem.

## Open watch items
- whether a separate **mobile-first client product** card now deserves to split away from the desktop-first lane;
- whether Dioxus’s future desktop renderer changes its placement materially;
- whether Slint should eventually become the conservative default for a narrower native-first desktop lane;
- whether the archive should add a separate **immediate-mode operator console / tool UI** card rather than forcing egui into this product lane.
