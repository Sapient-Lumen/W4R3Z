# Proof obligation — rev0040

Required local evidence:

- operator intent rejects bad signature, replay, rollback, fork, drift, bridge-action ambiguity, and resume-disabled policy.
- service breaker trips open on false service, hard negatives, withdrawal, operator pause, refusal-only loops, and failure streaks.
- service breaker only half-opens under diverse recovery.
- service exit joins operator intent with breaker, drain, continuity, and profile memory according to action.
- operationsfold passes and preserves rev0039 serviceops predecessor history.

Still open:

- live router/SAM stop/start side effects are not joined.
- service exit does not yet consume all historical branchlet report types directly.
- persistent operator intent storage and journal replay are not implemented.
