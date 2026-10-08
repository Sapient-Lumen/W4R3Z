# Audited backlog addendum — rev0030

## WMA-ASF-TINYSTEP-01 / U-273

Decision: **verified audited backlog; not strict-promoted**.

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

What was verified:

```text
Source trace:
  share scanning routes WMA metadata to TinyTag in all three archived lanes;
  WMA/ASF object-size validation rejects 0 and > filesize, but not nonzero
  object sizes smaller than the 24-byte object header.

Dynamic witness:
  object_size=8 produces overlapping/tiny-step object-loop starts and 127
  object-loop reads over a 1024-byte payload;
  object_size=24 produces normal non-overlapping starts and 43 loop reads.
```

Why backlog rather than strict:

```text
- local/share-scanner parser work, not peer-only protocol parsing;
- parser-step amplification rather than memory corruption or file disclosure;
- work remains bounded by file size and eventually reaches EOF;
- public source-shape and ASF parser-class adjacency require conservative
  novelty framing;
- lower value than U-123, PB-01, and SEARCH-RESP-01.
```

Suggested next target: **U-124 / Ogg continuation-packet accumulation**, unless queue re-scoring chooses a different compact media-parser row.
