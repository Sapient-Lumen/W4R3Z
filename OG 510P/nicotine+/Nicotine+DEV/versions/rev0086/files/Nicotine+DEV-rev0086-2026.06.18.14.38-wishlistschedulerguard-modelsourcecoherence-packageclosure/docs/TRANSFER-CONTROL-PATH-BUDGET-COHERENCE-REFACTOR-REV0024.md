# TRANSFER-CONTROL-PATH-BUDGET coherence refactor — rev0024

rev0024 deliberately **reduced** the number of standalone claims.

## Canonical packet

**TRANSFER-CONTROL-PATH-BUDGET-01** is the coherent packet. It contains:

```text
U-271 — QueueUpload and legacy TransferRequest virtual-path parser/handler budget.
U-274 — PlaceInQueueRequest lookup and PlaceInQueueResponse echo budget.
U-256 — FolderContentsRequest request-to-response directory echo budget.
```

## Folded/alias rows

```text
U-272 — duplicate/alias of U-256. Do not reopen separately.
U-47  — older place-in-queue amplification context. Do not count separately.
```

## Nearby but separate

```text
U-221 / U-224:
  incoming result/list display component validation;
  public PR #3741 overlaps these more directly.

FOLDER-RESP-01 / U-167 + U-255 + U-260 + U-268:
  inbound FolderContentsResponse token/parser-ordering behavior;
  not the same as FolderContentsRequest request-to-response echo.

UPLOAD-QUEUE-POLICY-01 / U-244:
  queue megabyte admission accounting;
  not a virtual-path semantic budget issue.

TR-STATUS-01 / U-158 + U-166:
  status/queue-position response provenance;
  not request path parsing/echo policy.
```

## Anti-pattern avoided

Avoid proposing a `PlaceInQueueRequest`-only fix, a `QueueUpload`-only fix, or a folder-only fix. Those would create inconsistent protocol behavior and leave one of the sibling request-control surfaces open.

The saner changeset is one shared virtual-path policy plus per-call-site tests that prove all four relevant request paths agree on total length, component count, component byte size, control characters, and echo behavior.
