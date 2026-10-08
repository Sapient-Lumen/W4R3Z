# Rev0998 audit: packed dense query-replace plans

## Why this was the next cut

Rev0997 removed a complete joined source string from delayed literal
query-replace, then named two remaining candidates: the temporary flat source at
regex startup and one retained Python edit object per planned match. The highest
risk was not obvious from doctrine, so rev0998 measured both before changing an
owner.

The dense-plan case was decisive. A 200,000-character one-line document with
100,000 literal matches retained roughly 12.8 MiB in the parent process after
planning. Most of that was not document text or accepted undo data. It was the
shape of the plan itself: one slotted `ReplacementEdit` object and two separately
allocated Python integers for every match. Plugin/runtime cleanup snapshots then
deep-copied that complete object graph even though the plan is immutable.

This is exactly the kind of waste Micromax should remove: ordinary product state
whose representation is much broader than the work it must perform. The change
stays inside the existing bounded planner and delayed interaction. It adds no
registry, transaction framework, background index, second document model, rope,
or piece tree.

## Reproduced waste

`tools/measure_qreplace_dense_plan.py` initializes the source and `Editor` before
starting `tracemalloc`, then compares two retained shapes over the same shallow
query-replace source witness:

1. a rev0997 reference tuple with 100,000 `ReplacementEdit` instances, each
   holding start, end, and the shared replacement string; and
2. an ordinary rev0998 literal query-replace session with packed source spans and
   one shared replacement value.

The permanent three-sample witness is:

| Retained plan shape | Traced current | Traced peak | Coordinate storage | Retained edit objects | Retained coordinate `int` objects |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rev0997 object-row reference | 12,792,104 B | 12,921,496 B | object fields | 100,000 | 200,000 |
| Rev0998 packed product | 1,694,286 B | 1,696,621 B | 1,600,000 B | 0 | 0 |

The sampled first, middle, and last rows are exact. The product retains one
replacement value and 16 bytes of packed start/end coordinates per match on this
interpreter. Relative to the reference, traced retained allocation falls
86.755% and traced peak falls 86.870%.

The reference directly constructs the legacy retained shape while the product
runs the actual scanner, so the elapsed figures are context rather than a speed
comparison. `tracemalloc` reports traced Python allocations, not RSS, allocator
arenas, native memory, child-process memory, or a portable bound. The permanent
artifact is `.artifacts/rev0998-qreplace-dense-plan.json`, SHA-256
`b1e4324cb6ac1a96c2f4e13fe4cb55ce0729dd2fde4a771a322ce861519ba22c`.

## Product correction

### 1. One packed immutable sequence

`ReplacementEdits` implements the existing read-only `Sequence[ReplacementEdit]`
contract while owning a much smaller representation:

- one private interleaved `array('Q')` of `start, end, start, end, ...` cells;
- one shared replacement string when every row has the same expanded value; or
- a tuple of replacement strings only when regex capture expansion actually
  varies by match.

Length, ordered iteration, negative indexing, slicing, equality, and projected
`ReplacementEdit` rows remain available to existing callers. Indexing creates
one short-lived row for the current operation; the delayed session no longer
retains a row object or Python coordinate integers for every future answer.

Literal scanning writes coordinates directly into its owned packed array. It
never creates the discarded object graph. Regex planning still receives plain
rows from the killable worker, but immediately packs their coordinates and
collapses identical expanded replacements before publishing the plan.

### 2. Immutable ownership is explicit across rollback snapshots

The plan has no public mutator and is complete before capture mode begins.
`ReplacementEdits.__deepcopy__` therefore memoizes and returns the same owner.
Plugin group/generation rollback, interaction snapshots, and other delayed-state
copies share that immutable plan instead of recreating every edit object.

This is not a general exemption from rollback. The mutable `QueryReplaceSession`
state, cursor, authority, source witness, accepted sparse history, and capture
mode are still copied/restored by their existing owners. Only the already-frozen
match plan is shared.

The measurement confirms that deep-copying the reference tuple rebuilds 100,000
edit objects, while deep-copying the packed plan returns the same plan object.
Focused plugin cleanup tests prove that failed cleanup still restores the live
session and provisional undo state correctly.

### 3. The external behavior remains a sequence of concrete rows

`ReplacementEdit` remains the projected public row. This avoids an invasive
rewrite of replacement application, rich preview materialization, or
query-replace navigation. Existing consumers continue to ask for ordered
`start`, `end`, and already-expanded `new` values.

The planner still preserves:

- left-to-right, non-overlapping coordinates;
- literal and regex start positions;
- replace-one versus replace-all behavior;
- Python Unicode ignore-case semantics for literal matching;
- concrete regex capture expansion before interaction;
- match, pattern, replacement, and result-budget failures before mutation; and
- one immutable session-start match set that never admits replacement-created
  targets.

The conservative result-budget accounting is intentionally unchanged. The new
representation uses fewer bytes, but silently expanding the established maximum
would be a policy change rather than a memory refactor.

## Adjacent audit and refactor

The change was traced through every owner of planned rows rather than stopping at
the scanner:

- `ReplacementEditScan` now publishes `ReplacementEdits` directly.
- `QueryReplaceSession` owns that plan without converting it back to a tuple.
- Runtime/plugin snapshots share it through the immutable deep-copy contract.
- Rich ordinary replace planning still projects its bounded display sample.
- Complete ordinary replace application still consumes ordered rows and produces
  the same result text.
- Query-replace still projects only the current row, validates the exact local
  old text, applies coordinate deltas, and records accepted sparse slices for one
  atomic Undo row.
- Literal line-vector scanning from rev0997 transfers its unpublished packed
  array into the plan without a second full-size coordinate copy.

A tempting broader refactor would have introduced a generic packed-span registry
or replaced every edit type in the editor. There is no second measured consumer
that needs that abstraction. Keeping the owner in `replace_plan.py` deletes the
actual waste while preserving narrow code and review boundaries.

## Correctness evidence

Rev0998 adds direct tests for:

- read-only sequence behavior, negative indexing, slicing, equality, and index
  type errors;
- exact 16-byte-per-match coordinate storage on this interpreter;
- uniform versus varying replacement ownership;
- dense literal planning without retained edit objects;
- exact literal and regex public rows;
- varying regex capture expansion;
- actual regex plans whose identical expansions collapse to one value;
- runtime snapshot identity sharing; and
- executable measurement with a greater-than-70% retained-allocation reduction.

The focused query-replace union passes 78 tests across planner behavior,
interaction lifecycle, buffer identity/generation, sparse history, rev0989 and
rev0997 measurements, and the new packed-plan evidence. Seven targeted plugin
cleanup/retirement tests pass, as do dispatcher, keybinding, and delayed-authority
checks around the interaction.

Two much broader, unrelated test modules contain long-running tails in this
cloudtainer: `test_editor_statusline.py` did not finish its nested help-navigation
case within 300 seconds, and `test_plugin_containment_and_caps.py` did not finish
its false-callback rollback case within 420 seconds. All tests reached before
those points passed, and the qreplace-specific plugin tests were then run by exact
node ID. These timeouts are not counted as passing full-suite evidence and are
not attributed to the packed-plan change.

## Primary-source research and what it changed

The implementation follows standard-library contracts rather than relying on a
private CPython layout:

- Python's `array` documentation defines compact homogeneous numeric arrays and
  exposes the architecture-specific cell size through `itemsize`. The product
  therefore records its actual coordinate bytes rather than claiming every
  platform has the same representation:
  <https://docs.python.org/3/library/array.html>
- `collections.abc.Sequence` defines the narrow read-only sequence surface. That
  allows existing callers to retain indexing and iteration without retaining a
  tuple of row objects:
  <https://docs.python.org/3/library/collections.abc.html>
- Python's `copy` protocol explicitly permits a class to control deep copying
  through `__deepcopy__(memo)`. Sharing is safe here because the plan is frozen
  before publication and exposes no mutator:
  <https://docs.python.org/3/library/copy.html>
- Python `re.finditer()` documents left-to-right, non-overlapping match order.
  The packed representation stores that established order; it does not invent a
  new matching algorithm:
  <https://docs.python.org/3/library/re.html>

The research reinforced one design constraint: representation and behavior
should be separated. A compact owner can satisfy the same sequence contract, so
no caller-facing query-replace dialect or new editor-wide span framework is
needed.

## Residual risk and speculation

- Plans remain O(matches). The fixed coordinate floor is 16 bytes per match on
  this interpreter, so the configured 100,000-match ceiling still owns about
  1.6 MiB of coordinates before container overhead.
- Regex begin still materializes one complete source in the editor and serializes
  work/result data across the killable worker boundary. A large regex journey
  may make that temporary parent/child/JSON peak the next query-replace cliff.
- Regex replacements whose capture expansions differ still retain one string
  reference per match. The packed coordinates remove the dominant fixed object
  graph but cannot share semantically different output values.
- Ordinary `replaceall` still constructs output pieces and one complete result
  string. This revision targets delayed plan retention, not the final changed
  document that the command must publish.
- The shallow source tuple and packed line starts remain O(lines), and one huge
  logical line remains O(line length) for changed string materialization.
- Private Python code could mutate `_spans`; the product/plugin language does not
  expose that object. A defensive bytes image would add a full coordinate copy
  and has no reproduced threat to justify it.

The most plausible next local cut is regex-start peak, but only after measuring
an actual large regex journey. Project-wide, the larger evidence gap remains an
executed hosted release/attestation run with downloaded subjects and
consumer-side verification. Neither gap justifies more registries or policy
prose in place of product evidence.

## Validation discipline

Run focused planner, query-replace, sparse-history, interaction-authority, and
plugin rollback tests first. Then run compile, lint, generated context/effects,
structural audit, revision hygiene, portability where touched, and archive
verification. Keep the permanent measurement artifact in the archive, remove
transient caches, regenerate `MICROMAX-CONTEXT.json`, and package only through
`tools/mkrevzip.py`.
