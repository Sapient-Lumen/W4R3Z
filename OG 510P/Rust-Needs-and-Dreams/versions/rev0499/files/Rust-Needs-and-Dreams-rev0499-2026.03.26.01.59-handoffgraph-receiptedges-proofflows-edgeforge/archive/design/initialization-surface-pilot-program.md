# Design: Initialization Surface pilot program (std baseline, cyclic bootstrap, unique-to-shared publication, pin-init lanes, self-referential lanes, and foreign-emplace lanes)

## Goal
Turn **Initialization Surface Kit** into a ranked pilot program that proves Rust teams can publish honest construction and teardown semantics without waiting for the language to settle every in-place initialization question first.

This pilot should make the archive prefer **lane-aware reports, phase maps, exposure timing, rollback vectors, and teardown posture** over another constructor macro, ad-hoc unsafe comment, or one fake “supports pinned initialization” summary.

## Why this now deserves a pilot
The strategic timing is unusually strong:
- Rust’s 2026 flagship themes put **immobile types and guaranteed destructors** plus **design alignment on in-place initialization** on the active roadmap.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The in-place-initialization goal says the project explicitly wants to compare competing approaches and experiment with real users such as the Linux kernel and Crubit before choosing a direction.
  https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- Std already exposes distinct lanes via `MaybeUninit`, `Box::pin`, `Arc::new_cyclic`, and `UniqueArc`.
  https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
  https://doc.rust-lang.org/std/boxed/struct.Box.html
  https://doc.rust-lang.org/std/sync/struct.Arc.html
  https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- Userland crate ecosystems already expose pinned in-place, projection/destruction, self-referential, and foreign-emplace lanes rather than one converged constructor story.
  https://docs.rs/pin-init
  https://docs.rs/pinned-init
  https://docs.rs/pin-project/latest/pin_project/attr.pin_project.html
  https://docs.rs/self_cell
  https://docs.rs/yoke/latest/yoke/struct.Yoke.html
  https://docs.rs/moveit

See the normative lane split in [`design/initialization-surface-lane-map.md`](./initialization-surface-lane-map.md).

## Pilot artifacts
The pilot should exercise a small but durable artifact family:
- `init-surface/v0`
- `placement-init-profile/v0`
- `init-sequence-profile/v0`
- `pin-destruction-profile/v0`
- `init-adapter-profile/v0`
- `init-vector-set/v0`
- `init-check-report/v0`
- `init-pack/v0`

Every pilot stage should prefer a few small example vectors and explicit caveats over giant generated blobs.

## Ranked rollout

### Stage 1 — std baseline: out-pointer and construct-then-pin truth
Subjects:
- `MaybeUninit` out-pointer patterns
- `Box::pin`
- optionally `Arc::new_uninit` / `Rc::new_uninit` notes where they clarify storage-vs-publication posture

Why first:
- this is the smallest lane split with the largest explanatory value
- it distinguishes caller-allocated initialization from ordinary constructors
- it distinguishes construct-then-pin from pinned-in-place

Outputs:
- one baseline `init-surface/v0`
- one `placement-init-profile/v0` proving storage origin and address-stability timing
- one small vector set covering normal success and incorrect assume-init / move assumptions as documented caveat lanes

### Stage 2 — cyclic bootstrap truth
Subjects:
- `Arc::new_cyclic`
- `Rc::new_cyclic`

Why second:
- this makes the allocated-but-not-fully-published phase explicit
- it proves the archive can talk about weak/self handles before full publication
- it creates a clean comparison against ordinary constructors and against later unique-to-shared publication

Outputs:
- one `init-sequence-profile/v0` with pre-publication weak-handle timing
- one vector proving that `upgrade` fails before construction is complete
- one adapter profile comparing ordinary constructors to cyclic bootstrap

### Stage 3 — unique-to-shared publication truth
Subjects:
- `UniqueArc`
- one local example showing fallible or async-shaped setup before publication

Why third:
- this is the cleanest practical lane for “unique during construction, shared after publication”
- it separates cyclic bootstrap from publication staging
- it gives the archive a better theory/practice story for fallible or async constructors than `Arc::new_cyclic` alone

Outputs:
- one publication-timing profile
- one adapter profile comparing `Arc::new_cyclic` to `UniqueArc`
- one vector covering failed setup before publication

### Stage 4 — pinned in-place / fallible lane truth
Subjects:
- `pin-init`
- `pinned-init`
- one `pin-project`-adjacent teardown/projection example where relevant

Why fourth:
- this is where “pinned from the start” becomes meaningfully different from “construct then pin”
- it forces rollback, partial-init, and teardown posture into the artifact family
- it gives the archive a real answer for kernel-ish or `!Unpin`-sensitive setup

Outputs:
- one lane profile for fixed-destination pinned assembly
- one vector for fallible setup and cleanup
- one teardown profile covering pinned drop / projection / replace posture when exposed

### Stage 5 — self-referential / borrow-carrying truth
Subjects:
- `self_cell`
- `yoke`

Why fifth:
- this proves the archive can model internal borrowing semantics, not just placement and pinning
- it keeps self-borrowing distinct from cyclic weak-self patterns
- it exposes teardown ordering and dependent exposure timing as first-class review concerns

Outputs:
- one owner/cart vs dependent profile
- one vector covering dependent validity timing
- one adapter report comparing self-referential and cyclic lanes without flattening them

### Stage 6 — foreign-emplace / destructor-coupled truth
Subjects:
- `moveit`
- one explicit interop or kernel-oriented note imported from the roadmap context

Why sixth:
- this is where foreign constructor and destructor semantics become central rather than incidental
- it gives the archive a disciplined place for C++ / kernel emplacement without pretending the language has fully settled the problem
- it prepares a migration surface for future in-place-init and guaranteed-destructor language work

Outputs:
- one foreign-emplace profile
- one vector covering non-relocatable or destructor-coupled setup expectations
- one migration note that is explicit about watch/wait posture

## Practical design rules
- Do not skip from Stage 1 straight to one grand abstraction.
- Every stage should attach at least one **semantic mismatch** or **unsupported / partial** outcome so the pack proves honesty, not just success.
- Every stage should preserve exact lane meaning from [`design/initialization-surface-lane-map.md`](./initialization-surface-lane-map.md).
- Teardown posture should never be buried inside constructor examples.
- If a language-native feature is still moving, say `watch` / `migration-lane` instead of implying convergence.

## What success looks like
A good pilot outcome would let a reviewer answer:
- where storage came from,
- when the object’s address became stable,
- when handles or internal borrows became valid,
- how failure / unwind / cancellation / leak were treated,
- whether publication into shared ownership had its own lane,
- and what destructor or teardown guarantees actually followed.

If the pilot cannot answer those questions with artifacts, the archive is still leaning on folklore.

## Boundaries
- **Pointer Surface Kit** still owns identity, aliasing, receiver, and projection truth after construction.
- **Validity Surface Kit** still owns invariants and invalid-value posture.
- **Borrowing Frontier Stack** imports initialization truth; it does not erase it.
- **Interop Commons Kit** may later host shared vocabulary, but this pilot remains the concrete proving ground.

## Near-term recommendation
Treat this pilot as the next concrete move for the broader **Borrowing Frontier Stack**: pointer/receiver truth first, lending/reborrow truth second, initialization lane truth third, and foreign/kernel migration notes after the initialization lanes are proven rather than before.
