# Next revision pointer rev0094

Suggested next seam: `nativefaultreplay-shadowgc-callledger`.

Potential work:

- replay native fault seals across restart;
- distinguish soft shadow evidence from hard native fault memory;
- add a call-ledger that keeps exact call-vector evidence without letting it authorize dispatch;
- audit the native branch spine for duplicate or stale root pointers.
