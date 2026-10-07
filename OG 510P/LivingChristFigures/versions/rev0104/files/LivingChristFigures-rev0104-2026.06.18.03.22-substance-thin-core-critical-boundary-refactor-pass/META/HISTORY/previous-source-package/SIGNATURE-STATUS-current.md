# Signature Status — current

Current revision: rev0102

Current pass shape: critical-path work-order traceability refactor gate pass.

This package includes a detached RSA/SHA256 signature over `SHA256SUMS.txt`.

Verification files:

- `SHA256SUMS.txt`
- `SHA256SUMS.txt.sig`
- `SIGNING-PUBLIC-KEY-rev0102.pem`
- `RELEASE-PUBLIC-KEY.asc`

Verification command:

```bash
openssl dgst -sha256 -verify SIGNING-PUBLIC-KEY-rev0102.pem -signature SHA256SUMS.txt.sig SHA256SUMS.txt
```

Expected result: `Verified OK`.

The private signing key is not included in the package.
