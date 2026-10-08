# Audited backlog addendum — rev0034

## Packet completed

**FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 / U-139** was verified and retained outside the strict/front lane.

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

## Decision

```text
verified audited backlog;
known/upstream-adjacent;
master partially fixes mapped-frame application/materialization;
not strict-promoted;
not production-ready disclosure text.
```

## Why it did not promote

```text
- Local/share-scanner media metadata parsing rather than inbound peer protocol
  message handling.
- Stable and 3.3.x behavior is real, but master no longer applies mapped ID3v2
  text fields when tags=False and avoids the full mapped-frame body read in the
  witness.
- Public TinyTag history includes FLAC files with ID3 headers, disabled tag
  parsing, FLAC applying ID3 tags after Vorbis, and ID3 parsing optimizations;
  this makes novelty weak even though no direct Nicotine+ exact issue was
  captured.
- The witness does not prove memory corruption or code execution.
- The strict/front lane remains stronger: U-123, PB-01, and SEARCH-RESP-01.
```

## Files added

```text
docs/FLAC-LEADING-ID3V2-DURATION-PRELUDE-01-REV0034.md
docs/FLAC-ID3V2-PRELUDE-COHERENCE-REFACTOR-REV0034.md
maintainer_artifacts/flac-leading-id3v2-duration-prelude-01/README.md
maintainer_artifacts/flac-leading-id3v2-duration-prelude-01/test_flac_leading_id3v2_duration_prelude_reproducer.py
report_drafts/FLAC-LEADING-ID3V2-DURATION-PRELUDE-01-maintainer-hardening-skeleton.md
evidence/rev0034-flac-leading-id3v2-duration-prelude-pytest-run.txt
evidence/rev0034-flac-leading-id3v2-duration-prelude-helper-rerun.txt
evidence/rev0034-flac-leading-id3v2-duration-prelude-source-trace.md
evidence/rev0034-flac-leading-id3v2-duration-prelude-source-trace.json
evidence/rev0034-flac-leading-id3v2-duration-prelude-behavior.json
evidence/rev0034-web-public-overlap-flac-leading-id3v2-prelude.md
data/rev0034_flac_leading_id3v2_prelude_probe_summary.csv/json
data/rev0034_flac_leading_id3v2_prelude_source_trace.csv/json
data/rev0034_public_overlap_flac_leading_id3v2_prelude.csv/json
data/rev0034_flac_leading_id3v2_prelude_coherence_refactor.csv/json
data/rev0034_queue_delta.csv/json
data/rev0034_ranked_audit_queue.csv/json
data/rev0034_strict_promotions.csv/json
```

## Queue movement

The next suggested action is to re-score the strict/front lane before taking another low-value media-parser row. If the session remains inside the media-parser cluster, U-138 is the adjacent ID3v2 frame row, but its public novelty is weak.
