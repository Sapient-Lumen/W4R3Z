# Wake from amnesia — rev0097

Start here after a context reset:

1. Read `docs/1008-rev0097-nativearchivereplay-promotereview-spinecompact.md`.
2. Run `pytest tests/test_rev0096_callarchive_promotedeny_shadowgc.py tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py`.
3. Run `python scripts/evidence/run_micro_simulation.py` and `python scripts/evidence/run_cube_audit.py`.

Remember the core rule: matching native shadow results can be archived and replayed, but promotion remains held and Python fallback remains authoritative.
