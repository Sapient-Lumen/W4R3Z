# Rev0956 audit summary

The primary audit follows the shipping payload-integrity path from the
allocation-independent store witness through the folder-process composition,
peer-service state machine, live/terminal status renderer, real CLI loop, and
same-process product regression.

The severe product defect was not corruption detection; rev0955 already failed
closed correctly. The defect was ownership: the retained peer service treated a
typed recoverable integrity alarm like every other exception and destroyed the
only live operator/control surface. Rev0956 makes that alarm one explicit
peer-owner state while preserving terminal behavior for unrelated failures.

The adjacent refactor found and corrected immediate loss of exact evidence after
repair. A bounded most-recent-recovery projection now retains the expected and
observed digests, persistence result, detection count, duration, and monotonic
age. It is never consulted for scheduling or payload authority.

The remaining notable performance debt is duplicate recovery observation. The
peer owner must independently clear the store witness even when a convergence
pass might not touch any payload. The following ordinary pass can observe the
same append-only namespace again. Passing the already re-proved immutable
snapshot into convergence is a promising later refactor, but only if its catalog,
replica, root, and terminal-cutpoint invariants remain unchanged.

The complete-registry audit also caught a test-oracle error: the shared status
validator required a process-local scrub report even for a ready empty folder
whose convergence path had never needed to open the payload store. The schema
and design already make that report nullable. The validator now accepts the
truthful null state while the non-empty corruption/recovery fixture separately
requires a concrete prior report.
