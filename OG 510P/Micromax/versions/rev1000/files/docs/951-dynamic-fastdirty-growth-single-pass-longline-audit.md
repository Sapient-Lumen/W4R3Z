# Rev0994 audit — live-growth fast-dirty and bounded long-line repair

## Why this was the next risk

Rev0993 left one concrete performance question ahead of another architecture
program: does the editor still become visibly expensive when a small or empty
buffer grows into a very large document, especially one dominated by one logical
line?

The answer was yes, but the first failure was not yet evidence for a rope, piece
tree, gap buffer, or second document model. Automatic `fastdirty` was selected
only from the saved baseline in `Editor.new_buffer()`. A buffer created below the
1 MiB threshold could grow to tens of megabytes and continue hashing the complete
logical document after every mutation forever. On the same path, same-line
insert, delete, and replace each spelled immutable string reconstruction
separately, and an exact dirty signature computed during the last edit was
computed again at `mark_clean()`.

That is the heart of this revision: make the existing policy follow the live text
generation, remove demonstrably repeated work, and stop before changing the
representation without evidence.

## Reproduced waste and correctness hazards

### Creation-time-only policy

A baseline of 1,048,575 bytes followed by one paste to 32,000,000 characters and
32 one-character follow-up edits stayed in exact mode before this revision. The
crossing edit and every later edit joined, encoded, and hashed the complete
logical document. The visible local option remained absent, even though a file
opened at the resulting size would have received `fastdirty=true` immediately.

### Repeated generation hashing at save and option synchronization

Exact mode already computes `(UTF-8 byte count, BLAKE2b digest)` after a mutation
to classify dirty state. `mark_clean()` discarded that generation result and
hashed the same text again. Recovery-open also sometimes computed an exact
line-vector signature immediately before save without retaining it for the live
generation.

A separate audit found that every local `fastdirty` option change resynchronized
all open buffers, and `Buffer.set_fastdirty(False)` rehashed exact text even when
the buffer was already in exact mode. Setting local policy on one small buffer
could therefore hash every unrelated exact buffer in the workspace. The setter
is now idempotent: only a real transition from sticky to exact mode recomputes
dirty truth. The broad option sync remains simple, but unchanged buffers perform
no document work.

### Divergent one-line reconstruction

Same-line insert, delete, and replace used separate chained-concatenation
expressions. They were semantically equivalent, but the duplication made it easy
for allocation shape and corner cases to drift. A no-op empty insertion still
constructed an expression even though the original immutable string could be
returned unchanged.

### Cross-line branch regression caught during the refactor

The first consolidation draft correctly routed same-line replacement through the
shared splice constructor but accidentally sent a multi-line range replaced by
one logical line through the true multi-part branch. That duplicated the single
replacement as both the first and last part and left two rows instead of merging
the surviving prefix and suffix. A flat-text differential audit found the defect
before packaging. The corrected branch performs one three-fragment join, returns
the original one-line cursor geometry, and round-trips through the exact inverse
witness.

### Cache invalidation at the mutable compatibility seam

Adding generation-signature reuse exposed a correctness requirement that did not
exist while every save rehashed unconditionally: every owned mutation must
invalidate or replace the cached signature. The normal `Buffer` primitives,
line-vector publication, history restore, failed-save rollback, recovery replay,
and macro rollback were audited. The temporary observed `Buffer.lines` view used
by aggregate transactions was the dangerous seam: it announces a raw write for
first-write capture but deliberately leaves version/dirty publication to the
historical `touch_external()` contract. Rev0994 now invalidates the generation
signature before every such observed raw mutation, so a missed late touch cannot
make save adopt the pre-mutation digest. Outside observation, direct mutation of
the raw public list still requires `touch_external()` as documented.

### Differential-test false failures

Rev0993 added random per-buffer recovery identities to aggregate snapshots. The
rev0986 and rev0987 eager-versus-first-write differential oracles created two
independent editors and compared those random IDs as though they were product
behavior. The untouched rev0993 baseline therefore produced 60 false failures in
one suite even when both transaction implementations were otherwise identical.
Both helpers now normalize only the nondeterministic recovery ID while retaining
text, options, cursors, dirty state, authority sidecars, and history behavior in
the comparison.

## Landing

### Live-generation automatic promotion

A buffer with no local `fastdirty` override and no enabled global value begins in
exact mode. After an exact mutation produces a generation at or above
`FASTDIRTY_AUTO_BYTES` (1 MiB), the buffer:

1. classifies that crossing mutation exactly against the saved baseline;
2. retains the exact generation signature;
3. switches subsequent mutations to sticky dirty tracking; and
4. mirrors the decision into visible `local_options["fastdirty"] = True`.

Promotion is sticky and truthful. `setlocal fastdirty false` remains the explicit
per-buffer opt-out: it disables automatic promotion, recomputes exact dirty state,
and keeps hashing later edits exactly. The global default value does not record
whether a user explicitly wrote `false`, so this revision does not claim a new
global force-disable control.

### Generation-local exact signature reuse

`Buffer` now retains an exact signature only for the current immutable text
generation. Every ordinary mutation invalidates it before dirty refresh; exact
refresh replaces it; fast-dirty mutations leave it unknown. `mark_clean()` adopts
the cached value when present and hashes only when the current generation is
unknown. Reapplying the already-active dirty mode is a no-op, so one buffer's
local option mutation does not rehash unrelated exact buffers.

The cache is propagated or invalidated at the owners that can move text without
the ordinary mutation sequence:

- interrupted-save snapshot and recovery replay;
- aggregate macro/`ed.with-undo` snapshot and rollback;
- nested line-vector restore;
- save cleanup rollback after write failure; and
- the observed mutable-line compatibility view.

The cache is derived state and does not itself create an undo event.

### Shared same-line splice constructor

Same-line insert, delete, and replace now call `_splice_line_text()`. It clamps
coordinates, preserves the original string for an empty no-op, omits unnecessary
empty fragments for edge deletion/replacement, and presents remaining fragments
to one `str.join()` operation. Multiline edge assembly uses the same single-join
helper where applicable.

This is intentionally not a segmented text representation. Prefix and suffix
slices plus the result still make one enormous changed line O(line length), and
traced peak allocation remains essentially unchanged.

## Measurement

The permanent local artifact is
`.artifacts/rev0994-dynamic-fastdirty-longline.json`, produced by
`tools/measure_dynamic_fastdirty_longline.py`.

On this cloudtainer, a 32,000,000-character middle splice over seven samples
reported:

- pre-revision chained-expression median: 0.022547390 s;
- shared single-join product median: 0.020891740 s;
- local elapsed reduction: 7.343%;
- exact result equality: true; and
- traced peak: about 64.0 MB on both paths, so no peak-memory reduction is
  claimed.

For the lived growth path—start at 1,048,575 characters, paste to 32,000,000,
then perform 32 follow-up one-character edits—the same local run reported:

- automatic product: 1 complete-document signature call and 0.173393803 s;
- explicit exact reference: 33 signature calls and 1.428605599 s;
- signature-call reduction: 96.970%;
- local elapsed reduction: 87.863%; and
- exact final text lengths on both paths.

The elapsed values are local attribution, not portable benchmarks. Python
allocation tracing is not RSS. The main product win is eliminating repeated
whole-document exact hashing after live threshold crossing; the `str.join`
refactor is a smaller copy-work improvement and does not remove the immutable
long-line cliff.

## Online comparison

Research was checked on 2026-07-29.

- Python's official sequence documentation warns that repeated concatenation of
  immutable sequences can become quadratic and recommends `str.join()` or other
  single-construction strategies for strings:
  <https://docs.python.org/3/library/stdtypes.html>.
- micro's current option documentation describes exact dirty hashing when
  `fastdirty` is false, sticky modified-bit behavior when true, and automatic
  enablement for sufficiently large buffers. Its documented threshold is 50 KiB;
  Micromax retains its independently measured 1 MiB threshold:
  <https://github.com/zyedidia/micro/blob/master/runtime/help/options.md>.
- VS Code's official text-buffer reimplementation account describes moving from
  a line array to a piece table/piece tree only after measured memory and
  performance failures across large-file workloads, not merely because a
  sophisticated representation existed:
  <https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation>.
- A current micro issue asking for a way to force-disable automatic fast-dirty
  reinforces that automatic policy must retain a truthful opt-out surface:
  <https://github.com/zyedidia/micro/issues/3817>.

The design choice follows those facts narrowly: use one-pass string assembly for
the current representation, make the existing large-buffer policy follow live
growth, preserve explicit exact mode, and defer a representation rewrite until
remaining read/edit/render/search evidence justifies it.

## Permanent evidence

`tests/test_rev0994_dynamic_fastdirty_longline.py` covers:

- exact UTF-8-byte threshold crossing, visible sticky promotion, and no later hash;
- explicit local false preserving exact mode without rehashing unrelated exact buffers;
- failed macro rollback restoring automatic-promotion authority;
- exact-generation reuse at `mark_clean()` and hashing for unknown fast-dirty
  generations;
- failed cleanup save restoring the cached crossing generation;
- observed raw-line mutation invalidating the cache before save adoption;
- 2,000 seeded Unicode/surrogate same-line differential splice cases;
- 1,500 seeded multi-line replacements against a flat-text oracle, including
  exact inverse-witness replay and the cross-line-to-one-line branch; and
- shared insert/delete/replace construction.

`tests/test_rev0994_dynamic_fastdirty_measurement.py` validates the permanent
measurement schema and exactness claims. Rev0986/rev0987 differential suites
retain their original broad transaction checks while normalizing only random
recovery identities.

Final executed evidence is recorded in `REV0994_AUDIT.md`; no monolithic-suite,
portable-latency, RSS, or cross-platform claim is made from the focused lane.

## Residual risk

- The threshold-crossing edit still pays one complete exact signature so dirty
  classification remains truthful.
- Once automatically promoted, dirty state is conservative until save or an
  explicit return to exact mode.
- One enormous changed logical line still copies slices and allocates one full
  result string; the measured 32-million-character splice retains about 64 MB of
  traced peak allocation.
- The threshold is fixed and promotion has no automatic demotion or hysteresis.
- Raw `Buffer.lines` mutation outside an active observer still requires
  `touch_external()`; private aliases retained before observation remain outside
  the supported cache contract.
- Query-replace still owns one immutable complete delayed planning source.
- Aggregate history still copies O(number of lines) pointer vectors for changed
  buffers.
- `undobytes` and `tracemalloc` do not bound object headers, allocator arenas,
  native memory, RSS, or portable latency.
- No grapheme/IME grouping, renderer segmentation, piece tree, rope, gap buffer,
  background index, or second document model is introduced.

## Highest-value next work

1. Finish signed/hermetic publication evidence and bind filesystem, terminal,
   Windows, and broader platform claims to executed receipts.
2. Exercise the post-rev0994 huge-line path through actual cursor movement,
   search, viewport projection, editing, Undo/Redo, and save. Prototype a
   segmented per-line representation only if the remaining O(line length) cost
   is still user-visible in that complete loop.
3. Revisit delayed query-replace planning only from measured interaction
   pressure.
4. Add cross-instance recovery refresh only after reproducing a stale-badge
   journey.
5. Measure line-vector pointer generation only when many-million-line use makes
   it material.
