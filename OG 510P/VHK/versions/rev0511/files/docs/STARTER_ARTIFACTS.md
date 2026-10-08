# Starter artifacts from `vhk init`

`vhk init` can now emit two onboarding artifacts alongside the project
skeleton:

- `docs/VHK_STARTER_GUIDE.md`
- `docs/VHK_STARTER_PLAN.json`

These are generated from the same planning model used by `vhk plan-project`.
The goal is to stop treating Linux-native setup, deployment surfaces, and
reference patterns as something the user discovers only after they have already
started authoring.

## Why this exists

VHK's planner already knows how to describe:

- likely product lanes
- integration targets
- deployable surfaces
- setup recipes
- toolchain choices
- reference patterns
- verification gates

Before this change, new projects started with the runtime skeleton but not the
planning language that explains how a Linux-native deployment should actually
work. The starter artifacts bridge that gap.

## Generated files

### `docs/VHK_STARTER_GUIDE.md`

Human-readable onboarding guide. It summarizes the most important planning
surfaces and suggests the first commands to run when moving from a skeleton to a
real target desktop.

### `docs/VHK_STARTER_PLAN.json`

Machine-readable snapshot of the planner output for the just-created project.
This gives future init/scaffold/studio/export work a stable artifact to consume
without shelling out to the CLI immediately.

## Important caveat

The starter artifacts are intentionally **session-agnostic**. They do not claim
that the current desktop can satisfy the project's needs. They should be
refreshed against a real target session with:

```bash
vhk doctor --json
vhk validate . --json
vhk plan-project . --json
```

## Typical flow

```bash
vhk init ./my_project --template vision
cd my_project
cat docs/VHK_STARTER_GUIDE.md
vhk doctor --json
vhk plan-project . --json
```
