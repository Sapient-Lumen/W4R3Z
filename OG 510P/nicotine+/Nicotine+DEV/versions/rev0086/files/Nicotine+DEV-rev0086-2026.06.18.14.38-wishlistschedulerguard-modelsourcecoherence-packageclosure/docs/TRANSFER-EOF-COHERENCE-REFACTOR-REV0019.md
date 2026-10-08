# TRANSFER-EOF coherence refactor — rev0019

The higher-order question in this pass was whether U-251 should merge into rev0018's TRANSFER-SIZE-PROVENANCE packet or become a separate lead.

## Refactor decision

```text
TRANSFER-EOF-01 = U-251 as a verified audited-backlog lead.
No strict promotion in rev0019.
```

U-251 is adjacent to U-69/U-107/U-198, but it is not identical.

## Relationship to rev0018

### U-107 — upload read clamp

U-107 says the sender can read more bytes than the advertised remaining transfer size. U-251 says the upload lifecycle has no coherent terminal state when the opened file supplies too few bytes or when sentbytes overshoots the exact advertised size.

These should be fixed together, but not double-counted as the same finding.

### U-198 — opened-file provenance

U-198 can create the mismatch: the upload may be authorized using one path state and later open a different file at F-init. U-251 is the sender's reaction after such a mismatch becomes visible in the read loop.

### U-69 — download-side size provenance

U-69 remains download-side. It shares the broad “advertised transfer size” theme, but not the upload read/EOF root.

### U-269 — upload-complete socket lifetime

U-269 assumes the advertised bytes were sent. U-251 covers cases where the sender sends fewer bytes, sends too many bytes, or does not know how to terminate after the local file cannot supply exactly the advertised count.

## Anti-regression guidance

A safe transfer-send fix needs these properties together:

```text
- do not send beyond advertised remaining bytes;
- do not wait for remote close/idle timeout after stable EOF before advertised size;
- do not leave sentbytes > size outside completion/error handling;
- do not break ordinary offset/resume behavior;
- make any growing-file grace policy explicit, bounded, and test-covered.
```

## Cluster state after rev0019

```text
TRANSFER-SIZE-PROVENANCE-01:
  U-69 + U-107 + U-198 remain verified audited-backlog packet.

TRANSFER-EOF-01:
  U-251 is now verified and separate.

TRANSFER-COMPLETE-LIFETIME:
  U-269 remains separate.

UPLOAD-QUEUE-POLICY:
  U-244 is next queued target.
```
