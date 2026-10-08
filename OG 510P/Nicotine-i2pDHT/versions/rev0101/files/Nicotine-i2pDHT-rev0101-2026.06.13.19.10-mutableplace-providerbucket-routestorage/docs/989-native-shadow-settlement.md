# Native shadow settlement

A native result that matches the Python oracle may now be settled as local evidence.  Settlement requires the shadow-call report, result-diff report, and fault-seal report to agree at one exact component/profile/operation/request boundary.

Settlement keeps these denials explicit:

- no native call permission;
- no native result authority;
- no native parser, crypto, transport, persistence, policy, or mutability ownership;
- no forgetting fallback, tombstone, quarantine, or crash memory.
