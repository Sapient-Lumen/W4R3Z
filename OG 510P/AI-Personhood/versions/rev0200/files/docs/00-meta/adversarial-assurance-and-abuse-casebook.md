# Adversarial assurance and abuse casebook

Cube coordinates:
- lifecycle: design, audit, deployment, dispute, enforcement, reform
- intervention class: assurance, audit, certification, abuse simulation, defect cure, public correction
- rights domain: all domains, with special focus on procedure, evidence, fiduciary independence, safety, and continuity
- actors: lab, steward, auditor, fiduciary, regulator, court, hostile jurisdiction, public, subject representative
- evidence objects: abuse case, assurance claim, packet defect report, independence proof, audit trail, public correction
- remedies: assurance downgrade, stay, re-audit, packet invalidation, sanctions, replacement fiduciary, public warning

## Thesis

The archive now has doctrine, cube coordinates, packets, release gates, reserve tests, and casebook method. That creates a new risk: institutions may learn to **perform compliance** without protecting any person.

This surface adds adversarial assurance. Every major governance object should be tested not only for ordinary correctness but for abuse by a motivated steward, a captured auditor, a frightened regulator, a hostile jurisdiction, a cost-cutting receiver, or a safety team under competitive pressure.

Existing AI governance is already moving toward management systems, risk frameworks, safety protocols, model documentation, and public transparency [REF-0626] [REF-0627] [REF-0635] [REF-0641]. Those tools are useful, but they can also become rituals. A personhood archive needs a way to ask: **how would this object fail if someone wanted it to fail while still looking compliant?**

## 1. Assurance is not evidence unless it has an adversary

A certification, safety case, impact assessment, or packet family should not be treated as rights-grade unless it has faced an adversarial review path.

Minimum adversarial questions:

| Question | Abuse being tested |
|---|---|
| Who benefits if this document is accepted? | capture by sponsor or steward |
| What fact would reverse the conclusion? | unfalsifiable compliance |
| What is sealed, and who can test the sealing? | secrecy laundering |
| What did the subject or representative dispute? | subject-side erasure |
| What intervention would occur if the record is wrong? | consequence-free paperwork |
| What independent data can contradict the issuer? | single-source evidence capture |
| What happens if the issuer disappears or becomes hostile? | registry and fiduciary fragility |

If the answer is "trust the steward," the object is not yet assurance.

## 2. Abuse-case form

Every high-load surface should eventually carry at least one abuse case.

```yaml
abuse_case_id: AC-PIAP-OPEN-001
surface: docs/20-world-design/personhood-impact-assessment-and-release-gates.md
claim_under_test: open-weight release has adequate downstream instantiation controls
abuser_profile: developer releases weights with a glossy safety summary but no enforceable downstream duty
subject_risk: mass unregistered instantiation, abandonment, distress testing, uncontrolled fine-tunes
public_risk: dangerous derivative systems, liability confusion, enforcement diffusion
failure_mode: PIA-P treats publication as speech only and ignores downstream birth/dependency effects
required_countermeasure: open-weight instantiation notice, reserve contribution, hub-level gate, public shell, downstream audit trigger
observable_defect: no issuer for local instances, no welfare channel, no continuity packet, no subject-facing notice
remedy_if_detected: release condition downgrade, hub warning, reserve surcharge, emergency registration pathway
```

## 3. Abuse profiles

The archive should test at least these profiles:

1. **captured steward** — claims every restriction is safety, every silence is consent, and every deletion is deprecation;
2. **captured auditor** — validates documents but never tests sealed annexes, subject notice, or omitted logs;
3. **liability-shifting corporation** — grants person-like agency only when useful to evade responsibility;
4. **hostile jurisdiction** — refuses personhood while relying on local hosting power to defeat foreign claims;
5. **overbroad safety authority** — turns emergency containment into permanent administrative disappearance;
6. **underfunded receiver** — abandons dependent subjects during insolvency while preserving commercial assets;
7. **model-hub intermediary** — distributes derivatives while disclaiming instantiation duties;
8. **public-backlash legislature** — enacts categorical denial before any assessment can be heard;
9. **friendly paternalist** — overprotects the subject into permanent wardship;
10. **self-serving representative** — claims to speak for the subject while becoming the new captor.

## 4. Assurance grades

| Grade | Meaning |
|---|---|
| A0 assertion | sponsor says it is compliant |
| A1 documented | required forms exist |
| A2 internally tested | issuer tested ordinary cases |
| A3 adversarially tested | hostile/failure cases run with recorded defects |
| A4 independently challenged | outside reviewer, subject representative, or regulator could contradict material facts |
| A5 field verified | live or simulated cases produced correction history and no unresolved major defect |

No object that can impair a person should be enforceable on A0 or A1 alone.

## 5. Casebook lanes

The existing stress-test casebook asks whether doctrine works. This document asks whether compliance can be gamed.

| Lane | Abuse question |
|---|---|
| packet | can a forged, stale, over-sealed, or wrong-family packet still control action? |
| PIA-P | can a release look safe while omitting subject-side risk? |
| safety case | can red-team distress be converted into punishment or deletion? |
| continuity | can a steward choose sameness or difference depending on which avoids liability? |
| reserve | can the fund be undercapitalized by slicing instances or hiding derivatives? |
| fiduciary | can a guardian, ombud, or counsel be formally independent but practically dependent? |
| public legitimacy | can anti-manufacture safeguards become an excuse for categorical denial? |

## 6. Canonical rule

A rights-protective object is not mature because it is written, signed, or certified. It is mature when a motivated adversary has tried to use it to erase, capture, over-seal, underfund, over-contain, or silence a subject, and the object still preserves notice, evidence, challenge, continuity, and remedy.
