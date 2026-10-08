# Scenario: federated bundle allowlist and local-only policy must not share peer-acceptance claims

This scenario protects another easy lie:

> “the service uses federation-aware SPIFFE verification, so trust-domain scope is obvious.”

A subject that accepts a reviewed allowlist of foreign trust domains is meaningfully different from one that is local-only.
Those subjects may also differ in whether peer identity is merely verified or actually returned to the application.
