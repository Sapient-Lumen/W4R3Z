# Native re-entry journal

The re-entry journal turns a preflight route into restart memory. It carries preflight and oracle-seal digests, artifact/source/fallback/oracle digests, loader id, and fallback/tombstone/quarantine/crash memory flags.

The journal exists because restart is a protocol boundary. Without it, a relaunch candidate could be rediscovered as fresh after restart and skip the exact-boundary checks that made it safe only as a route-to-load-gate marker.
