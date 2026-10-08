# Research notes — fork-derived images, spawn boundaries, and SQLite

Accessed 2026-07-18.

## Primary sources

- The Open Group, POSIX `fork`: https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html
  - For a multithreaded process, the child must restrict itself to async-signal-safe operations until a successful exec.
- The Open Group, POSIX `posix_spawn`: https://pubs.opengroup.org/onlinepubs/9799919799/functions/posix_spawn.html
  - Spawn creates a new process image while limiting pre-image work to standardized attributes and file actions.
- Linux `fork(2)`: https://man7.org/linux/man-pages/man2/fork.2.html
  - The child inherits copies of descriptors that refer to the same open file descriptions and therefore shares associated offsets/status and some lock semantics.
- Linux `posix_spawn(3)`: https://man7.org/linux/man-pages/man3/posix_spawn.3.html
  - Implementations may internally use fork-like mechanisms; the architectural value is that application code does not become the pre-exec child program.
- SQLite, “How To Corrupt An SQLite Database File,” section 2.7: https://www.sqlite.org/howtocorrupt.html
  - SQLite connections opened in a parent must not be used or closed through SQLite in the child; a connection used by the child must be opened there.

## Design inference

A crash oracle that needs application or SQLite work should start from a fresh executable image, verify its descriptor/environment/signal/process-group boundary, parse a small exact instruction, and only then acquire filesystem or database authority. Raw fork should be reserved for micro-oracles where inheritance itself is the fact being tested, and the child path should be small enough to audit as a fail-stop/syscall sequence.

`posix_spawn` is not itself a security sandbox and does not guarantee that the C library avoids every fork-like kernel primitive. The relevant guarantee for this test architecture is narrower: AnonSync application and SQLite code is not the program executing in the intermediate image.

## Speculation

The next useful process owner is a capture-capable self-exec supervisor with nonblocking bounded stdout/stderr collection. It could retire the allocator-fault fork-exec bridge and provide one reusable kill-and-reap implementation for older inheritance tests. Longer term, pidfds on supporting Linux kernels could reduce PID-reuse ambiguity, but any pidfd path should preserve a portable wait fallback and remain test infrastructure rather than production authority by accident.
