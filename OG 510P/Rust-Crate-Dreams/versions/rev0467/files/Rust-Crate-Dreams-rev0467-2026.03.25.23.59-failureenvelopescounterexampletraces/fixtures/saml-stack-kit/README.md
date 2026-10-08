# saml-stack-kit fixtures (starter)

Goal: a redistributable conformance and regression corpus that exercises:
- signature verification (valid/invalid)
- signature wrapping attack patterns (expected reject)
- assertion condition edge cases (clock skew, expiry, audience mismatch)

Keep fixtures synthetic where possible to avoid shipping real IdP metadata.
