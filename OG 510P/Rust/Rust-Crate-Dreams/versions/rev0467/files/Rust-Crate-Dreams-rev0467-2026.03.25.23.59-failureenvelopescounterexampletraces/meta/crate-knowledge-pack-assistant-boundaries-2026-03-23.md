# Crate Knowledge Pack assistant-facing boundaries — 2026-03-23

Keep the new answerability / claim-trace work inside **P-0536** without letting it expand into a generic AI product lane.

## 1. Not retrieval ranking or search quality

If the main question is embeddings, ranking, semantic retrieval, or which index/query system to use, that is outside this lane.

P-0536 owns the **portable pack and its honesty contract**, not search quality.

## 2. Not prompt engineering or answer writing

If the main question is prompt templates, model routing, citation style in generated answers, or autonomous response policy, that is outside this lane.

P-0536 may export compact sections and claim traces, but it is not the answer generator.

## 3. Not full offline docs hosting

If the main question is mirroring HTML, patching static assets, or building a local docs portal, that is a different product class.

P-0536 may import docs.rs downloads as materials, but it is not an offline browser.

## 4. Not docs coverage or execution truth

If the main question is undocumented APIs, doctest execution, or example-support classification, those remain primarily adjacent lanes.

P-0536 imports those facts into one handoff pack.
It does not replace their capture logic.

## 5. Not a universal correctness or safety oracle

A supported query class such as `getting_started` does not imply support for:
- performance advice,
- unsafe invariants,
- security posture,
- migration guarantees,
- or platform support beyond imported evidence.

The crate must keep refusal and manual-review zones first-class.

## Working rule

When future passes touch **P-0536**, prefer:
1. machine-facing pack structure,
2. query-support scope,
3. claim traceability,
4. refusal/manual-review honesty,
5. and portable bundle review.

Do not let the archive silently broaden into “assistant for Rust crates”.
