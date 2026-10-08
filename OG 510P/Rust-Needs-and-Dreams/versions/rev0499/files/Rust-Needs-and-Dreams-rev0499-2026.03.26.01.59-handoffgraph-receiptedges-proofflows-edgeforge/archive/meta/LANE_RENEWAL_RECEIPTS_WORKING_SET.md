## Current bet (rev0387)
The receipt corpus now covers the new **browser Wasm package** card.
That means the next practical move is not “prove the package-publication web lane exists.”
It is:
1. keep the browser-package receipt current as target, glue, and maintenance posture evolve;
2. keep browser-app, full-stack-web, and browser-package cards distinct instead of drifting back into one generic web lane;
3. renew the oldest central card whose lane-level answer materially changed;
4. only then widen the corpus again.

## Current bet (rev0386)
The receipt corpus now covers the new **full-stack Rust web product** card.
That means the next practical move is not “prove the full-stack web lane exists.”
It is:
1. keep the full-stack-web receipt current as SSR/hydration, server-function, and deployment posture evolve;
2. keep browser-only and full-stack web cards distinct instead of drifting back into one generic web lane;
3. decide whether the next split is **browser package / npm-published Wasm** or a renewal of the oldest central card whose lane-level answer changed;
4. only then widen the corpus again.


## Current bet (rev0385)
The receipt corpus now covers the new **browser web app** card.
That means the next practical move is not “prove the public web lane exists.”
It is:
1. keep the browser-web receipt current as render-mode, bundling, and deploy posture evolve;
2. decide whether the next split is **full-stack Rust web product** or **browser package / npm-published Wasm**;
3. renew the oldest central card whose lane-level answer materially changed;
4. only then widen the corpus again.

## Current bet (rev0384)
The receipt corpus now covers the missing **polyglot workspace component** card.
That means the next practical move is no longer “finish first receipts.”
It is:
1. renew the oldest central card whose lane-level answer materially changed;
2. keep the polyglot receipt current as Cargo workspace/config and host-package tooling move;
3. split a current card only when receipt evidence says it is no longer one lane;
4. only then widen the corpus with another public card.

## Current bet (rev0382)
The receipt corpus now covers the missing **installable CLI product** public-binary card.
That means the next practical move is no longer “prove the public CLI lane exists.”
It is:
1. keep the installable-product receipt current as Cargo/release-route tooling moves;
2. add the first receipt for `polyglot-workspace-component-2026Q1`;
3. renew older central cards when the lane-level answer changes;
4. only then widen the corpus with another public card.

## Current bet (rev0381)
The receipt corpus now covers the missing **publishable library** center card.
That means the next practical move is no longer “prove library discipline exists.”
It is:
1. keep the library receipt current as Cargo/docs.rs/crates.io surfaces move;
2. add the first receipt for `polyglot-workspace-component-2026Q1`;
3. renew older central cards when the lane-level answer changes;
4. only then widen the corpus with another public card.

# Meta: Lane Renewal Receipts Working Set

## Purpose
This is the compact reminder for revisions touching:
- `evidence/`
- `design/lane-default-renewal-receipts.md`
- `design/lane-default-evidence-bundle.md`
- `defaults/`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

Use it when the archive is large and the editor/assistant needs the current operating loop in one screen.

## Current bet (rev0380)
The archive’s next practical move is no longer just “add an evidence layer”.
It is:
1. instantiate that layer as **real renewal receipts**;
2. keep receipt sections visibly separated;
3. preserve exact package identity for named crates;
4. only then widen the default corpus materially.

## Required distinctions
Keep these separate in every receipt:
- default-card scope;
- renewal verdict;
- canonical references;
- registry / supply-chain evidence;
- API / compatibility evidence;
- maintenance / support-envelope facts;
- freshness / replay notes;
- lane-level judgment versus package-admission judgment.

## Exact-identity rule
If a receipt names a crate, prefer:
- exact crate identifier,
- direct docs / registry link,
- and an explicit note when lookalike names are part of the ecosystem risk.

Do not let colloquial memory replace exact identity.

## First files to re-read
1. `meta/ACTIVE_FRONTIER.md`
2. `meta/CANONICAL_WORKING_SET.md`
3. `meta/DEFAULT_CARD_RENEWAL_QUEUE.md`
4. `meta/DEFAULT_EVIDENCE_WORKING_SET.md`
5. `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`
6. `design/browser-wasm-package-default-lane.md`
7. `evidence/conservative-browser-wasm-package-2026Q1-renewal-2026-03-22.md`
8. `design/publishable-library-default-lane.md`
9. `design/lane-default-evidence-bundle.md`
10. `design/lane-default-renewal-receipts.md`
11. `evidence/README.md`
12. `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`
13. `evidence/conservative-internal-cli-2026Q1-renewal-2026-03-22.md`
14. `evidence/conservative-http-service-2026Q1-renewal-2026-03-22.md`
15. `evidence/polyglot-workspace-component-2026Q1-renewal-2026-03-22.md`
16. `evidence/script-repro-tiny-utility-2026Q1-renewal-2026-03-22.md`

## Default revision rule
Prefer, in order:
1. renew one existing card and update its receipt;
2. narrow a card whose receipt no longer supports the old claim;
3. add one bounded new card plus its first receipt;
4. only then add more abstract design prose.
