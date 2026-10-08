# TRANSFER-EOF-01 maintainer hardening skeleton

## Summary

The upload send loop currently has no explicit terminal/error invariant when the opened upload file returns EOF before the advertised `UploadFile.size`, and completion is recognized only when `offset + sentbytes == size` exactly.

## Current-behavior witness

```text
maintainer_artifacts/transfer-eof-01/test_upload_eof_before_advertised_size_reproducer.py
```

Observed across 3.3.10, 3.3.x, and master:

```text
- short read followed by EOF leaves the upload active;
- no local file error is emitted for stable EOF before advertised size;
- later file growth after an earlier EOF can still be sent;
- sentbytes overshoot above size misses the exact completion event.
```

## Suggested fixed-behavior direction

```text
- Clamp reads to advertised remaining bytes.
- Treat >= advertised size as locally complete for accounting.
- On EOF before advertised size, revalidate the opened handle and either fail immediately or apply a bounded, visible growing-file grace policy.
- Pair with opened-file provenance/fstat checks so the file represented at queue/advertise time is the one being sent.
```

## Caution

This should be presented as upload lifecycle/provenance hardening, not as peer-only RCE or direct file disclosure. The strongest preconditions involve local/shared-folder file changes or path/provenance mismatches.
