# `std::sync::Mutex` blocking and nightly `ReentrantLock` do not imply async-safety

This scenario keeps two facts separate:

- a lock may block and poison,
- a reentrant lock may exist experimentally,
- neither fact alone is an async-context endorsement.
