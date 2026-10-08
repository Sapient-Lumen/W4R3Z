# Design note: Pointer shared-ownership lane map (ergonomic ref-counting, weakless arcs, borrowed arcs, and read-mostly publication)

## Goal
Sharpen the archive’s **shared-ownership lane** beneath **Pointer Surface Kit** so future revisions stop flattening all ref-counted or cheaply-cloneable Rust state into one fake “Arc ergonomics” verdict.

The ecosystem now has several real but non-equivalent lanes:
- ordinary `Rc` shared ownership,
- ordinary `Arc` shared ownership,
- uniquely-owned-to-shared construction lanes,
- weakless / borrowed / layout-specialized arc families,
- read-mostly publication layers built on top of ref-counted pointers,
- and an adjacent-but-distinct **language ergonomics watch lane** for ergonomic ref-counting syntax.

A worthy contribution here is **not** another `Arc` clone or one more closure-capture helper.
It is a thin review layer that keeps those lanes explicit and comparable.

## Why this note is needed now
- Rust’s 2025H2 ergonomic-ref-counting goal says explicit cloning friction affects not only `Arc<T>`/`Rc<T>` directly, but also many ref-counted handles hidden inside APIs, especially in async and GUI code. It also says the project is now comparing an explicit `.use` design with a more automatic alternative plus lints.
  https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Rust’s 2026 flagship themes keep **prototype ergonomic ref-counting** active under **Just Add Async**, which is strong evidence that shared ownership remains an active frontier rather than solved background syntax.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Std `Arc`/`Rc` already expose materially different user-visible semantics around pointer identity, clone-on-write, weak dissociation, and uniqueness checks. Those are not tiny implementation details.
  https://doc.rust-lang.org/std/sync/struct.Arc.html
  https://doc.rust-lang.org/std/rc/struct.Rc.html
- Std `UniqueArc` now makes the uniquely-owned-to-shared construction lane explicit: weak pointers may exist during unique ownership, but they cannot upgrade until conversion to an ordinary `Arc`.
  https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- `triomphe` demonstrates a different family rather than a drop-in synonym: no weak refs, a borrowed-arc form (`ArcBorrow`), an offset form for FFI (`OffsetArc`), and thin/DST-specialized variants.
  https://docs.rs/triomphe/latest/triomphe/
- `arc-swap` is another important split signal. It is not “a better Arc”; it is an atomic storage/publication layer for ref-counted pointers, optimized for read-mostly scenarios, with lock-free readers, expensive writes, and explicit guard limitations.
  https://docs.rs/arc-swap
  https://docs.rs/arc-swap/latest/arc_swap/docs/performance/
  https://docs.rs/arc-swap/latest/arc_swap/docs/limitations/

## The ranked lane ladder
### 1) `Rc` lane — single-thread shared ownership
This is the baseline lane for shared ownership without cross-thread guarantees.
It matters because many ergonomics discussions start here, but it already has sharp semantics:
- cheap aliasing clone,
- `Weak` support,
- `ptr_eq` allocation identity,
- `get_mut` uniqueness checks,
- `make_mut` clone-on-write plus weak dissociation behavior.

What it should **not** be mistaken for:
- `Arc`’s cross-thread cost model,
- publication or lock-free update structures,
- or uniquely-owned staged construction.

### 2) `Arc` lane — cross-thread shared ownership
This is the default async/service/task-context lane and the primary subject of current ergonomic-ref-counting pressure.
It should preserve:
- atomic clone/share semantics,
- `Weak` and cycle posture,
- `ptr_eq` identity,
- `get_mut` / `is_unique` / `unwrap_or_clone` style uniqueness and extraction posture,
- and the fact that clone cost and mutation strategy still matter operationally.

What it should **not** be mistaken for:
- single-thread `Rc`,
- weakless arc families,
- or publication/storage wrappers that sit above `Arc`.

### 3) Unique-to-shared construction lane
This lane is adjacent to Initialization Surface rather than identical to ordinary shared ownership.
Use it when the important truth is:
- the value is currently uniquely owned,
- mutation or staged setup is still allowed,
- weak pointers may or may not already exist,
- and later conversion to an ordinary shared pointer changes what observers can do.

Std `UniqueArc` and `triomphe::UniqueArc` belong here.
This lane should remain visible because construction-time truths should not be back-written as steady-state shared-ownership truths.

### 4) Weakless / borrowed / layout-specialized arc lane
This is where crates like `triomphe` live.
The important distinction is not “faster Arc” in the abstract, but **which semantics were traded away or added**:
- no weak count,
- borrowed-arc forms that are layout-compatible with `&T`,
- offset/thin/DST-specialized pointer forms,
- and stronger FFI/layout adjacency.

What it should **not** be mistaken for:
- ordinary `Arc` with all std semantics preserved,
- or mere cosmetic ergonomics around closure capture.

### 5) Publication / read-mostly lane
This is where `arc-swap` belongs.
The archive should model it as a **consumer/storage layer above a ref-counted pointer family**, not as one more pointer type with the same semantics.

What belongs here:
- snapshot/publication posture,
- read-heavy / infrequent-write design intent,
- reader/writer cost asymmetry,
- guard/borrow lifetime limitations,
- and any async-yield or caching caveats.

Design rule: **do not let “uses Arc” hide whether the real abstraction under review is actually a publication/store layer.**

### 6) Ergonomic-ref-counting watch lane
This is the language-facing lane.
It is important, but it should stay explicitly separate from the semantic lane map.
The current Rust goal is comparing explicit `.use` syntax with a more automatic alternative plus lints.
That work may change how cheap-clone capture looks, but it does **not** erase the differences between:
- `Rc` and `Arc`,
- weakful and weakless arcs,
- unique-to-shared construction,
- or publication layers like `arc-swap`.

Design rule: **syntax ergonomics should import shared-ownership semantics, not redefine them.**

## What Pointer Surface Kit should import from this note
The next credible move is **not** a separate “ref-counting mega-kit”.
It is to let **Pointer Surface Kit** publish shared-ownership lane truth explicitly inside:
- `pointer-surface/v0`
- `alias-uniqueness-profile/v0`
- `pointer-transition-profile/v0`
- selected `pointer-vector-set/v0`
- and `pointer-check-report/v0`

At minimum, shared-ownership exports should preserve:
- `shared_ownership_lane`: `rc` / `arc` / `unique_to_shared` / `weakless_arc_family` / `publication_layer` / `watch_language_ergonomics`
- thread posture (`single-thread`, `cross-thread`, `storage-layer-over-pointer`)
- clone class (`cheap_alias`, `clone_on_write_gate`, `publication_snapshot`, `other`)
- weak posture (`supported`, `unsupported`, `temporarily-disabled-until-conversion`, `not-applicable`)
- uniqueness witness posture (`get_mut`, `is_unique`, temporary unique-owner phase, runtime guard, none)
- identity posture (`allocation`, `metadata-insensitive-allocation`, `mixed`)
- borrowed/layout-specialized forms when relevant
- publication or guard limitations when the lane is above the pointer itself

And `pointer-transition-profile/v0` should preserve shared-ownership drift such as:
- `Rc` ↔ `Arc` lane changes,
- ordinary `Arc` ↔ weakless arc-family changes,
- unique-owner ↔ ordinary shared-owner transitions,
- ordinary shared-owner ↔ publication-layer wrapper changes,
- and language-watch changes that alter capture ergonomics without changing semantic lane identity.

## What a worthy contribution should look like in theory and practice
A worthy Rust contribution here would be a **thin shared-ownership lane profiler and verifier** above std/docs/crate APIs rather than another “easier Arc” abstraction.

In practice that means:
1. one reviewable export that says **which shared-ownership lane** a crate or API is actually using;
2. explicit statements about weak support, uniqueness witnesses, clone-on-write posture, and pointer identity;
3. transition profiles that say what is lost or gained when moving between lanes;
4. publication-layer evidence that says when the real abstraction is snapshot/update storage rather than the pointer itself;
5. bounded handoffs into Async Lifecycle, Pointer Surface, Initialization Surface, and Native Edge notes.

That contribution would help:
- async/service authors who need to explain what shared state patterns they are really shipping,
- GUI/reactive libraries deciding whether they need syntax sugar or a different pointer lane,
- FFI/native adopters evaluating borrowed-arc and layout-specialized forms honestly,
- and future language ergonomics work that should build on crisp semantic lane distinctions instead of folklore.

## Non-goals
- replacing `Rc`, `Arc`, `triomphe`, or `arc-swap`;
- inventing a universal shared-ownership trait;
- pretending ergonomic-ref-counting syntax solves semantic lane differences;
- merging publication/storage layers into ordinary pointer identity;
- or turning one success story in async or GUI land into a fake universal verdict about ref-counting in Rust.
