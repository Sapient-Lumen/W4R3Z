# Court evidence bundle cover sheet (template — 1 page max)

**Track:** A (Deployable core)

**Purpose:** A human‑legible front page that makes an `EvidenceBundleManifest` usable in a real proceeding.
This is *not* a brief. It is a verification guide + custody summary that points to the cryptographic artifacts.

---

## 1) What claim this bundle supports (one claim)

- **Claim title:** _______________________________
- **Claim card:** `notes/claim.md` (or `claim.md`) — see DOC:`docs/217-claim-cards-and-traceability-minspec.md`
- **Scope boundary (one sentence):** ________________________________________________

## 2) Bundle identity (what exactly these bytes are)

- **Bundle manifest file:** `manifest.json` (schema: `schemas/EvidenceBundleManifest.json`)
- **Manifest digest (sha256):** `______________________________`
- **Manifest signature (if present):**
  - signer key id / fingerprint: `______________________________`
  - signer role (jurisdiction custodian / neutral packager): `______________________________`

## 3) How to verify (offline, reproducible)

**Goal:** let any party reproduce the same verification result using the observer kit.

- **Verifier tool:** `observer-kit/` → `tools/observer_verify_packet.py`
- **Verifier identity / hash (fill from output or build record):** `______________________________`

**Verification steps (fill with the exact command/output path used):**

1. Verify the bundle manifest signature (if present) and compute `sha256(manifest.json)`.
2. Verify the bundle contents match `manifest.json` (no missing/extra bytes).
3. Verify each envelope signature and each referenced receipt/gossip attachment.
4. Verify the claim‑specific objects (e.g., inclusion proofs, checkpoint chains, parity snapshot comparisons) as specified in:
   - `notes/verification_notes.md` (optional, bundle-local, 1–2 pages max)

**Expected verifier result (PASS/WARN/FAIL) and what it means:**
- PASS: ______________________________________________________
- WARN: ______________________________________________________
- FAIL: ______________________________________________________

## 4) What’s inside (minimal map)

List only the load‑bearing objects (kind + digest), not the full directory tree:

| Kind | Object digest (sha256) | Role in the claim |
|---|---|---|
| `hfv.public.notice` | `…` | __________________________________ |
| `…` | `…` | __________________________________ |

## 5) Chain of custody (who handled the bytes)

- **Origin of evidence bytes:** ________________________________________________
- **Who assembled this bundle:** _____________________________________________
- **When assembled (UTC):** _________________________________________________
- **Custody controls:** (write 3–6 bullets; keep factual)
  - __________________________________________________________
  - __________________________________________________________

If required, attach signed declarations in `notes/` (do not write long prose here).

## 6) Admissibility aids (keep bounded)

- **Court admissibility worksheet:** `notes/court-admissibility-worksheet.md` (template: `artifacts/templates/court-admissibility-worksheet.md`)
- **Crypto primer (1 page):** `notes/crypto-primer-one-page.md` (template: `artifacts/templates/crypto-primer-one-page.md`)
- **Expert declaration (optional):** `notes/expert-declaration.md` (template: `artifacts/templates/expert-declaration-outline.md`)

## 7) Limitations (non‑claims)

State the relevant boundary so the bundle can’t be misread:

- This bundle does **not** prove: _____________________________________________
- See non‑claims: DOC:`docs/167-non-claims-and-boundaries.md`

## 8) Contacts

- **Custodian / filing contact:** ____________________ (role / org)
- **Verification contact (technical):** _______________ (role / org)
- **Public key / trust anchors location (if any):** __________________________

