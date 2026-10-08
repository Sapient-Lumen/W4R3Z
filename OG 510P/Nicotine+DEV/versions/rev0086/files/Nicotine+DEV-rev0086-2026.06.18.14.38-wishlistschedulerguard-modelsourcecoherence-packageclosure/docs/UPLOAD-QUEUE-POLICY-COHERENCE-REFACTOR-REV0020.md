# UPLOAD-QUEUE-POLICY coherence refactor — rev0020

The higher-order question in rev0020 was whether U-244 should merge into the existing transfer-control, queue-position, or transfer-size/provenance families.

## Refactor decision

```text
UPLOAD-QUEUE-POLICY-01 = U-244 as a verified audited-backlog lead.
No strict promotion in rev0020.
```

U-244 is not a duplicate of the neighboring queue/transfer rows.

## Relationship to nearby rows

### U-271 / U-274 / U-47 — transfer-control string budget

These rows concern virtual-path decode, semantic path caps, lookup/logging/echo costs, and repeated queue-position request work. U-244 assumes the requested virtual path resolves to a shared file and focuses on candidate file size being excluded from megabyte-cap admission.

Keep separate.

### U-166 — queue-position response provenance

U-166 is download-side visible queue-position state. U-244 is upload-side queue admission. They share queue terminology but not a root cause.

Keep separate.

### U-69 / U-107 / U-198 — transfer size/provenance

U-69 is download-side peer-declared size. U-107/U-198 are upload send/read/opened-file provenance. U-244 is earlier: admission to the upload queue using the locally shared-file candidate size.

Keep separate, but a coherent upload-policy patch should avoid creating contradictory size semantics between queue admission, TransferRequest advertised size, and F-connection send clamps.

### U-251 — upload EOF lifecycle

U-251 is runtime send-loop behavior after an upload has started. U-244 is queue admission before a file is selected for upload.

Keep separate.

## Anti-regression guidance

A safe queue-policy fix should preserve these properties together:

```text
- preserve current file-count limit behavior unless intentionally changed;
- preserve buddy/friend no-limit exemptions;
- preserve modern QueueUpload and legacy TransferRequest compatibility;
- do not start blocking active uploads based on queued-byte caps unless explicitly intended;
- decide whether a single file larger than the cap should be denied, allowed once, or allowed only for privileged users;
- keep denial reasons consistent with existing `Too many megabytes` protocol reason.
```

## Cluster state after rev0020

```text
UPLOAD-QUEUE-POLICY-01:
  U-244 is now verified and separate.

TRANSFER-CONTROL-STRING-BUDGET:
  U-271 + U-274 + U-47 remain separate lower-value hardening work.

TR-STATUS-01:
  U-166 remains separate.

TRANSFER-SIZE-PROVENANCE-01:
  U-69 + U-107 + U-198 remain verified audited backlog.

TRANSFER-EOF-01:
  U-251 remains verified audited backlog.

SHARE-SCAN-CACHE-PROVENANCE:
  U-248 is next queued target.
```
