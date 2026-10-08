# rev0210 evidence-drop quarantine and live path refactor

rev0210 adds a narrower, earlier gate than LEAP: the live evidence drop ledger. The archive now treats the first landing of a raw external file as its own quarantined event before LEAP, custody, response, intake, import, challenge, replay, or computed floor can act on it.

The risk target is not abstract doctrine. The first genuine artifact can fail in the first few seconds: copied from a redaction instead of raw bytes, pasted from a tool result, pulled from an agent task artifact, bundled into a path-unsafe archive, or summarized without retaining the source payload. Once that happens, later schemas may look clean while the real evidence chain has already been lost.

New operational rule: raw external material must first pass `tools/stage_live_evidence_drop.py`. The tool records a source hash, copies the file into `examples/artifacts/live-evidence-drops/`, hashes the quarantine copy, scans zip payloads for nested archives and path traversal, classifies protocol/redaction/control material, and emits `examples/live-evidence-drop-ledger-rev0210-quarantine-control.json`. The ledger has no live-floor effect and cannot create response, intake, or import records.

The LEAP schema now requires `source_evidence_drop_ledger_ref` before `candidate-artifact-received` or `admitted-to-custody` states can validate. The admission graph was refactored from `LEAP -> custody -> response -> intake -> import -> computed floor` to `evidence drop -> LEAP -> custody -> response -> intake -> import -> computed floor`.

Two bypasses are now explicit negative fixtures. A redacted/public-shell copy cannot be substituted for raw custody. An MCP/A2A/federated/tool artifact cannot be promoted into custody merely because a protocol run succeeded or a provenance label is present. This matches the existing protocol boundary: MCP tool outputs and A2A task states are transport/coordination events, not counterparty authority, subject authorization, or receipt-class proof. [REF-0768] [REF-0769]

The refactor keeps RATS-style role separation intact: attester, verifier, and relying party remain distinct, and quarantine hashing is not verifier-adapter approval or live reliance. [REF-0700]

What remains blocked: no genuine live external receipt exists, no candidate LEAP exists, no live custody record exists, no actual live response/intake/import exists, and computed live receipt floor remains zero.
