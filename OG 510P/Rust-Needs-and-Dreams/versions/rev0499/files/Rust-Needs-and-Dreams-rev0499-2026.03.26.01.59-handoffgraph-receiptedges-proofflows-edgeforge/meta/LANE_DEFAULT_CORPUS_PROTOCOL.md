## Current note (rev0392)
The corpus now includes a first **native-shell mobile product** card and receipt:
- `defaults/conservative-native-shell-mobile-product-2026Q1.md`
- `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`

This means future corpus revisions should treat **cross-platform mobile shell product** and **native-shell mobile product** as two different maintained client lanes rather than collapsing them back into one generic “Rust mobile” bucket.

# Meta: Lane Default Corpus Protocol

## Purpose
This file is the small operating protocol for maintaining `defaults/`.
It exists because the archive now has real default cards and future revisions need a repeatable way to renew, narrow, replace, or extend them without collapsing back into folklore.

Read first when touching:
- `design/reviewable-lane-defaults.md`
- `design/lane-default-evaluation-framework.md`
- `design/reviewable-lane-defaults-corpus.md`
- anything under `defaults/`

## Current note (rev0391)
The corpus now includes a first **portable self-hosted Wasm edge host** card and receipt:
- `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
- `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`

This means future corpus revisions should treat **browser-first public web app**, **full-stack Rust web product**, **browser-consumed Wasm package**, **worker-first edge web product**, and **portable self-hosted Wasm edge host** as five different maintained public web/edge lanes rather than collapsing them back into one generic web bucket.

## Current corpus (rev0391)
1. `defaults/conservative-internal-cli-2026Q1.md`
2. `defaults/conservative-http-service-2026Q1.md`
3. `defaults/conservative-publishable-library-2026Q1.md`
4. `defaults/conservative-public-sdk-family-2026Q1.md`
5. `defaults/polyglot-workspace-component-2026Q1.md`
6. `defaults/script-repro-tiny-utility-2026Q1.md`
7. `defaults/conservative-installable-cli-product-2026Q1.md`
8. `defaults/conservative-desktop-app-product-2026Q1.md`
9. `defaults/conservative-browser-web-app-2026Q1.md`
10. `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
11. `defaults/conservative-browser-wasm-package-2026Q1.md`
12. `defaults/conservative-mobile-app-product-2026Q1.md`
13. `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
14. `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
15. `defaults/conservative-native-shell-mobile-product-2026Q1.md`

## Required distinctions
Future default-corpus revisions must keep these truths separate:
- project-class scope;
- current default lane;
- serious alternatives;
- slot guidance;
- escalation triggers;
- canonical references;
- renewal inputs;
- local institutional overlays;
- project-specific adoption briefs.

Do **not** let one default card silently become:
- the whole ecosystem atlas,
- an org-local policy overlay,
- a starter-template verdict,
- or a one-off project recommendation.

## When to update the corpus
Update the corpus when one of these is true:
- a recurring project class now has enough evidence to deserve a maintained default card;
- a current default card has materially drifted;
- a current serious alternative should become the default or vice versa;
- or the scope of a default card was over-broad and needs narrowing.

Do **not** update the corpus merely because one new blog post or one new crate release exists.
Renew only when the lane-level answer plausibly changed.

## Standard review sequence
1. Re-read `meta/ACTIVE_FRONTIER.md` and `meta/CANONICAL_WORKING_SET.md`.
2. Re-read `design/lane-default-evaluation-framework.md`.
3. Re-read the affected default card(s).
4. Check current canonical docs and current official Rust signals.
5. Decide whether the change is:
   - no change,
   - renewal,
   - narrowing,
   - replacement,
   - demotion to project-specific only,
   - or addition of a new card.
6. Update mirror copies and manifest in the same revision.

## Preferred moves
Prefer, in order:
1. renewing one existing default card;
2. improving the evaluation framework;
3. adding one truly recurring project-class card;
4. recording a narrowing/demotion when a public default was over-claiming.

Avoid adding many new default cards in one revision unless the evidence is overwhelming.

## Hygiene rule for LLMs
When summarizing or extending the corpus, always say:
- what the scope is,
- what the default is,
- what the serious alternatives are,
- and when to escalate.

If those four things are not obvious, the default card is not ready.
