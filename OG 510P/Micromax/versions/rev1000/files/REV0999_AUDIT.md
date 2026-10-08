# Rev0999 audit — file-backed regex transport and project-scan readiness

## Priority chosen

Rev0998 measured two query-replace peaks and corrected the retained dense plan.
The remaining foreground risk was regex startup: the editor joined the complete
line snapshot, embedded it in JSON, encoded another complete byte body, and kept
that request alive while the child decoded its own source. Rev0999 corrects that
measured transport rather than adding another doctrine layer, registry, or text
model.

## Severe waste corrected

Regex query-replace now streams canonical bounded windows from its immutable line
snapshot into one exclusively created file inside a private temporary directory.
The worker request contains only an exact path/byte/character descriptor. The
child validates the descriptor, regular file, opened inode, size, UTF-8
`surrogatepass` decode, and character count before applying the existing regex
memory-headroom, timeout, match, and result ceilings.

The permanent 16,781,311-character three-sample witness records a 16,785,671-byte
rev0998 request and a 437-byte rev0999 request, a 99.997% reduction. Parent traced
peak falls from 54,621,058 to 611,090 bytes (98.881%); parent incremental RSS peak
falls from 50,212,864 to 921,600 bytes (98.165%); process-tree incremental RSS
falls from 92,688,384 to 46,260,224 bytes (50.091%). Plans and visible match views
are exact, staged counts equal the document, and cleanup residue is empty.

The artifact is `.artifacts/rev0999-regex-transport.json`, SHA-256
`3d730fc911abde36d6b02b79e951ee38bfb02e66789a51b9b822386f4f4c86b9`.

## Audit and refactor

Flat-string and file-backed requests now share one worker deadline/budget policy,
one adapter execution path, and one replacement-row validator. Flat and
line-vector regex planning share replacement conversion, worker limits, failure
mapping, and packed-plan publication. The ordinary flat API remains intact for
callers that already own one string.

Protocol exactness rejects coercible float/string/bool/negative counts instead of
silently truncating them. Invalid expected source lengths fail before consuming
the source. The file is created exclusively; normal success, timeout, startup or
worker failure, generator/write failure, and interruption all leave the private
directory scope. Unexpected child-side transport faults now return an inspectable
worker envelope rather than crashing before response. Cleanup failure never
replaces the primary timeout or interruption; Python 3.11+ attaches a diagnostic
note, while the supported Python 3.10 path preserves the primary exception
without relying on `BaseException.add_note()`.

The adjacent worker audit also reproduced a product failure outside
query-replace. A one-file project scan in clean rev0998 could report
`project file scan timed out after 1s` because `multiprocessing` spawn returned
from `Process.start()` before the fresh interpreter had imported the target; the
nominal traversal clock was already running. Rev0999 adds one private socketpair
READY/GO gate. The existing five-second worker-start allowance now bounds target
entry, while the configured project-scan timeout begins only after the target is
ready to traverse. The clean 1.0-second probe fails before observing a file; the
same rev0999 probe succeeds with a 0.05-second traversal lease. Generic worker
ownership gained only an optional bounded post-start callback, so kill, reap,
framing, interruption, and startup-abandonment cleanup remain centralized.

The dedicated transport suite passes 32 tests. A 102-test focused changed-path
union, a 97-test adjacent query-replace/dispatcher/authority/history union, and
five exact plugin cleanup/retirement/rollback nodes pass. The complete generic
worker-process suite passes 31 tests, the project-file picker suite passes 21,
and the exact interaction-authority plus physical `Ctrl-O` regression pair
passes 10. Counts overlap and are not a full-suite claim. All 172 portability
cases and the bounded 31-test doctor preflight pass. Generated context,
structural audit, effect contracts, compile, and lint pass; mypy was not
installed in this offline cloudtainer, so no fresh typecheck claim is made.

Implementation, measurements, primary Python/Linux documentation, rejected
alternatives, and boundary limits are in
`docs/957-file-backed-regex-query-replace-transport-audit.md`.

## Residual risk and next work

- Python `re` still requires one contiguous child `str`; the temporary file also
  consumes filesystem/page-cache bytes, so this is a parent/protocol peak
  correction rather than zero-copy or total-memory proof.
- Staging precedes child startup and has no separate transfer deadline or disk
  lease; add one only from reproduced slow/full-filesystem behavior.
- `SIGKILL` or host loss can bypass cleanup; lone-surrogate capture output still
  cannot cross the existing strict JSON response.
- Project scanning now separates process construction, target readiness, and
  traversal deadlines. Other worker families should adopt a target-ready gate
  only after reproducing the same false-timeout shape; `Process.start()` alone is
  not claimed as target readiness.
- Packed plans remain O(matches), varying captures retain one string reference
  per match, and the shallow source remains O(lines).
- The configured hosted exact-byte release lane remains unexecuted evidence. The
  next highest-value step is to run it, download retained subjects, and verify
  attestation and receipt identity—not to add another local registry.
