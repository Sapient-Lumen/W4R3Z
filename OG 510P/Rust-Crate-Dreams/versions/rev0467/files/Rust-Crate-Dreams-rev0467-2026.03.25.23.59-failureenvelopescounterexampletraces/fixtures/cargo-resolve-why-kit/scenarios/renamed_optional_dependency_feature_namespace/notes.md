# Scenario: renamed optional dependency keeps the local feature namespace

Why this matters: the package on the registry is `foo`, but the subject manifest depends on it as `bar = { package = "foo", optional = true }`. A receiver-facing resolver bundle should preserve that the user-facing feature token is `bar`, not `foo`, and that metadata / registry surfaces describe the rename differently.
