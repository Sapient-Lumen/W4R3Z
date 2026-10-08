# Revision 0970 audit

## Priority judgment

The highest-risk unfinished item in rev0969 was executable foreground work, not another registry: a short caller-authored regex could block find, screen truth, replace, query-replace, or a VM hostcall indefinitely. The existing VM subprocess lane was too expensive at startup, depended on a shape heuristic, and still compiled patterns in the foreground after the first refactor. Rev0970 closes the full compile-to-result boundary.

## Severe findings and corrections

| Finding | Consequence | Correction |
|---|---|---|
| Direct editor regex ran synchronously | Catastrophic backtracking froze the interaction loop | Every non-literal editor scan uses a killable stdlib child |
| Foreground `re.compile()` remained after match isolation | A roughly 2 KB deeply nested pattern raised `RecursionError` before containment | Child owns compilation and returns stable `invalid-regex` |
| VM worker imported application/site state | Startup exceeded the default match deadline | One-shot `python -I -S` child with bounded ready handshake |
| Shape heuristic decided containment | Unknown backtracking forms stayed local | Every finite positive-timeout VM request is contained |
| `NaN`/infinite timeout selected the local branch | Malformed configuration disabled safety | Non-finite values normalize to 250 ms |
| One deadline covered startup and matching | Scheduler pressure caused false match timeouts | Separate startup and request clocks |
| `communicate()` waited for child exit | Complete flushed output could be rejected during slow teardown | Accept only complete valid deadline-captured output, then kill/reap |
| Query-replace rematched mutable text | Repeated CPU cost and replacement-created target drift | One immutable concrete row plan plus cumulative coordinate delta |
| Failed candidate search committed state | Prior replay query/provenance was lost | Scan candidate before register commit |
| Lowercased literal haystack supplied coordinates | Unicode length changes targeted wrong source spans | Escaped ignore-case matching on original source |
| Result limits were post-hoc | Large rows/expansions allocated before refusal | Incremental match and encoded-result checks |
| Worker teardown was duplicated | Divergent leak/failure behavior | Shared `terminate_worker_process` owner |
| Rendering helper began throwing invalid syntax | TUI compatibility regression | Best-effort helper catches bounded worker failures; commands retain exact errors |
| Structural audit checked only the first worker refactor | Foreground compile could regress unnoticed | Audit requires deep-parser, editor/replace, VM, and helper tests |

## Refactor assessment

The change adds two cohesive runtime files rather than a policy family: `regex_runtime.py` owns process/protocol/deadlines, and `regex_worker_child.py` owns pure stdlib execution. It removes the old heuristic from the safety decision, shares worker teardown, and moves query-replace engine work out of the delayed response loop. The child is one-shot; there is no pool, daemon, queue manager, registry, indexer, watcher, or background service.

## Waste removed

- no site/application import in the default regex child;
- no foreground caller-pattern compilation;
- no query-replace rematch after each keypress;
- no duplicate worker for status and highlight on one exact search generation;
- no full match-list build before a known result-budget refusal;
- no separate filesystem-versus-regex multiprocessing teardown implementation;
- no user option or persistent cache to administer the safety default.

## Boundary statement

This is a foreground availability boundary around Python `re`, not an operating-system sandbox. It does not cap child memory, make Python regex linear time, interrupt process creation before `Popen` returns, contain arbitrary Python/native plugin code, or make external effects atomic. The explicit finite nonpositive VM-timeout path remains an embedding opt-out that accepts local-engine risk.

## Remaining highest-value work

1. Repair the first recurring failure in a repeated buffer/recent/project-picker transcript.
2. Classify and shrink extension surfaces before considering process or WebAssembly isolation.
3. Revisit safe engines, pools, chunking, or indexing only from measured latency/memory/compatibility pressure.
4. Audit specialized line geometry only from a concrete edit/undo failure.
