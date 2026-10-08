# Frontier salience snapshot — 2026-03-22-164

This refresh keeps the support-contract frontier centered on toolchain, interop, MSRV, dependency lifecycle, and crate stewardship, but promotes **P-0011 Crate Health Contract Kit** back into the lead cluster.

## Ranked frontier after the latest scan

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0121 FFI Boundary & Bindings Conformance Kit**
3. **P-0036 MSRV Workspace Lab**
4. **P-0011 Crate Health Contract Kit**
5. **P-0535 Dependency Lifecycle Transition Kit**
6. **P-0532 Async Runtime Assurance Profile Kit**
7. **P-0434 Sanitizer Profile & Evidence Kit**
8. **P-0486 Debuggability Support Contract Kit**
9. **P-0503 Assurance Case Workbench Kit**
10. **P-0017 Trust Lens**

## Why P-0011 moves upward again

Recent official signals make one missing layer unusually explicit:

- the January 2026 maintenance post says the real work of maintenance spans triage, CI failures, security incidents, docs upkeep, review, and contributor enablement;
- the 2025 State of Rust survey says concern about maintainer/developer support ticked upward;
- the Rust Foundation strategic plan names **Sustainable Maintenance** as a core pillar;
- and crates.io’s current signal surface is richer than before, but still does not tell downstream users where maintenance work goes or what continuity exists if the obvious maintainer disappears.

That combination points toward a crate that helps teams publish **work routes**, **response-channel posture**, and **continuity backstops** instead of one vague “maintained” label.

## Planning conclusion

For the next pass or two, prefer:

1. keeping **P-0484**, **P-0121**, **P-0036**, **P-0011**, and **P-0535** in the lead cluster,
2. treating **P-0011** as the stewardship lane above registry signals and below migration/funding/social policy,
3. and resisting the temptation to express crate health as just a ranking or just a security/trust import.

## Freshness anchors

- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustfoundation.org/strategic-plan/
- https://openssf.org/blog/2025/09/23/open-infrastructure-is-not-free-a-joint-statement-on-sustainable-stewardship/
- https://docs.github.com/articles/about-code-owners
- https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability
