# Scenario: RustSec RSS is required when blog posts are not comprehensive

This scenario protects against one ordinary lie:

- the team watches the Rust blog,
- it assumes that is enough to hear about malicious crates,
- but the crates.io team has explicitly said routine malicious-crate removals will no longer each get a blog post and that RustSec advisories / RSS are the always-on path.

The fixture keeps `notification-channel.report` separate so blog visibility does not masquerade as comprehensive malware-watch coverage.
