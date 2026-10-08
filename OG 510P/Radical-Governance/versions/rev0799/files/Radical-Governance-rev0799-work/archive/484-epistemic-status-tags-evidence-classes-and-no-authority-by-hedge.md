# 484 — Epistemic status tags, evidence classes, and no authority by hedge

## One-line thesis

Consequential public-AI claims, notices, summaries, incident updates, and review packets should mark each load-bearing statement as observed, measured, attested, reported, inferred, disputed, or unknown, with an explicit confidence class tied to evidence completeness, so hedged prose cannot quietly launder uncertainty into authority.

## Why this matters

The archive already requires source-backed summaries, official communications as evidence, contemporaneous witnesses, structured decision traces, and portable review packets. What it still lacked was one compact rule for the **claim itself**.

That gap matters because consequential governance often fails in the sentence layer. A status page says a fix is “believed to be complete.” An incident note says a harm “appears isolated.” A public system card says a supplier dataset is “validated” without saying whether that is directly measured, internally attested, or merely reported by the supplier. A caseworker summary retells a disputed route choice as if it were an observed fact. A later reviewer cannot tell whether a sentence names firsthand evidence, an institutional attestation, a third-party claim, or an inference stacked on other inferences.

Without explicit epistemic marking, the archive can preserve lots of records while still letting uncertainty hide inside tone. Public governance then drifts toward one of its oldest pathologies: **authority by prose confidence**.

## Pattern pack

### 1. Tag the evidence class of each load-bearing statement

For consequential notices, summaries, incident updates, and review packets, mark load-bearing statements with a compact evidence-class label such as:

- **observed** — first-hand human observation tied to a named record or witness,
- **measured** — instrumented or system-captured observation tied to a named artifact,
- **attested** — a signed or institutionally accountable statement by a named role,
- **reported** — an external report, complaint, caller statement, media claim, or supplier claim not yet independently confirmed,
- **inferred** — a conclusion drawn from other tagged statements,
- **disputed** — credible accounts conflict,
- **unknown** — the institution does not currently know.

The archive should prefer plain tags over vague hedges.

### 2. Tie confidence to evidence completeness, not institutional rank

Confidence labels should say how complete and corroborated the evidence is for this claim, not how senior the speaker is. A compact scale can be enough, for example:

- **high** — the expected evidence set is present or a justified substitute exists,
- **medium** — some evidence exists but important corroboration or context is still missing,
- **low** — the statement relies on thin, indirect, or mainly reported evidence.

Confidence should not be used as a mood word. It should be tied to what is actually preserved.

### 3. Preserve promotion rules between evidence classes

A statement should not silently move upward in authority. Examples:

- reported should not become observed without a new evidence object,
- inferred should not become measured without actual instrumented basis,
- attested should not erase that the underlying fact remains disputed,
- and unknown should not disappear merely because a later summary sounds cleaner.

When a claim changes class, the archive should preserve what new evidence justified that change.

### 4. Keep dispute and unknown visible instead of narratively smoothing them away

Dispute is often governance-relevant content, not editorial noise. A good archive preserves when:

- two official channels conflicted,
- a public complaint contradicts the system witness,
- a supplier attestation conflicts with operator logs,
- or a route explanation remains unresolved.

Unknown is likewise a valid public state. The institution should not pretend to know in order to sound in control.

### 5. Require premise pointers for important inferences

If a consequential statement is inferred, the archive should preserve the premises it rests on or at least stable pointers to them. That keeps a reviewer from receiving only the conclusion while losing the chain that made it plausible.

### 6. Distinguish evidence class from governance status

A claim’s evidence class is different from its formal governance status. For example:

- a measured claim may still be provisional,
- an attested statement may still be unofficial,
- a reported incident may still trigger serious interim safeguards,
- and a disputed public update may still be the current official notice until corrected.

Do not flatten epistemic truth into procedural status or vice versa.

### 7. Say what would raise or lower confidence

For medium- or low-confidence consequential claims, the archive should preserve what evidence would change the posture, such as:

- independent verification,
- broader channel parity check,
- fresh witness capture,
- supplier raw artifact release,
- or human review of disputed route conditions.

That turns uncertainty from atmosphere into an actionable review state.

### 8. Make epistemic tags portable across surfaces

Public notice, operator panel, appeal packet, and regulator export do not need identical detail. They should still preserve the same underlying evidence class and confidence story rather than rewriting it differently on each surface.

## Guardrails

- Do not let hedge words substitute for evidence-class tags.
- Do not let institutional authority override thin evidence.
- Do not retell disputed or unknown claims as settled facts in later summaries.
- Do not erase the distinction between external reports and independently confirmed facts.
- Do not use confidence language with no visible basis.

## Failure modes

- **authority by hedge**: “appears,” “likely,” or “we believe” quietly carries decisive weight without explicit evidence class.
- **promotion without proof**: a reported or inferred claim is later narrated as observed with no new evidence object.
- **dispute laundering**: conflicting accounts are rewritten into one neat story.
- **confidence theater**: high confidence is asserted because the institution feels certain, not because the evidence stack is complete.
- **status collapse**: procedural labels such as approved, current, or official are mistaken for epistemic certainty.

## Practical tests

An epistemic-tag discipline passes when it can answer yes to all of the following:

1. Are the load-bearing statements in consequential notices or packets tagged by evidence class?
2. Is confidence tied to evidence completeness rather than prestige or tone?
3. When a claim changes class or confidence, is the new basis preserved?
4. Can the archive keep dispute and unknown visible where they are real?
5. Can public, operator, and reviewer surfaces point back to the same epistemic posture?

## Compression rule for the archive

If a consequential institution can state **what it says happened** but cannot also say **whether that sentence is observed, measured, attested, reported, inferred, disputed, or unknown — and why the confidence level is what it is**, then it is still letting **tone impersonate evidence**.
