# Epic proposal: Model Productization Stack

## Thesis
Rust needs a **portable, boring model-product boundary** above runtimes and formats.
The problem is no longer “can Rust load or run models?”
The problem is that model identity, tokenizer identity, artifact variants, backend/device posture, acquisition/cache/auth activation, and support/docs truth are still too often implicit.

## Why this would count as worthy
This contribution would help multiple major Rust lanes at once:
- scientific / numerical applications;
- local AI and edge inference;
- service-side inference products;
- agentic products that attach models and tokenizers dynamically;
- client and desktop products that bundle or fetch models;
- polyglot products that ship Rust model logic behind another host surface.

It would be boring in the right way:
- reviewable;
- importable by other tools;
- format-aware instead of format-denying;
- backend-aware instead of benchmark-theater;
- honest about cache/auth/runtime activation;
- useful to support and release teams, not only framework authors.

## Deliverables
- `design/model-productization-stack.md`
- `design/model-productization-pilot-program.md`
- `model-surface/v0` family refinements
- comparison pilots across Candle / Burn / `ort` / `tract`
- model-support/docproof import examples

## First proof bar
A first serious proof should show that one Rust project can publish a `model-pack/v0`-style bundle that keeps:
- model identity,
- tokenizer profile,
- artifact-set truth,
- backend/runtime capability profiles,
- acquisition/cache/auth posture,
- and checked support/docs evidence

all distinct while still being reusable by service, agent, scientific, and support consumers.

## Non-goals
- universal model serving framework;
- universal weight-format abstraction;
- universal hub or marketplace;
- replacing runtime-specific innovation with lowest-common-denominator metadata.
