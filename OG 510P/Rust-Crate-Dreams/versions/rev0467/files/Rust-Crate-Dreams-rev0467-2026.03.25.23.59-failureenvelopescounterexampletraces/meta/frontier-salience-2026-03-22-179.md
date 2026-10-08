# Frontier salience scan — 2026-03-22 (crate knowledge pack productization + cross-sector map)

This pass did **not** add another proposal.
It promoted one of the newest high-value lanes by making it more buildable and by checking it against a wider use-case map.

## Ranked frontier after this pass

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0011 Crate Health Contract Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0532 Async Runtime Assurance Profile Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0469 Cargo Rebuild Explanation Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0431 Public Dependency Boundary Kit**

## Why P-0536 moved up

The latest official signals strengthen it from several directions:

- docs remain Rust’s preferred canonical reference, while code study stays a major learning path and some learning behavior appears to be shifting toward LLM tooling;
- docs.rs now hosts rustdoc JSON and documents hosted README behavior, metadata knobs, sandbox limits, and target posture;
- Cargo/rustdoc JSON output still requires nightly + unstable flags, which means downstream consumers benefit from one version-aware, provenance-aware bundle rather than bespoke scraping;
- ecosystem challenges are increasingly domain-specific, which makes “one trustworthy crate handoff pack” more valuable to support, search, and review workflows than another general docs wrapper.

That combination makes **P-0536** a stronger contribution than it first looked.
It is not “AI tooling.”
It is **documentation authority infrastructure** for a world where more consumers are machine-mediated.

## Cross-sector conclusion

The new sector scan produced one strong pattern:

- highly specific domain work remains valuable, but the archive is already rich there;
- the scarcest and broadest-leverage missing work is still **shared support infrastructure** above existing substrate;
- therefore future sector passes should usually ask:
  1. does this need a genuinely new domain crate,
  2. or does it mainly need one of the shared support-contract lanes to become implementation-ready?

## What to reject after this pass

Do not add:

- another generic docs portal,
- another rustdoc JSON wrapper,
- another “chat with your crate” lane,
- another generic maintainer score,
- or another Cargo-performance umbrella crate

unless it clearly escapes the present ownership of **P-0536, P-0011, P-0535, P-0469, and P-0490**.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- https://doc.rust-lang.org/rustdoc/unstable-features.html
- https://rust-lang.github.io/rfcs/2963-rustdoc-json.html
