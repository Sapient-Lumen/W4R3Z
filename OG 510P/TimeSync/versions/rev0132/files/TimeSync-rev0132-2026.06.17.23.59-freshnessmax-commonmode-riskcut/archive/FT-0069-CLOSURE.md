# FT-0069 closure — authorized verifier challenge boundary

FT-0069 asked whether TimeSync should define a minimal challenge boundary for salts/preimages or leave all disclosure workflow fully external.

rev0070 chooses a narrow middle path:

```text
TimeSync may carry a detached challenge/result/receipt record.
TimeSync must not carry salt or preimage material in ordinary exchange or evidence summaries.
TimeSync must not treat the challenge result as profile evidence or reassessment.
```

The result is `schema/authorized-verifier-challenge.schema.json` and `spec/33-authorized-verifier-challenge-boundary.md`.

The validator now rejects expired challenge responses, target commitments not present in referenced summaries, preimage/salt export attempts, challenge/disclosure receipts used as profile-obligation evidence, and malformed discovery-returned challenge results.
