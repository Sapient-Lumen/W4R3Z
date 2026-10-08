# Rev0987 research note

This revision was driven by the operator's clarified workflow rather than a new
external protocol dependency: Linux/headless, multi-terabyte media trees,
mandatory delta transfer, mandatory selective sync, operator-owned credentials,
and conservative best-effort retention.

The principal open design questions remain target-scale memory and disk
behavior, content-defined or multilevel delta for insertion-heavy files,
placeholder and quota semantics, rename/move identity, directory semantics,
conflict presentation, and an Android storage/lifecycle adapter. Rev0987 does
not convert those research directions into product claims.
