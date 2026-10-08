# Profile cooldown after emergency freeze

Emergency freeze is not a pause button if the next resume signal can route around it. rev0042 makes cooldown profile-level, signed, sequenced, previous-linked, and cleared only by diverse recovery evidence.

`ProfileCooldownEntry` records an emergency freeze, key crisis, router crisis, operator hold, or clearance. Recovery requires explicit signal kinds such as operator resume, breaker recovery, router OK, hard-negative scan, announcement repair, and successor-key readiness.

Current risky cases tested:

- resume is held until `frozen_until` passes;
- missing recovery signal kinds hold;
- one-family recovery evidence holds;
- recovery signals reporting hard-negative pressure quarantine;
- cooldown signature failure, expiry/future time, replay, profile drift, rollback, same-sequence fork, and previous-link mismatch quarantine;
- clearance records are distinct from ordinary expired freeze records.

Design guess: after emergency freeze, slow conservative resume is better than allowing one fresh service proof to bypass local crisis memory.
