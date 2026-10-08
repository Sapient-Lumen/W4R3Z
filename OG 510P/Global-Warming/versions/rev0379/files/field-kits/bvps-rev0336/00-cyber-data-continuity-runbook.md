# BVPS rev0336 cyber/data continuity field kit

Use this runbook to capture local or anonymized proof without exposing credentials, network topology, IP addresses, secret keys, account names, vendor confidential details, or security-sensitive diagrams.

Minimum packet flow:

1. Assign owner/verifier and packet scope.
2. Hash every original artifact.
3. Create public-safe surrogate with sensitive annex link.
4. Record source clock, capture clock, and system clock offsets.
5. Classify packet as rejected, hold/no-upgrade, context/no-upgrade, accepted reopen signal, or candidate for adjudication.
6. Route candidates to CAP/retest/verifier before any readiness claim.

Never publish credentials, MFA seed material, tokens, API keys, IP ranges, firewall rules, VPN details, physical security details, or vendor incident confidential details.
