# Web/public-overlap refresh — WMA-ASF-TINYSTEP-01 / U-273 — rev0030

Date: 2026-06-14 (America/New_York)

## Captured searches

- `Nicotine+ WMA ASF TinyTag object_size smaller than 24 parser CPU amplification`
- `site:github.com/nicotine-plus/nicotine-plus tinytag WMA ASF object_size 24`
- `tinytag WMA ASF object_size header_len 24 seek object_size - header_len`
- `TinyTag ASF object_size smaller than header parse loop WMA`
- `site:github.com/tinytag/tinytag issues ASF WMA object_size header_len`
- `site:github.com/tinytag/tinytag pull request ASF WMA object_size header_len`
- `site:github.com/tinytag/tinytag "object_size" "header_len" WMA`
- `site:github.com/tinytag/tinytag "WMA" "ParseError" "object_size"`
- `tinytag WMA parser object_size less than 24`
- `tinytag ASF parser malformed WMA size denial of service`
- `"fh.seek(object_size - header_len" "_Wma"`

## Public material found

- The current public TinyTag project describes TinyTag as an audio metadata reader and lists WMA among supported formats. This confirms the parser class is in a public/upstream component, but it is not itself an issue report.
  URL: https://pypi.org/project/tinytag/

- Public TinyTag source search results show the same broad WMA parser shape around `_Wma`, `header_len`, `object_size`, and `fh.seek(object_size - header_len, SEEK_CUR)`. This is source-shape overlap, not a public bug report.
  URL: https://github.com/tinytag/tinytag/blob/master/tinytag/tinytag.py

- GitHub Advisory Database entry GHSA-5v7r-6r5c-r473 / CVE-2026-31808 describes a different package (`file-type`) with an ASF/WMV/WMA parser infinite loop when an ASF sub-header size is zero and a negative skip moves the read position backwards. This is strong class adjacency. It is not a direct Nicotine+/TinyTag WMA `0 < object_size < 24` tiny-step report, and Nicotine+'s vendored parser already breaks on exactly zero.
  URL: https://github.com/advisories/GHSA-5v7r-6r5c-r473

- Nicotine+ issue #3458 reports broad system slowdown during startup rescanning on 3.3.10 and is closed `wontfix`. It is share-scanner/performance adjacent but does not identify WMA/ASF object-size parsing or malformed local media metadata.
  URL: https://github.com/nicotine-plus/nicotine-plus/issues/3458

- Nicotine+ 3.3.11 RC release notes include broad network-message hardening, but the public note is network-message scoped, not local/share-scanner media parser scoped.
  URL: https://nicotine-plus.org/NEWS.html

## Local public snapshot cross-check

The embedded rev0003 GitHub open-issue and open-PR snapshots were not a complete historical issue corpus. They did not provide a direct open issue/PR for:

```text
WMA
ASF
TinyTag
object_size
header_len
fh.seek(object_size - header_len)
```

The web pass found public class/source adjacency but no direct Nicotine+ issue/PR/advisory naming the U-273 root cause.

## Overlap decision

Classification: **candidate no-direct-public-found / public-source and ASF-parser-class adjacent**.

Reason:

```text
- Current source proof confirms the behavior in all archived Nicotine+ lanes.
- The exact Nicotine+/TinyTag nonzero-under-header tiny-step behavior was not found as a public issue/PR/advisory in captured searches.
- A different package has a public 2026 ASF parser zero-size/backwards-move advisory, so novelty must be framed conservatively as adjacent class overlap.
- The impact remains local/share-scanner parser work, not peer-only remote compromise.
- Therefore U-273 belongs in verified audited backlog, not the strict/front lane.
```
