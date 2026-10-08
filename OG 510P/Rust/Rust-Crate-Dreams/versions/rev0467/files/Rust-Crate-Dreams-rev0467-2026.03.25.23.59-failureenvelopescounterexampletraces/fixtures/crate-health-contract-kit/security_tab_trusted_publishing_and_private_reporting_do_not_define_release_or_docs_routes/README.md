# Security tab, Trusted Publishing, and private vulnerability reporting still do not define release or docs routes

This scenario protects a common false reassurance pattern.

The crate surface looks polished:
- crates.io shows a Security tab,
- Trusted Publishing Only Mode is enabled,
- SLOC and `pubtime` are visible,
- and GitHub private vulnerability reporting is enabled.

Those are useful imported stewardship signals.
They still do **not** tell another person:
- who owns release orchestration,
- where documentation freshness issues should go,
- whether CI breakage has an explicit backup route,
- or whether maintainers intended those host signals to imply broader support.

The fixture keeps imported stewardship context separate from declared routing truth.
