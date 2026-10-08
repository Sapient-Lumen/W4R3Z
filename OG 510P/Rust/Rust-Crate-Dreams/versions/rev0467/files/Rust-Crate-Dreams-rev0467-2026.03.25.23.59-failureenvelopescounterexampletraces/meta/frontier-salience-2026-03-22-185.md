# Frontier salience — 2026-03-22 (185)

This pass did **not** open another debugger launcher, symbol server, or IDE integration lane.
It deepened **P-0486 Debuggability Support Contract Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0011 Crate Health Contract Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0036 MSRV Workspace Lab**
8. **P-0532 Async Runtime Assurance Profile Kit**
9. **P-0469 Cargo Rebuild Explanation Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0486 was the right lane to deepen now

Fresh official Rust sources keep making this lane more specific:

- the 2026 debugging survey says good Rust debugging should span multiple debuggers and operating systems, quality visualizers, async debugging, and Rust expression evaluation, while also noting that support can regress as debuggers and Rust internals change;
- the 2026 challenges write-up says debugging friction is compounded by compile-time pressure and by domains like embedded where optimized builds are often unavoidable;
- Cargo’s profile docs keep the key support knobs explicit (`debug`, `split-debuginfo`, `strip`) and warn that Cargo and `rustc` can still differ on `split-debuginfo` defaults;
- `rustc`’s codegen docs keep platform differences concrete (`pdb`, `dSYM`, `dwo`, `dwp`) and say `strip = debuginfo` can leave backtraces mostly intact while making interactive debugging ineffectual;
- the Rust Reference keeps `#[debugger_visualizer]` a stable, real surface;
- Cargo’s build-cache docs and the March 2026 Build Dir Layout v2 call-for-testing keep reinforcing that final-artifact routes and internal build-dir routes are related but not the same thing.

That combination sharpens the missing value.
The crate is not most missing as a debugger frontend.
It is missing as a **portable support contract** for:

1. **broad support posture**,
2. **exact backend observations**,
3. **source-material lookup and handoff truth**,
4. **portable review bundles**, and
5. **manual-review honesty when only artifact inference exists**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. one **backend-observation receipt** saying what debugger family / OS / version / capability lane was actually checked;
2. one **source-material manifest** saying what source bundle, remapped-path context, or sysroot source material is needed for lookup;
3. one **portable debug-support bundle** that keeps sidecars, backend evidence, source material, and share posture explicit;
4. one **support-posture verdict** that does not over-read those narrower artifacts; and
5. one **manual-review zone** when artifact richness exceeds actual checked capability evidence.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0486**, **P-0491**, **P-0493**, **P-0101**, and **P-0525**.

Especially resist:

- another debugger launcher or IDE plugin,
- another symbol-only archive tool that cannot describe support posture,
- another source-packaging helper that cannot keep share posture and lookup role explicit,
- or another dashboard that cannot say which backend/version/capability lane was actually checked.
