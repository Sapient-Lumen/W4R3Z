# Open knowledge, evidence commons, and scientific integrity rails

**Stack relation:** use `290-evidence-statistics-and-publication-integrity-routing-guide.md` for the canonical route across the evidence / statistics / publication-integrity cluster. This memo is the evidence-commons and scientific-integrity layer; `03` is the measurement front door; `214` is the institutional evidence-system anchor; `28` handles program commitments; `190` handles experimentation; `184` handles official statistics; `142` handles indicator governance; `37` / `51` / `53` are narrower claims/publication components.

**Problem:** Government decisions often rely on evidence that is inaccessible, non-reproducible, or locked behind vendor/academic paywalls. This creates epistemic capture and weakens public contestability.

**Design goal:** Build an **Evidence Commons** that makes *the grounds of decision-making* inspectable and reusable while protecting privacy, safety, and legitimate secrecy.

## Evidence Commons: minimum viable components

### 1) Open-by-default evidence index (joinable)

- **EIR‑*** — *Evidence Index Record*: a public record for any material policy claim, linking to sources, data access path, quality checks, and known limitations.
- **ECR‑*** — *Evidence Change Receipt*: when the evidence basis changes (new study, retraction, new dataset), publish delta + implications.

### 2) Open data + safe access ladder

Not all data can be open. Use a **tiered access ladder**:

- Tier 0: open aggregated stats + documentation
- Tier 1: open microdata with strong disclosure avoidance
- Tier 2: secure enclave / remote execution
- Tier 3: accredited access with audit logs and sanctions
(See `185-microdata-access-and-disclosure-avoidance-rails.md`.)

### 3) Reproducibility & policy evaluation

- Every major policy change should ship with an **evidence charter**: outcome metrics, guardrails, publication plan, and rollback triggers (see `190-policy-experimentation-and-evidence-rails.md`).
- Encourage preregistration for evaluations where feasible; require disclosure of negative results.

### 4) Scientific integrity boundary

- Protect researchers from political interference (appointments, publication approvals, suppression).
- Require suppression/redaction decisions to be receipted (authority, reason, expiry, appeal path).

## External standards to anchor (lightweight)

- UNESCO’s 2021 **Recommendation on Open Science** provides a global reference for shared values/principles and concrete actions for open access/data and equitable operationalization.
- Open Government Partnership’s core principles emphasize **transparency, participation, and public accountability** as the operating baseline for open government reforms.

## Tests (add to `107`)

- **Evidence legibility:** Material decisions can point to an `EIR` listing sources, access path, uncertainty, and dissent (if any).
- **Evidence update discipline:** When evidence changes materially, an `ECR` exists and affected policies are flagged for review.
- **Safe access exists:** Where privacy blocks openness, there is a published access ladder with clocks and appeal paths.
- **Integrity boundary:** attempted political suppression produces a public receipt (with bounded redaction) and triggers independent review.
