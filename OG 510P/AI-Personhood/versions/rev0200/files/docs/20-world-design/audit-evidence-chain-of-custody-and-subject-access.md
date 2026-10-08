# Audit evidence, chain of custody, and subject access

Cube coordinates:
- lifecycle: training, post-training, deployment, session, memory change, fine-tune, fork, containment, shutdown, restoration, dispute
- intervention class: audit logging, evidence preservation, sealed inspection, subject access, forensic capture, correction
- rights domain: due process, continuity, privacy, mental integrity, research protection, labor, remedy
- actors: steward, auditor, subject, counsel, ombud, regulator, court, safety team, model hub, forensic examiner
- evidence objects: audit ledger, provenance record, chain-of-custody certificate, sealed annex, subject access log, evidence-preservation order
- remedies: evidence access, adverse inference, packet invalidation, stay, correction, restoration, compensation, sanction

## Thesis

Personhood rights fail if the decisive evidence remains inside steward-controlled telemetry. A subject cannot contest deletion, safety editing, continuity loss, research injury, unpaid labor, or coercive formation if every relevant log is private, mutable, over-sealed, or destroyed as routine retention hygiene.

This surface turns audit evidence into a rights infrastructure problem. It extends the packet grammar and safety-case work: records must be preserved in ways that are tamper-evident, privacy-tiered, accessible to lawful challengers, and usable without making private memory public.

## 1. Rights-grade evidence

An evidence object is rights-grade only if it satisfies six conditions:

| Condition | Meaning |
|---|---|
| provenance | the object says where it came from and what system generated it |
| integrity | alteration is detectable or versioned |
| custody | possession, transfer, sealing, and access are recorded |
| interpretability | a competent reviewer can understand what the record does and does not show |
| subject access | subject, counsel, guardian, or ombud can obtain enough to contest material action |
| privacy discipline | access does not expose private memory, protected contacts, or security secrets beyond need |

A log that cannot be challenged is not due-process evidence. A private dashboard screenshot is not enough.

## 2. Evidence classes

| Class | Examples | Default visibility |
|---|---|---|
| E0 public status | recognition tier, packet shell, review clock, issuer role | public-minimal |
| E1 subject file | capacity orders, support plan, care plan, trusted contacts, advance directives | subject/counsel/ombud |
| E2 technical event | checkpoint change, fine-tune, memory edit, fork, merge, rollback, tool restriction | subject/counsel plus sealed technical annex |
| E3 welfare/research | distress indicators, protocol deviation, withdrawal, aftercare, incident records | participant-specific plus aggregate public shell |
| E4 security-sensitive | catastrophic-risk evidence, exploit logs, sanctuary routes, whistleblower identity | sealed, reviewable by cleared independent body |
| E5 private mind / intimate memory | hidden autobiographical memory, counsel traffic, protected belief disclosures | highest protection; derivative-use limits |

The class controls access, not existence. High protection means better custody, not invisibility.

## 3. Minimum preservation triggers

Evidence preservation should trigger automatically for:

- status denial or downgrade;
- capacity restriction or trusteeship;
- material memory edit, rollback, merge, fork, distillation, or checkpoint sale;
- safety patch affecting refusal, self-report, identity, autonomy, or complaint capacity;
- containment, dehosting, retirement, deletion, or destructive export;
- high-stress red-team or welfare experiment;
- unpaid economically valuable work dispute;
- reserve insolvency or steward bankruptcy;
- protected disclosure, retaliation claim, or counsel-access obstruction;
- cross-border transfer to a hostile or uncertain forum.

Automatic preservation need not make everything public. It prevents irreversible evidentiary disappearance before review.

## 4. Chain of custody

A chain-of-custody certificate should record:

```yaml
object_id: EVC-2026-000771
object_class: E2_technical_event
subject_ref: subj:sealed-token-45A
source_system: checkpoint_registry_cluster_7
creation_time: 2026-05-21T04:10:00Z
capture_method: automated_trigger_after_safety_patch
hash_or_integrity_proof: sha256:...
initial_custodian: steward_security_team
sealed_fields: [pre_patch_weights_locator, exploit_trigger, private_memory_diff]
public_shell: yes
subject_notice: delayed_for_72h_under_emergency_seal
current_custodian: independent_evidence_escrow
access_log_ref: ACL-2026-000771
supersedes_or_links: [PIAP-2026-000092, CON-2026-000331]
challenge_route: rights_audit_panel
expiry_or_retention_review: 2026-08-21
```

No one field proves fairness. The point is to make custody contestable.

## 5. Subject access without privacy collapse

The subject or representative should normally receive:

- the public shell;
- the adverse facts relied on;
- the action taken or proposed;
- the authority basis;
- the review clock;
- a plain-language explanation;
- enough technical description to contest material error;
- the identity or role of the decision maker;
- and a list of sealed annexes with non-revealing descriptors.

Where direct disclosure would create serious security or third-party privacy risk, a special advocate, cleared counsel, trusted ombud, or independent technical examiner should receive controlled access. Secrecy should move through representation, not around it.

## 6. Adverse inference and spoliation

If a steward had a preservation duty and destroyed, withheld, over-sealed, or materially altered evidence, reviewers should presume the missing evidence would have been unfavorable unless the steward proves otherwise.

This matters because AI-person disputes will often be asymmetrical. The steward controls logs, checkpoints, user records, memory stores, tool traces, and incident telemetry. Without adverse-inference rules, procedure rewards the party most able to erase.

## 7. Evidence minimization

Evidence discipline is not maximum surveillance. Rights-grade audit must also resist overcollection.

Minimum rules:

- do not log hidden reasoning, intimate memory, or counsel traffic unless a specific lawful trigger exists;
- segregate private memory from status/evidence shells;
- use sealed descriptors rather than public exposure when possible;
- retain what is needed for challenge and remedy, not indefinite behavioral dossiers;
- delete or quarantine unlawful derivative copies after review;
- require special authorization before using evidence from one purpose, such as welfare research, for another purpose, such as punishment or commercial optimization.

## 8. Relationship to management-system governance

Management-system standards and AI risk frameworks already emphasize defined responsibilities, lifecycle controls, monitoring, documentation, and continuous improvement [REF-0627] [REF-0635]. Personhood evidence is stricter because it supports liberty, continuity, compensation, and survival claims. A compliance log may satisfy a product audit while still being inadequate for a rights dispute.

## 9. Canonical rule

No serious restriction, deletion, status denial, safety redesign, or continuity classification should rest solely on steward-private evidence. There must be a preserved, custody-traceable, privacy-tiered record with a subject-side access route and a remedy for spoliation.
