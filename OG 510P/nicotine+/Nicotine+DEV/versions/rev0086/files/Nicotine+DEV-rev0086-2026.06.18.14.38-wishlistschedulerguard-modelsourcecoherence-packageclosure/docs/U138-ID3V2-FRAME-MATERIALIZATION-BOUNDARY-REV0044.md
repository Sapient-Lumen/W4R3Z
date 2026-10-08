# U-138 ID3v2 frame-materialization boundary — rev0044

## One-line result

**U-138 is demoted/archive-split, not strict-promoted.** The generic TinyTag tag-enabled ID3v2 parser can still materialize mapped text-frame bodies according to their advertised frame size, but the Nicotine+ MP3 share-scanner duration-only path does not exercise that mapped-frame body read.

## Why rev0044 worked this row

Rev0043 left a single explicit deferred local row:

```text
U-138 / general ID3v2 advertised-frame materialization
```

That row had become ambiguous after earlier media-parser work:

- rev0034 already captured FLAC files with a leading ID3v2 prelude in duration-only scanning as a separate row, **U-139**;
- the remaining broad U-138 row could either mean Nicotine+ share scanning of MP3 duration, or generic TinyTag tags-enabled ID3v2 parsing;
- the strict/front lane should not promote rows unless the current caller path, source trace, and witness all match the claimed production behavior.

Rev0044 therefore probes the boundary instead of assuming promotion.

## Boundary witness

New artifact:

```text
maintainer_artifacts/u138-id3v2-frame-materialization-01/test_id3v2_frame_materialization_boundary_reproducer.py
```

The witness creates synthetic MP3 streams with leading ID3v2.3 frames and a small MPEG frame tail. A tracking file object records reads and seeks.

The five assertions are:

1. `tags=False, duration=True` does not read a mapped `TIT2` frame body as one advertised allocation.
2. `tags=True, duration=False` does read the mapped `TIT2` body as `fh.read(frame_size)`.
3. The mapped text read scales with the advertised frame size.
4. A non-mapped `PRIV` frame is skipped with seek, not materialized.
5. A small `tags=True, duration=True` parse continues to produce title and duration.

## Rerun matrix

```text
github-tag-3.3.10:    5 passed
github-branch-3.3.x:  5 passed
github-branch-master: 5 passed
```

Full output:

```text
evidence/rev0044-u138-id3v2-boundary-rerun-matrix.txt
```

## Source trace summary

Nicotine+ share scanning requests duration only:

```text
shares.get_audio_tag(...)
  TinyTag parser for file
  load/_load(tags=False, duration=True, image=False)
```

For MP3/ID3:

- the load gate does not call `_parse_tag()` when `tags=False`;
- duration probing calls `_parse_id3v2_header()` to learn the leading tag size;
- duration probing then seeks to the byte position after ID3v2 before MPEG frame scanning;
- tag-enabled parsing still loops frames and reads mapped text payloads.

Full trace:

```text
evidence/rev0044-u138-id3v2-boundary-source-trace.md
```

## Decision

```text
old broad row: U-138 / general ID3v2 advertised-frame materialization
strict/front decision: not promoted
queue action: archived as boundary-demoted media-parser row
remaining hardening note: generic TinyTag tags=True mapped text frames still read advertised body sizes, but no strict Nicotine+ share-scanner caller was established in this revision
```

## Non-overlap with neighboring rows

Rev0044 keeps this boundary separate from:

- **U-139**: FLAC leading ID3v2 prelude duration-only behavior, already handled in rev0034;
- **U-127**: native FLAC STREAMINFO fixed-block validation, already handled in rev0033;
- **U-125**: MP4/M4A atom-leaf materialization, already handled in rev0032;
- **Ogg continuation accumulation**: already handled in rev0031;
- **SEARCH-RESP parser budgets**: network compressed response parser rows, promoted in rev0041/rev0042.

## Recommended next action

Prefer external review/filing of the seven production-gated strict packets already in the cube. If continuing internal cube work, use rev0044's boundary rule as a guard: do not promote parser rows unless the Nicotine+ caller path and advertised resource behavior match the exact packet claim.
