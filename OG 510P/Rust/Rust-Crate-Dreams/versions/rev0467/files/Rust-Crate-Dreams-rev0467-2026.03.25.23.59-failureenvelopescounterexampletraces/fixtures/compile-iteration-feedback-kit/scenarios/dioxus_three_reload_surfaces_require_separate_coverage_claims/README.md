# Scenario — Dioxus exposes three reload surfaces, not one broad hot-reload claim

This scenario freezes the fact that Dioxus documents RSX hot-reload, asset hot-reload, and experimental Rust hot-patching as distinct surfaces.
A fast markup or CSS update should not masquerade as broad Rust-code live-update coverage.
