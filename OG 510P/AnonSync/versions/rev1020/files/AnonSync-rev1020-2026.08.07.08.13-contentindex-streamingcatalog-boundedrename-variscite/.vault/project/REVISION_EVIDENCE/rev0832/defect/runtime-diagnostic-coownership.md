# Defect: replay-ledger runtime and restore diagnostics shared one translation unit

Rev0831 left five restore diagnostics, fixture construction, subprocess choreography, sleeps, waits, and five raw `fork()` sites in `src/sqlite_replay_ledger.cpp`. The file was both a production persistence owner and a diagnostic process harness. Ordinary runtime consumers therefore compiled production code in the same 5,356-line translation unit that owned roughly 900 lines of release diagnostics.

The mixed owner obscured the restore-lock capability, made dependency direction harder to audit, and encouraged raw post-fork C++ for isolation scenarios that did not require inheritance. Two holder scenarios have moved to the canonical self-exec boundary. Three raw forks remain only where inherited object destruction or inherited recursion evidence is the property under test.
