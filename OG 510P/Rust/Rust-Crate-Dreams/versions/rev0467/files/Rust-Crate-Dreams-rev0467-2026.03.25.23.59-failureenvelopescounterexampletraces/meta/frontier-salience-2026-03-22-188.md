# Frontier salience — 2026-03-22 (188)

This pass did **not** open another cache-policy helper, scheduler, or Cargo wrapper.
It deepened **P-0490 Cargo Lock Contention Witness Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0490 Cargo Lock Contention Witness Kit**
7. **P-0469 Cargo Rebuild Explanation Kit**
8. **P-0486 Debuggability Support Contract Kit**
9. **P-0036 MSRV Workspace Lab**
10. **P-0532 Async Runtime Assurance Profile Kit**

## Why P-0490 was the right lane to deepen now

Fresh official Cargo and rust-analyzer sources make the missing value here more specific than “better lock diagnostics” or “another build-blocking workaround list”:

- rust-analyzer’s FAQ still explicitly says rust-analyzer and manual Cargo commands can block one another, and recommends a separate target directory only as a trade against duplicated artifacts;
- rust-analyzer’s configuration docs still make the base command lane, override commands, invocation strategy, wrappers, and target-dir separation explicit enough to model conservatively;
- Cargo’s build-cache and config docs now keep `target-dir` and `build-dir` separate with first-class authority routes;
- Cargo’s unstable docs still say `build-dir-new-layout` exists to unblock caching and locking improvements;
- the March 2026 build-dir-layout-v2 testing call says teams should test any process touching `build-dir` / `target-dir`, and that separate `build-dir` alone may already expose breakage;
- the Cargo 1.94 development-cycle update says target-dir locking still has easy-to-overlook but significant residual contention cases, especially around proc-macros, build scripts, and some non-workspace-member cases;
- and Cargo’s current internal cache-lock docs now make package-cache lock semantics unusually concrete: `DownloadExclusive`, `Shared`, and `MutateExclusive`, with the important rule that `DownloadExclusive` does not interfere with `Shared`.

That combination sharpens the missing crate.
It is not most missing as another cache cleaner or generic contention doctor.
It is missing as a **portable contention witness contract** for:

1. **package-cache lock-mode truth**,
2. **residual contention after mitigation**,
3. **before/after outcome diffing**,
4. **portable witness bundles**, and
5. **manual-review honesty where upstream lock behavior is still evolving**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. one **package-cache lock-mode receipt** saying whether the relevant package-cache activity should interfere with the observed actor at all;
2. one **residual-contention report** saying which contention surfaces remain after target-dir / build-dir / workflow changes;
3. one **mitigation-outcome diff** saying what really changed before vs after, instead of only that a workaround was attempted;
4. one **portable support bundle** keeping root authority, actor lane, wait window, lock mode, residual surfaces, mitigation cost, and outcome diff together; and
5. one **manual-review zone** whenever older Cargo versions, build-dir-layout churn, or ambiguous process evidence outruns what the bundle can honestly prove.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0490**, **P-0436**, **P-0480**, **P-0469**, and **P-0494**.

Especially resist:

- another cache-policy crate that cannot witness a live blocked workflow,
- another scheduler/arbiter that cannot export a reviewable incident bundle,
- another Cargo wrapper that collapses lock-mode truth into folklore,
- or another “use a different target dir” helper that cannot explain residual contention and before/after outcome honestly.
