# Cooperation benchmark programs should publish direct primary verify and refresh target byte counts in handoff packs

If a compact-card handoff pack already publishes direct first verify and first refresh targets, it should also publish one small retained byte-count witness for each of those targets.

The goal is to remove one more inheritor lookup step: the inheritor should not have to scan the retained file manifest just to tell whether the first machine target is the expected small report object.

For the canonical compact-card handoff pack, that means publishing `primary_verify_target_bytes` and `primary_refresh_target_bytes` as strict aliases of the retained file-manifest bytes already bound by the pack. These fields are not a second retention semantics. They are a compact audit aid over the exact first machine targets already retained.
