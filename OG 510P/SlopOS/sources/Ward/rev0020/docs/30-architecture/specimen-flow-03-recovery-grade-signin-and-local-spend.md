# Specimen flow 03 — recovery-grade sign-in, session warrant, and local spend

This specimen exists to stop Ward from compressing sign-in, session hardening, and spendable trust into one success event.

## Scenario
A user signs in with a synced passkey on a website. The resulting session is later hardened with a device-bound session mechanism. A local service is considering whether that combined state is enough to allow a higher-value action.

## Desired separations
- **credential class** — synced passkey, device-bound passkey, security key, or other
- **approval locus** — where the human approved the action
- **account relation** — which local or remote account relation was established
- **session warrant** — what theft-resistance is currently in place for the session
- **spend gate** — the local rule that translates the above into a real consequence

## Flow sketch
1. The user completes a relying-party scoped sign-in ceremony with a synced passkey.
2. Ward records a custody posture that includes recovery and sync facts.
3. The site or local platform establishes a session warrant using a device-bound session mechanism.
4. A higher-value action asks for local spend.
5. The spend gate decides:
   - allow with present session warrant,
   - require step-up using a stronger credential class,
   - require local re-approval,
   - or deny.

## Why this specimen matters
Without it, Ward is tempted to lie in exactly the historical way that older systems lied:
- “the user authenticated” becomes
- “the session is good” becomes
- “the account is trusted for everything”.

## Promotion test
This specimen is promotable only if the same nouns can still survive:
- a fully device-bound path,
- a cross-device approval path,
- and a path where the session is hardened but the higher-value action still requires a stronger local consequence.
