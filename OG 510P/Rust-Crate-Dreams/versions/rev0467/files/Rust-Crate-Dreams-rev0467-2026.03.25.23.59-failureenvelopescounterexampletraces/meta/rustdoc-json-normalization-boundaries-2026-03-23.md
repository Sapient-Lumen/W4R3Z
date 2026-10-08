# Rustdoc JSON Support Contract Kit — normalization boundaries (2026-03-23)

When future revisions touch **P-0051**, do not let the archive collapse these into one fake “rustdoc JSON is handled” story:

1. **source route** — local nightly generation, docs.rs import, rustup `rust-docs-json`, or manual file import;
2. **raw format support** — whether the consumer can actually parse the observed `format_version`;
3. **normalization support** — whether the stable IR preserves or downgrades the needed relations;
4. **downstream query scope** — which public-API, docs, or semver queries are supported above the current IR;
5. **claim ceiling** — where missing cross-crate items, manifest facts, or unsupported fields force manual review.

Do not let any of the following stand in for an honest answer:

- “the file parsed,”
- “docs.rs had a JSON endpoint,”
- “the crate has rustdoc JSON,”
- “cargo-semver-checks supports many versions,”
- or “the normalized model loaded.”

A bundle can contain all of those facts and still fail to say what route was used, what versions are supported, and what was lost.
