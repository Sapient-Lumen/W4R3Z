# rev0095 — shadowsettlement-admission-callledger

This revision takes rev0094's native shadow-call/result-diff/fault-seal evidence and adds the next exact boundary: a matching shadow result can be settled as evidence, admitted only to a held shadow slot, and recorded in a call ledger that keeps the live route on Python.

Strongest sentence:

> A matching native shadow result is not a native call path; it is restart-sticky evidence until settlement, admission, and call-ledger memory all preserve Python authority.

New surfaces:

- `nativeshadowsettlement.py` joins shadow-call, result-diff, and fault-seal reports.
- `nativeadmission.py` admits only a side-effect-free shadow slot, never parser/crypto/transport/policy surfaces.
- `nativecallledger.py` makes the Python route sticky after native shadow evidence exists.
- `nativesettlementfold.py` audits the current rev0095 surface.

Nonclaim: this is still not native dispatch permission.
