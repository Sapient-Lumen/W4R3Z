# Workspace boundary and config discovery lanes — 2026-03-16

This note exists so future passes do **not** collapse several different Cargo discovery problems into one vague “workspace issue”.

## Keep these lanes separate

1. **Workspace membership lane**
   - is the package a root package, virtual-workspace member, auto-member, excluded package, or unexpected member?
2. **Parent-manifest discovery lane**
   - did a parent `Cargo.toml` become relevant when the user did not expect it?
3. **Parent-config probing lane**
   - did a parent `.cargo/config.toml` materially affect the invocation?
4. **Current-working-directory lane**
   - did invoking Cargo from one directory versus another change which config files mattered?
5. **`--manifest-path` split lane**
   - was the selected package in one directory while config probing still originated from another?
6. **Project-vs-environment config lane**
   - is the problem really that a project-specific setting still lives in config/env rather than in the manifest?
7. **Opt-out / future-upstream lane**
   - is the best answer a future feature such as `package.workspace = false` or broader project-config-in-manifest support?

## Working rule

Do not let the archive imply that every workspace surprise should be solved by “add `[workspace]`” or “move the file”.
A worthy crate in this lane should report:

- invocation context,
- discovered parents,
- config influence,
- membership classification,
- and whether the fix is immediate, repo-local, or upstream-dependent.

## Current neighboring proposals

- **P-0506 Cargo Workspace Boundary Doctor Kit** should own the boundary receipt / diagnosis / advice bundle.
- **P-0109 Cargo Workspace Policy Doctor Kit** is about policy stacks, not discovery poisoning.
- **P-0505 Cargo Host/Target Scope Contract Kit** is about build config scope, not workspace boundary discovery.

## Anti-collapse reminder

Future revisions must not flatten:

- parent-manifest poisoning,
- local-config bleed,
- auto-membership surprises,
- `--manifest-path` invocation splits,
- and missing project-specific manifest config

into one fake “Cargo workspace bug”.
