# rev0044 audit/refactor — ID3v2 media-parser coherence split

## Purpose

The requested audit/refactor pass focuses on the last explicit deferred local row, **U-138**, and prevents it from absorbing unrelated media-parser rows.

## Refactor result

| Row | Rev0044 disposition | Reason |
| --- | --- | --- |
| U-138 broad share-scanner ID3v2 mapped-frame materialization | Demoted / archived | MP3 share scanner uses `tags=False, duration=True`; witness shows no mapped body read on all three lanes. |
| Generic TinyTag tags-enabled mapped ID3v2 frame materialization | Backlog note only | Real parser behavior exists with `tags=True`, but no strict/front Nicotine+ share-scanner caller was established. |
| U-139 FLAC leading-ID3v2 duration prelude | Separate completed row | FLAC leading-ID3v2 behavior was captured in rev0034 and must not be merged into U-138. |
| U-127 FLAC STREAMINFO fixed block | Separate completed row | Native FLAC metadata-block validation is fixed-length STREAMINFO work, not generic ID3v2 frame parsing. |
| U-125 MP4 atom materialization | Separate completed row | Atom leaf materialization is container-specific and unrelated to ID3v2 frame mapping. |
| SEARCH-RESP parser budgets | Separate strict/front rows | Network compressed response parsing, not local media tag parsing. |

## Boundary rule added to the cube

A media-parser row must name both:

1. the **caller mode** (`tags=False/duration=True`, `tags=True`, image enabled, etc.); and
2. the **materialized object** (frame payload, atom payload, metadata block, result-list body, packet accumulator, etc.).

Without both, the row remains backlog-only.

## Queue impact

The internal queue no longer presents U-138 as the next likely strict/front promotion. The queue now prefers external review/filing of the seven production-gated strict packets or a new source-refresh discovery pass.

## Coherence-map delta

```text
before rev0044:
  U-138 = deferred general ID3v2 advertised-frame materialization

after rev0044:
  U-138 = archived boundary-demoted row
  U-138-GENERIC-TAGS = parser-hardening backlog note, not strict/front
```
