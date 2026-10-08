# Audited backlog addendum — rev0032

## Packet completed

**MP4-M4A-ATOM-BUDGET-01 / U-125** was verified and retained outside the strict/front lane.

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Decision

```text
verified audited backlog;
not strict-promoted;
not production-ready disclosure text.
```

## Why it did not promote

```text
- Local/share-scanner media metadata parsing rather than inbound peer protocol
  message handling.
- The witness demonstrates bytes-object materialization proportional to an MP4
  atom's advertised payload length, not memory corruption or code execution.
- Large MP4 atoms may be legitimate; the maintainable fix shape is a local
  metadata budget or fixed-prefix streaming parser rather than blanket rejection.
- Public adjacency exists in TinyTag source/support and general MP4 parser
  hardening history; captured searches did not find a direct Nicotine+ U-125
  public issue.
- The strict/front lane remains stronger: U-123, PB-01, and SEARCH-RESP-01.
```

## Files added

```text
docs/MP4-M4A-ATOM-BUDGET-01-REV0032.md
docs/MP4-M4A-ATOM-BUDGET-COHERENCE-REFACTOR-REV0032.md
maintainer_artifacts/mp4-m4a-atom-budget-01/README.md
maintainer_artifacts/mp4-m4a-atom-budget-01/test_mp4_m4a_atom_budget_reproducer.py
report_drafts/MP4-M4A-ATOM-BUDGET-01-maintainer-hardening-skeleton.md
evidence/rev0032-mp4-m4a-atom-budget-pytest-run.txt
evidence/rev0032-mp4-m4a-atom-budget-helper-rerun.txt
evidence/rev0032-mp4-m4a-atom-budget-source-trace.md
evidence/rev0032-mp4-m4a-atom-budget-source-trace.json
evidence/rev0032-web-public-overlap-mp4-m4a-atom-budget.md
data/rev0032_mp4_m4a_atom_budget_probe_summary.csv/json
data/rev0032_public_overlap_mp4_m4a_atom_budget.csv/json
data/rev0032_mp4_m4a_atom_budget_coherence_refactor.csv/json
data/rev0032_queue_delta.csv/json
data/rev0032_ranked_audit_queue.csv/json
data/rev0032_strict_promotions.csv/json
```

## Queue movement

The next local media-parser target is **U-127 / FLAC STREAMINFO block validation**, unless a source refresh or strict-lane re-score moves the session back to a higher-value peer/protocol binding candidate.
