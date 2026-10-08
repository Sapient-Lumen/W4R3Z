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