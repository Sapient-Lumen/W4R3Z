# Frontier salience — 2026-03-22 (190)

This pass did **not** open another Cargo feature lister, docs renderer, combo runner, or workspace-speed helper.
It deepened **P-0528 Cargo Feature Surface Contract Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0036 MSRV Workspace Lab**
8. **P-0532 Async Runtime Assurance Profile Kit**
9. **P-0469 Cargo Rebuild Explanation Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**
11. **P-0528 Cargo Feature Surface Contract Kit**

## Why P-0528 was the right lane to deepen now

Fresh official Cargo and docs.rs sources now make the missing layer more specific than “better feature docs” or “run more combinations”:

- Cargo’s feature reference still documents the sharp truths: default-feature leakage, SemVer sensitivity, optional-dependency aliases, `dep:` hiding, `?` forwarding, and the practical need to document which features are actually meant for users.
- That same reference now notes a crates.io limit of 300 features per published crate version, which increases the value of public-surface discipline.
- Resolver-v2 docs and the Rust 2021 edition-guide note keep scope-sensitive behavior concrete across target-specific dependencies, build/proc-macro edges, dev edges, workspace package selection, and `--no-default-features` behavior.
- docs.rs metadata still lets a crate build public docs with `features`, `all-features`, `no-default-features`, and target/default-target choices, which means the hosted public docs surface can differ from what downstream users build or support.
- Release notes and RFCs around weak/namespaced features and resolver-v2 keep signaling that Cargo features are not a solved “just read the table” problem.
- Survey and challenge work still say docs are canonical while compile/resource pain and ecosystem-navigation tacit knowledge remain active friction.

That combination sharpens the missing crate.
It is not most missing as another feature table viewer.
It is missing as a **portable feature-support contract** for:

1. **public names versus hidden plumbing**,
2. **named supported profiles**,
3. **exact observation scope**,
4. **hosted public-doc feature posture**,
5. **explicit conflict and unification risk**, and
6. **portable support bundles**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. one **feature-surface receipt** saying which feature names are public contract versus dependency plumbing;
2. one **activation-profile report** saying which named profiles are observed, sampled, unsupported, or still recipe-only;
3. one **resolution-scope receipt** saying which command/workspace/target scope those answers came from;
4. one **hosted-feature-profile receipt** saying what docs.rs or equivalent public docs are actually showing users;
5. one **unification/conflict answer** that keeps resolver and conflict semantics honest; and
6. one **portable feature-support bundle** that another reviewer can archive and diff later.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0528**, **P-0036**, **P-0469**, **P-0484**, and **P-0536**.

Especially resist:

- another feature table viewer that cannot export observation scope,
- another combo runner that cannot publish supported profile meaning,
- another docs.rs feature-page helper that cannot separate hosted docs posture from support truth,
- or another workspace feature helper that cannot hand another reviewer one honest bundle.
