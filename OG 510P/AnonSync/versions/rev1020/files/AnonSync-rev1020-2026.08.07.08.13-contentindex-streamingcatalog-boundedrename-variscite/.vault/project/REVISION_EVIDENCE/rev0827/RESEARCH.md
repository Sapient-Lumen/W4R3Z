# Rev0827 research notes

Primary-source review was used to bound the implementation and its claims.

## C++ object-representation boundary

The C++ `std::bit_cast` constraints require source and destination to be trivially
copyable and equally sized. A private constructor alone therefore did not prevent
well-defined fabrication of the first draft's eight-byte trivial proof. The final
public type is deliberately non-trivially-copyable, and a compile-failure reproducer
checks this exact constraint.

- C++ working draft, support utilities / `bit_cast`: https://eel.is/c++draft/support
- C++ working draft, object lifetime and execution model: https://eel.is/c++draft/basic.exec

## Process creation and lineage

`pthread_atfork` handlers run around ordinary `fork()`, with prepare handlers in
reverse registration order and parent/child handlers in registration order. After a
multithreaded fork, the child has only the calling thread and is heavily constrained
until exec. `_Fork()` intentionally does not invoke `pthread_atfork` handlers.

- pthread_atfork(3): https://man7.org/linux/man-pages/man3/pthread_atfork.3.html
- fork(2): https://man7.org/linux/man-pages/man2/fork.2.html
- _Fork(3): https://man7.org/linux/man-pages/man3/_Fork.3.html

Linux pidfds are useful stable handles for referring to another task, but they do not
replace this process-local ordinary-fork lineage and are unavailable on this
cloudtainer's Linux 4.4 kernel (`pidfd_open` arrived later).

- pidfd_open(2): https://man7.org/linux/man-pages/man2/pidfd_open.2.html

## Speculation for the next cube

The highest-value next model is a combined SQLite-VFS and filesystem-publication
cutpoint oracle. It should enumerate database, WAL/journal, temporary inode, receipt,
rename, directory-sync, retry, and ambiguous-return frontiers as one protocol. A
structurally valid database is insufficient when the externally published artifact
or receipt disagrees. The oracle should classify each cut as old state, new state, or
explicitly recoverable indeterminacy, then drive both a small reference model and the
production C++ implementation.
