# Design: Desktop app default lane

## Thesis
The defaults corpus now covers **internal CLI**, **installable public CLI**, **publishable library**, and a few narrower lanes, but it still lacks a boring answer for a recurring public product class Rust teams actively ask about:
**desktop applications with a real GUI**.

The ecosystem does not lack options.
It lacks a reviewable default lane that says when a team should currently start with:
- a webview-hosted shell,
- a native declarative UI,
- a Rust-first cross-platform app framework,
- or an immediate-mode / lower-level renderer path.

Read with:
- `design/client-productization-stack.md`
- `design/client-productization-pilot-program.md`
- `design/reviewable-lane-defaults-corpus.md`
- `defaults/conservative-desktop-app-product-2026Q1.md`
- `evidence/conservative-desktop-app-product-2026Q1-renewal-2026-03-22.md`

## Why this now
Several current signals converge on the same missing lane.

1. Rust’s March 20, 2026 challenges post still says ecosystem navigation suffers from **choice paralysis** and **tacit knowledge**.
   https://blog.rust-lang.org/2026/03/20/rust-challenges/

2. The 2025 State of Rust survey still says online docs remain the preferred canonical reference while LLM/editor-mediated learning rises.
   https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

3. Tauri 2 is stable and explicitly targets all major desktop and mobile platforms, but its own docs make webview, frontend, capability, and permission boundaries explicit rather than magical.
   https://v2.tauri.app/blog/tauri-20/
   https://v2.tauri.app/security/capabilities/
   https://v2.tauri.app/learn/security/using-plugin-permissions/
   https://v2.tauri.app/start/frontend/

4. Dioxus now presents a serious Rust-first cross-platform story with integrated tooling, but its own docs remain candid about system-webview assumptions on desktop and native-platform bundling limits.
   https://dioxuslabs.com/learn/0.7/
   https://dioxuslabs.com/learn/0.7/guides/platforms/desktop/
   https://dioxuslabs.com/learn/0.7/tutorial/bundle/

5. Slint is no longer only an embedded curiosity; it explicitly targets embedded, desktop, and mobile GUIs, and its docs expose backend/renderer choices instead of hiding them.
   https://slint.dev/
   https://docs.slint.dev/latest/docs/slint/guide/backends-and-renderers/backends_and_renderers/

6. AccessKit gives Rust toolkits a real shared accessibility substrate, which means the lane can now talk about a11y evidence separately from shell choice.
   https://accesskit.dev/

7. Mobile / store / native-project glue still remains fragmented enough that `cargo-mobile2` explicitly says it is maintained only for the Tauri use case, which is a warning against pretending the whole client-app story has one clean universal toolchain.
   https://github.com/tauri-apps/cargo-mobile2

Taken together, the next worthy corpus move is not a universal GUI winner.
It is a **desktop-app default lane** that stays honest about where the boring default currently is and where the serious alternatives win.

## The missing problem
Rust teams can already find framework comparisons and showcase pages.
What they still lack is a portable answer to:
- what should a boring cross-platform desktop app start with today?
- when is a webview-hosted shell the right default and when is it the wrong one?
- what accessibility substrate should be considered part of the lane instead of an afterthought?
- which packaging and support truths belong in the lane, and which belong in a later project-specific brief?

Current advice is scattered across:
- framework homepages,
- getting-started guides,
- bundle docs,
- accessibility notes,
- and maintainer folklore.

The defaults corpus can do something better:
**one bounded default card plus one readable receipt.**

## What the lane should optimize for
This lane is for teams that value:
- a supportable cross-platform desktop product,
- reviewable permissions/capabilities,
- sane packaging and distribution posture,
- and boring adoption over heroic renderer ideology.

It should optimize for:
- explicit app-shell choice;
- explicit permission/capability truth;
- explicit accessibility posture;
- explicit packaging/distribution posture;
- and visible escalation triggers when a desktop app really wants a different class of UI stack.

It should not optimize for:
- maximum theoretical purity,
- the most custom rendering control,
- or pretending mobile, desktop, embedded, and browser deployment are already one lane.

## Proposed lane shape
The lane should keep six truths separate.

### 1. App-shell truth
The card should say what kind of shell/runtime the default assumes.
For the conservative desktop lane today, that means a **desktop-first webview-hosted shell** is the default assumption.

Canon:
- https://v2.tauri.app/start/
- https://dioxuslabs.com/learn/0.7/guides/platforms/desktop/
- https://slint.dev/

### 2. Frontend/runtime truth
The lane should say whether it assumes:
- static web assets,
- a Rust-only UI layer,
- a native DSL/UI compiler,
- or immediate-mode / custom-renderer semantics.

Canon:
- https://v2.tauri.app/start/frontend/
- https://dioxuslabs.com/learn/0.7/
- https://docs.slint.dev/latest/docs/slint/guide/backends-and-renderers/backends_and_renderers/
- https://iced.rs/
- https://docs.rs/crate/egui/latest

### 3. Permission/capability truth
Desktop apps increasingly need to say what native/system powers are exposed, and to whom.
The default lane should reward frameworks that make that surface reviewable.

Canon:
- https://v2.tauri.app/security/capabilities/
- https://v2.tauri.app/learn/security/using-plugin-permissions/

### 4. Accessibility truth
A11y should not be hidden inside screenshots or demo videos.
The lane should keep accessibility substrate separate from app-shell choice and import AccessKit or semantic HTML posture where relevant.

Canon:
- https://accesskit.dev/
- https://slint.dev/blog/slint-1.1-released
- https://dioxuslabs.com/learn/0.7/tutorial/next_steps/

### 5. Packaging/distribution truth
Desktop product lanes are not only about UI code.
They also need a boring statement about bundle shapes, per-platform packaging, and when platform-native bundling constraints become a project-specific brief.

Canon:
- https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- https://v2.tauri.app/start/prerequisites/

### 6. Renewal-receipt truth
The lane should always carry a readable receipt that says:
- why the default still stands,
- which alternatives stayed serious,
- and why the judgment remains lane-level rather than project-specific.

Canon:
- `design/lane-default-renewal-receipts.md`
- `evidence/conservative-desktop-app-product-2026Q1-renewal-2026-03-22.md`

## Current lane judgment in theory
For the narrow scope of **cross-platform desktop product teams that want the most boring current default**, the lane should currently say:
- start with **Tauri 2**,
- use a simple static-asset frontend posture (usually Vite/SPA or equivalent),
- keep Rust↔frontend boundaries and capabilities explicit,
- keep accessibility evidence separate from shell choice,
- and escalate to **Slint** or **Dioxus** when the product wants a different UI/runtime contract.

Why Tauri gets the conservative default today:
- it is stable;
- it is explicitly desktop-capable and template-backed;
- it makes capabilities and plugin permissions reviewable;
- it is honest about frontend/static-host constraints;
- and it has the clearest “ordinary team can ship a desktop app” story in current primary docs.

Why it stays `default-with-caveats`:
- it is not the right default for embedded or resource-constrained native UI;
- it is not the right default for teams that want an all-Rust UI story;
- it is not the right default for apps that need lower-level rendering or immediate-mode interaction as a first principle;
- and mobile/store/tooling reality remains fragmented enough that the desktop lane should stay desktop-first.

## A thin companion-tool shape
If this became a tool contribution, the right shape would be thin:
- `cargo desktop-lane`
- or `desktop-product-pack/v0`

It should do boring review work:
- read app-shell/package truth;
- capture capability/permission files if present;
- capture bundling/deploy posture;
- attach accessibility posture notes;
- and emit a readable receipt.

It should **not** become:
- the one true GUI framework,
- a store-publishing control plane,
- a universal updater,
- or a scoreboard of Rust desktop frameworks.

## MVP for this archive
The archive does not need the tool first.
The MVP is:
1. a design note for the lane;
2. a default card;
3. a first receipt;
4. frontier updates so future revisions renew it rather than forget it.

## Why this is worthy
This would be a worthy Rust ecosystem contribution because it would:
- cover a recurring public product class the current corpus still under-serves;
- keep Tauri, Dioxus, Slint, iced, and egui visible without flattening them into one fake winner;
- connect the older **Client Productization Stack** to the newer defaults-and-receipts discipline;
- and turn “Rust GUI ecosystem energy” into one bounded, reviewable starting answer.

## Non-goals
- choosing a universal mobile lane;
- claiming Tauri is the answer for every GUI app;
- downgrading Slint or Dioxus into mere footnotes;
- pretending immediate-mode and retained/declarative UI are the same lane;
- or replacing project-specific client-productization briefs when packaging, store, accessibility, or runtime constraints dominate.
