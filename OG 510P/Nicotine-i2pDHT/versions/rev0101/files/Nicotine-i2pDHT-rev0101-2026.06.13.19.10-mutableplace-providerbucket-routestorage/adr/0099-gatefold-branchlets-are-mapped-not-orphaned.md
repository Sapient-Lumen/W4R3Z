# ADR 0099 — gatefold branchlets are mapped, not orphaned

When parallel cube branchlets contain useful work, the right refactor is to fold them into the active path, preserve their history, and make that fold auditable. Deleting branchlets loses wake-from-amnesia value; leaving them orphaned creates maintenance traps.

Status: accepted in rev0024.
