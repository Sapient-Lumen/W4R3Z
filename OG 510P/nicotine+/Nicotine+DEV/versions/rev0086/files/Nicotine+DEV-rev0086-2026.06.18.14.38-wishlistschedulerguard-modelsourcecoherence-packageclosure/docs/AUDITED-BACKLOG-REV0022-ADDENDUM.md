# Audited backlog addendum — rev0022

## Completed in this revision

### TRANSFER-COMPLETE-LIFETIME-01 / U-269

**Decision:** source/probe support complete in rev0022; **not promoted** as a standalone strict report.

The rev0022 pytest witness confirms that an upload which has sent exactly its advertised byte count remains active until remote close or idle cleanup. It also confirms the stronger behavior: post-completion input bytes from the receiving peer are discarded after `FileOffset` has already been processed, but those bytes still refresh connection activity and prevent generic idle cleanup from firing. This preserves `_file_upload_msgs`, `_file_init_msgs`, `_total_uploads`, and the live F socket beyond the idle window.

This is a real availability/queue-fairness hardening item. It is not code execution, not file disclosure, and not stronger than the existing strict transfer-token candidate U-123. Public upload-completion/stuck/incorrect-stat issues overlap the symptom area, so the cube marks it as **candidate no direct exact public match found / public-adjacent**, not as clean novelty.

## Files added

```text
docs/TRANSFER-COMPLETE-LIFETIME-01-REV0022.md
docs/TRANSFER-COMPLETE-LIFETIME-COHERENCE-REFACTOR-REV0022.md
maintainer_artifacts/transfer-complete-lifetime-01/test_completed_upload_socket_lifetime_reproducer.py
maintainer_artifacts/transfer-complete-lifetime-01/README.md
report_drafts/TRANSFER-COMPLETE-LIFETIME-01-maintainer-hardening-skeleton.md
evidence/rev0022-transfer-complete-lifetime-pytest-run.txt
evidence/rev0022-transfer-complete-lifetime-source-trace.md
evidence/rev0022-web-public-overlap-transfer-complete-lifetime.md
data/rev0022_transfer_complete_lifetime_probe_summary.csv
data/rev0022_public_overlap_transfer_complete_lifetime.csv
data/rev0022_transfer_complete_lifetime_coherence_refactor.csv
data/rev0022_queue_delta.csv
data/rev0022_ranked_audit_queue.csv
data/rev0022_strict_promotions.csv
```

## Strict lane status

```text
strict report-candidates: 3
production-ready disclosure texts: 0
new strict promotions in rev0022: 0
```

## Next work

Move to **DOWNLOAD-INCOMPLETE-PROVENANCE-01**, led by U-226/U-230/U-250/U-253 with U-222/U-249 as nearby provenance/finalization checks. That family has a better chance of surfacing a stronger integrity/provenance consequence than more upload-slot policy work.
