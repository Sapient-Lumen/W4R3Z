# Next revision pointer — rev0092

Suggested next codename: `nativeloadloop-callcanary-dispatchfence`.

Suggested focus:

- route rev0092 evidence back through `nativeload.py` without bypassing selection, promotion, and fallback-journal checks;
- add a no-network native-call canary that preserves Python as oracle;
- make the dispatch fence explicit before any future real native call.
