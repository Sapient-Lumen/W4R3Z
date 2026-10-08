# Multi-lab replication and boundary mapping

Revision: rev0012  
Created: 2026-05-25T04:56:00-04:00

This method note opens the cube's serious multi-lab replication lane. The seed distinguishes failed replications from negative results while also saying the corpora interlock. The rev0012 design therefore treats a replication record as an evidentiary route, not a gotcha verdict.

## Core rule

A multi-lab replication record should answer:

1. What exact claim or protocol was targeted?
2. Was the replication direct, conceptual, program-level, or a multi-effect boundary map?
3. What was the original estimate, if available?
4. What was the replication estimate, interval, and uncertainty?
5. Which labs, samples, populations, materials, settings, or endpoints define the boundary?
6. What did the infrastructure make visible: protocol, data, lab variation, reagent/material availability, or publication regardless of outcome?
7. What author responses, later syntheses, or field/practice lags remain missing?

## Outcome vocabulary

Use at least five states, not one binary:

- `robust_control`: a multi-lab effort supports the target effect while mapping magnitude and moderators.
- `shrunk`: the effect remains directionally present or mixed but smaller than the original estimate.
- `null_compatible`: the interval is compatible with no effect under the tested protocol.
- `failed_under_protocol`: the original target estimate is not recovered in a direct or close protocol.
- `infeasible_or_visibility_limited`: replication was blocked or constrained by missing protocol, data, materials, or cooperation.

## Rev0012 Promoted records

- `MKH-REP-0001`: Ego-depletion RRR.
- `MKH-REP-0006`: Facial-feedback RRR.
- `MKH-REP-0007`: Many Labs 1.
- `MKH-REP-0008`: Many Labs 2.
- `MKH-REP-0009`: Reproducibility Project: Cancer Biology.
- `MKH-REP-0010`: ManyBabies 1 successful-control record.

## Guardrail

Do not infer misconduct, field invalidity, or researcher blame from non-replication. The promoted parent records are source-backed but still one-pass. They need child records, author responses, and later-synthesis surfaces before any field-level status claim.
