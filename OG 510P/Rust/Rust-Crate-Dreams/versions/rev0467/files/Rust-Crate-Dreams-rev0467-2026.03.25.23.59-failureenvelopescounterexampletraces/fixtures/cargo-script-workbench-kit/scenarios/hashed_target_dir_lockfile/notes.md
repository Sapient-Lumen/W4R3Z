# Hashed target-dir and target-dir lockfile

This scenario captures the official single-file-package rule that the default target-dir lives under Cargo home and the lockfile lives there too.
A receiver should not mistake this for an ordinary workspace-local `target/` plus `Cargo.lock` story.
