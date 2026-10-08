# Crate Knowledge Pack frontier — answerability scope, claim traces, and refusal honesty (2026-03-23)

The archive already had the right broad lane for **P-0536 Crate Knowledge Pack Kit**:
turn scattered docs/api/example surfaces into one reviewable handoff pack.
What was still too easy to fake was the last mile for support/search/assistant consumers.

## Main judgment

The sharper missing crate is not a “chat with your crate” layer.
It is a **receiver-facing answerability contract** above rustdoc/docs.rs/README/example substrate.

A worthy crate here should help another engineer answer these boring questions cleanly:

1. **What compact pack did we hand to the machine consumer?**
2. **Which classes of questions is that pack actually allowed to answer?**
3. **Which question classes are only partially supported, manual-review-only, or refused?**
4. **Which exported claims can be traced back to exact excerpts and source materials?**
5. **Which gaps come from missing materials versus deliberate export policy?**

That is now sharper because current official surfaces are rich enough to tempt overclaiming:
- docs.rs hosts rustdoc JSON, HTML docs, README content, semver/latest redirects, downloadable archives, and configurable build metadata;
- Cargo exposes experimental rustdoc JSON generation and scraped-example substrate;
- the survey says online docs remain canonical while some learning/support flows appear to be moving toward LLM tooling.

The result is a predictable failure mode:
**a compact pack can look polished while still failing to say what it can honestly answer.**

## What the crate should provide other people now

At minimum, a serious implementation should export:

- `assistant-context.pack.json`
- `query-support.matrix.json`
- `claim-trace.report.json`
- alongside `material-basis.receipt.json`, `export-policy.receipt.json`, and `excerpt-lineage.report.json`

Those six artifacts together let another team reopen the bundle and tell:
- what the machine-facing slice was,
- what question classes it covered,
- which claims were grounded,
- and which areas still required human review.

## Why this is still worth building

A generic retrieval stack can consume raw docs and still bluff about:
- support scope,
- evidence scope,
- unresolved zones,
- or claim provenance.

P-0536 is strongest when it supplies the boring contract *before* any search or assistant product logic starts.

## Boundaries that matter more now

Keep this lane separate from:
- rustdoc JSON generation / compatibility,
- docs.rs parity and hosted-build debugging,
- doctest extraction / execution,
- docs coverage review,
- ranking/retrieval/model prompting,
- and full offline-doc hosting.

## Near-term epic-crate framing

This lane counts as epic when it stops being “a nicer export format” and becomes:

1. a maintainable cargo-adjacent tool,
2. with a stable schema family,
3. with refusal/manual-review honesty,
4. with claim traceability,
5. and with portable bundles other organizations can archive and diff.
