## Current note (rev0392)
The corpus now includes a first **native-shell mobile product** card and receipt:
- `defaults/conservative-native-shell-mobile-product-2026Q1.md`
- `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`

That means future corpus revisions should treat **cross-platform mobile shell product** and **native-shell mobile product** as distinct maintained lanes rather than letting them drift back into one generic “Rust mobile” bucket.


## Current note (rev0391)
The corpus now includes a first **portable self-hosted Wasm edge host** card and receipt:
- `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
- `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`

That means future corpus revisions should treat **worker-first managed edge runtime** and **portable self-hosted Wasm hosting** as distinct maintained lanes rather than letting them drift back into one generic “Rust on the edge / Wasm host” bucket.

## Current note (rev0390)
The corpus now includes a first **public SDK family** card and receipt:
- `defaults/conservative-public-sdk-family-2026Q1.md`
- `evidence/conservative-public-sdk-family-2026Q1-renewal-2026-03-22.md`

That means future corpus revisions should treat **publishable library**, **public SDK family**, and **polyglot workspace component** as distinct maintained lanes rather than letting them drift back into one generic “Rust crate/client/library” bucket.


## Current note (rev0389)
The corpus now includes a first **worker-first edge web product** card and receipt:
- `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
- `evidence/conservative-worker-first-edge-web-product-2026Q1-renewal-2026-03-22.md`

That means future corpus revisions should treat **browser-first public web app**, **full-stack Rust web product**, **browser-consumed Wasm package**, and **worker-first edge web product** as distinct maintained lanes rather than letting them drift back into one generic “Rust web” bucket.


## Current note (rev0388)
The corpus now includes a first **mobile app product** card and receipt:
- `defaults/conservative-mobile-app-product-2026Q1.md`
- `evidence/conservative-mobile-app-product-2026Q1-renewal-2026-03-22.md`

That means future corpus revisions should treat **desktop-first public app product**, **mobile-first public app product**, and **polyglot workspace component** as distinct maintained lanes rather than letting them drift back into one generic client/mobile bucket.

## Current note (rev0387)
The corpus now includes a first **browser Wasm package** card plus its first renewal receipt.

That completes the three-way public-web split the archive had been promising:
- **browser-first public web app**;
- **full-stack Rust web product**;
- **browser-consumed Wasm package**.

Immediate consequence:
- keep package-publication guidance distinct from both app-product lanes;
- keep **crate identity**, **npm package identity**, **generated JS glue / `.d.ts` truth**, **bundler/browser target truth**, and **tool-maintenance truth** visibly separate inside browser-package guidance;
- and, after this split, return the corpus to renewal-first discipline rather than widening the web frontier indefinitely.

## Current note (rev0386)
The corpus now includes a first **full-stack Rust web product** card plus its first renewal receipt.

That turns the older web-productization frontier into two maintained answers instead of one vague “Rust web” category:
- **browser-first public web app**;
- **full-stack Rust web product**.

Immediate consequence:
- keep the browser-web card distinct from the new **full-stack Rust web product** card;
- keep both app-product lanes distinct from any future **browser package / npm-published Wasm** card;
- keep **dual-target build truth**, **SSR/hydration truth**, **server-function/API truth**, and **auth/session/deploy truth** visibly separate inside full-stack web guidance;
- and do not widen the public corpus faster than these web distinctions can be renewed honestly.

## Current note (rev0385)
The corpus now includes a first **browser web app** card plus its first renewal receipt.

That turns the older web-productization frontier into a current maintained answer for one bounded public lane.

Immediate consequence:
- keep the browser-web card distinct from any future **full-stack Rust web product** or **browser package / npm-published Wasm** card;
- keep **render mode**, **bundle/base-path/deploy posture**, **browser capability / interop**, and **service boundary** visibly separate inside web guidance;
- and do not widen the public corpus faster than these web distinctions can be renewed honestly.

## Current note (rev0384)
The corpus now includes the missing first **polyglot workspace / monorepo component** receipt.

That closes the last first-receipt gap among the current maintained cards.

Immediate consequence:
- keep the polyglot card distinct from any future **public SDK / generated-client** or host-specific public-package lane;
- prefer renewal of older high-centrality cards before widening the public corpus again;
- and keep **workspace/config truth**, **host-package truth**, and **boundary-framework truth** separate inside mixed-language guidance.

## Current note (rev0383)
The corpus now includes a first **desktop app product** card plus its first renewal receipt.

That corrects another real imbalance: the archive had client-productization theory and several public non-GUI cards, but still lacked a maintained desktop-first GUI answer.

Immediate consequence:
- keep the desktop-product card distinct from both installable CLI productization and the broader client-productization stack;
- finish missing first-receipt coverage for older high-centrality cards;
- and do not widen the public corpus faster than those cards can be renewed.

## Current note (rev0382)
The corpus now includes a first **installable CLI product** card plus its first renewal receipt.

That corrects another real imbalance: the archive had a good internal CLI card, but it still lacked a public-binary lane where release/distribution/support routes are first-class.

Immediate consequence:
- keep the installable-product card distinct from the internal CLI card,
- finish missing first-receipt coverage for older high-centrality cards,
- and do not widen the public corpus faster than those cards can be renewed.

## Current note (rev0381)
The corpus now includes a first **conservative publishable library** card plus its first renewal receipt.

That corrects a real imbalance: the archive had become stronger at helping app teams than crate authors.

Immediate consequence:
- keep the library card central,
- complete missing first-receipt coverage for other high-centrality cards,
- and do not widen the public corpus faster than those cards can be renewed.

## Current note (rev0380)
The corpus now has a first readable renewal-receipts layer under `evidence/`.

That means a maintained default card should increasingly be understood as:
- the card,
- the latest receipt,
- and later a diff/index trail when the answer moves.

This makes the corpus more auditable without pretending it is already fully mechanized.

## Current note (rev0379)
The corpus is no longer just “cards plus renewal inputs”.
It now has an explicit evidence layer in `design/lane-default-evidence-bundle.md`.

That means a corpus card should increasingly be understood as:
- human-readable default card,
- plus a portable evidence pack,
- plus a renewal judgment,
- plus a diff against the prior review when the answer moved.

This keeps the corpus from becoming a pile of attractive but weakly renewable notes.

# Design: Reviewable Lane Defaults Corpus

## Thesis
The archive already has the right **layer** in `design/reviewable-lane-defaults.md`.
What it still lacked was a maintained **corpus** of actual default cards.

That missing step matters.
Without a corpus, “Reviewable Lane Defaults” stays philosophical.
With a corpus, the archive can finally publish bounded answers to questions like:
- what should a conservative internal CLI team start with right now?
- what is the default conservative HTTP/service lane right now?
- what should a polyglot workspace do before choosing PyO3, CXX, UniFFI, or Node bindings?

This file defines the corpus-level discipline for those answers.

Read with:
- `design/reviewable-lane-defaults.md`
- `design/lane-default-evaluation-framework.md`
- `design/adoption-navigation-bundle.md`
- `defaults/conservative-internal-cli-2026Q1.md`
- `defaults/conservative-http-service-2026Q1.md`
- `defaults/conservative-publishable-library-2026Q1.md`
- `defaults/conservative-public-sdk-family-2026Q1.md`
- `defaults/polyglot-workspace-component-2026Q1.md`
- `defaults/conservative-desktop-app-product-2026Q1.md`
- `defaults/conservative-browser-web-app-2026Q1.md`
- `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
- `defaults/conservative-browser-wasm-package-2026Q1.md`
- `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
- `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

## Why this is the next practical move
The archive had already done three useful things:
1. shaped **Adoption Navigation** into a concrete composition bundle;
2. promoted **Reviewable Lane Defaults** as the execution seam beneath it; and
3. clarified that scoped defaults are different from both candidate-space maps and project-specific adoption briefs.

But it still had not done the thing that makes the layer real:
**publishing maintained default cards.**

That is now the stronger move than another adjacent top-band note.

## What the corpus is
The corpus is a deliberately small maintained set of default cards for recurring project classes.
Each card should be:
- scoped,
- reviewable,
- freshness-aware,
- linked to canonical sources,
- explicit about serious alternatives,
- and explicit about when to escalate to a project-specific brief.

## What the corpus is not
The corpus is not:
- a global blessed-crates list;
- a ranking of the entire ecosystem;
- a replacement for Atlas candidate space;
- a replacement for project-specific adoption briefs;
- a starter-template catalog;
- or a hidden governance engine.

## Corpus artifact family
The corpus should stay small and use the existing lane-default artifact ideas.

### 1. Default card
A human-readable default card for one recurring project class.
Stored under `defaults/`.

### 2. Candidate matrix
A compact comparison of serious candidate lanes for that project class.
This can live inside the card or next to it.

### 3. Canonical reference set
Links to the maintainer-authored references worth importing first.

### 4. Renewal inputs
A short list of the signals that should be rechecked before renewal:
- canonical docs,
- crates.io / docs.rs signals,
- support or maintenance posture,
- obvious ecosystem motion,
- and any known compatibility shifts.

### 5. Renewal report
A short diff-oriented note when the default is renewed, demoted, narrowed, or replaced.

## Publish criteria
A card belongs in the corpus only if:
- the project class recurs often enough to matter;
- the scope is narrow enough to avoid fake universality;
- at least one serious alternative remains visible;
- the lane has enough canon/evidence to be responsibly reviewable;
- and renewal can be done in bounded time.

## Current ranked corpus entries
### 1. Conservative internal CLI / automation
Stored at `defaults/conservative-internal-cli-2026Q1.md`.

Why first:
- one of Rust’s strongest and most common adoption lanes;
- a real place where choice paralysis hurts;
- low enough complexity for a reusable default to be honest.

### 2. Conservative HTTP/service baseline
Stored at `defaults/conservative-http-service-2026Q1.md`.

Why second:
- highly consequential;
- forces runtime and middleware consequences into view;
- commonly over-simplified by folklore.

### 3. Conservative publishable library
Stored at `defaults/conservative-publishable-library-2026Q1.md`.

Why third:
- this is the corpus’s missing center card for reusable crates;
- Cargo/docs.rs/crates.io now expose enough explicit contract surface to support a reviewable lane;
- it captures manifest truth, docs truth, semver truth, public API boundary, and package-identity hygiene together.

### 4. Conservative public SDK family
Stored at `defaults/conservative-public-sdk-family-2026Q1.md`.

Why fourth:
- the archive already had a strong abstract SDK-productization frontier but still lacked one maintained answer for the most recurring public generated-client lane;
- current Rust-native OpenAPI tooling plus Oxide-style checked-in-generation practice make a bounded default unusually legible;
- it keeps source contract, generated surface, runtime/config posture, and release/docs truth reviewable together instead of smearing them across generic library advice.

### 5. Polyglot workspace component
Stored at `defaults/polyglot-workspace-component-2026Q1.md`.

Why fifth:
- many real teams adopt Rust inside larger non-Rust systems;
- this is where invisible packaging/runtime/boundary assumptions cause trouble;
- the correct default is often architectural restraint rather than immediate framework commitment.

### 6. Conservative desktop app product
Stored at `defaults/conservative-desktop-app-product-2026Q1.md`.

Why sixth:
- the corpus still under-served public GUI products even after gaining CLI-product and library cards;
- the ecosystem now has several credible desktop paths, which makes a bounded boring default unusually valuable;
- it connects older client-productization research to the newer defaults-and-receipts discipline.

### 7. Conservative browser web app
Stored at `defaults/conservative-browser-web-app-2026Q1.md`.

Why seventh:
- the archive already had a strong web-productization strategy layer but still lacked a maintained browser-first answer;
- browser-facing Wasm is a mainstream Rust lane, not a side experiment;
- a bounded default is unusually valuable because render mode, bundling, deploy posture, and browser interop are easy to flatten into folklore.

### 8. Conservative full-stack Rust web product
Stored at `defaults/conservative-full-stack-rust-web-product-2026Q1.md`.

Why eighth:
- the browser-web split exposed the next equally central missing answer for web teams that want Rust to own both browser and server halves;
- current docs now make the **CSR** versus **SSR/full-stack** split explicit enough to support a bounded maintained card;
- a bounded default is unusually valuable because dual-target builds, hydration, server functions, and deploy/auth truth are easy to flatten into folklore.

### 9. Conservative browser Wasm package
Stored at `defaults/conservative-browser-wasm-package-2026Q1.md`.

Why ninth:
- it completes the maintained three-way public-web split between deployable browser apps, Rust-owned full-stack web products, and reusable browser-consumed packages;
- current docs and maintenance signals make package identity, JS glue, target selection, and tool-maintenance caveats explicit enough to support a bounded card;
- a bounded default is unusually valuable because browser-package publication is still easy to flatten into either app-framework folklore or one-tool nostalgia.

### 10. Conservative mobile app product
Stored at `defaults/conservative-mobile-app-product-2026Q1.md`.

Why tenth:
- the corpus still lacked a maintained mobile-first product answer even after gaining desktop GUI, web, and package-publication cards;
- current signals make it clear that mobile guidance should not be flattened into either the desktop card or the generic polyglot-component lane;
- a bounded default is unusually valuable because shell/runtime choice, Rust-core boundaries, native escape hatches, and store/signing truth are easy to flatten into folklore.

### 11. Conservative worker-first edge web product
Stored at `defaults/conservative-worker-first-edge-web-product-2026Q1.md`.

Why eleventh:
- it closes the remaining gap in the archive’s public web/runtime map by separating managed edge-runtime products from both full-stack origin hosting and browser/package lanes;
- current docs now make runtime limits, bindings, service decomposition, routes/assets, and version/deploy posture explicit enough to support a bounded maintained card;
- a bounded default is unusually valuable because managed edge runtime work is still easy to flatten into either provider marketing or generic “serverless” folklore.

### 12. Script / repro / tiny utility
Stored at `defaults/script-repro-tiny-utility-2026Q1.md`.

Why twelfth:
- narrow but recurring scope;
- strong current official momentum around cargo-script / single-file packages;
- useful as a bounded lane, but less central than the broader app, library, and public-product cards.

## Default-card requirements
Every corpus card should say, in plain language:
- the scope;
- the default lane;
- why it is default *here*;
- serious alternatives and when they win;
- core slot guidance;
- escalation triggers;
- canonical references;
- renewal inputs;
- and explicit non-goals.

## What makes this a worthy contribution
A maintained corpus would be a worthy Rust ecosystem contribution because it would:
- reduce repeated recommendation work;
- preserve alternatives instead of hiding them;
- keep canon and freshness visible;
- help starter/bootstrap/onramp tooling consume bounded defaults;
- and give assistants something better to import than vibes.

The important thing is that the corpus is not just documentation.
It is a review discipline for **current scoped defaults**.

## What future revisions should do next
Prefer one of these moves:
1. improve the evaluation framework;
2. renew one existing default card;
3. add one new default card for a truly recurring project class;
4. add a bounded renewal report when the ecosystem shifted materially.

Do **not** respond to every new Rust blog post by minting another top-band seam.
The corpus only becomes valuable if it is maintained.
