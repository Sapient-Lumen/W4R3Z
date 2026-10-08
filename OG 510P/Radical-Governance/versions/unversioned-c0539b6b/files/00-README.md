# Radical Governance Archive (Working Draft)

**Last updated:** 2026-02-21 (rev9)  
**Scope:** governance design from micro-local to global, with a bias toward *small, reusable building blocks* rather than sprawling manifestos.

## How this archive stays small
- Each document is a **design memo**: decision-ready, bounded, and refactorable.
- Prefer **citations over quotations** and **summaries over dumps**.
- Add new documents only when they introduce a **new primitive**, **new scope**, or **new failure mode**.
- When in doubt, **refactor** existing memos instead of adding new ones.

## Document map
Core
- `01-principles.md` — cross-scope principles (subsidiarity, rights, openness, rule of law, etc.)
- `02-design-toolkit.md` — reusable institutional primitives (modules you can reuse everywhere)
- `03-metrics-and-evidence.md` — minimal measurement + falsification loops
- `04-threat-models.md` — cross-scope failure modes and mitigations

Shared primitives (cross-scope)
- `05-public-safety-and-coercion.md` — minimum-violence governance for coercive institutions
- `06-digital-and-algorithmic-governance.md` — governance of automated decisions + public digital systems
- `07-fiscal-and-budgetary-governance.md` — fiscal transparency, risk, and credible commitments
- `08-remedy-and-grievance.md` — how people challenge decisions and get enforceable fixes
- `09-public-service-and-state-capacity.md` — merit, skills, continuity, and “non-hollow” execution
- `11-commons-and-ecological-governance.md` — ecological limits + commons across boundaries (budgets, rights, accounts, compacts)
- `12-identity-and-recognition.md` — legal identity, CRVS, registries, and cross-boundary recognition
- `13-regulation-utilities-and-soes.md` — regulatory governance, utilities/concessions, and SOE governance

Scopes
- `10-micro-local.md` — building/block/neighborhood governance
- `20-municipal.md` — city/town governance
- `30-regional.md` — metro/watershed/county/state-like regions
- `40-national.md` — nation-state governance
- `50-supranational.md` — unions/confederations and cross-border regimes
- `60-global.md` — global public goods + world order institutions

Plumbing + migration
- `70-interoperability.md` — how scopes plug together (jurisdiction, escalation, data, finance)
- `80-implementation-roadmap.md` — migration path from “today” to “ideal”

Process
- `90-bibliography.md` — compact reference list (anchors only)
- `95-template-design-memo.md` — template for new memos
- `96-archive-governance.md` — how the research program stays coherent (and small)

## Style conventions
- **MUST / SHOULD / MAY** are used intentionally (RFC 2119 semantics): https://datatracker.ietf.org/doc/html/rfc2119
- “Ideal” here means: *maximizes legitimacy, capability, adaptability, and harm-limiting under realistic human constraints.*

## Contributing
Additions SHOULD:
1) name the scope,  
2) specify the *problem class* (collective action, distribution, externalities, violence, information), and  
3) propose *institutions + incentives + accountability*.

Before adding a new file, check `96-archive-governance.md`.
