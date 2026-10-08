---
id: P-0258
title: SMB2/SMB3 Interop & Evidence Kit — canonical trace bundles, capability matrices, and replay harness
status: idea
domains: [networking, filesystems, enterprise, interop, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/5606ad47-5ee0-437a-817e-70c366052962
  - https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/4287490c-602c-41c0-a23e-140a1f137832
  - https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/6eaf6e75-9c23-4eda-be99-c9223c60b181
  - https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/5cd64522-60b3-4f3e-a157-fe66f1228052
---

## Why this is missing
SMB2/3 is *everywhere* in enterprise and NAS, but interop debugging is still painful:
- captures are huge and hard to share safely,
- clients/servers disagree on dialect negotiation, signing, crediting, leases/oplocks,
- “it fails on this NAS firmware” is hard to turn into a CI test.

Microsoft’s open specifications define SMB2/3 message syntax and behavior; the docs explicitly note SMB2 is a major revision with different packet formats than SMB1. citeturn1search0turn1search5turn1search8  
SMB2 message layout begins with a fixed header; async vs sync header forms matter in real traces. citeturn1search1

Rust has SMB-related crates, but what’s missing is a **portable interop harness + evidence bundle format**.

## What the crate should provide
A harness that captures, normalizes, redacts, and replays SMB2/3 interactions in a controlled lab.

### Workspace
- `smbkit-ir` — parsed SMB2/3 messages + normalized “semantic events” (open, read, lease break, etc.)
- `smbkit-capture` — pcapng ingestion + dissector integration (optionally via tshark) → IR
- `smbkit-redact` — share-safe transformations (paths, usernames, domains, hostnames)
- `smbkit-sim` — deterministic replay against a target server (or recorded server responses)
- `smbkit-bundle` — emits `*.smbbundle.zip` with traces + decoded projections
- `smbkit-matrix` — capability matrix generator across servers/dialects

### Evidence bundle (`*.smbbundle.zip`)
- `trace.pcapng` (optional; can omit for sensitive environments)
- `events.jsonl` (normalized)
- `headers.csv` (quick grep-friendly)
- `capabilities.json` (dialects, signing, encryption, features)
- `redaction.yml` + `diff.md` (what changed between runs)

### MVP (6–8 weeks)
1. Pcapng → SMB2 header decode + minimal command parsing (NEGOTIATE, SESSION_SETUP, TREE_CONNECT, CREATE, READ/WRITE, CLOSE)
2. Canonical event stream + deterministic sorting/grouping (MessageId, SessionId, TreeId)
3. Redaction profiles + “public bundle” emission
4. One replay mode:
   - “client replay” (drive operations against a live server), or
   - “server stub replay” (respond from recorded corpus)

### De-risk plan
- Start with *analysis-only* mode (no replay), aimed at CI regression detection for clients.
- Validate parser against official doc fields (header/command tables) and a known-good dissector output.
- Keep a “minimum corpus” of real captures from Samba + Windows + one NAS device.

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
