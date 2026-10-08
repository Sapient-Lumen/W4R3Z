# Wake from amnesia — rev0082

You are in `rev0082 — nativeparity-abiguard-fallbackseal`.

The previous revision answered the GCC question: keep protocol semantics in Python and compile only narrow leaf kernels.  This revision tests the next risk: a native leaf could compile, load, or appear faster while being wrong.

Read in order:

1. `docs/858-rev0082-nativeparity-abiguard-fallbackseal.md`
2. `docs/859-native-parity-before-selection.md`
3. `docs/860-abi-guard-load-boundary.md`
4. `docs/861-fallback-seal-native-quarantine.md`
5. `tests/test_rev0082_nativeparity_abiguard_fallbackseal.py`

Key local rule:

```text
Native code is selected only after parity, ABI, and fallback seal agree.
```
