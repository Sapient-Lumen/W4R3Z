# Voting for intensity, tradeoffs, and anti-capture (QV and friends)

**Material floor (one sentence):** If a polity uses voting to allocate scarce attention/resources, the voting mechanism must be threat-modeled for capture, coercion, and identity manipulation.

## Why “one person, one vote” isn’t the whole story
Many decisions are not binary “who wins” elections: they’re **allocations** (budget slices, priorities, tradeoffs). Mechanisms that let people express **preference intensity** can be useful—but are fragile under bribery, sybil attacks, and unequal resources.

Quadratic voting (QV) is a prominent intensity mechanism; recent work studies its behavior and limits, and cryptographic / decentralized variants continue to emerge. See [BIB-INFORMS-QV-2024], [BIB-ACM-QVNET-2025], [BIB-NBER-OTREE-QVSR-2025].

## Mechanism menu (use-cases, not ideology)
- **Approval / score voting:** good for many-winner selection and avoiding spoilers; weak at budgeting intensity.
- **Participatory budgeting:** bundles deliberation + allocation; often best as a pipeline with an assembly step (`143-…`).
- **QV (credits-based):** lets people “spend” voice on what they care about; requires strong identity and anti-bribery controls.
- **Delegative / liquid democracy:** scalable expertise routing; requires recall, transparency, and coercion resistance.
- **Sortition + vote hybrids:** assemblies propose; electorate ratifies; reduces agenda capture (`119-…`, `143-…`).

## Governance test suite for any voting mechanism
Minimum evaluation dimensions:
1. **Identity hardness** (sybil resistance; enrollment integrity) (`125-identity-membership-and-civil-status.md`).
2. **Coercion & bribery resistance** (secret ballots, anti-buying constraints, audit). See `05-…`, `116-…`.
3. **Equity under unequal resources** (does wealth buy outcomes?).
4. **Legibility** (can participants understand consequences?) (`134-legibility-and-complexity-budgets.md`).
5. **Recountability & verifiability** (audit trails, dispute resolution) (`114-…`, `130-…`).
6. **Manipulation surfaces** (agenda control, bundling, turnout games) (`111-…`).

## QV deployment guidance (tight)
QV is most defensible when:
- it allocates **bounded** public goods or priorities,
- participants receive **equal voice credits** (not purchased),
- identity is robust and privacy-preserving,
- it is paired with deliberation (assembly/jury step) and clear binding rules (`143-…`, `111-…`).

QV is risky when:
- credits can be bought/traded,
- identity is weak or coercion risk is high,
- outcomes affect fundamental rights directly (use constitutional constraints instead).

## Cross-scope note
Micro-local: QV can allocate small discretionary budgets or issue prioritization in a neighborhood.
National/global: prefer QV as *one component* inside a deliberative+legislative pipeline, not as a primary legitimacy engine.
