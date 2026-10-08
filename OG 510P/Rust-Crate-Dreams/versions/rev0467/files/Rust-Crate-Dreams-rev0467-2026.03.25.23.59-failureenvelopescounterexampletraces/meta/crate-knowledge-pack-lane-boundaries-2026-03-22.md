# Crate knowledge pack lane boundaries — 2026-03-22

Keep **P-0536** separate from these adjacent lanes.

## 1. Not rustdoc JSON normalization itself

If the main question is rustdoc JSON generation, caching, compatibility windows, or schema-version handling, that belongs primarily to **P-0051**.

P-0536 imports that substrate.
It does not replace it.

## 2. Not docs.rs parity evidence

If the main question is “did local intent match what docs.rs hosted and why not?”, that belongs primarily to **P-0472**.

P-0536 may import docs.rs presence facts, but it is not the general hosted-build parity lane.

## 3. Not documentation coverage review

If the main question is “which public APIs lack docs/examples and what debt remains?”, that belongs primarily to **P-0476**.

P-0536 owns the handoff pack above documentation sources, not the whole debt/review workflow.

## 4. Not doctest extraction / execution truth

If the main question is how examples were extracted, rewritten, executed, or support-classified for doctest purposes, that belongs primarily to **P-0455**.

P-0536 may import doctest-support facts, but it is not the general example execution lane.

## 5. Not guidance or troubleshooting packs

If the main question is “how should a blocked user recover from an error or misconfiguration?”, that belongs closer to **P-0512** or **P-0525**.

P-0536 owns canonical crate knowledge handoff, not live remediation strategy.

## 6. Not search engine / assistant product logic

If the main question is ranking, embedding, retrieval, conversational UX, or model behavior, that remains outside this lane.

P-0536 owns the **portable handoff artifact**, not the consumer’s product logic.

## 7. Not a full docs portal

If the main question is hosting, rendering, browsing, full-text UI, or documentation site generation, that is a different product class.

P-0536 should stay bundle-first and review-first.

## Sources

- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/builds
- https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- https://rust-lang.github.io/rfcs/2963-rustdoc-json.html

## 8. Not a docs archive mirror or downloader-first tool

If the main question is how to mirror docs.rs downloads, patch static assets, or build an offline docs browser, that is a different product class.

P-0536 may import download-archive facts, but it is not the general archive-mirroring lane.

## 9. Not an answer generator

If the main question is prompt construction, retrieval ranking, conversational behavior, or automatic answer writing, that remains outside this lane.

P-0536 may export compact machine-consumable slices, but it must keep **material basis**, **export policy**, and **excerpt lineage** reviewable instead of pretending generated answers are authoritative.
