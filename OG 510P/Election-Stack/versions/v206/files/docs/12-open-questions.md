# Open questions / explicit non-claims

**Track:** A (Deployable core)


If you want a system that survives real-world adversaries, you must name what you **do not** solve.

## 1) Coercion resistance for unsupervised remote voting
- Revoting helps only if voters can reliably re-vote later in private.
- Stronger schemes exist (fake credentials, code sheets/return codes), but are heavy and easy to implement incorrectly.
- **Non-claim:** This pack does not claim coercion resistance for unsupervised remote voting.

## 2) Client malware
- Any solution that relies solely on the voter device UI is vulnerable.
- **Non-claim:** “E2E verifiable” does not automatically mean “safe against client compromise.”

## 3) Identity / eligibility without surveillance
- Strong credentials (citizen keys) risk building a turnout‑tracking or identity‑linkage system.
- We outline options (blind signatures / anonymous credentials), but deploying them politically and legally is non-trivial.

## 4) Denial of service
- You cannot guarantee availability on election day.
- You can only guarantee **safe failure modes** and a robust fallback (paper / in-person / extended window).

## 5) Governance
- Who runs federation nodes and witnesses? What legal obligations? How are compromises handled?
- This is as important as the crypto.

## 6) Certification path
- For U.S. contexts: VVSG 2.0 certification and state certification regimes matter.
- Build for evaluability: logs, test vectors, reproducible builds, and measurable requirements.