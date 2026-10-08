# Rev0999 audit: file-backed regex query-replace transport

## Why this was the next cut

Rev0998 removed the dense retained query-replace row graph, but its own handoff
left one conspicuous foreground peak uncorrected. Beginning a non-literal
query-replace still did all of the following in the editor process:

1. join the complete immutable line snapshot into one new `str`;
2. insert that complete string into the worker request;
3. JSON-escape the request into another complete `str`;
4. UTF-8 encode the request into complete `bytes`; and
5. keep the encoded request alive while the isolated child decoded its own
   complete source string.

The delayed session did not retain those copies, so this was easy to dismiss as
"temporary." Temporary allocation still matters on the foreground path. It can
produce a much larger peak than the compact line witness and packed plan it is
supposed to protect, and `subprocess.Popen.communicate()` deliberately buffers
its input/output rather than providing a bounded streaming protocol.

This revision changes that transport only. It does not replace Python's regex
engine, the one-shot killable child, query-replace semantics, the line-vector
document model, or the packed delayed plan.

## Reproduced pressure

`tools/measure_qreplace_regex_transport.py` runs the real editor journey in fresh
supervisor-owned processes. Source and `Editor` construction finish before a
READY/GO barrier. The reference monkeypatch exactly restores rev0998's
`"\n".join(lines)` plus full JSON/stdin haystack. The product enters ordinary
rev0999 query-replace. Both cases use the same 5-second finite worker deadline,
pattern, capture expansion, source geometry, and result budgets.

The permanent three-sample witness uses a 16,781,311-character, 4,096-line
buffer with one capture-expanded match:

| Median measurement | Rev0998 joined/JSON reference | Rev0999 file-backed product | Reduction |
| --- | ---: | ---: | ---: |
| Worker request bytes | 16,785,671 B | 437 B | 99.997% |
| Parent traced peak | 54,621,058 B | 611,090 B | 98.881% |
| Parent incremental RSS peak | 50,212,864 B | 921,600 B | 98.165% |
| Descendant RSS peak | 59,174,912 B | 45,473,792 B | 23.154% |
| Process-tree incremental RSS peak | 92,688,384 B | 46,260,224 B | 50.091% |
| Elapsed context | 0.322151 s | 0.144715 s | not a portable speed claim |

The concrete plan row and current `match_old`/`match_repl` views are exactly
equal. The reference request contains the complete source. The product request
does not; its descriptor reports exactly 16,781,311 staged bytes and characters.
No transport directory remains after any measured product sample.

The cgroup readings are retained only as context. Linux memory controllers can
charge file page cache, and deleted pages can remain charged until reclaim;
other processes also share this cloudtainer cgroup. Those sequential values are
therefore not presented as a clean product/reference bound.

The permanent artifact is `.artifacts/rev0999-regex-transport.json`, SHA-256
`3d730fc911abde36d6b02b79e951ee38bfb02e66789a51b9b822386f4f4c86b9`.

## Product correction

### 1. Stage canonical source chunks, not a parent flat string

`scan_regex_replacement_edits_lines()` consumes the existing immutable
`QueryReplaceSourceSnapshot.lines` and packed line starts. It uses the same
canonical fixed-offset chunk generator as literal planning, so every chunk is an
exact window of `"\n".join(lines)` without constructing that complete value.
Huge logical lines are split at the configured chunk size rather than handed to
the encoder as one unbounded piece.

`run_regex_worker_from_chunks()` writes those pieces once into an exclusively
created file inside a securely generated `TemporaryDirectory`. Text I/O uses
UTF-8 with `surrogatepass` and `newline=""`, preserving Python character
coordinates and line endings across supported platforms. The measured character
count must equal the immutable source witness before a child may start.
Malformed non-integer expected lengths are rejected before the source iterator
is consumed.

### 2. Send one small, exact descriptor

The request now carries `micromax.regex-haystack-file.v1` with:

- the private path;
- the exact staged byte count; and
- the exact Python character count.

It never carries both `haystack` and `haystack_file`. The ordinary flat-string
worker API remains available for VM/search callers that already own one string;
only the large line-vector query-replace path selects the new transport.

The child opens the descriptor read-only, with binary, close-on-exec, and
no-follow flags where the operating system exposes them. It requires a regular
file, verifies its exact size, reads through the already-open descriptor with the
same UTF-8/surrogate/newline policy, checks that the opened inode and size did not
change across the read, and verifies the exact decoded character count. Boolean,
float, string, negative, missing, or otherwise coercible coordinate witnesses
are protocol failures rather than silently truncated integers.

This is defensive exactness inside a private same-application handoff, not a
hostile same-UID filesystem sandbox. Same-size in-place modification by a
compromised peer process is outside the stated boundary.

### 3. Keep the existing regex containment contract

The child still materializes one contiguous Python `str`, because the standard
`re` API matches a complete `str` or `bytes` object rather than a chunk iterator.
It then installs the existing Linux `RLIMIT_AS` headroom above that owned source
baseline before compilation, matching, capture expansion, or response
construction. The existing startup handshake, match deadline, result ceiling,
match ceiling, response validation, process teardown, and plain-data failure
mapping are unchanged.

The refactor also removes duplicated policy code:

- flat and file-backed calls share timeout/startup/result/headroom normalization;
- subprocess and injected multiprocessing adapters share prepared-request
  execution and response validation;
- flat and line-vector regex scans share replacement-template conversion,
  worker limits, failure wording, and packed-plan publication; and
- flat and file-backed replacement rows share one response-row validator.

That consolidation is deliberately local. It adds no registry, transport
framework, second text model, or generic source abstraction.

### 4. Cleanup follows ownership

The parent retains the private directory only while the one-shot worker call is
owned. Context cleanup covers success, no-match, invalid regex/replacement,
worker protocol failure, startup failure, timeout, generator/write failure, and
`KeyboardInterrupt`. Focused tests observe the path during the call and prove it
is absent afterward. A cleanup error never replaces the primary worker failure:
Python 3.11 and later attach it as an exception note, while the supported Python
3.10 path preserves the primary exception without calling the then-unavailable
`BaseException.add_note()`. Unexpected child-side staging faults are converted to
the same inspectable worker envelope used elsewhere instead of crashing before a
response. `SIGKILL`, interpreter crash, or host loss can still bypass Python
cleanup and leave a private directory for external temporary-directory
maintenance.

## Adjacent audit: project-file target readiness

The final changed-path verification exposed a second, pre-existing foreground
failure. In clean rev0998, a one-file project scan with a one-second limit could
return no files and report `project file scan timed out after 1s`. The traversal
was not slow. The default filesystem worker uses the safe `spawn` start method;
`Process.start()` returned after arranging child execution, while the fresh
interpreter still had to bootstrap, import the test/application main module,
unpickle the target, and enter `_scan_project_files_worker()`. The one-second
operation/result deadline began before those steps completed.

Rev0999 separates three finite boundaries:

1. generic process construction/start retains its existing five-second absolute
   lease and late-owner cleanup;
2. one private `socket.socketpair()` READY/GO exchange gives the project target
   a separately bounded five seconds to enter; and
3. only after READY does the configured project traversal/result deadline begin.

`collect_worker_result()` gained one optional `after_start(pid)` callback that
runs before its result clock. It does not infer readiness or provide an unbounded
grace period; each caller must own and bound its own handshake. Project files are
the only new consumer. The child sends one byte, waits for one release byte, then
starts traversal. Callback failure, timeout, interruption, malformed readiness,
EOF, or release failure flows through the existing process termination, reap,
channel close, and abnormal-cleanup owner.

The same standalone one-file probe records:

| Path | Traversal limit | Result |
| --- | ---: | --- |
| Clean rev0998 | 1.0 s | timeout before any file (`files=()`) |
| Rev0999 | 0.05 s | success with `("ready.txt",)` |

This is not a claim that every project tree completes in 50 ms. It proves that
the user-configured scan lease now measures the traversal/result work it names,
not an unrelated fresh-interpreter import. The project picker remains one-shot,
transactional, symlink-conservative, and bounded by file/directory/depth/entry/
path-byte limits. No pool, daemon, watcher, retry loop, or generic readiness
registry was added.

## Semantic and lifecycle audit

The new tests compare file-backed scans with the established flat-string oracle
across one-character chunks, cross-line groups, multiline anchors, start offsets,
replace-one/all behavior, Unicode ignore-case behavior, and capture expansion.
They also cover the injected `spawn` adapter, exact lone-surrogate source
geometry, malformed byte/character witnesses, dual-source rejection, symlink
rejection where `O_NOFOLLOW` exists, parent length drift before spawn, and cleanup
on timeout/interruption.

At the editor boundary, a monkeypatched `QueryReplaceSourceSnapshot.materialize_text()`
that always raises no longer affects regex query-replace. Existing tests still
prove one plan is computed before capture mode, replacement-created matches are
never rescanned, generation/identity/local-old-text checks remain authoritative,
and accepted work remains one sparse atomic Undo row.

The focused changed-path union passes 102 tests. A second query-replace,
dispatcher, interaction-authority, simultaneous-edit, and measurement union
passes 97 tests. Five exact plugin cleanup, retired-generation, group, and
generation rollback nodes pass. The dedicated rev0999 transport suite passes 32
tests. The generic worker-process suite passes 31 tests, the project-file picker
suite passes 21, and the exact interaction-authority plus physical default
`Ctrl-O` regression pair passes 10. These counts overlap and are not represented
as a full-suite total.

All 172 portability cases and the bounded 31-test doctor preflight pass. The
generated context, structural audit, effect contracts, revision/docs hygiene,
compile, and lint checks pass. Mypy is absent from this offline cloudtainer, so
the typecheck wrapper reports that it skipped rather than fabricating a fresh
typecheck result.

## Primary-source research

The implementation and its limits follow primary documentation:

- Python documents that `Popen.communicate()` buffers data in memory and should
  not be used for large or unlimited data. Micromax retains `communicate()` for
  the now-small bounded descriptor/response, instead of pretending its pipe API
  streams the old complete source:
  <https://docs.python.org/3/library/subprocess.html>
- `tempfile` documents secure random names in shared temporary directories and
  automatic context-manager cleanup for `TemporaryDirectory`:
  <https://docs.python.org/3/library/tempfile.html>
- `TextIOWrapper` documents newline handling; `newline=""` enables recognition
  without translating returned line endings and avoids write translation:
  <https://docs.python.org/3/library/io.html>
- Python's codec registry defines `surrogatepass` for UTF-8/16/32 so surrogate
  code points can round-trip as ordinary code points:
  <https://docs.python.org/3/library/codecs.html>
- Python documents `BaseException.add_note()` as new in 3.11, so cleanup
  diagnostics use a feature probe instead of breaking the supported Python 3.10
  runtime:
  <https://docs.python.org/3.11/library/exceptions.html#BaseException.add_note>
- Python's `re` documentation defines matching over Unicode `str` or bytes and
  does not expose a streaming haystack API:
  <https://docs.python.org/3/library/re.html>
- Python documents `os.open`, `O_CLOEXEC`, and platform-specific `os` extensions;
  the child uses defensive flags only where available rather than claiming
  identical kernel behavior everywhere:
  <https://docs.python.org/3/library/os.html>
- Linux cgroup v2 documentation includes page cache among tracked userland
  memory, which is why the temporary file's cgroup measurement is reported as
  noisy context rather than omitted or mislabeled as RSS:
  <https://docs.kernel.org/admin-guide/cgroup-v2.html>
- Python documents that the `spawn` start method starts a fresh interpreter and
  is relatively slow, while `Process.start()` merely arranges for the object's
  `run()` method to be invoked in a separate process. The project scanner
  therefore uses an explicit target-entry witness rather than treating start
  return as readiness:
  <https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods>
  and
  <https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.start>
- Python documents `socket.socketpair()` as a connected socket pair and supports
  it on Windows as well as POSIX. The readiness handoff needs only two one-byte
  messages and no filesystem name or listening service:
  <https://docs.python.org/3/library/socket.html#socket.socketpair>

## Alternatives rejected

### Keep the joined JSON request

Rejected because the real journey reproduced a roughly 54.6 MiB parent traced
peak for a 16.8 MiB ASCII source and a 16.8 MiB request body. Delayed cleanup
does not make that foreground peak harmless.

### Manually stream source through stdin while simultaneously draining stdout

Rejected for this cut. Python explicitly warns about pipe deadlocks when callers
manage `stdin.write`, `stdout.read`, or `stderr.read` directly, while
`communicate()` is the safe ownership primitive but buffers its input. A custom
bidirectional pump would need portable partial-write/read deadlines, startup
handoff, interruption, stderr/result ceilings, and whole-process teardown. That
is substantially more failure surface than one private exact file and small
existing protocol.

### Shared memory, `memfd`, or an inherited anonymous descriptor

Rejected as the default because cross-platform naming/inheritance, Windows
handle transfer, resource-tracker behavior, lifecycle after spawn, and archive
installation testing would broaden the boundary. They also retain a complete
byte owner and do not remove the child's required `str`.

### Replace Python `re`, add a rope/piece tree, or create a generic transport registry

Rejected because the reproduced waste was parent request construction, not
regex semantics or the document model. A third-party engine would change
compatibility and packaging authority. A second text representation or generic
registry would add more permanent system than this single measured owner needs.

### Increase every worker timeout or add a fixed post-start sleep

Rejected for the project scan. A larger traversal timeout hides whether time was
spent importing or traversing, and a sleep guesses rather than witnesses target
entry. A process pool would add retained lifecycle, invalidation, and shutdown
surface. The one-byte gate preserves the short product budget and begins it at
the exact boundary it describes.

## Residual risk and next work

- The child still owns one contiguous decoded source string and Python regex
  native state; the existing deadline and Linux post-source headroom remain the
  containment boundary.
- The temporary file duplicates source bytes and can charge page cache until the
  kernel reclaims it. This correction bounds parent anonymous/protocol copies; it
  is not a zero-copy or total-cgroup-memory claim.
- Staging occurs synchronously before child startup and is not yet governed by a
  separate transfer deadline or filesystem-capacity lease. Add one only after a
  reproduced slow/full-filesystem product failure.
- Abrupt process/host death can leave a private transport directory. Normal
  exceptions and interruption clean it.
- The source transport round-trips lone surrogates, but the existing strict UTF-8
  JSON response cannot return a match/capture string containing a lone surrogate.
- Packed coordinates remain O(matches), varying capture expansions retain one
  string reference per match, and the shallow source witness remains O(lines).
- One fresh child per regex scan still has startup cost; pooling remains
  unauthorized without measured user-visible cold-scan latency.
- Project-file scanning now has explicit target readiness. Other short-timeout
  worker families may still charge post-`start()` bootstrap to their operation
  clock; change them only after reproducing a false timeout, not by applying this
  gate indiscriminately.
- The highest-risk unfinished project step is now external: execute the configured
  tag/manual hosted release lane, retain its exact subjects, and independently
  verify repository/workflow/ref/commit/receipt/attestation identity. Configuration
  is not evidence.
