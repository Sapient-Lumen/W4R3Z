# Scenario — virtual workspace needs `[workspace] resolver = "3"` to activate fallback

This scenario exists to prove that **policy intent** and **policy activation** are different things.

## Situation

- a repo contains a virtual workspace root;
- one or more member packages use `edition = "2024"` and the team expects the MSRV-aware resolver behavior that goes with resolver v3;
- but the root workspace never sets `[workspace] resolver = "3"`.

## Expected artifact truth

- `policy-activation.receipt` must record `expected_policy = "fallback"` and `observed_policy = "allow"` or another non-active state if that is what Cargo actually used;
- the receipt must say the workspace kind is `virtual_workspace`;
- the receipt must identify the resolver source as a default/root configuration problem rather than pretending the policy was active because a member crate used the 2024 edition.
