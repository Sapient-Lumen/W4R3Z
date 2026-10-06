# Compatibility view for “normally linked” binaries

Problem: users often need to run prebuilt/foreign binaries that assume:
- default library search paths (`/lib`, `/usr/lib`, …)
- unmodified dynamic-link expectations

Systems that relocate runtimes into a content-addressed store often need a “compat view” because binaries assume conventional loader and library paths.

FreeBSD offers two primitives that can make this cleaner **without mutating the host**:
- **libmap**: map a dependency name to another name/path (libmap.conf / LD_LIBMAP)
- **rtld hints**: `ldconfig`-generated hints file for fast lookup (and an override env var)

## DeriveBSD approach: a policy-governed “compat view”

A compat view is a derived runtime environment (jail or microVM) that:
- exposes a minimal, closure-derived set of libraries in conventional locations
- optionally installs libmap rules to redirect `libX.so` → store paths
- records the mapping as an evidence object so `derive explain` can answer:
  - what was mapped
  - why (policy)
  - which store digests were involved

Key design constraints:
- compat view is **opt-in** and policy-controlled
- compat mapping must never silently fall back to host libraries
- compat mapping is included in blast-radius diffs

## Non-goals (v1)

- perfect execution of arbitrary proprietary blobs
- “just run anything” without policy and evidence

See RFC-0074.
Last updated: 2026-02-23
