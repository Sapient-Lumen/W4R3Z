# Defect: final durable-outcome exception discarded its nested cause

## Previous shape

`reset_sqlite_replay_ledger()` caught a postcommit verification failure and
called `std::throw_with_nested(SqliteReplayLedgerResetDurableOutcomeError(...))`.
The error class was `final` and inherited only `std::runtime_error`.

## Why the claim was false

`std::throw_with_nested` conditionally creates an implementation wrapper that
derives from the supplied exception type and `std::nested_exception`. A final
type cannot be used as that base. The helper therefore threw the supplied
object without a nested wrapper, discarding the active root cause. The typed
outcome and receipt digest survived, but the causal diagnostic did not.

The source audit looked only for the helper call, so it produced a false-green
claim of cause preservation.

## Repair

`SqliteReplayLedgerResetDurableOutcomeError` now also derives from
`std::nested_exception`. Construction occurs inside the active catch, so the
base captures the current exception. Reset and protocol tests recursively call
`std::rethrow_if_nested` and require the injected cause text to appear in the
actual chain.

## Prevention

- Structural audit checks the exception inheritance and runtime oracle.
- Reset test proves the postcommit cause survives.
- Protocol test separately proves reset and publication causes survive.
- Release notes avoid treating a token such as `throw_with_nested` as behavioral
  evidence.
