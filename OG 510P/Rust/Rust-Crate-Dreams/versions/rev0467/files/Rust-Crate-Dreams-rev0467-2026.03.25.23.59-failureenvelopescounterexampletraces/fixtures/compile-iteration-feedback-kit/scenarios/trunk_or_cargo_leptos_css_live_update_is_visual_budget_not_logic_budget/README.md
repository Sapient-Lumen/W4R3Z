# Trunk or cargo-leptos CSS live update is a visual budget, not a logic budget

This scenario exists to force **P-0537** to keep readiness classes honest.

Leptos-adjacent docs explicitly say edited CSS files can be updated immediately in the browser with the live-reloading features of `trunk` and `cargo-leptos`.
That is useful, but it is a browser-visible feedback route, not automatically a general Rust-logic budget pass.
