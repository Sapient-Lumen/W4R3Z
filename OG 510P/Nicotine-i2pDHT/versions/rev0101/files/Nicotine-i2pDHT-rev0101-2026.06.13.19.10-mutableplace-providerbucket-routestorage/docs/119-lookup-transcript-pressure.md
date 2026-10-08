# Lookup transcript pressure

`lookuptranscript.py` creates a transport-neutral local evidence object:

```text
LookupTranscript
  lookup_id
  kind
  target
  events[]
```

Events record path id, family id, node id, event kind, timing, payload digest, and a short note.  The transcript digest is deterministic so a weird lookup can be preserved, shared in tests, or replayed by future audit tools.

## Pressure checks

`analyze_lookup_pressure()` currently checks:

- success-family count;
- success-path count;
- captured fast-window fraction;
- timeout fraction;
- bad-response count;
- whether the lookup kind is evidence-only.

The critical behavior is fast-window quarantine:

```text
If the earliest replies are dominated by one family, do not accept merely because the full candidate set looked diverse later.
```

This keeps the cube aligned with the disjoint-path instinct: speed is useful only after the path-family surface is not obviously captured.

## Nonclaim

A lookup transcript is not the DHT wire format.  It is a local reasoning format that can later be filled by SAM Streaming, datagrams, a fake transport, or recorded tests.
