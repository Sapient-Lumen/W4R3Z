# String preallocation and bounded value rendering (rev0974)

## Why this became the priority

Rev0973 made plugin instruction loops finite, but its own audit named the next
unowned boundary: one Python/native hostcall can allocate or block after a single
VM dispatch, beyond the reach of instruction fuel. The first measured journey was
not hypothetical. A valid plugin-callable `s-replace` request could project a
300,000,000-byte result while the VM's configured result ceiling was 1,048,576
bytes. Rev0973 constructed the Python string first and checked the budget only
after the hostcall returned.

Under a Linux `RLIMIT_AS` ceiling set 128 MiB above the running interpreter's
current virtual size, the old path failed as an empty wrapped `MicromaxError`,
discarded the three rewrite operands, and supplied no policy diagnosis:

```json
{"message":"","stack_preserved":false,"type":"MicromaxError"}
```

The corrected path rejects the exact projection before entering
`str.replace`, preserves all three operands, and remains usable under the same
address-space ceiling:

```json
{"message":"hostcall result budget exceeded: s-replace: 300000000 bytes > 1048576","stack_preserved":true,"type":"MicromaxError"}
```

This is the smallest honest owner for operations whose result geometry is known
before allocation. A process or WebAssembly migration would add a protocol and
runtime while still requiring an explicit memory limit and still leaving the
host implementation responsible for its own allocations.

## Landed boundary

The existing VM attributes remain the public resource contract:

- `hostcall_result_max_bytes` defaults to 1,048,576 bytes;
- `hostcall_result_max_cells` defaults to 8,192 visible cells; and
- a genuine integer `<= 0` is an explicit embedding opt-out.

Malformed, boolean, or fractional settings now fail to the finite defaults
instead of accidentally disabling enforcement.

The `mx.strings` reference host now predicts exact visible geometry before the
allocating CPython call for:

- `s+`: UTF-8 bytes of both operands;
- `s-split`: resulting payload bytes plus the list and every result cell;
- `s-join`: delimiter multiplication plus every part; and
- `s-replace`: source bytes plus non-overlapping match count multiplied by the
  replacement-width delta.

Failures preserve the complete request. `s-format` also restores its format and
count control cells when its output budget denies construction, making allocation
denial transactional across the string family.

## Waste removed during the audit

The correction is not another registry or post-hoc doctrine layer:

1. `s-join` no longer duplicates the caller's entire parts list merely to
   validate it.
2. Repeated references to one immutable string are byte-counted once through a
   fixed-size identity cache. Preflight stops on the first proven overrun, so a
   list containing 50,000 aliases is rejected after the second alias when two
   values already exceed the limit.
3. `s-format` no longer allocates a list of every format specifier and then scans
   the format a second time only to count it. Validation retains one integer
   count; construction is incremental.
4. UTF-8 budget accounting no longer creates a second full `bytes` object. One
   shared counter is reused by string, regex-input, source-load, and editor-query
   preflights.
5. Generic hostcall result-limit messages and prospective preflights share one
   formatter instead of drifting.

## Shared bounded renderer

The same failure shape existed outside hostcalls. `to-str`, `.`, `.s`, and
`s-format %s` could expand a modest object graph containing repeated references
into a very large Python string during one VM instruction. `value_text.py` now
owns one deterministic `StringIO` renderer with an embedding-tunable
`value_text_max_bytes` ceiling, defaulting to 1 MiB.

It preserves the established JSON-ish nested surface, sorted map keys, explicit
host booleans where required, depth-six elision, and top-level unquoted strings
for `.`. It reserves exact UTF-8/JSON-escaped bytes before materializing each
fragment. A denied `to-str` or `.` leaves the source operand untouched; `.s`
prints nothing on denial. A giant integer is rejected from its bit length before
decimal conversion when its minimum representation already exceeds the
remaining budget.

This shared owner removes the duplicated formatter that had begun to diverge
between core language words and string hostcalls.

## Research judgment

Official Python documentation says `str.replace` returns a copy and an
unbounded explicit-separator `str.split` performs all possible splits. CPython's
Unicode API and implementation allocate result storage for new Unicode objects;
a post-return checker is therefore too late to protect the host from the peak.
Linux `RLIMIT_AS` is useful regression evidence because it limits process address
space, but it is platform-specific and is not installed as Micromax's application
policy.

Wasmtime's current resource-limiter API reinforces the same design point: linear
memory growth is separately limited by the embedder, and default linear memory is
not bounded merely because execution fuel exists. A future Wasm plugin host would
still need an explicit memory-size policy and bounded host imports.

Official sources checked 2026-07-18:

- Python string methods: https://docs.python.org/3/library/stdtypes.html#str.replace
- Python split semantics: https://docs.python.org/3/library/stdtypes.html#str.split
- Python resource limits: https://docs.python.org/3/library/resource.html#resource.RLIMIT_AS
- CPython Unicode API: https://docs.python.org/3/c-api/unicode.html
- Wasmtime resource limiter: https://docs.wasmtime.dev/api/wasmtime/trait.ResourceLimiter.html
- Wasmtime store limits: https://docs.wasmtime.dev/api/wasmtime/struct.StoreLimits.html

## What this does not claim

- Existing input objects already occupy memory; this revision bounds result
  amplification, not the entire Python heap or retained plugin graph.
- Counting and native operations still consume CPU inside one dispatch. The
  fixed output ceiling bounds many renderer loops, but it is not a wall-clock
  deadline.
- `s-upper` and `s-lower` can still allocate their bounded-factor Unicode case
  mapping before the generic postcondition runs. Slice and trim allocate only a
  source-bounded result.
- Python/native crashes, syscalls, `os._exit`, extension corruption, and process
  compromise remain outside the in-process capability model.
- Rev0975 gives Linux regex children finite post-request address-space headroom.
  Parent serialization, child request decode, non-Linux workers, RSS/cgroup
  accounting, crashes, and syscalls remain outside that boundary.
- An embedding that deliberately disables byte/cell ceilings owns the resulting
  allocation risk or supplies stronger external containment.

## Next measured frontier

Keep rev0972's reduced plugin world, rev0973's unbypassable instruction fuel, and
this preallocation boundary fixed. The next isolation decision should come from a
plugin-accessible operation whose cost cannot be predicted honestly before entry:
a blocking native call, measured pre-decode child-memory growth, a crash, or a
syscall surface. Use input preflight or incremental construction when geometry
is known; use an owned killable worker, process limit, or component boundary only
when the measured operation requires it.
