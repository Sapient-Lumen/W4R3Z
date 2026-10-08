# Case study: Estonia’s individual verification (two-device pattern)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

Estonia is a prominent real-world deployment of national-scale internet voting. This note focuses on
the **individual verification** pattern: voting on one device (desktop) and verifying on another (smartphone).

## What Estonia does (high-level)

- Voter authenticates using ID-card / Mobile-ID / Smart-ID in the i-voting app.
- Votes are cast during an early voting period.
- Voters may **re-vote**; later votes supersede earlier ones.
- Voter can verify their cast vote using a separate **verification app**.

Official guidance describes both the voting flow and the verification (checking) flow.

## Verification mechanism (two-device)

- The voting client displays a QR code.
- The verification app scans it and shows (within a time window) which candidate/option was recorded.

## Security value

- Helps detect certain client-side manipulation (cast-as-intended) if the verifier device is independent.
- Helps detect certain server-side substitution for that voter within the verification window.

## Limitations (important)

- Individual verification typically answers “**recorded-as-cast** (for a window),” not full
  “**tallied-as-recorded**.”
- If both devices are compromised (or if malware times attacks), verification can fail.
- Verification windows and UX constraints can become attack surfaces (selective targeting).

## How this informs our design

- Keep “two-device verification” as a first-class pattern in `16-client-verification-patterns.md`.
- For a federated bulletin board, require verifiers to check inclusion against **witness-quorum checkpoints**
  (not just a single collection server).

## Primary references
See `references.md` for Estonia’s official guidance pages describing stages of i-voting and vote checking.