# rev0032 public-overlap notes — MP4-M4A-ATOM-BUDGET-01 / U-125

Status: **candidate no-direct-public-found / public-source and MP4 parser-class adjacent**.

## Captured searches

```text
site:github.com/nicotine-plus/nicotine-plus MP4 M4A TinyTag atom memory duration parser
site:github.com/nicotine-plus/nicotine-plus mp4 m4a tinytag memory atom
TinyTag MP4 atom read memory DoS CVE
tinytag MP4 _traverse_atoms fh.read(atom_size)
site:github.com/tinytag/tinytag MP4 atom_size read memory issue
site:github.com/devsnd/tinytag MP4 atom_size memory DoS issue
site:github.com/devsnd/tinytag tinytag MP4 _traverse_atoms atom_size issue
site:github.com/nicotine-plus/nicotine-plus tinytag MP4 issue
site:github.com/nicotine-plus/nicotine-plus/issues m4a metadata scanning memory
site:github.com/nicotine-plus/nicotine-plus/issues mp4 metadata scanning memory
site:github.com/nicotine-plus/nicotine-plus/issues share scan mp4 m4a duration
site:github.com/nicotine-plus/nicotine-plus/issues TinyTag m4a
```

## Result

No direct public Nicotine+ issue/PR/advisory was found in the captured searches for the exact U-125 shape: share-scanner MP4/M4A duration traversal materializing a matching atom leaf through `fh.read(atom_size)` before fixed-prefix parsing.

Public adjacency was found:

```text
- TinyTag repository/source and PyPI/support pages describe MP4/M4A metadata support.
- Current TinyTag source exposes the same broad MP4 traversal idiom and MP4 parser surface.
- Public MP4 parser vulnerability history exists in other projects/classes, so novelty language should stay conservative.
- Nicotine+ public source exposes the share-scanner metadata route, but the captured searches did not identify a direct issue for this atom-leaf materialization behavior.
```

## Decision

```text
verified audited backlog;
not strict-promoted;
no production-ready disclosure text.
```
