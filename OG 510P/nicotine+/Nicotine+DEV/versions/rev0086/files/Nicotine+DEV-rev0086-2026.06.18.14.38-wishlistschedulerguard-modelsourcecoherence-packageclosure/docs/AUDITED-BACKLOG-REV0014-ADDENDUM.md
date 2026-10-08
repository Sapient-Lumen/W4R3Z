# Audited backlog addendum — rev0014

rev0014 focused on **FOLDER-RESP-01**, led by U-167 with U-255/U-260/U-268 as support checks.

## Result

```text
U-167: source-confirmed across 3.3.10, 3.3.x, and master; maintainer-style reproducer passed all lanes.
U-255: source/test-confirmed support behavior; not standalone.
U-260: source/test-confirmed support behavior; public-adjacent; not standalone.
U-268: source/test-confirmed support behavior; partially master-gated; not standalone.
U-256/U-272: kept in the separate FolderContentsRequest request/echo/budget family.
```

## Ranking decision

U-167 moves up inside the audited backlog as a verified high-value regression/hardening item. It does not enter the strict document because master's allowed-response gate changes the current/future exploit shape and public folder-download issue history makes the novelty/priority less clean.

## Strict document state after rev0014

```text
Promoted report-candidates: 3
Production-ready disclosure texts: 0
New rev0014 promotions: 0
```

Retained strict candidates:

```text
U-123
PB-01 / U-168+U-176
SEARCH-RESP-01 / U-163
```
