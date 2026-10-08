# Operator key rotation and recovery

Operator keys sign high-impact local control: intent capsules, service exits, router stops, cooldown entries, and future profile operations. rev0042 treats operator-key succession as a risk surface instead of a maintenance chore.

`OperatorKeyNotice` supports rotation, compromise, recovery, and old-key freeze notices. Rotation requires old-key signature and successor-key cosign. Recovery can be accepted with witness-family diversity. Hard-negative digests can be required so compromise evidence is not silently dropped during succession.

Current risky cases tested:

- rotation accepts only when the successor key cosigns;
- missing successor cosign holds;
- scope drift/widening quarantines;
- recovery needs witness-family diversity;
- required hard-negative digest must be preserved;
- bad signatures, expiry/future time, replay, sequence rollback, same-sequence fork, previous-link mismatch, profile drift, old-key drift, and successor drift pressure are modeled.

Design guess: operator-key recovery should be boringly monotonic, local, and evidence-preserving before it ever becomes a UI flow.
