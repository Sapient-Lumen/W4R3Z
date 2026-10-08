# Design note: Python host lane map (extension ABI, free-threading, async bridges, and CPython-adoption adjacency)

## Goal
Sharpen the archive’s **Python lane** beneath **Host Package Kit** and **Polyglot Productization Stack** so future revisions stop flattening all Python/Rust work into one fake “PyO3 support” verdict.

The ecosystem now has several real but non-equivalent Python lanes:
- ordinary CPython extension modules with the full CPython API,
- limited-API / `abi3` extension modules,
- free-threaded Python extension modules,
- async bridge lanes joining Rust futures to Python `asyncio`,
- packaging / link / test / wheel-matrix handoff,
- and an adjacent-but-distinct lane for **embedding Python in Rust** or introducing Rust into CPython itself.

A worthy contribution here is **not** another wrapper that hides those differences.
It is a thin review layer that keeps them explicit and comparable.

## Why this note is needed now
- The Rust project’s February 2026 program-management update says the Rust/CPython collaboration is actively discussing: safely modeling Python objects attached/detached from Python threads, building/linking Rust std into Python extension modules without exposing conflicting symbols, per-target linker-argument differences for `bin` and `lib` in one crate, potential async interop between Rust and `asyncio`, and the broader problem of introducing Rust into a large existing C codebase.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- PyO3’s main guide still deliberately presents **two big families**: writing native Python modules in Rust, and embedding Python in a Rust binary. That is already enough to prove “Python support” is not one lane.
  https://pyo3.rs/main/
  https://pyo3.rs/main/building-and-distribution
- PyO3’s build/distribution docs say the `abi3` limited API can reduce wheel counts across Python versions, but only by restricting the Python API surface that an extension may use.
  https://pyo3.rs/main/building-and-distribution
  https://pyo3.rs/v0.28.2/features
- PyO3’s free-threaded guidance says the free-threaded build uses a **new ABI** and does **not** have an equivalent to the limited API; if `abi3` is enabled, PyO3 warns and ignores it for free-threaded builds.
  https://pyo3.rs/v0.28.2/free-threading
- PyO3 0.28.0 also made support for free-threaded Python opt-out rather than opt-in, which is a strong signal that this lane is graduating from curiosity to reviewable product concern.
  https://pyo3.rs/v0.28.2/changelog
- PyO3’s async docs say the built-in awaitable lane is explicitly **`asyncio`-only for now**, while `pyo3-async-runtimes` exists as a separate bridge crate with first-class support for popular Rust runtimes. That means “Rust async in Python” is a real lane, but not a universal one.
  https://pyo3.rs/v0.28.2/async-await
  https://docs.rs/crate/pyo3-async-runtimes/latest
- maturin’s distribution docs make manylinux / musllinux compliance, cross-compilation, and wheel portability first-class packaging concerns, while the PyO3 FAQ now says the old `extension-module` feature is deprecated and can break tests/workspaces unless newer packaging flows are used. That proves packaging and test/link handoff are not merely build trivia.
  https://www.maturin.rs/distribution.html
  https://pyo3.rs/v0.28.2/faq

## The ranked lane ladder
### 1) Full-CPython extension lane
This is the default “Rust extension module for CPython” lane.
Use it when the project wants the richest CPython-facing feature surface and accepts a tighter coupling to CPython-specific APIs and per-version build matrices.

What belongs here:
- module/package identity,
- interpreter family and version matrix,
- full-API-only features,
- native-base-class and `#[pyclass]` capabilities that are not available under limited API,
- packaging/test/link expectations for extension builds.

What it should **not** claim:
- multi-version wheel compatibility promised by `abi3`,
- free-threaded compatibility by default,
- or runtime-agnostic async interop.

### 2) `abi3` / limited-API extension lane
This lane exists for projects that explicitly trade some API reach for broader wheel compatibility across Python versions.
It should be treated as a **different product posture**, not as a build flag footnote.

What belongs here:
- minimum Python version carried by `abi3-pyXX`,
- restricted-API posture,
- wheel-compatibility benefits,
- any feature loss compared with full-API extension builds,
- runtime checks or compile-time guards needed when behavior differs across Python versions.

Design rule: **do not let “Python wheel” silently imply whether the wheel is full-API or limited-API.**

### 3) Free-threaded extension lane
This lane is now important enough to keep separate from both ordinary extension modules and `abi3`.
The free-threaded interpreter changes thread-attachment behavior and uses a distinct ABI.

What belongs here:
- free-threaded interpreter target identity,
- attach/detach assumptions for threads,
- unsupported-limited-API posture,
- version/build-matrix split from GIL-enabled extensions,
- any safety or soundness caveats that only appear in this lane.

Design rule: **do not let “supports Python 3.14t” silently inherit claims from ordinary CPython wheels.**

### 4) Async bridge lane (`asyncio` + Rust runtime)
This lane is real, but should be modeled as a bridge above one of the extension lanes, not as the definition of Python support.
PyO3’s current async story is explicitly `asyncio`-specific, and the external bridge crate carries runtime-specific integration posture.

What belongs here:
- whether async support comes from PyO3’s built-in experimental path or `pyo3-async-runtimes`,
- which Rust runtime family is in use,
- whether the Python awaitable contract is `asyncio`-only,
- stream / generator limitations,
- attach/detach and callback posture for cross-runtime calls.

Design rule: **do not let “async Python support” hide which event loop and which Rust runtime are actually joined.**

### 5) Packaging / link / test handoff lane
This is the lane that often gets buried under “just use maturin,” but it is strategically important.
The archive should preserve it as the place where wheel portability, symbol visibility, crate-layout quirks, and test/workspace behavior become product truths.

What belongs here:
- manylinux / musllinux / zig posture,
- wheel target matrix and portability claims,
- crate layout with mixed `bin`/`lib` targets when relevant,
- linker and symbol-visibility caveats,
- test/workspace build posture,
- packaging-tool versions and generated metadata.

This lane imports **Host Package**, **Native Edge**, and **Toolchain Productization** facts.
It should not be reduced to “packaging succeeded locally.”

### 6) Embedding / CPython-adoption adjacency lane
This is the most important **non-host-package** lane to keep visible.
PyO3 explicitly supports embedding Python in Rust, and the official Rust/CPython collaboration is exploring a still larger upstream adoption story inside CPython itself.
That is adjacent to the Python package lane, but not the same problem.

What belongs here:
- dynamic versus static embedding posture,
- interpreter initialization and distribution posture,
- PyOxidizer-like packaging if used,
- build/bootstrap cycle concerns,
- CPython-upstream language/toolchain/linker discussions.

Design rule: **do not let embedded-interpreter or CPython-upstream work silently masquerade as “Python wheel support.”**

## What Host Package Kit should import from this note
The next credible move is **not** a separate “Python mega-kit”.
It is to let **Host Package Kit** export Python-specific lane truth explicitly inside `hostpkg-manifest/v0` and `hostpkg-report/v0` when the lane is `python`.

At minimum, the Python branch of `hostpkg-manifest/v0` should preserve:
- `python_lane_family`: `cpython-extension-full-api` / `cpython-extension-abi3` / `cpython-extension-free-threaded` / `python-async-bridge` / `python-embedding-adjacent`;
- interpreter family/version matrix;
- module / wheel / sdist identities;
- build/distribution toolchain (`maturin`, setuptools-rust, manual, etc.);
- limited-API versus full-API posture;
- free-threaded posture;
- async bridge/runtime posture;
- link/test caveats;
- manylinux/musllinux/cross-compilation posture.

And `hostpkg-report/v0` should preserve Python-specific drift such as:
- full-API ↔ `abi3` lane changes,
- GIL-enabled ↔ free-threaded lane changes,
- `asyncio` bridge/runtime changes,
- wheel tag / portability changes,
- link/test/layout changes,
- embedding-adjacent or upstream-interop notes when those materially affect the shipped product.

## What a worthy contribution should look like in theory and practice
A worthy Rust contribution here would be a **thin Python lane-profiler and verifier** above PyO3/maturin rather than another hidden packaging abstraction.

In practice that means:
1. one reviewable export that says **which Python lane** a crate is actually shipping;
2. explicit statements about limited API, free-threaded ABI, and async-runtime posture;
3. packaging evidence that says what wheel or sdist matrix was actually built and why it is or is not portable;
4. link/test/layout evidence for mixed `bin`/`lib` or workspace-sensitive shapes;
5. bounded handoffs into release/support/adoption notes.

That contribution would help:
- PyO3 users who need to explain what they are actually shipping,
- downstream package maintainers and support teams,
- Rust adopters evaluating Python integration honestly,
- and future Rust/CPython work that should build on crisp lane distinctions instead of folklore.

## Non-goals
- replacing PyO3, maturin, or `pyo3-async-runtimes`;
- inventing a universal Python/Rust packaging framework;
- pretending `abi3`, free-threaded, and full-API extension modules are interchangeable;
- merging embedding/CPython-upstream work into ordinary wheel metadata;
- or turning one successful local import into a full support claim.
