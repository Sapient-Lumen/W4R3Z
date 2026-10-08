# LLM maintainer bootstrap

You are looking at a speculative DHT design datacube. Do not treat it as production software.

Current revision: rev0013 `proofhandshake-headwitness-latencyforge`.

## Scope

The cube designs a generic DHT above I2P. Future applications are consumers. The current turn is implementation-first and risk-first: it does not add live SAM/I2P transport, and it does not return to application integration.

## Current center

rev0013 starts from several hard surfaces:

1. **Provider proof handshakes** — a signed provider record is still only a claim. The cube now tests challenge-bound proof transcripts, wrong-content rejection, useful refusal, replay rejection, deadlines, and metadata exposure budgets.
2. **Mutable head witness pressure** — signed heads can be stale, forked, or broken-prev. The cube now tests path-family diversity, previous-link discipline, garden witness statements, and accept-with-watch behavior.
3. **Latency forge** — fake SAM-like transport pressure tests timeouts, useful refusals, captured fast windows, retries, and family-diverse responses before live transport exists.
4. **Cube audit/refactor** — the cube now prunes transient cache surfaces and writes a non-failing audit report for duplicate historical numbering and near-duplicate module names.

## Read first

1. `START_HERE.md`
2. `docs/108-wake-from-amnesia-rev0013.md`
3. `docs/102-rev0013-proofhandshake-headwitness-latencyforge.md`
4. `src/i2p_dht_lab/proofhandshake.py`
5. `src/i2p_dht_lab/headwitness.py`
6. `src/i2p_dht_lab/latencyforge.py`
7. `src/i2p_dht_lab/cubeaudit.py`
8. `tests/test_rev0013_proof_head_latency_audit.py`
9. `CLAIM_SURFACE.json`

## Preserve these principles

- DHT is control plane, not file store.
- Mutable heads are signed, history-aware observations, not voted truth.
- Provider records are claims, not semantic availability.
- Provider confirmation has a metadata cost.
- Garden nodes give capacity but do not author truth.
- Witness receipts are evidence, not quorum.
- Useful refusal is a positive capacity signal when signed, bounded, and local.
- Semantic lies cost more than silence.
- Path-family rotation comes before greedy speed when testing risky answers.
- Tests are design objects; wake-from-amnesia docs are part of the artifact.
