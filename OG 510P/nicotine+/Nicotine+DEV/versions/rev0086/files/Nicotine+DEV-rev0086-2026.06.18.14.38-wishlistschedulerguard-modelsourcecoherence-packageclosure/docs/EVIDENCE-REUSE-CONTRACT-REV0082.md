# Digest-bound evidence reuse contract — rev0082

Rev0081 already executed the unchanged baseline and candidate source states in independent disposable source trees, producing 60 passed and 1 skipped in each lane. Rev0082 changes only the consumer test packet and cube tooling; it does not change the candidate patch, source proxy, unit command, or JUnit evidence.

Rerunning the same 122 unit test cases would add runtime and mutable-environment risk without increasing discrimination. Rev0082 therefore reuses those results only after checking:

```text
source-bundle SHA-256
executable source ref
candidate patch path and SHA-256
lane status and test totals
JUnit path, existence, and SHA-256
baseline explicitly unpatched
patched lane explicitly applied
```

All 17 checks pass. Any source, patch, command-result, or JUnit change invalidates reuse and requires a new unit lane.

Machine evidence:

```text
data/rev0082_evidence_reuse.json
data/rev0082_evidence_reuse_checks.csv
```
