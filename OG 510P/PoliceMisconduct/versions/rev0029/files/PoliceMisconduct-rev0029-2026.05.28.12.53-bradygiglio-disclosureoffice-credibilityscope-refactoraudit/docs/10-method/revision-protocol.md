# Revision protocol

Each revision should leave a downloadable bundle named:

`PoliceMisconduct-rev####-YYYY.MM.DD.HH.MM-summary-highlight-codename.zip`

## Required updates for every substantive revision

- update `RELEASE-MANIFEST.json`;
- update `REVISION-RECEIPT.json`;
- update `CHANGELOG.md`;
- update `SURFACE-STATUS.json` if public/data/state posture changed;
- update owning ledgers for the change;
- run `make lint`.

## What a good revision does

A good revision reduces uncertainty, preserves a distinction, hardens a guardrail, adds a test, resolves an open question, or captures a rejected path.
A revision that merely adds prose without changing a controlled surface should explain why that prose is load-bearing.
