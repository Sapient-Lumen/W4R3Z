# Native optimization budget

`nativebudget.py` makes native optimization scarce.

The budget admits a native demand only when:

- parser hold accepts Python ownership,
- sanitizer plan accepts the native leaf posture,
- the component is explicitly allowed,
- Python fallback remains available,
- the demand stays within call-site, estimated-call, and input-size limits,
- the demand does not touch parsing, crypto, transport, persistence finality, policy authority, or protocol truth.

This keeps native code useful without letting performance work silently become design authority.

needle: native budget
