# Scenario — toolchain and support drift block a like-for-like MC/DC trend claim

This scenario protects the distinction between **a newer bundle exists** and **the newer bundle can honestly be trended against the older one**.

LLVM’s current docs say raw profiles are not forward- or backward-compatible and coverage mappings are not forward-compatible, while Rust’s own coverage substrate keeps branch/MC/DC support caveat-heavy.
A crate should therefore emit a `comparison-basis.receipt.json` before claiming that one MC/DC result improved over another.
