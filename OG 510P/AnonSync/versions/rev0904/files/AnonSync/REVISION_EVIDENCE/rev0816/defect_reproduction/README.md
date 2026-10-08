# Parent/current allocator-fault differential

The exact current rev0816 worker was compiled once against unchanged rev0815 production owners and once against rev0816. The parent worktree differed from the sealed parent only by the added test file and a focused CMake target. Three cut-1 traces fail on rev0815 and pass on rev0816: savepoint release under persistent failure, savepoint rollback under one-shot failure, and transaction commit under persistent failure.

This is executable defect evidence. It does not infer the bug solely from source shape.
