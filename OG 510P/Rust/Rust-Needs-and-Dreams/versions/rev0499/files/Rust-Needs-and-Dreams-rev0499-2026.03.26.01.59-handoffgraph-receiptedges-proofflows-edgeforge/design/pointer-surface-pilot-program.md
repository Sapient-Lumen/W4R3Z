# Design: Pointer Surface pilot program (`cargo pointer pilot`, `pointer-pilot-pack/v0`)

## Why this needs a pilot program
The archive already has a credible **Pointer Surface Kit**, but it is still missing the ranked execution layer that would turn it into a real ecosystem contribution.

Current official Rust signals argue for a staged rollout:
- the 2026 flagships keep **Beyond the `&`** active with experimental field projections, progress on reborrow traits, and design alignment on in-place initialization;
- the 2025H2 pin-ergonomics goal says `Pin` is still central but notoriously hard to use well, and it is actively experimenting with pinned borrowing syntax, pattern support, and pinned `self` receivers;
- RFC 3519 says custom smart pointers remain second-class citizens and motivates arbitrary self types with cross-language references, ref-counted semantics, and Rust-for-Linux use cases that cannot honestly pretend to be ordinary `&T`;
- RFC 3621 exists because third-party smart pointers still need explicit support to work with trait objects;
- the reborrow-traits goal says user-space types still cannot achieve **true reborrowing** and explicitly points to `Pin<&mut T>` and Rust-for-Linux-style needs;
- and the Rust-for-Linux tooling work already stabilized `CoercePointee` derive for kernel smart-pointer use, which shows the seam is operational rather than hypothetical.

That combination points to a ranked pilot program: standardize the review boundary around pointer/reference semantics now, while the language and library story keeps evolving.

## References (signals)
- 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- 2025H2 pin ergonomics:
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- 2025H2 field projections:
  https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- 2025H2 reborrow traits:
  https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- RFC 3519 arbitrary self types v2:
  https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
- RFC 3621 derive smart pointer:
  https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- Rust-for-Linux tooling goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html

## Design principles
1. **Pointer semantics before pointer winners.** The pilot should standardize review boundaries before it blesses any one abstraction family.
2. **Identity and aliasing stay explicit.** Allocation identity, value equality, uniqueness witnesses, clone cost, and weak behavior must stay separate.
3. **Receiver and coercion posture are first-class.** Whether a surface supports method calls, trait objects, or coercions is part of the promise, not a footnote.
4. **Projection families stay distinct.** Shared, mutable, pinned, and move-projection semantics are related but not interchangeable.
5. **Foreign semantics are valid semantics.** Some pointer-like surfaces intentionally do not obey Rust-reference exclusivity; the pilot must let them say so honestly.
6. **Language progress is an input, not a blocker.** The artifacts should help now and remain useful if reborrow traits, field projections, pin ergonomics, or in-place initialization advance.
7. **Adapters before canon.** The winning early pilot is one that makes semantic losses and safety preconditions visible before integration work starts.

## Artifact additions for pilot work
### `pointer-pilot-brief/v0`
Why this lane is being piloted now.

Should record:
- pilot id and summary
- lane family (`shared-ownership`, `pinned-projection`, `foreign-reference`, `receiver-dyn`, `transition-migration`)
- why the lane matters
- intended consumers and success bar

### `pointer-surface/v0`
Must remain the first-class statement of subject identity, pointer family, and supported operations.

### `alias-uniqueness-profile/v0`
Must remain the explicit statement of share/clone/mutation/weak semantics.

### `projection-family-profile/v0`
Must remain the explicit statement of subview, reborrow, invalidation, and husk/drop posture.

### `receiver-coercion-profile/v0`
Must stay explicit about method receivers, dyn posture, unsizing/coercion support, and derive/nightly dependence.

### `pointer-transition-profile/v0`
Must record lossless/lossy mappings, allocations, runtime checks, and safety preconditions when moving between pointer surfaces.

### `pointer-vector-set/v0`
Must make identity, clone/share, uniqueness, projection, receiver, dyn, and transition claims executable.

### `pointer-check-report/v0`
Must record what was actually exercised, skipped, degraded, or only partially checked.

### `pointer-pilot-scorecard/v0`
Should ask:
- did the pilot make identity/share/uniqueness/projection semantics more legible than docs alone?
- did it avoid becoming a universal smart-pointer trait in disguise?
- did it keep foreign semantics, pinning, and receiver posture explicit where needed?
- did at least one real consumer use the exported artifacts?
- is widening to more adapters or domains justified?

## Ranked pilots

### 1) Shared-ownership lane
**Why first**
- Rust’s ergonomic-ref-counting work is now explicitly comparing syntax directions, but the archive still needs one semantic lane map underneath that debate.
- `Rc`/`Arc`-style APIs already expose real semantic differences around cheap clone, weak references, uniqueness checks, and clone-on-write, while `triomphe` and `arc-swap` show that weakless families and publication layers are distinct lanes rather than minor implementation details.
- This is the cleanest place to prove the kit can make aliasing semantics legible without depending on unstable language features.

**Core artifacts**
- `pointer-pilot-brief/v0`
- `pointer-surface/v0`
- `alias-uniqueness-profile/v0`
- `pointer-transition-profile/v0`
- `pointer-vector-set/v0`
- `pointer-check-report/v0`
- bundled as `pointer-pack/v0`

**Acceptance bar**
- A library can publish clear clone/share/weak/unique semantics for one shared-ownership pointer surface and at least one transition profile to or from another common form.
- The pilot explicitly distinguishes ordinary `Rc`, ordinary `Arc`, unique-to-shared construction, weakless borrowed-arc families, publication/storage wrappers, and language-watch ergonomics instead of flattening them into one “Arc-like” bucket.
- Treat [`design/pointer-shared-ownership-lane-map.md`](./pointer-shared-ownership-lane-map.md) as the shared-ownership scoring guide for this lane.

### 2) Pinned-projection lane
**Why second**
- Pin ergonomics, field projections, and in-place initialization all sharpen the need for explicit projection and invalidation truth.
- This lane proves the archive can describe pinning without pretending pinning is just “a normal mutable reference with caveats”.

**Core artifacts**
- `projection-family-profile/v0`
- pin-focused `pointer-vector-set/v0`
- `pointer-check-report/v0`
- optional links to initialization or lending artifacts where relevant

**Acceptance bar**
- A reviewer can see exactly which projection families are supported, what invalidates them, and what husk/drop or post-move cleanup posture remains.

### 3) Foreign-reference lane
**Why third**
- RFC 3519 is explicit that some smart pointers need method-call ergonomics while intentionally not providing Rust-reference guarantees.
- This is where the kit proves it can describe “reference-shaped but not Rust-reference-like” honestly.

**Core artifacts**
- `pointer-surface/v0`
- `alias-uniqueness-profile/v0`
- `receiver-coercion-profile/v0`
- `pointer-vector-set/v0` focused on receiver and safety boundaries

**Acceptance bar**
- At least one pilot makes foreign/runtime-defined aliasing semantics and method-call posture obvious without smuggling in false exclusivity claims.

### 4) Receiver / dyn lane
**Why fourth**
- Arbitrary self types and derive-smart-pointer work make receiver and trait-object posture an active seam, not a niche detail.
- This lane proves the archive can compare method-call and trait-object ergonomics without conflating them with ownership or pinning.

**Core artifacts**
- `receiver-coercion-profile/v0`
- `pointer-transition-profile/v0`
- vectors around method calls, coercions, unsizing, and dyn support

**Acceptance bar**
- A pack can say exactly which receiver forms, coercions, and dyn behaviors are supported, which depend on derives or nightlies, and which are intentionally unsupported.

### 5) Transition / migration lane
**Why fifth**
- Once the earlier pilots exist, the highest leverage is often in comparing or migrating pointer surfaces rather than inventing new ones.
- This lane is where Atlas, docs, interop, and future language migration guides gain real value.

**Core artifacts**
- `pointer-transition-profile/v0`
- migration notes inside `pointer-pack/v0`
- check reports exercising adapter losses and safety preconditions

**Acceptance bar**
- At least one consumer can review a transition between pointer surfaces without source-diving unsafe code or reconstructing semantics from folklore.

## What should wait
- Do **not** start by proposing a universal smart-pointer trait hierarchy.
- Do **not** start by flattening `Rc`, `Arc`, `Pin`, foreign references, intrusive pointers, and handle wrappers into one fake “reference” story.
- Do **not** start by using the pilot to settle provenance, aliasing, or the full memory model.
- Do **not** start by treating unstable language experiments as if they were already settled.

Those may inform future work. First prove that pointer semantics can be exported, compared, and reviewed honestly.

## Immediate archive decision
Treat [`design/pointer-surface-kit.md`](./pointer-surface-kit.md) and [`proposals/epic-pointer-surface-kit.md`](../proposals/epic-pointer-surface-kit.md) as the schema/epic anchors, and treat this file as the **execution order**. The next credible move is a ranked pilot program (shared-ownership → pinned projection → foreign reference → receiver/dyn → transition/migration), not another clever smart-pointer crate or a wait-forever posture.
