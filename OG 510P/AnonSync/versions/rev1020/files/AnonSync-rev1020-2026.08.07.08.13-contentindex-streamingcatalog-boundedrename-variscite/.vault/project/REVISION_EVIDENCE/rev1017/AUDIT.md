# Rev1017 audit

Rev1017 composes the released owner-only Linux process-resource snapshot into a bounded fixed-schedule series. The command retains one compact aggregate point per round and one first/last/peak envelope per process, so its retained shape is O(processes + samples), not O(processes × samples). PID plus process-start ticks bind one lifetime across every round; restart or socket replacement fails closed.

The adjacent refactor centralizes socket selection, checked arithmetic, deadlines, identities, and round sampling between one-shot and series commands. The fixture now queries page size before mmap, closing a pre-RAII exception window.

This remains sampled diagnostic evidence. It is not an atomic global cutpoint, resource governor, cgroup observer, allocator profiler, Android port, or proof that a multi-terabyte share fits a particular memory budget.
