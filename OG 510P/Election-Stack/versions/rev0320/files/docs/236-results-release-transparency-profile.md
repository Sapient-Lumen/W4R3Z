# 236 — Results release transparency profile (anchoring + time)

**Track:** A (Deployable core)

Track A treats election-night reporting and downstream “official numbers” as a first-class **accountability surface**.
This doc defines a **tight profile** for how results releases are anchored into the Public Bulletin Board (PBB),
checkpointed by witnesses, and ordered in time **without** introducing new large artifacts.

Scope: this profile is about *publishing* and *verifying* results artifacts (CRO / ENRUpdate / RRP), not about
legal certification or audit procedures.

See also: `04` (PBB), `38` (secure time), `63` (ENR security), `68` (pipeline), `69` (drift), `192` (time attestation), `234–235` (corrections + hashing).


## 236.1 Threat focus
Results publishing is unusually vulnerable to:
- **Equivocation / split views** (different audiences see different “official” totals).
- **Backdating / re-ordering** (a later correction is presented as “what we always said”).
- **Key substitution** (fake or rotated keys presented as authoritative).
- **Selective omission** (some releases disappear or are not linked-forward).

This profile makes those failure modes *detectable* with small, content-addressed evidence.


## 236.2 Profile primitives

### A) Digest-first identifiers
For results objects that are referenced by digest, Track A uses:
- `sha256:<hex>` digests over RFC8785-JCS canonical JSON (`source: rfc8785_txt`).

For CRO self-reference avoidance and link-forward chaining, use `235`.

### B) PBB anchoring is the ordering oracle
Treat `generated_at` / UI timestamps as **informational**.
**Ordering** is derived from:
- PBB inclusion proofs, and
- witness-quorum checkpoints (cosigned STHs).

### C) Time attestation is a separate evidence surface
PBB timestamps are not automatically trustworthy.
Deployments SHOULD adopt a TimeBeacon policy (`38`, `192`) and MAY additionally use:
- RFC 3161 timestamp tokens for “I existed by time T” evidence (`source: rfc3161_txt`), and/or
- Roughtime for low-latency time attestations (`source: draft_ietf_ntp_roughtime_17_txt`).


## 236.3 Normative requirements (tight)

### 1) Every results release interval MUST produce a PBB anchor
Each published `ResultsReleasePackage` (RRP) interval MUST be published as an `EvidenceEnvelope`:
- `kind: hfv.results.release_package`
- `payload_schema: schemas/ResultsReleasePackage.json`
- the envelope MUST include required publication attachments per `artifacts/registries/envelope-attachment-requirements.csv` (receipt + gossip summary).

The interval MUST also be anchored into the PBB as a `LogEntry` with:
- `entry_type = RESULTS` (see `schemas/LogEntry.json`)
- `payload_hash_b64` = base64(SHA-256(JCS(RRP_payload_json)))
- *(optional)* `time_beacon_digests` = digests of published `hfv.time.beacon` envelopes used for this release epoch (binds ordering to independent time evidence; `192`)

Notes:
- The “canonical payload” for this leaf is the **RRP payload JSON** (the envelope payload), not the full packet bytes.
- Interop rule: the leaf digest MUST match the envelope’s `payload_digest` (format translation only; `238`).
- `payload_hash_b64` is base64 of the **raw SHA-256 bytes** of the JCS canonical payload (not base64 of a digest string).
- Mirrors MAY reformat JSON; the payload’s JCS digest is the cross-mirror equality check.

### 2) Each RESULTS anchor MUST be checkpointed by witnesses
For a release interval to be treated as FINAL by monitors:
- the RESULTS leaf MUST have an inclusion proof against an STH, and
- that STH MUST be witness-quorum cosigned (checkpoint).

This is the anti-equivocation contract: a publisher can’t quietly “swap” the current release without producing fork evidence.

### 3) Releases MUST be link-forward and correction-aware
If a release changes totals (decreases or materially reassigns counts), publishers MUST:
- link-forward via `prev_cro_hash` / `prev_package_hash` where applicable, and
- declare a correction in a bounded way (`234`), e.g.:
  - `ENRUpdate.is_correction=true` + `correction_reason`, and/or
  - a `PublicNotice` correction referencing both superseded and superseding digests (`220–222`).

### 4) Results signing keys MUST be auditable
Publishers MUST use a dedicated results-reporting signing key (not tally keys).
Key material and rotations MUST be published as small, content-addressed artifacts, e.g.:
- `KeyTransparencyEntry` (key registry + rotation), and/or
- `OfficialChannelDirectory` + `PublicNoticeSigningKeyset` for comms surfaces (`203`, `208`).

If a key is rotated during the reporting window, the rotation MUST be:
- announced (digest-first) and
- anchored into the PBB before it is used for signing new RRPs.


## 236.4 Minimal verifier checks (portable)
A verifier/monitor implementing this profile SHOULD:
- Verify `235` hashing rules for CRO and link-forward pointers.
- Verify the RESULTS `LogEntry` inclusion proof and witness checkpoint for each interval.
- Verify that the ENR UI/API is derived from the CRO referenced by the latest FINAL interval (`69`).
- Treat any “current totals” display as **UNVERIFIED** unless it matches a checkpointed release.


## 236.5 Publication ergonomics (non-normative)
Keep public artifacts small:
- Publish the RRP manifest, digests, and signatures.
- Publish large payloads (full ERR/CVR, raw exports) via content-addressed pointers with clear redaction logs (`225`) rather than inline.
- Use a short PublicNotice “release pointer” that carries:
  - `cro_hash`,
  - the RESULTS anchor checkpoint ID,
  - and (optionally) the latest TimeBeacon digest and/or the RRP envelope digest.

