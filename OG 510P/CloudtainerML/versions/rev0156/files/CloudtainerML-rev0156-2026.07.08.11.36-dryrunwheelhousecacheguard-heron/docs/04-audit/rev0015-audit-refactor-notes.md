# rev0015 audit/refactor notes

- Added a native probe index so C++ probes have a reentry map separate from compile receipts.
- Refactored smoke validation away from a massive static historical required-file list toward core structure + current revision artifacts + manifest validation.
- Kept the source-only native policy: binaries are compiled in temp directories and not shipped.
- Updated ledgers, cell notes, datacube CSV, and revision metadata for rev0015.
