# Proof obligation rev0081

Before native code can be trusted beyond lab status:

- Python reference must remain canonical.
- Native and Python results must match golden vectors.
- Native ABI must be stable and versioned.
- Inputs must be bounded.
- No cross-boundary heap ownership may occur.
- Sanitizer and fuzz lanes must exist for any untrusted-byte surface.
- Packaging must retain a fallback path when GCC/native build is unavailable.
