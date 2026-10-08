# 149 — Public science + R&D governance (knowledge as infrastructure)

**Purpose:** Treat public knowledge production (research, statistics, evaluation, standards, and public-interest R&D) as **critical governance infrastructure**—with independence, transparency, and error-correction—so policy can learn without capture or propaganda.

**Scope:** national science systems, public labs, universities under public funding, public statistical offices, evaluation units, standards bodies, and mission agencies; also cross-border research coordination.

**Anchors:** open science as a global norm ([BIB-UNESCO-OPENSCI-2021]); statistical independence ([BIB-OECD-GSP], [BIB-UNFPOS]); evaluation guidance ([BIB-UK-MAGENTA-2025]); evidence-building law infrastructure (US Evidence Act summary: [BIB-US-EVIDENCEACT-EVALGOV]). R&D definitions/measurement: Frascati ([BIB-OECD-FRASCATI-2015]).

---

## Design stance

- Knowledge systems fail in predictable ways: **funding capture**, **publication bias**, **data hoarding**, **metric gaming**, **political interference**, and **irreproducible results**.
- Fix by making public research **auditable** (receipts + registries), **contestable** (standing + re-analysis access), and **repairable** (corrections propagate and incentives reward replication).

---

## Minimal stack (portable across scopes)

### SCI-1 Independence + mandate clarity
MUST:
- define the mission of the public knowledge body as a **public-interest trust** (not ministerial messaging)
- protect leadership appointment/removal and publish a role/mandate register entry for authority-bearing positions (`113`, `132`)
- publish interference incidents as receipts (who asked, what they asked for, disposition), with protected channels for staff.

### SCI-2 Evidence Register (precommitment)
MUST:
- register evaluations, major studies, and high-stakes evidence reports **before** results, with:
  - question, primary outcomes, data sources, timeline, governance, and publication plan
  - deviation receipts if methods change (pair with `104` postmortem logic)
- publish negative/null results (or explicitly receipted reasons for non-publication).

(Join: evaluation registry patterns in [BIB-UK-EVALREG-GUIDE]; broader evidence plan norms: [BIB-US-EVIDENCEACT-EVALGOV].)

### SCI-3 Open-by-default outputs with safety exceptions
MUST:
- publish outputs (papers, reports, code, methods) under open terms by default
- publish data **or** a public pointer to a protected access path (safe rooms, enclaves, synthetic data, query layers), with clear access criteria.

(Anchor: [BIB-UNESCO-OPENSCI-2021]; join to secrecy governance `77` and data governance `33`/`144`.)

### SCI-4 Reproducibility + replication budget
SHOULD:
- reserve a bounded share of funding for replication, robustness checks, and re-analysis
- require joinable artifacts: versioned code, provenance (`PROV`/`DCAT` pointers), and “how to reproduce” receipts.

### SCI-5 Conflict-of-interest + influence joins
MUST:
- disclose funding, affiliations, and relevant conflicts; publish COI policy and enforcement lane
- for government-commissioned evidence, require a **counterparty ID** (`EID`) and publish contracts/awards (join to `110`/`38`).

(Anchor: OECD conflict-of-interest guidance [BIB-OECD-COI].)

### SCI-6 Error correction that propagates
MUST:
- publish correction/retraction receipts and ensure downstream policy artifacts that relied on the evidence are flagged for review (`NR-07/15`; `31`, `82`).

---

## Institutions (small set)

### Public Statistical Office as a rights institution
- Protect independence and methods; publish revision policies; publish quality dashboards (anchors: [BIB-OECD-GSP], [BIB-UNFPOS]).
- Treat major data products as `REL-*` releases with version semantics (`51`, `74`).

### Standards + measurement bodies
- Treat standards as **power**: publish drafts, rationales, and impact notes; maintain an open change-log (`118`, `39`).

### Mission agencies (public-interest R&D)
- Use *portfolio governance* (diversity of bets, stage gates, kill criteria) to prevent monoculture and sunk-cost capture.
- Require “exit-to-public” commitments: open licensing, data access plans, and de-risked pathways for adoption without vendor lock-in.

---

## Procurement + grants as levers (join to integrity)

- Use open contracting for research funding and procurement of scientific services (`110`, `38`).
- Require that **models/data/code** produced with public funds remain accessible (or safely accessible) after project end (portability rule `109`).
- Require reproducibility artifacts as deliverables for commissioned evidence (no “PDF-only deliverables”).

---

## Metrics (anti-Goodhart)

Publish a small dashboard, and do not use it mechanically for ranking:
- % studies registered pre-results; % deviations with receipts
- % outputs open (code/methods/data or protected-access pointer)
- replication share; correction/retraction rate (with context)
- time-to-publication; time-to-correction propagation into policy artifacts.

(See metric integrity `142` and Goodhart lens `03`.)

---

## Cross-scope notes

- **Municipal/regional:** focus on service evaluation, administrative burden measurement, and local data partnerships (join `82`, `64/68/69`).
- **National:** protect statistical independence; national registries; major mission portfolios.
- **Supranational/global:** align on open science norms, shared datasets, and cross-border health/climate research compacts (join `60`, `114`).

