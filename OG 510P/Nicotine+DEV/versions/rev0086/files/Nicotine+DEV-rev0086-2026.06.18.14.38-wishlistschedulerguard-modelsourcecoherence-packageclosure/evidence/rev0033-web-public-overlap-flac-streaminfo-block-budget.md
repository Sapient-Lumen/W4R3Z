# rev0033 public-overlap notes — FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127

Status: **candidate no-direct-public-found / public FLAC-spec and parser-class adjacent**.

## Captured searches

```text
Nicotine+ FLAC STREAMINFO advertised block size tinytag issue
site:github.com/nicotine-plus/nicotine-plus FLAC STREAMINFO TinyTag
TinyTag FLAC STREAMINFO block size 34 issue
tinytag flac streaminfo read size vulnerability
xiph FLAC format streaminfo metadata block 34 bytes
FLAC format streaminfo 34 bytes metadata block
```

## Result

No direct public Nicotine+ issue/PR/advisory was found in the captured searches for the exact U-127 shape: share-scanner FLAC duration parsing materializing an advertised STREAMINFO metadata-block payload with `fh.read(size)` before validating or bounding the fixed 34-byte STREAMINFO record.

Public adjacency was found:

```text
- RFC 9639 and Xiph documentation describe the FLAC metadata-block structure and
  STREAMINFO context. This supports the fixed-record invariant but is not a
  vulnerability report.
- TinyTag has public historical FLAC duration-parser bug discussion, but the
  captured issue is not an advertised STREAMINFO block-size materialization bug.
- Nicotine+ public discussion mentions possible FLAC validation/checksum work
  through tinytag, but not this malformed STREAMINFO current behavior.
- Public parser-class FLAC hardening/DoS examples exist in other projects and
  libraries, so novelty language should stay conservative.
```

## Decision

```text
verified audited backlog;
not strict-promoted;
no production-ready disclosure text.
```
