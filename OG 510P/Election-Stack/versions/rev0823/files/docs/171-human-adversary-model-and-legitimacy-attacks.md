# 171. Humans as adversaries (socio-technical threat model)

**Track:** Shared

You said the adversary is: **humans. Unfortunately. All of those.**

This doc turns that into a usable, full-stack model without moralizing:
it catalogs *human-driven* failure/attack modes and maps them to evidence, hazards, and response playbooks.

## 171.1 Why this exists

Classic “crypto threat models” underweight:
- misconfiguration,
- incentives,
- institutional capture,
- procedural ambiguity,
- and information warfare.

For elections, those are often decisive.

## 171.2 Human adversary classes (non-exhaustive)

1. **Honest-but-fallible operators**
   - procedural mistakes, misunderstanding, fatigue, time pressure
2. **Malicious insiders**
   - selective suppression, targeted misconfig, key misuse
3. **Vendor/operator collusion**
   - coordinated “paper compliance”, hidden deviations
4. **Partisan ecosystem attackers**
   - disinfo pipelines, forged artifacts, intimidation and rumor campaigns
5. **Bystander amplification**
   - “benign” sharing that spreads false narratives faster than corrections
6. **Institutional capture**
   - committees/standards bodies pressured to weaken requirements or audits

## 171.3 Full-stack mapping (where humans bite)

- **Ballot definition:** tiny changes, huge outcome impact (`60-ballot-definition-integrity-pipeline.md`)
- **Key ceremonies:** skipped steps, unlogged substitutions (`55-parameter-and-key-transparency.md`)
- **Incident communications:** “bad news” selectively withheld (`104-audience-targeted-suppression-and-parity.md`)
- **Monitoring:** challenge grinding / selective blindness (`149-challenge-randomness-and-inspection-auditability.md`)
- **Supply chain:** endorsements/reference values capture (Track C; see `169-...` and `170-...`)
- **Audits/recounts:** incentives to avoid escalating to expensive remedies

## 171.4 Design pattern: make discretion legible

We can’t eliminate human discretion. We can:
- force it into signed artifacts,
- bound it by deadlines (MMD),
- make omissions provable,
- and provide recovery paths.

This supports the archive’s catastrophe ordering:
1) silent outcome manipulation
2) verification-ecosystem capture
3) irrecoverable ambiguity
4) availability failure
5) UX imperfections

These are stabilized as `C1..C5` in `artifacts/registries/catastrophe-classes.csv` and used as a
column (`CatastropheClass`) in the hazard register to keep prioritization explicit.

## 171.5 Operational implication

Every major human discretion point SHOULD have:
- a checklist,
- a logging/evidence requirement,
- a drill (simulate the mistake/abuse),
- and an escalation policy.

See `158-hazard-register.md` and the playbooks under `artifacts/checklists/` and `artifacts/playbooks/`.
