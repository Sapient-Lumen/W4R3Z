# AnonSync rev0827 — neutral proof, bit-cast fence, mandatory owner audit

Rev0827 moves live process-incarnation authority out of the SQLite namespace and
turns the former `uint64_t` alias into a neutral C++ proof used by filesystem
publication and persistence owners. The generic library depends only on `Threads`;
atomic publication no longer reaches through a SQLite-branded capability target.

A deep second-pass review caught and corrected a flaw in the first strong-type draft:
a private constructor did not prevent `std::bit_cast` while the type remained
trivially copyable. The final public proof is non-trivially-copyable and rejects both
raw integer conversion and well-defined `std::bit_cast` fabrication. Internal
lock-free `uint64_t` atomics retain the representation needed by ordinary-fork hooks
and SQLite lifecycle locks. This is accidental domain separation, not cryptographic
or hostile in-process unforgeability.

The release gate also promotes three source audits into CTest. The mutex audit was
stale and failed 60/64 against the exact parent; it is repaired to 64/64. The
owner-generation audit passed 27/27 in the parent but was unregistered; it is now a
mandatory CTest and package-verifier obligation. Together with the new process audit,
the CTest inventory rises from 110 to 113 after the process-test rename.

Final evidence:

- parent ZIP **25/25**, parent directory **21/21**;
- active patch replay **190/190**;
- source delta **45 files, 1,104 insertions, 664 deletions**;
- uninterrupted complete CTest **113/113**;
- focused final CTest **10/10**;
- structural audits **241/241**;
- repeated fork/publication tests **80/80 executions**;
- Clang 17 `-Werror` **9/9**;
- GCC 14 ASan/UBSan **5/5** with `detect_leaks=1`; and
- final dependency closure: **no work**.

The next mission-level correction should be a combined SQLite-VFS and filesystem
publication crash-cut oracle, not another isolated success-path wrapper.
