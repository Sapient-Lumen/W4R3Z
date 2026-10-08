# Persisted-state proof page — flush evidence, shadowed values, and restart survival

## Purpose

Produce inspectable evidence for what was durably written, what still differs, and what survival ceiling the operator may claim.

This page exists to answer:

- `what exactly was persisted?`
- `what still differs between live, persisted, and boot-authoritative state?`
- `what restart/crash sentence is now honest?`

## Required sections

### 1. Proof header

Must show:

- object mutated
- proof timestamp
- storage home
- principal / runtime that wrote the proof
- evidence class (`flush confirmed`, `storage snapshot observed`, `config authority unchanged`, `restart survival observed`, `partial only`)

### 2. Value comparison table

Each row must publish:

- field name
- live value
- persisted value
- boot-authoritative value
- comparison verdict (`fully aligned`, `persisted-lags-live`, `boot-shadows-persisted`, `unknown`)

### 3. Survival ceiling block

Must distinguish:

- survives live runtime only
- survives orderly stop/start on same storage home
- survives unclean crash on same storage home
- survives boot under config-owned authority
- survives service/principal/storage-home change

### 4. Shadow / override block

Must show any stronger plane that can still defeat the persisted value:

- config file
- launch arg / service package default
- different service account storage root
- external package-enforced binding
- other stronger authority

### 5. Strongest safe sentence

Examples:

- `The persisted store now matches the running value on this storage home, but a config-owned boot plane still overrides restart behavior.`
- `This proof supports same-home restart survival only.`

### 6. Blocked stronger sentence

Examples:

- `The setting is globally durable everywhere this software can run.`
- `Persisted here means no stronger plane can override it later.`

## Receipt obligations

Any receipt derived from this page must preserve:

- proof timestamp
- storage home
- value comparison table or digest thereof
- survival ceiling
- override roster
- strongest safe sentence
- blocked stronger sentence
