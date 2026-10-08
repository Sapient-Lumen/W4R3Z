# Package coherence gate — rev0073

Rev0073 adds a final read-only package audit because earlier cube revisions accumulated enough historical material that a successful packet probe no longer guaranteed a coherent deliverable.

`tools/audit_rev0073_package.py` checks:

```text
- required current entrypoints and rev0073 evidence exist;
- REVISION.txt names rev0073;
- current rev0073 Python artifacts compile from source without writing bytecode;
- current landing pages contain none of the known stale construction names or metrics;
- the four archived rev0072 U-123 Python files retain their captured SHA-256 hashes;
- U-123 disposition and native-patch summaries pass, and the research-boundary inventory reports write idempotence;
- no Git metadata, symlinks, Python caches, embedded upstream source tree, or source bundle is packaged;
- the final SHA-256 manifest lists every packaged file except itself and matches all hashes.
```

Historical negative-control ZIPs remain because they are tiny provenance-bearing test fixtures; the gate specifically rejects a packaged Nicotine source bundle or an extracted `pynicotine/` tree.

Rerun after extraction:

```bash
PYTHONDONTWRITEBYTECODE=1 python tools/audit_rev0073_package.py
```

The delta inventory excludes its own outputs, the manifest, and the two package-preflight records to avoid a circular measurement dependency. The pre-manifest run is recorded in `data/rev0073_package_preflight.json`. The packaged manifest is generated last and verified again against the final tree before archive creation.
