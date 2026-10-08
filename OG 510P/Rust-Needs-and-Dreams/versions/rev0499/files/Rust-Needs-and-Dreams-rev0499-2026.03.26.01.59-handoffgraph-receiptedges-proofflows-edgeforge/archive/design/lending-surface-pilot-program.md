# Design: Lending Surface pilot program (`cargo lending pilot`, `lending-pilot-pack/v0`)

## Why this needs a pilot program
The archive already has a credible **Lending Surface Kit**, but the missing question is now practical: **how does this become a real ecosystem contribution without prematurely standardizing one trait, one runtime, or one magical “better stream” facade?**

Current official Rust signals argue for staged rollout:
- the 2025H1 async flagship said the next generation of async libraries has been blocked on stable solutions for async traits and streams, and explicitly tied progress on generators and pin ergonomics to that ecosystem future;
- the 2025H2 Polonius goal says future patterns such as lending iterators need the improved borrow checker, and the alpha analysis already accepts the filtering lending-iterator case;
- the 2025H2 reborrow-traits goal says userland still cannot achieve **true reborrowing** and aims to let users of crates like `reborrow` move to a core solution;
- pin ergonomics remains an active goal because async and generators depend on pinning but pinning is still hard to use well;
- and the 2026 flagships keep both **progress on reborrow traits** and **unblocking dormant traits / lending iterators** on the live roadmap.

That combination points to a ranked pilot program: standardize the review boundary around borrowing sequence semantics now, while letting the language/runtime story keep evolving.

## References (signals)
- 2025H1 async flagship:
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
  https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- 2025H2 Polonius:
  https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- 2025H2 reborrow traits:
  https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- 2025H2 pin ergonomics:
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- RFC 2996 async iterator:
  https://rust-lang.github.io/rfcs/2996-async-iterator.html
- RFC 3654 return type notation:
  https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- RFC 3668 async closures:
  https://rust-lang.github.io/rfcs/3668-async-closures.html

## Design principles
1. **Borrowing mode first, trait choice second.** The pilot should standardize semantics before it blesses an API shape.
2. **Adapters before winners.** We should learn where conversion is lossless, lossy, allocation-heavy, pin-heavy, or runtime-specific before talking about canon.
3. **Pinning and runtime assumptions must stay explicit.** They are part of the surface, not background noise.
4. **Keep sync and async linked but distinct.** The point is comparable seams, not one fake universal sequence trait.
5. **Language progress is an input, not a blocker.** The artifacts should help now and remain useful if Polonius, reborrow traits, RTN, async generators, or pin ergonomics advance.
6. **Pilot with real consumer questions.** The winning lane is one that answers “can I adopt this API?” faster than folklore, examples, and source diving.

## Artifact additions for pilot work
### `lending-pilot-brief/v0`
Why this lane is being piloted now.

Should record:
- pilot id and summary
- lane family (`sync-lending`, `async-bridge`, `borrow-callback`, `pin-runtime`, `domain-sequence`)
- why the lane matters
- intended consumers and success bar

### `borrow-mode-profile/v0`
Must stay the first-class statement of giving / streaming / lending / async-poll / async-call / generator-backed posture.

### `sequence-adapter-profile/v0`
Must record what is preserved, erased, boxed, cloned, buffered, pinned, runtime-bound, or unsupported when moving across surfaces.

### `yield-vector-set/v0`
Must make exhaustion, invalidation, cancellation, and adapter edge cases executable.

### `executor-runtime-profile/v0`
Optional, but required when runtime scheduling, local-vs-`Send`, or wake behavior materially affects semantics.

### `sequence-check-report/v0`
Must record what was actually exercised, skipped, degraded, or only partially checked.

### `lending-pilot-scorecard/v0`
Should ask:
- did the pilot make borrowing/invalidation semantics more legible than docs/examples alone?
- did it avoid becoming a new universal facade?
- did it keep pin/runtime assumptions explicit where needed?
- did at least one real consumer use the exported artifacts?
- is widening to more adapters or domains justified?

## Ranked pilots

### 1) Sync lending-iterator lane
**Why first**
- It is the most mature seam today: `streaming-iterator`, `lending-iterator`, and `lender` already prove that stable Rust needs borrow-friendly sequence APIs.
- It exercises the core truths without forcing async runtime choices too early.

**Core artifacts**
- `lending-surface/v0`
- `borrow-mode-profile/v0`
- `sequence-adapter-profile/v0`
- `yield-vector-set/v0`
- `sequence-check-report/v0`
- bundled as `lending-pack/v0`

**Acceptance bar**
- A library can publish clear invalidation, fusedness, mutable-borrow, and adapter-cost truth for one sync lending surface and at least one bridge to ordinary `Iterator`.

### 2) Async sequence bridge lane
**Why second**
- RFC 2996 makes the `AsyncIterator` story more explicit, but the ecosystem still lives across `Stream`, runtime-specific helpers, and unstable/std-facing terminology.
- This lane proves the archive can compare surfaces without pretending the language story is finished.

**Core artifacts**
- async-flavored `lending-surface/v0`
- adapter profiles between `Stream`-style and `AsyncIterator`-style surfaces
- `yield-vector-set/v0` with wake/cancel cases
- optional `executor-runtime-profile/v0`

**Acceptance bar**
- A reviewer can see where an async sequence surface is fundamentally compatible, where it becomes lossy, and where the mismatch is really about runtime/pinning/object-safety limits.

### 3) Borrowing callback / async-closure lane
**Why third**
- RTN and async closures are making it more possible to talk about futures that borrow from their inputs or captures, but the archive still needs a way to describe those surfaces without collapsing them into “just another callback.”
- This lane is the bridge between lending iteration and broader lending traits.

**Core artifacts**
- `borrow-mode-profile/v0` capturing self-borrowing / capture-borrowing posture
- `sequence-adapter-profile/v0` for callback-to-sequence or sequence-to-callback shims where relevant
- explicit RTN / `Send` / `'static` constraints in surface metadata

**Acceptance bar**
- At least one pilot makes it obvious which returned futures borrow, what extra bounds are required for spawning or buffering, and which adapters erase those properties.

### 4) Pin/runtime-sensitive adapter lane
**Why fourth**
- Pin ergonomics is still evolving, and some async sequence APIs fundamentally depend on pin posture, local executors, or runtime conventions.
- This lane ensures those assumptions become reviewable instead of becoming hidden folklore.

**Core artifacts**
- `executor-runtime-profile/v0`
- pin-sensitive adapter profiles
- yield vectors for cancellation / drop / wake behavior
- explicit unsupported markers

**Acceptance bar**
- A pack can say “works only under these runtime/pin assumptions” honestly, without pretending portability or dyn safety that it does not have.

### 5) Domain sequence lane
**Why fifth**
- Once the earlier pilots work, the kit should prove value in domains where borrow reuse materially matters: framed I/O, parser cursors, chunked readers, row windows, or zero-copy decoding.
- This is the lane that proves the work matters beyond iterator-enthusiast circles.

**Core artifacts**
- domain-shaped `lending-surface/v0`
- adapter profiles into higher-level protocol/dataset/media/service kits where relevant
- real vectors with invalidation and backpressure edge cases

**Acceptance bar**
- One domain guide or Atlas-style entry can recommend a sequence stack with an attached `lending-pack/v0`, not just code snippets and caveats.

## What should wait
- Do **not** start by choosing a universal replacement for `Stream`, `Iterator`, or future async sequence syntax.
- Do **not** start by flattening pinning, runtime dependence, and object-safety limitations into “minor caveats”.
- Do **not** start by forcing cross-runtime promises that current libraries cannot honestly make.
- Do **not** start by turning the pilot into a combinator empire or a new facade crate.

Those may become consumers or follow-on work. First prove that borrow-friendly sequence semantics can be exported, compared, and reviewed honestly.

## Immediate archive decision
Treat [`design/lending-surface-kit.md`](./lending-surface-kit.md) and [`proposals/epic-lending-surface-kit.md`](../proposals/epic-lending-surface-kit.md) as the schema/epic anchors, and treat this file as the **execution order**. The next credible move is a ranked pilot program (sync lending → async bridge → borrowing callback/async-closure lane → pin/runtime lane → domain lane), not another universal sequence facade or a wait-forever posture.
