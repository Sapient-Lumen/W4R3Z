# 431 — Data provenance chains and AI-ready dataset declarations

## One-line thesis

Public-sector AI should maintain a provenance chain for every consequential dataset and publish a compact dataset declaration that names source, collection method, transformations, representativeness limits, legal basis, sharing constraints, and reuse conditions.

## Why this matters

Most public AI failures look like model failures from the outside but turn out to be data-governance failures on inspection.

The institution may not know which source system contributed a field, how labels were generated, which records were excluded, what preprocessing changed the data’s meaning, whether synthetic or AI-generated data entered the pipeline, or whether the training, evaluation, and live-use datasets actually reflect the same operating context. Without that chain, bias review becomes guesswork, incident investigation slows down, and public explanation collapses into hand-waving.

Current official guidance supports a much more explicit standard. The UK Data and AI Ethics Framework says data transparency means communicating where data comes from, how it is collected, cleaned, used, stored, shared, analysed, and interpreted, plus the limitations of the data and how legal obligations were met. It specifically calls for documentation of provenance, preprocessing, data sharing and access conditions, and plain-language privacy and complaint information. The UK’s 2026 guidance on making government datasets ready for AI adds that AI-ready data requires transparent, reusable data structures, rich metadata, and explicit attention to legal, security, and ethical compliance. NIST’s AI RMF Playbook asks whether an entity has documented data provenance including sources, origins, transformations, augmentations, labels, dependencies, constraints, and metadata. NIST’s Generative AI Profile separately stresses tracking provenance of training data and metadata, documenting provenance limitations, and monitoring where AI-generated data may become a root cause of downstream performance issues.

The archive should therefore treat **dataset declarations** as first-class governance infrastructure. If public institutions publish system records without legible data lineage, they are disclosing the tool while obscuring the substrate that most shapes its behavior.

## Pattern pack

### 1. Keep a provenance chain from source collection to live use

For every consequential dataset, maintain a chain that records:

- source system or source organisation,
- collection or generation method,
- time window,
- lawful purpose and basis,
- schema and field meaning,
- transformations and joins,
- labeling or annotation process,
- quality checks,
- known exclusions,
- retention and disposal rules.

This chain should survive handoffs between policy, service, data, and vendor teams.

### 2. Publish a compact public dataset declaration for consequential systems

The public does not need every row-level detail, but it should be able to learn:

- what the main datasets are,
- why they are used,
- where they came from,
- what major preprocessing was done,
- what the main data-quality or representativeness limits are,
- whether the data is shared externally,
- and what rights or complaints routes apply.

A dataset declaration is the public-facing analogue of the internal lineage register.

### 3. Separate training, evaluation, live-input, and feedback data

Many governance failures come from collapsing different data roles into one vague description. Records should distinguish:

- training or fine-tuning data,
- evaluation and benchmark data,
- operational input data,
- retrieved or reference data,
- user feedback and appeals data,
- synthetic or AI-generated augmentation data.

Each serves a different governance purpose and carries different risks.

### 4. Treat every transformation as a meaning change until shown otherwise

Normalization, deduplication, thresholding, imputation, category collapse, translation, summarization, or retrieval preprocessing can materially change what the data means. Dataset declarations should therefore document:

- what was transformed,
- why it was transformed,
- who approved the transformation,
- what information may have been lost,
- and which downstream tasks the transformed data is still fit for.

This reduces the tendency to speak about “the data” as though it were unchanged from original collection to live inference.

### 5. Publish representativeness and group-performance caveats in plain language

A declaration should say when data is:

- incomplete,
- stale,
- geographically narrow,
- collected for a different original purpose,
- sparse for certain groups,
- biased by historical practice,
- or structurally incapable of supporting certain inferences.

Where group-level differential performance or uneven coverage is known, that should be stated alongside the dataset description, not hidden in a later evaluation annex.

### 6. Record access, reuse, and downstream sharing conditions

Public governance requires clarity about:

- who can access the data,
- what suppliers or third parties can process it,
- what data-sharing agreements apply,
- whether onward reuse is permitted,
- whether there are licensing or IP constraints,
- and how long the data is retained.

This makes it easier to audit the real boundary between public stewardship and external dependence.

### 7. Mark synthetic or AI-generated data as provenance events, not ordinary records

If a dataset includes AI-generated labels, synthetic examples, translated content, extracted entities, or summarized case material, that fact should be recorded explicitly. Synthetic or machine-derived data is not just another field source. It can import upstream model assumptions, distort error analysis, and blur accountability if later treated as ground truth.

## Guardrails

- Do not use “proprietary” or “vendor confidential” as a blanket excuse for losing internal lineage.
- Keep public declarations high-level where necessary, but never so vague that source, transformation, and rights conditions become invisible.
- Separate lawful basis from mere operational convenience.
- Distinguish unknown provenance from known provenance with limitations.
- Refresh dataset declarations when new sources, transformations, or sharing arrangements are introduced.

## Failure modes

- **mystery substrate**: the institution can describe the model but not the data path that shaped it.
- **merged-role blur**: training, evaluation, and live-use data are described as though they were one dataset.
- **transformation amnesia**: preprocessing steps materially changed the data but were not recorded as governance events.
- **representativeness theater**: data is called “representative” without showing where it is thin, missing, or historically skewed.
- **synthetic laundering**: AI-generated or machine-derived data enters the pipeline without explicit labeling or review.

## Practical tests

A provenance regime passes when it can answer yes to all of the following:

1. Can the institution trace each consequential dataset back to collection or generation origin?
2. Can a public reader see the main sources, transformations, and limitations in a compact declaration?
3. Are training, evaluation, operational, feedback, and synthetic data roles clearly separated?
4. Are access, sharing, licensing, and retention conditions visible?
5. Do new data sources or transformations trigger a declaration refresh?

## Compression rule for the archive

If a public AI system’s data can change meaning faster than its lineage can be reconstructed, governance is still operating without a real **substrate memory**.

