# rev0087 — nativeload-crashledger-perfguard

This revision keeps the optional GCC thread narrow. It does not add new native authority; it adds lifecycle brakes around the tiny leaf kernels already allowed by previous revisions.

Strong sentence:

> A promoted native leaf is not safe because selection passed; loading, crash memory, and performance observations are separate protocol boundaries.

New surfaces:

- `nativeload.py` — no-network load permission after native selection and promotion bind.
- `nativecrashledger.py` — sticky crash/fault memory that forces fallback/quarantine.
- `nativeperfguard.py` — performance data as operator hint only, never selection authority.
- `nativelifecyclefold.py` — audit/refactor fold pinning rev0087 to the public surface.

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production native ABI/loader, no native parser/crypto, no global reputation, no mutable-head consensus, and no Nicotine+ patch.
