# ADR 0009: BOOTSTRAPROSE is the lone ordinary entrance

**Status:** accepted in rev0004

## Context

A revision cube may be reopened by an office holder with no conversational memory.
Multiple top-level READMEs, plans, reports, and scripts require the reader to guess which
object is authoritative. The user asked for a single “wake from amnesia” entrance while
retaining the complete working repository in the datacube.

## Decision

The archive root contains one non-hidden entry: `BOOTSTRAPROSE.md`. The complete
working repository lives under the hidden `.datacube/` directory. Hidden `.gitignore`
and optional VCS metadata do not count as ordinary entrances.

`BOOTSTRAPROSE.md` is a living operational brief. The current office holder may and
should rewrite it thoroughly when implementation truth, decisions, build procedure, or
work order changes.

A repository-layout test enforces the one-entry rule in packaged form.

## Consequences

- An amnesiac reader has one deterministic starting point.
- The entrance must contain enough truth and commands to reach all deeper material.
- Build and maintenance tools operate from `.datacube/`.
- A second visible convenience file is a governance defect, not harmless clutter.
- Hiding is organizational discipline, not access control.

## Revisit when

A deployment medium cannot preserve dot-directories, or a tooling ecosystem requires a
visible root artifact that cannot be reached through the entrance. Any exception must
preserve a deterministic single-source wake sequence.
