# rev0870 — hash-oracle byte recovery and coverage-snapshot hardening

## Result

This revision restores **four exact canonical OCF source files totaling 53 bytes**. Each candidate is admitted only because its complete byte string matches the path-specific size and SHA-256 already fixed by `INDEX/files.csv`.

| Canonical path | Exact bytes | Size | SHA-256 |
|---|---:|---:|---|
| `sources/ocf_llm/examples/discovery_sdt_demo_v247/output.txt` | `hello SDT\n` | 10 | `836b37c417b56c8dfd8bf9d04f3e3e5068c73bb5949810d39501abcc5d253322` |
| `sources/ocf_llm/examples/dsc_summary_v1.json` | `{"n":64,"x":0}` | 14 | `083e790596b55d0b157e77ac222fe3f36c8b2c27f4365582f77bb2d2a40c4eee` |
| `sources/ocf_llm/examples/dsc_buc_summary_v1.json` | `{"n":64,"x":0}` | 14 | `083e790596b55d0b157e77ac222fe3f36c8b2c27f4365582f77bb2d2a40c4eee` |
| `sources/ocf_llm/examples/dsc_cbb_summary_v1.json` | `{"n":128,"x":0}` | 15 | `7f6e4595bed3392fb68b355ed50ba2f86823e5563e124c60eaaa187daac0c45a` |

The DSC values are reconstructed from surviving resolver-trace values (`suiteCount`, `n_actual`, and `x_actual`) and compact JSON serialization. The SDT output is a bounded semantic candidate. In every case, the decisive evidence is full size-and-digest equality—not plausibility or filename inference.

## Coverage movement

| Metric | rev0869 | rev0870 | Change |
|---|---:|---:|---:|
| Exact files at canonical paths | 103 | 107 | +4 |
| Exact bytes at canonical paths | 4,885,343 | 4,885,396 | +53 |
| Exact canonical source files | 16 | 20 | +4 |
| Rehydratable files including recovery objects | 119 | 123 | +4 |
| Unavailable files | 4,467 | 4,463 | −4 |
| Unavailable bytes | 101,448,546 | 101,448,493 | −53 |

The 17 present-path mismatches are unchanged; 16 remain protected by historical recovery objects and root `README.md` remains the sole unresolved mismatch.

## Search avenue closed

The index contains **270 duplicate size/SHA-256 identity groups covering 730 paths**. A live comparison against exact canonical files and content-addressed recovery objects found **zero unresolved paths whose exact identity is already available elsewhere**. This means duplicate-hash copying is exhausted for the current cube. It should not consume another session unless new bytes are mounted.

There remain **497 unresolved files of at most 256 bytes, totaling 47,085 bytes**. That is the most promising internal regeneration frontier, but candidates must come from surviving traces, generators, or protocol structure and pass exact path-specific hashes. Filenames alone are not evidence.

## Severe coverage-reader defect corrected

`canonical_coverage.py` feeds the primary overlay gate, but the inherited implementation separated:

1. a symlink/path precheck,
2. a pathname `stat`, and
3. a later pathname open/hash.

A file could therefore be replaced or mutated between those operations, allowing a coverage decision to combine metadata and bytes from different states. The inherited root check also resolved the path before testing `is_symlink`, which made that explicit test ineffective for a symlink root alias.

rev0870 replaces that trust path with descriptor-bound snapshots. A direct regression in this cloudtainer also showed that opening a directory symlink with `O_DIRECTORY | O_NOFOLLOW` could still return a directory descriptor. The implementation therefore does not treat the flag as sufficient:

- reject symlink components in the supplied root before resolution;
- inspect every relative component with no-follow metadata before and after opening it;
- require both metadata observations and the opened descriptor to name the same device, inode, and file type;
- require a regular file descriptor;
- compare device, inode, mode, link count, size, `mtime`, and `ctime` before and after reading;
- reopen the path through a fresh no-follow walk and require the same identity;
- parse `INDEX/files.csv` and the recovery inventory only from captured stable bytes;
- reject duplicate CSV columns and surplus unnamed cells.

The validator deterministically mutates a file after the first hash chunk in two ways: same-size pathname replacement and same-inode in-place modification. Both must fail. A stable file must still hash correctly.

The active gate also stops recursively running the complete rev0869 builder/reproducibility suite on every invocation. That historical suite took about 32 seconds and did not exercise rev0870 changed code. rev0870 keeps the inherited exact-byte assertions and the demonstrated local-header Unicode-path exploit regression in the live validator; the complete rev0869 suite is run once during release validation, alongside two deterministic builds and validation of the actual final ZIP.

## Recovery tool

`scripts/recover_indexed_low_entropy_constants_rev0870.py` is deliberately narrow. With no arguments it verifies all four live files. `--write` creates only absent recipe paths, never overwrites existing content, rejects symlinked parent traversal, and re-verifies the result against the canonical index. Its overwrite regression exposed and corrected a serious first-draft cleanup error: after `O_EXCL` refused an existing target, exception cleanup could unlink that pre-existing file. Cleanup is now conditional on this invocation having actually created the file, and the regression verifies the original bytes survive refusal.

```bash
python3 scripts/recover_indexed_low_entropy_constants_rev0870.py
python3 scripts/recover_indexed_low_entropy_constants_rev0870.py --json
```

## Remaining priority

The largest risks are still external-decision or missing-byte problems: owner-approved rights closure, the 17 StreamFold payloads, and the canonical root README. This revision does not obscure those blockers. It removes four real byte gaps and hardens the metric used to measure every later recovery.
