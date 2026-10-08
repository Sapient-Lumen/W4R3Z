# Durable decisions (rev1000)

Living decisions only. Per-revision surfaces, guarantees, and risks live in
`docs/revision-index.json`; prior bodies remain under `docs/history/`.

## D1 — The editor is the proving ground

Micromax exists to support a calm, trustworthy editor; language and VM cleverness
are means. **Consequence:** trust precedes taste, and taste precedes flow.

## D2 — The VM stays host-neutral

The semantic core has no ambient filesystem, process, network, clipboard,
persistence, or UI authority. **Consequence:** hosts install explicit policy;
future ports preserve observable semantics and contracts, not Python internals.

## D3 — Capabilities are honest application policy

Capabilities constrain Micromax code inside one process; they do not sandbox
hostile Python/native code or bound all memory. **Consequence:** restricted
startup is inert without grants, and documentation never implies OS isolation.

## D4 — Delayed effects retain identity, origin, and lower authority

A later keypress, prompt, timer, callback, recovery, or cleanup cannot replace
its captured object or authority. **Consequence:** delayed work carries identity,
generation, provenance, and coordinate witnesses; stale owners fail closed.

## D5 — Host work is finite and failure remains visible

Blocking or amplifying effects receive surface-appropriate time, byte, row,
depth, count, result, and step limits. **Consequence:** a timeout owns teardown;
partial state, survivors, or ambiguous success are product defects.
Constructor/start, target readiness, and operation use separate clocks when
spawn would consume a short lease.

## D6 — Headless truth precedes renderer behavior

Behavior and failure truth must be observable without curses; views consume
shared models rather than owning semantics. **Consequence:**
`micromax.screen.v1` is the stable compact projection, while the complete screen
graph stays an explicit internal diagnostic surface.

## D7 — Rollback claims stay scoped

Only named in-process state with an exact owner and pre-mutation witness is
restorable. **Consequence:** editor transactions may restore their stated model,
but disk, process, network, native, memory, wall-clock, and crash effects are not
called atomic; prefer the narrowest proved journal and visible cleanup.

## D8 — One owner graph should replace survivor-by-survivor policy

Repeated snapshot/restore/retag/remove families may justify one typed owner seam,
not another broad registry snapshot. **Consequence:** generalize only from a
proven resource family when doing so deletes code and clarifies lifecycle truth.

## D9 — Public extension contracts are smaller than internal Python surfaces

Stable hostcalls, lifecycle rows, and headless models need schemas and
compatibility rules; internal models do not. **Consequence:** reduce interfaces
before process or component isolation so `Editor` internals are not fossilized.

## D10 — Evidence supports the product; it is not the product

Contexts, audits, manifests, archives, and history matter only when they preserve
truthful handoff and reduce risk. **Consequence:** current guidance stays small;
history moves to the ledger; journeys outrank runner or schema expansion.

## D11 — Release claims are evidence-backed and fail closed

Revision, context, tested source, wheels, receipt, and archive must agree; focused
tests never imply a full suite. **Consequence:** capture source once, derive and
verify independent artifacts from it, normalize declared metadata, probe the
exact installed wheel, and block publication on drift or lineage mismatch.

## D12 — Refactoring follows demonstrated pressure

Large coordinators shrink through tested ownership boundaries, not speculative
rewrites or directory reshuffling. Exact caches and derived indexes are allowed
only when source/configuration witnesses and fail-safe invalidation are executable.
**Consequence:** extract only where identity, authority, stale state, rollback,
disclosure, repeated work, or resource pressure is measured.

## D13 — Recovery is staged review, not automatic overwrite

Recovery preserves interrupted-save text without replaying it onto a possibly
changed target. **Consequence:** open it dirty, leave disk untouched, suppress
autosave, and require explicit save/save-as or dismissal after conflict.

## D14 — Journal retirement follows durable verified commit

A writer return alone does not resolve a checkpoint. **Consequence:** retire only
after target authority, exact bytes, and required file/directory durability are
verified; surface cleanup failure without falsifying a completed save.

## D15 — Plugin approval names immutable bytes; activation and revoke are commits

Restricted startup is inert. Approval captures a bounded immutable package;
activation/reload commits it, replacement stays pending until reload, and revoke
removes managed runtime without trusting plugin cleanup code.

## D16 — Durability claims name completed boundaries and tested filesystems

File data, inode metadata, and directory namespace completion are distinct
witnesses. **Consequence:** name the exercised filesystem/platform; unsupported
synchronization is false, real I/O failure is visible, and broader power-loss
claims require matching evidence.

## D17 — Private residue cleanup requires process-instance and transaction proof

Names, age, basenames, and PIDs alone are not deletion authority. **Consequence:**
cleanup requires the exact private save lease and disproved creator identity in
the same PID namespace; unknown or cross-namespace evidence leaves residue.

## D18 — Matching bytes do not retire an incomplete metadata transaction

Atomic replacement, final mode, file sync, and directory sync are separate. A
versioned recovery row pins mode intent until an authority-checked continuation
completes and verifies every required boundary.

## D19 — A public screen contract has an independent finite consumer

`micromax.screen.v1` is closed, bounded, strict-JSON, and consumed independently.
Reject dimensions before traversal, neutralize terminal controls, version
semantic changes, and keep unknown valid token values forward-compatible.

## D20 — Reproducibility normalizes undeclared host metadata

Sealed sources include `SOURCE_DATE_EPOCH`; materialized files/directories use
0644/0755; phases use separate homes and copies; equality is checked at final
wheel/archive bytes and receipts. Executable package members need explicit policy.

## D21 — Direct manipulation must be visibly truthful

Selection and current search targets cannot exist only in hidden editor state.
Direct manipulation outranks syntax, and headless consumers receive the same
bounded row cues the renderer uses. **Consequence:** selections, selected
newlines, and current-match precedence remain explicit; styling stays separate
from tokenization, and new theme/schema surface requires a real consumer.

## D22 — One editing invocation has one coordinate space and one undo boundary

Every range in one multi-location edit belongs to one immutable pre-edit
document; visible cursor/selection state authorizes continuation. **Consequence:**
exact duplicates may coalesce, ambiguous overlap fails before mutation, one
validated plan maps all sidecars, and one invocation owns one editor history
boundary. Navigation-only macros add no row. External effects are never claimed
as part of editor rollback.

## D23 — Repeated search has one fixed loop and one source-coordinate truth

Navigation, count, and highlighting share one ordered set of non-empty,
non-overlapping source spans; rendering only projects it. **Consequence:** wrap
feedback is explicit, a sole match does not claim movement, and snapshots are
transient leases over exact buffer identity/version/query/options. Zero-width
interaction, full Unicode folding, grapheme coordinates, and persistent indexes
remain separate measured work—not hidden cache or schema claims.

## D24 — Caller-authored regex compilation and execution share one killable boundary

A timeout must own parsing, matching, capture expansion, and result construction;
pattern heuristics are not safety proof. **Consequence:** finite non-literal work
runs in one owned stdlib child with startup/request clocks and non-mutating
failure; query-replace consumes one immutable packed plan. Literal work stays local and an
explicit nonpositive VM timeout remains the embedding escape hatch. This bounds
foreground availability, not hostile code or all memory.

## D25 — Plugin imports are explicit; host presentation stays internal

Load order is not import authority, visibility is not write authority, and
renderer snapshots are not extension API. **Consequence:** plugin code may read
only self, Forth, and its declared dependency closure; only its own dictionary is
writable. Host-owned status, prompt, screen, gutter, viewport, and display models
remain internal. Mutable returns and shared hooks require explicit capabilities.
This is an in-process API boundary, not hostile-code containment.

## D26 — Specialized line edits project from one immutable source plan

Line edits may not mutate first and repair cursor geometry afterward. Half-open
line boundaries retain their semantic role. **Consequence:** move, duplicate,
and cut-line derive text, cursors, anchors, and one undo row from one pre-edit
plan. Unproved marks, diagnostics, folds, and decorations do not silently move.

## D27 — Code being limited cannot own the limiter

Script budgets are language controls, not host authority. **Consequence:** host
frames are separate, every active host frame charges every dispatch, and plugin
source/lifecycle/callback work receives one fresh finite allowance that cannot be
cleared by guest nesting. This proves instruction liveness only; blocking calls,
native work, memory, syscalls, and crashes need separate owners.

## D28 — Predictable result geometry is an entry precondition

Post-return budgets cannot own allocation inside a primitive. **Consequence:**
concatenate, split, join, replacement, and rendering preflight or build under
exact byte/cell ceilings while operands remain intact. Opaque measured work may
justify isolation; no total-heap or hostile-process claim follows.

## D29 — A killable opaque-native worker owns peak memory as well as time

A deadline does not bound native allocation. **Consequence:** finite regex work
gets host-owned headroom; Linux children lower `RLIMIT_AS` after owning input.
Large query-replace sends a file descriptor, not full parent text; flat callers,
non-Linux memory, page cache, RSS/cgroups, syscalls, and crashes remain residuals.

## D30 — A promised portable value domain is enforced at every typed seam

Micromax `Int` is a non-boolean signed i64 at source, conversion, bytecode,
dispatch, predicates, and typed consumers. Arithmetic checks before commit;
decimal ingress rejects before bignum materialization; `/` floors and `mod` is
paired. Python's arbitrary precision is not part of the language contract.

## D31 — Blocking host primitives need external finite owners

Capability and VM fuel stop at Python/native dispatch. **Consequence:** default
`ed.open-url` runs discovery/launch in a bounded isolated child and tears down
supported process trees on timeout. Permanently blocked construction may retain
one daemon starter. Windows descendants, detached effects, syscalls, total
memory, and crashes remain outside the claim.

## D32 — Completion follows resources

Leader exit is not completion while capture pipes or IPC survive. **Consequence:**
argv/shell capture owns one drain and supported pipe cleanup; filesystem workers
close IPC on every path; detached effects stay external. This is ownership, not
a registry or sandbox.

## D33 — A worker timeout owns every byte of one private terminal frame

One-shot workers publish one bounded private-socket frame. The parent reads its
header and body under one absolute deadline, rejects oversize before growth, and
owns producer and endpoint cleanup. Generic Queue/Pipe terminal receives do not
return to product owners; construction and child serialization remain residuals.

## D34 — Construction deadlines; sparse derived geometry

Construction and readiness/execution share one lease; derived geometry keeps
compact coordinates under exact source witnesses. Multiprocessing and Popen use
one pending starter with late cleanup. Rich rows stay at view/compatibility seams;
permanent starters and Windows trees remain residuals, and no broker is implied.

## D35 — Ordinary undo retains inverse edits, not document generations

Common one-cursor edits store exact old/new slices plus sidecars and refuse stale
replay without losing stack membership. D37 extends this to immediate groups. No
undo tree or text rewrite is implied.

## D36 — Linear history owns retained text at whole-row boundaries

Rows declare logical UTF-8 charges; `undobytes` retires only a complete oldest
prefix, clears abandoned redo, and preserves one oversized newest row visibly.
Cached totals/deques avoid rescans and shifts; aggregate rows retain full local
state only for changed buffers. This is not RSS/object/native accounting, a hard
limit, per-buffer chronology, persistence, or coalescing.

## D37 — Immediate simultaneous history is one sparse atomic group

Retain changed slices plus sidecars; validate every target before one commit;
preserve same-offset inverse order; omit equal-text payload. Empty-slice replay
checks geometry, not neighboring bytes. No undo tree or text-engine change follows.

## D38 — Grouping work does not authorize eager workspace capture

Aggregate work needs original state before mutation, not copies of possible
targets. **Consequence:** `ed.with-undo` and immediate macros capture one shallow
canonical line-vector generation at each touched buffer's first write;
untouched/navigation-only buffers stay lazy, and finalization rolls back. Eager
joined-text replay is a test oracle; query-replace keeps a delayed planning source
but emits sparse accepted history. The observer is process memory, not a generic
registry.

## D39 — Restore nested counters after guards unwind

Never restore a nesting counter before an active guard's final decrement.
**Consequence:** failed macros unwind local history suppression before restoring
state and preserves enclosing `ed.with-undo`.

## D40 — Typing groups are bounded exact splices, not implicit transactions

Consecutive top-level one-code-point InsertText, Backspace, or Delete actions may
replace only the exact newest compatible history row. **Consequence:** joining
requires continuous time, action serial, buffer version, sidecars, geometry,
authority, and edit kind; commands, motion, failure, nesting, selection,
multicursor and structural work remain boundaries. Every group is capped at 256
code points and replay keeps expected-text guards. This does not authorize an
undo tree, general transaction registry, IME composition model, or text-engine
rewrite.

## D41 — Delayed query-replace owns shallow source truth; history owns accepted slices

Stable delayed matches need coordinates, not joined text. **Consequence:** own
shallow lines, packed starts/spans, generation/text checks, accepted slices,
and one sparse row. Stale cases replay vectors. Literal scans use bounded
windows; regex stages one private file and its child still builds one `str`. No
registry, undo tree, persistent revision, or text-engine migration follows.

## D42 — Sparse replay is line-vector-native before text-engine migration

Grouped Undo/Redo validates one canonical line vector, joins only touched lines,
and publishes once. Flat replay remains an oracle. Exact-dirty, delayed planning,
and huge-line costs stay separate; replay does not authorize a new text engine.

## D43 — Immediate multi-range planning is line-vector-native

One immutable line vector owns duplicate/overlap/mapping geometry; only touched
lines are joined and one vector is published. History keeps changed slices, skips
suppressed inverses, and collapses net-zero composition. Pointer copies, delayed
planning, and huge lines remain explicit; no new text engine follows.


## D44 — Aggregate rollback owns shallow generations, not joined documents

Arbitrary quotations still need authoritative prior content. **Consequence:**
first write retains one detached tuple of immutable line strings per touched
buffer; finalization retains changed after tuples; restore notifies an enclosing
observer. A saturated mutation count gates exact `BufferChange` accounting so
rewound multi-write history falls back conservatively. Pointer/object overhead
remains out of scope; no generic registry or text-engine migration follows.

## D45 — Recovery text carries authority

History binds text and journal authority. Replay uses the current save baseline and never revives retired records.

## D46 — Performance policy follows live generations; representation follows evidence

Load-time size is not durable performance truth. Live threshold crossing may
adopt the same visible conservative policy as opening there, but the crossing
generation stays exact, per-buffer exact mode stays authoritative, and cached
signatures remain valid only for a witnessed immutable generation.

**Consequence:** remove repeated work in the line-list model first. A rope, piece
tree, gap buffer, segmented line, background index, or second document model
requires complete edit/read/search/render evidence of user-visible residual cost.

## D47 — One generation, one save payload

Share bytes only under exact Unix/UTF-8 identity. DOS, other codecs, and cleanup
stay separate; rollback starts before mutation. Async save needs a lease.

## D48 — Recovery authority and recovery payload are separate products

Most recovery decisions need authenticated metadata and payload identity, not a
returned payload object. **Consequence:** v2 stores compact authority before an
exact raw tail; inventory, inspection, residue discovery, permission continuation,
and commit verify the tail in bounded chunks, while only explicit load
materializes bytes. Immediate commit may reuse payload-free authority only while
it remains bound to the exact inode that was fsynced and published. Legacy v1
remains readable; no header-only unverified index, watcher, lock registry, eager
migration, or second journal tree follows.

## D49 — Release authority begins with exact bytes and ends with executed provenance

Configured CI and version labels are not release evidence. **Consequence:** one
source lock authorizes exact wheel hashes, the release child verifies and installs
those bytes without index resolution, and retained receipts bind source, subjects,
and provenance. Hosted, public, platform, sandbox, or consumer-verification claims
require their own executed evidence.

## D50 — Remove reproduced duplicate generations and row graphs first

Delayed query-replace needs shared source and ordered edits, not parent joins,
full-source JSON, or Python row graphs. **Consequence:** share immutable lines,
pack spans, project rows, and use file-backed transport when measurement warrants
it. A rope, registry, or new regex engine still requires product-visible pressure.

## D51 — Evidence state is a product fact

A lane, workflow, or manifest can exist while its evidence is stale, partial, or
failed. **Consequence:** report presence, source and test currency, internal
consistency, completeness, pass state, platform, and consumer verification
separately. Partial checkpoints remain useful but cannot support release claims.

## Open decisions

1. Archive revision, package version, and host API version relationship.
2. Executed hosted/public release publication plus filesystem, durability, and
   cross-platform support matrices.
3. Terminal-cell/grapheme semantics when a concrete second renderer needs them.
