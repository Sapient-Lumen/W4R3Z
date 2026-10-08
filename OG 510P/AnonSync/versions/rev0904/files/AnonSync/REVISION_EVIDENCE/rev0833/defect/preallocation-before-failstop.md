# Defect reproduction — exception construction before process-capability termination

## Parent behavior

A prepared immutable JSON publication retained the process incarnation that minted its destination authority. When a fork child tried to publish the inherited object, rev0832 detected the mismatch by concatenating the caller-controlled label into a `std::runtime_error`. The exception then entered publication failure composition and unwound copied C++ owners.

That behavior correctly denied publication but used allocator, exception, string, and destructor machinery in precisely the child path that should terminate without exercising inherited application state.

## Correction

Rev0833 routes mismatch to `require_sync_process_incarnation_or_fail_stop` with the static label `prepared immutable JSON publication destination authority`. The mismatch therefore terminates with the shared exact capability-violation exit code before filesystem mutation or C++ unwinding. Dynamic `implementation->label + ...` construction is forbidden by source audits.

## Proof

The retained raw-fork micro-oracle expects the exact fail-stop exit, verifies no final or temp artifact was created, and then proves the original parent capability is still valid by publishing the exact payload. The atomic-publication, raw-fork, crash-frontier, and process-incarnation audits all bind the revised path.
