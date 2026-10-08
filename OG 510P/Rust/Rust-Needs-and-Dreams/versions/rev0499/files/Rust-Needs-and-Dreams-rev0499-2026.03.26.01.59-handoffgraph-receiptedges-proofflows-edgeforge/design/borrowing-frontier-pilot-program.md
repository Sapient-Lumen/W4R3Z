# Design: Borrowing Frontier Pilot Program

## Goal
Give the **Borrowing Frontier Stack** a ranked execution path so the archive stops discussing pointer semantics, lending semantics, trait evolution, and initialization posture as if they were equally mature or equally blocked.

This pilot program exists to prove that the stack can produce **reviewable surfaces with honest readiness verdicts**, not to crown one universal abstraction.

Related stack:
- [`design/borrowing-frontier-stack.md`](./borrowing-frontier-stack.md)
- [`proposals/epic-borrowing-frontier-stack.md`](../proposals/epic-borrowing-frontier-stack.md)

Related kits:
- [`design/trait-surface-kit.md`](./trait-surface-kit.md)
- [`design/pointer-surface-kit.md`](./pointer-surface-kit.md)
- [`design/lending-surface-kit.md`](./lending-surface-kit.md)
- [`design/initialization-surface-kit.md`](./initialization-surface-kit.md)

## Pilot order

### 1) Pointer / receiver pilot
**Why first**
This is the most legible place where the frontier is already real: `Pin`, projections, receiver posture, arbitrary-self-types work, and custom smart-pointer semantics all have concrete subjects.

**Candidate subjects**
- `Pin<&mut T>` / `Pin<Box<T>>`-style receiver and projection examples
- `Rc` / `Arc` identity and aliasing surfaces
- one arbitrary-self-types / `Receiver`-aligned example
- one `pin-project`-style projection subject
- one foreign or non-`&T` reference wrapper with explicit caveats

**Expected artifacts**
- `pointer-surface/v0`
- `receiver-coercion-profile/v0`
- `projection-family-profile/v0`
- one linked `trait-surface/v0` where receiver posture matters

**Success bar**
A reviewer can tell whether a method/trait story depends on ordinary references, pinned references, custom receivers, or foreign-semantic wrappers without reading unsafe internals.

### 2) Lending / reborrow pilot
**Why second**
This is where ideal Rust pressure is highest and premature convergence is most dangerous. The point is to prove honest comparability, not final language closure.

**Candidate subjects**
- one sync lending iterator example (`lending-iterator` / `lender`-style)
- one async bridge example (`Stream` / `AsyncIterator` / adapter lane)
- one borrowing callback or async-closure lane
- one explicit reborrow-sensitive case that still needs language help

**Expected artifacts**
- `lending-surface/v0`
- borrowing-mode and adapter profiles
- vector sets with explicit language/runtime blockers
- watch/wait verdicts where userland cannot yet be fully honest

**Success bar**
The pilot publishes at least one useful comparison and at least one explicit “blocked on language/compiler work” result without pretending either is failure.

### 3) Dyn / return / initialization pilot
**Why third**
Async traits, RPITIT-heavy traits, and in-place initialization meet here. This is where trait-family review and construction/destruction review have to compose.

**Candidate subjects**
- one native async-trait-family example
- one `async-trait` or `dynosaur`-style bridge
- one `pinned-init` / `pin-init` / `moveit`-style in-place-init or pinned-return experiment tied to dyn / `-> impl Trait` posture
- one explicit return-shape profile requiring RTN-style bound clarity

**Expected artifacts**
- `trait-surface/v0`
- `return-shape-profile/v0`
- `dyn-dispatch-profile/v0`
- linked `init-sequence-profile/v0` / `pin-destruction-profile/v0`

**Success bar**
A reviewer can tell what is native, what is boxed/adapter-provided, what depends on in-place return semantics, and what remains future-facing.

### 4) Foreign / kernel / interop pilot
**Why fourth**
This is where fake `&T` stories become actively misleading. It is the best place to prove that the stack can stay useful even when semantics differ sharply from ordinary Rust references.

**Candidate subjects**
- one Rust-for-Linux-inspired custom reference / pointer surface
- one C++ interop constructor or pinned-emplace surface
- one trait family whose receivers cannot honestly be plain references

**Expected artifacts**
- pointer transition profiles with explicit semantic gaps
- init profiles for out-ptr / pinned construction
- trait/pointer linkage showing custom receiver semantics
- explicit foreign-runtime assumptions

**Success bar**
The archive demonstrates a real interop/system-facing lane without laundering foreign semantics into faux-Rust-reference claims.

### 5) Migration / consumer pilot
**Why fifth**
Only after the lower-level surfaces are legible should the archive widen toward guidance, migration, and ecosystem recommendation consumers.

**Candidate consumers**
- Ecosystem Atlas / Interop Commons lane
- Migration Truth Stack lane
- Canonical Learning / DocProof lane
- support or debugging-facing import summaries where relevant

**Expected artifacts**
- linked pack imports rather than rewritten semantics
- readiness / promotion / watch / wait verdicts
- migration notes explaining what future language stabilization would obsolete or preserve

**Success bar**
Downstream consumers can reuse the stack’s artifacts without inventing hidden trait/pointer/lending/init summaries of their own.

## Pilot-wide rules
1. **Every pilot must preserve native vs adapter vs blocked posture.**
2. **Every pilot must publish at least one explicit unsupported or watch/wait result if the lane demands it.**
3. **Do not widen consumer imports until lower-level surfaces are legible.**
4. **Avoid abstraction contests.** Compare approaches; do not declare one final winner too early.
5. **Prefer subjects with real downstream pressure** (async traits, `Pin`, foreign refs, lending iterators, interop constructors) over toy examples.

## Graduation criteria
The stack is ready for broader promotion when it can show all of the following:
- at least one trait-family pilot with honest dyn/return-shape truth,
- at least one pointer-surface pilot with honest receiver/projection truth,
- at least one lending pilot with explicit blocker reporting,
- at least one initialization pilot with honest staged-assembly / teardown truth,
- and at least one downstream consumer lane that imports the artifacts instead of rephrasing them.

Until then, the right posture is **promising frontier with ranked evidence lanes**, not “Rust solved borrowing ergonomics”.
