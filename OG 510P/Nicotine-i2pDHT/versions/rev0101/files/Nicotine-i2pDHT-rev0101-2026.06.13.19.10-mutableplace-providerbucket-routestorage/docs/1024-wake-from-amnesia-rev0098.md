# Wake from amnesia — rev0098

Start with `docs/1018-rev0098-nativebranchclose-promotearchive-policyseal.md`.

The important bit: rev0098 closes the current native/GCC branch as shadow-only. The archive says review happened; the policy says shadow-only; the branch-close join says future promotion must be a new branch.

Current smoke lane:

```bash
python scripts/evidence/check_surfaces.py
python scripts/evidence/run_micro_simulation.py
python scripts/evidence/run_cube_audit.py
pytest tests/test_rev0097_nativearchivereplay_promotereview_spinecompact.py tests/test_rev0098_nativebranchclose_promotearchive_policy.py
```
