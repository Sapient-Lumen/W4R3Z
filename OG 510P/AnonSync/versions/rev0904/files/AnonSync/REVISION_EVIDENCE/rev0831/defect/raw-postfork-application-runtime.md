# Defect reproduction — application runtime executed before exec

## Prior shape

The focused reset and combined crash-frontier tests followed this pattern:

```cpp
const pid_t child = ::fork();
if (child == 0) {
    // std::filesystem, std::string, exceptions, fixture C++, SQLite choreography
    ::_exit(...);
}
::waitpid(child, ...);
```

The test result exposed only the final status. It did not prove that the child
avoided inherited mutex/runtime state, SQLite state, accidental file
descriptors, ambient environment, blocked signals, or an unbounded wait.

## Why ordinary success did not close the defect

The child of a multithreaded fork contains only the calling thread but copies
process memory. A mutex copied while another thread owns it can remain locked by
a thread that no longer exists. Allocators, iostreams, filesystem libraries,
exception machinery, and SQLite may all contain such state. POSIX therefore
restricts the child to async-signal-safe operations before exec.

The defect was latent rather than deterministic: a quiet test runner could pass
for years while a sanitizer, logger, parallel test, library initialization, or
new thread changed the copied state enough to deadlock or corrupt the oracle.

## Corrected trace

The parent now performs all instruction construction, calls `posix_spawn()` on
its canonical executable, and receives one move-only owner. Spawn actions close
all descriptors from 3 upward; attributes reset signals and create an isolated
process group; envp is rebuilt. The new image verifies that boundary, parses one
versioned fixed-shape instruction, reopens fixture state, and rebinds exact
hash/path/cutpoint evidence before running the reviewed operation.

A positive sentinel descriptor proves close-from behavior on every successful
spawn. Timeouts and all owner-destruction paths kill and reap synchronously.
