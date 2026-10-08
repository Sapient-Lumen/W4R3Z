# Debuggability support backend-coverage boundaries — 2026-03-21

This note keeps **P-0486 Debuggability Support Contract Kit** from collapsing artifact posture into fake uniform debugger support.

## The sharper seam

Within **P-0486**, keep these truths separate:

1. **artifact posture exists**,
2. **symbol sidecars were discovered or handed off**,
3. **visualizer assets exist**,
4. **a specific debugger family / OS / version lane was actually checked**,
5. **advanced capability classes were checked**,
6. **portable support claims still need to fail closed when only narrower evidence exists**.

Those are related, but they are not the same product claim.

## What belongs in the backend-coverage seam

The backend-coverage seam is about questions like:

- Which debugger family and operating system combination was directly observed?
- Was the claim based on an actual session, on artifact inference only, or only on a declared asset?
- Does the claim cover basic symbol loading only, or also type visualizers, async debugging, and expression evaluation?
- Which debugger versions were actually in scope?
- What is the strongest **portable** debuggability claim that survives across backends?

## What it is not

### 1. Not broad support posture by itself

`interactive_debugger` versus `backtrace_only` is still a useful broad class.
Backend coverage asks **which debugger families** that class was actually checked against.

### 2. Not visualizer compatibility by itself

**P-0491** is about whether visualizer assets work with a backend/version combination.
Backend coverage is broader: it includes symbol loading, async debugging, expression evaluation, and portable claim ceilings.

### 3. Not source lookup / path hygiene

**P-0493** is about remapped paths, source components, and lookup consequences.
Backend coverage may import that information, but it is specifically about debugger-family capability claims.

### 4. Not a debugger frontend or launcher

This seam should not become a debugger UI, IDE plugin, launcher wrapper, or expression-evaluator project.
It stays at the contract/report layer.

## Working rule for future passes

When a future pass sharpens **P-0486**, it must say explicitly whether it is adding:

1. **support-class truth**,
2. **symbol-layout / handoff truth**,
3. **visualizer truth**,
4. **backend-coverage truth**,
5. **source-lookup impact truth**,
6. or **release-to-release debuggability drift truth**.

Do **not** let the archive quietly rephrase “PDB exists”, “NatVis exists”, or “GDB script exists” into a fake claim that multiple debugger families, async inspection, or Rust expression evaluation are all supported.
