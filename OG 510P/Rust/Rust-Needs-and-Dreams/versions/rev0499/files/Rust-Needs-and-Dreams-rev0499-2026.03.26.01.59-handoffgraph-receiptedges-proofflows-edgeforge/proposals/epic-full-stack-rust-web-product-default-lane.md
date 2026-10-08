# Epic proposal: Full-stack Rust web product default lane

## Problem
The archive can now answer two neighboring but different questions:
- what should a **browser-first Rust web app** start with?
- what should a **general Rust HTTP/service** start with?

It still could not answer the very common question in between:
**what should a serious full-stack Rust web product start with when Rust owns both the UI and server halves?**

That gap matters because the hard parts are not only “pick a framework.”
They are:
- dual-target build coordination;
- SSR/hydration mode honesty;
- server-function versus public-API boundary discipline;
- auth/session/cookie boundaries;
- and deploy/origin/base-path truth.

## Proposed contribution
Publish and maintain a bounded defaults-corpus lane for:

**conservative full-stack Rust web product (2026 Q1)**

with:
- one design note;
- one maintained default card;
- one renewal receipt;
- and the usual frontier/queue/meta updates.

## Intended default
The current conservative answer for this bounded lane is:

**Leptos SSR + Axum + `cargo-leptos`**

with **Dioxus Fullstack** and **Leptos + Actix** kept as serious alternatives, and with the browser-only CSR lane explicitly kept separate.

## Why this is worthy
This is worthy because it turns one of Rust’s most common fuzzy adoption conversations into a **bounded, reviewable, freshness-aware answer** instead of more tacit knowledge.

It does not try to bless “the Rust web stack.”
It does something more useful:
- preserve the web lane split that current docs already expose;
- publish one boring current answer for one recurring product class;
- keep serious alternatives visible;
- and make the review receipts portable and renewable.

## Artifacts
- `design/full-stack-rust-web-product-default-lane.md`
- `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
- `evidence/conservative-full-stack-rust-web-product-2026Q1-renewal-2026-03-22.md`

## Non-goals
- universal Rust web governance;
- replacing project-specific architecture briefs;
- hiding API/auth/deploy decisions behind a framework name;
- or silently turning server functions into a replacement for every public API contract.
