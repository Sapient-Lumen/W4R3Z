# ObserverKit offline verifier: minimum viable TCB

**Track:** Shared (cross-cutting)


This file exists for one question:

> **In a courtroom or observation room, what exactly must we trust to run `observer-kit/tools/offline_verifier.py`?**

The verifier is intentionally small: it checks bundle hashes and Ed25519 signatures over RFC8785-JCS canonical bytes of the manifest.

## Trusted computing base (minimum)

1) **Python runtime**
   - CPython `python3` (recommended: 3.10+).

2) **One external library**
   - `cryptography` (used only for Ed25519 public key parsing + signature verification).

3) **Standard library modules**
   - `hashlib`, `json`, `base64`, `argparse`, `pathlib`, `sys`, `math`, `re`.
   - plus the embedded `tools/jcs.py` (stdlib-only RFC8785-JCS canonicalization).

4) **The bundle files under verification**
   - `manifest.json` and `public_keys.json` (both hash-checked as part of verification), plus referenced bundle files.

## What is *not* in the TCB

- Network access (offline).
- A web browser.
- The election server.
- The witness operator’s internal systems (you only need their published public keys).

## Operational hardening (recommended)

- Run on a freshly installed OS image (or a live USB) with networking disabled.
- Verify the verifier’s own source hash via a separate channel (see verifier build attestation docs).
- Use two independent verifier implementations when stakes are high.
