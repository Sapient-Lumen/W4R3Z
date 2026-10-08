# Research notes — rev0966

The discarded retained-version prototype was useful only as a question generator. Importing it would have created another inventory traversal and restoration owner. The shipping slice instead reuses the existing immutable causal model, append-only payload owner, local action scheduler, rooted atomic publisher, and prepared local scanner.

A bounded response limit is not enough if construction clones the complete model. The corrected projection borrows immutable operations one at a time, asks for visible-path state only for the current candidate, and retains a max-heap no larger than the requested output. This keeps the additional response-owned operation state proportional to the owner request while preserving complete candidate/truncation counts.

Restoring historical bytes must create a present-tense synchronization event. Reactivating an old operation would obscure the current head transition and could violate causal assumptions on peers. Rev0966 therefore treats historical identity only as selection evidence; the ordinary scanner emits the successor that peers reconcile. A tombstone regression is important because current rooted absence and current rooted file replacement are distinct publication branches.

The next useful step is not a larger inventory. It is a deliberate history lifecycle: explicit reachability pins for current, retained-version, and in-flight bytes; owner-visible quotas and age classes; crash-safe mark, quarantine, revalidation, and unlink; friendly ordering metadata; and recovery behavior under ENOSPC, process kill, and qualified power-loss injection.
