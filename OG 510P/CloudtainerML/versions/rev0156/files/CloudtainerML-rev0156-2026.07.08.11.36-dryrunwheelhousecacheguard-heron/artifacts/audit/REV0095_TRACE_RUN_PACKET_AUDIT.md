# Trace run packet audit — REV0095

Status: `pass`  
Promotion allowed: `false`

## Target

- model: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- revision: `fe8a4ea1ffedaf415f4da2f062534de366a451e6`
- license: `apache-2.0`
- command: `ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/REV0095_RUN_TINYLLAMA_PUBLIC_TRACE.sh`

## Errors

- none

## Warnings

- none

## Interpretation

This audit converts the next step from a generic instruction into a concrete immutable public-model trace packet. It is still non-promotional until the trace is captured and accepted by the gate.
