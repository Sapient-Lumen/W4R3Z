# IoTox decision ledger

This directory records decisions that are already part of the design. Open questions belong in `../open-questions.md`; changing an accepted decision requires a new ADR that explains the transition rather than silently rewriting history.

| ADR | Decision | Current consequence |
|---|---|---|
| 0001 | C++20 with a narrow runtime c-toxcore adapter | IoTox-owned code stays C++; one boundary owns the external C API |
| 0002 | Separate peer transport from route | Tox/native, Tox/Tor, and Tox/I2P are routes; direct overlays are different transports |
| 0003 | Structured core with a ratox-style façade | Preserve “just werx” Unix simplicity without making FIFOs the durable protocol |
| 0004 | Permanent RecallRoot-v1 | A fixed eight-word Argon2id contract permits re-entry from memory and offline guessing |
| 0005 | No vendor reassignment authority | IoTox cannot reset or take ownership of customer devices |
| 0006 | Tox remains primary; contribute infrastructure | Native Tox is the first network gate and stewardship is part of the product plan |
| 0007 | Independent authorization ledger | Tox friendship never silently grants device capabilities |

## Product axioms carried by rev0002

```text
From memory, you can reach your devices.
No IoTox company key can reassign them.
Tox does the connection work.
IoTox decides authority above Tox.
The outside should feel simple; the inside must tell the truth.
```

## Decisions intentionally not frozen yet

- owner application signing primitive;
- domain-separated subkey KDF and labels;
- deterministic Tox secret-key/no-spam derivation;
- route identity rotation policy;
- device certificate and recovery-knock formats;
- authorization-ledger serialization and rollback protection;
- root-transition/race policy after phrase compromise;
- CBOR implementation and final protocol numbers;
- Tor/I2P topology.
