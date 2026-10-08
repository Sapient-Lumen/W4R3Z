# Rev0998 audit — packed dense query-replace plans

## Priority chosen

Rev0997 left two measurable query-replace risks: temporary regex source
flattening and one retained Python edit object per planned match. Rev0998 measured
both and selected the dense retained plan because a 100,000-match ordinary
literal session pinned about 12.8 MiB mostly in row objects and coordinate
integers. The correction stays inside the existing planner and delayed
interaction rather than adding another registry, transaction abstraction, or
text representation.

## Severe waste corrected

`ReplacementEdits` now stores interleaved start/end coordinates in one private
`array('Q')`. Literal plans retain one shared replacement string. Regex plans
also share one value when every expanded replacement is equal, and retain a
replacement tuple only when capture expansion varies.

The permanent 200,000-character, 100,000-match witness records 12,792,104 bytes
traced current and 12,921,496 bytes traced peak for the rev0997 object-row
reference. The ordinary rev0998 product records 1,694,286 bytes current and
1,696,621 bytes peak, with exact sampled rows. That is an 86.755% retained and
86.870% peak reduction. Coordinates occupy 1,600,000 bytes on this interpreter;
no per-match edit or Python coordinate objects remain retained.

The plan is complete and read-only before capture mode. Its explicit
`__deepcopy__` shares the immutable owner across plugin/runtime snapshots instead
of rebuilding 100,000 edit objects. Mutable session state, authority, capture,
source, accepted history, and rollback ownership remain unchanged.

## Audit and compatibility

The new owner preserves the existing `Sequence[ReplacementEdit]` behavior:
length, ordered iteration, indexing, negative indexing, slicing, equality, and
concrete already-expanded rows. Literal scanning writes directly into packed
cells and transfers its unpublished array without a second full-size copy.
Regex worker rows are packed immediately after return; varying capture outputs
remain exact. Query-replace consumes the plan directly rather than converting it
back into a tuple.

The established conservative result budget, match ceiling, regex worker
boundary, generation witness, local old-text validation, monotonic coordinate
delta, sparse accepted history, and atomic Undo behavior remain intact.

## Evidence

The focused query-replace union passes 78 tests. Seven exact plugin
cleanup/retirement tests pass, and dispatcher, default-keybinding, and interaction
-authority suites pass around the changed owner. The permanent artifact is
`.artifacts/rev0998-qreplace-dense-plan.json`, SHA-256
`b1e4324cb6ac1a96c2f4e13fe4cb55ce0729dd2fde4a771a322ce861519ba22c`.

Two unrelated broad modules did not finish within explicit cloudtainer deadlines:
a nested help-navigation statusline case exceeded 300 seconds, and a false plugin
callback rollback case exceeded 420 seconds. Tests reached before each tail
passed; these partial runs are not counted as full-suite evidence. The affected
qreplace plugin paths were run separately by exact node ID and passed.

Implementation rationale, primary Python documentation, rejected abstraction,
measurement limits, and residuals are in
`docs/956-packed-query-replace-plan-audit.md`.

## Residual risk and next work

- Packed coordinates remain O(matches), at 16 bytes per match on this interpreter.
- Varying regex capture expansion still retains one string reference per match.
- Regex begin still creates a temporary complete source and worker-protocol data;
  measure that peak from a real large-regex journey before changing the protocol.
- The shallow source witness remains O(lines), and ordinary replace-all still
  constructs the changed output it must publish.
- The configured hosted release/attestation lane still needs an executed run,
  retained-subject download, and consumer verification; Windows/macOS receipts
  remain unproved.

The next change should be measured regex-start pressure or executed release
provenance, not another policy registry. A streaming regex protocol, rope, piece
tree, watcher, or generic packed-span framework remains unauthorized without a
reproduced product failure.
