# Profile GC and config-change pressure

Profile changes are local protocol migrations. A node that changes router configuration, service catalog, telemetry retention, or start profile must not accidentally delete the very memory that makes it safe after restart.

rev0036 adds `profilegc.py`, which treats local profile memory as typed:

- soft: telemetry, peerbook hints, old service catalogs, old load sheaths;
- active: active profile and router config;
- hard negative: tombstones, revocations, key-crisis notices, provider-false evidence, witness-fork evidence.

The GC lane accepts soft compaction but rejects active profile drops, active router-config drops, future-generation memory, generation forks, and hard-negative loss.

Design guess: a restart profile is not just configuration. It is memory plus configuration plus refusal to forget inconvenient evidence.
