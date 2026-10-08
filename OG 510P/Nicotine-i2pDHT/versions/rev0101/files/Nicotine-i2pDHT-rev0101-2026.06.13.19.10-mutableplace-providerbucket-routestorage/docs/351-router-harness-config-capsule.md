# Router harness config capsule

`routerharness.py` is the next no-network seam after `samprobe.py`.

It recognizes three modes:

```text
bundled_i2pd
external_sam
offline_no_router
```

The harness catches mistakes that would be costly after live I2P is wired:

- transient/ephemeral destination use;
- accidental HTTP/SOCKS proxy exposure;
- bundle-first `notransit` island defaults;
- unapproved non-loopback SAM endpoints;
- generated-config digest mismatch;
- SAM endpoint drift between probe and harness;
- session-only probe being treated as streaming proof.

The cube still supports external SAM, but bundle-first remains the default future product posture.
