# Frontier salience — 2026-03-22 (189)

This pass did **not** open another docs portal, retrieval wrapper, or assistant-facing UX lane.
It deepened **P-0536 Crate Knowledge Pack Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0490 Cargo Lock Contention Witness Kit**
7. **P-0469 Cargo Rebuild Explanation Kit**
8. **P-0486 Debuggability Support Contract Kit**
9. **P-0036 MSRV Workspace Lab**
10. **P-0532 Async Runtime Assurance Profile Kit**

## Why P-0536 was the right lane to deepen now

Fresh official docs and ecosystem signals now make the missing layer more specific than “better crate docs tooling”:

- the 2025 State of Rust survey still says online documentation is the preferred canonical reference and that some learning behavior appears to be moving toward LLM tooling;
- the March 2026 challenge write-up still says ecosystem guidance and domain-specific learning materials deserve investment;
- docs.rs now explicitly hosts rustdoc JSON, hosted README surfaces, custom metadata, build summaries, and downloadable documentation archives;
- but docs.rs also says rustdoc JSON may have older `format_version`s, only started being built on 2025-05-23, and shorthand URLs deliberately float across semver or `latest` resolutions;
- download archives contain all-target HTML but still carry static-root and invocation-specific asset caveats;
- and Cargo/rustdoc still describe JSON output as experimental/nightly substrate.

That combination sharpens the missing crate.
It is not most missing as another viewer, retriever, or assistant wrapper.
It is missing as a **portable crate-knowledge contract** for:

1. **exact material basis**,
2. **export policy / redaction honesty**,
3. **excerpt-lineage reviewability**,
4. **portable knowledge-pack bundles**, and
5. **manual-review zones when hosted materials, versions, or formats stay caveated**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. one **material-basis receipt** saying what exact docs.rs / rustdoc / README / archive materials fed the pack;
2. one **export-policy receipt** saying what source kinds and redaction rules were allowed for a support/search/assistant export;
3. one **excerpt-lineage report** saying which exact fragments made it into the slice;
4. one **portable pack manifest** tying those answers to API authority, docs sources, example lineage, visibility, and drift; and
5. one **manual-review zone** whenever floating redirects, absent hosted JSON, or unstable JSON/output-format stories outrun what the bundle can honestly prove.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0536**, **P-0051**, **P-0472**, **P-0476**, and **P-0455**.

Especially resist:

- another docs portal that cannot export a pinned material basis,
- another retrieval/indexing helper that cannot export a slice policy and excerpt lineage,
- another rustdoc/docs.rs wrapper that cannot explain hosted-vs-imported authority,
- or another “assistant for crate docs” idea that cannot hand another reviewer one honest portable pack.
