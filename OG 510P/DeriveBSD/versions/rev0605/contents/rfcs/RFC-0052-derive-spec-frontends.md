# RFC-0052: Spec frontends and compilation to core IR

- Status: draft
- Created: 2026-02-23

## Summary
Define a core Spec IR (schema-versioned JSON) and optional authoring frontends (CUE/Pkl/Starlark) that compile to it.

## Goals
- keep evaluation minimal and deterministic
- allow rich validation and authoring ergonomics
- preserve reviewability and stable diffs
