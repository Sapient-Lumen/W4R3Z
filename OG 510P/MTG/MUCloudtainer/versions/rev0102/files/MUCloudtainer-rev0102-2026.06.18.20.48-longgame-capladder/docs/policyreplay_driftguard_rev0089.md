# rev0089 policy replay drift guard

The next risky failure mode after the adaptive-candidate firewall was not another policy tweak. It was evidence identity: the recent population panels mostly store policy names, and policy names are not enough once public-agent factories, ranker models, mulligan models, or terminal-orientation helpers evolve.

rev0089 adds an executable drift guard. It reconstructs deterministic game specs from stored raw evidence rows, reruns an evenly sampled panel under the current runtime, and compares terminal plus target-oriented focus fields. The sample covers rev0069 population frontier, rev0070 population precision, rev0080 complete size ladder, and rev0084 adaptive candidate transfer evidence.

Results:

- 1,632 source rows scanned.
- 64 rows replayed, 16 from each source panel.
- 0 Python errors.
- 0 terminal/focus mismatches.
- 10 source/model/runtime files hashed into `muc5.policy_replay_guard.v1`.
- 1,632 inherited rows lack explicit policy identity digests, so this is a legacy gap rather than an immediate mismatch.

Forward rule: newly generated population or candidate rows should carry `policy_runtime_digest` and `policy_pair_digest`. Historical rows remain usable because the current runtime still replays the sampled rows exactly, but they should not be treated as self-identifying beyond their source revision without replay or sidecar provenance.
