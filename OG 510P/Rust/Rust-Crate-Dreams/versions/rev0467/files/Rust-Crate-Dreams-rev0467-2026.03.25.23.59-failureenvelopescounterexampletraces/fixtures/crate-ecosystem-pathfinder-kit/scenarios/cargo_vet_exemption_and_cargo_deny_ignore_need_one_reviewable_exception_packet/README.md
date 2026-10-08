# Scenario — cargo vet exemption and cargo-deny ignore need one reviewable exception packet

This scenario proves that a worthy front-door crate should not treat tool-local exceptions as the final answer.

Situation:
- the frozen decision still prefers a crate for the current task profile,
- Cargo Vet is using an exemption because audit backlog remains,
- cargo-deny is ignoring one advisory with a written reason,
- and the team still wants a portable packet that says who owns the risk, where it applies, when it expires, and what removes it.

What should happen:
1. import the frozen decision and the local exception evidence,
2. emit one `policy-exception.receipt.json`,
3. keep the support ceiling explicit,
4. emit one `exception-expiry.ticket.json`,
5. and refuse to retell the exception as general recommendation truth.
