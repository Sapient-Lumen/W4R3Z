# Crate health routing boundaries — 2026-03-22

This note keeps **P-0011 Crate Health Contract Kit** from collapsing operational stewardship routing into adjacent lanes.

## The sharper seam

Within **P-0011**, keep these truths separate:

1. **broad health profile exists**,
2. **maintenance coverage exists**,
3. **work-routing exists**,
4. **response-channel posture exists**,
5. **continuity backstop exists**,
6. **succession / eventual handoff exists**.

They are related, but they are not the same claim.

## What belongs in the routing seam

The routing seam is about questions like:

- where should different kinds of maintenance work go,
- which routes are public vs private,
- which owner class is expected to respond,
- what backup or fallback exists,
- and whether downstream users can still find the right path when the primary maintainer is absent.

## What it is not

### 1. Not maintenance coverage by itself

Coverage asks whether a duty class is covered.
Routing asks **where that duty enters the system and who is expected to catch it**.

A crate can claim `security_incident_response = covered` while still failing to say whether reports go to public issues, private vulnerability reporting, email, or pure manual review.

### 2. Not succession / eventual handoff by itself

Succession asks who could take over later.
Continuity asks what keeps the crate responsive **now**, during absence, overload, or transition.

A named successor crate or backup maintainer is not the same as a live backstop for triage and incident response.

### 3. Not trust or security posture by itself

Trusted Publishing, the crates.io Security tab, RustSec visibility, and private vulnerability-reporting support are adjacent substrate.
They do not by themselves answer where docs fixes, CI failures, release problems, or ordinary bug reports go.

### 4. Not host-platform workflow policy

Issue forms, discussion boards, CODEOWNERS, branch-protection rules, and private vulnerability-reporting are useful host substrate.
**P-0011** owns the normalized contract above them, not the host-specific mechanics themselves.

### 5. Not maintainer-funding policy

Funding pages, sponsor links, and foundation support matter for sustainability.
They should inform reviews, but **P-0011** should not become a donor-score or payroll inference engine.

## Working rule for future passes

When a future pass sharpens **P-0011**, it must say explicitly whether it is adding:

1. health-profile truth,
2. maintenance-window truth,
3. succession-map truth,
4. support-intent truth,
5. maintenance-coverage truth,
6. work-routing truth,
7. response-channel truth,
8. continuity-backstop truth,
9. or health-check consistency truth.

Do **not** let the archive quietly rephrase any of the following into one fake “maintained” claim:

- `CODEOWNERS` exists,
- issues are enabled,
- a `SECURITY.md` file exists,
- private vulnerability reporting exists,
- an org owns the repo,
- or a funding link exists.

## Sources

- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustfoundation.org/strategic-plan/
- https://docs.github.com/articles/about-code-owners
- https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability


## Imported-signal boundary

`registry-signal.import` belongs in **P-0011** only as stewardship-adjacent context.
It exists to keep imported crates.io / GitHub facts visible and auditable.
It does **not** authorize the crate to flatten those facts into support promises.

Working rule:
- Security tab visibility is security context, not incident-response routing by itself.
- Trusted Publishing Only Mode is publish-identity hardening, not release-owner declaration.
- CODEOWNERS is review-routing substrate, not universal maintenance routing.
- private vulnerability reporting is a confidential security intake route, not broad support posture.
- repository transfer is host-state movement, not automatic continuity equivalence.
