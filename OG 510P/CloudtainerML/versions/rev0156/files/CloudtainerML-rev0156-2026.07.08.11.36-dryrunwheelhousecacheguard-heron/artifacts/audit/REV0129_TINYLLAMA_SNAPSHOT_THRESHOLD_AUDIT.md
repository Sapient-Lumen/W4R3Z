# TinyLlama snapshot threshold audit — REV0129

Status: `pass`  
Promotion allowed: `false`

## What this prevents

A legitimate pinned TinyLlama snapshot must not be rejected by impossible local minimum-size thresholds. Rev0126 had `config.json >= 1000` even though the locked tree reports `config.json` as 608 bytes.

## Errors

- none

## Warnings

- none
