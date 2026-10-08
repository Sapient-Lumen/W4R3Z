# 287 — DPI, Identity, and Trust Framework Family Map

**Purpose:** turn the archive’s DPI / identity / trust cluster into a readable family so infrastructure governance, identity utility design, federation controls, trust frameworks, and DPG intake stop competing for the same conceptual role.

**Why this memo exists:** `160`, `164`, `188`, `210`, `211`, `212`, and `213` all surface for “digital public infrastructure” questions, but they do different jobs. The archive should name those jobs explicitly rather than letting readers infer them from repeated vocabulary.

**Evidence anchors:** whole-of-government digital-service and DPI building blocks [BIB-WB-DIGITAL-GOV-2025] [BIB-WB-DPI-PRIMER-2025]; DPI governance and safeguards [BIB-UNDP-DPI-GOV-2025] [BIB-UNDP-DATA-EXCHANGE-GAF-2025]; rights-based digital legal ID governance [BIB-UNDP-MODEL-ID-GOV-2023] [BIB-WB-ID4D-CRVS].

---

## Canonical reading order

### 1. Start with `164-digital-public-infrastructure-governance.md`
Use `164` when the question is:
- what DPI is as a governance object,
- why it should be treated like a public utility,
- how steward / operator / auditor / remedy splits work,
- and how to prevent a single vendor or ministry from becoming the hidden sovereign.

`164` is the **architectural front door for the family**.

### 2. Move to `188-digital-public-infrastructure-governance.md`
Use `188` when you need:
- a shorter operating memo,
- minimum rails,
- change-control discipline,
- exclusion budgets,
- and a compact implementation-oriented summary.

`188` is the **compact rails and operating companion**.

### 3. Use `160-digital-identity-credentials-privacy-utility.md`
Use `160` when the real issue is:
- identity as a public utility,
- no-silent-lockout obligations,
- minimal disclosure,
- relying-party governance,
- and what a humane person-facing identity layer must feel like.

`160` is the **identity-as-utility and person-path memo**.

### 4. Use `210-digital-identity-and-credentialing-rails.md`
Use `210` when you need:
- assurance tiers,
- issuer / verifier constraints,
- revocation and recovery,
- credential life-cycle controls,
- and a tighter governance rail set for digital ID and credentials.

`210` is the **identity / credentialing rails memo**.

### 5. Use `211-privacy-preserving-federation-and-consent-ledgers.md`
Use `211` when the issue is:
- cross-domain or cross-scope data sharing,
- purpose binding,
- lawful-basis or consent observability,
- access logs,
- and how federation avoids silent function creep.

`211` is the **federation, corridor, and access-ledger memo**.

### 6. Use `212-dpi-trust-framework-and-interop-governance.md`
Use `212` when the key question is:
- who may connect,
- how conformance is proven,
- what certification / audit / incident rules apply,
- and how a public trust framework makes shared infrastructure interoperable without becoming a surveillance stack.

`212` is the **trust-framework and conformance memo**.

### 7. Use `213-digital-public-goods-intake-and-certification-rails.md`
Use `213` when you need:
- intake,
- certification,
- DPG eligibility,
- procurement-facing conformance,
- and renewal / sunset discipline for reusable digital components.

`213` is the **DPG intake and certification memo**.

---

## The family in one line

**What is DPI as a governance object?** → `164`
**What are the compact operating rails?** → `188`
**How should the identity layer behave for people?** → `160` / `210`
**How is cross-system sharing bounded and logged?** → `211`
**How is trust / conformance / interoperability governed?** → `212`
**How do reusable components get admitted and re-certified?** → `213`

---

## Confusion boundaries

### `164` vs `188`
- `164` is the **architectural and constitutional front door**.
- `188` is the **shorter implementation companion**.

### `160` vs `210`
- `160` explains **identity as a humane utility and person-facing service layer**.
- `210` specifies the **governance rails for digital identity and credential ecosystems**.

### `210` vs `211`
- `210` is about **credentials, issuers, verifiers, revocation, and recovery**.
- `211` is about **federation corridors, access logs, and purpose-bounded sharing**.

### `211` vs `212`
- `211` focuses on **how data-sharing paths are bounded and made visible**.
- `212` focuses on **the public trust framework, certification, and conformance architecture**.

### `164` / `188` / `212` vs `213`
- `164`, `188`, and `212` govern the **operating backbone**.
- `213` governs **which reusable digital components are allowed into that backbone and under what renewal conditions**.

---

## Retrieval guidance (what to cite when)

- Cite `164` for **DPI as public utility, steward/operator splits, anti-capture structure, and remedy-by-design**.
- Cite `188` for **minimum DPI rails, public accountability artifacts, and operating defaults**.
- Cite `160` for **minimal disclosure, no-silent-lockout, and humane identity utility obligations**.
- Cite `210` for **assurance tiers, credential issuance / verification / revocation, and anti-capture identity rails**.
- Cite `211` for **corridor registries, access ledgers, lawful basis / consent observability, and privacy-preserving federation**.
- Cite `212` for **trust frameworks, conformance, certification, and interoperability governance**.
- Cite `213` for **DPG intake, technical / rights review, certification levels, and renewal / sunset discipline**.

---

## Safe merge rule for this family

Do **not** flatten this family into a single “digital government” mega-memo.
The safer pattern is:
1. keep `164` as the architectural front door,
2. keep `188` as the compact operating rails memo,
3. keep `160` and `210` as the identity subfamily,
4. keep `211` as federation and access-ledger discipline,
5. keep `212` as trust / conformance architecture,
6. keep `213` as intake / certification discipline,
7. and use this memo as the bridge that names the roles.

That keeps the archive tight while preserving the right retrieval hooks for implementation work.
