# Process-topology lifecycle syscall inventory — rev0836

Total direct call sites: **9**.

| Translation unit | `kill`/`waitid`/`waitpid` call sites |
|---|---:|
| `tests/test_process_topology_owner.cpp` | 9 |
| `tests/inherited_test_process.cpp` | 0 |
| `tests/self_exec_test_process.cpp` | 0 |

All lifecycle syscalls in the two wrapper implementations are absent; the compiled common owner contains the complete direct syscall surface.

| Path | Line | Call |
|---|---:|---|
| `tests/test_process_topology_owner.cpp` | 55 | `waitid` |
| `tests/test_process_topology_owner.cpp` | 83 | `kill` |
| `tests/test_process_topology_owner.cpp` | 95 | `waitpid` |
| `tests/test_process_topology_owner.cpp` | 130 | `kill` |
| `tests/test_process_topology_owner.cpp` | 140 | `kill` |
| `tests/test_process_topology_owner.cpp` | 148 | `waitpid` |
| `tests/test_process_topology_owner.cpp` | 172 | `kill` |
| `tests/test_process_topology_owner.cpp` | 176 | `kill` |
| `tests/test_process_topology_owner.cpp` | 179 | `waitpid` |
