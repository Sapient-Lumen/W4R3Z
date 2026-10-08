# Audit — rev0966

Rev0966 turns already-retained immutable file operations and payloads into one bounded owner-operable recovery path. `versions` explicitly pays one complete rooted payload-store observation and one immutable replica observation, then projects active non-visible file operations into a default 64-entry, hard 1,024-entry response. It reports causal identity and exact payload presence rather than claiming wall-clock chronology or durable retention.

`restore` does not trust the earlier projection. It re-proves the selected active operation, the sole visible head, catalog state, rooted current path or absence, exact targeted payload, and guarded visible projection before descriptor-rooted atomic publication. The existing prepared local scanner must then mint or adopt a distinct causal successor. Tests cover ordinary predecessor restore and recovery from behind a tombstone; old evidence is neither rewritten nor reactivated.

The adjacent ownership audit removed whole-operation and whole-visible-path response clones. A borrowed immutable active-operation visitor plus a bounded max-heap makes extra projection storage O(requested entries), while complete candidate counts remain truthful. The same mutex-linearized action snapshot preserves history action generations, exact coalescing, changed-request rejection, and drain ordering. Polling status remains filesystem-cold.

Mechanical evidence binds a 16-file binary-aware patch reconstructed 16/16 against sealed rev0965, the 567-file active projection, 219/219 structural checks, all 258 GCC registry tests, independent 39/39 GCC product tests, focused 379-check folder-owner and 107-check local-control suites, a fresh 238-edge Clang ASan/UBSan product graph, and all 39 sanitizer product tests without a retained diagnostic.

The boundary remains deliberately narrow. This is causal predecessor recovery from bytes that happen to remain retained. It is not a retention window, reachability pin, quota, age policy, garbage collector, friendly timeline, conflict copy, batch/directory restore, rename identity, GUI, or cross-owner filesystem/SQLite transaction.
