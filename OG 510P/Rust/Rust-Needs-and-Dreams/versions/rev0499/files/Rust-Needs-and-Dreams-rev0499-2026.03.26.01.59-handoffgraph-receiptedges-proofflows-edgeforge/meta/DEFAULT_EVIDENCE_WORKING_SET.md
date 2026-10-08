
## Current note (rev0391)
The evidence layer now has a **portable self-hosted Wasm edge-host** card and receipt in addition to the managed-edge web lane.

That changes the maintenance order:
- keep the new portable-self-hosted-Wasm-host receipt current;
- keep **worker-first managed edge runtime** and **portable self-hosted Wasm edge host** distinct when renewing cards;
- prefer central-card renewal over novelty-card expansion;
- use `meta/DEFAULT_CARD_RENEWAL_QUEUE.md` when deciding whether a new lane really beats another renewal pass.

## Current note (rev0390)
The evidence layer now has a **public SDK-family** card and receipt in addition to the earlier library/app/script lanes.

That changes the maintenance order:
- keep the new public-SDK-family receipt current;
- keep **publishable library**, **public SDK family**, and **polyglot workspace component** distinct when renewing cards;
- prefer central-card renewal over novelty-card expansion;
- use `meta/DEFAULT_CARD_RENEWAL_QUEUE.md` when deciding whether a new lane really beats another renewal pass.

## Current note (rev0381)
The evidence layer now has a **library-centered** card and receipt in addition to app/script lanes.

That changes the maintenance order:
- keep the new publishable-library receipt current;
- finish receipt coverage for `polyglot-workspace-component`;
- prefer central-card renewal over novelty-card expansion;
- use `meta/DEFAULT_CARD_RENEWAL_QUEUE.md` when deciding whether a new lane really beats another renewal pass.

## Current note (rev0380)
The evidence layer is now instantiated as a first receipt corpus under `evidence/`.

That means future renewals should increasingly be understood as:
- default card,
- plus latest readable receipt,
- plus later diff/index layers when needed.

Additional hygiene import:
- preserve **exact package identity** for named crates; current RustSec lookalike removals make fuzzy naming a real archive risk, especially for LLM-driven edits.

# Meta: Default Evidence Working Set

## Purpose
This is the compact reminder for future revisions touching:
- `defaults/`
- `design/lane-default-evidence-bundle.md`
- `design/lane-default-evidence-pilot-program.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

Use it when the repo is large and the editor/assistant risks drifting back into prose-only default updates.

## Current bet (rev0391)
The archive’s next practical move is **not** “publish many more cards.”
It is:
1. renew central cards where lane-level answers moved;
2. keep the new **portable self-hosted Wasm edge host** lane distinct from **worker-first managed edge runtime**;
3. keep the **public SDK family** lane distinct from both **publishable library** and **polyglot workspace component**;
4. keep evidence receipts current for maintained defaults;
5. widen only when a new recurring lane clearly beats renewal work.

## Required distinctions
When renewing or adding a default card, keep these separate:
- canonical references;
- registry / supply-chain evidence;
- public API / compatibility evidence;
- maintenance / stewardship posture;
- support-envelope facts;
- freshness / replay inputs;
- final renewal judgment.

If these are flattened into one paragraph, the card is not ready.

## First files to re-read
1. `meta/ACTIVE_FRONTIER.md`
2. `meta/CANONICAL_WORKING_SET.md`
3. `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
4. `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
5. `design/portable-self-hosted-wasm-edge-host-default-lane.md`
6. `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
7. `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`
8. `design/worker-first-edge-web-product-default-lane.md`
9. `defaults/conservative-worker-first-edge-web-product-2026Q1.md`
10. `evidence/conservative-worker-first-edge-web-product-2026Q1-renewal-2026-03-22.md`
11. `design/public-sdk-family-default-lane.md`
12. `defaults/conservative-public-sdk-family-2026Q1.md`
13. `evidence/conservative-public-sdk-family-2026Q1-renewal-2026-03-22.md`
14. `design/sdk-productization-stack.md`
15. `design/lane-default-evaluation-framework.md`
16. `design/reviewable-lane-defaults-corpus.md`
17. `design/lane-default-evidence-bundle.md`
18. `design/lane-default-evidence-pilot-program.md`
19. `defaults/conservative-publishable-library-2026Q1.md`
20. `defaults/polyglot-workspace-component-2026Q1.md`
21. `defaults/conservative-internal-cli-2026Q1.md`
22. `defaults/conservative-http-service-2026Q1.md`
23. `defaults/script-repro-tiny-utility-2026Q1.md`

## Default revision rule
Prefer, in order:
1. renew one existing card with visible evidence imports;
2. add one bounded new card with strong official momentum;
3. narrow or demote an over-claimed card;
4. only then widen the corpus.
