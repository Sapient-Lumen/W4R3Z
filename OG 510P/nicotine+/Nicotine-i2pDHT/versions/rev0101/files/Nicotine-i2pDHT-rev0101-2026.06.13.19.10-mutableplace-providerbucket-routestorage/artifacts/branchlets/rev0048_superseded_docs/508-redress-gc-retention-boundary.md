# Redress GC retention pressure

`redressgc.py` treats cleanup as a protocol boundary.

A local node may want to minimize policy/redress evidence, but it must not garbage-collect live hard negatives, active redress, or fork evidence that makes later public-bridge behavior auditable. Soft expired evidence can be dropped; hard evidence is retained first. If hard evidence exceeds the local budget, the lane holds instead of pretending cleanup succeeded.

rev0048 adds an explicit check for externally-live hard-negative digests that only appear locally as expired evidence: that is effective loss of hard-negative memory and is quarantined.
