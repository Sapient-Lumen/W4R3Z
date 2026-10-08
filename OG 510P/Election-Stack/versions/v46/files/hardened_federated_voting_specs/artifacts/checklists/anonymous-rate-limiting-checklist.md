# Anonymous anti-abuse & rate limiting checklist (Privacy Pass profile)

- [ ] Anti-abuse tokens are **unlinkable** between issuance and redemption.
- [ ] Tokens are **context-bound** to election_id + gateway_id + purpose.
- [ ] Token verification occurs **before** expensive ZK ballot validation.
- [ ] Multiple independent issuers (or auditable single issuer with emergency fallback).
- [ ] Spent-token tracking is **append-only** and evidence-friendly (no silent denials).
- [ ] IP-based rate limiting is only a **coarse backstop**, not the primary control.
- [ ] Incident policy: token checks can be relaxed with **public signed notice**.
- [ ] Load tests include botnet floods + targeted region throttling attempts.
