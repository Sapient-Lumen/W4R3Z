# Scenario: nightly Cargo finding must remain a separate channel

A nightly `cargo::implicit_minimum_version_req` warning is useful, but it is not the same channel as stable rustc or Clippy findings.
The bundle must keep that provenance explicit so downstream review can decide whether it is blocking or advisory.
