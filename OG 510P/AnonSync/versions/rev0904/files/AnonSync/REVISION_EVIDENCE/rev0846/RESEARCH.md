# AnonSync rev0846 research notes

Accessed 2026-07-19. These primary sources informed the implementation and
audit. Citation does not imply that AnonSync implements every mechanism or
platform rule described.

## Native thread identifiers are observations, not lifetime authority

The C++ working draft explicitly permits a `thread::id` value to be reused after
the represented thread has terminated. POSIX similarly permits a thread ID to
be reused after a terminated thread has been joined or a detached thread has
terminated. A retained capability therefore cannot safely equate a native ID
with one exact lifetime.

- C++ working draft, `[thread.thread.id]`:
  https://eel.is/c++draft/thread
- Linux man-pages, `pthread_self(3)`:
  https://man7.org/linux/man-pages/man3/pthread_self.3.html
- Linux man-pages, `pthreads(7)`:
  https://man7.org/linux/man-pages/man7/pthreads.7.html

Rev0846 allocates a monotonically increasing process-local incarnation for each
observed C++ thread lifetime and freezes that typed proof in mutable authority
owners. The token is deliberately not an interchange format and exposes no
integer constructor or conversion.

## Thread-local lifetime is not merely storage syntax

C++ gives an object declared with `thread_local` thread storage duration: each
thread has a distinct object, and that object is destroyed on thread exit.
Those semantics can require compiler/runtime machinery even when initialization
looks constant. In the first extraction, storing the public token directly in
TLS emitted a guard, a TLS destructor, and `__cxa_thread_atexit` because the
public token intentionally has a non-trivial destructor.

- C++ working draft, storage duration and thread storage duration:
  https://eel.is/c++draft/basic

Rev0846 keeps only raw, trivially copyable and trivially destructible internal
words in namespace-scope `constinit thread_local` storage. GCC and Clang object
inspection in the revision evidence show no TLS guard, TLS destructor, or
`__cxa_thread_atexit` reference for the final implementation. This is an
implementation-level verification on the recorded toolchains, not a universal
ABI theorem.

## Fork inherits memory but not the vanished threads

After `fork()` in a multithreaded POSIX process, the child contains only the
calling thread while inheriting copies of process memory, including the states
of mutexes and other pthread objects. Until `execve()`, the child may safely call
only async-signal-safe functions. This makes lazy initialization guards, locks,
and runtime registration paths particularly hazardous in child-side authority
refresh.

- Linux man-pages, `fork(2)`:
  https://man7.org/linux/man-pages/man2/fork.2.html
- POSIX / Linux man-pages, `pthread_atfork(3)`:
  https://man7.org/linux/man-pages/man3/pthread_atfork.3.html

The thread-incarnation allocator is therefore namespace-scope,
constant-initialized, and required at compile time to be always lock-free. A
function-local static allocator was rejected during the audit because a child
could inherit its initialization guard while the owning parent thread vanished.
The TLS cache also binds the raw thread generation to the current process
incarnation so inherited bytes are refreshed after an ordinary tracked fork.

This does not make arbitrary library re-entry after a multithreaded fork safe.
The intended production rule remains fail closed or immediately replace the
image; controlled test children exercise only narrowly owned probes.

## Affinity does not cure a data race

The C++ memory model defines a data race as undefined behavior. Checking an
owner's thread token can reject sequential wrong-thread use before protected
state or kernel resources are touched, but it cannot retroactively legalize two
threads racing the owner object, its move, or its destruction.

- C++ working draft, `[intro.races]`:
  https://eel.is/c++draft/intro.races

That distinction drives the API documentation and release caveats: rev0846
establishes exact-thread affinity for selected owners, not internal locking,
shared ownership, or a race-freedom proof.

## Engineering inference and speculation

A monotonic typed token is a useful local capability ingredient, but repeated
pairing of process and thread checks across many owners can itself become a
change amplifier. A future dependency-light `ExecutionIncarnation` owner could
freeze the pair atomically at the type level, provided it preserves the current
post-fork raw-storage constraints and does not obscure fail-stop ordering.

More broadly, local mutable persistence authority should probably converge on a
single-threaded broker or event-loop model rather than accreting mutexes inside
every descriptor owner. That would make serialization an architectural property,
reduce the surface needing thread-affinity checks, and create a natural boundary
for resource limits and hostile-input isolation. This is architectural
speculation, not a rev0846 implementation claim.
