# ADR 0200 — nativeloadloopfold current revision audit

Accepted: rev0093.

The native branch now uses `nativeloadloopfold.py` and `nativefoldspine.py` to keep the GCC/native line auditable from rev0081 through rev0093.

Rationale: the native branch has many hold states; fold audit prevents them from becoming hidden permissions.
