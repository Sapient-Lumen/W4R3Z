# Web/public-overlap notes — rev0034 U-139

Searches captured for rev0034 did not identify a direct public Nicotine+ issue matching the exact U-139 shape: “share-scanner duration-only FLAC metadata scan parses/applies leading ID3v2 text frames in stable/3.3.x lanes.”

The overlap classification is nevertheless conservative because public TinyTag history explicitly includes FLAC files with ID3 headers, disabled tag parsing, FLAC applying ID3 tags after Vorbis, and ID3 parsing optimizations. General audio-tooling discussions also treat ID3v2-in-FLAC as a known interoperability shape.

## References recorded

- TinyTag README release history — public upstream TinyTag context: FLAC with ID3 header support, disable-tag-parsing history, FLAC applies ID3 tags after Vorbis, and later ID3 decoding optimizations; adjacent/known-class, not a direct Nicotine+ U-139 report: https://github.com/tinytag/tinytag/blob/master/README.md
- Nicotine+ release notes — current Nicotine+ release/public-fix context; no captured direct FLAC leading-ID3 duration-only issue in release notes search: https://nicotine-plus.org/NEWS.html
- Nicotine+ homepage — public project/version context; not a direct overlap: https://nicotine-plus.org/
- dhowden/tag issue #58 — cross-project public context that FLAC files with prepended ID3v2 tags are a known interoperability/parser shape; not TinyTag/Nicotine+ U-139: https://github.com/dhowden/tag/issues/58
- Mp3tag FLAC ID3v2 forum discussions — general user-visible FLAC-with-ID3v2 tag adjacency; not a vulnerability or Nicotine+ direct report: https://community.mp3tag.de/t/tags-flac-flac-and-flac-flac-id3v2/14381

## Classification

```text
known/upstream-adjacent parser-class overlap;
stable/3.3.x current-behavior witness retained as local hardening backlog;
master lane partially fixes the tag-field materialization/application shape;
not strict-promoted.
```
