# Bridge shadow publication side-effect

`bridgeshadow.py` adds a no-network side-effect gate after publication acceptance. It joins three reports that could otherwise be mistaken for independent permission:

- `PublicationReport`
- `PublicationLedgerReport`
- `BridgeQuenchReport`

A shadow step binds the profile, service, scope, request, action, component digests, payload digest, sequence, previous digest, family, and path family. The assessment rejects replay, rollback, same-sequence forks, previous-link mismatch, action drift, payload drift, component digest drift, and low family/path diversity.

The point is not to publish. The point is to make future publishing boringly dangerous in tests before a live transport exists.
