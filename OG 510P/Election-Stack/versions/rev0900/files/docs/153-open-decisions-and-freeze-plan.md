# 153. Open decisions and freeze plan

**Track:** Shared


Elections have deadlines. This pack should distinguish:

- **Open design decisions** (still in flux), from
- **Frozen interfaces** (schemas, EPB fields, receipt semantics), from
- **Operational policy** (can change with notice).

## 153.1 Freeze phases (suggested)

- **T-90 days:** freeze schemas and protocol messages used by verifiers/clients.
- **T-60 days:** freeze EPB structure, ballot definition pipeline, disclosure policy fields.
- **T-30 days:** freeze witness set admission rules and monitoring/inspection quotas.
- **Election week:** only emergency changes via published incident protocol + explicit evidence.

## 153.2 Emergency change gate

Any emergency change must include:

- a signed public statement (what, why, scope)
- EPB update (if parameters change)
- explicit migration/compatibility note
- evidence bundle showing pre/post behavior

## 153.3 Decision registry

Keep a single “decision register” file that points to all ADRs and their status:

- `adr/INDEX.md` (canonical ADR index / decision registry).
## 153.4 Mission-kernel live-evidence authentication freeze

ADR 0005 freezes the following verifier-visible rule: a digest plus free-text approval metadata is an unauthenticated candidate, not live evidence. Live promotion requires a canonical signed `EvidenceEnvelope` and an external trust profile that binds signer authorization, jurisdiction, election, payload schema, and authority scope.

Implementation decisions still open before a live pilot:

- the mission-kernel envelope kind and payload schema;
- the jurisdiction trust-profile acquisition and approval process;
- signer delegation, rotation, revocation, and emergency succession;
- recomputation or retrieval of the exact referenced source bytes; and
- privacy-preserving publication of public derivatives without treating a derivative digest as proof of the private source record.

