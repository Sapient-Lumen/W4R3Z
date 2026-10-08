# rev0029 web references

- Soulseek Protocol Documentation | Nicotine+ — https://nicotine-plus.org/doc/SLSKPROTOCOL.html — public protocol context for SharedFileListResponse, FileSearchResponse, FolderContentsResponse, and file-attribute count/value pairs.
- Nicotine+ Release Notes — https://nicotine-plus.org/NEWS.html — 3.3.11 RC broad uncompressed network-message-size hardening adjacency.
- Nicotine+ issue #2688 — https://github.com/nicotine-plus/nicotine-plus/issues/2688 — file-attributes public-adjacent issue; not an exact semantic-count cap report.
- Nicotine+ issue #2415 — https://github.com/nicotine-plus/nicotine-plus/issues/2415 — search-result/file-properties public-adjacent crash; not an exact semantic-count cap report.
- GitHub issue search: `"unpack_file_attributes"` — no direct exact issue/PR result found in captured searches.
- GitHub issue search: `"FileSearchResponse" "uncompressed" "128 MiB"` — broad uncompressed-message adjacency only in captured searches.
- GitHub issue search: `"file attributes" "FileSearchResponse"` — attribute UI/protocol adjacency only in captured searches.

# rev0030 web references

- TinyTag on PyPI — https://pypi.org/project/tinytag/ — public upstream context: TinyTag is an audio metadata reader and supports WMA.
- TinyTag public source — https://github.com/tinytag/tinytag/blob/master/tinytag/tinytag.py — public source-shape adjacency for the WMA parser and `object_size - header_len` seek pattern; not a public bug report.
- GitHub Advisory Database GHSA-5v7r-6r5c-r473 / CVE-2026-31808 — https://github.com/advisories/GHSA-5v7r-6r5c-r473 — ASF parser zero-size/backwards-move infinite-loop class adjacency in a different package.
- Nicotine+ issue #3458 — https://github.com/nicotine-plus/nicotine-plus/issues/3458 — broad share-rescan slowdown report; not an exact WMA/ASF malformed-object-size report.
- Nicotine+ Release Notes — https://nicotine-plus.org/NEWS.html — broad 3.3.11 RC hardening context; not local media-parser scoped.
- GitHub issue search: `site:github.com/nicotine-plus/nicotine-plus tinytag WMA ASF object_size 24` — no direct exact issue/PR result found in captured searches.
- GitHub issue search: `site:github.com/tinytag/tinytag issues ASF WMA object_size header_len` — no direct exact issue/PR result found in captured searches.

# Web references — rev0031

- TinyTag repository / README — public source and feature/support context for OGG metadata parsing: https://github.com/tinytag/tinytag
- TinyTag GHSA-f4rq-2259-hv29 — public adjacent parser-DoS advisory for ID3v2 SYLT, not direct Ogg overlap: https://github.com/tinytag/tinytag/security/advisories/GHSA-f4rq-2259-hv29
- Xiph Ogg logical bitstream framing — lacing values and page-spanning packet design: https://xiph.org/vorbis/doc/framing.html
- RFC 3533 — Ogg encapsulation format, lacing values and continued packets: https://www.rfc-editor.org/rfc/rfc3533.html
- libogg ogg_page documentation — maximum page body is under 64 KiB and packets can span pages: https://xiph.org/ogg/doc/libogg/ogg_page.html
- Nicotine+ release notes — 3.3.11 RC network-message hardening context: https://nicotine-plus.org/NEWS.html
- Nicotine+ issue #3458 — broad share-rescan slowdown/performance adjacency: https://github.com/nicotine-plus/nicotine-plus/issues/3458

# Web references — rev0033

- RFC 9639 FLAC format — https://www.rfc-editor.org/rfc/rfc9639.txt — normative FLAC metadata/STREAMINFO format context; fixed-record invariant and metadata block header context, not a vulnerability report
- Xiph FLAC format overview — https://xiph.org/flac/documentation_format_overview.html — public FLAC format overview; STREAMINFO and metadata-block context, not a direct U-127 report
- TinyTag issue #12 — https://github.com/tinytag/tinytag/issues/12 — historical TinyTag FLAC duration bug; adjacent FLAC duration parser context, not advertised STREAMINFO block materialization
- Nicotine+ issue #3384 — https://github.com/nicotine-plus/nicotine-plus/issues/3384 — public Nicotine+ discussion mentioning FLAC/tinytag validation ideas; not direct malformed STREAMINFO block report
- CERT/CC VU#924114 dr_flac — https://www.kb.cert.org/vuls/id/924114 — broad FLAC parser/metadata DoS class in different library; not TinyTag or Nicotine+ U-127
- FFmpeg FLAC streaminfo API docs — https://www.ffmpeg.org/doxygen/0.6/flac_8h.html — public parser-class reference to 34-byte STREAMINFO data; not a direct vulnerability overlap


## rev0034

- TinyTag README release history — public upstream TinyTag context: FLAC with ID3 header support, disable-tag-parsing history, FLAC applies ID3 tags after Vorbis, and later ID3 decoding optimizations; adjacent/known-class, not a direct Nicotine+ U-139 report: https://github.com/tinytag/tinytag/blob/master/README.md
- Nicotine+ release notes — current Nicotine+ release/public-fix context; no captured direct FLAC leading-ID3 duration-only issue in release notes search: https://nicotine-plus.org/NEWS.html
- Nicotine+ homepage — public project/version context; not a direct overlap: https://nicotine-plus.org/
- dhowden/tag issue #58 — cross-project public context that FLAC files with prepended ID3v2 tags are a known interoperability/parser shape; not TinyTag/Nicotine+ U-139: https://github.com/dhowden/tag/issues/58
- Mp3tag FLAC ID3v2 forum discussions — general user-visible FLAC-with-ID3v2 tag adjacency; not a vulnerability or Nicotine+ direct report: https://community.mp3tag.de/t/tags-flac-flac-and-flac-flac-id3v2/14381


## rev0034

- TinyTag README release history — public upstream TinyTag context: FLAC with ID3 header support, disable-tag-parsing history, FLAC applies ID3 tags after Vorbis, and later ID3 decoding optimizations; adjacent/known-class, not a direct Nicotine+ U-139 report: https://github.com/tinytag/tinytag/blob/master/README.md
- Nicotine+ release notes — current Nicotine+ release/public-fix context; no captured direct FLAC leading-ID3 duration-only issue in release notes search: https://nicotine-plus.org/NEWS.html
- Nicotine+ homepage — public project/version context; not a direct overlap: https://nicotine-plus.org/
- dhowden/tag issue #58 — cross-project public context that FLAC files with prepended ID3v2 tags are a known interoperability/parser shape; not TinyTag/Nicotine+ U-139: https://github.com/dhowden/tag/issues/58
- Mp3tag FLAC ID3v2 forum discussions — general user-visible FLAC-with-ID3v2 tag adjacency; not a vulnerability or Nicotine+ direct report: https://community.mp3tag.de/t/tags-flac-flac-and-flac-flac-id3v2/14381


## rev0034

- TinyTag README release history — public upstream TinyTag context: FLAC with ID3 header support, disable-tag-parsing history, FLAC applies ID3 tags after Vorbis, and later ID3 decoding optimizations; adjacent/known-class, not a direct Nicotine+ U-139 report: https://github.com/tinytag/tinytag/blob/master/README.md
- Nicotine+ release notes — current Nicotine+ release/public-fix context; no captured direct FLAC leading-ID3 duration-only issue in release notes search: https://nicotine-plus.org/NEWS.html
- Nicotine+ homepage — public project/version context; not a direct overlap: https://nicotine-plus.org/
- dhowden/tag issue #58 — cross-project public context that FLAC files with prepended ID3v2 tags are a known interoperability/parser shape; not TinyTag/Nicotine+ U-139: https://github.com/dhowden/tag/issues/58
- Mp3tag FLAC ID3v2 forum discussions — general user-visible FLAC-with-ID3v2 tag adjacency; not a vulnerability or Nicotine+ direct report: https://community.mp3tag.de/t/tags-flac-flac-and-flac-flac-id3v2/14381
