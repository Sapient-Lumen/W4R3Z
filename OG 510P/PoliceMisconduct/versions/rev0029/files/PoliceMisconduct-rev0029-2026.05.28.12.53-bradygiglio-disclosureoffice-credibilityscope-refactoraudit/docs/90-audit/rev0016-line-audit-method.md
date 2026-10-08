# Rev0016 file and line audit method

Rev0016 inspected every file from the rev0015 source bundle.

For every UTF-8-readable file, it recorded:

- byte count;
- SHA-256 file hash;
- line count;
- nonempty line count;
- factor-module assignment;
- per-line SHA-256 digest truncated to 16 hex characters;
- high-risk line categories where a line matched claim/public/person/source-custody patterns.

The line digest index intentionally stores hashes rather than line content. It can help future sessions detect drift without making the audit file a second copy of the whole cube.

Audit surfaces:

- `data/audit/rev0016_file_line_audit.json`
- `data/audit/rev0016_line_digest_index.json`
- `data/audit/rev0016_line_flag_index.json`
