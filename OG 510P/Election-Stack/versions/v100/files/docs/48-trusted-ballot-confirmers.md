# Trusted ballot confirmers (hardware-wallet style confirmation)

**Track:** B (Remote return / hard-mode research)


This is a creative hardening option aimed squarely at the hardest problem: **client malware**.

Instead of trying to “secure the voter’s laptop/phone,” you move the critical action
(confirming the human-readable ballot) onto a **small, purpose-built confirmer**.

## Pattern

1. Voting device constructs a ballot and sends a **BallotConfirmRequest** to the confirmer.
2. Confirmer displays the **human-readable selections** on its own trusted screen.
3. User approves; confirmer produces a signature / authorization tied to the ballot commitment.
4. Only then can the ballot be accepted by the bulletin board.

This resembles how hardware wallets prevent malware from changing a cryptocurrency transaction.

## Benefits

- Malware on the voting device cannot silently change the vote without the confirmer showing the wrong selection.
- Confirmer TCB can be tiny: display + confirm + sign.

## Risks / hard parts

- Distribution at scale, accessibility, replacement and recovery.
- Side channels: the confirmer must not leak vote via timing or radio emissions.
- Coercion: a coercer can still watch you approve; does not solve coercion.

## Minimal viable design rules

- Confirmer keys must be hardware-backed and non-exportable.
- UI must always display full choices (no ellipses or scrolling ambiguity).
- The authorization must bind to:
  - election id
  - ballot definition hash
  - encrypted ballot commitment
  - revote counter (if revoting)

## Where this fits

- Strongest option for remote ballot return if you insist on it.
- Also useful for high-risk populations (e.g., activists, diaspora) even if general voters use simpler flows.

## Open questions

- Can the confirmer be a commodity device with a hardened app? (Often: no.)
- Can we embed confirmer capability into an existing credential (e.g., smartcard with display)?
- What is the governance model for manufacturing and audits?
