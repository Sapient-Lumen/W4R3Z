# Successor-safe ceremony receipt package heads should ship compact verification reports

Once the archive already keeps a package manifest, lineage, head, and live status card, the next cheap inheritor question is not only "what is live now?" but also "what verification actually ran against it here?" A compact package verification report closes that gap without retaining bulky logs.

A useful report stays small and machine-checkable:
- authoritative manifest reference and active locator digest
- one explicit validation profile id
- the compact status card it was scoped against
- a short list of checks with `pass` / `blocked` / `fail`
- an explicit verification decision
- the environment boundary when local execution stopped

In this archive, the practical boundary is already stable: Python-integrity checks run here, while Rust execution is still blocked by missing `cargo` / `junest`. Future stewards should not have to rediscover that from chat history or infer it from a failed harness run.

The package head should therefore expose one current verification report beside the live status card. The status card answers whether the package is citable now; the verification report answers what was actually rechecked locally and where the cloudtainer boundary stopped.
