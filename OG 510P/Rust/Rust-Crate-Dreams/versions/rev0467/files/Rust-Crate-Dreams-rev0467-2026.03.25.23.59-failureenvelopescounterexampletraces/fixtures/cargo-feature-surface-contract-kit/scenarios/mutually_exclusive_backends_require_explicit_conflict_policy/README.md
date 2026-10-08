# Scenario — mutually exclusive backends require explicit conflict policy

Focus: feature pairs like `native-tls` and `rustls` must not be left as undocumented folklore when the crate intends them to be exclusive.

Feature-surface reading: if the crate cannot make the backends compose, it owes the user an explicit compile-time or precedence policy.
