# Gap: Publisher / Source Identity (organizational claims, namespace control, registry source truth)

## Summary
Rust’s package ecosystem now has **several different identity planes**, but they still do not compose into one reviewable story:
- human-facing organization/project identity,
- publish authority (owners, trusted publishers, namespace rights),
- registry/source identity (which source was configured, mirrored, or replaced),
- and downstream trust/policy/install conclusions.

Today those planes are easy to confuse.
A crate name prefix is treated like an org claim, a Trusted Publishing workflow is treated like a full trust verdict, a mirror is treated like a distinct registry, and an alternate registry entry is treated like enough provenance on its own.

The real missing contribution is a **portable publisher/source identity layer** that can answer:
- who or what may publish,
- how that authority was established,
- which source a package or install path came from,
- what namespace or claim semantics apply,
- and which later trust or policy conclusions are merely downstream consumers.

## Why now
Recent Rust signals make this seam more concrete than it used to be:
- crates.io now supports GitLab CI/CD for Trusted Publishing, plus Trusted-Publishing-only mode, strengthening issuer-backed publish authority rather than just long-lived token use;
- Cargo’s registry-authentication model now requires configured credential providers for authenticated registries, which means alternate-registry identity is no longer just “paste a URL into config”; 
- Cargo registries and source replacement remain separate mechanisms, and source replacement explicitly assumes exact equivalence rather than a new identity plane;
- RFC 3243 gives Rust an accepted optional-namespaces design, and the 2025H2 goal to implement open API namespaces says Cargo/compiler support is partially implemented while crates.io coordination is still needed;
- the Feb 2026 internals survey threads show the ecosystem is actively trying to reduce circular debate around org ownership, namespaces, and registry identity.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
- https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- https://internals.rust-lang.org/t/survey-of-organizational-ownership-and-registry-namespace-designs-for-cargo-and-crates-io/24027

## Where the seam is still awkward
Today the ecosystem mixes together several questions that should stay distinct:
1. **Human/project identity:** “Is this one of the crates from project X?”
2. **Publish authority:** “Who was actually authorized to publish this package/version?”
3. **Namespace/claim semantics:** “Is this crate name or namespace controlled, merely suggestive, or explicitly open to third parties?”
4. **Source identity:** “Did this come from crates.io, an alternate registry, or an exact-copy mirror/source replacement?”
5. **Trust/policy conclusions:** “Given all that, do we allow, warn, or require review?”

Because those are not captured portably, the same facts keep getting re-derived in ad hoc ways by registries, CI, internal policy, and support teams.

## What “good” looks like
A worthy contribution here is not “pick the one true namespace scheme”.
It is a reviewable identity substrate with at least:
- `publisher-report/v0` — owners / trusted-publisher issuers / publish-authority posture;
- `claim-report/v0` — project/org claims, namespace control posture, and explicit non-claims;
- `source-report/v0` — registry/source/mirror/replacement identity and auth posture;
- `publisher-source-pack/v0` — attachable bundle for package-admission, trust, and install consumers.

The winning version should:
- keep human org labels distinct from publish authority;
- keep alternate registries distinct from exact-copy mirrors/source replacements;
- support namespaces where available **without** requiring namespaces to express every valid org claim;
- let trust/policy/import consumers build on the identity facts instead of redefining them; and
- give Cargo users a humane UX for adding, verifying, and reporting sources without hand-editing config as the only path.
