# Program namespace ID audit

The archive now treats workstream (`WS-*`), bridge-experiment (`BR-*`), and research-frontier (`RF-*`) identifiers as a small namespace with uniqueness requirements. rev0286 left duplicated `WS-0033` and `BR-0033` entries and a stale `RF-33` gate pointer; rev0287 repairs those program identifiers and adds a generated audit.

The generated surface is `docs/30-program/program-id-namespace-audit.generated.md`. It is intentionally shallow but useful: it catches duplicate program IDs, missing sequence entries, and the current max ID for each namespace.
