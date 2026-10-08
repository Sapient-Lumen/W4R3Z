# Regex worker address-space headroom (rev0975)

## Measured failure

Rev0970 made caller-authored regex compilation and matching killable, but its
child had only time and result-size limits. That left a fast native-allocation
path: a pattern can finish before the 250 ms foreground deadline while CPython's
backtracking engine grows repeat state far beyond the source text.

On this Python 3.13.5 Linux cloudtainer, direct uncapped measurements produced:

| request | elapsed | maximum RSS |
|---|---:|---:|
| `(a?){500000}$` over 500,000 `a` characters | about 0.08 s | about 80 MiB |
| `(a?){1000000}$` over 1,000,000 `a` characters | about 0.16 s | about 140 MiB |
| `(a?){3000000}$` over 3,000,000 `a` characters | about 0.46 s | about 386 MiB |

The exact figures are machine- and CPython-dependent. The important ordering is
stable: timeout alone does not bound peak memory when the allocation-heavy match
completes quickly.

## Landed boundary

`run_regex_worker()` now puts a finite `max_memory_headroom_bytes` value in every
owned request. The default is 144 MiB. On Linux, the already-isolated child:

1. decodes the request;
2. reads its current virtual size from `/proc/self/statm`;
3. lowers both soft and hard `RLIMIT_AS` to current size plus the requested
   headroom, respecting any lower inherited limit; and
4. only then compiles and executes the regex.

The limit therefore covers regex compilation, native repeat/backtracking state,
capture/replacement expansion, result construction, and protocol serialization.
A failed allocation returns the stable operation kind `memory-limit` with
`regex worker memory headroom exceeded`; the one-shot child exits and the next
operation starts in a fresh process. A tiny failure envelope is materialized
before the ceiling is installed, so exhausting headroom during final response
JSON construction does not require another successful allocation to report the
failure.

The limit is installed inside the fresh child, not with
`subprocess.Popen(preexec_fn=...)`. Python explicitly warns that `preexec_fn` can
deadlock in a threaded parent. The pure `execute_request()` test seam does not
install process limits, while both the normal `python -I -S` lane and the explicit
multiprocessing compatibility adapter use the child-only wrapper.

The 144 MiB default is deliberately headroom, not a claim that the worker uses or
reserves that much resident memory. It leaves room for the existing 16 MiB result
budget and its JSON/string construction overhead while stopping the measured
hundreds-of-megabytes native growth. A Linux regression uses a two-million-repeat
request for margin, verifies the stable failure, and immediately proves a fresh
worker still matches normally.

## Audit and refactor

The same audit found a smaller allocate-before-denial defect in substitution.
`_apply_replacement_rows()` encoded every source prefix and expanded replacement
into temporary `bytes` objects merely to count UTF-8, and sliced source text
before knowing the result fit. The child now performs an allocation-free exact
UTF-8 preflight, uses a constant-time ASCII path, stops at the first proven
overrun, and only then creates source slices and the final joined string.
Surrogate replacement counting matches Python's `errors="replace"` behavior.

No option, language word, capability, worker pool, lifecycle registry, or schema
was added. One central default reaches editor search, query-replace, and finite
positive-timeout VM regex hostcalls through their existing shared runtime.
The generated effect contract now reports that live worker budget only for
compile/match/substitution hostcalls; `re.escape` remains an input-bounded local
transformation and no longer inherits stale worker claims from the shared row.

## Research judgment

Python documents `setrlimit()` as the process resource-limit interface and notes
that available limits are platform-dependent. Linux documents `RLIMIT_AS` as the
maximum virtual address space and says `brk`, `mmap`, and `mremap` fail with
`ENOMEM` when it is exceeded; stack growth can instead terminate the process.
CPython's current `_sre` state includes dynamically allocated data-stack and
repeat-pool storage, and its issue history includes cleanup fixes for matches
terminated by signals or allocation failure. Those sources support an OS memory
boundary around this engine rather than another pattern-shape heuristic.

Official sources checked 2026-07-18:

- Python resource limits: https://docs.python.org/3/library/resource.html
- Python subprocess `preexec_fn` warning: https://docs.python.org/3/library/subprocess.html
- Linux `RLIMIT_AS`: https://man7.org/linux/man-pages/man2/getrlimit.2.html
- CPython regex state: https://github.com/python/cpython/blob/main/Modules/_sre/sre.h
- CPython regex allocation/termination cleanup history: https://github.com/python/cpython/issues/67877
- Python `re` API: https://docs.python.org/3/library/re.html

## Honest residuals

- The application policy is enforced on Linux. Other platforms retain the
  killable wall-clock/result boundary until they have a tested native equivalent.
- Request JSON encoding in the parent and decoding in the default child occur
  before the post-request headroom is installed. They are proportional to the
  already-owned buffer/request, but are not covered by this limit.
- `RLIMIT_AS` bounds one child address space; it is not an RSS quota, cgroup,
  syscall filter, seccomp policy, hostile-code sandbox, or proof against native
  crashes.
- A parent can still spend memory materializing the request it already owns.
- An explicit nonpositive VM timeout still selects the documented local-engine
  embedding escape hatch and therefore does not use the child boundary.
- One fresh worker per scan remains a throughput tradeoff. Pooling or a different
  regex engine still requires measured latency or compatibility pressure.

## Next measured frontier

Keep this boundary fixed. The remaining high-risk candidates are a concrete
plugin-accessible blocking native call, crash, or syscall path that instruction
fuel and predictable-result preflight cannot own, or a real request-decoding
memory transcript that justifies moving the ceiling earlier. Do not infer a full
plugin sandbox from this regex-specific process limit.
