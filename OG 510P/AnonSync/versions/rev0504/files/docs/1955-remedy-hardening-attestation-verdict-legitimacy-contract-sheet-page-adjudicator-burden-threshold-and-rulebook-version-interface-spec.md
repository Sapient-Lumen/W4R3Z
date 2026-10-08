# Remedy-hardening-attestation verdict-legitimacy contract sheet page — adjudicator, burden, threshold, and rulebook version

## Purpose

This page is the compact contract for deciding whether the trusted current witnesses actually justify the sentence the product wants to say now.
It exists so the product can distinguish `trusted witness exists`, `current rulebook selected`, `authorized adjudicator present`, `burden met for named slice only`, `override still open`, `verdict ratified`, and `broader stronger sentence blocked`.

## Core fields

- verdict-legitimacy identifier
- source observer-integrity receipt identifier
- target sentence under adjudication
- current rulebook identifier
- current rulebook version
- rulebook scope by product version, platform, topology, and world
- authorized adjudicator class
- adjudicator identity or seat
- sentence-specific burden class
- threshold rule or decision function
- tie-break rule
- override or exception rule status
- admitted evidence set identifier
- excluded evidence set identifier
- current verdict-legitimacy class
- highest currently safe verdict sentence
- strongest blocked stronger sentence
- next fact that upgrades verdict legitimacy now
- next fact that collapses verdict legitimacy now

## Verdict-legitimacy classes

The page must model at least these distinct classes:

- trusted witness, burden not yet chosen
- current rulebook ambiguous
- authorized adjudicator missing or disputed
- current rulebook selected, threshold not met
- threshold met for named slice only
- threshold met but tie-break unresolved
- threshold met but override or exception review open
- threshold met under deprecated rulebook only
- verdict ratified under current rulebook
- broader stronger sentence blocked

## Burden classes

The page must support at least these burden classes:

- clue sufficient for operator attention only
- warning banner burden
- named-slice conformance burden
- named-slice breach-confirmation burden
- affected-party notice burden
- policy-still-governing burden
- broader estate-wide sentence burden

## Fixed rendering order

Every verdict-legitimacy contract sheet must render the same sections in the same order:

1. **Highest currently verdict-safe sentence**
2. **Target sentence, rulebook version, and adjudicator authority**
3. **Burden, threshold, and tie-break ledger**
4. **Admitted evidence, exclusions, and override state**
5. **Next fact that upgrades or collapses verdict legitimacy**

## Hard rules

The contract sheet must never let an operator hide:

- a green status behind an unstated burden class
- a trusted witness behind an unstated rulebook version
- one world's meaning behind `general product meaning` wording
- a visible queue behind an unstated operative threshold rule
- a pending exception or tie-break behind `verdict complete` wording
