# Next work — after rev0837

## 1. Anchor the complete pathname walk

The new owner rejects a final-component symlink/reparse point, but POSIX ancestor
components can still be renamed or replaced between lookup steps. Add a
Linux-specific `openat2()` backend rooted at a trusted directory descriptor with
`RESOLVE_BENEATH`, `RESOLVE_NO_SYMLINKS`, and `RESOLVE_NO_MAGICLINKS`, while
keeping the current backend as an explicitly weaker compatibility mode. Define
and test the Windows equivalent as a handle-relative namespace walk rather than
assuming a path string is a trust root.

## 2. Make the time bound real

`O_NONBLOCK` closes the FIFO hole; it does not make reads from every regular
filesystem cancellable. For hostile or operationally critical inputs, move the
entire read/parse operation into a disposable worker with parent-enforced
wall-clock termination, descriptor and memory ceilings, and a small typed
result. Treat timeout as an observation failure, never as partial authority.

## 3. Raise the Windows proof level

Build and run the Windows branch in a real Windows CI lane. Add reparse-point,
share-mode, replacement, truncation/growth, embedded-NUL, and close-error tests.
Use `FILE_ID_INFO` when identity must be compared across different handles;
`BY_HANDLE_FILE_INFORMATION` is adequate for the current same-handle before/
after check but its 64-bit index is not universally unique on ReFS.

## 4. Separate heartbeat bytes from heartbeat meaning

The bounded byte observation is now a leaf; heartbeat JSON parsing, schema,
process-incarnation interpretation, freshness policy, and operator reporting
remain coupled to the 15,202-line domain unit. Extract the next owner around a
canonical heartbeat document and make its acceptance rules executable through a
small corpus. Do not conflate “read exact bytes” with “those bytes authorize a
live daemon generation.”

## 5. Return to the core mission

Continue the larger roadmap: an executable convergence algebra for every
durable operation; a crash-cut oracle spanning SQLite, receipts, sidecars,
manifests, and filesystem publication; disposable hostile-database workers;
and an explicit confidentiality, metadata-leakage, enrollment, rotation,
revocation, recovery, and key-erasure design.
