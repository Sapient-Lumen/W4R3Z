# Machine fix applies but manifest feature rename remains

Focus: source-level rename suggestions can be machine-applied, but the upgrade still requires a `Cargo.toml` feature or dependency-policy edit that no source fixer witnessed.
This fixture exists to prove that “cargo fix succeeded” is not the same as “the upgrade lane is fully automated.”
