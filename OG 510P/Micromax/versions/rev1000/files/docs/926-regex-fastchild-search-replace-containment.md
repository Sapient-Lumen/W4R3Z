# Rev0970 — killable regex compilation, search, and replacement

## Outcome

Micromax no longer runs caller-authored editor regex compilation or matching on the editor thread. Whole-buffer find, status/highlight truth, replace planning, and interactive query-replace use one bounded one-shot standard-library child. The VM's `re.search`, `re.findall`, `re.sub`, and `re.subn` hostcalls use the same lane for every finite positive-timeout request rather than trusting a pattern-shape heuristic.

This is foreground CPU-availability containment, not a hostile-code sandbox. It keeps Python `re` and Micromax replacement semantics while making timeout ownership real from parser entry through bounded result decoding.

## What had gone severely wrong

1. **Direct editor regex could freeze the interaction loop.** `(a+)+$` against a near miss ran synchronously in find, screen search truth, replace, and query-replace. In this cloudtainer, 28 `a` characters plus `!` exceeded 12 seconds; 26 took about 5.2 seconds.
2. **The prior VM worker paid for the whole application at startup.** `forkserver`/`spawn` imported package/site state. First startup was about 2.65 seconds and repeated startup about 0.81 seconds, already greater than the 250 ms match deadline.
3. **A heuristic was treated as a safety boundary.** Only recognized nested-repeat/alternation/backreference shapes used the worker; unknown forms stayed local. `NaN` also made `timeout > 0` false.
4. **The first isolation refactor still compiled patterns in the foreground.** CPython's regex parser is recursive. Roughly 1,000 nested groups fit below the 10 KB pattern ceiling yet raise `RecursionError` during `re.compile()` before matching starts.
5. **Replacement rematched mutable text.** Every query-replace answer could invoke the engine again and let accepted replacement text change the later target set.
6. **Failure damaged replay state.** A timed-out or invalid candidate could replace the prior active search register and provenance before proving usable.
7. **Ignore-case literal replacement could corrupt coordinates.** Searching a lowercased copy changes length for characters such as U+0130.
8. **Budgets arrived too late and teardown was duplicated.** Large rows could be materialized before refusal, while regex and filesystem workers carried separate terminate/kill/join code.
9. **One deadline represented startup and matching.** Scheduler delay could consume the catastrophic-match allowance.
10. **Process exit was mistaken for result completion.** A child could flush a complete response before the deadline but miss its final scheduling slice during interpreter teardown.
11. **A compatibility helper regressed.** Once invalid syntax moved to the worker, the historical TUI highlight helper began raising instead of returning an empty match set.

## Implementation

### Minimal isolated child

`src/micromax/regex_worker_child.py` executes directly as:

```text
<sys.executable> -I -S <absolute-child-path> --handshake
```

It imports only the standard library. `-I` ignores caller Python configuration/current/user site and `-S` skips `site` initialization. No shell, Micromax editor import, native extension stack, or multiprocessing bootstrap participates in the default path.

The child owns portable flag parsing, `re.compile()`, matching, capture expansion, replacement construction, incremental match/result budgets, and stable failure classification. It emits plain JSON for VM search/findall/sub/subn, editor non-empty spans, and concrete replacement rows. Deep parser recursion becomes `invalid regex: pattern nesting exceeds engine limit`.

### Two clocks and owned teardown

The parent first waits for one small newline-delimited `micromax.regex-worker.v1` ready envelope under a 2 second startup allowance. Only after readiness does the 250 ms default request/match clock begin. A never-ready or timed-out child is killed and reaped. Python process creation remains outside the post-`Popen` startup clock because the standard API cannot reliably interrupt creation on every platform.

`subprocess.communicate(timeout=...)` waits for process exit as well as output. On timeout Micromax accepts only a complete valid protocol response already present in `TimeoutExpired.output`; bytes emitted after the deadline cannot convert timeout to success.

`src/micromax/worker_process.py` owns shared multiprocessing terminate/join/kill cleanup. The editor filesystem compatibility wrapper delegates to it instead of maintaining a second policy.

### Search is exact, reusable, and fail-closed

`src/micromax_editor/search.py` compiles only escaped literal patterns locally. A non-literal `CompiledSearch` is a source plan; the child owns syntax validation and execution. `SearchSnapshot` is bound to exact `Buffer` identity, `Buffer.version`, query, literal/case policy, and the editor execution policy. One worker-routed result is retained so status and highlight repaint do not relaunch the same request.

`Editor.find()` scans a candidate before committing active-search authority. Invalid syntax, parser recursion, timeout, match-limit, result/protocol failure, or worker failure leaves the previous query, provenance, cursor, and cached replay truth unchanged. A valid no-match query retains ordinary active-search semantics.

The historical `search_match_spans()` renderer helper remains best-effort and non-throwing. It returns no highlights on bounded worker failure. Command/navigation surfaces use `scan_buffer()` and preserve the exact error instead of hiding it.

### Replacement is planned once

`src/micromax_editor/replace_plan.py` returns immutable concrete rows. Regex compilation, matching, and `$...` capture expansion happen once against session-start source text. Interactive query-replace stores those rows, applies only the cumulative length delta from earlier accepted replacements, and validates exact object, generation, bounds, and old text before mutation. `yes`, `no`, `all`, and `last` never re-enter the regex engine or rematch replacement-created text. Accepted work remains one undo transaction.

Ignore-case literal replacement uses escaped `re.IGNORECASE` matching on the original source rather than offsets from a transformed copy.

### VM defaults no longer trust classification

`host_regex.py` preflights stack shape and byte ceilings locally. For a finite positive timeout, compilation and execution both occur in the child. The old classifier remains only for compatibility/diagnostics. Non-finite timeout values normalize to the 250 ms default. Only an explicit finite timeout `<= 0` selects the legacy local-engine embedding escape hatch, which still normalizes parser/template failures and keeps arguments visible on failure.

## Measured and executable evidence

In this cloudtainer:

- minimal `python -I -S` startup plus trivial result measured about 40–47 ms;
- 75 consecutive contained starts measured about 3.2 seconds total;
- `(a+)+$` against 28 `a` characters plus `!` is killed at a configured 100 ms;
- delayed readiness no longer consumes a 50 ms match deadline;
- a never-ready child is killed at its independent startup deadline;
- roughly 1,000 nested groups are classified inside the child in under one second;
- the focused editor/VM/worker/search/replace/TUI slice passes 154 tests after the compatibility repair.

Exact final structural, context, and archive validation is recorded in `REV0970_TESTS.md`. A collected 2,938-test aggregate isolation run exceeded the available execution window and was terminated with its child cleaned up; rev0970 therefore makes no complete-suite claim.

## Primary research

- Python `re` semantics and lack of a standard match-timeout parameter: https://docs.python.org/3/library/re.html
- CPython's recursive regex parser (`_parse_sub`/nested group parsing): https://raw.githubusercontent.com/python/cpython/3.14/Lib/re/_parser.py
- Python `RecursionError`: https://docs.python.org/3/library/exceptions.html#RecursionError
- Python subprocess timeout/kill/communicate behavior and uninterruptible process creation caveat: https://docs.python.org/3/library/subprocess.html
- Python isolated mode and `-S`: https://docs.python.org/3/using/cmdline.html
- Multiprocessing caller-context and termination cautions: https://docs.python.org/3/library/multiprocessing.html
- CPython issue #94675 exponential-backtracking example: https://github.com/python/cpython/issues/94675
- RE2's linear-time/smaller-language alternative: https://github.com/google/re2

Research checked 2026-07-18.

## Residual risk

- Python `re` remains a backtracking engine; the deadline is containment, not linear-time proof.
- `Popen` creation can block before Micromax owns a process handle.
- `-I -S` is interpreter isolation, not an OS sandbox. Rev0975 adds finite
  post-request `RLIMIT_AS` headroom on Linux, but there is still no cgroup,
  seccomp, job-object, RSS quota, or equivalent memory owner on other platforms.
- A single compile/match/capture expansion is now inside the Linux address-space
  ceiling, but parent JSON serialization and child request decode occur before
  that ceiling is installed. The parent still duplicates the buffer into JSON.
- One fresh process per distinct scan favors killability over throughput. Exact snapshot reuse avoids repaint churn but rapid changing queries still pay startup.
- Whole-buffer text and up to 100,000 spans remain eager, not an index.
- Coordinates are Python code points, not grapheme clusters or terminal cells; `re.IGNORECASE` is not full Unicode case-fold equivalence.
- Filesystem child discovery suits source trees and ordinary wheels; frozen executables/zipapps need an embedding adapter.
- An embedding that explicitly sets VM regex timeout to zero accepts local-engine risk.

## Next

Keep this boundary fixed unless a real compatibility, memory, or latency transcript contradicts it. Product work should return to repeated buffer/recent/project movement. Architecture work should classify and shrink extension surfaces before considering broader process or WebAssembly isolation.
