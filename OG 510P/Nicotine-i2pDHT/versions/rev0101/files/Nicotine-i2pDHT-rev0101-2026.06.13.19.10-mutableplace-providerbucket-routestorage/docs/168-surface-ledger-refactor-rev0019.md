# rev0019: surface ledger refactor

The active surface ledger now separates historical wake-from-amnesia surfaces from current rev0019 pressure modules. It keeps docs, tests, and modules linked without deleting useful history.

This refactor specifically removes duplicate active module entries from the audit path and adds the new storeflight / leasequorum surfaces alongside the broader hidden rev0019 store-contract work.
