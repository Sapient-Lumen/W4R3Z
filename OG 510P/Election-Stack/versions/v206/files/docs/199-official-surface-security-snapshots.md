# 199 — Official surface security snapshots (make comms hardening auditable)

**Track:** A (Deployable core)

Docs `186`/`194`/`195` treat public communications as evidence and require **cross‑channel parity**.
This doc adds a tight operational missing piece: publish **small, verifiable snapshots** of your
*official domain + email authenticity posture* so that:

- a takeover (domain, certificate, email, social) becomes easier to diagnose publicly,
- “we had DMARC/DNSSEC/CAA in place” is provable at a time boundary,
- defenders can point the public to a **content‑addressed** statement of controls (and changes).

This is not a substitute for proper security engineering; it is a way to make security controls
**auditable** in the same comms‑as‑evidence framework.

See also:
- `37-public-evidence-and-disinformation-resilience.md` (baseline anti‑spoofing controls)
- `45-routing-dns-availability-attacks.md` (DNS/TLS threat posture)
- `186-incident-communications-as-evidence.md` + `195-...public-surfaces.md` (PublicNotice digests + verifiable status surfaces)

---

## 199.1 Threat model (why snapshots matter)

A common legitimacy failure mode is a **plausible fake official statement**:

- a mis‑issued certificate makes a convincing clone site,
- a registrar/DNS change redirects the official domain,
- spoofed email appears to come from the election authority,
- a social account is hijacked, or recovery routes are abused.

In these cases, the public often asks: *“How do I know which surface is real right now?”*
Snapshots give operators and observers a compact, verifiable answer:

- what controls were in place **before** the incident,
- what changed **during** the incident,
- what the operator claims is the current intended configuration.

Snapshots are particularly valuable when combined with PublicNotice parity:
*the notice announces the snapshot digest; the snapshot points to raw probe outputs by digest.*

---

## 199.2 Minimal object: `OfficialSurfaceSecuritySnapshot`

Track A defines a small evidence object:

- Envelope kind: `hfv.public.surface_security_snapshot`
- Payload schema: `schemas/OfficialSurfaceSecuritySnapshot.json`
- Template: `artifacts/templates/official-surface-security-snapshot-payload.json`

Operator digest card (bounded; see `docs/206`):
- `python tools/official_surface_security_snapshot_card.py --packet <packet_dir>`
- or: `python tools/evidence_object_card.py --packet <packet_dir>`

**Design rules (tight):**
- The payload stays small; it contains **digests** (pointers) to raw probe outputs.
- Publish snapshots as an **append‑only series**: every change is a new snapshot.
- Optional chaining via `previous_snapshot_sha256` makes rollback/rewrites detectable.

The snapshot is intentionally limited to **auditable controls** that meaningfully affect spoofing risk:

- DNS CAA (restrict certificate issuance) — RFC 8659 (`source: rfc8659_txt`)
- DNSSEC posture (domain integrity hardening) — RFC 4033 (`source: rfc4033_txt`)
- Certificate Transparency monitoring (mis‑issuance detection ecosystem) — RFC 9162 (`source: rfc9162_txt`)
- Email anti‑spoofing: SPF / DKIM / DMARC — RFC 7208 / 6376 / 7489 (`source: rfc7208_txt`, `source: rfc6376_txt`, `source: rfc7489_txt`)

---

## 199.3 What goes in a snapshot (keep it boring)

A snapshot SHOULD include, at minimum:

- `dns_caa` — current CAA records for the official web domain
- `dnssec_ds` — DS record at the registrar (or an explicit “not deployed” statement)
- `tls_certificate` — leaf certificate chain and fingerprints for key public HTTPS endpoints
- `dmarc` — current DMARC record for the official email domain
- `spf` — current SPF record(s) for the official email domain
- `dkim` — current DKIM selector(s) used for public alert/newsletter streams

Each observation has:
- a short `summary` string (human‑readable, one line), and
- an `evidence` pointer to raw bytes (e.g., `dig` output, `openssl s_client`, header samples).

**Anti‑bloat rule:**
- do not paste large command outputs into the markdown archive; attach raw outputs as detached objects
  and reference them by digest from the snapshot payload.

---

## 199.4 Publication pattern (deployable)

Minimal deployable pattern:

1. **Pre‑election baseline**: publish a snapshot series for the official surfaces you expect the public to use.
2. **Announce via PublicNotice**: publish a `hfv.public.notice` whose `references` include:
   - the snapshot payload digest (`sha256:...`), and
   - retrieval hints (packet URI/mirrors).
3. **Cross‑channel parity**: mirror the *notice digest short form* on all official channels (`194`/`195`).
4. **On change / incident**: publish a new snapshot immediately after any registrar/DNS/cert/email policy change.

A rumor‑control/status board SHOULD link to the **latest snapshot digest** alongside its “How to verify” section.

---

## 199.5 Verification (what observers can check)

Given a published snapshot payload (and ideally the announcing PublicNotice digest), an observer can:

- re‑run probes from independent networks and compare the raw outputs,
- detect drift over time (snapshots form a series),
- detect rollback/rewrites if `previous_snapshot_sha256` chaining is used,
- publish a verifier or parity report if the observed configuration diverges.

Snapshots do not prevent compromise, but they make compromise **legible** and help the public
distinguish “operator intended state” from attacker‑presented state.

---

## 199.6 Source anchors (informative)

- DNS CAA: `source: rfc8659_txt`
- DNSSEC introduction/requirements: `source: rfc4033_txt`
- Certificate Transparency v2: `source: rfc9162_txt`
- SPF: `source: rfc7208_txt`
- DKIM: `source: rfc6376_txt`
- DMARC: `source: rfc7489_txt`
