# TR-STATUS-01 maintainer note skeleton — not production-ready

## Title

Download-side transfer status messages are applied by claimed username + virtual path without transfer-generation binding.

## Scope

This is a maintainer-facing hardening note, not a polished external advisory. It should likely be combined with peer/source-binding work rather than filed separately.

## Affected handlers

```text
Downloads._upload_failed()
Downloads._upload_denied()
Downloads._place_in_queue_response()
```

## Current behavior

A pytest witness in `maintainer_artifacts/tr-status-01/test_transfer_status_message_binding_reproducer.py` shows the following across 3.3.10, 3.3.x, and master:

```text
UploadFailed(filename) -> active download close + requeue by claimed username/path
UploadDenied(filename, reason) -> queued download failed/queued state by claimed username/path
PlaceInQueueResponse(filename, place) -> queue_position update by claimed username/path
```

## Proposed maintainer framing

The compatibility-preserving question is whether status messages should be bound to a pending transfer/request generation, or at least quarantined when they do not match expected source/session state.

## Caution

Do not overstate this as code execution or file disclosure. A legitimate uploading peer is expected to control its own transfer-status path. The more security-relevant case is a wrong source claiming that peer identity, which overlaps PB-01.
