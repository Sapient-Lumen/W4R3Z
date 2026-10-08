# Scenario — index checksum and `pubtime` are authoritative while docs/public surface still lags

This scenario exists so **P-0477** does not flatten “Cargo can resolve the release now” and “all public surfaces have converged” into one fact.

The Cargo index format now documents `pubtime`, and the index JSON is intended to remain stable after insertion except for `yanked` changes.
At the same time, docs.rs says documentation builds are queued and may take a while after publish.

The receipt should therefore say that index checksum / `pubtime` are authoritative for release presence while docs visibility is still a lagging surface.
