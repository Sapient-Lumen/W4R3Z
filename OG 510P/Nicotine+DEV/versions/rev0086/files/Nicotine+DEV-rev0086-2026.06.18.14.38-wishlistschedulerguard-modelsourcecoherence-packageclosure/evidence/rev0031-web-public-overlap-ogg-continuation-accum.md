# rev0031 web/public overlap — OGG-CONTINUATION-ACCUM-01 / U-124

Hard-search scope: targeted searches for direct Nicotine+/TinyTag Ogg continuation-packet accumulation reports, plus adjacent public parser and share-scanner material.

## Search result classification

```text
Direct Nicotine+ / TinyTag Ogg continuation packet accumulation advisory found: no, not in captured searches.
Direct Nicotine+ issue naming crafted Ogg continuation packet metadata parsing: no, not in captured searches.
Adjacent public material: yes.
```

## Adjacent material

- TinyTag is public source and publicly describes OGG support. This means the source shape is public, but public source is not the same as a filed vulnerability report.
- TinyTag's public changelog includes OGG maintenance such as “Stop reading after reaching EOS page” in 2.2.0. This is Ogg-parser adjacent, not a continuation-packet byte-budget match.
- TinyTag has a public 2026 advisory for a different parser sink: MP3 ID3v2 SYLT non-terminating loop in tinytag 2.2.0. This is media-parser DoS adjacent, but not Ogg continuation accumulation.
- The Ogg specification/design material explicitly allows packets to span pages and states that packets are not restricted to a maximum size. That makes the conservative fix shape a local metadata-scanner budget rather than a claim that the Ogg container is invalid.
- Nicotine+ 3.3.11 RC release notes mention maximum sizes for uncompressed network messages. That is network-message scoped and does not cover local/share-scanner Ogg metadata packet assembly.
- Nicotine+ issue #3458 is broad share-rescan slowdown/performance adjacent, but it does not identify Ogg continuation packets or TinyTag packet assembly as the cause.

## Working novelty language

Use conservative language:

```text
candidate no direct exact public match found in captured searches;
public source-shape, TinyTag media-parser advisory-class, Ogg-spec, and
share-rescan-performance adjacency exist;
not strict-promoted.
```

Avoid:

```text
- claiming a new CVE-ready vulnerability;
- presenting the Ogg spec's arbitrary packet span as inherently invalid;
- merging this with TinyTag's public ID3 SYLT advisory;
- merging this with Nicotine+'s network-message-size caps.
```

## References captured

```text
TinyTag repository / README: https://github.com/tinytag/tinytag
TinyTag GHSA-f4rq-2259-hv29: https://github.com/tinytag/tinytag/security/advisories/GHSA-f4rq-2259-hv29
Xiph Ogg framing: https://xiph.org/vorbis/doc/framing.html
RFC 3533 Ogg encapsulation: https://www.rfc-editor.org/rfc/rfc3533.html
libogg ogg_page docs: https://xiph.org/ogg/doc/libogg/ogg_page.html
Nicotine+ release notes: https://nicotine-plus.org/NEWS.html
Nicotine+ issue #3458: https://github.com/nicotine-plus/nicotine-plus/issues/3458
```
