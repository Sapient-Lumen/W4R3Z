# Rev0831 research and design inference

The sources below were rechecked online on 2026-07-18. They are design inputs,
not claims that AnonSync implements every mechanism they describe.

## Primary sources

1. The Open Group Base Specifications Issue 8, `fork()`  
   https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html

   In a multithreaded process, the application must ensure that the child calls
   only async-signal-safe operations until an exec function succeeds. Ordinary
   C++ allocation, iostream, mutex, filesystem, and SQLite paths do not satisfy
   that general post-fork contract.

2. Linux `fork(2)` manual  
   https://man7.org/linux/man-pages/man2/fork.2.html

   The child contains only the calling thread but inherits copies of the
   parent's virtual memory and open descriptors. Mutexes and other pthread state
   may therefore name vanished owners, while file descriptors continue to refer
   to the same open file descriptions.

3. SQLite, **How To Corrupt An SQLite Database File**, section 2.7  
   https://www.sqlite.org/howtocorrupt.html#carrying_an_open_database_connection_across_a_fork

   SQLite explicitly warns against using a parent-opened connection after fork
   and warns not even to call `sqlite3_close()` on that inherited connection in
   the child. A connection used by a child must be opened in the child.

4. Linux `posix_spawn(3)` manual  
   https://man7.org/linux/man-pages/man3/posix_spawn.3.html

   `posix_spawn()` combines process creation and exec while allowing the parent
   to define file actions and process attributes. This removes AnonSync's
   application-level C++ branch between raw fork and exec.

5. POSIX `posix_spawn(3p)` manual  
   https://man7.org/linux/man-pages/man3/posix_spawn.3p.html

   The specification defines the order in which inherited descriptors, file
   actions, process-group attributes, signal mask/defaults, argv, and the
   explicit environment are applied. A process-group value of zero makes the
   child process-group ID equal to its process ID.

6. GNU C Library manual, spawning processes and `addclosefrom_np`  
   https://sourceware.org/glibc/manual/latest/html_node/Process-Creation-Concepts.html  
   https://sourceware.org/glibc/manual/latest/html_node/Spawn-File-Actions.html

   The GNU close-from file action provides one race-resistant child action for
   closing all descriptors from a lower bound. It is intentionally treated as a
   Linux/glibc test dependency, not a portable production API.

## Design inference: exec is necessary but not sufficient

Replacing raw post-fork C++ with exec removes inherited language/runtime state,
but a bare exec can still inherit authority accidentally through descriptors,
environment, signal state, process group, working directory, credentials, and
unbounded instructions. The useful abstraction is therefore not “spawn a
process”; it is “mint one bounded, typed, reaped test capability.”

This led to six explicit layers in rev0831:

1. canonical executable object;
2. versioned and bounded instruction;
3. descriptor/environment/signal sanitation;
4. child-side verification before state opens;
5. exact fixture and digest rebinding after exec; and
6. move-only, deadline-bound parent ownership.

## Speculation: instruction files versus argv

The present instructions fit comfortably inside small fixed-shape argv records.
A future VFS fault corpus may need larger trace plans and result records. At that
point, passing arbitrary JSON paths in argv would create a new namespace race.
A stronger design would have the parent create a private directory, write and
sync one immutable instruction object, bind its object identity and digest, then
pass either a deliberately retained descriptor or an exact object-identity
record. Any retained descriptor must be an explicit exception to close-from and
verified by number, object type, flags, and identity in the exec image.

## Speculation: disposable hostile-database workers

The same process owner is a useful base for hostile SQLite inspection but is not
itself a sandbox. A disposable worker should add parent-enforced wall time,
`RLIMIT_CPU`, `RLIMIT_AS`, file-size and descriptor limits, no-new-privileges,
a narrow seccomp policy, and Landlock filesystem restrictions where available.
Those mechanisms should be layered and availability reported, not silently
assumed.

## Speculation: process-group completion evidence

The current reviewed helpers do not create descendants. If a future helper may
spawn them, observing the leader's exit is not sufficient proof that the process
group is empty. That extension should add an explicit descendant policy and a
race-reviewed completion protocol rather than merely issuing a best-effort
post-reap group kill.
