# MP4-M4A-ATOM-BUDGET-01 maintainer hardening skeleton

## Summary

The MP4/M4A metadata duration traversal calls parser leaves with `fh.read(atom_size)`. For `moov/mvhd`, the duration parser needs only a small fixed prefix, but current traversal materializes the entire advertised `mvhd` payload as one `bytes` object first.

## Current-behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q   maintainer_artifacts/mp4-m4a-atom-budget-01/test_mp4_m4a_atom_budget_reproducer.py
```

Expected current behavior in archived lanes:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Suggested fixed-behavior goals

```text
- Pick a local maximum MP4 metadata atom-leaf budget suitable for share scanning.
- Parse mvhd fixed-prefix fields without reading arbitrary trailing padding into
  one bytes object.
- Apply equivalent bounded-prefix or small-budget handling to mp4a/alac sample
  entry leaves.
- Preserve ordinary small MP4/M4A duration extraction.
- Add tests for normal leaves, exact-budget leaves, over-budget leaves, and
  unknown atoms that should continue to be skipped by seek.
```

## Non-goals

```text
- No claim of code execution.
- No claim of peer-only remote exploitability.
- No claim that large MP4 atoms are invalid in general.
- No claim that network-message-size caps address this local parser path.
- No PR patch included.
```
