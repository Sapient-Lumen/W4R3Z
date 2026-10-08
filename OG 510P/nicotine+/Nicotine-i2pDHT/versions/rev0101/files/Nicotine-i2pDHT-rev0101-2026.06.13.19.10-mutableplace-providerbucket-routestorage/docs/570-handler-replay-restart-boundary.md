# Handler replay restart boundary

`handlerreplay.py` models restart replay as a first-class boundary.

It records compact signed frames for component reports such as handler capsules, side-effect journals, and adapter fuzz reports. The assessor rejects bad signatures, expired frames, replays, sequence rollback, same-sequence forks, previous-link mismatch, exact profile/service/scope/request drift, component digest drift, hard-negative pressure, and low family/path diversity.

Design guess:

> A valid component report is not replay-safe after restart until monotonic local memory binds it to the same boundary again.

This is not a database format. It is executable pressure for the restart-memory semantics a production database would eventually need.
