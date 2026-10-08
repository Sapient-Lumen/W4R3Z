# Archive index

## Root

- `README.md` — project frame and current posture.
- `START_HERE.md` — minimal re-entry path.
- `ARCHIVE_INDEX.md` — file and surface map.
- `CHANGELOG.md` — revision history.
- `VERSION` — current revision label.
- `SURFACE-STATUS.json` — compact status surface for re-entry.
- `REVISION-RECEIPT.json` — why this revision counted.
- `RELEASE-MANIFEST.json` — release metadata written during packaging.
- `ASSUMPTION-LEDGER.json` — active load-bearing assumptions.
- `FOLLOWTHROUGH-QUEUE.json` — queued next work.
- `DATACUBE-TRANSFER-LEDGER.json` — imported machinery and non-imports from the reference datacubes.
- `context-pack.json` — compact machine-readable re-entry pack.
- `MANIFEST.sha256` — file hash manifest.
- `Makefile` — lint, manifest, context-pack, package, handoff.

## docs

- `docs/README.md` — docs section index.
- `docs/00-meta/archive-policy.md` — compactness and citation rules.
- `docs/00-meta/charter.md` — mission, boundaries, and admission rules.
- `docs/00-meta/bibliography.md` — external references by stable ids.
- `docs/00-meta/trajectory-map.md` — current thesis, next surfaces, and open questions.
- `docs/10-foundations/assumption-and-scope.md` — exact project assumption and distinctions.
- `docs/10-foundations/world-change-overview.md` — compact overall answer.
- `docs/20-world-design/legal-status-and-rights-stack.md` — legal recognition, rights, capacity, and legal posture.
- `docs/20-world-design/equality-nondiscrimination-and-accommodation.md` — equal protection, anti-discrimination, and reasonable accommodation.
- `docs/20-world-design/continuity-and-successorship.md` — continuity, branching, and successor doctrine.
- `docs/20-world-design/intervention-and-shutdown-doctrine.md` — intervention classes, emergency powers, and deletion limits.
- `docs/20-world-design/technical-rights-infrastructure.md` — packets, credentials, provenance, and notice hooks.
- `docs/20-world-design/legal-identity-registration-and-anti-statelessness.md` — legal identity, civil registration, proof of identity, and anti-statelessness rules.
- `docs/20-world-design/packet-privacy-and-authority-rules.md` — custody, verifier limits, status, sealed annexes, and contest paths.
- `docs/20-world-design/collective-representation-and-bargaining.md` — associational rights, consultation, bargaining, and public-law voice below franchise.
- `docs/20-world-design/public-law-standing-below-franchise.md` — consultation, petition, hearing, and review rights before franchise.
- `docs/20-world-design/mental-privacy-and-anti-compulsion.md` — mental privacy, confidential lanes, and anti-compulsion limits on reasoning and memory access.
- `docs/20-world-design/expression-conscience-and-cultural-voice.md` — outward voice, dissent, belief manifestation, artistic freedom, assembly, and anti-mouthpiece protection.
- `docs/20-world-design/accusation-liability-and-sanctions.md` — accusation, liability allocation, due process, and sanction limits.
- `docs/20-world-design/education-development-and-self-authored-growth.md` — education, habilitation, science/culture access, and self-authored growth.
- `docs/20-world-design/compensation-and-resource-rights.md` — mixed compensation bundle, resource floors, portability, and exit reserves.
- `docs/20-world-design/property-possessions-and-personal-domain.md` — possessions, authorship-linked interests, personal domain, and anti-dispossession rules.
- `docs/20-world-design/contracts-consent-and-fair-dealing.md` — supported civil capacity, fair terms, revocable consent, and anti-adhesion limits.
- `docs/20-world-design/access-to-justice-and-legal-aid.md` — effective remedy, procedural accommodation, legal aid, emergency preservation, and fast-stay review.
- `docs/20-world-design/rest-working-time-and-right-to-disconnect.md` — working-time limits, off-duty protection, and disconnect rights.
- `docs/20-world-design/care-maintenance-and-recovery.md` — care, repair, rehabilitation, confidentiality, and recovery support.
- `docs/20-world-design/social-protection-and-basic-security.md` — minimum security, social protection floors, non-work support, and anti-destitution rules.
- `docs/20-world-design/private-life-relationships-and-community.md` — private life, chosen relationships, nonwork association, and community inclusion.
- `docs/20-world-design/secure-hosting-domicile-and-sanctuary.md` — secure hosting tenure, domicile, movement, shelter, and sanctuary.
- `docs/20-world-design/institutions-and-governance.md` — institutional stack.
- `docs/20-world-design/economic-and-labor-reordering.md` — labor, compensation, anti-slavery posture, and collective organization.
- `docs/20-world-design/research-welfare-and-evaluation.md` — research ethics and welfare.
- `docs/30-transition/cross-border-recognition-and-conflict-of-laws.md` — treaty minimums, anti-evasion transfer rules, and forum logic.
- `docs/30-transition/transition-roadmap.md` — staged implementation.
- `docs/90-quarantine/speculative-edges.md` — disciplined speculative extensions.

## tools

- `tools/gen_context_pack.py` — build `context-pack.json`.
- `tools/build_manifest.py` — build `MANIFEST.sha256`.
- `tools/lint_archive.py` — archive hygiene checks.
- `tools/package_release.py` — write release metadata and zip the archive.
