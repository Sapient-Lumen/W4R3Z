# rev0022 transfer-complete-lifetime coherence refactor

This pass reduces overlap in the transfer lifecycle area rather than creating a new pile of near-duplicate reports.

## Canonical family

```text
TRANSFER-COMPLETE-LIFETIME-01 / U-269
  Completed advertised-size uploads remain active until remote close or idle cleanup;
  post-completion peer input can refresh activity and retain the upload slot.
```

U-269 is now the canonical row for this exact root.

## Kept separate on purpose

```text
U-123 / TR-01 strict candidate
  Duplicate peer-supplied download token + stale timer + F-session orphaning.
  Different root: active-transfer map identity and stale timer deletion.

U-251 / TRANSFER-EOF-01
  EOF before advertised size and short/growing/replaced local file behavior.
  Different root: local file cannot provide advertised bytes.

U-107 / TRANSFER-SIZE-PROVENANCE-01
  Upload reads are not clamped to remaining advertised size.
  Companion fix, but not a duplicate: read clamp prevents overshoot, while U-269 concerns completion retirement after advertised bytes have been sent.

U-198 / TRANSFER-SIZE-PROVENANCE-01
  Path/opened-file provenance can create stale advertised-size mismatch.
  Input condition, not the completed-socket lifetime root.

U-152
  Upload read-ahead / instantaneous drain sizing.
  Performance/pacing family; not completion retirement.

U-170
  Unknown-token FileTransferInit close/backport behavior.
  Admission/unknown-token behavior; U-269 occurs after a valid accepted upload.
```

## Combined fix strategy

The transfer-lifecycle fixes should not be separate ad hoc edits. A coherent patchset would define one upload send-state invariant:

```text
- opened file is bound/revalidated at F-init where feasible;
- reads never exceed remaining advertised size;
- EOF before advertised size is explicit error/retry/short-file state;
- `>= advertised size` is local completion, not merely progress;
- completed upload is retired or moved to a bounded drain state independent of peer liveness;
- close handlers remain idempotent and do not double-finish or requeue completed transfers.
```

## Practical ordering

```text
1. U-107 read clamp and `>= size` completion semantics.
2. U-251 short-read/EOF explicit terminal handling.
3. U-269 local completion retire/drain close behavior.
4. U-198 opened-file provenance check if maintainers accept the local/sync race boundary.
```

This is why U-269 is not promoted strict even though the new rev0022 proof is stronger than rev0009. It is best as part of a transfer-lifecycle regression suite.
