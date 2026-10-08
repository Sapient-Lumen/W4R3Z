# Scenario — RSX markup changes use UI hot reload, not general Rust code patching

This scenario exists because Dioxus now documents RSX hot-reload as a fast path that can update UI structure and styling without recompiling the whole app.

The point of this fixture is to keep **UI-only reload** separate from a broader claim that arbitrary Rust function edits are hotpatch-safe.
