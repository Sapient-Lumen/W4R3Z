# Rev0852 primary-source research

Checked on 2026-07-20 UTC.

## SQLite authorizer retention

SQLite documents that `sqlite3_set_authorizer()` stores a `void*` user-data
value and passes it as the first callback argument. Only one authorizer may be
installed per connection; a subsequent call replaces it, and a null callback
disables it. The correct callback may also be required during `sqlite3_step()`
when schema change triggers statement reprepare.

Source: SQLite C interface, `sqlite3_set_authorizer`:
https://sqlite.org/c3ref/set_authorizer.html

Design consequence: the callback interpretation and referent lifetime must
remain valid for the connection operation interval, not merely the setter call.
A callback and erased pointer supplied independently are therefore an unsafe
public authority shape even when the referent is kept alive.

## C++ shared ownership and aliasing

The C++ working draft specifies that the aliasing `shared_ptr` constructor stores
its supplied pointer while sharing ownership with the original `shared_ptr`.
The stored pointer and ownership group are intentionally distinct concepts.
Custom-deleter constructors similarly associate ownership with the provided
deleter.

Source: current C++ working draft, `[util.smartptr.shared.const]`:
https://eel.is/c++draft/util.smartptr.shared.const

Design consequence: retaining the exact `shared_ptr<T>` in the typed capsule is
stronger than reconstructing an owner from `void*`. It preserves constness,
aliasing pointer identity, the original control block, and custom deletion.

## `std::invoke` is an invocation mechanism, not an authority policy

The C++ working draft defines `std::invoke` in terms of the broader `INVOKE`
protocol. That protocol deliberately supports function objects and member
pointers in addition to ordinary function pointers.

Sources:
https://eel.is/c++draft/func.invoke
https://eel.is/c++draft/func.require

Design consequence: `is_invocable` alone is too permissive for an API whose
contract promises only non-null function pointers or stateless structural
adapters. Rev0852 uses `std::invoke` after an independent admissibility check;
this prevents a mechanically callable form from silently acquiring more
retained authority than intended.

## Post-fork lifetime limitations

POSIX restricts what a child of a multithreaded process may safely do before an
`exec` operation; only async-signal-safe functions are generally available in
that interval. Copied process memory also cannot establish that a C++ shared
ownership control block has valid post-fork synchronization provenance.

Source: The Open Group Base Specifications, `fork()`:
https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html

Design consequence: process-incarnation fail-stop checks prevent inherited
owners from being inspected, moved, invoked, or destroyed. A newly constructed
child owner is valid only as a child-local capability; this revision does not
claim to prove that an arbitrary supplied control block was not inherited.

## Speculation and next architecture

A connection-level callback teardown orchestrator remains attractive, but it
should register already-hardened, API-specific owners rather than flattening all
callbacks into one generic type-erased slot. The orchestrator can model named
slots, exact connection generation, dependency order, revoke-all-before-close,
and executable state inspection while each owner preserves its own C API's
replacement and synchronization rules.

The much larger product proof should remain separate: a deterministic
convergence reference model and generated histories need to define what update,
delete, recreation, rename, key epoch, and external-effect operations mean under
duplication, reordering, partition, concurrency, retry, restart, and crash.
Typed callback safety makes the local kernel harder to subvert; it does not make
distributed replicas converge.
