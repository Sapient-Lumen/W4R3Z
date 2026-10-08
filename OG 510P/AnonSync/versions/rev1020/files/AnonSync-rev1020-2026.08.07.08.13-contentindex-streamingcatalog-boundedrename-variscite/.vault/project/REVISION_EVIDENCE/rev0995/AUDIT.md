# Rev0995 audit

Rev0995 removes a source-side repeated-work multiplier from content-defined ranged transfer. The authenticated source session now retains one cohesive bounded object containing exact payload identity, descriptor metadata, the canonical manifest, its digest, and one cumulative chunk-offset index. Valid continuation ranges reuse that index; source change discards it as one lifetime.

At the exact 4 TiB / 4 MiB / 8,192-chunk frontier, the former implementation admitted 8,589,934,592 redundant prefix additions and 68,727,865,344 bytes of avoidable offset-vector element traffic. Runtime and protocol regressions bind those arithmetic limits without allocating a multi-terabyte file. A stale manifest reference fails before source index lookup and before payload range copy.

This is a bounded source-side scale correction, not a completed multi-terabyte transfer. A 4 TiB file still requires 1,048,576 serialized range turns at the current 4 MiB frame. Bounded multi-range or byte-window framing remains the next delta-transfer frontier.
