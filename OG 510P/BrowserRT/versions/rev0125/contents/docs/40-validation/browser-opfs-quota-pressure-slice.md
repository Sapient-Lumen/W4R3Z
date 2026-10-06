# Browser OPFS quota-pressure slice — rev0057

Current task: `browser:opfs-quota-pressure-proof`.

This slice focuses on the riskiest remaining storage boundary after the rev0056 restart proof: what the OPFS block-store does when the browser refuses more origin storage. It uses managed Chromium plus CDP to set a bounded quota for the probe origin, then writes unique OPFS blocks until the browser returns a real storage/quota rejection. Successful pre-rejection blocks are read, checksum-verified, deleted under the still-active override, and the quota override is reset before teardown.

Run it explicitly:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-quota-pressure-proof --jobs 1
```

Direct probe command:

```bash
node tools/browser_opfs_quota_pressure_probe.mjs --json artifacts/validation/REV0057-BROWSER-OPFS-QUOTA-PRESSURE-PROBE.json
```

Default budget:

```text
quota override: 768 KiB plus any baseline usage
block size:     256 KiB
max writes:     10
```

What it proves:

- CDP `Storage.getUsageAndQuota` can read the probe origin's usage/quota surface.
- CDP `Storage.overrideQuotaForOrigin` can activate and later reset a bounded origin quota.
- The OPFS async block-store reaches an actual browser storage/quota rejection without filling cloudtainer disk.
- Successful blocks written before the rejection remain readable and checksum-verifiable.
- Cleanup and delete continue to work while the quota override is active.
- Runtime telemetry emits `storage:opfs-block-put-error` and classifies quota failures as `BRT_OPFS_QUOTA_EXCEEDED` instead of opaque DOMException strings.

Non-claims:

- This is a Chromium/CDP proof, not a cross-browser quota conformance claim.
- This is a simulated origin quota boundary, not organic low-disk eviction pressure.
- This does not prove OPFS fsync durability, crash recovery, power-loss behavior, persistent-storage permission behavior, retention period, Storage Buckets behavior, or sync-access-handle behavior.
- This is not a throughput, latency, or capacity benchmark; the small quota and block sizes are intentional cloudtainer waste controls.
- Browser-light release remains browser-light; this proof stays browser/full/explicit-id only.

Why this changed:

Earlier speculation pointed toward quota/eviction pressure as the highest-risk unfinished storage surface, but a naive proof could waste gigabytes by trying to fill disk. The rev0057 path uses the browser's own CDP quota override so the failure is real, bounded, repeatable, and cheap.
