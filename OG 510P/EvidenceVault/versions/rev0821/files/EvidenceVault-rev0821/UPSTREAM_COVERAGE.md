# Upstream coverage (rev0436)

This file records how the unified EvidenceVault archive covers the prior upstream zip archives.

## Upstream zip digests

- `PACT_evolving_iter173.zip` sha256 `d10aa7b3d413280078fe91a3335d7d44db5dd2749570bac04cae3b0d149562ea`
- `docf_evolving_docs_v86_44_ai.zip` sha256 `24ac2442d9eb728c063c19f26f8ba1bb3d1b03fd4386a7c764ccb56f754ead2a`
- `ctg_evolving_docs_v219.zip` sha256 `6198d8e2c020a428b1715376d50b945a468c6501e55aaa22ae9b84fd3837d6c8`
- `zk_rtp_evolving_documents_portfolio_2026-02-28_v3.85draft_turn50.zip` sha256 `e753c11d23bba72be474fefd8f1ab6cec4b483e4bb4257eee157aac9036e1c2d`
- `zk_rtp_v2_02_archive_v2_02.zip` sha256 `8bccafc4b470769f06ea5ad4793ed548ebdecea215c9a66b9e624081f53579d7`
- `ocf_llm_paper_evolving_current_v264.zip` sha256 `882889866d6c7c9cd7bf40a7b5e9e8430360b871860d17816050e76c56096c78`
- `streamfold_evolving_docs_v3_26.zip` sha256 `9358b3dbec9b2179a1037e803d2df7a5ea05c646ad86c6de0bda300c5851e09b`

## Where each upstream archive lands

- `streamfold_evolving_docs_v3_26.zip` → curated StreamFold extracts under `artifacts/curated/streamfold/` plus legacy renders under `renders/legacy_pdfs/streamfold/`
- `docf_evolving_docs_v86_44_ai.zip` → `sources/docf/`
- `ctg_evolving_docs_v219.zip` → `sources/ctg/`
- `zk_rtp_evolving_documents_portfolio_2026-02-28_v3.85draft_turn50.zip` → curated zk-RTP portfolio extracts under `artifacts/curated/zkrtp_v2/` plus legacy renders under `renders/legacy_pdfs/zkrtp_portfolio/`
- `zk_rtp_v2_02_archive_v2_02.zip` → curated zk-RTP v2 extracts under `artifacts/curated/zkrtp_v2/` and `certs/curated/zkrtp_v2/` plus legacy renders under `renders/legacy_pdfs/zkrtp_v2/`
- `ocf_llm_paper_evolving_current_v264.zip` → `sources/ocf_llm/`
- `PACT_evolving_iter173.zip` → `sources/pact/`

## Restored legacy PDF renders

A small curated set of legacy PDFs from upstream is kept under `renders/legacy_pdfs/`, with exact byte-identical mirrors pruned when one canonical retained path already remains.

Curated lookup points may be compact path indexes when the retained source or cert tree already owns the exact bytes.
