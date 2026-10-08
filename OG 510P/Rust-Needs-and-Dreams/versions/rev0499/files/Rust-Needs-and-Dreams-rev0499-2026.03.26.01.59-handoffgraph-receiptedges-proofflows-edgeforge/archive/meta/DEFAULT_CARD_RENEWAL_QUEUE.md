# Meta: Default Card Renewal Queue

## Purpose
This file is the compact queue for future LLM-driven revisions touching `defaults/` and `evidence/`.
It exists so the archive does not drift into adding side-lanes while the central cards age.

## Current note (rev0392)
The corpus now includes a first **native-shell mobile product** card and receipt:
- `defaults/conservative-native-shell-mobile-product-2026Q1.md`
- `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`

This means future queue discipline should keep the mobile/client lanes distinct in practice:
- **desktop app product**;
- **cross-platform mobile shell product**;
- **native-shell mobile product**;
- **polyglot workspace component**.

And after adding that split, the queue should again prefer **renewal of older central cards** before another widening move.

## Current maintained cards
1. `defaults/conservative-internal-cli-2026Q1.md`
2. `defaults/conservative-http-service-2026Q1.md`
3. `defaults/polyglot-workspace-component-2026Q1.md`
4. `defaults/script-repro-tiny-utility-2026Q1.md`
5. `defaults/conservative-publishable-library-2026Q1.md`
6. `defaults/conservative-public-sdk-family-2026Q1.md`
7. `defaults/conservative-installable-cli-product-2026Q1.md`
8. `defaults/conservative-desktop-app-product-2026Q1.md`
9. `defaults/conservative-browser-web-app-2026Q1.md`
10. `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
11. `defaults/conservative-browser-wasm-package-2026Q1.md`
12. `defaults/conservative-mobile-app-product-2026Q1.md`
13. `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
14. `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
15. `defaults/conservative-native-shell-mobile-product-2026Q1.md`

## Current receipt coverage
- covered:
  - `conservative-internal-cli-2026Q1`
  - `conservative-http-service-2026Q1`
  - `polyglot-workspace-component-2026Q1`
  - `script-repro-tiny-utility-2026Q1`
  - `conservative-publishable-library-2026Q1`
  - `conservative-public-sdk-family-2026Q1`
  - `conservative-installable-cli-product-2026Q1`
  - `conservative-desktop-app-product-2026Q1`
  - `conservative-browser-web-app-2026Q1`
  - `conservative-full-stack-rust-web-product-2026Q1`
  - `conservative-browser-wasm-package-2026Q1`
  - `conservative-mobile-app-product-2026Q1`
  - `conservative-worker-first-edge-web-product-2026Q1`
  - `conservative-portable-self-hosted-wasm-edge-host-2026Q1`
  - `conservative-native-shell-mobile-product-2026Q1`
- no current first-receipt gaps remain

## Preferred next moves
1. renew the oldest central card whose lane-level answer materially changed;
2. narrow or split a current card whose receipt no longer supports the old claim;
3. only then add one bounded new public card.

## Candidate next new cards only after renewal work
- browser + Node dual-target Wasm package overlay distinct from the browser-only package card
- raw custom Wasmtime embedder distinct from the Spin-centered self-hosted-host card
- durable internal library distinct from publishable public library
- safety-tilted public library
- safety-tilted desktop/native app lane distinct from the conservative desktop product card

## Anti-drift rule
If a candidate card does not beat “renew an older central card” on recurring value and official momentum, do not add it yet.
