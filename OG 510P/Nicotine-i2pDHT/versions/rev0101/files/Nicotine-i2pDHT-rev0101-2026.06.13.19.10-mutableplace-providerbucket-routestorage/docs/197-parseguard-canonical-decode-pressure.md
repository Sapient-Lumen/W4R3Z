# Parseguard canonical decode pressure

The cube has many signed bencoded objects.  Encoding tests prove little about inbound bytes.  A future network peer can send:

- nested lists intended to burn stack or CPU,
- huge byte strings,
- duplicate dictionary keys,
- unsorted dictionary keys,
- integers with ambiguous encodings,
- trailing data after a valid prefix,
- bytes that parse one way locally and another way elsewhere.

`parseguard.py` adds a deliberately strict bdecode surface for this cube's own wire fixtures.  It is not a full BitTorrent parser.  It is a safety wall for the baby DHT lab: bounded bytes, bounded depth, bounded item count, sorted keys, no duplicates, canonical re-encode check, and structured rejection kinds.

Design guess:

```text
Canonical parse failure should be observable pressure, not an exception lost under transport noise.
```

The first tests reject leading-zero integers, negative zero, leading-zero string lengths, unsorted dictionaries, duplicate keys, trailing data, deep nesting, and oversized input.
