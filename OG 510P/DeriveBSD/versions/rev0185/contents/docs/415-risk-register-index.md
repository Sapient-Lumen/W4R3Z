# Risk register index (generated)

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** operability

This is a compact, deterministic index for the canonical long-form register: `docs/266-open-questions-and-risk-register.md`.

- Machine-readable index: `docs/_generated/risk_register.json`

## How to refresh
- `python3 tools/gen_risk_register_index.py --write`
- `python3 tools/check_generated_docs.py` (fails if this doc or the JSON index is stale)

## Items
| # | Topic | Risk |
|---:|---|---|
| 1 | Package recipe surface: how much language is allowed? | Risk: a rich language becomes the real product; the typed Spec becomes a veneer. |
| 2 | Cross compilation and multi-arch closures | Risk: subtle non-reproducible builds and broken caches. |
| 3 | Kernel/userland split: pkgbase vs “derive base” | Risk: base becomes a special snowflake lane. |
| 5 | Update distribution strategy | Risk: the secure path is too hard; people bypass it. |
| 6 | Human-scale debugging | Risk: beautiful theory, miserable incidents (if we never ship the human-scale views). |
| 7 | Desktop/interactive workload stance (if any) | Risk: unclear target leads to conflicting security postures. |
| 8 | Store growth + GC + long-lived fleets | Risk: fleets silently fall out of rollback coverage. |
| 9 | Human identity + home data model (portable homes vs host accounts) | Risk: users reinvent unsafe sharing (mount whole home everywhere) or admins keep homes always mounted (data exposure at rest). |
| 10 | Continuous fuzzing + regression localization (signal vs noise) | Risk: fuzzing becomes a vanity dashboard, while regressions still require heroics. |
| 11 | Kernel module policy + loader verification (don’t leave a pre-kernel hole) | Risk: secure boot becomes a checkbox while attackers (or accidents) still control which kernel code runs. |
| 12 | Removable media + device posture (USB is the universal footgun) | Risk: a single untrusted USB device collapses the security posture, or users invent ad-hoc bypass workflows. |
| 13 | Origin labels + quarantine metadata (prevent laundering and stripping) | Risk: the system reverts to mystery bytes, and the safe open path becomes optional folklore. |
| 14 | Outbound network policy + consent UX (avoid silent exfil or click-ops) | Risk: either networking becomes ambient again, or users/admins train themselves to bypass the safe path. |
| 15 | Witness networks as security parameters (availability, diversity, governance) | Risk: hard-coded witness lists (centralization) or brittle availability requirements. |
| 16 | Trustworthy time in hostile environments (rollback-by-clock, offline bootstrap) | Risk: security checks degrade into “ignore expiry” during incidents, which becomes normal. |
| 17 | Inbound exposure + firewall state (avoid ambient listeners and port-folklore) | Risk: services quietly become internet-facing, and incidents cannot answer *what was exposed and why*. |
| 18 | Formal methods lane: models become stale or theatre | Risk: models drift from implementation/intent and become diagramware; the lane becomes theatre instead of a safety tool. |
| 19 | Quorum approvals: click-ops, bypass, and governance drift | Risk: approvals become “click until it works” or a purely social process that attackers bypass. |
| 20 | Workload identity + credential issuance (avoid "static token" relapse) | Risk: either the identity lane becomes an overbuilt “mesh”, or it stays absent and people reintroduce static secrets. |
| 21 | Exec integrity enforcement: brittleness and bypass | Risk: enforcement is perceived as brittle, so it's disabled or bypassed, and the system returns to ambient execution from writable areas. |
| 22 | Keyless identity receipts: over-trust and identity confusion | Risk: supply chain checks devolve into "it's signed, ship it" with weak identity semantics. |
| 23 | Remote assistance + session recording: backdoors, stealth, and privacy drift | Risk: remote support becomes a permanent backdoor, or recording becomes surveillance; either outcome trains users to bypass the safe path. |
| 24 | Spec/policy authoring frontends: compiler trust and DSL sprawl | Risk: frontend tooling becomes a large, fast-moving TCB that operators bypass or that silently changes semantics. |
| 25 | Queryable metadata: privacy, laundering, and index integrity | Risk: either metadata is too hard to use (people ignore it), or it becomes ambient surveillance/exfiltration. |
| 26 | Multi-origin userlands: explicit strata vs ad-hoc chroots | Risk: the ecosystem invents unofficial composition patterns that bypass provenance, policy, and explainability. |
| 27 | “How it runs” source vs runtime artifact sprawl (component descriptors) | Risk: runtime policy becomes folklore; review/diff tooling loses leverage. |
| 28 | Permission creep despite explicit grants (need authority budgets) | Risk: components become overprivileged; sandbox primitives exist but are not used in practice. |
| 29 | Lazy mounts and partial fetch: integrity, side-channels, and fallback drift | Risk: the optimization becomes an unreviewed distribution path, or it becomes an ambient surveillance surface. |
| 30 | Snapshot UX vs security: revocation, secret retention, and ambient exposure | Risk: snapshots become a silent data-exfil path and undermine least-authority promises. |
| 31 | P2P distribution: poisoning, identity confusion, and privacy leakage | Risk: operators deploy P2P daemons outside the Derive trust/evidence model, or P2P becomes a stealthy exfil surface. |
| 32 | Structured diagnostics vs privacy (Inspect trees can become ambient surveillance) | Risk: operability features become a new exfiltration surface or a compliance nightmare. |
| 33 | Flight recorders: overhead, covert channels, and “debug mode” bypasses | Risk: performance regressions, covert channels, or an ecosystem split where the real debugging happens outside the Derive evidence model. |
| 34 | Trust bundles: format choice, interop renderers, and drift control | Risk: trust roots drift silently, TLS validation becomes inconsistent across libraries, and incidents can't answer "what roots were trust… |
| 35 | DNS mediation receipts: TOCTOU control vs privacy toxicity | Risk: either hostname policy devolves into folklore again, or DNS evidence becomes too sensitive to keep/ship. |
| 36 | Crypto operations portal: key abuse, user presence, and audit toxicity | Risk: operators fall back to file-based keys and ad-hoc agents, or the broker becomes an unreviewable, omnipotent signing daemon. |
| 37 | Trustworthy time: quorum failures, expiry safety, and operational response | Risk: expiry-based security becomes a bypass (“clock was wrong”), or operators add ad-hoc time tooling outside the Derive evidence model. |
| 38 | Installation and recovery: disk layout idempotency, encryption ergonomics, and “don't wipe the wrong disk” | Risk: installation is too brittle or scary, operators bypass the Derive model, and recovery devolves into unreceipted folklore tooling. |
| 39 | Operator access leases: JIT cert UX, audit value, and "no backdoor" posture | Risk: either operators keep static keys and bypass the Derive model, or we build an access broker that is too complex, too central, or to… |
| 40 | Measured boot in practice: event-log replay ergonomics, attester lifecycle, and variance policy | Risk: the lane exists “on paper” but is too painful to adopt, so secrets/update gates drift into bespoke vendor tooling outside the Deriv… |
| 41 | Backups and restore drills: key availability, privacy, and false confidence | Risk: fleets accumulate “feel-good backups” that cannot be restored, or build shadow backup tooling outside the Derive evidence model. |
| 42 | Kernel mutation control: sysctls, boot tunables, and module loading drift | Risk: kernel state becomes mutable folklore, undermining verification claims and making incident response depend on guesswork. |
| 43 | Hardware inventory + compatibility gates: safety, privacy, and operability | Risk: we either under-specify the lane and upgrades keep bricking hosts, or we over-collect identifiers and the evidence model becomes pr… |
| 44 | Firmware updates + UEFI variable drift: trust roots, remote bricks, and unreceipted platform mutation | Risk: firmware and boot policy drift happen outside the Derive evidence model, undermining attestation, trust-bootstrap claims, and upgra… |
| 45 | Network topology drift: routes, addresses, pf substrate, and remote-brick changes | Risk: networking becomes folklore again — remote incidents require SSH log spelunking, drift breaks reproducibility claims, and topology … |
| 46 | `/dev` drift: ambient device nodes, devfs ruleset folklore, and sandbox escapes | Risk: `/dev` becomes folklore again, sandboxing claims are undermined, and permission creep happens via invisible device exposure. |
| 47 | Product profiles (A–D) as first-class compilation targets | Risk: A–D becomes an untestable promise and the archive drifts toward a single implicit product shape. |
| 48 | Data-at-rest posture (ZFS encryption + keys + recovery) | Risk: deployments invent ad-hoc key handling that leaks secrets or makes recovery folklore. |
| 49 | Desktop viability constraints (even if desktop is not v0) | Risk: B becomes infeasible, forcing forks or abandoning the workstation story. |
| 50 | Export boundary drift: policy changes, redaction defaults, and exfil risk | Risk: exports revert to folklore (“someone emailed a tarball”), making incidents less explainable and turning support tooling into an exf… |
| 51 | Attestation admission policy drift: keep “what is gated?” stable and reviewable | Risk: admission control becomes folklore (“we totally check attestation”), turning attestation into theater and enabling accidental (or m… |

## Notes
- Treat missing `Risk:` lines as a hygiene failure; each item should state the failure mode explicitly.
- The index intentionally does not copy full sections; use `docs/266-...` for details and mitigation.

Last updated: <generated>
