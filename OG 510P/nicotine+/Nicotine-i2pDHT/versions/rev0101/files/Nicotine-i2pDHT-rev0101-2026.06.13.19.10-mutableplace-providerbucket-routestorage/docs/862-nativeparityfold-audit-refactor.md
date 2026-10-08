# nativeparityfold audit/refactor

`nativeparityfold.py` is the rev0082 current-path audit.

It checks that the new parity, ABI, fallback-seal, test, and documentation surfaces are present and visible.  It also preserves the rev0081 `nativeboundaryfold.py` predecessor so the GCC answer remains traceable instead of being overwritten by the next native seam.

The audit/refactor point of this revision is not more native code.  It is making native selection itself auditable.
