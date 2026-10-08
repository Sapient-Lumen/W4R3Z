# 483 — Competing eligible routes, arbitration witnesses, and abstain before forced choice

## One-line thesis

When several rule families, model paths, retrieval sets, process lanes, or intervention routes remain simultaneously eligible for a consequential public-AI act, the system should preserve the live candidate set, the rule allowed to choose among it, and the abstention or escalation path, rather than silently forcing one plausible choice and presenting it as inevitable.

## Why this matters

The archive already covers contestability, decision traces, contemporaneous witnesses, confusability budgets, basis-locked pending states, and source-backed summaries. What it still lacked was one explicit grammar for a recurring ambiguity seam: not *whether some route fit*, but *what should happen when several fit at once*.

That seam appears in many forms. Two appeal lanes look simultaneously applicable. Several policy heads or rubric branches seem plausible for the same case facts. A retrieval stack surfaces multiple authority-bearing sources with different downstream consequences. A triage model and a rule-based fallback both remain admissible. A human operator could send the matter to one of several review teams, each defensible in isolation. Later, the institution narrates the chosen route as if it were the only serious option.

That is dangerous because false inevitability hides both uncertainty and discretion. It lets semantic proximity, interface convenience, vendor-default ranking, recency, or staff habit choose outcomes that appear principled only after the fact. The archive needs a sharper rule: when consequential routing remains multiply eligible, ambiguity itself becomes part of the governed state.

## Pattern pack

### 1. Preserve the live candidate set when consequential ambiguity remains

If more than one consequential route, basis, or process lane remains genuinely admissible, the system should preserve at least a compact candidate-set witness naming:

- the eligible alternatives,
- the stage at which the tie existed,
- and the candidate that was ultimately chosen, if any.

The trace should not rewrite the scene as if only one option ever existed.

### 2. Name the arbitration rule that is allowed to choose

Selection among eligible alternatives should follow a declared rule such as:

- legal precedence,
- safety-first routing,
- claimant-protective tie-break,
- least irreversible path,
- mandatory human arbitration,
- or documented institutional priority ordering.

Absent a declared arbitration rule, the system should not pretend that the chosen path was self-explanatory.

### 3. Distinguish resolved choice from unresolved ambiguity

Some ties are legitimately resolved by explicit precedence. Others remain too close or too consequential to auto-resolve safely. The archive should distinguish:

- resolved by rule,
- resolved by human adjudication,
- unresolved and escalated,
- abstained pending more information,
- or narrowed only after additional evidence.

This prevents uncertainty from laundering itself into unjustified confidence.

### 4. Require abstention or escalation when the confusability budget is exceeded

Where candidate routes are too close, too risky to confuse, or too weakly separable on the available evidence, the system should:

- abstain,
- request more information,
- escalate to human review,
- or choose the less harmful reversible path.

A forced answer is not always a better governance answer.

### 5. Preserve what additional evidence would have broken the tie

A useful arbitration witness should say, where possible, what evidence or clarification would have changed the routing posture, such as:

- one missing document,
- one unresolved identity fact,
- one jurisdictional distinction,
- one threshold crossing,
- or one authoritative source confirmation.

This turns ambiguity into a workable next step instead of a mysterious dead end.

### 6. Export arbitration state into review and appeal packets

If a consequential act was chosen from among several eligible alternatives, reviewers should be able to see:

- that a tie or near-tie existed,
- what rule resolved it,
- whether a human confirmed it,
- and whether a safer abstention path was available.

Appeal rights are weaker when the archive erases the possibility that another legitimate route was alive.

### 7. Treat recurring tie zones as governance signal

Repeated ambiguity at the same boundary is evidence that something upstream may need work, such as:

- clearer forms,
- better disambiguation prompts,
- tighter policy drafting,
- improved source hierarchies,
- or more explicit routing precedence.

The goal is not only to document ambiguous choices. It is to reduce avoidable ambiguity over time.

## Guardrails

- Do not let ranking defaults or recency effects silently choose among consequentially different routes.
- Do not narrate one chosen path as inevitable when several candidates were genuinely live.
- Do not force automatic resolution where the safer answer is abstention, escalation, or additional evidence.
- Do not hide the arbitration rule inside opaque implementation detail.
- Do not treat recurring ambiguity as a one-off curiosity if it is structurally produced.

## Failure modes

- **false inevitability**: one plausible route is presented as if it were the only one.
- **ranking-by-habit**: convenience, vividness, or default order silently chooses the winner.
- **tie erasure**: review surfaces hide that multiple consequential candidates were live.
- **forced-choice overreach**: the system answers decisively where the better move was abstention or escalation.
- **ambiguity recurrence**: the same confusing boundary keeps generating discretionary choices with no structural repair.

## Practical tests

A competing-route arbitration discipline passes when it can answer yes to all of the following:

1. Can the institution preserve when more than one consequential route or basis was simultaneously eligible?
2. Is there a declared arbitration rule or human adjudication rule for choosing among live candidates?
3. Can the system distinguish resolved choice from unresolved ambiguity or abstention?
4. Does it escalate or abstain when candidate confusion exceeds defined tolerance?
5. Can reviewers and appellants inspect how the tie was handled and what evidence would have broken it?

## Compression rule for the archive

If a consequential system can say **this route was chosen** but cannot also say **what other routes were still live, what rule was allowed to choose among them, and when the safer move was to abstain or escalate**, then it is still letting **selection convenience impersonate governing judgment**.
