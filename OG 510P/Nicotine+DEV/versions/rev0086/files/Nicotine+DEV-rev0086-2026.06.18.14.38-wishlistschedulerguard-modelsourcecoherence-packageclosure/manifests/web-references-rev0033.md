# Web references — rev0033

- RFC 9639 FLAC format — normative FLAC metadata/STREAMINFO format context; fixed-record invariant and metadata block header context, not a vulnerability report: https://www.rfc-editor.org/rfc/rfc9639.txt
- Xiph FLAC format overview — public FLAC format overview; STREAMINFO and metadata-block context, not a direct U-127 report: https://xiph.org/flac/documentation_format_overview.html
- TinyTag issue #12 — historical TinyTag FLAC duration bug; adjacent FLAC duration parser context, not advertised STREAMINFO block materialization: https://github.com/tinytag/tinytag/issues/12
- Nicotine+ issue #3384 — public Nicotine+ discussion mentioning FLAC/tinytag validation ideas; not direct malformed STREAMINFO block report: https://github.com/nicotine-plus/nicotine-plus/issues/3384
- CERT/CC VU#924114 dr_flac — broad FLAC parser/metadata DoS class in different library; not TinyTag or Nicotine+ U-127: https://www.kb.cert.org/vuls/id/924114
- FFmpeg FLAC streaminfo API docs — public parser-class reference to 34-byte STREAMINFO data; not a direct vulnerability overlap: https://www.ffmpeg.org/doxygen/0.6/flac_8h.html
