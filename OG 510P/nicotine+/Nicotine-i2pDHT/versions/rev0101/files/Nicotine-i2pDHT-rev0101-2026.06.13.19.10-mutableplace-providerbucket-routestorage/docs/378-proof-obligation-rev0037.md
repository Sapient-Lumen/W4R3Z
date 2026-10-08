# Proof obligation rev0037

Required tests:

- accept exact-scope service tickets;
- reject ticket replay, bad signatures, expiry, rollback, same-sequence forks,
  caller/scope/request drift, unscheduled demands, and budget overclaim;
- accept completion/useful-refusal/partial receipt shapes;
- reject receipt replay, unit overclaim, bad result shape, binding drift,
  refusal-only loops, rollback, and same-sequence forks;
- make `ticketfold` and `foldregistry` pass for rev0037.
