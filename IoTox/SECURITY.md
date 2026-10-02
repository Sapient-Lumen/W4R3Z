# Security policy

IoTox is pre-release security-sensitive software. It is not yet suitable for protecting production
devices or secrets.

Do not open a public issue containing an exploitable vulnerability, private identity material,
RecallRoot phrases, Tox savedata, authority ledgers, or command stores. Until a private reporting
address is published, retain the report and open a minimal public issue asking maintainers to
establish a private channel.

An owner-operated bootstrap daemon's `key` is also private identity material. Its
`PUBLIC_ID.txt`, address, and port are publishable reachability records, but confer no IoTox
authority. See [`docs/bootstrap-relay-operations.md`](docs/bootstrap-relay-operations.md).

The current security design and explicit non-claims are documented in
[`docs/threat-model-draft.md`](docs/threat-model-draft.md).
