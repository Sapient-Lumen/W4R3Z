# Remedy-hardening-attestation durable-closure contract sheet page — rediscovery surfaces, latent survivors, and invalidator budget

## Purpose

This contract sheet exists so the archive can say exactly what it means for a closure claim to stay durable after the initial horizon closes.
It should prevent the operator from silently collapsing `closed now` into `safe if rediscovered later`.

## Required sections

The page must render the same sections in the same order:

1. **Closure durability horizon**
2. **Rediscovery surfaces and latent survivor inventory**
3. **Invalidator budget and re-open rules**
4. **Strongest honest durable-closure sentence**

### 1) Closure durability horizon

This section must show:

- initial closure verdict reference
- durability horizon length or class
- whether the claim is meant to survive routine rediscovery, hostile resurfacing, or both
- tolerated late-survivor classes if any
- required re-check cadence if durability is conditional

The operator must be able to answer: **for how long, and against what resurfacing conditions, is this closure claim meant to stay honest?**

### 2) Rediscovery surfaces and latent survivor inventory

This section must list every surface from which stale material could reappear, including at least:

- disconnected local folders still present in a filesystem
- selective-sync placeholders or refetch-capable shells
- hidden archive directories and restored versions
- expired-transfer UI remnants versus actual local files
- previously downloaded single-file copies
- forwarded or reshared copies
- local-share derivatives
- screenshots, exports, or other non-sync public artifacts when in scope

The operator must be able to answer: **what can still resurface later even though closure was once declared?**

### 3) Invalidator budget and re-open rules

This section must show:

- which rediscovery events automatically invalidate durable closure
- which rediscovery events only narrow the sentence
- which events merely require annotation
- tolerated unknown-survivor budget if policy allows one
- maximum honest lag before a rediscovery event must reopen the claim

The operator must be able to answer: **what would force us to reopen this closure verdict later?**

### 4) Strongest honest durable-closure sentence

This section must preserve two separate sentences:

- strongest honest durable-closure sentence now
- blocked stronger durable-closure sentence

Examples:

- `closure holds unless hidden archive or forwarded copy resurfaces`
- `durable for linked devices only; forwarded-recipient rediscovery reopens the claim`
- `point-in-time closure proven; durable closure not yet proven`
- `late survivor rediscovery would automatically collapse this verdict`

## Hard rules

The page must never:

- equate a past closure verdict with durable closure automatically
- omit rediscovery surfaces because they are inconvenient or hidden
- omit the invalidator set
- emit `durably closed` without naming what can still reopen that claim
