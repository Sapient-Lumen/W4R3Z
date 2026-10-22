# Source index

This file is a compact retained-source and family-representation map.
It complements `CATALOG.md` and `papers/EXTRACTION_MAP.json`; it does not replace canon ownership.

## Retained source roots

| Root | Files | Consumed by papers | Companion surfaces |
| --- | ---: | --- | --- |
| `sources/ctg` | 90 | `papers/ev_interpretation_profiles.tex`, `papers/ev_pact_ocf.tex` | `artifacts/curated/ctg/`, `papers/ev_pact_ocf.tex`, `papers/ev_interpretation_profiles.tex` |
| `sources/docf` | 658 | `papers/ev_interpretation_profiles.tex`, `papers/ev_streamfold.tex` | `artifacts/curated/docf/`, `renders/legacy_pdfs/docf/`, `papers/ev_streamfold.tex`, `papers/ev_interpretation_profiles.tex` |
| `sources/ocf_llm` | 2108 | `papers/ev_interpretation_profiles.tex`, `papers/ev_pact_ocf.tex` | `certs/curated/ocf_llm/`, `renders/legacy_pdfs/ocf_llm/`, `papers/ev_pact_ocf.tex`, `papers/ev_interpretation_profiles.tex` |
| `sources/pact` | 620 | `papers/ev_interpretation_profiles.tex`, `papers/ev_pact_ocf.tex` | `artifacts/curated/pact/`, `certs/curated/pact/`, `papers/ev_pact_ocf.tex`, `papers/ev_interpretation_profiles.tex` |

## Root details

### `sources/ctg` — CTG policy examples and traces
- Files: 90
- Consumed by: `papers/ev_interpretation_profiles.tex`, `papers/ev_pact_ocf.tex`
- Companion surfaces: `artifacts/curated/ctg/`, `papers/ev_pact_ocf.tex`, `papers/ev_interpretation_profiles.tex`
- Note: Retained CTG inputs stay as a compact full source tree; the curated CTG artifact directory is now mostly a canonical-path pointer rather than a duplicate mirror.
- Key subtrees:
  - `sources/ctg/policy_examples` — 2 files
  - `sources/ctg/traces` — 27 files

### `sources/docf` — dOCF data, examples, figures, and test vectors
- Files: 658
- Consumed by: `papers/ev_interpretation_profiles.tex`, `papers/ev_streamfold.tex`
- Companion surfaces: `artifacts/curated/docf/`, `renders/legacy_pdfs/docf/`, `papers/ev_streamfold.tex`, `papers/ev_interpretation_profiles.tex`
- Note: docf is the retained source tree that backs both the StreamFold family note and part of the interpretation bridge; curated docf artifacts stay as canonical-path pointers and unique local files rather than a full duplicate copy.
- Key subtrees:
  - `sources/docf/data` — 1 files
  - `sources/docf/examples` — 6 files
  - `sources/docf/figures` — 6 files
  - `sources/docf/test_vectors` — 169 files

### `sources/ocf_llm` — OCF LLM examples, profiles, schemas, tables, and verifier tooling
- Files: 2108
- Consumed by: `papers/ev_interpretation_profiles.tex`, `papers/ev_pact_ocf.tex`
- Companion surfaces: `certs/curated/ocf_llm/`, `renders/legacy_pdfs/ocf_llm/`, `papers/ev_pact_ocf.tex`, `papers/ev_interpretation_profiles.tex`
- Note: OCF LLM remains a large retained source family because many compact front / governance / admission examples still matter as audit substrate rather than just as rendered paper inputs.
- Key subtrees:
  - `sources/ocf_llm/archive` — 121 files
  - `sources/ocf_llm/examples` — 1544 files
  - `sources/ocf_llm/figs` — 22 files
  - `sources/ocf_llm/profiles` — 19 files
  - `sources/ocf_llm/schemas` — 6 files
  - `sources/ocf_llm/tables` — 101 files
  - `sources/ocf_llm/tools` — 276 files

### `sources/pact` — PACT workdir, demos, benchmarks, and replay-pack substrate
- Files: 620
- Consumed by: `papers/ev_interpretation_profiles.tex`, `papers/ev_pact_ocf.tex`
- Companion surfaces: `artifacts/curated/pact/`, `certs/curated/pact/`, `papers/ev_pact_ocf.tex`, `papers/ev_interpretation_profiles.tex`
- Note: PACT stays as a retained full source tree because replay packs, workdir benchmarks, and decision-object examples are still the canonical audit substrate for the PACT family extraction.
- Key subtrees:
  - `sources/pact/PACT_workdir` — 620 files

## Families represented without a retained `sources/` root

### `streamfold`
- Canonical paper: `papers/ev_streamfold.tex`
- Representation paths: `artifacts/curated/streamfold/`, `certs/curated/streamfold/`, `renders/legacy_pdfs/streamfold/`
- Note: StreamFold is represented in this unified archive by curated ABI material, signed examples, and retained legacy renders rather than a full retained sources/streamfold tree.

### `zkrtp`
- Canonical paper: `papers/ev_zkrtp.tex`
- Representation paths: `artifacts/curated/zkrtp_v2/`, `certs/curated/zkrtp_v2/`, `renders/legacy_pdfs/zkrtp_v2/`, `renders/legacy_pdfs/zkrtp_portfolio/`
- Note: zk-RTP is represented by curated material, signed examples, and retained legacy renders from v2 and portfolio lines rather than by a single retained full source tree under sources/.
