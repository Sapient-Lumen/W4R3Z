# Frontier salience snapshot — 2026-03-21-134

This pass did **not** add another debugger launcher, crash backend, or IDE integration crate.
It sharpened **P-0486 Debuggability Support Contract Kit** into a more backend-aware support contract.

## Why this frontier moved up

The official Rust debugging story is now precise enough that the sharper missing layer is increasingly obvious:

- the 2026 Rust debugging survey says ideal Rust debugging should support several versions of different debuggers across multiple operating systems, quality debugger visualizers, first-class async debugging, and Rust expression evaluation;
- the 2025 State of Rust survey still says debugging remains one of the top non-trivial productivity limits;
- the Rust Reference makes stable visualizer embedding explicit, but only for `natvis_file` and `gdb_script_file` inputs;
- Cargo and `rustc` now document debug/strip/split-debuginfo and path-sanitization posture clearly enough to classify artifact support;
- and the March 2026 Build Dir Layout v2 call-for-testing reinforces that artifact discovery and relocation are their own truth, separate from whether a given debugger/backend/capability lane was ever actually checked.

That combination means the missing crate is not merely “tell me where the `pdb` or `dSYM` went.”
The missing crate is now a **backend-aware debuggability contract** that can publish **debugger-family coverage**, **capability ceilings**, and **portable-claim ceilings** above build artifacts.

## Main conclusion

Promote **P-0486** upward again, but keep it narrow.
The next worthy move is not more launcher UX and not another debugger abstraction.

It should stay focused on:

1. freezing artifact/symbol/visualizer facts into a conservative support surface,
2. making **debugger-family / OS / version coverage** explicit,
3. making **async-debugging** and **expression-evaluation** claims visible as their own capability classes,
4. and downgrading broad portability claims when only one backend family or one capability slice was actually checked.

## Ranked near-term frontier from this pass

1. **P-0486 Debuggability Support Contract Kit** — strengthened because debugging remains a live pain point while the sharper missing layer is now clearly backend-coverage and capability-ceiling truth above existing artifact substrate.
2. **P-0493 Source Path Hygiene & Debug Source Kit** — still unusually strong because source lookup and path remapping remain adjacent but distinct support seams.
3. **P-0491 Debugger Visualizer Compatibility Kit** — still strong because visualizer assets still need backend/version compatibility evidence rather than mere presence.
4. **P-0525 Crate Diagnosis Surface Kit** — still strong because runtime symptom triage often begins exactly where debugger expectations fail.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still strong because async/background-work complexity affects what “debugging async code” even means for downstream users.

## Keep these boundaries sharp

- **P-0486** is the broad receiver-facing debuggability support contract.
- **P-0491** is visualizer/backend compatibility.
- **P-0493** is source-path hygiene and source-lookup diagnosis.
- **P-0525** is runtime symptom / first-diagnosis support.

Do not let “debugger support” flatten those lanes into one fake crate.
