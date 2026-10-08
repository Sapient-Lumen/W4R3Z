# Wake from amnesia — rev0084

Start here if returning to the cube after rev0084:

1. Read `docs/878-rev0084-parserhold-sanitizerplan-nativebudget.md`.
2. Read `parserhold.py` to see why hostile-byte parsing stays Python-owned.
3. Read `sanitizerplan.py` to see how native leaf candidates earn development sanitizer evidence.
4. Read `nativebudget.py` to see how native optimization stays scarce and fallback-bound.
5. Run `tests/test_rev0084_parserhold_sanitizer_nativebudget.py` before changing native boundaries.

The current direction remains Python-first: GCC is allowed to accelerate leaves, not to interpret hostile bytes or decide protocol truth.
