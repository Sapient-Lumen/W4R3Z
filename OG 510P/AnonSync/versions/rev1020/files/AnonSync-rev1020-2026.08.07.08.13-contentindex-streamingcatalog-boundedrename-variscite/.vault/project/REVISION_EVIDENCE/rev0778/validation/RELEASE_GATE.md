# Rev0778 release gate

Required source and runtime validation passes. Package checks are pending final staging.

- Fresh GCC Debug: 40/40 CTest; full suite repeated three times.
- Direct: authority 98, support 61, runtime policy 38, schema 58, domain 588, lifecycle 49.
- Stress: 9,800/9,800 authority checks.
- Audits: mutex capability 63/63; transaction stack 45/45; payload authority 38/38; authorizer ownership zero violations.
- Optional focused profiles: GCC Release, GCC ASan/UBSan, and Clang all pass 2/2.
- Final package manifest, safety, and ZIP-integrity fields are populated after staging.
