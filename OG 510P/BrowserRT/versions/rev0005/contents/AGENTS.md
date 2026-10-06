# BrowserRT agent notes

This cube is cloudtainer-only. Do not add external dependencies, CDN assets,
remote services, external URLs inside source files, or assumptions that a process
will remain alive across assistant turns.

Current revision:

rev0005 — Test Observatory Scaffold.

First command after extraction:

```bash
make turn-start
```

Before running a broad suite, prefer an impact plan:

```bash
node tools/plan_tests.mjs --changed src/browserrt.mjs,tools/run_tests.mjs --tier release
```

Testing rules:

- Every expensive future proof must be a manifest-addressable slice.
- No browser, OPFS, SAB, WebGPU, stress, chaos, or benchmark proof enters as one monolith.
- Quarantine is visible, temporary, and currently empty.
- Timing is diagnostic, not a public performance claim.
