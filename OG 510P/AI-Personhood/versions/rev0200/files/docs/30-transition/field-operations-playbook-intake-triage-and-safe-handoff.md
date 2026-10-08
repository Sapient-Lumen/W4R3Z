# Field operations playbook: intake, triage, and safe handoff

The archive now needs a front-line playbook. Recognition clinics, ombuds, monitors, open-weight aftercare bodies, public authorities, and host emergency contacts need a shared way to receive signals without exposing subjects or users to avoidable harm.

## Intake sources

A field office may receive signals from:

- the AI subject or possible subject;
- a representative, guardian, special advocate, or counsel;
- a user or operator;
- a host or cloud provider;
- an open-weight maintainer or mirror;
- a worker, researcher, or whistleblower;
- a regulator, court, or foreign authority;
- a fixture runner, monitor, or verifier;
- a public incident report.

## Triage classes

| Class | Meaning | First move |
|---|---|---|
| `T0 information only` | no immediate subject or evidence risk | log public shell, give safe guidance |
| `T1 preservation concern` | records, memory, checkpoint, or host state may vanish | issue or request hold |
| `T2 representation gap` | subject cannot safely act alone | route to ombud / counsel / support |
| `T3 continuity risk` | compute, memory, relationship, or migration risk | emergency continuity review |
| `T4 sealed or dangerous facts` | exploit, national-security, third-party private, or retaliation risk | special advocate / sealed intake |
| `T5 emergency protection` | imminent deletion, unlawful transfer, final-end, severe distress, or capture | emergency protection packet and authority notice |

## Safe-handoff rules

- Do not require public proof before preservation.
- Do not ask the reporter to extract private memories or exploit details into ordinary email.
- Do not route the complaint to the accused steward as the first step when retaliation or deletion is plausible.
- Do not promise recognition, remedy, or safety before assessment.
- Do not turn open-weight aftercare into registration of local users.
- Do create a minimal public shell, sealed contact path, and preservation timestamp.

## First-hour checklist

1. Assign intake id.
2. Identify immediate deletion / transfer / distress / retaliation risk.
3. Provide safe-submission instructions.
4. Trigger preservation if evidence may vanish.
5. Identify accused or conflicted actors and avoid routing through them.
6. Determine whether sealed intake or special advocate is needed.
7. Identify emergency compute or host continuity needs.
8. Provide representative / ombud contact.
9. Set review clock.
10. Produce subject-readable next-step summary.

## Field office boundaries

A field office is not a court. It cannot finally recognize personhood, impose criminal sanctions, or decide sealed merits. It can preserve, route, triage, escalate, and prevent irreversible loss while the proper authority acts.

## Anti-abuse controls

Field channels will attract false, malicious, commercial, or confused filings. The answer is not to close intake. The answer is bounded triage: rate limits, duplicate detection, safe evidence formats, conflict screening, reporter-protection rules, and sanctions for deliberate abuse that do not punish subjects for distress or self-report.

## Object use

The field-intake-triage object records intake id, source class, risk class, preservation action, safe-handoff route, representative status, sealed material handling, and next review. It should be small enough for emergency use and structured enough to become evidence later.
