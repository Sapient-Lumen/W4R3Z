# Revision 0969 audit

## Why this work outranked another feature

Rev0968 explicitly recommended a repeated navigation transcript. The first find
loop proved that Micromax already had all the named surfaces but not one coherent
behavior: repetition terminated at boundaries, newline matches could repeat
without movement, count/highlight/navigation disagreed, and viewport fragments
changed regex meaning. This is exactly the kind of high-frequency trust/flow
failure that should be repaired before adding workspace search, panes, watchers,
indices, options, or registries.

## Severe failures corrected

1. **Boundary termination.** Repeated next/previous stopped despite valid active
   matches elsewhere in the same buffer.
2. **Phantom newline progress.** `Cursor(col + 1)` could clamp to the same
   end-of-line source position and rediscover a newline-starting match.
3. **Overlap disagreement.** Navigation could visit overlapping literal hits
   that status and highlight did not count.
4. **Unicode coordinate drift.** Lower/casefold copies were used as search
   haystacks even though transformed-string offsets need not address the original
   buffer.
5. **Zero-width disagreement.** Regex navigation could succeed at a target that
   count/highlight intentionally omitted.
6. **Row-fragment regex drift.** Softwrap/hscroll suffixes could invent `^`
   matches, while real cross-line matches disappeared.
7. **Redundant and hidden screen work.** Status and highlight rescanned the whole
   buffer, and early projection still copied trailing match tuples per row.

## Refactor boundary

`search.py` is now the sole pure match/navigation/projection owner. `Editor`
retains only authority checks, cursor commits, public feedback, and composition.
The public screen shape and active-search capability model are unchanged.

The correction deliberately does not create a generalized search service. There
is no persistent cache, invalidation registry, results model, workspace index,
background thread/process, new option, or new schema. One composed screen may
hold one transient snapshot, and the snapshot dies with that call.

## Exact identity and staleness review

The first draft checked snapshot version/query/options. A late audit demonstrated
that two different buffers can both be at version zero, allowing the first
buffer's spans to be accepted for the second. The final snapshot retains the
exact `Buffer` object and requires object identity plus version and search state.
Mutation-stale and cross-buffer tests both prove transparent rescan.

This exact object reference is intentionally transient. It is not persisted,
registered, serialized, or retained beyond the screen/navigation call.

## Search policy review

- Non-empty, non-overlapping `finditer` order is shared by all surfaces.
- Zero-width targets are excluded because the editor has no visible advancing
  interaction for them.
- Ignore-case matching leaves source text untouched and uses `re.IGNORECASE`.
- Full Unicode case-fold equivalence is not claimed.
- Forward/backward wrapping is fixed and explicit; configurability was rejected
  as unproven surface growth.

## Viewport and complexity review

Whole-buffer spans are intersected with edit-window source fragments. Renderer
prefix cells and clipping never become regex input. A cross-line match projects
into each visible source segment, and the same source start identifies all
visible fragments of the current match.

Projection bisects sorted match ends to find the first possible intersection,
then indexes until starts pass the fragment end. It does not scan from match zero
and does not slice/copy the trailing tuple. Screen composition scans the active
buffer once when status and highlighting both require search truth.

This improves the repeated display path without claiming a large-file search
engine. Whole-buffer text and all match spans are still materialized.

## Authority, contract, and baseline review

Active-search read/replay authority remains unchanged. Search state created by a
plugin generation is still removed/retagged/restored by the existing lifecycle
owners. Denials remain argument-preserving.

The compact `micromax.screen.v1` object shape is unchanged. Existing search cue
values receive exact projected spans; the independent consumer and highlight
precedence tests remain green.

The working tree was compared against a fresh extraction of the verified
rev0968 archive. Classified changes are limited to current source/tests,
revision documentation, generated revision witnesses, and final context.

## Residual risks

- Direct editor regex execution remains synchronous Python `re`; catastrophic
  expressions are not time-contained.
- Full Unicode case-fold equivalence, grapheme clusters, and terminal-cell
  coordinates are not implemented.
- Pure newline matches have no dedicated visible cell.
- Match snapshots materialize all whole-buffer spans and are not a large-file
  indexing design.
- Search remains active-buffer, not workspace/project search.
- No complete repository-suite or universal performance claim is made.
